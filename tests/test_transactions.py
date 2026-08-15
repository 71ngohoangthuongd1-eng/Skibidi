"""Transaction-level tests: atomic purchases, stock, cart checkout and payment idempotency."""

from decimal import Decimal

from sqlalchemy import select, func

from bot.database.main import Database
from bot.database.models import User, BoughtGoods, ItemValues, Payments, Operations, ReferralEarnings
from bot.database.models.main import CartItems
from bot.database.methods.transactions import (
    buy_item_transaction,
    process_payment_with_referral,
    checkout_cart_transaction,
)


async def _balance(telegram_id: int) -> Decimal:
    async with Database().session() as s:
        user = (await s.execute(select(User).where(User.telegram_id == telegram_id))).scalars().one()
        return Decimal(str(user.balance))


class TestBuyItemTransaction:

    async def test_buy_item_success(self, user_factory, item_factory):
        await user_factory(telegram_id=100001, balance=500)
        await item_factory(name="Widget", price=100, values=[("val1", False)])

        success, msg, data = await buy_item_transaction(100001, "Widget")

        assert success is True
        assert msg == "success"
        assert data["item_name"] == "Widget"
        assert data["value"] == "val1"
        assert data["price"] == 100.0
        assert data["new_balance"] == 400.0
        assert await _balance(100001) == Decimal("400")

        async with Database().session() as s:
            bought = (await s.execute(select(BoughtGoods).where(BoughtGoods.buyer_id == 100001))).scalars().all()
            assert len(bought) == 1
            assert bought[0].item_name == "Widget"
            assert bought[0].value == "val1"
            remaining = (await s.execute(select(func.count(ItemValues.id)))).scalar()
            assert remaining == 0

    async def test_buy_item_insufficient_funds(self, user_factory, item_factory):
        await user_factory(telegram_id=100002, balance=50)
        await item_factory(name="Expensive", price=100, values=[("val1", False)])

        success, msg, data = await buy_item_transaction(100002, "Expensive")

        assert success is False
        assert msg == "insufficient_funds"
        assert data is None
        assert await _balance(100002) == Decimal("50")

    async def test_buy_item_out_of_stock(self, user_factory, item_factory):
        await user_factory(telegram_id=100003, balance=500)
        await item_factory(name="Empty", price=100, values=None)

        success, msg, data = await buy_item_transaction(100003, "Empty")

        assert success is False
        assert msg == "out_of_stock"
        assert data is None

    async def test_buy_item_user_not_found(self, item_factory):
        await item_factory(name="Gadget", price=100, values=[("val1", False)])

        success, msg, data = await buy_item_transaction(999999, "Gadget")

        assert success is False
        assert msg == "user_not_found"
        assert data is None

    async def test_buy_item_infinite_stock(self, user_factory, item_factory):
        await user_factory(telegram_id=100005, balance=500)
        await item_factory(name="InfItem", price=100, values=[("infinite_val", True)])

        success, msg, data = await buy_item_transaction(100005, "InfItem")

        assert success is True
        assert data["value"] == "infinite_val"
        assert await _balance(100005) == Decimal("400")

        async with Database().session() as s:
            remaining = (await s.execute(select(func.count(ItemValues.id)))).scalar()
            assert remaining == 1

    async def test_buy_all_stock_exhausts(self, user_factory, item_factory):
        await user_factory(telegram_id=100006, balance=1000)
        await item_factory(name="Multi", price=100,
                           values=[("v1", False), ("v2", False), ("v3", False)])

        bought = []
        for _ in range(3):
            success, msg, data = await buy_item_transaction(100006, "Multi")
            assert success is True
            bought.append(data["value"])
        assert sorted(bought) == ["v1", "v2", "v3"]

        success, msg, data = await buy_item_transaction(100006, "Multi")
        assert success is False
        assert msg == "out_of_stock"
        assert await _balance(100006) == Decimal("700")


class TestProcessPaymentWithReferral:

    async def test_payment_success(self, user_factory):
        await user_factory(telegram_id=200001, balance=0)

        success, msg = await process_payment_with_referral(
            user_id=200001, amount=Decimal("500"),
            provider="test_provider", external_id="ext_001",
        )

        assert success is True
        assert msg == "success"
        assert await _balance(200001) == Decimal("500")

        async with Database().session() as s:
            payment = (await s.execute(select(Payments).where(Payments.external_id == "ext_001"))).scalars().first()
            assert payment.status == "succeeded"
            ops = (await s.execute(select(Operations).where(Operations.user_id == 200001))).scalars().all()
            assert len(ops) == 1

    async def test_payment_idempotency(self, user_factory):
        await user_factory(telegram_id=200002, balance=0)

        success1, msg1 = await process_payment_with_referral(
            user_id=200002, amount=Decimal("300"),
            provider="prov_a", external_id="ext_dup",
        )
        assert success1 is True and msg1 == "success"

        success2, msg2 = await process_payment_with_referral(
            user_id=200002, amount=Decimal("300"),
            provider="prov_a", external_id="ext_dup",
        )
        assert success2 is False
        assert msg2 == "already_processed"
        assert await _balance(200002) == Decimal("300")

    async def test_referral_bonus(self, user_factory):
        await user_factory(telegram_id=200010, balance=0)
        await user_factory(telegram_id=200003, balance=0, referral_id=200010)

        success, msg = await process_payment_with_referral(
            user_id=200003, amount=Decimal("100"),
            provider="prov_ref", external_id="ext_ref_001", referral_percent=10,
        )

        assert success is True
        assert await _balance(200003) == Decimal("100")
        assert await _balance(200010) == Decimal("10")

        async with Database().session() as s:
            earnings = (await s.execute(
                select(ReferralEarnings).where(
                    ReferralEarnings.referrer_id == 200010,
                    ReferralEarnings.referral_id == 200003,
                )
            )).scalars().all()
            assert len(earnings) == 1
            assert Decimal(str(earnings[0].amount)) == Decimal("10")


class TestCheckoutCart:

    async def test_cart_checkout(self, user_factory, item_factory):
        await user_factory(telegram_id=300001, balance=1000)
        await item_factory(name="CartItem", price=100, values=[("c1", False), ("c2", False)])

        from bot.database.methods.create import add_to_cart
        await add_to_cart(300001, "CartItem")

        success, msg, results = await checkout_cart_transaction(300001)

        assert success is True
        assert msg == "success"
        assert len(results) == 1
        assert results[0]["item_name"] == "CartItem"
        assert await _balance(300001) == Decimal("900")

        async with Database().session() as s:
            remaining = (await s.execute(select(func.count(ItemValues.id)))).scalar()
            assert remaining == 1  # one stock item consumed
            cart_left = (await s.execute(select(func.count(CartItems.id)))).scalar()
            assert cart_left == 0

    async def test_empty_cart(self, user_factory):
        await user_factory(telegram_id=300002, balance=100)

        success, msg, results = await checkout_cart_transaction(300002)

        assert success is False
        assert msg == "cart_empty"
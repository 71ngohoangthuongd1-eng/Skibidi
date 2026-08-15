"""Exactly-once guarantees for SePay IPN payment + item delivery.

The six audit cases:
  1. Same transfer submitted twice             → processed exactly once
  2. Same transfer, concurrent webhooks        → exactly one delivery
  3. Retry after success                       → no second delivery
  4. Payment ok but downstream operation fail  → safe rollback, state recoverable
  5. Two payments, two buyers, distinct stock  → each gets their own item
  6. One stock unit, two concurrent payments   → exactly one buyer receives it
"""

import asyncio

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from bot.database.main import Database
from bot.database.models import User, BoughtGoods, ItemValues, Payments, Operations, Goods
from bot.database.methods.create import create_pending_payment
from bot.database.methods.transactions import (
    process_sepay_item_payment,
    ipn_claim_and_credit_topup,
)


async def _balance(telegram_id: int):
    async with Database().session() as s:
        user = (await s.execute(select(User).where(User.telegram_id == telegram_id))).scalars().one()
        return user.balance


async def _payment_row(payment_id: int):
    async with Database().session() as s:
        return (await s.execute(select(Payments).where(Payments.id == payment_id))).scalars().first()


async def _real_payment(external_id: str, user_id: int, amount) -> Payments:
    """Create a real payments row the way the direct-purchase flow does."""
    pid = await create_pending_payment(
        provider="sepay_item", external_id=external_id, user_id=user_id, amount=float(amount),
        currency="RUB",
    )
    return await _payment_row(pid)


async def _deliver(payment_ns, item_name: str, amount=None):
    amount = amount if amount is not None else payment_ns.amount
    return await process_sepay_item_payment(payment=payment_ns, amount=amount, item_name=item_name)


async def _buy_count(user_id: int, item_name: str) -> int:
    async with Database().session() as s:
        return (await s.execute(
            select(func.count(BoughtGoods.id)).where(
                BoughtGoods.buyer_id == user_id,
                BoughtGoods.item_name == item_name,
            )
        )).scalar()


async def _stock_left(item_name: str) -> int:
    async with Database().session() as s:
        gid = (await s.execute(select(Goods.id).where(Goods.name == item_name))).scalar()
        if not gid:
            return 0
        return (await s.execute(
            select(func.count(ItemValues.id)).where(ItemValues.item_id == gid)
        )).scalar()


class TestSameTransferTwice:

    async def test_two_submits_process_exactly_once(self, user_factory, item_factory):
        await user_factory(telegram_id=400001, balance=0)
        await item_factory(name="SePayItem", price=100, values=[("v1", False)])
        payment = await _real_payment("CODE_ABC", 400001, 100)

        status1, msg1, data1 = await _deliver(payment, "SePayItem")
        assert status1 == "delivered"
        assert data1["value"] == "v1"

        # Second webhook (SePay retry) observes the claimed payment as a no-op.
        status2, _, _ = await _deliver(payment, "SePayItem")
        assert status2 == "already_done"

        assert await _buy_count(400001, "SePayItem") == 1
        assert await _stock_left("SePayItem") == 0

        # Item payments never touch the balance or create an Operations record.
        assert await _balance(400001) == 0
        async with Database().session() as s:
            ops = (await s.execute(
                select(func.count(Operations.id)).where(Operations.user_id == 400001)
            )).scalar()
            assert ops == 0

    async def test_concurrent_same_transfer_single_delivery(self, user_factory, item_factory):
        await user_factory(telegram_id=400002, balance=0)
        await item_factory(name="RaceItem", price=100, values=[("r1", False)])
        payment = await _real_payment("CODE_CONC", 400002, 100)

        results = await asyncio.gather(
            _deliver(payment, "RaceItem"),
            _deliver(payment, "RaceItem"),
            _deliver(payment, "RaceItem"),
        )
        delivered = [r for r in results if r[0] == "delivered"]
        assert len(delivered) == 1
        assert await _buy_count(400002, "RaceItem") == 1
        assert await _stock_left("RaceItem") == 0


class TestRetryAfterSuccess:

    async def test_retry_after_success_does_not_deliver_again(self, user_factory, item_factory):
        await user_factory(telegram_id=400003, balance=0)
        await item_factory(name="RetryItem", price=100, values=[("r1", False), ("r2", False)])
        payment = await _real_payment("CODE_RETRY", 400003, 100)

        status1, _, _ = await _deliver(payment, "RetryItem")
        assert status1 == "delivered"

        status2, _, _ = await _deliver(payment, "RetryItem")
        assert status2 == "already_done"

        assert await _buy_count(400003, "RetryItem") == 1
        assert await _stock_left("RetryItem") == 1  # second unit untouched

    async def test_topup_retry_credits_once(self, user_factory):
        await user_factory(telegram_id=400004, balance=0)
        external_id = "CODE_TOPUP"
        pid = await create_pending_payment(
            provider="sepay", external_id=external_id, user_id=400004, amount=200.0, currency="RUB",
        )
        payment = await _payment_row(pid)

        ok1, msg1 = await ipn_claim_and_credit_topup(payment=payment, amount=200)
        assert ok1 is True and msg1 == "claimed"
        assert await _balance(400004) == 200

        ok2, msg2 = await ipn_claim_and_credit_topup(payment=payment, amount=200)
        assert ok2 is False and msg2 == "already_processed"
        assert await _balance(400004) == 200

        async with Database().session() as s:
            ops = (await s.execute(
                select(func.count(Operations.id)).where(Operations.user_id == 400004)
            )).scalar()
            assert ops == 1


class TestRollbackSafety:

    async def test_out_of_stock_refunds_balance_and_blocks_retry(self, user_factory, item_factory):
        await user_factory(telegram_id=400005, balance=0)
        await item_factory(name="OOSItem", price=150, values=None)
        payment = await _real_payment("CODE_OOS", 400005, 100)

        status, msg, data = await _deliver(payment, "OOSItem")
        assert status == "refunded"

        row = await _payment_row(payment.id)
        assert row.status == "balance_refunded"
        assert await _balance(400005) == 100  # money back on balance, not lost

        status2, _, _ = await _deliver(payment, "OOSItem")
        assert status2 == "already_done"
        assert await _balance(400005) == 100

    async def test_abort_leaves_payment_pending_and_recoverable(self, user_factory):
        await user_factory(telegram_id=400006, balance=0)
        payment = await _real_payment("CODE_NOITEM", 400006, 100)

        status, msg, data = await _deliver(payment, "NeverExistedItem")
        assert status in ("payment_error", "refunded")
        row = await _payment_row(payment.id)
        assert row.status in ("pending", "balance_refunded")
        assert await _balance(400006) in (0, 100)
        assert await _buy_count(400006, "NeverExistedItem") == 0


class TestDistinctBuyers:

    async def test_two_payments_two_buyers_each_get_own_item(self, user_factory, item_factory):
        await user_factory(telegram_id=400101, balance=0)
        await user_factory(telegram_id=400102, balance=0)
        await item_factory(name="TwoBuyers", price=100,
                           values=[("a1", False), ("a2", False), ("a3", False)])

        p1 = await _real_payment("CODE_B1", 400101, 100)
        p2 = await _real_payment("CODE_B2", 400102, 100)

        s1, _, d1 = await _deliver(p1, "TwoBuyers")
        s2, _, d2 = await _deliver(p2, "TwoBuyers")
        assert s1 == "delivered" and s2 == "delivered"

        r1 = await _payment_row(p1.id)
        r2 = await _payment_row(p2.id)
        assert r1.status == "succeeded" and r2.status == "succeeded"

        async with Database().session() as s:
            rows = (await s.execute(
                select(BoughtGoods).where(BoughtGoods.item_name == "TwoBuyers")
            )).scalars().all()
            assert len(rows) == 2
            assert {r.buyer_id for r in rows} == {400101, 400102}
            assert len({r.payment_id for r in rows}) == 2
        assert await _stock_left("TwoBuyers") == 1


class TestSingleStockConcurrency:

    async def test_one_stock_two_concurrent_payments_one_winner(self, user_factory, item_factory):
        await user_factory(telegram_id=400201, balance=0)
        await user_factory(telegram_id=400202, balance=0)
        await item_factory(name="LastStock", price=100, values=[("only", False)])

        p1 = await _real_payment("CODE_WS1", 400201, 100)
        p2 = await _real_payment("CODE_WS2", 400202, 100)

        results = await asyncio.gather(
            _deliver(p1, "LastStock"),
            _deliver(p2, "LastStock"),
        )
        statuses = sorted(r[0] for r in results)

        # Exactly one buyer receives the single physical unit; the other, never.
        assert "delivered" in statuses
        assert "refunded" in statuses
        assert statuses.count("delivered") == 1

        async with Database().session() as s:
            rows = (await s.execute(
                select(BoughtGoods).where(BoughtGoods.item_name == "LastStock")
            )).scalars().all()
            assert len(rows) == 1
        assert await _stock_left("LastStock") == 0

    async def test_unique_payment_link_is_enforced_at_db_level(self, user_factory, item_factory):
        await user_factory(telegram_id=400301, balance=0)
        await user_factory(telegram_id=400302, balance=0)
        await item_factory(name="UniqLink", price=100,
                           values=[("u1", False), ("u2", False), ("u3", False)])
        payment = await _real_payment("CODE_SHARED", 400301, 100)

        # First delivery occupies the payment link with a real BoughtGoods row.
        status, _, _ = await _deliver(payment, "UniqLink")
        assert status == "delivered"

        # A racing/retried path that double-delivers the same payment must fail
        # the BoughtGoods.payment_id unique constraint at the database level.
        inserted = "not_run"

        async def raw_insert():
            nonlocal inserted
            async with Database().session() as s:
                try:
                    row = BoughtGoods(name="UniqLink", value="x", price=100,
                                      buyer_id=400302, bought_datetime=None,
                                      unique_id=777777, payment_id=payment.id)
                    s.add(row)
                    await s.commit()
                    inserted = "duplicate"
                except IntegrityError:
                    await s.rollback()
                    inserted = "integrity_error"

        await raw_insert()
        assert inserted == "integrity_error"
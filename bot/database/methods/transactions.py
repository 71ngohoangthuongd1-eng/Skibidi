from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import exists as sa_exists_top

from bot.database.models import User, ItemValues, Goods, BoughtGoods, Payments, Operations
from bot.database.models.main import PromoCodes, PromoCodeUsages, CartItems
from bot.database import Database
from bot.misc import EnvKeys
from bot.database.methods.read import invalidate_user_cache, invalidate_stats_cache, invalidate_item_cache
from bot.database.methods.cache_utils import safe_create_task
from bot.database.methods.audit import log_audit

_PAYMENT_CLAIMABLE = ("pending", "submitted")


async def buy_item_transaction(telegram_id: int, item_name: str, promo_code: str = None,
                               charge_limit: Decimal | None = None,
                               charge_source: str | None = None) -> tuple[bool, str, dict | None]:
    """
    Complete transactional purchase of goods with checks and locks.
    Returns: (success, message, purchase_data)

    ``charge_limit``: when set (direct payments credited out-of-band) the item
    must sell for at most this amount; pricing beyond it aborts. The balance
    check is softened in that case because the funds are not on the balance.
    ``charge_source``: optional label (e.g. a payment id) stored on the purchase.
    """
    from sqlalchemy import exists as sa_exists
    max_retries = 3
    for attempt in range(max_retries):
        async with Database().session() as s:
            try:
                # 1. Lock the user to check the balance
                user = (await s.execute(
                    select(User).where(User.telegram_id == telegram_id).with_for_update()
                )).scalars().one_or_none()

                if not user:
                    await s.rollback()
                    return False, "user_not_found", None

                # 2. Get information about the product
                goods = (await s.execute(
                    select(Goods).where(Goods.name == item_name).with_for_update()
                )).scalars().one_or_none()

                if not goods:
                    await s.rollback()
                    return False, "item_not_found", None

                price = Decimal(str(goods.price))
                final_price = price
                discount_info = None

                # 2.5. Apply promo code if provided
                if promo_code:
                    promo = (await s.execute(
                        select(PromoCodes).where(PromoCodes.code == promo_code.upper()).with_for_update()
                    )).scalars().first()

                    if not promo or not promo.is_active:
                        await s.rollback()
                        return False, "promo_invalid", None

                    if promo.discount_type == "balance":
                        await s.rollback()
                        return False, "promo_invalid", None

                    if promo.expires_at and promo.expires_at < datetime.now(timezone.utc):
                        await s.rollback()
                        return False, "promo_expired", None

                    if promo.max_uses > 0 and promo.current_uses >= promo.max_uses:
                        await s.rollback()
                        return False, "promo_max_uses", None

                    # Check per-user usage
                    used = (await s.execute(
                        select(sa_exists().where(
                            PromoCodeUsages.promo_id == promo.id,
                            PromoCodeUsages.user_id == telegram_id
                        ))
                    )).scalar()
                    if used:
                        await s.rollback()
                        return False, "promo_already_used", None

                    # Check item/category binding
                    if promo.item_id and promo.item_id != goods.id:
                        await s.rollback()
                        return False, "promo_wrong_item", None
                    if promo.category_id and promo.category_id != goods.category_id:
                        await s.rollback()
                        return False, "promo_wrong_category", None

                    # Apply discount
                    if promo.discount_type == 'percent':
                        final_price = price * (1 - Decimal(str(promo.discount_value)) / 100)
                    else:
                        final_price = max(price - Decimal(str(promo.discount_value)), Decimal(0))
                    final_price = final_price.quantize(Decimal("0.01"))

                    # Record usage
                    promo.current_uses += 1
                    s.add(PromoCodeUsages(promo_id=promo.id, user_id=telegram_id))
                    discount_info = {
                        "code": promo.code,
                        "original_price": float(price),
                        "discount": float(price - final_price),
                    }

                # 3. Checking the balance (softened when charge_limit is imposed)
                if charge_limit is not None:
                    if final_price > charge_limit:
                        await s.rollback()
                        return False, "price_mismatch", None
                elif user.balance < final_price:
                    await s.rollback()
                    return False, "insufficient_funds", None

                # 4. Receive and lock the goods for purchase
                item_value = (await s.execute(
                    select(ItemValues).where(ItemValues.item_id == goods.id).with_for_update(skip_locked=True)
                )).scalars().first()

                if not item_value:
                    await s.rollback()
                    return False, "out_of_stock", None

                # 5. If the product is not endless, we remove it
                if not item_value.is_infinity:
                    await s.delete(item_value)

                # 6. Write off the balance (only when no charge limit: SePay direct
                # purchases were paid out-of-band and are settled at the end).
                if charge_limit is None:
                    user.balance -= final_price

                # 7. Create a purchase record
                bought_item = BoughtGoods(
                    name=item_name,
                    value=item_value.value,
                    price=final_price,
                    buyer_id=telegram_id,
                    bought_datetime=datetime.now(timezone.utc),
                    unique_id=uuid4().int >> 65,
                    payment_id=charge_source,
                )
                s.add(bought_item)
                await s.flush()

                # 8. Commit the transaction
                await s.commit()

                safe_create_task(invalidate_user_cache(telegram_id))
                safe_create_task(invalidate_stats_cache())
                safe_create_task(invalidate_item_cache(item_name))

                result_data = {
                    "item_name": item_name,
                    "value": item_value.value,
                    "price": float(final_price),
                    "new_balance": None if charge_limit is not None else float(user.balance),
                    "unique_id": bought_item.unique_id,
                    "bought_id": bought_item.id,
                    "bought_datetime": bought_item.bought_datetime.isoformat(),
                }
                if discount_info:
                    result_data["discount"] = discount_info

                return True, "success", result_data

            except IntegrityError as e:
                await s.rollback()
                if "unique_id" in str(e).lower() and attempt < max_retries - 1:
                    continue  # Retry with a new unique_id
                await log_audit(
                    "purchase_failed",
                    level="WARNING",
                    user_id=telegram_id,
                    resource_type="Item",
                    resource_id=item_name,
                    details=str(e),
                )
                return False, "transaction_error", None

            except Exception as e:
                await s.rollback()
                await log_audit(
                    "purchase_failed",
                    level="WARNING",
                    user_id=telegram_id,
                    resource_type="Item",
                    resource_id=item_name,
                    details=str(e),
                )
                return False, "transaction_error", None

    return False, "transaction_error", None


async def ipn_claim_and_credit_topup(payment: Payments, amount: Decimal, referral_percent: int = 0) -> tuple[bool, str]:
    """Atomically finalize a bank top-up honoured by a SePay IPN webhook.

    The payment row is the single source of truth: it is locked, validated, and
    marked ``succeeded`` in the exact transaction that credits the user's balance.
    Retried webhooks (duplicates, concurrent deliveries across serverless
    instances) observe the terminal status and are rejected before any side
    effect, so funds are credited exactly once.

    Returns (success, message):
      - success=True,  "claimed"            — this invocation finalized the payment
      - success=False, "already_processed"  — another invocation already did
      - success=False, "amount_mismatch"    — payload amount differs from the stored one
    """
    from bot.database.models import Operations, ReferralEarnings

    async with Database().session() as s:
        try:
            claimed = (await s.execute(
                # Existing payment rows are pending/submitted here; locking serializes
                # concurrent webhooks so only one can run the full claim below.
                select(Payments).where(Payments.id == payment.id).with_for_update()
            )).scalars().first()

            if claimed:
                if claimed.status in ("succeeded", "failed", "balance_refunded"):
                    await s.rollback()
                    return False, "already_processed"
                if Decimal(str(claimed.amount)) != amount:
                    await s.rollback()
                    return False, "amount_mismatch"
                claimed.status = "succeeded"
            else:
                claimed = Payments(
                    provider=payment.provider,
                    external_id=payment.external_id,
                    user_id=payment.user_id,
                    amount=amount,
                    currency=payment.currency or EnvKeys.PAY_CURRENCY,
                    status="succeeded",
                )
                s.add(claimed)

            user = (await s.execute(
                select(User).where(User.telegram_id == payment.user_id).with_for_update()
            )).scalars().one_or_none()
            if not user:
                await s.rollback()
                return False, "payment_error"

            user.balance += amount
            s.add(Operations(
                user_id=payment.user_id,
                operation_value=amount,
                operation_time=datetime.now(timezone.utc),
            ))

            if referral_percent > 0 and user.referral_id and user.referral_id != user.telegram_id:
                referral_amount = (Decimal(referral_percent) / Decimal(100)) * amount
                if referral_amount > 0:
                    referrer = (await s.execute(
                        select(User).where(User.telegram_id == user.referral_id).with_for_update()
                    )).scalars().one_or_none()
                    if referrer:
                        referrer.balance += referral_amount
                        s.add(ReferralEarnings(
                            referrer_id=user.referral_id,
                            referral_id=payment.user_id,
                            amount=referral_amount,
                            original_amount=amount,
                        ))
                        await log_audit(
                            "referral_bonus",
                            user_id=user.referral_id,
                            resource_type="User",
                            resource_id=str(payment.user_id),
                            details=f"paid={amount}, bonus={referral_amount}",
                        )

            await s.commit()

            safe_create_task(invalidate_user_cache(payment.user_id))
            safe_create_task(invalidate_stats_cache())
            return True, "claimed"

        except Exception as e:
            await s.rollback()
            await log_audit(
                "payment_failed",
                level="WARNING",
                user_id=payment.user_id,
                resource_type="Payment",
                resource_id=str(payment.id),
                details=f"provider={payment.provider}, amount={amount}, error={e}",
            )
            return False, "payment_error"


async def process_sepay_item_payment(
    payment: Payments, amount: Decimal, item_name: str, promo_code: str | None = None
) -> tuple[str, str | None, dict | None]:
    """Atomically settle a SePay direct-purchase payment AND deliver the item.

    Exactly-once, fully in one DB transaction guarded by the payment row:
      - only ``pending``/``submitted`` payments can be claimed; any later webhook
        (concurrent or retried) sees the terminal status and becomes a no-op
      - the physical purchase is recorded against ``BoughtGoods.payment_id`` with a
        unique constraint, so a second concurrent delivery for the same payment is
        impossible at the database level
      - every state change (claim, balance credit, stock drop, promo usage) commits
        together or rolls back together — a crash or failure leaves the payment
        ``pending`` and fully recoverable by the retrying webhook.

    Returns (status, message, purchase_data):
      - status "delivered"     → item granted to user's balance is untouched
      - status "refunded"      → money went to user's balance instead of an item
      - status "already_done"  → a previous webhook already settled this payment
      - status "payment_error" → unexpected failure (session rolled back)
    """
    async with Database().session() as s:
        try:
            # 1. Serialize on the payments row (FOR UPDATE blocks concurrent webhooks).
            locked = (await s.execute(
                select(Payments).where(Payments.id == payment.id).with_for_update()
            )).scalars().first()

            if locked:
                if locked.status in ("succeeded", "failed", "balance_refunded"):
                    await s.rollback()
                    return "already_done", "already_processed", None
                if Decimal(str(locked.amount)) != amount:
                    await s.rollback()
                    return "payment_error", "amount_mismatch", None
                # 2. Atomic compare-and-set claim. Even if two webhooks read
                #    "pending" concurrently, exactly one UPDATE wins and flushes
                #    first; the loser's flush raises StatementError and this
                #    handler rolls back below. (Database-level guarantee, no
                #    in-memory flag / singleton involved.)
                result = await s.execute(
                    update(Payments)
                    .where(
                        Payments.id == payment.id,
                        Payments.status.in_((_PAYMENT_CLAIMABLE)),
                    )
                    .values(status="succeeded")
                )
                if result.rowcount != 1:
                    await s.rollback()
                    return "already_done", "already_processed", None
            else:
                locked = Payments(
                    provider=payment.provider,
                    external_id=payment.external_id,
                    user_id=payment.user_id,
                    amount=amount,
                    currency=payment.currency or EnvKeys.PAY_CURRENCY,
                    status="succeeded",
                )
                s.add(locked)
                await s.flush()

            payment_row_id = locked.id if locked else payment.id

            user = (await s.execute(
                select(User).where(User.telegram_id == payment.user_id).with_for_update()
            )).scalars().one_or_none()
            if not user:
                await s.rollback()
                return "payment_error", "user_not_found", None

            paid_amount = amount

            # 3. Allocate the physical item inside the SAME transaction as the claim.
            goods = (await s.execute(
                select(Goods).where(Goods.name == item_name).with_for_update()
            )).scalars().one_or_none()

            async def _refund(reason: str) -> tuple[str, str | None, dict | None]:
                """Atomically convert the claim into a balance refund (terminal)."""
                await s.execute(
                    update(Payments)
                    .where(Payments.id == payment_row_id)
                    .values(status="balance_refunded")
                )
                user.balance = user.balance + Decimal(str(paid_amount))
                await s.commit()
                return "refunded", reason, None

            if not goods:
                # Item vanished after checkout — keep the user whole.
                return await _refund("item_not_found")

            price = Decimal(str(goods.price))
            final_price = price
            discount_info = None

            # 3.1. Atomically claim exactly one physical unit. A single guarded
            #      DELETE..RETURNING removes at most one row at the SQL level, so
            #      no row-lock / SKIP LOCKED is needed and the same statement is
            #      race-safe on SQLite and Postgres alike. "Unlimited" rows are
            #      never deleted; they are read back when finite stock runs out.
            claimed = (await s.execute(
                delete(ItemValues)
                .where(ItemValues.id == (
                    select(ItemValues.id)
                    .where(ItemValues.item_id == goods.id, ItemValues.is_infinity.is_(False))
                    .order_by(ItemValues.id)
                    .limit(1)
                ).scalar_subquery())
                .returning(ItemValues.value)
            )).first()

            if not claimed:
                claimed = (await s.execute(
                    select(ItemValues.value).where(
                        ItemValues.item_id == goods.id, ItemValues.is_infinity.is_(True)
                    ).order_by(ItemValues.id).limit(1)
                )).first()

            if not claimed:
                # No stock left: refund atomically so the buyer is never left out.
                return await _refund("out_of_stock")

            claimed_value = claimed[0]

            # 3.2. Apply the promo code recorded at checkout, if still valid.
            #      Only after the stock claim succeeds (a refund never touches it).
            if promo_code:
                promo = (await s.execute(
                    select(PromoCodes).where(PromoCodes.code == promo_code.upper()).with_for_update()
                )).scalars().first()
                promo_ok = bool(
                    promo and promo.is_active and promo.discount_type != "balance"
                    and not (promo.expires_at and promo.expires_at < datetime.now(timezone.utc))
                    and not (promo.max_uses > 0 and promo.current_uses >= promo.max_uses)
                )
                if promo_ok:
                    used = (await s.execute(
                        select(sa_exists_top().where(
                            PromoCodeUsages.promo_id == promo.id,
                            PromoCodeUsages.user_id == payment.user_id,
                        ))
                    )).scalar()
                    if not used:
                        if promo.discount_type == "percent":
                            final_price = price * (Decimal("1") - Decimal(str(promo.discount_value)) / Decimal(100))
                        else:
                            final_price = max(price - Decimal(str(promo.discount_value)), Decimal(0))
                        final_price = final_price.quantize(Decimal("0.01"))
                        discount_info = {
                            "code": promo.code,
                            "original_price": float(price),
                            "discount": float(price - final_price),
                        }
                        promo.current_uses += 1
                        s.add(PromoCodeUsages(promo_id=promo.id, user_id=payment.user_id))

            if final_price > paid_amount:
                # Price moved above what the user paid (promo vanished): refund.
                return await _refund("price_mismatch")

            # 3.3. Record the purchase against the payment (unique payment_id ⇒
            #      a second delivery attempt for this payment is a constraint error).
            bought_item = BoughtGoods(
                name=item_name,
                value=claimed_value,
                price=final_price,
                buyer_id=payment.user_id,
                bought_datetime=datetime.now(timezone.utc),
                unique_id=uuid4().int >> 65,
                payment_id=payment_row_id,
            )
            s.add(bought_item)
            await s.flush()

            await s.commit()

            purchase_data = {
                "item_name": item_name,
                "value": claimed_value,
                "price": float(final_price),
                "unique_id": bought_item.unique_id,
                "bought_id": bought_item.id,
                "bought_datetime": bought_item.bought_datetime.isoformat(),
            }
            if discount_info:
                purchase_data["discount"] = discount_info

            safe_create_task(invalidate_user_cache(payment.user_id))
            safe_create_task(invalidate_stats_cache())
            safe_create_task(invalidate_item_cache(item_name))
            return "delivered", "success", purchase_data

        except IntegrityError as e:
            await s.rollback()
            # BoughtGoods.payment_id unique or duplicate claim insert: someone
            # else already settled this payment — exactly-once is preserved.
            await log_audit(
                "payment_failed",
                level="WARNING",
                user_id=payment.user_id,
                resource_type="Payment",
                resource_id=str(payment.id),
                details=f"duplicate delivery blocked: {e}",
            )
            return "payment_error", "already_processed", None

        except Exception as e:
            await s.rollback()
            await log_audit(
                "payment_failed",
                level="WARNING",
                user_id=payment.user_id,
                resource_type="Payment",
                resource_id=str(payment.id),
                details=f"provider={payment.provider}, amount={amount}, item={item_name}, error={e}",
            )
            return "payment_error", str(e), None


async def process_payment_with_referral(
        user_id: int,
        amount: Decimal,
        provider: str,
        external_id: str,
        referral_percent: int = 0
) -> tuple[bool, str]:
    """
    Processing a payment with a referral bonus in one transaction.
    Returns (success, message)
    """

    async with Database().session() as s:
        try:
            # 1. Check the idempotency of the payment
            existing_payment = (await s.execute(
                select(Payments).where(
                    Payments.provider == provider,
                    Payments.external_id == external_id
                ).with_for_update()
            )).scalars().first()

            if existing_payment:
                if existing_payment.status == "succeeded":
                    await s.rollback()
                    return False, "already_processed"
                existing_payment.status = "succeeded"
            else:
                payment = Payments(
                    provider=provider,
                    external_id=external_id,
                    user_id=user_id,
                    amount=amount,
                    currency=EnvKeys.PAY_CURRENCY,
                    status="succeeded"
                )
                s.add(payment)

            # 2. Update the user's balance
            user = (await s.execute(
                select(User).where(User.telegram_id == user_id).with_for_update()
            )).scalars().one()

            user.balance += amount

            # 3. Create a transaction record
            operation = Operations(
                user_id=user_id,
                operation_value=amount,
                operation_time=datetime.now(timezone.utc)
            )
            s.add(operation)

            # 4. Process the referral bonus
            if referral_percent > 0 and user.referral_id and user.referral_id != user_id:
                referral_amount = (Decimal(referral_percent) / Decimal(100)) * amount

                if referral_amount > 0:
                    referrer = (await s.execute(
                        select(User).where(User.telegram_id == user.referral_id).with_for_update()
                    )).scalars().one_or_none()

                    if referrer:
                        referrer.balance += referral_amount
                        await log_audit(
                            "referral_bonus",
                            user_id=user.referral_id,
                            resource_type="User",
                            resource_id=str(user_id),
                            details=f"paid={amount}, bonus={referral_amount}",
                        )

                        from bot.database.models import ReferralEarnings
                        earning = ReferralEarnings(
                            referrer_id=user.referral_id,
                            referral_id=user_id,
                            amount=referral_amount,
                            original_amount=amount
                        )
                        s.add(earning)

            referrer_id = user.referral_id if referral_percent > 0 else None

            await s.commit()

            safe_create_task(invalidate_user_cache(user_id))
            safe_create_task(invalidate_stats_cache())
            if referrer_id:
                safe_create_task(invalidate_user_cache(referrer_id))

            return True, "success"

        except IntegrityError:
            await s.rollback()
            return False, "already_processed"

        except Exception as e:
            await s.rollback()
            await log_audit(
                "payment_failed",
                level="WARNING",
                user_id=user_id,
                resource_type="Payment",
                details=f"provider={provider}, amount={amount}, error={e}",
            )
            return False, "payment_error"


async def checkout_cart_transaction(user_id: int) -> tuple[bool, str, list | None]:
    """
    Atomic cart checkout — purchase all items from user's cart in one transaction.
    Promo codes are read from cart_items.promo_code and validated at checkout time.
    Returns: (success, message, list[purchase_data])
    """
    from sqlalchemy import delete as sa_delete
    from sqlalchemy import exists as sa_exists

    async with Database().session() as s:
        try:
            # 1. Lock user
            user = (await s.execute(
                select(User).where(User.telegram_id == user_id).with_for_update()
            )).scalars().one_or_none()
            if not user:
                await s.rollback()
                return False, "user_not_found", None

            # 2. Get cart items
            cart_items = (await s.execute(
                select(CartItems).where(CartItems.user_id == user_id)
            )).scalars().all()

            if not cart_items:
                await s.rollback()
                return False, "cart_empty", None

            # 3. Resolve items, validate promos, calculate total
            purchases = []
            total_price = Decimal(0)
            items_to_remove = []
            promos_to_record = []  # (promo_obj, promo_id) for usage tracking
            claimed_value_ids: set[int] = set()

            for ci in cart_items:
                goods = (await s.execute(
                    select(Goods).where(Goods.name == ci.item_name).with_for_update()
                )).scalars().first()

                if not goods:
                    items_to_remove.append(ci.id)
                    continue

                query = select(ItemValues).where(ItemValues.item_id == goods.id)
                if claimed_value_ids:
                    query = query.where(ItemValues.id.notin_(claimed_value_ids))
                item_value = (await s.execute(
                    query.with_for_update(skip_locked=True)
                )).scalars().first()

                if not item_value:
                    items_to_remove.append(ci.id)
                    continue

                claimed_value_ids.add(item_value.id)

                price = Decimal(str(goods.price))
                final_price = price

                # Validate and apply promo code if stored on cart item
                if ci.promo_code:
                    promo = (await s.execute(
                        select(PromoCodes).where(PromoCodes.code == ci.promo_code.upper()).with_for_update()
                    )).scalars().first()

                    promo_valid = False
                    if promo and promo.is_active and promo.discount_type != 'balance':
                        if not (promo.expires_at and promo.expires_at < datetime.now(timezone.utc)):
                            if not (promo.max_uses > 0 and promo.current_uses >= promo.max_uses):
                                # Check per-user usage
                                used = (await s.execute(
                                    select(sa_exists().where(
                                        PromoCodeUsages.promo_id == promo.id,
                                        PromoCodeUsages.user_id == user_id
                                    ))
                                )).scalar()
                                if not used:
                                    # Check item/category binding
                                    if promo.item_id and promo.item_id != goods.id:
                                        pass
                                    elif promo.category_id and promo.category_id != goods.category_id:
                                        pass
                                    else:
                                        promo_valid = True

                    if promo_valid:
                        if promo.discount_type == 'percent':
                            final_price = price * (1 - Decimal(str(promo.discount_value)) / 100)
                        else:
                            final_price = max(price - Decimal(str(promo.discount_value)), Decimal(0))
                        final_price = final_price.quantize(Decimal("0.01"))
                        promos_to_record.append(promo)

                purchases.append({
                    'cart_item': ci,
                    'goods': goods,
                    'item_value': item_value,
                    'price': final_price,
                })
                total_price += final_price

            # Remove invalid cart items
            if items_to_remove:
                await s.execute(
                    sa_delete(CartItems).where(CartItems.id.in_(items_to_remove))
                )

            if not purchases:
                await s.commit()
                return False, "cart_items_unavailable", None

            # 4. Check balance
            if user.balance < total_price:
                await s.rollback()
                return False, "insufficient_funds", None

            # 5. Process each purchase
            results = []
            for p in purchases:
                if not p['item_value'].is_infinity:
                    await s.delete(p['item_value'])

                bought_item = BoughtGoods(
                    name=p['goods'].name,
                    value=p['item_value'].value,
                    price=p['price'],
                    buyer_id=user_id,
                    bought_datetime=datetime.now(timezone.utc),
                    unique_id=uuid4().int >> 65
                )
                s.add(bought_item)
                await s.flush()
                results.append({
                    "item_name": p['goods'].name,
                    "value": p['item_value'].value,
                    "price": float(p['price']),
                    "bought_id": bought_item.id,
                    "unique_id": bought_item.unique_id,
                    "bought_datetime": bought_item.bought_datetime.isoformat(),
                })

            # 6. Record promo usage
            for promo in promos_to_record:
                promo.current_uses += 1
                s.add(PromoCodeUsages(promo_id=promo.id, user_id=user_id))

            # 7. Deduct total
            user.balance -= total_price

            # 8. Clear cart
            await s.execute(
                sa_delete(CartItems).where(CartItems.user_id == user_id)
            )

            await s.commit()

            safe_create_task(invalidate_user_cache(user_id))
            safe_create_task(invalidate_stats_cache())
            # Invalidate cache for all purchased items
            purchased_names = {r["item_name"] for r in results}
            for name in purchased_names:
                safe_create_task(invalidate_item_cache(name))

            return True, "success", results

        except Exception as e:
            await s.rollback()
            await log_audit(
                "cart_checkout_failed",
                level="WARNING",
                user_id=user_id,
                details=str(e),
            )
            return False, "transaction_error", None


async def admin_balance_change(telegram_id: int, amount: Decimal) -> tuple[bool, str]:
    """
    Atomic admin balance change (top-up or deduction) with operation record.
    amount > 0 for top-up, amount < 0 for deduction.
    Returns (success, message).
    Raises ValueError if insufficient funds for deduction.
    """
    async with Database().session() as s:
        try:
            user = (await s.execute(
                select(User).where(User.telegram_id == telegram_id).with_for_update()
            )).scalars().one_or_none()

            if not user:
                await s.rollback()
                return False, "user_not_found"

            if amount < 0 and user.balance < abs(amount):
                await s.rollback()
                raise ValueError("insufficient_funds")

            user.balance += amount

            operation = Operations(
                user_id=telegram_id,
                operation_value=amount,
                operation_time=datetime.now(timezone.utc)
            )
            s.add(operation)

            await s.commit()

            safe_create_task(invalidate_user_cache(telegram_id))
            safe_create_task(invalidate_stats_cache())

            return True, "success"

        except ValueError:
            raise

        except Exception as e:
            await s.rollback()
            await log_audit(
                "admin_balance_change_failed",
                level="WARNING",
                user_id=telegram_id,
                resource_type="User",
                details=f"amount={amount}, error={e}",
            )
            return False, "balance_change_error"


async def redeem_balance_promo(code: str, user_id: int) -> tuple[bool, str, Decimal | None]:
    """
    Redeem a balance-type promo code: add discount_value to user balance.
    Returns (success, error_key_or_empty, amount_added).
    """
    async with Database().session() as s:
        try:
            user = (await s.execute(
                select(User).where(User.telegram_id == user_id).with_for_update()
            )).scalars().one_or_none()
            if not user:
                await s.rollback()
                return False, "promo.not_found", None

            promo = (await s.execute(
                select(PromoCodes).where(PromoCodes.code == code.upper()).with_for_update()
            )).scalars().first()

            if not promo:
                await s.rollback()
                return False, "promo.not_found", None
            if not promo.is_active:
                await s.rollback()
                return False, "promo.inactive", None
            if promo.discount_type != "balance":
                await s.rollback()
                return False, "promo.not_balance_type", None
            if promo.expires_at and promo.expires_at < datetime.now(timezone.utc):
                await s.rollback()
                return False, "promo.expired", None
            if promo.max_uses > 0 and promo.current_uses >= promo.max_uses:
                await s.rollback()
                return False, "promo.max_uses_reached", None

            used = (await s.execute(
                select(sa_exists_top().where(
                    PromoCodeUsages.promo_id == promo.id,
                    PromoCodeUsages.user_id == user_id
                ))
            )).scalar()
            if used:
                await s.rollback()
                return False, "promo.already_used", None

            amount = Decimal(str(promo.discount_value))
            user.balance += amount
            promo.current_uses += 1
            s.add(PromoCodeUsages(promo_id=promo.id, user_id=user_id))
            s.add(Operations(
                user_id=user_id,
                operation_value=amount,
                operation_time=datetime.now(timezone.utc),
            ))

            await s.commit()
            safe_create_task(invalidate_user_cache(user_id))
            safe_create_task(invalidate_stats_cache())
            return True, "", amount

        except Exception as e:
            await s.rollback()
            await log_audit(
                "promo_redeem_failed",
                level="WARNING",
                user_id=user_id,
                resource_type="PromoCode",
                resource_id=code,
                details=str(e),
            )
            return False, "errors.something_wrong", None

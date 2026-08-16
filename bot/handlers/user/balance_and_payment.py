import json
import uuid
from decimal import Decimal, ROUND_HALF_UP

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, PreCheckoutQuery, SuccessfulPayment, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.enums.chat_type import ChatType
from aiogram.enums import ChatAction
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from sqlalchemy import select, update

from bot.database.methods import (
    get_user_referral, buy_item_transaction, process_payment_with_referral,
    create_pending_payment, get_item_info_cached,
)
from bot.database.methods.transactions import (
    ipn_claim_and_credit_topup,
    process_sepay_item_payment,
)
from bot.keyboards import back, payment_menu, close, get_payment_choice, sepay_menu, sepay_confirm_menu, \
    simple_buttons, direct_purchase_choice
from bot.logger_mesh import logger
from bot.database.methods.audit import log_audit
from bot.misc import EnvKeys, ItemPurchaseRequest, validate_telegram_id, validate_money_amount, PaymentRequest, \
    sanitize_html
from bot.handlers.other import _any_payment_method_enabled, is_safe_item_name
from bot.misc.metrics import get_metrics
from bot.misc.services import CryptoPayAPI, CryptoPayAPIError, send_stars_invoice, send_fiat_invoice, \
    is_sepay_configured, convert_balance_amount_to_vnd, build_sepay_transfer_content, \
    build_vietqr_url, fetch_qr_image, send_chat_action
from bot.misc.services.payment import _minor_units_for
from bot.filters import ValidAmountFilter
from bot.i18n import localize, localize_for
from bot.i18n.store import get_user_locale
from bot.states import BalanceStates
from bot.database import Database
from bot.database.models import Payments
from bot.misc.direct_purchase_store import (
    get_direct_purchase_intent,
    set_direct_purchase_intent,
    delete_direct_purchase_intent,
)
from bot.database.methods.read import check_value, select_item_values_amount_cached

router = Router()


async def _notify_referrer_bonus(bot, user_id: int, amount: int, payer_name: str, payer_id: int):
    """Send referral bonus notification to the referrer if applicable."""
    referral_id = await get_user_referral(user_id)
    if not referral_id or not EnvKeys.REFERRAL_PERCENT:
        return
    try:
        bonus = int(Decimal(EnvKeys.REFERRAL_PERCENT) / Decimal(100) * Decimal(amount))
        if bonus > 0:
            await bot.send_message(
                referral_id,
                localize('payments.referral.bonus',
                         amount=bonus, name=payer_name,
                         id=payer_id, currency=EnvKeys.PAY_CURRENCY),
                reply_markup=close()
            )
    except (TelegramBadRequest, TelegramForbiddenError) as e:
        logger.error(f"Failed to send referral notification to user {referral_id}: {e}")


def _owner_locale() -> str | None:
    return get_user_locale(EnvKeys.OWNER_ID)


def _transfer_content(external_id: str) -> str:
    return build_sepay_transfer_content(external_id)


async def _get_payment_by_id(payment_id: int) -> Payments | None:
    async with Database().session() as s:
        result = await s.execute(select(Payments).where(Payments.id == payment_id))
        return result.scalars().first()


async def _set_payment_status(payment_id: int, status: str) -> None:
    async with Database().session() as s:
        await s.execute(
            update(Payments).where(Payments.id == payment_id).values(status=status)
        )


def _sepay_bank_name() -> str:
    return EnvKeys.SEPAY_BANK_NAME or EnvKeys.SEPAY_ACCOUNT_NO


def _sepay_account_name_line(locale: str | None = None) -> str:
    if not EnvKeys.SEPAY_ACCOUNT_NAME:
        return ""
    return localize_for(locale, "payments.sepay.account_name_line", account_name=EnvKeys.SEPAY_ACCOUNT_NAME)


def _sepay_context(payment: Payments, locale: str | None = None) -> dict:
    return {
        "amount": payment.amount,
        "currency": payment.currency,
        "amount_vnd": convert_balance_amount_to_vnd(payment.amount),
        "bank_name": _sepay_bank_name(),
        "account_no": EnvKeys.SEPAY_ACCOUNT_NO,
        "account_name": EnvKeys.SEPAY_ACCOUNT_NAME,
        "account_name_line": _sepay_account_name_line(locale),
        "transfer_content": _transfer_content(payment.external_id),
    }


async def _edit_message_content(message, *, text: str, reply_markup):
    if getattr(message, "caption", None):
        await message.edit_caption(caption=text, reply_markup=reply_markup)
    else:
        await message.edit_text(text, reply_markup=reply_markup)


def _extract_sepay_amount(payload: dict) -> Decimal:
    raw_amount = payload.get("transferAmount")
    if raw_amount is None:
        raw_amount = payload.get("amount")
    if raw_amount is None:
        raw_amount = payload.get("order", {}).get("order_amount")
    return Decimal(str(raw_amount or "0"))


def _extract_sepay_code(payload: dict) -> str:
    for key in ("payment_code", "code"):
        value = payload.get(key)
        if value:
            return str(value).strip()
    content = payload.get("content") or payload.get("description") or payload.get("order", {}).get("order_invoice_number")
    return str(content).strip() if content else ""


def _normalize_sepay_code(code: str) -> str:
    prefix = (EnvKeys.SEPAY_PAYMENT_PREFIX or "SP").strip().upper()
    normalized = (code or "").strip().upper()
    if prefix and normalized.startswith(prefix):
        return normalized[len(prefix):]
    return normalized


async def handle_sepay_ipn(payload: dict, bot) -> None:
    """
    Process a SePay IPN event and finalize the matching pending payment.

    Both branches root on a single atomic DB claim of the ``payments`` row so
    duplicate / concurrent webhooks (Vercel retries) are settled exactly once:
      - provider == "sepay"      → balance top-up credited once (ipn_claim_and_credit_topup)
      - provider == "sepay_item" → item delivered once (process_sepay_item_payment)
    """
    transfer_type = (payload.get("transfer_type") or payload.get("transferType") or "").lower()
    if transfer_type not in {"credit", "in"}:
        await log_audit(
            "sepay_ipn_skip_transfer_type",
            level="WARNING",
            details=f"transfer_type={transfer_type!r}",
        )
        return

    amount = _extract_sepay_amount(payload)
    if amount <= 0:
        await log_audit(
            "sepay_ipn_skip_invalid_amount",
            level="WARNING",
            details=f"transfer_type={transfer_type}, amount={amount}",
        )
        return

    code = _extract_sepay_code(payload)
    if not code:
        await log_audit(
            "sepay_ipn_skip_no_code",
            level="WARNING",
            details=f"transfer_type={transfer_type}, amount={amount}",
        )
        return
    normalized_code = _normalize_sepay_code(code)

    async with Database().session() as s:
        payment = (await s.execute(
            select(Payments).where(
                Payments.provider.in_(("sepay", "sepay_item")),
                Payments.external_id == normalized_code,
                Payments.status.in_(("pending", "submitted")),
            )
        )).scalars().first()

    if not payment:
        await log_audit(
            "sepay_ipn_unmatched",
            level="WARNING",
            resource_type="Payment",
            details=f"code={code}, normalized={normalized_code}, amount={amount}, payload={payload}",
        )
        return

    expected_amount = Decimal(str(payment.amount))
    if amount != expected_amount:
        await log_audit(
            "sepay_ipn_amount_mismatch",
            level="WARNING",
            user_id=payment.user_id,
            resource_type="Payment",
            resource_id=str(payment.id),
            details=f"expected={expected_amount}, got={amount}, code={code}",
        )
        return

    if payment.provider == "sepay":
        success, claim_status = await ipn_claim_and_credit_topup(
            payment=payment,
            amount=expected_amount,
            referral_percent=EnvKeys.REFERRAL_PERCENT,
        )
        if not success:
            await log_audit(
                "sepay_ipn_process_failed",
                level="WARNING",
                user_id=payment.user_id,
                resource_type="Payment",
                resource_id=str(payment.id),
                details=f"provider={payment.provider}, status={claim_status}",
            )
            return

        amount_int = int(expected_amount.quantize(Decimal("1."), rounding=ROUND_HALF_UP))
        try:
            user_info = await bot.get_chat(payment.user_id)
            payer_name = user_info.full_name or user_info.first_name
        except Exception:
            payer_name = str(payment.user_id)

        await _notify_referrer_bonus(bot, payment.user_id, amount_int, payer_name, payment.user_id)

        try:
            user_locale = get_user_locale(payment.user_id)
            await bot.send_message(
                payment.user_id,
                localize_for(
                    user_locale,
                    "payments.sepay.approved",
                    amount=payment.amount,
                    currency=payment.currency,
                ),
                reply_markup=simple_buttons([(localize_for(user_locale, "btn.back"), "profile")]),
            )
        except Exception as e:
            logger.error(f"Failed to notify user {payment.user_id} about approved SePay payment: {e}")

        return

    intent = await get_direct_purchase_intent(payment.id)
    if not intent:
        # Redis intent expired or lost: the payment row carries the delivery hints
        # that the direct-purchase flow attached locally.
        intent = {"item_name": getattr(payment, "item_name", None),
                  "promo_code": getattr(payment, "promo_code", None)}
    if not intent or not intent.get("item_name"):
        await log_audit(
            "sepay_ipn_no_intent",
            level="WARNING",
            user_id=payment.user_id,
            resource_type="Payment",
            resource_id=str(payment.id),
            details="sepay_item webhook without a direct-purchase intent",
        )
        return

    item_name = intent.get("item_name")
    if not item_name:
        return

    status, purchase_message, purchase_data = await process_sepay_item_payment(
        payment=payment,
        amount=expected_amount,
        item_name=item_name,
        promo_code=intent.get("promo_code"),
    )

    if status == "delivered":
        await _send_direct_purchase_receipt(bot, payment.user_id, purchase_data)
        await delete_direct_purchase_intent(payment.id)
        await log_audit(
            "sepay_ipn_delivered",
            level="INFO",
            user_id=payment.user_id,
            resource_type="Payment",
            resource_id=str(payment.id),
            details=f"item={item_name}, unique_id={purchase_data.get('unique_id')}",
        )
    elif status == "refunded":
        try:
            user_locale = get_user_locale(payment.user_id)
            await bot.send_message(
                payment.user_id,
                localize_for(
                    user_locale,
                    "shop.direct_purchase.approved_balance_only",
                    reason=purchase_message,
                    amount=payment.amount,
                    currency=payment.currency,
                ),
                reply_markup=simple_buttons([(localize_for(user_locale, "btn.back"), "profile")]),
            )
        except Exception as e:
            logger.error(f"Failed to notify user {payment.user_id} about SePay direct purchase fallback: {e}")
        await delete_direct_purchase_intent(payment.id)
    elif status == "already_done":
        logger.info(f"SePay IPN retry for payment {payment.id}: already processed, skipped")
    else:
        await log_audit(
            "sepay_ipn_process_failed",
            level="WARNING",
            user_id=payment.user_id,
            resource_type="Payment",
            resource_id=str(payment.id),
            details=f"provider={payment.provider}, status={status}, msg={purchase_message}",
        )


def _price_with_promo(raw_price: Decimal, state_data: dict) -> Decimal:
    applied_promo = state_data.get("applied_promo")
    if not applied_promo:
        return raw_price.quantize(Decimal("0.01"))

    promo_data = state_data.get("applied_promo_data", {})
    if promo_data.get("discount_type") == "percent":
        discount = raw_price * Decimal(str(promo_data.get("discount_value", 0))) / Decimal(100)
    else:
        discount = min(Decimal(str(promo_data.get("discount_value", 0))), raw_price)
    return (raw_price - discount).quantize(Decimal("0.01"))


async def _create_or_reuse_direct_purchase_payment(
    state: FSMContext, user_id: int, item_name: str, amount: Decimal, promo_code: str | None
) -> Payments:
    data = await state.get_data()
    existing_id = data.get("direct_purchase_payment_id")

    if existing_id:
        payment = await _get_payment_by_id(int(existing_id))
        intent = await get_direct_purchase_intent(int(existing_id))
        if (
            payment
            and payment.user_id == user_id
            and payment.provider == "sepay_item"
            and payment.status in {"pending", "submitted"}
            and intent
            and intent.get("item_name") == item_name
            and intent.get("promo_code") == promo_code
            and Decimal(str(payment.amount)) == amount
        ):
            return payment

    payment_id = await create_pending_payment(
        provider="sepay_item",
        external_id=uuid.uuid4().hex[:10].upper(),
        user_id=user_id,
        amount=float(amount),
        currency=EnvKeys.PAY_CURRENCY,
        item_name=item_name,
        promo_code=promo_code,
    )
    await set_direct_purchase_intent(payment_id, item_name=item_name, promo_code=promo_code)
    await state.update_data(
        direct_purchase_payment_id=payment_id,
        direct_purchase_item=item_name,
        direct_purchase_promo=promo_code,
    )
    payment = await _get_payment_by_id(payment_id)
    return payment


async def _send_direct_purchase_receipt(bot, user_id: int, purchase_data: dict):
    try:
        user_info = await bot.get_chat(user_id)
    except (TelegramBadRequest, TelegramForbiddenError):
        user_info = None

    username = (
        getattr(user_info, "username", None)
        or getattr(user_info, "first_name", None)
        or str(user_id)
    )

    buttons = [
        (f"📦 {purchase_data['item_name']}", f"bought-item:{purchase_data['bought_id']}:back_to_menu"),
        (localize_for(get_user_locale(user_id), "btn.back"), "back_to_menu"),
    ]
    await bot.send_message(
        user_id,
        localize_for(
            get_user_locale(user_id),
            "shop.purchase.receipt",
            item_name=purchase_data["item_name"],
            price=purchase_data["price"],
            unique_id=purchase_data["unique_id"],
            datetime=purchase_data["bought_datetime"],
            username=username,
            user_id=user_id,
            value=sanitize_html(purchase_data["value"]),
            currency=EnvKeys.PAY_CURRENCY,
        ),
        parse_mode="HTML",
        reply_markup=simple_buttons(buttons),
    )


@router.callback_query(F.data == "replenish_balance")
async def replenish_balance_callback_handler(call: CallbackQuery, state: FSMContext):
    """Ask user for the amount if at least one payment method is enabled."""
    await _ask_replenish_balance(call, state)


@router.message(Command("balance"))
async def balance_command_handler(message: Message, state: FSMContext):
    """Open the balance/refill screen from the /balance command."""
    if message.chat.type != ChatType.PRIVATE:
        return
    await state.clear()
    await _ask_replenish_balance(message, state)
    try:
        await message.delete()
    except TelegramBadRequest:
        pass


async def _ask_replenish_balance(target, state: FSMContext):
    """Ask user for the amount if at least one payment method is enabled.
    `target` can be CallbackQuery or Message."""
    if not _any_payment_method_enabled():
        if hasattr(target, 'message'):
            await target.answer(localize("payments.not_configured"), show_alert=True)
        else:
            await target.answer(localize("payments.not_configured"), reply_markup=back('back_to_menu'))
        return

    text = localize("payments.replenish_prompt", currency=EnvKeys.PAY_CURRENCY)
    if hasattr(target, 'message'):
        await target.message.edit_text(text, reply_markup=back('profile'))
    else:
        await target.answer(text, reply_markup=back('profile'))
    await state.set_state(BalanceStates.waiting_amount)


@router.message(BalanceStates.waiting_amount, ValidAmountFilter())
async def replenish_balance_amount(message: Message, state: FSMContext):
    """Store amount and show payment methods."""
    try:
        # Validate amount using Pydantic
        amount = validate_money_amount(
            message.text,
            min_amount=Decimal(EnvKeys.MIN_AMOUNT),
            max_amount=Decimal(EnvKeys.MAX_AMOUNT)
        )

        await state.update_data(amount=int(amount))

        await message.answer(
            localize("payments.method_choose"),
            reply_markup=get_payment_choice()
        )
        await state.set_state(BalanceStates.waiting_payment)

    except ValueError as e:
        await message.answer(
            localize("payments.replenish_invalid",
                     min_amount=EnvKeys.MIN_AMOUNT,
                     max_amount=EnvKeys.MAX_AMOUNT,
                     currency=EnvKeys.PAY_CURRENCY),
            reply_markup=back('replenish_balance')
        )


@router.message(BalanceStates.waiting_amount)
async def invalid_amount(message: Message, state: FSMContext):
    """
    Tell user the amount is invalid.
    """
    await message.answer(
        localize("payments.replenish_invalid",
                 min_amount=EnvKeys.MIN_AMOUNT,
                 max_amount=EnvKeys.MAX_AMOUNT,
                 currency=EnvKeys.PAY_CURRENCY),
        reply_markup=back('replenish_balance')
    )


@router.callback_query(
    BalanceStates.waiting_payment,
    F.data.in_(["pay_sepay", "pay_usdt", "pay_cryptopay", "pay_stars", "pay_fiat"])
)
async def process_replenish_balance(call: CallbackQuery, state: FSMContext):
    """Create an invoice for the chosen payment method."""
    data = await state.get_data()
    amount = data.get('amount')

    if amount is None:
        await call.answer(localize("payments.session_expired"), show_alert=True)
        await call.message.edit_text(localize("menu.title"), reply_markup=back('back_to_menu'))
        await state.clear()
        return

    # Map callback data to provider
    provider_map = {
        "pay_sepay": "sepay",
        "pay_usdt": "usdt",
        "pay_cryptopay": "cryptopay",
        "pay_stars": "stars",
        "pay_fiat": "fiat"
    }
    provider = provider_map.get(call.data)

    try:
        # Validate payment request
        payment_request = PaymentRequest(
            amount=Decimal(amount),
            currency=EnvKeys.PAY_CURRENCY,
            provider=provider
        )

        amount_dec = payment_request.amount
        ttl_seconds = int(EnvKeys.PAYMENT_TIME)

        if call.data == "pay_sepay":
            if not is_sepay_configured():
                await call.answer(localize("payments.sepay.not_configured"), show_alert=True)
                return

            external_id = uuid.uuid4().hex[:10].upper()
            payment_id = await create_pending_payment(
                provider=provider,
                external_id=external_id,
                user_id=call.from_user.id,
                amount=int(amount_dec),
                currency=payment_request.currency,
            )

            await state.update_data(payment_id=payment_id, payment_type=provider)

            await call.message.edit_text(
                localize("payments.sepay.instructions", **_sepay_context(await _get_payment_by_id(payment_id))),
                reply_markup=sepay_menu(payment_id),
            )

        elif call.data in {"pay_cryptopay", "pay_usdt"}:
            if not EnvKeys.CRYPTO_PAY_TOKEN:
                await call.answer(localize("payments.not_configured"), show_alert=True)
                return

            try:
                crypto = CryptoPayAPI()
                crypto_asset = payment_request.currency.upper() if payment_request.currency.upper() in {"USDT", "TON", "BTC", "ETH", "LTC", "BNB", "TRX", "USDC"} else None
                accepted_assets = "USDT" if call.data == "pay_usdt" else "TON,USDT,BTC,ETH"
                invoice = await crypto.create_invoice(
                    amount=float(amount_dec),
                    expires_in=ttl_seconds,
                    currency=payment_request.currency,
                    accepted_assets=accepted_assets,
                    asset=crypto_asset,
                    payload=str(call.from_user.id),
                )
            except CryptoPayAPIError as e:
                await log_audit("cryptopay_error", level="ERROR", user_id=call.from_user.id, resource_type="Payment", details=f"[{e.code}] {e.name}")
                await call.answer(localize("payments.crypto.api_error", error=e.name), show_alert=True)
                return
            except Exception as e:
                await log_audit("cryptopay_invoice_fail", level="ERROR", user_id=call.from_user.id, resource_type="Payment", details=str(e))
                await call.answer(localize("payments.crypto.create_fail", error=str(e)), show_alert=True)
                return

            pay_url = invoice.get("mini_app_invoice_url")
            invoice_id = invoice.get("invoice_id")

            await create_pending_payment(
                provider=provider,
                external_id=str(invoice_id),
                user_id=call.from_user.id,
                amount=int(amount_dec),
                currency=payment_request.currency,
            )

            await state.update_data(invoice_id=invoice_id, payment_type=provider)

            await call.message.edit_text(
                localize("payments.invoice.summary",
                         amount=int(amount_dec),
                         minutes=int(ttl_seconds / 60),
                         button=localize("btn.check_payment"),
                         currency=payment_request.currency),
                reply_markup=payment_menu(pay_url)
            )

        elif call.data == "pay_stars":
            if EnvKeys.STARS_PER_VALUE > 0:
                try:
                    await send_stars_invoice(
                        bot=call.message.bot,
                        chat_id=call.from_user.id,
                        amount=int(amount_dec),
                    )
                except Exception as e:
                    await log_audit("stars_invoice_fail", level="ERROR", user_id=call.from_user.id, resource_type="Payment", details=str(e))
                    await call.answer(localize("payments.stars.create_fail", error=str(e)), show_alert=True)
                    return
                await state.clear()
            else:
                await call.answer(localize("payments.not_configured"), show_alert=True)
                return

        elif call.data == "pay_fiat":
            if not EnvKeys.TELEGRAM_PROVIDER_TOKEN:
                await call.answer(localize("payments.not_configured"), show_alert=True)
                return

            try:
                await send_fiat_invoice(
                    bot=call.message.bot,
                    chat_id=call.from_user.id,
                    amount=int(amount_dec),
                )
            except Exception as e:
                await log_audit("fiat_invoice_fail", level="ERROR", user_id=call.from_user.id, resource_type="Payment", details=str(e))
                await call.answer(localize("payments.fiat.create_fail", error=str(e)), show_alert=True)
                return
            await state.clear()

    except Exception as e:
        logger.error(f"Payment processing error: {e}")
        await call.answer(localize("errors.something_wrong"), show_alert=True)


@router.callback_query(F.data.startswith("sepay_show_account:"))
async def sepay_show_account_callback_handler(call: CallbackQuery):
    """Show the SePay transfer details for an existing payment."""
    try:
        payment_id = int(call.data.split(":", maxsplit=1)[1])
    except (IndexError, ValueError):
        await call.answer(localize("errors.invalid_data"), show_alert=True)
        return

    payment = await _get_payment_by_id(payment_id)
    if not payment or payment.provider not in {"sepay", "sepay_item"} or payment.user_id != call.from_user.id:
        await call.answer(localize("errors.invalid_data"), show_alert=True)
        return

    await call.message.answer(
        localize("payments.sepay.instructions", **_sepay_context(payment)),
        reply_markup=sepay_menu(payment_id),
    )
    await call.answer()


@router.callback_query(F.data.startswith("sepay_done:"))
async def sepay_done_callback_handler(call: CallbackQuery, state: FSMContext):
    """Mark a SePay payment as submitted so webhook matching can finalize it."""
    try:
        payment_id = int(call.data.split(":", maxsplit=1)[1])
    except (IndexError, ValueError):
        await call.answer(localize("errors.invalid_data"), show_alert=True)
        return

    payment = await _get_payment_by_id(payment_id)
    if not payment or payment.provider != "sepay" or payment.user_id != call.from_user.id:
        await call.answer(localize("errors.invalid_data"), show_alert=True)
        return

    if payment.status == "succeeded":
        await call.answer(localize("payments.already_processed"), show_alert=True)
        return

    await _set_payment_status(payment_id, "submitted")

    await state.clear()
    await _edit_message_content(
        call.message,
        text=localize(
            "payments.sepay.submitted",
            amount=payment.amount,
            currency=payment.currency,
        ),
        reply_markup=back("profile"),
    )
    await call.answer(localize("payments.sepay.submitted_alert"))


@router.callback_query(F.data.in_(["buy_direct_account"]))
async def buy_direct_sepay_callback_handler(call: CallbackQuery, state: FSMContext):
    """Create or reuse a direct-purchase SePay transfer request for the current item."""
    data = await state.get_data()
    item_name = data.get("csrf_item")
    if not item_name:
        await call.answer(localize("shop.item.not_found"), show_alert=True)
        return
    if not (await check_value(item_name)) and await select_item_values_amount_cached(item_name) <= 0:
        await call.answer(localize("shop.out_of_stock"), show_alert=True)
        return

    item_info_data = await get_item_info_cached(item_name)
    if not item_info_data:
        await call.answer(localize("shop.item.not_found"), show_alert=True)
        return

    price = _price_with_promo(Decimal(str(item_info_data["price"])), data)
    payment = await _create_or_reuse_direct_purchase_payment(
        state,
        call.from_user.id,
        item_name,
        price,
        data.get("applied_promo"),
    )
    context = {
        "item_name": item_name,
        **_sepay_context(payment),
    }

    # Acknowledge now so Telegram stops the loading spinner before the
    # potentially slower VietQR fetch / photo upload below.
    await call.answer()

    amount_vnd = int(context["amount_vnd"])
    transfer_content = context["transfer_content"]

    # Signal "uploading a photo" while we build + fetch the QR image.
    await send_chat_action(call.bot, call.message.chat.id, ChatAction.UPLOAD_PHOTO)

    qr_bytes = None
    try:
        qr_url = build_vietqr_url(
            bank=EnvKeys.SEPAY_BANK_NAME,
            account_no=EnvKeys.SEPAY_ACCOUNT_NO,
            amount_vnd=amount_vnd,
            content=transfer_content,
            holder=EnvKeys.SEPAY_ACCOUNT_NAME,
        )
        qr_bytes = await fetch_qr_image(qr_url)
    except Exception:
        logger.exception("QR generation failed for payment %s", payment.id)

    if qr_bytes:
        try:
            await call.message.answer_photo(
                BufferedInputFile(qr_bytes, filename="sepay_qr.png"),
                caption=localize("shop.direct_purchase.qr_caption", **context),
                reply_markup=sepay_confirm_menu(payment.id, back_cb="back_to_item"),
            )
        except Exception:
            logger.exception("Failed to send QR photo for payment %s", payment.id)
            qr_bytes = None

    if not qr_bytes:
        # Fallback to a plain-text message so the payment is never lost.
        await call.message.answer(
            localize("shop.direct_purchase.instructions", **context),
            reply_markup=sepay_confirm_menu(payment.id, back_cb="back_to_item"),
        )


@router.callback_query(F.data == "check")
async def checking_payment(call: CallbackQuery, state: FSMContext):
    """
    Check CryptoPay invoice status and credit balance if paid.
    """
    user_id = call.from_user.id
    data = await state.get_data()
    payment_type = data.get("payment_type")

    if not payment_type:
        await call.answer(localize("payments.no_active_invoice"), show_alert=True)
        return

    if payment_type in {"cryptopay", "usdt"}:
        invoice_id = data.get("invoice_id")
        if not invoice_id:
            await call.answer(localize("payments.invoice_not_found"), show_alert=True)
            await state.clear()
            return

        try:
            crypto = CryptoPayAPI()
            info = await crypto.get_invoice(invoice_id)
        except CryptoPayAPIError as e:
            await log_audit("cryptopay_check_error", level="ERROR", user_id=user_id, resource_type="Payment", details=f"[{e.code}] {e.name}")
            await call.answer(localize("payments.crypto.api_error", error=e.name), show_alert=True)
            return
        except Exception as e:
            await log_audit("cryptopay_get_fail", level="ERROR", user_id=user_id, resource_type="Payment", details=str(e))
            await call.answer(localize("payments.crypto.check_fail", error=str(e)), show_alert=True)
            return

        status = info.get("status")
        if status == "paid":
            balance_amount = int(Decimal(str(info.get("amount", "0"))).quantize(Decimal("1.")))

            # Use transactional payment processing
            success, error_msg = await process_payment_with_referral(
                user_id=user_id,
                amount=Decimal(balance_amount),
                provider=payment_type,
                external_id=str(invoice_id),
                referral_percent=EnvKeys.REFERRAL_PERCENT
            )

            if not success:
                if error_msg == "already_processed":
                    await call.answer(localize("payments.already_processed"), show_alert=True)
                else:
                    await call.answer(localize("errors.general_error", e=error_msg), show_alert=True)
                return

            metrics = get_metrics()
            if metrics:
                metrics.track_event("payment", user_id, {"amount": balance_amount, "provider": payment_type})

            # Send a notification to the referrer
            await _notify_referrer_bonus(call.bot, user_id, balance_amount, call.from_user.first_name, call.from_user.id)

            await call.message.edit_text(
                localize("payments.topped_simple",
                         amount=balance_amount,
                         currency=EnvKeys.PAY_CURRENCY),
                reply_markup=back('profile')
            )
            await state.clear()

            # Audit log
            try:
                user_info = await call.bot.get_chat(user_id)
                await log_audit(
                    "balance_replenish",
                    user_id=user_id,
                    resource_type="Payment",
                    details=f"name={user_info.first_name}, amount={balance_amount} {EnvKeys.PAY_CURRENCY}, provider={payment_type}",
                )
            except (TelegramBadRequest, TelegramForbiddenError) as e:
                await log_audit("balance_replenish", level="ERROR", user_id=user_id, resource_type="Payment", details=f"log_failed: {e}")

        elif status == "active":
            await call.answer(localize("payments.not_paid_yet"))
        else:
            await call.answer(localize("payments.expired"), show_alert=True)


@router.pre_checkout_query()
async def pre_checkout_handler(query: PreCheckoutQuery):
    """Validate the payment before Telegram processes it."""
    try:
        payload = json.loads(query.invoice_payload or "{}")
    except Exception:
        await query.answer(ok=False, error_message="Invalid payload")
        return

    amount = int(payload.get("amount", 0) or payload.get("amount_rub", 0))
    if amount <= 0:
        await query.answer(ok=False, error_message="Invalid amount")
        return

    if amount > int(EnvKeys.MAX_AMOUNT):
        await query.answer(ok=False, error_message="Amount exceeds maximum")
        return

    await query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    """
    Handle successful payment:
    - XTR (Stars): total_amount is ⭐. take CURRENCY from payload (amount) or convert ⭐ → CURRENCY.
    - Fiat: total_amount is minor units; divide by 100 (or 1 for JPY/KRW).
    """
    sp: SuccessfulPayment = message.successful_payment
    user_id = message.from_user.id

    payload = {}
    try:
        if sp.invoice_payload:
            payload = json.loads(sp.invoice_payload)
    except Exception:
        payload = {}

    amount = 0

    if sp.currency == "XTR":
        # Stars
        if "amount" in payload:
            amount = int(payload["amount"])
        else:
            amount = int(
                (Decimal(int(sp.total_amount)) / Decimal(str(EnvKeys.STARS_PER_VALUE)))
                .to_integral_value(rounding=ROUND_HALF_UP)
            )
    else:
        # Fiat
        currency = sp.currency.upper()
        multiplier = _minor_units_for(currency)
        amount = int(Decimal(sp.total_amount) / Decimal(multiplier))

    if amount <= 0:
        await message.answer(localize("payments.unable_determine_amount"), reply_markup=close())
        return

    # Idempotence
    provider = "telegram" if sp.currency != "XTR" else "stars"
    external_id = sp.telegram_payment_charge_id or sp.provider_payment_charge_id or f"{provider}:{user_id}:{uuid.uuid4().hex}"

    success, error_msg = await process_payment_with_referral(
        user_id=user_id,
        amount=Decimal(amount),
        provider=provider,
        external_id=external_id,
        referral_percent=EnvKeys.REFERRAL_PERCENT
    )

    if not success:
        if error_msg == "already_processed":
            await message.answer(localize("payments.already_processed"), reply_markup=close())
        else:
            await message.answer(localize("payments.processing_error"), reply_markup=close())
        return

    # Sending notification to referrer
    await _notify_referrer_bonus(message.bot, user_id, amount, message.from_user.first_name, message.from_user.id)

    metrics = get_metrics()
    if metrics:
        metrics.track_event("payment", user_id, {"amount": amount, "provider": provider})

    suffix = localize("payments.success_suffix.stars") if sp.currency == "XTR" else localize(
        "payments.success_suffix.tg")
    await message.answer(
        localize('payments.topped_with_suffix', amount=amount, suffix=suffix, currency=EnvKeys.PAY_CURRENCY),
        reply_markup=back('profile')
    )

    # audit log
    try:
        user_info = await message.bot.get_chat(user_id)
        await log_audit(
            "balance_replenish",
            user_id=user_id,
            resource_type="Payment",
            details=f"name={user_info.first_name}, amount={amount} {EnvKeys.PAY_CURRENCY}, provider={suffix}",
        )
    except (TelegramBadRequest, TelegramForbiddenError) as e:
        await log_audit("balance_replenish", level="ERROR", user_id=user_id, resource_type="Payment", details=f"log_failed: {e}")


@router.callback_query(F.data == "buy")
async def buy_item_callback_handler(call: CallbackQuery, state: FSMContext):
    """Show direct-purchase options after the user taps Buy."""
    try:
        data = await state.get_data()
        raw_item_name = data.get('csrf_item')

        if not raw_item_name:
            await call.answer(localize("middleware.security.invalid_csrf"), show_alert=True)
            return
        if not is_sepay_configured():
            await call.answer(localize("payments.sepay.not_configured"), show_alert=True)
            return
        if not (await check_value(raw_item_name)) and await select_item_values_amount_cached(raw_item_name) <= 0:
            await call.answer(localize("shop.out_of_stock"), show_alert=True)
            return
        item_info_data = await get_item_info_cached(raw_item_name)
        if not item_info_data:
            await call.answer(localize("shop.item.not_found"), show_alert=True)
            return

        price = _price_with_promo(Decimal(str(item_info_data["price"])), data)
        await call.message.edit_text(
            localize(
                "shop.direct_purchase.choose_option",
                item_name=raw_item_name,
                amount=price,
                currency=EnvKeys.PAY_CURRENCY,
                bank_name=_sepay_bank_name(),
                account_no=EnvKeys.SEPAY_ACCOUNT_NO,
            ),
            reply_markup=direct_purchase_choice("back_to_item"),
        )
        await call.answer()

    except Exception as e:
        logger.error(f"Critical error in purchase handler: {e}")
        await call.answer(
            localize("errors.something_wrong"),
            show_alert=True
        )

EN_TRANSLATIONS: dict[str, str] = {
    "btn.shop": "🛍️ Buy",
    "btn.rules": "📜 Rules",
    "btn.profile": "👤 Profile",
    "btn.support": "🆘 Support",
    "btn.channel": "ℹ News Channel",
    "btn.admin_menu": "🎛 Admin Panel",
    "btn.back": "⬅️ Back",
    "btn.to_menu": "🏠 Menu",
    "btn.close": "✖ Close",
    "btn.buy": "🛒 Buy",
    "btn.out_of_stock": "❌ Out of Stock",
    "btn.yes": "✅ Yes",
    "btn.no": "❌ No",
    "btn.check": "🔄 Check",
    "btn.check_subscription": "🔄 Check Subscription",
    "btn.pay": "💳 Pay",
    "btn.check_payment": "🔄 Check Payment",
    "btn.pay.usdt": "💵 USDT",
    "btn.pay.crypto": "💎 CryptoPay",
    "btn.pay.stars": "⭐ Telegram Stars",
    "btn.pay.tg": "💸 Telegram Payments",
    "btn.replenish": "💳 Top Up Balance",
    "btn.referral": "🎲 Referral System",
    "btn.purchased": "🎁 Purchased Items",
    "btn.view_referrals": "👥 My Referrals",
    "btn.view_earnings": "💰 My Earnings",
    "btn.back_to_referral": "⬅️ Back to Referral",
    "btn.apply_promo": "🏷 Apply Promo Code",
    "btn.remove_promo": "❌ Remove Promo Code",
    "btn.redeem_promo": "🏷 Redeem Promo Code",
    "btn.cart": "🛒 Cart ({count})",
    "btn.cart_empty": "🛒 Cart",
    "btn.add_to_cart": "🛒 Add to Cart",
    "btn.cart_checkout": "💳 Checkout",
    "btn.cart_clear": "🗑 Clear Cart",
    "btn.operation_history": "📋 Operation History",
    "btn.leave_review": "⭐ Leave Review",
    "btn.view_reviews": "📝 Reviews ({count})",
    "btn.skip_review_text": "⏭ Skip Text",
    "btn.add_values_finish": "Add Listed Goods",
    "menu.title": (
        "📌 Quick Start:\n"
        "1. Tap \"🛍️ Buy\".\n"
        "2. Open the product you want.\n"
        "3. Tap \"🛒 Buy\" on the product page.\n"
        "4. Choose direct transfer or bank account.\n"
        "5. Transfer the exact amount shown by the bot.\n"
        "6. Wait for delivery after payment is confirmed.\n\n"
        "📌 Please choose a menu:"
    ),
    "profile.caption": "👤 <b>Profile</b> — <a href='tg://user?id={id}'>{name}</a>",
    "rules.not_set": "❌ Rules have not been added yet",
    "btn.language": "🌐 Language",
    "language.title": "🌐 Choose a language",
    "language.changed": "✅ Language changed: {locale}",
    "language.name.vi": "Tiếng Việt",
    "language.name.en": "English",
    "commands.start": "🚀 Start bot",
    "commands.shop": "🛍️ Shop",
    "commands.profile": "👤 My profile",
    "commands.orders": "📦 My orders",
    "commands.balance": "💰 Balance & Top up",
    "commands.rules": "📜 Rules",
    "commands.help": "❓ Help",
    "help.text": (
        "📘 <b>User Guide</b>\n\n"
        "How to buy:\n"
        "1. Open \"🛍️ Buy\".\n"
        "2. Choose a product.\n"
        "3. Tap \"🛒 Buy\".\n"
        "4. Choose direct transfer or bank account.\n"
        "5. Transfer the exact amount shown.\n"
        "6. Wait for delivery.\n\n"
        "Useful commands:\n"
        "/start — start the bot\n"
        "/shop — open the shop\n"
        "/profile — view your profile\n"
        "/orders — view your purchased items\n"
        "/balance — view balance and top up\n"
        "/rules — show the rules\n"
        "/help — open this guide\n\n"
        "🌐 Switch language with the 🇻🇳 Tiếng Việt / 🇬🇧 English button in the main menu."
    ),
    "subscribe.prompt": "Please subscribe to the news channel first",
    "subscribe.open_channel": "Open Channel",
    "profile.referral_id": "👤 <b>Referrer</b> — <code>{id}</code>",
    "profile.id": "🆔 <b>ID</b> — <code>{id}</code>",
    "profile.balance": "💳 <b>Balance</b> — <code>{amount}</code> {currency}",
    "profile.total_topup": "💵 <b>Total Top-ups</b> — <code>{amount}</code> {currency}",
    "profile.purchased_count": "🎁 <b>Purchased Items</b> — {count}",
    "profile.registration_date": "🕢 <b>Registration Date</b> — <code>{dt}</code>",
    "referral.title": "💚 Referral System",
    "referral.link": "🔗 Link: https://t.me/{bot_username}?start={user_id}",
    "referral.count": "Referrals count: {count}",
    "referral.description": (
        "📔 The referral system lets you earn money without investment. "
        "Just share your referral link and you will receive {percent}% from your referrals' top-ups to your bot balance."
    ),
    "referrals.list.title": "👥 Your referrals:",
    "referrals.list.empty": "You don't have active referrals yet",
    "referrals.item.format": "ID: {telegram_id} | Earned: {total_earned} {currency}",
    "referral.earnings.title": "💰 Earnings from referral <code>{telegram_id}</code> (<a href='tg://user?id={telegram_id}'>{name}</a>):",
    "referral.earnings.empty": "No earnings yet from referral <code>{id}</code> (<a href='tg://user?id={id}'>{name}</a>)",
    "referral.earning.format": "{amount} {currency} | {date} | (from {original_amount} {currency})",
    "referral.item.info": (
        "💰 Earning #<code>{id}</code>\n"
        "👤 Referral: <code>{telegram_id}</code> (<a href='tg://user?id={telegram_id}'>{name}</a>)\n"
        "🔢 Amount: {amount} {currency}\n"
        "🕘 Date: <code>{date}</code>\n"
        "💵 From top-up of {original_amount} {currency}"
    ),
    "all.earnings.title": "💰 All your referral earnings:",
    "all.earnings.empty": "You don't have referral earnings yet",
    "all.earning.format": "{amount} {currency} from ID:{referral_id} | {date}",
    "referrals.stats.template": (
        "📊 Referral statistics:\n\n"
        "👥 Active referrals: {active_count}\n"
        "💰 Total earned: {total_earned} {currency}\n"
        "📈 Total referral top-ups: {total_original} {currency}\n"
        "🔢 Earnings count: {earnings_count}"
    ),
    "payments.replenish_prompt": "Enter top-up amount in {currency}:",
    "payments.replenish_invalid": "❌ Invalid amount. Enter a number from {min_amount} to {max_amount} {currency}.",
    "payments.deduct_prompt": "Enter deduction amount in {currency}:",
    "payments.deduct_invalid": "❌ Invalid amount. Enter a number from {min_amount} to {max_amount} {currency}.",
    "payments.method_choose": "Choose a payment method:",
    "payments.not_configured": "❌ Top-ups are not configured",
    "payments.session_expired": "Payment session expired. Please start again.",
    "payments.crypto.create_fail": "❌ Failed to create invoice: {error}",
    "payments.crypto.api_error": "❌ CryptoPay API error: {error}",
    "payments.crypto.check_fail": "❌ Payment check failed: {error}",
    "payments.stars.create_fail": "❌ Failed to create Stars invoice: {error}",
    "payments.fiat.create_fail": "❌ Failed to create invoice: {error}",
    "payments.no_active_invoice": "❌ No active invoices found. Start top-up again.",
    "payments.invoice_not_found": "❌ Invoice not found. Please start again.",
    "payments.not_paid_yet": "⌛ Payment is not completed yet.",
    "payments.expired": "❌ Invoice has expired.",
    "payments.invoice.summary": (
        "💵 Top-up amount: {amount} {currency}.\n"
        "⌛ You have {minutes} minutes to pay.\n"
        "<b>❗ After payment, press '{button}'</b>"
    ),
    "payments.unable_determine_amount": "❌ Failed to determine the paid amount.",
    "payments.topped_simple": "✅ Balance topped up by {amount} {currency}",
    "payments.topped_with_suffix": "✅ Balance topped up by {amount} {currency} ({suffix})",
    "payments.success_suffix.stars": "Telegram Stars",
    "payments.success_suffix.tg": "Telegram Payments",
    "payments.referral.bonus": "✅ You received {amount} {currency} from your referral <a href='tg://user?id={id}'>{name}</a>",
    "payments.invoice.title.topup": "Balance Top-up",
    "payments.invoice.desc.topup.stars": "Top up {amount} {currency} via Telegram Stars",
    "payments.invoice.desc.topup.fiat": "Pay via Telegram Payments (card)",
    "payments.invoice.label.fiat": "Top up {amount} {currency}",
    "payments.invoice.label.stars": "{stars} ⭐",
    "payments.already_processed": "This payment has already been processed ✅",
    "payments.processing_error": "Payment processing error. Please try again later.",
    "shop.categories.title": "🏪 Shop Categories",
    "shop.goods.choose": "🏪 Choose a Product",
    "shop.item.not_found": "Item not found",
    "shop.item.title": "🏪 Item {name}",
    "shop.item.description": "Description: {description}",
    "shop.item.price": "Price — {amount} {currency}",
    "shop.item.price_discounted": "💰 <b>Price</b>: <s>{original}</s> <b>{discounted}</b> {currency} (promo {code})",
    "shop.item.quantity_unlimited": "Quantity — unlimited",
    "shop.item.quantity_left": "Quantity — {count} pcs",
    "shop.insufficient_funds": "❌ Insufficient funds",
    "shop.out_of_stock": "❌ Item is out of stock",
    "shop.purchase.success": "✅ Item purchased. <b>Balance</b>: <i>{balance}</i> {currency}\n\n{value}",
    "shop.purchase.receipt": (
        "✅ Order placed successfully!\n"
        "────────────\n"
        "📃 Item: {item_name}\n"
        "💰 Price: {price} {currency}\n"
        "📦 Qty: 1\n"
        "💡 Order: {unique_id}\n"
        "🕐 Time: {datetime}\n"
        "💲 Total: {price} {currency}\n"
        "👤 Buyer: @{username} ({user_id})\n"
        "────────────\n"
        "🔑 Value:\n<code>{value}</code>"
    ),
    "shop.purchase.processing": "⏳ Processing purchase...",
    "shop.purchase.fail.user_not_found": "❌ User not found in the system",
    "shop.purchase.fail.general": "❌ Purchase error: {message}",
    "purchases.title": "Purchased items:",
    "purchases.pagination.invalid": "Invalid pagination data",
    "purchases.item.not_found": "Purchase not found",
    "purchases.item.name": "<b>🧾 Item</b>: <code>{name}</code>",
    "purchases.item.price": "<b>💵 Price</b>: <code>{amount}</code> {currency}",
    "purchases.item.datetime": "<b>🕒 Purchased at</b>: <code>{dt}</code>",
    "purchases.item.unique_id": "<b>🧾 Unique ID</b>: <code>{uid}</code>",
    "purchases.item.value": "<b>🔑 Value</b>:\n<code>{value}</code>",
    "purchases.item.buyer": "<b>Buyer</b>: <code>{buyer}</code>",
    "cart.title": "🛒 <b>Cart</b>",
    "cart.empty": "Cart is empty.",
    "cart.item": "• {name} — {price} {currency}",
    "cart.total": "\n💰 <b>Total</b>: {total} {currency}",
    "cart.added": "✅ {name} added to cart.",
    "cart.full": "❌ Cart is full (max 10 items).",
    "cart.item_not_found": "❌ Item not found.",
    "cart.removed": "✅ Item removed from cart.",
    "cart.cleared": "✅ Cart cleared.",
    "cart.checkout_confirm": "Checkout {count} item(s) for {total} {currency}?",
    "cart.checkout_success": "✅ Order placed! Bought {count} item(s).\n\n💰 Balance: {balance} {currency}",
    "cart.checkout_receipt": (
        "✅ Order placed!\n"
        "────────────\n"
        "📦 Qty: {count}\n"
        "💲 Total: {total} {currency}\n"
        "👤 Buyer: @{username} ({user_id})\n"
        "🕐 Time: {datetime}\n"
        "────────────\n"
        "Tap an item to view details:"
    ),
    "cart.checkout_fail": "❌ Checkout failed: {reason}",
    "cart.items_unavailable": "Some items are no longer available and were removed from the cart.",
    "history.title": "📋 <b>Operation History</b>",
    "history.empty": "Operation history is empty.",
    "history.topup": "💰 Top-up: +{amount} {currency}",
    "history.purchase": "🛒 Purchase: {amount} {currency}",
    "history.referral": "🎲 Referral bonus: +{amount} {currency}",
    "history.date": "📅 {date}",
    "review.disabled": "Reviews are disabled.",
    "review.prompt_rating": "Rate <b>{name}</b> from 1 to 5:",
    "review.prompt_text": "Write a review (up to 500 chars) or click Skip:",
    "review.created": "✅ Thank you for your review!",
    "review.already_exists": "You already reviewed this item.",
    "review.not_purchased": "You haven't purchased this item.",
    "review.avg_rating": "⭐ Rating: {rating}/5 ({count} reviews)",
    "review.item": "⭐ {rating}/5 — {text}",
    "review.item_no_text": "⭐ {rating}/5",
    "review.list_title": "📝 <b>Reviews for {name}</b>",
    "review.list_empty": "No reviews yet.",
    "promo.not_found": "❌ Promo code not found.",
    "promo.inactive": "❌ Promo code is inactive.",
    "promo.expired": "❌ Promo code has expired.",
    "promo.max_uses_reached": "❌ Promo code usage limit reached.",
    "promo.already_used": "❌ You already used this promo code.",
    "promo.wrong_item": "❌ Promo code is not valid for this item.",
    "promo.wrong_category": "❌ Promo code is not valid for this category.",
    "promo.applied": "✅ Promo code <code>{code}</code> applied! Discount: {discount}",
    "promo.enter_code": "Enter promo code:",
    "promo.removed": "Promo code removed.",
    "promo.not_balance_type": "❌ This promo code is not for balance top-up.",
    "promo.enter_redeem_code": "Enter promo code to redeem:",
    "promo.balance_redeemed": "✅ Promo code <code>{code}</code> redeemed! {amount} {currency} added to your balance.",
    "errors.not_subscribed": "You are not subscribed",
    "errors.something_wrong": "❌ Something went wrong. Please try again.",
    "errors.pagination_invalid": "Invalid pagination data",
    "errors.invalid_data": "❌ Invalid data",
    "errors.id_should_be_number": "❌ ID must be a number.",
    "errors.channel.telegram_not_found": "I can't write to the channel. Add me as a channel admin for uploads @{channel} with permission to post messages.",
    "errors.channel.telegram_forbidden_error": "Channel not found. Check the channel username for uploads @{channel}.",
    "errors.channel.telegram_bad_request": "Failed to send to the upload channel: {e}",
    "errors.general_error": "❌ Error: {e}",
    "middleware.ban": "⏳ You are temporarily blocked. Wait {time} seconds.",
    "middleware.above_limits": "⚠️ Too many requests! You are temporarily blocked.",
    "middleware.waiting": "⏳ Wait {time} seconds before the next action.",
    "middleware.security.session_outdated": "⚠️ Session is outdated. Please start again.",
    "middleware.security.invalid_data": "❌ Invalid data",
    "middleware.security.blocked": "❌ Access blocked",
    "middleware.security.not_admin": "⛔ Insufficient permissions",
    "middleware.security.invalid_csrf": "⚠️ Session expired. Please try again.",
    "maintenance.active": "🔧 The bot is under maintenance. Please try again later.",
    "admin.menu.main": "⛩️ Admin Menu",
    "admin.menu.shop": "🛒 Shop Management",
    "admin.menu.goods": "📦 Item Management",
    "admin.menu.categories": "📂 Category Management",
    "admin.menu.users": "👥 User Management",
    "admin.menu.broadcast": "📝 Broadcast",
    "admin.menu.roles": "🛡 Role Management",
    "admin.menu.promo": "🏷 Promo Codes",
    "admin.menu.rights": "Insufficient permissions",
    "admin.menu.maintenance_on": "🔧 Maintenance: ON",
    "admin.menu.maintenance_off": "🔧 Maintenance: OFF",
    "admin.maintenance.enabled": "✅ Maintenance mode enabled",
    "admin.maintenance.disabled": "✅ Maintenance mode disabled",

    # === Auto product ad ===
    "product_ad.title": "🔥 <b>Featured product</b>",
    "product_ad.name": "📦 <b>{name}</b>",
    "product_ad.description": "📝 {description}",
    "product_ad.price": "💰 Price: {amount} {currency}",
    "product_ad.stock_left": "📦 In stock: {count} pcs",
    "product_ad.stock_unlimited": "📦 Unlimited stock",
    "product_ad.buy_cta": "👇 Tap the button below to open the product and buy it!",
    "product_ad.btn.buy": "🛒 Buy Now",
}
EN_TRANSLATIONS.update({
    "admin.shop.logs.file_label": "{name} log file",
    "admin.goods.add.prompt.category.pick": "Choose a category:",
    "admin.goods.add.category.empty": "No categories yet. Create a category first in category management.",
    "admin.goods.positions.title": "Choose a product to view:",
    "admin.goods.positions.empty": "No products yet. Add a product first.",
    "shop.goods.empty": "No products available yet.",
    "admin.shop.stats.perm.use": "USE",
    "admin.shop.stats.perm.broadcast": "BROADCAST",
    "admin.shop.stats.perm.settings": "SETTINGS",
    "admin.shop.stats.perm.users": "USERS",
    "admin.shop.stats.perm.catalog": "CATALOG",
    "admin.shop.stats.perm.admins": "ADMINS",
    "admin.shop.stats.perm.owner": "OWNER",
    "admin.shop.stats.perm.stats": "STATS",
    "admin.shop.stats.perm.balance": "BALANCE",
    "admin.shop.stats.perm.promos": "PROMOS",
    "admin.promo.action.activate": "✅ Activate",
    "admin.promo.action.deactivate": "⛔ Deactivate",
    "admin.promo.action.delete": "🗑 Delete",
})

EN_TRANSLATIONS.update({
    "btn.buy_direct_account": "🏦 Direct Transfer",
    "btn.buy_direct_account": "🏦 Transfer Info",
    "btn.pay.sepay": "🏦 SePay / Bank Transfer",
    "btn.pay.sepay_account": "📄 Transfer Details",
    "btn.pay.sepay_done": "✅ I Have Transferred",
    "payments.sepay.not_configured": "❌ SePay bank transfer is not configured yet.",
    "payments.sepay.submitted": (
        "✅ Transfer request received.\n"
        "Amount: <code>{amount}</code> {currency}\n"
        "SePay will confirm it automatically."
    ),
    "payments.sepay.submitted_alert": "Waiting for SePay confirmation.",
    "payments.sepay.already_submitted": "This transfer is already waiting for SePay confirmation.",
    "payments.sepay.approved": "✅ Your SePay transfer was confirmed. {amount} {currency} has been added to your balance.",
    "payments.sepay.rejected": "❌ Your SePay transfer was rejected. Please contact support if you already paid.",
    "payments.sepay.owner.done": "SePay payment updated.",
    "shop.direct_purchase.choose_option": (
        "🛍 <b>Direct purchase via SePay</b>\n\n"
        "Item: <code>{item_name}</code>\n"
        "Price: <code>{amount}</code> {currency}\n"
        "Main account: <code>{bank_name}</code> - <code>{account_no}</code>\n\n"
        "Use the transfer details below. SePay will confirm the payment automatically."
    ),
    "shop.direct_purchase.instructions": (
        "🛍 <b>Direct purchase via SePay</b>\n\n"
        "Item: <code>{item_name}</code>\n"
        "Price: <code>{amount}</code> {currency}\n"
        "Amount to transfer: <code>{amount_vnd}</code> VND\n"
        "Bank: <code>{bank_name}</code>\n"
        "Account number: <code>{account_no}</code>\n"
        "{account_name_line}"
        "Transfer content: <code>{transfer_content}</code>\n\n"
        "Send the exact transfer content above. SePay will confirm the order automatically."
    ),
    "shop.direct_purchase.account_info": (
        "🛍 <b>Main account for direct purchase</b>\n\n"
        "Item: <code>{item_name}</code>\n"
        "Price: <code>{amount}</code> {currency}\n"
        "Bank: <code>{bank_name}</code>\n"
        "Account number: <code>{account_no}</code>\n"
        "{account_name_line}"
        "Amount to transfer: <code>{amount_vnd}</code> VND\n"
        "Transfer content: <code>{transfer_content}</code>\n\n"
        "After sending money, SePay will confirm the order automatically."
    ),
    "shop.direct_purchase.submitted": (
        "✅ Direct purchase request received.\n"
        "Item: <code>{item_name}</code>\n"
        "Amount: <code>{amount}</code> {currency}\n"
        "SePay will confirm it automatically."
    ),
    "shop.direct_purchase.submitted_alert": "Waiting for SePay confirmation.",
    "shop.direct_purchase.approved_balance_only": (
        "✅ The payment was confirmed, but the bot could not deliver the item automatically.\n"
        "Reason: {reason}\n"
        "{amount} {currency} has been added to your balance. You can use it to buy the item again."
    ),
})

VI_TRANSLATIONS: dict[str, str] = {}

VI_TRANSLATIONS.update({
    "btn.buy_direct_account": "🏦 Chuyển khoản trực tiếp",
    "btn.buy_direct_account": "🏦 Thông tin chuyển khoản",
    "btn.pay.sepay": "🏦 SePay / Chuyển khoản",
    "btn.pay.sepay_account": "📄 Chi tiết chuyển khoản",
    "btn.pay.sepay_done": "✅ Tôi đã chuyển khoản",
    "payments.sepay.not_configured": "❌ Chưa cấu hình chuyển khoản SePay.",
    "payments.sepay.submitted": (
        "✅ Đã nhận yêu cầu chuyển khoản.\n"
        "Số tiền: <code>{amount}</code> {currency}\n"
        "SePay sẽ tự động xác nhận."
    ),
    "payments.sepay.submitted_alert": "Đang chờ SePay xác nhận.",
    "payments.sepay.already_submitted": "Giao dịch này đang chờ SePay xác nhận rồi.",
    "payments.sepay.approved": "✅ Chuyển khoản SePay của bạn đã được xác nhận. {amount} {currency} đã được cộng vào số dư.",
    "payments.sepay.rejected": "❌ Chuyển khoản SePay của bạn bị từ chối. Nếu bạn đã thanh toán, hãy liên hệ hỗ trợ.",
    "payments.sepay.owner.done": "Đã cập nhật trạng thái thanh toán SePay.",
    "shop.direct_purchase.choose_option": (
        "🛍 <b>Mua hàng qua SePay</b>\n\n"
        "Sản phẩm: <code>{item_name}</code>\n"
        "Giá: <code>{amount}</code> {currency}\n"
        "TK chính: <code>{bank_name}</code> - <code>{account_no}</code>\n\n"
        "Dùng thông tin bên dưới, SePay sẽ tự động xác nhận thanh toán."
    ),
    "shop.direct_purchase.instructions": (
        "🛍 <b>Mua hàng qua SePay</b>\n\n"
        "Sản phẩm: <code>{item_name}</code>\n"
        "Giá: <code>{amount}</code> {currency}\n"
        "Số tiền cần chuyển: <code>{amount_vnd}</code> VND\n"
        "Ngân hàng: <code>{bank_name}</code>\n"
        "Số tài khoản: <code>{account_no}</code>\n"
        "{account_name_line}"
        "Nội dung chuyển khoản: <code>{transfer_content}</code>\n\n"
        "Hãy gửi đúng nội dung chuyển khoản ở trên. SePay sẽ tự động xác nhận đơn hàng."
    ),
    "shop.direct_purchase.account_info": (
        "🛍 <b>TK chính để mua hàng</b>\n\n"
        "Sản phẩm: <code>{item_name}</code>\n"
        "Giá: <code>{amount}</code> {currency}\n"
        "Ngân hàng: <code>{bank_name}</code>\n"
        "Số tài khoản: <code>{account_no}</code>\n"
        "{account_name_line}"
        "Số tiền cần chuyển: <code>{amount_vnd}</code> VND\n"
        "Nội dung chuyển khoản: <code>{transfer_content}</code>\n\n"
        "Sau khi chuyển tiền, SePay sẽ tự động xác nhận đơn hàng."
    ),
    "shop.direct_purchase.submitted": (
        "✅ Đã nhận yêu cầu mua hàng trực tiếp.\n"
        "Sản phẩm: <code>{item_name}</code>\n"
        "Số tiền: <code>{amount}</code> {currency}\n"
        "SePay sẽ tự động xác nhận."
    ),
    "shop.direct_purchase.submitted_alert": "Đang chờ SePay xác nhận.",
    "shop.direct_purchase.approved_balance_only": (
        "✅ Thanh toán đã được xác nhận, nhưng bot chưa giao được hàng tự động.\n"
        "Lý do: {reason}\n"
        "{amount} {currency} đã được cộng vào số dư. Bạn có thể dùng số dư này để mua lại sản phẩm."
    ),
})

EN_TRANSLATIONS.update({
    "btn.buy_direct_account": "🏦 Direct Transfer",
        "4. Choose direct transfer or bank account.\n"
    "btn.pay.sepay": "🏦 SePay / Bank Transfer",
    "btn.pay.sepay_account": "📷 Pay With Details",
    "btn.pay.sepay_done": "✅ I Have Transferred",
    "btn.admin.payment_approve": "✅ Approve",
    "btn.admin.payment_reject": "❌ Reject",
    "payments.sepay.not_configured": "❌ SePay is not configured yet.",
    "payments.sepay.pending_message": "SePay payment request created below.",
    "payments.sepay.choose_option": (
        "🏦 <b>Bank transfer</b>\n\n"
        "Top-up amount: <code>{amount}</code> {currency}\n"
        "Main account: <code>{bank_name}</code> - <code>{account_no}</code>\n\n"
        "Choose one payment option below."
    ),
    "payments.sepay.instructions": (
        "🏦 <b>Bank transfer via SePay</b>\n\n"
        "Balance top-up: <code>{amount}</code> {currency}\n"
        "Amount to transfer: <code>{amount_vnd}</code> VND\n"
        "Bank: <code>{bank_name}</code>\n"
        "Account number: <code>{account_no}</code>\n"
        "{account_name_line}"
        "Transfer content: <code>{transfer_content}</code>\n\n"
        "Use the transfer details below or transfer manually. After sending money, tap the confirmation button below."
    ),
    "payments.sepay.account_info": (
        "4. Choose direct transfer or bank account.\n"
        "Bank: <code>{bank_name}</code>\n"
        "Account number: <code>{account_no}</code>\n"
        "{account_name_line}"
        "Amount to transfer: <code>{amount_vnd}</code> VND\n"
        "Transfer content: <code>{transfer_content}</code>\n\n"
        "Use this account for transfer, then tap the confirmation button."
    ),
    "payments.sepay.account_name_line": "Account name: <code>{account_name}</code>\n",
    "payments.sepay.submitted": (
        "✅ SePay payment request submitted.\n"
        "Amount: <code>{amount}</code> {currency}\n"
        "Your transfer is waiting for manual confirmation."
    ),
    "payments.sepay.submitted_alert": "Payment sent for confirmation.",
    "payments.sepay.already_submitted": "This SePay payment is already waiting for review.",
    "payments.sepay.already_rejected": "This SePay payment was already rejected.",
    "payments.sepay.approved": "✅ Your SePay transfer was confirmed. {amount} {currency} has been added to your balance.",
    "payments.sepay.rejected": "❌ Your SePay transfer was rejected. Please contact support if you already paid.",
    "payments.sepay.owner.review": (
        "🏦 <b>SePay transfer review</b>\n\n"
        "Payment ID: <code>{payment_id}</code>\n"
        "User: <a href='tg://user?id={user_id}'>{name}</a> (<code>{user_id}</code>)\n"
        "Balance top-up: <code>{amount}</code> {currency}\n"
        "Transferred amount: <code>{amount_vnd}</code> VND\n"
        "Bank: <code>{bank_name}</code>\n"
        "Account number: <code>{account_no}</code>\n"
        "Account name: <code>{account_name}</code>\n"
        "Transfer content: <code>{transfer_content}</code>\n\n"
        "Check your bank app and approve or reject this request."
    ),
    "payments.sepay.owner.approved": (
        "✅ SePay payment approved.\n"
        "Payment ID: <code>{payment_id}</code>\n"
        "User: <code>{user_id}</code>\n"
        "Credited: <code>{amount}</code> {currency}"
    ),
    "payments.sepay.owner.rejected": (
        "❌ SePay payment rejected.\n"
        "Payment ID: <code>{payment_id}</code>\n"
        "User: <code>{user_id}</code>\n"
        "Requested: <code>{amount}</code> {currency}"
    ),
    "payments.sepay.owner.done": "SePay payment updated.",
    "shop.direct_purchase.choose_option": (
        "🛍 <b>Direct purchase</b>\n\n"
        "Item: <code>{item_name}</code>\n"
        "Price: <code>{amount}</code> {currency}\n"
        "Main account: <code>{bank_name}</code> - <code>{account_no}</code>\n\n"
        "Choose one payment option below."
    ),
    "shop.direct_purchase.instructions": (
        "🛍 <b>Direct purchase via bank transfer</b>\n\n"
        "Item: <code>{item_name}</code>\n"
        "Price: <code>{amount}</code> {currency}\n"
        "Amount to transfer: <code>{amount_vnd}</code> VND\n"
        "Bank: <code>{bank_name}</code>\n"
        "Account number: <code>{account_no}</code>\n"
        "{account_name_line}"
        "Transfer content: <code>{transfer_content}</code>\n\n"
        "Use the transfer details below or transfer manually. After sending money, tap the confirmation button below."
    ),
    "shop.direct_purchase.account_info": (
        "4. Choose direct transfer or bank account.\n"
        "Item: <code>{item_name}</code>\n"
        "Price: <code>{amount}</code> {currency}\n"
        "Bank: <code>{bank_name}</code>\n"
        "Account number: <code>{account_no}</code>\n"
        "{account_name_line}"
        "Amount to transfer: <code>{amount_vnd}</code> VND\n"
        "Transfer content: <code>{transfer_content}</code>\n\n"
        "After transfer, tap the confirmation button."
    ),
    "shop.direct_purchase.submitted": (
        "✅ Direct purchase payment submitted.\n"
        "Item: <code>{item_name}</code>\n"
        "Amount: <code>{amount}</code> {currency}\n"
        "Your payment is waiting for manual confirmation."
    ),
    "shop.direct_purchase.submitted_alert": "Direct purchase request sent for confirmation.",
    "shop.direct_purchase.owner.review": (
        "🛍 <b>Direct purchase review</b>\n\n"
        "Payment ID: <code>{payment_id}</code>\n"
        "User: <a href='tg://user?id={user_id}'>{name}</a> (<code>{user_id}</code>)\n"
        "Item: <code>{item_name}</code>\n"
        "Charge: <code>{amount}</code> {currency}\n"
        "Transferred amount: <code>{amount_vnd}</code> VND\n"
        "Bank: <code>{bank_name}</code>\n"
        "Account number: <code>{account_no}</code>\n"
        "{account_name_line}"
        "Transfer content: <code>{transfer_content}</code>\n\n"
        "Check your bank app and approve or reject this request."
    ),
    "shop.direct_purchase.owner.approved": (
        "✅ Direct purchase approved.\n"
        "Payment ID: <code>{payment_id}</code>\n"
        "User: <code>{user_id}</code>\n"
        "Item: <code>{item_name}</code>\n"
        "Charged: <code>{amount}</code> {currency}"
    ),
    "shop.direct_purchase.owner.rejected": (
        "❌ Direct purchase rejected.\n"
        "Payment ID: <code>{payment_id}</code>\n"
        "User: <code>{user_id}</code>\n"
        "Item: <code>{item_name}</code>\n"
        "Requested: <code>{amount}</code> {currency}"
    ),
    "shop.direct_purchase.approved_balance_only": (
        "✅ Your payment was confirmed, but the item could not be delivered automatically.\n"
        "Reason: {reason}\n"
        "{amount} {currency} was added to your balance. You can buy the item from balance now."
    ),
})

_ADMIN_VI_TRANSLATIONS = {
    "admin.goods.add.prompt.category.pick": "Chọn danh mục:",
    "admin.goods.add.category.empty": "Chưa có danh mục nào. Hãy tạo danh mục trước trong phần quản lý danh mục.",
    "admin.goods.positions.title": "Chọn sản phẩm để xem:",
    "admin.goods.positions.empty": "Chưa có sản phẩm nào. Hãy thêm sản phẩm trước.",
    "shop.goods.empty": "Chưa có sản phẩm nào để mua.",
    "admin.categories.add": "➕ Thêm danh mục",
    "admin.categories.add.exist": "❌ Không tạo được danh mục vì đã tồn tại",
    "admin.categories.add.success": "✅ Đã tạo danh mục",
    "admin.categories.delete": "🗑 Xóa danh mục",
    "admin.categories.delete.not_found": "❌ Không xóa được danh mục vì không tồn tại",
    "admin.categories.delete.success": "✅ Đã xóa danh mục",
    "admin.categories.menu.title": "⛩️ Quản lý danh mục",
    "admin.categories.prompt.add": "Nhập tên danh mục mới:",
    "admin.categories.prompt.delete": "Nhập tên danh mục cần xóa:",
    "admin.categories.prompt.rename.new": "Nhập tên danh mục mới:",
    "admin.categories.prompt.rename.old": "Nhập tên danh mục hiện tại cần đổi:",
    "admin.categories.rename": "✏️ Đổi tên danh mục",
    "admin.categories.rename.exist": "❌ Không thể đổi tên vì tên mới đã tồn tại",
    "admin.categories.rename.not_found": "❌ Không tìm thấy danh mục để cập nhật",
    "admin.categories.rename.success": "✅ Đã đổi tên danh mục từ \"{old}\" thành \"{new}\"",
    "admin.goods.add.category.not_found": "❌ Không thể tạo sản phẩm vì danh mục không hợp lệ",
    "admin.goods.add.infinity.question": "Sản phẩm này có hàng vô hạn không? (mọi người sẽ nhận cùng một nội dung sao chép)",
    "admin.goods.add.name.exists": "❌ Không thể tạo sản phẩm vì đã tồn tại",
    "admin.goods.add.price.invalid": "⚠️ Giá không hợp lệ. Hãy nhập một số.",
    "admin.goods.add.prompt.category": "Nhập danh mục của sản phẩm:",
    "admin.goods.add.prompt.description": "Nhập mô tả sản phẩm:",
    "admin.goods.add.prompt.name": "Nhập tên sản phẩm",
    "admin.goods.add.prompt.price": "Nhập giá sản phẩm ({currency}):",
    "admin.goods.add.result.added": "📦 Số giá trị đã thêm: <b>{n}</b>",
    "admin.goods.add.result.created": "✅ Đã tạo sản phẩm.",
    "admin.goods.add.result.skipped_batch_dup": "🔁 Bỏ qua do trùng trong danh sách nhập: <b>{n}</b>",
    "admin.goods.add.result.skipped_db_dup": "↩️ Bỏ qua do đã có trong cơ sở dữ liệu: <b>{n}</b>",
    "admin.goods.add.result.skipped_invalid": "🚫 Bỏ qua do rỗng hoặc không hợp lệ: <b>{n}</b>",
    "admin.goods.add.single.created": "✅ Đã tạo sản phẩm và thêm giá trị",
    "admin.goods.add.single.empty": "⚠️ Giá trị không được để trống.",
    "admin.goods.add.single.prompt_value": "Nhập một giá trị cho sản phẩm:",
    "admin.goods.add.values.added": "✅ Đã thêm giá trị “{value}” vào danh sách ({count} mục).",
    "admin.goods.add.values.added_batch": "✅ Đã thêm {added_now} dòng. Tổng trong danh sách: {count}.",
    "admin.goods.add.values.prompt_multi": "Gửi giá trị sản phẩm sao cho mỗi dòng không rỗng là 1 hàng hóa riêng.\nBạn có thể dán nhiều dòng trong cùng 1 tin nhắn.\nKhi xong, bấm “Thêm các hàng hóa đã liệt kê”.",
    "admin.goods.add_item": "➕ Nạp thêm hàng cho sản phẩm",
    "admin.goods.add_position": "➕ Thêm sản phẩm",
    "admin.goods.delete.position.not_found": "❌ Không xóa được vì sản phẩm không tồn tại",
    "admin.goods.delete.position.success": "✅ Đã xóa sản phẩm",
    "admin.goods.delete.prompt.name": "Nhập tên sản phẩm",
    "admin.goods.delete_position": "❌ Xóa sản phẩm",
    "admin.goods.item.already_deleted_or_missing": "Sản phẩm đã bị xóa hoặc không tồn tại",
    "admin.goods.item.delete.button": "❌ Xóa mục hàng",
    "admin.goods.item.deleted": "✅ Đã xóa mục hàng",
    "admin.goods.item.info.id": "<b>ID duy nhất</b>: <code>{id}</code>",
    "admin.goods.item.info.position": "<b>Sản phẩm</b>: <code>{name}</code>",
    "admin.goods.item.info.price": "<b>Giá</b>: <code>{price}</code> {currency}",
    "admin.goods.item.info.value": "<b>Nội dung</b>: <code>{value}</code>",
    "admin.goods.item.invalid": "Dữ liệu không hợp lệ",
    "admin.goods.item.invalid_id": "ID mục hàng không hợp lệ",
    "admin.goods.item.not_found": "Không tìm thấy mục hàng",
    "admin.goods.list_in_position.empty": "ℹ️ Sản phẩm này chưa có hàng.",
    "admin.goods.list_in_position.title": "Danh sách hàng trong sản phẩm:",
    "admin.goods.menu.title": "⛩️ Quản lý sản phẩm",
    "admin.goods.position.not_found": "❌ Không tìm thấy sản phẩm",
    "admin.goods.prompt.enter_item_name": "Nhập tên sản phẩm",
    "admin.goods.show_items": "📄 Xem hàng trong sản phẩm",
    "admin.goods.update.amount.infinity_forbidden": "❌ Không thể thêm giá trị vì sản phẩm đang ở chế độ vô hạn",
    "admin.goods.update.amount.not_exists": "❌ Không thể thêm giá trị vì sản phẩm không tồn tại",
    "admin.goods.update.amount.prompt.name": "Nhập tên sản phẩm",
    "admin.goods.update.infinity.deny.question": "Bạn có muốn tắt chế độ vô hạn không?",
    "admin.goods.update.infinity.make.question": "Bạn có muốn chuyển sản phẩm sang chế độ vô hạn không?",
    "admin.goods.update.not_exists": "❌ Không thể cập nhật vì sản phẩm không tồn tại",
    "admin.goods.update.position.exists": "Đã có sản phẩm khác với tên này.",
    "admin.goods.update.position.invalid": "Không tìm thấy sản phẩm.",
    "admin.goods.update.prompt.description": "Nhập mô tả sản phẩm:",
    "admin.goods.update.prompt.name": "Nhập tên sản phẩm",
    "admin.goods.update.prompt.new_name": "Nhập tên sản phẩm mới:",
    "admin.goods.update.success": "✅ Đã cập nhật sản phẩm",
    "admin.goods.update.values.result.title": "✅ Đã thêm các giá trị",
    "admin.goods.update_position": "📝 Chỉnh sửa sản phẩm",
    "admin.promo.binding.category": "Danh mục",
    "admin.promo.binding.item": "Sản phẩm",
    "admin.promo.binding.none": "Không ràng buộc",
    "admin.promo.category_not_found": "❌ Không tìm thấy danh mục.",
    "admin.promo.code_exists": "❌ Mã khuyến mãi đã tồn tại.",
    "admin.promo.confirm_delete": "Xóa mã khuyến mãi <code>{code}</code>?",
    "admin.promo.create": "➕ Tạo mã khuyến mãi",
    "admin.promo.created": "✅ Đã tạo mã khuyến mãi <code>{code}</code>!",
    "admin.promo.deleted": "✅ Đã xóa mã khuyến mãi.",
    "admin.promo.detail": "🏷 <b>Mã khuyến mãi</b>: <code>{code}</code>\n📊 Loại: {discount_type}\n💰 Giá trị giảm: {discount_value}\n🔢 Lượt dùng: {current_uses}/{max_uses}\n📅 Hết hạn: {expires_at}\n✅ Kích hoạt: {is_active}",
    "admin.promo.invalid_date": "❌ Ngày không hợp lệ. Định dạng đúng: YYYY-MM-DD",
    "admin.promo.invalid_value": "❌ Giá trị không hợp lệ. Hãy thử lại.",
    "admin.promo.item_not_found": "❌ Không tìm thấy sản phẩm.",
    "admin.promo.list_empty": "Chưa có mã khuyến mãi nào.",
    "admin.promo.prompt.binding": "Ràng buộc theo danh mục hoặc sản phẩm?\n\nGửi:\n• Tên danh mục\n• Tên sản phẩm\n• 0 — không ràng buộc",
    "admin.promo.prompt.binding_type": "Ràng buộc mã khuyến mãi với danh mục hay sản phẩm?",
    "admin.promo.prompt.category_name": "Nhập tên danh mục:",
    "admin.promo.prompt.code": "Nhập mã khuyến mãi (tối đa 50 ký tự):",
    "admin.promo.prompt.expires": "Nhập ngày hết hạn (YYYY-MM-DD) hoặc 0 nếu không hết hạn:",
    "admin.promo.prompt.item_name": "Nhập tên sản phẩm:",
    "admin.promo.prompt.max_uses": "Nhập số lượt dùng tối đa (0 = không giới hạn):",
    "admin.promo.prompt.type": "Chọn loại giảm giá:",
    "admin.promo.prompt.value": "Nhập giá trị giảm ({type}):",
    "admin.promo.title": "🏷 <b>Quản lý mã khuyến mãi</b>",
    "admin.promo.toggled_off": "⛔ Đã tắt mã khuyến mãi.",
    "admin.promo.toggled_on": "✅ Đã bật mã khuyến mãi.",
    "admin.promo.type.balance": "💰 Nạp số dư",
    "admin.promo.type.fixed": "💰 Giảm số tiền cố định",
    "admin.promo.type.percent": "📊 Giảm theo phần trăm (%)",
    "admin.promo.action.activate": "✅ Kích hoạt",
    "admin.promo.action.deactivate": "⛔ Tắt",
    "admin.promo.action.delete": "🗑 Xóa",
    "admin.roles.assign_prompt": "Chọn vai trò cho người dùng {id}:",
    "admin.roles.assigned": "✅ Đã gán vai trò {role} cho {name}",
    "admin.roles.assigned_notify": "ℹ️ Vai trò của bạn đã được đặt thành: {role}",
    "admin.roles.confirm": "✅ Xác nhận",
    "admin.roles.create": "➕ Tạo vai trò",
    "admin.roles.created": "✅ Đã tạo vai trò \"{name}\"",
    "admin.roles.delete": "🗑 Xóa",
    "admin.roles.delete_confirm": "Bạn có chắc muốn xóa vai trò \"{name}\" không?",
    "admin.roles.delete_fail": "❌ Xóa thất bại: {error}",
    "admin.roles.deleted": "✅ Đã xóa vai trò",
    "admin.roles.detail": "🛡 <b>Vai trò</b>: {name}\n📋 Quyền: {perms}\n👥 Người dùng: {users}",
    "admin.roles.edit": "✏️ Chỉnh sửa",
    "admin.roles.edit_name_prompt": "Nhập tên vai trò mới (hoặc /skip để giữ nguyên):",
    "admin.roles.list_title": "🛡 Các vai trò trong hệ thống:",
    "admin.roles.name_exists": "❌ Đã có vai trò với tên này",
    "admin.roles.name_invalid": "⚠️ Tên không hợp lệ hoặc dài quá 64 ký tự.",
    "admin.roles.perm_denied": "⚠️ Bạn không đủ quyền cho thao tác này",
    "admin.roles.prompt_name": "Nhập tên vai trò (tối đa 64 ký tự):",
    "admin.roles.select_perms": "Chọn quyền cho vai trò \"{name}\":",
    "admin.roles.updated": "✅ Đã cập nhật vai trò \"{name}\"",
    "admin.shop.bought.not_found": "❌ Không tìm thấy hàng đã mua với mã duy nhất này",
    "admin.shop.bought.prompt_id": "Nhập mã duy nhất của hàng đã mua",
    "admin.shop.logs.caption": "Nhật ký bot",
    "admin.shop.logs.empty": "❗️ Chưa có log nào",
    "admin.shop.logs.file_label": "Tệp log {name}",
    "admin.shop.menu.logs": "📁 Xem log",
    "admin.shop.menu.search_bought": "🔎 Tìm hàng đã mua",
    "admin.shop.menu.statistics": "📊 Thống kê",
    "admin.shop.menu.title": "⛩️ Quản lý cửa hàng",
    "admin.shop.menu.users": "👤 Người dùng",
    "admin.shop.stats.roles_header": "\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n◽<b>VAI TRÒ</b>",
    "admin.shop.stats.template": "Thống kê cửa hàng:\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n<b>◽NGƯỜI DÙNG</b>\n◾️Mới trong 24h: {today_users}\n◾️Tổng số: {users}\n◾️Người mua: {buyers}\n◾️Đã chặn: {blocked}\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n◽<b>DOANH THU</b>\n◾Doanh số 24h: {today_orders} {currency} ({today_sold_count} sản phẩm)\n◾Tổng đã bán: {all_orders} {currency}\n◾Đơn trung bình: {avg_order} {currency}\n◾Nạp trong 24h: {today_topups} {currency}\n◾Tiền trong hệ thống: {system_balance} {currency}\n◾Tổng đã nạp: {all_topups} {currency}\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n◽<b>DANH MỤC</b>\n◾Hàng tồn: {items} mục\n◾Sản phẩm: {goods} mục\n◾Danh mục: {categories} mục\n◾Đã bán: {sold_count} mục",
    "admin.shop.stats.perm.use": "DÙNG",
    "admin.shop.stats.perm.broadcast": "THÔNG BÁO",
    "admin.shop.stats.perm.settings": "CÀI ĐẶT",
    "admin.shop.stats.perm.users": "NGƯỜI DÙNG",
    "admin.shop.stats.perm.catalog": "DANH MỤC",
    "admin.shop.stats.perm.admins": "QUẢN TRỊ",
    "admin.shop.stats.perm.owner": "CHỦ SỞ HỮU",
    "admin.shop.stats.perm.stats": "THỐNG KÊ",
    "admin.shop.stats.perm.balance": "SỐ DƯ",
    "admin.shop.stats.perm.promos": "KHUYẾN MÃI",
    "admin.shop.users.title": "Danh sách người dùng bot:",
    "admin.users.balance.deducted": "✅ Đã trừ {amount} {currency} khỏi số dư của {name}",
    "admin.users.balance.deducted.notify": "ℹ️ Bạn đã bị trừ {amount} {currency} khỏi số dư",
    "admin.users.balance.insufficient": "❌ Không đủ số dư. Số dư hiện tại: {balance} {currency}",
    "admin.users.balance.topped": "✅ Đã cộng {amount} {currency} vào số dư của {name}",
    "admin.users.balance.topped.notify": "✅ Số dư của bạn đã được cộng thêm {amount} {currency}",
    "admin.users.blocked.success": "🚫 Đã chặn người dùng {name}",
    "admin.users.btn.view_earnings": "💰 Xem thu nhập của user",
    "admin.users.btn.view_referrals": "👥 Xem người được giới thiệu của user",
    "admin.users.cannot_block_owner": "❌ Không thể chặn chủ bot",
    "admin.users.cannot_change_owner": "Bạn không thể thay đổi vai trò của chủ bot",
    "admin.users.invalid_id": "⚠️ Hãy nhập Telegram ID hợp lệ bằng số.",
    "admin.users.not_found": "❌ Không tìm thấy người dùng",
    "admin.users.profile_unavailable": "❌ Không có hồ sơ vì người dùng này chưa từng tồn tại",
    "admin.users.prompt_enter_id": "👤 Nhập ID người dùng để xem hoặc chỉnh sửa dữ liệu",
    "admin.users.referrals": "👥 <b>Số người được giới thiệu</b> — {count}",
    "admin.users.remove_admin.notify": "❌ Quyền ADMIN của bạn đã bị thu hồi",
    "admin.users.remove_admin.success": "✅ Đã thu hồi quyền admin của {name}",
    "admin.users.role": "🎛 <b>Vai trò</b> — {role}",
    "admin.users.set_admin.notify": "✅ Bạn đã được cấp quyền ADMIN",
    "admin.users.set_admin.success": "✅ Đã gán vai trò cho {name}",
    "admin.users.status.blocked": "🚫 <b>Trạng thái</b> — Đã chặn",
    "admin.users.unblocked.success": "✅ Đã bỏ chặn người dùng {name}",
    "broadcast.cancel": "❌ Đã hủy thông báo hàng loạt.",
    "broadcast.creating": "📤 Bắt đầu gửi thông báo...\n👥 Tổng người dùng: {ids}",
    "broadcast.done": "✅ Đã gửi thông báo xong!\n\n📊 Thống kê:\n👥 Tổng: {total}\n✅ Thành công: {sent}\n❌ Thất bại: {failed}\n🚫 Đã chặn bot: ~{blocked}\n📈 Tỷ lệ thành công: {success}%\n⏱ Thời gian: {duration} giây",
    "broadcast.progress": "📤 Đang gửi thông báo...\n\n📊 Tiến độ: {progress:.1f}%{n}✅ Đã gửi: {sent}/{total}\n❌ Lỗi: {failed}\n⏱ Đã trôi qua: {time} giây",
    "broadcast.prompt": "Gửi tin nhắn cần phát cho toàn bộ người dùng:",
    "broadcast.warning": "Không có phiên phát thông báo nào đang chạy",
    "btn.admin.assign_role": "🛡 Gán vai trò",
    "btn.admin.block": "🚫 Chặn",
    "btn.admin.deduct_user": "💳 Trừ số dư",
    "btn.admin.demote": "⬇️ Gỡ quyền admin",
    "btn.admin.promote": "⬆️ Cấp quyền admin",
    "btn.admin.replenish_user": "💸 Cộng số dư",
    "btn.admin.unblock": "✅ Bỏ chặn",
    "btn.admin.view_profile": "👁 Xem hồ sơ",
}

VI_TRANSLATIONS: dict[str, str] = {**_ADMIN_VI_TRANSLATIONS,
    "btn.shop": "🛍️ Mua hàng",
    "btn.rules": "📜 Quy định",
    "btn.profile": "👤 Hồ sơ",
    "btn.support": "🆘 Hỗ trợ",
    "btn.channel": "ℹ Kênh tin tức",
    "btn.admin_menu": "🎛 Bảng quản trị",
    "btn.back": "⬅️ Quay lại",
    "btn.to_menu": "🏠 Menu",
    "btn.close": "✖ Đóng",
    "btn.buy": "🛒 Mua",
    "btn.out_of_stock": "❌ Hết hàng",
    "btn.yes": "✅ Có",
    "btn.no": "❌ Không",
    "btn.check": "🔄 Kiểm tra",
    "btn.check_subscription": "🔄 Kiểm tra đăng ký",
    "btn.pay": "💳 Thanh toán",
    "btn.check_payment": "🔄 Kiểm tra thanh toán",
    "btn.pay.usdt": "💵 USDT",
    "btn.pay.crypto": "💎 CryptoPay",
    "btn.pay.stars": "⭐ Telegram Stars",
    "btn.pay.tg": "💸 Telegram Payments",
    "btn.replenish": "💳 Nạp số dư",
    "btn.referral": "🎲 Giới thiệu",
    "btn.purchased": "🎁 Đã mua",
    "btn.view_referrals": "👥 Người giới thiệu của tôi",
    "btn.view_earnings": "💰 Thu nhập của tôi",
    "btn.back_to_referral": "⬅️ Về mục giới thiệu",
    "btn.apply_promo": "🏷 Áp mã giảm giá",
    "btn.remove_promo": "❌ Gỡ mã giảm giá",
    "btn.redeem_promo": "🏷 Đổi mã khuyến mãi",
    "btn.cart": "🛒 Giỏ hàng ({count})",
    "btn.cart_empty": "🛒 Giỏ hàng",
    "btn.add_to_cart": "🛒 Thêm vào giỏ",
    "btn.cart_checkout": "💳 Thanh toán giỏ hàng",
    "btn.cart_clear": "🗑 Xóa giỏ hàng",
    "btn.operation_history": "📋 Lịch sử giao dịch",
    "btn.leave_review": "⭐ Đánh giá",
    "btn.view_reviews": "📝 Đánh giá ({count})",
    "btn.skip_review_text": "⏭ Bỏ qua nội dung",
    "btn.add_values_finish": "Thêm các hàng hóa đã liệt kê",

    # === Auto product ad ===
    "product_ad.title": "🔥 <b>Sản phẩm nổi bật</b>",
    "product_ad.name": "📦 <b>{name}</b>",
    "product_ad.description": "📝 {description}",
    "product_ad.price": "💰 Giá: {amount} {currency}",
    "product_ad.stock_left": "📦 Còn hàng: {count}",
    "product_ad.stock_unlimited": "📦 Hàng vô hạn",
    "product_ad.buy_cta": "👇 Nhấn nút bên dưới để mở sản phẩm và mua ngay!",
    "product_ad.btn.buy": "🛒 Mua Ngay",

    "menu.title": (
        "📌 Hướng dẫn nhanh:\n"
        "1. Nhấn \"🛍️ Mua hàng\".\n"
        "2. Mở sản phẩm bạn muốn mua.\n"
        "3. Nhấn \"🛒 Mua\" trong trang sản phẩm.\n"

        "5. Chuyển đúng số tiền bot hiển thị.\n"
        "6. Chờ bot xử lý sau khi thanh toán được xác nhận.\n\n"
        "📌 Vui lòng chọn menu:"
    ),
    "profile.caption": "👤 <b>Hồ sơ</b> — <a href='tg://user?id={id}'>{name}</a>",
    "rules.not_set": "❌ Chưa cấu hình quy định",
    "btn.language": "🌐 Ngôn ngữ",
    "language.title": "🌐 Chọn ngôn ngữ",
    "language.changed": "✅ Đã đổi ngôn ngữ: {locale}",
    "language.name.vi": "Tiếng Việt",
    "language.name.en": "English",
    "commands.start": "🚀 Khởi động bot",
    "commands.shop": "🛍️ Mua hàng",
    "commands.profile": "👤 Hồ sơ của tôi",
    "commands.orders": "📦 Đơn hàng đã mua",
    "commands.balance": "💰 Số dư & Nạp tiền",
    "commands.rules": "📜 Quy định",
    "commands.help": "❓ Trợ giúp",
    "help.text": (
        "📘 <b>Hướng dẫn sử dụng</b>\n\n"
        "Cách mua hàng:\n"
        "1. Mở \"🛍️ Mua hàng\".\n"
        "2. Chọn sản phẩm.\n"
        "3. Nhấn \"🛒 Mua\".\n"
        "4. Chọn chuyển khoản trực tiếp hoặc TK chính.\n"
        "5. Chuyển đúng số tiền bot hiển thị.\n"
        "6. Chờ bot giao hàng.\n\n"
        "Các lệnh hữu ích:\n"
        "/start — khởi động bot\n"
        "/shop — mở cửa hàng\n"
        "/profile — xem hồ sơ của bạn\n"
        "/orders — xem đơn hàng đã mua\n"
        "/balance — xem số dư và nạp tiền\n"
        "/rules — xem quy định\n"
        "/help — mở hướng dẫn này\n\n"
        "🌐 Đổi ngôn ngữ bằng nút 🇻🇳 Tiếng Việt / 🇬🇧 English trong menu chính."
    ),
    "subscribe.prompt": "Vui lòng đăng ký kênh tin tức trước",
    "subscribe.open_channel": "Mở kênh",
    "profile.referral_id": "👤 <b>Người giới thiệu</b> — <code>{id}</code>",
    "profile.id": "🆔 <b>ID</b> — <code>{id}</code>",
    "profile.balance": "💳 <b>Số dư</b> — <code>{amount}</code> {currency}",
    "profile.total_topup": "💵 <b>Tổng đã nạp</b> — <code>{amount}</code> {currency}",
    "profile.purchased_count": "🎁 <b>Số món đã mua</b> — {count}",
    "profile.registration_date": "🕢 <b>Ngày đăng ký</b> — <code>{dt}</code>",
    "referral.title": "💚 Hệ thống giới thiệu",
    "referral.link": "🔗 Liên kết: https://t.me/{bot_username}?start={user_id}",
    "referral.count": "Số người được giới thiệu: {count}",
    "referral.description": (
        "📔 Hệ thống giới thiệu giúp bạn kiếm tiền mà không cần vốn. "
        "Chỉ cần chia sẻ liên kết giới thiệu của bạn và bạn sẽ nhận {percent}% từ các lần nạp của người được giới thiệu."
    ),
    "referrals.list.title": "👥 Danh sách người được giới thiệu:",
    "referrals.list.empty": "Bạn chưa có người giới thiệu nào hoạt động",
    "referrals.item.format": "ID: {telegram_id} | Đã mang về: {total_earned} {currency}",
    "referral.earnings.title": "💰 Thu nhập từ người giới thiệu <code>{telegram_id}</code> (<a href='tg://user?id={telegram_id}'>{name}</a>):",
    "referral.earnings.empty": "Chưa có thu nhập nào từ người giới thiệu <code>{id}</code> (<a href='tg://user?id={id}'>{name}</a>)",
    "referral.earning.format": "{amount} {currency} | {date} | (từ {original_amount} {currency})",
    "referral.item.info": (
        "💰 Khoản thu #<code>{id}</code>\n"
        "👤 Người giới thiệu: <code>{telegram_id}</code> (<a href='tg://user?id={telegram_id}'>{name}</a>)\n"
        "🔢 Số tiền: {amount} {currency}\n"
        "🕘 Ngày: <code>{date}</code>\n"
        "💵 Từ lần nạp {original_amount} {currency}"
    ),
    "all.earnings.title": "💰 Toàn bộ thu nhập giới thiệu của bạn:",
    "all.earnings.empty": "Bạn chưa có thu nhập giới thiệu nào",
    "all.earning.format": "{amount} {currency} từ ID:{referral_id} | {date}",
    "referrals.stats.template": (
        "📊 Thống kê giới thiệu:\n\n"
        "👥 Người giới thiệu đang hoạt động: {active_count}\n"
        "💰 Tổng đã kiếm: {total_earned} {currency}\n"
        "📈 Tổng tiền nạp từ người giới thiệu: {total_original} {currency}\n"
        "🔢 Số lần nhận thưởng: {earnings_count}"
    ),
    "payments.replenish_prompt": "Nhập số tiền muốn nạp bằng {currency}:",
    "payments.replenish_invalid": "❌ Số tiền không hợp lệ. Hãy nhập từ {min_amount} đến {max_amount} {currency}.",
    "payments.deduct_prompt": "Nhập số tiền cần trừ bằng {currency}:",
    "payments.deduct_invalid": "❌ Số tiền không hợp lệ. Hãy nhập từ {min_amount} đến {max_amount} {currency}.",
    "payments.method_choose": "Chọn phương thức thanh toán:",
    "payments.not_configured": "❌ Chưa cấu hình nạp tiền",
    "payments.session_expired": "Phiên thanh toán đã hết hạn. Vui lòng bắt đầu lại.",
    "payments.crypto.create_fail": "❌ Không thể tạo hóa đơn: {error}",
    "payments.crypto.api_error": "❌ Lỗi CryptoPay API: {error}",
    "payments.crypto.check_fail": "❌ Kiểm tra thanh toán thất bại: {error}",
    "payments.stars.create_fail": "❌ Không thể tạo hóa đơn Stars: {error}",
    "payments.fiat.create_fail": "❌ Không thể tạo hóa đơn: {error}",
    "payments.no_active_invoice": "❌ Không tìm thấy hóa đơn đang hoạt động. Hãy nạp lại từ đầu.",
    "payments.invoice_not_found": "❌ Không tìm thấy hóa đơn. Vui lòng bắt đầu lại.",
    "payments.not_paid_yet": "⌛ Thanh toán chưa hoàn tất.",
    "payments.expired": "❌ Hóa đơn đã hết hạn.",
    "payments.invoice.summary": (
        "💵 Số tiền nạp: {amount} {currency}.\n"
        "⌛ Bạn có {minutes} phút để thanh toán.\n"
        "<b>❗ Sau khi thanh toán, nhấn '{button}'</b>"
    ),
    "payments.unable_determine_amount": "❌ Không xác định được số tiền đã thanh toán.",
    "payments.topped_simple": "✅ Đã nạp {amount} {currency} vào số dư",
    "payments.topped_with_suffix": "✅ Đã nạp {amount} {currency} vào số dư ({suffix})",
    "payments.success_suffix.stars": "Telegram Stars",
    "payments.success_suffix.tg": "Telegram Payments",
    "payments.referral.bonus": "✅ Bạn nhận được {amount} {currency} từ người giới thiệu <a href='tg://user?id={id}'>{name}</a>",
    "payments.invoice.title.topup": "Nạp số dư",
    "payments.invoice.desc.topup.stars": "Nạp {amount} {currency} qua Telegram Stars",
    "payments.invoice.desc.topup.fiat": "Thanh toán qua Telegram Payments (thẻ)",
    "payments.invoice.label.fiat": "Nạp {amount} {currency}",
    "payments.invoice.label.stars": "{stars} ⭐",
    "payments.already_processed": "Thanh toán này đã được xử lý ✅",
    "payments.processing_error": "Lỗi xử lý thanh toán. Vui lòng thử lại sau.",
    "shop.categories.title": "🏪 Danh mục cửa hàng",
    "shop.goods.choose": "🏪 Chọn sản phẩm",
    "shop.item.not_found": "Không tìm thấy sản phẩm",
    "shop.item.title": "🏪 Sản phẩm {name}",
    "shop.item.description": "Mô tả: {description}",
    "shop.item.price": "Giá — {amount} {currency}",
    "shop.item.price_discounted": "💰 <b>Giá</b>: <s>{original}</s> <b>{discounted}</b> {currency} (mã {code})",
    "shop.item.quantity_unlimited": "Số lượng — không giới hạn",
    "shop.item.quantity_left": "Số lượng — còn {count}",
    "shop.insufficient_funds": "❌ Không đủ số dư",
    "shop.out_of_stock": "❌ Sản phẩm đã hết hàng",
    "shop.purchase.success": "✅ Đã mua thành công. <b>Số dư</b>: <i>{balance}</i> {currency}\n\n{value}",
    "shop.purchase.receipt": (
        "✅ Đặt hàng thành công!\n"
        "────────────\n"
        "📃 Sản phẩm: {item_name}\n"
        "💰 Giá: {price} {currency}\n"
        "📦 Số lượng: 1\n"
        "💡 Mã đơn: {unique_id}\n"
        "🕐 Thời gian: {datetime}\n"
        "💲 Tổng tiền: {price} {currency}\n"
        "👤 Người mua: @{username} ({user_id})\n"
        "────────────\n"
        "🔑 Nội dung:\n<code>{value}</code>"
    ),
    "shop.purchase.processing": "⏳ Đang xử lý mua hàng...",
    "shop.purchase.fail.user_not_found": "❌ Không tìm thấy người dùng trong hệ thống",
    "shop.purchase.fail.general": "❌ Lỗi mua hàng: {message}",
    "purchases.title": "Các món đã mua:",
    "purchases.pagination.invalid": "Dữ liệu phân trang không hợp lệ",
    "purchases.item.not_found": "Không tìm thấy giao dịch mua",
    "purchases.item.name": "<b>🧾 Sản phẩm</b>: <code>{name}</code>",
    "purchases.item.price": "<b>💵 Giá</b>: <code>{amount}</code> {currency}",
    "purchases.item.datetime": "<b>🕒 Thời điểm mua</b>: <code>{dt}</code>",
    "purchases.item.unique_id": "<b>🧾 Mã duy nhất</b>: <code>{uid}</code>",
    "purchases.item.value": "<b>🔑 Nội dung</b>:\n<code>{value}</code>",
    "purchases.item.buyer": "<b>Người mua</b>: <code>{buyer}</code>",
    "cart.title": "🛒 <b>Giỏ hàng</b>",
    "cart.empty": "Giỏ hàng đang trống.",
    "cart.item": "• {name} — {price} {currency}",
    "cart.total": "\n💰 <b>Tổng cộng</b>: {total} {currency}",
    "cart.added": "✅ Đã thêm {name} vào giỏ.",
    "cart.full": "❌ Giỏ hàng đã đầy (tối đa 10 sản phẩm).",
    "cart.item_not_found": "❌ Không tìm thấy sản phẩm.",
    "cart.removed": "✅ Đã xóa sản phẩm khỏi giỏ.",
    "cart.cleared": "✅ Đã xóa toàn bộ giỏ hàng.",
    "cart.checkout_confirm": "Thanh toán {count} sản phẩm với tổng {total} {currency}?",
    "cart.checkout_success": "✅ Đặt hàng thành công! Đã mua {count} sản phẩm.\n\n💰 Số dư: {balance} {currency}",
    "cart.checkout_receipt": (
        "✅ Đặt hàng thành công!\n"
        "────────────\n"
        "📦 Số lượng: {count}\n"
        "💲 Tổng tiền: {total} {currency}\n"
        "👤 Người mua: @{username} ({user_id})\n"
        "🕐 Thời gian: {datetime}\n"
        "────────────\n"
        "Nhấn vào một sản phẩm để xem chi tiết:"
    ),
    "cart.checkout_fail": "❌ Thanh toán thất bại: {reason}",
    "cart.items_unavailable": "Một số sản phẩm không còn khả dụng và đã bị xóa khỏi giỏ.",
    "history.title": "📋 <b>Lịch sử giao dịch</b>",
    "history.empty": "Lịch sử giao dịch đang trống.",
    "history.topup": "💰 Nạp tiền: +{amount} {currency}",
    "history.purchase": "🛒 Mua hàng: {amount} {currency}",
    "history.referral": "🎲 Thưởng giới thiệu: +{amount} {currency}",
    "history.date": "📅 {date}",
    "review.disabled": "Tính năng đánh giá đang tắt.",
    "review.prompt_rating": "Hãy chấm <b>{name}</b> từ 1 đến 5:",
    "review.prompt_text": "Viết đánh giá (tối đa 500 ký tự) hoặc bấm Bỏ qua:",
    "review.created": "✅ Cảm ơn bạn đã đánh giá!",
    "review.already_exists": "Bạn đã đánh giá sản phẩm này rồi.",
    "review.not_purchased": "Bạn chưa mua sản phẩm này.",
    "review.avg_rating": "⭐ Điểm: {rating}/5 ({count} đánh giá)",
    "review.item": "⭐ {rating}/5 — {text}",
    "review.item_no_text": "⭐ {rating}/5",
    "review.list_title": "📝 <b>Đánh giá cho {name}</b>",
    "review.list_empty": "Chưa có đánh giá nào.",
    "promo.not_found": "❌ Không tìm thấy mã giảm giá.",
    "promo.inactive": "❌ Mã giảm giá đang bị tắt.",
    "promo.expired": "❌ Mã giảm giá đã hết hạn.",
    "promo.max_uses_reached": "❌ Mã giảm giá đã hết lượt sử dụng.",
    "promo.already_used": "❌ Bạn đã dùng mã giảm giá này rồi.",
    "promo.wrong_item": "❌ Mã giảm giá không áp dụng cho sản phẩm này.",
    "promo.wrong_category": "❌ Mã giảm giá không áp dụng cho danh mục này.",
    "promo.applied": "✅ Đã áp dụng mã <code>{code}</code>! Giảm: {discount}",
    "promo.enter_code": "Nhập mã giảm giá:",
    "promo.removed": "Đã gỡ mã giảm giá.",
    "promo.not_balance_type": "❌ Mã này không dùng để nạp số dư.",
    "promo.enter_redeem_code": "Nhập mã để đổi:",
    "promo.balance_redeemed": "✅ Đã đổi mã <code>{code}</code>! {amount} {currency} đã được cộng vào số dư.",
    "errors.not_subscribed": "Bạn chưa đăng ký kênh",
    "errors.something_wrong": "❌ Có lỗi xảy ra. Vui lòng thử lại.",
    "errors.pagination_invalid": "Dữ liệu phân trang không hợp lệ",
    "errors.invalid_data": "❌ Dữ liệu không hợp lệ",
    "errors.id_should_be_number": "❌ ID phải là số.",
    "errors.channel.telegram_not_found": "Tôi không thể gửi vào kênh. Hãy thêm tôi làm admin kênh @{channel} với quyền đăng bài.",
    "errors.channel.telegram_forbidden_error": "Không tìm thấy kênh. Hãy kiểm tra username kênh @{channel}.",
    "errors.channel.telegram_bad_request": "Không gửi được vào kênh upload: {e}",
    "errors.general_error": "❌ Lỗi: {e}",
    "middleware.ban": "⏳ Bạn đang bị chặn tạm thời. Hãy chờ {time} giây.",
    "middleware.above_limits": "⚠️ Quá nhiều yêu cầu! Bạn bị chặn tạm thời.",
    "middleware.waiting": "⏳ Hãy chờ {time} giây trước khi thao tác tiếp.",
    "middleware.security.session_outdated": "⚠️ Phiên đã cũ. Vui lòng bắt đầu lại.",
    "middleware.security.invalid_data": "❌ Dữ liệu không hợp lệ",
    "middleware.security.blocked": "❌ Truy cập bị chặn",
    "middleware.security.not_admin": "⛔ Không đủ quyền",
    "middleware.security.invalid_csrf": "⚠️ Phiên đã hết hạn. Vui lòng thử lại.",
    "maintenance.active": "🔧 Bot đang bảo trì. Vui lòng thử lại sau.",
    "admin.menu.main": "⛩️ Menu quản trị",
    "admin.menu.shop": "🛒 Quản lý cửa hàng",
    "admin.menu.goods": "📦 Quản lý sản phẩm",
    "admin.menu.categories": "📂 Quản lý danh mục",
    "admin.menu.users": "👥 Quản lý người dùng",
    "admin.menu.broadcast": "📝 Gửi thông báo",
    "admin.menu.roles": "🛡 Quản lý vai trò",
    "admin.menu.promo": "🏷 Mã khuyến mãi",
    "admin.menu.rights": "Không đủ quyền",
    "admin.menu.maintenance_on": "🔧 Bảo trì: BẬT",
    "admin.menu.maintenance_off": "🔧 Bảo trì: TẮT",
    "admin.maintenance.enabled": "✅ Đã bật chế độ bảo trì",
    "admin.maintenance.disabled": "✅ Đã tắt chế độ bảo trì",
}

VI_TRANSLATIONS.update({
    "btn.buy_direct_account": "🏦 Chuyển khoản trực tiếp",

    "btn.pay.sepay": "🏦 Chuyển khoản SePay",
    "btn.pay.sepay_account": "📷 Chi tiết chuyển khoản",
    "btn.pay.sepay_done": "✅ Tôi đã chuyển khoản",
    "btn.admin.payment_approve": "✅ Duyệt",
    "btn.admin.payment_reject": "❌ Từ chối",
    "payments.sepay.not_configured": "❌ Chưa cấu hình SePay.",
    "payments.sepay.pending_message": "Yêu cầu thanh toán SePay đã được tạo ở tin nhắn bên dưới.",
    "payments.sepay.choose_option": (
        "🏦 <b>Chuyển khoản ngân hàng</b>\n\n"
        "Số dư cần nạp: <code>{amount}</code> {currency}\n"
        "TK chính: <code>{bank_name}</code> - <code>{account_no}</code>\n\n"
        "Chọn một trong hai cách thanh toán bên dưới."
    ),
    "payments.sepay.instructions": (
        "🏦 <b>Chuyển khoản ngân hàng qua SePay</b>\n\n"
        "Số dư cần nạp: <code>{amount}</code> {currency}\n"
        "Số tiền cần chuyển: <code>{amount_vnd}</code> VND\n"
        "Ngân hàng: <code>{bank_name}</code>\n"
        "Số tài khoản: <code>{account_no}</code>\n"
        "{account_name_line}"
        "Nội dung chuyển khoản: <code>{transfer_content}</code>\n\n"
        "Hãy dùng thông tin chuyển khoản bên dưới hoặc chuyển khoản thủ công. Sau khi chuyển xong, bấm nút xác nhận bên dưới."
    ),
    "payments.sepay.account_info": (
        "🏦 <b>Thông tin TK chính</b>\n\n"
        "Ngân hàng: <code>{bank_name}</code>\n"
        "Số tài khoản: <code>{account_no}</code>\n"
        "{account_name_line}"
        "Số tiền cần chuyển: <code>{amount_vnd}</code> VND\n"
        "Nội dung chuyển khoản: <code>{transfer_content}</code>\n\n"
        "Hãy dùng thông tin này để chuyển khoản thủ công, sau đó bấm nút xác nhận."
    ),
    "payments.sepay.account_name_line": "Tên tài khoản: <code>{account_name}</code>\n",
    "payments.sepay.submitted": (
        "✅ Đã gửi yêu cầu xác nhận thanh toán SePay.\n"
        "Số tiền: <code>{amount}</code> {currency}\n"
        "Giao dịch của bạn đang chờ quản trị viên duyệt."
    ),
    "payments.sepay.submitted_alert": "Đã gửi yêu cầu xác nhận.",
    "payments.sepay.already_submitted": "Giao dịch SePay này đang chờ duyệt rồi.",
    "payments.sepay.already_rejected": "Giao dịch SePay này đã bị từ chối.",
    "payments.sepay.approved": "✅ Chuyển khoản SePay của bạn đã được xác nhận. {amount} {currency} đã được cộng vào số dư.",
    "payments.sepay.rejected": "❌ Chuyển khoản SePay của bạn bị từ chối. Nếu bạn đã thanh toán, hãy liên hệ hỗ trợ.",
    "payments.sepay.owner.review": (
        "🏦 <b>Duyệt chuyển khoản SePay</b>\n\n"
        "Mã thanh toán: <code>{payment_id}</code>\n"
        "Người dùng: <a href='tg://user?id={user_id}'>{name}</a> (<code>{user_id}</code>)\n"
        "Số dư cần nạp: <code>{amount}</code> {currency}\n"
        "Số tiền đã chuyển: <code>{amount_vnd}</code> VND\n"
        "Ngân hàng: <code>{bank_name}</code>\n"
        "Số tài khoản: <code>{account_no}</code>\n"
        "Tên tài khoản: <code>{account_name}</code>\n"
        "Nội dung chuyển khoản: <code>{transfer_content}</code>\n\n"
        "Hãy kiểm tra ứng dụng ngân hàng rồi bấm duyệt hoặc từ chối."
    ),
    "payments.sepay.owner.approved": (
        "✅ Đã duyệt thanh toán SePay.\n"
        "Mã thanh toán: <code>{payment_id}</code>\n"
        "Người dùng: <code>{user_id}</code>\n"
        "Đã cộng: <code>{amount}</code> {currency}"
    ),
    "payments.sepay.owner.rejected": (
        "❌ Đã từ chối thanh toán SePay.\n"
        "Mã thanh toán: <code>{payment_id}</code>\n"
        "Người dùng: <code>{user_id}</code>\n"
        "Yêu cầu: <code>{amount}</code> {currency}"
    ),
    "payments.sepay.owner.done": "Đã cập nhật trạng thái thanh toán SePay.",
    "shop.direct_purchase.choose_option": (
        "🛍 <b>Mua hàng trực tiếp</b>\n\n"
        "Sản phẩm: <code>{item_name}</code>\n"
        "Giá: <code>{amount}</code> {currency}\n"
        "TK chính: <code>{bank_name}</code> - <code>{account_no}</code>\n\n"
        "Chọn một trong hai cách thanh toán bên dưới."
    ),
    "shop.direct_purchase.instructions": (
        "🛍 <b>Mua hàng trực tiếp qua chuyển khoản</b>\n\n"
        "Sản phẩm: <code>{item_name}</code>\n"
        "Giá: <code>{amount}</code> {currency}\n"
        "Số tiền cần chuyển: <code>{amount_vnd}</code> VND\n"
        "Ngân hàng: <code>{bank_name}</code>\n"
        "Số tài khoản: <code>{account_no}</code>\n"
        "{account_name_line}"
        "Nội dung chuyển khoản: <code>{transfer_content}</code>\n\n"
        "Hãy dùng thông tin chuyển khoản bên dưới hoặc chuyển khoản thủ công. Sau khi chuyển xong, bấm nút xác nhận bên dưới."
    ),
    "shop.direct_purchase.account_info": (
        "🛍 <b>TK chính để mua hàng trực tiếp</b>\n\n"
        "Sản phẩm: <code>{item_name}</code>\n"
        "Giá: <code>{amount}</code> {currency}\n"
        "Ngân hàng: <code>{bank_name}</code>\n"
        "Số tài khoản: <code>{account_no}</code>\n"
        "{account_name_line}"
        "Số tiền cần chuyển: <code>{amount_vnd}</code> VND\n"
        "Nội dung chuyển khoản: <code>{transfer_content}</code>\n\n"
        "Sau khi chuyển xong, bấm nút xác nhận."
    ),
    "shop.direct_purchase.submitted": (
        "✅ Đã gửi yêu cầu mua hàng trực tiếp.\n"
        "Sản phẩm: <code>{item_name}</code>\n"
        "Số tiền: <code>{amount}</code> {currency}\n"
        "Giao dịch của bạn đang chờ quản trị viên duyệt."
    ),
    "shop.direct_purchase.submitted_alert": "Đã gửi yêu cầu mua hàng trực tiếp.",
    "shop.direct_purchase.owner.review": (
        "🛍 <b>Duyệt mua hàng trực tiếp</b>\n\n"
        "Mã thanh toán: <code>{payment_id}</code>\n"
        "Người dùng: <a href='tg://user?id={user_id}'>{name}</a> (<code>{user_id}</code>)\n"
        "Sản phẩm: <code>{item_name}</code>\n"
        "Số tiền: <code>{amount}</code> {currency}\n"
        "Số tiền đã chuyển: <code>{amount_vnd}</code> VND\n"
        "Ngân hàng: <code>{bank_name}</code>\n"
        "Số tài khoản: <code>{account_no}</code>\n"
        "{account_name_line}"
        "Nội dung chuyển khoản: <code>{transfer_content}</code>\n\n"
        "Hãy kiểm tra ngân hàng rồi bấm duyệt hoặc từ chối."
    ),
    "shop.direct_purchase.owner.approved": (
        "✅ Đã duyệt mua hàng trực tiếp.\n"
        "Mã thanh toán: <code>{payment_id}</code>\n"
        "Người dùng: <code>{user_id}</code>\n"
        "Sản phẩm: <code>{item_name}</code>\n"
        "Đã thu: <code>{amount}</code> {currency}"
    ),
    "shop.direct_purchase.owner.rejected": (
        "❌ Đã từ chối mua hàng trực tiếp.\n"
        "Mã thanh toán: <code>{payment_id}</code>\n"
        "Người dùng: <code>{user_id}</code>\n"
        "Sản phẩm: <code>{item_name}</code>\n"
        "Yêu cầu: <code>{amount}</code> {currency}"
    ),
    "shop.direct_purchase.approved_balance_only": (
        "✅ Thanh toán của bạn đã được xác nhận, nhưng bot chưa giao hàng tự động được.\n"
        "Lý do: {reason}\n"
        "{amount} {currency} đã được cộng vào số dư. Bạn có thể dùng số dư để mua lại sản phẩm."
    ),
})

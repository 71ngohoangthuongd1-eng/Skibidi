from functools import partial

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.handlers.other import generate_short_hash
from bot.i18n import localize
from bot.database.models import Permission
from bot.database.methods import get_item_info_cached, delete_item, get_goods_info, delete_item_from_position, \
    query_items_in_position, query_goods_names
from bot.keyboards.inline import back, simple_buttons, lazy_paginated_keyboard
from bot.database.methods.audit import log_audit
from bot.filters import HasPermissionFilter
from bot.misc import EnvKeys, LazyPaginator
from bot.states import GoodsFSM

router = Router()


async def _render_position_picker(
        message,
        state: FSMContext,
        page: int = 0,
        *,
        title_key: str = 'admin.goods.positions.title',
        pick_prefix: str = 'spv_',
        nav_prefix: str = 'gpp_',
        back_cb: str = "goods_management",
        state_prefix: str = "goods_picker",
):
    paginator_state = (await state.get_data()).get(f'{state_prefix}_paginator')
    paginator = LazyPaginator(query_goods_names, per_page=10, state=paginator_state)

    total = await paginator.get_total_count()
    if total == 0:
        await message.edit_text(
            localize('admin.goods.positions.empty'),
            reply_markup=back("goods_management")
        )
        await state.clear()
        return

    items = await paginator.get_page(page)
    item_hash_mapping = {
        generate_short_hash(name): name
        for name in items
    }

    markup = await lazy_paginated_keyboard(
        paginator=paginator,
        item_text=lambda name: str(name),
        item_callback=lambda name: f"{pick_prefix}{generate_short_hash(name)}",
        page=page,
        back_cb=back_cb,
        nav_cb_prefix=nav_prefix
    )

    await message.edit_text(localize(title_key), reply_markup=markup)
    await state.update_data(
        **{
            f'{state_prefix}_paginator': paginator.get_state(),
            f'{state_prefix}_item_hash_mapping': item_hash_mapping,
            f'{state_prefix}_page': page,
        }
    )


async def _render_items_in_position(message, state: FSMContext, item_name: str, page: int = 0, *, edit: bool = True):
    render = message.edit_text if edit else message.answer
    item = await get_item_info_cached(item_name)
    if not item:
        await render(
            localize('admin.goods.position.not_found'),
            reply_markup=back('show__items_in_position')
        )
        return

    query_func = partial(query_items_in_position, item_name)
    paginator_state = (await state.get_data()).get('items_in_position_paginator')
    paginator = LazyPaginator(query_func, per_page=10, state=paginator_state)

    total = await paginator.get_total_count()
    if total == 0:
        await render(
            localize('admin.goods.list_in_position.empty'),
            reply_markup=back('show__items_in_position')
        )
        return

    item_hash = generate_short_hash(item_name)
    await state.update_data(
        item_hash_mapping={item_hash: item_name},
        current_position_name=item_name
    )

    markup = await lazy_paginated_keyboard(
        paginator=paginator,
        item_text=lambda g: str(g),
        item_callback=lambda g: f"si_{g}_{item_hash}_{page}",
        page=page,
        back_cb="show__items_in_position",
        nav_cb_prefix=f"gip_{item_hash}_"
    )

    await render(localize('admin.goods.list_in_position.title'), reply_markup=markup)
    await state.update_data(items_in_position_paginator=paginator.get_state())


@router.callback_query(F.data == 'goods_management', HasPermissionFilter(permission=Permission.CATALOG_MANAGE))
async def goods_management_callback_handler(call: CallbackQuery, state):
    """
    Opens the positions (goods) management menu.
    """
    actions = [
        (localize("admin.goods.add_position"), "add_item"),
        (localize("admin.goods.add_item"), "update_item_amount"),
        (localize("admin.goods.update_position"), "update_item"),
        (localize("admin.goods.delete_position"), "delete_item"),
        (localize("admin.goods.show_items"), "show__items_in_position"),
        (localize("btn.back"), "console"),
    ]
    markup = simple_buttons(actions, per_row=1)
    await call.message.edit_text(localize('admin.goods.menu.title'), reply_markup=markup)
    await state.clear()


@router.callback_query(F.data == 'delete_item', HasPermissionFilter(permission=Permission.CATALOG_MANAGE))
async def delete_item_callback_handler(call: CallbackQuery, state):
    """
    Requests a position name to delete.
    """
    await _render_position_picker(
        call.message,
        state,
        0,
        title_key='admin.goods.delete.prompt.name',
        pick_prefix='sdel_',
        nav_prefix='gdel_',
        back_cb='goods_management',
        state_prefix='delete_goods_picker',
    )
    await state.set_state(GoodsFSM.waiting_item_name_delete)


@router.message(GoodsFSM.waiting_item_name_delete, F.text)
async def delete_str_item(message: Message, state):
    """
    Deletes a position by the provided name.
    """
    item_name = message.text
    item = await get_item_info_cached(item_name)
    if not item:
        await message.answer(
            localize('admin.goods.delete.position.not_found'),
            reply_markup=back('goods_management')
        )
    else:
        await delete_item(item_name)
        await message.answer(
            localize('admin.goods.delete.position.success'),
            reply_markup=back('goods_management')
        )
        admin_info = await message.bot.get_chat(message.from_user.id)
        await log_audit("delete_item", user_id=message.from_user.id, resource_type="Item", resource_id=item_name, details=f"admin={admin_info.first_name}")
    await state.clear()


@router.callback_query(F.data.startswith('gdel_'), HasPermissionFilter(permission=Permission.CATALOG_MANAGE))
async def navigate_delete_item_picker(call: CallbackQuery, state: FSMContext):
    try:
        page = int(call.data.split('_', 1)[1])
    except (TypeError, ValueError):
        page = 0
    await _render_position_picker(
        call.message,
        state,
        page,
        title_key='admin.goods.delete.prompt.name',
        pick_prefix='sdel_',
        nav_prefix='gdel_',
        back_cb='goods_management',
        state_prefix='delete_goods_picker',
    )


@router.callback_query(F.data.startswith('sdel_'), HasPermissionFilter(permission=Permission.CATALOG_MANAGE))
async def delete_item_from_picker(call: CallbackQuery, state: FSMContext):
    item_hash = call.data[5:]
    item_name = (await state.get_data()).get('delete_goods_picker_item_hash_mapping', {}).get(item_hash)
    if not item_name:
        await call.answer(localize('errors.invalid_data'), show_alert=True)
        return

    item = await get_item_info_cached(item_name)
    if not item:
        await call.message.edit_text(
            localize('admin.goods.delete.position.not_found'),
            reply_markup=back('goods_management')
        )
    else:
        await delete_item(item_name)
        await call.message.edit_text(
            localize('admin.goods.delete.position.success'),
            reply_markup=back('goods_management')
        )
        admin_info = await call.message.bot.get_chat(call.from_user.id)
        await log_audit("delete_item", user_id=call.from_user.id, resource_type="Item", resource_id=item_name, details=f"admin={admin_info.first_name}")
    await state.clear()


@router.callback_query(F.data == 'show__items_in_position', HasPermissionFilter(permission=Permission.CATALOG_MANAGE))
async def show_items_callback_handler(call: CallbackQuery, state):
    """
    Show product buttons to choose which product's values to view.
    """
    await _render_position_picker(call.message, state, 0)


@router.callback_query(F.data.startswith('gpp_'), HasPermissionFilter(permission=Permission.CATALOG_MANAGE))
async def navigate_position_picker(call: CallbackQuery, state: FSMContext):
    try:
        page = int(call.data.split('_', 1)[1])
    except (TypeError, ValueError):
        page = 0
    await _render_position_picker(call.message, state, page)


@router.callback_query(F.data.startswith('spv_'), HasPermissionFilter(permission=Permission.CATALOG_MANAGE))
async def show_position_from_picker(call: CallbackQuery, state: FSMContext):
    payload = call.data[4:]
    try:
        item_hash, page_str = payload.rsplit('_', 1)
        page = int(page_str)
    except (TypeError, ValueError):
        item_hash, page = payload, 0

    data = await state.get_data()
    item_name = data.get('picker_item_hash_mapping', {}).get(item_hash)
    if not item_name:
        await call.answer(localize('errors.invalid_data'), show_alert=True)
        return

    await state.update_data(goods_picker_page=page)
    await _render_items_in_position(call.message, state, item_name, 0)


@router.message(GoodsFSM.waiting_item_name_show, F.text)
async def show_str_item(message: Message, state: FSMContext):
    """
    Shows all items in the selected position with lazy loading pagination.
    """
    item_name = message.text.strip()
    await _render_items_in_position(message, state, item_name, 0, edit=False)


@router.callback_query(F.data.startswith('gip_'), HasPermissionFilter(permission=Permission.CATALOG_MANAGE))
async def navigate_items_in_goods(call: CallbackQuery, state: FSMContext):
    """
    Paginates items inside a position with lazy loading.
    Callback data format: gip_{item_hash}_{page}
    """
    payload = call.data[4:]  # Remove 'gip_'
    try:
        item_hash, page_str = payload.rsplit('_', 1)
        current_index = int(page_str)
    except ValueError:
        item_hash, current_index = payload, 0

    # Get saved state
    data = await state.get_data()
    paginator_state = data.get('items_in_position_paginator')
    item_hash_mapping = data.get('item_hash_mapping', {})

    # Get the actual item name from hash
    item_name = item_hash_mapping.get(item_hash)
    if not item_name:
        # Try to get it from current_position_name
        item_name = data.get('current_position_name')
        if not item_name:
            await call.answer(localize('errors.invalid_data'), show_alert=True)
            return

    # Create paginator with cached state
    query_func = partial(query_items_in_position, item_name)
    paginator = LazyPaginator(query_func, per_page=10, state=paginator_state)

    # Check if there are any items
    total = await paginator.get_total_count()
    if total == 0:
        await call.message.edit_text(
            localize('admin.goods.list_in_position.empty'),
            reply_markup=back('goods_management')
        )
        return

    markup = await lazy_paginated_keyboard(
        paginator=paginator,
        item_text=lambda g: str(g),
        item_callback=lambda g: f"si_{g}_{item_hash}_{current_index}",
        page=current_index,
        back_cb="show__items_in_position",
        nav_cb_prefix=f"gip_{item_hash}_"
    )

    await call.message.edit_text(localize('admin.goods.list_in_position.title'), reply_markup=markup)

    # Update state
    await state.update_data(
        items_in_position_paginator=paginator.get_state(),
        current_position_name=item_name,
        item_hash_mapping={item_hash: item_name}
    )


@router.callback_query(F.data.startswith('si_'), HasPermissionFilter(permission=Permission.CATALOG_MANAGE))
async def item_info_callback_handler(call: CallbackQuery, state: FSMContext):
    """
    Shows details for a specific item within a position.
    Callback data format: si_{id}_{item_hash}_{page}
    """
    payload = call.data[3:]  # Remove 'si_'

    # Parse compact format
    parts = payload.split('_')
    if len(parts) < 2:
        await call.answer(localize("admin.goods.item.invalid"), show_alert=True)
        return

    item_id_str = parts[0]
    item_hash = parts[1] if len(parts) > 1 else ""
    page = parts[2] if len(parts) > 2 else "0"

    try:
        item_id = int(item_id_str)
    except ValueError:
        await call.answer(localize("admin.goods.item.invalid_id"), show_alert=True)
        return

    item_info = await get_goods_info(item_id)
    if not item_info:
        await call.answer(localize("admin.goods.item.not_found"), show_alert=True)
        return

    position_info = await get_item_info_cached(item_info["item_name"])

    # Store item info in state for delete handler
    await state.update_data(
        delete_item_id=item_id,
        delete_item_hash=item_hash,
        delete_page=page,
        delete_item_name=item_info["item_name"]
    )

    actions = [
        (localize("admin.goods.item.delete.button"), f"dip_{item_id}"),  # Simplified callback
        (localize("btn.back"), f"gip_{item_hash}_{page}"),
    ]
    markup = simple_buttons(actions, per_row=1)

    text = (
        f'{localize("admin.goods.item.info.position", name=item_info["item_name"])}\n'
        f'{localize("admin.goods.item.info.price", price=position_info["price"], currency=EnvKeys.PAY_CURRENCY)}\n'
        f'{localize("admin.goods.item.info.id", id=item_info["id"])}\n'
        f'{localize("admin.goods.item.info.value", value=item_info["value"])}'
    )

    await call.message.edit_text(text, parse_mode='HTML', reply_markup=markup)


@router.callback_query(
    F.data.startswith('dip_'),  # Shortened from 'delete-item-from-position_'
    HasPermissionFilter(permission=Permission.CATALOG_MANAGE)
)
async def process_delete_item_from_position(call: CallbackQuery, state: FSMContext):
    """
    Delete item from position and refresh the list with lazy loading.
    Callback data format: dip_{id}
    """
    payload = call.data[4:]  # Remove 'dip_'
    try:
        item_id = int(payload)
    except ValueError:
        await call.answer(localize("admin.goods.item.invalid"), show_alert=True)
        return

    # Get stored data from state
    data = await state.get_data()
    item_hash = data.get('delete_item_hash', '')
    page = data.get('delete_page', '0')
    item_name = data.get('delete_item_name', '')

    item_info = await get_goods_info(item_id)
    if not item_info:
        await call.answer(localize("admin.goods.item.already_deleted_or_missing"), show_alert=True)
        await call.message.edit_text(
            localize("admin.goods.list_in_position.title"),
            reply_markup=back(f"gip_{item_hash}_{page}")
        )
        return

    position_name = item_info["item_name"]
    await delete_item_from_position(item_id)

    # Redraw the list page if needed
    if item_hash and item_name:
        try:
            page_int = int(page)
        except Exception:
            await call.message.edit_text(
                localize('admin.goods.item.deleted'),
                reply_markup=back(f"gip_{item_hash}_{page}")
            )
            return

        # Get saved state
        paginator_state = data.get('items_in_position_paginator')

        # Create paginator with cached state (but clear cache to refresh after deletion)
        from bot.database.methods.lazy_queries import query_items_in_position
        from functools import partial
        from bot.misc.lazy_paginator import LazyPaginator

        query_func = partial(query_items_in_position, item_name)
        paginator = LazyPaginator(query_func, per_page=10, state=paginator_state)

        # Clear cache to force reload after deletion
        paginator.clear_cache()

        # Check if there are any items left
        total = await paginator.get_total_count()
        if total == 0:
            await call.message.edit_text(
                localize('admin.goods.list_in_position.empty'),
                reply_markup=back("show__items_in_position")
            )
        else:
            # Adjust page if needed (if deleted last item on last page)
            max_page = max((total - 1) // 10, 0)
            page_int = max(0, min(page_int, max_page))

            markup = await lazy_paginated_keyboard(
                paginator=paginator,
                item_text=lambda g: str(g),
                item_callback=lambda g: f"si_{g}_{item_hash}_{page_int}",
                page=page_int,
                back_cb="show__items_in_position",
                nav_cb_prefix=f"gip_{item_hash}_"
            )

            await call.message.edit_text(
                f'{localize("admin.goods.item.deleted")}\n\n{localize("admin.goods.list_in_position.title")}',
                reply_markup=markup
            )

            # Update state with new paginator
            await state.update_data(
                items_in_position_paginator=paginator.get_state(),
                item_hash_mapping={item_hash: item_name}
            )
    else:
        await call.message.edit_text(
            localize('admin.goods.item.deleted'),
            reply_markup=back("goods_management")
        )

    admin_info = await call.message.bot.get_chat(call.from_user.id)
    await log_audit("delete_item_value", user_id=call.from_user.id, resource_type="ItemValue", resource_id=str(item_id), details=f"admin={admin_info.first_name}, position={position_name or '<?>'}")

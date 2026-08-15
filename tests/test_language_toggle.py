"""Tests for the main-menu language toggle.

Coverage:
- The main menu exposes a single direct-switch button (no intermediate picker).
- It targets the opposite language based on the user's current locale.
- The locale is persisted through the project's existing store mechanism.
- The old guidance line in ``menu.title`` has been removed for EN/VI.
"""

import bot.i18n.store as store
from bot.i18n.main import localize, set_active_locale, reset_active_locale
from bot.keyboards.inline import main_menu


def _buttons(markup):
    return [b for row in markup.inline_keyboard for b in row]


def _toggle_button(markup):
    for b in _buttons(markup):
        if b.callback_data and b.callback_data.startswith("lang_set:"):
            return b
    return None


class TestToggleButton:

    def test_vi_locale_shows_english_toggle(self):
        set_active_locale("vi")
        try:
            markup = main_menu(role=0)
        finally:
            reset_active_locale()

        btn = _toggle_button(markup)
        assert btn is not None
        assert btn.text == "🇬🇧 English"
        assert btn.callback_data == "lang_set:en"

    def test_en_locale_shows_vietnamese_toggle(self):
        set_active_locale("en")
        try:
            markup = main_menu(role=0)
        finally:
            reset_active_locale()

        btn = _toggle_button(markup)
        assert btn is not None
        assert btn.text == "🇻🇳 Tiếng Việt"
        assert btn.callback_data == "lang_set:vi"

    def test_no_intermediate_language_menu_anymore(self):
        set_active_locale("vi")
        try:
            markup = main_menu(role=0)
        finally:
            reset_active_locale()

        cbs = [b.callback_data for b in _buttons(markup)]
        assert "language_menu" not in cbs
        assert "🌐" not in [b.text for b in _buttons(markup)]


class TestMenuTitleGuidance:

    def test_en_menu_title_has_no_language_hint(self):
        set_active_locale("en")
        try:
            title = localize("menu.title")
        finally:
            reset_active_locale()
        assert "Need another language" not in title
        assert 'Tap "Language"' not in title

    def test_vi_menu_title_has_no_language_hint(self):
        set_active_locale("vi")
        try:
            title = localize("menu.title")
        finally:
            reset_active_locale()
        assert "Muốn đổi ngôn ngữ" not in title
        assert "Ngôn ngữ" not in title


class TestLocalePersistence:

    def test_set_user_locale_roundtrip(self, tmp_path, monkeypatch):
        monkeypatch.setenv("USER_LOCALES_DIR", str(tmp_path))
        store._CACHE = None
        store._CACHE_PATH = None
        try:
            assert store.set_user_locale(555777, "en") == "en"
            assert store.get_user_locale(555777) == "en"

            assert store.set_user_locale(555777, "vi") == "vi"
            assert store.get_user_locale(555777) == "vi"
        finally:
            store._CACHE = None
            store._CACHE_PATH = None

    def test_unknown_user_has_no_locale(self, tmp_path, monkeypatch):
        monkeypatch.setenv("USER_LOCALES_DIR", str(tmp_path))
        store._CACHE = None
        store._CACHE_PATH = None
        try:
            assert store.get_user_locale(123) is None
        finally:
            store._CACHE = None
            store._CACHE_PATH = None
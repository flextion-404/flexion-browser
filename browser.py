import os
import sys
import time
import json
import math
import random
import base64
from string import Template
from urllib.parse import quote_plus, urlparse, quote

if sys.platform == "win32":
    import winreg
else:
    winreg = None

os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = " ".join([
    "--enable-gpu-rasterization", "--enable-zero-copy",
    "--ignore-gpu-blocklist", "--enable-accelerated-video-decode",
    "--enable-smooth-scrolling", "--use-gl=angle", "--use-angle=default",
    "--enable-native-gpu-memory-buffers", "--num-raster-threads=4",
    "--disable-quic",
])

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTabWidget, QTabBar, QLabel,
    QComboBox, QFormLayout, QFrame, QStackedWidget, QTableWidget,
    QTableWidgetItem, QFileDialog, QMessageBox, QHeaderView,
    QAbstractItemView, QMenu, QInputDialog, QDialog, QScrollArea,
    QProgressBar, QSizePolicy, QStyleOptionTab, QGridLayout,
    QToolButton, QColorDialog, QSplitter, QToolTip,
    QGraphicsOpacityEffect,
)
from PyQt6.QtCore import (
    QUrl, QTimer, Qt, QEvent, QObject, pyqtSlot, pyqtSignal,
    QSettings, QStandardPaths, QPropertyAnimation, pyqtProperty,
    QSize, QPointF, QPoint, QRectF, QRect,
    QEasingCurve, QVariantAnimation,
)
from PyQt6.QtGui import (
    QAction, QKeySequence, QPainter, QColor, QBrush, QPixmap, QPen,
    QIcon, QPolygonF, QFont, QPainterPath, QCursor, QShortcut,
    QFontDatabase, QLinearGradient, QRadialGradient, QFontMetrics,
    QPixmapCache,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import (
    QWebEngineProfile, QWebEngineSettings,
    QWebEngineUrlRequestInterceptor, QWebEnginePage,
)
from PyQt6.QtWebChannel import QWebChannel


APP_NAME = "Flexion Browser"
APP_KEY = "FlexionBrowser"
APP_VERSION = "1.0"
GITHUB_USERNAME = "flextion-404"
GITHUB_URL = f"https://github.com/{GITHUB_USERNAME}"

CACHE_DIR = os.path.join(os.path.expanduser("~"), ".flexion")
os.makedirs(CACHE_DIR, exist_ok=True)
ICONS_DIR = os.path.join(CACHE_DIR, "icons")
os.makedirs(ICONS_DIR, exist_ok=True)
PASSWORDS_FILE = os.path.join(CACHE_DIR, "passwords.json")
HISTORY_FILE = os.path.join(CACHE_DIR, "history.json")
BOOKMARKS_FILE = os.path.join(CACHE_DIR, "bookmarks.json")

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/130.0.0.0 Safari/537.36")

SEARCH_ENGINES = {
    "DuckDuckGo": {"home": "https://duckduckgo.com",
                   "search": "https://duckduckgo.com/?q={}"},
    "Google": {"home": "https://www.google.com",
               "search": "https://www.google.com/search?q={}"},
    "Brave Search": {"home": "https://search.brave.com",
                     "search": "https://search.brave.com/search?q={}"},
    "Microsoft Bing": {"home": "https://www.bing.com",
                       "search": "https://www.bing.com/search?q={}"},
    "Yahoo!": {"home": "https://search.yahoo.com",
               "search": "https://search.yahoo.com/search?p={}"},
}

HOME_OPTIONS_ORDER = ["home", "empty", "ddg", "brave", "google", "bing", "yahoo"]
HOME_LABELS = {
    "home": "home_opt_home", "empty": "home_opt_empty", "ddg": "home_opt_ddg",
    "brave": "home_opt_brave", "google": "home_opt_google",
    "bing": "home_opt_bing", "yahoo": "home_opt_yahoo",
}
HOME_URLS = {
    "ddg": SEARCH_ENGINES["DuckDuckGo"]["home"],
    "brave": SEARCH_ENGINES["Brave Search"]["home"],
    "google": SEARCH_ENGINES["Google"]["home"],
    "bing": SEARCH_ENGINES["Microsoft Bing"]["home"],
    "yahoo": SEARCH_ENGINES["Yahoo!"]["home"],
}

UI_FONTS = ["Segoe UI", "Arial", "Calibri", "Verdana", "Tahoma",
            "Helvetica", "Roboto", "Open Sans", "Ubuntu", "Inter",
            "Consolas", "Courier New", "Georgia", "Times New Roman"]

DENSITY_PRESETS = {
    "auto": {"btn_pad": "5px 16px", "input_pad": "6px 14px",
             "tab_h": 30, "tab_min_w": 100, "tab_max_w": 220,
             "tab_radius": 15.0, "tab_extra": 32, "title_bar_h": 44,
             "nav_btn_size": 34, "nav_btn_h": 28,
             "nav_margin": 6, "nav_spacing": 6},
    "standard": {"btn_pad": "5px 16px", "input_pad": "6px 14px",
                 "tab_h": 30, "tab_min_w": 100, "tab_max_w": 220,
                 "tab_radius": 15.0, "tab_extra": 32, "title_bar_h": 44,
                 "nav_btn_size": 34, "nav_btn_h": 28,
                 "nav_margin": 6, "nav_spacing": 6},
    "compact": {"btn_pad": "2px 12px", "input_pad": "3px 12px",
                "tab_h": 22, "tab_min_w": 70, "tab_max_w": 170,
                "tab_radius": 11.0, "tab_extra": 24, "title_bar_h": 34,
                "nav_btn_size": 28, "nav_btn_h": 22,
                "nav_margin": 4, "nav_spacing": 4},
    "touch": {"btn_pad": "10px 22px", "input_pad": "11px 20px",
              "tab_h": 42, "tab_min_w": 130, "tab_max_w": 280,
              "tab_radius": 21.0, "tab_extra": 40, "title_bar_h": 58,
              "nav_btn_size": 46, "nav_btn_h": 38,
              "nav_margin": 8, "nav_spacing": 8},
}

TRANSLATE_LANGS = {
    "ru": "Русский", "en": "English", "uk": "Українська",
    "de": "Deutsch", "fr": "Français", "es": "Español",
    "it": "Italiano", "pt": "Português", "pl": "Polski",
    "tr": "Türkçe", "zh-CN": "中文 (简体)", "ja": "日本語",
    "ko": "한국어", "ar": "العربية", "hi": "हिन्दी",
}

LIVE_WALLPAPER_MODES = [
    "none",
    "gradient", "stars", "snow", "aurora", "bubbles",
    "matrix", "rain", "fireflies", "confetti", "parallax",
    "particles", "rings", "hex", "plasma", "nebula",
    "waves", "lightning", "pulse", "ink", "vortex", "grid",
]

SETTINGS_THEME = 0
SETTINGS_COLORS = 1
SETTINGS_SEARCH = 2
SETTINGS_ZOOM = 3
SETTINGS_DOWNLOADS = 4
SETTINGS_PASSWORDS = 5
SETTINGS_HISTORY = 6
SETTINGS_BOOKMARKS = 7
SETTINGS_SYSTEM = 8
SETTINGS_ABOUT = 9


def _fmt_size(n):
    try:
        n = float(n)
    except (TypeError, ValueError):
        return "0 B"
    if n <= 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while n >= 1024.0 and i < len(units) - 1:
        n /= 1024.0
        i += 1
    return f"{int(n)} {units[i]}" if i == 0 else f"{n:.1f} {units[i]}"


DARK_CSS = """
html, body { background-color: #ffffff !important; }
html { filter: invert(90%) hue-rotate(180deg) !important; }
img, video, svg, iframe, picture, canvas,
[style*="background-image"], [style*="background: url"] {
    filter: invert(100%) hue-rotate(180deg) !important;
}
"""

CHECK_DARK_JS = """
(function() {
    try {
        var el = document.body || document.documentElement;
        if (!el) return false;
        var bg = window.getComputedStyle(el).backgroundColor;
        if (!bg || bg === 'transparent' || bg === 'rgba(0, 0, 0, 0)') {
            bg = window.getComputedStyle(document.documentElement).backgroundColor;
        }
        var m = bg.match(/\\d+/g);
        if (!m || m.length < 3) return false;
        var r = parseInt(m[0]), g = parseInt(m[1]), b = parseInt(m[2]);
        var brightness = (r * 299 + g * 587 + b * 114) / 1000;
        return brightness < 110;
    } catch (e) { return false; }
})();
"""

# Middle-click autoscroll. Speeds up to 120 px/frame at 150+ px distance.
AUTOSCROLL_JS = """
(function() {
    if (window.__flexionAutoscroll) return;
    window.__flexionAutoscroll = true;
    var ACCENT = '__ACCENT__';
    var BG = 'rgba(24, 24, 28, 0.75)';

    var indicator = null, dot = null;
    var active = false;
    var startX = 0, startY = 0, curX = 0, curY = 0;
    var rafId = null;
    var suppressUntil = 0;
    var moveHandler = null;

    function createIndicator(x, y) {
        indicator = document.createElement('div');
        indicator.style.cssText =
            'position: fixed;' +
            'left: ' + (x - 22) + 'px; top: ' + (y - 22) + 'px;' +
            'width: 44px; height: 44px;' +
            'border-radius: 50%;' +
            'background: ' + BG + ';' +
            'border: 2px solid ' + ACCENT + ';' +
            'box-shadow: 0 4px 18px rgba(0,0,0,0.5);' +
            'z-index: 2147483647;' +
            'pointer-events: none;' +
            'box-sizing: border-box;' +
            'display: flex; align-items: center; justify-content: center;';
        dot = document.createElement('div');
        dot.style.cssText =
            'width: 12px; height: 12px;' +
            'background: ' + ACCENT + ';' +
            'border-radius: 50%;' +
            'box-shadow: 0 0 8px ' + ACCENT + ';' +
            'transition: transform 40ms linear;';
        indicator.appendChild(dot);
        (document.body || document.documentElement).appendChild(indicator);
    }

    function removeIndicator() {
        if (indicator && indicator.parentNode) indicator.parentNode.removeChild(indicator);
        indicator = null;
        dot = null;
    }

    function tick() {
        if (!active) return;
        var dx = curX - startX;
        var dy = curY - startY;
        var dist = Math.sqrt(dx*dx + dy*dy);
        if (dist > 6) {
            // Speed ramps up linearly with distance, capped at 120 px/frame at 150px
            var maxSpeed = 120;
            var maxDist = 150;
            var factor = Math.min(1, dist / maxDist);
            var speed = maxSpeed * factor;
            var vx = (dx / dist) * speed;
            var vy = (dy / dist) * speed;
            try {
                window.scrollBy({left: vx, top: vy, behavior: 'instant'});
            } catch (e) {
                window.scrollBy(vx, vy);
            }
        }
        rafId = requestAnimationFrame(tick);
    }

    function stop() {
        active = false;
        if (rafId) { cancelAnimationFrame(rafId); rafId = null; }
        removeIndicator();
        if (moveHandler) {
            document.removeEventListener('mousemove', moveHandler, true);
            moveHandler = null;
        }
    }

    document.addEventListener('mousedown', function(e) {
        if (e.button !== 1) return;

        if (active) {
            e.preventDefault();
            e.stopPropagation();
            suppressUntil = Date.now() + 500;
            stop();
            return;
        }

        var t = e.target;
        if (t && t.closest && t.closest('a')) return;
        if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable)) return;

        e.preventDefault();
        e.stopPropagation();
        active = true;
        startX = e.clientX; startY = e.clientY;
        curX = startX; curY = startY;
        createIndicator(startX, startY);
        suppressUntil = Date.now() + 500;

        moveHandler = function(ev) {
            curX = ev.clientX; curY = ev.clientY;
            var ddx = curX - startX, ddy = curY - startY;
            var d = Math.sqrt(ddx*ddx + ddy*ddy);
            var mx = d > 0 ? (ddx/d) * Math.min(d/3, 14) : 0;
            var my = d > 0 ? (ddy/d) * Math.min(d/3, 14) : 0;
            if (dot) dot.style.transform = 'translate(' + mx + 'px, ' + my + 'px)';
        };
        document.addEventListener('mousemove', moveHandler, true);
        rafId = requestAnimationFrame(tick);
    }, true);

    document.addEventListener('mouseup', function(e) {
        if (e.button !== 1) return;
        if (Date.now() < suppressUntil) {
            e.preventDefault();
            e.stopPropagation();
        }
    }, true);

    document.addEventListener('auxclick', function(e) {
        if (e.button !== 1) return;
        if (Date.now() < suppressUntil) {
            e.preventDefault();
            e.stopPropagation();
        }
    }, true);
})();
"""

SMOOTH_SCROLL_ON_JS = """
(function() {
    var s = document.getElementById('__flexion_smooth__');
    if (!s) {
        s = document.createElement('style');
        s.id = '__flexion_smooth__';
        (document.head || document.documentElement).appendChild(s);
    }
    s.textContent = 'html, body { scroll-behavior: smooth !important; }';
})();
"""

SMOOTH_SCROLL_OFF_JS = """
(function() {
    var s = document.getElementById('__flexion_smooth__');
    if (!s) {
        s = document.createElement('style');
        s.id = '__flexion_smooth__';
        (document.head || document.documentElement).appendChild(s);
    }
    s.textContent = 'html, body { scroll-behavior: auto !important; }';
})();
"""


LANG = {
    "ru": {
        "sb_theme": "Кастомизация", "sb_search": "Поисковые системы",
        "sb_zoom": "Масштаб", "sb_downloads": "Загрузки",
        "sb_passwords": "Логины и пароли", "sb_language": "Система",
        "sb_about": "О браузере", "sb_history": "История",
        "sb_bookmarks": "Закладки",
        "settings_search_placeholder": "Поиск по настройкам...",
        "theme_title": "Кастомизация",
        "theme_sub": "Темы, цвета и обои в одном разделе.",
        "theme_label": "Тема:",
        "dark_sites_label": "Тёмная тема для сайтов",
        "dark_sites_sub": "Применяет тёмную тему к светлым сайтам. Тёмные сайты остаются без изменений.",
        "close_glow_label": "Красная вспышка при закрытии",
        "close_glow_sub": "Подсвечивает вкладку красным при закрытии.",
        "window_section_title": "Окно браузера",
        "hide_wall_btn_label": "Скрыть кнопку выбора обоев",
        "hide_wall_btn_sub": "Убирает кнопку выбора обоев с новой вкладки.",
        "rtl_label": "Отражение интерфейса",
        "rtl_sub": "Зеркальное отображение панели навигации и контента (RTL).",
        "smooth_scroll_label": "Плавная прокрутка",
        "smooth_scroll_sub": "Плавная прокрутка колесом мыши — работает и в веб-страницах, и в интерфейсе.",
        "custom_colors_title": "Пользовательские цвета",
        "custom_colors_sub": "Переопределение цветов темы. Клик — выбор цвета, ПКМ — сброс к значениям темы.",
        "color_text": "Текст", "color_text2": "Второстепенный",
        "color_bg": "Фон", "color_panel": "Панель",
        "color_border": "Границы", "color_hover": "Наведение",
        "color_accent": "Акцент", "color_accent_text": "Текст на акценте",
        "reset_colors": "Сбросить цвета",
        "wallpaper_settings_title": "Обои",
        "wallpaper_settings_sub": "Статические обои или анимированные фоны.",
        "wallpaper_pick": "Изменить...", "wallpaper_reset": "Сбросить",
        "wallpaper_current": "Текущие обои:",
        "wallpaper_none": "Не заданы (цвет темы)",
        "live_wall_title": "Живые обои",
        "live_wall_sub": "Анимированный фон. Работает только на активной вкладке, минимальная нагрузка на процессор.",
        "live_none": "Выключены", "live_gradient": "Градиент",
        "live_stars": "Звёздное небо", "live_snow": "Снег",
        "live_aurora": "Северное сияние", "live_bubbles": "Пузыри",
        "live_matrix": "Матрица", "live_rain": "Дождь",
        "live_fireflies": "Светлячки", "live_confetti": "Конфетти",
        "live_parallax": "Параллакс", "live_particles": "Частицы",
        "live_rings": "Кольца", "live_hex": "Гексагоны",
        "live_plasma": "Плазма", "live_nebula": "Туманность",
        "live_waves": "Волны", "live_lightning": "Молнии",
        "live_pulse": "Пульс", "live_ink": "Чернила",
        "live_vortex": "Вихрь", "live_grid": "Сетка",
        "live_speed": "Скорость",
        "search_title": "Поисковые системы",
        "search_sub": "Параметры поиска и домашней страницы.",
        "search_engine_label": "Поисковая система:",
        "search_engine_desc": "Используется для поиска из адресной строки.",
        "home_section_title": "Домашняя страница",
        "home_section_sub": "Что открывать при запуске браузера и создании новых вкладок.",
        "home_new_windows": "Новые окна",
        "home_new_windows_sub": "Что открывать при запуске браузера.",
        "home_new_tabs": "Новые вкладки",
        "home_new_tabs_sub": "Что открывать при создании новой вкладки.",
        "home_opt_home": "Домашняя страница", "home_opt_empty": "Пустая страница",
        "home_opt_ddg": "DuckDuckGo", "home_opt_brave": "Brave Search",
        "home_opt_google": "Google", "home_opt_bing": "Microsoft Bing",
        "home_opt_yahoo": "Yahoo!",
        "zoom_title": "Масштаб", "zoom_sub": "Настройки масштаба страниц и текста.",
        "page_zoom_label": "Масштаб страницы",
        "page_zoom_sub": "Масштабирование содержимого страницы.",
        "text_zoom_label": "Масштаб текста",
        "text_zoom_sub": "Изменение размера шрифтов.",
        "downloads_title": "Загрузки", "downloads_sub": "Параметры скачивания файлов.",
        "dl_path_label": "Папка загрузок",
        "dl_path_sub": "Расположение для сохранения скачанных файлов.",
        "passwords_title": "Логины и пароли",
        "passwords_sub": "Сохранённые учётные данные. Хранятся локально.",
        "col_site": "Сайт", "col_login": "Логин", "col_password": "Пароль",
        "history_title": "История",
        "history_sub": "Все посещённые страницы. Удаление отдельных записей или полная очистка.",
        "history_col_title": "Заголовок",
        "history_col_url": "Адрес",
        "history_open": "Открыть",
        "history_delete": "Удалить выбранное",
        "history_clear_all": "Очистить историю",
        "history_clear_confirm": "Удалить всю историю посещений?",
        "history_empty": "История пуста",
        "bookmarks_title": "Закладки",
        "bookmarks_sub": "Сохранённые страницы. Двойной клик открывает закладку.",
        "col_bm_title": "Название",
        "col_bm_url": "Адрес",
        "bm_open": "Открыть",
        "bm_delete": "Удалить выбранное",
        "bm_clear_all": "Очистить закладки",
        "bm_clear_confirm": "Удалить все закладки?",
        "bm_empty": "Закладок нет",
        "bm_open_new_tab": "Открыть в новой вкладке",
        "bm_open_new_window": "Открыть в новом окне",
        "bm_edit": "Изменить название",
        "tip_bookmark": "Добавить в закладки (Ctrl+D)",
        "tip_unbookmark": "Убрать из закладок",
        "menu_bookmarks": "Закладки",
        "bookmark_bar_label": "Показывать панель закладок",
        "bookmark_bar_sub": "Полоса с закладками под адресной строкой. Ctrl+B переключает.",
        "ctx_bookmark_link": "Добавить ссылку в закладки",
        "ctx_add_bookmark": "Добавить страницу в закладки",
        "ctx_remove_bookmark": "Убрать из закладок",
        "bm_added": "Добавлено в закладки",
        "bm_removed": "Удалено из закладок",
        "language_title": "Система",
        "language_sub": "Параметры системы и языка интерфейса.",
        "language_label": "Язык интерфейса",
        "language_sub2": "Язык кнопок, меню и подписей браузера.",
        "autostart_label": "Запуск при старте системы",
        "autostart_sub": "Автоматически запускать Flexion при старте системы.",
        "restore_tabs_label": "Сохранять открытые вкладки",
        "restore_tabs_sub": "Восстанавливать вкладки при следующем запуске.",
        "layout_title": "Расположение панели", "layout_label": "Расположение",
        "layout_sub": "Размещение панели навигации.",
        "pos_top": "Сверху", "pos_bottom": "Снизу",
        "font_section_title": "Шрифт",
        "font_section_sub": "Семейство шрифта применяется ко всему интерфейсу.",
        "font_family_label": "Семейство шрифта",
        "font_family_sub": "Выберите шрифт из установленных в системе.",
        "browsing_data_title": "Данные просмотра",
        "browsing_data_sub": "Кэш ускоряет загрузку, куки сохраняют сессии, история хранит посещённые сайты.",
        "clear_cache": "Очистить кэш", "clear_cookies": "Удалить куки",
        "clear_history": "Очистить историю", "clear_all": "Удалить всё",
        "clear_done_title": "Готово", "clear_cache_done": "Кэш браузера очищен.",
        "clear_cookies_done": "Куки и связанные данные удалены.",
        "clear_history_done": "История посещений очищена.",
        "clear_all_confirm_title": "Удалить все данные?",
        "clear_all_confirm_msg": "Будут удалены кэш, куки, история и сохранённые вкладки. Для входа на сайты потребуется авторизация заново.",
        "clear_all_done": "Все данные просмотра удалены.",
        "density_title": "Плотность окна",
        "density_sub": "Настройка плотности интерфейса.",
        "density_auto": "Автоматически",
        "density_auto_sub": "Автоматический выбор плотности интерфейса.",
        "density_standard": "Стандартная",
        "density_standard_sub": "Сбалансированная плотность для большинства экранов.",
        "density_compact": "Компактная",
        "density_compact_sub": "Уменьшенные интервалы для небольших экранов.",
        "density_touch": "Сенсорная",
        "density_touch_sub": "Увеличенные элементы для сенсорных экранов.",
        "btn_change": "Изменить...", "btn_open": "Открыть",
        "btn_add": "Добавить", "btn_delete": "Удалить выбранное",
        "btn_cancel": "Отмена",
        "site_field": "Сайт (домен):", "login_field": "Логин:",
        "password_field": "Пароль:", "new_entry": "Новая запись",
        "tip_back": "Назад", "tip_forward": "Вперёд", "tip_reload": "Обновить",
        "tip_downloads": "Загрузки", "tip_settings": "Меню",
        "tip_search": "Настройки поисковой системы", "tip_translate": "Перевести",
        "url_placeholder": "Введите адрес или поисковый запрос...",
        "new_tab_title": "Новая вкладка", "settings_tab_title": "Настройки",
        "about_tab_title": "О браузере",
        "no_downloads": "Загрузок нет", "dl_open_folder": "Открыть папку",
        "dl_open_file_folder": "Показать в папке", "status_done": "Готово",
        "save_pwd_title": "Сохранить пароль?",
        "save_pwd_msg": "Сохранить логин и пароль для\n{host}?\n\nЛогин: {user}",
        "choose_folder": "Выберите папку загрузок",
        "translate_title": "Перевести страницу?", "translate_from": "Перевести с:",
        "translate_to": "Перевести на:", "translate_go": "Перевести",
        "translate_auto": "Определить язык",
        "lang_ru": "Русский", "lang_en": "English",
        "ctx_back": "Назад", "ctx_forward": "Вперёд", "ctx_reload": "Обновить",
        "ctx_save_page": "Сохранить страницу",
        "ctx_view_source": "Исходный код страницы",
        "wallpaper": "Обои", "wallpaper_title": "Обои новой вкладки",
        "wallpaper_auto": "Как в теме", "wallpaper_custom": "Пользовательские обои",
        "wallpaper_choose": "Выберите изображение",
        "wallpaper_filter": "Изображения (*.png *.jpg *.jpeg *.bmp *.webp *.gif)",
        "find_placeholder": "Найти на странице...",
        "close_tab_tip": "Закрыть вкладку",
        "menu_new_window": "Новое окно",
        "menu_new_tab": "Новая вкладка",
        "menu_downloads": "Загрузки",
        "menu_settings": "Настройки",
        "menu_customization": "Кастомизация",
        "menu_zoom": "Масштаб",
        "menu_about": "О браузере",
        "menu_find": "Найти на странице",
        "menu_save_as": "Сохранить как...",
        "menu_translate": "Перевести страницу",
        "menu_passwords": "Логины и пароли",
        "menu_history": "История",
        "menu_exit": "Выход",
        "ctx_open_link_new_tab": "Открыть ссылку в новой вкладке",
        "ctx_open_link_split": "Открыть в разделённом экране",
        "ctx_open_link_new_window": "Открыть ссылку в новом окне",
        "ctx_preview_link": "Предпросмотр ссылки",
        "ctx_save_object": "Сохранить объект как...",
        "ctx_copy_link": "Копировать ссылку",
        "ctx_copy_link_clean": "Копировать очищенную ссылку",
        "ctx_search_for": "Искать «{q}»",
        "ctx_inspect": "Инспектировать",
        "ctx_select_all": "Выделить всё",
        "ctx_save_page_as": "Сохранить страницу как...",
        "ctx_screenshot": "Сделать снимок экрана",
        "ctx_copy_image": "Копировать изображение",
        "ctx_copy_image_link": "Копировать ссылку на изображение",
        "ctx_search_image": "Поиск по изображению (Google Lens)",
        "ctx_set_wallpaper": "Установить как обои",
        "ctx_play": "Воспроизвести",
        "ctx_pause": "Пауза",
        "ctx_mute": "Отключить звук",
        "ctx_unmute": "Включить звук",
        "ctx_speed": "Скорость",
        "ctx_loop": "Повтор",
        "ctx_fullscreen": "Полноэкранный режим",
        "ctx_show_controls": "Элементы управления",
        "ctx_open_video_new_tab": "Открыть видео в новой вкладке",
        "ctx_pip": "Картинка в картинке",
        "ctx_save_video": "Сохранить видео как...",
        "ctx_copy_video_link": "Копировать ссылку на видео",
        "split_title": "Разделённый экран",
    },
    "en": {
        "sb_theme": "Customization", "sb_search": "Search Engines",
        "sb_zoom": "Zoom", "sb_downloads": "Downloads",
        "sb_passwords": "Logins & Passwords", "sb_language": "System",
        "sb_about": "About", "sb_history": "History",
        "sb_bookmarks": "Bookmarks",
        "settings_search_placeholder": "Search settings...",
        "theme_title": "Customization",
        "theme_sub": "Themes, colors and wallpapers in one place.",
        "theme_label": "Theme:",
        "dark_sites_label": "Dark theme for websites",
        "dark_sites_sub": "Applies a dark theme to light sites. Dark sites are left unchanged.",
        "close_glow_label": "Red flash on close",
        "close_glow_sub": "Highlights the tab in red when closed.",
        "window_section_title": "Browser window",
        "hide_wall_btn_label": "Hide wallpaper button",
        "hide_wall_btn_sub": "Removes the wallpaper chooser from the new tab.",
        "rtl_label": "Mirror interface",
        "rtl_sub": "Mirrors the navigation bar and content (RTL).",
        "smooth_scroll_label": "Smooth scrolling",
        "smooth_scroll_sub": "Smooth mouse-wheel scrolling — works on web pages and in the interface.",
        "custom_colors_title": "Custom colors",
        "custom_colors_sub": "Override theme colors. Click to pick, right-click to reset.",
        "color_text": "Text", "color_text2": "Secondary",
        "color_bg": "Background", "color_panel": "Panel",
        "color_border": "Border", "color_hover": "Hover",
        "color_accent": "Accent", "color_accent_text": "Text on accent",
        "reset_colors": "Reset colors",
        "wallpaper_settings_title": "Wallpaper",
        "wallpaper_settings_sub": "Static wallpapers or animated backgrounds.",
        "wallpaper_pick": "Change...", "wallpaper_reset": "Reset",
        "wallpaper_current": "Current wallpaper:",
        "wallpaper_none": "Not set (theme color)",
        "live_wall_title": "Live wallpapers",
        "live_wall_sub": "Animated background. Runs only on the active tab — minimal CPU load.",
        "live_none": "Disabled", "live_gradient": "Gradient",
        "live_stars": "Starry sky", "live_snow": "Snow",
        "live_aurora": "Aurora", "live_bubbles": "Bubbles",
        "live_matrix": "Matrix", "live_rain": "Rain",
        "live_fireflies": "Fireflies", "live_confetti": "Confetti",
        "live_parallax": "Parallax", "live_particles": "Particles",
        "live_rings": "Rings", "live_hex": "Hexagons",
        "live_plasma": "Plasma", "live_nebula": "Nebula",
        "live_waves": "Waves", "live_lightning": "Lightning",
        "live_pulse": "Pulse", "live_ink": "Ink",
        "live_vortex": "Vortex", "live_grid": "Grid",
        "live_speed": "Speed",
        "search_title": "Search Engines",
        "search_sub": "Search and homepage settings.",
        "search_engine_label": "Engine:",
        "search_engine_desc": "Used for search from the address bar.",
        "home_section_title": "Homepage",
        "home_section_sub": "What to open at startup and in new tabs.",
        "home_new_windows": "New windows",
        "home_new_windows_sub": "What to open when the browser starts.",
        "home_new_tabs": "New tabs",
        "home_new_tabs_sub": "What to open when a new tab is created.",
        "home_opt_home": "Homepage", "home_opt_empty": "Blank page",
        "home_opt_ddg": "DuckDuckGo", "home_opt_brave": "Brave Search",
        "home_opt_google": "Google", "home_opt_bing": "Microsoft Bing",
        "home_opt_yahoo": "Yahoo!",
        "zoom_title": "Zoom", "zoom_sub": "Page and text zoom settings.",
        "page_zoom_label": "Page zoom",
        "page_zoom_sub": "Scales all page content.",
        "text_zoom_label": "Text zoom",
        "text_zoom_sub": "Changes font size only.",
        "downloads_title": "Downloads", "downloads_sub": "File download settings.",
        "dl_path_label": "Download folder",
        "dl_path_sub": "Location for downloaded files.",
        "passwords_title": "Logins & Passwords",
        "passwords_sub": "Saved credentials. Stored locally.",
        "col_site": "Site", "col_login": "Login", "col_password": "Password",
        "history_title": "History",
        "history_sub": "All visited pages. Delete single entries or clear all.",
        "history_col_title": "Title",
        "history_col_url": "Address",
        "history_open": "Open",
        "history_delete": "Delete selected",
        "history_clear_all": "Clear history",
        "history_clear_confirm": "Delete all browsing history?",
        "history_empty": "History is empty",
        "bookmarks_title": "Bookmarks",
        "bookmarks_sub": "Saved pages. Double-click to open.",
        "col_bm_title": "Title",
        "col_bm_url": "Address",
        "bm_open": "Open",
        "bm_delete": "Delete selected",
        "bm_clear_all": "Clear bookmarks",
        "bm_clear_confirm": "Delete all bookmarks?",
        "bm_empty": "No bookmarks",
        "bm_open_new_tab": "Open in new tab",
        "bm_open_new_window": "Open in new window",
        "bm_edit": "Edit title",
        "tip_bookmark": "Add bookmark (Ctrl+D)",
        "tip_unbookmark": "Remove bookmark",
        "menu_bookmarks": "Bookmarks",
        "bookmark_bar_label": "Show bookmarks bar",
        "bookmark_bar_sub": "Bar with bookmarks below the address bar. Ctrl+B toggles it.",
        "ctx_bookmark_link": "Bookmark link",
        "ctx_add_bookmark": "Bookmark this page",
        "ctx_remove_bookmark": "Remove bookmark",
        "bm_added": "Bookmark added",
        "bm_removed": "Bookmark removed",
        "language_title": "System",
        "language_sub": "System and interface language settings.",
        "language_label": "Interface language",
        "language_sub2": "Language of buttons, menus and browser labels.",
        "autostart_label": "Launch at system startup",
        "autostart_sub": "Automatically launch Flexion when the system starts.",
        "restore_tabs_label": "Restore open tabs",
        "restore_tabs_sub": "Reopen tabs on next launch.",
        "layout_title": "Panel layout", "layout_label": "Layout",
        "layout_sub": "Where to place the navigation bar.",
        "pos_top": "Top", "pos_bottom": "Bottom",
        "font_section_title": "Font",
        "font_section_sub": "Font family applies to the whole interface.",
        "font_family_label": "Font family",
        "font_family_sub": "Choose a font installed on your system.",
        "browsing_data_title": "Browsing data",
        "browsing_data_sub": "Cache speeds up loading, cookies keep you logged in, history stores visited sites.",
        "clear_cache": "Clear cache", "clear_cookies": "Delete cookies",
        "clear_history": "Clear history", "clear_all": "Clear all",
        "clear_done_title": "Done", "clear_cache_done": "Browser cache cleared.",
        "clear_cookies_done": "Cookies and associated data removed.",
        "clear_history_done": "History cleared.",
        "clear_all_confirm_title": "Clear all data?",
        "clear_all_confirm_msg": "Cache, cookies, history and saved tabs will be removed. You will need to sign in again.",
        "clear_all_done": "All browsing data cleared.",
        "density_title": "Window density",
        "density_sub": "Adjust the browser interface density.",
        "density_auto": "Automatic",
        "density_auto_sub": "Automatic interface density selection.",
        "density_standard": "Standard",
        "density_standard_sub": "Balanced density for most screens.",
        "density_compact": "Compact",
        "density_compact_sub": "Reduced spacing for smaller screens.",
        "density_touch": "Touch",
        "density_touch_sub": "Enlarged elements for touch screens.",
        "btn_change": "Change...", "btn_open": "Open",
        "btn_add": "Add", "btn_delete": "Delete selected",
        "btn_cancel": "Cancel",
        "site_field": "Site (domain):", "login_field": "Login:",
        "password_field": "Password:", "new_entry": "New entry",
        "tip_back": "Back", "tip_forward": "Forward", "tip_reload": "Reload",
        "tip_downloads": "Downloads", "tip_settings": "Menu",
        "tip_search": "Search engine settings", "tip_translate": "Translate",
        "url_placeholder": "Enter address or search query...",
        "new_tab_title": "New tab", "settings_tab_title": "Settings",
        "about_tab_title": "About",
        "no_downloads": "No downloads", "dl_open_folder": "Open folder",
        "dl_open_file_folder": "Show in folder", "status_done": "Done",
        "save_pwd_title": "Save password?",
        "save_pwd_msg": "Save login and password for\n{host}?\n\nLogin: {user}",
        "choose_folder": "Choose download folder",
        "translate_title": "Translate this page?", "translate_from": "Translate from:",
        "translate_to": "Translate to:", "translate_go": "Translate",
        "translate_auto": "Detect language",
        "lang_ru": "Русский", "lang_en": "English",
        "ctx_back": "Back", "ctx_forward": "Forward", "ctx_reload": "Reload",
        "ctx_save_page": "Save page", "ctx_view_source": "View page source",
        "wallpaper": "Wallpaper", "wallpaper_title": "New tab wallpaper",
        "wallpaper_auto": "Follow theme", "wallpaper_custom": "Custom wallpaper",
        "wallpaper_choose": "Choose a wallpaper image",
        "wallpaper_filter": "Images (*.png *.jpg *.jpeg *.bmp *.webp *.gif)",
        "find_placeholder": "Find on page...",
        "close_tab_tip": "Close tab",
        "menu_new_window": "New window",
        "menu_new_tab": "New tab",
        "menu_downloads": "Downloads",
        "menu_settings": "Settings",
        "menu_customization": "Customization",
        "menu_zoom": "Zoom",
        "menu_about": "About",
        "menu_find": "Find on page",
        "menu_save_as": "Save as...",
        "menu_translate": "Translate page",
        "menu_passwords": "Logins & Passwords",
        "menu_history": "History",
        "menu_exit": "Exit",
        "ctx_open_link_new_tab": "Open link in new tab",
        "ctx_open_link_split": "Open link in split view",
        "ctx_open_link_new_window": "Open link in new window",
        "ctx_preview_link": "Preview link",
        "ctx_save_object": "Save object as...",
        "ctx_copy_link": "Copy link",
        "ctx_copy_link_clean": "Copy clean link",
        "ctx_search_for": "Search for \"{q}\"",
        "ctx_inspect": "Inspect",
        "ctx_select_all": "Select all",
        "ctx_save_page_as": "Save page as...",
        "ctx_screenshot": "Take screenshot",
        "ctx_copy_image": "Copy image",
        "ctx_copy_image_link": "Copy image link",
        "ctx_search_image": "Search by image (Google Lens)",
        "ctx_set_wallpaper": "Set as wallpaper",
        "ctx_play": "Play",
        "ctx_pause": "Pause",
        "ctx_mute": "Mute",
        "ctx_unmute": "Unmute",
        "ctx_speed": "Speed",
        "ctx_loop": "Loop",
        "ctx_fullscreen": "Enter fullscreen",
        "ctx_show_controls": "Show controls",
        "ctx_open_video_new_tab": "Open video in new tab",
        "ctx_pip": "Picture in picture",
        "ctx_save_video": "Save video as...",
        "ctx_copy_video_link": "Copy video link",
        "split_title": "Split view",
    },
}


THEME_PALETTES = {
    "dark":     {"bg": "#2b2b2b", "panel": "#373737", "panel_hover": "#3a3a3a",
                 "border": "#4a4a4a", "text": "#eeeeee", "text2": "#cccccc",
                 "hover": "#4a4a4a", "accent": "#5a5a5a", "accent_text": "#ffffff",
                 "accent_pressed": "#3d3d3d"},
    "light":    {"bg": "#f5f5f5", "panel": "#ffffff", "panel_hover": "#e8e8e8",
                 "border": "#c0c0c0", "text": "#222222", "text2": "#444444",
                 "hover": "#e8e8e8", "accent": "#d0d0d0", "accent_text": "#000000",
                 "accent_pressed": "#b0b0b0"},
    "purple":   {"bg": "#1e1a2e", "panel": "#2a2140", "panel_hover": "#2a2140",
                 "border": "#4a3a6a", "text": "#e5e0f0", "text2": "#b8aed0",
                 "hover": "#3a2e57", "accent": "#a855f7", "accent_text": "#ffffff",
                 "accent_pressed": "#8b3fe0"},
    "green":    {"bg": "#0f2419", "panel": "#1a3a2a", "panel_hover": "#1f4532",
                 "border": "#2d5c42", "text": "#d1fae5", "text2": "#86efac",
                 "hover": "#2d5c42", "accent": "#22c55e", "accent_text": "#ffffff",
                 "accent_pressed": "#16a34a"},
    "red":      {"bg": "#1c0a0a", "panel": "#2d1010", "panel_hover": "#3d1818",
                 "border": "#5c2020", "text": "#fecaca", "text2": "#f87171",
                 "hover": "#5c2020", "accent": "#ef4444", "accent_text": "#ffffff",
                 "accent_pressed": "#dc2626"},
    "pink":     {"bg": "#1f0f1a", "panel": "#2e1728", "panel_hover": "#3f2035",
                 "border": "#5c2d4f", "text": "#fce7f3", "text2": "#f9a8d4",
                 "hover": "#5c2d4f", "accent": "#ec4899", "accent_text": "#ffffff",
                 "accent_pressed": "#db2777"},
    "nord":     {"bg": "#2e3440", "panel": "#3b4252", "panel_hover": "#434c5e",
                 "border": "#4c566a", "text": "#eceff4", "text2": "#d8dee9",
                 "hover": "#434c5e", "accent": "#88c0d0", "accent_text": "#2e3440",
                 "accent_pressed": "#5e81ac"},
    "dracula":  {"bg": "#282a36", "panel": "#343746", "panel_hover": "#44475a",
                 "border": "#6272a4", "text": "#f8f8f2", "text2": "#bd93f9",
                 "hover": "#44475a", "accent": "#bd93f9", "accent_text": "#282a36",
                 "accent_pressed": "#ff79c6"},
    "mono":     {"bg": "#1a1a1a", "panel": "#2d2d2d", "panel_hover": "#3d3d3d",
                 "border": "#555555", "text": "#e5e5e5", "text2": "#a0a0a0",
                 "hover": "#3d3d3d", "accent": "#888888", "accent_text": "#ffffff",
                 "accent_pressed": "#666666"},
    "black_green":  {"bg": "#0a0a0a", "panel": "#161616", "panel_hover": "#1f1f1f",
                     "border": "#22c55e", "text": "#e5e5e5", "text2": "#86efac",
                     "hover": "#1f1f1f", "accent": "#22c55e", "accent_text": "#0a0a0a",
                     "accent_pressed": "#16a34a"},
    "black_cyan":   {"bg": "#0a0a0a", "panel": "#161616", "panel_hover": "#1f1f1f",
                     "border": "#06b6d4", "text": "#e5e5e5", "text2": "#67e8f9",
                     "hover": "#1f1f1f", "accent": "#06b6d4", "accent_text": "#0a0a0a",
                     "accent_pressed": "#0891b2"},
    "black_purple": {"bg": "#0a0a0a", "panel": "#161616", "panel_hover": "#1f1f1f",
                     "border": "#a855f7", "text": "#e5e5e5", "text2": "#c4b5fd",
                     "hover": "#1f1f1f", "accent": "#a855f7", "accent_text": "#ffffff",
                     "accent_pressed": "#8b3fe0"},
    "white_red":    {"bg": "#fefefe", "panel": "#f5f5f5", "panel_hover": "#e8e8e8",
                     "border": "#ef4444", "text": "#1a1a1a", "text2": "#dc2626",
                     "hover": "#fecaca", "accent": "#ef4444", "accent_text": "#ffffff",
                     "accent_pressed": "#dc2626"},
    "white_blue":   {"bg": "#fefefe", "panel": "#f5f5f5", "panel_hover": "#e8e8e8",
                     "border": "#3b82f6", "text": "#1a1a1a", "text2": "#2563eb",
                     "hover": "#dbeafe", "accent": "#3b82f6", "accent_text": "#ffffff",
                     "accent_pressed": "#2563eb"},
    "catppuccin_mocha": {"bg": "#1e1e2e", "panel": "#313244", "panel_hover": "#45475a",
                         "border": "#585b70", "text": "#cdd6f4", "text2": "#a6adc8",
                         "hover": "#45475a", "accent": "#cba6f7", "accent_text": "#1e1e2e",
                         "accent_pressed": "#b4befe"},
    "catppuccin_latte": {"bg": "#eff1f5", "panel": "#ffffff", "panel_hover": "#e6e9ef",
                         "border": "#bcc0cc", "text": "#4c4f69", "text2": "#6c6f85",
                         "hover": "#e6e9ef", "accent": "#8839ef", "accent_text": "#ffffff",
                         "accent_pressed": "#7287fd"},
    "tokyo_night": {"bg": "#1a1b26", "panel": "#24283b", "panel_hover": "#414868",
                    "border": "#414868", "text": "#c0caf5", "text2": "#a9b1d6",
                    "hover": "#414868", "accent": "#7aa2f7", "accent_text": "#1a1b26",
                    "accent_pressed": "#bb9af7"},
    "gruvbox_dark": {"bg": "#282828", "panel": "#3c3836", "panel_hover": "#504945",
                     "border": "#665c54", "text": "#ebdbb2", "text2": "#d5c4a1",
                     "hover": "#504945", "accent": "#fabd2f", "accent_text": "#282828",
                     "accent_pressed": "#d79921"},
    "solarized_dark": {"bg": "#002b36", "panel": "#073642", "panel_hover": "#0a4b5a",
                       "border": "#586e75", "text": "#93a1a1", "text2": "#839496",
                       "hover": "#0a4b5a", "accent": "#268bd2", "accent_text": "#fdf6e3",
                       "accent_pressed": "#2aa198"},
    "solarized_light": {"bg": "#fdf6e3", "panel": "#eee8d5", "panel_hover": "#e0dac6",
                        "border": "#93a1a1", "text": "#073642", "text2": "#586e75",
                        "hover": "#e0dac6", "accent": "#268bd2", "accent_text": "#fdf6e3",
                        "accent_pressed": "#2aa198"},
    "one_dark": {"bg": "#282c34", "panel": "#353b45", "panel_hover": "#3e4451",
                 "border": "#4b5263", "text": "#abb2bf", "text2": "#98c379",
                 "hover": "#3e4451", "accent": "#61afef", "accent_text": "#282c34",
                 "accent_pressed": "#528bcc"},
    "ayu_dark": {"bg": "#0b0e14", "panel": "#131721", "panel_hover": "#1c202a",
                 "border": "#2c313a", "text": "#b3b1ad", "text2": "#8d8b86",
                 "hover": "#1c202a", "accent": "#ffb454", "accent_text": "#0b0e14",
                 "accent_pressed": "#e69f48"},
    "material_ocean": {"bg": "#0f1419", "panel": "#1a1f2a", "panel_hover": "#262b36",
                       "border": "#3c4350", "text": "#d4d8dd", "text2": "#a0a8b4",
                       "hover": "#262b36", "accent": "#4dd0e1", "accent_text": "#0f1419",
                       "accent_pressed": "#26c6da"},
    "rose_pine": {"bg": "#191724", "panel": "#1f1d2e", "panel_hover": "#26233a",
                  "border": "#403d52", "text": "#e0def4", "text2": "#908caa",
                  "hover": "#26233a", "accent": "#ebbcba", "accent_text": "#191724",
                  "accent_pressed": "#c4a7e7"},
    "everforest": {"bg": "#2d353b", "panel": "#343f44", "panel_hover": "#3d484d",
                   "border": "#4f585e", "text": "#d3c6aa", "text2": "#a7c080",
                   "hover": "#3d484d", "accent": "#a7c080", "accent_text": "#2d353b",
                   "accent_pressed": "#8da36b"},
    "cyberpunk": {"bg": "#0a0014", "panel": "#1a0b2e", "panel_hover": "#2a1550",
                  "border": "#ff00ff", "text": "#00ffff", "text2": "#ff00ff",
                  "hover": "#2a1550", "accent": "#ff00ff", "accent_text": "#0a0014",
                  "accent_pressed": "#cc00cc"},
    "sunset": {"bg": "#1a0e1f", "panel": "#2d1830", "panel_hover": "#3d2140",
               "border": "#5c2f52", "text": "#ffd9b3", "text2": "#ff9d7a",
               "hover": "#3d2140", "accent": "#ff6b6b", "accent_text": "#1a0e1f",
               "accent_pressed": "#ffa500"},
    "mint": {"bg": "#f0faf5", "panel": "#ffffff", "panel_hover": "#e0f2e8",
             "border": "#a8d5ba", "text": "#1a3a2a", "text2": "#4a7a5c",
             "hover": "#e0f2e8", "accent": "#10b981", "accent_text": "#ffffff",
             "accent_pressed": "#059669"},
}

THEME_NAMES = {
    "dark": {"ru": "Тёмная", "en": "Dark"},
    "light": {"ru": "Светлая", "en": "Light"},
    "purple": {"ru": "Фиолетовая", "en": "Purple"},
    "green": {"ru": "Зелёная", "en": "Green"},
    "red": {"ru": "Красная", "en": "Red"},
    "pink": {"ru": "Розовая", "en": "Pink"},
    "nord": {"ru": "Nord", "en": "Nord"},
    "dracula": {"ru": "Dracula", "en": "Dracula"},
    "mono": {"ru": "Монохром", "en": "Monochrome"},
    "black_green": {"ru": "Чёрная с зелёной", "en": "Black & Green"},
    "black_cyan": {"ru": "Чёрная с бирюзовой", "en": "Black & Cyan"},
    "black_purple": {"ru": "Чёрная с фиолетовой", "en": "Black & Purple"},
    "white_red": {"ru": "Белая с красной", "en": "White & Red"},
    "white_blue": {"ru": "Белая с синей", "en": "White & Blue"},
    "catppuccin_mocha": {"ru": "Catppuccin Mocha", "en": "Catppuccin Mocha"},
    "catppuccin_latte": {"ru": "Catppuccin Latte", "en": "Catppuccin Latte"},
    "tokyo_night": {"ru": "Tokyo Night", "en": "Tokyo Night"},
    "gruvbox_dark": {"ru": "Gruvbox Dark", "en": "Gruvbox Dark"},
    "solarized_dark": {"ru": "Solarized Dark", "en": "Solarized Dark"},
    "solarized_light": {"ru": "Solarized Light", "en": "Solarized Light"},
    "one_dark": {"ru": "One Dark", "en": "One Dark"},
    "ayu_dark": {"ru": "Ayu Dark", "en": "Ayu Dark"},
    "material_ocean": {"ru": "Material Ocean", "en": "Material Ocean"},
    "rose_pine": {"ru": "Rosé Pine", "en": "Rosé Pine"},
    "everforest": {"ru": "Everforest", "en": "Everforest"},
    "cyberpunk": {"ru": "Киберпанк", "en": "Cyberpunk"},
    "sunset": {"ru": "Закат", "en": "Sunset"},
    "mint": {"ru": "Мята", "en": "Mint"},
}

COLOR_SLOTS = [
    ("text", "color_text"), ("text2", "color_text2"),
    ("bg", "color_bg"), ("panel", "color_panel"),
    ("border", "color_border"), ("hover", "color_hover"),
    ("accent", "color_accent"), ("accent_text", "color_accent_text"),
]


def _effective_palette(theme_name, custom_colors=None):
    pal = dict(THEME_PALETTES.get(theme_name, THEME_PALETTES["dark"]))
    if custom_colors:
        for k, v in custom_colors.items():
            if k in pal and v:
                pal[k] = v
    return pal


def _css_icon_path(p):
    return p.replace("\\", "/")


def _generate_arrow_icon(theme_name, palette):
    arrow_color = QColor(palette["text2"])
    arrow_path = os.path.join(ICONS_DIR, f"arrow_{theme_name}.png")
    pix = QPixmap(24, 14)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(arrow_color); pen.setWidthF(2.0)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.drawLine(5, 5, 12, 11)
    p.drawLine(12, 11, 19, 5)
    p.end()
    pix.save(arrow_path, "PNG")
    return arrow_path


def _generate_close_icons(theme_name, palette):
    close_color = QColor(palette["text2"])
    close_hover = QColor(palette["text"])
    close_path = os.path.join(ICONS_DIR, f"close_{theme_name}.png")
    pix = QPixmap(24, 24); pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix); p.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(close_color); pen.setWidthF(2.4)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    p.drawLine(6, 6, 18, 18); p.drawLine(18, 6, 6, 18)
    p.end(); pix.save(close_path, "PNG")

    close_hover_path = os.path.join(ICONS_DIR, f"close_hover_{theme_name}.png")
    pix = QPixmap(24, 24); pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix); p.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(close_hover); pen.setWidthF(2.6)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    p.drawLine(6, 6, 18, 18); p.drawLine(18, 6, 6, 18)
    p.end(); pix.save(close_hover_path, "PNG")
    return close_path, close_hover_path


def _generate_search_icon(theme_name, palette):
    color = QColor(palette["text2"])
    path = os.path.join(ICONS_DIR, f"search_{theme_name}.png")
    pix = QPixmap(20, 20); pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix); p.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(color); pen.setWidthF(1.8)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    p.drawEllipse(3, 3, 10, 10)
    p.drawLine(12, 12, 17, 17)
    p.end(); pix.save(path, "PNG")
    return path


def _generate_translate_icon(theme_name, palette):
    color = QColor(palette["text2"])
    path = os.path.join(ICONS_DIR, f"translate_{theme_name}.png")
    pix = QPixmap(20, 20); pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix); p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
    p.setPen(QPen(color))
    fa = QFont("Segoe UI", 10); fa.setBold(True)
    p.setFont(fa); p.drawText(0, 13, "A")
    fw = QFont("Microsoft YaHei", 9); fw.setBold(True)
    p.setFont(fw); p.drawText(9, 19, "文")
    p.end(); pix.save(path, "PNG")
    return path


def _generate_folder_icon(theme_name, palette):
    color = QColor(palette["text2"])
    path = os.path.join(ICONS_DIR, f"folder_{theme_name}.png")
    pix = QPixmap(18, 18); pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix); p.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(color); pen.setWidthF(1.5)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen); p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawPolyline(QPolygonF([
        QPointF(2.5, 6), QPointF(2.5, 3.5), QPointF(7, 3.5),
        QPointF(8, 5), QPointF(15.5, 5), QPointF(15.5, 14.5),
        QPointF(2.5, 14.5), QPointF(2.5, 6)]))
    p.end(); pix.save(path, "PNG")
    return path


def _make_bookmark_pixmap(color, filled=False, size=18):
    if isinstance(color, str):
        color = QColor(color)
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    s = float(size)
    cx = s / 2.0; cy = s / 2.0
    outer = s * 0.44; inner = s * 0.19
    poly = QPolygonF()
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        r = outer if i % 2 == 0 else inner
        poly.append(QPointF(cx + r * math.cos(ang), cy + r * math.sin(ang)))
    pen = QPen(color)
    pen.setWidthF(max(1.3, s * 0.09))
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    if filled:
        p.setBrush(QBrush(color))
    else:
        p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawPolygon(poly)
    p.end()
    return pix


def _generate_bookmark_icon(theme_name, palette, filled=False):
    color = QColor(palette["accent"] if filled else palette["text2"])
    suffix = "filled" if filled else "outline"
    path = os.path.join(ICONS_DIR, f"bookmark_{suffix}_{theme_name}.png")
    pix = _make_bookmark_pixmap(color, filled=filled, size=18)
    pix.save(path, "PNG")
    return path


def _generate_nav_icons(theme_name, palette):
    color = QColor(palette["text2"])

    def _np():
        px = QPixmap(20, 20); px.fill(Qt.GlobalColor.transparent); return px

    def _npen(painter, w=1.8):
        pen = QPen(color); pen.setWidthF(w)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)

    back_path = os.path.join(ICONS_DIR, f"back_{theme_name}.png")
    pix = _np(); p = QPainter(pix); p.setRenderHint(QPainter.RenderHint.Antialiasing)
    _npen(p); p.drawLine(14, 10, 5, 10); p.drawLine(9, 5, 5, 10); p.drawLine(9, 15, 5, 10)
    p.end(); pix.save(back_path, "PNG")

    forward_path = os.path.join(ICONS_DIR, f"forward_{theme_name}.png")
    pix = _np(); p = QPainter(pix); p.setRenderHint(QPainter.RenderHint.Antialiasing)
    _npen(p); p.drawLine(6, 10, 15, 10); p.drawLine(11, 5, 15, 10); p.drawLine(11, 15, 15, 10)
    p.end(); pix.save(forward_path, "PNG")

    reload_path = os.path.join(ICONS_DIR, f"reload_{theme_name}.png")
    pix = _np(); p = QPainter(pix); p.setRenderHint(QPainter.RenderHint.Antialiasing)
    cx, cy = 10.0, 10.0; radius = 6.0
    pen = QPen(color); pen.setWidthF(1.8)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen); p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawArc(int(cx - radius), int(cy - radius),
              int(radius * 2), int(radius * 2), 0, -300 * 16)
    ea = math.radians(-300)
    ex = cx + radius * math.cos(ea)
    ey = cy - radius * math.sin(ea)
    tx = math.sin(ea); ty = math.cos(ea)
    px_ = -ty; py_ = tx
    al = 4.0; ah = 2.2
    tip = (ex + tx * al, ey + ty * al)
    b1 = (ex + px_ * ah, ey + py_ * ah)
    b2 = (ex - px_ * ah, ey - py_ * ah)
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(color))
    p.drawPolygon(QPolygonF([QPointF(*tip), QPointF(*b1), QPointF(*b2)]))
    p.end(); pix.save(reload_path, "PNG")

    downloads_path = os.path.join(ICONS_DIR, f"downloads_{theme_name}.png")
    pix = _np(); p = QPainter(pix); p.setRenderHint(QPainter.RenderHint.Antialiasing)
    _npen(p)
    p.drawLine(10, 3, 10, 12); p.drawLine(6, 8, 10, 12)
    p.drawLine(14, 8, 10, 12); p.drawLine(4, 16, 16, 16)
    p.end(); pix.save(downloads_path, "PNG")

    menu_path = os.path.join(ICONS_DIR, f"menu_{theme_name}.png")
    pix = _np(); p = QPainter(pix); p.setRenderHint(QPainter.RenderHint.Antialiasing)
    _npen(p, 2.0)
    p.drawLine(4, 6, 16, 6); p.drawLine(4, 10, 16, 10); p.drawLine(4, 14, 16, 14)
    p.end(); pix.save(menu_path, "PNG")
    return back_path, forward_path, reload_path, downloads_path, menu_path


def _make_window_button_icon(kind, color):
    pix = QPixmap(14, 14); pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix); p.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(color); pen.setWidthF(1.2)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen); p.setBrush(Qt.BrushStyle.NoBrush)
    if kind == "min":
        p.drawLine(2, 7, 12, 7)
    elif kind == "max":
        p.drawRect(QRect(2, 2, 10, 10))
    elif kind == "restore":
        p.drawRect(QRect(2, 4, 8, 8))
        p.drawLine(4, 4, 4, 2); p.drawLine(4, 2, 12, 2)
        p.drawLine(12, 2, 12, 10); p.drawLine(12, 10, 10, 10)
    elif kind == "close":
        p.drawLine(3, 3, 11, 11); p.drawLine(11, 3, 3, 11)
    p.end()
    return QIcon(pix)


def _make_wallpaper_icon(color, size=20):
    pix = QPixmap(size, size); pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix); p.setRenderHint(QPainter.RenderHint.Antialiasing)
    s = float(size)

    pen = QPen(color); pen.setWidthF(max(1.2, s * 0.09))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen); p.setBrush(Qt.BrushStyle.NoBrush)

    frame = QRectF(s * 0.14, s * 0.2, s * 0.72, s * 0.6)
    p.drawRoundedRect(frame, s * 0.1, s * 0.1)

    sun_r = s * 0.07
    sun_c = QPointF(frame.left() + frame.width() * 0.3,
                    frame.top() + frame.height() * 0.35)
    p.drawEllipse(sun_c, sun_r, sun_r)

    p.save()
    clip = QPainterPath(); clip.addRoundedRect(frame, s * 0.1, s * 0.1)
    p.setClipPath(clip)
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(color)

    m1 = QPainterPath()
    m1.moveTo(frame.left() - s * 0.1, frame.bottom())
    m1.lineTo(frame.left() + frame.width() * 0.34, frame.top() + frame.height() * 0.52)
    m1.lineTo(frame.left() + frame.width() * 0.64, frame.bottom())
    m1.closeSubpath()
    p.drawPath(m1)

    m2 = QPainterPath()
    m2.moveTo(frame.left() + frame.width() * 0.5, frame.bottom())
    m2.lineTo(frame.left() + frame.width() * 0.72, frame.top() + frame.height() * 0.6)
    m2.lineTo(frame.right() + s * 0.1, frame.bottom())
    m2.closeSubpath()
    p.drawPath(m2)

    p.restore()
    p.end()
    return pix


def _make_gear_icon_pixmap(color, size=16):
    """Draw an 8-tooth cog with a hole in the center."""
    try:
        if isinstance(color, str):
            color = QColor(color)
        if not color.isValid():
            color = QColor("#888888")
        pix = QPixmap(size, size)
        pix.fill(Qt.GlobalColor.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        s = float(size)
        cx = cy = s / 2.0
        num_teeth = 8
        tip_r = s * 0.46
        valley_r = s * 0.32

        outer = QPainterPath()
        for i in range(num_teeth * 2):
            ang = i * math.pi / num_teeth - math.pi / 2
            r = tip_r if i % 2 == 0 else valley_r
            pt = QPointF(cx + r * math.cos(ang), cy + r * math.sin(ang))
            if i == 0:
                outer.moveTo(pt)
            else:
                outer.lineTo(pt)
        outer.closeSubpath()

        hole = QPainterPath()
        hole.addEllipse(QPointF(cx, cy), s * 0.16, s * 0.16)

        gear = outer.subtracted(hole)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(color)
        p.drawPath(gear)
        p.end()
        return pix
    except Exception:
        pix = QPixmap(size, size)
        pix.fill(Qt.GlobalColor.transparent)
        return pix


def _make_file_icon(ext, base_color, size=36):
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
    s = float(size)

    ext = (ext or "").lower().lstrip(".")

    palettes = {
        "image": "#22c55e", "video": "#ef4444", "audio": "#a855f7",
        "archive": "#f59e0b", "pdf": "#dc2626", "doc": "#3b82f6",
        "code": "#06b6d4", "text": "#94a3b8", "exec": "#ec4899",
        "font": "#14b8a6", "other": None,
    }
    if ext in ("png", "jpg", "jpeg", "gif", "webp", "bmp", "svg", "ico",
               "avif", "tiff", "tif", "heic"):
        kind = "image"
    elif ext in ("mp4", "webm", "mkv", "avi", "mov", "flv", "m4v", "wmv", "mpg", "mpeg"):
        kind = "video"
    elif ext in ("mp3", "ogg", "wav", "flac", "m4a", "aac", "opus", "wma"):
        kind = "audio"
    elif ext in ("zip", "rar", "7z", "tar", "gz", "bz2", "xz", "iso"):
        kind = "archive"
    elif ext == "pdf":
        kind = "pdf"
    elif ext in ("doc", "docx", "odt", "rtf", "xls", "xlsx", "ods",
                 "ppt", "pptx", "odp"):
        kind = "doc"
    elif ext in ("js", "ts", "py", "html", "htm", "css", "scss", "json",
                 "xml", "cpp", "c", "h", "hpp", "java", "rs", "go", "rb",
                 "php", "sh", "bat", "ps1"):
        kind = "code"
    elif ext in ("txt", "md", "log", "csv"):
        kind = "text"
    elif ext in ("exe", "msi", "app", "deb", "rpm", "apk", "dmg"):
        kind = "exec"
    elif ext in ("ttf", "otf", "woff", "woff2", "eot"):
        kind = "font"
    else:
        kind = "other"

    color = QColor(palettes.get(kind) or base_color)
    if not color.isValid():
        color = QColor(base_color)

    m = s * 0.14
    w = s - 2 * m
    h = s - 2 * m
    fold = s * 0.26

    body = QPainterPath()
    body.moveTo(m, m)
    body.lineTo(m + w - fold, m)
    body.lineTo(m + w, m + fold)
    body.lineTo(m + w, m + h)
    body.lineTo(m, m + h)
    body.closeSubpath()

    p.setPen(Qt.PenStyle.NoPen)
    shadow = QColor(0, 0, 0, 45)
    sp = QPainterPath(body)
    p.setBrush(shadow)
    p.translate(1.0, 1.2)
    p.drawPath(sp)
    p.translate(-1.0, -1.2)

    grad = QLinearGradient(QPointF(m, m), QPointF(m, m + h))
    grad.setColorAt(0.0, color.lighter(115))
    grad.setColorAt(1.0, color)
    p.setBrush(QBrush(grad))
    p.drawPath(body)

    corner = QPainterPath()
    corner.moveTo(m + w - fold, m)
    corner.lineTo(m + w, m + fold)
    corner.lineTo(m + w - fold, m + fold)
    corner.closeSubpath()
    darker = QColor(color)
    darker = darker.darker(135)
    p.setBrush(darker)
    p.drawPath(corner)

    if ext:
        label = ext.upper()
        if len(label) > 4:
            label = label[:4]
        p.setPen(QColor("#ffffff"))
        fsize = s * (0.22 if len(label) <= 3 else 0.17)
        f = QFont("Segoe UI", 1)
        f.setPixelSize(max(7, int(fsize)))
        f.setBold(True)
        p.setFont(f)
        text_rect = QRectF(m, m + fold * 0.4, w, h - fold * 0.4 - 2)
        p.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, label)

    p.end()
    return pix


def _make_sidebar_pixmap(kind, color, size=18):
    """Always returns a valid non-null QPixmap."""
    if isinstance(color, str):
        color = QColor(color)
    if not color.isValid():
        color = QColor("#888888")
    try:
        pix = QPixmap(size, size)
        pix.fill(Qt.GlobalColor.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        s = float(size) / 18.0
        p.scale(s, s)

        pen = QPen(color); pen.setWidthF(1.6)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen); p.setBrush(Qt.BrushStyle.NoBrush)

        if kind == "sparkle":
            cx, cy = 8.0, 9.5; outer = 6.5; inner = 1.4
            pm = QPainterPath()
            pm.moveTo(cx, cy - outer)
            pm.quadTo(cx + inner, cy - inner, cx + outer, cy)
            pm.quadTo(cx + inner, cy + inner, cx, cy + outer)
            pm.quadTo(cx - inner, cy + inner, cx - outer, cy)
            pm.quadTo(cx - inner, cy - inner, cx, cy - outer); pm.closeSubpath()
            cx2, cy2 = 14.5, 4.0; o2 = 2.8; i2 = 0.6
            ps = QPainterPath()
            ps.moveTo(cx2, cy2 - o2)
            ps.quadTo(cx2 + i2, cy2 - i2, cx2 + o2, cy2)
            ps.quadTo(cx2 + i2, cy2 + i2, cx2, cy2 + o2)
            ps.quadTo(cx2 - i2, cy2 + i2, cx2 - o2, cy2)
            ps.quadTo(cx2 - i2, cy2 - i2, cx2, cy2 - o2); ps.closeSubpath()
            p.setPen(Qt.PenStyle.NoPen); p.setBrush(color)
            p.drawPath(pm); p.drawPath(ps)
        elif kind == "search":
            p.drawEllipse(3, 3, 9, 9); p.drawLine(11, 11, 15, 15)
        elif kind == "eye":
            pe = QPainterPath()
            pe.moveTo(2, 9); pe.cubicTo(5, 4, 13, 4, 16, 9)
            pe.cubicTo(13, 14, 5, 14, 2, 9)
            p.drawPath(pe); p.drawEllipse(7, 7, 4, 4)
        elif kind == "download":
            p.drawLine(9, 2, 9, 11); p.drawLine(5, 8, 9, 12)
            p.drawLine(13, 8, 9, 12); p.drawLine(3, 15, 15, 15)
        elif kind == "lock":
            p.drawRoundedRect(1, 9, 8, 6, 1.2, 1.2); p.drawArc(2, 5, 6, 8, 0, 180 * 16)
            p.setBrush(color); p.drawEllipse(4, 11, 2, 2); p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(11, 5, 5, 5); p.drawLine(13, 10, 13, 16)
            p.drawLine(13, 12, 16, 12); p.drawLine(13, 14, 16, 14)
        elif kind == "sliders":
            p.drawLine(2, 4, 16, 4); p.drawLine(2, 9, 16, 9); p.drawLine(2, 14, 16, 14)
            p.setBrush(color); p.drawEllipse(11, 2, 4, 4)
            p.drawEllipse(3, 7, 4, 4); p.drawEllipse(10, 12, 4, 4)
        elif kind == "splitscreen":
            p.drawRoundedRect(1, 3, 7, 12, 1.5, 1.5)
            p.drawRoundedRect(10, 3, 7, 12, 1.5, 1.5)
        elif kind == "info":
            p.drawEllipse(2, 2, 14, 14)
            p.drawLine(9, 8, 9, 13)
            p.setBrush(color); p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(8, 5, 2, 2)
        elif kind == "history":
            p.drawEllipse(2, 2, 14, 14)
            p.drawLine(9, 5, 9, 9)
            p.drawLine(9, 9, 13, 11)
        elif kind == "bookmark":
            cx, cy = 9.0, 9.0
            outer = 7.0; inner = 3.0
            poly = QPolygonF()
            for k in range(10):
                ang = -math.pi / 2 + k * math.pi / 5
                r = outer if k % 2 == 0 else inner
                poly.append(QPointF(cx + r * math.cos(ang), cy + r * math.sin(ang)))
            p.setPen(Qt.PenStyle.NoPen); p.setBrush(color)
            p.drawPolygon(poly)
        elif kind == "palette":
            p.drawEllipse(2, 2, 14, 14)
            p.setBrush(color); p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(5, 6, 2, 2); p.drawEllipse(11, 6, 2, 2)
            p.drawEllipse(5, 11, 2, 2); p.drawEllipse(11, 11, 2, 2)
        elif kind == "bolt":
            path = QPainterPath()
            path.moveTo(10, 2)
            path.lineTo(5, 10)
            path.lineTo(8.5, 10)
            path.lineTo(7, 16)
            path.lineTo(13, 8)
            path.lineTo(9.5, 8)
            path.lineTo(12, 2)
            path.closeSubpath()
            p.setPen(Qt.PenStyle.NoPen); p.setBrush(color)
            p.drawPath(path)
        elif kind == "shield":
            path = QPainterPath()
            path.moveTo(9, 2)
            path.lineTo(15, 4)
            path.lineTo(15, 10)
            path.quadTo(15, 14, 9, 16)
            path.quadTo(3, 14, 3, 10)
            path.lineTo(3, 4)
            path.closeSubpath()
            p.drawPath(path)
            pen2 = QPen(color); pen2.setWidthF(1.4)
            pen2.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen2.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            p.setPen(pen2); p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawLine(6, 9, 8, 11); p.drawLine(8, 11, 12, 7)
        elif kind == "globe":
            p.drawEllipse(2, 2, 14, 14)
            p.drawEllipse(7, 2, 4, 14)
            p.drawLine(2, 9, 16, 9)
        elif kind == "keyboard":
            p.drawRoundedRect(1, 5, 16, 9, 1.5, 1.5)
            pen2 = QPen(color); pen2.setWidthF(1.4)
            pen2.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen2)
            p.drawLine(4, 8, 5, 8); p.drawLine(7, 8, 8, 8)
            p.drawLine(10, 8, 11, 8); p.drawLine(13, 8, 14, 8)
            p.drawLine(4, 11, 5, 11); p.drawLine(7, 11, 8, 11)
            p.drawLine(10, 11, 11, 11); p.drawLine(13, 11, 14, 11)
            p.drawLine(6, 12, 12, 12)
        elif kind == "window":
            p.drawRect(2, 3, 14, 12)
            p.drawLine(2, 6, 16, 6)
            p.setBrush(color); p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(4.0, 4.5), 1.2, 1.2)
            p.drawEllipse(QPointF(6.5, 4.5), 1.2, 1.2)
            p.drawEllipse(QPointF(9.0, 4.5), 1.2, 1.2)
        elif kind == "plus_tab":
            p.drawEllipse(2, 2, 14, 14)
            p.drawLine(QPointF(9.0, 5.5), QPointF(9.0, 12.5))
            p.drawLine(QPointF(5.5, 9.0), QPointF(12.5, 9.0))
        elif kind == "save":
            p.drawRect(3, 3, 12, 12)
            p.drawLine(3, 3, 11, 3)
            p.drawLine(11, 3, 15, 7)
            p.drawLine(15, 7, 15, 15)
            p.drawRect(6, 10, 6, 5)
            p.drawRect(QRectF(6.0, 3.5, 5.0, 3.0))
        elif kind == "exit":
            p.drawLine(3, 9, 12, 9)
            p.drawLine(9, 6, 12, 9)
            p.drawLine(9, 12, 12, 9)
            p.drawLine(13, 3, 15, 3)
            p.drawLine(15, 3, 15, 15)
            p.drawLine(15, 15, 13, 15)
        elif kind == "zoom_in":
            p.drawEllipse(3, 3, 9, 9)
            p.drawLine(11, 11, 15, 15)
            p.drawLine(QPointF(5.0, 7.5), QPointF(10.0, 7.5))
            p.drawLine(QPointF(7.5, 5.0), QPointF(7.5, 10.0))
        elif kind == "wallpaper":
            pen2 = QPen(color); pen2.setWidthF(1.4)
            pen2.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen2.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            p.setPen(pen2); p.setBrush(Qt.BrushStyle.NoBrush)
            frame = QRectF(2.5, 4.5, 13.0, 9.0)
            p.drawRoundedRect(frame, 1.5, 1.5)
            p.drawEllipse(QPointF(6.0, 7.5), 1.2, 1.2)
            p.save()
            clip = QPainterPath()
            clip.addRoundedRect(frame, 1.5, 1.5)
            p.setClipPath(clip)
            p.setPen(Qt.PenStyle.NoPen); p.setBrush(color)
            m = QPainterPath()
            m.moveTo(1.0, 13.5)
            m.lineTo(7.0, 9.0)
            m.lineTo(12.0, 13.5)
            m.closeSubpath()
            p.drawPath(m)
            p.restore()
        p.end()
        if pix.isNull():
            pix = QPixmap(size, size)
            pix.fill(color)
        return pix
    except Exception:
        pix = QPixmap(size, size)
        pix.fill(color)
        return pix


def _make_state_icon(kind, palette, size=18):
    """Return a QIcon with On/Off states. Fallback to solid color if generation fails."""
    try:
        text2 = QColor(palette.get("text2", "#cccccc"))
        accent_text = QColor(palette.get("accent_text", "#ffffff"))
        if not text2.isValid():
            text2 = QColor("#cccccc")
        if not accent_text.isValid():
            accent_text = QColor("#ffffff")
        normal = _make_sidebar_pixmap(kind, text2, size)
        checked = _make_sidebar_pixmap(kind, accent_text, size)
        icon = QIcon()
        if normal is not None and not normal.isNull():
            icon.addPixmap(normal, QIcon.Mode.Normal, QIcon.State.Off)
        if checked is not None and not checked.isNull():
            icon.addPixmap(checked, QIcon.Mode.Normal, QIcon.State.On)
        return icon
    except Exception:
        return QIcon()


def _sidebar_button_style(palette):
    """Inline stylesheet — highest priority in QSS, guaranteed to apply."""
    return f"""
        QPushButton {{
            color: {palette['text2']};
            background-color: transparent;
            text-align: left;
            padding: 7px 18px 7px 14px;
            margin: 2px 8px;
            border: none;
            border-radius: 17px;
            font-weight: 600;
            font-size: 13px;
            min-height: 20px;
            spacing: 8px;
        }}
        QPushButton:hover {{
            background-color: {palette['panel_hover']};
            color: {palette['text']};
        }}
        QPushButton:checked {{
            background-color: {palette['accent']};
            color: {palette['accent_text']};
        }}
    """


_THEME_TEMPLATE = Template("""
QMainWindow, QDialog { background-color: $bg; }
QWidget { background-color: $bg; color: $text; }
QLineEdit { background-color: $panel; color: $text; font-weight: 600;
    border: 1px solid $border; border-radius: 16px; padding: $input_pad; }
QLineEdit:focus { border: 2px solid $accent; }
QPushButton { background-color: $panel; color: $text; font-weight: 700;
    border: 1px solid $border; border-radius: 14px; padding: $btn_pad; }
QPushButton:hover { background-color: $hover; }
QPushButton:pressed { background-color: $accent_pressed; }
QPushButton#navBtn { background: transparent; border: none; border-radius: 10px; padding: 0; }
QPushButton#navBtn:hover { background: $panel_hover; border: none; }
QPushButton#navBtn:pressed { background: $accent_pressed; border: none; }
QTabWidget::pane { border: none; }
QTabBar { background: transparent; }
QPushButton#tabCloseBtn { background: transparent; border: none; padding: 0; margin: 0; }
QPushButton#tabCloseBtn:hover { background: transparent; border: none; }
QComboBox { background-color: $panel; color: $text;
    border: 1px solid $border; border-radius: 16px; padding: 6px 36px 6px 16px; }
QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: center right;
    width: 30px; border: none; background: transparent; }
QComboBox::down-arrow { image: url("$arrow_path"); width: 24px; height: 14px; }
QComboBox QAbstractItemView { background-color: $panel; color: $text;
    border: 1px solid $border; border-radius: 10px;
    selection-background-color: $accent; selection-color: $accent_text;
    outline: none; padding: 4px; }
QLabel { color: $text; background: transparent; }
QLabel#formLabel { font-weight: 700; }
QTableWidget { background: $panel; color: $text;
    gridline-color: $border; border: 1px solid $border; border-radius: 14px; }
QHeaderView::section { background: $bg; color: $text;
    padding: 8px; border: none; border-bottom: 1px solid $border; }
QMenu { background-color: $bg; color: $text; border: 1px solid $border;
    border-radius: 12px; padding: 6px; }
QMenu::item { padding: 8px 20px; border-radius: 8px; }
QMenu::item:selected { background: $accent; color: $accent_text; }
#sidebarWidget { background: $bg; border-right: 1px solid $border; }
QLineEdit#settingsSearch { background: $panel; color: $text;
    border: 1px solid $border; border-radius: 18px; padding: 7px 16px;
    font-size: 12px; font-weight: 500; min-height: 22px; }
QLineEdit#settingsSearch:focus { border: 1px solid $accent; }
QPushButton#newTabBtn { background: transparent; color: $text2; border: none;
    border-radius: 10px; font-size: 17px; font-weight: 500; padding: 0 0 3px 0; }
QPushButton#newTabBtn:hover { background: $panel_hover; color: $text; }
QPushButton#newTabBtn:pressed { background: $accent_pressed; }
QPushButton#winBtn { background: transparent; color: $text; border: none;
    border-radius: 0; padding: 0; }
QPushButton#winBtn:hover { background: $panel_hover; }
QPushButton#winBtn:pressed { background: $accent_pressed; }
QPushButton#winCloseBtn { background: transparent; color: $text; border: none;
    border-radius: 0; padding: 0; }
QPushButton#winCloseBtn:hover { background: #e81123; }
QPushButton#winCloseBtn:pressed { background: #b30e1c; }
#titleBar { background: $bg; border-bottom: 1px solid $border; }
#navBarTop { background: $bg; border-bottom: 1px solid $border; }
#navBarBottom { background: $bg; border-top: 1px solid $border; }
#bookmarksBar { background: $bg; border-bottom: 1px solid $border; }
QTabBar::scroller { width: 0px; }
QScrollArea { background: transparent; border: none; }
QScrollBar:vertical { background: transparent; width: 10px;
    border-radius: 5px; margin: 2px 2px 2px 0; }
QScrollBar::handle:vertical { background: $border; border-radius: 5px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: $hover; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { background: none; height: 0; }
QWidget#findBarWrapper { background-color: $bg; }
QWidget#findBar { background: $panel; border: 1px solid $border; border-radius: 18px; }
QLineEdit#findInput { background: transparent; color: $text;
    border: none; padding: 0 4px; font-size: 13px; font-weight: 500; }
QLabel#findCountLabel { color: $text2; background: transparent;
    padding: 0 6px; font-size: 12px; font-weight: 600; }
QPushButton#findBtn { background: transparent; color: $text2; border: none;
    border-radius: 13px; padding: 0; font-weight: 700; font-size: 14px;
    min-width: 26px; min-height: 26px; max-width: 26px; max-height: 26px; }
QPushButton#findBtn:hover { background: $panel_hover; color: $text; }
QPushButton#findBtn:pressed { background: $accent_pressed; }
QFrame#settingsCard { background-color: $panel; border: 1px solid $border; border-radius: 12px; }
QFrame#settingsSeparator { background-color: $border; max-height: 1px; border: none; }
QLabel#settingsSection { font-size: 16px; font-weight: 700; background: transparent; }
QLabel#settingsRowTitle { font-size: 14px; font-weight: 600; background: transparent; }
QLabel#settingsRowSub { font-size: 12px; color: $text2; background: transparent; }
QLabel#wallpaperHint { background-color: $bg; color: $text2;
    padding: 6px 12px; border-radius: 10px; }
QLabel#aboutTitle { font-size: 28px; font-weight: 800; background: transparent; }
QLabel#aboutTagline { font-size: 15px; font-weight: 600; color: $accent; background: transparent; }
QLabel#aboutText { font-size: 13px; color: $text2; background: transparent; }
QLabel#aboutFeatureTitle { font-size: 14px; font-weight: 700; background: transparent; }
QLabel#aboutFeatureDesc { font-size: 12px; color: $text2; background: transparent; }
QFrame#aboutCard { background-color: $panel; border: 1px solid $border; border-radius: 12px; }
""")


def build_style(theme_name, density="auto", custom_colors=None):
    palette = _effective_palette(theme_name, custom_colors)
    arrow = _generate_arrow_icon(theme_name, palette)
    preset = DENSITY_PRESETS.get(density, DENSITY_PRESETS["auto"])
    return _THEME_TEMPLATE.substitute(
        **palette, arrow_path=_css_icon_path(arrow),
        btn_pad=preset["btn_pad"], input_pad=preset["input_pad"])


def _build_combo_view_qss(theme_name, custom_colors=None):
    pal = _effective_palette(theme_name, custom_colors)
    return f"""
    QAbstractItemView {{ background-color: {pal['panel']}; color: {pal['text']};
        border: 1px solid {pal['border']}; border-radius: 10px;
        selection-background-color: {pal['accent']};
        selection-color: {pal['accent_text']}; outline: none; padding: 4px; }}
    QAbstractItemView::item {{ background-color: transparent; color: {pal['text']};
        padding: 6px 10px; border-radius: 6px; min-height: 22px; }}
    QAbstractItemView::item:selected {{ background-color: {pal['accent']};
        color: {pal['accent_text']}; }}
    """


def _refresh_all_combo_views(theme_name, custom_colors=None):
    qss = _build_combo_view_qss(theme_name, custom_colors)
    for w in QApplication.allWidgets():
        if isinstance(w, QComboBox):
            try: w.view().setStyleSheet(qss)
            except Exception: pass


def _build_ctx_menu_qss(theme_name, custom_colors=None):
    pal = _effective_palette(theme_name, custom_colors)
    return f"""
QMenu {{ background-color: {pal['bg']}; color: {pal['text']};
    border: 1px solid {pal['border']}; border-radius: 12px; padding: 6px; }}
QMenu::item {{ padding: 8px 26px 8px 22px; border-radius: 8px;
    background: transparent; color: {pal['text']}; }}
QMenu::item:selected {{ background-color: {pal['accent']}; color: {pal['accent_text']}; }}
QMenu::item:disabled {{ color: {pal['text2']}; }}
QMenu::separator {{ height: 1px; background: {pal['border']}; margin: 6px 10px; }}
"""


LOADING_HTML = """
<!DOCTYPE html><html><head><meta charset="utf-8"><style>
html,body{margin:0;padding:0;height:100%;background:#2b2b2b;color:#888;
font-family:'Segoe UI',Arial,sans-serif}
body{display:flex;align-items:center;justify-content:center}
.dot{display:inline-block;width:10px;height:10px;margin:0 4px;
background:#a855f7;border-radius:50%;animation:b 1.2s infinite ease-in-out}
.dot:nth-child(2){animation-delay:.15s}.dot:nth-child(3){animation-delay:.3s}
@keyframes b{0%,80%,100%{transform:scale(.5);opacity:.4}40%{transform:scale(1);opacity:1}}
p{margin-top:16px;font-size:14px;letter-spacing:1px}
</style></head><body>
<div style="text-align:center">
<div class="dot"></div><div class="dot"></div><div class="dot"></div>
<p>Loading...</p></div></body></html>
"""


PASSWORD_HOOK_JS = """
(function() {
    if (window.__flexionHookReady) return;
    window.__flexionHookReady = true;
    var script = document.createElement('script');
    script.src = 'qrc:///qtwebchannel/qwebchannel.js';
    script.onload = function() {
        new QWebChannel(qt.webChannelTransport, function(channel) {
            window.__flexionBridge = channel.objects.bridge;
            document.addEventListener('submit', function(e) {
                try {
                    var form = e.target;
                    var pwd = form.querySelector('input[type=password]');
                    var user = form.querySelector(
                        'input[type=text], input[type=email], input[name*=user i], input[name*=login i]');
                    if (pwd && user && pwd.value && user.value) {
                        window.__flexionBridge.suggestSave(window.location.href, user.value, pwd.value);
                    }
                } catch (err) {}
            }, true);
        });
    };
    document.head.appendChild(script);
})();
"""


class HistoryStore:
    MAX = 500

    def __init__(self):
        self.entries = []
        self.load()

    def load(self):
        if not os.path.exists(HISTORY_FILE):
            self.entries = []
            return
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                self.entries = [e for e in data
                                if isinstance(e, dict) and "url" in e]
        except Exception:
            self.entries = []

    def save(self):
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.entries[-self.MAX:], f,
                          ensure_ascii=False, indent=2)
        except Exception:
            pass

    def add(self, url, title):
        if not url:
            return
        if url.startswith("about:") or url.startswith("chrome://"):
            return
        title = (title or url)[:200]
        self.entries = [e for e in self.entries if e.get("url") != url]
        self.entries.append({"url": url, "title": title, "time": time.time()})
        self.entries = self.entries[-self.MAX:]
        self.save()

    def remove(self, url):
        self.entries = [e for e in self.entries if e.get("url") != url]
        self.save()

    def clear(self):
        self.entries = []
        self.save()

    def recent(self, n=30):
        return list(reversed(self.entries[-n:]))


class BookmarkStore:
    def __init__(self):
        self.entries = []
        self.load()

    def load(self):
        if not os.path.exists(BOOKMARKS_FILE):
            self.entries = []
            return
        try:
            with open(BOOKMARKS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                self.entries = [e for e in data
                                if isinstance(e, dict) and "url" in e]
        except Exception:
            self.entries = []

    def save(self):
        try:
            with open(BOOKMARKS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.entries, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def has(self, url):
        if not url:
            return False
        return any(e.get("url") == url for e in self.entries)

    def add(self, url, title):
        if not url:
            return False
        if url.startswith("about:") or url.startswith("chrome://"):
            return False
        if self.has(url):
            return False
        title = (title or url)[:200]
        self.entries.append({"url": url, "title": title,
                             "time": time.time()})
        self.save()
        return True

    def remove(self, url):
        if not url:
            return False
        n = len(self.entries)
        self.entries = [e for e in self.entries if e.get("url") != url]
        if len(self.entries) != n:
            self.save()
            return True
        return False

    def toggle(self, url, title):
        if self.has(url):
            self.remove(url)
            return False
        self.add(url, title)
        return True

    def clear(self):
        self.entries = []
        self.save()

    def update_title(self, url, new_title):
        for e in self.entries:
            if e.get("url") == url:
                e["title"] = (new_title or "")[:200]
                self.save()
                return True
        return False


class SmoothScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._smooth = False
        self._anim = QPropertyAnimation(self.verticalScrollBar(), b"value", self)
        self._anim.setDuration(230)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def set_smooth(self, enabled):
        self._smooth = bool(enabled)

    def wheelEvent(self, e):
        if not self._smooth:
            super().wheelEvent(e)
            return
        delta = e.angleDelta().y()
        if delta == 0:
            super().wheelEvent(e)
            return
        sb = self.verticalScrollBar()
        if sb is None:
            super().wheelEvent(e); return
        step = max(40, int(self.viewport().height() / 4))
        direction = -1 if delta > 0 else 1
        target = sb.value() + direction * step
        target = max(sb.minimum(), min(sb.maximum(), target))
        self._anim.stop()
        self._anim.setStartValue(sb.value())
        self._anim.setEndValue(target)
        self._anim.start()
        e.accept()


class LiveWallpaperEngine:
    def __init__(self, mode="none"):
        self.mode = mode
        self.t = 0.0
        self.particles = []
        self.extra = {}
        self._rebuild_particles()

    def set_mode(self, mode):
        if mode == self.mode: return
        self.mode = mode
        self.t = 0.0
        self._rebuild_particles()

    def _rebuild_particles(self):
        self.particles = []
        self.extra = {}
        rng = random.Random(42)
        m = self.mode
        if m == "stars":
            for _ in range(90):
                self.particles.append({
                    "x": rng.random(), "y": rng.random(),
                    "r": 0.8 + rng.random() * 2.0, "phase": rng.random() * 6.28})
        elif m == "snow":
            for _ in range(70):
                self.particles.append({
                    "x": rng.random(), "y": rng.random(),
                    "r": 0.8 + rng.random() * 2.2,
                    "phase": rng.random() * 6.28,
                    "vy": 0.008 + rng.random() * 0.02,
                    "drift": (rng.random() - 0.5) * 0.008})
        elif m == "bubbles":
            for _ in range(45):
                self.particles.append({
                    "x": rng.random(), "y": rng.random(),
                    "r": 0.8 + rng.random() * 2.5,
                    "phase": rng.random() * 6.28,
                    "vy": -0.005 - rng.random() * 0.01,
                    "drift": (rng.random() - 0.5) * 0.008})
        elif m == "matrix":
            cols = 55
            for i in range(cols):
                self.particles.append({
                    "x": i / cols + 0.005,
                    "y": rng.random() * 1.5 - 0.5,
                    "speed": 0.20 + rng.random() * 0.35,
                    "tail": 8 + rng.randint(0, 12)})
        elif m == "rain":
            for _ in range(140):
                self.particles.append({
                    "x": rng.random(), "y": rng.random(),
                    "len": 0.015 + rng.random() * 0.030,
                    "speed": 0.5 + rng.random() * 0.8})
        elif m == "fireflies":
            for _ in range(45):
                self.particles.append({
                    "x": rng.random(), "y": rng.random(),
                    "vx": (rng.random() - 0.5) * 0.03,
                    "vy": (rng.random() - 0.5) * 0.03,
                    "phase": rng.random() * 6.28,
                    "pulse": 0.5 + rng.random() * 1.5})
        elif m == "confetti":
            palette = ["#ff6b6b", "#ffd93d", "#6bcb77",
                       "#4d96ff", "#c56cf0", "#ff9f43", "#ff6ec7"]
            for _ in range(90):
                self.particles.append({
                    "x": rng.random(), "y": rng.random(),
                    "w": 0.006 + rng.random() * 0.010,
                    "h": 0.012 + rng.random() * 0.018,
                    "rot": rng.random() * 360,
                    "vrot": (rng.random() - 0.5) * 300,
                    "vy": 0.02 + rng.random() * 0.05,
                    "drift": (rng.random() - 0.5) * 0.04,
                    "color": rng.choice(palette)})
        elif m == "parallax":
            for _ in range(160):
                d = rng.random() ** 2
                self.particles.append({
                    "x": rng.random(), "y": rng.random(),
                    "r": 0.4 + d * 2.2, "depth": d,
                    "phase": rng.random() * 6.28})
        elif m == "particles":
            for _ in range(55):
                self.particles.append({
                    "x": rng.random(), "y": rng.random(),
                    "vx": (rng.random() - 0.5) * 0.045,
                    "vy": (rng.random() - 0.5) * 0.045})
        elif m == "rings":
            for i in range(7):
                self.particles.append({"phase": i * 0.65, "hue": i * 45})
        elif m == "hex":
            self.extra["cols"] = 26
            self.extra["rows"] = 16
            for r_ in range(16):
                for c_ in range(26):
                    self.particles.append({
                        "r": r_, "c": c_, "phase": rng.random() * 6.28})
        elif m == "nebula":
            for _ in range(9):
                self.particles.append({
                    "x": rng.random(), "y": rng.random(),
                    "r": 0.25 + rng.random() * 0.35,
                    "hue": rng.random() * 360,
                    "phase": rng.random() * 6.28,
                    "vx": (rng.random() - 0.5) * 0.02,
                    "vy": (rng.random() - 0.5) * 0.02})
        elif m == "waves":
            self.extra["rows"] = 6
        elif m == "lightning":
            for _ in range(18):
                self.particles.append({
                    "x": rng.random(), "y": rng.random(),
                    "len": 0.06 + rng.random() * 0.20,
                    "angle": rng.random() * 360,
                    "phase": rng.random() * 6.28,
                    "freq": 0.3 + rng.random() * 1.2})
        elif m == "ink":
            for _ in range(11):
                self.particles.append({
                    "x": 0.1 + rng.random() * 0.8,
                    "y": 0.1 + rng.random() * 0.8,
                    "r": 0.05 + rng.random() * 0.10,
                    "hue": rng.random() * 360,
                    "phase": rng.random() * 6.28})
        elif m == "vortex":
            for _ in range(120):
                self.particles.append({
                    "angle": rng.random() * 6.28,
                    "radius": 0.05 + rng.random() * 0.55,
                    "speed": 0.4 + rng.random() * 1.4,
                    "r": 0.5 + rng.random() * 1.8,
                    "hue": rng.random() * 360})
        elif m == "grid":
            self.extra["cols"] = 30
            self.extra["rows"] = 20

    def advance(self, dt):
        if self.mode == "none": return
        self.t += dt
        m = self.mode
        if m == "snow":
            for p in self.particles:
                p["y"] += p["vy"] * dt
                p["x"] += p["drift"] * dt
                if p["y"] > 1.05:
                    p["y"] = -0.05; p["x"] = random.random()
                if p["x"] > 1.05: p["x"] = -0.05
                elif p["x"] < -0.05: p["x"] = 1.05
        elif m == "bubbles":
            for p in self.particles:
                p["y"] += p["vy"] * dt
                p["x"] += p["drift"] * dt
                if p["y"] < -0.05:
                    p["y"] = 1.05; p["x"] = random.random()
                if p["x"] > 1.05: p["x"] = -0.05
                elif p["x"] < -0.05: p["x"] = 1.05
        elif m == "matrix":
            for p in self.particles:
                p["y"] += p["speed"] * dt
                if p["y"] - p["tail"] * 0.02 > 1.3:
                    p["y"] = -0.3 - random.random() * 0.5
                    p["speed"] = 0.20 + random.random() * 0.35
        elif m == "rain":
            for p in self.particles:
                p["y"] += p["speed"] * dt
                if p["y"] > 1.05:
                    p["y"] = -0.05; p["x"] = random.random()
        elif m == "fireflies":
            for p in self.particles:
                p["x"] += p["vx"] * dt
                p["y"] += p["vy"] * dt
                if p["x"] < 0.02 or p["x"] > 0.98: p["vx"] *= -1
                if p["y"] < 0.02 or p["y"] > 0.98: p["vy"] *= -1
                p["vx"] += (random.random() - 0.5) * 0.008
                p["vy"] += (random.random() - 0.5) * 0.008
                p["vx"] = max(-0.05, min(0.05, p["vx"]))
                p["vy"] = max(-0.05, min(0.05, p["vy"]))
        elif m == "confetti":
            for p in self.particles:
                p["y"] += p["vy"] * dt
                p["x"] += p["drift"] * dt
                p["rot"] += p["vrot"] * dt
                if p["y"] > 1.05:
                    p["y"] = -0.05; p["x"] = random.random()
                if p["x"] > 1.05: p["x"] = -0.05
                elif p["x"] < -0.05: p["x"] = 1.05
        elif m == "parallax":
            for p in self.particles:
                p["y"] += (0.004 + p["depth"] * 0.035) * dt
                if p["y"] > 1.02:
                    p["y"] = -0.02; p["x"] = random.random()
        elif m == "particles":
            for p in self.particles:
                p["x"] += p["vx"] * dt
                p["y"] += p["vy"] * dt
                if p["x"] < 0 or p["x"] > 1: p["vx"] *= -1
                if p["y"] < 0 or p["y"] > 1: p["vy"] *= -1
                p["x"] = max(0.0, min(1.0, p["x"]))
                p["y"] = max(0.0, min(1.0, p["y"]))
        elif m == "nebula":
            for p in self.particles:
                p["x"] += p["vx"] * dt
                p["y"] += p["vy"] * dt
                if p["x"] < 0.1 or p["x"] > 0.9: p["vx"] *= -1
                if p["y"] < 0.1 or p["y"] > 0.9: p["vy"] *= -1

    def paint(self, painter, rect, base_color, accent_color):
        m = self.mode
        w, h = rect.width(), rect.height()
        tl = QPointF(float(rect.left()), float(rect.top()))
        br = QPointF(float(rect.right()), float(rect.bottom()))

        if m == "gradient":
            phase = self.t * 0.12
            h1 = (phase * 40) % 360
            h2 = (h1 + 140) % 360
            c1 = QColor.fromHsv(int(h1), 160, 70)
            c2 = QColor.fromHsv(int(h2), 160, 35)
            grad = QLinearGradient(tl, br)
            grad.setColorAt(0, c1); grad.setColorAt(1, c2)
            painter.fillRect(rect, grad)
        elif m == "stars":
            painter.fillRect(rect, QColor("#08080f"))
            painter.setPen(Qt.PenStyle.NoPen)
            for p in self.particles:
                x, y, r = p["x"] * w, p["y"] * h, p["r"]
                b = 0.5 + 0.5 * math.sin(self.t * 1.5 + p["phase"])
                c = QColor(255, 255, 255); c.setAlpha(int(80 + 175 * b))
                painter.setBrush(c); painter.drawEllipse(QPointF(x, y), r, r)
        elif m == "snow":
            painter.fillRect(rect, QColor("#1a1f2a"))
            painter.setPen(Qt.PenStyle.NoPen)
            for p in self.particles:
                x, y, r = p["x"] * w, p["y"] * h, p["r"] * 1.5
                c = QColor(230, 240, 255)
                c.setAlpha(int(150 + 100 * math.sin(self.t + p["phase"])))
                painter.setBrush(c); painter.drawEllipse(QPointF(x, y), r, r)
        elif m == "aurora":
            painter.fillRect(rect, QColor("#0a0f1a"))
            painter.setPen(Qt.PenStyle.NoPen)
            for i in range(6):
                ph = self.t * 0.3 + i * 0.9
                cx = (0.5 + 0.35 * math.sin(ph)) * w
                cy = (0.3 + 0.2 * math.cos(ph * 1.3)) * h
                r = 180 + 80 * math.sin(ph * 0.7)
                col = QColor.fromHsv(int((self.t * 30 + i * 40) % 360), 200, 200)
                col.setAlpha(45)
                rg = QRadialGradient(QPointF(cx, cy), r)
                rg.setColorAt(0, col)
                ce = QColor(col); ce.setAlpha(0)
                rg.setColorAt(1, ce)
                painter.setBrush(rg); painter.drawEllipse(QPointF(cx, cy), r, r)
        elif m == "bubbles":
            painter.fillRect(rect, QColor(base_color))
            painter.setPen(Qt.PenStyle.NoPen)
            for p in self.particles:
                x, y, r = p["x"] * w, p["y"] * h, p["r"] * 4
                c = QColor(accent_color)
                c.setAlpha(int(50 + 70 * math.sin(self.t * 2 + p["phase"])))
                painter.setBrush(c); painter.drawEllipse(QPointF(x, y), r, r)
        elif m == "matrix":
            painter.fillRect(rect, QColor("#000600"))
            f = QFont("Consolas", 10); f.setBold(True)
            painter.setFont(f)
            fm = painter.fontMetrics(); row_h = fm.height() + 2
            for p in self.particles:
                x = p["x"] * w; head_y = p["y"] * h; tail = p["tail"]
                for k in range(tail):
                    y = head_y - k * row_h
                    if y < -row_h or y > h + row_h: continue
                    if k == 0:
                        c = QColor(200, 255, 200); c.setAlpha(255)
                    else:
                        a = int(255 * (1 - k / tail) ** 1.5)
                        c = QColor(0, 255, 70); c.setAlpha(a)
                    painter.setPen(c)
                    ch = chr(0x30A0 + ((int(x) + k + int(self.t * 10)) % 96))
                    painter.drawText(QPointF(x, y), ch)
            painter.setPen(Qt.PenStyle.NoPen)
        elif m == "rain":
            painter.fillRect(rect, QColor("#0a1220"))
            pen = QPen(QColor(140, 180, 255, 180))
            pen.setWidthF(1.4); pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            for p in self.particles:
                x = p["x"] * w; y = p["y"] * h; ly = p["len"] * h
                c = QColor(140, 180, 255); c.setAlpha(int(90 + 120 * (1 - p["y"])))
                pen.setColor(c); painter.setPen(pen)
                painter.drawLine(QPointF(x, y), QPointF(x - 3, y + ly))
            painter.setPen(Qt.PenStyle.NoPen)
        elif m == "fireflies":
            painter.fillRect(rect, QColor("#0a0a14"))
            painter.setPen(Qt.PenStyle.NoPen)
            for p in self.particles:
                x, y = p["x"] * w, p["y"] * h
                pulse = 0.5 + 0.5 * math.sin(self.t * p["pulse"] + p["phase"])
                r = 2.0 + 2.0 * pulse
                c = QColor(255, 230, 130); c.setAlpha(int(60 + 180 * pulse))
                rg = QRadialGradient(QPointF(x, y), r * 4)
                rg.setColorAt(0, c)
                ce = QColor(c); ce.setAlpha(0)
                rg.setColorAt(1, ce)
                painter.setBrush(rg); painter.drawEllipse(QPointF(x, y), r * 4, r * 4)
        elif m == "confetti":
            painter.fillRect(rect, QColor("#101820"))
            painter.setPen(Qt.PenStyle.NoPen)
            for p in self.particles:
                x, y = p["x"] * w, p["y"] * h
                c = QColor(p["color"]); c.setAlpha(230)
                painter.save()
                painter.translate(x, y); painter.rotate(p["rot"])
                painter.setBrush(c)
                pw = p["w"] * w; ph = p["h"] * h
                painter.drawRect(QRectF(-pw / 2, -ph / 2, pw, ph))
                painter.restore()
        elif m == "parallax":
            painter.fillRect(rect, QColor("#050510"))
            painter.setPen(Qt.PenStyle.NoPen)
            for p in self.particles:
                x, y = p["x"] * w, p["y"] * h; r = p["r"]
                c = QColor(255, 255, 255); c.setAlpha(int(60 + 180 * p["depth"]))
                painter.setBrush(c); painter.drawEllipse(QPointF(x, y), r, r)
        elif m == "particles":
            painter.fillRect(rect, QColor("#0d1117"))
            pts = [(p["x"] * w, p["y"] * h) for p in self.particles]
            pen = QPen(QColor(100, 180, 255)); pen.setWidthF(1.0)
            D2 = 130 * 130
            for i in range(len(pts)):
                for j in range(i + 1, len(pts)):
                    dx = pts[i][0] - pts[j][0]
                    dy = pts[i][1] - pts[j][1]
                    d2 = dx * dx + dy * dy
                    if d2 < D2:
                        a = int(120 * (1 - math.sqrt(d2) / 130))
                        c = QColor(100, 180, 255); c.setAlpha(max(0, a))
                        pen.setColor(c); painter.setPen(pen)
                        painter.drawLine(QPointF(*pts[i]), QPointF(*pts[j]))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(120, 200, 255))
            for x, y in pts:
                painter.drawEllipse(QPointF(x, y), 2.2, 2.2)
        elif m == "rings":
            painter.fillRect(rect, QColor("#0a0a14"))
            cx, cy = w / 2, h / 2
            max_r = math.hypot(w, h) / 2
            for p in self.particles:
                phase = (self.t * 0.35 + p["phase"]) % 1.0
                r = phase * max_r
                alpha = int(180 * (1 - phase))
                c = QColor.fromHsv(int((p["hue"] + self.t * 20) % 360), 200, 220)
                c.setAlpha(alpha)
                pen = QPen(c); pen.setWidthF(3.0)
                painter.setPen(pen); painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(QPointF(cx, cy), r, r)
            painter.setPen(Qt.PenStyle.NoPen)
        elif m == "hex":
            painter.fillRect(rect, QColor("#0a1218"))
            cols = self.extra.get("cols", 26); rows = self.extra.get("rows", 16)
            cw = w / cols; ch = h / rows
            R = min(cw, ch) / 2 * 0.95
            painter.setPen(Qt.PenStyle.NoPen)
            for p in self.particles:
                cx = (p["c"] + 0.5) * cw + (p["r"] % 2) * cw / 2
                cy = (p["r"] + 0.5) * ch
                pulse = 0.5 + 0.5 * math.sin(self.t * 1.2 + p["phase"])
                a = int(40 + 120 * pulse)
                c = QColor(80, 180, 220); c.setAlpha(a)
                painter.setBrush(c)
                poly = QPolygonF()
                for k in range(6):
                    ang = math.radians(60 * k - 30)
                    poly.append(QPointF(cx + R * math.cos(ang),
                                        cy + R * math.sin(ang)))
                painter.drawPolygon(poly)
        elif m == "plasma":
            step = 32
            for yy in range(0, int(h), step):
                for xx in range(0, int(w), step):
                    nx = xx / w; ny = yy / h
                    v = (math.sin(nx * 8 + self.t * 1.2)
                         + math.sin(ny * 8 + self.t * 1.7)
                         + math.sin((nx + ny) * 8 + self.t * 0.9)
                         + math.sin(math.hypot(nx - 0.5, ny - 0.5) * 20 - self.t * 2.0))
                    hue = int((v + 4) / 8 * 360) % 360
                    c = QColor.fromHsv(hue, 180, 120)
                    painter.fillRect(xx, yy, step, step, c)
        elif m == "nebula":
            painter.fillRect(rect, QColor("#04040e"))
            painter.setPen(Qt.PenStyle.NoPen)
            for p in self.particles:
                cx, cy = p["x"] * w, p["y"] * h
                r = p["r"] * min(w, h)
                pulse = 0.5 + 0.5 * math.sin(self.t * 0.6 + p["phase"])
                hue = int(p["hue"] + self.t * 8) % 360
                c = QColor.fromHsv(hue, 180, 180)
                c.setAlpha(int(50 + 80 * pulse))
                rg = QRadialGradient(QPointF(cx, cy), r)
                rg.setColorAt(0, c)
                ce = QColor(c); ce.setAlpha(0)
                rg.setColorAt(1, ce)
                painter.setBrush(rg); painter.drawEllipse(QPointF(cx, cy), r, r)
        elif m == "waves":
            painter.fillRect(rect, QColor("#0a1020"))
            rows = self.extra.get("rows", 6)
            painter.setPen(Qt.PenStyle.NoPen)
            for i in range(rows):
                yy = (i + 0.5) * h / rows
                amp = h * 0.05
                path = QPainterPath(); path.moveTo(0, yy)
                for xx in range(0, int(w) + 1, 6):
                    nx = xx / w
                    y = yy + amp * math.sin(nx * 6 + self.t * 1.2 + i * 0.9)
                    path.lineTo(xx, y)
                path.lineTo(w, h); path.lineTo(0, h); path.closeSubpath()
                hue = int((i * 40 + self.t * 25) % 360)
                c = QColor.fromHsv(hue, 180, 180)
                c.setAlpha(int(90 + 40 * math.sin(self.t + i)))
                painter.setBrush(c); painter.drawPath(path)
        elif m == "lightning":
            painter.fillRect(rect, QColor("#0a0a10"))
            for p in self.particles:
                bright = math.sin(self.t * p["freq"] + p["phase"])
                if bright < 0.4: continue
                alpha = int(220 * (bright - 0.4) / 0.6)
                x = p["x"] * w; y = p["y"] * h
                ang = math.radians(p["angle"])
                length = p["len"] * min(w, h)
                ex = x + math.cos(ang) * length
                ey = y + math.sin(ang) * length
                c = QColor(180, 220, 255); c.setAlpha(alpha)
                pen = QPen(c); pen.setWidthF(1.6)
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                painter.setPen(pen)
                painter.drawLine(QPointF(x, y), QPointF(ex, ey))
            painter.setPen(Qt.PenStyle.NoPen)
        elif m == "pulse":
            painter.fillRect(rect, QColor("#0d0a14"))
            cx, cy = w / 2, h / 2
            max_r = min(w, h) * 0.7
            for i in range(5):
                ph = (self.t * 0.5 + i * 0.2) % 1.0
                r = ph * max_r
                a = int(150 * (1 - ph))
                c = QColor(accent_color); c.setAlpha(a)
                pen = QPen(c); pen.setWidthF(4.0)
                painter.setPen(pen); painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(QPointF(cx, cy), r, r)
            g = 0.5 + 0.5 * math.sin(self.t * 1.5)
            c = QColor(accent_color); c.setAlpha(int(80 + 80 * g))
            rg = QRadialGradient(QPointF(cx, cy), max_r * 0.4)
            rg.setColorAt(0, c)
            ce = QColor(c); ce.setAlpha(0)
            rg.setColorAt(1, ce)
            painter.setPen(Qt.PenStyle.NoPen); painter.setBrush(rg)
            painter.drawEllipse(QPointF(cx, cy), max_r * 0.4, max_r * 0.4)
        elif m == "ink":
            painter.fillRect(rect, QColor("#0a0a12"))
            painter.setPen(Qt.PenStyle.NoPen)
            for p in self.particles:
                cx, cy = p["x"] * w, p["y"] * h
                pulse = 0.5 + 0.5 * math.sin(self.t * 0.5 + p["phase"])
                r = p["r"] * min(w, h) * (0.7 + 0.5 * pulse)
                hue = int(p["hue"] + self.t * 10) % 360
                c = QColor.fromHsv(hue, 180, 220)
                c.setAlpha(int(40 + 60 * pulse))
                rg = QRadialGradient(QPointF(cx, cy), r)
                rg.setColorAt(0, c)
                ce = QColor(c); ce.setAlpha(0)
                rg.setColorAt(1, ce)
                painter.setBrush(rg); painter.drawEllipse(QPointF(cx, cy), r, r)
        elif m == "vortex":
            painter.fillRect(rect, QColor("#06060c"))
            cx, cy = w / 2, h / 2
            painter.setPen(Qt.PenStyle.NoPen)
            for p in self.particles:
                ang = p["angle"] + self.t * p["speed"]
                r = p["radius"] * min(w, h)
                x = cx + math.cos(ang) * r
                y = cy + math.sin(ang) * r
                hue = int((p["hue"] + self.t * 40) % 360)
                c = QColor.fromHsv(hue, 200, 230); c.setAlpha(200)
                painter.setBrush(c)
                painter.drawEllipse(QPointF(x, y), p["r"], p["r"])
        elif m == "grid":
            painter.fillRect(rect, QColor("#080a14"))
            cols = self.extra.get("cols", 30); rows = self.extra.get("rows", 20)
            cw = w / cols; ch = h / rows
            pen = QPen(QColor(80, 180, 220, 90)); pen.setWidthF(1.0)
            painter.setPen(pen)
            offset_x = (self.t * 20) % cw
            offset_y = (self.t * 20) % ch
            for i in range(cols + 2):
                x = i * cw - offset_x
                painter.drawLine(QPointF(x, 0), QPointF(x, h))
            for j in range(rows + 2):
                y = j * ch - offset_y
                painter.drawLine(QPointF(0, y), QPointF(w, y))
            painter.setPen(Qt.PenStyle.NoPen)
            for i in range(cols + 2):
                for j in range(rows + 2):
                    x = i * cw - offset_x; y = j * ch - offset_y
                    pulse = 0.5 + 0.5 * math.sin(self.t * 2 + i * 0.5 + j * 0.7)
                    a = int(60 + 120 * pulse)
                    c = QColor(100, 220, 255); c.setAlpha(a)
                    painter.setBrush(c)
                    painter.drawEllipse(QPointF(x, y), 2.0, 2.0)


class AdBlock(QWebEngineUrlRequestInterceptor):
    BLOCKED = [
        b"doubleclick.net", b"googlesyndication.com", b"google-analytics.com",
        b"googletagmanager.com", b"googletagservices.com", b"adservice.google",
        b"ads.yahoo.com", b"adnxs.com", b"criteo.com", b"criteo.net",
        b"taboola.com", b"outbrain.com", b"facebook.com/tr", b"vk.com/rtrg",
        b"top-fwz1.mail.ru", b"hotjar.com", b"fullstory.com", b"heap.io",
        b"mixpanel.com", b"segment.io", b"segment.com", b"amplitude.com",
        b"branch.io", b"adjust.com", b"appsflyer.com", b"kochava.com",
        b"quantcast.com", b"scorecardresearch.com", b"comscore.com",
        b"nielsen.com", b"chartbeat.com", b"parsely.com", b"newrelic.com",
        b"bugsnag.com", b"sentry.io", b"logrocket.com", b"mouseflow.com",
        b"crazyegg.com", b"luckyorange.com", b"inspectlet.com",
        b"clarity.ms", b"bat.bing.com", b"linkedin.com/px",
        b"twitter.com/i/adsct", b"t.co/i/adsct", b"snapchat.com/tr",
        b"analytics.tiktok.com", b"ct.pinterest.com",
        b"reddit.com/static/pixel", b"yandex.ru/metrika", b"mc.yandex",
        b"metrika.yandex", b"adfox.ru", b"adriver.ru", b"admon.pro",
        b"bumlam.com", b"mradx.net", b"yadro.ru",
    ]
    WHITELIST = [
        b"yandex.ru", b"yandex.net", b"yandex.com", b"yastatic.net",
        b"dzen.ru", b"dzeninfra.ru", b"mail.ru", b"vk.com", b"ok.ru",
        b"google.com", b"youtube.com", b"googlevideo.com",
        b"brave.com", b"search.brave.com", b"duckduckgo.com",
        b"bing.com", b"yahoo.com", b"translate.google.com",
        b"translate.googleusercontent.com",
    ]

    def interceptRequest(self, info):
        page = bytes(info.firstPartyUrl().toString().lower(), "utf-8")
        for w in self.WHITELIST:
            if w in page: return
        url = bytes(info.requestUrl().toString().lower(), "utf-8")
        for b in self.BLOCKED:
            if b in url:
                info.block(True); return


class PasswordStore:
    def __init__(self):
        self.entries = []
        self.load()

    def load(self):
        if not os.path.exists(PASSWORDS_FILE):
            self.entries = []; return
        try:
            with open(PASSWORDS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for e in data:
                self.entries.append({
                    "site": e["site"],
                    "username": base64.b64decode(e["username"]).decode(),
                    "password": base64.b64decode(e["password"]).decode(),
                })
        except Exception:
            self.entries = []

    def save(self):
        data = [{
            "site": e["site"],
            "username": base64.b64encode(e["username"].encode()).decode(),
            "password": base64.b64encode(e["password"].encode()).decode(),
        } for e in self.entries]
        try:
            with open(PASSWORDS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception: pass

    @staticmethod
    def _norm(u):
        h = urlparse(u).netloc.lower() if "://" in u else u.lower()
        return h[4:] if h.startswith("www.") else h

    def find(self, url):
        h = self._norm(url)
        if not h: return None
        for e in self.entries:
            if self._norm(e["site"]) == h: return e
        return None

    def upsert(self, url, u, p):
        h = self._norm(url)
        if not h: return
        for e in self.entries:
            if self._norm(e["site"]) == h:
                e["username"] = u; e["password"] = p; self.save(); return
        self.entries.append({"site": h, "username": u, "password": p})
        self.save()

    def delete(self, idx):
        if 0 <= idx < len(self.entries):
            self.entries.pop(idx); self.save()


class PasswordBridge(QObject):
    saveRequested = pyqtSignal(str, str, str)

    @pyqtSlot(str, str, str)
    def suggestSave(self, url, u, p):
        self.saveRequested.emit(url, u, p)


class ToggleSwitch(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(self, checked=False, parent=None):
        super().__init__(parent)
        self._checked = bool(checked)
        self._offset = 1.0 if self._checked else 0.0
        self.setFixedSize(46, 24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._on_color = QColor("#3b82f6")
        self._off_color = QColor("#555555")
        self._knob_color = QColor("#ffffff")
        self._anim = QPropertyAnimation(self, b"offset", self)
        self._anim.setDuration(140)

    @pyqtProperty(float)
    def offset(self): return self._offset

    @offset.setter
    def offset(self, v): self._offset = v; self.update()

    def setColors(self, on_color, off_color, knob_color="#ffffff"):
        self._on_color = QColor(on_color); self._off_color = QColor(off_color)
        self._knob_color = QColor(knob_color); self.update()

    def isChecked(self): return self._checked

    def setChecked(self, v, animate=True):
        v = bool(v)
        if self._checked == v: return
        self._checked = v
        if animate:
            self._anim.stop(); self._anim.setStartValue(self._offset)
            self._anim.setEndValue(1.0 if self._checked else 0.0); self._anim.start()
        else:
            self._offset = 1.0 if self._checked else 0.0; self.update()
        self.toggled.emit(self._checked)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.setChecked(not self._checked)
        super().mousePressEvent(e)

    def paintEvent(self, e):
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height(); r = h / 2.0
        cr = int(self._off_color.red() + (self._on_color.red() - self._off_color.red()) * self._offset)
        cg = int(self._off_color.green() + (self._on_color.green() - self._off_color.green()) * self._offset)
        cb = int(self._off_color.blue() + (self._on_color.blue() - self._off_color.blue()) * self._offset)
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(QColor(cr, cg, cb)))
        p.drawRoundedRect(0, 0, w, h, r, r)
        ks = h - 6
        kx = 3 + self._offset * (w - ks - 6)
        p.setBrush(QBrush(self._knob_color)); p.drawEllipse(int(kx), 3, ks, ks)
        p.end()


class ColorPickerButton(QPushButton):
    colorChanged = pyqtSignal(str)

    def __init__(self, current, default, parent=None):
        super().__init__(parent)
        self._current = current or ""
        self._default = default
        self.setFixedSize(48, 26)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_style()

    def _update_style(self):
        c = self._current if self._current else self._default
        border = "#888" if self._current else "#666"
        self.setStyleSheet(
            f"QPushButton {{ background: {c}; border: 1px solid {border}; "
            f"border-radius: 6px; color: transparent; }}"
            f"QPushButton:hover {{ border: 1px solid #fff; }}")

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.RightButton:
            self._current = ""
            self._update_style()
            self.colorChanged.emit("")
            return
        initial = QColor(self._current or self._default)
        c = QColorDialog.getColor(initial, self, "Choose color")
        if c.isValid():
            self._current = c.name()
            self._update_style()
            self.colorChanged.emit(self._current)


class DownloadsButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("navBtn")
        self.setFixedSize(34, 28); self.setIconSize(QSize(18, 18))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._progress = 0.0; self._downloading = False
        self._flash = 0.0; self._phase = 0.0
        self._arc_color = QColor("#3b82f6"); self._done_color = QColor("#22c55e")
        self._timer = QTimer(self); self._timer.setInterval(25)
        self._timer.timeout.connect(self._tick)
        self._flash_timer = QTimer(self); self._flash_timer.setSingleShot(True)
        self._flash_timer.timeout.connect(self._on_flash_end)

    def set_arc_color(self, c): self._arc_color = QColor(c); self.update()

    def set_progress(self, v):
        try: v = float(v)
        except (TypeError, ValueError): v = 0.0
        self._progress = max(0.0, min(1.0, v)); self.update()

    def set_downloading(self, a):
        a = bool(a)
        if self._downloading == a:
            if a and not self._timer.isActive(): self._timer.start()
            return
        self._downloading = a
        if a:
            if not self._timer.isActive(): self._timer.start()
        elif self._flash <= 0:
            self._timer.stop()
        self.update()

    def flash_done(self):
        self._flash = 1.0; self._flash_timer.start(1200)
        if not self._timer.isActive(): self._timer.start()
        self.update()

    def _on_flash_end(self):
        self._flash = 0.0
        if not self._downloading: self._timer.stop()
        self.update()

    def _tick(self):
        self._phase = (self._phase + 0.03) % 1.0; self.update()

    def paintEvent(self, e):
        super().paintEvent(e)
        if not self._downloading and self._flash <= 0: return
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w / 2.0, h / 2.0; radius = 11.5
        rect = QRectF(cx - radius, cy - radius, radius * 2, radius * 2)
        pen = QPen(QColor(255, 255, 255, 40)); pen.setWidthF(2.0)
        p.setPen(pen); p.setBrush(Qt.BrushStyle.NoBrush); p.drawEllipse(rect)
        if self._downloading:
            span = int(self._progress * 360 * 16)
            if span > 0:
                pen = QPen(self._arc_color); pen.setWidthF(2.6)
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                p.setPen(pen); p.drawArc(rect, 90 * 16, -span)
            angle = self._phase * 360.0; rad = math.radians(angle)
            dx = cx + radius * math.cos(rad); dy = cy - radius * math.sin(rad)
            p.setPen(Qt.PenStyle.NoPen); p.setBrush(self._arc_color)
            p.drawEllipse(QPointF(dx, dy), 2.0, 2.0)
        elif self._flash > 0:
            pen = QPen(self._done_color); pen.setWidthF(2.6)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen); p.drawEllipse(rect)
        p.end()


class DownloadToast(QWidget):
    def __init__(self, main_window, name, parent=None):
        super().__init__(parent or main_window)
        self.main = main_window
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(320, 84)
        self._name = name or "download"
        self._progress = 0.0
        self._status = "0%"
        self._opacity = QGraphicsOpacityEffect(self)
        self._opacity.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity)
        self._fade = QPropertyAnimation(self._opacity, b"opacity", self)
        self._fade.setDuration(220)

    def set_progress(self, p, status=None):
        try:
            self._progress = max(0.0, min(1.0, float(p)))
        except (TypeError, ValueError):
            self._progress = 0.0
        if status is not None:
            self._status = status
        self.update()

    def show_toast(self):
        parent = self.parent()
        if parent is not None:
            try:
                w = parent.width(); h = parent.height()
                self.move(max(0, w - self.width() - 24),
                          max(0, h - self.height() - 24))
            except Exception:
                pass
        self.show()
        self.raise_()
        self._fade.stop()
        self._fade.setStartValue(self._opacity.opacity())
        self._fade.setEndValue(1.0)
        self._fade.start()

    def fade_out_and_close(self):
        self._fade.stop()
        try:
            self._fade.finished.disconnect()
        except Exception:
            pass
        self._fade.setStartValue(self._opacity.opacity())
        self._fade.setEndValue(0.0)
        self._fade.finished.connect(self.deleteLater)
        self._fade.start()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        pal = self.main.get_effective_palette()
        r = QRectF(2, 2, self.width() - 4, self.height() - 4)
        p.setPen(QPen(QColor(pal["border"]), 1))
        p.setBrush(QColor(pal["panel"]))
        p.drawRoundedRect(r, 12, 12)

        p.setPen(QColor(pal["text"]))
        f = QFont(); f.setPointSize(10); f.setBold(True)
        p.setFont(f)
        p.drawText(QRect(16, 10, self.width() - 32, 22),
                   Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                   self._name[:40])

        p.setPen(QColor(pal["text2"]))
        f2 = QFont(); f2.setPointSize(9)
        p.setFont(f2)
        p.drawText(QRect(16, 32, self.width() - 32, 18),
                   Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                   self._status)

        bar = QRectF(16, 60, self.width() - 32, 6)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(pal["bg"]))
        p.drawRoundedRect(bar, 3, 3)
        if self._progress > 0:
            fill = QRectF(bar.left(), bar.top(),
                          bar.width() * self._progress, bar.height())
            p.setBrush(QColor(pal["accent"]))
            p.drawRoundedRect(fill, 3, 3)
        p.end()


class TabDragGhost(QWidget):
    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self._pixmap = pixmap
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(pixmap.size())

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        p.setOpacity(0.88); p.drawPixmap(0, 0, self._pixmap); p.end()


class WallpaperButton(QWidget):
    clicked = pyqtSignal()
    BASE = 34
    EXPANDED = 128

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main = main_window
        self._w = self.BASE
        self.setFixedSize(self.BASE, self.BASE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._anim = QPropertyAnimation(self, b"animWidth", self)
        self._anim.setDuration(200)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._on_change = None

    @pyqtProperty(int)
    def animWidth(self): return self._w

    @animWidth.setter
    def animWidth(self, val):
        old = self._w
        self._w = int(val)
        self.setFixedWidth(self._w)
        if self._on_change: self._on_change(self._w, old)
        self.update()

    def set_position_change_callback(self, cb): self._on_change = cb

    def enterEvent(self, e):
        self._anim.stop(); self._anim.setStartValue(self._w)
        self._anim.setEndValue(self.EXPANDED); self._anim.start()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._anim.stop(); self._anim.setStartValue(self._w)
        self._anim.setEndValue(self.BASE); self._anim.start()
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton: self.clicked.emit()

    def paintEvent(self, e):
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        pal = self.main.get_effective_palette()
        w, h = self.width(), self.height()
        p.setPen(QPen(QColor(pal["border"]), 1))
        p.setBrush(QColor(pal["panel"]))
        p.drawRoundedRect(0, 0, w - 1, h - 1, h / 2.0, h / 2.0)
        icon = _make_wallpaper_icon(QColor(pal["text"]), 20)
        ix = w - 20 - 7; iy = (h - 20) // 2
        p.drawPixmap(ix, iy, icon)
        if w > self.BASE + 8:
            p.setPen(QColor(pal["text"]))
            font = QFont(); font.setPointSize(9); font.setBold(True)
            p.setFont(font)
            p.drawText(QRect(10, 0, w - 36, h),
                       Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                       self.main.tr("wallpaper"))
        p.end()


class WallpaperPopup(QDialog):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main = main_window
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setFixedWidth(300)
        pal = main_window.get_effective_palette()
        self.setStyleSheet(f"""
            QDialog {{ background-color: {pal['panel']};
                border: 1px solid {pal['border']}; border-radius: 12px; }}
            QLabel {{ color: {pal['text']}; background: transparent; }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 14); layout.setSpacing(10)
        title = QLabel(main_window.tr("wallpaper_title"))
        title.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {pal['text']};")
        layout.addWidget(title)
        grid = QGridLayout(); grid.setSpacing(8)
        current = main_window.qsettings.value("new_tab_color", "auto")
        has_custom = bool(main_window.get_new_tab_wallpaper())
        colors = [("auto", main_window.tr("wallpaper_auto"), pal["bg"])]
        for key, theme_pal in THEME_PALETTES.items():
            colors.append((key, THEME_NAMES[key].get(main_window.language, key),
                           theme_pal["bg"]))
        cols = 3
        for i, (key, name, color) in enumerate(colors):
            btn = QPushButton(); btn.setFixedSize(80, 60)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            is_sel = (current == key) and not has_custom
            border = pal["accent"] if is_sel else pal["border"]
            bw = 2 if is_sel else 1
            btn.setStyleSheet(f"""
                QPushButton {{ background-color: {color};
                    border: {bw}px solid {border}; border-radius: 8px; }}
                QPushButton:hover {{ border: 2px solid {pal['accent']}; }}
            """)
            btn.setToolTip(name)
            btn.clicked.connect(lambda c=False, k=key: self._pick(k))
            grid.addWidget(btn, i // cols, i % cols)
        custom_btn = QPushButton("+"); custom_btn.setFixedSize(80, 60)
        custom_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        f = QFont(); f.setPointSize(20); f.setWeight(QFont.Weight.Light)
        custom_btn.setFont(f)
        custom_btn.setStyleSheet(f"""
            QPushButton {{ background: transparent; border: 2px dashed {pal['border']};
                border-radius: 8px; color: {pal['text2']}; padding: 0 0 3px 0; }}
            QPushButton:hover {{ border: 2px dashed {pal['accent']}; color: {pal['accent']};
                background: {pal['panel_hover']}; }}
        """)
        custom_btn.setToolTip(main_window.tr("wallpaper_custom"))
        custom_btn.clicked.connect(self._pick_custom)
        ci = len(colors)
        grid.addWidget(custom_btn, ci // cols, ci % cols)
        layout.addLayout(grid)

    def _pick(self, key):
        self.main.set_new_tab_color(key); self.accept()

    def _pick_custom(self):
        self.accept()
        QTimer.singleShot(100, lambda m=self.main: WallpaperPopup._open_file(m))

    @staticmethod
    def _open_file(main):
        start = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.PicturesLocation) or os.path.expanduser("~")
        cur = main.get_new_tab_wallpaper()
        if cur and os.path.exists(os.path.dirname(cur)):
            start = os.path.dirname(cur)
        path, _ = QFileDialog.getOpenFileName(
            main, main.tr("wallpaper_choose"), start, main.tr("wallpaper_filter"))
        if path:
            main.set_new_tab_wallpaper(path)


class NewTabPage(QWidget):
    def __init__(self, main_window, parent=None, show_wallpaper_button=True):
        super().__init__(parent)
        self.main = main_window
        self.show_wallpaper_button = show_wallpaper_button
        self.setAutoFillBackground(False)
        self._wp_pixmap = None
        self._wp_pixmap_path = None
        self._wp_pixmap_size = None
        self._live_engine = None
        self._live_speed = 1.0
        self._live_timer = QTimer(self)
        self._live_timer.setInterval(50)
        self._live_timer.timeout.connect(self._live_tick)

        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0); v.addStretch()
        h = QHBoxLayout(); h.addStretch()
        self.wall_btn = None
        if show_wallpaper_button:
            self.wall_btn = WallpaperButton(main_window, self)
            self.wall_btn.clicked.connect(self._open_wallpaper_popup)
            self.wall_btn.set_position_change_callback(self._reposition_btn)
            self.wall_btn.setParent(self); self.wall_btn.move(0, 0)
            self.apply_wall_btn_visibility()
        v.addLayout(h)
        self._update_live_state()

    def _update_live_state(self):
        mode = self.main.get_live_wallpaper_mode()
        self._live_speed = self.main.get_live_wallpaper_speed()
        if mode and mode != "none":
            if self._live_engine is None:
                self._live_engine = LiveWallpaperEngine(mode)
            elif self._live_engine.mode != mode:
                self._live_engine.set_mode(mode)
            if self.isVisible() and not self._live_timer.isActive():
                self._live_timer.start()
        else:
            self._live_timer.stop()
            self._live_engine = None
        self.update()

    def _live_tick(self):
        if not self.isVisible() or self._live_engine is None: return
        self._live_engine.advance(0.05 * self._live_speed)
        self.update()

    def showEvent(self, e):
        super().showEvent(e); self._update_live_state()

    def hideEvent(self, e):
        super().hideEvent(e); self._live_timer.stop()

    def apply_wall_btn_visibility(self):
        if self.wall_btn is None: return
        self.wall_btn.setVisible(self.show_wallpaper_button and
                                 not self.main.hide_wallpaper_button)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._wp_pixmap = None; self._wp_pixmap_path = None
        self._wp_pixmap_size = None
        if self.wall_btn is None: return
        btn = self.wall_btn
        bx = self.width() - btn.width() - 28
        by = self.height() - btn.height() - 28
        btn.move(max(0, bx), max(0, by))

    def _reposition_btn(self, nw, ow):
        if self.wall_btn is None or nw == ow: return
        self.wall_btn.move(self.wall_btn.x() - (nw - ow), self.wall_btn.y())
        if self.wall_btn.x() < 10:
            self.wall_btn.move(10, self.wall_btn.y())

    def _open_wallpaper_popup(self):
        if self.wall_btn is None: return
        popup = WallpaperPopup(self.main, self.window()); popup.adjustSize()
        btn = self.wall_btn
        tl = btn.mapToGlobal(QPoint(0, 0))
        right = tl.x() + btn.width()
        top = tl.y(); bottom = tl.y() + btn.height()
        pw, ph = popup.width(), popup.height()
        screen = QApplication.primaryScreen().availableGeometry()
        m = 8
        x = right - pw; y = top - ph - 8
        if y < screen.top() + m:
            y = bottom + 8 if bottom + 8 + ph <= screen.bottom() - m else screen.top() + m
        if x < screen.left() + m: x = screen.left() + m
        if x + pw > screen.right() - m: x = screen.right() - pw - m
        if y + ph > screen.bottom() - m: y = screen.bottom() - ph - m
        if y < screen.top() + m: y = screen.top() + m
        popup.move(QPoint(int(x), int(y))); popup.exec()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        drew = False
        if self._live_engine is not None:
            pal = self.main.get_effective_palette()
            self._live_engine.paint(p, self.rect(),
                                    self.main.get_new_tab_color(), pal["accent"])
            drew = True
        if not drew and self.show_wallpaper_button:
            wp = self.main.get_new_tab_wallpaper()
            if wp and os.path.exists(wp):
                if (self._wp_pixmap is None or self._wp_pixmap_path != wp
                        or self._wp_pixmap_size != self.size()):
                    pix = QPixmap(wp)
                    if not pix.isNull():
                        scaled = pix.scaled(self.size(),
                                            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                            Qt.TransformationMode.SmoothTransformation)
                        self._wp_pixmap = scaled
                        self._wp_pixmap_path = wp
                        self._wp_pixmap_size = self.size()
                    else:
                        self._wp_pixmap = None; self._wp_pixmap_path = None
                        self._wp_pixmap_size = None
                if self._wp_pixmap is not None:
                    x = (self.width() - self._wp_pixmap.width()) // 2
                    y = (self.height() - self._wp_pixmap.height()) // 2
                    p.drawPixmap(x, y, self._wp_pixmap); drew = True
        if not drew:
            p.fillRect(self.rect(), QColor(self.main.get_new_tab_color()))
        p.end()


class BookmarksBar(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main = main_window
        self.setObjectName("bookmarksBar")
        self.setFixedHeight(30)
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(8, 2, 8, 2)
        self._layout.setSpacing(2)
        self._rebuild()

    def _clear(self):
        while self._layout.count():
            it = self._layout.takeAt(0)
            w = it.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

    def _rebuild(self):
        self._clear()
        pal = self.main.get_effective_palette()
        entries = self.main.bookmarks.entries
        if not entries:
            hint = QLabel(self.main.tr("bm_empty"))
            hint.setStyleSheet(
                f"color: {pal['text2']}; font-size: 11px; "
                f"background: transparent; padding: 0 6px;")
            self._layout.addWidget(hint)
            self._layout.addStretch()
            return
        for bm in entries[-40:]:
            title = bm.get("title", "") or bm.get("url", "")
            short = title[:28] + ("…" if len(title) > 29 else "")
            btn = QPushButton(short)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFlat(True)
            btn.setToolTip(bm.get("url", ""))
            btn.setStyleSheet(f"""
                QPushButton {{ background: transparent; color: {pal['text']};
                    border: none; border-radius: 6px; padding: 3px 8px;
                    font-size: 12px; font-weight: 500; }}
                QPushButton:hover {{ background: {pal['panel_hover']}; }}
            """)
            url = bm.get("url", "")
            btn.clicked.connect(lambda c=False, u=url: self.main.add_tab(u))
            btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            btn.customContextMenuRequested.connect(
                lambda pos, b=bm, w=btn: self._ctx_menu(pos, b, w))
            self._layout.addWidget(btn)
        self._layout.addStretch()

    def _ctx_menu(self, pos, bm, widget):
        url = bm.get("url", "")
        menu = QMenu(self)
        menu.setStyleSheet(_build_ctx_menu_qss(self.main.current_theme,
                                                self.main.custom_colors))
        a1 = menu.addAction(self.main.tr("bm_open_new_tab"))
        a1.triggered.connect(lambda c=False, u=url: self.main.add_tab(u))
        a2 = menu.addAction(self.main.tr("bm_open_new_window"))
        a2.triggered.connect(lambda c=False, u=url:
                             self.main.open_url_in_new_window(u))
        menu.addSeparator()
        a3 = menu.addAction(self.main.tr("bm_edit"))
        a3.triggered.connect(lambda c=False, b=bm: self._edit_title(b))
        menu.addSeparator()
        a4 = menu.addAction(self.main.tr("bm_delete"))
        a4.triggered.connect(lambda c=False, u=url: self._delete(url))
        menu.exec(widget.mapToGlobal(pos))

    def _edit_title(self, bm):
        new_title, ok = QInputDialog.getText(
            self, self.main.tr("bm_edit"), self.main.tr("col_bm_title"),
            text=bm.get("title", ""))
        if ok and new_title.strip():
            self.main.bookmarks.update_title(bm.get("url", ""), new_title.strip())
            self.main.bookmark_changed()

    def _delete(self, url):
        self.main.bookmarks.remove(url)
        self.main.bookmark_changed()


class TabAnimOverlay(QWidget):
    def __init__(self, pixmap, appear=False, glow_color=None, parent=None):
        super().__init__(parent)
        self._pixmap = pixmap; self._appear = appear
        self._glow_color = glow_color; self._progress = 0.0
        self._cb = None
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(pixmap.size())
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(280)
        self._anim.setStartValue(0.0); self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.valueChanged.connect(self._on_v)
        self._anim.finished.connect(self._on_f)

    def set_finished_callback(self, cb): self._cb = cb

    def _on_v(self, v): self._progress = float(v); self.update()

    def _on_f(self):
        cb = self._cb; self._cb = None
        if cb:
            try: cb()
            except Exception: pass
        self.deleteLater()

    def start(self): self.show(); self.raise_(); self._anim.start()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        t = self._progress
        if self._appear:
            scale = 0.72 + 0.28 * t; opacity = t
        else:
            scale = 1.0 - 0.28 * t; opacity = 1.0 - t
        p.setOpacity(max(0.0, min(1.0, opacity)))
        w = max(1, int(self.width() * scale))
        h = max(1, int(self.height() * scale))
        x = (self.width() - w) // 2; y = (self.height() - h) // 2
        if (not self._appear) and self._glow_color is not None and t < 0.85:
            tint = 1.0 - t / 0.85
            tinted = QPixmap(self._pixmap.size())
            tinted.fill(Qt.GlobalColor.transparent)
            tp = QPainter(tinted)
            tp.setRenderHint(QPainter.RenderHint.Antialiasing)
            tp.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            tp.drawPixmap(0, 0, self._pixmap)
            tp.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceAtop)
            c = QColor(self._glow_color); c.setAlpha(int(210 * tint))
            tp.fillRect(tinted.rect(), c); tp.end()
            p.drawPixmap(QRect(x, y, w, h), tinted)
        else:
            p.drawPixmap(QRect(x, y, w, h), self._pixmap)
        p.end()


class ResizeHandle(QWidget):
    def __init__(self, edge, win, parent=None):
        super().__init__(parent)
        self.edge = edge; self.win = win
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setStyleSheet("background: transparent;")
        cursors = {"tl": Qt.CursorShape.SizeFDiagCursor,
                   "tr": Qt.CursorShape.SizeBDiagCursor,
                   "bl": Qt.CursorShape.SizeBDiagCursor,
                   "br": Qt.CursorShape.SizeFDiagCursor,
                   "t": Qt.CursorShape.SizeVerCursor,
                   "b": Qt.CursorShape.SizeVerCursor,
                   "l": Qt.CursorShape.SizeHorCursor,
                   "r": Qt.CursorShape.SizeHorCursor}
        self.setCursor(cursors.get(edge, Qt.CursorShape.ArrowCursor))
        self._start_pos = None; self._start_geo = None

    def mousePressEvent(self, e):
        if (e.button() == Qt.MouseButton.LeftButton
                and not self.win.isMaximized() and not self.win.isFullScreen()):
            self._start_pos = e.globalPosition().toPoint()
            self._start_geo = self.win.geometry(); e.accept()
        else:
            super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        if self._start_pos is not None and (e.buttons() & Qt.MouseButton.LeftButton):
            self.win._apply_resize(self.edge, self._start_pos, self._start_geo,
                                   e.globalPosition().toPoint()); e.accept()
        else:
            super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        self._start_pos = None; self._start_geo = None; e.accept()


class PlusTabBar(QTabBar):
    layoutChanged = pyqtSignal()
    scrollRequested = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setElideMode(Qt.TextElideMode.ElideRight)
        self.setExpanding(False); self.setDrawBase(False)
        self.setUsesScrollButtons(False); self.setMouseTracking(True)
        self.setMovable(True)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.setMinimumWidth(0)
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        preset = DENSITY_PRESETS["standard"]
        self.TAB_MIN_WIDTH = preset["tab_min_w"]
        self.TAB_MAX_WIDTH = preset["tab_max_w"]
        self.TAB_HEIGHT = preset["tab_h"]
        self.TAB_RADIUS = preset["tab_radius"]
        self.TAB_EXTRA_PADDING = preset["tab_extra"]
        self.setFixedHeight(self.TAB_HEIGHT)

        self._hover_index = -1
        self._theme_name = "dark"
        self._custom_colors = None
        self._hidden_indices = set()
        self._drag_press_idx = -1
        self._drag_press_pos = None
        self._drag_started = False
        self._drag_ghost = None
        self._drag_ghost_offset_x = 0
        self._drag_target_idx = -1
        self._rtl = False

    def set_rtl(self, rtl):
        self._rtl = bool(rtl)
        self.update()

    def set_density(self, preset):
        self.TAB_MIN_WIDTH = preset["tab_min_w"]
        self.TAB_MAX_WIDTH = preset["tab_max_w"]
        self.TAB_HEIGHT = preset["tab_h"]
        self.TAB_RADIUS = preset["tab_radius"]
        self.TAB_EXTRA_PADDING = preset["tab_extra"]
        self.setFixedHeight(self.TAB_HEIGHT)
        self.updateGeometry()
        for i in range(self.count()):
            self.setTabText(i, self.tabText(i))
        self.update()

    def set_theme(self, name, custom_colors=None):
        self._theme_name = name; self._custom_colors = custom_colors
        self.update()

    def grab_tab_pixmap(self, index):
        rect = self.tabRect(index)
        if rect.isEmpty(): return None, rect
        return self.grab(rect), rect

    def start_appear_animation(self, idx):
        if idx < 0 or idx >= self.count():
            self._hidden_indices.discard(idx); self.update(); return
        self._hidden_indices.discard(idx); self.update()
        try: self.repaint()
        except Exception: pass
        pix, rect = self.grab_tab_pixmap(idx)
        if pix is None or pix.isNull() or rect.isEmpty():
            self._hidden_indices.discard(idx); self.update(); return
        self._hidden_indices.add(idx); self.update()
        top = self.window()
        if top is None or top is self:
            self._hidden_indices.discard(idx); self.update(); return
        pos = self.mapTo(top, rect.topLeft())
        overlay = TabAnimOverlay(pix, appear=True, parent=top)
        overlay.move(pos)
        overlay.set_finished_callback(lambda i=idx: self._on_appear_finished(i))
        overlay.start()

    def _on_appear_finished(self, idx):
        self._hidden_indices.discard(idx); self.update()

    def tabSizeHint(self, index):
        s = super().tabSizeHint(index)
        w = s.width() + self.TAB_EXTRA_PADDING
        w = max(self.TAB_MIN_WIDTH, min(self.TAB_MAX_WIDTH, w))
        return QSize(w, self.TAB_HEIGHT)

    def leaveEvent(self, e):
        if self._hover_index != -1:
            self._hover_index = -1; self.update()
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            idx = self.tabAt(e.pos())
            if idx != -1:
                self._drag_press_idx = idx
                self._drag_press_pos = e.pos()
                self._drag_started = False
        super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        idx = self.tabAt(e.pos())
        if idx != self._hover_index:
            self._hover_index = idx; self.update()
        if (self._drag_press_idx != -1 and
                (e.buttons() & Qt.MouseButton.LeftButton) and
                not self._drag_started and self._drag_press_pos is not None):
            if (e.pos() - self._drag_press_pos).manhattanLength() > 8:
                self._start_drag()
        if self._drag_started and self._drag_ghost is not None:
            top = self.window()
            if top is not None:
                piw = self.mapTo(top, e.pos())
                gx = piw.x() - self._drag_ghost_offset_x
                bp = self.mapTo(top, QPoint(0, 0))
                gy = bp.y() + (self.height() - self._drag_ghost.height()) // 2
                self._drag_ghost.move(gx, gy)
            new_idx = self._index_for_x(e.pos().x())
            if new_idx != self._drag_target_idx:
                self._drag_target_idx = new_idx; self.update()
            e.accept(); return
        super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        if self._drag_started and e.button() == Qt.MouseButton.LeftButton:
            src = self._drag_press_idx
            target = self._drag_target_idx if self._drag_target_idx >= 0 else src
            self._drag_started = False; self._drag_press_idx = -1
            self._drag_press_pos = None; self._drag_target_idx = -1
            if self._drag_ghost is not None:
                self._drag_ghost.hide(); self._drag_ghost.deleteLater()
                self._drag_ghost = None
            if src != -1 and target != -1 and src != target:
                try: self.moveTab(src, target)
                except Exception: pass
            self.update(); e.accept(); return
        self._drag_press_idx = -1; self._drag_press_pos = None
        self._drag_started = False; self._drag_target_idx = -1
        super().mouseReleaseEvent(e)

    def _start_drag(self):
        idx = self._drag_press_idx
        if idx < 0 or idx >= self.count(): return
        pix, rect = self.grab_tab_pixmap(idx)
        if pix is None or pix.isNull(): return
        self._drag_started = True; self._drag_target_idx = idx
        self._drag_ghost_offset_x = self._drag_press_pos.x() - rect.x()
        top = self.window()
        if top is None: top = self
        self._drag_ghost = TabDragGhost(pix, parent=top)
        piw = self.mapTo(top, rect.topLeft())
        self._drag_ghost.move(piw)
        self._drag_ghost.show(); self._drag_ghost.raise_(); self.update()

    def _index_for_x(self, x):
        n = self.count()
        if n == 0: return -1
        for i in range(n):
            r = self.tabRect(i)
            if x < r.center().x(): return i
        return n - 1

    def tabLayoutChange(self):
        super().tabLayoutChange(); self.layoutChanged.emit()

    def tabInserted(self, index):
        super().tabInserted(index); self.layoutChanged.emit()
        self._hidden_indices.add(index); self.update()
        QTimer.singleShot(0, lambda i=index: self.start_appear_animation(i))

    def tabRemoved(self, index):
        super().tabRemoved(index)
        new_hidden = set()
        for h in self._hidden_indices:
            if h < index: new_hidden.add(h)
            elif h > index: new_hidden.add(h - 1)
        self._hidden_indices = new_hidden
        self.layoutChanged.emit(); self.update()

    def wheelEvent(self, e):
        d = e.angleDelta().y()
        if d == 0: super().wheelEvent(e); return
        self.scrollRequested.emit(-1 if d > 0 else 1); e.accept()

    def paintEvent(self, e):
        pal = _effective_palette(self._theme_name, self._custom_colors)
        painter = QPainter(self); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        current = self.currentIndex(); radius = self.TAB_RADIUS
        rtl = self._rtl

        for i in range(self.count()):
            if i in self._hidden_indices: continue
            option = QStyleOptionTab(); self.initStyleOption(option, i)
            rect = self.tabRect(i)
            if rect.isEmpty() or rect.width() <= 0: continue
            tr_ = QRectF(rect.x() + 2, rect.y() + 2,
                         rect.width() - 5, rect.height() - 4)
            if tr_.width() <= 0 or tr_.height() <= 0: continue
            if i == current:
                bg = QColor(pal['hover']); fg = QColor(pal['text'])
            elif i == self._hover_index:
                bg = QColor(pal['panel_hover']); fg = QColor(pal['text'])
            else:
                bg = QColor(pal['panel']); fg = QColor(pal['text2'])
            painter.setOpacity(1.0)
            painter.setPen(QPen(QColor(pal['border']), 1))
            painter.setBrush(bg)
            painter.drawRoundedRect(tr_, radius, radius)

            if self._drag_started and self._drag_target_idx >= 0:
                ti = self._drag_target_idx
                if 0 <= ti < self.count():
                    trr = self.tabRect(ti)
                    lx = trr.left() + 1 if ti <= self._drag_press_idx else trr.right() - 1
                    painter.setPen(QPen(QColor(pal['accent']), 3,
                                        Qt.PenStyle.SolidLine,
                                        Qt.PenCapStyle.RoundCap))
                    painter.drawLine(lx, trr.top() + 6, lx, trr.bottom() - 6)

            pad = 12
            close_space = 32
            icon_size = 16
            icon_gap = 6
            icon_width = 0
            icon_pix = None
            try:
                data = self.tabData(i)
            except Exception:
                data = None
            if isinstance(data, QIcon) and not data.isNull():
                try:
                    pm = data.pixmap(icon_size, icon_size)
                    if not pm.isNull():
                        icon_pix = pm
                        icon_width = icon_size + icon_gap
                except Exception:
                    icon_pix = None
            if icon_pix is not None:
                if rtl:
                    ix = tr_.right() - close_space - icon_size
                else:
                    ix = tr_.left() + pad
                iy = tr_.top() + (tr_.height() - icon_size) / 2.0
                painter.drawPixmap(int(ix), int(iy), icon_size, icon_size, icon_pix)

            painter.setPen(fg)
            if rtl:
                text_rect = QRect(
                    int(tr_.left()) + close_space,
                    int(tr_.top()),
                    max(0, int(tr_.width()) - close_space - pad - icon_width),
                    int(tr_.height()))
                align = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight
            else:
                text_rect = QRect(
                    int(tr_.left()) + pad + icon_width,
                    int(tr_.top()),
                    max(0, int(tr_.width()) - close_space - pad - icon_width),
                    int(tr_.height()))
                align = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
            if text_rect.width() > 0:
                metrics = painter.fontMetrics()
                elided = metrics.elidedText(option.text, Qt.TextElideMode.ElideRight,
                                            text_rect.width())
                painter.drawText(text_rect, align, elided)
            painter.setOpacity(1.0)
        painter.end()


class TabCloseButton(QPushButton):
    def __init__(self, normal_icon, hover_icon, parent=None):
        super().__init__(parent)
        self.setObjectName("tabCloseBtn")
        self.setFixedSize(24, 24); self.setIconSize(QSize(18, 18))
        self._normal = QIcon(normal_icon); self._hover = QIcon(hover_icon)
        self.setIcon(self._normal)
        self.setCursor(Qt.CursorShape.PointingHandCursor); self.setFlat(True)

    def enterEvent(self, e): self.setIcon(self._hover); super().enterEvent(e)
    def leaveEvent(self, e): self.setIcon(self._normal); super().leaveEvent(e)

    def update_theme(self, np, hp):
        self._normal = QIcon(np); self._hover = QIcon(hp)
        self.setIcon(self._normal)


class TabCloseWrapper(QWidget):
    def __init__(self, normal_icon, hover_icon, right_margin=24, parent=None):
        super().__init__(parent)
        self._btn = TabCloseButton(normal_icon, hover_icon)
        self._right_margin = right_margin
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, right_margin, 0)
        layout.setSpacing(0); layout.addStretch(); layout.addWidget(self._btn)
        self.setStyleSheet("background: transparent;")

    @property
    def btn(self): return self._btn

    def set_side(self, rtl):
        layout = self.layout()
        if layout is None: return
        while layout.count(): layout.takeAt(0)
        if rtl:
            layout.setContentsMargins(self._right_margin, 0, 0, 0)
            layout.addWidget(self._btn); layout.addStretch()
        else:
            layout.setContentsMargins(0, 0, self._right_margin, 0)
            layout.addStretch(); layout.addWidget(self._btn)


class CustomTabWidget(QWidget):
    currentChanged = pyqtSignal(int)
    tabCloseRequested = pyqtSignal(int)

    def __init__(self, bar: PlusTabBar, parent=None):
        super().__init__(parent)
        self.setObjectName("customTabWidget")
        self._bar = bar
        self._stack = QStackedWidget(self)
        self._stack.setObjectName("tabPagesStack")
        l = QVBoxLayout(self)
        l.setContentsMargins(0, 0, 0, 0); l.setSpacing(0)
        l.addWidget(self._stack)
        self._bar.currentChanged.connect(self._on_bar_current)
        self._bar.tabCloseRequested.connect(self.tabCloseRequested.emit)
        self._bar.tabMoved.connect(self._on_bar_moved)

    def _on_bar_current(self, idx):
        if 0 <= idx < self._stack.count() and self._stack.currentIndex() != idx:
            self._stack.setCurrentIndex(idx)
        self.currentChanged.emit(idx)

    def _on_bar_moved(self, from_idx, to_idx):
        if from_idx == to_idx: return
        w = self._stack.widget(from_idx)
        if w is None: return
        cur = self._bar.currentIndex()
        self._stack.removeWidget(w)
        self._stack.insertWidget(to_idx, w)
        self._bar.blockSignals(True); self._bar.setCurrentIndex(cur)
        self._bar.blockSignals(False)
        if 0 <= cur < self._stack.count(): self._stack.setCurrentIndex(cur)

    def addTab(self, w, t):
        self._stack.addWidget(w); return self._bar.addTab(t)

    def removeTab(self, i):
        w = self._stack.widget(i)
        if w is not None: self._stack.removeWidget(w)
        self._bar.removeTab(i)

    def count(self): return self._bar.count()
    def widget(self, i): return self._stack.widget(i)
    def indexOf(self, w): return self._stack.indexOf(w)
    def currentIndex(self): return self._bar.currentIndex()

    def setCurrentIndex(self, i):
        self._bar.setCurrentIndex(i)
        try: self._on_bar_current(i)
        except Exception: self._stack.setCurrentIndex(i)

    def currentWidget(self): return self._stack.currentWidget()
    def setTabText(self, i, t): self._bar.setTabText(i, t)
    def tabText(self, i): return self._bar.tabText(i)
    def setTabButton(self, i, p, w): self._bar.setTabButton(i, p, w)
    def tabBar(self): return self._bar
    def setMovable(self, m): self._bar.setMovable(m)
    def setTabsClosable(self, v): pass
    def setTabPosition(self, pos): pass


class DragArea(QWidget):
    def __init__(self, parent_window, parent=None):
        super().__init__(parent)
        self._win = parent_window; self._drag_pos = None
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setCursor(Qt.CursorShape.ArrowCursor); self.setMinimumWidth(1)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = (e.globalPosition().toPoint()
                              - self._win.frameGeometry().topLeft()); e.accept()

    def mouseMoveEvent(self, e):
        if self._drag_pos is not None and (e.buttons() & Qt.MouseButton.LeftButton):
            if self._win.isMaximized():
                self._win.showNormal()
                geo = self._win.frameGeometry()
                self._drag_pos = QPoint(geo.width() // 2, self._drag_pos.y())
            self._win.move(e.globalPosition().toPoint() - self._drag_pos); e.accept()

    def mouseReleaseEvent(self, e): self._drag_pos = None

    def mouseDoubleClickEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton: self._win.toggle_maximize()


class TitleBarButton(QPushButton):
    def __init__(self, kind, is_close=False, parent=None):
        super().__init__(parent)
        self.setObjectName("winCloseBtn" if is_close else "winBtn")
        self.setFixedSize(46, 30)
        self._kind = kind; self._is_close = is_close
        self.setCursor(Qt.CursorShape.ArrowCursor); self.setFlat(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def set_kind(self, k): self._kind = k; self.update()

    def set_icon_color(self, color):
        self.setIcon(_make_window_button_icon(self._kind, color))
        self.setIconSize(QSize(14, 14)); self.update()


class BrowserView(QWebEngineView):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main = main_window
        self._ctx_pos = QPoint(0, 0)

    def contextMenuEvent(self, e):
        self._ctx_pos = e.globalPos()
        vp = e.pos()
        js = (
            "(function(){"
            f"var el = document.elementFromPoint({vp.x()}, {vp.y()});"
            "if (!el) return {type:'page', sel:''};"
            "var t = el.tagName.toLowerCase();"
            "var a = el.closest('a');"
            "if (a) return {type:'link', href:a.href||'', text:(a.textContent||'').trim().substring(0,80)};"
            "if (t === 'img') return {type:'image', src:el.src||'', alt:el.alt||'', pageHref:(el.closest('a')||{}).href||''};"
            "if (t === 'picture'){var im=el.querySelector('img'); if(im) return {type:'image',src:im.src||'',alt:im.alt||'',pageHref:(im.closest('a')||{}).href||''};}"
            "if (t === 'video' || t === 'audio') return {type:'media', kind:t, src:el.currentSrc||el.src||'', paused:!!el.paused, muted:!!el.muted, loop:!!el.loop, rate:el.playbackRate||1, controls:!!el.controls};"
            "var v = el.querySelector && el.querySelector('video');"
            "if (v) return {type:'media', kind:'video', src:v.currentSrc||v.src||'', paused:!!v.paused, muted:!!v.muted, loop:!!v.loop, rate:v.playbackRate||1, controls:!!v.controls};"
            "return {type:'page', sel:(window.getSelection()||{}).toString()||''};"
            "})();"
        )
        self.page().runJavaScript(js, self._on_ctx_info)
        e.accept()

    def _on_ctx_info(self, info):
        if not isinstance(info, dict):
            info = {"type": "page", "sel": ""}
        t = info.get("type", "page")
        menu = QMenu(self)
        menu.setStyleSheet(_build_ctx_menu_qss(self.main.current_theme,
                                               self.main.custom_colors))
        if t == "link":
            self._build_link_menu(menu, info)
        elif t == "image":
            self._build_image_menu(menu, info)
        elif t == "media":
            self._build_media_menu(menu, info)
        else:
            self._build_page_menu(menu, info)
        menu.exec(self._ctx_pos)

    def _bookmark(self, url, title):
        if not url:
            return
        self.main.bookmarks.add(url, title or url)
        self.main.bookmark_changed()

    def _unbookmark(self, url):
        if not url:
            return
        self.main.bookmarks.remove(url)
        self.main.bookmark_changed()

    def _build_page_menu(self, menu, info):
        m = self.main
        b = menu.addAction(m.tr("ctx_back")); b.setEnabled(self.history().canGoBack())
        b.triggered.connect(self.back)
        f = menu.addAction(m.tr("ctx_forward")); f.setEnabled(self.history().canGoForward())
        f.triggered.connect(self.forward)
        r = menu.addAction(m.tr("ctx_reload")); r.triggered.connect(self.reload)

        url = self.url().toString()
        if url and url not in ("about:blank", "") and not url.startswith("chrome://"):
            menu.addSeparator()
            if m.bookmarks.has(url):
                bm = menu.addAction(m.tr("ctx_remove_bookmark"))
                bm.triggered.connect(lambda c=False, u=url: self._unbookmark(u))
            else:
                bm = menu.addAction(m.tr("ctx_add_bookmark"))
                bm.triggered.connect(
                    lambda c=False, u=url: self._bookmark(u, self.title()))

        menu.addSeparator()
        sa = menu.addAction(m.tr("ctx_select_all"))
        sa.triggered.connect(lambda: self.page().triggerAction(
            QWebEnginePage.WebAction.SelectAll))
        sp = menu.addAction(m.tr("ctx_save_page_as")); sp.triggered.connect(self._save_page_as)
        ss = menu.addAction(m.tr("ctx_screenshot")); ss.triggered.connect(self._screenshot)
        menu.addSeparator()
        vs = menu.addAction(m.tr("ctx_view_source")); vs.triggered.connect(self._view_source)
        ins = menu.addAction(m.tr("ctx_inspect")); ins.triggered.connect(self._inspect)

    def _build_link_menu(self, menu, info):
        m = self.main
        href = info.get("href", "")
        text = info.get("text", "")
        if href:
            a = menu.addAction(m.tr("ctx_open_link_new_tab"))
            a.triggered.connect(lambda c=False, h=href: m.add_tab(h))
            b = menu.addAction(m.tr("ctx_open_link_split"))
            b.triggered.connect(lambda c=False, h=href: m.open_in_split(h))
            c = menu.addAction(m.tr("ctx_open_link_new_window"))
            c.triggered.connect(lambda c=False, h=href: m.open_url_in_new_window(h))
            d = menu.addAction(m.tr("ctx_preview_link"))
            d.triggered.connect(lambda c=False, h=href: self._preview(h))
            menu.addSeparator()
            e = menu.addAction(m.tr("ctx_save_object"))
            e.triggered.connect(lambda c=False, h=href: self._save_url(h))
            menu.addSeparator()
            f = menu.addAction(m.tr("ctx_copy_link"))
            f.triggered.connect(lambda c=False, h=href: QApplication.clipboard().setText(h))
            g = menu.addAction(m.tr("ctx_copy_link_clean"))
            g.triggered.connect(lambda c=False, h=href: QApplication.clipboard().setText(
                h.split("?")[0].split("#")[0]))
            menu.addSeparator()
            if m.bookmarks.has(href):
                bm = menu.addAction(m.tr("ctx_remove_bookmark"))
                bm.triggered.connect(lambda c=False, h=href: self._unbookmark(h))
            else:
                bm = menu.addAction(m.tr("ctx_bookmark_link"))
                bm.triggered.connect(
                    lambda c=False, h=href, t=text: self._bookmark(h, t))
            menu.addSeparator()
        if text:
            s = menu.addAction(m.tr("ctx_search_for", q=text[:40]))
            s.triggered.connect(lambda c=False, t=text: m.add_tab(
                m.search_engine_template.format(quote_plus(t))))
            menu.addSeparator()
        ins = menu.addAction(m.tr("ctx_inspect")); ins.triggered.connect(self._inspect)

    def _build_image_menu(self, menu, info):
        m = self.main
        src = info.get("src", "")
        page_href = info.get("pageHref", "")
        target = page_href if page_href else src
        if target:
            a = menu.addAction(m.tr("ctx_open_link_new_tab"))
            a.triggered.connect(lambda c=False, u=target: m.add_tab(u))
            b = menu.addAction(m.tr("ctx_open_link_split"))
            b.triggered.connect(lambda c=False, u=target: m.open_in_split(u))
            c = menu.addAction(m.tr("ctx_open_link_new_window"))
            c.triggered.connect(lambda c=False, u=target: m.open_url_in_new_window(u))
            d = menu.addAction(m.tr("ctx_preview_link"))
            d.triggered.connect(lambda c=False, u=target: self._preview(u))
        menu.addSeparator()
        if src:
            e = menu.addAction(m.tr("ctx_save_object"))
            e.triggered.connect(lambda c=False, s=src: self._save_url(s))
            menu.addSeparator()
            f = menu.addAction(m.tr("ctx_copy_link"))
            f.triggered.connect(lambda c=False, s=src: QApplication.clipboard().setText(s))
            g = menu.addAction(m.tr("ctx_copy_link_clean"))
            g.triggered.connect(lambda c=False, s=src: QApplication.clipboard().setText(
                s.split("?")[0].split("#")[0]))
            menu.addSeparator()
            if m.bookmarks.has(src):
                bm = menu.addAction(m.tr("ctx_remove_bookmark"))
                bm.triggered.connect(lambda c=False, s=src: self._unbookmark(s))
            else:
                bm = menu.addAction(m.tr("ctx_bookmark_link"))
                bm.triggered.connect(
                    lambda c=False, s=src, t=info.get("alt", ""):
                    self._bookmark(s, t))
            menu.addSeparator()
            h = menu.addAction(m.tr("ctx_copy_image"))
            h.triggered.connect(self._copy_image)
            i = menu.addAction(m.tr("ctx_copy_image_link"))
            i.triggered.connect(lambda c=False, s=src: QApplication.clipboard().setText(s))
            j = menu.addAction(m.tr("ctx_search_image"))
            j.triggered.connect(lambda c=False, s=src: m.add_tab(
                "https://lens.google.com/uploadbyurl?url=" + quote(s, safe="")))
            k = menu.addAction(m.tr("ctx_set_wallpaper"))
            k.triggered.connect(lambda c=False, s=src: m.set_wallpaper_from_url(s))
            menu.addSeparator()
        ins = menu.addAction(m.tr("ctx_inspect")); ins.triggered.connect(self._inspect)

    def _build_media_menu(self, menu, info):
        m = self.main
        src = info.get("src", "")
        paused = info.get("paused", True)
        muted = info.get("muted", False)
        loop = info.get("loop", False)
        rate = float(info.get("rate", 1.0) or 1.0)
        controls = info.get("controls", True)
        a = menu.addAction(m.tr("ctx_play") if paused else m.tr("ctx_pause"))
        a.triggered.connect(lambda c=False, p=paused: self._js_media(
            "play" if p else "pause"))
        b = menu.addAction(m.tr("ctx_unmute") if muted else m.tr("ctx_mute"))
        b.triggered.connect(lambda c=False, mu=muted: self._js_media(
            "unmute" if mu else "mute"))
        sp = menu.addMenu(m.tr("ctx_speed"))
        sp.setStyleSheet(_build_ctx_menu_qss(m.current_theme, m.custom_colors))
        for label, val in [("0.25x", 0.25), ("0.5x", 0.5), ("0.75x", 0.75),
                           ("1x", 1.0), ("1.25x", 1.25), ("1.5x", 1.5),
                           ("1.75x", 1.75), ("2x", 2.0)]:
            act = sp.addAction(label)
            act.setCheckable(True)
            if abs(rate - val) < 0.01:
                act.setChecked(True)
            act.triggered.connect(lambda c=False, v=val: self._js_media(f"rate:{v}"))
        lp = menu.addAction(m.tr("ctx_loop"))
        lp.setCheckable(True); lp.setChecked(loop)
        lp.triggered.connect(lambda c=False: self._js_media("loop"))
        menu.addSeparator()
        fs = menu.addAction(m.tr("ctx_fullscreen"))
        fs.triggered.connect(lambda c=False: self._js_media("fullscreen"))
        sc = menu.addAction(m.tr("ctx_show_controls"))
        sc.setCheckable(True); sc.setChecked(controls)
        sc.triggered.connect(lambda c=False: self._js_media("controls"))
        menu.addSeparator()
        if src:
            ot = menu.addAction(m.tr("ctx_open_video_new_tab"))
            ot.triggered.connect(lambda c=False, s=src: m.add_tab(s))
            pip = menu.addAction(m.tr("ctx_pip"))
            pip.triggered.connect(lambda c=False: self._js_media("pip"))
            menu.addSeparator()
            sv = menu.addAction(m.tr("ctx_save_video"))
            sv.triggered.connect(lambda c=False, s=src: self._save_url(s))
            cl = menu.addAction(m.tr("ctx_copy_video_link"))
            cl.triggered.connect(lambda c=False, s=src: QApplication.clipboard().setText(s))
            menu.addSeparator()
        ss = menu.addAction(m.tr("ctx_screenshot")); ss.triggered.connect(self._screenshot)
        menu.addSeparator()
        ins = menu.addAction(m.tr("ctx_inspect")); ins.triggered.connect(self._inspect)

    def _js_media(self, action):
        if action == "play":
            js = "document.querySelectorAll('video,audio').forEach(v=>v.play&&v.play())"
        elif action == "pause":
            js = "document.querySelectorAll('video,audio').forEach(v=>v.pause&&v.pause())"
        elif action == "mute":
            js = "document.querySelectorAll('video,audio').forEach(v=>v.muted=true)"
        elif action == "unmute":
            js = "document.querySelectorAll('video,audio').forEach(v=>v.muted=false)"
        elif action == "loop":
            js = "document.querySelectorAll('video,audio').forEach(v=>v.loop=!v.loop)"
        elif action == "controls":
            js = "document.querySelectorAll('video,audio').forEach(v=>v.controls=!v.controls)"
        elif action == "fullscreen":
            js = ("(function(){var v=document.querySelector('video');"
                  "if(v && v.requestFullscreen) v.requestFullscreen();})()")
        elif action == "pip":
            js = ("(function(){var v=document.querySelector('video');"
                  "if(v && v.requestPictureInPicture) v.requestPictureInPicture();})()")
        elif action.startswith("rate:"):
            val = action.split(":", 1)[1]
            js = f"document.querySelectorAll('video,audio').forEach(v=>v.playbackRate={val})"
        else:
            return
        self.page().runJavaScript(js)

    def _save_page_as(self):
        try:
            self.page().triggerAction(QWebEnginePage.WebAction.SavePage)
        except Exception: pass

    def _save_url(self, url):
        try:
            self.page().download(QUrl(url))
        except Exception:
            try: QApplication.clipboard().setText(url)
            except Exception: pass

    def _screenshot(self):
        try:
            pix = self.grab()
            home = os.path.expanduser("~")
            path, _ = QFileDialog.getSaveFileName(
                self, self.main.tr("ctx_screenshot"),
                os.path.join(home, "screenshot.png"),
                "PNG Image (*.png);;JPEG Image (*.jpg)")
            if path:
                pix.save(path)
        except Exception: pass

    def _view_source(self):
        url = self.url().toString()
        if not url or url.startswith("view-source:"):
            return
        self.main.add_tab(f"view-source:{url}")

    def _inspect(self):
        try:
            t = self.main.current_browser_tab()
            if t is None:
                return
            if t.devtools.height() <= 0:
                if t.devtools.page is None:
                    t.devtools.attach_to(self.page())
                t.devtools.show()
                QTimer.singleShot(0, t.devtools.show_animated)
                QTimer.singleShot(400, self._do_inspect)
            else:
                self._do_inspect()
        except Exception:
            pass

    def _do_inspect(self):
        try:
            self.page().triggerAction(QWebEnginePage.WebAction.InspectElement)
        except Exception:
            pass

    def _preview(self, url):
        try:
            QToolTip.showText(QCursor.pos(), url, self)
        except Exception: pass

    def _copy_image(self):
        try:
            local_pos = self.mapFromGlobal(self._ctx_pos)
            r = QRect(local_pos.x() - 100, local_pos.y() - 100, 200, 200)
            pix = self.grab(r)
            QApplication.clipboard().setPixmap(pix)
        except Exception: pass


class DevToolsPanel(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main = main_window
        self.setFixedHeight(0); self._target_h = 400
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(0)
        pal = main_window.get_effective_palette()
        header = QWidget(); header.setFixedHeight(26)
        header.setStyleSheet(f"background-color: {pal['panel']}; "
                             f"border-top: 1px solid {pal['border']};")
        hh = QHBoxLayout(header); hh.setContentsMargins(10, 0, 6, 0); hh.setSpacing(4)
        label = QLabel("DevTools")
        label.setStyleSheet(f"color: {pal['text2']}; font-weight: 700; font-size: 12px;")
        hh.addWidget(label); hh.addStretch()
        close_btn = QPushButton("✕"); close_btn.setObjectName("findBtn")
        close_btn.setFixedSize(22, 22)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.hide_animated); hh.addWidget(close_btn)
        layout.addWidget(header)
        self.view = QWebEngineView(self); self.page = None
        layout.addWidget(self.view, 1)
        self._anim = QPropertyAnimation(self, b"panelHeight", self)
        self._anim.setDuration(240); self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    @pyqtProperty(int)
    def panelHeight(self): return self.height()

    @panelHeight.setter
    def panelHeight(self, h): self.setFixedHeight(int(h))

    def attach_to(self, bp):
        p = QWebEngineProfile.defaultProfile()
        self.page = QWebEnginePage(p, self.view)
        self.view.setPage(self.page); bp.setDevToolsPage(self.page)

    def show_animated(self):
        self._anim.stop(); self._anim.setStartValue(self.height())
        self._anim.setEndValue(self._target_h); self._anim.start()

    def hide_animated(self):
        self._anim.stop(); self._anim.setStartValue(self.height())
        self._anim.setEndValue(0); self._anim.start()


class MenuRow(QPushButton):
    def __init__(self, icon_pix, label, shortcut, pal, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(34)
        self._icon_pix = icon_pix
        self._label = label
        self._shortcut = shortcut
        self._pal = pal
        self.setFlat(True)
        self.setStyleSheet(f"""
            QPushButton {{ background: transparent; border: none; padding: 0; }}
            QPushButton:hover {{ background: {pal['panel_hover']}; border-radius: 8px; }}
        """)
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

    def paintEvent(self, e):
        super().paintEvent(e)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        if self._icon_pix is not None:
            ix = 12
            iy = (h - self._icon_pix.height()) // 2
            p.drawPixmap(ix, iy, self._icon_pix)
        p.setPen(QColor(self._pal["text"]))
        f = QFont(self.font()); f.setPointSize(10); f.setBold(False)
        p.setFont(f)
        p.drawText(QRect(42, 0, w - 42 - 78, h),
                   Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                   self._label)
        if self._shortcut:
            p.setPen(QColor(self._pal["text2"]))
            f2 = QFont(self.font()); f2.setPointSize(9)
            p.setFont(f2)
            p.drawText(QRect(w - 82, 0, 70, h),
                       Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
                       self._shortcut)
        p.end()


class MainMenuPopup(QDialog):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main = main_window
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setFixedWidth(310)
        pal = main_window.get_effective_palette()
        self.setStyleSheet(f"""
            QDialog {{ background-color: {pal['panel']};
                border: 1px solid {pal['border']}; border-radius: 12px; }}
            QFrame#menuSep {{ background: {pal['border']}; max-height: 1px; border: none; }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 8, 6, 8)
        layout.setSpacing(1)
        icon_color = pal["text2"]

        def _sep():
            fr = QFrame(); fr.setObjectName("menuSep")
            fr.setFixedHeight(1); fr.setContentsMargins(0, 4, 0, 4)
            layout.addWidget(fr)

        def _row(kind, label_key, shortcut, cb):
            label = self.main.tr(label_key)
            icon_pix = _make_sidebar_pixmap(kind, icon_color, 18)
            row = MenuRow(icon_pix, label, shortcut, pal)
            row.clicked.connect(lambda c=False, f=cb: self._run(f))
            layout.addWidget(row)

        _row("window", "menu_new_window", "Ctrl+N", self._new_window)
        _row("plus_tab", "menu_new_tab", "Ctrl+T", self._new_tab)
        _row("download", "menu_downloads", "Ctrl+J", self._downloads)
        _sep()
        _row("sliders", "menu_settings", "Ctrl+,", self._settings)
        _row("sparkle", "menu_customization", "Ctrl+Shift+A", self._customization)
        _row("zoom_in", "menu_zoom", "", self._zoom)
        _row("history", "menu_history", "", self._history)
        _row("bookmark", "menu_bookmarks", "Ctrl+Shift+O", self._bookmarks)
        _row("info", "menu_about", "", self._about)
        _sep()
        _row("search", "menu_find", "Ctrl+F", self._find)
        _row("save", "menu_save_as", "Ctrl+S", self._save)
        _row("globe", "menu_translate", "", self._translate)
        _row("lock", "menu_passwords", "Ctrl+P", self._passwords)
        _sep()
        _row("exit", "menu_exit", "Ctrl+Q", self._exit)

    def _run(self, fn):
        self.accept()
        QTimer.singleShot(10, fn)

    def _new_window(self): self.main.open_new_window()
    def _new_tab(self): self.main.add_tab()

    def _downloads(self):
        t = self.main.current_browser_tab()
        if t: t._open_downloads_popup()
        else: self.main.open_downloads_folder()

    def _settings(self): self.main.open_settings(SETTINGS_THEME)
    def _customization(self): self.main.open_settings(SETTINGS_THEME)
    def _zoom(self): self.main.open_settings(SETTINGS_ZOOM)
    def _history(self): self.main.open_settings(SETTINGS_HISTORY)
    def _bookmarks(self): self.main.open_settings(SETTINGS_BOOKMARKS)
    def _about(self): self.main.open_settings(SETTINGS_ABOUT)
    def _find(self): self.main.find_on_page()

    def _save(self):
        t = self.main.current_browser_tab()
        if t:
            try:
                t.browser.page().triggerAction(QWebEnginePage.WebAction.SavePage)
            except Exception: pass

    def _translate(self):
        t = self.main.current_browser_tab()
        if t:
            try: t._open_translate_popup()
            except Exception: pass

    def _passwords(self): self.main.open_settings(SETTINGS_PASSWORDS)
    def _exit(self): self.main.close()

    def showEvent(self, e):
        super().showEvent(e)
        self.setWindowOpacity(0.0)
        self._anim = QPropertyAnimation(self, b"windowOpacity", self)
        self._anim.setDuration(120)
        self._anim.setStartValue(0.0); self._anim.setEndValue(1.0)
        self._anim.start()


class BrowserTab(QWidget):
    def __init__(self, main_window, start_url, empty_mode=False, parent=None):
        super().__init__(parent)
        self.main = main_window
        if start_url is not None and not isinstance(start_url, str):
            start_url = None
        self._start_url = start_url
        self._showing_loading = start_url is not None
        self._startup_phase = start_url is not None
        self._retry_count = 0; self._max_retries = 3
        self._dark_applied = False
        self._empty_mode = bool(empty_mode)
        self.nav_widget = None; self.stack = None
        self._create_widgets(); self._setup_layout()
        self.bridge = PasswordBridge()
        self.bridge.saveRequested.connect(self._on_save_requested)
        self.channel = QWebChannel()
        self.channel.registerObject("bridge", self.bridge)
        self.browser.page().setWebChannel(self.channel)
        self.back_btn.clicked.connect(self.browser.back)
        self.forward_btn.clicked.connect(self.browser.forward)
        self.reload_btn.clicked.connect(self.browser.reload)
        self.search_btn.clicked.connect(lambda: self.main.open_settings(SETTINGS_SEARCH))
        self.translate_btn.clicked.connect(self._open_translate_popup)
        self.input_url.returnPressed.connect(self._on_url_return)
        self.settings_btn.clicked.connect(self._open_main_menu)
        self.downloads_btn.clicked.connect(self._open_downloads_popup)
        self.bookmark_btn.clicked.connect(self._toggle_bookmark)
        self.browser.urlChanged.connect(self._on_url_changed)
        self.browser.titleChanged.connect(self._on_title_changed)
        self.browser.iconChanged.connect(self._on_icon_changed)
        self.browser.loadFinished.connect(self._on_load_finished)
        self.browser.page().findTextFinished.connect(self._on_find_finished)
        if self._start_url:
            self.browser.setHtml(LOADING_HTML, QUrl("about:blank"))
            self.stack.setCurrentWidget(self.browser)
        else:
            self.stack.setCurrentWidget(self.new_tab_page)

    def _create_widgets(self):
        icon_size = QSize(18, 18)
        self.back_btn = QPushButton(); self.back_btn.setObjectName("navBtn")
        self.back_btn.setFixedSize(34, 28); self.back_btn.setIconSize(icon_size)
        self.back_btn.setIcon(QIcon(self.main._icon_back))
        self.back_btn.setToolTip(self.main.tr("tip_back"))
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.forward_btn = QPushButton(); self.forward_btn.setObjectName("navBtn")
        self.forward_btn.setFixedSize(34, 28); self.forward_btn.setIconSize(icon_size)
        self.forward_btn.setIcon(QIcon(self.main._icon_forward))
        self.forward_btn.setToolTip(self.main.tr("tip_forward"))
        self.forward_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reload_btn = QPushButton(); self.reload_btn.setObjectName("navBtn")
        self.reload_btn.setFixedSize(34, 28); self.reload_btn.setIconSize(icon_size)
        self.reload_btn.setIcon(QIcon(self.main._icon_reload))
        self.reload_btn.setToolTip(self.main.tr("tip_reload"))
        self.reload_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.search_btn = QPushButton(); self.search_btn.setObjectName("navBtn")
        self.search_btn.setFixedSize(34, 28); self.search_btn.setIconSize(icon_size)
        self.search_btn.setIcon(QIcon(self.main._search_icon_path))
        self.search_btn.setToolTip(self.main.tr("tip_search"))
        self.search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.input_url = QLineEdit()
        self.input_url.setPlaceholderText(self.main.tr("url_placeholder"))
        self.input_url.setMinimumHeight(32)
        self.translate_btn = QPushButton(); self.translate_btn.setObjectName("navBtn")
        self.translate_btn.setFixedSize(34, 28); self.translate_btn.setIconSize(icon_size)
        self.translate_btn.setIcon(QIcon(self.main._icon_translate))
        self.translate_btn.setToolTip(self.main.tr("tip_translate"))
        self.translate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.bookmark_btn = QPushButton(); self.bookmark_btn.setObjectName("navBtn")
        self.bookmark_btn.setFixedSize(34, 28); self.bookmark_btn.setIconSize(icon_size)
        self.bookmark_btn.setIcon(QIcon(self.main._icon_bookmark_outline))
        self.bookmark_btn.setToolTip(self.main.tr("tip_bookmark"))
        self.bookmark_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.downloads_btn = DownloadsButton()
        self.downloads_btn.setIconSize(icon_size)
        self.downloads_btn.setIcon(QIcon(self.main._icon_downloads))
        self.downloads_btn.setToolTip(self.main.tr("tip_downloads"))
        self.settings_btn = QPushButton(); self.settings_btn.setObjectName("navBtn")
        self.settings_btn.setFixedSize(34, 28); self.settings_btn.setIconSize(icon_size)
        self.settings_btn.setIcon(QIcon(self.main._icon_menu))
        self.settings_btn.setToolTip(self.main.tr("tip_settings"))
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.browser = BrowserView(self.main)
        s = self.browser.settings()
        s.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled,
                      bool(self.main.smooth_scroll))
        s.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.DnsPrefetchEnabled, True)
        self.new_tab_page = NewTabPage(self.main,
                                       show_wallpaper_button=not self._empty_mode)
        self.bookmarks_bar = BookmarksBar(self.main)
        self.bookmarks_bar.setVisible(bool(self.main.show_bookmarks_bar))
        self.find_bar = QWidget(); self.find_bar.setObjectName("findBar")
        self.find_bar.setFixedHeight(36)
        fb = QHBoxLayout(self.find_bar)
        fb.setContentsMargins(14, 3, 6, 3); fb.setSpacing(2)
        self.find_input = QLineEdit(); self.find_input.setObjectName("findInput")
        self.find_input.setPlaceholderText(self.main.tr("find_placeholder"))
        self.find_input.setMinimumWidth(220)
        self.find_input.returnPressed.connect(self._find_next)
        self.find_input.textChanged.connect(self._find_text_changed)
        fb.addWidget(self.find_input, 1)
        self.find_count_lbl = QLabel(""); self.find_count_lbl.setObjectName("findCountLabel")
        fb.addWidget(self.find_count_lbl)
        self.find_prev_btn = QPushButton("↑"); self.find_prev_btn.setObjectName("findBtn")
        self.find_prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.find_prev_btn.clicked.connect(self._find_prev); fb.addWidget(self.find_prev_btn)
        self.find_next_btn = QPushButton("↓"); self.find_next_btn.setObjectName("findBtn")
        self.find_next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.find_next_btn.clicked.connect(self._find_next); fb.addWidget(self.find_next_btn)
        self.find_close_btn = QPushButton("✕"); self.find_close_btn.setObjectName("findBtn")
        self.find_close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.find_close_btn.clicked.connect(self._hide_find_bar)
        fb.addWidget(self.find_close_btn)
        self.find_bar_wrapper = QWidget(); self.find_bar_wrapper.setObjectName("findBarWrapper")
        fbw = QHBoxLayout(self.find_bar_wrapper); fbw.setContentsMargins(0, 6, 0, 6)
        fbw.addStretch(); fbw.addWidget(self.find_bar); fbw.addStretch()
        self.find_bar_wrapper.hide()
        self.devtools = DevToolsPanel(self.main, self); self.devtools.hide()

    def apply_smooth_scroll(self, enabled):
        try:
            self.browser.settings().setAttribute(
                QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled,
                bool(enabled))
        except Exception:
            pass
        try:
            js = SMOOTH_SCROLL_ON_JS if enabled else SMOOTH_SCROLL_OFF_JS
            self.browser.page().runJavaScript(js)
        except Exception:
            pass

    def _inject_smooth_scroll(self):
        try:
            js = (SMOOTH_SCROLL_ON_JS if self.main.smooth_scroll
                  else SMOOTH_SCROLL_OFF_JS)
            self.browser.page().runJavaScript(js)
        except Exception:
            pass

    def _inject_autoscroll(self):
        try:
            accent = self.main.get_effective_palette().get("accent", "#5a5a5a")
            js = AUTOSCROLL_JS.replace("__ACCENT__", accent)
            self.browser.page().runJavaScript(js)
        except Exception:
            pass

    def _on_icon_changed(self, icon):
        try:
            QTimer.singleShot(0, lambda ic=icon: self._apply_tab_icon(ic))
        except Exception:
            pass

    def _apply_tab_icon(self, icon):
        parent = self.parent()
        while parent is not None:
            if isinstance(parent, CustomTabWidget):
                idx = parent.indexOf(self)
                if idx != -1:
                    bar = parent.tabBar()
                    try:
                        if icon is not None and not icon.isNull():
                            bar.setTabData(idx, icon)
                        else:
                            bar.setTabData(idx, None)
                        bar.update()
                    except Exception:
                        pass
                return
            parent = parent.parent()

    def _toggle_bookmark(self):
        url = self.browser.url().toString()
        if not url or url in ("about:blank", "") or url.startswith("chrome://"):
            return
        title = self.browser.title() or url
        added = self.main.bookmarks.toggle(url, title)
        self._update_bookmark_icon()
        self.main.bookmark_changed()
        try:
            pos = self.bookmark_btn.mapToGlobal(
                self.bookmark_btn.rect().bottomLeft())
            QToolTip.showText(
                pos,
                self.main.tr("bm_added" if added else "bm_removed"),
                self.bookmark_btn)
        except Exception:
            pass

    def _update_bookmark_icon(self, url=None):
        if not hasattr(self, "bookmark_btn"):
            return
        if url is None:
            url = self.browser.url().toString()
        has = bool(url) and self.main.bookmarks.has(url)
        if has:
            self.bookmark_btn.setIcon(QIcon(self.main._icon_bookmark_filled))
            self.bookmark_btn.setToolTip(self.main.tr("tip_unbookmark"))
        else:
            self.bookmark_btn.setIcon(QIcon(self.main._icon_bookmark_outline))
            self.bookmark_btn.setToolTip(self.main.tr("tip_bookmark"))

    def _open_main_menu(self):
        popup = MainMenuPopup(self.main, self.window())
        popup.adjustSize()
        br = self.settings_btn.rect()
        bl = self.settings_btn.mapToGlobal(br.bottomLeft())
        pw, ph = popup.width(), popup.height()
        x = bl.x() + br.width() - pw
        y = bl.y() + 6
        screen = QApplication.primaryScreen().availableGeometry()
        if x < screen.left() + 10: x = screen.left() + 10
        if x + pw > screen.right() - 10: x = screen.right() - pw - 10
        if y + ph > screen.bottom() - 10: y = screen.bottom() - ph - 10
        if y < screen.top() + 10: y = screen.top() + 10
        popup.move(QPoint(int(x), int(y)))
        popup.exec()

    def _on_url_return(self): self.navigate(self.input_url.text())

    def _setup_layout(self):
        old = self.layout()
        if old is not None:
            while old.count(): old.takeAt(0)
            QWidget().setLayout(old)
        pos = self.main.layout_position
        preset = DENSITY_PRESETS.get(self.main.density, DENSITY_PRESETS["auto"])
        nm = preset["nav_margin"]; ns = preset["nav_spacing"]
        nbs = preset["nav_btn_size"]; nbh = preset["nav_btn_h"]
        for b in (self.back_btn, self.forward_btn, self.reload_btn,
                  self.search_btn, self.translate_btn, self.settings_btn,
                  self.bookmark_btn):
            b.setFixedSize(nbs, nbh)
        self.downloads_btn.setFixedSize(nbs, nbh)
        if self.nav_widget is None:
            self.nav_widget = QWidget()
            nl = QHBoxLayout(self.nav_widget)
            nl.setContentsMargins(nm, nm, nm, nm); nl.setSpacing(ns)
            nl.addWidget(self.back_btn); nl.addWidget(self.forward_btn)
            nl.addWidget(self.reload_btn); nl.addWidget(self.search_btn)
            nl.addWidget(self.input_url, 1)
            nl.addWidget(self.bookmark_btn)
            nl.addWidget(self.translate_btn)
            nl.addWidget(self.downloads_btn); nl.addWidget(self.settings_btn)
        else:
            nl = self.nav_widget.layout()
            if nl is not None:
                nl.setContentsMargins(nm, nm, nm, nm); nl.setSpacing(ns)
        self.nav_widget.setObjectName("navBarTop" if pos == "top" else "navBarBottom")
        self.nav_widget.setLayoutDirection(self.main.layoutDirection())
        try:
            self.nav_widget.style().unpolish(self.nav_widget)
            self.nav_widget.style().polish(self.nav_widget)
        except Exception: pass
        if self.stack is None:
            self.stack = QStackedWidget(); self.stack.setObjectName("tabContentStack")
            self.stack.addWidget(self.new_tab_page); self.stack.addWidget(self.browser)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0); outer.setSpacing(0)
        if pos == "bottom":
            outer.addWidget(self.find_bar_wrapper)
            outer.addWidget(self.stack, 1)
            outer.addWidget(self.bookmarks_bar)
            outer.addWidget(self.nav_widget)
            outer.addWidget(self.devtools)
        else:
            outer.addWidget(self.nav_widget)
            outer.addWidget(self.bookmarks_bar)
            outer.addWidget(self.stack, 1)
            outer.addWidget(self.find_bar_wrapper)
            outer.addWidget(self.devtools)

    def relayout(self): self._setup_layout()

    def update_theme_icons(self):
        self.back_btn.setIcon(QIcon(self.main._icon_back))
        self.forward_btn.setIcon(QIcon(self.main._icon_forward))
        self.reload_btn.setIcon(QIcon(self.main._icon_reload))
        self.search_btn.setIcon(QIcon(self.main._search_icon_path))
        self.translate_btn.setIcon(QIcon(self.main._icon_translate))
        self.downloads_btn.setIcon(QIcon(self.main._icon_downloads))
        self.settings_btn.setIcon(QIcon(self.main._icon_menu))
        self._update_bookmark_icon()

    def set_download_state(self, p, d):
        self.downloads_btn.set_progress(p); self.downloads_btn.set_downloading(d)

    def flash_download_done(self): self.downloads_btn.flash_done()

    def retranslate(self):
        self.back_btn.setToolTip(self.main.tr("tip_back"))
        self.forward_btn.setToolTip(self.main.tr("tip_forward"))
        self.reload_btn.setToolTip(self.main.tr("tip_reload"))
        self.search_btn.setToolTip(self.main.tr("tip_search"))
        self.translate_btn.setToolTip(self.main.tr("tip_translate"))
        self.downloads_btn.setToolTip(self.main.tr("tip_downloads"))
        self.settings_btn.setToolTip(self.main.tr("tip_settings"))
        self.input_url.setPlaceholderText(self.main.tr("url_placeholder"))
        self.find_input.setPlaceholderText(self.main.tr("find_placeholder"))
        self._update_bookmark_icon()

    def refresh_new_tab_page(self):
        if hasattr(self, "new_tab_page"):
            self.new_tab_page.apply_wall_btn_visibility()
            self.new_tab_page._update_live_state()
            self.new_tab_page.update()

    def open_find_bar(self):
        self.find_bar_wrapper.show(); self.find_input.setFocus()
        self.find_input.selectAll()

    def _hide_find_bar(self):
        self.find_bar_wrapper.hide(); self.browser.setFocus()

    def _find_text_changed(self, text):
        if not text: self.find_count_lbl.setText(""); return
        self.browser.page().findText(text)

    def _find_next(self):
        t = self.find_input.text()
        if t: self.browser.page().findText(t)

    def _find_prev(self):
        t = self.find_input.text()
        if t: self.browser.page().findText(t, QWebEnginePage.FindFlag.FindBackward)

    def _on_find_finished(self, r):
        try:
            total = r.numberOfMatches(); active = r.activeMatch()
            self.find_count_lbl.setText("0/0" if total == 0 else f"{active}/{total}")
        except Exception:
            self.find_count_lbl.setText("")

    def toggle_devtools(self):
        if self.devtools.height() > 0:
            self.devtools.hide_animated()
        else:
            if self.devtools.page is None:
                self.devtools.attach_to(self.browser.page())
            self.devtools.show()
            QTimer.singleShot(0, self.devtools.show_animated)

    def _inject_dark_css(self):
        js = (f"(function(){{var s=document.getElementById('__flexion_dark__');"
              f"if(!s){{s=document.createElement('style');s.id='__flexion_dark__';"
              f"(document.head||document.documentElement).appendChild(s);}}"
              f"s.textContent = `{DARK_CSS}`;}})();")
        self.browser.page().runJavaScript(js); self._dark_applied = True

    def _remove_dark_css(self):
        self.browser.page().runJavaScript(
            "(function(){var s=document.getElementById('__flexion_dark__');"
            "if(s) s.remove();})();")
        self._dark_applied = False

    def _apply_dark_theme(self):
        if not self.main.dark_mode: return
        self.browser.page().runJavaScript(CHECK_DARK_JS, self._on_dark_check_result)

    def _on_dark_check_result(self, is_dark):
        if is_dark: self._remove_dark_css()
        else: self._inject_dark_css()

    def update_dark_mode(self):
        if self.main.dark_mode: self._apply_dark_theme()
        else: self._remove_dark_css()

    def _open_translate_popup(self):
        url = self.browser.url().toString()
        if not url or url.startswith("about:") or url.startswith("chrome://"): return
        popup = TranslatePopup(self.main, self.main.translate_target, self.window())
        popup.adjustSize()
        br = self.translate_btn.rect()
        bl = self.translate_btn.mapToGlobal(br.bottomLeft())
        tr = self.translate_btn.mapToGlobal(br.topRight())
        x = bl.x() + br.width() - popup.width() + 30
        y = bl.y() + 6
        screen = QApplication.primaryScreen().availableGeometry()
        if x + popup.width() > screen.right(): x = screen.right() - popup.width() - 10
        if x < screen.left() + 10: x = screen.left() + 10
        if y + popup.height() > screen.bottom(): y = tr.y() - popup.height() - 6
        popup.move(QPoint(x, y))
        if popup.exec() == QDialog.DialogCode.Accepted:
            src, dst = popup.get_values()
            self.main.translate_target = dst
            self.main.qsettings.setValue("translate_target", dst)
            self.main.translate_page(url, src, dst)

    def _open_downloads_popup(self):
        popup = DownloadsPopup(self.main, self.window()); popup.adjustSize()
        br = self.downloads_btn.rect()
        bl = self.downloads_btn.mapToGlobal(br.bottomLeft())
        tr = self.downloads_btn.mapToGlobal(br.topRight())
        x = bl.x() + br.width() - popup.width() + 20
        y = bl.y() + 6
        screen = QApplication.primaryScreen().availableGeometry()
        if x + popup.width() > screen.right(): x = screen.right() - popup.width() - 10
        if x < screen.left() + 10: x = screen.left() + 10
        if y + popup.height() > screen.bottom(): y = tr.y() - popup.height() - 6
        popup.move(QPoint(x, y))
        self.main._downloads_popup = popup
        try: popup.exec()
        finally: self.main._downloads_popup = None

    def load_start_page(self):
        if self._start_url:
            self._showing_loading = False
            self.stack.setCurrentWidget(self.browser)
            self.browser.setUrl(QUrl(self._start_url))
        else:
            self._showing_loading = False
            self.stack.setCurrentWidget(self.new_tab_page)

    def _on_load_finished(self, ok):
        if self._showing_loading: return
        if ok:
            self._startup_phase = False; self._retry_count = 0
            self.browser.page().runJavaScript(PASSWORD_HOOK_JS)
            self._inject_autoscroll()
            QTimer.singleShot(50, self._inject_smooth_scroll)
            if self.main.dark_mode:
                QTimer.singleShot(200, self._apply_dark_theme)
            QTimer.singleShot(500, self._try_autofill)
            url = self.browser.url().toString()
            title = self.browser.title() or url
            if url and url not in ("about:blank", "") and not url.startswith("chrome://"):
                self.main.history.add(url, title)
            self._update_bookmark_icon()
            try:
                icon = self.browser.icon()
                if icon is not None and not icon.isNull():
                    self._apply_tab_icon(icon)
            except Exception:
                pass
            return
        if self._startup_phase and self._retry_count < self._max_retries:
            self._retry_count += 1
            QTimer.singleShot(400, self.browser.reload)

    def _try_autofill(self):
        url = self.browser.url().toString()
        creds = self.main.passwords.find(url)
        if not creds: return
        js = (f"(function(){{"
              f"var u=document.querySelector('input[type=text],input[type=email],"
              f"input[name*=user i],input[name*=login i]');"
              f"var p=document.querySelector('input[type=password]');"
              f"if(u&&p&&!u.value&&!p.value){{"
              f"u.value={json.dumps(creds['username'])};"
              f"p.value={json.dumps(creds['password'])};"
              f"u.dispatchEvent(new Event('input',{{bubbles:true}}));"
              f"p.dispatchEvent(new Event('input',{{bubbles:true}}));"
              f"}}}})();")
        self.browser.page().runJavaScript(js)

    def _on_save_requested(self, url, u, p):
        existing = self.main.passwords.find(url)
        if existing and existing["username"] == u and existing["password"] == p:
            return
        host = urlparse(url).netloc
        msg = self.main.tr("save_pwd_msg", host=host, user=u)
        r = QMessageBox.question(self, self.main.tr("save_pwd_title"), msg,
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if r == QMessageBox.StandardButton.Yes:
            self.main.passwords.upsert(url, u, p)
            self.main.refresh_password_settings()

    def navigate(self, text):
        text = text.strip()
        if not text: return
        self._retry_count = 0; self._startup_phase = False
        looks_url = (text.startswith("http://") or text.startswith("https://")
                     or ("." in text and " " not in text))
        if looks_url:
            if not text.startswith("http"): text = "https://" + text
            elif text.startswith("http://"): text = text.replace("http://", "https://", 1)
            url = text
        else:
            url = self.main.search_engine_template.format(quote_plus(text))
        if self.input_url.text() != url: self.input_url.setText(url)
        if self.stack.currentWidget() is not self.browser:
            self.stack.setCurrentWidget(self.browser)
        self.browser.setUrl(QUrl(url))

    def _on_url_changed(self, qurl):
        t = qurl.toString()
        if self.input_url.text() != t: self.input_url.setText(t)
        if (t not in ("about:blank", "")
                and self.stack.currentWidget() is self.new_tab_page):
            self.stack.setCurrentWidget(self.browser)
        self._update_bookmark_icon(t)

    def _on_title_changed(self, title):
        parent = self.parent()
        while parent is not None:
            if isinstance(parent, CustomTabWidget):
                idx = parent.indexOf(self)
                if idx != -1:
                    short = (title[:20] + "…") if len(title) > 21 else title
                    parent.setTabText(idx, short or self.main.tr("new_tab_title"))
                return
            parent = parent.parent()

    def zoom_in(self):
        v = round(min(self.browser.zoomFactor() + 0.1, 3.0), 2)
        self.browser.setZoomFactor(v)

    def zoom_out(self):
        v = round(max(self.browser.zoomFactor() - 0.1, 0.25), 2)
        self.browser.setZoomFactor(v)

    def zoom_reset(self): self.browser.setZoomFactor(1.0)


class SettingsTab(QWidget):
    is_settings_tab = True

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main = main_window
        self._scroll_areas = []
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self._build()

    def _build(self):
        try:
            old = self.layout()
            if old is not None:
                while old.count():
                    item = old.takeAt(0); w = item.widget()
                    if w: w.setParent(None); w.deleteLater()
                QWidget().setLayout(old)
            self._scroll_areas = []
            layout = QHBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(0)

            sidebar_wrapper = QWidget()
            sidebar_wrapper.setObjectName("sidebarWidget")
            sidebar_wrapper.setFixedWidth(270)
            wrapper_layout = QVBoxLayout(sidebar_wrapper)
            wrapper_layout.setContentsMargins(0, 0, 0, 0)
            wrapper_layout.setSpacing(0)

            sidebar = QWidget()
            sidebar.setStyleSheet("background: transparent;")
            sl = QVBoxLayout(sidebar)
            sl.setContentsMargins(12, 18, 12, 18); sl.setSpacing(3)

            self.settings_search = QLineEdit()
            self.settings_search.setObjectName("settingsSearch")
            self.settings_search.setPlaceholderText(self.main.tr("settings_search_placeholder"))
            self.settings_search.setClearButtonEnabled(True)
            self.settings_search.textChanged.connect(self._on_search_text)
            sl.addWidget(self.settings_search); sl.addSpacing(12)

            palette = self.main.get_effective_palette()
            self.nav_buttons = []
            items = [
                ("sparkle", self.main.tr("sb_theme")),
                ("palette", self.main.tr("custom_colors_title")),
                ("search", self.main.tr("sb_search")),
                ("eye", self.main.tr("sb_zoom")),
                ("download", self.main.tr("sb_downloads")),
                ("lock", self.main.tr("sb_passwords")),
                ("history", self.main.tr("sb_history")),
                ("bookmark", self.main.tr("sb_bookmarks")),
                ("sliders", self.main.tr("sb_language")),
                ("info", self.main.tr("sb_about")),
            ]
            for i, (kind, name) in enumerate(items):
                b = QPushButton(name)
                b.setObjectName("sidebarBtn")
                b.setCheckable(True); b.setAutoExclusive(True)
                b.setCursor(Qt.CursorShape.PointingHandCursor)
                b.setFixedHeight(34)
                b.setIconSize(QSize(18, 18))
                # Inline stylesheet guarantees colors apply
                b.setStyleSheet(_sidebar_button_style(palette))
                # State-based icon (On/Off)
                try:
                    icon = _make_state_icon(kind, palette, 18)
                    if not icon.isNull():
                        b.setIcon(icon)
                except Exception:
                    pass
                b.clicked.connect(lambda c=False, idx=i: self._on_nav_click(idx))
                sl.addWidget(b); self.nav_buttons.append(b)
            sl.addStretch()
            self.nav_buttons[0].setChecked(True)

            sidebar_scroll = QScrollArea()
            sidebar_scroll.setWidgetResizable(True)
            sidebar_scroll.setFrameShape(QFrame.Shape.NoFrame)
            sidebar_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            sidebar_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            sidebar_scroll.setWidget(sidebar)
            sidebar_scroll.setStyleSheet("""
                QScrollArea { background: transparent; border: none; }
                QScrollBar:vertical { background: transparent; width: 6px; margin: 0; }
                QScrollBar::handle:vertical { background: rgba(128,128,128,0.4);
                    border-radius: 3px; min-height: 20px; }
                QScrollBar::handle:vertical:hover { background: rgba(128,128,128,0.7); }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
            """)
            wrapper_layout.addWidget(sidebar_scroll)

            self.stack = QStackedWidget()
            self.stack.addWidget(self._page_theme())        # 0
            self.stack.addWidget(self._page_colors())       # 1
            self.stack.addWidget(self._page_search())       # 2
            self.stack.addWidget(self._page_zoom())         # 3
            self.stack.addWidget(self._page_downloads())    # 4
            self.stack.addWidget(self._page_passwords())    # 5
            self.stack.addWidget(self._page_history())      # 6
            self.stack.addWidget(self._page_bookmarks())    # 7
            self.stack.addWidget(self._page_system())       # 8
            self.stack.addWidget(self._page_about())        # 9
            layout.addWidget(sidebar_wrapper); layout.addWidget(self.stack, 1)
            for sa in self._scroll_areas:
                sa.set_smooth(self.main.smooth_scroll)
            QTimer.singleShot(0, lambda: _refresh_all_combo_views(
                self.main.current_theme, self.main.custom_colors))
        except Exception as e:
            try:
                print(f"SettingsTab._build error: {e}", file=sys.stderr)
            except Exception:
                pass

    def rebuild_preserving_page(self):
        try:
            idx = self.stack.currentIndex()
        except Exception:
            idx = 0
        try:
            self._build()
            if hasattr(self, 'stack') and 0 <= idx < self.stack.count():
                self.stack.setCurrentIndex(idx)
                if idx < len(self.nav_buttons):
                    self.nav_buttons[idx].setChecked(True)
        except Exception as e:
            try:
                print(f"SettingsTab.rebuild error: {e}", file=sys.stderr)
            except Exception:
                pass

    def _on_nav_click(self, index):
        self.stack.setCurrentIndex(index)
        if index == SETTINGS_HISTORY:
            try: self.refresh_history()
            except Exception: pass
        elif index == SETTINGS_BOOKMARKS:
            try: self.refresh_bookmarks()
            except Exception: pass

    def _on_search_text(self, text):
        text = text.strip().lower()
        for i, b in enumerate(self.nav_buttons):
            b.setVisible((not text) or (text in b.text().lower()))
        if text:
            cur = self.stack.currentIndex()
            if 0 <= cur < len(self.nav_buttons) and not self.nav_buttons[cur].isVisible():
                for i, b in enumerate(self.nav_buttons):
                    if b.isVisible():
                        self.stack.setCurrentIndex(i); b.setChecked(True); break

    def refresh_theme_icons(self):
        # After theme change, rebuild_preserving_page is called separately.
        # This method is kept for compatibility but does nothing extra.
        pass

    def show_page(self, index):
        if not (0 <= index < self.stack.count()): return
        self.stack.setCurrentIndex(index); self.nav_buttons[index].setChecked(True)
        if index == SETTINGS_HISTORY:
            try: self.refresh_history()
            except Exception: pass
        elif index == SETTINGS_BOOKMARKS:
            try: self.refresh_bookmarks()
            except Exception: pass

    def retranslate(self): self._build()
    def tab_title(self): return self.main.tr("settings_tab_title")

    def apply_smooth_scroll(self, enabled):
        for sa in self._scroll_areas:
            try: sa.set_smooth(enabled)
            except Exception: pass

    def _pal(self): return self.main.get_effective_palette()

    def _card(self):
        f = QFrame(); f.setObjectName("settingsCard")
        lay = QVBoxLayout(f); lay.setContentsMargins(16, 4, 16, 4); lay.setSpacing(0)
        return f, lay

    def _row(self, pl, title, sub, w, sep=False):
        if sep:
            s = QFrame(); s.setObjectName("settingsSeparator")
            s.setFrameShape(QFrame.Shape.HLine); pl.addWidget(s)
        row = QWidget(); row.setStyleSheet("background: transparent;")
        h = QHBoxLayout(row); h.setContentsMargins(0, 12, 0, 12); h.setSpacing(16)
        txt = QVBoxLayout(); txt.setSpacing(2)
        tl = QLabel(title); tl.setObjectName("settingsRowTitle"); txt.addWidget(tl)
        if sub:
            sl = QLabel(sub); sl.setObjectName("settingsRowSub")
            sl.setWordWrap(True); txt.addWidget(sl)
        h.addLayout(txt, 1)
        if w is not None: h.addWidget(w, 0, Qt.AlignmentFlag.AlignVCenter)
        pl.addWidget(row)

    def _section(self, v, title, subtitle=None):
        if title:
            l = QLabel(title); l.setObjectName("settingsSection")
            l.setContentsMargins(2, 12, 0, 0); v.addWidget(l)
        if subtitle:
            s = QLabel(subtitle)
            s.setStyleSheet(f"font-size: 12px; color: {self._pal()['text2']}; "
                            f"background: transparent;")
            s.setWordWrap(True); s.setContentsMargins(2, 0, 0, 6); v.addWidget(s)

    def _titled(self, title, subtitle=None):
        outer = QWidget(); ov = QVBoxLayout(outer)
        ov.setContentsMargins(0, 0, 0, 0); ov.setSpacing(0)
        scroll = SmoothScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.set_smooth(self.main.smooth_scroll)
        self._scroll_areas.append(scroll)
        inner = QWidget(); inner.setStyleSheet("background: transparent;")
        v = QVBoxLayout(inner); v.setContentsMargins(48, 32, 48, 48); v.setSpacing(8)
        t = QLabel(title)
        t.setStyleSheet("font-size: 24px; font-weight: 800; background: transparent;")
        v.addWidget(t)
        if subtitle:
            s = QLabel(subtitle)
            s.setStyleSheet(f"font-size: 13px; color: {self._pal()['text2']}; "
                            f"background: transparent;")
            s.setWordWrap(True); v.addWidget(s)
        v.addSpacing(10)
        scroll.setWidget(inner); ov.addWidget(scroll)
        return outer, v

    def _page_theme(self):
        w, v = self._titled(self.main.tr("theme_title"), self.main.tr("theme_sub"))
        pal = self._pal()

        c1, cl1 = self._card()
        self.theme_combo = QComboBox(); self.theme_combo.setMinimumWidth(240)
        for key in THEME_PALETTES.keys():
            self.theme_combo.addItem(THEME_NAMES[key].get(self.main.language, key), key)
        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemData(i) == self.main.current_theme:
                self.theme_combo.setCurrentIndex(i); break
        self.theme_combo.currentIndexChanged.connect(self._on_theme)
        self._row(cl1, self.main.tr("theme_label"), None, self.theme_combo)
        self.dark_toggle = ToggleSwitch(checked=self.main.dark_mode)
        self.dark_toggle.setColors(on_color=pal["accent"], off_color=pal["border"])
        self.dark_toggle.toggled.connect(self._on_dark_sites)
        self._row(cl1, self.main.tr("dark_sites_label"), self.main.tr("dark_sites_sub"),
                  self.dark_toggle, sep=True)
        self.close_glow_toggle = ToggleSwitch(checked=self.main.close_glow_effect)
        self.close_glow_toggle.setColors(on_color=pal["accent"], off_color=pal["border"])
        self.close_glow_toggle.toggled.connect(self._on_close_glow)
        self._row(cl1, self.main.tr("close_glow_label"), self.main.tr("close_glow_sub"),
                  self.close_glow_toggle, sep=True)
        v.addWidget(c1); v.addSpacing(10)

        self._section(v, self.main.tr("window_section_title"), None)
        c2, cl2 = self._card()
        self.hide_wall_toggle = ToggleSwitch(checked=self.main.hide_wallpaper_button)
        self.hide_wall_toggle.setColors(on_color=pal["accent"], off_color=pal["border"])
        self.hide_wall_toggle.toggled.connect(self._on_hide_wall)
        self._row(cl2, self.main.tr("hide_wall_btn_label"),
                  self.main.tr("hide_wall_btn_sub"), self.hide_wall_toggle)
        self.rtl_toggle = ToggleSwitch(checked=self.main.rtl_mode)
        self.rtl_toggle.setColors(on_color=pal["accent"], off_color=pal["border"])
        self.rtl_toggle.toggled.connect(self._on_rtl)
        self._row(cl2, self.main.tr("rtl_label"), self.main.tr("rtl_sub"),
                  self.rtl_toggle, sep=True)
        self.smooth_scroll_toggle = ToggleSwitch(checked=self.main.smooth_scroll)
        self.smooth_scroll_toggle.setColors(on_color=pal["accent"], off_color=pal["border"])
        self.smooth_scroll_toggle.toggled.connect(self._on_smooth_scroll)
        self._row(cl2, self.main.tr("smooth_scroll_label"),
                  self.main.tr("smooth_scroll_sub"),
                  self.smooth_scroll_toggle, sep=True)
        v.addWidget(c2); v.addSpacing(10)

        self._section(v, self.main.tr("wallpaper_settings_title"),
                      self.main.tr("wallpaper_settings_sub"))
        c3, cl3 = self._card()
        wp_w = QWidget(); wp_w.setStyleSheet("background: transparent;")
        wpl = QHBoxLayout(wp_w); wpl.setContentsMargins(0, 0, 0, 0); wpl.setSpacing(6)
        self.wp_hint = QLabel(self._wp_text())
        self.wp_hint.setObjectName("wallpaperHint")
        self.wp_hint.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.wp_hint.setMinimumWidth(180)
        wpl.addWidget(self.wp_hint, 1)
        pb = QPushButton(self.main.tr("wallpaper_pick"))
        pb.setCursor(Qt.CursorShape.PointingHandCursor)
        pb.clicked.connect(self._pick_wp); wpl.addWidget(pb)
        rb = QPushButton(self.main.tr("wallpaper_reset"))
        rb.setCursor(Qt.CursorShape.PointingHandCursor)
        rb.clicked.connect(self._reset_wp); wpl.addWidget(rb)
        self._row(cl3, self.main.tr("wallpaper_settings_title"), None, wp_w)
        v.addWidget(c3); v.addSpacing(10)

        self._section(v, self.main.tr("live_wall_title"), self.main.tr("live_wall_sub"))
        c4, cl4 = self._card()
        self.live_combo = QComboBox(); self.live_combo.setMinimumWidth(220)
        for k in LIVE_WALLPAPER_MODES:
            self.live_combo.addItem(self.main.tr(f"live_{k}"), k)
        cur = self.main.get_live_wallpaper_mode()
        for i in range(self.live_combo.count()):
            if self.live_combo.itemData(i) == cur:
                self.live_combo.setCurrentIndex(i); break
        self.live_combo.currentIndexChanged.connect(self._on_live_mode)
        self._row(cl4, self.main.tr("live_wall_title"), None, self.live_combo)
        spd_w = QWidget(); spd_w.setStyleSheet("background: transparent;")
        spd_l = QHBoxLayout(spd_w); spd_l.setContentsMargins(0, 0, 0, 0)
        self.live_speed = QComboBox(); self.live_speed.setMinimumWidth(120)
        for lbl, val in [("0.5x", 0.5), ("0.75x", 0.75), ("1x", 1.0),
                         ("1.5x", 1.5), ("2x", 2.0)]:
            self.live_speed.addItem(lbl, val)
        cur_s = self.main.get_live_wallpaper_speed()
        for i in range(self.live_speed.count()):
            if abs(self.live_speed.itemData(i) - cur_s) < 0.01:
                self.live_speed.setCurrentIndex(i); break
        self.live_speed.currentIndexChanged.connect(self._on_live_speed)
        spd_l.addWidget(self.live_speed)
        self._row(cl4, self.main.tr("live_speed"), None, spd_w, sep=True)
        v.addWidget(c4); v.addStretch()
        return w

    def _page_colors(self):
        w, v = self._titled(self.main.tr("custom_colors_title"),
                            self.main.tr("custom_colors_sub"))
        c, cl = self._card()
        grid_w = QWidget(); grid_w.setStyleSheet("background: transparent;")
        grid = QGridLayout(grid_w)
        grid.setContentsMargins(0, 12, 0, 12); grid.setSpacing(10)
        self._color_buttons = {}
        theme_pal = THEME_PALETTES.get(self.main.current_theme,
                                       THEME_PALETTES["dark"])
        for i, (key, label_key) in enumerate(COLOR_SLOTS):
            lbl = QLabel(self.main.tr(label_key))
            lbl.setObjectName("settingsRowTitle")
            grid.addWidget(lbl, i // 2, (i % 2) * 2)
            btn = ColorPickerButton(self.main.custom_colors.get(key, ""),
                                    theme_pal.get(key, "#000000"))
            btn.colorChanged.connect(lambda val, k=key: self._on_color_changed(k, val))
            self._color_buttons[key] = btn
            grid.addWidget(btn, i // 2, (i % 2) * 2 + 1)
        cl.addWidget(grid_w)
        reset_row = QWidget(); reset_row.setStyleSheet("background: transparent;")
        rr = QHBoxLayout(reset_row); rr.setContentsMargins(0, 6, 0, 12)
        rr.addStretch()
        reset_btn = QPushButton(self.main.tr("reset_colors"))
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.clicked.connect(self._reset_all_colors)
        rr.addWidget(reset_btn)
        cl.addWidget(reset_row)
        v.addWidget(c); v.addStretch()
        return w

    def _on_color_changed(self, key, val):
        if val: self.main.custom_colors[key] = val
        else: self.main.custom_colors.pop(key, None)
        self.main.save_custom_colors()
        self.main.apply_theme(self.main.current_theme, save=False)

    def _reset_all_colors(self):
        self.main.custom_colors = {}
        self.main.save_custom_colors()
        self.main.apply_theme(self.main.current_theme, save=False)
        theme_pal = THEME_PALETTES.get(self.main.current_theme,
                                       THEME_PALETTES["dark"])
        for key, btn in self._color_buttons.items():
            btn._current = ""
            btn._default = theme_pal.get(key, "#000000")
            btn._update_style()

    def _wp_text(self):
        wp = self.main.get_new_tab_wallpaper()
        if wp and os.path.exists(wp):
            return f"{self.main.tr('wallpaper_current')} {os.path.basename(wp)}"
        return self.main.tr("wallpaper_none")

    def _refresh_wp_hint(self):
        if hasattr(self, "wp_hint") and self.wp_hint is not None:
            try: self.wp_hint.setText(self._wp_text())
            except RuntimeError: pass

    def _pick_wp(self):
        popup = WallpaperPopup(self.main, self.window()); popup.adjustSize()
        btn = getattr(self, "wp_hint", None)
        if btn is None:
            screen = QApplication.primaryScreen().availableGeometry()
            x = screen.left() + (screen.width() - popup.width()) // 2
            y = screen.top() + (screen.height() - popup.height()) // 2
        else:
            br = btn.rect()
            bl = btn.mapToGlobal(br.bottomLeft())
            tr_ = btn.mapToGlobal(br.topRight())
            pw, ph = popup.width(), popup.height()
            screen = QApplication.primaryScreen().availableGeometry(); m = 8
            x = bl.x() + br.width() - pw; y = bl.y() + 6
            if y + ph > screen.bottom() - m: y = tr_.y() - ph - 6
            if x < screen.left() + m: x = screen.left() + m
            if x + pw > screen.right() - m: x = screen.right() - pw - m
            if y < screen.top() + m: y = screen.top() + m
        popup.move(QPoint(int(x), int(y))); popup.exec()
        self._refresh_wp_hint()

    def _reset_wp(self):
        self.main.set_new_tab_color("auto"); self._refresh_wp_hint()

    def _on_theme(self, idx):
        key = self.theme_combo.itemData(idx)
        self.main.apply_theme(key)
        QTimer.singleShot(0, lambda k=key: _refresh_all_combo_views(k,
                                                                   self.main.custom_colors))

    def _on_dark_sites(self, c): self.main.apply_dark_mode(c)

    def _on_close_glow(self, c):
        self.main.close_glow_effect = bool(c)
        self.main.qsettings.setValue("close_glow", "true" if c else "false")

    def _on_hide_wall(self, c): self.main.apply_hide_wallpaper_button(c)
    def _on_rtl(self, c): self.main.apply_rtl(c)
    def _on_smooth_scroll(self, c): self.main.apply_smooth_scroll(c)
    def _on_live_mode(self, idx):
        self.main.set_live_wallpaper_mode(self.live_combo.itemData(idx))
    def _on_live_speed(self, idx):
        self.main.set_live_wallpaper_speed(self.live_speed.itemData(idx))

    def _page_search(self):
        w, v = self._titled(self.main.tr("search_title"), self.main.tr("search_sub"))
        self._section(v, self.main.tr("search_engine_label").rstrip(":"),
                      self.main.tr("search_engine_desc"))
        c1, cl1 = self._card()
        self.search_combo = QComboBox(); self.search_combo.setMinimumWidth(220)
        for n in SEARCH_ENGINES: self.search_combo.addItem(n)
        self.search_combo.setCurrentText(self.main.search_engine_name)
        self.search_combo.currentTextChanged.connect(self._on_search)
        self._row(cl1, self.main.tr("search_engine_label").rstrip(":"), None, self.search_combo)
        v.addWidget(c1); v.addSpacing(10)
        self._section(v, self.main.tr("home_section_title"), self.main.tr("home_section_sub"))
        c2, cl2 = self._card()
        self.new_window_home_combo = QComboBox(); self.new_window_home_combo.setMinimumWidth(240)
        for k in HOME_OPTIONS_ORDER:
            self.new_window_home_combo.addItem(self.main.tr(HOME_LABELS[k]), k)
        cw = self.main.qsettings.value("new_window_home", "home")
        for i in range(self.new_window_home_combo.count()):
            if self.new_window_home_combo.itemData(i) == cw:
                self.new_window_home_combo.setCurrentIndex(i); break
        self.new_window_home_combo.currentIndexChanged.connect(self._on_nw_home)
        self._row(cl2, self.main.tr("home_new_windows"),
                  self.main.tr("home_new_windows_sub"), self.new_window_home_combo)
        self.new_tab_home_combo = QComboBox(); self.new_tab_home_combo.setMinimumWidth(240)
        for k in HOME_OPTIONS_ORDER:
            self.new_tab_home_combo.addItem(self.main.tr(HOME_LABELS[k]), k)
        ct = self.main.qsettings.value("new_tab_home", "home")
        for i in range(self.new_tab_home_combo.count()):
            if self.new_tab_home_combo.itemData(i) == ct:
                self.new_tab_home_combo.setCurrentIndex(i); break
        self.new_tab_home_combo.currentIndexChanged.connect(self._on_nt_home)
        self._row(cl2, self.main.tr("home_new_tabs"),
                  self.main.tr("home_new_tabs_sub"), self.new_tab_home_combo, sep=True)
        v.addWidget(c2); v.addStretch()
        return w

    def _on_search(self, n): self.main.set_search_engine(n)
    def _on_nw_home(self, i):
        self.main.qsettings.setValue("new_window_home",
                                     self.new_window_home_combo.itemData(i))
    def _on_nt_home(self, i):
        self.main.qsettings.setValue("new_tab_home",
                                     self.new_tab_home_combo.itemData(i))

    def _page_zoom(self):
        w, v = self._titled(self.main.tr("zoom_title"), self.main.tr("zoom_sub"))
        c, cl = self._card()
        self.zoom_combo = QComboBox(); self.zoom_combo.setMinimumWidth(220)
        for z in [50, 75, 100, 125, 150, 175, 200]:
            self.zoom_combo.addItem(f"{z}%", z / 100)
        idx = min(range(self.zoom_combo.count()),
                  key=lambda i: abs(self.zoom_combo.itemData(i) - self.main.current_zoom))
        self.zoom_combo.setCurrentIndex(idx)
        self.zoom_combo.currentIndexChanged.connect(
            lambda i: self.main.apply_zoom(self.zoom_combo.itemData(i)))
        self._row(cl, self.main.tr("page_zoom_label"),
                  self.main.tr("page_zoom_sub"), self.zoom_combo)
        self.text_zoom_combo = QComboBox(); self.text_zoom_combo.setMinimumWidth(220)
        for z in [80, 90, 100, 110, 125, 150, 175, 200]:
            self.text_zoom_combo.addItem(f"{z}%", z / 100)
        idx2 = min(range(self.text_zoom_combo.count()),
                   key=lambda i: abs(self.text_zoom_combo.itemData(i) - self.main.current_text_zoom))
        self.text_zoom_combo.setCurrentIndex(idx2)
        self.text_zoom_combo.currentIndexChanged.connect(
            lambda i: self.main.apply_text_zoom(self.text_zoom_combo.itemData(i)))
        self._row(cl, self.main.tr("text_zoom_label"),
                  self.main.tr("text_zoom_sub"), self.text_zoom_combo, sep=True)
        v.addWidget(c); v.addStretch()
        return w

    def _page_downloads(self):
        w, v = self._titled(self.main.tr("downloads_title"), self.main.tr("downloads_sub"))
        c, cl = self._card()
        pw = QWidget(); pw.setStyleSheet("background: transparent;")
        ph = QHBoxLayout(pw); ph.setContentsMargins(0, 0, 0, 0); ph.setSpacing(6)
        self.dl_path_label = QLabel(self.main.download_path)
        self.dl_path_label.setStyleSheet(
            f"background: {self._pal()['bg']}; padding: 6px 12px; border-radius: 10px;")
        self.dl_path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        ph.addWidget(self.dl_path_label)
        cb = QPushButton(self.main.tr("btn_change"))
        cb.clicked.connect(self._change_dl); ph.addWidget(cb)
        ob = QPushButton(self.main.tr("btn_open"))
        ob.clicked.connect(lambda: os.startfile(self.main.download_path)); ph.addWidget(ob)
        self._row(cl, self.main.tr("dl_path_label"), self.main.tr("dl_path_sub"), pw)
        v.addWidget(c); v.addStretch()
        return w

    def _change_dl(self):
        p = QFileDialog.getExistingDirectory(self, self.main.tr("choose_folder"),
                                             self.main.download_path)
        if p:
            self.main.set_download_path(p); self.dl_path_label.setText(p)

    def _page_passwords(self):
        w, v = self._titled(self.main.tr("passwords_title"), self.main.tr("passwords_sub"))
        c, cl = self._card()
        self.pw_table = QTableWidget(0, 3)
        self.pw_table.setHorizontalHeaderLabels([
            self.main.tr("col_site"), self.main.tr("col_login"),
            self.main.tr("col_password")])
        self.pw_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.pw_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.pw_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.pw_table.setMinimumHeight(260)
        self.pw_table.setStyleSheet("background: transparent; border: none;")
        tw = QWidget(); tw.setStyleSheet("background: transparent;")
        tl = QVBoxLayout(tw); tl.setContentsMargins(0, 8, 0, 8); tl.setSpacing(8)
        tl.addWidget(self.pw_table)
        br = QHBoxLayout()
        ab = QPushButton(self.main.tr("btn_add"))
        ab.clicked.connect(self._add_pw); br.addWidget(ab)
        db = QPushButton(self.main.tr("btn_delete"))
        db.clicked.connect(self._del_pw); br.addWidget(db)
        br.addStretch(); tl.addLayout(br)
        cl.addWidget(tw); v.addWidget(c); self.refresh_passwords(); v.addStretch()
        return w

    def refresh_passwords(self):
        if not hasattr(self, "pw_table"): return
        self.pw_table.setRowCount(0)
        for i, e in enumerate(self.main.passwords.entries):
            self.pw_table.insertRow(i)
            self.pw_table.setItem(i, 0, QTableWidgetItem(e["site"]))
            self.pw_table.setItem(i, 1, QTableWidgetItem(e["username"]))
            self.pw_table.setItem(i, 2, QTableWidgetItem("•" * len(e["password"])))

    def _add_pw(self):
        s, ok = QInputDialog.getText(self, self.main.tr("new_entry"),
                                     self.main.tr("site_field"))
        if not ok or not s.strip(): return
        u, ok = QInputDialog.getText(self, self.main.tr("new_entry"),
                                     self.main.tr("login_field"))
        if not ok: return
        p, ok = QInputDialog.getText(self, self.main.tr("new_entry"),
                                     self.main.tr("password_field"),
                                     QLineEdit.EchoMode.Password)
        if not ok: return
        s = s.strip()
        if not s.startswith("http"): s = "https://" + s
        self.main.passwords.upsert(s, u, p); self.refresh_passwords()

    def _del_pw(self):
        r = self.pw_table.currentRow()
        if r < 0: return
        self.main.passwords.delete(r); self.refresh_passwords()

    def _page_history(self):
        w, v = self._titled(self.main.tr("history_title"), self.main.tr("history_sub"))
        c, cl = self._card()
        self.history_table = QTableWidget(0, 2)
        self.history_table.setHorizontalHeaderLabels([
            self.main.tr("history_col_title"),
            self.main.tr("history_col_url")])
        self.history_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self.history_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        self.history_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers)
        self.history_table.setMinimumHeight(320)
        self.history_table.setStyleSheet("background: transparent; border: none;")
        tw = QWidget(); tw.setStyleSheet("background: transparent;")
        tl = QVBoxLayout(tw); tl.setContentsMargins(0, 8, 0, 8); tl.setSpacing(8)
        tl.addWidget(self.history_table)
        br = QHBoxLayout()
        ob = QPushButton(self.main.tr("history_open"))
        ob.setCursor(Qt.CursorShape.PointingHandCursor)
        ob.clicked.connect(self._open_history_row); br.addWidget(ob)
        db = QPushButton(self.main.tr("history_delete"))
        db.setCursor(Qt.CursorShape.PointingHandCursor)
        db.clicked.connect(self._delete_history_row); br.addWidget(db)
        cb = QPushButton(self.main.tr("history_clear_all"))
        cb.setCursor(Qt.CursorShape.PointingHandCursor)
        cb.clicked.connect(self._clear_all_history); br.addWidget(cb)
        br.addStretch(); tl.addLayout(br)
        cl.addWidget(tw)
        v.addWidget(c); self.refresh_history(); v.addStretch()
        return w

    def refresh_history(self):
        if not hasattr(self, "history_table"): return
        self.history_table.setRowCount(0)
        entries = self.main.history.recent(500)
        for i, e in enumerate(entries):
            self.history_table.insertRow(i)
            self.history_table.setItem(i, 0, QTableWidgetItem(e.get("title", "")))
            self.history_table.setItem(i, 1, QTableWidgetItem(e.get("url", "")))

    def _open_history_row(self):
        r = self.history_table.currentRow()
        if r < 0: return
        item = self.history_table.item(r, 1)
        if item is None: return
        url = item.text()
        if url:
            self.main.add_tab(url)

    def _delete_history_row(self):
        r = self.history_table.currentRow()
        if r < 0: return
        item = self.history_table.item(r, 1)
        if item is None: return
        self.main.history.remove(item.text())
        self.refresh_history()

    def _clear_all_history(self):
        r = QMessageBox.question(
            self, self.main.tr("history_title"),
            self.main.tr("history_clear_confirm"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if r == QMessageBox.StandardButton.Yes:
            self.main.history.clear()
            self.refresh_history()

    def _page_bookmarks(self):
        w, v = self._titled(self.main.tr("bookmarks_title"),
                            self.main.tr("bookmarks_sub"))
        c0, cl0 = self._card()
        self.bm_bar_toggle_p = ToggleSwitch(checked=self.main.show_bookmarks_bar)
        self.bm_bar_toggle_p.setColors(
            on_color=self._pal()["accent"], off_color=self._pal()["border"])
        self.bm_bar_toggle_p.toggled.connect(self._on_bm_bar_toggle)
        self._row(cl0, self.main.tr("bookmark_bar_label"),
                  self.main.tr("bookmark_bar_sub"),
                  self.bm_bar_toggle_p)
        v.addWidget(c0); v.addSpacing(10)

        c, cl = self._card()
        self.bm_table = QTableWidget(0, 2)
        self.bm_table.setHorizontalHeaderLabels([
            self.main.tr("col_bm_title"),
            self.main.tr("col_bm_url")])
        self.bm_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self.bm_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        self.bm_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers)
        self.bm_table.setMinimumHeight(320)
        self.bm_table.setStyleSheet("background: transparent; border: none;")
        self.bm_table.doubleClicked.connect(self._open_bookmark_row)
        tw = QWidget(); tw.setStyleSheet("background: transparent;")
        tl = QVBoxLayout(tw); tl.setContentsMargins(0, 8, 0, 8); tl.setSpacing(8)
        tl.addWidget(self.bm_table)
        br = QHBoxLayout()
        ob = QPushButton(self.main.tr("bm_open"))
        ob.setCursor(Qt.CursorShape.PointingHandCursor)
        ob.clicked.connect(self._open_bookmark_row); br.addWidget(ob)
        db = QPushButton(self.main.tr("bm_delete"))
        db.setCursor(Qt.CursorShape.PointingHandCursor)
        db.clicked.connect(self._delete_bookmark_row); br.addWidget(db)
        cb = QPushButton(self.main.tr("bm_clear_all"))
        cb.setCursor(Qt.CursorShape.PointingHandCursor)
        cb.clicked.connect(self._clear_all_bookmarks); br.addWidget(cb)
        br.addStretch(); tl.addLayout(br)
        cl.addWidget(tw)
        v.addWidget(c); self.refresh_bookmarks(); v.addStretch()
        return w

    def _on_bm_bar_toggle(self, c):
        self.main.toggle_bookmarks_bar(c)

    def refresh_bookmarks(self):
        if not hasattr(self, "bm_table"): return
        self.bm_table.setRowCount(0)
        entries = list(reversed(self.main.bookmarks.entries))
        for i, e in enumerate(entries):
            self.bm_table.insertRow(i)
            self.bm_table.setItem(i, 0, QTableWidgetItem(e.get("title", "")))
            self.bm_table.setItem(i, 1, QTableWidgetItem(e.get("url", "")))

    def _open_bookmark_row(self, *args):
        r = self.bm_table.currentRow()
        if r < 0: return
        item = self.bm_table.item(r, 1)
        if item is None: return
        url = item.text()
        if url:
            self.main.add_tab(url)

    def _delete_bookmark_row(self):
        r = self.bm_table.currentRow()
        if r < 0: return
        item = self.bm_table.item(r, 1)
        if item is None: return
        self.main.bookmarks.remove(item.text())
        self.main.bookmark_changed()

    def _clear_all_bookmarks(self):
        r = QMessageBox.question(
            self, self.main.tr("bookmarks_title"),
            self.main.tr("bm_clear_confirm"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if r == QMessageBox.StandardButton.Yes:
            self.main.bookmarks.clear()
            self.main.bookmark_changed()

    def _page_system(self):
        w, v = self._titled(self.main.tr("language_title"), self.main.tr("language_sub"))
        pal = self._pal()
        self._section(v, self.main.tr("language_label").rstrip(":"),
                      self.main.tr("language_sub2"))
        c1, cl1 = self._card()
        self.lang_combo = QComboBox(); self.lang_combo.setMinimumWidth(220)
        self.lang_combo.addItem(self.main.tr("lang_ru"), "ru")
        self.lang_combo.addItem(self.main.tr("lang_en"), "en")
        for i in range(self.lang_combo.count()):
            if self.lang_combo.itemData(i) == self.main.language:
                self.lang_combo.setCurrentIndex(i); break
        self.lang_combo.currentIndexChanged.connect(
            lambda i: self.main.apply_language(self.lang_combo.itemData(i)))
        self._row(cl1, self.main.tr("language_label").rstrip(":"), None, self.lang_combo)
        self.layout_combo = QComboBox(); self.layout_combo.setMinimumWidth(220)
        self.layout_combo.addItem(self.main.tr("pos_top"), "top")
        self.layout_combo.addItem(self.main.tr("pos_bottom"), "bottom")
        for i in range(self.layout_combo.count()):
            if self.layout_combo.itemData(i) == self.main.layout_position:
                self.layout_combo.setCurrentIndex(i); break
        self.layout_combo.currentIndexChanged.connect(
            lambda i: self.main.apply_layout(self.layout_combo.itemData(i)))
        self._row(cl1, self.main.tr("layout_label"), self.main.tr("layout_sub"),
                  self.layout_combo, sep=True)
        v.addWidget(c1); v.addSpacing(10)
        c2, cl2 = self._card()
        self.autostart_toggle = ToggleSwitch(checked=is_autostart_enabled())
        self.autostart_toggle.setColors(on_color=pal["accent"], off_color=pal["border"])
        self.autostart_toggle.toggled.connect(self._on_autostart)
        self._row(cl2, self.main.tr("autostart_label"),
                  self.main.tr("autostart_sub"), self.autostart_toggle)
        self.restore_tabs_toggle = ToggleSwitch(checked=self.main.restore_tabs)
        self.restore_tabs_toggle.setColors(on_color=pal["accent"], off_color=pal["border"])
        self.restore_tabs_toggle.toggled.connect(self._on_restore_tabs)
        self._row(cl2, self.main.tr("restore_tabs_label"),
                  self.main.tr("restore_tabs_sub"), self.restore_tabs_toggle, sep=True)
        v.addWidget(c2); v.addSpacing(10)
        self._section(v, self.main.tr("font_section_title"),
                      self.main.tr("font_section_sub"))
        cf, clf = self._card()
        self.font_combo = QComboBox(); self.font_combo.setMinimumWidth(220)
        try: available = set(QFontDatabase.families())
        except Exception: available = set()
        font_list = []
        for f in UI_FONTS:
            if (not available) or (f in available): font_list.append(f)
        if available:
            for f in sorted(available):
                if f not in font_list: font_list.append(f)
        if not font_list: font_list = list(UI_FONTS)
        for f in font_list: self.font_combo.addItem(f)
        cur = self.main.ui_font
        idx = self.font_combo.findText(cur)
        if idx < 0:
            self.font_combo.addItem(cur); idx = self.font_combo.count() - 1
        self.font_combo.setCurrentIndex(idx)
        self.font_combo.currentTextChanged.connect(
            lambda t: self.main.apply_font(t) if t else None)
        self._row(clf, self.main.tr("font_family_label"),
                  self.main.tr("font_family_sub"), self.font_combo)
        v.addWidget(cf); v.addSpacing(10)
        self._section(v, self.main.tr("density_title"), self.main.tr("density_sub"))
        c3, cl3 = self._card()
        self.density_toggles = {}
        density_items = [("auto", "density_auto", "density_auto_sub"),
                         ("standard", "density_standard", "density_standard_sub"),
                         ("compact", "density_compact", "density_compact_sub"),
                         ("touch", "density_touch", "density_touch_sub")]
        cur_d = getattr(self.main, "density", "auto")
        for i, (k, nk, sk) in enumerate(density_items):
            tg = ToggleSwitch(checked=(cur_d == k))
            tg.setColors(on_color=pal["accent"], off_color=pal["border"])
            tg.toggled.connect(lambda c, kk=k: self._on_density(kk, c))
            self.density_toggles[k] = tg
            self._row(cl3, self.main.tr(nk), self.main.tr(sk), tg, sep=(i > 0))
        v.addWidget(c3); v.addSpacing(10)
        self._section(v, self.main.tr("browsing_data_title"),
                      self.main.tr("browsing_data_sub"))
        cd, cld = self._card()
        dw = QWidget(); dw.setStyleSheet("background: transparent;")
        dl = QGridLayout(dw); dl.setContentsMargins(0, 0, 0, 0); dl.setSpacing(6)
        for i, (lbl, fn) in enumerate([
                (self.main.tr("clear_cache"), self._clear_cache),
                (self.main.tr("clear_cookies"), self._clear_cookies),
                (self.main.tr("clear_history"), self._clear_history),
                (self.main.tr("clear_all"), self._clear_all)]):
            b = QPushButton(lbl); b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(fn); dl.addWidget(b, i // 2, i % 2)
        self._row(cld, self.main.tr("browsing_data_title"), None, dw)
        v.addWidget(cd); v.addStretch()
        return w

    def _clear_cache(self):
        try: QWebEngineProfile.defaultProfile().clearHttpCache()
        except Exception: pass
        QMessageBox.information(self, self.main.tr("clear_done_title"),
                                self.main.tr("clear_cache_done"))

    def _clear_cookies(self):
        try:
            p = QWebEngineProfile.defaultProfile()
            p.cookieStore().deleteAllCookies()
            try: p.clearAllVisitedLinks()
            except Exception: pass
        except Exception: pass
        QMessageBox.information(self, self.main.tr("clear_done_title"),
                                self.main.tr("clear_cookies_done"))

    def _clear_history(self):
        try:
            p = QWebEngineProfile.defaultProfile()
            try: p.clearAllVisitedLinks()
            except Exception: pass
            self.main.qsettings.setValue("saved_tabs", "[]")
            self.main.history.clear()
        except Exception: pass
        try: self.refresh_history()
        except Exception: pass
        QMessageBox.information(self, self.main.tr("clear_done_title"),
                                self.main.tr("clear_history_done"))

    def _clear_all(self):
        r = QMessageBox.question(self, self.main.tr("clear_all_confirm_title"),
                                 self.main.tr("clear_all_confirm_msg"),
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if r != QMessageBox.StandardButton.Yes: return
        try:
            p = QWebEngineProfile.defaultProfile()
            p.clearHttpCache(); p.cookieStore().deleteAllCookies()
            try: p.clearAllVisitedLinks()
            except Exception: pass
            self.main.qsettings.setValue("saved_tabs", "[]")
            self.main.history.clear()
        except Exception: pass
        try: self.refresh_history()
        except Exception: pass
        QMessageBox.information(self, self.main.tr("clear_done_title"),
                                self.main.tr("clear_all_done"))

    def _on_density(self, key, checked):
        tg = self.density_toggles.get(key)
        if tg is None: return
        if not checked:
            if all(not t.isChecked() for t in self.density_toggles.values()):
                tg.blockSignals(True); tg.setChecked(True, animate=True)
                tg.blockSignals(False)
            return
        for k, other in self.density_toggles.items():
            if k != key and other.isChecked():
                other.blockSignals(True); other.setChecked(False, animate=True)
                other.blockSignals(False)
        self.main.apply_density(key)

    def _on_autostart(self, c):
        if not set_autostart(c):
            self.autostart_toggle.blockSignals(True)
            self.autostart_toggle.setChecked(not c, animate=True)
            self.autostart_toggle.blockSignals(False)

    def _on_restore_tabs(self, c):
        self.main.restore_tabs = bool(c)
        self.main.qsettings.setValue("restore_tabs", "true" if c else "false")

    def _about_content(self):
        if self.main.language == "ru":
            return {
                "title": "О Flexion Browser",
                "version": f"Версия {APP_VERSION}",
                "tagline": "Быстрый. Гибкий. Твой.",
                "desc": ("Flexion — браузер, созданный с упором на скорость, "
                         "минимализм и максимальную кастомизацию. Никаких лишних "
                         "элементов и слежки — только вы и интернет."),
                "features_title": "Возможности",
                "features": [
                    ("bolt", "Скорость", "Быстрый запуск, мгновенная загрузка, GPU-ускорение рендеринга."),
                    ("palette", "Глубокая кастомизация", "28 встроенных тем, пользовательские цвета, обои, шрифты и плотность."),
                    ("wallpaper", "22 живых обоев", "Матрица, звёзды, северное сияние, вихрь и другие. Приостанавливаются при неактивности вкладки."),
                    ("shield", "Блокировка рекламы", "Встроенный блокировщик рекламных сетей и трекеров."),
                    ("lock", "Менеджер паролей", "Локальное хранилище учётных данных с автозаполнением."),
                    ("history", "История", "Все посещённые страницы. Удаление отдельных записей и полная очистка."),
                    ("bookmark", "Закладки", "Кнопка-звёздочка для быстрого сохранения, панель закладок под адресной строкой."),
                    ("globe", "Перевод страниц", "Google Translate в один клик прямо из панели."),
                    ("download", "Менеджер загрузок", "Индикатор прогресса в панели, история и быстрый доступ к файлам."),
                    ("keyboard", "Горячие клавиши", "Полный набор сочетаний — работа без использования мыши."),
                    ("search", "Поиск на странице", "Ctrl+F — стандартное поведение как в других браузерах."),
                ],
                "shortcuts_title": "Горячие клавиши",
                "shortcuts": [
                    ("Ctrl+T", "Новая вкладка"), ("Ctrl+W", "Закрыть вкладку"),
                    ("Ctrl+Tab", "Следующая вкладка"), ("Ctrl+Shift+Tab", "Предыдущая вкладка"),
                    ("Ctrl+N", "Новое окно"), ("Ctrl+L / F6", "Адресная строка"),
                    ("Ctrl+F", "Найти на странице"), ("Ctrl+J", "Загрузки"),
                    ("Ctrl+D", "Добавить в закладки"), ("Ctrl+B", "Панель закладок"),
                    ("Ctrl+Shift+O", "Менеджер закладок"),
                    ("Ctrl+P", "Логины и пароли"), ("Ctrl+,", "Настройки"),
                    ("Ctrl++", "Увеличить"), ("Ctrl+-", "Уменьшить"),
                    ("Ctrl+0", "Сбросить масштаб"), ("F5 / Ctrl+R", "Обновить"),
                    ("F11", "Полный экран"), ("F12", "DevTools"),
                    ("Ctrl+Shift+A", "Кастомизация"), ("Ctrl+Q", "Выход"),
                ],
                "credits": "Сделано с ❤ на Python + PyQt6 + QtWebEngine",
            }
        return {
            "title": "About Flexion Browser",
            "version": f"Version {APP_VERSION}",
            "tagline": "Fast. Flexible. Yours.",
            "desc": ("Flexion is a browser built around speed, minimalism "
                     "and deep customization. No bloat, no tracking — "
                     "just you and the web."),
            "features_title": "Features",
            "features": [
                ("bolt", "Speed", "Fast startup, instant loading, GPU-accelerated rendering."),
                ("palette", "Deep customization", "28 built-in themes, custom colors, wallpapers, fonts and density."),
                ("wallpaper", "22 live wallpapers", "Matrix, stars, aurora, vortex and more. Paused when the tab is inactive."),
                ("shield", "Ad blocking", "Built-in blocker for ad networks and trackers."),
                ("lock", "Password manager", "Local credential vault with autofill."),
                ("history", "History", "All visited pages. Delete single entries or clear all."),
                ("bookmark", "Bookmarks", "Star button for quick save, bookmarks bar below the address bar."),
                ("globe", "Page translation", "Google Translate in one click from the toolbar."),
                ("download", "Download manager", "Progress indicator in the toolbar, history and quick file access."),
                ("keyboard", "Hotkeys", "Full keyboard shortcut set — no mouse needed."),
                ("search", "Find on page", "Ctrl+F — standard behavior like other browsers."),
            ],
            "shortcuts_title": "Keyboard shortcuts",
            "shortcuts": [
                ("Ctrl+T", "New tab"), ("Ctrl+W", "Close tab"),
                ("Ctrl+Tab", "Next tab"), ("Ctrl+Shift+Tab", "Previous tab"),
                ("Ctrl+N", "New window"), ("Ctrl+L / F6", "Address bar"),
                ("Ctrl+F", "Find on page"), ("Ctrl+J", "Downloads"),
                ("Ctrl+D", "Add bookmark"), ("Ctrl+B", "Bookmarks bar"),
                ("Ctrl+Shift+O", "Bookmarks manager"),
                ("Ctrl+P", "Logins & Passwords"), ("Ctrl+,", "Settings"),
                ("Ctrl++", "Zoom in"), ("Ctrl+-", "Zoom out"),
                ("Ctrl+0", "Reset zoom"), ("F5 / Ctrl+R", "Reload"),
                ("F11", "Fullscreen"), ("F12", "DevTools"),
                ("Ctrl+Shift+A", "Customization"), ("Ctrl+Q", "Quit"),
            ],
            "credits": "Made with ❤ on Python + PyQt6 + QtWebEngine",
        }

    def _page_about(self):
        content = self._about_content()
        w, v = self._titled(content["title"], content["tagline"])
        pal = self._pal()
        hc, hcl = self._card()
        header_w = QWidget(); header_w.setStyleSheet("background: transparent;")
        hl = QHBoxLayout(header_w)
        hl.setContentsMargins(0, 16, 0, 16); hl.setSpacing(16)
        logo = QLabel(); logo.setFixedSize(72, 72)
        logo.setPixmap(self._make_logo(72))
        hl.addWidget(logo, 0, Qt.AlignmentFlag.AlignVCenter)
        text_w = QWidget(); text_w.setStyleSheet("background: transparent;")
        tl = QVBoxLayout(text_w); tl.setContentsMargins(0, 0, 0, 0); tl.setSpacing(4)
        tn = QLabel(content["title"]); tn.setObjectName("aboutTitle")
        tv = QLabel(content["version"]); tv.setObjectName("aboutTagline")
        td = QLabel(content["desc"]); td.setObjectName("aboutText")
        td.setWordWrap(True)
        tl.addWidget(tn); tl.addWidget(tv); tl.addWidget(td)
        hl.addWidget(text_w, 1)
        hcl.addWidget(header_w)
        v.addWidget(hc); v.addSpacing(16)
        self._section(v, content["features_title"], None)
        icon_color = pal["accent"]
        for kind, title, desc in content["features"]:
            fc, fcl = self._card()
            fw = QWidget(); fw.setStyleSheet("background: transparent;")
            fl = QHBoxLayout(fw)
            fl.setContentsMargins(0, 10, 0, 10); fl.setSpacing(14)
            il = QLabel()
            pix = _make_sidebar_pixmap(kind, icon_color, 24)
            il.setPixmap(pix)
            il.setFixedSize(30, 30)
            il.setAlignment(Qt.AlignmentFlag.AlignCenter)
            il.setStyleSheet("background: transparent;")
            fl.addWidget(il, 0, Qt.AlignmentFlag.AlignVCenter)
            tw = QWidget(); tw.setStyleSheet("background: transparent;")
            tl2 = QVBoxLayout(tw); tl2.setContentsMargins(0, 0, 0, 0); tl2.setSpacing(2)
            t1 = QLabel(title); t1.setObjectName("aboutFeatureTitle")
            t2 = QLabel(desc); t2.setObjectName("aboutFeatureDesc")
            t2.setWordWrap(True)
            tl2.addWidget(t1); tl2.addWidget(t2)
            fl.addWidget(tw, 1)
            fcl.addWidget(fw)
            v.addWidget(fc); v.addSpacing(6)
        v.addSpacing(16)
        self._section(v, content["shortcuts_title"], None)
        sc, scl = self._card()
        gw = QWidget(); gw.setStyleSheet("background: transparent;")
        grid = QGridLayout(gw)
        grid.setContentsMargins(0, 10, 0, 10); grid.setHorizontalSpacing(30)
        grid.setVerticalSpacing(8)
        for i, (key, desc) in enumerate(content["shortcuts"]):
            kl = QLabel(key)
            kl.setStyleSheet(
                f"background: {pal['bg']}; padding: 4px 10px; "
                f"border-radius: 6px; font-family: 'Consolas', monospace; "
                f"font-size: 12px; font-weight: 700;")
            dl = QLabel(desc)
            dl.setStyleSheet(f"color: {pal['text2']}; background: transparent; "
                             f"font-size: 13px;")
            grid.addWidget(kl, i // 2, (i % 2) * 2)
            grid.addWidget(dl, i // 2, (i % 2) * 2 + 1)
        scl.addWidget(gw)
        v.addWidget(sc); v.addSpacing(20)
        cr = QLabel(content["credits"])
        cr.setStyleSheet(f"color: {pal['text2']}; background: transparent; "
                         f"font-size: 12px;")
        cr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(cr)

        github_link = QLabel(
            f'<a href="{GITHUB_URL}" style="color: {pal["accent"]};">'
            f'GitHub: @{GITHUB_USERNAME}</a>'
        )
        github_link.setOpenExternalLinks(True)
        github_link.setTextFormat(Qt.TextFormat.RichText)
        github_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        github_link.setStyleSheet(
            "font-size: 13px; font-weight: 600; background: transparent; "
            "padding: 8px 0;")
        v.addWidget(github_link)

        v.addStretch()
        return w

    def _make_logo(self, size):
        pix = QPixmap(size, size); pix.fill(Qt.GlobalColor.transparent)
        p = QPainter(pix); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        pal = self._pal()
        accent = QColor(pal["accent"])
        grad = QLinearGradient(0.0, 0.0, float(size), float(size))
        grad.setColorAt(0, accent)
        c2 = QColor(accent); c2.setHsv((c2.hue() + 60) % 360, c2.saturation(),
                                        min(255, c2.value() + 30))
        grad.setColorAt(1, c2)
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(grad))
        p.drawRoundedRect(0, 0, size, size, size * 0.22, size * 0.22)
        p.setPen(QPen(QColor(pal["accent_text"])))
        f = QFont("Segoe UI", int(size * 0.45)); f.setBold(True)
        p.setFont(f)
        p.drawText(QRect(0, -int(size * 0.05), size, size),
                   Qt.AlignmentFlag.AlignCenter, "F")
        p.setBrush(QColor(pal["accent_text"])); p.setPen(Qt.PenStyle.NoPen)
        cx, cy = size * 0.76, size * 0.24; r = size * 0.08
        sp = QPainterPath()
        sp.moveTo(cx, cy - r)
        sp.quadTo(cx + r * 0.2, cy - r * 0.2, cx + r, cy)
        sp.quadTo(cx + r * 0.2, cy + r * 0.2, cx, cy + r)
        sp.quadTo(cx - r * 0.2, cy + r * 0.2, cx - r, cy)
        sp.quadTo(cx - r * 0.2, cy - r * 0.2, cx, cy - r)
        sp.closeSubpath()
        p.drawPath(sp); p.end()
        return pix


class DownloadsPopup(QDialog):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main = main_window
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setFixedWidth(440)
        self.palette_ = main_window.get_effective_palette()
        pal = self.palette_
        self.setStyleSheet(f"""
            QDialog {{ background-color: {pal['panel']}; border: 1px solid {pal['border']};
                border-radius: 12px; }}
            QLabel {{ color: {pal['text']}; background: transparent; }}
            QScrollArea {{ background: transparent; border: none; }}
            QScrollArea > QWidget > QWidget {{ background: transparent; }}
            QScrollBar:vertical {{ background: transparent; width: 8px;
                border-radius: 4px; margin: 0; }}
            QScrollBar::handle:vertical {{ background: {pal['border']};
                border-radius: 4px; min-height: 20px; }}
            QScrollBar::handle:vertical:hover {{ background: {pal['hover']}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                background: none; height: 0; }}
            QPushButton#dlFolderBtn {{ background: transparent; border: none;
                border-radius: 6px; padding: 0; }}
            QPushButton#dlFolderBtn:hover {{ background: {pal['hover']}; }}
            QPushButton#dlHeaderBtn {{ background: transparent; border: none;
                border-radius: 6px; padding: 0; }}
            QPushButton#dlHeaderBtn:hover {{ background: {pal['hover']}; }}
            QFrame#dlSeparator {{ background: {pal['border']};
                max-height: 1px; border: none; }}
            QProgressBar {{ background-color: {pal['bg']}; border: none;
                border-radius: 3px; }}
            QProgressBar::chunk {{ background-color: {pal['accent']};
                border-radius: 3px; }}
        """)

        header = QWidget()
        header.setStyleSheet("background: transparent;")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(14, 0, 10, 0)
        hl.setSpacing(4)
        title = QLabel(main_window.tr("sb_downloads"))
        title.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {pal['text']};")
        hl.addWidget(title)
        hl.addStretch()
        hfb = QPushButton()
        hfb.setObjectName("dlHeaderBtn")
        hfb.setFixedSize(26, 26)
        hfb.setIconSize(QSize(16, 16))
        hfb.setIcon(QIcon(self.main._icon_folder))
        hfb.setCursor(Qt.CursorShape.PointingHandCursor)
        hfb.setToolTip(main_window.tr("dl_open_folder"))
        hfb.clicked.connect(self._open_folder)
        hl.addWidget(hfb)

        sep = QFrame(); sep.setObjectName("dlSeparator")
        sep.setFrameShape(QFrame.Shape.HLine)

        self.scroll = SmoothScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.set_smooth(main_window.smooth_scroll)
        self.content = QWidget()
        self.content.setStyleSheet("background: transparent;")
        self.list_layout = QVBoxLayout(self.content)
        self.list_layout.setContentsMargins(4, 4, 4, 4)
        self.list_layout.setSpacing(0)
        self.scroll.setWidget(self.content)
        self._build_list()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 12)
        layout.setSpacing(0)
        layout.addWidget(header)
        layout.addSpacing(8)
        layout.addWidget(sep)
        layout.addWidget(self.scroll, 1)

        self._anim = QPropertyAnimation(self, b"windowOpacity", self)
        self._anim.setDuration(140)

    def _clear(self):
        while self.list_layout.count():
            it = self.list_layout.takeAt(0)
            w = it.widget()
            if w is not None:
                w.setParent(None); w.deleteLater()

    def _build_list(self):
        self._clear()
        pal = self.palette_
        dl = self.main.downloads
        if not dl:
            e = QLabel(self.main.tr("no_downloads"))
            e.setAlignment(Qt.AlignmentFlag.AlignCenter)
            e.setStyleSheet(
                f"color: {pal['text2']}; padding: 30px 10px; font-size: 13px;")
            self.list_layout.addWidget(e)
            self.scroll.setMinimumHeight(90)
            self.scroll.setMaximumHeight(110)
            return

        for idx, d in enumerate(reversed(dl[-20:])):
            if idx > 0:
                s = QFrame()
                s.setStyleSheet(
                    f"background: {pal['border']}; max-height: 1px; border: none;")
                s.setFixedHeight(1)
                self.list_layout.addWidget(s)
            row_w = self._make_row(d)
            self.list_layout.addWidget(row_w)

        vis = min(len(dl), 20)
        h = min(40 + vis * 68, 420)
        self.scroll.setMinimumHeight(h)
        self.scroll.setMaximumHeight(h)

    def _make_row(self, d):
        pal = self.palette_
        name = d.get("name", "download")
        path = d.get("path", "")
        fin = d.get("finished", False)
        pr = float(d.get("progress", 0.0))
        status = d.get("status", "0%")
        total = d.get("total", 0)
        received = d.get("received", 0)

        ext = ""
        if "." in name:
            ext = name.rsplit(".", 1)[-1].lower()

        rw = QWidget()
        rw.setStyleSheet("background: transparent;")
        rw.setFixedHeight(64)
        row = QHBoxLayout(rw)
        row.setContentsMargins(12, 8, 10, 8)
        row.setSpacing(12)

        icon_lbl = QLabel()
        icon_pix = _make_file_icon(ext, pal["accent"], 36)
        icon_lbl.setPixmap(icon_pix)
        icon_lbl.setFixedSize(36, 36)
        icon_lbl.setStyleSheet("background: transparent;")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(icon_lbl, 0, Qt.AlignmentFlag.AlignVCenter)

        text_w = QWidget()
        text_w.setStyleSheet("background: transparent;")
        tl = QVBoxLayout(text_w)
        tl.setContentsMargins(0, 0, 0, 0)
        tl.setSpacing(3)

        name_lbl = QLabel()
        name_lbl.setStyleSheet(
            f"color: {pal['text']}; font-size: 13px; font-weight: 600; "
            f"background: transparent;")
        name_lbl.setToolTip(name)
        name_lbl.setMinimumWidth(180)
        fm = QFontMetrics(name_lbl.font())
        elided = fm.elidedText(name, Qt.TextElideMode.ElideMiddle, 260)
        name_lbl.setText(elided)
        tl.addWidget(name_lbl)

        if not fin and pr < 1.0:
            if total > 0:
                info_txt = f"{_fmt_size(received)} / {_fmt_size(total)}  ·  {status}"
            else:
                info_txt = status
            info_lbl = QLabel(info_txt)
            info_lbl.setStyleSheet(
                f"color: {pal['text2']}; font-size: 11px; background: transparent;")
            tl.addWidget(info_lbl)

            bar = QProgressBar()
            bar.setRange(0, 1000)
            bar.setValue(int(pr * 1000))
            bar.setTextVisible(False)
            bar.setFixedHeight(4)
            bar.setStyleSheet(
                f"QProgressBar {{ background-color: {pal['bg']}; "
                f"border: none; border-radius: 2px; }}"
                f"QProgressBar::chunk {{ background-color: {pal['accent']}; "
                f"border-radius: 2px; }}")
            tl.addWidget(bar)
        else:
            size_txt = ""
            if total > 0:
                size_txt = _fmt_size(total)
            elif path and os.path.exists(path):
                try: size_txt = _fmt_size(os.path.getsize(path))
                except Exception: size_txt = ""
            info_lbl = QLabel(size_txt or self.main.tr("status_done"))
            info_lbl.setStyleSheet(
                f"color: {pal['text2']}; font-size: 11px; background: transparent;")
            tl.addWidget(info_lbl)

        row.addWidget(text_w, 1)

        if path:
            fb = QPushButton()
            fb.setObjectName("dlFolderBtn")
            fb.setFixedSize(28, 28)
            fb.setIconSize(QSize(16, 16))
            fb.setIcon(QIcon(self.main._icon_folder))
            fb.setCursor(Qt.CursorShape.PointingHandCursor)
            fb.setToolTip(self.main.tr("dl_open_file_folder"))
            fb.clicked.connect(lambda c=False, p=path: self._open_file_folder(p))
            row.addWidget(fb, 0, Qt.AlignmentFlag.AlignVCenter)

        return rw

    def refresh_downloads(self):
        self._build_list()

    def _open_file_folder(self, path):
        try:
            f = os.path.dirname(path)
            if os.path.exists(f):
                os.startfile(f)
            else:
                os.startfile(self.main.download_path)
        except Exception:
            pass
        self.accept()

    def _open_folder(self):
        try:
            os.makedirs(self.main.download_path, exist_ok=True)
            os.startfile(self.main.download_path)
        except Exception:
            pass
        self.accept()

    def showEvent(self, e):
        super().showEvent(e)
        self.setWindowOpacity(0.0)
        self._anim.stop()
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.start()


class TranslatePopup(QDialog):
    def __init__(self, main_window, target_lang, parent=None):
        super().__init__(parent)
        self.main = main_window
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setMinimumWidth(300)
        pal = main_window.get_effective_palette()
        self.setStyleSheet(f"""
            QDialog {{ background-color: {pal['panel']}; border: 1px solid {pal['border']};
                border-radius: 12px; }}
            QLabel {{ color: {pal['text']}; background: transparent; }}
            QComboBox {{ background-color: {pal['bg']}; color: {pal['text']};
                border: 1px solid {pal['border']}; border-radius: 10px; padding: 5px 12px; }}
            QComboBox QAbstractItemView {{ background-color: {pal['bg']}; color: {pal['text']};
                selection-background-color: {pal['accent']}; }}
            QPushButton {{ background-color: {pal['bg']}; color: {pal['text']};
                border: 1px solid {pal['border']}; border-radius: 10px;
                padding: 5px 14px; font-weight: 700; }}
            QPushButton:hover {{ background-color: {pal['hover']}; }}
        """)
        t = QLabel(main_window.tr("translate_title"))
        t.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {pal['text']};")
        form = QFormLayout(); form.setSpacing(10); form.setContentsMargins(14, 4, 14, 4)
        self.from_combo = QComboBox()
        self.from_combo.addItem(main_window.tr("translate_auto"), "auto")
        for c, n in TRANSLATE_LANGS.items(): self.from_combo.addItem(n, c)
        self.to_combo = QComboBox()
        for c, n in TRANSLATE_LANGS.items(): self.to_combo.addItem(n, c)
        for i in range(self.to_combo.count()):
            if self.to_combo.itemData(i) == target_lang:
                self.to_combo.setCurrentIndex(i); break
        form.addRow(QLabel(main_window.tr("translate_from")), self.from_combo)
        form.addRow(QLabel(main_window.tr("translate_to")), self.to_combo)
        br = QHBoxLayout(); br.setContentsMargins(14, 4, 14, 14); br.setSpacing(8)
        br.addStretch()
        cb = QPushButton(main_window.tr("btn_cancel"))
        cb.clicked.connect(self.reject); br.addWidget(cb)
        gb = QPushButton(main_window.tr("translate_go"))
        gb.clicked.connect(self.accept); br.addWidget(gb)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 0); layout.setSpacing(8)
        layout.addWidget(t, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addLayout(form); layout.addLayout(br)
        self._anim = QPropertyAnimation(self, b"windowOpacity", self)
        self._anim.setDuration(140)

    def showEvent(self, e):
        super().showEvent(e)
        self.setWindowOpacity(0.0)
        self._anim.stop(); self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0); self._anim.start()

    def get_values(self):
        return self.from_combo.currentData(), self.to_combo.currentData()


class FlexionBrowser(QMainWindow):
    RESIZE_MARGIN = 6

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle(APP_NAME)
        self.resize(1200, 800)
        try:
            self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
            self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        except Exception: pass

        self._was_maximized_before_fs = False
        self._is_fs_mode = False

        self.qsettings = QSettings()
        self.language = self.qsettings.value("language", "ru")

        saved_theme = self.qsettings.value("theme", "dark")
        if saved_theme not in THEME_PALETTES: saved_theme = "dark"
        self.current_theme = saved_theme

        saved_density = self.qsettings.value("density", "auto")
        if saved_density not in DENSITY_PRESETS: saved_density = "auto"
        self.density = saved_density

        self.layout_position = self.qsettings.value("layout_position", "top")
        self.current_zoom = float(self.qsettings.value("zoom", 1.0))
        self.current_text_zoom = float(self.qsettings.value("text_zoom", 1.0))

        saved_engine = self.qsettings.value("search_engine", "DuckDuckGo")
        if saved_engine not in SEARCH_ENGINES: saved_engine = "DuckDuckGo"
        self.search_engine_name = saved_engine
        self.search_engine_template = SEARCH_ENGINES.get(
            self.search_engine_name, SEARCH_ENGINES["DuckDuckGo"])["search"]
        self.download_path = self.qsettings.value(
            "download_path",
            QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadLocation))

        dm = self.qsettings.value("dark_mode", "false")
        self.dark_mode = dm if isinstance(dm, bool) else str(dm).lower() == "true"
        cg = self.qsettings.value("close_glow", "false")
        self.close_glow_effect = cg if isinstance(cg, bool) else str(cg).lower() == "true"
        rt = self.qsettings.value("restore_tabs", "false")
        self.restore_tabs = rt if isinstance(rt, bool) else str(rt).lower() == "true"
        hw = self.qsettings.value("hide_wallpaper_button", "false")
        self.hide_wallpaper_button = hw if isinstance(hw, bool) else str(hw).lower() == "true"
        rtl_raw = self.qsettings.value("rtl_mode", "false")
        self.rtl_mode = rtl_raw if isinstance(rtl_raw, bool) else str(rtl_raw).lower() == "true"
        ss_raw = self.qsettings.value("smooth_scroll", "true")
        self.smooth_scroll = ss_raw if isinstance(ss_raw, bool) else str(ss_raw).lower() == "true"
        bmb = self.qsettings.value("show_bookmarks_bar", "true")
        self.show_bookmarks_bar = (bmb if isinstance(bmb, bool)
                                   else str(bmb).lower() == "true")

        self.ui_font = self.qsettings.value("ui_font", "Segoe UI") or "Segoe UI"
        self.translate_target = self.qsettings.value("translate_target", "ru")
        self.custom_colors = self._load_custom_colors()

        palette = self.get_effective_palette()
        self._close_icon, self._close_icon_hover = _generate_close_icons(
            self.current_theme, palette)
        self._search_icon_path = _generate_search_icon(self.current_theme, palette)
        self._icon_translate = _generate_translate_icon(self.current_theme, palette)
        self._icon_folder = _generate_folder_icon(self.current_theme, palette)
        (self._icon_back, self._icon_forward, self._icon_reload,
         self._icon_downloads, self._icon_menu) = _generate_nav_icons(
            self.current_theme, palette)
        self._icon_bookmark_outline = _generate_bookmark_icon(
            self.current_theme, palette, filled=False)
        self._icon_bookmark_filled = _generate_bookmark_icon(
            self.current_theme, palette, filled=True)

        self.passwords = PasswordStore()
        self.history = HistoryStore()
        self.bookmarks = BookmarkStore()
        self.downloads = []
        self._downloads_popup = None
        self._first_navigation_done = False
        self._settings_tab = None

        f = QFont(self.ui_font)
        try: f.setPointSize(10)
        except Exception: pass
        QApplication.instance().setFont(f)

        for name, seq, slot in [
            ("NewTab", "Ctrl+T", lambda: self.add_tab()),
            ("CloseTab", "Ctrl+W", self.close_current_tab),
            ("Settings", "Ctrl+,", lambda: self.open_settings()),
            ("Quit", "Ctrl+Q", self.close),
            ("SaveAs", "Ctrl+S", self.save_current_page),
            ("ZoomPlus1", "Ctrl++", self.zoom_in),
            ("ZoomPlus2", "Ctrl+=", self.zoom_in),
            ("ZoomPlus3", "Ctrl+Shift+=", self.zoom_in),
            ("ZoomMinus1", "Ctrl+-", self.zoom_out),
            ("ZoomMinus2", "Ctrl+Shift+-", self.zoom_out),
            ("Zoom0", "Ctrl+0", self.zoom_reset),
            ("Fullscreen", "F11", self.toggle_fullscreen_animated),
            ("NewWindow", "Ctrl+N", self.open_new_window),
            ("OpenDownloads", "Ctrl+J", self.open_downloads_folder),
            ("QuitAlt", "Ctrl+Shift+Q", self.close),
            ("SettingsTheme", "Ctrl+Shift+A", lambda: self.open_settings(SETTINGS_THEME)),
            ("SettingsHistory", "Ctrl+H", lambda: self.open_settings(SETTINGS_HISTORY)),
            ("SettingsPasswords", "Ctrl+P", lambda: self.open_settings(SETTINGS_PASSWORDS)),
            ("SettingsBookmarks", "Ctrl+Shift+O",
             lambda: self.open_settings(SETTINGS_BOOKMARKS)),
            ("BookmarkCurrent", "Ctrl+D", self.toggle_bookmark_current),
            ("ToggleBookmarksBar", "Ctrl+B",
             lambda: self.toggle_bookmarks_bar(None)),
            ("Find", "Ctrl+F", self.find_on_page),
            ("FindNext", "F3", self.find_next_page),
            ("Reload2", "F5", self.reload_current),
            ("Reload3", "Ctrl+R", self.reload_current),
            ("FocusUrl", "F6", self.focus_url_bar),
            ("FocusUrl2", "Ctrl+L", self.focus_url_bar),
            ("DevTools", "F12", self.open_devtools_current),
            ("DevTools2", "Ctrl+Shift+I", self.open_devtools_current),
            ("Escape", "Esc", self._on_escape),
        ]:
            act = QAction(name, self)
            act.setShortcut(QKeySequence(seq))
            act.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
            act.triggered.connect(slot)
            self.addAction(act)

        self.tab_bar = PlusTabBar()
        self.tabs = CustomTabWidget(self.tab_bar)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tab_bar.installEventFilter(self)

        self.title_bar = QWidget()
        self.title_bar.setObjectName("titleBar")
        self.title_bar.setFixedHeight(DENSITY_PRESETS[self.density]["title_bar_h"])
        self.title_bar.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self._title_bar_layout = QHBoxLayout(self.title_bar)
        self._title_bar_layout.setContentsMargins(8, 6, 0, 6)
        self._title_bar_layout.setSpacing(6)
        self._title_bar_layout.addWidget(self.tab_bar, 0, Qt.AlignmentFlag.AlignVCenter)

        self.plus_btn = QPushButton("+")
        self.plus_btn.setObjectName("newTabBtn")
        self.plus_btn.setFixedSize(28, 28)
        self.plus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.plus_btn.setToolTip("New tab (Ctrl+T)")
        self.plus_btn.clicked.connect(lambda: self.add_tab())
        self._title_bar_layout.addWidget(self.plus_btn, 0, Qt.AlignmentFlag.AlignVCenter)

        self.drag_area = DragArea(self)
        self._title_bar_layout.addWidget(self.drag_area, 1)

        self.btn_min = TitleBarButton("min", parent=self.title_bar)
        self.btn_max = TitleBarButton("max", parent=self.title_bar)
        self.btn_close = TitleBarButton("close", is_close=True, parent=self.title_bar)
        self.btn_min.clicked.connect(self.showMinimized)
        self.btn_max.clicked.connect(self.toggle_maximize)
        self.btn_close.clicked.connect(self.close)
        self._title_bar_layout.addWidget(self.btn_min)
        self._title_bar_layout.addWidget(self.btn_max)
        self._title_bar_layout.addWidget(self.btn_close)

        central = QWidget()
        central.setObjectName("centralWidget")
        self.central_layout = QVBoxLayout(central)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setSpacing(0)
        self.central_layout.addWidget(self.title_bar)
        self.central_layout.addWidget(self.tabs, 1)
        self.setCentralWidget(central)

        self._resize_handles = []
        for edge in ("tl", "t", "tr", "l", "r", "bl", "b", "br"):
            h = ResizeHandle(edge, self, self); h.show(); h.raise_()
            self._resize_handles.append((edge, h))

        self.apply_theme(self.current_theme)

        restored = False
        if self.restore_tabs:
            try:
                raw = self.qsettings.value("saved_tabs", "[]") or "[]"
                urls = json.loads(raw)
                for u in urls:
                    if isinstance(u, str) and u:
                        self.add_tab(u); restored = True
            except Exception: pass
        if not restored:
            self._open_initial_home()

        QTimer.singleShot(0, lambda: self.apply_density(self.density, save=False))

        if self.rtl_mode:
            QTimer.singleShot(50, lambda: self.apply_rtl(True, save=False))

        QApplication.instance().installEventFilter(self)
        QTimer.singleShot(0, self._update_tab_bar_width)

        self._fs_hover_timer = QTimer(self)
        self._fs_hover_timer.setInterval(120)
        self._fs_hover_timer.timeout.connect(self._check_fs_hover)

    def _load_custom_colors(self):
        raw = self.qsettings.value("custom_colors", "{}")
        try:
            d = json.loads(raw) if isinstance(raw, str) else {}
            return d if isinstance(d, dict) else {}
        except Exception:
            return {}

    def save_custom_colors(self):
        try:
            self.qsettings.setValue("custom_colors", json.dumps(self.custom_colors))
        except Exception: pass

    def get_effective_palette(self):
        return _effective_palette(self.current_theme, self.custom_colors)

    def get_live_wallpaper_mode(self):
        m = self.qsettings.value("live_wallpaper_mode", "none")
        return m if m in LIVE_WALLPAPER_MODES else "none"

    def get_live_wallpaper_speed(self):
        try: return float(self.qsettings.value("live_wallpaper_speed", 1.0))
        except Exception: return 1.0

    def set_live_wallpaper_mode(self, mode):
        if mode not in LIVE_WALLPAPER_MODES: mode = "none"
        self.qsettings.setValue("live_wallpaper_mode", mode)
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if hasattr(w, "refresh_new_tab_page"): w.refresh_new_tab_page()

    def set_live_wallpaper_speed(self, speed):
        try: speed = float(speed)
        except Exception: speed = 1.0
        self.qsettings.setValue("live_wallpaper_speed", speed)
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if hasattr(w, "refresh_new_tab_page"): w.refresh_new_tab_page()

    def showEvent(self, e):
        super().showEvent(e)
        QTimer.singleShot(0, self._layout_resize_handles)

    def _apply_resize(self, edge, sp, sg, cp):
        if self.isMaximized() or self.isFullScreen(): return
        dx = cp.x() - sp.x(); dy = cp.y() - sp.y()
        geo = QRect(sg); min_w = 500; min_h = 350
        if "l" in edge:
            nl = geo.left() + dx
            if geo.right() - nl >= min_w: geo.setLeft(nl)
        if "r" in edge:
            nr = geo.right() + dx
            if nr - geo.left() >= min_w: geo.setRight(nr)
        if "t" in edge:
            nt = geo.top() + dy
            if geo.bottom() - nt >= min_h: geo.setTop(nt)
        if "b" in edge:
            nb = geo.bottom() + dy
            if nb - geo.top() >= min_h: geo.setBottom(nb)
        self.setGeometry(geo)

    def _layout_resize_handles(self):
        if not hasattr(self, "_resize_handles"): return
        m = self.RESIZE_MARGIN; w = self.width(); h = self.height()
        show = not (self.isMaximized() or self.isFullScreen())
        for edge, hd in self._resize_handles:
            if not show:
                hd.hide(); continue
            hd.show()
            if edge == "tl": hd.setGeometry(0, 0, m, m)
            elif edge == "t": hd.setGeometry(m, 0, max(1, w - 2 * m), m)
            elif edge == "tr": hd.setGeometry(w - m, 0, m, m)
            elif edge == "l": hd.setGeometry(0, m, m, max(1, h - 2 * m))
            elif edge == "r": hd.setGeometry(w - m, m, m, max(1, h - 2 * m))
            elif edge == "bl": hd.setGeometry(0, h - m, m, m)
            elif edge == "b": hd.setGeometry(m, h - m, max(1, w - 2 * m), m)
            elif edge == "br": hd.setGeometry(w - m, h - m, m, m)
            hd.raise_()

    def changeEvent(self, e):
        super().changeEvent(e)
        if e.type() == QEvent.Type.WindowStateChange:
            self._refresh_max_btn()
            QTimer.singleShot(0, self._layout_resize_handles)

    def _open_initial_home(self):
        mode = self.qsettings.value("new_window_home", "home")
        if mode == "empty": self.add_tab(force_home="empty")
        elif mode in HOME_URLS: self.add_tab(HOME_URLS[mode])
        else: self.add_tab()

    def get_new_tab_color(self):
        c = self.qsettings.value("new_tab_color", "auto")
        if not c or c == "auto":
            return self.get_effective_palette()["bg"]
        if c in THEME_PALETTES:
            return THEME_PALETTES[c]["bg"]
        return c

    def get_new_tab_wallpaper(self):
        v = self.qsettings.value("new_tab_wallpaper", "")
        return str(v) if v else ""

    def set_new_tab_color(self, key):
        self.qsettings.setValue("new_tab_color", key)
        self.qsettings.setValue("new_tab_wallpaper", "")
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if hasattr(w, "refresh_new_tab_page"): w.refresh_new_tab_page()

    def set_new_tab_wallpaper(self, path):
        if path and os.path.exists(path):
            self.qsettings.setValue("new_tab_wallpaper", str(path))
        else:
            self.qsettings.setValue("new_tab_wallpaper", "")
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if hasattr(w, "refresh_new_tab_page"): w.refresh_new_tab_page()

    def set_wallpaper_from_url(self, url):
        try:
            from urllib.request import urlopen, Request
            cache = os.path.join(CACHE_DIR, "wallpapers")
            os.makedirs(cache, exist_ok=True)
            ext = ".jpg"
            for cand in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"):
                if cand in url.lower():
                    ext = cand; break
            name = f"wp_{abs(hash(url)) % 10**10}{ext}"
            path = os.path.join(cache, name)
            req = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(req, timeout=15) as r, open(path, "wb") as f:
                f.write(r.read())
            self.set_new_tab_wallpaper(path)
        except Exception as e:
            QMessageBox.warning(self, self.tr("ctx_set_wallpaper"),
                                f"Не удалось: {e}")

    def apply_hide_wallpaper_button(self, enabled):
        self.hide_wallpaper_button = bool(enabled)
        self.qsettings.setValue("hide_wallpaper_button",
                                "true" if enabled else "false")
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if hasattr(w, "refresh_new_tab_page"): w.refresh_new_tab_page()

    def toggle_bookmarks_bar(self, checked=None):
        if checked is None:
            checked = not self.show_bookmarks_bar
        self.show_bookmarks_bar = bool(checked)
        self.qsettings.setValue("show_bookmarks_bar",
                                "true" if checked else "false")
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if hasattr(w, "bookmarks_bar") and w.bookmarks_bar is not None:
                w.bookmarks_bar.setVisible(self.show_bookmarks_bar)

    def toggle_bookmark_current(self):
        t = self.current_browser_tab()
        if t:
            t._toggle_bookmark()

    def bookmark_changed(self):
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if hasattr(w, "bookmarks_bar") and w.bookmarks_bar is not None:
                try: w.bookmarks_bar._rebuild()
                except Exception: pass
        if self._settings_tab is not None:
            try: self._settings_tab.refresh_bookmarks()
            except Exception: pass
        t = self.current_browser_tab()
        if t:
            try: t._update_bookmark_icon()
            except Exception: pass

    def next_tab(self):
        n = self.tabs.count()
        if n == 0: return
        i = self.tabs.currentIndex()
        self.tabs.setCurrentIndex((i + 1) % n)

    def prev_tab(self):
        n = self.tabs.count()
        if n == 0: return
        i = self.tabs.currentIndex()
        self.tabs.setCurrentIndex((i - 1) % n)

    def apply_font(self, family, save=True):
        if not family: family = "Segoe UI"
        self.ui_font = family
        if save: self.qsettings.setValue("ui_font", family)
        try:
            app = QApplication.instance()
            if app is not None:
                cur = 10
                try:
                    cur = app.font().pointSize()
                    if cur <= 0: cur = 10
                except Exception: pass
                f = QFont(family)
                try: f.setPointSize(cur)
                except Exception: pass
                app.setFont(f)
                for w in app.allWidgets():
                    try: w.setFont(f)
                    except Exception: pass
        except Exception: pass
        QTimer.singleShot(0, lambda: _refresh_all_combo_views(
            self.current_theme, self.custom_colors))

    def apply_rtl(self, enabled, save=True):
        self.rtl_mode = bool(enabled)
        if save:
            self.qsettings.setValue("rtl_mode", "true" if enabled else "false")
        direction = (Qt.LayoutDirection.RightToLeft if enabled
                     else Qt.LayoutDirection.LeftToRight)
        try: self.setLayoutDirection(direction)
        except Exception: pass
        try:
            self.title_bar.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            self.tab_bar.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        except Exception: pass
        try: self.tab_bar.set_rtl(enabled)
        except Exception: pass
        self._reapply_tab_close_positions()
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            try: w.setLayoutDirection(direction)
            except Exception: pass
            if hasattr(w, "relayout"):
                try: w.relayout()
                except RuntimeError: pass
        QTimer.singleShot(0, self._update_tab_bar_width)

    def apply_smooth_scroll(self, enabled):
        self.smooth_scroll = bool(enabled)
        self.qsettings.setValue("smooth_scroll", "true" if enabled else "false")
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if hasattr(w, "apply_smooth_scroll"):
                w.apply_smooth_scroll(enabled)
        if self._settings_tab is not None:
            try: self._settings_tab.apply_smooth_scroll(enabled)
            except Exception: pass

    def _reapply_tab_close_positions(self):
        bar = self.tabs.tabBar()
        if bar is None: return
        rtl = self.rtl_mode
        desired = (QTabBar.ButtonPosition.LeftSide if rtl
                   else QTabBar.ButtonPosition.RightSide)
        for i in range(self.tabs.count()):
            wrapper = None
            for pos in (QTabBar.ButtonPosition.LeftSide,
                        QTabBar.ButtonPosition.RightSide):
                try: b = bar.tabButton(i, pos)
                except Exception: b = None
                if isinstance(b, TabCloseWrapper):
                    wrapper = b; break
            if wrapper is None: continue
            try: bar.setTabButton(i, QTabBar.ButtonPosition.LeftSide, None)
            except Exception: pass
            try: bar.setTabButton(i, QTabBar.ButtonPosition.RightSide, None)
            except Exception: pass
            try: wrapper.set_side(rtl)
            except Exception: pass
            try: bar.setTabButton(i, desired, wrapper)
            except Exception: pass
        bar.update()

    def _update_tab_bar_width(self):
        if not hasattr(self, "tab_bar"): return
        reserved = (self.plus_btn.width() +
                    self.btn_min.width() + self.btn_max.width() +
                    self.btn_close.width() + 40 + 30)
        try: self.tab_bar.setMaximumWidth(max(100, self.width() - reserved))
        except Exception: pass

    def apply_density(self, density, save=True):
        if density not in DENSITY_PRESETS: density = "auto"
        self.density = density
        if save: self.qsettings.setValue("density", density)
        preset = DENSITY_PRESETS[density]
        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(build_style(self.current_theme, density,
                                          self.custom_colors))
        if hasattr(self, "tab_bar") and self.tab_bar is not None:
            self.tab_bar.set_density(preset)
        if hasattr(self, "title_bar") and self.title_bar is not None:
            self.title_bar.setFixedHeight(preset["title_bar_h"])
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if hasattr(w, "relayout"):
                try: w.relayout()
                except RuntimeError: pass
        QTimer.singleShot(0, lambda: _refresh_all_combo_views(
            self.current_theme, self.custom_colors))
        QTimer.singleShot(0, self._update_tab_bar_width)

    def apply_layout(self, position):
        self.layout_position = position
        self.qsettings.setValue("layout_position", position)
        if hasattr(self, "central_layout"):
            while self.central_layout.count():
                self.central_layout.takeAt(0)
            if position == "bottom":
                self.central_layout.addWidget(self.tabs, 1)
                self.central_layout.addWidget(self.title_bar)
            else:
                self.central_layout.addWidget(self.title_bar)
                self.central_layout.addWidget(self.tabs, 1)
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if hasattr(w, "relayout"):
                try: w.relayout()
                except RuntimeError: pass
        QTimer.singleShot(0, self._layout_resize_handles)
        self.update()

    def toggle_maximize(self):
        if self.isMaximized(): self.showNormal()
        else: self.showMaximized()
        self._refresh_max_btn()

    def _refresh_max_btn(self):
        color = QColor(self.get_effective_palette()["text"])
        if self.isMaximized(): self.btn_max.set_kind("restore")
        else: self.btn_max.set_kind("max")
        self.btn_max.set_icon_color(color)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._update_tab_bar_width()
        self._layout_resize_handles()

    def tr(self, key, **kw):
        lang = LANG.get(self.language, LANG["ru"])
        text = lang.get(key, key)
        if kw: text = text.format(**kw)
        return text

    def apply_language(self, code):
        self.language = code
        self.qsettings.setValue("language", code)
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if hasattr(w, "retranslate"): w.retranslate()
            if hasattr(w, "tab_title"): self.tabs.setTabText(i, w.tab_title())
        QTimer.singleShot(0, self.tabs.tabBar().update)

    def eventFilter(self, obj, event):
        try:
            if event.type() == QEvent.Type.KeyPress:
                if event.key() == Qt.Key.Key_Tab and (
                        event.modifiers() & Qt.KeyboardModifier.ControlModifier):
                    if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                        self.prev_tab()
                    else:
                        self.next_tab()
                    return True
        except Exception:
            pass
        if obj is self.tabs.tabBar() and event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.MiddleButton:
                idx = self.tabs.tabBar().tabAt(event.pos())
                if idx != -1:
                    self.close_tab(idx); return True
        return super().eventFilter(obj, event)

    def toggle_fullscreen_animated(self):
        going = not self.isFullScreen()
        fo = QPropertyAnimation(self, b"windowOpacity", self)
        fo.setDuration(140); fo.setStartValue(1.0); fo.setEndValue(0.0)
        fo.setEasingCurve(QEasingCurve.Type.InCubic)

        def mid():
            if going:
                self._was_maximized_before_fs = self.isMaximized()
                self._set_chrome_visible(False)
                self.showFullScreen()
                self._fs_hover_timer.start()
            else:
                self._fs_hover_timer.stop()
                if self._was_maximized_before_fs: self.showMaximized()
                else: self.showNormal()
                self._set_chrome_visible(True)
            QTimer.singleShot(0, self._layout_resize_handles)
            fi = QPropertyAnimation(self, b"windowOpacity", self)
            fi.setDuration(200); fi.setStartValue(0.0); fi.setEndValue(1.0)
            fi.setEasingCurve(QEasingCurve.Type.OutCubic)
            fi.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            self._fs_anim_in = fi

        fo.finished.connect(mid)
        fo.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        self._fs_anim_out = fo

    def _set_chrome_visible(self, v):
        try: self.title_bar.setVisible(v)
        except Exception: pass
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if hasattr(w, "nav_widget"):
                try: w.nav_widget.setVisible(v)
                except Exception: pass
            if hasattr(w, "bookmarks_bar") and w.bookmarks_bar is not None:
                try: w.bookmarks_bar.setVisible(v and self.show_bookmarks_bar)
                except Exception: pass

    def _check_fs_hover(self):
        if not self.isFullScreen(): self._fs_hover_timer.stop(); return
        c = QCursor.pos()
        s = QApplication.primaryScreen().availableGeometry()
        if c.y() <= s.top() + 5:
            if not self.title_bar.isVisible(): self._set_chrome_visible(True)
        else:
            if self.title_bar.isVisible() and c.y() > s.top() + 80:
                self._set_chrome_visible(False)

    def current_browser_tab(self):
        w = self.tabs.currentWidget()
        if hasattr(w, "browser"): return w
        return None

    def find_on_page(self):
        t = self.current_browser_tab()
        if t: t.open_find_bar()

    def find_next_page(self):
        t = self.current_browser_tab()
        if t: t.open_find_bar(); t._find_next()

    def reload_current(self):
        t = self.current_browser_tab()
        if t: t.browser.reload()

    def focus_url_bar(self):
        t = self.current_browser_tab()
        if t: t.input_url.setFocus(); t.input_url.selectAll()

    def open_devtools_current(self):
        t = self.current_browser_tab()
        if t: t.toggle_devtools()

    def save_current_page(self):
        t = self.current_browser_tab()
        if t:
            try:
                t.browser.page().triggerAction(QWebEnginePage.WebAction.SavePage)
            except Exception: pass

    def _on_escape(self):
        t = self.current_browser_tab()
        if t and hasattr(t, "find_bar_wrapper") and t.find_bar_wrapper.isVisible():
            t._hide_find_bar()

    def schedule_tab_load(self, tab, delay):
        QTimer.singleShot(delay, tab.load_start_page)

    def add_tab(self, url=None, force_home=None):
        if not isinstance(url, str): url = None
        empty_mode = False
        if url is None:
            mode = force_home if force_home is not None else self.qsettings.value(
                "new_tab_home", "home")
            if mode == "empty": empty_mode = True
            elif mode in HOME_URLS: url = HOME_URLS[mode]
        tab = BrowserTab(self, url, empty_mode=empty_mode)
        tab.browser.setZoomFactor(self.current_zoom)
        self._apply_text_zoom_to_view(tab.browser, self.current_text_zoom)
        idx = self.tabs.addTab(tab, self.tr("new_tab_title"))
        wrapper = TabCloseWrapper(self._close_icon, self._close_icon_hover, right_margin=6)
        wrapper.set_side(self.rtl_mode)
        wrapper.btn.clicked.connect(
            lambda c=False, w=tab: self._close_tab_widget(w))
        pos = (QTabBar.ButtonPosition.LeftSide if self.rtl_mode
               else QTabBar.ButtonPosition.RightSide)
        self.tabs.tabBar().setTabButton(idx, pos, wrapper)
        self.tabs.setCurrentIndex(idx)
        tab.input_url.setFocus()
        active = [d for d in self.downloads if not d.get("finished", False)]
        if active and hasattr(tab, "set_download_state"):
            tab.set_download_state(active[-1].get("progress", 0.0), True)
        if url is not None:
            if not self._first_navigation_done:
                self.schedule_tab_load(tab, 900); self._first_navigation_done = True
            else:
                self.schedule_tab_load(tab, 150)
        QTimer.singleShot(0, self._update_tab_bar_width)

    def open_url_in_new_window(self, url):
        try:
            win = FlexionBrowser()
            win.showMaximized()
            QTimer.singleShot(400, lambda: win.add_tab(url))
            app = QApplication.instance()
            if not hasattr(app, "_extra_windows"):
                app._extra_windows = []
            app._extra_windows.append(win)
        except Exception:
            self.add_tab(url)

    def open_in_split(self, url):
        try:
            tab = BrowserTab(self, None, empty_mode=True)
            tab.browser.setZoomFactor(self.current_zoom)
            self._apply_text_zoom_to_view(tab.browser, self.current_text_zoom)

            second = BrowserView(self)
            s = second.settings()
            s.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled,
                          bool(self.smooth_scroll))
            s.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
            s.setAttribute(QWebEngineSettings.WebAttribute.DnsPrefetchEnabled, True)
            second.setUrl(QUrl(url))

            old_outer = tab.layout()
            if old_outer is not None:
                while old_outer.count():
                    old_outer.takeAt(0)
                QWidget().setLayout(old_outer)

            outer = QVBoxLayout(tab)
            outer.setContentsMargins(0, 0, 0, 0)
            outer.setSpacing(0)
            outer.addWidget(tab.nav_widget, 0)
            outer.addWidget(tab.bookmarks_bar, 0)

            splitter = QSplitter(Qt.Orientation.Horizontal)
            splitter.setStyleSheet(
                f"QSplitter::handle {{ background: {self.get_effective_palette()['border']}; }}")
            splitter.addWidget(tab.browser)
            splitter.addWidget(second)
            splitter.setSizes([800, 800])
            outer.addWidget(splitter, 1)

            idx = self.tabs.addTab(tab, self.tr("split_title"))
            wrapper = TabCloseWrapper(self._close_icon, self._close_icon_hover, right_margin=6)
            wrapper.set_side(self.rtl_mode)
            wrapper.btn.clicked.connect(
                lambda c=False, w=tab: self._close_tab_widget(w))
            pos = (QTabBar.ButtonPosition.LeftSide if self.rtl_mode
                   else QTabBar.ButtonPosition.RightSide)
            self.tabs.tabBar().setTabButton(idx, pos, wrapper)
            self.tabs.setCurrentIndex(idx)
        except Exception:
            self.add_tab(url)

    def _close_tab_widget(self, widget):
        idx = self.tabs.indexOf(widget)
        if idx != -1: self.close_tab(idx)

    def close_tab(self, idx):
        widget = self.tabs.widget(idx)
        if widget is None: return
        bar = self.tabs.tabBar()
        if isinstance(bar, PlusTabBar):
            try:
                pix, rect = bar.grab_tab_pixmap(idx)
                if pix is not None and not pix.isNull() and not rect.isEmpty():
                    pos = bar.mapTo(self, rect.topLeft())
                    glow = QColor("#ef4444") if self.close_glow_effect else None
                    ov = TabAnimOverlay(pix, appear=False, glow_color=glow, parent=self)
                    ov.move(pos); ov.start()
            except Exception: pass
        self._do_close_tab(widget)

    def _do_close_tab(self, widget):
        idx = self.tabs.indexOf(widget)
        if idx == -1: return
        self.tabs.removeTab(idx)
        if widget is self._settings_tab: self._settings_tab = None
        widget.deleteLater()
        if self.tabs.count() == 0: self.add_tab()
        else:
            QTimer.singleShot(0, self.tabs.tabBar().update)
            QTimer.singleShot(0, self._update_tab_bar_width)

    def close_current_tab(self): self.close_tab(self.tabs.currentIndex())

    def zoom_in(self):
        t = self.current_browser_tab()
        if t:
            v = round(min(t.browser.zoomFactor() + 0.1, 3.0), 2)
            t.browser.setZoomFactor(v); self.current_zoom = v
            self.qsettings.setValue("zoom", v)

    def zoom_out(self):
        t = self.current_browser_tab()
        if t:
            v = round(max(t.browser.zoomFactor() - 0.1, 0.25), 2)
            t.browser.setZoomFactor(v); self.current_zoom = v
            self.qsettings.setValue("zoom", v)

    def zoom_reset(self):
        t = self.current_browser_tab()
        if t:
            t.zoom_reset(); self.current_zoom = 1.0
            self.qsettings.setValue("zoom", 1.0)

    def _refresh_settings_tab_icon(self, idx=None):
        try:
            palette = self.get_effective_palette()
            gear_pix = _make_gear_icon_pixmap(QColor(palette["text2"]), 16)
            gear_icon = QIcon(gear_pix)
            if idx is not None and 0 <= idx < self.tabs.count():
                self.tabs.tabBar().setTabData(idx, gear_icon)
            else:
                for i in range(self.tabs.count()):
                    w = self.tabs.widget(i)
                    if getattr(w, 'is_settings_tab', False):
                        self.tabs.tabBar().setTabData(i, gear_icon)
            self.tabs.tabBar().update()
        except Exception:
            pass

    def open_settings(self, page_index=None):
        if self._settings_tab is not None:
            idx = self.tabs.indexOf(self._settings_tab)
            if idx != -1:
                self.tabs.setCurrentIndex(idx)
                if page_index is not None: self._settings_tab.show_page(page_index)
                return
        self._settings_tab = SettingsTab(self)
        idx = self.tabs.addTab(self._settings_tab, self.tr("settings_tab_title"))
        wrapper = TabCloseWrapper(self._close_icon, self._close_icon_hover, right_margin=6)
        wrapper.set_side(self.rtl_mode)
        wrapper.btn.clicked.connect(
            lambda c=False, w=self._settings_tab: self._close_tab_widget(w))
        pos = (QTabBar.ButtonPosition.LeftSide if self.rtl_mode
               else QTabBar.ButtonPosition.RightSide)
        self.tabs.tabBar().setTabButton(idx, pos, wrapper)
        self.tabs.setCurrentIndex(idx)
        # Add gear icon to settings tab
        try:
            palette = self.get_effective_palette()
            gear_pix = _make_gear_icon_pixmap(QColor(palette["text2"]), 16)
            self.tabs.tabBar().setTabData(idx, QIcon(gear_pix))
        except Exception:
            pass
        if page_index is not None: self._settings_tab.show_page(page_index)
        QTimer.singleShot(0, self._update_tab_bar_width)

    def refresh_password_settings(self):
        if self._settings_tab is not None:
            self._settings_tab.refresh_passwords()

    def apply_dark_mode(self, enabled):
        self.dark_mode = enabled
        self.qsettings.setValue("dark_mode", "true" if enabled else "false")
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if hasattr(w, "update_dark_mode"): w.update_dark_mode()

    def translate_page(self, url, src, dst):
        tr_url = (f"https://translate.google.com/translate?hl={dst}"
                  f"&sl={src}&tl={dst}&u={quote(url, safe='')}")
        self.add_tab(tr_url)

    def apply_theme(self, theme, save=True):
        if theme not in THEME_PALETTES: theme = "dark"
        self.current_theme = theme
        if save: self.qsettings.setValue("theme", theme)
        try:
            QPixmapCache.clear()
        except Exception:
            pass
        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet("")
            app.setStyleSheet(build_style(theme, self.density, self.custom_colors))
        palette = self.get_effective_palette()
        self._close_icon, self._close_icon_hover = _generate_close_icons(theme, palette)
        self._search_icon_path = _generate_search_icon(theme, palette)
        self._icon_translate = _generate_translate_icon(theme, palette)
        self._icon_folder = _generate_folder_icon(theme, palette)
        (self._icon_back, self._icon_forward, self._icon_reload,
         self._icon_downloads, self._icon_menu) = _generate_nav_icons(theme, palette)
        self._icon_bookmark_outline = _generate_bookmark_icon(theme, palette, filled=False)
        self._icon_bookmark_filled = _generate_bookmark_icon(theme, palette, filled=True)
        if hasattr(self, "tabs") and self.tabs is not None:
            bar = self.tabs.tabBar()
            if isinstance(bar, PlusTabBar):
                bar.set_theme(theme, self.custom_colors)
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if hasattr(w, "update_theme_icons"): w.update_theme_icons()
            if hasattr(w, "refresh_new_tab_page"): w.refresh_new_tab_page()
            if hasattr(w, "bookmarks_bar") and w.bookmarks_bar is not None:
                try: w.bookmarks_bar._rebuild()
                except Exception: pass
            for pos in (QTabBar.ButtonPosition.RightSide,
                        QTabBar.ButtonPosition.LeftSide):
                wrapper = self.tabs.tabBar().tabButton(i, pos)
                if isinstance(wrapper, TabCloseWrapper):
                    wrapper.btn.update_theme(self._close_icon, self._close_icon_hover)
                    break
        c = QColor(palette["text"])
        self.btn_min.set_icon_color(c); self.btn_max.set_icon_color(c)
        self.btn_close.set_icon_color(c)
        self._refresh_max_btn()
        # Update gear icon for settings tab
        self._refresh_settings_tab_icon()
        QTimer.singleShot(0, lambda t=theme: _refresh_all_combo_views(
            t, self.custom_colors))
        QTimer.singleShot(0, self.tabs.tabBar().update)
        QTimer.singleShot(0, self._update_tab_bar_width)
        # Rebuild settings tab to refresh all inline styles
        if self._settings_tab is not None:
            QTimer.singleShot(0, self._settings_tab.rebuild_preserving_page)

    def apply_zoom(self, zoom):
        self.current_zoom = zoom; self.qsettings.setValue("zoom", zoom)
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if hasattr(w, "browser"): w.browser.setZoomFactor(zoom)

    def apply_text_zoom(self, factor):
        self.current_text_zoom = factor
        self.qsettings.setValue("text_zoom", factor)
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if hasattr(w, "browser"):
                self._apply_text_zoom_to_view(w.browser, factor)
                if w.browser.url().toString() not in ("", "about:blank"):
                    w.browser.reload()

    @staticmethod
    def _apply_text_zoom_to_view(view, factor):
        s = view.settings()
        s.setFontSize(QWebEngineSettings.FontSize.DefaultFontSize,
                      max(6, int(16 * factor)))
        s.setFontSize(QWebEngineSettings.FontSize.DefaultFixedFontSize,
                      max(6, int(13 * factor)))

    def set_search_engine(self, name):
        if name not in SEARCH_ENGINES: name = "DuckDuckGo"
        self.search_engine_name = name
        self.search_engine_template = SEARCH_ENGINES.get(
            name, SEARCH_ENGINES["DuckDuckGo"])["search"]
        self.qsettings.setValue("search_engine", name)

    def get_homepage(self):
        return SEARCH_ENGINES.get(self.search_engine_name,
                                  SEARCH_ENGINES["DuckDuckGo"])["home"]

    def set_download_path(self, path):
        self.download_path = path; self.qsettings.setValue("download_path", path)

    def open_new_window(self):
        win = FlexionBrowser(); win.showMaximized()
        app = QApplication.instance()
        if not hasattr(app, "_extra_windows"): app._extra_windows = []
        app._extra_windows.append(win)

    def open_downloads_folder(self):
        try:
            os.makedirs(self.download_path, exist_ok=True)
            os.startfile(self.download_path)
        except Exception: pass

    def on_download_requested(self, download):
        os.makedirs(self.download_path, exist_ok=True)
        suggested = download.downloadFileName() or "download"
        if "." not in suggested:
            ext = self._guess_extension(download)
            if ext: suggested = f"{suggested}.{ext}"
        target = os.path.join(self.download_path, suggested)
        target = self._unique_path(target)
        download.setDownloadDirectory(self.download_path)
        download.setDownloadFileName(os.path.basename(target))
        download.accept()
        entry = {"name": os.path.basename(target), "path": target, "status": "0%",
                 "total": 0, "received": 0, "progress": 0.0, "finished": False}
        self.downloads.append(entry)
        self._update_downloads_indicator()

        toast = DownloadToast(self, entry["name"], parent=self)
        toast.show_toast()
        entry["_toast"] = toast

        def on_prog():
            total = download.totalBytes(); rec = download.receivedBytes()
            entry["total"] = total; entry["received"] = rec
            if total > 0:
                pct = rec * 100.0 / total
                entry["progress"] = min(1.0, pct / 100.0)
                entry["status"] = f"{pct:.0f}%  ·  {_fmt_size(rec)} / {_fmt_size(total)}"
            else:
                entry["status"] = _fmt_size(rec)
            t = entry.get("_toast")
            if t is not None:
                try: t.set_progress(entry["progress"], entry["status"])
                except Exception: pass
            self._update_downloads_indicator()
            if self._downloads_popup is not None:
                self._downloads_popup.refresh_downloads()

        def on_fin():
            entry["finished"] = True; entry["progress"] = 1.0
            entry["status"] = self.tr("status_done")
            t = entry.get("_toast")
            if t is not None:
                try:
                    t.set_progress(1.0, self.tr("status_done"))
                    QTimer.singleShot(1500, t.fade_out_and_close)
                except Exception: pass
            self._update_downloads_indicator()
            if all(d.get("finished", False) for d in self.downloads):
                self._flash_downloads_done()
            if self._downloads_popup is not None:
                self._downloads_popup.refresh_downloads()

        download.receivedBytesChanged.connect(on_prog)
        download.isFinishedChanged.connect(on_fin)

    def _update_downloads_indicator(self):
        active = [d for d in self.downloads if not d.get("finished", False)]
        if active:
            latest = active[-1]
            progress = float(latest.get("progress", 0.0)); dl = True
        else:
            progress = 1.0 if self.downloads else 0.0; dl = False
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if hasattr(w, "set_download_state"):
                w.set_download_state(progress, dl)

    def _flash_downloads_done(self):
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if hasattr(w, "flash_download_done"): w.flash_download_done()

    @staticmethod
    def _guess_extension(download):
        up = download.url().path()
        if "." in up:
            e = up.rsplit(".", 1)[-1].lower()
            if 1 <= len(e) <= 5 and e.isalnum(): return e
        try: mime = (download.mimeType() or "").lower()
        except AttributeError: mime = ""
        M = {"image/png": "png", "image/jpeg": "jpg", "image/jpg": "jpg",
             "image/gif": "gif", "image/webp": "webp", "image/bmp": "bmp",
             "image/svg+xml": "svg", "image/x-icon": "ico", "image/avif": "avif",
             "video/mp4": "mp4", "video/webm": "webm", "video/x-matroska": "mkv",
             "audio/mpeg": "mp3", "audio/ogg": "ogg", "audio/wav": "wav",
             "audio/flac": "flac", "application/pdf": "pdf",
             "application/zip": "zip", "application/x-rar-compressed": "rar",
             "application/x-7z-compressed": "7z", "text/plain": "txt",
             "text/html": "html", "application/json": "json",
             "application/javascript": "js", "text/css": "css"}
        for m, e in M.items():
            if mime.startswith(m): return e
        return None

    @staticmethod
    def _unique_path(path):
        if not os.path.exists(path): return path
        base, ext = os.path.splitext(path); i = 1
        while os.path.exists(f"{base} ({i}){ext}"): i += 1
        return f"{base} ({i}){ext}"

    def closeEvent(self, e):
        try:
            if self.restore_tabs:
                urls = []
                for i in range(self.tabs.count()):
                    w = self.tabs.widget(i)
                    if hasattr(w, "browser") and not getattr(w, "is_settings_tab", False):
                        u = w.browser.url().toString()
                        if u and u not in ("about:blank",) and not u.startswith("chrome://"):
                            urls.append(u)
                self.qsettings.setValue("saved_tabs", json.dumps(urls))
            else:
                self.qsettings.setValue("saved_tabs", "[]")
        except Exception: pass
        super().closeEvent(e)


def is_autostart_enabled():
    if winreg is None: return False
    try:
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                           r"Software\Microsoft\Windows\CurrentVersion\Run",
                           0, winreg.KEY_READ)
        try:
            winreg.QueryValueEx(k, APP_KEY); return True
        except FileNotFoundError:
            return False
        finally: winreg.CloseKey(k)
    except FileNotFoundError: return False
    except Exception: return False


def set_autostart(enabled):
    if winreg is None: return False
    try:
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                           r"Software\Microsoft\Windows\CurrentVersion\Run",
                           0, winreg.KEY_SET_VALUE)
        if enabled:
            px = sys.executable
            pw = px.replace("python.exe", "pythonw.exe")
            if not os.path.exists(pw): pw = px
            script = os.path.abspath(sys.argv[0])
            winreg.SetValueEx(k, APP_KEY, 0, winreg.REG_SZ,
                              f'"{pw}" "{script}"')
        else:
            try: winreg.DeleteValue(k, APP_KEY)
            except FileNotFoundError: pass
        winreg.CloseKey(k); return True
    except Exception: return False


if __name__ == "__main__":
    import ctypes
    
    try:
        myappid = 'flexion.browser.1.0' 
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    QApplication.setOrganizationName(APP_KEY)
    QApplication.setApplicationName(APP_KEY)
    app = QApplication(sys.argv)

    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    icon_file = resource_path("icon_browser.ico")
    if os.path.exists(icon_file):
        app.setWindowIcon(QIcon(icon_file))

    profile = QWebEngineProfile.defaultProfile()
    profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
    profile.setPersistentCookiesPolicy(
        QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
    profile.setCachePath(os.path.join(CACHE_DIR, "cache"))
    profile.setPersistentStoragePath(os.path.join(CACHE_DIR, "storage"))
    profile.setHttpUserAgent(USER_AGENT)
    adblock = AdBlock(profile)
    profile.setUrlRequestInterceptor(adblock)
    
    window = FlexionBrowser()
    
    if os.path.exists(icon_file):
        window.setWindowIcon(QIcon(icon_file))

    profile.downloadRequested.connect(window.on_download_requested)
    window.showMaximized()
    sys.exit(app.exec())
"""Theme definitions and runtime theme switching."""
import logging
from PyQt6.QtWidgets import QApplication

logger = logging.getLogger(__name__)

# ── Palette definitions ────────────────────────────────────────────────────── #

_PALETTES = {
    "deep_navy": dict(
        label="Deep Navy / Crimson",
        swatch="#e94560",
        bg="#1a1a2e",        surface="#16213e",    border="#0f3460",
        accent="#e94560",    accent_hover="#c73652", accent_press="#a52a40",
        text="#e0e0e0",      text_dim="#8899bb",
        panel_bg="#12122a",  panel_header="#0f0f24",
        secondary_bg="#0f3460",
        tab_unsel="#0f3460", tab_unsel_text="#a0a0a0", tab_hover="#1a5276",
        header_bg="#0f3460",
        rec_bg="#1b4a2a",   rec_fg="#80ffb0",  rec_border="#2a7a40", rec_hover="#256038",
        stp_bg="#4a1b1b",   stp_fg="#ffaaaa",  stp_border="#7a2a2a", stp_hover="#602525",
        fin_bg="#1b6b3a",   fin_fg="#a0f0b0",  fin_hover="#228b4a",
    ),
    "obsidian": dict(
        label="Obsidian / Violet",
        swatch="#7c4dff",
        bg="#0f0f17",        surface="#1a1828",    border="#2d2050",
        accent="#7c4dff",    accent_hover="#6535e0", accent_press="#4e22b5",
        text="#e8e0ff",      text_dim="#9988cc",
        panel_bg="#0a0a12",  panel_header="#0c0c18",
        secondary_bg="#2d2050",
        tab_unsel="#2d2050", tab_unsel_text="#9988cc", tab_hover="#3d2e6a",
        header_bg="#2d2050",
        rec_bg="#2a1f4a",   rec_fg="#b39ddb",  rec_border="#5c3d9e", rec_hover="#3d2e6a",
        stp_bg="#4a1f2a",   stp_fg="#ff8a80",  stp_border="#8a2040", stp_hover="#6a2535",
        fin_bg="#1a2f4a",   fin_fg="#80d8ff",  fin_hover="#1e4068",
    ),
    "slate_cyan": dict(
        label="Slate / Cyan",
        swatch="#00b4d8",
        bg="#0d1821",        surface="#1b2838",    border="#1e3a5f",
        accent="#00b4d8",    accent_hover="#0096c7", accent_press="#0077b6",
        text="#caf0f8",      text_dim="#6699aa",
        panel_bg="#0a1520",  panel_header="#0b1825",
        secondary_bg="#1e3a5f",
        tab_unsel="#1e3a5f", tab_unsel_text="#6699aa", tab_hover="#2a5280",
        header_bg="#1e3a5f",
        rec_bg="#003a4a",   rec_fg="#90e0ef",  rec_border="#006a8a", rec_hover="#005070",
        stp_bg="#4a1b1b",   stp_fg="#ff8a80",  stp_border="#7a2a2a", stp_hover="#602525",
        fin_bg="#003a30",   fin_fg="#80ffee",  fin_hover="#005045",
    ),
}

THEME_KEYS  = list(_PALETTES.keys())
THEME_NAMES = {k: v["label"] for k, v in _PALETTES.items()}


# ── QSS generator ─────────────────────────────────────────────────────────── #

def _build_qss(p: dict) -> str:
    return f"""
/* ── Recording panel ─── */
QWidget#recording_panel {{
    background-color: {p['panel_bg']};
    border-right: 1px solid {p['border']};
}}
QWidget#recording_header {{
    background-color: {p['panel_header']};
    border-bottom: 1px solid {p['border']};
}}
QLabel#status_detail {{
    color: {p['text_dim']};
    font-size: 12px;
    padding: 2px 0;
}}

/* ── Record / Stop buttons ─── */
QPushButton#btn_record {{
    background-color: {p['rec_bg']};
    color: {p['rec_fg']};
    border: 1px solid {p['rec_border']};
    padding: 10px 14px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 13px;
    text-align: left;
    min-height: 38px;
}}
QPushButton#btn_record:hover {{ background-color: {p['rec_hover']}; }}
QPushButton#btn_stop {{
    background-color: {p['stp_bg']};
    color: {p['stp_fg']};
    border: 1px solid {p['stp_border']};
    padding: 10px 14px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 13px;
    text-align: left;
    min-height: 38px;
}}
QPushButton#btn_stop:hover {{ background-color: {p['stp_hover']}; }}

/* ── Global ─── */
QMainWindow, QWidget {{
    background-color: {p['bg']};
    color: {p['text']};
    font-family: "Segoe UI", sans-serif;
    font-size: 14px;
}}

/* ── Labels ─── */
QLabel#screen_title {{
    font-size: 24px;
    font-weight: bold;
    color: {p['accent']};
    padding-bottom: 8px;
}}
QLabel#subject_label {{
    font-size: 15px;
    color: {p['accent']};
    font-weight: bold;
}}
QLabel#state_label {{
    color: {p['accent']};
    font-weight: bold;
    font-size: 15px;
}}
QLabel#elapsed_label {{
    font-size: 22px;
    font-weight: bold;
    color: {p['text']};
    font-family: monospace;
    min-width: 70px;
}}
QLabel#error_label {{
    color: #ff6b6b;
    font-size: 13px;
    padding: 2px 0;
}}

/* ── Cards ─── */
QWidget#login_card {{
    background-color: {p['surface']};
    border: 1px solid {p['border']};
    border-radius: 8px;
}}

/* ── Buttons ─── */
QPushButton#btn_primary {{
    background-color: {p['accent']};
    color: white;
    border: none;
    padding: 10px 24px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 14px;
    min-height: 36px;
}}
QPushButton#btn_primary:hover   {{ background-color: {p['accent_hover']}; }}
QPushButton#btn_primary:pressed {{ background-color: {p['accent_press']}; }}

QPushButton#btn_secondary {{
    background-color: {p['secondary_bg']};
    color: {p['text']};
    border: 1px solid {p['border']};
    padding: 10px 24px;
    border-radius: 4px;
    font-size: 14px;
    min-height: 36px;
}}
QPushButton#btn_secondary:hover {{ background-color: {p['tab_hover']}; }}

QPushButton#btn_danger {{
    background-color: #6b2737;
    color: #f0a0a0;
    border: none;
    padding: 8px 20px;
    border-radius: 4px;
    font-size: 14px;
    min-height: 34px;
}}
QPushButton#btn_danger:hover {{ background-color: #8b3748; }}

QPushButton#btn_finish {{
    background-color: {p['fin_bg']};
    color: {p['fin_fg']};
    border: none;
    padding: 10px 24px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 14px;
    min-height: 38px;
}}
QPushButton#btn_finish:hover {{ background-color: {p['fin_hover']}; }}

QPushButton {{
    background-color: {p['surface']};
    color: {p['text']};
    border: 1px solid {p['border']};
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 13px;
    min-height: 32px;
}}
QPushButton:hover {{
    background-color: {p['tab_hover']};
    color: {p['text']};
}}
QPushButton:disabled {{
    background-color: {p['bg']};
    color: #555555;
    border-color: #333333;
}}

/* ── Inputs ─── */
QLineEdit, QTextEdit, QSpinBox {{
    background-color: {p['surface']};
    color: {p['text']};
    border: 1px solid {p['border']};
    border-radius: 4px;
    padding: 7px;
    font-size: 14px;
    selection-background-color: {p['accent']};
}}
QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {{
    border-color: {p['accent']};
}}

/* ── Tables ─── */
QTableWidget {{
    background-color: {p['surface']};
    alternate-background-color: {p['bg']};
    gridline-color: {p['border']};
    border: 1px solid {p['border']};
    border-radius: 4px;
    font-size: 13px;
}}
QTableWidget::item:selected {{
    background-color: {p['accent']};
    color: white;
}}
QHeaderView::section {{
    background-color: {p['header_bg']};
    color: {p['text']};
    padding: 8px;
    border: none;
    font-weight: bold;
    font-size: 13px;
}}

/* ── List ─── */
QListWidget {{
    background-color: {p['surface']};
    border: 1px solid {p['border']};
    border-radius: 4px;
    font-size: 14px;
}}
QListWidget::item {{ padding: 8px; }}
QListWidget::item:selected {{ background-color: {p['accent']}; color: white; }}
QListWidget::item:hover {{ background-color: {p['tab_hover']}; }}

/* ── Tabs ─── */
QTabWidget::pane {{
    border: 1px solid {p['border']};
    background-color: {p['bg']};
    padding: 8px;
}}
QTabBar::tab {{
    background-color: {p['tab_unsel']};
    color: {p['tab_unsel_text']};
    padding: 10px 24px;
    border-radius: 4px 4px 0 0;
    margin-right: 2px;
    font-size: 14px;
    min-width: 80px;
}}
QTabBar::tab:selected {{ background-color: {p['accent']}; color: white; }}
QTabBar::tab:hover:!selected {{
    background-color: {p['tab_hover']};
    color: {p['text']};
}}

/* ── Combo ─── */
QComboBox {{
    background-color: {p['surface']};
    color: {p['text']};
    border: 1px solid {p['border']};
    border-radius: 4px;
    padding: 7px;
    font-size: 14px;
    min-height: 32px;
}}
QComboBox::drop-down {{ border: none; }}
QComboBox QAbstractItemView {{
    background-color: {p['surface']};
    color: {p['text']};
    selection-background-color: {p['accent']};
    font-size: 14px;
}}

/* ── Scrollbar ─── */
QScrollBar:vertical {{
    background-color: {p['surface']};
    width: 10px;
}}
QScrollBar::handle:vertical {{
    background-color: {p['border']};
    border-radius: 4px;
}}
QScrollBar::handle:vertical:hover {{ background-color: {p['tab_hover']}; }}

/* ── Message boxes ─── */
QMessageBox {{
    background-color: {p['bg']};
    color: {p['text']};
    font-size: 14px;
}}

/* ── Radio buttons ─── */
QRadioButton {{
    color: {p['text']};
    font-size: 14px;
    spacing: 7px;
}}
QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border-radius: 8px;
    border: 2px solid {p['border']};
    background-color: {p['surface']};
}}
QRadioButton::indicator:hover {{
    border-color: {p['accent']};
}}
QRadioButton::indicator:checked {{
    background-color: {p['accent']};
    border-color: {p['accent']};
}}
"""


# ── Persistence (stored in the settings table) ─────────────────────────────── #

def load_theme() -> str:
    """Return the saved theme key, defaulting to 'deep_navy'."""
    try:
        from app.database.connection import get_connection
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT value FROM settings WHERE key='theme'"
            ).fetchone()
            if row and row["value"] in _PALETTES:
                return row["value"]
        finally:
            conn.close()
    except Exception as exc:
        logger.warning("Could not load theme setting: %s", exc)
    return "deep_navy"


def save_theme(key: str) -> None:
    """Persist the chosen theme key to the settings table."""
    if key not in _PALETTES:
        return
    try:
        from app.database.connection import get_connection
        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO settings (key, value, description) VALUES (?, ?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value, "
                "updated_at=strftime('%Y-%m-%dT%H:%M:%SZ','now')",
                (key, key, "UI color theme"),
            )
            conn.commit()
        finally:
            conn.close()
    except Exception as exc:
        logger.warning("Could not save theme setting: %s", exc)


def apply_theme(key: str) -> None:
    """Apply *key* theme to the running QApplication and save it."""
    if key not in _PALETTES:
        logger.warning("Unknown theme key: %s", key)
        return
    qss = _build_qss(_PALETTES[key])
    app = QApplication.instance()
    if app:
        app.setStyleSheet(qss)
    save_theme(key)
    logger.info("Theme applied: %s", key)


def get_current_qss(key: str = "deep_navy") -> str:
    """Return the QSS string for *key* without touching the DB."""
    p = _PALETTES.get(key, _PALETTES["deep_navy"])
    return _build_qss(p)


def palette(key: str) -> dict:
    """Return the raw palette dict for a theme key."""
    return _PALETTES.get(key, _PALETTES["deep_navy"])

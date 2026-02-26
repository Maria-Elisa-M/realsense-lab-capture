"""Theme preview — shows all UI components with live theme switching.

Run from the project root:
    venv/Scripts/python scripts/preview_theme.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QListWidget, QListWidgetItem, QTabWidget, QComboBox,
    QFrame, QScrollArea, QSpinBox, QSplitter, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

# ── Theme definitions ──────────────────────────────────────────────────────── #

THEMES = {
    "Deep Navy / Crimson": dict(
        bg="#1a1a2e", surface="#16213e", border="#0f3460",
        accent="#e94560", accent_hover="#c73652", accent_press="#a52a40",
        text="#e0e0e0", text_dim="#8899bb",
        rec_bg="#1b4a2a", rec_fg="#80ffb0", rec_border="#2a7a40", rec_hover="#256038",
        stp_bg="#4a1b1b", stp_fg="#ffaaaa", stp_border="#7a2a2a", stp_hover="#602525",
        fin_bg="#1b6b3a", fin_fg="#a0f0b0", fin_hover="#228b4a",
        tab_unsel="#0f3460", tab_unsel_text="#a0a0a0", tab_hover="#1a5276",
        header_bg="#0f3460",
    ),
    "Obsidian / Violet": dict(
        bg="#0f0f17", surface="#1a1828", border="#2d2050",
        accent="#7c4dff", accent_hover="#6535e0", accent_press="#4e22b5",
        text="#e8e0ff", text_dim="#9988cc",
        rec_bg="#2a1f4a", rec_fg="#b39ddb", rec_border="#5c3d9e", rec_hover="#3d2e6a",
        stp_bg="#4a1f2a", stp_fg="#ff8a80", stp_border="#8a2040", stp_hover="#6a2535",
        fin_bg="#1a2f4a", fin_fg="#80d8ff", fin_hover="#1e4068",
        tab_unsel="#2d2050", tab_unsel_text="#9988cc", tab_hover="#3d2e6a",
        header_bg="#2d2050",
    ),
    "Carbon / Amber": dict(
        bg="#111111", surface="#1c1c1c", border="#2e2e2e",
        accent="#f5a623", accent_hover="#d4881a", accent_press="#b06a10",
        text="#e8e8e8", text_dim="#999999",
        rec_bg="#2a1f00", rec_fg="#ffd180", rec_border="#7a5500", rec_hover="#3d2e00",
        stp_bg="#3a0f0f", stp_fg="#ff8a80", stp_border="#7a2020", stp_hover="#550f0f",
        fin_bg="#1a2a00", fin_fg="#ccff90", fin_hover="#253d00",
        tab_unsel="#2e2e2e", tab_unsel_text="#999999", tab_hover="#3d3d3d",
        header_bg="#2e2e2e",
    ),
    "Slate / Cyan": dict(
        bg="#0d1821", surface="#1b2838", border="#1e3a5f",
        accent="#00b4d8", accent_hover="#0096c7", accent_press="#0077b6",
        text="#caf0f8", text_dim="#6699aa",
        rec_bg="#003a4a", rec_fg="#90e0ef", rec_border="#006a8a", rec_hover="#005070",
        stp_bg="#4a1b1b", stp_fg="#ff8a80", stp_border="#7a2a2a", stp_hover="#602525",
        fin_bg="#003a30", fin_fg="#80ffee", fin_hover="#005045",
        tab_unsel="#1e3a5f", tab_unsel_text="#6699aa", tab_hover="#2a5280",
        header_bg="#1e3a5f",
    ),
    "Volcanic / Orange": dict(
        bg="#141414", surface="#1e1e1e", border="#333333",
        accent="#ff6b35", accent_hover="#e05520", accent_press="#bf4010",
        text="#f0f0f0", text_dim="#999999",
        rec_bg="#2a1500", rec_fg="#ffb347", rec_border="#7a4000", rec_hover="#3d1f00",
        stp_bg="#3a0f0f", stp_fg="#ff8a80", stp_border="#7a2020", stp_hover="#550f0f",
        fin_bg="#1a2000", fin_fg="#d4ff80", fin_hover="#253000",
        tab_unsel="#333333", tab_unsel_text="#999999", tab_hover="#444444",
        header_bg="#333333",
    ),
    "Forest / Emerald": dict(
        bg="#0d1f1a", surface="#132a22", border="#1a4035",
        accent="#00c896", accent_hover="#00a87e", accent_press="#008060",
        text="#d0f0e8", text_dim="#669988",
        rec_bg="#0a3020", rec_fg="#80ffcc", rec_border="#1a7050", rec_hover="#0f4530",
        stp_bg="#3a0f15", stp_fg="#ff8a90", stp_border="#7a2030", stp_hover="#550f18",
        fin_bg="#0a3020", fin_fg="#80ffcc", fin_hover="#0f4530",
        tab_unsel="#1a4035", tab_unsel_text="#669988", tab_hover="#255545",
        header_bg="#1a4035",
    ),
}


def build_qss(t: dict) -> str:
    return f"""
QMainWindow, QWidget {{
    background-color: {t['bg']};
    color: {t['text']};
    font-family: "Segoe UI", sans-serif;
    font-size: 14px;
}}
QGroupBox {{
    background-color: {t['surface']};
    border: 1px solid {t['border']};
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 8px;
    font-weight: bold;
    color: {t['text_dim']};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}}
QPushButton {{
    background-color: {t['surface']};
    color: {t['text']};
    border: 1px solid {t['border']};
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 13px;
    min-height: 32px;
}}
QPushButton:hover {{
    background-color: {t['tab_hover']};
    color: {t['text']};
}}
QPushButton:disabled {{
    background-color: {t['bg']};
    color: #555555;
    border-color: #333333;
}}
QPushButton#btn_primary {{
    background-color: {t['accent']};
    color: white;
    border: none;
    padding: 10px 24px;
    font-weight: bold;
    font-size: 14px;
    min-height: 36px;
}}
QPushButton#btn_primary:hover {{ background-color: {t['accent_hover']}; }}
QPushButton#btn_primary:pressed {{ background-color: {t['accent_press']}; }}
QPushButton#btn_secondary {{
    background-color: {t['tab_unsel']};
    color: {t['text']};
    border: 1px solid {t['border']};
    padding: 10px 24px;
    font-size: 14px;
    min-height: 36px;
}}
QPushButton#btn_secondary:hover {{ background-color: {t['tab_hover']}; }}
QPushButton#btn_danger {{
    background-color: #6b2737;
    color: #f0a0a0;
    border: none;
    padding: 8px 20px;
    font-size: 14px;
    min-height: 34px;
}}
QPushButton#btn_danger:hover {{ background-color: #8b3748; }}
QPushButton#btn_record {{
    background-color: {t['rec_bg']};
    color: {t['rec_fg']};
    border: 1px solid {t['rec_border']};
    padding: 10px 14px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 13px;
    min-height: 38px;
    text-align: left;
}}
QPushButton#btn_record:hover {{ background-color: {t['rec_hover']}; }}
QPushButton#btn_stop {{
    background-color: {t['stp_bg']};
    color: {t['stp_fg']};
    border: 1px solid {t['stp_border']};
    padding: 10px 14px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 13px;
    min-height: 38px;
    text-align: left;
}}
QPushButton#btn_stop:hover {{ background-color: {t['stp_hover']}; }}
QPushButton#btn_finish {{
    background-color: {t['fin_bg']};
    color: {t['fin_fg']};
    border: none;
    padding: 10px 24px;
    font-weight: bold;
    font-size: 14px;
    min-height: 38px;
}}
QPushButton#btn_finish:hover {{ background-color: {t['fin_hover']}; }}
QLabel#screen_title {{
    font-size: 24px;
    font-weight: bold;
    color: {t['accent']};
    padding-bottom: 6px;
}}
QLabel#subject_label {{
    font-size: 15px;
    color: {t['accent']};
    font-weight: bold;
}}
QLabel#state_label {{
    color: {t['accent']};
    font-weight: bold;
    font-size: 15px;
}}
QLabel#elapsed_label {{
    font-size: 22px;
    font-weight: bold;
    font-family: monospace;
}}
QLabel#error_label {{ color: #ff6b6b; font-size: 13px; }}
QLabel#status_detail {{ color: {t['text_dim']}; font-size: 12px; }}
QLineEdit, QTextEdit, QSpinBox {{
    background-color: {t['surface']};
    color: {t['text']};
    border: 1px solid {t['border']};
    border-radius: 4px;
    padding: 7px;
    font-size: 14px;
    selection-background-color: {t['accent']};
}}
QLineEdit:focus, QSpinBox:focus {{ border-color: {t['accent']}; }}
QComboBox {{
    background-color: {t['surface']};
    color: {t['text']};
    border: 1px solid {t['border']};
    border-radius: 4px;
    padding: 7px;
    font-size: 14px;
    min-height: 32px;
}}
QComboBox QAbstractItemView {{
    background-color: {t['surface']};
    color: {t['text']};
    selection-background-color: {t['accent']};
}}
QTableWidget {{
    background-color: {t['surface']};
    alternate-background-color: {t['bg']};
    gridline-color: {t['border']};
    border: 1px solid {t['border']};
    border-radius: 4px;
    font-size: 13px;
}}
QTableWidget::item:selected {{ background-color: {t['accent']}; color: white; }}
QHeaderView::section {{
    background-color: {t['header_bg']};
    color: {t['text']};
    padding: 8px;
    border: none;
    font-weight: bold;
    font-size: 13px;
}}
QListWidget {{
    background-color: {t['surface']};
    border: 1px solid {t['border']};
    border-radius: 4px;
    font-size: 14px;
}}
QListWidget::item {{ padding: 8px; }}
QListWidget::item:selected {{ background-color: {t['accent']}; color: white; }}
QListWidget::item:hover {{ background-color: {t['tab_hover']}; }}
QTabWidget::pane {{
    border: 1px solid {t['border']};
    background-color: {t['bg']};
    padding: 8px;
}}
QTabBar::tab {{
    background-color: {t['tab_unsel']};
    color: {t['tab_unsel_text']};
    padding: 10px 24px;
    border-radius: 4px 4px 0 0;
    margin-right: 2px;
    font-size: 14px;
    min-width: 80px;
}}
QTabBar::tab:selected {{ background-color: {t['accent']}; color: white; }}
QTabBar::tab:hover:!selected {{ background-color: {t['tab_hover']}; color: {t['text']}; }}
QScrollBar:vertical {{
    background-color: {t['surface']};
    width: 10px;
}}
QScrollBar::handle:vertical {{
    background-color: {t['border']};
    border-radius: 4px;
}}
QScrollBar::handle:vertical:hover {{ background-color: {t['tab_hover']}; }}
QFrame[frameShape="4"] {{ color: {t['border']}; }}
"""


# ── Preview window ─────────────────────────────────────────────────────────── #

class PreviewWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Theme Preview")
        self.setMinimumSize(1100, 780)
        self.resize(1200, 840)
        self._current_theme = list(THEMES.keys())[0]
        self._build_ui()
        self._apply_theme(self._current_theme)

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Theme switcher bar ──────────────────────────────────────── #
        bar = QWidget()
        bar.setFixedHeight(54)
        bar.setStyleSheet("background-color: #080810; border-bottom: 1px solid #222;")
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(12, 8, 12, 8)
        bar_layout.setSpacing(8)

        lbl = QLabel("Theme:")
        lbl.setStyleSheet("color: #888; font-size: 12px;")
        bar_layout.addWidget(lbl)

        self._theme_buttons: dict[str, QPushButton] = {}
        for name in THEMES:
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setFixedHeight(36)
            btn.setStyleSheet(self._theme_btn_style(False))
            btn.clicked.connect(lambda checked, n=name: self._apply_theme(n))
            bar_layout.addWidget(btn)
            self._theme_buttons[name] = btn

        bar_layout.addStretch()
        layout.addWidget(bar)

        # ── Main content ────────────────────────────────────────────── #
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)

        content_layout.addLayout(self._build_left_column(), 1)
        content_layout.addLayout(self._build_right_column(), 1)

        scroll.setWidget(content)
        layout.addWidget(scroll)

    # ── Left column ─────────────────────────────────────────────────── #

    def _build_left_column(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(16)

        # Labels
        grp_lbl = QGroupBox("Labels")
        lbl_layout = QVBoxLayout(grp_lbl)
        t = QLabel("Screen Title")
        t.setObjectName("screen_title")
        lbl_layout.addWidget(t)
        s = QLabel("Subject: LAB-042")
        s.setObjectName("subject_label")
        lbl_layout.addWidget(s)
        st = QLabel("Recording Data")
        st.setObjectName("state_label")
        lbl_layout.addWidget(st)
        el = QLabel("02:47")
        el.setObjectName("elapsed_label")
        lbl_layout.addWidget(el)
        d = QLabel("Calibration: 12.3s  |  Data: 45.6s")
        d.setObjectName("status_detail")
        lbl_layout.addWidget(d)
        e = QLabel("Error: invalid credentials")
        e.setObjectName("error_label")
        lbl_layout.addWidget(e)
        col.addWidget(grp_lbl)

        # Buttons
        grp_btn = QGroupBox("Buttons")
        btn_layout = QVBoxLayout(grp_btn)
        for name, obj in [
            ("Primary Button", "btn_primary"),
            ("Secondary Button", "btn_secondary"),
            ("Danger / Logout", "btn_danger"),
            ("Finish Session", "btn_finish"),
        ]:
            b = QPushButton(name)
            b.setObjectName(obj)
            btn_layout.addWidget(b)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        btn_layout.addWidget(sep)

        rec = QPushButton("▶  Start Data Recording")
        rec.setObjectName("btn_record")
        btn_layout.addWidget(rec)
        stp = QPushButton("■  Stop Recording")
        stp.setObjectName("btn_stop")
        btn_layout.addWidget(stp)
        dis = QPushButton("Disabled Button")
        dis.setEnabled(False)
        btn_layout.addWidget(dis)
        col.addWidget(grp_btn)

        # Inputs
        grp_inp = QGroupBox("Inputs")
        inp_layout = QVBoxLayout(grp_inp)
        inp_layout.addWidget(QLineEdit(placeholderText="Subject code…"))
        inp_layout.addWidget(QLineEdit(placeholderText="Password", echoMode=QLineEdit.EchoMode.Password))
        spin = QSpinBox()
        spin.setValue(30)
        inp_layout.addWidget(spin)
        combo = QComboBox()
        combo.addItems(["operator", "admin"])
        inp_layout.addWidget(combo)
        col.addWidget(grp_inp)

        col.addStretch()
        return col

    # ── Right column ─────────────────────────────────────────────────── #

    def _build_right_column(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(16)

        # Tabs
        tabs = QTabWidget()
        tab1 = QWidget()
        t1l = QVBoxLayout(tab1)
        t1l.addWidget(QLabel("Content of Users tab"))
        tabs.addTab(tab1, "Users")
        tab2 = QWidget()
        tabs.addTab(tab2, "Subjects")
        tab3 = QWidget()
        tabs.addTab(tab3, "Settings")
        col.addWidget(tabs)

        # Table with buttons
        grp_tbl = QGroupBox("Table with action buttons")
        tbl_layout = QVBoxLayout(grp_tbl)
        table = QTableWidget(4, 4)
        table.setHorizontalHeaderLabels(["ID", "Subject", "Sessions", "Actions"])
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(0, 45)
        table.setColumnWidth(2, 75)
        table.setColumnWidth(3, 220)
        table.verticalHeader().setDefaultSectionSize(46)
        table.verticalHeader().setMinimumSectionSize(46)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        for row, (sid, code, n) in enumerate([
            ("1", "LAB-001", "3"), ("2", "LAB-002", "1"),
            ("3", "LAB-007", "5"), ("4", "LAB-012", "2"),
        ]):
            table.setItem(row, 0, QTableWidgetItem(sid))
            table.setItem(row, 1, QTableWidgetItem(code))
            table.setItem(row, 2, QTableWidgetItem(n))
            cell = QWidget()
            cl = QHBoxLayout(cell)
            cl.setContentsMargins(4, 4, 4, 4)
            cl.setSpacing(6)
            b1 = QPushButton("View Sessions")
            b1.setObjectName("btn_secondary")
            b2 = QPushButton("Edit")
            cl.addWidget(b1)
            cl.addWidget(b2)
            table.setCellWidget(row, 3, cell)
        tbl_layout.addWidget(table)
        col.addWidget(grp_tbl)

        # List widget
        grp_list = QGroupBox("List")
        lst_layout = QVBoxLayout(grp_list)
        lst = QListWidget()
        for item in ["LAB-001 — Alice", "LAB-002 — Bob", "LAB-007 — Carol"]:
            lst.addItem(QListWidgetItem(item))
        lst.setMaximumHeight(110)
        lst_layout.addWidget(lst)
        col.addWidget(grp_list)

        col.addStretch()
        return col

    # ── Theme application ─────────────────────────────────────────────── #

    def _apply_theme(self, name: str) -> None:
        self._current_theme = name
        qss = build_qss(THEMES[name])
        QApplication.instance().setStyleSheet(qss)

        for n, btn in self._theme_buttons.items():
            btn.setChecked(n == name)
            btn.setStyleSheet(self._theme_btn_style(n == name))

        self.setWindowTitle(f"Theme Preview — {name}")

    def _theme_btn_style(self, active: bool) -> str:
        if active:
            return ("QPushButton { background-color: #e94560; color: white; "
                    "border: none; padding: 6px 14px; border-radius: 4px; "
                    "font-size: 12px; font-weight: bold; }")
        return ("QPushButton { background-color: #1a1a2e; color: #aaaaaa; "
                "border: 1px solid #333355; padding: 6px 14px; border-radius: 4px; "
                "font-size: 12px; } "
                "QPushButton:hover { background-color: #252545; color: #ffffff; }")


# ── Entry point ────────────────────────────────────────────────────────────── #

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PreviewWindow()
    win.show()
    sys.exit(app.exec())

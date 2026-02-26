"""Admin tab: Application settings."""
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QHBoxLayout, QLabel, QMessageBox,
    QFileDialog, QSpinBox, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt
from app.config.settings import load_settings, save_settings, AppSettings
from app.ui.themes import THEME_KEYS, THEME_NAMES, load_theme

logger = logging.getLogger(__name__)


class SettingsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        form = QFormLayout()
        form.setSpacing(8)

        # Output directory
        dir_row = QHBoxLayout()
        self.input_output_dir = QLineEdit()
        btn_browse = QPushButton("Browse…")
        btn_browse.clicked.connect(self._browse_dir)
        dir_row.addWidget(self.input_output_dir)
        dir_row.addWidget(btn_browse)
        form.addRow("Output Directory:", dir_row)

        # Color stream
        form.addRow(QLabel("<b>Color Stream</b>"))
        self.spin_color_w = QSpinBox()
        self.spin_color_w.setRange(320, 3840)
        self.spin_color_w.setSingleStep(16)
        self.spin_color_h = QSpinBox()
        self.spin_color_h.setRange(240, 2160)
        self.spin_color_h.setSingleStep(16)
        self.spin_color_fps = QSpinBox()
        self.spin_color_fps.setRange(1, 90)
        form.addRow("Width:", self.spin_color_w)
        form.addRow("Height:", self.spin_color_h)
        form.addRow("FPS:", self.spin_color_fps)

        # Depth stream
        form.addRow(QLabel("<b>Depth Stream</b>"))
        self.spin_depth_w = QSpinBox()
        self.spin_depth_w.setRange(320, 1280)
        self.spin_depth_w.setSingleStep(16)
        self.spin_depth_h = QSpinBox()
        self.spin_depth_h.setRange(240, 720)
        self.spin_depth_h.setSingleStep(16)
        self.spin_depth_fps = QSpinBox()
        self.spin_depth_fps.setRange(1, 90)
        form.addRow("Width:", self.spin_depth_w)
        form.addRow("Height:", self.spin_depth_h)
        form.addRow("FPS:", self.spin_depth_fps)

        # Infrared stream
        form.addRow(QLabel("<b>Infrared Stream</b>"))
        self.spin_ir_w = QSpinBox()
        self.spin_ir_w.setRange(320, 1280)
        self.spin_ir_w.setSingleStep(16)
        self.spin_ir_h = QSpinBox()
        self.spin_ir_h.setRange(240, 720)
        self.spin_ir_h.setSingleStep(16)
        self.spin_ir_fps = QSpinBox()
        self.spin_ir_fps.setRange(1, 90)
        form.addRow("Width:", self.spin_ir_w)
        form.addRow("Height:", self.spin_ir_h)
        form.addRow("FPS:", self.spin_ir_fps)

        # Preview
        form.addRow(QLabel("<b>Preview</b>"))
        self.spin_preview_fps = QSpinBox()
        self.spin_preview_fps.setRange(1, 60)
        form.addRow("Preview FPS:", self.spin_preview_fps)

        outer.addLayout(form)

        # Theme selector
        form.addRow(QLabel("<b>Appearance</b>"))
        theme_row = QHBoxLayout()
        theme_row.setSpacing(24)
        self._theme_radios: dict[str, QRadioButton] = {}
        self._theme_group = QButtonGroup(self)
        for key in THEME_KEYS:
            radio = QRadioButton(THEME_NAMES[key])
            radio.toggled.connect(lambda checked, k=key: self._on_theme_clicked(k) if checked else None)
            self._theme_group.addButton(radio)
            self._theme_radios[key] = radio
            theme_row.addWidget(radio)
        theme_row.addStretch()
        form.addRow("Theme:", theme_row)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_save = QPushButton("Save Settings")
        btn_save.setObjectName("btn_primary")
        btn_save.clicked.connect(self._on_save)
        btn_row.addWidget(btn_save)
        outer.addLayout(btn_row)
        outer.addStretch()

    def _on_theme_clicked(self, key: str) -> None:
        from app.ui.themes import apply_theme
        apply_theme(key)
        mw = self.window()
        if hasattr(mw, "_on_theme_selected"):
            mw._on_theme_selected(key)

    def _sync_theme_radios(self, active_key: str) -> None:
        for key, radio in self._theme_radios.items():
            radio.blockSignals(True)
            radio.setChecked(key == active_key)
            radio.blockSignals(False)

    def refresh(self) -> None:
        self._sync_theme_radios(load_theme())
        s = load_settings()
        self.input_output_dir.setText(s.output_directory)
        self.spin_color_w.setValue(s.color_width)
        self.spin_color_h.setValue(s.color_height)
        self.spin_color_fps.setValue(s.color_fps)
        self.spin_depth_w.setValue(s.depth_width)
        self.spin_depth_h.setValue(s.depth_height)
        self.spin_depth_fps.setValue(s.depth_fps)
        self.spin_ir_w.setValue(s.infrared_width)
        self.spin_ir_h.setValue(s.infrared_height)
        self.spin_ir_fps.setValue(s.infrared_fps)
        self.spin_preview_fps.setValue(s.preview_fps)

    def _browse_dir(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", self.input_output_dir.text()
        )
        if path:
            self.input_output_dir.setText(path)

    def _on_save(self) -> None:
        s = AppSettings(
            output_directory=self.input_output_dir.text().strip(),
            color_width=self.spin_color_w.value(),
            color_height=self.spin_color_h.value(),
            color_fps=self.spin_color_fps.value(),
            depth_width=self.spin_depth_w.value(),
            depth_height=self.spin_depth_h.value(),
            depth_fps=self.spin_depth_fps.value(),
            infrared_width=self.spin_ir_w.value(),
            infrared_height=self.spin_ir_h.value(),
            infrared_fps=self.spin_ir_fps.value(),
            preview_fps=self.spin_preview_fps.value(),
        )
        if not s.output_directory:
            QMessageBox.warning(self, "Validation", "Output directory cannot be empty.")
            return
        save_settings(s)
        logger.info("Settings saved.")
        QMessageBox.information(self, "Settings", "Settings saved successfully.")

"""Left-panel recording controls with icons, state display, and elapsed timer."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QSizePolicy, QApplication
)
from PyQt6.QtCore import QTimer, Qt, QSize
from PyQt6.QtGui import QIcon


def _icon(standard_pixmap) -> QIcon:
    return QApplication.style().standardIcon(standard_pixmap)


class RecordingControls(QWidget):
    """Vertical left panel housing all recording buttons, status, and timer."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(260)
        self.setObjectName("recording_panel")

        self._elapsed_seconds = 0
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(6)

        # ── State ──────────────────────────────────────────────────────── #
        self.lbl_state = QLabel("Ready")
        self.lbl_state.setObjectName("state_label")
        self.lbl_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_state.setWordWrap(True)
        layout.addWidget(self.lbl_state)

        layout.addWidget(self._separator())

        # ── Calibration buttons ────────────────────────────────────────── #
        layout.addWidget(self._section("CALIBRATION"))

        SP = QApplication.style().StandardPixmap
        self.btn_start_calibration = self._btn(
            "Start Calibration", SP.SP_MediaPlay, "btn_record")
        self.btn_stop_calibration = self._btn(
            "Stop Calibration", SP.SP_MediaStop, "btn_stop")
        self.btn_restart_calibration = self._btn(
            "Re-record Calibration", SP.SP_BrowserReload)

        layout.addWidget(self.btn_start_calibration)
        layout.addWidget(self.btn_stop_calibration)
        layout.addWidget(self.btn_restart_calibration)

        layout.addWidget(self._separator())

        # ── Data buttons ───────────────────────────────────────────────── #
        layout.addWidget(self._section("DATA RECORDING"))

        self.btn_start_data = self._btn(
            "Start Data Recording", SP.SP_MediaPlay, "btn_record")
        self.btn_stop_data = self._btn(
            "Stop Data Recording", SP.SP_MediaStop, "btn_stop")
        self.btn_restart_data = self._btn(
            "Re-record Data", SP.SP_BrowserReload)

        layout.addWidget(self.btn_start_data)
        layout.addWidget(self.btn_stop_data)
        layout.addWidget(self.btn_restart_data)

        layout.addWidget(self._separator())

        # ── Finish ────────────────────────────────────────────────────── #
        self.btn_finish = self._btn(
            "Finish Session", SP.SP_DialogApplyButton, "btn_finish")
        layout.addWidget(self.btn_finish)

        layout.addStretch()
        layout.addWidget(self._separator())

        # ── Status labels ─────────────────────────────────────────────── #
        layout.addWidget(self._section("STATUS"))
        self.lbl_calibration_status = QLabel("Calibration: —")
        self.lbl_calibration_status.setWordWrap(True)
        self.lbl_calibration_status.setObjectName("status_detail")
        self.lbl_data_status = QLabel("Data: —")
        self.lbl_data_status.setWordWrap(True)
        self.lbl_data_status.setObjectName("status_detail")
        layout.addWidget(self.lbl_calibration_status)
        layout.addWidget(self.lbl_data_status)

        layout.addWidget(self._separator())

        # ── Recording indicator + elapsed timer ───────────────────────── #
        self.lbl_rec_indicator = QLabel("● REC")
        self.lbl_rec_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_rec_indicator.setStyleSheet(
            "color: #ff4444; font-weight: bold; font-size: 13px; letter-spacing: 2px;"
        )
        self.lbl_rec_indicator.setVisible(False)
        layout.addWidget(self.lbl_rec_indicator)

        self.lbl_elapsed = QLabel("00:00")
        self.lbl_elapsed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_elapsed.setObjectName("elapsed_label")
        self.lbl_elapsed.setVisible(False)
        layout.addWidget(self.lbl_elapsed)

        # Hide all but start calibration initially
        for btn in [self.btn_stop_calibration, self.btn_restart_calibration,
                    self.btn_start_data, self.btn_stop_data,
                    self.btn_restart_data, self.btn_finish]:
            btn.setVisible(False)

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _btn(self, text: str, pixmap, object_name: str = "") -> QPushButton:
        btn = QPushButton(text)
        btn.setIcon(_icon(pixmap))
        btn.setIconSize(QSize(18, 18))
        if object_name:
            btn.setObjectName(object_name)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.setMinimumHeight(40)
        return btn

    def _separator(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("color: #2a2a4a;")
        return line

    def _section(self, title: str) -> QLabel:
        lbl = QLabel(title)
        lbl.setStyleSheet(
            "color: #666688; font-size: 10px; font-weight: bold; letter-spacing: 1px;"
        )
        return lbl

    # ------------------------------------------------------------------ #
    # Timer                                                                #
    # ------------------------------------------------------------------ #

    def start_timer(self) -> None:
        self._elapsed_seconds = 0
        self._update_label()
        self.lbl_rec_indicator.setVisible(True)
        self.lbl_elapsed.setVisible(True)
        self._timer.start()

    def stop_timer(self) -> None:
        self._timer.stop()
        self.lbl_rec_indicator.setVisible(False)
        self.lbl_elapsed.setVisible(False)

    def _tick(self) -> None:
        self._elapsed_seconds += 1
        self._update_label()

    def _update_label(self) -> None:
        minutes, seconds = divmod(self._elapsed_seconds, 60)
        self.lbl_elapsed.setText(f"{minutes:02d}:{seconds:02d}")

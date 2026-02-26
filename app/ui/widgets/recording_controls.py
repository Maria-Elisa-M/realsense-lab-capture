"""Context-sensitive recording control panel with elapsed timer display."""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import QTimer, Qt


class RecordingControls(QWidget):
    """Displays recording buttons and an elapsed-time counter."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._elapsed_seconds = 0
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.lbl_elapsed = QLabel("00:00")
        self.lbl_elapsed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_elapsed.setObjectName("elapsed_label")
        self.lbl_elapsed.setVisible(False)

        self.btn_start_calibration = QPushButton("Start Calibration")
        self.btn_stop_calibration = QPushButton("Stop Calibration")
        self.btn_restart_calibration = QPushButton("Re-record Calibration")
        self.btn_start_data = QPushButton("Start Data Recording")
        self.btn_stop_data = QPushButton("Stop Data Recording")
        self.btn_restart_data = QPushButton("Re-record Data")
        self.btn_finish = QPushButton("Finish Session")

        for btn in [self.btn_stop_calibration, self.btn_restart_calibration,
                    self.btn_start_data, self.btn_stop_data,
                    self.btn_restart_data, self.btn_finish]:
            btn.setVisible(False)

        self.btn_finish.setObjectName("btn_finish")

        for w in [self.btn_start_calibration, self.btn_stop_calibration,
                  self.btn_restart_calibration, self.btn_start_data,
                  self.btn_stop_data, self.btn_restart_data,
                  self.btn_finish, self.lbl_elapsed]:
            layout.addWidget(w)

    def start_timer(self) -> None:
        self._elapsed_seconds = 0
        self._update_label()
        self.lbl_elapsed.setVisible(True)
        self._timer.start()

    def stop_timer(self) -> None:
        self._timer.stop()
        self.lbl_elapsed.setVisible(False)

    def _tick(self) -> None:
        self._elapsed_seconds += 1
        self._update_label()

    def _update_label(self) -> None:
        minutes, seconds = divmod(self._elapsed_seconds, 60)
        self.lbl_elapsed.setText(f"{minutes:02d}:{seconds:02d}")

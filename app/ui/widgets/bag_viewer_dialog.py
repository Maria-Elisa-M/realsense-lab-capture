"""In-app .bag file viewer dialog with play/pause and restart controls."""
import os
import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy
)
from PyQt6.QtCore import QThread

from app.camera.bag_playback_worker import BagPlaybackWorker
from app.ui.widgets.camera_preview_widget import CameraPreviewWidget

logger = logging.getLogger(__name__)


class BagViewerDialog(QDialog):
    """Plays back a .bag recording file using the built-in RealSense pipeline."""

    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self._file_path = file_path
        self._worker: BagPlaybackWorker | None = None
        self._thread:  QThread | None = None
        self._paused   = False

        fname = os.path.basename(file_path)
        self.setWindowTitle(f"Viewer — {fname}")
        self.setMinimumSize(960, 580)
        self.resize(1100, 650)

        self._build_ui()
        self._start_playback()

    # ------------------------------------------------------------------ #
    # UI                                                                   #
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        self._preview = CameraPreviewWidget()
        self._preview.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self._preview)

        # Control bar
        ctrl = QHBoxLayout()

        self._lbl_status = QLabel("Loading…")
        self._lbl_status.setStyleSheet("color: #8899bb; font-size: 11px;")
        ctrl.addWidget(self._lbl_status)
        ctrl.addStretch()

        self._btn_restart = QPushButton("Restart")
        self._btn_restart.setObjectName("btn_secondary")
        self._btn_restart.setEnabled(False)
        self._btn_restart.clicked.connect(self._on_restart)
        ctrl.addWidget(self._btn_restart)

        self._btn_pause = QPushButton("Pause")
        self._btn_pause.setObjectName("btn_secondary")
        self._btn_pause.clicked.connect(self._on_pause_resume)
        ctrl.addWidget(self._btn_pause)

        btn_close = QPushButton("Close")
        btn_close.setObjectName("btn_secondary")
        btn_close.clicked.connect(self.close)
        ctrl.addWidget(btn_close)

        layout.addLayout(ctrl)

    # ------------------------------------------------------------------ #
    # Playback lifecycle                                                   #
    # ------------------------------------------------------------------ #

    def _start_playback(self) -> None:
        self._paused = False
        self._btn_pause.setText("Pause")
        self._btn_pause.setEnabled(True)
        self._btn_restart.setEnabled(False)
        self._lbl_status.setText("Playing…")

        self._worker = BagPlaybackWorker(self._file_path)
        self._thread = QThread()
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.frame_ready.connect(self._preview.set_frame)
        self._worker.playback_ended.connect(self._on_playback_ended)
        self._worker.error_occurred.connect(self._on_error)
        self._thread.start()

    def _stop_worker(self) -> None:
        if self._worker:
            self._worker.stop()
        if self._thread:
            self._thread.quit()
            self._thread.wait(3000)
        self._worker = None
        self._thread = None

    # ------------------------------------------------------------------ #
    # Slots                                                                #
    # ------------------------------------------------------------------ #

    def _on_pause_resume(self) -> None:
        if self._worker is None:
            return
        if self._paused:
            self._worker.resume()
            self._paused = False
            self._btn_pause.setText("Pause")
            self._lbl_status.setText("Playing…")
        else:
            self._worker.pause()
            self._paused = True
            self._btn_pause.setText("Resume")
            self._lbl_status.setText("Paused")

    def _on_restart(self) -> None:
        self._stop_worker()
        self._preview.show_no_signal("Restarting…")
        self._start_playback()

    def _on_playback_ended(self) -> None:
        self._lbl_status.setText("Playback complete")
        self._btn_pause.setEnabled(False)
        self._btn_restart.setEnabled(True)

    def _on_error(self, message: str) -> None:
        logger.error("Bag viewer error: %s", message)
        self._lbl_status.setText(f"Error: {message}")
        self._btn_pause.setEnabled(False)
        self._btn_restart.setEnabled(True)
        self._preview.show_no_signal(f"Error: {message}")

    def closeEvent(self, event) -> None:
        self._stop_worker()
        super().closeEvent(event)

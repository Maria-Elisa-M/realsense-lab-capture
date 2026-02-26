"""Recording screen — state machine + preview + recording workers."""
import logging
from datetime import datetime, timezone
from enum import Enum, auto
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSlot, pyqtSignal
from PyQt6.QtGui import QImage

from app.database.models import Subject, Session, Recording
import app.database.repositories.session_repository as session_repo
import app.database.repositories.recording_repository as recording_repo
from app.auth.auth_service import current_user
from app.config.settings import load_settings
from app.utils.file_utils import build_output_path
from app.camera.preview_worker import PreviewWorker
from app.camera.recording_worker import RecordingWorker
from app.ui.widgets.camera_preview_widget import CameraPreviewWidget
from app.ui.widgets.recording_controls import RecordingControls

logger = logging.getLogger(__name__)


class RecordingState(Enum):
    IDLE_NO_CALIBRATION = auto()
    RECORDING_CALIBRATION = auto()
    IDLE_CALIBRATION_DONE = auto()
    RECORDING_DATA = auto()
    BOTH_DONE = auto()


class RecordingScreen(QWidget):
    """Main recording screen managing the 5-state recording flow."""

    session_finished = pyqtSignal(object)  # emits Session on finish

    def __init__(self, parent=None):
        super().__init__(parent)
        self._subject: Subject | None = None
        self._session: Session | None = None
        self._state = RecordingState.IDLE_NO_CALIBRATION
        self._calibration_recording: Recording | None = None
        self._data_recording: Recording | None = None

        # Thread management
        self._preview_thread: QThread | None = None
        self._preview_worker: PreviewWorker | None = None
        self._rec_thread: QThread | None = None
        self._rec_worker: RecordingWorker | None = None
        self._rec_file_path: str = ""

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # Header
        header = QHBoxLayout()
        self.lbl_subject = QLabel("Subject: —")
        self.lbl_subject.setObjectName("subject_label")
        self.lbl_state = QLabel()
        self.lbl_state.setObjectName("state_label")
        self.btn_logout = QPushButton("Logout")
        self.btn_logout.setObjectName("btn_danger")
        self.btn_logout.clicked.connect(self._on_logout)
        header.addWidget(self.lbl_subject)
        header.addStretch()
        header.addWidget(self.lbl_state)
        header.addWidget(self.btn_logout)
        layout.addLayout(header)

        # Camera preview
        self.preview = CameraPreviewWidget()
        self.preview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.preview)

        # Status bar
        status_row = QHBoxLayout()
        self.lbl_calibration_status = QLabel("Calibration: Not recorded")
        self.lbl_data_status = QLabel("Data: Not recorded")
        status_row.addWidget(self.lbl_calibration_status)
        status_row.addStretch()
        status_row.addWidget(self.lbl_data_status)
        layout.addLayout(status_row)

        # Controls
        self.controls = RecordingControls()
        layout.addWidget(self.controls)

        # Wire up buttons
        self.controls.btn_start_calibration.clicked.connect(self._start_calibration)
        self.controls.btn_stop_calibration.clicked.connect(self._stop_calibration)
        self.controls.btn_restart_calibration.clicked.connect(self._restart_calibration)
        self.controls.btn_start_data.clicked.connect(self._start_data)
        self.controls.btn_stop_data.clicked.connect(self._stop_data)
        self.controls.btn_restart_data.clicked.connect(self._restart_data)
        self.controls.btn_finish.clicked.connect(self._finish_session)

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def setup_session(self, subject: Subject) -> None:
        """Called by main_window before showing this screen."""
        self._subject = subject
        user = current_user()
        self._session = session_repo.create(subject.id, user.id)
        self._calibration_recording = None
        self._data_recording = None
        self.lbl_subject.setText(
            f"Subject: {subject.subject_code}"
        )
        self._set_state(RecordingState.IDLE_NO_CALIBRATION)
        self._start_preview()

    def teardown(self) -> None:
        """Stop all workers — called when navigating away."""
        self._stop_preview()
        self._stop_recording_worker()

    # ------------------------------------------------------------------ #
    # State machine                                                        #
    # ------------------------------------------------------------------ #

    def _set_state(self, state: RecordingState) -> None:
        self._state = state
        c = self.controls
        # Hide all first
        for btn in [c.btn_start_calibration, c.btn_stop_calibration,
                    c.btn_restart_calibration, c.btn_start_data,
                    c.btn_stop_data, c.btn_restart_data, c.btn_finish]:
            btn.setVisible(False)

        state_labels = {
            RecordingState.IDLE_NO_CALIBRATION: "Awaiting Calibration",
            RecordingState.RECORDING_CALIBRATION: "● Recording Calibration",
            RecordingState.IDLE_CALIBRATION_DONE: "Calibration Done",
            RecordingState.RECORDING_DATA: "● Recording Data",
            RecordingState.BOTH_DONE: "Session Complete",
        }
        self.lbl_state.setText(state_labels.get(state, ""))

        if state == RecordingState.IDLE_NO_CALIBRATION:
            c.btn_start_calibration.setVisible(True)
        elif state == RecordingState.RECORDING_CALIBRATION:
            c.btn_stop_calibration.setVisible(True)
            c.lbl_elapsed.setVisible(True)
        elif state == RecordingState.IDLE_CALIBRATION_DONE:
            c.btn_restart_calibration.setVisible(True)
            c.btn_start_data.setVisible(True)
        elif state == RecordingState.RECORDING_DATA:
            c.btn_stop_data.setVisible(True)
            c.lbl_elapsed.setVisible(True)
        elif state == RecordingState.BOTH_DONE:
            c.btn_restart_calibration.setVisible(True)
            c.btn_restart_data.setVisible(True)
            c.btn_finish.setVisible(True)

    # ------------------------------------------------------------------ #
    # Button handlers                                                      #
    # ------------------------------------------------------------------ #

    def _start_calibration(self) -> None:
        self._begin_recording("calibration")
        self._set_state(RecordingState.RECORDING_CALIBRATION)

    def _stop_calibration(self) -> None:
        self._stop_recording_worker()

    def _restart_calibration(self) -> None:
        reply = QMessageBox.question(
            self, "Re-record Calibration",
            "This will overwrite the existing calibration recording. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        if self._calibration_recording:
            recording_repo.delete_by_id(self._calibration_recording.id)
            self._calibration_recording = None
        self.lbl_calibration_status.setText("Calibration: Not recorded")
        self._set_state(RecordingState.IDLE_NO_CALIBRATION)

    def _start_data(self) -> None:
        self._begin_recording("data")
        self._set_state(RecordingState.RECORDING_DATA)

    def _stop_data(self) -> None:
        self._stop_recording_worker()

    def _restart_data(self) -> None:
        reply = QMessageBox.question(
            self, "Re-record Data",
            "This will overwrite the existing data recording. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        if self._data_recording:
            recording_repo.delete_by_id(self._data_recording.id)
            self._data_recording = None
        self.lbl_data_status.setText("Data: Not recorded")
        self._set_state(RecordingState.IDLE_CALIBRATION_DONE)

    def _finish_session(self) -> None:
        if self._session:
            session_repo.close_session(self._session.id)
        self.teardown()
        # Signal parent
        mw = self.window()
        if hasattr(mw, "on_session_finished"):
            mw.on_session_finished(self._session)

    def _on_logout(self) -> None:
        reply = QMessageBox.question(
            self, "Logout",
            "Are you sure you want to logout? Any unsaved session will be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.teardown()
            mw = self.window()
            if hasattr(mw, "logout"):
                mw.logout()

    # ------------------------------------------------------------------ #
    # Recording lifecycle                                                  #
    # ------------------------------------------------------------------ #

    def _begin_recording(self, rec_type: str) -> None:
        """Stop preview, create DB record, start recording worker."""
        self._stop_preview()

        settings = load_settings()
        file_path = build_output_path(
            settings.output_directory,
            self._subject.subject_code,
            self._session.id,
            rec_type,
        )
        self._rec_file_path = file_path
        started_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        rec = recording_repo.create(self._session.id, rec_type, file_path, started_at)
        if rec_type == "calibration":
            self._calibration_recording = rec
        else:
            self._data_recording = rec

        self._rec_worker = RecordingWorker(
            file_path=file_path,
            color_width=settings.color_width,
            color_height=settings.color_height,
            color_fps=settings.color_fps,
            depth_width=settings.depth_width,
            depth_height=settings.depth_height,
            depth_fps=settings.depth_fps,
            infrared_width=settings.infrared_width,
            infrared_height=settings.infrared_height,
            infrared_fps=settings.infrared_fps,
        )
        self._rec_thread = QThread()
        self._rec_worker.moveToThread(self._rec_thread)
        self._rec_thread.started.connect(self._rec_worker.run)
        self._rec_worker.recording_stopped.connect(self._on_recording_stopped)
        self._rec_worker.error_occurred.connect(self._on_recording_error)
        self._rec_thread.start()
        self.controls.start_timer()

    def _stop_recording_worker(self) -> None:
        if self._rec_worker:
            self._rec_worker.stop()
        if self._rec_thread:
            self._rec_thread.quit()
            self._rec_thread.wait(5000)
        self._rec_worker = None
        self._rec_thread = None
        self.controls.stop_timer()

    @pyqtSlot(str, float)
    def _on_recording_stopped(self, file_path: str, duration: float) -> None:
        ended_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.controls.stop_timer()

        current_type = None
        current_rec = None
        if self._state == RecordingState.RECORDING_CALIBRATION:
            current_type = "calibration"
            current_rec = self._calibration_recording
        elif self._state == RecordingState.RECORDING_DATA:
            current_type = "data"
            current_rec = self._data_recording

        if current_rec:
            recording_repo.finalize(current_rec.id, ended_at, duration, file_path)

        if current_type == "calibration":
            self.lbl_calibration_status.setText(
                f"Calibration: {duration:.1f}s — {file_path}"
            )
            self._set_state(RecordingState.IDLE_CALIBRATION_DONE)
        elif current_type == "data":
            self.lbl_data_status.setText(
                f"Data: {duration:.1f}s — {file_path}"
            )
            self._set_state(RecordingState.BOTH_DONE)

        # Restart preview after recording
        self._start_preview()

    @pyqtSlot(str)
    def _on_recording_error(self, message: str) -> None:
        logger.error("Recording error: %s", message)
        self.controls.stop_timer()
        QMessageBox.critical(self, "Recording Error", message)
        # Return to appropriate idle state
        if self._calibration_recording and self._data_recording:
            self._set_state(RecordingState.BOTH_DONE)
        elif self._calibration_recording:
            self._set_state(RecordingState.IDLE_CALIBRATION_DONE)
        else:
            self._set_state(RecordingState.IDLE_NO_CALIBRATION)
        self._start_preview()

    # ------------------------------------------------------------------ #
    # Preview lifecycle                                                    #
    # ------------------------------------------------------------------ #

    def _start_preview(self) -> None:
        settings = load_settings()
        self._preview_worker = PreviewWorker(
            color_width=settings.color_width,
            color_height=settings.color_height,
            color_fps=settings.color_fps,
            preview_fps=settings.preview_fps,
        )
        self._preview_thread = QThread()
        self._preview_worker.moveToThread(self._preview_thread)
        self._preview_thread.started.connect(self._preview_worker.run)
        self._preview_worker.frame_ready.connect(self.preview.set_frame)
        self._preview_worker.error_occurred.connect(self._on_preview_error)
        self._preview_thread.start()

    def _stop_preview(self) -> None:
        if self._preview_worker:
            self._preview_worker.stop()
        if self._preview_thread:
            self._preview_thread.quit()
            self._preview_thread.wait(3000)
        self._preview_worker = None
        self._preview_thread = None

    @pyqtSlot(str)
    def _on_preview_error(self, message: str) -> None:
        logger.warning("Preview error: %s", message)
        self.preview.show_no_signal(f"Camera error: {message}")

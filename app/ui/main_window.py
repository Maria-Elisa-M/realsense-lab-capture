"""Main application window — QStackedWidget navigation controller."""
import logging
from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from PyQt6.QtCore import Qt

from app.auth import auth_service
from app.database.models import Session, Subject
from app.ui.screens.login_screen import LoginScreen
from app.ui.screens.subject_select_screen import SubjectSelectScreen
from app.ui.screens.recording_screen import RecordingScreen
from app.ui.screens.session_review_screen import SessionReviewScreen
from app.ui.screens.admin.admin_dashboard_screen import AdminDashboardScreen

logger = logging.getLogger(__name__)

# Screen index constants
IDX_LOGIN = 0
IDX_SUBJECT_SELECT = 1
IDX_RECORDING = 2
IDX_SESSION_REVIEW = 3
IDX_ADMIN = 4


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RealSense Lab Video Capture")
        self.setMinimumSize(1000, 700)
        self.resize(1280, 800)

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        # Instantiate screens
        self._login = LoginScreen()
        self._subject_select = SubjectSelectScreen()
        self._recording = RecordingScreen()
        self._session_review = SessionReviewScreen()
        self._admin = AdminDashboardScreen()

        self._stack.addWidget(self._login)          # 0
        self._stack.addWidget(self._subject_select) # 1
        self._stack.addWidget(self._recording)      # 2
        self._stack.addWidget(self._session_review) # 3
        self._stack.addWidget(self._admin)          # 4

        # Wire signals
        self._login.login_successful.connect(self._on_login_successful)
        self._subject_select.subject_selected.connect(self._on_subject_selected)

        self._stack.setCurrentIndex(IDX_LOGIN)

    # ------------------------------------------------------------------ #
    # Navigation                                                           #
    # ------------------------------------------------------------------ #

    def _on_login_successful(self) -> None:
        user = auth_service.current_user()
        if user is None:
            return
        logger.info("Navigating after login: role=%s", user.role)
        if user.role == "admin":
            self._admin.refresh()
            self._stack.setCurrentIndex(IDX_ADMIN)
        else:
            self._subject_select.refresh()
            self._stack.setCurrentIndex(IDX_SUBJECT_SELECT)

    def _on_subject_selected(self, subject: Subject) -> None:
        logger.info("Subject selected: %s", subject.subject_code)
        self._recording.setup_session(subject)
        self._stack.setCurrentIndex(IDX_RECORDING)

    def on_session_finished(self, session: Session) -> None:
        """Called by RecordingScreen when the operator finishes a session."""
        import app.database.repositories.subject_repository as subject_repo
        subject = subject_repo.get_by_id(session.subject_id)
        self._session_review.load_session(session, subject)
        self._stack.setCurrentIndex(IDX_SESSION_REVIEW)

    def go_subject_select(self) -> None:
        """Navigate back to subject selection (for operators)."""
        self._subject_select.refresh()
        self._stack.setCurrentIndex(IDX_SUBJECT_SELECT)

    def logout(self) -> None:
        logger.info("Logging out.")
        # Teardown recording if active
        try:
            self._recording.teardown()
        except Exception:
            pass
        auth_service.logout()
        self._login.clear()
        self._stack.setCurrentIndex(IDX_LOGIN)

    def closeEvent(self, event) -> None:
        """Ensure workers are stopped on window close."""
        try:
            self._recording.teardown()
        except Exception:
            pass
        super().closeEvent(event)

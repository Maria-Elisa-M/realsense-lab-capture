"""Main application window — QStackedWidget navigation controller."""
import logging
from PyQt6.QtWidgets import (
    QMainWindow, QStackedWidget, QWidget, QHBoxLayout,
    QLabel, QVBoxLayout, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt

from app.auth import auth_service
from app.database.models import Session, Subject
from app.ui.themes import apply_theme, load_theme, THEME_KEYS, THEME_NAMES, palette
from app.ui.screens.login_screen import LoginScreen
from app.ui.screens.subject_select_screen import SubjectSelectScreen
from app.ui.screens.session_history_screen import SessionHistoryScreen
from app.ui.screens.recording_screen import RecordingScreen
from app.ui.screens.session_review_screen import SessionReviewScreen
from app.ui.screens.admin.admin_dashboard_screen import AdminDashboardScreen

logger = logging.getLogger(__name__)

# Screen index constants
IDX_LOGIN           = 0
IDX_SUBJECT_SELECT  = 1
IDX_SESSION_HISTORY = 2
IDX_RECORDING       = 3
IDX_SESSION_REVIEW  = 4
IDX_ADMIN           = 5


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RealSense Lab Video Capture")
        self.setMinimumSize(1000, 700)
        self.resize(1280, 800)

        # Root widget: theme bar on top, then the screen stack
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        self.setCentralWidget(root)

        root_layout.addWidget(self._build_theme_bar())

        self._stack = QStackedWidget()
        root_layout.addWidget(self._stack)

        # Instantiate screens
        self._login           = LoginScreen()
        self._subject_select  = SubjectSelectScreen()
        self._session_history = SessionHistoryScreen()
        self._recording       = RecordingScreen()
        self._session_review  = SessionReviewScreen()
        self._admin           = AdminDashboardScreen()

        self._stack.addWidget(self._login)           # 0
        self._stack.addWidget(self._subject_select)  # 1
        self._stack.addWidget(self._session_history) # 2
        self._stack.addWidget(self._recording)       # 3
        self._stack.addWidget(self._session_review)  # 4
        self._stack.addWidget(self._admin)           # 5

        # Wire signals
        self._login.login_successful.connect(self._on_login_successful)
        self._subject_select.subject_selected.connect(self._on_subject_selected)

        self._stack.setCurrentIndex(IDX_LOGIN)

    # ------------------------------------------------------------------ #
    # Theme bar                                                            #
    # ------------------------------------------------------------------ #

    def _build_theme_bar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(36)
        bar.setStyleSheet("background-color: #080810; border-bottom: 1px solid #1a1a30;")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.setSpacing(20)

        lbl = QLabel("Theme:")
        lbl.setStyleSheet("color: #666688; font-size: 11px;")
        layout.addWidget(lbl)

        self._theme_radios: dict[str, QRadioButton] = {}
        self._theme_group = QButtonGroup(bar)
        current = load_theme()

        for key in THEME_KEYS:
            radio = QRadioButton(THEME_NAMES[key])
            radio.setChecked(key == current)
            radio.setStyleSheet("color: #cccccc; font-size: 12px; spacing: 6px;")
            radio.toggled.connect(lambda checked, k=key: self._on_theme_selected(k) if checked else None)
            self._theme_group.addButton(radio)
            self._theme_radios[key] = radio
            layout.addWidget(radio)

        layout.addStretch()
        return bar

    def _on_theme_selected(self, key: str) -> None:
        apply_theme(key)
        # Sync settings screen if the admin tab is open
        if hasattr(self._admin, "_sync_theme_radios"):
            self._admin._sync_theme_radios(key)

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
        """Subject picked — show session history before starting a new recording."""
        logger.info("Subject selected: %s", subject.subject_code)
        self._session_history.load_subject(subject)
        self._stack.setCurrentIndex(IDX_SESSION_HISTORY)

    def start_recording(self, subject: Subject) -> None:
        """Called by SessionHistoryScreen 'New Session' button."""
        logger.info("Starting new recording session for: %s", subject.subject_code)
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

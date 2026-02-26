"""Admin dashboard — tabbed interface for admin functions."""
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton, QLabel
)
from app.ui.screens.admin.user_management_screen import UserManagementScreen
from app.ui.screens.admin.subject_browser_screen import SubjectBrowserScreen
from app.ui.screens.admin.settings_screen import SettingsScreen
from app.auth.auth_service import current_user

logger = logging.getLogger(__name__)


class AdminDashboardScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        header = QHBoxLayout()
        title = QLabel("Admin Dashboard")
        title.setObjectName("screen_title")
        self.lbl_user = QLabel()
        btn_logout = QPushButton("Logout")
        btn_logout.setObjectName("btn_danger")
        btn_logout.clicked.connect(self._on_logout)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.lbl_user)
        header.addWidget(btn_logout)
        layout.addLayout(header)

        self.tabs = QTabWidget()
        self.tab_users = UserManagementScreen()
        self.tab_subjects = SubjectBrowserScreen()
        self.tab_settings = SettingsScreen()

        self.tabs.addTab(self.tab_users, "Users")
        self.tabs.addTab(self.tab_subjects, "Subjects")
        self.tabs.addTab(self.tab_settings, "Settings")
        self.tabs.currentChanged.connect(self._on_tab_changed)

        layout.addWidget(self.tabs)

    def refresh(self) -> None:
        user = current_user()
        if user:
            self.lbl_user.setText(f"Logged in as: {user.username}")
        self.tab_users.refresh()
        self.tab_subjects.refresh()
        self.tab_settings.refresh()

    def _on_tab_changed(self, index: int) -> None:
        if index == 0:
            self.tab_users.refresh()
        elif index == 1:
            self.tab_subjects.refresh()
        elif index == 2:
            self.tab_settings.refresh()

    def _sync_theme_radios(self, key: str) -> None:
        """Propagate theme change to the settings tab radio buttons."""
        self.tab_settings._sync_theme_radios(key)

    def _on_logout(self) -> None:
        mw = self.window()
        if hasattr(mw, "logout"):
            mw.logout()

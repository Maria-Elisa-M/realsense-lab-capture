"""Login screen."""
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from app.auth import auth_service

logger = logging.getLogger(__name__)


class LoginScreen(QWidget):
    login_successful = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QWidget()
        card.setObjectName("login_card")
        card.setFixedWidth(360)
        layout = QVBoxLayout(card)
        layout.setSpacing(12)
        layout.setContentsMargins(32, 32, 32, 32)

        title = QLabel("RealSense Lab Capture")
        title.setObjectName("screen_title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("Username")
        self.input_username.returnPressed.connect(self._on_login)

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Password")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.returnPressed.connect(self._on_login)

        self.btn_login = QPushButton("Login")
        self.btn_login.setObjectName("btn_primary")
        self.btn_login.clicked.connect(self._on_login)

        self.lbl_error = QLabel()
        self.lbl_error.setObjectName("error_label")
        self.lbl_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_error.setVisible(False)

        layout.addWidget(QLabel("Username"))
        layout.addWidget(self.input_username)
        layout.addWidget(QLabel("Password"))
        layout.addWidget(self.input_password)
        layout.addWidget(self.lbl_error)
        layout.addWidget(self.btn_login)

        outer.addWidget(card)

    def _on_login(self) -> None:
        username = self.input_username.text().strip()
        password = self.input_password.text()

        if not username or not password:
            self._show_error("Please enter username and password.")
            return

        user = auth_service.authenticate(username, password)
        if user is None:
            self._show_error("Invalid username or password.")
            self.input_password.clear()
            return

        auth_service.login(user)
        self.lbl_error.setVisible(False)
        logger.info("Login screen: user '%s' logged in.", username)
        self.login_successful.emit()

    def _show_error(self, msg: str) -> None:
        self.lbl_error.setText(msg)
        self.lbl_error.setVisible(True)

    def clear(self) -> None:
        self.input_username.clear()
        self.input_password.clear()
        self.lbl_error.setVisible(False)

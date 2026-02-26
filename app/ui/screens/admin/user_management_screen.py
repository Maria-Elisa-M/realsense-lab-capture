"""Admin tab: User management."""
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QLineEdit, QComboBox,
    QDialogButtonBox, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt
import app.database.repositories.user_repository as user_repo
from app.auth.auth_service import create_user, change_password, current_user
from app.utils.validators import validate_username, validate_password
from app.database.models import User

logger = logging.getLogger(__name__)


class UserManagementScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._users: list[User] = []
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_add = QPushButton("+ Add User")
        btn_add.setObjectName("btn_secondary")
        btn_add.clicked.connect(self._on_add_user)
        btn_row.addWidget(btn_add)
        layout.addLayout(btn_row)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Username", "Role", "Active", "Actions"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

    def refresh(self) -> None:
        self._users = user_repo.list_all()
        self.table.setRowCount(len(self._users))
        for row, user in enumerate(self._users):
            self.table.setItem(row, 0, QTableWidgetItem(str(user.id)))
            self.table.setItem(row, 1, QTableWidgetItem(user.username))
            self.table.setItem(row, 2, QTableWidgetItem(user.role))
            self.table.setItem(row, 3, QTableWidgetItem("Yes" if user.is_active else "No"))

            actions = QWidget()
            act_layout = QHBoxLayout(actions)
            act_layout.setContentsMargins(2, 2, 2, 2)

            btn_pw = QPushButton("Change PW")
            btn_pw.clicked.connect(lambda checked, u=user: self._change_password(u))

            btn_toggle = QPushButton("Deactivate" if user.is_active else "Activate")
            btn_toggle.clicked.connect(lambda checked, u=user: self._toggle_active(u))

            # Prevent deactivating yourself or the last admin
            me = current_user()
            if me and user.id == me.id:
                btn_toggle.setEnabled(False)
                btn_toggle.setToolTip("Cannot deactivate your own account")

            act_layout.addWidget(btn_pw)
            act_layout.addWidget(btn_toggle)
            self.table.setCellWidget(row, 4, actions)

    def _on_add_user(self) -> None:
        dlg = AddUserDialog(self)
        if dlg.exec():
            self.refresh()

    def _change_password(self, user: User) -> None:
        dlg = ChangePasswordDialog(user, self)
        if dlg.exec():
            self.refresh()

    def _toggle_active(self, user: User) -> None:
        action = "deactivate" if user.is_active else "activate"
        reply = QMessageBox.question(
            self, f"Confirm {action.capitalize()}",
            f"Are you sure you want to {action} user '{user.username}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            user_repo.set_active(user.id, not user.is_active)
            self.refresh()


class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add User")
        self.setMinimumWidth(360)
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.input_username = QLineEdit()
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.combo_role = QComboBox()
        self.combo_role.addItems(["operator", "admin"])

        form.addRow("Username:", self.input_username)
        form.addRow("Password:", self.input_password)
        form.addRow("Role:", self.combo_role)
        layout.addLayout(form)

        self.lbl_error = QLabel()
        self.lbl_error.setObjectName("error_label")
        self.lbl_error.setVisible(False)
        layout.addWidget(self.lbl_error)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_accept(self) -> None:
        username = self.input_username.text().strip()
        password = self.input_password.text()
        role = self.combo_role.currentText()

        err = validate_username(username) or validate_password(password)
        if err:
            self.lbl_error.setText(err)
            self.lbl_error.setVisible(True)
            return

        if user_repo.get_by_username(username):
            self.lbl_error.setText(f"Username '{username}' is already taken.")
            self.lbl_error.setVisible(True)
            return

        create_user(username, password, role)
        logger.info("Admin created user '%s' (%s)", username, role)
        self.accept()


class ChangePasswordDialog(QDialog):
    def __init__(self, user: User, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Change Password — {user.username}")
        self._user = user
        self.setMinimumWidth(320)
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.input_new = QLineEdit()
        self.input_new.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_confirm = QLineEdit()
        self.input_confirm.setEchoMode(QLineEdit.EchoMode.Password)

        form.addRow("New Password:", self.input_new)
        form.addRow("Confirm:", self.input_confirm)
        layout.addLayout(form)

        self.lbl_error = QLabel()
        self.lbl_error.setObjectName("error_label")
        self.lbl_error.setVisible(False)
        layout.addWidget(self.lbl_error)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_accept(self) -> None:
        pw = self.input_new.text()
        confirm = self.input_confirm.text()
        from app.utils.validators import validate_password
        err = validate_password(pw)
        if err:
            self.lbl_error.setText(err)
            self.lbl_error.setVisible(True)
            return
        if pw != confirm:
            self.lbl_error.setText("Passwords do not match.")
            self.lbl_error.setVisible(True)
            return
        change_password(self._user.id, pw)
        self.accept()

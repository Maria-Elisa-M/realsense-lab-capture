"""Dialog for creating a new subject."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QTextEdit, QLabel, QDialogButtonBox
)
from app.utils.validators import validate_subject_code
import app.database.repositories.subject_repository as subject_repo
from app.auth.auth_service import current_user
from app.database.models import Subject


class SubjectFormDialog(QDialog):
    """Modal dialog to add a new subject.

    On accept(), the new Subject is available via .created_subject.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Subject")
        self.setMinimumWidth(380)
        self.created_subject: Subject | None = None

        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.input_code = QLineEdit()
        self.input_code.setPlaceholderText("e.g. P001, subject-42, JD_2026")
        self.input_notes = QTextEdit()
        self.input_notes.setPlaceholderText("Optional notes")
        self.input_notes.setMaximumHeight(80)

        form.addRow("Subject ID*:", self.input_code)
        form.addRow("Notes:", self.input_notes)
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
        code = self.input_code.text().strip()
        notes = self.input_notes.toPlainText().strip() or None

        err = validate_subject_code(code)
        if err:
            self._show_error(err)
            return

        if subject_repo.get_by_code(code):
            self._show_error(f"Subject ID '{code}' already exists.")
            return

        user = current_user()
        if user is None:
            self._show_error("Not authenticated.")
            return

        self.created_subject = subject_repo.create(code, user.id, notes)
        self.accept()

    def _show_error(self, message: str) -> None:
        self.lbl_error.setText(message)
        self.lbl_error.setVisible(True)

"""Admin tab: Subject browser with edit capability."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QTextEdit,
    QDialogButtonBox, QLabel, QLineEdit
)
import app.database.repositories.subject_repository as subject_repo
from app.ui.widgets.subject_form_widget import SubjectFormDialog
from app.database.models import Subject


class SubjectBrowserScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._subjects: list[Subject] = []
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        toolbar = QHBoxLayout()
        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("Search by ID…")
        self.input_search.textChanged.connect(self._on_search)
        btn_new = QPushButton("+ New Subject")
        btn_new.setObjectName("btn_secondary")
        btn_new.clicked.connect(self._on_new_subject)
        toolbar.addWidget(self.input_search)
        toolbar.addWidget(btn_new)
        layout.addLayout(toolbar)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Subject ID", "Created", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

    def refresh(self) -> None:
        self._load_subjects("")
        self.input_search.clear()

    def _on_search(self, text: str) -> None:
        self._load_subjects(text.strip())

    def _load_subjects(self, query: str) -> None:
        self._subjects = subject_repo.search(query) if query else subject_repo.list_all()
        self.table.setRowCount(len(self._subjects))
        for row, s in enumerate(self._subjects):
            self.table.setItem(row, 0, QTableWidgetItem(str(s.id)))
            self.table.setItem(row, 1, QTableWidgetItem(s.subject_code))
            self.table.setItem(row, 2, QTableWidgetItem(s.created_at[:10]))

            btn_edit = QPushButton("Edit Notes")
            btn_edit.clicked.connect(lambda checked, subj=s: self._edit_subject(subj))
            self.table.setCellWidget(row, 3, btn_edit)

    def _on_new_subject(self) -> None:
        dlg = SubjectFormDialog(self)
        if dlg.exec():
            self._load_subjects(self.input_search.text().strip())

    def _edit_subject(self, subject: Subject) -> None:
        dlg = EditSubjectDialog(subject, self)
        if dlg.exec():
            self._load_subjects(self.input_search.text().strip())


class EditSubjectDialog(QDialog):
    def __init__(self, subject: Subject, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Edit Subject — {subject.subject_code}")
        self._subject = subject
        self.setMinimumWidth(380)
        layout = QVBoxLayout(self)
        form = QFormLayout()

        form.addRow("Subject ID:", QLabel(subject.subject_code))
        self.input_notes = QTextEdit(subject.notes or "")
        self.input_notes.setMaximumHeight(100)
        form.addRow("Notes:", self.input_notes)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_accept(self) -> None:
        notes = self.input_notes.toPlainText().strip() or None
        subject_repo.update(self._subject.id, notes)
        self.accept()

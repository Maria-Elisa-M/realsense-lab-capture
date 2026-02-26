"""Admin tab: Subject browser with edit capability and session viewer."""
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QTextEdit,
    QDialogButtonBox, QLabel, QLineEdit
)
from PyQt6.QtGui import QColor
import app.database.repositories.subject_repository as subject_repo
import app.database.repositories.session_repository as session_repo
from app.ui.widgets.subject_form_widget import SubjectFormDialog
from app.database.models import Subject
from app.utils.viewer_utils import open_in_app_viewer


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

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Subject ID", "Created", "Sessions", "Actions"]
        )
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 45)
        self.table.setColumnWidth(2, 105)
        self.table.setColumnWidth(3, 75)
        self.table.setColumnWidth(4, 250)
        vh = self.table.verticalHeader()
        vh.setDefaultSectionSize(46)
        vh.setMinimumSectionSize(46)
        vh.setVisible(False)
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

            sessions = session_repo.list_for_subject(s.id)
            self.table.setItem(row, 3, QTableWidgetItem(str(len(sessions))))

            btn_row = QHBoxLayout()
            btn_row.setContentsMargins(2, 2, 2, 2)
            btn_row.setSpacing(4)

            btn_sessions = QPushButton("View Sessions")
            btn_sessions.setObjectName("btn_secondary")
            btn_sessions.clicked.connect(
                lambda checked, subj=s: self._view_sessions(subj)
            )

            btn_edit = QPushButton("Edit")
            btn_edit.clicked.connect(
                lambda checked, subj=s: self._edit_subject(subj)
            )

            cell_widget = QWidget()
            cell_layout = QHBoxLayout(cell_widget)
            cell_layout.setContentsMargins(4, 4, 4, 4)
            cell_layout.setSpacing(6)
            cell_layout.addWidget(btn_sessions)
            cell_layout.addWidget(btn_edit)
            self.table.setCellWidget(row, 4, cell_widget)

        self.table.resizeRowsToContents()

    def _on_new_subject(self) -> None:
        dlg = SubjectFormDialog(self)
        if dlg.exec():
            self._load_subjects(self.input_search.text().strip())

    def _edit_subject(self, subject: Subject) -> None:
        dlg = EditSubjectDialog(subject, self)
        if dlg.exec():
            self._load_subjects(self.input_search.text().strip())

    def _view_sessions(self, subject: Subject) -> None:
        dlg = SubjectSessionsDialog(subject, self)
        dlg.exec()


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


class SubjectSessionsDialog(QDialog):
    """Dialog showing all sessions and recordings for a subject, with Open in Viewer."""

    def __init__(self, subject: Subject, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Sessions — {subject.subject_code}")
        self.setMinimumSize(900, 480)
        self._subject = subject
        self._build_ui()
        self._populate()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        lbl = QLabel(f"All recorded sessions for subject: {self._subject.subject_code}")
        lbl.setObjectName("subject_label")
        layout.addWidget(lbl)

        # Columns: Session | Date | Operator | Type | Duration | Size | File Path | Open
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "Session", "Date", "Operator", "Type", "Duration", "Size", "File Path", ""
        ])
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        for col, w in [(0, 65), (1, 150), (2, 105), (3, 105), (4, 80), (5, 80), (7, 140)]:
            self.table.setColumnWidth(col, w)
        vh = self.table.verticalHeader()
        vh.setDefaultSectionSize(46)
        vh.setMinimumSectionSize(46)
        vh.setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        close_btn = QPushButton("Close")
        close_btn.setObjectName("btn_secondary")
        close_btn.clicked.connect(self.accept)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    def _populate(self) -> None:
        rows = session_repo.list_with_recordings_for_subject(self._subject.id)

        seen_sessions: dict[int, int] = {}
        color_even = QColor("#1a2a50")
        color_odd  = QColor("#16213e")

        for data in rows:
            if data["rec_id"] is None:
                continue

            sid = data["session_id"]
            if sid not in seen_sessions:
                seen_sessions[sid] = len(seen_sessions) % 2

            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)

            bg = color_even if seen_sessions[sid] == 0 else color_odd

            def _item(text: str) -> QTableWidgetItem:
                it = QTableWidgetItem(text)
                it.setBackground(bg)
                return it

            dur = (
                f"{data['duration_seconds']:.1f}s"
                if data["duration_seconds"] is not None else "—"
            )
            size = (
                f"{data['file_size_bytes'] / (1024*1024):.1f} MB"
                if data["file_size_bytes"] is not None else "—"
            )
            date_str = (data["session_started"] or "")[:16].replace("T", " ")
            rec_type  = (data["recording_type"] or "").capitalize()

            self.table.setItem(row_idx, 0, _item(str(sid)))
            self.table.setItem(row_idx, 1, _item(date_str))
            self.table.setItem(row_idx, 2, _item(data["operator"] or ""))
            self.table.setItem(row_idx, 3, _item(rec_type))
            self.table.setItem(row_idx, 4, _item(dur))
            self.table.setItem(row_idx, 5, _item(size))
            self.table.setItem(row_idx, 6, _item(data["file_path"] or ""))

            file_path = data["file_path"] or ""
            btn_open = QPushButton("Open in Viewer")
            btn_open.setObjectName("btn_secondary")
            btn_open.setEnabled(bool(file_path) and os.path.exists(file_path))
            btn_open.clicked.connect(
                lambda checked, fp=file_path: open_in_app_viewer(fp, self)
            )
            self.table.setCellWidget(row_idx, 7, btn_open)

        self.table.resizeRowsToContents()
        if not seen_sessions:
            no_data = QLabel("No recordings found for this subject.")
            no_data.setStyleSheet("color: #888888; padding: 16px;")
            self.table.hide()
            self.layout().insertWidget(1, no_data)

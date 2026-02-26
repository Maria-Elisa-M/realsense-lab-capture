"""Session review screen — shown after a session is completed."""
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
import app.database.repositories.recording_repository as recording_repo
from app.database.models import Session, Subject


class SessionReviewScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._session: Session | None = None
        self._subject: Subject | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(12)

        title = QLabel("Session Summary")
        title.setObjectName("screen_title")
        layout.addWidget(title)

        self.lbl_info = QLabel()
        layout.addWidget(self.lbl_info)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Type", "Started", "Duration (s)", "File Size", "File Path"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.ResizeMode.Stretch
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_new_session = QPushButton("New Session")
        self.btn_new_session.setObjectName("btn_primary")
        self.btn_new_session.clicked.connect(self._go_new_session)
        btn_row.addWidget(self.btn_new_session)

        self.btn_logout = QPushButton("Logout")
        self.btn_logout.setObjectName("btn_secondary")
        self.btn_logout.clicked.connect(self._go_logout)
        btn_row.addWidget(self.btn_logout)
        layout.addLayout(btn_row)

    def load_session(self, session: Session, subject: Subject) -> None:
        self._session = session
        self._subject = subject
        self.lbl_info.setText(
            f"Subject: {subject.subject_code} — {subject.subject_name}  |  "
            f"Session ID: {session.id}  |  Started: {session.started_at}"
        )
        self._populate_table(session.id)

    def _populate_table(self, session_id: int) -> None:
        recordings = recording_repo.list_for_session(session_id)
        self.table.setRowCount(len(recordings))
        for row, rec in enumerate(recordings):
            size_str = ""
            if rec.file_size_bytes is not None:
                size_str = f"{rec.file_size_bytes / (1024*1024):.1f} MB"
            dur_str = f"{rec.duration_seconds:.1f}" if rec.duration_seconds else "—"
            self.table.setItem(row, 0, QTableWidgetItem(rec.recording_type.capitalize()))
            self.table.setItem(row, 1, QTableWidgetItem(rec.started_at or "—"))
            self.table.setItem(row, 2, QTableWidgetItem(dur_str))
            self.table.setItem(row, 3, QTableWidgetItem(size_str))
            self.table.setItem(row, 4, QTableWidgetItem(rec.file_path))

    def _go_new_session(self) -> None:
        mw = self.window()
        if hasattr(mw, "go_subject_select"):
            mw.go_subject_select()

    def _go_logout(self) -> None:
        mw = self.window()
        if hasattr(mw, "logout"):
            mw.logout()

"""Session history screen — shows past sessions and recordings for a subject."""
import os
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

import app.database.repositories.session_repository as session_repo
from app.database.models import Subject
from app.utils.viewer_utils import open_in_app_viewer

logger = logging.getLogger(__name__)


class SessionHistoryScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._subject: Subject | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(12)

        header_row = QHBoxLayout()
        self.lbl_title = QLabel("Session History")
        self.lbl_title.setObjectName("screen_title")
        header_row.addWidget(self.lbl_title)
        header_row.addStretch()
        layout.addLayout(header_row)

        self.lbl_subject = QLabel()
        self.lbl_subject.setObjectName("subject_label")
        layout.addWidget(self.lbl_subject)

        self.lbl_hint = QLabel(
            "Previous recordings for this subject are listed below. "
            "Click 'Open in Viewer' to review a recording, or 'New Session' to record again."
        )
        self.lbl_hint.setStyleSheet("color: #8899bb; font-size: 11px;")
        self.lbl_hint.setWordWrap(True)
        layout.addWidget(self.lbl_hint)

        # Columns: Session | Date | Operator | Type | Duration | File Size | File Path | Open
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "Session", "Date", "Operator", "Type", "Duration", "Size", "File Path", ""
        ])
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        for col, w in [(0, 70), (1, 160), (2, 105), (3, 105), (4, 80), (5, 80), (7, 140)]:
            self.table.setColumnWidth(col, w)
        vh = self.table.verticalHeader()
        vh.setDefaultSectionSize(46)
        vh.setMinimumSectionSize(46)
        vh.setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        btn_row = QHBoxLayout()
        btn_back = QPushButton("← Back")
        btn_back.setObjectName("btn_secondary")
        btn_back.clicked.connect(self._go_back)
        btn_row.addWidget(btn_back)
        btn_row.addStretch()

        self.btn_new_session = QPushButton("New Session")
        self.btn_new_session.setObjectName("btn_primary")
        self.btn_new_session.clicked.connect(self._go_new_session)
        btn_row.addWidget(self.btn_new_session)
        layout.addLayout(btn_row)

    def load_subject(self, subject: Subject) -> None:
        """Load and display all sessions + recordings for the given subject."""
        self._subject = subject
        self.lbl_title.setText("Session History")
        self.lbl_subject.setText(f"Subject: {subject.subject_code}")
        self._populate_table(subject.id)

    def _populate_table(self, subject_id: int) -> None:
        rows = session_repo.list_with_recordings_for_subject(subject_id)
        self.table.setRowCount(0)

        if not rows:
            self.lbl_hint.setText(
                "No previous sessions found. Click 'New Session' to start recording."
            )
            return

        self.lbl_hint.setText(
            "Previous recordings for this subject are listed below. "
            "Click 'Open in Viewer' to review a recording, or 'New Session' to record again."
        )

        # Track session rows for alternating session background
        seen_sessions: dict[int, int] = {}  # session_id → color_index
        color_even = QColor("#1a2a50")
        color_odd = QColor("#16213e")

        for data in rows:
            # Skip rows where there's no recording
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
            rec_type = (data["recording_type"] or "").capitalize()

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

    def _go_new_session(self) -> None:
        mw = self.window()
        if hasattr(mw, "start_recording") and self._subject:
            mw.start_recording(self._subject)

    def _go_back(self) -> None:
        mw = self.window()
        if hasattr(mw, "go_subject_select"):
            mw.go_subject_select()

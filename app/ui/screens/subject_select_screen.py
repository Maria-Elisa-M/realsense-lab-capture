"""Subject selection screen — search, pick, or create a subject."""
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
import app.database.repositories.subject_repository as subject_repo
from app.ui.widgets.subject_form_widget import SubjectFormDialog
from app.database.models import Subject

logger = logging.getLogger(__name__)


class SubjectSelectScreen(QWidget):
    subject_selected = pyqtSignal(object)  # Subject

    def __init__(self, parent=None):
        super().__init__(parent)
        self._subjects: list[Subject] = []
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(12)

        title = QLabel("Select Subject")
        title.setObjectName("screen_title")
        layout.addWidget(title)

        search_row = QHBoxLayout()
        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("Search by name or code…")
        self.input_search.textChanged.connect(self._on_search)
        btn_new = QPushButton("+ New Subject")
        btn_new.setObjectName("btn_secondary")
        btn_new.clicked.connect(self._on_new_subject)
        search_row.addWidget(self.input_search)
        search_row.addWidget(btn_new)
        layout.addLayout(search_row)

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.list_widget)

        self.lbl_hint = QLabel("Double-click a subject or select and click Start Session")
        self.lbl_hint.setStyleSheet("color: #666666; font-size: 11px;")
        layout.addWidget(self.lbl_hint)

        btn_row = QHBoxLayout()
        btn_logout = QPushButton("Logout")
        btn_logout.setObjectName("btn_danger")
        btn_logout.clicked.connect(self._on_logout)
        btn_row.addWidget(btn_logout)
        btn_row.addStretch()
        self.btn_select = QPushButton("Start Session")
        self.btn_select.setObjectName("btn_primary")
        self.btn_select.clicked.connect(self._on_select)
        btn_row.addWidget(self.btn_select)
        layout.addLayout(btn_row)

    def refresh(self) -> None:
        """Reload subjects from DB and reset search."""
        self.input_search.clear()
        self._load_subjects("")

    def _load_subjects(self, query: str) -> None:
        if query:
            self._subjects = subject_repo.search(query)
        else:
            self._subjects = subject_repo.list_all()
        self.list_widget.clear()
        for s in self._subjects:
            item = QListWidgetItem(s.subject_code)
            item.setData(Qt.ItemDataRole.UserRole, s)
            self.list_widget.addItem(item)

    def _on_search(self, text: str) -> None:
        self._load_subjects(text.strip())

    def _on_select(self) -> None:
        item = self.list_widget.currentItem()
        if item is None:
            QMessageBox.warning(self, "No Selection", "Please select a subject.")
            return
        subject: Subject = item.data(Qt.ItemDataRole.UserRole)
        self.subject_selected.emit(subject)

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        subject: Subject = item.data(Qt.ItemDataRole.UserRole)
        self.subject_selected.emit(subject)

    def _on_logout(self) -> None:
        mw = self.window()
        if hasattr(mw, "logout"):
            mw.logout()

    def _on_new_subject(self) -> None:
        dlg = SubjectFormDialog(self)
        if dlg.exec() and dlg.created_subject:
            self._load_subjects(self.input_search.text().strip())
            logger.info("New subject created: %s", dlg.created_subject.subject_code)
            # Auto-select the new subject and proceed directly to recording
            self.subject_selected.emit(dlg.created_subject)

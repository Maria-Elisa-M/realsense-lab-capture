"""Camera preview widget — displays live QImage frames scaled to fit."""
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QImage, QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import Qt


class CameraPreviewWidget(QLabel):
    """Displays camera frames scaled to fit. Supports overlay messages."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(640, 360)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: #0d0d1a; color: #888888;")
        self.setText("No camera feed")
        self._last_pixmap: QPixmap | None = None
        self._overlay_text: str = ""

    def set_frame(self, image: QImage) -> None:
        """Update the displayed frame."""
        self._overlay_text = ""
        pixmap = QPixmap.fromImage(image)
        self._last_pixmap = pixmap
        self._render()

    def show_no_signal(self, message: str = "No camera feed") -> None:
        self._last_pixmap = None
        self._overlay_text = ""
        self.clear()
        self.setText(message)

    def show_recording(self, recording_type: str) -> None:
        """Show a 'recording in progress' overlay on the last frame (or black)."""
        self._overlay_text = f"● Recording {recording_type.capitalize()}…"
        self._render()

    def _render(self) -> None:
        if self._last_pixmap is None:
            self.clear()
            self.setText(self._overlay_text or "No camera feed")
            return

        scaled = self._last_pixmap.scaled(
            self.width(), self.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        if self._overlay_text:
            result = QPixmap(scaled.size())
            result.fill(Qt.GlobalColor.transparent)
            painter = QPainter(result)
            painter.drawPixmap(0, 0, scaled)
            # Semi-transparent red bar at top
            painter.fillRect(0, 0, result.width(), 36,
                             QColor(180, 20, 20, 200))
            painter.setPen(QColor(255, 255, 255))
            font = QFont()
            font.setBold(True)
            font.setPointSize(12)
            painter.setFont(font)
            painter.drawText(result.rect(), Qt.AlignmentFlag.AlignTop |
                             Qt.AlignmentFlag.AlignHCenter, self._overlay_text)
            painter.end()
            self.setPixmap(result)
        else:
            self.setPixmap(scaled)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._last_pixmap:
            self._render()

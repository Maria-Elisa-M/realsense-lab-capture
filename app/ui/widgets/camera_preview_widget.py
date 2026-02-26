"""Camera preview widget — displays live QImage frames scaled to fit."""
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt


class CameraPreviewWidget(QLabel):
    """QLabel subclass that displays camera frames, scaled to fit while keeping aspect ratio."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(640, 360)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: #1a1a2e; color: #888888;")
        self.setText("No camera feed")
        self._no_signal = True

    def set_frame(self, image: QImage) -> None:
        """Update the displayed frame."""
        if self._no_signal:
            self._no_signal = False
        pixmap = QPixmap.fromImage(image)
        scaled = pixmap.scaled(
            self.width(), self.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.setPixmap(scaled)

    def show_no_signal(self, message: str = "No camera feed") -> None:
        self._no_signal = True
        self.clear()
        self.setText(message)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Re-scale current pixmap on resize
        if not self._no_signal and self.pixmap() and not self.pixmap().isNull():
            scaled = self.pixmap().scaled(
                self.width(), self.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.setPixmap(scaled)

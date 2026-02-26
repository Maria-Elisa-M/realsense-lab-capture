"""Launch Intel RealSense Viewer with a .bag file."""
import os
import subprocess
import logging
from PyQt6.QtWidgets import QMessageBox

logger = logging.getLogger(__name__)

_VIEWER_CANDIDATES = [
    r"C:\Program Files (x86)\Intel RealSense SDK 2.0\tools\realsense-viewer.exe",
    r"C:\Program Files\Intel RealSense SDK 2.0\tools\realsense-viewer.exe",
    r"C:\Program Files (x86)\Intel RealSense SDK 2.0\bin\realsense-viewer.exe",
    r"C:\Program Files\Intel RealSense SDK 2.0\bin\realsense-viewer.exe",
]


def _find_viewer() -> str | None:
    for path in _VIEWER_CANDIDATES:
        if os.path.exists(path):
            return path
    # Fall back to PATH
    try:
        result = subprocess.run(
            ["where", "realsense-viewer"], capture_output=True, text=True
        )
        if result.returncode == 0:
            return result.stdout.strip().splitlines()[0]
    except Exception:
        pass
    return None


def open_in_viewer(file_path: str, parent=None) -> None:
    """Open *file_path* in the Intel RealSense Viewer.

    Shows a user-friendly error dialog if the viewer or file is not found.
    """
    if not os.path.exists(file_path):
        QMessageBox.warning(
            parent, "File Not Found",
            f"Recording file not found:\n{file_path}"
        )
        return

    viewer = _find_viewer()
    if viewer is None:
        QMessageBox.warning(
            parent, "Viewer Not Found",
            "Intel RealSense Viewer could not be found.\n\n"
            "Please install the Intel RealSense SDK 2.0 from:\n"
            "https://github.com/IntelRealSense/librealsense/releases"
        )
        return

    try:
        subprocess.Popen([viewer, file_path])
        logger.info("Opened viewer: %s -> %s", viewer, file_path)
    except Exception as exc:
        logger.error("Failed to launch viewer: %s", exc)
        QMessageBox.critical(parent, "Error", f"Could not launch viewer:\n{exc}")


def open_in_app_viewer(file_path: str, parent=None) -> None:
    """Open *file_path* in the built-in bag viewer dialog."""
    if not os.path.exists(file_path):
        QMessageBox.warning(
            parent, "File Not Found",
            f"Recording file not found:\n{file_path}"
        )
        return

    from app.ui.widgets.bag_viewer_dialog import BagViewerDialog
    dlg = BagViewerDialog(file_path, parent)
    dlg.exec()

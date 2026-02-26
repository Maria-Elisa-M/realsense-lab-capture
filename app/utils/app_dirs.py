"""Resolve user-writable directories for data and logs.

On Windows, Program Files is read-only for normal users, so the database
and logs must live in %APPDATA%/RealSense Lab Capture/ instead.
"""
import os
from pathlib import Path

APP_NAME = "RealSense Lab Capture"


def _app_data_root() -> Path:
    """Return %APPDATA%/RealSense Lab Capture on Windows, ~/.<app> elsewhere."""
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / APP_NAME
    return Path.home() / f".{APP_NAME.lower().replace(' ', '_')}"


APP_DATA_DIR = _app_data_root()
LOG_DIR = APP_DATA_DIR / "logs"
DB_DIR = APP_DATA_DIR / "data"

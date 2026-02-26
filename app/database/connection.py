"""Database connection factory with WAL mode and foreign key enforcement."""
import sqlite3
from pathlib import Path
from app.utils.app_dirs import DB_DIR

DB_PATH = DB_DIR / "video_capture.db"


def get_connection() -> sqlite3.Connection:
    """Open a new SQLite connection with WAL journal mode and foreign keys enabled."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

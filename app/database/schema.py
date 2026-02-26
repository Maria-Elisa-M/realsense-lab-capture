"""Database schema initialization and seeding."""
import logging
import sqlite3
import bcrypt
from app.database.connection import get_connection

logger = logging.getLogger(__name__)

DDL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'operator')),
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_name TEXT,
    subject_code TEXT NOT NULL UNIQUE,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    created_by INTEGER NOT NULL REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL REFERENCES subjects(id),
    operator_id INTEGER NOT NULL REFERENCES users(id),
    started_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    ended_at TEXT
);

CREATE TABLE IF NOT EXISTS recordings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL REFERENCES sessions(id),
    recording_type TEXT NOT NULL CHECK(recording_type IN ('calibration', 'data')),
    file_path TEXT NOT NULL,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    duration_seconds REAL,
    file_size_bytes INTEGER,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);
"""

DEFAULT_SETTINGS = [
    ("output_directory", "C:/Users/marie/video_capture/recordings",
     "Root directory for storing .bag recordings"),
    ("color_width", "1280", "Color stream width in pixels"),
    ("color_height", "720", "Color stream height in pixels"),
    ("color_fps", "30", "Color stream frames per second"),
    ("depth_width", "1280", "Depth stream width in pixels"),
    ("depth_height", "720", "Depth stream height in pixels"),
    ("depth_fps", "30", "Depth stream frames per second"),
    ("infrared_width", "1280", "Infrared stream width in pixels"),
    ("infrared_height", "720", "Infrared stream height in pixels"),
    ("infrared_fps", "30", "Infrared stream frames per second"),
    ("preview_fps", "15", "Preview display frames per second"),
]


def init_db() -> None:
    """Create all tables and seed default data if not already present."""
    conn = get_connection()
    try:
        conn.executescript(DDL)
        conn.commit()
        _seed_admin(conn)
        _seed_settings(conn)
        conn.commit()
        logger.info("Database initialized successfully.")
    finally:
        conn.close()


def _seed_admin(conn: sqlite3.Connection) -> None:
    """Insert default admin user if no admin exists."""
    row = conn.execute("SELECT id FROM users WHERE role='admin' LIMIT 1").fetchone()
    if row is None:
        pw_hash = bcrypt.hashpw(b"admin", bcrypt.gensalt()).decode()
        conn.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'admin')",
            ("admin", pw_hash),
        )
        logger.info("Default admin user seeded (username='admin', password='admin').")


def _seed_settings(conn: sqlite3.Connection) -> None:
    """Insert default settings rows if they don't exist."""
    for key, value, description in DEFAULT_SETTINGS:
        conn.execute(
            "INSERT OR IGNORE INTO settings (key, value, description) VALUES (?, ?, ?)",
            (key, value, description),
        )

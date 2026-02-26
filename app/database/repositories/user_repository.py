"""CRUD operations for the users table."""
import sqlite3
from typing import Optional, List
from app.database.connection import get_connection
from app.database.models import User


def _row_to_user(row: sqlite3.Row) -> User:
    return User(
        id=row["id"],
        username=row["username"],
        password_hash=row["password_hash"],
        role=row["role"],
        is_active=bool(row["is_active"]),
        created_at=row["created_at"],
    )


def get_by_username(username: str) -> Optional[User]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        return _row_to_user(row) if row else None
    finally:
        conn.close()


def get_by_id(user_id: int) -> Optional[User]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return _row_to_user(row) if row else None
    finally:
        conn.close()


def list_all() -> List[User]:
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM users ORDER BY username").fetchall()
        return [_row_to_user(r) for r in rows]
    finally:
        conn.close()


def create(username: str, password_hash: str, role: str) -> User:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return _row_to_user(row)
    finally:
        conn.close()


def update_password(user_id: int, password_hash: str) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (password_hash, user_id),
        )
        conn.commit()
    finally:
        conn.close()


def set_active(user_id: int, is_active: bool) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE users SET is_active = ? WHERE id = ?",
            (int(is_active), user_id),
        )
        conn.commit()
    finally:
        conn.close()


def update_role(user_id: int, role: str) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE users SET role = ? WHERE id = ?",
            (role, user_id),
        )
        conn.commit()
    finally:
        conn.close()

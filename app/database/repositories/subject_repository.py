"""CRUD operations for the subjects table."""
import sqlite3
from typing import Optional, List
from app.database.connection import get_connection
from app.database.models import Subject


def _row_to_subject(row: sqlite3.Row) -> Subject:
    return Subject(
        id=row["id"],
        subject_code=row["subject_code"],
        subject_name=row["subject_name"],
        notes=row["notes"],
        created_at=row["created_at"],
        created_by=row["created_by"],
    )


def get_by_id(subject_id: int) -> Optional[Subject]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM subjects WHERE id = ?", (subject_id,)
        ).fetchone()
        return _row_to_subject(row) if row else None
    finally:
        conn.close()


def get_by_code(subject_code: str) -> Optional[Subject]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM subjects WHERE subject_code = ?", (subject_code,)
        ).fetchone()
        return _row_to_subject(row) if row else None
    finally:
        conn.close()


def list_all() -> List[Subject]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM subjects ORDER BY subject_code"
        ).fetchall()
        return [_row_to_subject(r) for r in rows]
    finally:
        conn.close()


def create(subject_code: str, created_by: int,
           notes: Optional[str] = None) -> Subject:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO subjects (subject_code, notes, created_by) VALUES (?, ?, ?)",
            (subject_code, notes, created_by),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM subjects WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return _row_to_subject(row)
    finally:
        conn.close()


def update(subject_id: int, notes: Optional[str]) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE subjects SET notes = ? WHERE id = ?",
            (notes, subject_id),
        )
        conn.commit()
    finally:
        conn.close()


def search(query: str) -> List[Subject]:
    conn = get_connection()
    try:
        pattern = f"%{query}%"
        rows = conn.execute(
            "SELECT * FROM subjects WHERE subject_code LIKE ? "
            "ORDER BY subject_code",
            (pattern,),
        ).fetchall()
        return [_row_to_subject(r) for r in rows]
    finally:
        conn.close()

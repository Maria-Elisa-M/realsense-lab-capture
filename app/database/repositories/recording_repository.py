"""CRUD operations for the recordings table."""
import sqlite3
import os
from typing import Optional, List
from app.database.connection import get_connection
from app.database.models import Recording


def _row_to_recording(row: sqlite3.Row) -> Recording:
    return Recording(
        id=row["id"],
        session_id=row["session_id"],
        recording_type=row["recording_type"],
        file_path=row["file_path"],
        started_at=row["started_at"],
        ended_at=row["ended_at"],
        duration_seconds=row["duration_seconds"],
        file_size_bytes=row["file_size_bytes"],
        notes=row["notes"],
    )


def create(session_id: int, recording_type: str, file_path: str,
           started_at: str) -> Recording:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO recordings (session_id, recording_type, file_path, started_at) "
            "VALUES (?, ?, ?, ?)",
            (session_id, recording_type, file_path, started_at),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM recordings WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return _row_to_recording(row)
    finally:
        conn.close()


def finalize(recording_id: int, ended_at: str, duration_seconds: float,
             file_path: str) -> None:
    """Update recording with end time, duration, and file size."""
    file_size = 0
    try:
        file_size = os.path.getsize(file_path)
    except OSError:
        pass

    conn = get_connection()
    try:
        conn.execute(
            "UPDATE recordings SET ended_at=?, duration_seconds=?, file_size_bytes=? "
            "WHERE id=?",
            (ended_at, duration_seconds, file_size, recording_id),
        )
        conn.commit()
    finally:
        conn.close()


def get_by_id(recording_id: int) -> Optional[Recording]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM recordings WHERE id = ?", (recording_id,)
        ).fetchone()
        return _row_to_recording(row) if row else None
    finally:
        conn.close()


def list_for_session(session_id: int) -> List[Recording]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM recordings WHERE session_id = ? ORDER BY started_at",
            (session_id,),
        ).fetchall()
        return [_row_to_recording(r) for r in rows]
    finally:
        conn.close()


def delete_by_id(recording_id: int) -> None:
    conn = get_connection()
    try:
        conn.execute("DELETE FROM recordings WHERE id = ?", (recording_id,))
        conn.commit()
    finally:
        conn.close()

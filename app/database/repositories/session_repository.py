"""CRUD operations for the sessions table."""
import sqlite3
from typing import Optional, List
from app.database.connection import get_connection
from app.database.models import Session


def _row_to_session(row: sqlite3.Row) -> Session:
    return Session(
        id=row["id"],
        subject_id=row["subject_id"],
        operator_id=row["operator_id"],
        started_at=row["started_at"],
        ended_at=row["ended_at"],
    )


def create(subject_id: int, operator_id: int) -> Session:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO sessions (subject_id, operator_id) VALUES (?, ?)",
            (subject_id, operator_id),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM sessions WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return _row_to_session(row)
    finally:
        conn.close()


def close_session(session_id: int) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE sessions SET ended_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now') "
            "WHERE id = ?",
            (session_id,),
        )
        conn.commit()
    finally:
        conn.close()


def get_by_id(session_id: int) -> Optional[Session]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
        return _row_to_session(row) if row else None
    finally:
        conn.close()


def list_for_subject(subject_id: int) -> List[Session]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM sessions WHERE subject_id = ? ORDER BY started_at DESC",
            (subject_id,),
        ).fetchall()
        return [_row_to_session(r) for r in rows]
    finally:
        conn.close()


def list_with_recordings_for_subject(subject_id: int) -> List[dict]:
    """Return all sessions + recordings for a subject, enriched with operator username.

    Each row in the result is a dict with keys:
      session_id, session_started, session_ended, operator,
      rec_id, recording_type, file_path, duration_seconds, file_size_bytes
    Rows with no recordings still appear (rec_id will be None).
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT
                s.id          AS session_id,
                s.started_at  AS session_started,
                s.ended_at    AS session_ended,
                u.username    AS operator,
                r.id          AS rec_id,
                r.recording_type,
                r.file_path,
                r.duration_seconds,
                r.file_size_bytes
            FROM sessions s
            JOIN users u ON u.id = s.operator_id
            LEFT JOIN recordings r ON r.session_id = s.id
            WHERE s.subject_id = ?
            ORDER BY s.started_at DESC, r.recording_type
            """,
            (subject_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

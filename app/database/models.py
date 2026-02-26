"""Dataclass models corresponding to database tables."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class User:
    id: int
    username: str
    password_hash: str
    role: str  # 'admin' | 'operator'
    is_active: bool
    created_at: str


@dataclass
class Subject:
    id: int
    subject_name: str
    subject_code: str
    notes: Optional[str]
    created_at: str
    created_by: int


@dataclass
class Session:
    id: int
    subject_id: int
    operator_id: int
    started_at: str
    ended_at: Optional[str] = None


@dataclass
class Recording:
    id: int
    session_id: int
    recording_type: str  # 'calibration' | 'data'
    file_path: str
    started_at: str
    ended_at: Optional[str] = None
    duration_seconds: Optional[float] = None
    file_size_bytes: Optional[int] = None
    notes: Optional[str] = None

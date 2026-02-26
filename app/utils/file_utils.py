"""File path utilities for building recording output paths."""
import os
from datetime import datetime
from pathlib import Path


def ensure_directory(path: str) -> str:
    """Create directory (and parents) if it doesn't exist. Returns path."""
    Path(path).mkdir(parents=True, exist_ok=True)
    return path


def build_output_path(output_dir: str, subject_code: str, session_id: int,
                      recording_type: str) -> str:
    """Return the full .bag file path for a recording.

    Pattern:
        {output_dir}/{subject_code}/session_{session_id}/
            {subject_code}_{recording_type}_{YYYYMMDD_HHMMSS}.bag
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{subject_code}_{recording_type}_{timestamp}.bag"
    session_dir = os.path.join(output_dir, subject_code, f"session_{session_id}")
    ensure_directory(session_dir)
    return os.path.join(session_dir, filename)

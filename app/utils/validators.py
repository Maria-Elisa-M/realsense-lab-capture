"""Input validation helpers."""
import re


def validate_subject_code(code: str) -> str:
    """Return error message or empty string if valid.

    Subject codes must match LAB-NNN format (e.g. LAB-001).
    """
    if not code:
        return "Subject code is required."
    if not re.match(r'^[A-Z]{2,6}-\d{3,6}$', code):
        return "Subject code must match pattern: LAB-001 (letters, dash, digits)."
    return ""


def validate_username(username: str) -> str:
    """Return error message or empty string if valid."""
    if not username:
        return "Username is required."
    if len(username) < 3:
        return "Username must be at least 3 characters."
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return "Username may only contain letters, digits, and underscores."
    return ""


def validate_password(password: str) -> str:
    """Return error message or empty string if valid."""
    if not password:
        return "Password is required."
    if len(password) < 6:
        return "Password must be at least 6 characters."
    return ""

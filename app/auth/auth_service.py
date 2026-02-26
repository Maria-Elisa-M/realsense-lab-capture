"""Authentication service — login, logout, current user singleton."""
import logging
from typing import Optional
import bcrypt
from app.database.models import User
import app.database.repositories.user_repository as user_repo

logger = logging.getLogger(__name__)

_current_user: Optional[User] = None


def authenticate(username: str, password: str) -> Optional[User]:
    """Verify credentials and return User on success, None on failure."""
    user = user_repo.get_by_username(username)
    if user is None:
        logger.warning("Login attempt for unknown username: %s", username)
        return None
    if not user.is_active:
        logger.warning("Login attempt for inactive user: %s", username)
        return None
    pw_bytes = password.encode("utf-8")
    hash_bytes = user.password_hash.encode("utf-8")
    if bcrypt.checkpw(pw_bytes, hash_bytes):
        logger.info("User authenticated: %s (%s)", username, user.role)
        return user
    logger.warning("Bad password for user: %s", username)
    return None


def login(user: User) -> None:
    global _current_user
    _current_user = user


def logout() -> None:
    global _current_user
    logger.info("User logged out: %s", _current_user.username if _current_user else "none")
    _current_user = None


def current_user() -> Optional[User]:
    return _current_user


def change_password(user_id: int, new_password: str) -> None:
    """Hash and persist a new password for the given user."""
    pw_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode()
    user_repo.update_password(user_id, pw_hash)
    logger.info("Password changed for user id=%d", user_id)


def create_user(username: str, password: str, role: str) -> User:
    """Create a new user with a bcrypt-hashed password."""
    pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode()
    return user_repo.create(username, pw_hash, role)

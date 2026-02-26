"""Application settings — loaded from and saved to the settings table."""
from dataclasses import dataclass
from app.database.connection import get_connection


@dataclass
class AppSettings:
    output_directory: str
    color_width: int
    color_height: int
    color_fps: int
    depth_width: int
    depth_height: int
    depth_fps: int
    infrared_width: int
    infrared_height: int
    infrared_fps: int
    preview_fps: int


def load_settings() -> AppSettings:
    conn = get_connection()
    try:
        rows = conn.execute("SELECT key, value FROM settings").fetchall()
        d = {r["key"]: r["value"] for r in rows}
    finally:
        conn.close()

    return AppSettings(
        output_directory=d.get("output_directory", "recordings"),
        color_width=int(d.get("color_width", 1280)),
        color_height=int(d.get("color_height", 720)),
        color_fps=int(d.get("color_fps", 30)),
        depth_width=int(d.get("depth_width", 1280)),
        depth_height=int(d.get("depth_height", 720)),
        depth_fps=int(d.get("depth_fps", 30)),
        infrared_width=int(d.get("infrared_width", 1280)),
        infrared_height=int(d.get("infrared_height", 720)),
        infrared_fps=int(d.get("infrared_fps", 30)),
        preview_fps=int(d.get("preview_fps", 15)),
    )


def save_settings(settings: AppSettings) -> None:
    updates = {
        "output_directory": settings.output_directory,
        "color_width": str(settings.color_width),
        "color_height": str(settings.color_height),
        "color_fps": str(settings.color_fps),
        "depth_width": str(settings.depth_width),
        "depth_height": str(settings.depth_height),
        "depth_fps": str(settings.depth_fps),
        "infrared_width": str(settings.infrared_width),
        "infrared_height": str(settings.infrared_height),
        "infrared_fps": str(settings.infrared_fps),
        "preview_fps": str(settings.preview_fps),
    }
    conn = get_connection()
    try:
        for key, value in updates.items():
            conn.execute(
                "UPDATE settings SET value=?, updated_at=strftime('%Y-%m-%dT%H:%M:%SZ','now') "
                "WHERE key=?",
                (value, key),
            )
        conn.commit()
    finally:
        conn.close()

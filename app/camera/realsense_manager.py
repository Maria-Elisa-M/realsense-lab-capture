"""RealSense pipeline configuration builder and device detection."""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import pyrealsense2 as rs
    REALSENSE_AVAILABLE = True
except ImportError:
    rs = None  # type: ignore
    REALSENSE_AVAILABLE = False
    logger.warning("pyrealsense2 not available — camera features will be disabled.")


def is_camera_connected() -> bool:
    """Return True if at least one RealSense device is attached."""
    if not REALSENSE_AVAILABLE:
        return False
    try:
        ctx = rs.context()
        devices = ctx.query_devices()
        return len(devices) > 0
    except Exception as exc:
        logger.error("Error querying RealSense devices: %s", exc)
        return False


def get_connected_device_info() -> Optional[str]:
    """Return a human-readable description of the first connected device."""
    if not REALSENSE_AVAILABLE:
        return None
    try:
        ctx = rs.context()
        devices = ctx.query_devices()
        if len(devices) == 0:
            return None
        dev = devices[0]
        name = dev.get_info(rs.camera_info.name)
        serial = dev.get_info(rs.camera_info.serial_number)
        fw = dev.get_info(rs.camera_info.firmware_version)
        return f"{name} | Serial: {serial} | FW: {fw}"
    except Exception as exc:
        logger.error("Error reading device info: %s", exc)
        return None


def build_preview_config(color_width: int = 1280, color_height: int = 720,
                         color_fps: int = 30) -> "rs.config":
    """Build a pipeline config for preview (color only, lower fps optional)."""
    config = rs.config()
    config.enable_stream(rs.stream.color, color_width, color_height,
                         rs.format.bgr8, color_fps)
    return config


def build_recording_config(file_path: str, color_width: int, color_height: int,
                            color_fps: int, depth_width: int, depth_height: int,
                            depth_fps: int, infrared_width: int,
                            infrared_height: int, infrared_fps: int) -> "rs.config":
    """Build a pipeline config that records all three streams to a .bag file."""
    config = rs.config()
    config.enable_record_to_file(file_path)
    config.enable_stream(rs.stream.color, color_width, color_height,
                         rs.format.bgr8, color_fps)
    config.enable_stream(rs.stream.depth, depth_width, depth_height,
                         rs.format.z16, depth_fps)
    config.enable_stream(rs.stream.infrared, 1, infrared_width, infrared_height,
                         rs.format.y8, infrared_fps)
    return config

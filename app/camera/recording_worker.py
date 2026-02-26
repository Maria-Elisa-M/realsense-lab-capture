"""Recording worker — runs RealSense recording pipeline in a thread."""
import logging
import time
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

logger = logging.getLogger(__name__)

try:
    import pyrealsense2 as rs
    REALSENSE_AVAILABLE = True
except ImportError:
    rs = None  # type: ignore
    REALSENSE_AVAILABLE = False


class RecordingWorker(QObject):
    """Records all 3 RealSense streams to a .bag file.

    Signals:
        recording_stopped(file_path, duration_seconds)
        error_occurred(message)
    """

    recording_stopped = pyqtSignal(str, float)
    error_occurred = pyqtSignal(str)

    def __init__(self, file_path: str, color_width: int, color_height: int,
                 color_fps: int, depth_width: int, depth_height: int,
                 depth_fps: int, infrared_width: int, infrared_height: int,
                 infrared_fps: int):
        super().__init__()
        self._file_path = file_path
        self._color_width = color_width
        self._color_height = color_height
        self._color_fps = color_fps
        self._depth_width = depth_width
        self._depth_height = depth_height
        self._depth_fps = depth_fps
        self._infrared_width = infrared_width
        self._infrared_height = infrared_height
        self._infrared_fps = infrared_fps
        self._running = False

    @pyqtSlot()
    def run(self) -> None:
        if not REALSENSE_AVAILABLE:
            self.error_occurred.emit("pyrealsense2 is not installed.")
            return

        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_record_to_file(self._file_path)
        config.enable_stream(rs.stream.color, self._color_width, self._color_height,
                             rs.format.bgr8, self._color_fps)
        config.enable_stream(rs.stream.depth, self._depth_width, self._depth_height,
                             rs.format.z16, self._depth_fps)
        config.enable_stream(rs.stream.infrared, 1, self._infrared_width,
                             self._infrared_height, rs.format.y8, self._infrared_fps)

        start_time = 0.0
        try:
            pipeline.start(config)
            self._running = True
            start_time = time.time()
            logger.info("Recording started → %s", self._file_path)

            while self._running:
                try:
                    pipeline.wait_for_frames(timeout_ms=1000)
                except Exception:
                    continue

        except Exception as exc:
            logger.error("Recording worker error: %s", exc)
            self.error_occurred.emit(str(exc))
            return
        finally:
            try:
                pipeline.stop()
            except Exception:
                pass

        duration = time.time() - start_time
        logger.info("Recording stopped. Duration=%.1f s, file=%s", duration, self._file_path)
        self.recording_stopped.emit(self._file_path, duration)

    def stop(self) -> None:
        self._running = False

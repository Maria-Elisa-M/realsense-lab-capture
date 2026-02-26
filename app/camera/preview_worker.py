"""Preview worker — runs RealSense pipeline in a thread, emits QImage frames."""
import logging
import numpy as np
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage

logger = logging.getLogger(__name__)

try:
    import pyrealsense2 as rs
    REALSENSE_AVAILABLE = True
except ImportError:
    rs = None  # type: ignore
    REALSENSE_AVAILABLE = False


class PreviewMode(str, Enum):
    CALIBRATION = "calibration"  # RGB (left) + colorized Depth (right) side by side
    DATA = "data"                # Colorized Depth only


class PreviewWorker(QObject):
    """Runs in a QThread. Emits processed frames as QImage.

    CALIBRATION mode: RGB and colorized depth side by side.
    DATA mode: colorized depth only.
    """

    frame_ready = pyqtSignal(QImage)
    error_occurred = pyqtSignal(str)

    def __init__(self, color_width: int = 1280, color_height: int = 720,
                 color_fps: int = 30, preview_fps: int = 15,
                 mode: PreviewMode = PreviewMode.CALIBRATION):
        super().__init__()
        self._color_width = color_width
        self._color_height = color_height
        self._color_fps = color_fps
        self._preview_fps = preview_fps
        self._mode = mode
        self._running = False

    @pyqtSlot()
    def run(self) -> None:
        if not REALSENSE_AVAILABLE:
            self.error_occurred.emit("pyrealsense2 is not installed.")
            return

        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, self._color_width, self._color_height,
                             rs.format.bgr8, self._color_fps)
        config.enable_stream(rs.stream.depth, self._color_width, self._color_height,
                             rs.format.z16, self._color_fps)

        # Align depth to color so both share the same coordinate system
        align = rs.align(rs.stream.color)

        # Jet colormap for depth visualisation
        colorizer = rs.colorizer()
        colorizer.set_option(rs.option.color_scheme, 0)  # 0 = Jet

        try:
            pipeline.start(config)
            self._running = True
            logger.info("Preview pipeline started (mode=%s).", self._mode)

            frame_interval = max(1, self._color_fps // self._preview_fps)
            frame_count = 0

            while self._running:
                try:
                    frames = pipeline.wait_for_frames(timeout_ms=1000)
                except Exception:
                    continue

                frame_count += 1
                if frame_count % frame_interval != 0:
                    continue

                aligned = align.process(frames)
                depth_frame = aligned.get_depth_frame()
                if not depth_frame:
                    continue

                depth_colored = colorizer.colorize(depth_frame)
                depth_rgb = np.asarray(depth_colored.get_data()).copy()

                if self._mode == PreviewMode.DATA:
                    h, w, ch = depth_rgb.shape
                    qimg = QImage(depth_rgb.data, w, h, ch * w,
                                  QImage.Format.Format_RGB888)
                    self.frame_ready.emit(qimg.copy())

                else:  # CALIBRATION — RGB left, Depth right
                    color_frame = aligned.get_color_frame()
                    if not color_frame:
                        continue
                    color_bgr = np.asarray(color_frame.get_data())
                    color_rgb = color_bgr[:, :, ::-1].copy()
                    combined = np.hstack([color_rgb, depth_rgb])
                    h, w, ch = combined.shape
                    qimg = QImage(combined.data, w, h, ch * w,
                                  QImage.Format.Format_RGB888)
                    self.frame_ready.emit(qimg.copy())

        except Exception as exc:
            logger.error("Preview worker error: %s", exc)
            self.error_occurred.emit(str(exc))
        finally:
            try:
                pipeline.stop()
            except Exception:
                pass
            logger.info("Preview pipeline stopped.")

    def stop(self) -> None:
        self._running = False

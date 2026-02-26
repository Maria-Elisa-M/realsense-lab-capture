"""Preview worker — runs RealSense pipeline in a thread, emits QImage frames."""
import logging
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage

logger = logging.getLogger(__name__)

try:
    import pyrealsense2 as rs
    REALSENSE_AVAILABLE = True
except ImportError:
    rs = None  # type: ignore
    REALSENSE_AVAILABLE = False


class PreviewWorker(QObject):
    """Runs in a QThread. Emits color frames as QImage.

    Usage:
        worker = PreviewWorker(config)
        thread = QThread()
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.frame_ready.connect(...)
        thread.start()
        # To stop:
        worker.stop()
        thread.quit()
        thread.wait()
    """

    frame_ready = pyqtSignal(QImage)
    error_occurred = pyqtSignal(str)

    def __init__(self, color_width: int = 1280, color_height: int = 720,
                 color_fps: int = 30, preview_fps: int = 15):
        super().__init__()
        self._color_width = color_width
        self._color_height = color_height
        self._color_fps = color_fps
        self._preview_fps = preview_fps
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

        try:
            pipeline.start(config)
            self._running = True
            logger.info("Preview pipeline started.")
            frame_interval = max(1, self._color_fps // self._preview_fps)
            frame_count = 0

            while self._running:
                try:
                    frames = pipeline.wait_for_frames(timeout_ms=1000)
                except Exception:
                    # Timeout or transient error — keep trying
                    continue

                frame_count += 1
                if frame_count % frame_interval != 0:
                    continue

                color_frame = frames.get_color_frame()
                if not color_frame:
                    continue

                # Convert to QImage (BGR -> RGB)
                data = np.asarray(color_frame.get_data())
                rgb = data[:, :, ::-1].copy()  # BGR → RGB, force copy
                h, w, ch = rgb.shape
                qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
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

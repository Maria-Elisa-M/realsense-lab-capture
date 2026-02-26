"""Bag file playback worker — reads .bag frames and emits QImage signals."""
import time
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


class BagPlaybackWorker(QObject):
    """Reads frames from a .bag file and emits them as QImage.

    Shows RGB (left) + colorised Depth (right) side-by-side when both streams
    are present; falls back to whichever stream is available.

    Pause/resume is handled by setting _paused; the worker sleeps in the loop
    rather than calling wait_for_frames, which keeps the bag position intact.
    """

    frame_ready     = pyqtSignal(QImage)
    error_occurred  = pyqtSignal(str)
    playback_ended  = pyqtSignal()

    TARGET_FPS = 30

    def __init__(self, file_path: str):
        super().__init__()
        self._file_path = file_path
        self._running = False
        self._paused  = False

    @pyqtSlot()
    def run(self) -> None:
        if not REALSENSE_AVAILABLE:
            self.error_occurred.emit("pyrealsense2 is not installed.")
            return

        pipeline  = rs.pipeline()
        config    = rs.config()
        config.enable_device_from_file(self._file_path, repeat_playback=False)

        colorizer = rs.colorizer()
        colorizer.set_option(rs.option.color_scheme, 0)  # Jet

        try:
            profile  = pipeline.start(config)
            playback = profile.get_device().as_playback()
            # Disable real-time mode so we drive the frame rate ourselves
            playback.set_real_time(False)

            self._running = True
            frame_interval = 1.0 / self.TARGET_FPS
            logger.info("Bag playback started: %s", self._file_path)

            while self._running:
                # Honour pause
                if self._paused:
                    time.sleep(0.05)
                    continue

                t0 = time.monotonic()

                try:
                    frames = pipeline.wait_for_frames(timeout_ms=2000)
                except RuntimeError:
                    # End of bag file
                    self.playback_ended.emit()
                    break
                except Exception as exc:
                    if self._running:
                        self.error_occurred.emit(str(exc))
                    break

                color_frame = frames.get_color_frame()
                depth_frame = frames.get_depth_frame()

                if not color_frame and not depth_frame:
                    continue

                parts: list[np.ndarray] = []
                if color_frame:
                    color_bgr = np.asarray(color_frame.get_data())
                    parts.append(color_bgr[:, :, ::-1].copy())

                if depth_frame:
                    depth_colored = colorizer.colorize(depth_frame)
                    parts.append(np.asarray(depth_colored.get_data()).copy())

                combined = np.hstack(parts) if len(parts) > 1 else parts[0]
                h, w, ch = combined.shape
                qimg = QImage(combined.data, w, h, ch * w,
                              QImage.Format.Format_RGB888)
                self.frame_ready.emit(qimg.copy())

                # Throttle to TARGET_FPS
                elapsed = time.monotonic() - t0
                sleep_t = frame_interval - elapsed
                if sleep_t > 0:
                    time.sleep(sleep_t)

        except Exception as exc:
            logger.error("Bag playback worker error: %s", exc)
            self.error_occurred.emit(str(exc))
        finally:
            try:
                pipeline.stop()
            except Exception:
                pass
            logger.info("Bag playback stopped.")

    def pause(self) -> None:
        self._paused = True

    def resume(self) -> None:
        self._paused = False

    def stop(self) -> None:
        """Stop playback; also clears _paused so the loop can exit."""
        self._paused  = False
        self._running = False

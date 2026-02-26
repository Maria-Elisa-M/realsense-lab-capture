"""Recording worker — runs RealSense recording pipeline in a thread,
records to .bag and emits live preview frames at a reduced rate."""
import logging
import time
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


class RecordingWorker(QObject):
    """Records all 3 RealSense streams to a .bag file.

    Also emits preview QImage frames at *preview_fps* rate so the UI
    can display a live feed during recording without a separate pipeline.

    Preview mode:
        "calibration"  →  RGB (left) + colorised Depth (right) side-by-side
        "data"         →  colorised Depth only
    """

    recording_stopped = pyqtSignal(str, float)   # file_path, duration_s
    error_occurred    = pyqtSignal(str)
    frame_ready       = pyqtSignal(QImage)        # live preview during recording

    def __init__(self, file_path: str,
                 color_width: int, color_height: int, color_fps: int,
                 depth_width: int, depth_height: int, depth_fps: int,
                 infrared_width: int, infrared_height: int, infrared_fps: int,
                 preview_mode: str = "calibration",
                 preview_fps: int = 15):
        super().__init__()
        self._file_path       = file_path
        self._color_width     = color_width
        self._color_height    = color_height
        self._color_fps       = color_fps
        self._depth_width     = depth_width
        self._depth_height    = depth_height
        self._depth_fps       = depth_fps
        self._infrared_width  = infrared_width
        self._infrared_height = infrared_height
        self._infrared_fps    = infrared_fps
        self._preview_mode    = preview_mode   # "calibration" | "data"
        self._preview_fps     = preview_fps
        self._running         = False

    @pyqtSlot()
    def run(self) -> None:
        if not REALSENSE_AVAILABLE:
            self.error_occurred.emit("pyrealsense2 is not installed.")
            return

        pipeline = rs.pipeline()
        config   = rs.config()
        config.enable_record_to_file(self._file_path)
        config.enable_stream(rs.stream.color,    self._color_width,    self._color_height,
                             rs.format.bgr8, self._color_fps)
        config.enable_stream(rs.stream.depth,    self._depth_width,    self._depth_height,
                             rs.format.z16,  self._depth_fps)
        config.enable_stream(rs.stream.infrared, 1,
                             self._infrared_width, self._infrared_height,
                             rs.format.y8,   self._infrared_fps)

        colorizer = rs.colorizer()
        colorizer.set_option(rs.option.color_scheme, 0)   # Jet
        align     = rs.align(rs.stream.color)

        frame_interval = max(1, self._color_fps // self._preview_fps)
        frame_count    = 0
        start_time     = 0.0

        try:
            pipeline.start(config)
            self._running = True
            start_time    = time.time()
            logger.info("Recording started → %s", self._file_path)

            while self._running:
                try:
                    frames = pipeline.wait_for_frames(timeout_ms=1000)
                except Exception:
                    continue

                frame_count += 1

                # Emit a preview frame at reduced rate
                if frame_count % frame_interval == 0:
                    try:
                        aligned     = align.process(frames)
                        depth_frame = aligned.get_depth_frame()
                        if not depth_frame:
                            continue

                        depth_colored = colorizer.colorize(depth_frame)
                        depth_rgb     = np.asarray(depth_colored.get_data()).copy()

                        if self._preview_mode == "calibration":
                            color_frame = aligned.get_color_frame()
                            if color_frame:
                                color_bgr = np.asarray(color_frame.get_data())
                                color_rgb = color_bgr[:, :, ::-1].copy()
                                combined  = np.hstack([color_rgb, depth_rgb])
                            else:
                                combined = depth_rgb
                        else:          # "data" — depth only
                            combined = depth_rgb

                        h, w, ch = combined.shape
                        qimg = QImage(combined.data, w, h, ch * w,
                                      QImage.Format.Format_RGB888)
                        self.frame_ready.emit(qimg.copy())
                    except Exception:
                        pass   # preview failure must never abort the recording

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
        logger.info("Recording stopped. Duration=%.1f s, file=%s",
                    duration, self._file_path)
        self.recording_stopped.emit(self._file_path, duration)

    def stop(self) -> None:
        self._running = False

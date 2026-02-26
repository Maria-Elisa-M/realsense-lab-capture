"""Standalone camera test — records 5 seconds to a temp .bag file.

Run from the project root:
    python scripts/test_camera.py
"""
import sys
import time
import tempfile
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import pyrealsense2 as rs
except ImportError:
    print("ERROR: pyrealsense2 is not installed.")
    sys.exit(1)

from app.camera.realsense_manager import is_camera_connected, get_connected_device_info

def main():
    print("Checking for RealSense camera...")
    if not is_camera_connected():
        print("ERROR: No RealSense camera detected. Check USB connection.")
        sys.exit(1)

    info = get_connected_device_info()
    print(f"Camera found: {info}")

    with tempfile.TemporaryDirectory() as tmpdir:
        bag_path = os.path.join(tmpdir, "test_recording.bag")
        print(f"Recording 5 seconds to: {bag_path}")

        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_record_to_file(bag_path)
        config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
        config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
        config.enable_stream(rs.stream.infrared, 1, 1280, 720, rs.format.y8, 30)

        pipeline.start(config)
        start = time.time()
        frame_count = 0

        try:
            while time.time() - start < 5.0:
                frames = pipeline.wait_for_frames(timeout_ms=2000)
                frame_count += 1
                elapsed = time.time() - start
                print(f"\rRecorded {elapsed:.1f}s / 5.0s  ({frame_count} frames)", end="")
        finally:
            pipeline.stop()

        print(f"\nPipeline stopped.")

        size = os.path.getsize(bag_path)
        if size > 0:
            print(f"SUCCESS: .bag file exists, size = {size / (1024*1024):.1f} MB")
        else:
            print("FAILURE: .bag file is empty.")
            sys.exit(1)

    print("Test completed successfully. Open the .bag in Intel RealSense Viewer to verify all 3 streams.")


if __name__ == "__main__":
    main()

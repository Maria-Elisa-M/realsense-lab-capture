# RealSense Lab Video Capture

Desktop application for recording research subjects with an Intel RealSense camera. Captures synchronized RGB, Depth, and Infrared streams as `.bag` files.

## Features

- **Two roles** — Admin and Operator
- **Calibration + data recording** per subject session
- **Live camera preview** during sessions
- **SQLite** session/recording metadata storage
- **Admin panel** — user management, subject browser, output directory settings

## Requirements

- Windows 10/11 (64-bit)
- Python 3.11 (pyrealsense2 not available for 3.12+)
- [Intel RealSense SDK 2.0](https://github.com/IntelRealSense/librealsense/releases)

## Setup

```bat
:: 1. Create virtual environment with Python 3.11
py -3.11 -m venv venv
venv\Scripts\activate

:: 2. Install dependencies
pip install -r requirements.txt

:: 3. Run
python main.py
```

Default login: **admin / admin** (change on first use via Admin → Users)

## Building the installer

Requires [Inno Setup 6](https://jrsoftware.org/isinfo.php).

```bat
build_installer.bat
```

Output: `installer/output/RealSenseCapture_Setup_v1.0.0.exe`

## Project structure

```
video_capture/
├── main.py                          # Entry point
├── requirements.txt
├── build_installer.bat              # Builds installer exe
├── video_capture.spec               # PyInstaller config
├── app/
│   ├── auth/                        # Login, bcrypt auth
│   ├── camera/                      # RealSense pipeline workers
│   ├── config/                      # App settings
│   ├── database/                    # SQLite schema, models, repositories
│   ├── ui/                          # PyQt6 screens and widgets
│   └── utils/                       # File path and validation helpers
├── installer/
│   └── installer.iss                # Inno Setup script
└── scripts/
    ├── create_icon.py               # Generates assets/icon.ico
    └── test_camera.py               # Standalone camera test
```

## Recording file layout

```
{output_dir}/{subject_code}/session_{id}/
    {subject_code}_calibration_{YYYYMMDD_HHMMSS}.bag
    {subject_code}_data_{YYYYMMDD_HHMMSS}.bag
```

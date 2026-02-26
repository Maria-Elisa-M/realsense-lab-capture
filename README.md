# RealSense Lab Video Capture

Desktop application for recording research subjects with an Intel RealSense camera. Captures synchronized RGB, Depth, and Infrared streams as `.bag` files.

## Features

- **Two roles** — Admin and Operator
- **Calibration + data recording** per subject session
- **Live camera preview** during sessions
- **SQLite** session/recording metadata storage
- **Admin panel** — user management, subject browser, output directory settings

---

## Installation Guide (End Users)

### Step 1 — Install the Intel RealSense SDK 2.0

The application requires the Intel RealSense SDK to communicate with the camera. Install it **before or after** the app, but the camera will not work without it.

1. Go to the [RealSense releases page](https://github.com/IntelRealSense/librealsense/releases)
2. Download `Intel.RealSense.SDK-WIN10-<version>.exe`
3. Run the installer and follow the on-screen instructions
4. **Restart your computer** after the SDK is installed

### Step 2 — Install RealSense Lab Capture

1. Run `RealSenseCapture_Setup_v1.0.0.exe`
2. Follow the on-screen steps
3. Make sure **"Create a desktop shortcut"** is checked
4. Click **Install**

### Step 3 — First Launch

1. Double-click the **RealSense Lab Capture** icon on your desktop
2. Log in with the default admin credentials:
   - **Username:** `admin`
   - **Password:** `admin`
3. **Change the admin password immediately** — Admin Dashboard → Users → Change PW
4. To add operator accounts — Admin Dashboard → Users → Add User → set role to `Operator`
5. To set where recordings are saved — Admin Dashboard → Settings → Output Directory → Browse

### Step 4 — Connecting the Camera

1. Plug the Intel RealSense camera into a **USB 3.0 port** (blue port) — USB 2.0 will not work correctly
2. Wait a few seconds for Windows to recognise the device
3. Launch the app — the live preview will appear automatically on the recording screen

### Troubleshooting

| Problem | Solution |
|---------|----------|
| Camera not detected | Confirm RealSense SDK is installed · Use a USB 3.0 (blue) port · Unplug and replug the camera · Restart the app |
| Login not working | Default credentials are `admin` / `admin` (all lowercase) · Contact your administrator if the password was changed |
| App does not start | Confirm you are on Windows 10/11 64-bit · Try right-clicking the shortcut and selecting **Run as administrator** |
| Recordings not saving | Check the Output Directory in Admin → Settings · Confirm the folder exists and you have write access |

---

## Developer Setup

### Requirements

- Windows 10/11 (64-bit)
- Python 3.11 — `pyrealsense2` has no PyPI wheels for Python 3.12+
- [Intel RealSense SDK 2.0](https://github.com/IntelRealSense/librealsense/releases)

### Running from source

```bat
py -3.11 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Building the installer

Requires [Inno Setup 6](https://jrsoftware.org/isinfo.php).

```bat
build_installer.bat
```

Output: `installer/output/RealSenseCapture_Setup_v1.0.0.exe`

---

## Project Structure

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
│   ├── installer.iss                # Inno Setup script
│   └── INSTALL_GUIDE.txt            # End-user installation guide
└── scripts/
    ├── create_icon.py               # Generates assets/icon.ico
    └── test_camera.py               # Standalone camera test
```

## Recording File Layout

```
{output_dir}/{subject_id}/session_{id}/
    {subject_id}_calibration_{YYYYMMDD_HHMMSS}.bag
    {subject_id}_data_{YYYYMMDD_HHMMSS}.bag
```

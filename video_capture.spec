# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for RealSense Lab Video Capture
# Build with: pyinstaller video_capture.spec

from PyInstaller.utils.hooks import collect_all, collect_data_files

block_cipher = None

# Collect everything from pyrealsense2 (DLLs + Python files)
rs_datas, rs_binaries, rs_hiddenimports = collect_all('pyrealsense2')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=rs_binaries,
    datas=[
        *rs_datas,
    ],
    hiddenimports=[
        'bcrypt',
        'sqlite3',
        'numpy',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        *rs_hiddenimports,
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'scipy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RealSenseCapture',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,          # UPX can break native DLLs — leave off
    console=False,      # no console window
    disable_windowed_traceback=False,
    icon='assets/icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='RealSenseCapture',
)

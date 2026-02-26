@echo off
setlocal EnableDelayedExpansion

echo ============================================================
echo  RealSense Lab Capture -- Installer Build Script
echo ============================================================
echo.

:: ── Locate project root (same folder as this script) ─────────────────────────
set "ROOT=%~dp0"
cd /d "%ROOT%"

:: ── Check venv exists ─────────────────────────────────────────────────────────
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found.
    echo Please create it first:
    echo   py -3.11 -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

:: ── Activate venv ─────────────────────────────────────────────────────────────
call venv\Scripts\activate.bat
echo [1/5] Virtual environment activated.

:: ── Install / upgrade PyInstaller ─────────────────────────────────────────────
echo [2/5] Installing PyInstaller...
pip install --quiet --upgrade pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller.
    pause
    exit /b 1
)

:: ── Generate icon ─────────────────────────────────────────────────────────────
echo [3/5] Generating application icon...
if not exist "assets\icon.ico" (
    python scripts\create_icon.py
    if errorlevel 1 (
        echo WARNING: Icon generation failed. Build will continue without a custom icon.
    )
) else (
    echo        Icon already exists, skipping.
)

:: ── Run PyInstaller ───────────────────────────────────────────────────────────
echo [4/5] Bundling application with PyInstaller...
if exist "dist\RealSenseCapture" rmdir /s /q "dist\RealSenseCapture"
if exist "build\RealSenseCapture"  rmdir /s /q "build\RealSenseCapture"

pyinstaller video_capture.spec --noconfirm
if errorlevel 1 (
    echo ERROR: PyInstaller failed. See output above.
    pause
    exit /b 1
)
echo        Bundle created: dist\RealSenseCapture\

:: ── Run Inno Setup compiler ───────────────────────────────────────────────────
echo [5/5] Compiling installer with Inno Setup...

set "ISCC="
for %%P in (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    "C:\Program Files\Inno Setup 6\ISCC.exe"
    "C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
) do (
    if exist %%P set "ISCC=%%P"
)

if not defined ISCC (
    echo.
    echo WARNING: Inno Setup not found. Skipping installer compilation.
    echo.
    echo To create the installer:
    echo   1. Download Inno Setup 6 from https://jrsoftware.org/isinfo.php
    echo   2. Install it, then re-run this script.
    echo.
    echo The bundled application is ready at:
    echo   %ROOT%dist\RealSenseCapture\RealSenseCapture.exe
    pause
    exit /b 0
)

if not exist "installer\output" mkdir "installer\output"
%ISCC% "installer\installer.iss"
if errorlevel 1 (
    echo ERROR: Inno Setup compilation failed.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  BUILD COMPLETE
echo  Installer: %ROOT%installer\output\RealSenseCapture_Setup_v1.0.0.exe
echo ============================================================
pause

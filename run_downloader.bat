@echo off
title YouTube Video and Shorts Downloader
color 0A

:: Ensure the script runs in its current folder
cd /d "%~dp0"

echo ======================================================================
echo             YOUTUBE VIDEO ^& SHORTS DOWNLOADER (1-CLICK RUN)
echo ======================================================================
echo.

:: 1. Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    color 0C
    echo [ERROR] Python is not installed or not added to your system PATH!
    echo.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check the box: "Add python.exe to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: 2. Check and install dependencies if missing
echo [*] Checking dependencies...
python -c "import yt_dlp, imageio_ffmpeg" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [*] Installing required packages from requirements.txt...
    pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        color 0C
        echo.
        echo [ERROR] Failed to install dependencies. Please check your internet connection.
        echo.
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed successfully!
    echo.
)

:: 3. Launch the downloader
echo [*] Launching Downloader...
echo.
python downloader.py

:: 4. Prevent window from closing immediately when done
echo.
echo ======================================================================
echo Execution finished.
echo ======================================================================
pause

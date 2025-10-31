@echo off
REM DoggoBot Face Detection Startup Script (Windows)
REM This script starts the face detection system with GPU acceleration

echo ======================================================================
echo 🤖 DoggoBot - GPU-Accelerated Face Detection Startup
echo ======================================================================
echo.

REM Check if in correct directory
if not exist "scripts" (
    echo ❌ Error: Please run this script from the DoggoBot root directory
    exit /b 1
)

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+
    exit /b 1
)

echo ✅ Python found
python --version
echo.

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import cv2" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  OpenCV not installed. Installing dependencies...
    cd scripts
    pip install -r requirements.txt
    cd ..
) else (
    echo ✅ Dependencies installed
)
echo.

REM Run GPU check
echo Checking GPU availability...
cd scripts
python check_gpu.py
set GPU_STATUS=%ERRORLEVEL%
cd ..
echo.

REM Find cameras
echo Detecting cameras...
cd scripts
python find_camera.py
cd ..
echo.

REM Prompt for camera index
set /p CAMERA_INDEX="Enter camera index (default: 0): "
if "%CAMERA_INDEX%"=="" set CAMERA_INDEX=0
echo.

REM Prompt for whitelist
set /p HAS_WHITELIST="Do you have a whitelist directory? (y/N): "
set WHITELIST_ARG=
if /i "%HAS_WHITELIST%"=="y" (
    set /p WHITELIST_DIR="Enter whitelist directory path: "
    if exist "!WHITELIST_DIR!" (
        set WHITELIST_ARG=--whitelist-dir "!WHITELIST_DIR!"
        echo ✅ Whitelist directory found
    ) else (
        echo ⚠️  Directory not found, continuing without whitelist
    )
)
echo.

REM Set FPS based on GPU
if %GPU_STATUS%==0 (
    set DEFAULT_FPS=30
    echo GPU detected! Using higher FPS
) else (
    set DEFAULT_FPS=10
    echo CPU mode - using lower FPS for stability
)

set /p FPS="Target FPS (default: %DEFAULT_FPS%): "
if "%FPS%"=="" set FPS=%DEFAULT_FPS%
echo.

REM Start face detection
echo ======================================================================
echo 🚀 Starting Face Detection
echo ======================================================================
echo.
echo Settings:
echo   • Camera Index: %CAMERA_INDEX%
echo   • Target FPS: %FPS%
if defined WHITELIST_ARG (
    echo   • Whitelist: %WHITELIST_ARG%
) else (
    echo   • Whitelist: None
)
if %GPU_STATUS%==0 (
    echo   • GPU: Enabled
) else (
    echo   • GPU: Disabled (CPU mode)
)
echo.
echo Press Ctrl+C to stop
echo.

cd scripts
python face_detector_real.py --camera-index %CAMERA_INDEX% --fps %FPS% %WHITELIST_ARG%

echo.
echo ======================================================================
echo ✅ Face Detection Stopped
echo ======================================================================
pause

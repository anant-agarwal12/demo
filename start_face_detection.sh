#!/bin/bash
# DoggoBot Face Detection Startup Script
# This script starts the face detection system with GPU acceleration

set -e  # Exit on error

echo "======================================================================"
echo "🤖 DoggoBot - GPU-Accelerated Face Detection Startup"
echo "======================================================================"
echo ""

# Check if in correct directory
if [ ! -d "scripts" ] || [ ! -d "backend" ]; then
    echo "❌ Error: Please run this script from the DoggoBot root directory"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if dependencies are installed
echo "Checking dependencies..."
if ! python3 -c "import cv2" 2>/dev/null; then
    echo "⚠️  OpenCV not installed. Installing dependencies..."
    cd scripts
    pip install -r requirements.txt
    cd ..
else
    echo "✅ Dependencies installed"
fi
echo ""

# Run GPU check
echo "Checking GPU availability..."
cd scripts
python3 check_gpu.py
GPU_STATUS=$?
cd ..
echo ""

# Find cameras
echo "Detecting cameras..."
cd scripts
python3 find_camera.py
cd ..
echo ""

# Prompt for camera index
echo "Which camera do you want to use?"
read -p "Enter camera index (default: 0): " CAMERA_INDEX
CAMERA_INDEX=${CAMERA_INDEX:-0}
echo ""

# Prompt for whitelist
read -p "Do you have a whitelist directory? (y/N): " HAS_WHITELIST
WHITELIST_ARG=""
if [ "$HAS_WHITELIST" = "y" ] || [ "$HAS_WHITELIST" = "Y" ]; then
    read -p "Enter whitelist directory path: " WHITELIST_DIR
    if [ -d "$WHITELIST_DIR" ]; then
        WHITELIST_ARG="--whitelist-dir $WHITELIST_DIR"
        echo "✅ Whitelist directory found"
    else
        echo "⚠️  Directory not found, continuing without whitelist"
    fi
fi
echo ""

# Set FPS based on GPU
if [ $GPU_STATUS -eq 0 ]; then
    DEFAULT_FPS=30
    echo "GPU detected! Using higher FPS"
else
    DEFAULT_FPS=10
    echo "CPU mode - using lower FPS for stability"
fi

read -p "Target FPS (default: $DEFAULT_FPS): " FPS
FPS=${FPS:-$DEFAULT_FPS}
echo ""

# Start face detection
echo "======================================================================"
echo "🚀 Starting Face Detection"
echo "======================================================================"
echo ""
echo "Settings:"
echo "  • Camera Index: $CAMERA_INDEX"
echo "  • Target FPS: $FPS"
echo "  • Whitelist: ${WHITELIST_ARG:-None}"
echo "  • GPU: $([ $GPU_STATUS -eq 0 ] && echo 'Enabled' || echo 'Disabled (CPU mode)')"
echo ""
echo "Press Ctrl+C to stop"
echo ""

cd scripts
python3 face_detector_real.py \
    --camera-index $CAMERA_INDEX \
    --fps $FPS \
    $WHITELIST_ARG

echo ""
echo "======================================================================"
echo "✅ Face Detection Stopped"
echo "======================================================================"

#!/usr/bin/env python3
"""
Check GPU availability for face recognition
"""

import sys

print("🔍 GPU Availability Check for DoggoBot")
print("=" * 60)

# Check dlib
print("\n1️⃣ Checking dlib (face_recognition backend)...")
try:
    import dlib
    print(f"   ✅ dlib installed: version {dlib.__version__ if hasattr(dlib, '__version__') else 'unknown'}")
    
    if dlib.DLIB_USE_CUDA:
        print("   ✅ dlib compiled with CUDA support!")
        print(f"   GPU devices available: {dlib.cuda.get_num_devices()}")
    else:
        print("   ℹ️  dlib using CPU only (no CUDA support)")
        print("   💡 To enable GPU: pip uninstall dlib && pip install dlib-cuda")
except ImportError:
    print("   ⚠️  dlib not installed")
    print("   Install with: pip install dlib")

# Check OpenCV
print("\n2️⃣ Checking OpenCV...")
try:
    import cv2
    print(f"   ✅ OpenCV installed: version {cv2.__version__}")
    
    # Check if CUDA is available
    if cv2.cuda.getCudaEnabledDeviceCount() > 0:
        print(f"   ✅ OpenCV built with CUDA support!")
        print(f"   CUDA devices: {cv2.cuda.getCudaEnabledDeviceCount()}")
        device_info = cv2.cuda.getDevice()
        print(f"   Current device: {device_info}")
    else:
        print("   ℹ️  OpenCV using CPU only")
        print("   💡 For GPU: pip install opencv-contrib-python (requires CUDA)")
except Exception as e:
    print(f"   ℹ️  OpenCV CUDA not available: {e}")

# Check PyTorch (if available - for future deep learning models)
print("\n3️⃣ Checking PyTorch (optional)...")
try:
    import torch
    print(f"   ✅ PyTorch installed: version {torch.__version__}")
    if torch.cuda.is_available():
        print(f"   ✅ CUDA available!")
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
        print(f"   CUDA version: {torch.version.cuda}")
    else:
        print("   ℹ️  PyTorch using CPU only")
except ImportError:
    print("   ℹ️  PyTorch not installed (not required)")

# Check TensorFlow (if available)
print("\n4️⃣ Checking TensorFlow (optional)...")
try:
    import tensorflow as tf
    print(f"   ✅ TensorFlow installed: version {tf.__version__}")
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        print(f"   ✅ GPUs available: {len(gpus)}")
        for gpu in gpus:
            print(f"      - {gpu}")
    else:
        print("   ℹ️  TensorFlow using CPU only")
except ImportError:
    print("   ℹ️  TensorFlow not installed (not required)")

# Check NVIDIA GPU
print("\n5️⃣ Checking NVIDIA GPU (system level)...")
try:
    import subprocess
    result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
    if result.returncode == 0:
        print("   ✅ NVIDIA GPU detected!")
        # Parse nvidia-smi output
        lines = result.stdout.split('\n')
        for line in lines:
            if 'NVIDIA' in line or 'Tesla' in line or 'GeForce' in line or 'RTX' in line:
                print(f"   {line.strip()}")
    else:
        print("   ℹ️  No NVIDIA GPU detected or nvidia-smi not found")
except FileNotFoundError:
    print("   ℹ️  nvidia-smi not found (no NVIDIA GPU or drivers not installed)")
except Exception as e:
    print(f"   ⚠️  Error checking GPU: {e}")

# Summary and recommendations
print("\n" + "=" * 60)
print("\n📊 SUMMARY")
print("-" * 60)

try:
    import dlib
    if dlib.DLIB_USE_CUDA:
        print("✅ Your system is GPU-accelerated!")
        print("   Face recognition will use GPU for faster processing")
    else:
        print("ℹ️  Currently using CPU processing")
        print("\n💡 TO ENABLE GPU ACCELERATION:")
        print("   1. Install CUDA Toolkit: https://developer.nvidia.com/cuda-downloads")
        print("   2. Install cuDNN: https://developer.nvidia.com/cudnn")
        print("   3. Install GPU-enabled dlib:")
        print("      pip uninstall dlib")
        print("      pip install dlib-cuda")
        print("   4. Or compile dlib from source with CUDA")
except:
    print("⚠️  dlib not installed - install it first")

print("\n📈 PERFORMANCE EXPECTATIONS:")
print("   CPU: ~5-10 FPS face detection")
print("   GPU: ~20-60 FPS face detection (depending on GPU)")

print("\n" + "=" * 60)

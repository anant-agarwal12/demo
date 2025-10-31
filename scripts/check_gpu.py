#!/usr/bin/env python3
"""
Check GPU/CUDA availability for face recognition

This script checks if:
- NVIDIA GPU is available
- dlib has CUDA support compiled in
- OpenCV has GPU support
- face_recognition library is installed
"""

import sys

def check_nvidia_gpu():
    """Check if NVIDIA GPU is available via nvidia-smi"""
    try:
        import subprocess
        result = subprocess.run(
            ['nvidia-smi'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✅ NVIDIA GPU detected:")
            # Extract GPU name from output
            lines = result.stdout.split('\n')
            for line in lines:
                if 'GeForce' in line or 'RTX' in line or 'GTX' in line or 'Tesla' in line or 'Quadro' in line:
                    print(f"   {line.strip()}")
                    return True
            print("   GPU found (check nvidia-smi output)")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
        return False
    return False

def check_dlib_cuda():
    """Check if dlib has CUDA support"""
    try:
        import dlib
        if hasattr(dlib, 'DLIB_USE_CUDA'):
            cuda_enabled = dlib.DLIB_USE_CUDA
            if cuda_enabled:
                print("✅ dlib compiled with CUDA support!")
                if hasattr(dlib, 'cuda.get_num_devices'):
                    num_devices = dlib.cuda.get_num_devices()
                    print(f"   GPU devices available: {num_devices}")
                return True
            else:
                print("⚠️  dlib compiled WITHOUT CUDA support (CPU only)")
                return False
        else:
            print("⚠️  Cannot determine dlib CUDA support")
            return False
    except ImportError:
        print("❌ dlib not installed")
        return False

def check_opencv_gpu():
    """Check if OpenCV has GPU support"""
    try:
        import cv2
        # Check if CUDA is available in OpenCV
        try:
            count = cv2.cuda.getCudaEnabledDeviceCount()
            if count > 0:
                print(f"✅ OpenCV compiled with CUDA support!")
                print(f"   CUDA devices: {count}")
                return True
            else:
                print("⚠️  OpenCV CUDA enabled but no devices found")
                return False
        except AttributeError:
            print("⚠️  OpenCV does not have CUDA support compiled")
            return False
    except ImportError:
        print("❌ OpenCV not installed")
        return False

def check_face_recognition():
    """Check if face_recognition library is installed"""
    try:
        import face_recognition
        print("✅ face_recognition library installed")
        
        # Check which models are available
        import os
        face_recognition_path = face_recognition.__file__
        print(f"   Location: {face_recognition_path}")
        return True
    except ImportError:
        print("❌ face_recognition library not installed")
        print("   Install with: pip install face-recognition")
        return False

def main():
    print("🔍 Checking GPU/CUDA Setup for DoggoBot\n")
    
    has_gpu = check_nvidia_gpu()
    if not has_gpu:
        print("⚠️  NVIDIA GPU not detected via nvidia-smi")
        print("   You may still have a GPU - check manually with: nvidia-smi")
    print()
    
    has_dlib_cuda = check_dlib_cuda()
    print()
    
    has_opencv_cuda = check_opencv_gpu()
    print()
    
    has_face_recognition = check_face_recognition()
    print()
    
    print("=" * 50)
    print("Summary:")
    print("=" * 50)
    
    if has_gpu and has_dlib_cuda:
        print("✅ GPU acceleration READY")
        print("   You can use --detection-model cnn for GPU acceleration")
    elif has_dlib_cuda:
        print("⚠️  dlib has CUDA but GPU not detected")
        print("   Check nvidia-smi and GPU drivers")
    else:
        print("⚠️  GPU acceleration NOT available")
        print("   System will use CPU mode (HOG detector)")
        print("   This is fine for most use cases!")
    
    if not has_face_recognition:
        print("\n❌ face_recognition not installed - required for face detection")
        print("   Run: pip install face-recognition")
    
    print()

if __name__ == "__main__":
    main()

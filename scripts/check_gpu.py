#!/usr/bin/env python3
"""
GPU Acceleration Check Script for DoggoBot

This script checks if your system has GPU acceleration available
for face recognition (dlib CUDA support) and computer vision (OpenCV).
"""

import sys

def check_nvidia_gpu():
    """Check if NVIDIA GPU is available"""
    try:
        import subprocess
        result = subprocess.run(['nvidia-smi'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            print("✅ NVIDIA GPU detected!")
            # Parse GPU info
            output = result.stdout.decode('utf-8')
            for line in output.split('\n'):
                if 'NVIDIA' in line or 'GeForce' in line or 'RTX' in line or 'GTX' in line:
                    print(f"   {line.strip()}")
            return True
        else:
            print("❌ No NVIDIA GPU found (nvidia-smi not available)")
            return False
    except FileNotFoundError:
        print("❌ nvidia-smi not found - no NVIDIA GPU or drivers not installed")
        return False
    except Exception as e:
        print(f"⚠️  Error checking GPU: {e}")
        return False

def check_cuda():
    """Check CUDA availability"""
    try:
        import subprocess
        result = subprocess.run(['nvcc', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            output = result.stdout.decode('utf-8')
            for line in output.split('\n'):
                if 'release' in line.lower():
                    print(f"✅ CUDA Toolkit installed: {line.strip()}")
                    return True
        else:
            print("❌ CUDA Toolkit not found (nvcc not available)")
            return False
    except FileNotFoundError:
        print("❌ CUDA Toolkit not installed")
        return False
    except Exception as e:
        print(f"⚠️  Error checking CUDA: {e}")
        return False

def check_dlib_cuda():
    """Check if dlib was compiled with CUDA support"""
    try:
        import dlib
        if dlib.DLIB_USE_CUDA:
            print("✅ dlib compiled with CUDA support!")
            try:
                gpu_count = dlib.cuda.get_num_devices()
                print(f"   GPU devices available: {gpu_count}")
                return True
            except:
                print("   (GPU device count unavailable)")
                return True
        else:
            print("❌ dlib compiled WITHOUT CUDA support (using CPU)")
            print("   To enable GPU: pip uninstall dlib && compile dlib from source with CUDA")
            return False
    except ImportError:
        print("⚠️  dlib not installed")
        print("   Install with: pip install dlib")
        return False
    except AttributeError:
        print("⚠️  dlib installed but CUDA support unknown (old version?)")
        return False

def check_opencv_cuda():
    """Check if OpenCV was compiled with CUDA support"""
    try:
        import cv2
        build_info = cv2.getBuildInformation()
        
        if 'CUDA' in build_info:
            # Check if CUDA is enabled
            cuda_enabled = False
            for line in build_info.split('\n'):
                if 'CUDA' in line and 'YES' in line:
                    cuda_enabled = True
                    break
            
            if cuda_enabled:
                print("✅ OpenCV compiled with CUDA support!")
                return True
            else:
                print("❌ OpenCV compiled WITHOUT CUDA support")
                return False
        else:
            print("❌ OpenCV compiled WITHOUT CUDA support")
            print("   Using CPU version (opencv-python)")
            print("   For GPU: compile OpenCV from source or use opencv-contrib-python")
            return False
    except ImportError:
        print("⚠️  OpenCV not installed")
        return False

def check_face_recognition():
    """Check if face_recognition library is available"""
    try:
        import face_recognition
        print("✅ face_recognition library installed")
        return True
    except ImportError:
        print("⚠️  face_recognition library not installed")
        print("   Install with: pip install face-recognition")
        return False

def main():
    print("\n" + "="*60)
    print("🔍 DoggoBot GPU Acceleration Check")
    print("="*60 + "\n")
    
    print("📊 Hardware Check:")
    print("-" * 40)
    has_gpu = check_nvidia_gpu()
    print()
    
    if has_gpu:
        print("🔧 CUDA Toolkit:")
        print("-" * 40)
        check_cuda()
        print()
    
    print("📚 Software Libraries:")
    print("-" * 40)
    has_dlib_cuda = check_dlib_cuda()
    has_opencv_cuda = check_opencv_cuda()
    has_face_rec = check_face_recognition()
    print()
    
    print("="*60)
    print("📝 Summary:")
    print("="*60)
    
    if has_gpu and has_dlib_cuda:
        print("✅ GPU Acceleration: ENABLED")
        print("   Your system is configured for GPU-accelerated face recognition!")
        print("   Expected performance: 20-60 FPS (depending on GPU)")
    elif has_gpu and not has_dlib_cuda:
        print("⚠️  GPU Acceleration: PARTIALLY AVAILABLE")
        print("   You have an NVIDIA GPU, but dlib is not compiled with CUDA.")
        print("   Current performance: 5-10 FPS (CPU only)")
        print("\n   To enable GPU acceleration:")
        print("   1. Install CUDA Toolkit: https://developer.nvidia.com/cuda-downloads")
        print("   2. Compile dlib with CUDA: see GPU_ACCELERATION_GUIDE.md")
    else:
        print("ℹ️  GPU Acceleration: DISABLED (CPU mode)")
        print("   Running in CPU mode.")
        print("   Expected performance: 5-10 FPS")
        if has_face_rec:
            print("   This is sufficient for most use cases!")
        else:
            print("\n   Install face recognition library:")
            print("   pip install face-recognition")
    
    print("\n" + "="*60)
    print()
    
    # Exit code: 0 if GPU available, 1 otherwise
    sys.exit(0 if (has_gpu and has_dlib_cuda) else 1)

if __name__ == "__main__":
    main()

# 🚀 GPU Acceleration Guide for DoggoBot

## Current Status: **CPU Processing**

By default, the face recognition system uses **CPU processing**. This works fine for most use cases but can be slower (5-10 FPS).

---

## 🔍 Check Your Current Setup

Run this to see if GPU is available:

```bash
cd scripts
python check_gpu.py
```

This will show:
- Whether you have an NVIDIA GPU
- If dlib has CUDA support
- If OpenCV has GPU support
- Current processing mode (CPU/GPU)

---

## ⚡ Performance Comparison

| Processing Mode | Speed | Hardware Required |
|----------------|-------|-------------------|
| **CPU** | 5-10 FPS | Any computer |
| **GPU (CUDA)** | 20-60 FPS | NVIDIA GPU with CUDA |

---

## 🎮 How to Enable GPU Acceleration

### Prerequisites

1. **NVIDIA GPU** (GTX/RTX series, or Tesla/Quadro)
2. **CUDA Toolkit** installed
3. **cuDNN** library installed

### Step 1: Check if You Have an NVIDIA GPU

**Windows:**
```bash
nvidia-smi
```

**Linux:**
```bash
lspci | grep -i nvidia
nvidia-smi
```

If you see GPU info, you're good to go!

---

### Step 2: Install CUDA Toolkit

**Windows:**
1. Download from: https://developer.nvidia.com/cuda-downloads
2. Install CUDA Toolkit (recommended: CUDA 11.8 or 12.x)
3. Verify installation: `nvcc --version`

**Linux (Ubuntu/Debian):**
```bash
# Add NVIDIA package repositories
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600
sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/3bf863cc.pub
sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/ /"
sudo apt-get update

# Install CUDA
sudo apt-get -y install cuda

# Verify
nvcc --version
```

---

### Step 3: Install cuDNN

1. Download cuDNN from: https://developer.nvidia.com/cudnn
2. Extract and copy files to CUDA directory
3. Follow NVIDIA's installation guide for your OS

---

### Step 4: Install GPU-Enabled dlib

**Option A: Using pip (easier)**
```bash
cd scripts

# Uninstall CPU version
pip uninstall dlib face-recognition

# Try GPU version (may not work on all systems)
pip install dlib-cuda
pip install face-recognition
```

**Option B: Compile from Source (more reliable)**
```bash
# Install build tools
# Windows: Install Visual Studio with C++ tools
# Linux:
sudo apt-get install build-essential cmake

# Clone dlib
git clone https://github.com/davisking/dlib.git
cd dlib

# Build with CUDA
mkdir build
cd build
cmake .. -DDLIB_USE_CUDA=1 -DUSE_AVX_INSTRUCTIONS=1
cmake --build . --config Release
cd ..

# Install
python setup.py install

# Verify CUDA is enabled
python -c "import dlib; print('CUDA:', dlib.DLIB_USE_CUDA)"
```

---

### Step 5: Optional - GPU OpenCV

For even faster frame processing:

```bash
# Uninstall CPU version
pip uninstall opencv-python

# Install GPU version (requires CUDA)
pip install opencv-contrib-python

# Note: You may need to compile OpenCV from source for full CUDA support
```

---

## ✅ Verify GPU Acceleration

After installation:

```bash
cd scripts
python check_gpu.py
```

Should show:
```
✅ dlib compiled with CUDA support!
   GPU devices available: 1
```

Then run the detector:
```bash
python face_detector_real.py --camera-index 2 --fps 30
```

You should see significantly faster processing!

---

## 🔧 Optimization Tips

### 1. Adjust Batch Processing
Edit `face_detector_real.py`:

```python
# Line ~346: Process more frames per second with GPU
process_every = 1  # Process every frame (GPU can handle it)
# process_every = 3  # CPU default
```

### 2. Higher Resolution
With GPU, you can use higher camera resolution:

```python
# Line ~45-48
self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)  # Full HD
self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
```

### 3. More FPS
```bash
# CPU
python face_detector_real.py --fps 10

# GPU
python face_detector_real.py --fps 30
```

---

## 🐛 Troubleshooting

### "CUDA not available" after installation

1. Check CUDA path:
   ```bash
   # Linux
   echo $LD_LIBRARY_PATH
   export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
   
   # Windows - add to PATH
   C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\bin
   C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\libnvvp
   ```

2. Verify CUDA installation:
   ```bash
   nvcc --version
   nvidia-smi
   ```

3. Reinstall GPU drivers from: https://www.nvidia.com/Download/index.aspx

### dlib compilation fails

**Windows:**
- Install Visual Studio 2019/2022 with C++ tools
- Use Visual Studio Developer Command Prompt

**Linux:**
```bash
sudo apt-get install build-essential cmake
sudo apt-get install libopenblas-dev liblapack-dev
sudo apt-get install libx11-dev libgtk-3-dev
```

### Out of memory errors

Reduce batch size or image resolution:

```python
# In face_detector_real.py, line ~193
small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)  # More aggressive resize
```

---

## 📊 Monitoring GPU Usage

While running the detector:

```bash
# Watch GPU usage in real-time
nvidia-smi -l 1

# Or use
watch -n 1 nvidia-smi
```

Look for:
- **GPU Utilization**: Should be 40-90% when processing faces
- **Memory Usage**: Face recognition typically uses 500MB-2GB
- **Temperature**: Should stay under 80°C

---

## 🎯 Expected Performance

### CPU Mode (Current Default)
- **Speed**: 5-10 FPS
- **Latency**: 100-200ms per frame
- **Good for**: Testing, low-traffic scenarios
- **Hardware**: Any modern CPU

### GPU Mode (NVIDIA)
- **Speed**: 20-60 FPS (depending on GPU)
- **Latency**: 20-50ms per frame
- **Good for**: Production, high-traffic, real-time
- **Hardware**: GTX 1050+ or better

### Examples by GPU:
| GPU | Expected FPS |
|-----|--------------|
| GTX 1050 Ti | 15-25 FPS |
| GTX 1660 | 25-35 FPS |
| RTX 2060 | 35-50 FPS |
| RTX 3060 | 40-60 FPS |
| RTX 4090 | 60+ FPS |

---

## 💡 Do You Need GPU?

### Use CPU if:
- ✅ You have 1-3 cameras
- ✅ 5-10 FPS is acceptable
- ✅ Budget/power constrained
- ✅ Testing/development

### Use GPU if:
- ✅ You need 20+ FPS
- ✅ Multiple cameras
- ✅ Real-time reactions required
- ✅ Large whitelist (100+ people)
- ✅ High-resolution cameras

---

## 🔄 Switching Between CPU and GPU

The detector automatically uses GPU if available. To force CPU:

```python
# Edit face_detector_real.py, add near top:
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Force CPU
```

To use specific GPU (if you have multiple):

```python
os.environ['CUDA_VISIBLE_DEVICES'] = '0'  # Use GPU 0
os.environ['CUDA_VISIBLE_DEVICES'] = '1'  # Use GPU 1
```

---

## 📚 Additional Resources

- **CUDA Toolkit**: https://developer.nvidia.com/cuda-toolkit
- **cuDNN**: https://developer.nvidia.com/cudnn
- **dlib CUDA guide**: http://dlib.net/compile.html
- **NVIDIA Drivers**: https://www.nvidia.com/Download/index.aspx

---

## 🎓 Summary

1. **Check current setup**: `python check_gpu.py`
2. **CPU is default**: Works fine for most cases
3. **GPU gives 3-6x speedup**: If you need it
4. **Installation**: CUDA → cuDNN → dlib-cuda
5. **Verify**: Run `check_gpu.py` again

**Need help?** The system works great on CPU for getting started. Add GPU later if needed!

---

**Current recommendation**: Start with CPU, measure your actual FPS needs, then decide if GPU is worth the setup effort.

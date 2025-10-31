# 🚀 DoggoBot Startup Guide

## What You Need to Run

### 3 Components:
1. **Backend** (FastAPI server)
2. **Frontend** (React dashboard)
3. **Face Detector** (Camera + Recognition)

---

## 🎯 Quick Start (3 Steps)

### Step 1: Start Backend & Frontend

**Option A - Docker (Easiest):**
```bash
cd C:/Coding/demo
docker-compose up -d
```

**Option B - Manual:**

**Terminal 1 - Backend:**
```bash
cd C:/Coding/demo/backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd C:/Coding/demo/frontend
npm install
npm run dev
```

### Step 2: Add People to Whitelist

1. Open: **http://localhost:3000**
2. Go to **Settings** → **Whitelist Management**
3. Add people:
   - Enter name
   - Upload 3-5 photos
   - Click "Add Person"

### Step 3: Start Face Detector

```bash
cd C:/Coding/demo/scripts
conda activate yolov8-env

# Basic (15 FPS)
python face_detector_real.py --camera-index 0 --fps 15

# Smooth (30 FPS)
python face_detector_real.py --camera-index 0 --fps 30
```

---

## ⚡ GPU Acceleration Setup

### Current Status: **CPU Only**

To enable GPU acceleration (3-6x faster):

### Prerequisites Check:
```bash
# Check if you have NVIDIA GPU
nvidia-smi
```

### Option 1: Install GPU-Enabled dlib (Recommended)

```bash
cd C:/Coding/demo/scripts
conda activate yolov8-env

# Uninstall CPU versions
pip uninstall dlib face-recognition

# Install CUDA Toolkit first (if not installed)
# Download from: https://developer.nvidia.com/cuda-downloads
# Install CUDA 11.8 or 12.x

# Install cuDNN
# Download from: https://developer.nvidia.com/cudnn
# Extract and copy to CUDA folder

# Install GPU-enabled dlib
pip install dlib-cuda
pip install face-recognition

# Verify GPU support
python -c "import dlib; print('CUDA:', dlib.DLIB_USE_CUDA)"
```

### Option 2: Use YOLOv8 for Face Detection (Since you have yolov8-env)

This is likely **faster** since you already have the environment!

```bash
conda activate yolov8-env
pip install ultralytics torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

I can create a YOLOv8-based detector if you want (much faster with GPU)!

---

## 📊 Complete Workflow

### Daily Usage:

```bash
# 1. Start services (once)
cd C:/Coding/demo
docker-compose up -d

# 2. Start detector (new terminal)
cd C:/Coding/demo/scripts
conda activate yolov8-env
python face_detector_real.py --camera-index 0 --fps 30

# 3. Open dashboard
# Browser: http://localhost:3000

# 4. Monitor
# - Command Center: Live feed with bounding boxes
# - Alerts: Detection history
# - Settings: Manage whitelist
```

### Stop Services:

```bash
# Stop detector: Press 'q' in detector window

# Stop backend/frontend:
cd C:/Coding/demo
docker-compose down
```

---

## 🎮 What Each Component Does

| Component | What It Does | Port |
|-----------|--------------|------|
| **Backend** | API server, stores alerts, manages whitelist | 8000 |
| **Frontend** | Web dashboard UI | 3000 |
| **Face Detector** | Camera capture, face recognition, posts to backend | N/A |

### Flow:
```
Camera → Detector → Recognizes faces → Posts to Backend → Shows in Frontend
           ↓
    (Uses whitelist from backend)
```

---

## 🔧 Check What's Running

```bash
# Check backend
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000

# Check if detector is posting frames
# (Should see activity in backend logs)
docker-compose logs -f backend
```

---

## ⚡ GPU Performance

### Current (CPU):
- **Speed**: 5-10 FPS
- **Detection time**: 100-200ms per frame

### With GPU:
- **Speed**: 20-60 FPS
- **Detection time**: 20-50ms per frame

### To Monitor GPU Usage:
```bash
# Run in separate terminal
nvidia-smi -l 1
```

---

## 🎯 Quick GPU Test

Want me to create a YOLOv8-based detector? It will be:
- ✅ Faster (GPU accelerated)
- ✅ More accurate
- ✅ Uses your existing yolov8-env
- ✅ Still uses whitelist from website

---

## 📝 Troubleshooting

### "No whitelist entries"
- Go to http://localhost:3000/settings
- Add people with photos
- Press 'r' in detector window to reload

### "Backend connection failed"
- Check backend is running: `curl http://localhost:8000/health`
- Start backend: `docker-compose up -d` or run manually

### "Camera not found"
- Try different indices: `--camera-index 0`, `--camera-index 1`, `--camera-index 2`
- Run: `python test_camera.py --all`

### Slow performance
- Lower FPS: `--fps 10`
- Enable GPU acceleration (see above)
- Use YOLOv8 detector (I can create it)

---

## 💡 Recommended Setup

Since you have **yolov8-env**, I recommend:

1. ✅ Keep current detector for now (it's working)
2. ✅ Let me create a **YOLOv8 GPU detector** for you
3. ✅ Test both and see which is faster

Want me to create the YOLOv8 version? It'll be much faster on GPU! 🚀

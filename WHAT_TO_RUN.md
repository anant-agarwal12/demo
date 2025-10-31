# 🎯 What to Run - Simple Guide

## TL;DR - 3 Commands

```bash
# 1. Start Backend + Frontend (Terminal 1)
cd C:/Coding/demo
docker-compose up -d

# 2. Start Face Detector (Terminal 2)
cd C:/Coding/demo/scripts
conda activate yolov8-env
python face_detector_yolov8_gpu.py --camera-index 0 --fps 30

# 3. Open Browser
# http://localhost:3000
```

---

## 🚀 For GPU Acceleration

### Install GPU Dependencies (One-time)

```bash
cd C:/Coding/demo/scripts
conda activate yolov8-env

# Install PyTorch with CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Install YOLOv8
pip install ultralytics

# Verify GPU
python -c "import torch; print('CUDA:', torch.cuda.is_available())"
```

### Run GPU-Accelerated Detector

```bash
cd C:/Coding/demo/scripts
conda activate yolov8-env

# YOLOv8 GPU version (RECOMMENDED - fastest!)
python face_detector_yolov8_gpu.py --camera-index 0 --fps 30

# OR regular version (slower, CPU-only)
python face_detector_real.py --camera-index 0 --fps 15
```

---

## 📊 Version Comparison

| Version | Speed | GPU | Accuracy | Recommended |
|---------|-------|-----|----------|-------------|
| **face_detector_real.py** | 5-10 FPS | ❌ CPU | High | Testing |
| **face_detector_yolov8_gpu.py** | 30-60 FPS | ✅ GPU | Very High | **Production** |

---

## ✅ What Each Terminal Does

### Terminal 1: Backend + Frontend
```bash
cd C:/Coding/demo
docker-compose up -d
```
- Runs FastAPI backend (port 8000)
- Runs React frontend (port 3000)
- Stores alerts and whitelist

### Terminal 2: Face Detector
```bash
cd C:/Coding/demo/scripts
conda activate yolov8-env
python face_detector_yolov8_gpu.py --camera-index 0 --fps 30
```
- Captures camera feed
- Detects faces with GPU
- Checks against whitelist from backend
- Posts frames + alerts to backend
- Shows bounding boxes on dashboard feed

### Browser: Dashboard
```
http://localhost:3000
```
- **Command Center**: Live feed with bounding boxes
- **Alerts**: Detection history
- **Settings**: Manage whitelist (add people here!)

---

## 🎮 Controls

### Detector Window:
- **'q'** → Quit
- **'r'** → Reload whitelist (after adding people)

### Dashboard:
- **Command Center** → See live feed
- **Alerts** → View detection history
- **Settings** → Add people to whitelist

---

## 🔧 Quick Setup

### First Time Setup:

```bash
# 1. Install GPU dependencies
cd C:/Coding/demo/scripts
conda activate yolov8-env
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install ultralytics face-recognition

# 2. Start services
cd C:/Coding/demo
docker-compose up -d

# 3. Add people to whitelist
# Open http://localhost:3000/settings
# Upload 3-5 photos per person

# 4. Start detector
cd C:/Coding/demo/scripts
conda activate yolov8-env
python face_detector_yolov8_gpu.py --camera-index 0 --fps 30
```

---

## 📈 Performance Tips

### Smooth Feed (30+ FPS):
```bash
python face_detector_yolov8_gpu.py --camera-index 0 --fps 30
```

### Ultra Smooth (60 FPS):
```bash
python face_detector_yolov8_gpu.py --camera-index 0 --fps 60
```

### Low Spec System (10 FPS):
```bash
python face_detector_real.py --camera-index 0 --fps 10
```

---

## 🛑 Stop Everything

```bash
# Stop detector: Press 'q' in window

# Stop backend/frontend:
cd C:/Coding/demo
docker-compose down
```

---

## ✨ Expected Results

When running correctly, you should see:

1. **Detector Window**:
   - Live camera feed
   - Bounding boxes on faces (green=known, red=unknown)
   - FPS counter
   - "GPU" or "CUDA" indicator

2. **Dashboard (http://localhost:3000)**:
   - Live video feed with same bounding boxes
   - Alerts appearing in real-time
   - Status updates

3. **Console Output**:
   ```
   ✅ Camera initialized at index 0
   ✅ YOLOv8 model loaded on: cuda
   ✅ Whitelist loaded: 5 total encodings
   🤖 Starting YOLOv8 GPU Face Detector
   🚨 Alert: UNKNOWN - Unknown Person
   🚨 Alert: FRIENDLY - John (0.89)
   ```

---

## 🎯 Summary

**Minimum Required:**
1. Backend + Frontend running
2. Face detector running
3. Browser open to dashboard

**For Best Performance:**
- Use `face_detector_yolov8_gpu.py` 
- Run at 30 FPS
- Add people to whitelist

That's it! 🚀

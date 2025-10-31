# 🎯 Face Detection with GPU Acceleration & Bounding Boxes

This guide covers setting up and running the GPU-accelerated face detection system with bounding boxes displayed on the live feed.

---

## ✨ Features

- ✅ **GPU Acceleration**: Automatic detection and use of NVIDIA CUDA for 3-6x speed boost
- ✅ **Real-time Face Detection**: Detects faces in video feed with low latency
- ✅ **Face Recognition**: Identify known people from whitelist
- ✅ **Bounding Boxes**: Visual overlay showing detected faces on live feed
- ✅ **Status Indicators**: Color-coded boxes (Green=Friendly, Orange=Unknown, Red=Suspicious)
- ✅ **Live Dashboard**: Real-time face count and detection status

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd scripts
pip install -r requirements.txt
```

This will install:
- `opencv-python` - Computer vision library
- `face-recognition` - Face detection and recognition
- `dlib` - Machine learning library (with optional CUDA support)
- `numpy`, `requests`, `Pillow` - Supporting libraries

### 2. Check GPU Availability (Optional)

```bash
cd scripts
python check_gpu.py
```

This will show:
- ✅ Whether you have an NVIDIA GPU
- ✅ If CUDA is installed
- ✅ If dlib has CUDA support
- ✅ Expected performance (CPU vs GPU)

**Don't have GPU? No problem!** The system works great on CPU (5-10 FPS).

### 3. Start the Backend

```bash
cd backend
python main.py
```

Backend will start on `http://localhost:8000`

### 4. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will start on `http://localhost:5173`

### 5. Run Face Detection

**Basic usage (no whitelist):**
```bash
cd scripts
python face_detector_real.py --camera-index 0 --fps 30
```

**With face recognition:**
```bash
python face_detector_real.py --camera-index 0 --fps 30 --whitelist-dir /path/to/whitelist
```

---

## 📁 Whitelist Setup

To enable face recognition, organize your whitelist images like this:

```
whitelist/
├── John_Doe/
│   ├── photo1.jpg
│   ├── photo2.jpg
│   └── photo3.jpg
├── Jane_Smith/
│   ├── img1.jpg
│   └── img2.jpg
└── Bob_Johnson/
    └── face.jpg
```

**Requirements:**
- One folder per person (folder name = person's name)
- 1-5 photos per person (more is better)
- Clear face photos (front-facing, good lighting)
- Supported formats: `.jpg`, `.jpeg`, `.png`, `.bmp`

**Then run:**
```bash
python face_detector_real.py --camera-index 0 --whitelist-dir ./whitelist
```

---

## 🎮 Command Line Options

```bash
python face_detector_real.py [OPTIONS]
```

### Options:

| Option | Default | Description |
|--------|---------|-------------|
| `--camera-index` | 0 | Camera device index (0=default, try 1,2,3...) |
| `--fps` | 30 | Target frames per second |
| `--api-url` | http://localhost:8000 | Backend API URL |
| `--api-key` | doggobot-secret-key-change-me | API authentication key |
| `--whitelist-dir` | None | Path to whitelist directory |
| `--no-gpu` | False | Force CPU mode (disable GPU) |
| `--no-preview` | False | Disable preview window |
| `--post-every` | 1 | Post frame every N frames (reduce bandwidth) |

### Examples:

**Use a different camera:**
```bash
python face_detector_real.py --camera-index 2
```

**Force CPU mode:**
```bash
python face_detector_real.py --no-gpu
```

**Higher FPS (requires GPU):**
```bash
python face_detector_real.py --fps 60
```

**Run headless (no preview):**
```bash
python face_detector_real.py --no-preview
```

**Reduce bandwidth (post every 3rd frame):**
```bash
python face_detector_real.py --post-every 3
```

---

## 🎨 Bounding Box Colors

The live feed shows color-coded bounding boxes:

| Color | Status | Meaning |
|-------|--------|---------|
| 🟢 **Green** | FRIENDLY | Known person from whitelist |
| 🟠 **Orange** | UNKNOWN | Face detected but not recognized |
| 🔴 **Red** | SUSPICIOUS | Reserved for future threat detection |

Each box displays:
- **Top line**: Person's name (or "Unknown")
- **Bottom line**: Status text

---

## ⚡ GPU Acceleration

### Performance Comparison

| Mode | Speed | Hardware |
|------|-------|----------|
| **CPU** | 5-10 FPS | Any computer |
| **GPU (CUDA)** | 20-60 FPS | NVIDIA GPU with CUDA |

### Enabling GPU Acceleration

For detailed GPU setup instructions, see: **[GPU_ACCELERATION_GUIDE.md](./GPU_ACCELERATION_GUIDE.md)**

**Quick summary:**
1. Install CUDA Toolkit from NVIDIA
2. Install cuDNN library
3. Compile dlib with CUDA support
4. Run `python check_gpu.py` to verify

**The system automatically uses GPU if available!**

---

## 🖥️ Frontend - Viewing Bounding Boxes

Once everything is running:

1. Open browser to `http://localhost:5173`
2. Navigate to the **Live Feed** section
3. You should see:
   - ✅ Live video stream from camera
   - ✅ Bounding boxes around detected faces
   - ✅ Names and status labels
   - ✅ Face count in header (e.g., "2 faces detected")

**The bounding boxes update in real-time** as faces are detected!

---

## 🔧 Troubleshooting

### No camera found

**Error:** `Failed to open camera 0`

**Solutions:**
- Try different camera indices: `--camera-index 1`, `--camera-index 2`, etc.
- On Linux, check permissions: `sudo chmod 666 /dev/video0`
- On Windows, close other apps using the camera (Skype, Teams, etc.)
- Check available cameras:
  ```bash
  python -c "import cv2; print([i for i in range(10) if cv2.VideoCapture(i).isOpened()])"
  ```

### Bounding boxes not showing

**Possible causes:**

1. **Face detector not running**
   - Make sure `face_detector_real.py` is running
   - Check console for errors

2. **Backend not receiving frames**
   - Check backend logs for `/frame` POST requests
   - Verify API URL and key match

3. **Frontend not fetching detections**
   - Open browser console (F12) and check for errors
   - Verify backend is running on `http://localhost:8000`

4. **No faces detected**
   - Make sure you're in front of camera
   - Ensure good lighting
   - Try adjusting camera angle

### Low FPS / Slow performance

**On CPU:**
- Reduce target FPS: `--fps 10`
- Post fewer frames: `--post-every 3`
- Close other applications

**To improve with GPU:**
- See [GPU_ACCELERATION_GUIDE.md](./GPU_ACCELERATION_GUIDE.md)
- Install CUDA and compile dlib with GPU support

### Face recognition not working

**Common issues:**

1. **Whitelist not loaded**
   - Check console output for "Whitelist loaded: X people"
   - Verify folder structure (one folder per person)
   - Ensure photos contain clear faces

2. **Poor photo quality**
   - Use front-facing photos
   - Ensure good lighting
   - Multiple photos per person improves accuracy

3. **Distance/angle issues**
   - Face recognition works best when face is:
     - Front-facing (±30°)
     - Well-lit
     - 0.5-3 meters from camera

### Import errors

**Error:** `ModuleNotFoundError: No module named 'face_recognition'`

**Solution:**
```bash
cd scripts
pip install -r requirements.txt
```

**Error:** `dlib compilation failed`

**Solution:**
- Windows: Install Visual Studio with C++ tools
- Linux: `sudo apt-get install build-essential cmake`
- Then: `pip install dlib`

---

## 📊 Performance Metrics

The face detector displays real-time metrics:

**In preview window:**
- FPS: Current frames per second
- Faces: Number of faces detected
- Frame: Total frames processed
- GPU: ON/OFF status

**In browser (Live Feed header):**
- Face count: "X faces detected"

**In console:**
- Detection alerts: "📸 Alert: John Doe detected"
- Frame processing stats
- Whitelist loading status

---

## 🔐 Security Notes

- Default API key is `doggobot-secret-key-change-me`
- **Change this in production!** Edit in:
  - `scripts/face_detector_real.py` (API_KEY constant)
  - `backend/main.py` (API_KEY from .env)
  - When running: `--api-key YOUR_SECRET_KEY`

---

## 🎯 Next Steps

1. ✅ **Set up whitelist**: Add photos of people you want to recognize
2. ✅ **Optimize performance**: Install CUDA for GPU acceleration
3. ✅ **Adjust settings**: Fine-tune FPS, camera resolution, etc.
4. ✅ **Integrate with robot**: Connect to ROS2 for robot actions
5. ✅ **Add more features**: Emotion detection, age estimation, etc.

---

## 📚 Related Documentation

- [GPU_ACCELERATION_GUIDE.md](./GPU_ACCELERATION_GUIDE.md) - Detailed GPU setup
- [WHITELIST_SETUP_GUIDE.md](./WHITELIST_SETUP_GUIDE.md) - Face recognition setup
- [QUICK_START.md](./QUICK_START.md) - General DoggoBot setup
- [API.md](./docs/API.md) - Backend API reference

---

## 🆘 Getting Help

If you encounter issues:

1. Check console output for error messages
2. Run `python check_gpu.py` to diagnose GPU issues
3. Verify all services are running (backend, frontend, detector)
4. Check browser console for frontend errors (F12)
5. Review this troubleshooting section

---

## 🎉 Success!

When everything is working, you should see:

✅ Face detector console showing FPS and detections  
✅ Backend receiving frame and alert POST requests  
✅ Frontend displaying video with bounding boxes  
✅ Real-time updates as faces move in/out of frame  
✅ Color-coded boxes showing recognition status  

**Enjoy your GPU-accelerated face detection system! 🚀**

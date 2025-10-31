# 🎬 Scripts Folder

This folder contains various scripts for testing and running the DoggoBot face detection system.

---

## 📝 Scripts Overview

### 🎯 Main Scripts

#### `face_detector_real.py` ⭐
**The main face detection script** - Use this for real face recognition!

```bash
# Basic usage (camera 2, 15 FPS)
python face_detector_real.py

# Custom settings
python face_detector_real.py --camera-index 2 --fps 20

# Help
python face_detector_real.py --help
```

**Features:**
- Real face recognition using uploaded whitelist
- Detects friendly vs unknown people
- Posts alerts to backend
- Live preview window
- Press 'r' to reload whitelist
- Press 'q' to quit

---

### 🧪 Test & Setup Scripts

#### `test_camera.py`
Test which camera indices work on your system

```bash
# Test common cameras (0, 1, 2)
python test_camera.py

# Test specific camera
python test_camera.py --index 2

# Test all cameras (0-10)
python test_camera.py --all
```

#### `download_cascade.py`
Download Haar Cascade file if OpenCV can't find it

```bash
python download_cascade.py
```

Run this if you see errors about missing cascade files.

---

### 🔧 Other Scripts

#### `face_recognition_integrated.py`
Basic face detection without whitelist matching (demo/testing only)

```bash
python face_recognition_integrated.py --source 2 --fps 30
```

#### `sim_reactor_stub.py`
ROS2 reactor stub - listens to alerts and can trigger robot actions

```bash
python sim_reactor_stub.py
```

#### `ros2_reactor.py`
Full ROS2 integration (requires ROS2 installation)

---

## 📦 Installation

Install all dependencies:

```bash
cd scripts
pip install -r requirements.txt
```

### Requirements:
- `opencv-python` - Camera and video processing
- `face-recognition` - Face detection and recognition
- `dlib` - Face detection backend
- `numpy` - Array processing
- `requests` - API communication
- `Pillow` - Image processing

### Troubleshooting Installation:

**dlib won't install?**
```bash
# Ubuntu/Debian
sudo apt-get install build-essential cmake
sudo apt-get install libopenblas-dev liblapack-dev
pip install dlib

# macOS
brew install cmake
pip install dlib

# Windows
# Download pre-built wheel from:
# https://github.com/z-mahmud22/Dlib_Windows_Python3.x
```

---

## 🚀 Quick Start Workflow

1. **Test your camera first:**
   ```bash
   python test_camera.py
   ```

2. **Start backend/frontend:**
   ```bash
   cd ..
   docker-compose up -d
   ```

3. **Add people to whitelist:**
   - Open http://localhost:3000/settings
   - Upload photos of people you want to recognize

4. **Run the detector:**
   ```bash
   python face_detector_real.py
   ```

5. **Monitor alerts:**
   - View in dashboard at http://localhost:3000

---

## 🎮 Usage Tips

### Camera Selection
- Try `--camera-index 0`, `1`, or `2`
- Use `test_camera.py --all` to find available cameras
- On Windows, built-in webcam is usually index 0
- External USB cameras are typically index 1 or 2

### Performance
- **Slow computer?** Lower FPS: `--fps 10`
- **Fast computer?** Higher FPS: `--fps 30`
- Edit `process_every` in script to process fewer frames
- Lower camera resolution in script

### Recognition Accuracy
- Upload 3-5 photos per person to whitelist
- Use different angles and lighting
- Ensure faces are clearly visible
- Good lighting improves accuracy

---

## 🔍 What Each Script Does

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `face_detector_real.py` | Main face recognition | Production use |
| `test_camera.py` | Test camera setup | Before first run |
| `download_cascade.py` | Fix cascade errors | If OpenCV errors |
| `face_recognition_integrated.py` | Basic detection demo | Testing only |
| `sim_reactor_stub.py` | ROS2 alert listener | Robot integration |

---

## ⚙️ Configuration

### Default Settings:
- **Camera Index:** 2
- **FPS:** 15
- **Resolution:** 1280x720
- **Face Match Tolerance:** 0.6
- **Alert Cooldown:** 10 seconds

### To Change:
- Command line args: `--camera-index`, `--fps`, etc.
- Edit script directly for advanced settings
- Backend API URL: `--api-url http://localhost:8000`
- API Key: `--api-key your-key-here`

---

## 📚 More Help

- Main docs: `../HOW_TO_USE_FACE_RECOGNITION.md`
- API docs: http://localhost:8000/docs (when backend running)
- Project README: `../README.md`

---

**Questions?** Check the troubleshooting sections in the docs!

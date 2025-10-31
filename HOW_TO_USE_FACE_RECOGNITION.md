# 🎯 How to Use Face Recognition with DoggoBot

## Overview
The system now uses **real face recognition** to detect people from your camera and compare them against a whitelist you manage through the website.

---

## 🚀 Quick Start

### Step 1: Start the Backend & Frontend

```bash
# Option 1: Docker (easiest)
docker-compose up -d

# Option 2: Manual
# Terminal 1 - Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

### Step 2: Add People to Whitelist

1. Open the dashboard: **http://localhost:3000**
2. Go to **Settings** → **Whitelist Management**
3. For each person you want to recognize:
   - Enter their name (e.g., "John", "Sarah")
   - Upload 3-5 clear photos of their face
   - Click **"Add Person"**
4. After adding people, click **"Refresh Encodings"**

### Step 3: Install Face Recognition Library

```bash
cd scripts

# Install dependencies (includes face_recognition)
pip install -r requirements.txt

# Note: On some systems you may need to install cmake first:
# Ubuntu/Debian: sudo apt-get install cmake
# macOS: brew install cmake
# Windows: Download from https://cmake.org/download/
```

### Step 4: Run the Face Detector

```bash
# Basic usage (camera index 2, 15 FPS)
python face_detector_real.py

# Custom settings
python face_detector_real.py --camera-index 2 --fps 20

# Different camera
python face_detector_real.py --camera-index 0
```

---

## 🎮 How It Works

### Detection Status
The system assigns one of three statuses to detected people:

- **🟢 FRIENDLY** (Green box)
  - Person is in the whitelist
  - Shows their name + confidence score
  - Example: "John (0.89)"

- **🔴 UNKNOWN** (Red box)  
  - Person not in whitelist
  - Shows "Unknown"
  - Creates alert in dashboard

- **🟠 SUSPICIOUS** (Orange box)
  - Can be triggered by specific behaviors
  - Loitering detection (future feature)

### Alert Cooldown
- Alerts for the same person are sent every 10 seconds (configurable)
- Prevents spam from continuous detection

### Live Preview
- Shows camera feed with detection boxes
- Press **'q'** to quit
- Press **'r'** to reload whitelist (after adding new people)

---

## 📊 Monitoring in Dashboard

Once the detector is running:

1. **Command Center** shows:
   - Live video feed with detection boxes
   - Real-time alerts as people are detected
   - Alert cards color-coded by status

2. **Alerts Page** shows:
   - Full history of all detections
   - Filter by status (friendly/unknown)
   - Snapshot images of each detection

3. **Settings Page** allows:
   - Adding/removing whitelist people
   - Configuring detection thresholds
   - Managing API keys

---

## 🔧 Configuration

### Camera Settings
Edit in the script or use command-line args:
- **Camera Index**: Which camera to use (default: 2)
- **FPS**: Streaming frame rate (default: 15)
- **Resolution**: 1280x720 (configured in script)

### Recognition Settings
- **Tolerance**: 0.6 (lower = stricter matching)
- **Process Every N Frames**: 3 (for performance)
- **Alert Cooldown**: 10 seconds

### Backend Settings
In `backend/.env`:
```bash
API_KEY=doggobot-secret-key-change-me
HOST=0.0.0.0
PORT=8000
```

---

## 🛠️ Troubleshooting

### "face_recognition library not installed"
```bash
# Install dependencies
pip install face-recognition dlib

# If dlib fails to install:
# Ubuntu/Debian
sudo apt-get install build-essential cmake
sudo apt-get install libopenblas-dev liblapack-dev
pip install dlib

# macOS
brew install cmake
pip install dlib

# Windows
# Download pre-built wheel from https://github.com/z-mahmud22/Dlib_Windows_Python3.x
```

### "Could not open camera at index 2"
```bash
# Try different camera indices
python face_detector_real.py --camera-index 0
python face_detector_real.py --camera-index 1

# List available cameras (Linux)
ls /dev/video*
```

### No faces detected
- Ensure good lighting
- Face camera directly
- Use clear, high-quality photos for whitelist
- Upload 3-5 different photos per person (different angles)

### Low recognition accuracy
- Add more whitelist photos per person
- Use photos with clear, front-facing faces
- Adjust tolerance in script (line 158): `tolerance=0.6` → `tolerance=0.7`
- Ensure whitelist photos match lighting conditions

### "No whitelist entries found"
1. Go to http://localhost:3000/settings
2. Add people via Whitelist Management
3. Press 'r' in the detector window to reload
4. Or restart the detector script

---

## 💡 Tips

### For Best Recognition
- Upload 3-5 photos per person
- Use photos with different angles and lighting
- Ensure faces are clearly visible
- Use recent photos

### For Performance
- Lower FPS if system is slow: `--fps 10`
- Increase `process_every` in script (line 346)
- Use smaller camera resolution

### For Smooth Feed
- Higher FPS: `--fps 20` or `--fps 30`
- Ensure good network connection (if remote)
- Close other programs using the camera

---

## 📝 Example Workflow

1. **Start services**: `docker-compose up -d`
2. **Open dashboard**: http://localhost:3000
3. **Add people**: Go to Settings → Upload photos of family members
4. **Start detector**: `cd scripts && python face_detector_real.py`
5. **Monitor**: Watch Command Center for real-time detections
6. **Acknowledge**: Click "Ack" on alerts to review them

---

## 🔐 Security Notes

- **Change API key** in production (`backend/.env`)
- **Restrict access** to whitelist management
- **Regular backups** of the database
- **Privacy**: Snapshots are stored locally in `storage/snapshots/`

---

## 🎯 What's Next?

After basic setup works:
- Add more people to whitelist
- Integrate with robot controls (sim_reactor)
- Set up loitering detection
- Configure alert notifications
- Deploy to production server

---

**Need help?** Check the main README.md or open an issue!

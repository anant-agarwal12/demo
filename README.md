# ?? DoggoBot - Face Detection System

Simple, clean face detection with bounding boxes and whitelist management.

## ?? Quick Start

### 1. Install Dependencies
```bash
cd scripts
pip install -r requirements.txt
```

### 2. Start Backend
```bash
cd backend
python main.py
```

### 3. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

### 4. Run Face Detector
```bash
cd scripts
python face_detector.py
```

**Open browser**: http://localhost:5173

---

## ? Features

- ?? Webcam face detection
- ?? HOG (CPU) or CNN (GPU) modes
- ?? Whitelist management via website
- ?? Real-time bounding boxes on live feed
- ? Face recognition with color-coded status
  - ?? Green = Known person (friendly)
  - ?? Orange = Unknown person

---

## ?? Commands

### Face Detector

**CPU Mode (default)**
```bash
python face_detector.py
```

**GPU Mode**
```bash
python face_detector.py --mode cnn
```

**Different Camera**
```bash
python face_detector.py --camera 1
```

### Hotkeys (in preview window)
- **q** - Quit
- **r** - Reload whitelist from backend
- **m** - Toggle HOG/CNN mode

---

## ?? Add People to Whitelist

1. Open http://localhost:5173
2. Go to **Settings** page
3. Click **Add to Whitelist**
4. Enter name and upload 2-5 photos
5. Press **'r'** in face detector to reload

---

## ?? Structure

```
??? backend/          # FastAPI backend
?   ??? main.py       # API endpoints
?   ??? database.py   # SQLite database
?   ??? ...
??? frontend/         # React frontend
?   ??? src/
?       ??? components/
?       ?   ??? VideoFeed.jsx  # Bounding boxes
?       ??? ...
??? scripts/
    ??? face_detector.py      # MAIN SCRIPT
    ??? requirements.txt
```

---

## ?? Tech Stack

- **Backend**: FastAPI, SQLite
- **Frontend**: React, Vite, Tailwind CSS
- **Detection**: OpenCV, face_recognition, dlib
- **Modes**: HOG (CPU) or CNN (GPU)

---

## ?? Documentation

- [SIMPLE_SETUP.md](SIMPLE_SETUP.md) - Full setup guide
- [QUICK_COMMANDS.md](QUICK_COMMANDS.md) - Quick reference

---

## ?? Configuration

Edit `scripts/face_detector.py`:
```python
API_URL = "http://localhost:8000"
API_KEY = "doggobot-secret-key-change-me"
```

---

**Clean. Simple. Works.** ??

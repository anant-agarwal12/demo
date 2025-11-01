# 🚀 Quick Commands

## Install
```bash
cd scripts
pip install -r requirements.txt
```

## Start System

### Backend
```bash
cd backend
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Face Detector

**CPU Mode (default)**
```bash
cd scripts
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

## Hotkeys

In the face detector preview window:
- **q** - Quit
- **r** - Reload whitelist
- **m** - Toggle HOG/CNN mode

## Access Points

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Add People to Whitelist

1. Go to http://localhost:5173
2. Click **Settings**
3. **Add to Whitelist**
4. Upload 2-5 photos
5. Press **'r'** in face detector

## Modes

| Mode | Speed | Hardware |
|------|-------|----------|
| HOG | 5-15 FPS | CPU (any) |
| CNN | 20-60 FPS | NVIDIA GPU |

Switch with `--mode` or press **'m'** while running!

## Full Example
```bash
# Terminal 1
cd backend && python main.py

# Terminal 2
cd frontend && npm run dev

# Terminal 3
cd scripts && python face_detector.py

# Browser: http://localhost:5173
```

**Done!** 🎉

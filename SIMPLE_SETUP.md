# 🚀 Simple Face Detection Setup

Clean and simple face detection with bounding boxes!

## ✨ Features

- 📹 Webcam face detection
- 🧠 HOG (CPU) or CNN (GPU) modes
- 👤 Whitelist management from website
- 📦 Bounding boxes on live feed
- ⚡ Real-time face recognition

---

## 🎯 Quick Start

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

Backend runs on `http://localhost:8000`

### 3. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`

### 4. Run Face Detector

```bash
cd scripts
python face_detector.py
```

**That's it!** 🎉

---

## 📝 Usage

### Basic (CPU mode)
```bash
python face_detector.py
```

### GPU mode (CNN)
```bash
python face_detector.py --mode cnn
```

### Different camera
```bash
python face_detector.py --camera 1
```

### Hotkeys (in preview window)
- **q** - Quit
- **r** - Reload whitelist from backend
- **m** - Toggle between HOG (CPU) and CNN (GPU)

---

## 👤 Managing Whitelist

### Add People via Website:

1. Open `http://localhost:5173`
2. Go to **Settings** page
3. Click **"Add to Whitelist"**
4. Enter name
5. Upload 2-5 photos
6. Click **Submit**

### Reload in Detector:

Press **'r'** in the face detector preview window to reload whitelist.

---

## 🎨 What You'll See

### In Browser (`localhost:5173`):
- **Live video feed**
- **Green boxes** around known people (from whitelist)
- **Orange boxes** around unknown people
- **Face counter** in header

### In Preview Window:
- Same as browser
- Plus FPS counter
- Current mode (HOG/CNN)
- Face count

---

## ⚙️ Modes

### HOG Mode (CPU) - Default
```bash
python face_detector.py --mode hog
```
- **Speed**: 5-15 FPS
- **Works on**: Any computer
- **Good for**: Testing, single person

### CNN Mode (GPU)
```bash
python face_detector.py --mode cnn
```
- **Speed**: 20-60 FPS
- **Requires**: NVIDIA GPU with CUDA
- **Good for**: Multiple people, production

**Toggle anytime**: Press **'m'** in preview window!

---

## 🔧 Configuration

Edit at top of `face_detector.py`:

```python
API_URL = "http://localhost:8000"  # Backend URL
API_KEY = "doggobot-secret-key-change-me"  # API key
```

Or pass via command line:

```bash
python face_detector.py --api-url http://192.168.1.100:8000 --api-key your-key
```

---

## 🐛 Troubleshooting

### Camera not opening
```bash
# Try different camera indices
python face_detector.py --camera 0
python face_detector.py --camera 1
python face_detector.py --camera 2
```

### No bounding boxes on website
1. Make sure face detector is running
2. Check backend is running (port 8000)
3. Refresh browser page

### Whitelist not loading
1. Add people via website Settings page first
2. Press **'r'** in detector window to reload
3. Check backend console for errors

### Low FPS
- Use HOG mode (CPU): `python face_detector.py --mode hog`
- CNN mode requires NVIDIA GPU

---

## 📊 Status Indicators

| Color | Status | Meaning |
|-------|--------|---------|
| 🟢 Green | FRIENDLY | Person in whitelist |
| 🟠 Orange | UNKNOWN | Face detected, not in whitelist |

---

## 💡 Tips

1. **Better lighting = better detection**
2. **2-5 photos per person** in whitelist
3. **Front-facing photos** work best
4. **Press 'm'** to switch modes on-the-fly
5. **Press 'r'** after adding people to whitelist

---

## 🎯 Complete Example

```bash
# Terminal 1: Backend
cd backend
python main.py

# Terminal 2: Frontend  
cd frontend
npm run dev

# Terminal 3: Face Detector
cd scripts
pip install -r requirements.txt
python face_detector.py --mode hog

# Browser: http://localhost:5173
# Add people to whitelist in Settings
# Press 'r' in detector window
# Watch bounding boxes appear!
```

---

## ✅ Success Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Face detector running with preview window
- [ ] Can see yourself in preview
- [ ] Bounding box appears on website
- [ ] Added person to whitelist
- [ ] Green box shows for known person

---

**Simple and clean! 🎊**

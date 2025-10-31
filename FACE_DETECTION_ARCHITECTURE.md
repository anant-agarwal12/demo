# Face Detection System Architecture

## 🏗️ System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        HARDWARE LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  📹 Camera (USB/Built-in)  ←→  🖥️ CPU  ←→  🎮 GPU (Optional)   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    FACE DETECTION LAYER                          │
│                  (face_detector_real.py)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. Capture Frame (OpenCV)                                       │
│       ↓                                                           │
│  2. Detect Faces (dlib + CUDA/CPU)                               │
│       ↓                                                           │
│  3. Generate Encodings (face_recognition)                        │
│       ↓                                                           │
│  4. Match Against Whitelist                                      │
│       ↓                                                           │
│  5. Generate Bounding Box Data                                   │
│       ↓                                                           │
│  6. Draw Overlays (names, status, boxes)                         │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     COMMUNICATION LAYER                          │
│                    (HTTP POST Requests)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  POST /frame                                                      │
│    ├─ Frame: JPEG image data                                     │
│    └─ Detections: JSON array                                     │
│         [                                                         │
│           {                                                       │
│             "bbox": {"x": 100, "y": 50, "width": 150, ...},      │
│             "name": "John Doe",                                   │
│             "status": "friendly"                                  │
│           },                                                      │
│           ...                                                     │
│         ]                                                         │
│                                                                   │
│  POST /alert (when face detected)                                │
│    ├─ Snapshot: JPEG image                                       │
│    └─ Payload: JSON alert data                                   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND API LAYER                           │
│                        (main.py)                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Global State:                                                    │
│    • latest_frame: Current video frame                           │
│    • latest_detections: Current bounding box data                │
│                                                                   │
│  Endpoints:                                                       │
│    • GET  /video_feed   → MJPEG stream                           │
│    • GET  /detections   → Latest detection data                  │
│    • POST /frame        → Upload frame + detections              │
│    • POST /alert        → Create detection alert                 │
│    • GET  /stream       → SSE for real-time updates              │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND LAYER                               │
│                    (VideoFeed.jsx)                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Components:                                                      │
│    1. <img> element: Video stream display                        │
│    2. <canvas> overlay: Bounding boxes                           │
│                                                                   │
│  React Hooks:                                                     │
│    • useEffect #1: Fetch detections (100ms interval)             │
│    • useEffect #2: Update video dimensions                       │
│    • useEffect #3: Draw bounding boxes (RAF loop)                │
│                                                                   │
│  Drawing Logic:                                                   │
│    1. Clear canvas                                                │
│    2. Calculate scale factors                                     │
│    3. For each detection:                                         │
│        a. Scale bbox coordinates                                  │
│        b. Choose color (green/orange/red)                         │
│        c. Draw rectangle                                          │
│        d. Draw label background                                   │
│        e. Draw name and status text                              │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       USER INTERFACE                             │
│                     (Browser Display)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌───────────────────────────────────────────────────────┐      │
│  │ Live Feed                         2 faces detected ✓  │      │
│  ├───────────────────────────────────────────────────────┤      │
│  │                                                         │      │
│  │   ┌─────────────────┐                                  │      │
│  │   │ John Doe        │  🟢 Green box (Friendly)         │      │
│  │   │ FRIENDLY        │                                  │      │
│  │   └─────────────────┘                                  │      │
│  │                                                         │      │
│  │            ┌─────────────────┐                         │      │
│  │            │ Unknown         │  🟠 Orange box          │      │
│  │            │ UNKNOWN         │                         │      │
│  │            └─────────────────┘                         │      │
│  │                                                         │      │
│  └─────────────────────────────────────────────────────────┘      │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow

### Frame Processing Pipeline

```
Camera Frame
    ↓
[1] OpenCV Capture (cv2.VideoCapture)
    • Read frame from camera
    • Apply FPS limiting
    ↓
[2] Pre-processing
    • Resize to 50% for speed (optional)
    • Convert BGR → RGB
    ↓
[3] Face Detection (dlib)
    • Model: CNN (GPU) or HOG (CPU)
    • Returns: [(top, right, bottom, left), ...]
    ↓
[4] Face Encoding (face_recognition)
    • Generate 128-D face embeddings
    • One per detected face
    ↓
[5] Face Matching
    • Compare with whitelist encodings
    • Calculate face distances
    • Match if distance < threshold (0.6)
    ↓
[6] Generate Detection Data
    • Bounding box coordinates
    • Matched name or "Unknown"
    • Status: friendly/unknown/suspicious
    ↓
[7] Draw Overlays (local preview)
    • Draw rectangles
    • Add labels and status
    • Show FPS and stats
    ↓
[8] Encode as JPEG
    • Quality: 85%
    • Format: JPEG bytes
    ↓
[9] HTTP POST to Backend
    • Endpoint: /frame
    • Body: multipart/form-data
    • Parts: frame (image), detections (JSON)
    ↓
[10] Backend Storage
    • Store in global variables
    • latest_frame ← frame data
    • latest_detections ← JSON array
    ↓
[11] Frontend Fetch (parallel)
    ├─ Video: GET /video_feed (MJPEG stream)
    └─ Data: GET /detections (JSON polling)
    ↓
[12] Browser Rendering
    • <img>: Display video frame
    • <canvas>: Draw bounding boxes
    • Update face counter
```

---

## 🎨 Frontend Rendering Details

### Canvas Overlay System

```javascript
// 1. Setup
<div style="position: relative">
  <img src="/video_feed" />     ← Video layer (background)
  <canvas />                     ← Overlay layer (foreground)
</div>

// 2. Coordinate Scaling
containerWidth = 1920  // Display width
containerHeight = 1080 // Display height
videoWidth = 1280      // Actual video width
videoHeight = 720      // Actual video height

scaleX = containerWidth / videoWidth
scaleY = containerHeight / videoHeight
scale = min(scaleX, scaleY)  // Maintain aspect ratio

// 3. Bounding Box Transformation
displayX = (detectionX * scale) + offsetX
displayY = (detectionY * scale) + offsetY
displayWidth = detectionWidth * scale
displayHeight = detectionHeight * scale

// 4. Drawing (60 FPS via requestAnimationFrame)
ctx.clearRect(0, 0, width, height)
for each detection:
  - Draw rectangle (strokeRect)
  - Draw label background (fillRect)
  - Draw name text (fillText)
  - Draw status text (fillText)
```

---

## ⚡ Performance Optimizations

### 1. Frame Processing
```
┌────────────────────────────────────┐
│ Original: 1280x720 (921,600 pixels)│
│           ↓ Resize 50%              │
│ Processed: 640x360 (230,400 pixels)│  ← 4x faster
│           ↓ Scale back              │
│ Display: 1280x720                   │
└────────────────────────────────────┘
```

### 2. Detection Throttling
```python
# Process every frame (GPU)
if frame_count % 1 == 0:
    detect_faces()

# Process every 3rd frame (CPU)
if frame_count % 3 == 0:
    detect_faces()
```

### 3. Frontend Polling
```javascript
// Video stream: 30 FPS (MJPEG built-in)
// Detection data: 10 FPS (setInterval 100ms)
// Canvas rendering: 60 FPS (requestAnimationFrame)
```

### 4. GPU Acceleration
```
CPU Mode:
  Face Detection: 100-200ms per frame → 5-10 FPS

GPU Mode (CUDA):
  Face Detection: 20-50ms per frame → 20-60 FPS
```

---

## 🔐 Security Flow

```
Face Detector              Backend              Frontend
     │                        │                     │
     │ POST /frame            │                     │
     ├───────────────────────>│                     │
     │ X-API-KEY: secret      │                     │
     │                        │                     │
     │ ✓ Key validated        │                     │
     │<───────────────────────┤                     │
     │ 200 OK                 │                     │
     │                        │                     │
     │                        │ GET /detections     │
     │                        │<────────────────────┤
     │                        │                     │
     │                        │ ✓ Public endpoint   │
     │                        ├────────────────────>│
     │                        │ JSON data           │
```

---

## 📊 State Management

### Backend Global State
```python
# Shared between all requests
latest_frame: bytes = None          # JPEG image data
latest_detections: List[Dict] = []  # Detection metadata
frame_lock: asyncio.Lock            # Thread safety
```

### Frontend Component State
```javascript
// React component state
const [detections, setDetections] = useState([])
const [videoSize, setVideoSize] = useState({width: 0, height: 0})

// Refs (non-reactive)
const videoRef = useRef(null)        // <img> element
const canvasRef = useRef(null)       // <canvas> element
const animationFrameRef = useRef()   // RAF handle
```

---

## 🧪 Detection Data Schema

### Sent from Detector → Backend
```json
{
  "bbox": {
    "x": 100,          // Left coordinate
    "y": 50,           // Top coordinate
    "width": 150,      // Box width
    "height": 200      // Box height
  },
  "name": "John Doe", // Matched name or "Unknown"
  "status": "friendly" // friendly|unknown|suspicious
}
```

### Stored in Backend
```python
latest_detections = [
  {
    "bbox": {"x": 100, "y": 50, "width": 150, "height": 200},
    "name": "John Doe",
    "status": "friendly"
  },
  # ... more detections
]
```

### Retrieved by Frontend
```javascript
{
  "detections": [
    {
      "bbox": {"x": 100, "y": 50, "width": 150, "height": 200},
      "name": "John Doe",
      "status": "friendly"
    }
  ],
  "timestamp": 1698765432.123
}
```

---

## 🎯 Key Technologies

| Layer | Technology | Purpose |
|-------|------------|---------|
| Camera | OpenCV (cv2) | Frame capture |
| Detection | dlib + CUDA | Face detection |
| Recognition | face_recognition | Face encoding/matching |
| Backend | FastAPI | HTTP API server |
| Frontend | React | UI components |
| Rendering | Canvas 2D | Bounding box overlay |
| Streaming | MJPEG | Video transport |
| Sync | Polling + RAF | Real-time updates |

---

## 🚀 Scalability Notes

### Single Camera Performance
- **CPU**: 5-10 FPS, ~10-20% CPU usage
- **GPU**: 20-60 FPS, ~20-40% GPU usage

### Multiple Cameras
Run multiple detector instances:
```bash
# Camera 0
python face_detector_real.py --camera-index 0 --api-key key1

# Camera 1
python face_detector_real.py --camera-index 1 --api-key key2

# Camera 2
python face_detector_real.py --camera-index 2 --api-key key3
```

Each instance:
- Independent processing
- Shared backend
- Separate preview windows
- Own detection data

---

## 💡 Future Enhancements

### Potential Improvements
1. **WebSocket** instead of polling for lower latency
2. **WebCodecs API** for hardware video decoding
3. **Web Workers** for off-main-thread canvas rendering
4. **Redis** for multi-backend scaling
5. **RTSP** for professional cameras
6. **TensorRT** for even faster GPU inference
7. **Face tracking** to maintain identity across frames
8. **Emotion detection** using facial landmarks
9. **Age/gender estimation** with additional models

---

This architecture provides a solid foundation for real-time face detection with room for growth! 🎉

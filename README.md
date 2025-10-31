# ?? DoggoBot Dashboard

A full-stack security robot monitoring dashboard with real-time detection alerts, operator controls, and natural language commands.

## ?? Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Development Setup](#development-setup)
- [API Documentation](#api-documentation)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## ? Features

### ?? NEW: GPU-Accelerated Face Detection
- **GPU Acceleration**: CUDA support for 3-6x performance boost (20-60 FPS vs 5-10 FPS)
- **Real-time Bounding Boxes**: Visual face detection overlay on live feed
- **Face Recognition**: Whitelist-based identification of known people
- **Color-coded Detection**: Green=Friendly, Orange=Unknown, Red=Suspicious
- **Live Face Counter**: Shows number of detected faces in real-time
- **Auto GPU Detection**: Automatically uses GPU when available, falls back to CPU

?? **See:** [GPU_AND_BOUNDING_BOXES_UPDATE.md](./GPU_AND_BOUNDING_BOXES_UPDATE.md) for setup instructions

### Command Center
- **Live Video Feed**: MJPEG streaming from robot camera with face detection overlays
- **Real-time Alerts**: Server-Sent Events (SSE) for instant notifications
- **Alert Cards**: Color-coded status (Friendly/Unknown/Suspicious)
- **Operator Controls**: Start/Stop patrol, Return home, Follow, Investigate
- **NLP Chat**: Natural language command interface with TTS responses
- **Audit Timeline**: Historical view of all detection events

### Alert Management
- **Full History**: Comprehensive alert listing with filtering
- **Filters**: By status, acknowledged state, time range
- **Bulk Actions**: Acknowledge multiple alerts, export CSV
- **Snapshot Viewing**: Expand and download detection images

### Settings & Configuration
- **Whitelist Management**: Add/remove known people with face images
- **API Key Management**: Secure authentication for perception nodes
- **Threshold Configuration**: Adjust detection sensitivity, loitering time, distance limits

## ?? Tech Stack

### Backend
- **FastAPI**: Modern async Python web framework
- **SQLite**: Lightweight database for alerts and whitelist
- **pyttsx3**: Offline text-to-speech synthesis
- **SSE**: Server-Sent Events for real-time updates
- **Python 3.10+**

### Frontend
- **React 18**: Modern UI framework
- **Vite**: Lightning-fast build tool
- **TailwindCSS**: Utility-first CSS framework
- **React Router**: Client-side routing

### DevOps
- **Docker**: Containerized deployment
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Reverse proxy for production

## ?? Architecture

```
???????????????????
?  Perception     ? ???
?  Node (Camera)  ?   ?
???????????????????   ?
                      ? POST /frame
???????????????????   ? POST /alert
?  Detector       ? ???
?  Publisher      ?   ?
???????????????????   ?
                      ?
              ????????????????
              ?   Backend    ?
              ?   FastAPI    ?
              ?              ?
              ?  - REST API  ?
              ?  - SSE       ?
              ?  - TTS       ?
              ?  - SQLite    ?
              ????????????????
                     ?
                     ? SSE Stream
                     ? REST API
                     ?
              ????????????????
              ?   Frontend   ?
              ?   React      ?
              ?              ?
              ?  - Dashboard ?
              ?  - Alerts    ?
              ?  - Settings  ?
              ????????????????
                     ?
                     ? ROS2 Commands
                     ?
              ????????????????
              ?  Sim Reactor ?
              ?  (Gazebo)    ?
              ????????????????
```

## ?? Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd workspace

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Access the dashboard
open http://localhost:3000
```

### Option 2: Manual Setup

**Backend:**

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

**Frontend:**

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## ?? Development Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose (optional)

### Backend Setup

1. **Install Dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure Environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Run Development Server:**
   ```bash
   python main.py
   # Server runs on http://localhost:8000
   ```

4. **API Documentation:**
   Open http://localhost:8000/docs for interactive Swagger UI

### Frontend Setup

1. **Install Dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure Environment:**
   ```bash
   # Create .env file
   echo "VITE_API_BASE=http://localhost:8000" > .env
   ```

3. **Run Development Server:**
   ```bash
   npm run dev
   # Frontend runs on http://localhost:3000
   ```

## ?? API Documentation

### Authentication

Protected endpoints require an `X-API-KEY` header:

```bash
curl -H "X-API-KEY: your-api-key" http://localhost:8000/frame
```

### Key Endpoints

#### POST /frame
Upload video frame for live feed.

```bash
curl -X POST http://localhost:8000/frame \
  -H "X-API-KEY: doggobot-secret-key-change-me" \
  -F "frame=@frame.jpg"
```

#### POST /alert
Create detection alert.

```bash
curl -X POST http://localhost:8000/alert \
  -H "X-API-KEY: doggobot-secret-key-change-me" \
  -F 'payload={"label":"person","status":"unknown","confidence":0.89}' \
  -F "snapshot=@snapshot.jpg"
```

#### GET /stream
SSE stream for real-time events.

```bash
curl -N http://localhost:8000/stream
```

#### POST /nlp
Send natural language command.

```bash
curl -X POST http://localhost:8000/nlp \
  -H "Content-Type: application/json" \
  -d '{"text": "status"}'
```

#### GET /alerts
List alerts with filtering.

```bash
curl "http://localhost:8000/alerts?status=unknown&limit=20"
```

#### POST /alerts/{id}/ack
Acknowledge an alert.

```bash
curl -X POST http://localhost:8000/alerts/alert_123/ack
```

### Full API Reference

Visit http://localhost:8000/docs when the backend is running for complete API documentation.

## ?? Usage Examples

### Running the Detector Publisher

The detector publisher simulates a perception node that sends frames and alerts:

```bash
cd scripts
pip install -r requirements.txt

# Run with default settings
python detector_example.py

# Custom configuration
python detector_example.py \
  --api-url http://localhost:8000 \
  --api-key doggobot-secret-key-change-me \
  --fps 10
```

### Running the Simulation Reactor

The sim reactor listens to alerts and reacts accordingly:

```bash
cd scripts

# Connect via SSE (recommended)
python sim_reactor_stub.py

# Poll mode
python sim_reactor_stub.py --mode poll --poll-interval 5
```

### Adding People to Whitelist

Via API:

```bash
curl -X POST http://localhost:8000/whitelist/add \
  -F "name=Alice" \
  -F "images=@alice1.jpg" \
  -F "images=@alice2.jpg" \
  -F "images=@alice3.jpg"
```

Via UI:
1. Go to Settings ? Whitelist Management
2. Enter person's name
3. Upload 3-5 images
4. Click "Add Person"
5. Click "Refresh Encodings"

## ?? Configuration

### Backend (.env)

```bash
# API Security
API_KEY=doggobot-secret-key-change-me

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Storage
STORAGE_PATH=./storage
```

### Frontend (.env)

```bash
# Backend API URL
VITE_API_BASE=http://localhost:8000
```

### Detection Thresholds

Configure in the UI (Settings ? Thresholds):
- **Face Match Threshold**: 0.6 (lower = more lenient)
- **Loitering Time**: 30 seconds
- **Detection Distance**: 10 meters

## ?? Deployment

### Production with Docker

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

### Production Considerations

1. **Change API Key:**
   ```bash
   # In backend/.env or docker-compose.yml
   API_KEY=your-secure-random-key-here
   ```

2. **Enable HTTPS:**
   - Use Nginx with Let's Encrypt
   - Update CORS settings in `backend/main.py`

3. **Set DEBUG=False:**
   ```bash
   # In backend/.env
   DEBUG=False
   ```

4. **Configure CORS:**
   ```python
   # In backend/main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://yourdomain.com"],
       ...
   )
   ```

5. **Persistent Storage:**
   Docker volumes are configured for persistence. Backup regularly:
   ```bash
   docker-compose exec backend tar czf /backup.tar.gz /app/storage
   docker cp doggobot-backend:/backup.tar.gz ./backup.tar.gz
   ```

## ?? Troubleshooting

### Backend Won't Start

**Issue:** `ImportError: No module named 'fastapi'`
```bash
cd backend
pip install -r requirements.txt
```

**Issue:** `pyttsx3` errors on Linux
```bash
sudo apt-get install espeak libespeak-dev
```

### Frontend Won't Connect

**Issue:** "Failed to connect to backend"
- Check backend is running: `curl http://localhost:8000/health`
- Verify VITE_API_BASE in `frontend/.env`
- Check CORS settings in `backend/main.py`

### Video Feed Not Working

**Issue:** Black screen or "No signal"
- Ensure detector is posting frames: run `scripts/detector_example.py`
- Check browser console for errors
- Verify `/video_feed` endpoint: `curl http://localhost:8000/video_feed`

### SSE Connection Issues

**Issue:** "SSE disconnected" or constant reconnection
- Check firewall rules (port 8000)
- Disable proxy buffering (nginx config provided)
- Browser console: look for CORS errors

### Docker Issues

**Issue:** Port already in use
```bash
# Check what's using the port
sudo lsof -i :8000
sudo lsof -i :3000

# Stop conflicting services or change ports in docker-compose.yml
```

**Issue:** Permission denied
```bash
# Linux: add user to docker group
sudo usermod -aG docker $USER
# Log out and back in
```

## ?? Project Structure

```
workspace/
??? backend/                 # FastAPI backend
?   ??? main.py             # Main application
?   ??? database.py         # SQLite database layer
?   ??? tts_engine.py       # Text-to-speech
?   ??? nlp_handler.py      # NLP command processor
?   ??? requirements.txt    # Python dependencies
?   ??? Dockerfile          # Backend container
?   ??? .env                # Environment variables
?
??? frontend/               # React frontend
?   ??? src/
?   ?   ??? pages/          # Page components
?   ?   ??? components/     # Reusable components
?   ?   ??? hooks/          # Custom React hooks
?   ?   ??? api/            # API client
?   ?   ??? App.jsx         # Main app component
?   ??? package.json        # Node dependencies
?   ??? Dockerfile          # Frontend container
?   ??? .env                # Environment variables
?
??? scripts/                # Example scripts
?   ??? detector_example.py # Simulated perception node
?   ??? sim_reactor_stub.py # Gazebo reactor example
?   ??? requirements.txt    # Script dependencies
?
??? docker-compose.yml      # Multi-container setup
??? .gitignore             # Git ignore rules
??? README.md              # This file
```

## ?? NLP Commands

The system understands natural language commands:

| Command | Action |
|---------|--------|
| `status` | Report current system status |
| `start patrol` | Begin autonomous patrol |
| `stop` / `halt` | Stop all movement |
| `return home` | Navigate to home position |
| `follow` | Enter follow mode |
| `investigate` | Approach and investigate area |
| `greet` | Play greeting animation |
| `alarm` | Sound alarm |

## ?? Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## ?? License

This project is licensed under the MIT License.

## ?? Known Issues & Future Work

- [ ] TTS may have latency on first synthesis (engine warmup)
- [ ] SSE reconnection logic could be more robust
- [ ] Add proper face recognition integration (currently stubs)
- [ ] Implement actual ROS2 commands in sim_reactor
- [ ] Add user authentication (multi-operator support)
- [ ] Mobile-responsive improvements
- [ ] Add dark mode
- [ ] Implement alert replay with frame sequences
- [ ] Add system metrics dashboard

## ?? Tips

1. **Performance**: Adjust FPS in detector_example.py based on network capacity
2. **Testing**: Use detector_example.py to generate test data
3. **Monitoring**: Check `/metrics` endpoint for system health
4. **Debugging**: Set `DEBUG=True` in backend for detailed logs
5. **Privacy**: Auto-delete old snapshots (see Settings ? Thresholds)

## ?? Support

For issues and questions:
1. Check this README
2. Review API docs at `/docs`
3. Check browser console for frontend errors
4. Check backend logs for server errors
5. Open an issue on GitHub

---

**Built with ?? for the DoggoBot Hackathon**

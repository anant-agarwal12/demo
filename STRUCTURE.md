# ?? DoggoBot Project Structure

```
workspace/
?
??? ?? README.md                    # Main documentation
??? ?? PROJECT_SUMMARY.md           # Project completion summary
??? ?? STRUCTURE.md                 # This file
??? ?? .gitignore                   # Git ignore patterns
??? ?? start.sh                     # Quick start script
??? ?? docker-compose.yml           # Docker orchestration
?
??? ?? backend/                     # FastAPI Backend
?   ??? ?? main.py                  # Main FastAPI application
?   ??? ?? database.py              # SQLite database layer
?   ??? ?? tts_engine.py            # Text-to-speech engine
?   ??? ?? nlp_handler.py           # NLP command processor
?   ??? ?? requirements.txt         # Python dependencies
?   ??? ?? Dockerfile               # Backend container
?   ??? ?? .env                     # Environment config
?   ??? ?? .env.example             # Example config
?
??? ?? frontend/                    # React Frontend
?   ??? ?? package.json             # Node dependencies
?   ??? ?? vite.config.js           # Vite configuration
?   ??? ?? tailwind.config.js       # Tailwind config
?   ??? ?? postcss.config.js        # PostCSS config
?   ??? ?? nginx.conf               # Nginx proxy config
?   ??? ?? Dockerfile               # Frontend container
?   ??? ?? .env                     # Environment config
?   ??? ?? index.html               # HTML entry point
?   ?
?   ??? ?? src/
?       ??? ?? main.jsx             # React entry point
?       ??? ?? App.jsx              # Main app component
?       ??? ?? index.css            # Global styles
?       ?
?       ??? ?? pages/               # Page components
?       ?   ??? ?? CommandCenter.jsx    # Main dashboard
?       ?   ??? ?? AlertsPage.jsx       # Alert history
?       ?   ??? ?? SettingsPage.jsx     # Settings & config
?       ?
?       ??? ?? components/          # Reusable components
?       ?   ??? ?? AlertCard.jsx        # Alert display
?       ?   ??? ?? VideoFeed.jsx        # Live video feed
?       ?   ??? ?? OperatorControls.jsx # Control buttons
?       ?   ??? ?? NLPChat.jsx          # Chat interface
?       ?
?       ??? ?? hooks/               # Custom React hooks
?       ?   ??? ?? useSSE.js            # SSE connection
?       ?
?       ??? ?? api/                 # API client
?           ??? ?? api.js               # Backend API calls
?
??? ?? scripts/                     # Example scripts
?   ??? ?? requirements.txt         # Script dependencies
?   ??? ?? detector_example.py      # Perception node simulator
?   ??? ?? sim_reactor_stub.py      # Gazebo reactor example
?
??? ?? docs/                        # Documentation
    ??? ?? API.md                   # Complete API reference
    ??? ?? QUICKSTART.md            # Quick start guide
```

## ?? Key Components

### Backend Endpoints
- **Health**: `/health`, `/metrics`
- **Video**: `POST /frame`, `GET /video_feed`
- **Alerts**: `POST /alert`, `GET /alerts`, `POST /alerts/{id}/ack`
- **Real-time**: `GET /stream` (SSE)
- **NLP**: `POST /nlp`
- **Whitelist**: `POST /whitelist/add`, `GET /whitelist`, `POST /whitelist/refresh`

### Frontend Pages
- **Command Center** (`/`) - Live feed, alerts, controls, NLP chat
- **Alerts** (`/alerts`) - Full history with filtering
- **Settings** (`/settings`) - Whitelist & configuration

### Database Tables
- **alerts** - Detection alerts with snapshots
- **whitelist** - Known people with face images

### Storage Structure
```
storage/
??? snapshots/      # Alert snapshot images
??? tts/           # Generated TTS audio files
??? whitelist/     # Whitelist face images
??? doggobot.db   # SQLite database
```

## ?? Quick Start

**Option 1: Docker (One Command)**
```bash
./start.sh
```

**Option 2: Docker Compose**
```bash
docker-compose up -d
open http://localhost:3000
```

**Option 3: Manual**
```bash
# Terminal 1: Backend
cd backend && python main.py

# Terminal 2: Frontend
cd frontend && npm run dev

# Terminal 3: Detector
cd scripts && python detector_example.py
```

## ?? Statistics

- **Total Files**: 30+ source files
- **Lines of Code**: ~4,000+ lines
- **API Endpoints**: 14 endpoints
- **React Components**: 7+ components
- **Database Tables**: 2 tables
- **Docker Containers**: 2 services

## ?? Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| Dashboard | http://localhost:3000 | Main UI |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Video Feed | http://localhost:8000/video_feed | MJPEG stream |
| SSE Stream | http://localhost:8000/stream | Real-time events |

## ?? Documentation

1. **README.md** - Complete project documentation
2. **docs/API.md** - Full API reference with examples
3. **docs/QUICKSTART.md** - 5-minute getting started guide
4. **PROJECT_SUMMARY.md** - Implementation summary
5. **STRUCTURE.md** - This file

## ?? Technology Stack

**Backend**
- FastAPI (Python 3.10+)
- SQLite
- pyttsx3 (TTS)
- Server-Sent Events

**Frontend**
- React 18
- Vite
- TailwindCSS
- React Router

**DevOps**
- Docker & Docker Compose
- Nginx

## ? Completion Status

All 14 tasks completed:
- ? Project structure
- ? Backend with all endpoints
- ? Database layer
- ? TTS integration
- ? API authentication
- ? React frontend setup
- ? Command Center page
- ? Alerts page
- ? Settings page
- ? SSE client
- ? Detector example script
- ? Sim reactor script
- ? Docker setup
- ? Complete documentation

---

**Status**: Production Ready ??

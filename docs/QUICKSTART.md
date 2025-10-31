# ?? DoggoBot Quick Start Guide

Get up and running with DoggoBot in 5 minutes!

## Option 1: Docker (Easiest)

### Prerequisites
- Docker & Docker Compose installed

### Steps

1. **Clone and Navigate:**
   ```bash
   cd workspace
   ```

2. **Start Services:**
   ```bash
   docker-compose up -d
   ```

3. **Verify Services:**
   ```bash
   # Check containers are running
   docker-compose ps
   
   # View logs
   docker-compose logs -f
   ```

4. **Access Dashboard:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

5. **Test with Detector:**
   ```bash
   # Install script dependencies
   cd scripts
   pip install -r requirements.txt
   
   # Run detector example
   python detector_example.py
   ```

6. **Watch Alerts:**
   - Go to http://localhost:3000
   - You should see live feed and incoming alerts
   - Try NLP commands like "status" or "stop"

## Option 2: Manual Development Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- pip & npm

### Backend Setup

1. **Navigate and Install:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure:**
   ```bash
   # .env is already configured with defaults
   cat .env
   ```

3. **Start Backend:**
   ```bash
   python main.py
   ```
   
   Backend running at http://localhost:8000

### Frontend Setup

1. **Navigate and Install:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start Frontend:**
   ```bash
   npm run dev
   ```
   
   Frontend running at http://localhost:3000

### Test the Stack

1. **Start Detector Publisher:**
   ```bash
   cd scripts
   pip install -r requirements.txt
   python detector_example.py
   ```

2. **Start Simulation Reactor (Optional):**
   ```bash
   # In another terminal
   cd scripts
   python sim_reactor_stub.py
   ```

3. **Open Dashboard:**
   - Visit http://localhost:3000
   - Watch real-time alerts appear
   - Try operator controls
   - Test NLP chat with commands

## First Steps Tutorial

### 1. View Live Feed

The Command Center shows the live video feed. With `detector_example.py` running, you'll see:
- Live camera feed (or simulated frames)
- Detection boxes overlaid
- Updates ~5 times per second

### 2. Monitor Alerts

Watch the alerts sidebar:
- **Green badges**: Friendly detections (known people)
- **Red badges**: Unknown persons
- **Orange badges**: Suspicious activity

Click on an alert to expand the snapshot image.

### 3. Use Operator Controls

Test the control buttons:
- **Start Patrol**: Begin autonomous mode
- **Stop**: Halt all movement
- **Status**: Get system report
- **Investigate**: Approach detected person
- **Return Home**: Navigate back to base

### 4. Try NLP Commands

In the chat box, type natural language commands:
- `status` - Get current system status
- `stop` - Stop patrol
- `start patrol` - Begin patrol
- `investigate` - Check unknown person
- `return home` - Go back to start

The system responds with text and synthesized speech.

### 5. Acknowledge Alerts

Click the "Ack" button on any alert to mark it as reviewed. This:
- Dims the alert card
- Removes it from unacknowledged count
- Broadcasts acknowledgement to other clients

### 6. View Alert History

Navigate to **Alerts** page:
- See all historical alerts
- Filter by status or acknowledgement
- Select multiple alerts for bulk actions
- Export alerts to CSV

### 7. Manage Whitelist

Navigate to **Settings ? Whitelist**:
- Add known people with their photos
- Upload 3-5 images per person
- Click "Refresh Encodings" to update
- Future detections of these people will be marked "Friendly"

## Common Commands

### Start Everything (Docker)
```bash
docker-compose up -d
```

### Stop Everything (Docker)
```bash
docker-compose down
```

### View Logs (Docker)
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Restart Service (Docker)
```bash
docker-compose restart backend
docker-compose restart frontend
```

### Start Backend (Manual)
```bash
cd backend
source venv/bin/activate
python main.py
```

### Start Frontend (Manual)
```bash
cd frontend
npm run dev
```

### Run Detector Example
```bash
cd scripts
python detector_example.py --fps 5
```

### Run Sim Reactor
```bash
cd scripts
python sim_reactor_stub.py
```

## Verification Checklist

? **Backend Health:**
```bash
curl http://localhost:8000/health
```
Should return: `{"status": "healthy", ...}`

? **Frontend Accessible:**
```bash
curl http://localhost:3000
```
Should return HTML

? **SSE Stream:**
```bash
curl -N http://localhost:8000/stream
```
Should stream events (press Ctrl+C to stop)

? **API Docs:**
Open http://localhost:8000/docs - should see Swagger UI

? **Metrics:**
```bash
curl http://localhost:8000/metrics
```
Should return system stats

## Troubleshooting

### Port Already in Use

**Backend (8000):**
```bash
# Find process using port
lsof -i :8000
# Kill it or change PORT in .env
```

**Frontend (3000):**
```bash
# Find process using port
lsof -i :3000
# Kill it or change port in vite.config.js
```

### Backend Won't Start

**Missing dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

**TTS errors on Linux:**
```bash
sudo apt-get install espeak libespeak-dev
```

### Frontend Shows "Failed to Connect"

1. Check backend is running:
   ```bash
   curl http://localhost:8000/health
   ```

2. Check VITE_API_BASE in `frontend/.env`:
   ```bash
   VITE_API_BASE=http://localhost:8000
   ```

3. Restart frontend:
   ```bash
   npm run dev
   ```

### No Video Feed

1. Start detector:
   ```bash
   cd scripts
   python detector_example.py
   ```

2. Check frames are being posted:
   ```bash
   # Look for "?? Frames posted: X" in detector output
   ```

3. Check browser console for errors

### Docker Issues

**Containers won't start:**
```bash
docker-compose down
docker-compose up -d --build
```

**Permission denied:**
```bash
# Linux: add user to docker group
sudo usermod -aG docker $USER
# Log out and back in
```

**See container logs:**
```bash
docker-compose logs backend
docker-compose logs frontend
```

## Next Steps

Once everything is running:

1. **Customize Configuration:**
   - Change API key in `backend/.env`
   - Adjust detection thresholds in Settings UI
   - Configure frame rate in detector

2. **Add Whitelist People:**
   - Go to Settings ? Whitelist
   - Add known people with photos
   - Test friendly detection

3. **Integrate with Robot:**
   - Modify `detector_example.py` for your camera
   - Add YOLO/face detection
   - Connect `sim_reactor_stub.py` to ROS2

4. **Deploy to Production:**
   - Set up HTTPS with Nginx + Let's Encrypt
   - Change DEBUG=False
   - Use strong API keys
   - Configure CORS properly

## Quick Reference

| Component | URL | Purpose |
|-----------|-----|---------|
| Dashboard | http://localhost:3000 | Main UI |
| API | http://localhost:8000 | Backend REST API |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Video Feed | http://localhost:8000/video_feed | MJPEG stream |
| SSE Stream | http://localhost:8000/stream | Real-time events |

## Support

- ?? Full docs: `README.md`
- ?? API reference: `docs/API.md`
- ?? Issues: GitHub Issues
- ?? Questions: Check troubleshooting section

---

**Happy monitoring! ????**

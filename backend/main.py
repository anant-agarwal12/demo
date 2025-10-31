from fastapi import FastAPI, File, UploadFile, Form, Header, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import os
import json
import asyncio
import time
import base64
from datetime import datetime
from io import BytesIO
from PIL import Image

from database import Database
from tts_engine import TTSEngine
from nlp_handler import NLPHandler

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("API_KEY", "doggobot-secret-key-change-me")
STORAGE_PATH = os.getenv("STORAGE_PATH", "./storage")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Initialize
app = FastAPI(title="DoggoBot API", version="1.0.0", debug=DEBUG)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create storage directories
os.makedirs(f"{STORAGE_PATH}/snapshots", exist_ok=True)
os.makedirs(f"{STORAGE_PATH}/tts", exist_ok=True)
os.makedirs(f"{STORAGE_PATH}/whitelist", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=STORAGE_PATH), name="static")

# Initialize services
db = Database(f"{STORAGE_PATH}/doggobot.db")
tts_engine = TTSEngine(f"{STORAGE_PATH}/tts")
nlp_handler = NLPHandler(db)

# Global state for live feed
latest_frame = None
latest_bounding_boxes = []
frame_lock = asyncio.Lock()

# SSE clients
sse_clients = []

# Helper functions
def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key for protected endpoints"""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

async def broadcast_sse_event(event_type: str, data: dict):
    """Broadcast event to all SSE clients"""
    event_data = json.dumps({"type": event_type, **data})
    disconnected = []
    
    for queue in sse_clients:
        try:
            await queue.put(event_data)
        except:
            disconnected.append(queue)
    
    # Remove disconnected clients
    for queue in disconnected:
        sse_clients.remove(queue)

# Endpoints

@app.get("/")
async def root():
    return {"message": "DoggoBot API v1.0.0", "status": "online"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected",
        "storage": "available"
    }

@app.get("/metrics")
async def metrics():
    """System metrics"""
    alerts = db.get_alerts(limit=1000)
    total_alerts = len(alerts)
    unacknowledged = sum(1 for a in alerts if not a['acknowledged'])
    
    return {
        "total_alerts": total_alerts,
        "unacknowledged_alerts": unacknowledged,
        "sse_clients": len(sse_clients),
        "storage_path": STORAGE_PATH,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/frame")
async def upload_frame(
    frame: UploadFile = File(...),
    bounding_boxes: Optional[str] = Form(None),
    face_count: Optional[int] = Form(None),
    x_api_key: str = Header(None)
):
    """Upload a frame for live video feed with optional bounding boxes"""
    verify_api_key(x_api_key)
    
    global latest_frame, latest_bounding_boxes
    
    try:
        # Read frame data
        frame_data = await frame.read()
        
        # Parse bounding boxes if provided
        boxes = []
        if bounding_boxes:
            try:
                boxes = json.loads(bounding_boxes)
            except json.JSONDecodeError:
                boxes = []
        
        # Store latest frame and bounding boxes
        async with frame_lock:
            latest_frame = frame_data
            latest_bounding_boxes = boxes
        
        return {
            "status": "ok",
            "size": len(frame_data),
            "face_count": len(boxes) if boxes else 0,
            "bounding_boxes": boxes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/alert")
async def create_alert(
    payload: str = Form(...),
    snapshot: Optional[UploadFile] = File(None),
    x_api_key: str = Header(None)
):
    """Create a new detection alert"""
    verify_api_key(x_api_key)
    
    try:
        # Parse payload
        alert_data = json.loads(payload)
        
        # Generate alert ID
        alert_id = f"alert_{int(datetime.now().timestamp() * 1000)}"
        alert_data['id'] = alert_id
        
        # Save snapshot if provided
        if snapshot:
            snapshot_filename = f"{alert_id}.jpg"
            snapshot_path = os.path.join(STORAGE_PATH, "snapshots", snapshot_filename)
            
            with open(snapshot_path, "wb") as f:
                f.write(await snapshot.read())
            
            alert_data['snapshot_path'] = f"static/snapshots/{snapshot_filename}"
        
        # Insert into database
        db.insert_alert(alert_data)
        
        # Broadcast via SSE
        await broadcast_sse_event("alert", {"alert": alert_data})
        
        return JSONResponse({"id": alert_id}, status_code=200)
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/video_feed")
async def video_feed():
    """MJPEG video feed endpoint"""
    async def generate():
        while True:
            async with frame_lock:
                if latest_frame:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + latest_frame + b'\r\n')
            await asyncio.sleep(0.033)  # ~30 FPS
    
    return StreamingResponse(
        generate(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/frame_data")
async def get_frame_data():
    """Get latest frame and bounding box data as JSON"""
    async with frame_lock:
        if latest_frame:
            frame_b64 = base64.b64encode(latest_frame).decode('utf-8')
            return {
                "frame": f"data:image/jpeg;base64,{frame_b64}",
                "bounding_boxes": latest_bounding_boxes,
                "face_count": len(latest_bounding_boxes)
            }
        return {"frame": None, "bounding_boxes": [], "face_count": 0}

@app.get("/stream")
async def sse_stream(request: Request):
    """Server-Sent Events stream for real-time updates"""
    async def event_generator():
        queue = asyncio.Queue()
        sse_clients.append(queue)
        
        try:
            # Send initial connection message
            yield f"data: {json.dumps({'type': 'connected', 'timestamp': time.time()})}\n\n"
            
            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    break
                
                try:
                    # Wait for event with timeout
                    event_data = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"data: {event_data}\n\n"
                except asyncio.TimeoutError:
                    # Send heartbeat
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': time.time()})}\n\n"
        
        finally:
            sse_clients.remove(queue)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.post("/nlp")
async def process_nlp(request: Request):
    """Process natural language command"""
    try:
        data = await request.json()
        text = data.get("text", "")
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Process command
        response = nlp_handler.process_command(text)
        
        # Generate TTS
        tts_path = tts_engine.synthesize(response['text'])
        if tts_path:
            response['tts'] = tts_path
        
        response['ok'] = True
        
        # Broadcast via SSE
        await broadcast_sse_event("nlp", response)
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/alerts")
async def get_alerts(
    limit: int = 20,
    offset: int = 0,
    status: Optional[str] = None,
    acknowledged: Optional[bool] = None
):
    """Get alerts with filtering"""
    try:
        alerts = db.get_alerts(limit=limit, offset=offset, status=status, acknowledged=acknowledged)
        return {"alerts": alerts, "count": len(alerts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/alerts/{alert_id}")
async def get_alert(alert_id: str):
    """Get specific alert by ID"""
    alert = db.get_alert_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@app.post("/alerts/{alert_id}/ack")
async def acknowledge_alert(alert_id: str):
    """Acknowledge an alert"""
    success = db.acknowledge_alert(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Broadcast ack event
    await broadcast_sse_event("ack", {"alert_id": alert_id})
    
    return {"status": "acknowledged", "alert_id": alert_id}

@app.post("/ack/{alert_id}")
async def acknowledge_alert_alt(alert_id: str):
    """Alternative acknowledge endpoint"""
    return await acknowledge_alert(alert_id)

@app.post("/whitelist/add")
async def add_to_whitelist(
    name: str = Form(...),
    images: List[UploadFile] = File(...)
):
    """Add person to whitelist"""
    try:
        saved_images = []
        
        # Save images
        for idx, image in enumerate(images):
            image_filename = f"{name}_{idx}_{int(time.time())}.jpg"
            image_path = os.path.join(STORAGE_PATH, "whitelist", image_filename)
            
            with open(image_path, "wb") as f:
                f.write(await image.read())
            
            saved_images.append(f"static/whitelist/{image_filename}")
        
        # Add to database
        person_id = db.add_whitelist_person(name, saved_images)
        
        return {
            "status": "success",
            "person_id": person_id,
            "name": name,
            "images": saved_images
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/whitelist/refresh")
async def refresh_whitelist():
    """Refresh whitelist encodings (placeholder)"""
    try:
        whitelist = db.get_whitelist()
        
        # TODO: Implement face encoding refresh
        # This would call whitelist_encode.py or similar
        
        return {
            "status": "success",
            "message": f"Refreshed {len(whitelist)} whitelist entries",
            "count": len(whitelist)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/whitelist")
async def get_whitelist():
    """Get all whitelist entries"""
    try:
        whitelist = db.get_whitelist()
        return {"whitelist": whitelist, "count": len(whitelist)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=DEBUG
    )

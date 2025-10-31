# DoggoBot API Reference

Complete API documentation for the DoggoBot backend.

## Base URL

```
http://localhost:8000
```

## Authentication

Most endpoints are public. Protected endpoints require an API key:

```http
X-API-KEY: your-api-key-here
```

Protected endpoints:
- `POST /frame`
- `POST /alert`

## Endpoints

### Health & Status

#### GET /
Get API version and status.

**Response:**
```json
{
  "message": "DoggoBot API v1.0.0",
  "status": "online"
}
```

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-31T12:00:00",
  "database": "connected",
  "storage": "available"
}
```

#### GET /metrics
System metrics and statistics.

**Response:**
```json
{
  "total_alerts": 42,
  "unacknowledged_alerts": 5,
  "sse_clients": 2,
  "storage_path": "./storage",
  "timestamp": "2025-10-31T12:00:00"
}
```

### Video Feed

#### POST /frame
Upload a video frame for the live feed.

**Authentication:** Required

**Request:**
- Content-Type: `multipart/form-data`
- Body: `frame` (file)

**Response:**
```json
{
  "status": "ok",
  "size": 12345
}
```

#### GET /video_feed
MJPEG video stream endpoint.

**Response:**
- Content-Type: `multipart/x-mixed-replace; boundary=frame`
- Streams JPEG frames continuously

**Usage:**
```html
<img src="http://localhost:8000/video_feed" />
```

### Alerts

#### POST /alert
Create a new detection alert.

**Authentication:** Required

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `payload` (form field): JSON string
  - `snapshot` (file, optional): JPEG image

**Payload Schema:**
```json
{
  "label": "person",
  "angle": 0.12,
  "distance": 2.1,
  "confidence": 0.89,
  "status": "friendly",
  "identity": "Alice",
  "timestamp": 1698765432.123
}
```

**Response:**
```json
{
  "id": "alert_1698765432123"
}
```

#### GET /alerts
List alerts with optional filtering.

**Query Parameters:**
- `limit` (int): Number of alerts to return (default: 20)
- `offset` (int): Pagination offset (default: 0)
- `status` (string): Filter by status (`friendly`, `unknown`, `suspicious`)
- `acknowledged` (boolean): Filter by acknowledgement state

**Response:**
```json
{
  "alerts": [
    {
      "id": "alert_123",
      "timestamp": 1698765432.123,
      "status": "unknown",
      "identity": "Unknown Person",
      "confidence": 0.89,
      "angle": 0.12,
      "distance": 2.1,
      "snapshot_path": "static/snapshots/alert_123.jpg",
      "acknowledged": false,
      "meta": {}
    }
  ],
  "count": 1
}
```

#### GET /alerts/{alert_id}
Get a specific alert by ID.

**Response:**
```json
{
  "id": "alert_123",
  "timestamp": 1698765432.123,
  "status": "unknown",
  "identity": "Unknown Person",
  "confidence": 0.89,
  "angle": 0.12,
  "distance": 2.1,
  "snapshot_path": "static/snapshots/alert_123.jpg",
  "acknowledged": false,
  "meta": {}
}
```

#### POST /alerts/{alert_id}/ack
Acknowledge an alert.

**Alternative:** `POST /ack/{alert_id}`

**Response:**
```json
{
  "status": "acknowledged",
  "alert_id": "alert_123"
}
```

### Real-time Events

#### GET /stream
Server-Sent Events (SSE) stream for real-time updates.

**Response:**
- Content-Type: `text/event-stream`
- Streams JSON events

**Event Types:**

**Connected Event:**
```json
{
  "type": "connected",
  "timestamp": 1698765432.123
}
```

**Heartbeat Event:**
```json
{
  "type": "heartbeat",
  "timestamp": 1698765432.123
}
```

**Alert Event:**
```json
{
  "type": "alert",
  "alert": {
    "id": "alert_123",
    "status": "unknown",
    "identity": "Unknown Person",
    ...
  }
}
```

**NLP Event:**
```json
{
  "type": "nlp",
  "intent": "status",
  "text": "System status: 3 alerts. 1 unacknowledged.",
  "tts": "static/tts/tts_123.wav",
  "action": null
}
```

**Acknowledgement Event:**
```json
{
  "type": "ack",
  "alert_id": "alert_123"
}
```

### Natural Language Processing

#### POST /nlp
Process a natural language command.

**Request:**
```json
{
  "text": "status"
}
```

**Response:**
```json
{
  "ok": true,
  "intent": "status",
  "text": "System status: 3 alerts. 1 unacknowledged.",
  "tts": "static/tts/tts_123.wav",
  "action": null,
  "data": {
    "total": 3,
    "unacknowledged": 1,
    "friendly": 1,
    "unknown": 1,
    "suspicious": 1
  }
}
```

**Supported Intents:**
- `status` - Get system status
- `stop` - Stop patrol
- `start` - Start patrol
- `follow` - Enter follow mode
- `return_home` - Return to home position
- `greet` - Greet person
- `investigate` - Investigate area
- `alarm` - Sound alarm

### Whitelist Management

#### GET /whitelist
Get all whitelist entries.

**Response:**
```json
{
  "whitelist": [
    {
      "id": 1,
      "name": "Alice",
      "sample_images": [
        "static/whitelist/alice_0_123.jpg",
        "static/whitelist/alice_1_123.jpg"
      ],
      "enc_count": 2,
      "created_at": 1698765432.123
    }
  ],
  "count": 1
}
```

#### POST /whitelist/add
Add a person to the whitelist.

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `name` (form field): Person's name
  - `images` (files): Multiple JPEG images

**Response:**
```json
{
  "status": "success",
  "person_id": 1,
  "name": "Alice",
  "images": [
    "static/whitelist/alice_0_123.jpg",
    "static/whitelist/alice_1_123.jpg"
  ]
}
```

#### POST /whitelist/refresh
Refresh face encodings for all whitelist entries.

**Response:**
```json
{
  "status": "success",
  "message": "Refreshed 5 whitelist entries",
  "count": 5
}
```

## Error Responses

All endpoints may return error responses:

**401 Unauthorized:**
```json
{
  "detail": "Invalid API key"
}
```

**404 Not Found:**
```json
{
  "detail": "Alert not found"
}
```

**400 Bad Request:**
```json
{
  "detail": "Invalid JSON payload"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Database connection error"
}
```

## Rate Limiting

- `/frame`: Recommended max 10 FPS per client
- `/alert`: Recommended max 5 per second per client

No hard rate limiting implemented in development mode.

## CORS

CORS is enabled for all origins in development mode. For production, configure allowed origins in `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    ...
)
```

## Static Files

All uploaded files are served from `/static`:

- Snapshots: `/static/snapshots/{filename}.jpg`
- TTS Audio: `/static/tts/{filename}.wav`
- Whitelist Images: `/static/whitelist/{filename}.jpg`

**Example:**
```
http://localhost:8000/static/snapshots/alert_123.jpg
```

## WebSocket Alternative

While not currently implemented, the SSE stream could be replaced with WebSocket for bidirectional communication:

```python
# Placeholder for future implementation
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Handle messages
```

## Examples

### Python Client

```python
import requests

API_URL = "http://localhost:8000"
API_KEY = "doggobot-secret-key-change-me"

# Post a frame
with open("frame.jpg", "rb") as f:
    response = requests.post(
        f"{API_URL}/frame",
        files={"frame": f},
        headers={"X-API-KEY": API_KEY}
    )
    print(response.json())

# Create an alert
alert_data = {
    "label": "person",
    "status": "unknown",
    "confidence": 0.89,
    "distance": 2.5,
    "angle": 0.3,
    "timestamp": time.time()
}

with open("snapshot.jpg", "rb") as f:
    response = requests.post(
        f"{API_URL}/alert",
        data={"payload": json.dumps(alert_data)},
        files={"snapshot": f},
        headers={"X-API-KEY": API_KEY}
    )
    print(response.json())

# Get alerts
response = requests.get(f"{API_URL}/alerts?status=unknown&limit=10")
print(response.json())

# Send NLP command
response = requests.post(
    f"{API_URL}/nlp",
    json={"text": "status"}
)
print(response.json())
```

### JavaScript Client

```javascript
// Post NLP command
async function sendCommand(text) {
  const response = await fetch('http://localhost:8000/nlp', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  });
  return response.json();
}

// Connect to SSE stream
const eventSource = new EventSource('http://localhost:8000/stream');

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Event:', data);
  
  if (data.type === 'alert') {
    console.log('New alert:', data.alert);
  }
};

eventSource.onerror = (error) => {
  console.error('SSE error:', error);
};

// Get alerts
async function getAlerts() {
  const response = await fetch('http://localhost:8000/alerts?limit=20');
  return response.json();
}

// Acknowledge alert
async function acknowledgeAlert(alertId) {
  const response = await fetch(`http://localhost:8000/alerts/${alertId}/ack`, {
    method: 'POST'
  });
  return response.json();
}
```

## Interactive Documentation

For interactive API documentation with try-it-out functionality, visit:

```
http://localhost:8000/docs
```

This provides a Swagger UI interface for testing all endpoints.

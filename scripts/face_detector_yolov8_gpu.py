#!/usr/bin/env python3
"""
YOLOv8 GPU-Accelerated Face Detector for DoggoBot
- Uses YOLOv8 for fast GPU face detection
- Compares against whitelist from backend
- Posts alerts with bounding boxes to dashboard

REQUIRES: ultralytics, torch with CUDA

Usage:
    python face_detector_yolov8_gpu.py --camera-index 0 --fps 30
"""

import cv2
import requests
import json
import time
import argparse
import numpy as np
from datetime import datetime

# Check for required libraries
try:
    from ultralytics import YOLO
    import torch
    YOLO_AVAILABLE = True
    print(f"✅ YOLOv8 loaded")
    print(f"   PyTorch version: {torch.__version__}")
    print(f"   CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
except ImportError as e:
    YOLO_AVAILABLE = False
    print(f"❌ YOLOv8 not available: {e}")
    print("   Install with: pip install ultralytics torch torchvision")
    exit(1)

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
    print("✅ face_recognition loaded (for matching)")
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("⚠️  face_recognition not available - whitelist matching disabled")


class YOLOFaceDetector:
    def __init__(self, api_url="http://localhost:8000", api_key="doggobot-secret-key-change-me", camera_index=0):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.headers = {"X-API-KEY": api_key}
        
        # Initialize camera
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            print(f"❌ Could not open camera at index {camera_index}")
            self.cap = None
        else:
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            print(f"✅ Camera initialized at index {camera_index}")
            print(f"   Resolution: {int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
        
        # Initialize YOLOv8
        print("\n🔄 Loading YOLOv8 model...")
        self.model = YOLO('yolov8n.pt')  # Use nano model (fast)
        
        # Use GPU if available
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model.to(self.device)
        print(f"✅ YOLOv8 model loaded on: {self.device}")
        
        # Whitelist data
        self.known_face_encodings = []
        self.known_face_names = []
        
        # Alert tracking
        self.last_alert_time = {}
        self.alert_cooldown = 10
        
        # Detection cache
        self.last_detections = []
    
    def load_whitelist(self):
        """Download whitelist from backend and compute encodings"""
        print("\n📥 Loading whitelist from backend...")
        
        if not FACE_RECOGNITION_AVAILABLE:
            print("⚠️  face_recognition not available - all faces will be 'unknown'")
            return True
        
        try:
            response = requests.get(f"{self.api_url}/whitelist", timeout=5)
            if response.status_code != 200:
                print(f"⚠️  Failed to load whitelist: {response.status_code}")
                return False
            
            data = response.json()
            whitelist_entries = data.get('whitelist', [])
            
            if not whitelist_entries:
                print("⚠️  No whitelist entries found")
                print("   Add people at: http://localhost:3000/settings")
                return True
            
            print(f"   Found {len(whitelist_entries)} whitelist entries")
            
            self.known_face_encodings = []
            self.known_face_names = []
            
            for entry in whitelist_entries:
                name = entry['name']
                images = entry.get('sample_images', [])
                
                if not images:
                    print(f"   ⚠️  No images for {name}")
                    continue
                
                encodings_for_person = []
                for image_path in images:
                    full_url = f"{self.api_url}/{image_path}"
                    try:
                        img_response = requests.get(full_url, timeout=5)
                        if img_response.status_code == 200:
                            img_array = np.frombuffer(img_response.content, np.uint8)
                            image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                            
                            face_encodings = face_recognition.face_encodings(rgb_image)
                            if face_encodings:
                                encodings_for_person.append(face_encodings[0])
                    except Exception as e:
                        print(f"   ⚠️  Error loading {image_path}: {e}")
                
                if encodings_for_person:
                    self.known_face_encodings.extend(encodings_for_person)
                    self.known_face_names.extend([name] * len(encodings_for_person))
                    print(f"   ✅ Loaded {len(encodings_for_person)} encodings for {name}")
            
            print(f"\n✅ Whitelist loaded: {len(self.known_face_names)} total encodings\n")
            return True
            
        except Exception as e:
            print(f"❌ Error loading whitelist: {e}")
            return False
    
    def match_face(self, face_crop):
        """Match a face crop against whitelist"""
        if not FACE_RECOGNITION_AVAILABLE or not self.known_face_encodings:
            return None, 0.0
        
        try:
            rgb_crop = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
            face_encodings = face_recognition.face_encodings(rgb_crop)
            
            if not face_encodings:
                return None, 0.0
            
            face_encoding = face_encodings[0]
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.6)
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
                    confidence = 1.0 - face_distances[best_match_index]
                    return name, confidence
            
            return None, 0.0
        except:
            return None, 0.0
    
    def detect_faces_yolo(self, frame):
        """Detect faces using YOLOv8"""
        # Run YOLOv8 detection
        results = self.model(frame, classes=[0], verbose=False)  # class 0 = person
        
        detections = []
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get bounding box
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                
                # Only process high-confidence detections
                if conf < 0.5:
                    continue
                
                # Extract face region for matching
                h, w = frame.shape[:2]
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(w, x2)
                y2 = min(h, y2)
                
                face_crop = frame[y1:y2, x1:x2]
                
                # Match against whitelist
                name, match_conf = self.match_face(face_crop)
                
                detections.append({
                    'bbox': (x1, y1, x2, y2),
                    'name': name,
                    'confidence': match_conf,
                    'detection_conf': conf
                })
        
        return detections
    
    def post_frame(self, frame):
        """Post frame to backend"""
        try:
            _, buffer = cv2.imencode('.jpg', frame)
            files = {'frame': ('frame.jpg', buffer.tobytes(), 'image/jpeg')}
            response = requests.post(
                f"{self.api_url}/frame",
                files=files,
                headers=self.headers,
                timeout=1
            )
            return response.status_code == 200
        except:
            return False
    
    def post_alert(self, name, status, frame, confidence=0.0):
        """Post alert to backend"""
        try:
            alert_data = {
                "label": "person",
                "status": status,
                "identity": name if name else "Unknown Person",
                "confidence": confidence,
                "timestamp": time.time(),
                "angle": 0.0,
                "distance": None
            }
            
            _, buffer = cv2.imencode('.jpg', frame)
            files = {'snapshot': ('snapshot.jpg', buffer.tobytes(), 'image/jpeg')}
            data = {'payload': json.dumps(alert_data)}
            
            response = requests.post(
                f"{self.api_url}/alert",
                data=data,
                files=files,
                headers=self.headers,
                timeout=3
            )
            
            if response.status_code == 200:
                print(f"🚨 Alert: {status.upper()} - {alert_data['identity']} (conf: {confidence:.2f})")
                return True
            return False
        except Exception as e:
            print(f"❌ Error posting alert: {e}")
            return False
    
    def should_send_alert(self, identifier):
        """Check if enough time has passed since last alert"""
        current_time = time.time()
        if identifier not in self.last_alert_time:
            self.last_alert_time[identifier] = current_time
            return True
        
        if current_time - self.last_alert_time[identifier] >= self.alert_cooldown:
            self.last_alert_time[identifier] = current_time
            return True
        
        return False
    
    def run(self, fps=30):
        """Main detection loop"""
        if not self.cap:
            print("❌ No camera available")
            return
        
        # Load whitelist
        self.load_whitelist()
        
        print(f"\n🤖 Starting YOLOv8 GPU Face Detector")
        print(f"   API URL: {self.api_url}")
        print(f"   Streaming FPS: {fps}")
        print(f"   Device: {self.device.upper()}")
        print(f"   Whitelist: {len(self.known_face_names)} face encodings")
        print(f"   🎨 Bounding boxes will appear on backend live feed!")
        print(f"\nPress 'q' to quit, 'r' to reload whitelist\n")
        
        frame_interval = 1.0 / fps
        frame_count = 0
        fps_start_time = time.time()
        fps_counter = 0
        current_fps = 0
        
        try:
            while True:
                start_time = time.time()
                
                ret, frame = self.cap.read()
                if not ret:
                    continue
                
                frame_count += 1
                fps_counter += 1
                
                # Calculate FPS every second
                if time.time() - fps_start_time >= 1.0:
                    current_fps = fps_counter
                    fps_counter = 0
                    fps_start_time = time.time()
                
                # Detect faces using YOLOv8
                detections = self.detect_faces_yolo(frame)
                self.last_detections = detections
                
                # Send alerts for new detections
                for detection in detections:
                    name = detection['name']
                    confidence = detection['confidence']
                    status = "friendly" if name else "unknown"
                    identifier = name if name else "unknown"
                    
                    if self.should_send_alert(identifier):
                        self.post_alert(name, status, frame, confidence)
                
                # Draw bounding boxes on frame
                for detection in detections:
                    x1, y1, x2, y2 = detection['bbox']
                    name = detection['name']
                    confidence = detection['confidence']
                    det_conf = detection['detection_conf']
                    
                    # Color coding
                    if name:
                        color = (0, 255, 0)  # Green for known
                        label = f"{name} ({confidence:.2f})"
                    else:
                        color = (0, 0, 255)  # Red for unknown
                        label = "Unknown"
                    
                    # Draw thick box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                    
                    # Draw label with background
                    label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                    cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                                (x1 + label_size[0], y1), color, -1)
                    cv2.putText(frame, label, (x1, y1 - 5),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Status overlay
                whitelist_count = len(set(self.known_face_names))
                detected_count = len(detections)
                
                status_lines = [
                    f"FPS: {current_fps} | Detected: {detected_count} | Whitelist: {whitelist_count}",
                    f"Device: {self.device.upper()} | Frame: {frame_count}"
                ]
                
                y_offset = 25
                for line in status_lines:
                    text_size = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                    cv2.rectangle(frame, (5, y_offset - 20), (text_size[0] + 15, y_offset + 5), (0, 0, 0), -1)
                    cv2.putText(frame, line, (10, y_offset), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    y_offset += 30
                
                # Post frame to backend
                self.post_frame(frame)
                
                # Show local preview
                cv2.imshow('YOLOv8 GPU Detector (q=quit, r=reload)', frame)
                
                # Handle keys
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    print("\n🔄 Reloading whitelist...")
                    self.load_whitelist()
                
                # Maintain FPS
                elapsed = time.time() - start_time
                sleep_time = max(0, frame_interval - elapsed)
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Stopped by user")
        finally:
            if self.cap:
                self.cap.release()
            cv2.destroyAllWindows()
            print(f"\n✅ Total frames processed: {frame_count}")
            print(f"   Average FPS: {frame_count / (time.time() - fps_start_time + 0.001):.1f}")


def main():
    parser = argparse.ArgumentParser(description="YOLOv8 GPU Face Detector for DoggoBot")
    parser.add_argument('--api-url', default='http://localhost:8000',
                       help='Backend API URL')
    parser.add_argument('--api-key', default='doggobot-secret-key-change-me',
                       help='API key')
    parser.add_argument('--camera-index', type=int, default=0,
                       help='Camera index (default: 0)')
    parser.add_argument('--fps', type=int, default=30,
                       help='Target FPS (default: 30)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 YOLOv8 GPU Face Detector for DoggoBot")
    print("=" * 60)
    
    detector = YOLOFaceDetector(
        api_url=args.api_url,
        api_key=args.api_key,
        camera_index=args.camera_index
    )
    detector.run(fps=args.fps)


if __name__ == "__main__":
    main()

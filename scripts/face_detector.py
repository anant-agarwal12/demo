#!/usr/bin/env python3
"""
Simple Face Detection with Bounding Boxes for DoggoBot

Features:
- Webcam capture
- HOG (CPU) or CNN (GPU) detection modes
- Fetches whitelist from backend
- Sends frames with bounding boxes to backend
- Real-time face recognition

Usage:
    python face_detector.py
    python face_detector.py --camera 0
    python face_detector.py --mode cnn  # GPU mode
"""

import cv2
import face_recognition
import requests
import json
import time
import argparse
import numpy as np
from typing import List, Dict, Tuple

# Configuration
API_URL = "http://localhost:8000"
API_KEY = "doggobot-secret-key-change-me"

class SimpleFaceDetector:
    def __init__(self, camera_index=0, mode="hog", api_url=API_URL, api_key=API_KEY):
        self.camera_index = camera_index
        self.mode = mode  # "hog" (CPU) or "cnn" (GPU)
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.headers = {"X-API-KEY": api_key}
        
        # Initialize camera
        print(f"\n🎥 Opening camera {camera_index}...")
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"❌ Failed to open camera {camera_index}")
        print("✅ Camera opened")
        
        # Whitelist data
        self.known_faces = []  # List of {name, encoding}
        
        # Stats
        self.frame_count = 0
        self.fps = 0
        self.last_fps_time = time.time()
        
        print(f"🧠 Detection mode: {mode.upper()} {'(GPU)' if mode == 'cnn' else '(CPU)'}")
        print(f"🌐 API: {self.api_url}\n")
        
        # Load whitelist
        self.load_whitelist()
    
    def load_whitelist(self):
        """Fetch whitelist from backend"""
        try:
            print("📥 Loading whitelist from backend...")
            response = requests.get(f"{self.api_url}/whitelist", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                whitelist = data.get('whitelist', [])
                
                self.known_faces = []
                for person in whitelist:
                    name = person.get('name')
                    images = person.get('images', [])
                    
                    # Load and encode faces
                    for img_path in images:
                        try:
                            # Get full image URL
                            img_url = f"{self.api_url}/{img_path}"
                            img_response = requests.get(img_url, timeout=5)
                            
                            if img_response.status_code == 200:
                                # Convert to numpy array
                                img_array = np.frombuffer(img_response.content, np.uint8)
                                image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                                
                                # Get face encoding
                                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                                encodings = face_recognition.face_encodings(rgb_image)
                                
                                if encodings:
                                    self.known_faces.append({
                                        'name': name,
                                        'encoding': encodings[0]
                                    })
                                    print(f"  ✓ Loaded {name}")
                        except Exception as e:
                            print(f"  ⚠ Failed to load image for {name}: {e}")
                
                print(f"✅ Loaded {len(self.known_faces)} face(s) from whitelist\n")
            else:
                print("⚠️  No whitelist found on backend\n")
        
        except Exception as e:
            print(f"⚠️  Failed to load whitelist: {e}\n")
    
    def detect_faces(self, frame):
        """Detect faces and identify them"""
        # Resize for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        face_locations = face_recognition.face_locations(rgb_frame, model=self.mode)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        # Scale locations back to original size
        face_locations = [(top*2, right*2, bottom*2, left*2) 
                         for (top, right, bottom, left) in face_locations]
        
        # Identify faces
        detections = []
        for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
            name = "Unknown"
            status = "unknown"
            
            # Compare with known faces
            if self.known_faces:
                face_distances = face_recognition.face_distance(
                    [kf['encoding'] for kf in self.known_faces],
                    encoding
                )
                
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    if face_distances[best_match_index] < 0.6:
                        name = self.known_faces[best_match_index]['name']
                        status = "friendly"
            
            detections.append({
                'bbox': {
                    'x': left,
                    'y': top,
                    'width': right - left,
                    'height': bottom - top
                },
                'name': name,
                'status': status
            })
        
        return face_locations, detections
    
    def draw_faces(self, frame, face_locations, detections):
        """Draw bounding boxes on frame"""
        for (top, right, bottom, left), detection in zip(face_locations, detections):
            name = detection['name']
            status = detection['status']
            
            # Color based on status
            color = (0, 255, 0) if status == "friendly" else (0, 165, 255)
            
            # Draw box
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            # Draw label
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            cv2.putText(frame, name, (left + 6, bottom - 18), 
                       cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(frame, status.upper(), (left + 6, bottom - 6),
                       cv2.FONT_HERSHEY_DUPLEX, 0.4, (255, 255, 255), 1)
        
        return frame
    
    def post_frame(self, frame, detections):
        """Send frame and detections to backend"""
        try:
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            
            files = {'frame': ('frame.jpg', buffer.tobytes(), 'image/jpeg')}
            data = {'detections': json.dumps(detections)}
            
            requests.post(
                f"{self.api_url}/frame",
                files=files,
                data=data,
                headers=self.headers,
                timeout=1.0
            )
        except:
            pass  # Silent fail
    
    def update_fps(self):
        """Calculate FPS"""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_time >= 1.0:
            self.fps = self.frame_count / (current_time - self.last_fps_time)
            self.frame_count = 0
            self.last_fps_time = current_time
    
    def run(self):
        """Main detection loop"""
        print("🚀 Starting face detection...")
        print("Press 'q' to quit, 'r' to reload whitelist, 'm' to toggle mode\n")
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("⚠️  Failed to read frame")
                    time.sleep(0.1)
                    continue
                
                # Detect faces
                face_locations, detections = self.detect_faces(frame)
                
                # Draw on frame
                display_frame = self.draw_faces(frame.copy(), face_locations, detections)
                
                # Add stats
                self.update_fps()
                cv2.putText(display_frame, f"FPS: {self.fps:.1f} | Mode: {self.mode.upper()} | Faces: {len(detections)}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Send to backend
                self.post_frame(display_frame, detections)
                
                # Show preview
                cv2.imshow("DoggoBot Face Detector (q=quit, r=reload, m=toggle mode)", display_frame)
                
                # Handle keys
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    print("\n🔄 Reloading whitelist...")
                    self.load_whitelist()
                elif key == ord('m'):
                    self.mode = "cnn" if self.mode == "hog" else "hog"
                    print(f"\n🔄 Switched to {self.mode.upper()} mode")
        
        except KeyboardInterrupt:
            print("\n\n🛑 Interrupted by user")
        
        finally:
            self.cap.release()
            cv2.destroyAllWindows()
            print("\n✅ Stopped\n")

def main():
    parser = argparse.ArgumentParser(description="Simple Face Detector for DoggoBot")
    parser.add_argument('--camera', type=int, default=0, help='Camera index (default: 0)')
    parser.add_argument('--mode', choices=['hog', 'cnn'], default='hog', 
                       help='Detection mode: hog (CPU) or cnn (GPU)')
    parser.add_argument('--api-url', default=API_URL, help='Backend API URL')
    parser.add_argument('--api-key', default=API_KEY, help='API key')
    
    args = parser.parse_args()
    
    try:
        detector = SimpleFaceDetector(
            camera_index=args.camera,
            mode=args.mode,
            api_url=args.api_url,
            api_key=args.api_key
        )
        detector.run()
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

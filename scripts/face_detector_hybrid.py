#!/usr/bin/env python3
"""
Hybrid Face Recognition for DoggoBot
- Uses local whitelist.pkl (fast, reliable)
- Posts frames and alerts to backend
- Works offline if backend is down

Usage:
    python face_detector_hybrid.py --source 0 --fps 30
"""

import cv2
import face_recognition
import pickle
import numpy as np
import argparse
import os
import time
import json
import requests
from datetime import datetime

# ---------------- CONFIG ----------------
WHITELIST_FILE = "whitelist.pkl"
MATCH_THRESHOLD = 0.6    # lower = stricter match
MODEL = "cnn"             # "hog" for CPU, "cnn" for GPU (if available)
API_URL = "http://localhost:8000"
API_KEY = "doggobot-secret-key-change-me"
# ----------------------------------------

class HybridDetector:
    def __init__(self, source, api_url, api_key, fps=30):
        self.source = source
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.headers = {"X-API-KEY": api_key}
        self.fps = fps
        
        # Alert tracking
        self.last_alert_time = {}
        self.alert_cooldown = 10  # seconds
        
        # Backend status
        self.backend_available = self.check_backend()
        
        # Load whitelist
        self.known_names, self.known_encs = self.load_whitelist()
        
        # Open camera
        self.cap = cv2.VideoCapture(
            int(source) if str(source).isdigit() else source,
            cv2.CAP_DSHOW
        )
        
        if not self.cap.isOpened():
            print(f"❌ Could not open camera/video: {source}")
            exit(1)
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        print(f"✅ Camera opened: {source}")
        print(f"   Resolution: {int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
    
    def check_backend(self):
        """Check if backend is available"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=2)
            if response.status_code == 200:
                print(f"✅ Backend connected: {self.api_url}")
                return True
        except:
            pass
        print(f"⚠️  Backend not available: {self.api_url}")
        print("   Running in offline mode (no alerts posted)")
        return False
    
    def load_whitelist(self):
        """Load whitelist from pickle file"""
        if not os.path.exists(WHITELIST_FILE):
            print(f"⚠️  '{WHITELIST_FILE}' not found.")
            print("   Create it with: whitelist_encode.py")
            print("   All faces will be marked as 'unknown'")
            return [], []
        
        with open(WHITELIST_FILE, "rb") as f:
            enc = pickle.load(f)
        
        names, encs = [], []
        for n, arr in enc.items():
            for e in arr:
                names.append(n)
                encs.append(e)
        
        print(f"✅ Loaded whitelist: {len(enc)} person(s), {len(encs)} encodings")
        return names, encs
    
    def post_frame(self, frame):
        """Post frame to backend"""
        if not self.backend_available:
            return False
        
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
    
    def post_alert(self, name, status, frame, confidence):
        """Post alert to backend"""
        if not self.backend_available:
            return False
        
        try:
            alert_data = {
                "label": "person",
                "status": status,
                "identity": name if name else "Unknown Person",
                "confidence": float(confidence),
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
            
            return response.status_code == 200
        except Exception as e:
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
    
    def run(self):
        """Main detection loop"""
        print(f"\n🤖 Starting DoggoBot Hybrid Detector")
        print(f"   Whitelist: {len(set(self.known_names))} people")
        print(f"   FPS: {self.fps}")
        print(f"   Model: {MODEL}")
        print(f"   Backend: {'Connected' if self.backend_available else 'Offline'}")
        print(f"\nPress 'q' to quit, 'r' to reload whitelist\n")
        
        frame_interval = 1.0 / self.fps
        frame_count = 0
        
        try:
            while True:
                start_time = time.time()
                
                ret, frame = self.cap.read()
                if not ret:
                    print("No frame, exiting.")
                    break
                
                frame_count += 1
                
                # Convert to RGB for face_recognition
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Detect faces
                face_locations = face_recognition.face_locations(rgb, model=MODEL)
                face_encs = face_recognition.face_encodings(rgb, known_face_locations=face_locations)
                
                # Process each detected face
                for (top, right, bottom, left), enc in zip(face_locations, face_encs):
                    name = None
                    color = (0, 0, 255)  # Red for unknown
                    status = "unknown"
                    distance = 1.0
                    
                    # Compare with known faces
                    if self.known_encs:
                        dists = face_recognition.face_distance(self.known_encs, enc)
                        best_idx = int(np.argmin(dists))
                        best_dist = dists[best_idx]
                        
                        if best_dist < MATCH_THRESHOLD:
                            # Recognized!
                            name = self.known_names[best_idx]
                            color = (0, 255, 0)  # Green
                            status = "friendly"
                            distance = best_dist
                            label = f"{name} ({best_dist:.2f})"
                            identifier = name
                        else:
                            # Unknown person
                            label = f"Unknown ({best_dist:.2f})"
                            identifier = "unknown"
                    else:
                        label = "Unknown"
                        identifier = "unknown"
                    
                    # Draw box and label
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                    cv2.rectangle(frame, (left, bottom - 25), (right, bottom), color, cv2.FILLED)
                    cv2.putText(frame, label, (left + 4, bottom - 4), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    
                    # Send alert if cooldown passed
                    if self.should_send_alert(identifier):
                        confidence = 1.0 - distance
                        if self.post_alert(name, status, frame, confidence):
                            print(f"🚨 Alert: {status.upper()} - {name if name else 'Unknown'} ({confidence:.2f})")
                
                # Add status overlay
                status_text = f"Frame: {frame_count} | Whitelist: {len(set(self.known_names))} | FPS: {self.fps}"
                cv2.putText(frame, status_text, (10, 30),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Post frame to backend (every other frame)
                if frame_count % 2 == 0:
                    self.post_frame(frame)
                
                # Show preview
                cv2.imshow("DoggoBot Face Detector (press q to quit, r to reload)", frame)
                
                # Handle keypresses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    print("\n🔄 Reloading whitelist...")
                    self.known_names, self.known_encs = self.load_whitelist()
                
                # Maintain frame rate
                elapsed = time.time() - start_time
                sleep_time = max(0, frame_interval - elapsed)
                time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            print("\n\n⏹️  Stopped by user")
        finally:
            self.cap.release()
            cv2.destroyAllWindows()
            print(f"\n✅ Total frames processed: {frame_count}")


def main():
    parser = argparse.ArgumentParser(description="DoggoBot Hybrid Face Detector")
    parser.add_argument('--source', default=0, 
                       help='Webcam index or video path (default: 0)')
    parser.add_argument('--fps', type=int, default=30,
                       help='Frame rate (default: 30)')
    parser.add_argument('--api-url', default='http://localhost:8000',
                       help='Backend API URL')
    parser.add_argument('--api-key', default='doggobot-secret-key-change-me',
                       help='API key')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎯 DoggoBot Hybrid Face Recognition")
    print("=" * 60)
    
    detector = HybridDetector(
        source=args.source,
        api_url=args.api_url,
        api_key=args.api_key,
        fps=args.fps
    )
    detector.run()


if __name__ == "__main__":
    main()

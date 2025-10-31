#!/usr/bin/env python3
"""
Real Face Recognition Detector for DoggoBot
- Uses camera feed to detect faces
- Compares against whitelist from backend
- Posts alerts with proper status (friendly/unknown/suspicious)

Usage:
    python face_detector_real.py --camera-index 2 --fps 15
"""

import cv2
import requests
import json
import time
import argparse
import numpy as np
from datetime import datetime

# Try to import face_recognition library
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("⚠️  face_recognition library not installed!")
    print("   Install with: pip install face-recognition")
    print("   Falling back to basic detection mode\n")


class FaceDetector:
    def __init__(self, api_url="http://localhost:8000", api_key="doggobot-secret-key-change-me", camera_index=2):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.headers = {"X-API-KEY": api_key}
        
        # Initialize camera
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            print(f"❌ Could not open camera at index {camera_index}")
            self.cap = None
        else:
            # Set camera properties for better quality
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            print(f"✅ Camera initialized at index {camera_index}")
            print(f"   Resolution: {int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
        
        # Whitelist data
        self.whitelist = {}
        self.known_face_encodings = []
        self.known_face_names = []
        
        # Alert tracking
        self.last_alert_time = {}
        self.alert_cooldown = 10  # seconds between alerts for same person
        
        # Load OpenCV face detector as fallback
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    def load_whitelist(self):
        """Download whitelist from backend and compute encodings"""
        print("📥 Loading whitelist from backend...")
        
        try:
            response = requests.get(f"{self.api_url}/whitelist", timeout=5)
            if response.status_code != 200:
                print(f"⚠️  Failed to load whitelist: {response.status_code}")
                return False
            
            data = response.json()
            whitelist_entries = data.get('whitelist', [])
            
            if not whitelist_entries:
                print("⚠️  No whitelist entries found. Add people via the Settings page!")
                return True
            
            print(f"   Found {len(whitelist_entries)} whitelist entries")
            
            if not FACE_RECOGNITION_AVAILABLE:
                # Just store names without encodings
                for entry in whitelist_entries:
                    self.whitelist[entry['name']] = entry
                print("   ⚠️  Running without face_recognition library - basic mode only")
                return True
            
            # Compute face encodings for whitelist
            self.known_face_encodings = []
            self.known_face_names = []
            
            for entry in whitelist_entries:
                name = entry['name']
                images = entry.get('sample_images', [])
                
                if not images:
                    print(f"   ⚠️  No images for {name}")
                    continue
                
                # Load and encode each image
                encodings_for_person = []
                for image_path in images:
                    # Download image from backend
                    full_url = f"{self.api_url}/{image_path}"
                    try:
                        img_response = requests.get(full_url, timeout=5)
                        if img_response.status_code == 200:
                            # Convert to numpy array
                            img_array = np.frombuffer(img_response.content, np.uint8)
                            image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                            
                            # Get face encoding
                            face_encodings = face_recognition.face_encodings(rgb_image)
                            if face_encodings:
                                encodings_for_person.append(face_encodings[0])
                    except Exception as e:
                        print(f"   ⚠️  Error loading {image_path}: {e}")
                
                # Add all encodings for this person
                if encodings_for_person:
                    self.known_face_encodings.extend(encodings_for_person)
                    self.known_face_names.extend([name] * len(encodings_for_person))
                    print(f"   ✅ Loaded {len(encodings_for_person)} encodings for {name}")
                else:
                    print(f"   ⚠️  No valid face encodings for {name}")
            
            print(f"\n✅ Whitelist loaded: {len(self.known_face_names)} total encodings\n")
            return True
            
        except Exception as e:
            print(f"❌ Error loading whitelist: {e}")
            return False
    
    def detect_faces_opencv(self, frame):
        """Fallback face detection using OpenCV"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        results = []
        for (x, y, w, h) in faces:
            results.append({
                'location': (y, x+w, y+h, x),  # top, right, bottom, left (face_recognition format)
                'name': None,
                'confidence': 0.0,
                'method': 'opencv'
            })
        
        return results
    
    def detect_faces_recognition(self, frame):
        """Advanced face detection and recognition"""
        # Resize frame for faster processing (optional)
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Find faces
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        results = []
        for face_location, face_encoding in zip(face_locations, face_encodings):
            # Scale back up face locations
            top, right, bottom, left = face_location
            top *= 2
            right *= 2
            bottom *= 2
            left *= 2
            
            # Compare with known faces
            name = None
            confidence = 0.0
            
            if self.known_face_encodings:
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.6)
                face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                        confidence = 1.0 - face_distances[best_match_index]
            
            results.append({
                'location': (top, right, bottom, left),
                'name': name,
                'confidence': confidence,
                'method': 'face_recognition'
            })
        
        return results
    
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
                result = response.json()
                print(f"🚨 Alert: {status.upper()} - {alert_data['identity']} (confidence: {confidence:.2f})")
                return True
            return False
        except Exception as e:
            print(f"❌ Error posting alert: {e}")
            return False
    
    def should_send_alert(self, identifier):
        """Check if enough time has passed since last alert for this person"""
        current_time = time.time()
        if identifier not in self.last_alert_time:
            self.last_alert_time[identifier] = current_time
            return True
        
        if current_time - self.last_alert_time[identifier] >= self.alert_cooldown:
            self.last_alert_time[identifier] = current_time
            return True
        
        return False
    
    def run(self, fps=15):
        """Main detection loop"""
        if not self.cap:
            print("❌ No camera available")
            return
        
        # Load whitelist
        self.load_whitelist()
        
        print(f"\n🤖 Starting DoggoBot Face Detector")
        print(f"   API URL: {self.api_url}")
        print(f"   Streaming FPS: {fps}")
        print(f"   Face Recognition: {'Enabled' if FACE_RECOGNITION_AVAILABLE else 'Disabled (OpenCV fallback)'}")
        print(f"   Whitelist: {len(self.known_face_names)} face encodings loaded")
        print(f"\nPress 'q' to quit, 'r' to reload whitelist\n")
        
        frame_interval = 1.0 / fps
        frame_count = 0
        process_every = 3  # Process faces every N frames for performance
        
        try:
            while True:
                start_time = time.time()
                
                ret, frame = self.cap.read()
                if not ret:
                    continue
                
                frame_count += 1
                
                # Detect faces periodically
                if frame_count % process_every == 0:
                    if FACE_RECOGNITION_AVAILABLE and self.known_face_encodings:
                        faces = self.detect_faces_recognition(frame)
                    else:
                        faces = self.detect_faces_opencv(frame)
                    
                    # Process detections
                    for face in faces:
                        top, right, bottom, left = face['location']
                        name = face['name']
                        confidence = face['confidence']
                        
                        # Draw box and label
                        if name:
                            # Known person - green box
                            color = (0, 255, 0)
                            status = "friendly"
                            label = f"{name} ({confidence:.2f})"
                            identifier = name
                        else:
                            # Unknown person - red box
                            color = (0, 0, 255)
                            status = "unknown"
                            label = "Unknown"
                            identifier = "unknown"
                        
                        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                        cv2.putText(frame, label, (left, top - 10),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                        
                        # Send alert if cooldown passed
                        if self.should_send_alert(identifier):
                            self.post_alert(name, status, frame, confidence)
                
                # Add status overlay
                status_text = f"Frames: {frame_count} | Whitelist: {len(set(self.known_face_names))} people"
                cv2.putText(frame, status_text, (10, 30),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Post frame to backend
                if frame_count % 2 == 0:  # Post every other frame
                    self.post_frame(frame)
                
                # Show preview
                cv2.imshow('DoggoBot Face Detector (press q to quit, r to reload)', frame)
                
                # Handle keypresses
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


def main():
    parser = argparse.ArgumentParser(description="DoggoBot Real Face Detection & Recognition")
    parser.add_argument('--api-url', default='http://localhost:8000',
                       help='Backend API URL (default: http://localhost:8000)')
    parser.add_argument('--api-key', default='doggobot-secret-key-change-me',
                       help='API key for authentication')
    parser.add_argument('--camera-index', type=int, default=2,
                       help='Camera index (default: 2)')
    parser.add_argument('--fps', type=int, default=15,
                       help='Frame rate for streaming (default: 15)')
    
    args = parser.parse_args()
    
    detector = FaceDetector(
        api_url=args.api_url,
        api_key=args.api_key,
        camera_index=args.camera_index
    )
    detector.run(fps=args.fps)


if __name__ == "__main__":
    main()

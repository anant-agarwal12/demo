#!/usr/bin/env python3
"""
GPU-Accelerated Face Recognition System for DoggoBot

This script provides real-time face detection and recognition with:
- GPU acceleration support (CUDA/dlib)
- Bounding box detection
- Whitelist face recognition
- Real-time streaming to backend with detection data

Usage:
    python face_detector_real.py --camera-index 0 --fps 30
    python face_detector_real.py --camera-index 2 --whitelist-dir ./whitelist
"""

import cv2
import face_recognition
import requests
import json
import time
import argparse
import os
import sys
import platform
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# Default configuration
API_URL = "http://localhost:8000"
API_KEY = "doggobot-secret-key-change-me"
DEFAULT_FPS = 30
DEFAULT_CAMERA_INDEX = 0

class FaceDetectorGPU:
    """GPU-accelerated face detection and recognition system"""
    
    def __init__(
        self,
        api_url: str = API_URL,
        api_key: str = API_KEY,
        camera_index: int = DEFAULT_CAMERA_INDEX,
        target_fps: int = DEFAULT_FPS,
        whitelist_dir: Optional[str] = None,
        use_gpu: bool = True
    ):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.headers = {"X-API-KEY": api_key}
        self.camera_index = camera_index
        self.target_fps = target_fps
        self.use_gpu = use_gpu
        
        # Check GPU availability
        self.gpu_available = self._check_gpu()
        
        # Initialize camera
        self.cap = self._init_camera(camera_index)
        if self.cap is None:
            raise RuntimeError(f"Failed to initialize camera {camera_index}")
        
        # Whitelist data
        self.known_face_encodings = []
        self.known_face_names = []
        self.whitelist_dir = whitelist_dir
        
        if whitelist_dir:
            self._load_whitelist(whitelist_dir)
        
        # Performance tracking
        self.frame_count = 0
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.actual_fps = 0.0
        
        # Alert throttling
        self.last_alert_time = {}
        self.alert_cooldown = 5.0  # seconds
        
        print(f"\n{'='*60}")
        print(f"🤖 DoggoBot Face Detector Initialized")
        print(f"{'='*60}")
        print(f"GPU Acceleration: {'✅ ENABLED' if self.gpu_available and self.use_gpu else '❌ DISABLED (CPU mode)'}")
        print(f"Camera Index: {camera_index}")
        print(f"Target FPS: {target_fps}")
        print(f"Whitelist: {len(self.known_face_names)} known faces")
        print(f"API URL: {self.api_url}")
        print(f"{'='*60}\n")
    
    def _check_gpu(self) -> bool:
        """Check if GPU acceleration is available"""
        try:
            import dlib
            if hasattr(dlib, 'DLIB_USE_CUDA') and dlib.DLIB_USE_CUDA:
                try:
                    gpu_count = dlib.cuda.get_num_devices()
                    print(f"✅ GPU acceleration available ({gpu_count} GPU(s) detected)")
                    return True
                except:
                    print("✅ GPU acceleration available")
                    return True
            else:
                print("ℹ️  GPU acceleration not available (using CPU)")
                return False
        except (ImportError, AttributeError):
            print("ℹ️  GPU acceleration not available (using CPU)")
            return False
    
    def _init_camera(self, camera_index: int):
        """Initialize camera capture"""
        try:
            # On Windows, prefer DirectShow backend
            if platform.system().lower().startswith("win"):
                cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
            else:
                cap = cv2.VideoCapture(camera_index)
            
            if not cap.isOpened():
                print(f"❌ Failed to open camera {camera_index}")
                return None
            
            # Set camera properties for better performance
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            cap.set(cv2.CAP_PROP_FPS, self.target_fps)
            
            # Try to set MJPEG codec for better performance
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            
            print(f"✅ Camera {camera_index} initialized")
            return cap
        
        except Exception as e:
            print(f"❌ Error initializing camera: {e}")
            return None
    
    def _load_whitelist(self, whitelist_dir: str):
        """Load known faces from whitelist directory"""
        whitelist_path = Path(whitelist_dir)
        
        if not whitelist_path.exists():
            print(f"⚠️  Whitelist directory not found: {whitelist_dir}")
            return
        
        print(f"Loading whitelist from: {whitelist_dir}")
        
        # Supported image extensions
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
        
        for person_dir in whitelist_path.iterdir():
            if not person_dir.is_dir():
                continue
            
            person_name = person_dir.name
            person_encodings = []
            
            for image_file in person_dir.iterdir():
                if image_file.suffix.lower() not in image_extensions:
                    continue
                
                try:
                    # Load image
                    image = face_recognition.load_image_file(str(image_file))
                    
                    # Get face encodings
                    encodings = face_recognition.face_encodings(
                        image,
                        model='small' if not self.gpu_available else 'large'
                    )
                    
                    if encodings:
                        person_encodings.append(encodings[0])
                        print(f"  ✓ Loaded {person_name}/{image_file.name}")
                    else:
                        print(f"  ⚠ No face found in {person_name}/{image_file.name}")
                
                except Exception as e:
                    print(f"  ✗ Error loading {person_name}/{image_file.name}: {e}")
            
            # Average encodings for this person
            if person_encodings:
                avg_encoding = np.mean(person_encodings, axis=0)
                self.known_face_encodings.append(avg_encoding)
                self.known_face_names.append(person_name)
                print(f"✅ {person_name}: {len(person_encodings)} images loaded")
        
        print(f"\n✅ Whitelist loaded: {len(self.known_face_names)} people\n")
    
    def detect_faces(self, frame: np.ndarray) -> Tuple[List, List, List]:
        """
        Detect faces in frame and return locations, encodings, and names
        
        Returns:
            face_locations: List of (top, right, bottom, left) tuples
            face_encodings: List of face encodings
            face_names: List of identified names
        """
        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        # Use CNN model if GPU available, HOG otherwise
        model = 'cnn' if self.gpu_available and self.use_gpu else 'hog'
        
        face_locations = face_recognition.face_locations(rgb_frame, model=model)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        # Scale face locations back to original frame size
        face_locations = [(top*2, right*2, bottom*2, left*2) 
                          for (top, right, bottom, left) in face_locations]
        
        # Identify faces
        face_names = []
        for face_encoding in face_encodings:
            name = "Unknown"
            
            if self.known_face_encodings:
                # Compare with known faces
                matches = face_recognition.compare_faces(
                    self.known_face_encodings,
                    face_encoding,
                    tolerance=0.6
                )
                
                # Use the known face with smallest distance
                face_distances = face_recognition.face_distance(
                    self.known_face_encodings,
                    face_encoding
                )
                
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                        confidence = 1.0 - face_distances[best_match_index]
            
            face_names.append(name)
        
        return face_locations, face_encodings, face_names
    
    def draw_faces(self, frame: np.ndarray, face_locations: List, face_names: List) -> np.ndarray:
        """Draw bounding boxes and labels on frame"""
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Determine color based on recognition
            if name != "Unknown":
                color = (0, 255, 0)  # Green for known faces
                status = "FRIENDLY"
            else:
                color = (0, 165, 255)  # Orange for unknown faces
                status = "UNKNOWN"
            
            # Draw bounding box
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            # Draw label background
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            
            # Draw text
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, f"{name}", (left + 6, bottom - 12), font, 0.6, (255, 255, 255), 1)
            cv2.putText(frame, status, (left + 6, bottom - 28), font, 0.4, (255, 255, 255), 1)
        
        return frame
    
    def post_frame_with_detections(self, frame: np.ndarray, face_locations: List, face_names: List):
        """Post frame to backend with detection metadata"""
        try:
            # Prepare detection data
            detections = []
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                detections.append({
                    'bbox': {'x': left, 'y': top, 'width': right - left, 'height': bottom - top},
                    'name': name,
                    'status': 'friendly' if name != "Unknown" else 'unknown'
                })
            
            # Encode frame
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            
            # Prepare multipart request
            files = {'frame': ('frame.jpg', buffer.tobytes(), 'image/jpeg')}
            data = {'detections': json.dumps(detections)}
            
            # Post to backend
            response = requests.post(
                f"{self.api_url}/frame",
                files=files,
                data=data,
                headers=self.headers,
                timeout=1.0
            )
            
            return response.status_code == 200
        
        except Exception as e:
            # Silent fail to avoid spamming console
            return False
    
    def post_alert(self, frame: np.ndarray, face_location: Tuple, name: str):
        """Post detection alert to backend"""
        try:
            top, right, bottom, left = face_location
            
            # Prepare alert data
            alert_data = {
                "label": "person",
                "status": "friendly" if name != "Unknown" else "unknown",
                "identity": name if name != "Unknown" else None,
                "confidence": 0.85,
                "bbox": {
                    "x": left,
                    "y": top,
                    "width": right - left,
                    "height": bottom - top
                },
                "timestamp": time.time()
            }
            
            # Encode snapshot
            _, buffer = cv2.imencode('.jpg', frame)
            
            # Post alert
            files = {'snapshot': ('snapshot.jpg', buffer.tobytes(), 'image/jpeg')}
            data = {'payload': json.dumps(alert_data)}
            
            response = requests.post(
                f"{self.api_url}/alert",
                data=data,
                files=files,
                headers=self.headers,
                timeout=3.0
            )
            
            if response.status_code == 200:
                print(f"📸 Alert: {name} detected")
                return True
            
            return False
        
        except Exception as e:
            print(f"⚠️  Alert failed: {e}")
            return False
    
    def should_send_alert(self, name: str) -> bool:
        """Check if enough time has passed to send another alert for this person"""
        current_time = time.time()
        
        if name not in self.last_alert_time:
            self.last_alert_time[name] = current_time
            return True
        
        if current_time - self.last_alert_time[name] >= self.alert_cooldown:
            self.last_alert_time[name] = current_time
            return True
        
        return False
    
    def update_fps(self):
        """Update FPS counter"""
        self.fps_counter += 1
        current_time = time.time()
        
        if current_time - self.fps_start_time >= 1.0:
            self.actual_fps = self.fps_counter / (current_time - self.fps_start_time)
            self.fps_counter = 0
            self.fps_start_time = current_time
    
    def run(self, show_preview: bool = True, post_every_frame: int = 1):
        """Run the face detection loop"""
        print("🚀 Starting face detection...")
        print("Press 'q' to quit\n")
        
        frame_interval = 1.0 / self.target_fps
        
        try:
            while True:
                loop_start = time.time()
                
                # Capture frame
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    print("⚠️  Failed to read frame, retrying...")
                    time.sleep(0.1)
                    continue
                
                self.frame_count += 1
                
                # Detect faces
                face_locations, face_encodings, face_names = self.detect_faces(frame)
                
                # Draw bounding boxes
                display_frame = self.draw_faces(frame.copy(), face_locations, face_names)
                
                # Add FPS and info overlay
                self.update_fps()
                info_text = f"FPS: {self.actual_fps:.1f} | Faces: {len(face_locations)} | Frame: {self.frame_count}"
                cv2.putText(display_frame, info_text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                gpu_text = f"GPU: {'ON' if self.gpu_available and self.use_gpu else 'OFF'}"
                cv2.putText(display_frame, gpu_text, (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # Post frame to backend (with detections)
                if self.frame_count % post_every_frame == 0:
                    self.post_frame_with_detections(display_frame, face_locations, face_names)
                
                # Post alerts for new detections
                for face_location, name in zip(face_locations, face_names):
                    if self.should_send_alert(name):
                        self.post_alert(frame, face_location, name)
                
                # Show preview
                if show_preview:
                    cv2.imshow("DoggoBot Face Detector (Press 'q' to quit)", display_frame)
                    
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print("\n🛑 Quit requested")
                        break
                
                # Maintain target FPS
                elapsed = time.time() - loop_start
                sleep_time = frame_interval - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            print("\n\n🛑 Interrupted by user")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Release resources"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print(f"\n✅ Stopped. Total frames processed: {self.frame_count}")
        print(f"   Average FPS: {self.actual_fps:.1f}\n")

def main():
    parser = argparse.ArgumentParser(
        description="GPU-Accelerated Face Detection for DoggoBot"
    )
    
    parser.add_argument(
        '--camera-index',
        type=int,
        default=DEFAULT_CAMERA_INDEX,
        help=f'Camera index (default: {DEFAULT_CAMERA_INDEX})'
    )
    
    parser.add_argument(
        '--fps',
        type=int,
        default=DEFAULT_FPS,
        help=f'Target FPS (default: {DEFAULT_FPS})'
    )
    
    parser.add_argument(
        '--api-url',
        default=API_URL,
        help=f'Backend API URL (default: {API_URL})'
    )
    
    parser.add_argument(
        '--api-key',
        default=API_KEY,
        help='API key for backend authentication'
    )
    
    parser.add_argument(
        '--whitelist-dir',
        default=None,
        help='Directory containing whitelist face images (organized by person name)'
    )
    
    parser.add_argument(
        '--no-gpu',
        action='store_true',
        help='Disable GPU acceleration (force CPU mode)'
    )
    
    parser.add_argument(
        '--no-preview',
        action='store_true',
        help='Disable preview window'
    )
    
    parser.add_argument(
        '--post-every',
        type=int,
        default=1,
        help='Post frame to backend every N frames (default: 1)'
    )
    
    args = parser.parse_args()
    
    try:
        detector = FaceDetectorGPU(
            api_url=args.api_url,
            api_key=args.api_key,
            camera_index=args.camera_index,
            target_fps=args.fps,
            whitelist_dir=args.whitelist_dir,
            use_gpu=not args.no_gpu
        )
        
        detector.run(
            show_preview=not args.no_preview,
            post_every_frame=args.post_every
        )
    
    except RuntimeError as e:
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

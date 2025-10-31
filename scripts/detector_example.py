#!/usr/bin/env python3
"""
Example perception node that publishes frames and alerts to DoggoBot backend.

This script simulates a detection system by:
1. Capturing frames from webcam (or generating dummy frames)
2. Simulating person detections with random attributes
3. Posting frames and alerts to the DoggoBot API

Usage:
    python detector_example.py [--api-url http://localhost:8000] [--api-key YOUR_KEY]
"""

import requests
import cv2
import numpy as np
import time
import json
import argparse
import random
from datetime import datetime
from io import BytesIO
from PIL import Image

class DetectorPublisher:
    def __init__(self, api_url="http://localhost:8000", api_key="doggobot-secret-key-change-me"):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.headers = {"X-API-KEY": api_key}
        
        # Try to initialize webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("??  No webcam found, will generate dummy frames")
            self.cap = None
        else:
            print("? Webcam initialized")
        
        # Sample names for simulation
        self.known_people = ["Alice", "Bob", "Charlie", "Diana"]
        self.last_alert_time = 0
        self.alert_interval = 5  # seconds between alerts
    
    def generate_dummy_frame(self):
        """Generate a dummy frame with text"""
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        cv2.putText(frame, f"DoggoBot Sim - {timestamp}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Add random "detection" box
        if random.random() > 0.5:
            x1, y1 = random.randint(50, 400), random.randint(50, 300)
            x2, y2 = x1 + random.randint(80, 150), y1 + random.randint(100, 200)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, "Person", (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame
    
    def get_frame(self):
        """Capture or generate a frame"""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
        
        return self.generate_dummy_frame()
    
    def post_frame(self, frame):
        """Post a frame to the /frame endpoint"""
        try:
            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            
            files = {'frame': ('frame.jpg', buffer.tobytes(), 'image/jpeg')}
            response = requests.post(
                f"{self.api_url}/frame",
                files=files,
                headers=self.headers,
                timeout=2
            )
            
            if response.status_code == 200:
                return True
            else:
                print(f"? Frame upload failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"? Error posting frame: {e}")
            return False
    
    def generate_alert(self):
        """Generate a simulated detection alert"""
        # Randomly decide status
        status_types = ['friendly', 'unknown', 'suspicious']
        status = random.choice(status_types)
        
        # Generate alert data
        alert = {
            "label": "person",
            "angle": random.uniform(-1.5, 1.5),  # radians
            "distance": random.uniform(1.0, 8.0),  # meters
            "confidence": random.uniform(0.7, 0.99),
            "status": status,
            "timestamp": time.time()
        }
        
        # Add identity for friendly status
        if status == 'friendly':
            alert["identity"] = random.choice(self.known_people)
        elif status == 'unknown':
            alert["identity"] = "Unknown Person"
        else:
            alert["identity"] = None
        
        return alert
    
    def post_alert(self, alert_data, snapshot=None):
        """Post an alert to the /alert endpoint"""
        try:
            # Prepare form data
            payload = json.dumps(alert_data)
            files = {}
            data = {'payload': payload}
            
            # Add snapshot if provided
            if snapshot is not None:
                _, buffer = cv2.imencode('.jpg', snapshot)
                files['snapshot'] = ('snapshot.jpg', buffer.tobytes(), 'image/jpeg')
            
            response = requests.post(
                f"{self.api_url}/alert",
                data=data,
                files=files if files else None,
                headers=self.headers,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"? Alert posted: {alert_data['status']} - {alert_data.get('identity', 'N/A')} (ID: {result.get('id')})")
                return True
            else:
                print(f"? Alert post failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"? Error posting alert: {e}")
            return False
    
    def run(self, fps=5, alert_enabled=True):
        """Run the publisher loop"""
        print(f"\n?? Starting DoggoBot detector publisher")
        print(f"   API URL: {self.api_url}")
        print(f"   Frame rate: {fps} FPS")
        print(f"   Alerts: {'Enabled' if alert_enabled else 'Disabled'}\n")
        
        frame_interval = 1.0 / fps
        frame_count = 0
        
        try:
            while True:
                start_time = time.time()
                
                # Get frame
                frame = self.get_frame()
                
                # Post frame
                if self.post_frame(frame):
                    frame_count += 1
                    if frame_count % (fps * 5) == 0:  # Every 5 seconds
                        print(f"?? Frames posted: {frame_count}")
                
                # Periodically generate and post alerts
                if alert_enabled:
                    current_time = time.time()
                    if current_time - self.last_alert_time >= self.alert_interval:
                        alert = self.generate_alert()
                        self.post_alert(alert, snapshot=frame)
                        self.last_alert_time = current_time
                
                # Maintain frame rate
                elapsed = time.time() - start_time
                sleep_time = max(0, frame_interval - elapsed)
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            print("\n\n??  Stopped by user")
        finally:
            if self.cap:
                self.cap.release()
            print(f"\n?? Total frames posted: {frame_count}")

def main():
    parser = argparse.ArgumentParser(description="DoggoBot Detector Publisher Example")
    parser.add_argument('--api-url', default='http://localhost:8000',
                       help='Backend API URL (default: http://localhost:8000)')
    parser.add_argument('--api-key', default='doggobot-secret-key-change-me',
                       help='API key for authentication')
    parser.add_argument('--fps', type=int, default=5,
                       help='Frame rate (default: 5)')
    parser.add_argument('--no-alerts', action='store_true',
                       help='Disable alert generation')
    
    args = parser.parse_args()
    
    publisher = DetectorPublisher(api_url=args.api_url, api_key=args.api_key)
    publisher.run(fps=args.fps, alert_enabled=not args.no_alerts)

if __name__ == "__main__":
    main()

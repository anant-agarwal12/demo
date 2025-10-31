#!/usr/bin/env python3
"""
GPU-Accelerated Face Detection for DoggoBot

This script uses face_recognition library with GPU support (dlib CUDA)
to detect faces and send frames with bounding boxes to the backend.

Usage:
    python face_detector_gpu.py --camera-index 0 --fps 30
    python face_detector_gpu.py --camera-index 2 --fps 30
"""

import cv2
import requests
import json
import time
import argparse
import sys
import platform
import os
import numpy as np

# Try to import face_recognition with GPU support
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    print("⚠️  face_recognition library not found. Installing...")
    FACE_RECOGNITION_AVAILABLE = False

# Check for GPU support
def check_gpu_support():
    """Check if dlib has CUDA support"""
    try:
        import dlib
        if hasattr(dlib, 'DLIB_USE_CUDA'):
            return dlib.DLIB_USE_CUDA
        return False
    except ImportError:
        return False

API_URL = "http://localhost:8000"
API_KEY = "doggobot-secret-key-change-me"

def open_capture(source):
    """Open cv2.VideoCapture and try Windows DirectShow backend when appropriate."""
    try:
        if isinstance(source, int):
            # On Windows prefer DirectShow to avoid MSMF issues
            if platform.system().lower().startswith("win"):
                cap = cv2.VideoCapture(source, cv2.CAP_DSHOW)
            else:
                cap = cv2.VideoCapture(source)
        else:
            cap = cv2.VideoCapture(source)
        
        if cap.isOpened():
            # Set resolution for better detection
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        return cap
    except Exception as e:
        print(f"Error opening capture: {e}")
        return None

def detect_faces(frame, detection_model='hog'):
    """
    Detect faces in a frame using face_recognition library
    
    Args:
        frame: OpenCV frame (BGR format)
        detection_model: 'hog' (CPU) or 'cnn' (GPU/CUDA) - requires GPU support
    
    Returns:
        List of bounding boxes in format [(top, right, bottom, left), ...]
    """
    if not FACE_RECOGNITION_AVAILABLE:
        return []
    
    # Convert BGR to RGB for face_recognition
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Detect faces - use 'cnn' if GPU available, otherwise 'hog'
    face_locations = face_recognition.face_locations(rgb_frame, model=detection_model)
    
    return face_locations

def draw_bounding_boxes(frame, face_locations, recognized_names=None):
    """
    Draw bounding boxes on frame
    
    Args:
        frame: OpenCV frame
        face_locations: List of (top, right, bottom, left) tuples
        recognized_names: Optional list of names for each face
    
    Returns:
        Frame with bounding boxes drawn
    """
    for i, (top, right, bottom, left) in enumerate(face_locations):
        # Draw rectangle (BGR format)
        color = (0, 255, 0)  # Green for detected faces
        thickness = 2
        
        cv2.rectangle(frame, (left, top), (right, bottom), color, thickness)
        
        # Add label if name provided
        if recognized_names and i < len(recognized_names) and recognized_names[i]:
            label = recognized_names[i]
            # Draw background rectangle for text
            (text_width, text_height), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1
            )
            cv2.rectangle(
                frame,
                (left, top - text_height - 10),
                (left + text_width, top),
                color,
                -1
            )
            cv2.putText(
                frame,
                label,
                (left, top - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 0),
                1
            )
        else:
            # Just show "Face" if no name
            cv2.putText(
                frame,
                "Face",
                (left, top - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )
    
    return frame

def post_frame_with_boxes(api_url, api_key, frame, bounding_boxes, timeout=1.0):
    """
    Post frame with bounding box metadata to backend
    
    Args:
        api_url: Backend API URL
        api_key: API key
        frame: OpenCV frame
        bounding_boxes: List of (top, right, bottom, left) tuples
        timeout: Request timeout
    """
    try:
        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        
        # Convert bounding boxes to JSON format
        boxes_data = []
        for top, right, bottom, left in bounding_boxes:
            boxes_data.append({
                "top": int(top),
                "right": int(right),
                "bottom": int(bottom),
                "left": int(left),
                "width": int(right - left),
                "height": int(bottom - top)
            })
        
        # Prepare multipart form data
        files = {'frame': ('frame.jpg', buffer.tobytes(), 'image/jpeg')}
        data = {
            'bounding_boxes': json.dumps(boxes_data),
            'face_count': len(bounding_boxes)
        }
        
        response = requests.post(
            f"{api_url}/frame",
            files=files,
            data=data,
            headers={"X-API-KEY": api_key},
            timeout=timeout
        )
        
        return response.status_code == 200
    except Exception as e:
        print(f"[WARN] post_frame_with_boxes failed: {e}")
        return False

def post_alert(api_url, api_key, frame, payload, timeout=3.0):
    """Post alert to backend"""
    try:
        _, buffer = cv2.imencode('.jpg', frame)
        files = {'snapshot': ('snapshot.jpg', buffer.tobytes(), 'image/jpeg')}
        data = {'payload': json.dumps(payload)}
        r = requests.post(
            f"{api_url}/alert",
            data=data,
            files=files,
            headers={"X-API-KEY": api_key},
            timeout=timeout
        )
        return r.status_code if r is not None else None
    except Exception as e:
        print(f"[WARN] post_alert failed: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="GPU-Accelerated Face Detection for DoggoBot")
    parser.add_argument("--camera-index", type=int, default=0, help="Camera index (default: 0)")
    parser.add_argument("--fps", type=float, default=30.0, help="Target processing FPS (default: 30)")
    parser.add_argument("--detection-model", default="hog", choices=["hog", "cnn"],
                       help="Detection model: 'hog' (CPU) or 'cnn' (GPU/CUDA)")
    parser.add_argument("--post-frame-every", type=int, default=1,
                       help="Post frame to backend every N frames (default: 1)")
    parser.add_argument("--alert-interval", type=float, default=5.0,
                       help="Minimum seconds between alert posts (default: 5.0)")
    args = parser.parse_args()

    # Check if face_recognition is available
    if not FACE_RECOGNITION_AVAILABLE:
        print("❌ Error: face_recognition library not installed.")
        print("   Install with: pip install face-recognition")
        sys.exit(1)

    # Check GPU support
    has_gpu = check_gpu_support()
    if has_gpu:
        print("✅ GPU (CUDA) support detected in dlib!")
        if args.detection_model == "hog":
            print("⚠️  Using HOG model. For GPU acceleration, use --detection-model cnn")
    else:
        print("⚠️  No GPU (CUDA) support detected. Using CPU mode.")
        if args.detection_model == "cnn":
            print("⚠️  CNN model requires GPU. Switching to HOG model.")
            args.detection_model = "hog"

    # Open camera
    cap = open_capture(args.camera_index)
    if cap is None or not cap.isOpened():
        print(f"❌ ERROR: Could not open camera: {args.camera_index}")
        return

    print(f"✅ Camera opened: {args.camera_index}")
    print(f"📡 Posting frames/alerts to: {API_URL}")
    print(f"🎯 Detection model: {args.detection_model.upper()}")
    print("Press 'q' in the preview window to quit\n")

    frame_count = 0
    last_alert_time = 0.0
    target_fps = args.fps if args.fps > 0 else 30.0
    min_frame_time = 1.0 / target_fps
    fps_history = []

    try:
        while True:
            loop_start = time.time()
            ret, frame = cap.read()
            if not ret or frame is None:
                time.sleep(0.05)
                continue

            frame_count += 1

            # Detect faces
            face_locations = detect_faces(frame, detection_model=args.detection_model)
            
            # Draw bounding boxes on frame
            frame_with_boxes = draw_bounding_boxes(frame.copy(), face_locations)

            # Post frame with bounding boxes
            if args.post_frame_every > 0 and frame_count % args.post_frame_every == 0:
                post_frame_with_boxes(
                    API_URL, API_KEY, frame_with_boxes, face_locations, timeout=1.0
                )

            # Post alert if faces detected and enough time passed
            now = time.time()
            if len(face_locations) > 0 and (now - last_alert_time) > args.alert_interval:
                payload = {
                    "label": "person",
                    "status": "unknown" if len(face_locations) > 0 else None,
                    "identity": None,
                    "confidence": 0.85,
                    "distance": None,
                    "angle": 0.0,
                    "timestamp": now,
                    "face_count": len(face_locations),
                    "bounding_boxes": [
                        {"top": top, "right": right, "bottom": bottom, "left": left}
                        for top, right, bottom, left in face_locations
                    ]
                }
                code = post_alert(API_URL, API_KEY, frame_with_boxes, payload, timeout=3.0)
                if code is not None:
                    print(f"📸 Alert posted ({len(face_locations)} faces) at frame {frame_count}")
                last_alert_time = now

            # Calculate FPS
            elapsed = time.time() - loop_start
            current_fps = 1.0 / elapsed if elapsed > 0 else 0
            fps_history.append(current_fps)
            if len(fps_history) > 30:
                fps_history.pop(0)
            avg_fps = sum(fps_history) / len(fps_history)

            # Overlay info on frame
            display_text = f"Frame: {frame_count} | FPS: {avg_fps:.1f} | Faces: {len(face_locations)}"
            cv2.putText(
                frame_with_boxes, display_text, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
            )
            
            # Show model info
            model_text = f"Model: {args.detection_model.upper()}{' (GPU)' if has_gpu and args.detection_model == 'cnn' else ' (CPU)'}"
            cv2.putText(
                frame_with_boxes, model_text, (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2
            )

            cv2.imshow("DoggoBot Face Detection (press q to quit)", frame_with_boxes)

            # Quit on 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # Limit loop to target FPS
            elapsed = time.time() - loop_start
            sleep_for = min_frame_time - elapsed
            if sleep_for > 0:
                time.sleep(sleep_for)

    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print(f"\n✅ Stopped. Total frames processed: {frame_count}")

if __name__ == "__main__":
    main()

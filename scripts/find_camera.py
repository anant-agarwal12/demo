#!/usr/bin/env python3
"""
Camera Detection Utility for DoggoBot

This script helps you find available cameras on your system.
"""

import cv2
import sys

def test_camera(index, max_wait=1.0):
    """Test if a camera at given index is available"""
    try:
        # Try to open camera
        cap = cv2.VideoCapture(index)
        
        if not cap.isOpened():
            return None
        
        # Try to read a frame
        ret, frame = cap.read()
        
        if not ret or frame is None:
            cap.release()
            return None
        
        # Get camera properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        cap.release()
        
        return {
            'index': index,
            'width': width,
            'height': height,
            'fps': fps
        }
    
    except Exception as e:
        return None

def main():
    print("\n" + "="*60)
    print("🎥 DoggoBot Camera Detection")
    print("="*60 + "\n")
    
    print("Scanning for cameras (this may take a few seconds)...\n")
    
    found_cameras = []
    
    # Test camera indices 0-9
    for i in range(10):
        info = test_camera(i)
        if info:
            found_cameras.append(info)
            print(f"✅ Camera {i} detected:")
            print(f"   Resolution: {info['width']}x{info['height']}")
            print(f"   FPS: {info['fps']}")
            print()
    
    print("="*60)
    
    if found_cameras:
        print(f"\n🎉 Found {len(found_cameras)} camera(s)!\n")
        print("To use a camera, run:")
        print(f"  python face_detector_real.py --camera-index {found_cameras[0]['index']}")
        
        if len(found_cameras) > 1:
            print("\nOther available cameras:")
            for cam in found_cameras[1:]:
                print(f"  python face_detector_real.py --camera-index {cam['index']}")
        
        print("\n" + "="*60 + "\n")
        return 0
    else:
        print("\n❌ No cameras found!\n")
        print("Troubleshooting:")
        print("  • Make sure a camera is connected")
        print("  • On Linux: Check permissions (sudo chmod 666 /dev/video0)")
        print("  • On Windows: Close apps that might be using camera")
        print("  • Try external USB camera")
        print("\n" + "="*60 + "\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())

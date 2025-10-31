#!/usr/bin/env python3
"""
Download Haar Cascade file for face detection
Run this if you're having issues with OpenCV face detection
"""

import os
import urllib.request

# Create haarcascades directory
os.makedirs('haarcascades', exist_ok=True)

cascade_url = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
cascade_path = "haarcascades/haarcascade_frontalface_default.xml"

print("📥 Downloading Haar Cascade for face detection...")
print(f"   From: {cascade_url}")
print(f"   To: {cascade_path}")

try:
    urllib.request.urlretrieve(cascade_url, cascade_path)
    print("✅ Download complete!")
    print(f"\nCascade file saved to: {os.path.abspath(cascade_path)}")
    print("\nYou can now run face_detector_real.py")
except Exception as e:
    print(f"❌ Download failed: {e}")
    print("\nAlternative: Download manually from:")
    print(cascade_url)
    print(f"And save it to: {os.path.abspath(cascade_path)}")

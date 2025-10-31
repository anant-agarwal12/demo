#!/usr/bin/env python3
"""
DroidCam Connection Tester

This script helps you find the correct way to connect to DroidCam.
DroidCam can work in multiple modes:
1. USB mode (appears as video device)
2. WiFi mode (IP camera stream)
"""

import cv2
import sys
import platform

def test_video_device(index, backend=None):
    """Test a video device with optional backend"""
    try:
        print(f"Testing camera index {index}", end="")
        if backend:
            print(f" with {backend} backend...", end="")
            cap = cv2.VideoCapture(index, backend)
        else:
            print("...", end="")
            cap = cv2.VideoCapture(index)
        
        if not cap.isOpened():
            print(" ❌ Failed to open")
            return False
        
        # Try to read a frame with timeout
        for attempt in range(3):
            ret, frame = cap.read()
            if ret and frame is not None:
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                print(f" ✅ Success! Resolution: {width}x{height}")
                
                # Show the frame briefly
                cv2.imshow(f"DroidCam Test - Camera {index}", frame)
                cv2.waitKey(1000)
                cv2.destroyAllWindows()
                
                cap.release()
                return True
        
        print(" ❌ Failed to read frame")
        cap.release()
        return False
    
    except Exception as e:
        print(f" ❌ Error: {e}")
        return False

def test_ip_stream(ip_address, port=4747):
    """Test DroidCam WiFi mode (IP camera)"""
    urls_to_try = [
        f"http://{ip_address}:{port}/video",
        f"http://{ip_address}:{port}/mjpegfeed",
        f"http://{ip_address}:{port}/videofeed",
    ]
    
    for url in urls_to_try:
        try:
            print(f"Testing URL: {url}...", end="")
            cap = cv2.VideoCapture(url)
            
            if not cap.isOpened():
                print(" ❌ Failed to open")
                continue
            
            ret, frame = cap.read()
            if ret and frame is not None:
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                print(f" ✅ Success! Resolution: {width}x{height}")
                print(f"\n🎉 Found DroidCam at: {url}")
                
                cv2.imshow("DroidCam WiFi Test", frame)
                cv2.waitKey(2000)
                cv2.destroyAllWindows()
                
                cap.release()
                return url
            else:
                print(" ❌ Failed to read frame")
            
            cap.release()
        
        except Exception as e:
            print(f" ❌ Error: {e}")
    
    return None

def main():
    print("\n" + "="*60)
    print("📱 DroidCam Connection Tester")
    print("="*60 + "\n")
    
    system = platform.system().lower()
    
    # First, try video device indices
    print("🔍 Testing USB/Video Device Mode...")
    print("-" * 60)
    
    found_devices = []
    
    # Test different backends on Windows
    if system.startswith("win"):
        backends = [
            (cv2.CAP_DSHOW, "DirectShow"),
            (cv2.CAP_MSMF, "Media Foundation"),
            (None, "Default")
        ]
        
        for index in range(10):
            for backend, name in backends:
                if test_video_device(index, backend):
                    found_devices.append((index, name))
                    break  # Found it, no need to try other backends
    else:
        # Linux/Mac
        for index in range(10):
            if test_video_device(index):
                found_devices.append((index, "Default"))
    
    print()
    
    # Ask about WiFi mode
    print("\n🌐 WiFi Mode (IP Camera)")
    print("-" * 60)
    print("DroidCam WiFi mode uses IP address streaming.")
    print("Check the DroidCam app on your phone for the IP address.")
    print()
    
    use_wifi = input("Do you want to test WiFi mode? (y/N): ").strip().lower()
    
    wifi_url = None
    if use_wifi == 'y':
        ip_address = input("Enter IP address from DroidCam app (e.g., 192.168.1.100): ").strip()
        port = input("Enter port (default 4747): ").strip()
        port = int(port) if port else 4747
        
        print()
        wifi_url = test_ip_stream(ip_address, port)
    
    # Summary
    print("\n" + "="*60)
    print("📝 SUMMARY")
    print("="*60)
    
    if found_devices:
        print("\n✅ USB/Video Device Mode:")
        for index, backend in found_devices:
            print(f"   • Camera {index} ({backend})")
        print("\n   Use with:")
        index, backend = found_devices[0]
        if system.startswith("win") and backend != "Default":
            print(f"   python face_detector_real.py --camera-index {index} --droidcam-usb")
        else:
            print(f"   python face_detector_real.py --camera-index {index}")
    else:
        print("\n❌ No USB/Video devices found")
    
    if wifi_url:
        print("\n✅ WiFi Mode:")
        print(f"   • URL: {wifi_url}")
        print("\n   Use with:")
        print(f"   python face_detector_real.py --camera-url \"{wifi_url}\"")
    
    if not found_devices and not wifi_url:
        print("\n❌ No DroidCam connections found!")
        print("\nTroubleshooting:")
        print("1. Make sure DroidCam app is running on your phone")
        print("2. For USB: Connect phone via USB and enable USB debugging")
        print("3. For WiFi: Make sure phone and PC are on same network")
        print("4. Try restarting the DroidCam app")
        print("5. On Windows, install DroidCam Client from droidcam.com")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)

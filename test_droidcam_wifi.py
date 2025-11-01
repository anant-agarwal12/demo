#!/usr/bin/env python3
"""Quick DroidCam WiFi test for IP: 10.9.48.59"""

import cv2
import sys

IP = "10.9.48.59"
PORT = 4747

print(f"\n{'='*60}")
print(f"Testing DroidCam WiFi: {IP}:{PORT}")
print(f"{'='*60}\n")

# Try different URL formats
urls = [
    f"http://{IP}:{PORT}/video",
    f"http://{IP}:{PORT}/mjpegfeed",
    f"http://{IP}:{PORT}/videofeed",
]

success_url = None

for url in urls:
    print(f"Testing: {url} ... ", end="", flush=True)
    try:
        cap = cv2.VideoCapture(url)
        
        if not cap.isOpened():
            print("❌ Failed to open")
            continue
        
        # Try to read a frame
        ret, frame = cap.read()
        
        if ret and frame is not None:
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(f"✅ SUCCESS! ({width}x{height})")
            
            # Show preview
            cv2.imshow("DroidCam Preview - Press any key", frame)
            print("\n📸 Showing preview... press any key to continue")
            cv2.waitKey(3000)
            cv2.destroyAllWindows()
            
            success_url = url
            cap.release()
            break
        else:
            print("❌ Can't read frames")
        
        cap.release()
    
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "="*60)

if success_url:
    print("🎉 SUCCESS! DroidCam WiFi is working!")
    print("="*60)
    print(f"\n✅ Working URL: {success_url}\n")
    print("📋 Use this command to start face detection:\n")
    print(f'python face_detector_real.py --camera-url "{success_url}"\n')
    print("Or with options:")
    print(f'python face_detector_real.py --camera-url "{success_url}" --fps 20 --whitelist-dir ./whitelist\n')
else:
    print("❌ Could not connect to DroidCam")
    print("="*60)
    print("\n🔧 Troubleshooting:")
    print(f"1. Make sure DroidCam app is running on your phone")
    print(f"2. Check the IP shown in app matches: {IP}")
    print(f"3. Try opening in browser: http://{IP}:{PORT}/video")
    print(f"4. Make sure phone and PC are on same WiFi network")
    print(f"5. Check firewall isn't blocking port {PORT}")

print("\n" + "="*60 + "\n")

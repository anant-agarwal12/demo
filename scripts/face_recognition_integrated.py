#!/usr/bin/env python3
"""
Face Recognition Node - integrated with backend posting + FPS limiter.

Usage:
    python face_recognition_integrated.py --source 0 --fps 30
    python face_recognition_integrated.py --source video.mp4

Notes:
 - On Windows the script will try to open cameras with DirectShow (CAP_DSHOW).
 - If you pass a video file as --source, the FPS limiter is not strictly enforced
   (we read frames as the file provides them).
"""

import cv2
import requests
import json
import time
import argparse
import sys
import platform

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
        return cap
    except Exception as e:
        print("Error opening capture:", e)
        return None

def post_frame(api_url, api_key, frame, timeout=1.0):
    try:
        _, buffer = cv2.imencode('.jpg', frame)
        files = {'frame': ('frame.jpg', buffer.tobytes(), 'image/jpeg')}
        requests.post(f"{api_url}/frame", files=files, headers={"X-API-KEY": api_key}, timeout=timeout)
        return True
    except Exception:
        return False

def post_alert(api_url, api_key, frame, payload, timeout=3.0):
    try:
        _, buffer = cv2.imencode('.jpg', frame)
        files = {'snapshot': ('snapshot.jpg', buffer.tobytes(), 'image/jpeg')}
        data = {'payload': json.dumps(payload)}
        r = requests.post(f"{api_url}/alert", data=data, files=files, headers={"X-API-KEY": api_key}, timeout=timeout)
        return r.status_code if r is not None else None
    except Exception as e:
        # don't spam the console with requests errors every frame
        print(f"[WARN] post_alert failed: {e}")
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=0, help="webcam index or path to video file")
    parser.add_argument("--fps", type=float, default=30.0, help="target processing FPS (webcam only)")
    parser.add_argument("--post-frame-every", type=int, default=3, help="post frame to backend every N frames (0=never)")
    parser.add_argument("--alert-interval", type=float, default=5.0, help="minimum seconds between alert posts")
    args = parser.parse_args()

    # parse source
    source = int(args.source) if str(args.source).isdigit() else args.source
    cap = open_capture(source)
    if cap is None or not cap.isOpened():
        print(f"ERROR: Could not open camera/source: {source}")
        return

    print(f"✅ Camera/source opened: {source}")
    print(f"📡 Posting frames/alerts to: {API_URL}")
    print("Press 'q' in the preview window to quit\n")

    frame_count = 0
    last_alert_time = 0.0
    target_fps = args.fps if args.fps and args.fps > 0 else 30.0
    min_frame_time = 1.0 / target_fps
    is_video_file = isinstance(source, str) and not str(source).isdigit()

    try:
        while True:
            loop_start = time.time()
            ret, frame = cap.read()
            if not ret or frame is None:
                # If it's a video file, end normally; for webcam, keep trying briefly
                if is_video_file:
                    print("[INFO] End of video file or can't read frame.")
                    break
                else:
                    # webcam dropped a frame; sleep a bit and continue
                    time.sleep(0.05)
                    continue

            frame_count += 1

            # Post frame occasionally (reduce bandwidth)
            if args.post_frame_every and args.post_frame_every > 0:
                if frame_count % args.post_frame_every == 0:
                    ok = post_frame(API_URL, API_KEY, frame, timeout=1.0)
                    if not ok:
                        # silent fail, but you can debug by enabling prints
                        pass

            # Post a synthetic alert every alert_interval seconds (demo / placeholder)
            now = time.time()
            if now - last_alert_time > args.alert_interval:
                payload = {
                    "label": "person",
                    "status": "unknown",
                    "identity": None,
                    "confidence": 0.85,
                    "distance": None,
                    "angle": 0.0,
                    "timestamp": now
                }
                code = post_alert(API_URL, API_KEY, frame, payload, timeout=3.0)
                if code is not None:
                    print(f"📸 Alert posted (http {code}) at frame {frame_count}")
                last_alert_time = now

            # Overlay info and show preview
            display_text = f"Frame: {frame_count} | FPS target: {target_fps:.1f}"
            cv2.putText(frame, display_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("DoggoBot Camera (press q to quit)", frame)

            # quit key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # If processing a webcam, limit loop to target FPS
            if not is_video_file:
                elapsed = time.time() - loop_start
                sleep_for = min_frame_time - elapsed
                if sleep_for > 0:
                    time.sleep(sleep_for)
                # quick small safeguard to avoid drift
                # (no exact hard real-time guarantee but it'll be close)
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print(f"\n✅ Stopped. Total frames processed: {frame_count}")

if __name__ == "__main__":
    main()

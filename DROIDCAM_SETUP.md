# 📱 DroidCam Setup Guide for Face Detection

## Problem

DroidCam requires special handling because it can work in two modes:
1. **USB Mode** - Phone connected via USB
2. **WiFi Mode** - Phone connected over network

The "failed to read frame" error usually happens when:
- Wrong camera backend is used (DirectShow vs Media Foundation)
- DroidCam is in WiFi mode but you're trying to use it as USB device
- Camera index is wrong

---

## ✅ Quick Fix

### Step 1: Find Your DroidCam Connection

Run this test script:
```bash
cd scripts
python test_droidcam.py
```

This will:
- Scan all camera indices (0-9)
- Test different backends (DirectShow, Media Foundation)
- Show you which one works
- Test WiFi mode if you provide IP address

### Step 2: Use the Correct Command

The test script will tell you exactly which command to use!

---

## 📱 DroidCam USB Mode

### Setup
1. Connect phone via USB
2. Enable USB debugging on phone
3. Open DroidCam app on phone
4. Select "USB" mode
5. On Windows, make sure DroidCam Client is installed

### Find Camera Index
```bash
python test_droidcam.py
```

### Run Face Detector
```bash
# If test found camera at index 2 with DirectShow
python face_detector_real.py --camera-index 2 --droidcam-usb

# If test found it at different index
python face_detector_real.py --camera-index X --droidcam-usb
```

---

## 🌐 DroidCam WiFi Mode (Recommended!)

### Setup
1. Make sure phone and computer are on **same WiFi network**
2. Open DroidCam app on phone
3. Note the IP address shown (e.g., 192.168.1.100)
4. Note the port (usually 4747)

### Get the URL
Run test script and choose WiFi mode:
```bash
python test_droidcam.py
# When asked, enter your phone's IP address
```

Or manually try these URLs:
- `http://YOUR_IP:4747/video`
- `http://YOUR_IP:4747/mjpegfeed`
- `http://YOUR_IP:4747/videofeed`

### Run Face Detector with URL
```bash
# Replace with your IP address
python face_detector_real.py --camera-url "http://192.168.1.100:4747/video"
```

Example:
```bash
python face_detector_real.py --camera-url "http://192.168.1.100:4747/video" --fps 20
```

---

## 🔧 Common Issues & Solutions

### Issue 1: "Failed to open camera"
**Solution:** Wrong camera index
```bash
# Run the tester
python test_droidcam.py

# It will show you the correct index
```

### Issue 2: "Failed to read frame"  (Your current issue!)
**Solutions:**

**A. Try USB with `--droidcam-usb` flag:**
```bash
python face_detector_real.py --camera-index 0 --droidcam-usb
python face_detector_real.py --camera-index 1 --droidcam-usb
python face_detector_real.py --camera-index 2 --droidcam-usb
```

**B. Switch to WiFi mode (often more reliable):**
```bash
# Get IP from DroidCam app on phone
python face_detector_real.py --camera-url "http://192.168.1.100:4747/video"
```

**C. Install DroidCam Client (Windows only):**
- Download from: https://www.dev47apps.com/droidcam/windows/
- This creates a proper virtual webcam device

### Issue 3: "Connection timed out" (WiFi mode)
**Causes:**
- Phone and PC on different WiFi networks
- Firewall blocking connection
- Wrong IP address

**Solutions:**
```bash
# Check phone IP address in DroidCam app
# Make sure both devices on same network
# Try pinging the phone:
ping 192.168.1.100

# Try in browser first:
# Open: http://192.168.1.100:4747/video
# If you see video, the URL works!
```

### Issue 4: Low FPS or choppy video
**Solutions:**
```bash
# Lower FPS target
python face_detector_real.py --camera-url "http://192.168.1.100:4747/video" --fps 15

# Post fewer frames to backend
python face_detector_real.py --camera-url "http://192.168.1.100:4747/video" --post-every 3

# Use lower resolution in DroidCam app settings
```

---

## 🎯 Recommended Setup for DroidCam

### Best Method: WiFi Mode

**Why?**
- More reliable frame reading
- No USB cable needed
- Usually better performance
- Works with any platform

**Steps:**
1. Connect phone to WiFi
2. Open DroidCam app
3. Note IP address (e.g., 192.168.1.100)
4. Test in browser: `http://192.168.1.100:4747/video`
5. If you see video, use that URL!

```bash
# Example command
python face_detector_real.py \
    --camera-url "http://192.168.1.100:4747/video" \
    --fps 20 \
    --whitelist-dir ./whitelist
```

---

## 📝 Quick Commands

### Test Connection
```bash
cd scripts
python test_droidcam.py
```

### USB Mode (Camera Index 0)
```bash
python face_detector_real.py --camera-index 0 --droidcam-usb
```

### USB Mode (Camera Index 1)
```bash
python face_detector_real.py --camera-index 1 --droidcam-usb
```

### WiFi Mode
```bash
# Replace with YOUR phone's IP!
python face_detector_real.py --camera-url "http://192.168.1.100:4747/video"
```

### With Face Recognition
```bash
python face_detector_real.py \
    --camera-url "http://192.168.1.100:4747/video" \
    --whitelist-dir ./whitelist \
    --fps 20
```

---

## 🔍 Debug Mode

If you're still having issues, try this simple test:

```bash
# Create a simple test script
python -c "
import cv2
cap = cv2.VideoCapture(0)  # Try different numbers: 0, 1, 2...
print('Opened:', cap.isOpened())
ret, frame = cap.read()
print('Read frame:', ret)
if ret:
    cv2.imshow('Test', frame)
    cv2.waitKey(5000)
cap.release()
"
```

---

## 💡 Pro Tips

1. **WiFi is usually better than USB** for DroidCam
2. **Check IP in browser first**: Open `http://YOUR_IP:4747/video` in Chrome/Firefox
3. **Restart DroidCam app** if connection drops
4. **Keep phone plugged in** (DroidCam drains battery)
5. **Good lighting** helps face detection significantly

---

## 🆘 Still Not Working?

Try these in order:

1. **Run the tester:**
   ```bash
   python test_droidcam.py
   ```

2. **Test in browser:**
   Open `http://YOUR_PHONE_IP:4747/video` in web browser

3. **Check DroidCam app:**
   - Is it running?
   - What mode is selected?
   - What IP does it show?

4. **Try simple OpenCV test:**
   ```bash
   python -c "import cv2; cap=cv2.VideoCapture('http://192.168.1.100:4747/video'); print(cap.read()[0])"
   ```

5. **Check firewall:**
   - Temporarily disable firewall
   - Add exception for port 4747

---

## ✅ Success Indicators

You'll know it's working when:
- ✅ `test_droidcam.py` shows "Success!"
- ✅ You can see preview window with your face
- ✅ Terminal shows "FPS: X.X"
- ✅ No "failed to read frame" errors
- ✅ Bounding boxes appear in browser

---

**Need more help?** Run `python test_droidcam.py` and share the output!

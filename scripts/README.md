# DoggoBot Face Detection Scripts

This directory contains the face detection and recognition system for DoggoBot.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Check Your Setup
```bash
# Check GPU availability
python check_gpu.py

# Find available cameras
python find_camera.py
```

### 3. Run Face Detector
```bash
# Basic usage (CPU mode, no whitelist)
python face_detector_real.py --camera-index 0

# With whitelist (face recognition)
python face_detector_real.py --camera-index 0 --whitelist-dir /path/to/whitelist

# High performance (with GPU)
python face_detector_real.py --camera-index 0 --fps 60
```

## 📁 Files

| File | Description |
|------|-------------|
| `face_detector_real.py` | Main GPU-accelerated face detection system |
| `check_gpu.py` | GPU diagnostics and setup verification |
| `find_camera.py` | Camera detection utility |
| `face_recognition_integrated.py` | Legacy basic frame capture script |
| `detector_example.py` | Example detector for testing backend |
| `requirements.txt` | Python dependencies |

## 🎯 Recommended Scripts

**For production face detection:**
→ Use `face_detector_real.py` (GPU-accelerated, full features)

**For testing backend only:**
→ Use `detector_example.py` (simulated detections)

**For basic frame streaming:**
→ Use `face_recognition_integrated.py` (no face detection)

## 📚 Documentation

See main documentation:
- [FACE_DETECTION_SETUP.md](../FACE_DETECTION_SETUP.md)
- [GPU_ACCELERATION_GUIDE.md](../GPU_ACCELERATION_GUIDE.md)
- [GPU_AND_BOUNDING_BOXES_UPDATE.md](../GPU_AND_BOUNDING_BOXES_UPDATE.md)

## 💡 Examples

**Check if GPU is available:**
```bash
python check_gpu.py
```

**Find your camera:**
```bash
python find_camera.py
```

**Run with default settings:**
```bash
python face_detector_real.py
```

**Run with custom camera and FPS:**
```bash
python face_detector_real.py --camera-index 2 --fps 30
```

**Run with face recognition:**
```bash
python face_detector_real.py --whitelist-dir ./my_whitelist --fps 30
```

**Run headless (no preview window):**
```bash
python face_detector_real.py --no-preview
```

**Force CPU mode:**
```bash
python face_detector_real.py --no-gpu
```

## 🎓 Whitelist Setup

For face recognition, organize your whitelist like this:

```
whitelist/
├── Person_1/
│   ├── photo1.jpg
│   ├── photo2.jpg
│   └── photo3.jpg
├── Person_2/
│   └── photo.jpg
└── Person_3/
    ├── img1.jpg
    └── img2.jpg
```

- One folder per person
- Folder name = person's name
- 2-5 photos per person (more is better)
- Front-facing photos with good lighting

## ⚡ Performance Tips

**For best performance:**
1. Enable GPU acceleration (see GPU_ACCELERATION_GUIDE.md)
2. Use higher FPS (30-60) with GPU
3. Reduce `--post-every` to save bandwidth
4. Close other camera-using applications
5. Use good lighting for better detection

**CPU mode:**
- Use lower FPS (10-15)
- Post every 3rd frame (`--post-every 3`)
- Consider lower camera resolution

## 🔧 Troubleshooting

**Camera not found:**
```bash
python find_camera.py  # Find available cameras
```

**Low FPS:**
- Reduce `--fps` value
- Use `--post-every 3` to reduce load
- Enable GPU acceleration

**Face recognition not working:**
- Check whitelist directory structure
- Ensure photos contain clear faces
- Use multiple photos per person
- Verify good lighting in photos

**GPU not detected:**
```bash
python check_gpu.py  # Diagnose GPU issues
```

**Import errors:**
```bash
pip install -r requirements.txt  # Reinstall dependencies
```

## 📝 Notes

- The system automatically uses GPU if available
- Default API endpoint: `http://localhost:8000`
- Default API key: `doggobot-secret-key-change-me`
- Default camera: index 0
- Default FPS: 30

## 🆘 Need Help?

Check the full documentation:
- [FACE_DETECTION_SETUP.md](../FACE_DETECTION_SETUP.md) - Complete setup guide
- [GPU_ACCELERATION_GUIDE.md](../GPU_ACCELERATION_GUIDE.md) - GPU setup
- [QUICK_START.md](../QUICK_START.md) - General DoggoBot setup

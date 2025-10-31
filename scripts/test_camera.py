#!/usr/bin/env python3
"""
Test camera setup - verify which camera indices work
"""

import cv2
import argparse

def test_camera(index):
    """Test if camera at given index works"""
    print(f"\n📹 Testing camera index {index}...")
    
    cap = cv2.VideoCapture(index)
    
    if not cap.isOpened():
        print(f"   ❌ Could not open camera at index {index}")
        return False
    
    # Get camera properties
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"   ✅ Camera opened successfully!")
    print(f"   Resolution: {int(width)}x{int(height)}")
    print(f"   FPS: {int(fps) if fps > 0 else 'Unknown'}")
    
    # Try to read a frame
    ret, frame = cap.read()
    if ret:
        print(f"   ✅ Successfully captured frame")
        
        # Show preview for 3 seconds
        print(f"   Showing preview for 3 seconds (press 'q' to skip)...")
        cv2.imshow(f'Camera {index} Preview', frame)
        
        # Wait for 3 seconds or 'q' key
        key = cv2.waitKey(3000)
        cv2.destroyAllWindows()
        
        if key == ord('q'):
            print(f"   Skipped by user")
    else:
        print(f"   ⚠️  Could not capture frame")
    
    cap.release()
    return True


def main():
    parser = argparse.ArgumentParser(description="Test camera setup")
    parser.add_argument('--index', type=int, help='Test specific camera index')
    parser.add_argument('--all', action='store_true', help='Test all camera indices (0-10)')
    
    args = parser.parse_args()
    
    print("🎥 DoggoBot Camera Tester")
    print("=" * 50)
    
    if args.index is not None:
        test_camera(args.index)
    elif args.all:
        print("\nScanning camera indices 0-10...")
        found = []
        for i in range(11):
            if test_camera(i):
                found.append(i)
        
        print("\n" + "=" * 50)
        print(f"\n✅ Found {len(found)} working camera(s): {found}")
        if found:
            print(f"\nTo use camera {found[0]} with the detector, run:")
            print(f"   python face_detector_real.py --camera-index {found[0]}")
    else:
        # Test common indices
        print("\nTesting common camera indices...")
        for i in [0, 1, 2]:
            test_camera(i)
        
        print("\n" + "=" * 50)
        print("\nTip: Use --all to test all camera indices 0-10")
        print("     Use --index N to test a specific camera")


if __name__ == "__main__":
    main()

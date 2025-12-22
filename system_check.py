"""
System Check Script - Verify Your PC is Ready
Tests: Camera, Dependencies, Performance
"""

import sys
import time

print("=" * 70)
print("   SYSTEM READINESS CHECK - 3D Gesture Cube Controller")
print("=" * 70)
print()

# Test 1: Python Version
print("1. Checking Python version...")
python_version = sys.version_info
print(f"   Python {python_version.major}.{python_version.minor}.{python_version.micro}")
if python_version.major == 3 and python_version.minor >= 8 and python_version.minor <= 12:
    print("   ✅ Python version is compatible!")
else:
    print("   ⚠️  Warning: Recommended Python 3.8-3.12")
print()

# Test 2: Import Libraries
print("2. Checking required libraries...")
missing = []

try:
    import cv2
    print(f"   ✅ OpenCV {cv2.__version__}")
except ImportError:
    print("   ❌ OpenCV not found")
    missing.append("opencv-python")

try:
    import mediapipe as mp
    print(f"   ✅ MediaPipe {mp.__version__}")
except ImportError:
    print("   ❌ MediaPipe not found")
    missing.append("mediapipe")

try:
    import numpy as np
    print(f"   ✅ NumPy {np.__version__}")
except ImportError:
    print("   ❌ NumPy not found")
    missing.append("numpy")

if missing:
    print()
    print("   ⚠️  Missing libraries. Install with:")
    print(f"   pip install {' '.join(missing)}")
    print()
    sys.exit(1)

print()

# Test 3: Camera Check
print("3. Checking camera access...")
try:
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            h, w = frame.shape[:2]
            print(f"   ✅ Camera opened successfully!")
            print(f"   Resolution: {w}x{h}")
        else:
            print("   ❌ Camera opened but cannot read frames")
        cap.release()
    else:
        print("   ❌ Cannot open camera")
        print("   Troubleshooting:")
        print("      - Check if another app is using camera")
        print("      - Try CAMERA_INDEX = 1 in config.py")
        print("      - Check Windows Camera permissions")
except Exception as e:
    print(f"   ❌ Camera error: {e}")

print()

# Test 4: MediaPipe Hand Detection
print("4. Testing MediaPipe hand detection...")
try:
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        model_complexity=0,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.5
    )
    print("   ✅ MediaPipe initialized successfully!")
    print("   Model: Lite (Complexity 0) - Optimized for 7GB RAM")
    hands.close()
except Exception as e:
    print(f"   ❌ MediaPipe error: {e}")

print()

# Test 5: Performance Estimate
print("5. Estimating performance...")
import psutil
import platform

# Get system info
cpu_count = psutil.cpu_count(logical=False)
ram_gb = psutil.virtual_memory().total / (1024**3)
ram_available = psutil.virtual_memory().available / (1024**3)

print(f"   CPU Cores: {cpu_count}")
print(f"   Total RAM: {ram_gb:.1f} GB")
print(f"   Available RAM: {ram_available:.1f} GB")
print(f"   OS: {platform.system()} {platform.release()}")

# Performance prediction
if ram_available >= 2.0 and cpu_count >= 1:
    print("   ✅ Expected FPS: 25-30 (SMOOTH)")
elif ram_available >= 1.5:
    print("   ⚠️  Expected FPS: 20-25 (GOOD)")
else:
    print("   ❌ Warning: Low available RAM")
    print("      Close other applications before running")

print()

# Test 6: Frame Processing Speed Test
print("6. Running performance test...")
try:
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        model_complexity=0,
        min_detection_confidence=0.6
    )
    
    times = []
    print("   Testing 30 frames...", end="", flush=True)
    
    for i in range(30):
        start = time.time()
        ret, frame = cap.read()
        if ret:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)
        elapsed = time.time() - start
        times.append(elapsed)
        if i % 10 == 0:
            print(".", end="", flush=True)
    
    print(" Done!")
    
    avg_time = sum(times) / len(times)
    estimated_fps = 1.0 / avg_time if avg_time > 0 else 0
    
    print(f"   Average frame time: {avg_time*1000:.1f}ms")
    print(f"   Estimated FPS: {estimated_fps:.1f}")
    
    if estimated_fps >= 25:
        print("   ✅ Performance: EXCELLENT")
    elif estimated_fps >= 20:
        print("   ✅ Performance: GOOD")
    elif estimated_fps >= 15:
        print("   ⚠️  Performance: ACCEPTABLE")
    else:
        print("   ❌ Performance: LOW - Close background apps")
    
    cap.release()
    hands.close()
    
except Exception as e:
    print(f"   ❌ Performance test failed: {e}")

print()

# Final Summary
print("=" * 70)
print("   SYSTEM CHECK COMPLETE")
print("=" * 70)
print()
print("✅ If all checks passed, you're ready to run:")
print("   python simple_cube_control.py")
print()
print("   or double-click: run_optimized.bat")
print()
print("=" * 70)

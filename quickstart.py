"""
Quick Start Script
Run this to verify your installation and test the system
"""

import sys
import subprocess

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(text.center(60))
    print("=" * 60 + "\n")

def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    print(f"  Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("  ✗ Python 3.8+ required")
        return False
    
    print("  ✓ Python version OK")
    return True

def check_dependencies():
    """Check if all dependencies are installed"""
    print("\nChecking dependencies...")
    
    required = [
        ("cv2", "opencv-python"),
        ("mediapipe", "mediapipe"),
        ("numpy", "numpy"),
        ("flask", "flask")
    ]
    
    missing = []
    
    for module, package in required:
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} not found")
            missing.append(package)
    
    if missing:
        print(f"\n  Missing packages: {', '.join(missing)}")
        print("  Run: pip install -r requirements.txt")
        return False
    
    return True

def test_camera():
    """Test camera access"""
    print("\nTesting camera access...")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("  ✗ Could not open camera")
            print("    - Check camera permissions")
            print("    - Try changing CAMERA_INDEX in config.py")
            return False
        
        ret, frame = cap.read()
        if not ret:
            print("  ✗ Could not read from camera")
            cap.release()
            return False
        
        cap.release()
        print("  ✓ Camera OK")
        return True
    
    except Exception as e:
        print(f"  ✗ Camera test failed: {e}")
        return False

def test_mediapipe():
    """Test MediaPipe hands"""
    print("\nTesting MediaPipe Hands...")
    
    try:
        import mediapipe as mp
        import cv2
        import numpy as np
        
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
            static_image_mode=True,
            max_num_hands=1,
            min_detection_confidence=0.5
        )
        
        # Create test image
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        results = hands.process(test_image)
        
        hands.close()
        print("  ✓ MediaPipe OK")
        return True
    
    except Exception as e:
        print(f"  ✗ MediaPipe test failed: {e}")
        return False

def test_flask():
    """Test Flask"""
    print("\nTesting Flask...")
    
    try:
        from flask import Flask
        app = Flask(__name__)
        print("  ✓ Flask OK")
        return True
    
    except Exception as e:
        print(f"  ✗ Flask test failed: {e}")
        return False

def main():
    """Run all checks"""
    print_header("GESTURE EARTH CONTROL - QUICK START")
    
    print("This script will verify your installation.\n")
    
    all_ok = True
    
    # Run checks
    all_ok &= check_python_version()
    all_ok &= check_dependencies()
    all_ok &= test_camera()
    all_ok &= test_mediapipe()
    all_ok &= test_flask()
    
    # Summary
    print_header("SUMMARY")
    
    if all_ok:
        print("✓ All checks passed!")
        print("\nYou're ready to run the application:")
        print("\n    python main.py\n")
        print("Controls:")
        print("  - Show your hand to the camera")
        print("  - Perform gestures (pinch, swipe, tap, palm)")
        print("  - Press 'Q' to quit")
        print("  - Press 'H' for help")
    else:
        print("✗ Some checks failed.")
        print("\nPlease fix the issues above and run this script again.")
        print("\nCommon fixes:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Check camera permissions")
        print("  3. Update Python to 3.8+")
    
    print_header("END")

if __name__ == "__main__":
    main()

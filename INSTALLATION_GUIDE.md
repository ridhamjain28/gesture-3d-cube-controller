# Step-by-Step Installation and Setup Guide

## System Requirements

### Minimum Requirements
- **CPU**: Dual-core processor (2.0 GHz+)
- **RAM**: 4 GB
- **Webcam**: Any USB or integrated camera
- **OS**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Browser**: Chrome 90+, Firefox 88+, or Edge 90+

### Recommended Requirements
- **CPU**: Quad-core processor (2.5 GHz+)
- **RAM**: 8 GB
- **Webcam**: 720p or higher resolution
- **GPU**: Integrated graphics or better

## Step 1: Install Python

### Windows

1. Download Python 3.8+ from [python.org](https://www.python.org/downloads/)
2. Run installer
3. **Important**: Check "Add Python to PATH"
4. Click "Install Now"
5. Verify installation:
   ```bash
   python --version
   pip --version
   ```

### macOS

Using Homebrew:
```bash
brew install python@3.11
python3 --version
pip3 --version
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3 python3-pip
python3 --version
pip3 --version
```

## Step 2: Set Up Project

### Option A: Download Files

1. Download all project files to a folder named `gesture-earth-control`
2. Open terminal/command prompt
3. Navigate to project directory:
   ```bash
   cd path\to\gesture-earth-control
   ```

### Option B: Using Git (if you have files in repository)

```bash
git clone <repository-url>
cd gesture-earth-control
```

## Step 3: Create Virtual Environment (Recommended)

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

## Step 4: Install Dependencies

With virtual environment activated:

```bash
pip install -r requirements.txt
```

This installs:
- opencv-python (computer vision)
- mediapipe (hand tracking)
- numpy (numerical computing)
- flask (web server)
- selenium (browser automation, optional)
- pyautogui (GUI automation, optional)

### Installation Progress

You'll see output like:
```
Collecting opencv-python==4.8.1.78
  Downloading opencv_python-4.8.1.78-cp311-cp311-win_amd64.whl (38.1 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 38.1/38.1 MB 10.2 MB/s eta 0:00:00
...
Successfully installed opencv-python-4.8.1.78 mediapipe-0.10.8 ...
```

### Troubleshooting Installation

**Issue: pip not found**
```bash
# Windows
python -m pip install --upgrade pip

# macOS/Linux
python3 -m pip install --upgrade pip
```

**Issue: Permission denied (Linux/macOS)**
```bash
pip install --user -r requirements.txt
```

**Issue: Slow download**
```bash
pip install -r requirements.txt --timeout 1000
```

## Step 5: Verify Installation

Test that key libraries work:

```bash
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "import mediapipe; print('MediaPipe:', mediapipe.__version__)"
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "import flask; print('Flask:', flask.__version__)"
```

Expected output:
```
OpenCV: 4.8.1
MediaPipe: 0.10.8
NumPy: 1.24.3
Flask: 3.0.0
```

## Step 6: Configure Camera

### Test Camera Access

Run this test script:

```bash
python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera FAIL'); cap.release()"
```

If you see "Camera FAIL":

1. **Check permissions**: Allow camera access in system settings
2. **Try different index**: Edit `config.py`, change `CAMERA_INDEX = 0` to `1` or `2`
3. **Close other apps**: Ensure no other program is using camera

### Configure Settings

Edit `config.py` to match your setup:

```python
# Camera settings
CAMERA_INDEX = 0  # Change if default camera fails
FRAME_WIDTH = 1280  # Lower if performance is poor (try 640)
FRAME_HEIGHT = 720  # Lower if performance is poor (try 480)

# Performance
MODEL_COMPLEXITY = 1  # Set to 0 for faster processing
```

## Step 7: Get Cesium Access Token (Optional)

For enhanced Earth imagery:

1. Go to [https://cesium.com/ion/signup](https://cesium.com/ion/signup)
2. Create free account
3. Navigate to "Access Tokens"
4. Copy your default token
5. Edit `config.py`:
   ```python
   CESIUM_ACCESS_TOKEN = "your_token_here"
   ```

**Note**: The system works without a token using default imagery.

## Step 8: First Run

### Test Hand Tracking

Test just the hand tracker:

```bash
python hand_tracker.py
```

You should see:
- Camera window opens
- Your hand is detected with green landmarks
- FPS counter shows frame rate
- Press 'q' to quit

### Test Gesture Recognition

```bash
python gesture_recognizer.py
```

Perform gestures and see them detected in real-time.

### Run Full Application

```bash
python main.py
```

What happens:
1. Camera window opens
2. Browser opens with Earth visualization
3. System waits for hand gestures
4. Perform gestures to control Earth

## Step 9: Calibration (If Needed)

If gestures aren't detected well, adjust `config.py`:

### Too Sensitive

```python
PINCH_CLOSE_THRESHOLD = 20  # Decrease (was 30)
SWIPE_THRESHOLD = 150  # Increase (was 100)
GESTURE_COOLDOWN = 0.8  # Increase (was 0.5)
DEBOUNCE_FRAMES = 3  # Increase (was 2)
```

### Not Sensitive Enough

```python
PINCH_CLOSE_THRESHOLD = 40  # Increase (was 30)
SWIPE_THRESHOLD = 80  # Decrease (was 100)
DETECTION_CONFIDENCE = 0.5  # Decrease (was 0.7)
DEBOUNCE_FRAMES = 1  # Decrease (was 2)
```

### Low FPS

```python
FRAME_WIDTH = 640  # Reduce resolution
FRAME_HEIGHT = 480
MODEL_COMPLEXITY = 0  # Use lite model
SMOOTHING_WINDOW = 3  # Reduce smoothing
```

## Step 10: Testing Best Practices

### Optimal Environment

1. **Lighting**: Bright, even illumination
2. **Background**: Plain, contrasting with hand
3. **Distance**: 30-60 cm from camera
4. **Position**: Center hand in frame

### Hand Positioning

- Keep hand flat and visible
- Avoid occlusion (fingers blocking each other)
- Move smoothly, not jerkily
- Pause briefly between gestures

### Gesture Tips

**Pinch**:
- Start with fingers apart (5+ cm)
- Bring thumb and index together
- Separate smoothly to zoom in

**Swipe**:
- Open palm, fingers together
- Move hand horizontally/vertically
- Keep movement smooth and quick

**Tap**:
- Extend index finger
- Quick forward motion toward camera
- Pull back

**Palm Open/Close**:
- Fully extend all fingers for "open"
- Curl all fingers to fist for "close"

## Common Issues and Solutions

### Issue: Camera Permission Denied

**Windows**:
1. Settings → Privacy → Camera
2. Enable "Allow apps to access camera"
3. Enable for Python

**macOS**:
1. System Preferences → Security & Privacy → Camera
2. Check box for Terminal/Python

**Linux**:
```bash
sudo usermod -a -G video $USER
```
Then log out and back in.

### Issue: Browser Doesn't Open

- Manually open: `http://127.0.0.1:5000`
- Check firewall settings
- Try different browser

### Issue: Poor Detection

1. Improve lighting
2. Use plain background
3. Lower confidence thresholds
4. Adjust camera angle

### Issue: High CPU Usage

1. Reduce frame resolution
2. Set `MODEL_COMPLEXITY = 0`
3. Close other applications
4. Limit FPS: `FPS_TARGET = 15`

### Issue: Gestures Not Mapped

1. Check `config.py` - gesture must be enabled
2. Verify gesture performed correctly
3. Check console for logged gestures
4. Increase sensitivity thresholds

## Keyboard Shortcuts

While application is running:

- **Q**: Quit application
- **R**: Reset Earth view
- **H**: Show help/instructions
- **M**: Show gesture mappings

## Next Steps

1. Read [GESTURE_GUIDE.md](GESTURE_GUIDE.md) for detailed gesture instructions
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) to understand system
3. See [EXTENDING.md](EXTENDING.md) to add custom gestures

## Uninstallation

To remove the project:

1. Deactivate virtual environment:
   ```bash
   deactivate
   ```

2. Delete project folder:
   ```bash
   # Windows
   rmdir /s gesture-earth-control
   
   # macOS/Linux
   rm -rf gesture-earth-control
   ```

## Getting Help

If you encounter issues:

1. Check console output for error messages
2. Enable debug mode: `DEBUG_MODE = True` in `config.py`
3. Test components individually (hand_tracker.py, gesture_recognizer.py)
4. Review troubleshooting section above

## System Verification Checklist

Before first run, verify:

- [ ] Python 3.8+ installed
- [ ] All dependencies installed (`pip list`)
- [ ] Camera accessible
- [ ] Virtual environment activated (if using)
- [ ] config.py settings appropriate
- [ ] Adequate lighting setup
- [ ] No other apps using camera

If all checked, you're ready to run!

```bash
python main.py
```

Enjoy controlling the Earth with your hands! 🌍✋

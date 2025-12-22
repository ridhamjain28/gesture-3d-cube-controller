# 🚀 GETTING STARTED - Quick Reference

## What You Have

A complete gesture-controlled Earth navigation system with:

✅ Hand tracking (MediaPipe)
✅ Gesture recognition (Pinch, Swipe, Tap, Palm)
✅ 3D Earth visualization (CesiumJS)
✅ Real-time control (30+ FPS)
✅ Full documentation
✅ Extensible architecture

## File Structure

```
D:\Img projecy\
├── Core Application Files
│   ├── main.py                    # Run this to start!
│   ├── hand_tracker.py           # Hand detection & tracking
│   ├── gesture_recognizer.py     # Gesture classification
│   ├── gesture_mapper.py         # Gesture-to-action mapping
│   ├── earth_controller.py       # Earth visualization control
│   ├── config.py                 # All configuration settings
│   └── utils.py                  # Helper functions
│
├── Setup & Installation
│   ├── requirements.txt          # Python dependencies
│   ├── quickstart.py            # Installation verifier
│   ├── setup_project.bat        # Windows setup script
│   └── gesture_earth_setup.py   # Directory creator
│
├── Documentation
│   ├── PROJECT_README.md         # Complete project guide
│   ├── INSTALLATION_GUIDE.md    # Step-by-step setup
│   ├── ARCHITECTURE.md          # System design
│   ├── GESTURE_GUIDE.md         # How to perform gestures
│   └── gesture-earth-control-README.md  # Quick reference
│
└── This File
    └── GETTING_STARTED.md        # You are here!
```

## Installation (3 Steps)

### Step 1: Install Python Packages

```bash
pip install opencv-python mediapipe numpy flask
```

Or use requirements file:
```bash
pip install -r requirements.txt
```

### Step 2: Verify Installation

```bash
python quickstart.py
```

This checks:
- ✅ Python version (3.8+)
- ✅ All dependencies installed
- ✅ Camera access working
- ✅ MediaPipe functional

### Step 3: Run Application

```bash
python main.py
```

That's it! 🎉

## What Happens When You Run

1. **Camera Window Opens**
   - Shows your webcam feed
   - Green dots on your hand (landmarks)
   - FPS counter in corner
   - Gesture labels displayed

2. **Browser Opens**
   - Shows 3D Earth (CesiumJS)
   - Info panel with coordinates
   - Gesture feedback overlay

3. **You Control Earth**
   - Show hand to camera
   - Perform gestures
   - See Earth respond in real-time

## Gestures (Quick Reference)

| Gesture | How To | What It Does |
|---------|--------|--------------|
| 🤏 Pinch In | Fingers together | Zoom Out |
| 🤏 Pinch Out | Fingers apart | Zoom In |
| 👈 Swipe Left | Move hand left | Rotate Left |
| 👉 Swipe Right | Move hand right | Rotate Right |
| 👆 Swipe Up | Move hand up | Tilt Up |
| 👇 Swipe Down | Move hand down | Tilt Down |
| 👆 Tap | Quick push forward | Select |
| ✋ Palm Open | Spread fingers | Reset View |

## Keyboard Controls

- **Q** - Quit
- **R** - Reset view
- **H** - Help
- **M** - Show mappings

## Testing Individual Components

Test each part separately:

### Test Camera Only
```bash
python -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'FAIL')"
```

### Test Hand Tracking
```bash
python hand_tracker.py
```
- Shows camera with hand landmarks
- Press 'Q' to quit

### Test Gesture Recognition
```bash
python gesture_recognizer.py
```
- Perform gestures
- See detection in console
- Press 'Q' to quit

### Test Earth Visualization
```bash
python earth_controller.py
```
- Opens browser with Earth
- Tests camera controls
- Press Ctrl+C to stop

## Common First-Run Issues

### "No module named cv2"
**Solution**: `pip install opencv-python`

### "No module named mediapipe"
**Solution**: `pip install mediapipe`

### "Could not open camera"
**Solutions**:
1. Check camera permissions (Settings → Privacy → Camera)
2. Close other apps using camera (Zoom, Skype, etc.)
3. Try different camera: Change `CAMERA_INDEX` in `config.py` (0, 1, 2)

### Browser doesn't open
**Solutions**:
1. Manually open: http://127.0.0.1:5000
2. Check firewall
3. Wait a few seconds after camera opens

### Gestures not detected
**Solutions**:
1. Improve lighting (bright, even light)
2. Use plain background
3. Keep hand 30-60cm from camera
4. Lower thresholds in `config.py`

## Configuration Quick Tweaks

Edit `config.py` to customize:

### Make Gestures More Sensitive
```python
PINCH_CLOSE_THRESHOLD = 40      # Increase from 30
SWIPE_THRESHOLD = 80            # Decrease from 100
GESTURE_COOLDOWN = 0.3          # Decrease from 0.5
DEBOUNCE_FRAMES = 1             # Decrease from 2
```

### Make Gestures Less Sensitive
```python
PINCH_CLOSE_THRESHOLD = 20      # Decrease from 30
SWIPE_THRESHOLD = 150           # Increase from 100
GESTURE_COOLDOWN = 0.8          # Increase from 0.5
DEBOUNCE_FRAMES = 3             # Increase from 2
```

### Improve Performance (Speed)
```python
FRAME_WIDTH = 640               # Decrease from 1280
FRAME_HEIGHT = 480              # Decrease from 720
MODEL_COMPLEXITY = 0            # Change from 1
MAX_HANDS = 1                   # Ensure it's 1
```

### Improve Accuracy (Quality)
```python
DETECTION_CONFIDENCE = 0.8      # Increase from 0.7
TRACKING_CONFIDENCE = 0.7       # Increase from 0.5
SMOOTHING_WINDOW = 7            # Increase from 5
MODEL_COMPLEXITY = 1            # Ensure it's 1
```

## Tips for Best Results

### Lighting
- ✅ Bright, even lighting
- ✅ Light source in front or side
- ❌ Avoid backlighting (window behind you)
- ❌ Avoid harsh shadows

### Background
- ✅ Plain, solid color
- ✅ Contrasts with skin tone
- ❌ Cluttered background
- ❌ Moving objects behind

### Hand Position
- ✅ Center of frame
- ✅ 30-60 cm from camera
- ✅ Palm facing camera
- ✅ All fingers visible
- ❌ Too close (fills frame)
- ❌ Too far (too small)
- ❌ Angled away from camera

### Gesture Technique
- ✅ Smooth, deliberate movements
- ✅ Pause between gestures
- ✅ Hold position briefly
- ❌ Rushed movements
- ❌ Continuous rapid gestures

## Next Steps

### 1. Master Basic Gestures
- Practice pinch zoom
- Practice swipe navigation
- Get comfortable with tap
- Try palm reset

### 2. Customize Configuration
- Adjust thresholds to your preference
- Set comfortable sensitivity
- Optimize for your camera/lighting

### 3. Explore Code
- Read `hand_tracker.py` comments
- Understand gesture math in `gesture_recognizer.py`
- See how actions map in `gesture_mapper.py`

### 4. Extend System
- Add your own gestures
- Create custom actions
- Modify Earth controls
- Experiment with new features

## Documentation Guide

**Start Here** (You are here!)
- `GETTING_STARTED.md` - Quick setup

**For Installation Help**
- `INSTALLATION_GUIDE.md` - Detailed setup steps

**For Using System**
- `GESTURE_GUIDE.md` - Complete gesture reference
- `PROJECT_README.md` - Full project overview

**For Understanding System**
- `ARCHITECTURE.md` - System design deep dive

**For Modifying System**
- Code comments in each .py file
- `config.py` - All parameters explained

## Quick Commands Reference

```bash
# Run application
python main.py

# Test installation
python quickstart.py

# Test individual components
python hand_tracker.py
python gesture_recognizer.py
python earth_controller.py

# Install dependencies
pip install -r requirements.txt

# Update a package
pip install --upgrade opencv-python

# Check installed versions
pip list | grep -E "opencv|mediapipe|numpy|flask"
```

## Debug Mode

Enable verbose logging in `config.py`:

```python
DEBUG_MODE = True           # Print detailed logs
LOG_GESTURES = True         # Log detected gestures
LOG_LANDMARKS = True        # Log hand coordinates (very verbose)
SHOW_FPS = True            # Show frame rate
SHOW_GESTURE_HISTORY = True # Show last 5 gestures
```

## Performance Monitoring

Check performance while running:

```python
# In config.py
ENABLE_PROFILING = True     # Track function timing
SHOW_FPS = True            # Display FPS counter
```

Watch console output for timing information.

## Getting Help

If you get stuck:

1. ✅ Check error message in console
2. ✅ Review troubleshooting sections in docs
3. ✅ Test components individually
4. ✅ Enable debug mode
5. ✅ Verify camera/lighting setup
6. ✅ Check configuration values

## Example Session

```
$ python main.py

============================================================
    GESTURE-CONTROLLED EARTH NAVIGATION SYSTEM
============================================================

Initializing components...
[HandTracker] Initialized with:
  - Detection confidence: 0.7
  - Tracking confidence: 0.5
  - Model complexity: 1
  - Max hands: 1
[GestureRecognizer] Initialized
[GestureMapper] Initialized with default mappings
[EarthController] Initialized

============================================================
                  STARTING APPLICATION
============================================================

Opening camera 0...
✓ Camera opened: 1280x720

Starting Earth visualization...
[EarthController] Opening browser: http://127.0.0.1:5000
[EarthController] Server started

✓ System ready! Waiting for hand gestures...

[Gesture] Gesture(pinch_out, conf=0.90)
[EarthController] Action: zoom_in | Params: {'factor': 1.2}

[Gesture] Gesture(swipe_left, conf=0.80)
[EarthController] Action: rotate_left | Params: {'amount': 30.0}

...
```

## Success Checklist

Before considering setup complete:

- [ ] Camera opens and shows video
- [ ] Hand detected with green landmarks
- [ ] Browser opens with Earth
- [ ] Pinch gesture zooms Earth
- [ ] Swipe gesture rotates Earth
- [ ] FPS shows 25+ frames per second
- [ ] No error messages in console

If all checked, **you're ready to explore!** 🚀

---

## Summary

You now have:
1. ✅ Complete gesture control system
2. ✅ All source code (well-documented)
3. ✅ Comprehensive documentation
4. ✅ Working examples and tests
5. ✅ Configuration options
6. ✅ Troubleshooting guides

**Just run:** `python main.py`

**Have fun controlling Earth with your hands!** 🌍✋

---

*For detailed information, see the documentation files listed above.*

*Built for learning, experimentation, and fun!*

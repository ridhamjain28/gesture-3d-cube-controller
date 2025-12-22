# Gesture Guide

Complete reference for performing gestures and understanding their mathematical detection.

## Quick Reference

| Gesture | Motion | Action | Key |
|---------|--------|--------|-----|
| 🤏 Pinch In | Bring fingers together | Zoom Out | Thumb+Index < 30px |
| 🤏 Pinch Out | Separate fingers | Zoom In | Thumb+Index > 100px |
| 👈 Swipe Left | Move hand left | Rotate Left | Displacement > 100px |
| 👉 Swipe Right | Move hand right | Rotate Right | Displacement > 100px |
| 👆 Swipe Up | Move hand up | Tilt Up | Displacement > 100px |
| 👇 Swipe Down | Move hand down | Tilt Down | Displacement > 100px |
| 👆 Tap | Quick forward push | Select/Click | Z-change < -0.05 |
| ✋ Palm Open | Extend all fingers | Reset View | Fingers spread |
| ✊ Palm Close | Make fist | Pause/Toggle | Fingers curled |

## Detailed Gesture Descriptions

### 1. Pinch Zoom

The pinch gesture uses the distance between thumb tip and index fingertip.

#### Pinch In (Zoom Out)

**How to perform**:
1. Start with thumb and index finger separated (3-5 cm)
2. Smoothly bring them together
3. Stop when fingertips are almost touching
4. Separate again to repeat

**What the system detects**:
```
Distance = √[(thumb_x - index_x)² + (thumb_y - index_y)²]

When Distance < 30 pixels:
  - State changes from "open" to "closed"
  - Triggers PINCH_IN gesture
  - Earth zooms out (altitude increases)
```

**Mathematical formula**:
```
new_altitude = current_altitude × zoom_factor
where zoom_factor = 1.2 (default)
```

**Tips**:
- Keep hand steady, move only fingers
- Don't pinch too fast (debouncing may block)
- Ensure both fingertips are visible
- Maintain distance from camera

**Common issues**:
- *Fingers too far*: Increase PINCH_CLOSE_THRESHOLD in config
- *Too sensitive*: Decrease threshold
- *Not detected*: Improve lighting, ensure clear view

#### Pinch Out (Zoom In)

**How to perform**:
1. Start with thumb and index together (pinched)
2. Smoothly separate them
3. Maintain 5+ cm distance
4. Bring together to repeat

**Detection**:
```
When Distance > 100 pixels:
  - State changes from "closed" to "open"
  - Triggers PINCH_OUT gesture
  - Earth zooms in (altitude decreases)
```

**Configuration**:
```python
# In config.py
PINCH_CLOSE_THRESHOLD = 30   # Pixels for "closed"
PINCH_OPEN_THRESHOLD = 100   # Pixels for "open"
PINCH_ZOOM_SPEED = 0.5       # Sensitivity multiplier
```

---

### 2. Swipe Gestures

Swipe gestures detect hand movement in a specific direction.

#### Swipe Left (Rotate Left)

**How to perform**:
1. Open hand with palm facing camera
2. Position hand at right side of frame
3. Quickly move hand to left
4. Maintain smooth, straight motion

**Detection algorithm**:
```
1. Track palm center over time (position history)
2. Calculate displacement vector:
   Δ = current_position - start_position
   
3. Compute magnitude:
   distance = |Δ| = √(Δx² + Δy²)
   
4. Compute velocity:
   velocity = distance / time_elapsed
   
5. Determine direction:
   If |Δx| > |Δy| AND Δx < 0:
      Gesture = SWIPE_LEFT
```

**Action**:
```
rotation_amount = distance × ROTATION_SENSITIVITY
Earth heading -= rotation_amount
```

**Tips**:
- Move entire hand, not just fingers
- Keep fingers together (open palm)
- Swift motion (velocity > 50 px/frame)
- Straight trajectory (not diagonal)

#### Swipe Right (Rotate Right)

Same as Swipe Left but moving right (Δx > 0).

#### Swipe Up (Tilt Up)

**How to perform**:
1. Open hand with palm facing camera
2. Position hand at bottom of frame
3. Quickly move hand upward
4. Maintain vertical trajectory

**Detection**:
```
If |Δy| > |Δx| AND Δy < 0:  # Y increases downward in image
   Gesture = SWIPE_UP
```

**Action**:
```
tilt_amount = distance × PAN_SENSITIVITY
Earth pitch -= tilt_amount  # Look more down at Earth
```

#### Swipe Down (Tilt Down)

Same as Swipe Up but moving down (Δy > 0).

**Configuration**:
```python
# In config.py
SWIPE_THRESHOLD = 100           # Minimum distance (pixels)
SWIPE_MIN_VELOCITY = 50         # Minimum speed (px/frame)
SWIPE_DIRECTION_TOLERANCE = 0.3 # Direction precision (0-1)
ROTATION_SENSITIVITY = 0.2      # Degrees per pixel
PAN_SENSITIVITY = 0.1           # Degrees per pixel
```

---

### 3. Tap Gesture

Tap detects forward motion of index finger using depth (Z-axis).

**How to perform**:
1. Extend index finger (point forward)
2. Curl other fingers slightly
3. Quick push toward camera
4. Pull back immediately

**Detection algorithm**:
```
1. Track index fingertip Z-coordinate (depth)
2. Calculate change from previous frame:
   Δz = current_z - previous_z
   
3. Detect forward motion (toward camera):
   If Δz < -TAP_Z_THRESHOLD:
      Gesture = TAP
```

**Z-coordinate interpretation**:
- Smaller Z = closer to camera
- Negative Δz = moving toward camera
- Positive Δz = moving away from camera

**Action**:
- Triggers "select" action
- Can be used to click on Earth locations
- Customizable for other interactions

**Tips**:
- Clear, quick motion
- Don't hold position (tap and release)
- Keep other fingers still
- Perpendicular to camera

**Configuration**:
```python
TAP_Z_THRESHOLD = 0.05      # Normalized Z-change
TAP_DURATION_MAX = 0.3      # Max tap duration (seconds)
TAP_COOLDOWN = 0.5          # Min time between taps
```

---

### 4. Palm Open

Palm Open detects a fully extended hand.

**How to perform**:
1. Extend all five fingers
2. Spread fingers apart
3. Face palm toward camera
4. Hold for brief moment

**Detection algorithm**:
```
1. Calculate palm center (average of wrist and knuckle bases)

2. For each fingertip:
   distance[i] = euclidean_distance(fingertip[i], palm_center)

3. Calculate average distance:
   avg_distance = mean(distance)

4. Normalize by hand size:
   hand_size = distance(wrist, middle_finger_base)
   normalized_distance = avg_distance / hand_size

5. Detect open hand:
   If normalized_distance > PALM_OPEN_THRESHOLD:
      State = "open"
```

**Action**:
- Resets Earth view to default position
- Returns to original lat/lon/altitude
- Smooth camera animation

**Tips**:
- Fully extend all fingers
- Spread fingers apart (not together)
- Keep hand flat
- Brief hold is sufficient

---

### 5. Palm Close

Palm Close detects a closed fist.

**How to perform**:
1. Curl all fingers into palm
2. Make tight fist
3. Face fist toward camera
4. Hold for brief moment

**Detection**:
```
If normalized_distance < PALM_CLOSE_THRESHOLD:
   State = "closed"
```

**Action**:
- Pause/resume functionality (optional)
- Can be customized for other actions
- Screenshot, mode toggle, etc.

**Configuration**:
```python
PALM_OPEN_THRESHOLD = 0.3   # Normalized distance for "open"
PALM_CLOSE_THRESHOLD = 0.1  # Normalized distance for "closed"
```

---

## Advanced Techniques

### Gesture Combinations (Future)

Plan for two-hand gestures:

- **Two-hand pinch**: Zoom with both hands
- **Two-hand spread**: Rotate with left/right hands
- **Grab and rotate**: Fist on one hand, open on other

### Continuous Gestures

Some gestures can be continuous (not discrete):

- **Continuous pinch**: Hold pinch and adjust distance for variable zoom
- **Continuous swipe**: Hold swipe for ongoing rotation

To enable: Set `GESTURE_COOLDOWN = 0` for specific gestures

### Gesture Confidence

Each gesture has a confidence score (0.0-1.0):

```python
GESTURE_CONFIDENCE_THRESHOLD = 0.6  # Minimum to accept
```

Higher threshold = fewer false positives, but harder detection

---

## Troubleshooting Gestures

### Gesture Not Detected

**Symptoms**: You perform gesture but nothing happens

**Solutions**:
1. Check lighting (bright, even)
2. Check hand visibility (all landmarks visible)
3. Lower detection confidence
4. Increase sensitivity (decrease thresholds)
5. Check console for logged gestures

**Debug commands**:
```python
# In config.py
DEBUG_MODE = True      # Enable verbose logging
LOG_GESTURES = True    # Log all detected gestures
SHOW_GESTURE_HISTORY = True  # Display history on screen
```

### False Positives

**Symptoms**: Gestures detected when not intended

**Solutions**:
1. Increase DEBOUNCE_FRAMES (require more consecutive detections)
2. Increase GESTURE_COOLDOWN (longer time between gestures)
3. Increase thresholds (stricter detection)
4. Improve hand stability

**Configuration**:
```python
DEBOUNCE_FRAMES = 4         # Increase from 2
GESTURE_COOLDOWN = 0.8      # Increase from 0.5
PINCH_CLOSE_THRESHOLD = 20  # Decrease for stricter
SWIPE_THRESHOLD = 150       # Increase for stricter
```

### Jittery Detection

**Symptoms**: Gesture detected multiple times, unstable

**Solutions**:
1. Increase SMOOTHING_WINDOW
2. Increase GESTURE_COOLDOWN
3. Use debouncing
4. Stabilize hand position

**Configuration**:
```python
SMOOTHING_WINDOW = 7       # Increase from 5
GESTURE_COOLDOWN = 1.0     # Longer cooldown
```

### Poor Accuracy

**Symptoms**: Swipes detected as wrong direction, pinch not precise

**Solutions**:
1. Perform gestures more deliberately
2. Improve lighting and background
3. Adjust direction tolerance
4. Calibrate thresholds for your hand size

**Calibration process**:
```bash
python tests/calibrate_camera.py
```

---

## Performance Optimization

### For Faster Detection

```python
MODEL_COMPLEXITY = 0        # Use lite model
SMOOTHING_WINDOW = 3        # Less smoothing
DEBOUNCE_FRAMES = 1         # Faster response
```

### For More Accurate Detection

```python
MODEL_COMPLEXITY = 1        # Use full model
SMOOTHING_WINDOW = 7        # More smoothing
DEBOUNCE_FRAMES = 3         # Stricter validation
DETECTION_CONFIDENCE = 0.8  # Higher confidence
```

---

## Practice Exercises

### Exercise 1: Pinch Precision

1. Start with fingers 10cm apart
2. Slowly pinch together
3. Note exact distance when detected
4. Practice consistent trigger

**Goal**: Trigger pinch at same distance every time

### Exercise 2: Swipe Control

1. Practice horizontal swipes (left/right)
2. Practice vertical swipes (up/down)
3. Ensure no diagonal detection
4. Vary speed and distance

**Goal**: 100% correct direction detection

### Exercise 3: Tap Timing

1. Practice quick tap motion
2. Vary distance from camera
3. Ensure consistent detection
4. Avoid false positives

**Goal**: Reliable tap without multiple triggers

### Exercise 4: Gesture Transitions

1. Pinch → Swipe → Tap → Palm sequence
2. Smooth transitions between gestures
3. No missed detections
4. No false positives

**Goal**: Fluid gesture control without errors

---

## Custom Gesture Configuration

Create personalized gesture profiles:

```python
# In config.py - Custom profile

# Profile 1: Sensitive (fast response)
if PROFILE == "sensitive":
    PINCH_CLOSE_THRESHOLD = 40
    SWIPE_THRESHOLD = 80
    GESTURE_COOLDOWN = 0.3
    DEBOUNCE_FRAMES = 1

# Profile 2: Precise (accurate detection)
elif PROFILE == "precise":
    PINCH_CLOSE_THRESHOLD = 25
    SWIPE_THRESHOLD = 120
    GESTURE_COOLDOWN = 0.7
    DEBOUNCE_FRAMES = 3

# Profile 3: Balanced (default)
else:
    PINCH_CLOSE_THRESHOLD = 30
    SWIPE_THRESHOLD = 100
    GESTURE_COOLDOWN = 0.5
    DEBOUNCE_FRAMES = 2
```

---

## Gesture Design Principles

When designing new gestures:

1. **Distinctiveness**: Each gesture should be clearly different
2. **Naturalness**: Should feel intuitive
3. **Reliability**: Should work consistently
4. **Comfort**: Should not cause hand strain
5. **Speed**: Should be quick to perform

---

## Accessibility Considerations

For users with limited hand mobility:

1. Adjust thresholds to require less movement
2. Enable alternative gesture mappings
3. Use larger detection zones
4. Reduce required gesture precision

```python
# Accessibility mode
PINCH_CLOSE_THRESHOLD = 50  # Easier pinch
SWIPE_THRESHOLD = 60        # Shorter swipes required
PALM_OPEN_THRESHOLD = 0.2   # Easier palm detection
```

---

## Summary

Master these gestures to fully control the Earth visualization:

✅ **Pinch**: Precise zoom control
✅ **Swipe**: Intuitive navigation
✅ **Tap**: Quick selection
✅ **Palm**: Mode control

Practice makes perfect! Experiment with different speeds, distances, and angles to find your optimal gesture style.

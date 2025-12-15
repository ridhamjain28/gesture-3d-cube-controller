# System Architecture

## Overview

The Gesture-Controlled Earth Navigation System is built on a modular architecture with clear separation of concerns. The system follows a pipeline pattern where data flows from camera input through hand tracking, gesture recognition, action mapping, and finally to Earth control.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     GESTURE EARTH CONTROL                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────────┐
         │         Main Application (main.py)      │
         │  - Initializes all components           │
         │  - Main processing loop                 │
         │  - User interface coordination          │
         └────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐     ┌──────────────┐      ┌──────────────┐
│   Camera     │     │    Config    │      │    Utils     │
│   Input      │     │   (config.py)│      │  (utils.py)  │
│   (OpenCV)   │     │              │      │              │
└──────────────┘     └──────────────┘      └──────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────┐
│              Hand Tracker (hand_tracker.py)               │
│  - MediaPipe Hands integration                            │
│  - 21-landmark detection per hand                         │
│  - Real-time tracking at 30+ FPS                          │
│  - Landmark smoothing and stabilization                   │
└──────────────────────────────────────────────────────────┘
        │
        │ Raw Landmarks (21 x (x,y,z))
        ▼
┌──────────────────────────────────────────────────────────┐
│          Gesture Recognizer (gesture_recognizer.py)       │
│  - Geometric gesture detection                            │
│  - Temporal gesture analysis                              │
│  - Debouncing and confidence filtering                    │
│  - Gesture types: Pinch, Swipe, Tap, Palm                 │
└──────────────────────────────────────────────────────────┘
        │
        │ Gesture Objects
        ▼
┌──────────────────────────────────────────────────────────┐
│           Gesture Mapper (gesture_mapper.py)              │
│  - Gesture-to-action translation                          │
│  - Parameter scaling and transformation                   │
│  - Enable/disable gesture control                         │
└──────────────────────────────────────────────────────────┘
        │
        │ Action Objects
        ▼
┌──────────────────────────────────────────────────────────┐
│         Earth Controller (earth_controller.py)            │
│  - Flask web server                                       │
│  - CesiumJS 3D Earth rendering                            │
│  - Camera control (zoom, rotate, tilt)                    │
│  - REST API for browser communication                     │
└──────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────┐
│                      Web Browser                          │
│  - CesiumJS viewer                                        │
│  - Real-time Earth visualization                          │
│  - Smooth camera animations                               │
└──────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Hand Tracker (`hand_tracker.py`)

**Purpose**: Detect and track hands in real-time video stream

**Key Technologies**:
- MediaPipe Hands (Google)
- OpenCV for video capture
- NumPy for numerical processing

**Key Features**:
- 21 landmark detection per hand
- 3D coordinates (x, y, z)
- Configurable confidence thresholds
- Smoothing to reduce jitter
- FPS monitoring

**Data Flow**:
- Input: BGR video frame (numpy array)
- Output: 21 landmarks (x, y, z), handedness (left/right)

**Mathematical Model**:
MediaPipe uses machine learning models trained on thousands of hand images to predict 21 keypoints representing hand anatomy.

### 2. Gesture Recognizer (`gesture_recognizer.py`)

**Purpose**: Classify hand poses and movements into meaningful gestures

**Gesture Detection Methods**:

#### A. Pinch Detection
```
Distance = sqrt((thumb_x - index_x)² + (thumb_y - index_y)²)

if Distance < PINCH_CLOSE_THRESHOLD:
    State = "closed" (Zoom Out)
elif Distance > PINCH_OPEN_THRESHOLD:
    State = "open" (Zoom In)
```

#### B. Swipe Detection
```
Displacement = Current_Position - Previous_Position
Velocity = Displacement / Time_Elapsed

if |Displacement| > SWIPE_THRESHOLD:
    Direction = atan2(dy, dx)
    Gesture = Swipe_Direction
```

#### C. Tap Detection
```
Z_Change = Current_Z - Previous_Z

if Z_Change < -TAP_THRESHOLD:
    Gesture = Tap
```

#### D. Palm Detection
```
Avg_Fingertip_Distance = mean(distance(fingertip, palm_center))
Normalized_Distance = Avg_Distance / Hand_Size

if Normalized_Distance > PALM_OPEN_THRESHOLD:
    State = "open"
else:
    State = "closed"
```

**Temporal Processing**:
- Position history buffer (deque)
- Debouncing (N consecutive frames required)
- Cooldown period between gestures
- State change detection

### 3. Gesture Mapper (`gesture_mapper.py`)

**Purpose**: Abstract layer between gesture recognition and Earth control

**Mapping Strategy**:
```
Gesture Type → Action Type + Parameters
```

**Examples**:
- `PINCH_IN` → `zoom_out(factor=1.2)`
- `SWIPE_LEFT` → `rotate_left(amount=distance*0.2)`
- `TAP` → `select(position="center")`

**Benefits**:
- Easy to modify gesture behavior
- Enable/disable gestures at runtime
- Scale gesture parameters
- Future: gesture combinations

### 4. Earth Controller (`earth_controller.py`)

**Purpose**: Control 3D Earth visualization in web browser

**Architecture**:
- Flask web server (Python backend)
- CesiumJS (JavaScript frontend)
- REST API for communication

**Communication Protocol**:
1. Python executes action → adds to queue
2. Browser polls `/api/actions` every 100ms
3. Browser receives actions → updates camera
4. Camera state synced back to Python

**Camera Model**:
- Position: (latitude, longitude, altitude)
- Orientation: (heading, pitch, roll)
- Smooth transitions with flyTo()

### 5. Configuration System (`config.py`)

**Purpose**: Centralized parameter management

**Configuration Categories**:
- Camera settings
- Hand tracking parameters
- Gesture thresholds
- Earth control settings
- Visualization options
- Debug flags

**Usage**:
```python
import config

# Read parameter
threshold = config.PINCH_CLOSE_THRESHOLD

# Update parameter
config.update_gesture_config("pinch_zoom_in", "sensitivity", 0.8)

# Check if gesture enabled
if config.is_gesture_enabled("swipe_left"):
    # Process gesture
```

## Data Flow Example

Let's trace a complete gesture through the system:

### User performs "Pinch Out" gesture:

1. **Camera captures frame** (640x480 BGR image)

2. **Hand Tracker**:
   - Converts BGR → RGB
   - Feeds to MediaPipe
   - Receives 21 landmarks
   - Smooths coordinates
   - Returns landmarks array

3. **Gesture Recognizer**:
   - Calculates thumb-index distance
   - Distance = 115 pixels (> 100 threshold)
   - Previous state was "closed"
   - Detects state transition → PINCH_OUT
   - Applies debouncing (2 consecutive frames)
   - Returns `Gesture(PINCH_OUT, confidence=0.9)`

4. **Gesture Mapper**:
   - Maps PINCH_OUT → zoom_in action
   - Retrieves config (factor=1.2, sensitivity=0.5)
   - Returns `Action("zoom_in", {factor: 1.2})`

5. **Earth Controller**:
   - Receives zoom_in action
   - Updates camera state: `altitude /= 1.2`
   - Queues camera update for browser
   - Browser polls, receives update
   - CesiumJS animates camera zoom

6. **Visual Feedback**:
   - Video frame shows "PINCH OUT" text
   - Browser shows gesture indicator
   - Info panel updates altitude value

## Performance Optimization

### Bottleneck Analysis

**Most expensive operations**:
1. MediaPipe hand detection (10-15ms per frame)
2. Video frame capture (5-10ms)
3. OpenCV rendering (2-5ms)

**Optimization strategies**:
1. Reduce camera resolution
2. Lower MediaPipe model complexity
3. Limit max_hands to 1
4. Use frame skipping if needed
5. Disable verbose logging

### Target Performance

- **FPS**: 30+ frames per second
- **Latency**: <100ms gesture-to-action
- **CPU**: <50% on modern processors

## Error Handling

### Camera Failures
- Check camera permissions
- Try alternate camera indices
- Provide clear error messages

### Hand Tracking Failures
- Gracefully handle no detection
- Reset temporal state when hand lost
- Continue operation without crashes

### Network Issues
- Browser polling handles failures
- Queue system prevents lost actions
- Timeouts configured appropriately

## Extensibility Points

### Adding New Gestures

1. Define gesture detection in `gesture_recognizer.py`
2. Add mapping in `gesture_mapper.py`
3. Implement action in `earth_controller.py`
4. Configure parameters in `config.py`

### Multi-Hand Gestures

1. Set `MAX_HANDS = 2` in config
2. Process both hand landmarks
3. Detect hand interactions (distance, angles)
4. Map to new action types

### Alternative Visualization

1. Replace CesiumJS with other library
2. Implement action handler interface
3. Maintain same action API

## Security Considerations

- Web server runs on localhost only
- No external network access required
- Camera permission requested explicitly
- No data collected or transmitted

## Testing Strategy

1. **Unit tests**: Individual gesture detection
2. **Integration tests**: End-to-end gesture flow
3. **Performance tests**: FPS and latency
4. **Camera calibration**: Environment-specific tuning

## Dependencies

- **opencv-python**: Computer vision
- **mediapipe**: Hand tracking
- **numpy**: Numerical processing
- **flask**: Web server
- **selenium** (optional): Browser automation

## Future Enhancements

1. Machine learning gesture classifier
2. Gesture recording and playback
3. Multi-user support
4. Voice commands integration
5. VR/AR support
6. Mobile app version

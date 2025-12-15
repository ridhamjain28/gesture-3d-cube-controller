"""
Configuration file for Gesture-Controlled Earth System
Adjust these parameters to optimize performance and gesture sensitivity
"""

# ============================================================================
# CAMERA SETTINGS
# ============================================================================
CAMERA_INDEX = 0  # Default camera (0=built-in, 1=external USB, etc.)
FRAME_WIDTH = 1280  # Camera resolution width (640, 1280, 1920)
FRAME_HEIGHT = 720  # Camera resolution height (480, 720, 1080)
FPS_TARGET = 30  # Target frames per second

# ============================================================================
# MEDIAPIPE HAND TRACKING SETTINGS
# ============================================================================
# Detection confidence: Higher = fewer false positives, lower = better detection
DETECTION_CONFIDENCE = 0.7  # Range: 0.0-1.0 (recommended: 0.5-0.8)

# Tracking confidence: Higher = more stable tracking, lower = faster response
TRACKING_CONFIDENCE = 0.5  # Range: 0.0-1.0 (recommended: 0.5-0.7)

# Model complexity: 0=lite (fast), 1=full (accurate)
MODEL_COMPLEXITY = 1  # 0 or 1 (use 0 for low-end hardware)

# Maximum number of hands to detect
MAX_HANDS = 1  # 1 or 2 (start with 1 for better performance)

# Static image mode: False for video stream (recommended)
STATIC_IMAGE_MODE = False

# ============================================================================
# GESTURE RECOGNITION THRESHOLDS
# ============================================================================

# PINCH GESTURE
# Distance between thumb tip and index tip in pixels
PINCH_CLOSE_THRESHOLD = 30  # Fingers closer than this = pinch detected
PINCH_OPEN_THRESHOLD = 100  # Fingers farther than this = pinch released
PINCH_ZOOM_SPEED = 0.5  # Zoom sensitivity multiplier

# SWIPE GESTURE
# Minimum distance (pixels) hand must move to register as swipe
SWIPE_THRESHOLD = 100  # Recommended: 80-150
SWIPE_MIN_VELOCITY = 50  # Pixels per frame minimum speed
SWIPE_DIRECTION_TOLERANCE = 0.3  # 0.0=strict, 1.0=lenient direction detection

# TAP GESTURE
# Forward/backward movement of index finger toward camera
TAP_Z_THRESHOLD = 0.05  # Change in normalized Z-coordinate (depth)
TAP_DURATION_MAX = 0.3  # Maximum time (seconds) for tap
TAP_COOLDOWN = 0.5  # Minimum time between taps

# PALM OPEN/CLOSE
# Based on distances between fingertips
PALM_OPEN_THRESHOLD = 0.3  # Normalized distance for "open hand"
PALM_CLOSE_THRESHOLD = 0.1  # Normalized distance for "closed fist"

# ============================================================================
# GESTURE STABILIZATION
# ============================================================================
# Prevents jittery/repeated gesture detection

# Cooldown period (seconds) between same gesture detections
GESTURE_COOLDOWN = 0.5  # Recommended: 0.3-0.8

# Smoothing window size for landmark positions (reduces noise)
SMOOTHING_WINDOW = 5  # Number of frames to average (3-10)

# Minimum confidence to accept a gesture
GESTURE_CONFIDENCE_THRESHOLD = 0.6  # Range: 0.0-1.0

# Debounce: Number of consecutive frames gesture must be detected
DEBOUNCE_FRAMES = 2  # Recommended: 2-4

# ============================================================================
# EARTH CONTROLLER SETTINGS
# ============================================================================
# Controls how gestures map to Earth movements

# Rotation sensitivity (degrees per pixel)
ROTATION_SENSITIVITY = 0.2

# Zoom levels
ZOOM_MIN = 1000  # Minimum altitude (meters)
ZOOM_MAX = 20000000  # Maximum altitude (meters)
ZOOM_STEP = 1.2  # Multiplicative zoom factor per gesture

# Pan sensitivity
PAN_SENSITIVITY = 0.1  # Degrees per pixel

# Smooth camera transitions
CAMERA_SMOOTH_TIME = 0.5  # Seconds for camera animation

# ============================================================================
# VISUALIZATION SETTINGS
# ============================================================================
# Display options for hand tracking window

# Show hand landmarks and connections
SHOW_LANDMARKS = True

# Show gesture labels on screen
SHOW_GESTURE_LABELS = True

# Show FPS counter
SHOW_FPS = True

# Show hand bounding box
SHOW_BOUNDING_BOX = True

# Show gesture history (last N gestures)
SHOW_GESTURE_HISTORY = True
GESTURE_HISTORY_LENGTH = 5

# Landmark drawing colors (B, G, R format)
LANDMARK_COLOR = (0, 255, 0)  # Green
CONNECTION_COLOR = (255, 0, 0)  # Blue
BOUNDING_BOX_COLOR = (0, 255, 255)  # Yellow

# Text display settings
FONT_SCALE = 0.7
FONT_THICKNESS = 2
TEXT_COLOR = (255, 255, 255)  # White

# ============================================================================
# WEB SERVER SETTINGS
# ============================================================================
# For serving the Earth visualization webpage

WEB_SERVER_PORT = 5000
WEB_SERVER_HOST = "127.0.0.1"
AUTO_OPEN_BROWSER = True

# ============================================================================
# CESIUM / EARTH VISUALIZATION
# ============================================================================
# Your Cesium Ion access token (get free token at https://cesium.com/ion/signup)
# Leave empty to use default public imagery
CESIUM_ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI5ZmZhMGUwZC1iZWM1LTRkZDYtODcyMi1jMGI3NjNlYzljNTEiLCJpZCI6MzY5ODMzLCJpYXQiOjE3NjU3OTQzNDR9.IoIMed7Biph26OwZDmFIWokVRKa96FVu4lIJJISAVoE"

# Default camera position
DEFAULT_LATITUDE = 40.7128  # New York City
DEFAULT_LONGITUDE = -74.0060
DEFAULT_ALTITUDE = 10000000  # meters

# ============================================================================
# DEBUGGING & LOGGING
# ============================================================================
DEBUG_MODE = True  # Print detailed logs
LOG_GESTURES = True  # Log detected gestures
LOG_LANDMARKS = False  # Log hand landmark coordinates (verbose)

# Performance monitoring
ENABLE_PROFILING = False  # Track function execution times

# ============================================================================
# ADVANCED SETTINGS
# ============================================================================

# Multi-hand gesture combinations (experimental)
ENABLE_TWO_HAND_GESTURES = False

# Gesture prediction (ML-based, requires trained model)
ENABLE_ML_GESTURES = False
ML_MODEL_PATH = "models/gesture_classifier.pkl"

# Record gesture data for training
RECORD_TRAINING_DATA = False
TRAINING_DATA_PATH = "training_data/"

# Virtual hand mode (simulate gestures without camera, for testing)
VIRTUAL_HAND_MODE = False

# ============================================================================
# GESTURE-SPECIFIC PARAMETERS
# ============================================================================

# Dictionary of gesture configurations for easy customization
GESTURE_PARAMS = {
    "pinch_zoom_in": {
        "enabled": True,
        "threshold": PINCH_OPEN_THRESHOLD,
        "action": "zoom_in",
        "sensitivity": PINCH_ZOOM_SPEED
    },
    "pinch_zoom_out": {
        "enabled": True,
        "threshold": PINCH_CLOSE_THRESHOLD,
        "action": "zoom_out",
        "sensitivity": PINCH_ZOOM_SPEED
    },
    "swipe_left": {
        "enabled": True,
        "threshold": SWIPE_THRESHOLD,
        "action": "rotate_left",
        "sensitivity": ROTATION_SENSITIVITY
    },
    "swipe_right": {
        "enabled": True,
        "threshold": SWIPE_THRESHOLD,
        "action": "rotate_right",
        "sensitivity": ROTATION_SENSITIVITY
    },
    "swipe_up": {
        "enabled": True,
        "threshold": SWIPE_THRESHOLD,
        "action": "tilt_up",
        "sensitivity": PAN_SENSITIVITY
    },
    "swipe_down": {
        "enabled": True,
        "threshold": SWIPE_THRESHOLD,
        "action": "tilt_down",
        "sensitivity": PAN_SENSITIVITY
    },
    "tap": {
        "enabled": True,
        "threshold": TAP_Z_THRESHOLD,
        "action": "select",
        "cooldown": TAP_COOLDOWN
    },
    "palm_open": {
        "enabled": True,
        "threshold": PALM_OPEN_THRESHOLD,
        "action": "reset_view",
        "cooldown": 2.0
    }
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_gesture_config(gesture_name):
    """Get configuration for a specific gesture"""
    return GESTURE_PARAMS.get(gesture_name, None)

def update_gesture_config(gesture_name, param, value):
    """Update a gesture configuration parameter"""
    if gesture_name in GESTURE_PARAMS:
        GESTURE_PARAMS[gesture_name][param] = value
        return True
    return False

def is_gesture_enabled(gesture_name):
    """Check if a gesture is enabled"""
    return GESTURE_PARAMS.get(gesture_name, {}).get("enabled", False)

"""
Gesture Recognizer Module
Classifies hand gestures from landmark data using geometric and temporal analysis
Implements pinch, swipe, tap, and palm gestures with debouncing
"""

import numpy as np
import time
from collections import deque
from enum import Enum
import config


class GestureType(Enum):
    """Enumeration of recognized gestures"""
    NONE = "none"
    PINCH_IN = "pinch_in"  # Zoom out
    PINCH_OUT = "pinch_out"  # Zoom in
    SWIPE_LEFT = "swipe_left"
    SWIPE_RIGHT = "swipe_right"
    SWIPE_UP = "swipe_up"
    SWIPE_DOWN = "swipe_down"
    TAP = "tap"
    PALM_OPEN = "palm_open"
    PALM_CLOSE = "palm_close"


class Gesture:
    """Data class for gesture information"""
    def __init__(self, gesture_type, confidence=1.0, parameters=None):
        self.type = gesture_type
        self.confidence = confidence
        self.parameters = parameters or {}
        self.timestamp = time.time()
    
    def __repr__(self):
        return f"Gesture({self.type.value}, conf={self.confidence:.2f})"


class GestureRecognizer:
    """
    Recognizes hand gestures from landmark data
    
    Mathematical principles:
    - Pinch: Euclidean distance between thumb and index fingertips
    - Swipe: Velocity vector and displacement of palm center
    - Tap: Z-axis (depth) change of index finger
    - Palm: Average distance of fingertips from palm center
    """
    
    def __init__(self, hand_tracker):
        """
        Initialize gesture recognizer
        
        Args:
            hand_tracker: HandTracker instance
        """
        self.hand_tracker = hand_tracker
        
        # History buffers for temporal analysis
        self.position_history = deque(maxlen=10)
        self.pinch_history = deque(maxlen=5)
        self.palm_history = deque(maxlen=5)
        
        # Gesture state tracking
        self.last_gesture = GestureType.NONE
        self.last_gesture_time = 0
        self.gesture_start_time = 0
        
        # Debouncing: require N consecutive frames for detection
        self.gesture_debounce_buffer = deque(maxlen=config.DEBOUNCE_FRAMES)
        
        # Previous states for change detection
        self.prev_pinch_state = None  # "open" or "closed"
        self.prev_palm_state = None  # "open" or "closed"
        self.prev_palm_center = None
        self.prev_index_z = None
        
        # Gesture detection flags
        self.in_swipe = False
        self.swipe_start_pos = None
        self.swipe_start_time = None
        
        print("[GestureRecognizer] Initialized")
        print(f"  - Debounce frames: {config.DEBOUNCE_FRAMES}")
        print(f"  - Gesture cooldown: {config.GESTURE_COOLDOWN}s")
    
    def recognize(self, landmarks):
        """
        Recognize gesture from current hand landmarks
        
        Args:
            landmarks: numpy array (21, 3) of hand landmarks
            
        Returns:
            Gesture object or None
        """
        if landmarks is None:
            self._reset_temporal_state()
            return None
        
        # Check cooldown to prevent repeated detections
        if not self._check_cooldown():
            return None
        
        # Update position history
        palm_center = self.hand_tracker.get_palm_center()
        if palm_center:
            self.position_history.append(palm_center)
        
        # Try to detect each gesture type (in priority order)
        gesture = None
        
        # 1. Pinch gesture (highest priority - precise control)
        gesture = self._detect_pinch(landmarks)
        if gesture:
            return self._debounce_gesture(gesture)
        
        # 2. Tap gesture (quick interaction)
        gesture = self._detect_tap(landmarks)
        if gesture:
            return self._debounce_gesture(gesture)
        
        # 3. Swipe gestures (navigation)
        gesture = self._detect_swipe(landmarks)
        if gesture:
            return self._debounce_gesture(gesture)
        
        # 4. Palm gestures (mode changes)
        gesture = self._detect_palm(landmarks)
        if gesture:
            return self._debounce_gesture(gesture)
        
        # No gesture detected
        self.gesture_debounce_buffer.clear()
        return None
    
    def _detect_pinch(self, landmarks):
        """
        Detect pinch gesture based on thumb-index distance
        
        Pinch In (Zoom Out): Distance decreases below threshold
        Pinch Out (Zoom In): Distance increases above threshold
        
        Mathematical formula:
            distance = sqrt((x1-x2)² + (y1-y2)²)
        
        Returns:
            Gesture or None
        """
        # Get thumb and index finger tip positions
        thumb_tip = landmarks[self.hand_tracker.THUMB_TIP]
        index_tip = landmarks[self.hand_tracker.INDEX_TIP]
        
        # Calculate 2D distance
        distance = np.sqrt(
            (thumb_tip[0] - index_tip[0])**2 + 
            (thumb_tip[1] - index_tip[1])**2
        )
        
        # Add to history
        self.pinch_history.append(distance)
        
        # Determine current pinch state
        current_state = None
        if distance < config.PINCH_CLOSE_THRESHOLD:
            current_state = "closed"
        elif distance > config.PINCH_OPEN_THRESHOLD:
            current_state = "open"
        
        # Detect state change (transition)
        gesture = None
        if self.prev_pinch_state and current_state:
            if self.prev_pinch_state == "open" and current_state == "closed":
                # Pinching in (zoom out)
                gesture = Gesture(
                    GestureType.PINCH_IN,
                    confidence=0.9,
                    parameters={"distance": distance}
                )
            elif self.prev_pinch_state == "closed" and current_state == "open":
                # Pinching out (zoom in)
                gesture = Gesture(
                    GestureType.PINCH_OUT,
                    confidence=0.9,
                    parameters={"distance": distance}
                )
        
        # Update state
        if current_state:
            self.prev_pinch_state = current_state
        
        return gesture
    
    def _detect_swipe(self, landmarks):
        """
        Detect swipe gesture based on palm movement velocity
        
        Swipe = displacement over time in one direction
        
        Mathematical formula:
            velocity = displacement / time
            direction = atan2(dy, dx)
        
        Returns:
            Gesture or None
        """
        if len(self.position_history) < 3:
            return None  # Need history for velocity calculation
        
        # Get current and previous palm positions
        current_pos = np.array(self.position_history[-1][:2])  # x, y only
        start_pos = np.array(self.position_history[0][:2])
        
        # Calculate displacement vector
        displacement = current_pos - start_pos
        distance = np.linalg.norm(displacement)
        
        # Calculate time elapsed
        time_elapsed = len(self.position_history) * (1.0 / config.FPS_TARGET)
        
        # Calculate velocity
        if time_elapsed > 0:
            velocity = distance / time_elapsed
        else:
            velocity = 0
        
        # Check if movement exceeds threshold
        if distance < config.SWIPE_THRESHOLD:
            return None
        
        if velocity < config.SWIPE_MIN_VELOCITY:
            return None
        
        # Determine swipe direction
        dx, dy = displacement
        
        # Calculate dominant direction
        abs_dx = abs(dx)
        abs_dy = abs(dy)
        
        gesture = None
        
        if abs_dx > abs_dy:
            # Horizontal swipe
            if abs_dx > abs_dy * (1 + config.SWIPE_DIRECTION_TOLERANCE):
                if dx > 0:
                    gesture = Gesture(
                        GestureType.SWIPE_RIGHT,
                        confidence=0.8,
                        parameters={"distance": distance, "velocity": velocity}
                    )
                else:
                    gesture = Gesture(
                        GestureType.SWIPE_LEFT,
                        confidence=0.8,
                        parameters={"distance": distance, "velocity": velocity}
                    )
        else:
            # Vertical swipe
            if abs_dy > abs_dx * (1 + config.SWIPE_DIRECTION_TOLERANCE):
                if dy > 0:
                    gesture = Gesture(
                        GestureType.SWIPE_DOWN,
                        confidence=0.8,
                        parameters={"distance": distance, "velocity": velocity}
                    )
                else:
                    gesture = Gesture(
                        GestureType.SWIPE_UP,
                        confidence=0.8,
                        parameters={"distance": distance, "velocity": velocity}
                    )
        
        # Clear position history after detecting swipe
        if gesture:
            self.position_history.clear()
        
        return gesture
    
    def _detect_tap(self, landmarks):
        """
        Detect tap gesture based on Z-axis (depth) change
        
        Tap = quick forward motion of index finger toward camera
        
        Z-coordinate: smaller value = closer to camera
        
        Returns:
            Gesture or None
        """
        # Get index finger tip Z coordinate (depth)
        index_tip = landmarks[self.hand_tracker.INDEX_TIP]
        current_z = index_tip[2]
        
        if self.prev_index_z is None:
            self.prev_index_z = current_z
            return None
        
        # Calculate Z change (negative = moving toward camera)
        z_change = current_z - self.prev_index_z
        
        # Detect quick forward motion (tap)
        gesture = None
        if z_change < -config.TAP_Z_THRESHOLD:
            gesture = Gesture(
                GestureType.TAP,
                confidence=0.7,
                parameters={"z_change": z_change}
            )
        
        # Update previous Z
        self.prev_index_z = current_z
        
        return gesture
    
    def _detect_palm(self, landmarks):
        """
        Detect palm open/close gesture
        
        Palm Open: All fingers extended (large spread)
        Palm Close: Fist (fingers curled, small spread)
        
        Mathematical approach:
            - Calculate average distance from fingertips to palm center
            - Normalize by hand size
            - Compare to thresholds
        
        Returns:
            Gesture or None
        """
        # Check if hand is open
        is_open = self.hand_tracker.is_hand_open()
        
        # Determine current state
        current_state = "open" if is_open else "closed"
        
        # Detect state change
        gesture = None
        if self.prev_palm_state and self.prev_palm_state != current_state:
            if current_state == "open":
                gesture = Gesture(
                    GestureType.PALM_OPEN,
                    confidence=0.85,
                    parameters={"state": "open"}
                )
            else:
                gesture = Gesture(
                    GestureType.PALM_CLOSE,
                    confidence=0.85,
                    parameters={"state": "closed"}
                )
        
        # Update state
        self.prev_palm_state = current_state
        
        return gesture
    
    def _debounce_gesture(self, gesture):
        """
        Debounce gesture detection: require N consecutive frames
        
        This prevents false positives from noisy detection
        
        Args:
            gesture: Detected gesture
            
        Returns:
            Gesture or None (if not debounced)
        """
        if gesture is None:
            self.gesture_debounce_buffer.clear()
            return None
        
        # Add to debounce buffer
        self.gesture_debounce_buffer.append(gesture.type)
        
        # Check if buffer is full and all same gesture
        if len(self.gesture_debounce_buffer) == config.DEBOUNCE_FRAMES:
            if all(g == gesture.type for g in self.gesture_debounce_buffer):
                # Gesture confirmed!
                self.gesture_debounce_buffer.clear()
                self._update_gesture_state(gesture)
                return gesture
        
        return None
    
    def _check_cooldown(self):
        """
        Check if enough time has passed since last gesture
        
        Prevents repeated detection of same gesture
        
        Returns:
            bool: True if cooldown expired
        """
        current_time = time.time()
        elapsed = current_time - self.last_gesture_time
        
        return elapsed >= config.GESTURE_COOLDOWN
    
    def _update_gesture_state(self, gesture):
        """Update internal state after gesture detection"""
        self.last_gesture = gesture.type
        self.last_gesture_time = time.time()
        
        if config.LOG_GESTURES:
            print(f"[Gesture] {gesture}")
    
    def _reset_temporal_state(self):
        """Reset temporal tracking when hand is lost"""
        self.position_history.clear()
        self.pinch_history.clear()
        self.prev_pinch_state = None
        self.prev_palm_state = None
        self.prev_palm_center = None
        self.prev_index_z = None
    
    def get_gesture_history(self, n=5):
        """Get last N detected gestures (for UI display)"""
        # This would require storing gesture history
        # For now, return last gesture
        return [self.last_gesture]


# Example usage and testing
if __name__ == "__main__":
    print("Testing GestureRecognizer...")
    print("Perform gestures:")
    print("  - Pinch fingers together/apart")
    print("  - Swipe hand left/right/up/down")
    print("  - Tap index finger forward")
    print("  - Open/close palm")
    print("\nPress 'q' to quit")
    
    import cv2
    from hand_tracker import HandTracker
    
    # Initialize
    tracker = HandTracker()
    recognizer = GestureRecognizer(tracker)
    
    # Open camera
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        exit(1)
    
    # Gesture history for display
    gesture_history = deque(maxlen=config.GESTURE_HISTORY_LENGTH)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Track hand
        processed_frame, landmarks, handedness = tracker.process_frame(frame)
        
        # Recognize gesture
        gesture = recognizer.recognize(landmarks)
        
        # Display gesture
        if gesture:
            gesture_history.append(gesture)
        
        # Draw gesture history
        if config.SHOW_GESTURE_HISTORY and len(gesture_history) > 0:
            y_offset = 150
            cv2.putText(
                processed_frame,
                "Recent Gestures:",
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )
            
            for i, g in enumerate(gesture_history):
                y_offset += 30
                text = f"{i+1}. {g.type.value}"
                cv2.putText(
                    processed_frame,
                    text,
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 255),
                    1
                )
        
        # Show current gesture (if detected)
        if gesture:
            cv2.putText(
                processed_frame,
                f"GESTURE: {gesture.type.value.upper()}",
                (10, processed_frame.shape[0] - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 0),
                3
            )
        
        cv2.imshow("Gesture Recognizer Test", processed_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    tracker.release()
    print("Test completed!")

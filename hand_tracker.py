"""
Hand Tracker Module
Uses MediaPipe Hands to detect and track hand landmarks in real-time
Provides normalized 3D coordinates of 21 hand landmarks
"""

import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque
import config


class HandTracker:
    """
    Real-time hand tracking using MediaPipe Hands
    
    MediaPipe detects 21 landmarks per hand:
    0: Wrist
    1-4: Thumb (CMC, MCP, IP, TIP)
    5-8: Index finger (MCP, PIP, DIP, TIP)
    9-12: Middle finger (MCP, PIP, DIP, TIP)
    13-16: Ring finger (MCP, PIP, DIP, TIP)
    17-20: Pinky (MCP, PIP, DIP, TIP)
    """
    
    # Landmark indices for easy reference
    WRIST = 0
    THUMB_TIP = 4
    INDEX_TIP = 8
    MIDDLE_TIP = 12
    RING_TIP = 16
    PINKY_TIP = 20
    INDEX_MCP = 5  # Base of index finger
    THUMB_CMC = 1  # Base of thumb
    
    def __init__(self):
        """Initialize MediaPipe Hands and tracking parameters"""
        
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Configure hand tracking
        self.hands = self.mp_hands.Hands(
            static_image_mode=config.STATIC_IMAGE_MODE,
            max_num_hands=config.MAX_HANDS,
            model_complexity=config.MODEL_COMPLEXITY,
            min_detection_confidence=config.DETECTION_CONFIDENCE,
            min_tracking_confidence=config.TRACKING_CONFIDENCE
        )
        
        # Tracking state
        self.landmarks = None  # Current frame landmarks
        self.handedness = None  # Left or Right hand
        self.frame_count = 0
        
        # Smoothing buffer for landmark positions
        self.landmark_history = deque(maxlen=config.SMOOTHING_WINDOW)
        
        # FPS calculation
        self.fps = 0
        self.frame_time = time.time()
        
        # Hand detection status
        self.hand_detected = False
        
        print("[HandTracker] Initialized with:")
        print(f"  - Detection confidence: {config.DETECTION_CONFIDENCE}")
        print(f"  - Tracking confidence: {config.TRACKING_CONFIDENCE}")
        print(f"  - Model complexity: {config.MODEL_COMPLEXITY}")
        print(f"  - Max hands: {config.MAX_HANDS}")
    
    def process_frame(self, frame):
        """
        Process a video frame and detect hands
        
        Args:
            frame: BGR image from camera (numpy array)
            
        Returns:
            tuple: (processed_frame, landmarks, handedness)
                - processed_frame: Frame with drawings (if enabled)
                - landmarks: List of 21 landmarks or None
                - handedness: "Left" or "Right" or None
        """
        self.frame_count += 1
        
        # Convert BGR to RGB (MediaPipe uses RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Improve performance by marking frame as not writeable
        rgb_frame.flags.writeable = False
        
        # Process frame with MediaPipe
        results = self.hands.process(rgb_frame)
        
        # Make frame writeable again for drawing
        rgb_frame.flags.writeable = True
        frame_copy = frame.copy()
        
        # Reset detection status
        self.hand_detected = False
        self.landmarks = None
        self.handedness = None
        
        # Process detected hands
        if results.multi_hand_landmarks:
            # Get first detected hand (if multiple, use first)
            hand_landmarks = results.multi_hand_landmarks[0]
            hand_handedness = results.multi_handedness[0]
            
            # Extract landmark coordinates
            self.landmarks = self._extract_landmarks(hand_landmarks, frame.shape)
            self.handedness = hand_handedness.classification[0].label
            self.hand_detected = True
            
            # Apply smoothing
            if config.SMOOTHING_WINDOW > 1:
                self.landmarks = self._smooth_landmarks(self.landmarks)
            
            # Draw landmarks on frame
            if config.SHOW_LANDMARKS:
                self._draw_landmarks(frame_copy, hand_landmarks)
            
            # Draw bounding box
            if config.SHOW_BOUNDING_BOX:
                self._draw_bounding_box(frame_copy, self.landmarks)
        
        # Calculate and display FPS
        if config.SHOW_FPS:
            self._update_fps()
            self._draw_fps(frame_copy)
        
        # Display hand status
        self._draw_status(frame_copy)
        
        return frame_copy, self.landmarks, self.handedness
    
    def _extract_landmarks(self, hand_landmarks, frame_shape):
        """
        Extract landmark coordinates and convert to pixel values
        
        MediaPipe provides normalized coordinates (0.0-1.0)
        We convert to pixel coordinates and preserve depth (z)
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            frame_shape: (height, width, channels)
            
        Returns:
            numpy array: Shape (21, 3) with (x, y, z) coordinates
                x, y in pixels
                z normalized (smaller = closer to camera)
        """
        h, w, c = frame_shape
        landmarks = []
        
        for landmark in hand_landmarks.landmark:
            # Convert normalized coordinates to pixels
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            z = landmark.z  # Keep z normalized (depth)
            
            landmarks.append([x, y, z])
        
        return np.array(landmarks)
    
    def _smooth_landmarks(self, landmarks):
        """
        Apply moving average smoothing to reduce jitter
        
        Args:
            landmarks: Current frame landmarks (21, 3)
            
        Returns:
            numpy array: Smoothed landmarks
        """
        # Add current landmarks to history
        self.landmark_history.append(landmarks)
        
        # Average over history window
        if len(self.landmark_history) > 0:
            smoothed = np.mean(self.landmark_history, axis=0)
            return smoothed
        
        return landmarks
    
    def _draw_landmarks(self, frame, hand_landmarks):
        """Draw hand landmarks and connections on frame"""
        self.mp_drawing.draw_landmarks(
            frame,
            hand_landmarks,
            self.mp_hands.HAND_CONNECTIONS,
            self.mp_drawing_styles.get_default_hand_landmarks_style(),
            self.mp_drawing_styles.get_default_hand_connections_style()
        )
    
    def _draw_bounding_box(self, frame, landmarks):
        """Draw bounding box around detected hand"""
        if landmarks is None or len(landmarks) == 0:
            return
        
        # Find min/max coordinates
        x_coords = landmarks[:, 0]
        y_coords = landmarks[:, 1]
        
        x_min, x_max = int(np.min(x_coords)), int(np.max(x_coords))
        y_min, y_max = int(np.min(y_coords)), int(np.max(y_coords))
        
        # Add padding
        padding = 20
        x_min = max(0, x_min - padding)
        y_min = max(0, y_min - padding)
        x_max = min(frame.shape[1], x_max + padding)
        y_max = min(frame.shape[0], y_max + padding)
        
        # Draw rectangle
        cv2.rectangle(
            frame,
            (x_min, y_min),
            (x_max, y_max),
            config.BOUNDING_BOX_COLOR,
            2
        )
    
    def _update_fps(self):
        """Calculate current FPS"""
        current_time = time.time()
        elapsed = current_time - self.frame_time
        
        if elapsed > 0:
            self.fps = 1.0 / elapsed
        
        self.frame_time = current_time
    
    def _draw_fps(self, frame):
        """Display FPS on frame"""
        fps_text = f"FPS: {self.fps:.1f}"
        cv2.putText(
            frame,
            fps_text,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            config.FONT_SCALE,
            config.TEXT_COLOR,
            config.FONT_THICKNESS
        )
    
    def _draw_status(self, frame):
        """Display hand detection status"""
        if self.hand_detected:
            status_text = f"Hand: {self.handedness}"
            color = (0, 255, 0)  # Green
        else:
            status_text = "No hand detected"
            color = (0, 0, 255)  # Red
        
        cv2.putText(
            frame,
            status_text,
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            config.FONT_SCALE,
            color,
            config.FONT_THICKNESS
        )
    
    def get_landmark_position(self, landmark_id):
        """
        Get position of a specific landmark
        
        Args:
            landmark_id: Index (0-20) of landmark
            
        Returns:
            tuple: (x, y, z) or None if not detected
        """
        if self.landmarks is not None and landmark_id < len(self.landmarks):
            return tuple(self.landmarks[landmark_id])
        return None
    
    def get_distance_between_landmarks(self, id1, id2):
        """
        Calculate Euclidean distance between two landmarks
        
        Args:
            id1, id2: Landmark indices
            
        Returns:
            float: Distance in pixels (or None)
        """
        if self.landmarks is None:
            return None
        
        if id1 >= len(self.landmarks) or id2 >= len(self.landmarks):
            return None
        
        p1 = self.landmarks[id1]
        p2 = self.landmarks[id2]
        
        # 2D distance (x, y only)
        distance = np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
        
        return distance
    
    def get_palm_center(self):
        """
        Calculate center of palm
        
        Returns:
            tuple: (x, y, z) of palm center or None
        """
        if self.landmarks is None:
            return None
        
        # Average of wrist and base knuckles
        palm_landmarks = [
            self.WRIST,
            self.INDEX_MCP,
            5,  # Index MCP
            9,  # Middle MCP
            13,  # Ring MCP
            17   # Pinky MCP
        ]
        
        palm_points = self.landmarks[palm_landmarks]
        center = np.mean(palm_points, axis=0)
        
        return tuple(center)
    
    def is_hand_open(self):
        """
        Check if hand is open (fingers extended)
        
        Returns:
            bool: True if hand is open
        """
        if self.landmarks is None:
            return False
        
        # Check if fingertips are far from palm center
        palm_center = self.get_palm_center()
        if palm_center is None:
            return False
        
        fingertips = [
            self.THUMB_TIP,
            self.INDEX_TIP,
            self.MIDDLE_TIP,
            self.RING_TIP,
            self.PINKY_TIP
        ]
        
        # Calculate average distance from palm to fingertips
        distances = []
        for tip_id in fingertips:
            tip = self.landmarks[tip_id]
            dist = np.sqrt(
                (tip[0] - palm_center[0])**2 + 
                (tip[1] - palm_center[1])**2
            )
            distances.append(dist)
        
        avg_distance = np.mean(distances)
        
        # Normalize by hand size (wrist to middle finger MCP distance)
        wrist = self.landmarks[self.WRIST]
        middle_mcp = self.landmarks[9]
        hand_size = np.sqrt(
            (wrist[0] - middle_mcp[0])**2 + 
            (wrist[1] - middle_mcp[1])**2
        )
        
        if hand_size == 0:
            return False
        
        normalized_distance = avg_distance / hand_size
        
        # Threshold for "open hand"
        return normalized_distance > config.PALM_OPEN_THRESHOLD
    
    def release(self):
        """Release resources"""
        self.hands.close()
        print("[HandTracker] Released resources")


# Example usage and testing
if __name__ == "__main__":
    print("Testing HandTracker...")
    print("Press 'q' to quit")
    
    # Initialize tracker
    tracker = HandTracker()
    
    # Open camera
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        exit(1)
    
    print("\nCamera opened successfully!")
    print("Show your hand to the camera...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
            break
        
        # Process frame
        processed_frame, landmarks, handedness = tracker.process_frame(frame)
        
        # Display additional info
        if landmarks is not None:
            # Show pinch distance
            pinch_dist = tracker.get_distance_between_landmarks(
                tracker.THUMB_TIP,
                tracker.INDEX_TIP
            )
            if pinch_dist:
                cv2.putText(
                    processed_frame,
                    f"Pinch: {pinch_dist:.1f}px",
                    (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 0),
                    2
                )
            
            # Show hand open/close status
            is_open = tracker.is_hand_open()
            status = "OPEN" if is_open else "CLOSED"
            cv2.putText(
                processed_frame,
                f"Hand: {status}",
                (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2
            )
        
        # Show frame
        cv2.imshow("Hand Tracker Test", processed_frame)
        
        # Quit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    tracker.release()
    print("Test completed!")

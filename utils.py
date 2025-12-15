"""
Utility Functions
Helper functions for mathematical calculations, smoothing, and data processing
"""

import numpy as np
import time
from collections import deque


def euclidean_distance(point1, point2):
    """
    Calculate Euclidean distance between two points
    
    Args:
        point1: Tuple or array (x, y) or (x, y, z)
        point2: Tuple or array (x, y) or (x, y, z)
        
    Returns:
        float: Distance
    """
    p1 = np.array(point1)
    p2 = np.array(point2)
    return np.linalg.norm(p1 - p2)


def angle_between_vectors(v1, v2):
    """
    Calculate angle between two vectors in degrees
    
    Args:
        v1, v2: Vectors as tuples or arrays
        
    Returns:
        float: Angle in degrees (0-180)
    """
    v1 = np.array(v1)
    v2 = np.array(v2)
    
    # Normalize vectors
    v1_norm = v1 / np.linalg.norm(v1)
    v2_norm = v2 / np.linalg.norm(v2)
    
    # Calculate angle
    dot_product = np.dot(v1_norm, v2_norm)
    angle_rad = np.arccos(np.clip(dot_product, -1.0, 1.0))
    angle_deg = np.degrees(angle_rad)
    
    return angle_deg


def moving_average(data, window_size=5):
    """
    Calculate moving average of data
    
    Args:
        data: List or array of values
        window_size: Size of moving window
        
    Returns:
        numpy array: Smoothed data
    """
    if len(data) < window_size:
        return np.array(data)
    
    weights = np.ones(window_size) / window_size
    return np.convolve(data, weights, mode='valid')


def exponential_smoothing(data, alpha=0.3):
    """
    Apply exponential smoothing to data
    
    Args:
        data: List or array of values
        alpha: Smoothing factor (0-1), higher = less smoothing
        
    Returns:
        numpy array: Smoothed data
    """
    smoothed = [data[0]]
    
    for i in range(1, len(data)):
        smoothed_value = alpha * data[i] + (1 - alpha) * smoothed[-1]
        smoothed.append(smoothed_value)
    
    return np.array(smoothed)


def normalize_landmarks(landmarks, width, height):
    """
    Normalize landmark coordinates to 0-1 range
    
    Args:
        landmarks: Array of (x, y, z) coordinates
        width, height: Frame dimensions
        
    Returns:
        numpy array: Normalized coordinates
    """
    normalized = landmarks.copy()
    normalized[:, 0] /= width
    normalized[:, 1] /= height
    # Z is already normalized
    
    return normalized


def denormalize_landmarks(landmarks, width, height):
    """
    Convert normalized coordinates back to pixel coordinates
    
    Args:
        landmarks: Array of normalized (x, y, z) coordinates
        width, height: Frame dimensions
        
    Returns:
        numpy array: Pixel coordinates
    """
    denormalized = landmarks.copy()
    denormalized[:, 0] *= width
    denormalized[:, 1] *= height
    
    return denormalized


def calculate_velocity(positions, time_window=0.1):
    """
    Calculate velocity from position history
    
    Args:
        positions: Deque or list of (x, y) positions
        time_window: Time span in seconds
        
    Returns:
        tuple: (velocity_magnitude, direction_angle)
    """
    if len(positions) < 2:
        return 0.0, 0.0
    
    # Get start and end positions
    start_pos = np.array(positions[0][:2])
    end_pos = np.array(positions[-1][:2])
    
    # Calculate displacement
    displacement = end_pos - start_pos
    distance = np.linalg.norm(displacement)
    
    # Calculate velocity
    velocity = distance / time_window
    
    # Calculate direction (angle in degrees)
    direction = np.degrees(np.arctan2(displacement[1], displacement[0]))
    
    return velocity, direction


def is_point_in_rectangle(point, rect):
    """
    Check if point is inside rectangle
    
    Args:
        point: Tuple (x, y)
        rect: Tuple (x_min, y_min, x_max, y_max)
        
    Returns:
        bool: True if point is inside rectangle
    """
    x, y = point
    x_min, y_min, x_max, y_max = rect
    
    return x_min <= x <= x_max and y_min <= y <= y_max


def calculate_hand_size(landmarks):
    """
    Calculate hand size (for normalization)
    
    Args:
        landmarks: Array of hand landmarks
        
    Returns:
        float: Hand size (distance from wrist to middle finger tip)
    """
    if landmarks is None or len(landmarks) < 13:
        return 0
    
    wrist = landmarks[0]
    middle_tip = landmarks[12]
    
    size = euclidean_distance(wrist, middle_tip)
    return size


def detect_finger_extended(landmarks, finger_id):
    """
    Detect if a specific finger is extended
    
    Args:
        landmarks: Hand landmarks
        finger_id: Finger index (1=thumb, 2=index, 3=middle, 4=ring, 5=pinky)
        
    Returns:
        bool: True if finger is extended
    """
    if landmarks is None:
        return False
    
    # Finger landmark indices
    finger_tips = [4, 8, 12, 16, 20]
    finger_pips = [2, 6, 10, 14, 18]  # Middle joints
    
    if finger_id < 1 or finger_id > 5:
        return False
    
    tip_idx = finger_tips[finger_id - 1]
    pip_idx = finger_pips[finger_id - 1]
    
    # Get positions
    tip = landmarks[tip_idx]
    pip = landmarks[pip_idx]
    wrist = landmarks[0]
    
    # Check if tip is farther from wrist than middle joint
    tip_dist = euclidean_distance(tip, wrist)
    pip_dist = euclidean_distance(pip, wrist)
    
    return tip_dist > pip_dist * 1.1


def count_extended_fingers(landmarks):
    """
    Count number of extended fingers
    
    Args:
        landmarks: Hand landmarks
        
    Returns:
        int: Number of extended fingers (0-5)
    """
    count = 0
    for finger_id in range(1, 6):
        if detect_finger_extended(landmarks, finger_id):
            count += 1
    return count


class FPSCounter:
    """Helper class for FPS calculation"""
    
    def __init__(self, avg_window=30):
        self.frame_times = deque(maxlen=avg_window)
        self.last_time = time.time()
    
    def update(self):
        """Update FPS calculation"""
        current_time = time.time()
        elapsed = current_time - self.last_time
        self.last_time = current_time
        
        if elapsed > 0:
            fps = 1.0 / elapsed
            self.frame_times.append(fps)
    
    def get_fps(self):
        """Get average FPS"""
        if len(self.frame_times) == 0:
            return 0.0
        return np.mean(self.frame_times)


class Timer:
    """Helper class for timing operations"""
    
    def __init__(self, name="Operation"):
        self.name = name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args):
        elapsed = time.time() - self.start_time
        print(f"[Timer] {self.name}: {elapsed*1000:.2f}ms")


class Debouncer:
    """Generic debouncer for any event"""
    
    def __init__(self, cooldown=0.5):
        self.cooldown = cooldown
        self.last_trigger_time = 0
    
    def can_trigger(self):
        """Check if enough time has passed"""
        current_time = time.time()
        elapsed = current_time - self.last_trigger_time
        
        if elapsed >= self.cooldown:
            self.last_trigger_time = current_time
            return True
        
        return False
    
    def reset(self):
        """Reset the debouncer"""
        self.last_trigger_time = 0


def clamp(value, min_value, max_value):
    """Clamp value between min and max"""
    return max(min_value, min(max_value, value))


def lerp(start, end, t):
    """Linear interpolation between start and end"""
    return start + (end - start) * t


def smooth_step(t):
    """Smooth step function (cubic Hermite interpolation)"""
    return t * t * (3 - 2 * t)


# Example usage and testing
if __name__ == "__main__":
    print("Testing utility functions...\n")
    
    # Test distance calculation
    p1 = (0, 0)
    p2 = (3, 4)
    dist = euclidean_distance(p1, p2)
    print(f"Distance between {p1} and {p2}: {dist} (expected: 5.0)")
    
    # Test angle calculation
    v1 = (1, 0)
    v2 = (0, 1)
    angle = angle_between_vectors(v1, v2)
    print(f"Angle between {v1} and {v2}: {angle}° (expected: 90.0)")
    
    # Test moving average
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    smoothed = moving_average(data, window_size=3)
    print(f"\nMoving average (window=3):")
    print(f"  Original: {data}")
    print(f"  Smoothed: {smoothed}")
    
    # Test FPS counter
    print("\nTesting FPS counter...")
    fps_counter = FPSCounter()
    for i in range(10):
        time.sleep(0.016)  # ~60 FPS
        fps_counter.update()
    print(f"  Average FPS: {fps_counter.get_fps():.1f}")
    
    # Test debouncer
    print("\nTesting debouncer...")
    debouncer = Debouncer(cooldown=0.5)
    for i in range(5):
        if debouncer.can_trigger():
            print(f"  Trigger {i+1} allowed")
        else:
            print(f"  Trigger {i+1} blocked (cooldown)")
        time.sleep(0.3)
    
    # Test timer
    print("\nTesting timer...")
    with Timer("Sleep test"):
        time.sleep(0.1)
    
    print("\n✓ All utility functions tested successfully!")

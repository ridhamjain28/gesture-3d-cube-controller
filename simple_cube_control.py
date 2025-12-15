"""
ULTRA SIMPLE 3D Cube Control with Hand Gestures
Simplified gesture detection - won't crash!
"""

import cv2
import time
import numpy as np
import mediapipe as mp

class SimpleCube:
    """Simple rotating 3D cube with colored faces"""
    def __init__(self):
        # 3D cube vertices
        self.vertices = np.array([
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
        ], dtype=float)
        
        self.edges = [
            (0,1), (1,2), (2,3), (3,0),
            (4,5), (5,6), (6,7), (7,4),
            (0,4), (1,5), (2,6), (3,7)
        ]
        
        # Define faces (each face is 4 vertices)
        self.faces = [
            (0, 1, 2, 3),  # Back face
            (4, 5, 6, 7),  # Front face
            (0, 1, 5, 4),  # Bottom face
            (2, 3, 7, 6),  # Top face
            (0, 3, 7, 4),  # Left face
            (1, 2, 6, 5)   # Right face
        ]
        
        # Colors for each face (BGR format)
        self.face_colors = [
            (0, 0, 255),      # Back - RED
            (0, 255, 0),      # Front - GREEN
            (255, 0, 0),      # Bottom - BLUE
            (0, 255, 255),    # Top - YELLOW
            (255, 0, 255),    # Left - MAGENTA
            (255, 255, 0)     # Right - CYAN
        ]
        
        self.rotation_x = 0
        self.rotation_y = 0
        self.rotation_z = 0
        self.scale = 100
        self.zoom = 3
        
    def rotate_x(self, angle):
        rad = np.radians(angle)
        return np.array([
            [1, 0, 0],
            [0, np.cos(rad), -np.sin(rad)],
            [0, np.sin(rad), np.cos(rad)]
        ])
    
    def rotate_y(self, angle):
        rad = np.radians(angle)
        return np.array([
            [np.cos(rad), 0, np.sin(rad)],
            [0, 1, 0],
            [-np.sin(rad), 0, np.cos(rad)]
        ])
    
    def rotate_z(self, angle):
        rad = np.radians(angle)
        return np.array([
            [np.cos(rad), -np.sin(rad), 0],
            [np.sin(rad), np.cos(rad), 0],
            [0, 0, 1]
        ])
    
    def draw(self, frame):
        height, width = frame.shape[:2]
        
        # Apply rotations
        rotated = self.vertices.copy()
        rotated = rotated @ self.rotate_x(self.rotation_x).T
        rotated = rotated @ self.rotate_y(self.rotation_y).T
        rotated = rotated @ self.rotate_z(self.rotation_z).T
        rotated = rotated * self.zoom
        
        # Project to 2D
        projected = []
        depths = []
        for vertex in rotated:
            x, y, z = vertex
            depths.append(z)
            factor = 200 / (200 + z)
            x = x * factor * self.scale + width // 2
            y = y * factor * self.scale + height // 2
            projected.append((int(x), int(y)))
        
        # Calculate face centers for depth sorting
        face_depths = []
        for i, face in enumerate(self.faces):
            avg_depth = sum(depths[v] for v in face) / 4
            face_depths.append((avg_depth, i))
        
        # Sort faces by depth (back to front)
        face_depths.sort(reverse=True)
        
        # Draw filled faces (back to front for proper occlusion)
        for _, face_idx in face_depths:
            face = self.faces[face_idx]
            points = np.array([projected[v] for v in face], dtype=np.int32)
            color = self.face_colors[face_idx]
            
            # Draw filled polygon
            cv2.fillPoly(frame, [points], color)
            
            # Draw face outline (darker)
            darker_color = tuple(int(c * 0.5) for c in color)
            cv2.polylines(frame, [points], True, darker_color, 3)
        
        # Draw vertices as white dots
        for pt in projected:
            cv2.circle(frame, pt, 5, (255, 255, 255), -1)
            cv2.circle(frame, pt, 5, (0, 0, 0), 1)


def calculate_distance(point1, point2):
    """Calculate distance between two points"""
    return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


def main():
    print("=" * 70)
    print("SIMPLE 3D CUBE CONTROLLER")
    print("=" * 70)
    
    # Initialize MediaPipe
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    )
    mp_draw = mp.solutions.drawing_utils
    
    # Initialize cube
    cube = SimpleCube()
    
    # Open camera
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    if not camera.isOpened():
        print("ERROR: Cannot open camera!")
        return
    
    print("\n✓ Camera opened successfully!")
    print("\n" + "=" * 70)
    print("GESTURE INSTRUCTIONS:")
    print("=" * 70)
    print("\n1. PINCH (Thumb + Index finger together)")
    print("   - HOLD pinch and MOVE LEFT → Rotate cube LEFT")
    print("   - HOLD pinch and MOVE RIGHT → Rotate cube RIGHT")
    print("   - HOLD pinch and MOVE UP → Rotate cube UP")
    print("   - HOLD pinch and MOVE DOWN → Rotate cube DOWN")
    print("\n2. SPREAD FINGERS (All 5 fingers open wide)")
    print("   - Opens fingers → Zoom IN (cube gets bigger)")
    print("   - Close fingers to fist → Zoom OUT (cube gets smaller)")
    print("\n3. Press 'R' → Reset cube to original position")
    print("4. Press 'Q' → Quit program")
    print("=" * 70)
    print("\n✓ READY! Show your hand to the camera...\n")
    
    # Tracking variables
    prev_pinch_pos = None
    prev_hand_openness = None
    last_gesture_time = time.time()
    gesture_cooldown = 0.5  # Longer cooldown to prevent confusion
    zoom_direction = None  # Track zoom direction
    
    # Main loop
    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                break
            
            # Flip for mirror effect (fixes left/right)
            frame = cv2.flip(frame, 1)
            
            # Create display
            display = np.zeros_like(frame)
            display[:] = (30, 30, 30)  # Dark background
            
            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)
            
            current_gesture = "NO HAND DETECTED"
            
            # Process hand landmarks
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw hand on frame
                    h, w, _ = frame.shape
                    
                    # Get key points
                    thumb_tip = hand_landmarks.landmark[4]
                    index_tip = hand_landmarks.landmark[8]
                    middle_tip = hand_landmarks.landmark[12]
                    ring_tip = hand_landmarks.landmark[16]
                    pinky_tip = hand_landmarks.landmark[20]
                    
                    wrist = hand_landmarks.landmark[0]
                    
                    # Convert to pixel coordinates
                    thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
                    index_x, index_y = int(index_tip.x * w), int(index_tip.y * h)
                    wrist_x, wrist_y = int(wrist.x * w), int(wrist.y * h)
                    
                    # Calculate pinch distance
                    pinch_dist = calculate_distance((thumb_x, thumb_y), (index_x, index_y))
                    
                    # Calculate hand openness (average distance from wrist)
                    avg_dist = (
                        calculate_distance((thumb_x, thumb_y), (wrist_x, wrist_y)) +
                        calculate_distance((int(middle_tip.x*w), int(middle_tip.y*h)), (wrist_x, wrist_y)) +
                        calculate_distance((int(pinky_tip.x*w), int(pinky_tip.y*h)), (wrist_x, wrist_y))
                    ) / 3
                    
                    # Draw hand on small preview
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    
                    current_time = time.time()
                    
                    # GESTURE 1: PINCH AND DRAG
                    if pinch_dist < 40:  # Pinching
                        current_gesture = f"PINCH (dist: {pinch_dist:.0f})"
                        
                        if prev_pinch_pos is not None:
                            # Calculate movement
                            dx = index_x - prev_pinch_pos[0]
                            dy = index_y - prev_pinch_pos[1]
                            
                            # Apply rotation based on movement
                            if abs(dx) > 5:
                                cube.rotation_y += dx * 0.5
                                current_gesture += " → ROTATING"
                            if abs(dy) > 5:
                                cube.rotation_x += dy * 0.5
                                current_gesture += " → ROTATING"
                        
                        prev_pinch_pos = (index_x, index_y)
                    else:
                        prev_pinch_pos = None
                    
                    # GESTURE 2: HAND OPENNESS (ZOOM)
                    # More reliable: only detect significant changes
                    if prev_hand_openness is not None and current_time - last_gesture_time > gesture_cooldown:
                        diff = avg_dist - prev_hand_openness
                        
                        # Need bigger movement to trigger zoom
                        if diff > 30:  # Hand opening wider (zoom in)
                            if zoom_direction != "in":  # Prevent rapid switching
                                cube.zoom += 0.8
                                if cube.zoom > 8:
                                    cube.zoom = 8
                                current_gesture = "ZOOM IN (Spreading fingers)"
                                last_gesture_time = current_time
                                zoom_direction = "in"
                        elif diff < -30:  # Hand closing (zoom out)
                            if zoom_direction != "out":  # Prevent rapid switching
                                cube.zoom -= 0.8
                                if cube.zoom < 1:
                                    cube.zoom = 1
                                current_gesture = "ZOOM OUT (Closing to fist)"
                                last_gesture_time = current_time
                                zoom_direction = "out"
                        else:
                            # Reset zoom direction if no significant change
                            if abs(diff) < 10:
                                zoom_direction = None
                    
                    prev_hand_openness = avg_dist
            else:
                prev_pinch_pos = None
                prev_hand_openness = None
            
            # Draw cube
            cube.draw(display)
            
            # Auto-rotate Z for effect
            cube.rotation_z += 0.3
            
            # Add small camera preview
            small_cam = cv2.resize(frame, (320, 240))
            display[10:250, 10:330] = small_cam
            
            # Display info
            y = 270
            cv2.putText(display, f"Gesture: {current_gesture}", (10, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            y += 30
            cv2.putText(display, f"Zoom: {cube.zoom:.1f}x", (10, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y += 30
            cv2.putText(display, f"Rotation X: {cube.rotation_x:.0f}", (10, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y += 25
            cv2.putText(display, f"Rotation Y: {cube.rotation_y:.0f}", (10, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Show window (force it to front)
            cv2.imshow("3D Cube - Gesture Control", display)
            cv2.setWindowProperty("3D Cube - Gesture Control", cv2.WND_PROP_TOPMOST, 1)
            
            # Handle keyboard
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # Q or ESC
                print("\nQuitting...")
                break
            elif key == ord('r'):
                print("Resetting cube...")
                cube.rotation_x = 0
                cube.rotation_y = 0
                cube.rotation_z = 0
                cube.zoom = 3
                print("✓ Cube reset!")
    
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        camera.release()
        cv2.destroyAllWindows()
        hands.close()
        print("\n" + "=" * 70)
        print("APPLICATION CLOSED")
        print("=" * 70)


if __name__ == "__main__":
    main()

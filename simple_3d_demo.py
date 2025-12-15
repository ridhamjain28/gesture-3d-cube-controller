"""
Simple 3D Object Control with Hand Gestures
Control a 3D cube with your hands - no external APIs needed!
"""

import cv2
import time
import numpy as np
from hand_tracker import HandTracker
from gesture_recognizer import GestureRecognizer
import config

class Simple3DController:
    """Simple 3D object that responds to hand gestures"""
    
    def __init__(self):
        # 3D cube vertices
        self.vertices = np.array([
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],  # Back face
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]       # Front face
        ], dtype=float)
        
        # Cube edges (which vertices connect)
        self.edges = [
            (0,1), (1,2), (2,3), (3,0),  # Back face
            (4,5), (5,6), (6,7), (7,4),  # Front face
            (0,4), (1,5), (2,6), (3,7)   # Connecting edges
        ]
        
        # Rotation angles
        self.rotation_x = 0
        self.rotation_y = 0
        self.rotation_z = 0
        
        # Scale and position
        self.scale = 100
        self.zoom = 5
        self.offset_x = 0
        self.offset_y = 0
        
        # Colors
        self.cube_color = (0, 255, 0)  # Green
        self.bg_color = (20, 20, 20)   # Dark gray
        
    def rotate_x(self, angle):
        """Rotate around X axis"""
        rad = np.radians(angle)
        rotation = np.array([
            [1, 0, 0],
            [0, np.cos(rad), -np.sin(rad)],
            [0, np.sin(rad), np.cos(rad)]
        ])
        return rotation
    
    def rotate_y(self, angle):
        """Rotate around Y axis"""
        rad = np.radians(angle)
        rotation = np.array([
            [np.cos(rad), 0, np.sin(rad)],
            [0, 1, 0],
            [-np.sin(rad), 0, np.cos(rad)]
        ])
        return rotation
    
    def rotate_z(self, angle):
        """Rotate around Z axis"""
        rad = np.radians(angle)
        rotation = np.array([
            [np.cos(rad), -np.sin(rad), 0],
            [np.sin(rad), np.cos(rad), 0],
            [0, 0, 1]
        ])
        return rotation
    
    def project(self, vertices, width, height):
        """Project 3D vertices to 2D screen"""
        # Apply rotations
        rotated = vertices.copy()
        rotated = rotated @ self.rotate_x(self.rotation_x).T
        rotated = rotated @ self.rotate_y(self.rotation_y).T
        rotated = rotated @ self.rotate_z(self.rotation_z).T
        
        # Apply zoom
        rotated = rotated * self.zoom
        
        # Project to 2D (simple perspective)
        projected = []
        for vertex in rotated:
            x, y, z = vertex
            # Simple perspective projection
            factor = 200 / (200 + z)
            x = x * factor * self.scale + width // 2 + self.offset_x
            y = y * factor * self.scale + height // 2 + self.offset_y
            projected.append((int(x), int(y)))
        
        return projected
    
    def draw(self, frame):
        """Draw the 3D cube on the frame"""
        height, width = frame.shape[:2]
        
        # Project vertices
        projected = self.project(self.vertices, width, height)
        
        # Draw edges
        for edge in self.edges:
            pt1 = projected[edge[0]]
            pt2 = projected[edge[1]]
            cv2.line(frame, pt1, pt2, self.cube_color, 2)
        
        # Draw vertices as circles
        for pt in projected:
            cv2.circle(frame, pt, 5, (255, 255, 0), -1)
        
        return frame
    
    def handle_gesture(self, gesture):
        """Handle gesture and update cube"""
        if gesture is None:
            return
        
        gesture_type = gesture.type.value
        
        if gesture_type == "swipe_left":
            self.rotation_y -= 10
        elif gesture_type == "swipe_right":
            self.rotation_y += 10
        elif gesture_type == "swipe_up":
            self.rotation_x -= 10
        elif gesture_type == "swipe_down":
            self.rotation_x += 10
        elif gesture_type == "pinch_out":
            self.zoom += 0.5
            if self.zoom > 10:
                self.zoom = 10
        elif gesture_type == "pinch_in":
            self.zoom -= 0.5
            if self.zoom < 1:
                self.zoom = 1
        elif gesture_type == "palm_open":
            # Reset view
            self.rotation_x = 0
            self.rotation_y = 0
            self.rotation_z = 0
            self.zoom = 5
            self.offset_x = 0
            self.offset_y = 0
        
        return gesture_type


def main():
    """Main application loop"""
    print("=" * 60)
    print("HAND-CONTROLLED 3D CUBE")
    print("=" * 60)
    print("\nInitializing...")
    
    # Initialize components
    hand_tracker = HandTracker()
    gesture_recognizer = GestureRecognizer(hand_tracker)
    cube_controller = Simple3DController()
    
    # Open camera
    camera = cv2.VideoCapture(config.CAMERA_INDEX)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
    
    if not camera.isOpened():
        print("✗ Error: Could not open camera")
        return
    
    print("✓ Camera opened")
    print("\n" + "=" * 60)
    print("CONTROLS:")
    print("=" * 60)
    print("👋 SWIPE LEFT/RIGHT → Rotate cube horizontally")
    print("👋 SWIPE UP/DOWN → Rotate cube vertically")
    print("🤏 PINCH APART → Zoom in")
    print("🤏 PINCH TOGETHER → Zoom out")
    print("✋ OPEN PALM → Reset cube")
    print("Q → Quit")
    print("=" * 60)
    print("\n✓ Ready! Show your hand to the camera...\n")
    
    # Main loop
    fps_time = time.time()
    frame_count = 0
    last_gesture_name = "None"
    
    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                print("✗ Error reading frame")
                break
            
            # Flip horizontally to make it mirror-like (fixes the left/right issue!)
            frame = cv2.flip(frame, 1)
            
            # Create display frame
            display = np.ones_like(frame) * 20  # Dark background
            
            # Track hand
            processed_frame, landmarks, handedness = hand_tracker.process_frame(frame)
            
            # Recognize gesture
            gesture = gesture_recognizer.recognize(landmarks)
            
            # Handle gesture
            if gesture:
                gesture_name = cube_controller.handle_gesture(gesture)
                if gesture_name:
                    last_gesture_name = gesture_name.replace("_", " ").upper()
            
            # Draw cube on dark background
            display = cube_controller.draw(display)
            
            # Combine camera feed (small) with 3D view
            small_cam = cv2.resize(processed_frame, (320, 240))
            display[10:250, 10:330] = small_cam
            
            # Display info
            frame_count += 1
            if time.time() - fps_time > 1:
                fps = frame_count / (time.time() - fps_time)
                frame_count = 0
                fps_time = time.time()
            else:
                fps = 0
            
            # Info panel
            y_pos = 270
            cv2.putText(display, f"FPS: {fps:.1f}", (10, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_pos += 30
            cv2.putText(display, f"Gesture: {last_gesture_name}", (10, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            y_pos += 30
            cv2.putText(display, f"Zoom: {cube_controller.zoom:.1f}", (10, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_pos += 30
            cv2.putText(display, f"Rotation: X={cube_controller.rotation_x:.0f} Y={cube_controller.rotation_y:.0f}", 
                       (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Auto-rotate slightly for cool effect
            cube_controller.rotation_z += 0.5
            
            # Show display
            cv2.imshow("3D Cube Controller", display)
            
            # Handle keyboard
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\nQuitting...")
                break
            elif key == ord('r'):
                print("Resetting cube...")
                cube_controller.rotation_x = 0
                cube_controller.rotation_y = 0
                cube_controller.rotation_z = 0
                cube_controller.zoom = 5
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    
    finally:
        camera.release()
        cv2.destroyAllWindows()
        hand_tracker.release()
        print("\n" + "=" * 60)
        print("APPLICATION CLOSED")
        print("=" * 60)


if __name__ == "__main__":
    main()

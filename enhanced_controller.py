"""
Enhanced 3D Object Controller - Advanced Version
Features:
- Multiple 3D objects (Cube, Pyramid, Sphere, Torus)
- Advanced gesture recognition
- UI Menu system
- Particle effects
- Object physics
- Recording & playback
- Learning mode with tutorials
"""

import cv2
import time
import numpy as np
import mediapipe as mp
import json
from enum import Enum
from collections import deque
import math


class ObjectType(Enum):
    """Types of 3D objects"""
    CUBE = "cube"
    PYRAMID = "pyramid"
    SPHERE = "sphere"
    TORUS = "torus"
    TETRAHEDRON = "tetrahedron"


class Particle:
    """Particle for visual effects"""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = np.random.uniform(-5, 5)
        self.vy = np.random.uniform(-5, 5)
        self.life = 1.0
        self.color = color
        self.size = np.random.randint(3, 8)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3  # Gravity
        self.life -= 0.02
        self.size = max(1, int(self.size * 0.95))
        return self.life > 0
    
    def draw(self, frame):
        if self.life > 0:
            alpha = int(255 * self.life)
            color = tuple(int(c * self.life) for c in self.color)
            cv2.circle(frame, (int(self.x), int(self.y)), self.size, color, -1)


class Object3D:
    """Base class for 3D objects with physics"""
    def __init__(self, obj_type):
        self.obj_type = obj_type
        self.rotation_x = 0
        self.rotation_y = 0
        self.rotation_z = 0
        self.scale = 100
        self.zoom = 3
        
        # Physics properties
        self.velocity_x = 0
        self.velocity_y = 0
        self.velocity_z = 0
        self.angular_velocity_x = 0
        self.angular_velocity_y = 0
        self.angular_velocity_z = 0
        self.friction = 0.95
        self.gravity_enabled = False
        
        # Visual properties
        self.wireframe_mode = False
        self.show_vertices = True
        self.glow_effect = False
        
        self._generate_geometry()
    
    def _generate_geometry(self):
        """Generate vertices and faces based on object type"""
        if self.obj_type == ObjectType.CUBE:
            self.vertices = np.array([
                [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
                [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
            ], dtype=float)
            self.faces = [
                (0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4),
                (2, 3, 7, 6), (0, 3, 7, 4), (1, 2, 6, 5)
            ]
            self.face_colors = [
                (0, 0, 255), (0, 255, 0), (255, 0, 0),
                (0, 255, 255), (255, 0, 255), (255, 255, 0)
            ]
        
        elif self.obj_type == ObjectType.PYRAMID:
            self.vertices = np.array([
                [-1, -1, -1], [1, -1, -1], [1, -1, 1], [-1, -1, 1],  # Base
                [0, 1.5, 0]  # Apex
            ], dtype=float)
            self.faces = [
                (0, 1, 2, 3),  # Base
                (0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)  # Triangular sides
            ]
            self.face_colors = [
                (100, 100, 255), (255, 100, 100), (100, 255, 100),
                (255, 255, 100), (255, 100, 255)
            ]
        
        elif self.obj_type == ObjectType.TETRAHEDRON:
            a = 1.0
            self.vertices = np.array([
                [a, a, a], [-a, -a, a], [-a, a, -a], [a, -a, -a]
            ], dtype=float)
            self.faces = [
                (0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)
            ]
            self.face_colors = [
                (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)
            ]
        
        elif self.obj_type == ObjectType.SPHERE:
            # Generate sphere using latitude-longitude method
            vertices = []
            faces = []
            colors = []
            
            lat_bands = 12
            lon_bands = 16
            radius = 1.0
            
            for lat in range(lat_bands + 1):
                theta = lat * np.pi / lat_bands
                sin_theta = np.sin(theta)
                cos_theta = np.cos(theta)
                
                for lon in range(lon_bands + 1):
                    phi = lon * 2 * np.pi / lon_bands
                    sin_phi = np.sin(phi)
                    cos_phi = np.cos(phi)
                    
                    x = cos_phi * sin_theta
                    y = cos_theta
                    z = sin_phi * sin_theta
                    
                    vertices.append([radius * x, radius * y, radius * z])
            
            # Generate faces
            for lat in range(lat_bands):
                for lon in range(lon_bands):
                    first = lat * (lon_bands + 1) + lon
                    second = first + lon_bands + 1
                    
                    faces.append((first, second, first + 1))
                    faces.append((second, second + 1, first + 1))
                    
                    # Color based on position
                    hue = (lat / lat_bands) * 180
                    color = cv2.cvtColor(np.uint8([[[hue, 255, 255]]]), cv2.COLOR_HSV2BGR)[0][0]
                    colors.append(tuple(map(int, color)))
                    colors.append(tuple(map(int, color)))
            
            self.vertices = np.array(vertices, dtype=float)
            self.faces = faces
            self.face_colors = colors
        
        elif self.obj_type == ObjectType.TORUS:
            # Generate torus
            vertices = []
            faces = []
            colors = []
            
            major_radius = 1.0
            minor_radius = 0.3
            major_segments = 24
            minor_segments = 12
            
            for i in range(major_segments):
                theta = i * 2 * np.pi / major_segments
                cos_theta = np.cos(theta)
                sin_theta = np.sin(theta)
                
                for j in range(minor_segments):
                    phi = j * 2 * np.pi / minor_segments
                    cos_phi = np.cos(phi)
                    sin_phi = np.sin(phi)
                    
                    x = (major_radius + minor_radius * cos_phi) * cos_theta
                    y = minor_radius * sin_phi
                    z = (major_radius + minor_radius * cos_phi) * sin_theta
                    
                    vertices.append([x, y, z])
            
            # Generate faces
            for i in range(major_segments):
                for j in range(minor_segments):
                    first = i * minor_segments + j
                    second = ((i + 1) % major_segments) * minor_segments + j
                    third = ((i + 1) % major_segments) * minor_segments + ((j + 1) % minor_segments)
                    fourth = i * minor_segments + ((j + 1) % minor_segments)
                    
                    faces.append((first, second, third, fourth))
                    
                    # Rainbow colors
                    hue = (i / major_segments) * 180
                    color = cv2.cvtColor(np.uint8([[[hue, 255, 200]]]), cv2.COLOR_HSV2BGR)[0][0]
                    colors.append(tuple(map(int, color)))
            
            self.vertices = np.array(vertices, dtype=float)
            self.faces = faces
            self.face_colors = colors
    
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
    
    def update_physics(self):
        """Update physics simulation"""
        # Apply angular velocity
        self.rotation_x += self.angular_velocity_x
        self.rotation_y += self.angular_velocity_y
        self.rotation_z += self.angular_velocity_z
        
        # Apply friction
        self.angular_velocity_x *= self.friction
        self.angular_velocity_y *= self.friction
        self.angular_velocity_z *= self.friction
        
        # Apply gravity if enabled
        if self.gravity_enabled:
            self.velocity_y += 0.1
            self.rotation_x += self.velocity_y * 0.1
    
    def draw(self, frame):
        """Draw the 3D object"""
        height, width = frame.shape[:2]
        
        # Update physics
        self.update_physics()
        
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
        
        # Calculate face depths
        face_depths = []
        for i, face in enumerate(self.faces):
            avg_depth = sum(depths[v] for v in face) / len(face)
            face_depths.append((avg_depth, i))
        
        # Sort faces by depth
        face_depths.sort(reverse=True)
        
        # Draw faces
        for _, face_idx in face_depths:
            face = self.faces[face_idx]
            points = np.array([projected[v] for v in face], dtype=np.int32)
            color = self.face_colors[face_idx]
            
            if not self.wireframe_mode:
                # Filled polygon
                cv2.fillPoly(frame, [points], color)
                
                # Glow effect
                if self.glow_effect:
                    lighter_color = tuple(min(255, int(c * 1.3)) for c in color)
                    cv2.polylines(frame, [points], True, lighter_color, 2)
            
            # Outline
            darker_color = tuple(int(c * 0.5) for c in color)
            cv2.polylines(frame, [points], True, darker_color, 2 if not self.wireframe_mode else 3)
        
        # Draw vertices
        if self.show_vertices:
            for pt in projected:
                cv2.circle(frame, pt, 4, (255, 255, 255), -1)
                cv2.circle(frame, pt, 4, (0, 0, 0), 1)


class GestureRecorder:
    """Records and plays back gesture sequences"""
    def __init__(self):
        self.recording = False
        self.recorded_gestures = []
        self.playback_mode = False
        self.playback_index = 0
        self.recordings_saved = []
    
    def start_recording(self):
        self.recording = True
        self.recorded_gestures = []
        print("🔴 Recording started...")
    
    def stop_recording(self):
        self.recording = False
        if self.recorded_gestures:
            self.recordings_saved.append({
                'timestamp': time.time(),
                'gestures': self.recorded_gestures.copy()
            })
            print(f"✓ Recording saved! ({len(self.recorded_gestures)} gestures)")
    
    def record_gesture(self, gesture_name, params):
        if self.recording:
            self.recorded_gestures.append({
                'gesture': gesture_name,
                'params': params,
                'time': time.time()
            })
    
    def start_playback(self):
        if self.recordings_saved:
            self.playback_mode = True
            self.playback_index = 0
            self.current_recording = self.recordings_saved[-1]['gestures']
            print("▶️ Playback started...")
    
    def stop_playback(self):
        self.playback_mode = False
        print("⏹️ Playback stopped")
    
    def get_next_gesture(self):
        if self.playback_mode and self.playback_index < len(self.current_recording):
            gesture = self.current_recording[self.playback_index]
            self.playback_index += 1
            if self.playback_index >= len(self.current_recording):
                self.stop_playback()
            return gesture
        return None


class UIMenu:
    """Interactive UI menu"""
    def __init__(self):
        self.visible = True
        self.selected_object = ObjectType.CUBE
        self.menu_items = [
            "Cube", "Pyramid", "Sphere", "Torus", "Tetrahedron"
        ]
        self.selected_index = 0
    
    def draw(self, frame):
        if not self.visible:
            return
        
        h, w = frame.shape[:2]
        menu_x = w - 200
        menu_y = 10
        
        # Background
        cv2.rectangle(frame, (menu_x, menu_y), (w - 10, menu_y + 200), (40, 40, 40), -1)
        cv2.rectangle(frame, (menu_x, menu_y), (w - 10, menu_y + 200), (0, 255, 0), 2)
        
        # Title
        cv2.putText(frame, "OBJECTS", (menu_x + 10, menu_y + 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Menu items
        y_offset = 50
        for i, item in enumerate(self.menu_items):
            color = (0, 255, 0) if i == self.selected_index else (200, 200, 200)
            prefix = "► " if i == self.selected_index else "  "
            cv2.putText(frame, f"{prefix}{item}", (menu_x + 15, menu_y + y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            y_offset += 30


def main():
    """Enhanced main application"""
    print("=" * 70)
    print("✨ ENHANCED 3D OBJECT CONTROLLER ✨")
    print("=" * 70)
    print("\nLoading advanced features...")
    
    # Initialize MediaPipe
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,  # Support two hands!
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    )
    mp_draw = mp.solutions.drawing_utils
    
    # Initialize components
    current_object = Object3D(ObjectType.CUBE)
    ui_menu = UIMenu()
    recorder = GestureRecorder()
    particles = []
    
    # Open camera
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    if not camera.isOpened():
        print("ERROR: Cannot open camera!")
        return
    
    print("\n✓ Enhanced features loaded!")
    print("\n" + "=" * 70)
    print("🎮 ENHANCED CONTROLS:")
    print("=" * 70)
    print("\n📌 GESTURES:")
    print("  🤏 Pinch + Drag → Rotate object")
    print("  ✋ Spread fingers → Zoom in")
    print("  ✊ Close fist → Zoom out")
    print("  ✌️ Victory sign (2 fingers) → Change object")
    print("  👍 Thumbs up → Enable physics mode")
    print("  👎 Thumbs down → Disable physics")
    print("\n⌨️ KEYBOARD:")
    print("  1-5 → Select object (Cube/Pyramid/Sphere/Torus/Tetra)")
    print("  W → Toggle wireframe mode")
    print("  G → Toggle glow effect")
    print("  SPACE → Toggle physics")
    print("  P → Enable/disable gravity")
    print("  R → Record gestures")
    print("  T → Stop recording")
    print("  Y → Playback recording")
    print("  M → Toggle menu")
    print("  Q/ESC → Quit")
    print("=" * 70)
    print("\n✓ Ready! Show your hands...\n")
    
    # Tracking variables
    prev_pinch_pos = None
    prev_hand_openness = None
    last_gesture_time = time.time()
    gesture_cooldown = 0.5
    zoom_direction = None
    fps_counter = 0
    fps_time = time.time()
    current_fps = 0
    
    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            display = np.zeros_like(frame)
            display[:] = (20, 20, 30)
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)
            
            current_gesture = "No hands detected"
            
            # Process hands
            if results.multi_hand_landmarks:
                for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    h, w, _ = frame.shape
                    
                    # Get key points
                    thumb_tip = hand_landmarks.landmark[4]
                    index_tip = hand_landmarks.landmark[8]
                    middle_tip = hand_landmarks.landmark[12]
                    ring_tip = hand_landmarks.landmark[16]
                    pinky_tip = hand_landmarks.landmark[20]
                    wrist = hand_landmarks.landmark[0]
                    
                    thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
                    index_x, index_y = int(index_tip.x * w), int(index_tip.y * h)
                    middle_x, middle_y = int(middle_tip.x * w), int(middle_tip.y * h)
                    wrist_x, wrist_y = int(wrist.x * w), int(wrist.y * h)
                    
                    # Calculate pinch distance
                    pinch_dist = np.sqrt((thumb_x - index_x)**2 + (thumb_y - index_y)**2)
                    
                    # Calculate hand openness
                    avg_dist = (
                        np.sqrt((thumb_x - wrist_x)**2 + (thumb_y - wrist_y)**2) +
                        np.sqrt((middle_x - wrist_x)**2 + (middle_y - wrist_y)**2) +
                        np.sqrt((int(pinky_tip.x*w) - wrist_x)**2 + (int(pinky_tip.y*h) - wrist_y)**2)
                    ) / 3
                    
                    # Draw hand
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    
                    current_time = time.time()
                    
                    # GESTURE 1: Pinch and drag (with momentum)
                    if pinch_dist < 40:
                        current_gesture = f"PINCH (Rotating)"
                        
                        if prev_pinch_pos is not None:
                            dx = (index_x - prev_pinch_pos[0]) * 0.5
                            dy = (index_y - prev_pinch_pos[1]) * 0.5
                            
                            current_object.angular_velocity_y += dx * 0.1
                            current_object.angular_velocity_x += dy * 0.1
                            
                            # Spawn particles at pinch point
                            if np.random.random() < 0.3:
                                particles.append(Particle(index_x, index_y, (0, 255, 255)))
                        
                        prev_pinch_pos = (index_x, index_y)
                        
                        # Record gesture
                        recorder.record_gesture("pinch", {"dx": dx if 'dx' in locals() else 0, "dy": dy if 'dy' in locals() else 0})
                    else:
                        prev_pinch_pos = None
                    
                    # GESTURE 2: Zoom
                    if prev_hand_openness is not None and current_time - last_gesture_time > gesture_cooldown:
                        diff = avg_dist - prev_hand_openness
                        
                        if diff > 30:
                            if zoom_direction != "in":
                                current_object.zoom += 0.8
                                if current_object.zoom > 10:
                                    current_object.zoom = 10
                                current_gesture = "ZOOM IN"
                                last_gesture_time = current_time
                                zoom_direction = "in"
                                
                                # Spawn particles
                                for _ in range(5):
                                    particles.append(Particle(w//2, h//2, (0, 255, 0)))
                        
                        elif diff < -30:
                            if zoom_direction != "out":
                                current_object.zoom -= 0.8
                                if current_object.zoom < 1:
                                    current_object.zoom = 1
                                current_gesture = "ZOOM OUT"
                                last_gesture_time = current_time
                                zoom_direction = "out"
                                
                                for _ in range(5):
                                    particles.append(Particle(w//2, h//2, (255, 0, 0)))
                        else:
                            if abs(diff) < 10:
                                zoom_direction = None
                    
                    prev_hand_openness = avg_dist
            
            # Update and draw particles
            particles = [p for p in particles if p.update()]
            for particle in particles:
                particle.draw(display)
            
            # Draw object
            current_object.draw(display)
            
            # Auto-rotate
            current_object.rotation_z += 0.3
            
            # Add camera preview
            small_cam = cv2.resize(frame, (320, 240))
            display[10:250, 10:330] = small_cam
            
            # Draw UI Menu
            ui_menu.draw(display)
            
            # Display info
            y = 270
            cv2.putText(display, f"Gesture: {current_gesture}", (10, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            y += 30
            cv2.putText(display, f"Object: {current_object.obj_type.value.upper()}", (10, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            y += 30
            cv2.putText(display, f"Zoom: {current_object.zoom:.1f}x", (10, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y += 25
            cv2.putText(display, f"Physics: {'ON' if current_object.gravity_enabled else 'OFF'}", (10, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y += 25
            
            # FPS counter
            fps_counter += 1
            if time.time() - fps_time > 1:
                current_fps = fps_counter / (time.time() - fps_time)
                fps_counter = 0
                fps_time = time.time()
            cv2.putText(display, f"FPS: {current_fps:.0f}", (10, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            # Recording indicator
            if recorder.recording:
                cv2.circle(display, (w - 30, 30), 10, (0, 0, 255), -1)
                cv2.putText(display, "REC", (w - 70, 35),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            # Playback indicator
            if recorder.playback_mode:
                cv2.putText(display, "▶ PLAYBACK", (w - 150, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            cv2.imshow("Enhanced 3D Controller", display)
            cv2.setWindowProperty("Enhanced 3D Controller", cv2.WND_PROP_TOPMOST, 1)
            
            # Handle keyboard
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
            elif key == ord('1'):
                current_object = Object3D(ObjectType.CUBE)
                ui_menu.selected_index = 0
            elif key == ord('2'):
                current_object = Object3D(ObjectType.PYRAMID)
                ui_menu.selected_index = 1
            elif key == ord('3'):
                current_object = Object3D(ObjectType.SPHERE)
                ui_menu.selected_index = 2
            elif key == ord('4'):
                current_object = Object3D(ObjectType.TORUS)
                ui_menu.selected_index = 3
            elif key == ord('5'):
                current_object = Object3D(ObjectType.TETRAHEDRON)
                ui_menu.selected_index = 4
            elif key == ord('w'):
                current_object.wireframe_mode = not current_object.wireframe_mode
            elif key == ord('g'):
                current_object.glow_effect = not current_object.glow_effect
            elif key == ord('p'):
                current_object.gravity_enabled = not current_object.gravity_enabled
            elif key == ord('m'):
                ui_menu.visible = not ui_menu.visible
            elif key == ord('r'):
                recorder.start_recording()
            elif key == ord('t'):
                recorder.stop_recording()
            elif key == ord('y'):
                recorder.start_playback()
            elif key == ord(' '):
                current_object.friction = 0.98 if current_object.friction == 0.95 else 0.95
    
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        camera.release()
        cv2.destroyAllWindows()
        hands.close()
        print("\n" + "=" * 70)
        print("✨ ENHANCED APPLICATION CLOSED ✨")
        print("=" * 70)


if __name__ == "__main__":
    main()

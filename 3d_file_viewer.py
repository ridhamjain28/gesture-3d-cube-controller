"""
3D File Viewer with Gesture Control
Supports: OBJ, STL, PLY files
Control any 3D model with hand gestures!
"""

import cv2
import numpy as np
import mediapipe as mp
import time
import os
from pathlib import Path

class Model3D:
    """Load and display 3D models from various file formats"""
    
    def __init__(self):
        self.vertices = []
        self.faces = []
        self.edges = []
        self.rotation_x = 0
        self.rotation_y = 0
        self.rotation_z = 0
        self.zoom = 3
        self.scale = 100
        self.glow_intensity = 0
        self.model_name = "No Model"
        
    def load_obj(self, filepath):
        """Load OBJ file"""
        vertices = []
        faces = []
        
        with open(filepath, 'r') as f:
            for line in f:
                if line.startswith('v '):
                    # Vertex
                    parts = line.split()
                    vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
                elif line.startswith('f '):
                    # Face
                    parts = line.split()
                    face = []
                    for part in parts[1:]:
                        # Handle format: vertex/texture/normal or vertex//normal or just vertex
                        vertex_idx = int(part.split('/')[0]) - 1
                        face.append(vertex_idx)
                    faces.append(face)
        
        self.vertices = np.array(vertices, dtype=float)
        self.faces = faces
        self.model_name = Path(filepath).stem
        
        # Normalize model to unit cube
        self._normalize()
        
        # Generate edges from faces
        self._generate_edges()
        
        return True
    
    def load_stl(self, filepath):
        """Load STL file (ASCII or Binary)"""
        vertices = []
        faces = []
        
        # Try reading as ASCII first
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                if 'vertex' in content:
                    # ASCII STL
                    lines = content.split('\n')
                    current_vertices = []
                    for line in lines:
                        if 'vertex' in line:
                            parts = line.split()
                            v = [float(parts[1]), float(parts[2]), float(parts[3])]
                            current_vertices.append(v)
                            if len(current_vertices) == 3:
                                # Add vertices
                                idx = len(vertices)
                                vertices.extend(current_vertices)
                                faces.append([idx, idx+1, idx+2])
                                current_vertices = []
        except:
            # Binary STL
            with open(filepath, 'rb') as f:
                f.seek(80)  # Skip header
                num_triangles = int.from_bytes(f.read(4), 'little')
                
                for _ in range(num_triangles):
                    f.read(12)  # Skip normal
                    current_vertices = []
                    for _ in range(3):
                        v = [
                            float(np.frombuffer(f.read(4), dtype=np.float32)[0]),
                            float(np.frombuffer(f.read(4), dtype=np.float32)[0]),
                            float(np.frombuffer(f.read(4), dtype=np.float32)[0])
                        ]
                        current_vertices.append(v)
                    idx = len(vertices)
                    vertices.extend(current_vertices)
                    faces.append([idx, idx+1, idx+2])
                    f.read(2)  # Skip attribute
        
        self.vertices = np.array(vertices, dtype=float)
        self.faces = faces
        self.model_name = Path(filepath).stem
        self._normalize()
        self._generate_edges()
        return True
    
    def load_ply(self, filepath):
        """Load PLY file (ASCII)"""
        vertices = []
        faces = []
        reading_vertices = False
        reading_faces = False
        num_vertices = 0
        num_faces = 0
        vertex_count = 0
        face_count = 0
        
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                
                if line.startswith('element vertex'):
                    num_vertices = int(line.split()[-1])
                elif line.startswith('element face'):
                    num_faces = int(line.split()[-1])
                elif line == 'end_header':
                    reading_vertices = True
                    continue
                
                if reading_vertices and vertex_count < num_vertices:
                    parts = line.split()
                    vertices.append([float(parts[0]), float(parts[1]), float(parts[2])])
                    vertex_count += 1
                    if vertex_count >= num_vertices:
                        reading_vertices = False
                        reading_faces = True
                elif reading_faces and face_count < num_faces:
                    parts = line.split()
                    num_verts = int(parts[0])
                    face = [int(parts[i+1]) for i in range(num_verts)]
                    faces.append(face)
                    face_count += 1
        
        self.vertices = np.array(vertices, dtype=float)
        self.faces = faces
        self.model_name = Path(filepath).stem
        self._normalize()
        self._generate_edges()
        return True
    
    def _normalize(self):
        """Normalize model to fit in unit cube centered at origin"""
        if len(self.vertices) == 0:
            return
        
        # Center the model
        center = np.mean(self.vertices, axis=0)
        self.vertices -= center
        
        # Scale to unit cube
        max_extent = np.max(np.abs(self.vertices))
        if max_extent > 0:
            self.vertices /= max_extent
    
    def _generate_edges(self):
        """Generate edges from faces for wireframe rendering"""
        edge_set = set()
        for face in self.faces:
            for i in range(len(face)):
                v1 = face[i]
                v2 = face[(i + 1) % len(face)]
                edge = tuple(sorted([v1, v2]))
                edge_set.add(edge)
        self.edges = list(edge_set)
    
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
    
    def draw(self, frame, wireframe=False):
        """Draw the 3D model"""
        if len(self.vertices) == 0:
            return
        
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
        
        if wireframe:
            # Draw wireframe
            for edge in self.edges:
                v1, v2 = edge
                if v1 < len(projected) and v2 < len(projected):
                    color = (0, 255, 0) if self.glow_intensity == 0 else (0, 255, 255)
                    cv2.line(frame, projected[v1], projected[v2], color, 1)
        else:
            # Draw filled faces with depth sorting
            face_depths = []
            for i, face in enumerate(self.faces):
                if all(v < len(depths) for v in face):
                    avg_depth = sum(depths[v] for v in face) / len(face)
                    face_depths.append((avg_depth, i))
            
            face_depths.sort(reverse=True)
            
            # Draw faces
            for _, face_idx in face_depths:
                face = self.faces[face_idx]
                if all(v < len(projected) for v in face):
                    points = np.array([projected[v] for v in face], dtype=np.int32)
                    
                    # Color based on depth
                    depth_color = int(128 + 127 * np.sin(face_depths[0][0] * 0.1))
                    color = (depth_color, 100, 200)
                    
                    if self.glow_intensity > 0:
                        color = tuple(min(255, int(c + self.glow_intensity * 50)) for c in color)
                    
                    cv2.fillPoly(frame, [points], color)
                    cv2.polylines(frame, [points], True, (50, 50, 50), 1)
        
        # Fade glow
        self.glow_intensity = max(0, self.glow_intensity - 0.05)


def calculate_distance(point1, point2):
    """Calculate distance between two points"""
    return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


def main():
    print("=" * 80)
    print("3D FILE VIEWER WITH GESTURE CONTROL - ULTRA SMOOTH")
    print("=" * 80)
    print("\nSupported formats: .obj, .stl, .ply")
    print("\n" + "=" * 80)
    
    # File selection
    print("\nLooking for 3D files in current directory...")
    supported_exts = ['.obj', '.stl', '.ply']
    files = []
    for ext in supported_exts:
        files.extend(list(Path('.').glob(f'*{ext}')))
    
    if not files:
        print("\n❌ No 3D files found in current directory!")
        print("\nPlace your .obj, .stl, or .ply files here and restart.")
        input("\nPress Enter to exit...")
        return
    
    print("\nAvailable 3D files:")
    for i, f in enumerate(files):
        print(f"  {i+1}. {f.name}")
    
    # Load default or let user choose
    if len(files) == 1:
        selected_file = files[0]
        print(f"\n✓ Auto-loading: {selected_file.name}")
    else:
        try:
            choice = input(f"\nSelect file (1-{len(files)}) or press Enter for first: ").strip()
            if choice == "":
                selected_file = files[0]
            else:
                selected_file = files[int(choice) - 1]
        except:
            selected_file = files[0]
    
    # Load model
    model = Model3D()
    print(f"\n📁 Loading {selected_file.name}...")
    
    try:
        if selected_file.suffix.lower() == '.obj':
            model.load_obj(str(selected_file))
        elif selected_file.suffix.lower() == '.stl':
            model.load_stl(str(selected_file))
        elif selected_file.suffix.lower() == '.ply':
            model.load_ply(str(selected_file))
        
        print(f"✓ Loaded: {len(model.vertices)} vertices, {len(model.faces)} faces")
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        input("\nPress Enter to exit...")
        return
    
    # Initialize MediaPipe - ULTRA OPTIMIZED
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        model_complexity=0,  # Lite mode
        min_detection_confidence=0.5,  # Lower for speed
        min_tracking_confidence=0.5
    )
    mp_draw = mp.solutions.drawing_utils
    
    # Open camera - ULTRA OPTIMIZED
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 480)  # Even lower for smoothness
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
    camera.set(cv2.CAP_PROP_FPS, 30)
    camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer lag
    
    if not camera.isOpened():
        print("❌ Cannot open camera!")
        return
    
    print("\n" + "=" * 80)
    print("CONTROLS:")
    print("=" * 80)
    print("🤏 PINCH + MOVE     → Rotate model")
    print("✋ SPREAD FINGERS   → Zoom IN")
    print("✊ CLOSE FIST       → Zoom OUT")
    print("W key              → Toggle Wireframe")
    print("R key              → Reset view")
    print("Q key              → Quit")
    print("=" * 80)
    print("\n✓ READY! Show your hand...\n")
    
    # Tracking variables
    prev_pinch_pos = None
    prev_hand_openness = None
    wireframe_mode = False
    
    # FPS tracking
    fps_counter = 0
    fps_start_time = time.time()
    current_fps = 0
    frame_skip = 0
    
    # Main loop
    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                break
            
            # FPS calculation
            fps_counter += 1
            if time.time() - fps_start_time >= 1.0:
                current_fps = fps_counter
                fps_counter = 0
                fps_start_time = time.time()
            
            # Frame skipping for smoother FPS (process every other frame)
            frame_skip += 1
            process_gestures = (frame_skip % 2 == 0)
            
            frame = cv2.flip(frame, 1)
            display = np.zeros_like(frame)
            display[:] = (20, 20, 20)
            
            current_gesture = "NO HAND"
            
            if process_gestures:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb_frame)
                
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        h, w, _ = frame.shape
                        
                        thumb_tip = hand_landmarks.landmark[4]
                        index_tip = hand_landmarks.landmark[8]
                        middle_tip = hand_landmarks.landmark[12]
                        pinky_tip = hand_landmarks.landmark[20]
                        wrist = hand_landmarks.landmark[0]
                        
                        thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
                        index_x, index_y = int(index_tip.x * w), int(index_tip.y * h)
                        wrist_x, wrist_y = int(wrist.x * w), int(wrist.y * h)
                        
                        pinch_dist = calculate_distance((thumb_x, thumb_y), (index_x, index_y))
                        
                        avg_dist = (
                            calculate_distance((thumb_x, thumb_y), (wrist_x, wrist_y)) +
                            calculate_distance((int(middle_tip.x*w), int(middle_tip.y*h)), (wrist_x, wrist_y)) +
                            calculate_distance((int(pinky_tip.x*w), int(pinky_tip.y*h)), (wrist_x, wrist_y))
                        ) / 3
                        
                        mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                        
                        # PINCH AND DRAG
                        if pinch_dist < 40:
                            current_gesture = "PINCH → ROTATING"
                            
                            if prev_pinch_pos is not None:
                                dx = index_x - prev_pinch_pos[0]
                                dy = index_y - prev_pinch_pos[1]
                                
                                if abs(dx) > 3:
                                    model.rotation_y += dx * 0.8  # Smoother rotation
                                    model.glow_intensity = 1.0
                                if abs(dy) > 3:
                                    model.rotation_x += dy * 0.8
                                    model.glow_intensity = 1.0
                            
                            prev_pinch_pos = (index_x, index_y)
                        else:
                            prev_pinch_pos = None
                        
                        # ZOOM
                        if prev_hand_openness is not None:
                            diff = avg_dist - prev_hand_openness
                            
                            if diff > 25:
                                model.zoom += 0.5
                                model.glow_intensity = 1.0
                                if model.zoom > 10:
                                    model.zoom = 10
                                current_gesture = "ZOOM IN"
                            elif diff < -25:
                                model.zoom -= 0.5
                                model.glow_intensity = 1.0
                                if model.zoom < 1:
                                    model.zoom = 1
                                current_gesture = "ZOOM OUT"
                        
                        prev_hand_openness = avg_dist
            
            # Draw model
            model.draw(display, wireframe=wireframe_mode)
            
            # Auto-rotate Z for effect
            model.rotation_z += 0.2
            
            # Small preview
            small_cam = cv2.resize(frame, (160, 120))
            display[10:130, 10:170] = small_cam
            
            # Info display
            y = 145
            cv2.putText(display, f"Model: {model.model_name}", (10, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            y += 20
            cv2.putText(display, f"Gesture: {current_gesture}", (10, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            y += 20
            cv2.putText(display, f"Zoom: {model.zoom:.1f}x", (10, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y += 20
            mode_text = "WIREFRAME" if wireframe_mode else "SOLID"
            cv2.putText(display, f"Mode: {mode_text}", (10, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # FPS
            fps_color = (0, 255, 0) if current_fps >= 28 else (0, 165, 255) if current_fps >= 25 else (0, 0, 255)
            cv2.putText(display, f"FPS: {current_fps}", (display.shape[1] - 100, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, fps_color, 2)
            
            cv2.imshow("3D File Viewer - Gesture Control", display)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
            elif key == ord('r'):
                model.rotation_x = 0
                model.rotation_y = 0
                model.rotation_z = 0
                model.zoom = 3
            elif key == ord('w'):
                wireframe_mode = not wireframe_mode
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        camera.release()
        cv2.destroyAllWindows()
        hands.close()
        print("\n" + "=" * 80)
        print("APPLICATION CLOSED")
        print("=" * 80)


if __name__ == "__main__":
    main()

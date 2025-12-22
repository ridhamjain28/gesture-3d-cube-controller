"""
Main Application Entry Point
Integrates hand tracking, gesture recognition, and Earth control
Run this script to start the gesture-controlled Earth system
"""

import cv2
import time
import signal
import sys
from hand_tracker import HandTracker
from gesture_recognizer import GestureRecognizer
from gesture_mapper import GestureMapper
from earth_controller import EarthController
import config


class GestureEarthApp:
    """Main application class that integrates all components"""
    
    def __init__(self):
        """Initialize all components"""
        print("=" * 60)
        print("GESTURE-CONTROLLED EARTH NAVIGATION SYSTEM")
        print("=" * 60)
        print("\nInitializing components...")
        
        # Initialize components
        self.hand_tracker = HandTracker()
        self.gesture_recognizer = GestureRecognizer(self.hand_tracker)
        self.gesture_mapper = GestureMapper()
        self.earth_controller = EarthController()
        
        # Camera capture
        self.camera = None
        
        # Application state
        self.running = False
        
        print("\n✓ All components initialized successfully!")
        
    def initialize_camera(self):
        """Initialize camera capture"""
        print(f"\nOpening camera {config.CAMERA_INDEX}...")
        
        self.camera = cv2.VideoCapture(config.CAMERA_INDEX)
        
        if not self.camera.isOpened():
            print("✗ Error: Could not open camera")
            print("\nTroubleshooting tips:")
            print("  1. Check if another application is using the camera")
            print("  2. Try different CAMERA_INDEX values in config.py (0, 1, 2)")
            print("  3. Check camera permissions in system settings")
            return False
        
        # Set camera properties
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
        self.camera.set(cv2.CAP_PROP_FPS, config.FPS_TARGET)
        
        # Verify settings
        actual_width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
        
        print(f"✓ Camera opened: {int(actual_width)}x{int(actual_height)}")
        
        return True
    
    def start(self):
        """Start the application"""
        print("\n" + "=" * 60)
        print("STARTING APPLICATION")
        print("=" * 60)
        
        # Initialize camera
        if not self.initialize_camera():
            return
        
        # Start Earth controller web server
        print("\nStarting Earth visualization...")
        self.earth_controller.start_server()
        
        # Print instructions
        self.print_instructions()
        
        # Main loop
        self.running = True
        self.main_loop()
    
    def main_loop(self):
        """Main processing loop"""
        print("\n✓ System ready! Waiting for hand gestures...\n")
        
        frame_count = 0
        start_time = time.time()
        
        try:
            while self.running:
                # Read frame from camera
                ret, frame = self.camera.read()
                
                if not ret:
                    print("✗ Error: Could not read frame from camera")
                    break
                
                frame_count += 1
                
                # Track hand
                processed_frame, landmarks, handedness = self.hand_tracker.process_frame(frame)
                
                # Recognize gesture
                gesture = self.gesture_recognizer.recognize(landmarks)
                
                # Map gesture to action
                if gesture:
                    action = self.gesture_mapper.map_gesture(gesture)
                    
                    # Execute action on Earth
                    if action:
                        self.earth_controller.execute_action(action)
                        
                        # Display gesture on video frame
                        self._draw_gesture_feedback(processed_frame, gesture)
                
                # Display frame
                cv2.imshow("Gesture Earth Control", processed_frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\nQuitting...")
                    break
                elif key == ord('r'):
                    print("\nResetting view...")
                    from gesture_mapper import Action
                    self.earth_controller.execute_action(Action("reset_view", {}))
                elif key == ord('h'):
                    self.print_instructions()
                elif key == ord('m'):
                    self.gesture_mapper.print_mappings()
                
                # Performance monitoring
                if config.ENABLE_PROFILING and frame_count % 100 == 0:
                    elapsed = time.time() - start_time
                    avg_fps = frame_count / elapsed
                    print(f"[Performance] Avg FPS: {avg_fps:.1f}")
        
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
        
        except Exception as e:
            print(f"\n✗ Error in main loop: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.cleanup()
    
    def _draw_gesture_feedback(self, frame, gesture):
        """Draw gesture name on frame with animation"""
        # Large text in center
        text = gesture.type.value.upper().replace('_', ' ')
        
        # Get text size
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.5
        thickness = 3
        (text_width, text_height), baseline = cv2.getTextSize(
            text, font, font_scale, thickness
        )
        
        # Center position
        x = (frame.shape[1] - text_width) // 2
        y = (frame.shape[0] + text_height) // 2
        
        # Background rectangle
        padding = 20
        cv2.rectangle(
            frame,
            (x - padding, y - text_height - padding),
            (x + text_width + padding, y + baseline + padding),
            (0, 255, 0),
            -1
        )
        
        # Text
        cv2.putText(
            frame,
            text,
            (x, y),
            font,
            font_scale,
            (0, 0, 0),
            thickness
        )
    
    def print_instructions(self):
        """Print user instructions"""
        print("\n" + "=" * 60)
        print("GESTURE CONTROLS")
        print("=" * 60)
        print("\n🤏 PINCH:")
        print("   - Pinch fingers together → Zoom Out")
        print("   - Pinch fingers apart → Zoom In")
        
        print("\n👋 SWIPE:")
        print("   - Swipe Left → Rotate Earth Left")
        print("   - Swipe Right → Rotate Earth Right")
        print("   - Swipe Up → Tilt View Up")
        print("   - Swipe Down → Tilt View Down")
        
        print("\n👆 TAP:")
        print("   - Quick forward tap with index finger → Select/Click")
        
        print("\n✋ PALM:")
        print("   - Open palm fully → Reset View")
        print("   - Close to fist → Pause/Toggle")
        
        print("\n" + "=" * 60)
        print("KEYBOARD CONTROLS")
        print("=" * 60)
        print("  Q - Quit application")
        print("  R - Reset view")
        print("  H - Show this help")
        print("  M - Show gesture mappings")
        print("=" * 60 + "\n")
    
    def cleanup(self):
        """Clean up resources"""
        print("\nCleaning up...")
        
        self.running = False
        
        if self.camera:
            self.camera.release()
            print("✓ Camera released")
        
        cv2.destroyAllWindows()
        print("✓ Windows closed")
        
        self.hand_tracker.release()
        print("✓ Hand tracker released")
        
        self.earth_controller.stop_server()
        print("✓ Earth controller stopped")
        
        print("\n" + "=" * 60)
        print("APPLICATION TERMINATED")
        print("=" * 60)


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\nReceived interrupt signal...")
    sys.exit(0)


def main():
    """Main entry point"""
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create and start application
    app = GestureEarthApp()
    app.start()


if __name__ == "__main__":
    main()

"""
Gesture Mapper Module
Maps recognized gestures to Earth control actions
Provides abstraction layer between gesture recognition and Earth controller
"""

from gesture_recognizer import GestureType
import config


class Action:
    """Data class for control actions"""
    def __init__(self, action_type, parameters=None):
        self.type = action_type
        self.parameters = parameters or {}
    
    def __repr__(self):
        return f"Action({self.type}, {self.parameters})"


class GestureMapper:
    """
    Maps gestures to Earth control actions
    
    This provides a flexible layer to:
    - Customize gesture-to-action mappings
    - Scale/transform gesture parameters
    - Enable/disable specific gestures
    - Handle gesture combinations (future)
    """
    
    def __init__(self):
        """Initialize gesture mapper with default mappings"""
        
        # Define gesture-to-action mappings
        self.mappings = {
            GestureType.PINCH_IN: self._map_pinch_in,
            GestureType.PINCH_OUT: self._map_pinch_out,
            GestureType.SWIPE_LEFT: self._map_swipe_left,
            GestureType.SWIPE_RIGHT: self._map_swipe_right,
            GestureType.SWIPE_UP: self._map_swipe_up,
            GestureType.SWIPE_DOWN: self._map_swipe_down,
            GestureType.TAP: self._map_tap,
            GestureType.PALM_OPEN: self._map_palm_open,
            GestureType.PALM_CLOSE: self._map_palm_close,
        }
        
        print("[GestureMapper] Initialized with default mappings")
    
    def map_gesture(self, gesture):
        """
        Map a gesture to a control action
        
        Args:
            gesture: Gesture object from GestureRecognizer
            
        Returns:
            Action object or None
        """
        if gesture is None:
            return None
        
        # Check if gesture is enabled
        if not config.is_gesture_enabled(gesture.type.value):
            return None
        
        # Get mapping function
        mapping_func = self.mappings.get(gesture.type)
        
        if mapping_func:
            return mapping_func(gesture)
        
        return None
    
    def _map_pinch_in(self, gesture):
        """
        Map pinch in (fingers together) to zoom out
        
        Args:
            gesture: Gesture object
            
        Returns:
            Action for zoom out
        """
        # Get gesture config
        gesture_config = config.get_gesture_config("pinch_zoom_out")
        
        # Calculate zoom amount based on pinch distance
        distance = gesture.parameters.get("distance", 0)
        
        # Zoom out by configured step
        zoom_factor = config.ZOOM_STEP
        
        return Action(
            "zoom_out",
            {
                "factor": zoom_factor,
                "sensitivity": gesture_config.get("sensitivity", 1.0)
            }
        )
    
    def _map_pinch_out(self, gesture):
        """
        Map pinch out (fingers apart) to zoom in
        
        Args:
            gesture: Gesture object
            
        Returns:
            Action for zoom in
        """
        gesture_config = config.get_gesture_config("pinch_zoom_in")
        
        distance = gesture.parameters.get("distance", 0)
        zoom_factor = config.ZOOM_STEP
        
        return Action(
            "zoom_in",
            {
                "factor": zoom_factor,
                "sensitivity": gesture_config.get("sensitivity", 1.0)
            }
        )
    
    def _map_swipe_left(self, gesture):
        """
        Map swipe left to rotate Earth left (counterclockwise)
        
        Args:
            gesture: Gesture object
            
        Returns:
            Action for rotate left
        """
        gesture_config = config.get_gesture_config("swipe_left")
        
        distance = gesture.parameters.get("distance", 0)
        velocity = gesture.parameters.get("velocity", 0)
        
        # Calculate rotation amount based on swipe distance
        rotation_amount = distance * config.ROTATION_SENSITIVITY
        
        return Action(
            "rotate_left",
            {
                "amount": rotation_amount,
                "velocity": velocity,
                "sensitivity": gesture_config.get("sensitivity", 1.0)
            }
        )
    
    def _map_swipe_right(self, gesture):
        """Map swipe right to rotate Earth right (clockwise)"""
        gesture_config = config.get_gesture_config("swipe_right")
        
        distance = gesture.parameters.get("distance", 0)
        velocity = gesture.parameters.get("velocity", 0)
        
        rotation_amount = distance * config.ROTATION_SENSITIVITY
        
        return Action(
            "rotate_right",
            {
                "amount": rotation_amount,
                "velocity": velocity,
                "sensitivity": gesture_config.get("sensitivity", 1.0)
            }
        )
    
    def _map_swipe_up(self, gesture):
        """Map swipe up to tilt Earth up (look down)"""
        gesture_config = config.get_gesture_config("swipe_up")
        
        distance = gesture.parameters.get("distance", 0)
        velocity = gesture.parameters.get("velocity", 0)
        
        tilt_amount = distance * config.PAN_SENSITIVITY
        
        return Action(
            "tilt_up",
            {
                "amount": tilt_amount,
                "velocity": velocity,
                "sensitivity": gesture_config.get("sensitivity", 1.0)
            }
        )
    
    def _map_swipe_down(self, gesture):
        """Map swipe down to tilt Earth down (look up)"""
        gesture_config = config.get_gesture_config("swipe_down")
        
        distance = gesture.parameters.get("distance", 0)
        velocity = gesture.parameters.get("velocity", 0)
        
        tilt_amount = distance * config.PAN_SENSITIVITY
        
        return Action(
            "tilt_down",
            {
                "amount": tilt_amount,
                "velocity": velocity,
                "sensitivity": gesture_config.get("sensitivity", 1.0)
            }
        )
    
    def _map_tap(self, gesture):
        """Map tap to select/click at screen center"""
        gesture_config = config.get_gesture_config("tap")
        
        return Action(
            "select",
            {
                "position": "center",  # Could be extended to track finger position
                "z_change": gesture.parameters.get("z_change", 0)
            }
        )
    
    def _map_palm_open(self, gesture):
        """Map palm open to reset view to default"""
        gesture_config = config.get_gesture_config("palm_open")
        
        return Action(
            "reset_view",
            {
                "duration": config.CAMERA_SMOOTH_TIME
            }
        )
    
    def _map_palm_close(self, gesture):
        """Map palm close to pause/resume (optional functionality)"""
        # This could be used for pause, screenshot, or other features
        return Action(
            "pause_toggle",
            {}
        )
    
    def set_custom_mapping(self, gesture_type, mapping_func):
        """
        Set a custom mapping function for a gesture
        
        Args:
            gesture_type: GestureType enum value
            mapping_func: Function(gesture) -> Action
        """
        self.mappings[gesture_type] = mapping_func
        print(f"[GestureMapper] Custom mapping set for {gesture_type.value}")
    
    def disable_gesture(self, gesture_name):
        """
        Disable a specific gesture
        
        Args:
            gesture_name: String name of gesture (e.g., "pinch_zoom_in")
        """
        config.update_gesture_config(gesture_name, "enabled", False)
        print(f"[GestureMapper] Disabled gesture: {gesture_name}")
    
    def enable_gesture(self, gesture_name):
        """Enable a specific gesture"""
        config.update_gesture_config(gesture_name, "enabled", True)
        print(f"[GestureMapper] Enabled gesture: {gesture_name}")
    
    def get_available_actions(self):
        """
        Get list of all available actions
        
        Returns:
            List of action type strings
        """
        return [
            "zoom_in",
            "zoom_out",
            "rotate_left",
            "rotate_right",
            "tilt_up",
            "tilt_down",
            "select",
            "reset_view",
            "pause_toggle"
        ]
    
    def print_mappings(self):
        """Print current gesture-to-action mappings"""
        print("\n[GestureMapper] Current Mappings:")
        print("-" * 50)
        
        for gesture_type, func in self.mappings.items():
            enabled = config.is_gesture_enabled(gesture_type.value)
            status = "✓" if enabled else "✗"
            
            # Get corresponding action from config
            gesture_config = config.GESTURE_PARAMS.get(gesture_type.value, {})
            action = gesture_config.get("action", "N/A")
            
            print(f"{status} {gesture_type.value:20s} -> {action}")
        
        print("-" * 50)


# Example usage and testing
if __name__ == "__main__":
    print("Testing GestureMapper...")
    
    from gesture_recognizer import Gesture, GestureType
    
    # Initialize mapper
    mapper = GestureMapper()
    
    # Print current mappings
    mapper.print_mappings()
    
    print("\n--- Testing Gesture Mappings ---")
    
    # Test each gesture type
    test_gestures = [
        Gesture(GestureType.PINCH_IN, 0.9, {"distance": 25}),
        Gesture(GestureType.PINCH_OUT, 0.9, {"distance": 110}),
        Gesture(GestureType.SWIPE_LEFT, 0.8, {"distance": 150, "velocity": 75}),
        Gesture(GestureType.SWIPE_RIGHT, 0.8, {"distance": 150, "velocity": 75}),
        Gesture(GestureType.SWIPE_UP, 0.8, {"distance": 120, "velocity": 60}),
        Gesture(GestureType.SWIPE_DOWN, 0.8, {"distance": 120, "velocity": 60}),
        Gesture(GestureType.TAP, 0.7, {"z_change": -0.08}),
        Gesture(GestureType.PALM_OPEN, 0.85, {"state": "open"}),
    ]
    
    for gesture in test_gestures:
        action = mapper.map_gesture(gesture)
        print(f"\n{gesture}")
        print(f"  -> {action}")
    
    # Test disabling/enabling gestures
    print("\n--- Testing Gesture Enable/Disable ---")
    mapper.disable_gesture("swipe_left")
    mapper.print_mappings()
    
    mapper.enable_gesture("swipe_left")
    
    # Test custom mapping
    print("\n--- Testing Custom Mapping ---")
    
    def custom_pinch_mapping(gesture):
        return Action(
            "custom_zoom",
            {"custom_param": "test_value"}
        )
    
    mapper.set_custom_mapping(GestureType.PINCH_IN, custom_pinch_mapping)
    
    test_gesture = Gesture(GestureType.PINCH_IN, 0.9, {"distance": 25})
    action = mapper.map_gesture(test_gesture)
    print(f"\nCustom mapping result: {action}")
    
    print("\n--- Available Actions ---")
    print(mapper.get_available_actions())
    
    print("\nGestureMapper test completed!")

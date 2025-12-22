"""
Earth Controller Module
Controls 3D Earth visualization through web browser interface
Supports CesiumJS for interactive globe rendering and camera control
"""

import time
import webbrowser
import json
import os
from threading import Thread
from flask import Flask, render_template_string, jsonify, request
import config


class EarthController:
    """
    Controls Earth visualization in web browser
    
    Uses Flask web server to host CesiumJS visualization
    Communicates actions via REST API / JavaScript bridge
    """
    
    def __init__(self):
        """Initialize Earth controller"""
        
        # Flask app for web server
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'gesture-earth-control'
        
        # Current camera state
        self.camera_state = {
            "latitude": config.DEFAULT_LATITUDE,
            "longitude": config.DEFAULT_LONGITUDE,
            "altitude": config.DEFAULT_ALTITUDE,
            "heading": 0.0,  # degrees
            "pitch": -90.0,  # degrees (looking down)
            "roll": 0.0
        }
        
        # Action queue for communicating with browser
        self.action_queue = []
        
        # Setup routes
        self._setup_routes()
        
        # Server thread
        self.server_thread = None
        self.running = False
        
        print("[EarthController] Initialized")
        print(f"  - Default position: ({config.DEFAULT_LATITUDE}, {config.DEFAULT_LONGITUDE})")
        print(f"  - Default altitude: {config.DEFAULT_ALTITUDE}m")
    
    def start_server(self):
        """Start Flask web server in background thread"""
        if self.running:
            print("[EarthController] Server already running")
            return
        
        self.running = True
        
        # Start server in separate thread
        self.server_thread = Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        
        # Wait a moment for server to start
        time.sleep(2)
        
        # Open browser
        if config.AUTO_OPEN_BROWSER:
            url = f"http://{config.WEB_SERVER_HOST}:{config.WEB_SERVER_PORT}"
            print(f"[EarthController] Opening browser: {url}")
            webbrowser.open(url)
        
        print("[EarthController] Server started")
    
    def _run_server(self):
        """Run Flask server (called in background thread)"""
        self.app.run(
            host=config.WEB_SERVER_HOST,
            port=config.WEB_SERVER_PORT,
            debug=False,
            use_reloader=False
        )
    
    def _setup_routes(self):
        """Setup Flask routes for web interface"""
        
        @self.app.route('/')
        def index():
            """Main page with Cesium Earth viewer"""
            return self._get_html_template()
        
        @self.app.route('/api/actions', methods=['GET'])
        def get_actions():
            """Get pending actions for browser to execute"""
            actions = self.action_queue.copy()
            self.action_queue.clear()
            return jsonify(actions)
        
        @self.app.route('/api/camera', methods=['GET'])
        def get_camera():
            """Get current camera state"""
            return jsonify(self.camera_state)
        
        @self.app.route('/api/camera', methods=['POST'])
        def update_camera():
            """Update camera state from browser"""
            data = request.json
            self.camera_state.update(data)
            return jsonify({"status": "ok"})
    
    def execute_action(self, action):
        """
        Execute a control action on the Earth
        
        Args:
            action: Action object from GestureMapper
        """
        if action is None:
            return
        
        action_type = action.type
        params = action.parameters
        
        # Map action to camera update
        if action_type == "zoom_in":
            self._zoom_in(params)
        elif action_type == "zoom_out":
            self._zoom_out(params)
        elif action_type == "rotate_left":
            self._rotate_left(params)
        elif action_type == "rotate_right":
            self._rotate_right(params)
        elif action_type == "tilt_up":
            self._tilt_up(params)
        elif action_type == "tilt_down":
            self._tilt_down(params)
        elif action_type == "select":
            self._select(params)
        elif action_type == "reset_view":
            self._reset_view(params)
        elif action_type == "pause_toggle":
            self._pause_toggle(params)
        
        if config.DEBUG_MODE:
            print(f"[EarthController] Action: {action_type} | Params: {params}")
    
    def _zoom_in(self, params):
        """Zoom in (decrease altitude)"""
        factor = params.get("factor", config.ZOOM_STEP)
        self.camera_state["altitude"] /= factor
        
        # Clamp to minimum
        if self.camera_state["altitude"] < config.ZOOM_MIN:
            self.camera_state["altitude"] = config.ZOOM_MIN
        
        self._queue_camera_update()
    
    def _zoom_out(self, params):
        """Zoom out (increase altitude)"""
        factor = params.get("factor", config.ZOOM_STEP)
        self.camera_state["altitude"] *= factor
        
        # Clamp to maximum
        if self.camera_state["altitude"] > config.ZOOM_MAX:
            self.camera_state["altitude"] = config.ZOOM_MAX
        
        self._queue_camera_update()
    
    def _rotate_left(self, params):
        """Rotate camera left (counterclockwise)"""
        amount = params.get("amount", 10)
        self.camera_state["heading"] -= amount
        
        # Normalize to 0-360
        self.camera_state["heading"] = self.camera_state["heading"] % 360
        
        self._queue_camera_update()
    
    def _rotate_right(self, params):
        """Rotate camera right (clockwise)"""
        amount = params.get("amount", 10)
        self.camera_state["heading"] += amount
        
        self.camera_state["heading"] = self.camera_state["heading"] % 360
        
        self._queue_camera_update()
    
    def _tilt_up(self, params):
        """Tilt camera up (look more down at Earth)"""
        amount = params.get("amount", 5)
        self.camera_state["pitch"] -= amount
        
        # Clamp to -90 to 0 (looking down to horizon)
        if self.camera_state["pitch"] < -90:
            self.camera_state["pitch"] = -90
        
        self._queue_camera_update()
    
    def _tilt_down(self, params):
        """Tilt camera down (look more toward horizon)"""
        amount = params.get("amount", 5)
        self.camera_state["pitch"] += amount
        
        # Clamp
        if self.camera_state["pitch"] > 0:
            self.camera_state["pitch"] = 0
        
        self._queue_camera_update()
    
    def _select(self, params):
        """Select/click at position"""
        # Queue a click action
        self.action_queue.append({
            "type": "click",
            "position": params.get("position", "center")
        })
    
    def _reset_view(self, params):
        """Reset camera to default position"""
        self.camera_state = {
            "latitude": config.DEFAULT_LATITUDE,
            "longitude": config.DEFAULT_LONGITUDE,
            "altitude": config.DEFAULT_ALTITUDE,
            "heading": 0.0,
            "pitch": -90.0,
            "roll": 0.0
        }
        
        self._queue_camera_update()
    
    def _pause_toggle(self, params):
        """Toggle pause state"""
        self.action_queue.append({
            "type": "pause_toggle"
        })
    
    def _queue_camera_update(self):
        """Queue a camera update action for browser"""
        self.action_queue.append({
            "type": "camera_update",
            "camera": self.camera_state.copy(),
            "duration": config.CAMERA_SMOOTH_TIME
        })
    
    def _get_html_template(self):
        """
        Generate HTML template for Cesium Earth viewer
        
        Returns:
            HTML string with embedded JavaScript
        """
        
        cesium_token = config.CESIUM_ACCESS_TOKEN or "YOUR_CESIUM_ION_ACCESS_TOKEN"
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gesture-Controlled Earth</title>
    
    <!-- Cesium CSS -->
    <link href="https://cesium.com/downloads/cesiumjs/releases/1.109/Build/Cesium/Widgets/widgets.css" rel="stylesheet">
    
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: Arial, sans-serif;
            overflow: hidden;
        }}
        
        #cesiumContainer {{
            width: 100vw;
            height: 100vh;
        }}
        
        #info-panel {{
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 15px;
            border-radius: 8px;
            font-size: 14px;
            z-index: 1000;
            max-width: 300px;
        }}
        
        #gesture-display {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(0, 255, 0, 0.8);
            color: black;
            padding: 20px 40px;
            border-radius: 10px;
            font-size: 24px;
            font-weight: bold;
            display: none;
            z-index: 1001;
            animation: fadeIn 0.3s;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translate(-50%, -50%) scale(0.8); }}
            to {{ opacity: 1; transform: translate(-50%, -50%) scale(1); }}
        }}
        
        .info-row {{
            margin: 5px 0;
        }}
        
        .label {{
            font-weight: bold;
            color: #4CAF50;
        }}
    </style>
</head>
<body>
    <div id="cesiumContainer"></div>
    
    <div id="info-panel">
        <h3 style="margin-bottom: 10px; color: #4CAF50;">🌍 Gesture Control Active</h3>
        <div class="info-row">
            <span class="label">Latitude:</span> <span id="lat">0</span>°
        </div>
        <div class="info-row">
            <span class="label">Longitude:</span> <span id="lon">0</span>°
        </div>
        <div class="info-row">
            <span class="label">Altitude:</span> <span id="alt">0</span> km
        </div>
        <div class="info-row">
            <span class="label">Heading:</span> <span id="heading">0</span>°
        </div>
        <div class="info-row">
            <span class="label">Last Action:</span> <span id="action">-</span>
        </div>
    </div>
    
    <div id="gesture-display"></div>
    
    <!-- Cesium JS -->
    <script src="https://cesium.com/downloads/cesiumjs/releases/1.109/Build/Cesium/Cesium.js"></script>
    
    <script>
        // Set Cesium Ion access token
        Cesium.Ion.defaultAccessToken = '{cesium_token}';
        
        // Create Cesium viewer
        const viewer = new Cesium.Viewer('cesiumContainer', {{
            terrainProvider: Cesium.createWorldTerrain(),
            animation: false,
            timeline: false,
            baseLayerPicker: false,
            geocoder: false,
            homeButton: false,
            sceneModePicker: false,
            navigationHelpButton: false,
            fullscreenButton: false
        }});
        
        // Set initial camera position
        viewer.camera.setView({{
            destination: Cesium.Cartesian3.fromDegrees(
                {config.DEFAULT_LONGITUDE},
                {config.DEFAULT_LATITUDE},
                {config.DEFAULT_ALTITUDE}
            ),
            orientation: {{
                heading: Cesium.Math.toRadians(0),
                pitch: Cesium.Math.toRadians(-90),
                roll: 0.0
            }}
        }});
        
        // Update info panel
        function updateInfo() {{
            const camera = viewer.camera;
            const position = camera.positionCartographic;
            
            document.getElementById('lat').textContent = 
                Cesium.Math.toDegrees(position.latitude).toFixed(4);
            document.getElementById('lon').textContent = 
                Cesium.Math.toDegrees(position.longitude).toFixed(4);
            document.getElementById('alt').textContent = 
                (position.height / 1000).toFixed(2);
            document.getElementById('heading').textContent = 
                Cesium.Math.toDegrees(camera.heading).toFixed(2);
        }}
        
        // Poll for actions from server
        async function pollActions() {{
            try {{
                const response = await fetch('/api/actions');
                const actions = await response.json();
                
                for (const action of actions) {{
                    executeAction(action);
                }}
            }} catch (error) {{
                console.error('Error polling actions:', error);
            }}
            
            // Poll every 100ms
            setTimeout(pollActions, 100);
        }}
        
        // Execute action
        function executeAction(action) {{
            console.log('Executing action:', action);
            
            if (action.type === 'camera_update') {{
                updateCamera(action.camera, action.duration);
                document.getElementById('action').textContent = 'Camera Update';
            }} else if (action.type === 'click') {{
                showGesture('TAP');
                document.getElementById('action').textContent = 'Tap/Click';
            }} else if (action.type === 'pause_toggle') {{
                showGesture('PAUSE TOGGLE');
                document.getElementById('action').textContent = 'Pause Toggle';
            }}
        }}
        
        // Update camera position
        function updateCamera(cameraState, duration) {{
            viewer.camera.flyTo({{
                destination: Cesium.Cartesian3.fromDegrees(
                    cameraState.longitude,
                    cameraState.latitude,
                    cameraState.altitude
                ),
                orientation: {{
                    heading: Cesium.Math.toRadians(cameraState.heading),
                    pitch: Cesium.Math.toRadians(cameraState.pitch),
                    roll: Cesium.Math.toRadians(cameraState.roll)
                }},
                duration: duration
            }});
        }}
        
        // Show gesture feedback
        function showGesture(gestureName) {{
            const display = document.getElementById('gesture-display');
            display.textContent = gestureName;
            display.style.display = 'block';
            
            setTimeout(() => {{
                display.style.display = 'none';
            }}, 1000);
        }}
        
        // Update info panel every frame
        viewer.scene.postRender.addEventListener(updateInfo);
        
        // Start polling for actions
        pollActions();
        
        console.log('Cesium Earth viewer initialized');
        console.log('Waiting for gesture commands...');
    </script>
</body>
</html>
        """
        
        return html
    
    def stop_server(self):
        """Stop the web server"""
        self.running = False
        print("[EarthController] Server stopped")


# Example usage and testing
if __name__ == "__main__":
    print("Testing EarthController...")
    print("This will start a web server and open your browser.")
    print("Press Ctrl+C to stop")
    
    from gesture_mapper import Action
    
    # Initialize controller
    controller = EarthController()
    
    # Start server
    controller.start_server()
    
    print("\nServer running. Testing actions...")
    print("Watch the browser window for changes.\n")
    
    # Simulate some actions
    try:
        time.sleep(3)
        
        print("Testing zoom in...")
        controller.execute_action(Action("zoom_in", {"factor": 2.0}))
        time.sleep(2)
        
        print("Testing zoom out...")
        controller.execute_action(Action("zoom_out", {"factor": 2.0}))
        time.sleep(2)
        
        print("Testing rotate left...")
        controller.execute_action(Action("rotate_left", {"amount": 45}))
        time.sleep(2)
        
        print("Testing rotate right...")
        controller.execute_action(Action("rotate_right", {"amount": 45}))
        time.sleep(2)
        
        print("Testing tilt...")
        controller.execute_action(Action("tilt_up", {"amount": 20}))
        time.sleep(2)
        
        print("Testing reset view...")
        controller.execute_action(Action("reset_view", {}))
        time.sleep(2)
        
        print("\nTest complete! Press Ctrl+C to exit.")
        
        # Keep running
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\nStopping server...")
        controller.stop_server()
        print("Test completed!")

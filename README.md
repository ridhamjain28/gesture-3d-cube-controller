# 🎮 Hand Gesture 3D Cube Controller

Control a colorful 3D cube using just your hand gestures! No keyboard, no mouse - just wave your hands! 👋

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![OpenCV](https://img.shields.io/badge/opencv-4.12-green.svg)
![MediaPipe](https://img.shields.io/badge/mediapipe-0.10-orange.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

- 🎨 **Colorful 3D Cube** with 6 different colored faces (RED, GREEN, BLUE, YELLOW, MAGENTA, CYAN)
- 👋 **Hand Gesture Recognition** using MediaPipe
- 🔄 **Pinch & Drag** to rotate the cube in any direction
- 🔍 **Zoom In/Out** by spreading or closing your hand
- 📹 **Real-time Camera Feed** showing hand tracking
- 🎯 **Smooth Animations** with 3D perspective projection
- ⚡ **Low Latency** gesture detection

## 🎬 Demo

The cube responds to your hand movements in real-time:
- **Pinch** your thumb and index finger together, then drag to rotate
- **Spread** your fingers wide to zoom in
- **Close** your hand into a fist to zoom out

### ✨ **NEW: Enhanced Version Available!**

Check out the **enhanced version** with amazing features:
- 🎨 **5 Different 3D Objects** (Cube, Pyramid, Sphere, Torus, Tetrahedron)
- ⚙️ **Physics Engine** with gravity and momentum
- ✨ **Particle Effects** for visual feedback
- 🎬 **Recording & Playback** of gesture sequences
- 📋 **Interactive UI Menu**
- 🎓 **Comprehensive Learning Guide** for students

Run it: `python enhanced_controller.py`

See `LEARNING_GUIDE.md` for tutorials and learning resources!

## 🚀 Quick Start

### Prerequisites

- Python 3.11 (MediaPipe doesn't support Python 3.13 yet)
- Webcam
- Windows 10/11 (tested on Windows 10)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ridhamjain28/gesture-3d-cube-controller.git
   cd gesture-3d-cube-controller
   ```

2. **Install dependencies**
   ```bash
   pip install opencv-python mediapipe numpy
   ```

3. **Run the application**
   ```bash
   python simple_cube_control.py
   ```
   
   Or simply double-click `run_cube.bat` on Windows!

## 🎮 Controls

### Gesture Controls

| Gesture | Action | How To Do It |
|---------|--------|--------------|
| 🤏 **Pinch & Drag** | Rotate Cube | Touch thumb and index finger together, then move your hand left/right/up/down |
| ✋ **Spread Fingers** | Zoom In | Open all 5 fingers wide apart |
| ✊ **Close Fist** | Zoom Out | Close your hand into a fist |

### Keyboard Controls

| Key | Action |
|-----|--------|
| `R` | Reset cube to original position |
| `Q` | Quit application |
| `ESC` | Quit application |

## 📁 Project Structure

```
gesture-3d-cube-controller/
├── simple_cube_control.py    # Main application (simplified version)
├── main.py                    # Full Earth control system
├── hand_tracker.py           # Hand tracking module
├── gesture_recognizer.py     # Gesture recognition engine
├── gesture_mapper.py         # Maps gestures to actions
├── earth_controller.py       # 3D Earth visualization (Cesium)
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── run_cube.bat             # Windows launcher
└── README.md                 # This file
```

## 🛠️ How It Works

### 1. Hand Tracking
Uses **MediaPipe Hands** to detect 21 hand landmarks in real-time from your webcam feed.

### 2. Gesture Recognition
Analyzes hand landmark positions to recognize:
- **Pinch**: Distance between thumb and index finger < 40 pixels
- **Hand Openness**: Average distance of fingertips from wrist

### 3. 3D Projection
- Applies rotation matrices (X, Y, Z axis)
- Projects 3D coordinates to 2D screen using perspective projection
- Depth-sorts faces for proper rendering (painter's algorithm)

### 4. Visual Feedback
- 6 colored cube faces for easy rotation visibility
- Real-time camera preview with hand landmarks
- On-screen gesture status display

## 🎨 Color Coding

Each face of the cube has a unique color to clearly see rotations:

- 🔴 **RED** - Back face
- 🟢 **GREEN** - Front face
- 🔵 **BLUE** - Bottom face
- 🟡 **YELLOW** - Top face
- 🟣 **MAGENTA** - Left face
- 🔷 **CYAN** - Right face

## ⚙️ Configuration

Edit `config.py` to adjust:
- Camera resolution and FPS
- Gesture sensitivity thresholds
- Hand tracking confidence levels
- Zoom limits and rotation speeds

## 🐛 Troubleshooting

### Camera Not Opening
- Check if another application is using the camera
- Try changing `CAMERA_INDEX` in config.py (0, 1, or 2)
- Enable camera permissions in Windows Settings → Privacy → Camera

### Gestures Not Detected
- Ensure good lighting conditions
- Position hand clearly in front of camera
- Keep hand at arm's length from camera
- Try adjusting `DETECTION_CONFIDENCE` in config.py

### Mirror/Reversed Image
- The app automatically flips the image horizontally (mirror mode)
- Your right hand appears as right hand on screen

## 🌍 Bonus: Earth Controller

This project also includes a full **Gesture-Controlled Earth Navigation System** using Cesium!

To use it:
1. Get a free Cesium Ion token from https://cesium.com/ion/signup
2. Add token to `config.py`
3. Run: `python main.py`

Control a 3D interactive Earth globe with the same hand gestures!

## 📦 Requirements

```
opencv-python>=4.8.0
mediapipe>=0.10.0
numpy>=1.24.0
flask>=3.0.0 (for Earth controller)
```

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new gestures
- Improve documentation
- Add new features

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **MediaPipe** by Google for hand tracking
- **OpenCV** for computer vision
- **Cesium** for 3D Earth visualization

## 👨‍💻 Author

Created with ❤️ by Ridham Jain

## 📧 Contact

- GitHub: [@ridhamjain28](https://github.com/ridhamjain28)
- Issues: [Report a bug](https://github.com/ridhamjain28/gesture-3d-cube-controller/issues)

---

**⭐ If you found this project helpful, please give it a star!**


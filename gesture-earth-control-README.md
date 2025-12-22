# Gesture-Controlled Earth Navigation System

A real-time hand gesture recognition system for controlling an interactive 3D Earth globe using computer vision.

## 🎯 Project Overview

This project enables intuitive control of a 3D Earth visualization using hand gestures detected through your webcam. Built with Python, OpenCV, and MediaPipe, it demonstrates practical applications of computer vision, gesture recognition, and human-computer interaction.

## ✨ Features

- **Real-time Hand Tracking**: 21-landmark hand detection using MediaPipe Hands
- **Gesture Recognition**: Pinch, Swipe, Tap, Palm gestures
- **3D Earth Visualization**: CesiumJS-based interactive globe
- **Debouncing & Stabilization**: Smooth gesture detection
- **Performance Optimized**: 30+ FPS real-time processing
- **Extensible Architecture**: Easy to add custom gestures

## 📋 Prerequisites

- Python 3.8+
- Webcam
- Modern web browser

## 🚀 Quick Start

### Installation

```bash
# Navigate to project
cd gesture-earth-control

# Install dependencies  
pip install opencv-python mediapipe numpy pyautogui selenium flask
```

### Run

```bash
python main.py
```

## 📦 Project Structure

```
gesture-earth-control/
├── src/
│   ├── hand_tracker.py          # Hand detection
│   ├── gesture_recognizer.py    # Gesture classification
│   ├── gesture_mapper.py        # Action mapping
│   ├── earth_controller.py      # Earth interface
│   ├── utils.py                 # Utilities
│   └── config.py                # Configuration
├── tests/
│   ├── test_gestures.py
│   └── calibrate_camera.py
├── docs/
│   ├── ARCHITECTURE.md
│   ├── GESTURE_GUIDE.md
│   └── EXTENDING.md
├── web/
│   └── earth_viewer.html
├── requirements.txt
├── main.py
└── README.md
```

## 🎮 Gestures

1. **Pinch In/Out**: Zoom
2. **Swipe**: Pan/Rotate
3. **Tap**: Select
4. **Palm Open/Close**: Reset

## 🔧 Troubleshooting

- **Camera not detected**: Check permissions, try different camera index
- **Poor detection**: Improve lighting, plain background
- **Low FPS**: Reduce resolution, close other apps
- **Too sensitive**: Adjust thresholds in config.py

## 📝 License

MIT License

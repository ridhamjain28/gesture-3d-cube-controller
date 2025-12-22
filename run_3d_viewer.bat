@echo off
REM Ultra-Smooth 3D File Viewer Launcher
color 0A
cls
echo.
echo    ========================================================================
echo                     3D FILE VIEWER - GESTURE CONTROL
echo    ========================================================================
echo.
echo    View ANY 3D file with hand gestures!
echo    ------------------------------------
echo    Supported: .OBJ, .STL, .PLY files
echo.
echo    Performance:
echo    - Resolution: 480x360 (ULTRA SMOOTH)
echo    - Target FPS: 30 (Stable)
echo    - Model: MediaPipe Lite
echo    - Optimized for: 7GB RAM
echo.
echo    Controls:
echo    - Pinch + Move = Rotate
echo    - Spread Fingers = Zoom In
echo    - Close Fist = Zoom Out
echo    - W = Wireframe Toggle
echo    - R = Reset
echo    - Q = Quit
echo.
echo    ========================================================================
echo.
echo    Starting 3D File Viewer...
echo    Place your .obj, .stl, or .ply files in this folder!
echo.
echo    ========================================================================
echo.
python 3d_file_viewer.py
echo.
echo    ========================================================================
echo    Application closed
echo    ========================================================================
echo.
pause

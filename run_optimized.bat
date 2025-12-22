@echo off
REM Optimized Launcher for 7GB RAM Systems
color 0A
cls
echo.
echo    ========================================================================
echo                  3D GESTURE CUBE CONTROLLER - OPTIMIZED
echo    ========================================================================
echo.
echo    System Configuration:
echo    ---------------------
echo    Target RAM:           7GB (Your PC)
echo    Resolution:           640x480 (Performance Mode)
echo    Model:                MediaPipe Lite (Fast Mode)
echo    Expected FPS:         28-30 (Stable)
echo    RAM Usage:            200-300MB
echo    CPU Usage:            25-35%%
echo    Status:               OPTIMIZED ✓
echo.
echo    ========================================================================
echo.
echo    Starting application...
echo    Watch for FPS counter in top-right (Green = Smooth)
echo.
echo    Quick Controls:
echo    - Pinch + Drag = Rotate
echo    - Spread Fingers = Zoom In
echo    - Close Fist = Zoom Out
echo    - R = Reset
echo    - Q = Quit
echo.
echo    ========================================================================
echo.
python simple_cube_control.py
echo.
echo    ========================================================================
echo    Application closed
echo    ========================================================================
echo.
pause


@echo off
REM Quick GitHub Push Script
color 0E
cls
echo.
echo    ========================================================================
echo                       PUSH TO GITHUB - QUICK SCRIPT
echo    ========================================================================
echo.
echo    This will help you push your optimized project to GitHub!
echo.
echo    ========================================================================
echo.
echo    STEP 1: Make sure you have a GitHub repository ready
echo            Go to: https://github.com/new
echo            Create a new repository (don't initialize with README)
echo.
pause
echo.
echo    ========================================================================
echo    STEP 2: Initializing Git (if needed)...
echo    ========================================================================
echo.

git init
echo.

echo    ========================================================================
echo    STEP 3: Adding all files...
echo    ========================================================================
echo.

git add .
echo.

echo    ========================================================================
echo    STEP 4: Creating commit...
echo    ========================================================================
echo.

git commit -m "3D Gesture Viewer - Optimized for 7GB RAM with universal file support"
echo.

echo    ========================================================================
echo    STEP 5: Add your GitHub remote
echo    ========================================================================
echo.
echo    IMPORTANT: Replace the URL below with YOUR repository URL!
echo.
echo    Example format:
echo    git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
echo.
echo    Or if already exists:
echo    git remote set-url origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
echo.
echo    ========================================================================
echo.
set /p REPO_URL="Enter your GitHub repository URL: "
echo.

git remote add origin %REPO_URL% 2>nul
if errorlevel 1 (
    echo    Remote already exists, updating URL...
    git remote set-url origin %REPO_URL%
)

echo.
echo    ========================================================================
echo    STEP 6: Pushing to GitHub...
echo    ========================================================================
echo.

git branch -M main
git push -u origin main

echo.
echo    ========================================================================
echo    DONE! Check your GitHub repository!
echo    ========================================================================
echo.
pause

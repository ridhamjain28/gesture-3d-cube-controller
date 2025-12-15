@echo off
echo Creating Gesture Earth Control Project Structure...
echo.

cd /d "D:\Img projecy"

if not exist "gesture-earth-control" mkdir "gesture-earth-control"
cd gesture-earth-control

if not exist "src" mkdir "src"
if not exist "tests" mkdir "tests"
if not exist "docs" mkdir "docs"
if not exist "web" mkdir "web"

echo Project structure created successfully!
echo.
echo Directory: %CD%
echo.
dir /B
echo.
echo Now creating project files...
pause

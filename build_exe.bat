@echo off
echo *** SHIVAM OPTICALS - PYTHON BUILDER ***
echo.
echo This script will build the Shivam Opticals application as an executable.
echo.

rem Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python is not installed or not in your PATH!
    echo Please install Python from https://www.python.org/downloads/
    echo Be sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo Python found. Starting build process...
echo.

rem Run the Python build script
python build.py

echo.
echo Build process complete!
echo.
pause 
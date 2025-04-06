"""
Build script for Shivam Opticals - Creates an executable using PyInstaller
"""
import os
import sys
import shutil
import subprocess
import platform

print("=" * 60)
print("Shivam Opticals - Build Script")
print("=" * 60)

# Check Python version
print(f"Python version: {platform.python_version()}")
print(f"Platform: {platform.system()} {platform.architecture()[0]}")

# Create build directory if it doesn't exist
if not os.path.exists("build"):
    os.makedirs("build")

# Ensure required packages are installed
required_packages = ["pyinstaller", "pillow"]
print("\nChecking required packages...")

for package in required_packages:
    try:
        __import__(package)
        print(f"  ✓ {package} is installed")
    except ImportError:
        print(f"  ✗ {package} is not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Install tkinter if not already installed (platform-specific)
if platform.system() == "Linux":
    try:
        import tkinter
        print("  ✓ tkinter is installed")
    except ImportError:
        print("  ✗ tkinter is not installed. Please install it manually with:")
        print("    sudo apt-get install python3-tk  # for Debian/Ubuntu")
        print("    sudo dnf install python3-tkinter  # for Fedora")
        sys.exit(1)

print("\nBuilding executable with PyInstaller...")

# Create PyInstaller command
pyinstaller_cmd = [
    "pyinstaller",
    "--name=ShivamOpticals",
    "--windowed",  # No console window in Windows
    "--onefile",   # Single executable file
    "--clean",     # Clean cache before building
    "main.py"
]

# Add icon if it exists
if os.path.exists("icon.ico"):
    pyinstaller_cmd.insert(3, f"--icon=icon.ico")
elif os.path.exists("icon.png"):
    # Try to convert png to ico using PIL if on Windows
    if platform.system() == "Windows":
        try:
            from PIL import Image
            print("Converting icon.png to icon.ico...")
            img = Image.open("icon.png")
            icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
            img.save("icon.ico", sizes=icon_sizes)
            pyinstaller_cmd.insert(3, "--icon=icon.ico")
        except Exception as e:
            print(f"Could not convert icon: {e}")

# Run PyInstaller
try:
    subprocess.check_call(pyinstaller_cmd)
    
    # Copy database file if it exists (for existing data)
    if os.path.exists("optical_shop.db"):
        shutil.copy("optical_shop.db", "dist/")
        print("Copied existing database file")
    
    # Copy icon file
    for icon_file in ["icon.png", "icon.ico"]:
        if os.path.exists(icon_file):
            shutil.copy(icon_file, "dist/")
            print(f"Copied {icon_file}")
    
    print("\n" + "=" * 60)
    print("Build completed successfully!")
    print("=" * 60)
    print("\nYou can find the executable in the 'dist' folder:")
    
    if platform.system() == "Windows":
        print(f"  dist\\ShivamOpticals.exe")
    else:
        print(f"  dist/ShivamOpticals")
    
    print("\nTo run the application, simply double-click the executable file.")
    
except subprocess.CalledProcessError as e:
    print(f"Error building executable: {e}")
    sys.exit(1)

# Ask to run the application
if platform.system() == "Windows":
    print("\nDo you want to run the application now? (y/n)")
    if input().lower() == 'y':
        exe_path = os.path.join("dist", "ShivamOpticals.exe")
        if os.path.exists(exe_path):
            subprocess.Popen([exe_path])
        else:
            print(f"Executable not found at {exe_path}") 
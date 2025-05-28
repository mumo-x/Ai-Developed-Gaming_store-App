import os
import sys
import shutil
from PyInstaller.__main__ import run

# Configuration
app_name = "PS"
main_script = "main.py"
# Use a default icon from PyQt5 if the custom icon doesn't exist
icon_path = None
for path in ["PS Gamers.ico", "PS Gamers.png", "ps_gamers.png", "logo.png"]:
    if os.path.exists(path):
        icon_path = path
        break

version = "1.0.0"

print(f"Building {app_name} version {version}...")

# Clean previous build
if os.path.exists("build"):
    print("Cleaning previous build directory...")
    shutil.rmtree("build")
if os.path.exists("dist"):
    print("Cleaning previous dist directory...")
    shutil.rmtree("dist")
if os.path.exists(f"{app_name}.spec"):
    print("Removing previous spec file...")
    os.remove(f"{app_name}.spec")

# Create necessary directories if they don't exist
for directory in ["qr_codes", "data", "reports"]:
    if not os.path.exists(directory):
        print(f"Creating {directory} directory...")
        os.makedirs(directory)

# Build command
build_cmd = [
    main_script,
    "--name", app_name,
    "--onefile",
    "--windowed",
    "--hidden-import", "PIL._tkinter_finder",
    "--clean",
]

# Add icon if available
if icon_path:
    print(f"Using icon: {icon_path}")
    build_cmd.extend(["--icon", icon_path])
    build_cmd.extend(["--add-data", f"{icon_path};."])

# Add data directories
build_cmd.extend(["--add-data", "data;data"])
build_cmd.extend(["--add-data", "qr_codes;qr_codes"])
build_cmd.extend(["--add-data", "reports;reports"])

# Run PyInstaller
print("Starting PyInstaller build process...")
run(build_cmd)

print(f"Build completed. Executable is in the dist folder.")

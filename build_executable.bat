@echo off
echo Trinix Gaming Shop Management System - Build Executable
echo =====================================================

echo Installing required Python packages...
pip install -r requirements.txt

echo.
echo Building executable...
python build_exe.py

echo.
echo Build complete! The executable is in the dist folder.
echo.

pause
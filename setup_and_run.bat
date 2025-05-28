@echo off
echo Trinix Gaming Shop Management System Setup
echo =========================================

echo Installing required Python packages...
pip install -r requirements.txt

echo.
echo Creating necessary directories...
if not exist qr_codes mkdir qr_codes

echo.
echo Setup complete!
echo.
echo Running Trinix Gaming Shop Management System...
python main.py

pause
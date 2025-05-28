@echo off
echo Building Trinix Gaming Shop Application...
echo.

echo Step 1: Installing dependencies...
call npm install
if %ERRORLEVEL% neq 0 (
    echo Error installing dependencies. Please make sure Node.js is installed.
    pause
    exit /b 1
)
echo Dependencies installed successfully.
echo.

echo Step 2: Building application...
call npm run build
if %ERRORLEVEL% neq 0 (
    echo Error building application.
    pause
    exit /b 1
)
echo.

echo Build completed successfully!
echo.
echo Your installer should be available in the 'dist' folder.
echo Full path: %CD%\dist
echo.
echo Press any key to open the dist folder...
pause > nul
start "" "%CD%\dist"
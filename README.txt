PS Gaming Shop Management System
================================

This application helps manage customer check-ins, registrations, and analytics for PS Gaming Shop.

Installation Instructions:
-------------------------

1. Make sure you have Python 3.8 or higher installed on your computer.
   You can download Python from https://www.python.org/downloads/

2. Install the required dependencies by running:
   pip install -r requirements.txt

3. Set up the application:
   python setup_app.py
   This will create necessary directories and generate the logo and icons.

4. Run the application using one of these methods:
   - Double-click on run_PS_app.bat (recommended for first-time users)
   - Open a command prompt and run: python main.py

5. Double click the .exe file created after runing python PS_app.py

Features:
--------

1. Check-in / Register Tab:
   - Scan customer QR codes using your laptop camera
   - Register new customers and generate unique QR codes
   - Record game preferences, console choice, payment details, and referrals

2. Customer Management Tab:
   - View and search all customer details
   - Filter customers by various criteria
   - Regenerate QR codes for customers who lost theirs
   - Add, edit, and delete customer records

3. Analytics Tab:
   - View sales and customer visit charts
   - Export data to Excel
   - Generate end-of-shift reports in PDF format

File Structure:
--------------

- main.py: Main application file
- database_manager.py: Handles data storage and retrieval
- qr_utils.py: Manages QR code generation and scanning
- report_generator.py: Creates reports and exports data
- requirements.txt: Lists required Python packages
- run_PS_app.bat: Batch file to run the application
- data/: Directory for storing customer and visit data
- qr_codes/: Directory for storing generated QR codes
- reports/: Directory for storing generated reports

Utilities:
---------

The application includes several utilities to help with QR code generation, scanning, and camera testing:

1. qr_test.py - Test QR code generation and scanning
   Run: python qr_test.py [optional_qr_code_image_path]
   Or use: test_qr_codes.bat

2. qr_viewer.py - View and decode QR codes from image files
   Run: python qr_viewer.py
   Or use: view_qr_codes.bat

3. test_camera.py - Test your camera functionality
   Run: python test_camera.py
   Or use: test_camera.bat

4. create_logo.py - Create a PS Gaming logo
   Run: python create_logo.py

Troubleshooting:
---------------

If you encounter issues with QR code scanning:
1. Make sure the QR code is well-lit and clearly visible
2. Hold the QR code steady in front of the camera
3. Try installing the optional pyzbar library: pip install pyzbar
4. Use the qr_test.py utility to test QR code scanning

General troubleshooting:
1. Make sure all required dependencies are installed
2. Check that your webcam is properly connected and working
3. Ensure you have write permissions in the application directory
4. Check the console for error messages

For further assistance, please contact designerssplendor@gmail.com

NB: THE .exe FILE IS NOT UPLOADED

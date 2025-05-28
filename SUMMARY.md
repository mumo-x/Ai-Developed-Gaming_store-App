# Trinix Gaming Shop Management System

## Overview

The Trinix Gaming Shop Management System is a comprehensive application designed to manage customer check-ins, registrations, and analytics for Trinix Gaming Shop. The application features a modern, gamer-friendly interface with the Trinix Gaming logo prominently displayed.

## Key Features

### Check-in / Register Tab
- **QR Code Scanning**: Scan customer QR codes using the laptop camera
- **Customer Registration**: Register new customers and generate unique QR codes
- **Game Preferences**: Record game genre, console choice, payment details, and referrals
- **Payment Tracking**: Track different payment methods (Cash, Mobile Money, Card, Transfer)

### Customer Management Tab
- **Customer Database**: View and search all customer details
- **Filtering Options**: Filter customers by various criteria
- **QR Code Management**: Regenerate QR codes for customers who lost theirs
- **Customer Records**: Add, edit, and delete customer records

### Analytics Tab
- **Visual Reports**: View sales and customer visit charts
- **Data Export**: Export data to Excel for further analysis
- **Shift Reports**: Generate end-of-shift reports in PDF format
- **Visit Tracking**: Track customer visit frequency and preferences

## Technical Details

### Architecture
The application is built using a modular architecture with the following components:

1. **Main Application (main.py)**: The core application with the user interface
2. **Database Manager (database_manager.py)**: Handles data storage and retrieval
3. **QR Code Utilities (qr_utils.py)**: Manages QR code generation and scanning
4. **Report Generator (rt_generator.py)**: Creates reports and exports data

### Data Storage
- Customer data is stored in CSV files for simplicity and portability
- QR codes are stored in a dedicated folder for easy access
- Reports are generated in PDF format for professional presentation

### User Interface
- Modern dark theme optimized for gaming aesthetics
- Tab-based navigation for intuitive user experience
- Responsive layout that works well on various screen sizes
- Trinix Gaming branding throughout the application

## Installation and Usage

### Prerequisites
- Python 3.8 or higher
- Required Python packages (see requirements.txt)
- Webcam for QR code scanning

### Installation
1. Install required dependencies: `pip install -r requirements.txt`
2. Run the application: `python main.py` or use the provided batch file

### Building the Executable
1. Run the build script: `python build_exe.py`
2. The executable will be created in the `dist` folder

## File Structure
```
trinix_gaming_shop/
├── main.py                  # Main application file
├── database_manager.py      # Database management module
├── qr_utils.py              # QR code utilities
├── rt_generator.py          # Report generation module
├── qr_icon.py               # QR code icon generator
├── requirements.txt         # Python dependencies
├── build_exe.py             # Script to build executable
├── installer.nsi            # NSIS installer script
├── LICENSE.txt              # License information
├── README.txt               # User documentation
├── run_trinix_app.bat       # Batch file to run application
├── build_executable.bat     # Batch file to build executable
├── data/                    # Data storage directory
├── qr_codes/                # QR code storage directory
└── reports/                 # Generated reports directory
```

## Future Enhancements
- Integration with cloud storage for data backup
- Mobile application for customers to view their gaming history
- Advanced analytics with predictive modeling for business insights
- Loyalty program management for regular customers
- Integration with payment gateways for online payments
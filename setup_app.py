import os
import sys

def setup_app():
    """Set up the PS Gaming Shop application"""
    print("Setting up PS Gaming Shop application...")
    
    # Create necessary directories
    directories = ['data', 'qr_codes', 'reports']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Create logo if it doesn't exist
    if not any(os.path.exists(logo) for logo in ["PS Logo.png", "PS_logo.png"]):
        try:
            print("Creating logo...")
            from create_logo import create_logo
            logo_path = create_logo()
            print(f"Logo created: {logo_path}")
        except Exception as e:
            print(f"Error creating logo: {e}")
    
    # Create QR icon if it doesn't exist
    if not os.path.exists("qr_icon.png"):
        try:
            print("Creating QR icon...")
            from qr_icon import create_qr_icon
            icon_path = create_qr_icon()
            print(f"QR icon created: {icon_path}")
        except Exception as e:
            print(f"Error creating QR icon: {e}")
    
    print("\nSetup complete! You can now run the application using:")
    print("python main.py")
    print("or by double-clicking run_PS_app.bat")

if __name__ == "__main__":
    setup_app()

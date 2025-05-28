import os
import sys
import cv2
import qrcode
from PIL import Image
import numpy as np

def create_test_qr_code(data, filename="test_qr.png"):
    """Create a test QR code with the given data"""
    print(f"Creating QR code with data: {data}")
    
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    
    # Add data to QR code
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create QR code image
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR code
    qr_img.save(filename)
    print(f"QR code saved to {filename}")
    
    return filename

def test_qr_code_reading(image_path):
    """Test reading a QR code from an image file"""
    print(f"Testing QR code reading from {image_path}")
    
    # Read image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not read image from {image_path}")
        return
    
    # Create QR code detector
    detector = cv2.QRCodeDetector()
    
    # Detect and decode QR code
    data, bbox, _ = detector.detectAndDecode(image)
    
    if bbox is not None:
        print(f"QR code detected with data: {data}")
    else:
        print("No QR code detected with OpenCV")
        
        # Try with pyzbar if available
        try:
            import pyzbar.pyzbar as pyzbar
            
            # Convert image to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Decode QR code
            decoded_objects = pyzbar.decode(gray)
            
            if decoded_objects:
                print(f"QR code detected with pyzbar: {decoded_objects[0].data.decode('utf-8')}")
            else:
                print("No QR code detected with pyzbar")
        except ImportError:
            print("pyzbar not available, install with: pip install pyzbar")

def main():
    """Main function"""
    # Create a test QR code
    test_data = "TRINIX-CUSTOMER:John Doe:1234567890:Nairobi"
    qr_path = create_test_qr_code(test_data)
    
    # Test reading the QR code
    test_qr_code_reading(qr_path)
    
    # Test with a custom QR code if provided
    if len(sys.argv) > 1:
        custom_qr_path = sys.argv[1]
        if os.path.exists(custom_qr_path):
            test_qr_code_reading(custom_qr_path)
        else:
            print(f"Error: File {custom_qr_path} does not exist")

if __name__ == "__main__":
    main()
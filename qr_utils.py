import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np

class QRCodeManager:
    """
    Utility class for generating and reading QR codes
    """
    
    def __init__(self, qr_dir="qr_codes", logo_path=None):
        """Initialize the QR code manager"""
        self.qr_dir = qr_dir
        self.logo_path = logo_path
        
        # Create QR codes directory if it doesn't exist
        os.makedirs(qr_dir, exist_ok=True)
    
    def generate_qr_code(self, data, customer_id, customer_name=None, include_logo=True):
        """
        Generate a QR code with the given data
        
        Args:
            data: The data to encode in the QR code
            customer_id: The customer ID (used for filename)
            customer_name: The customer name (used for filename)
            include_logo: Whether to include the Trinix logo in the QR code
            
        Returns:
            The path to the generated QR code image
        """
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction for logo
            box_size=10,
            border=4,
        )
        
        # Add data to QR code
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGBA')
        
        # Add logo if requested and logo path is provided
        if include_logo and self.logo_path and os.path.exists(self.logo_path):
            try:
                # Open logo image
                logo = Image.open(self.logo_path).convert('RGBA')
                
                # Calculate logo size (max 30% of QR code)
                qr_width, qr_height = qr_img.size
                logo_size = min(qr_width, qr_height) // 3
                
                # Resize logo
                logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
                
                # Calculate position to center logo
                pos_x = (qr_width - logo_size) // 2
                pos_y = (qr_height - logo_size) // 2
                
                # Create a white background for the logo
                logo_bg = Image.new('RGBA', (logo_size, logo_size), (255, 255, 255, 255))
                
                # Paste logo onto QR code
                qr_img.paste(logo_bg, (pos_x, pos_y), logo_bg)
                qr_img.paste(logo, (pos_x, pos_y), logo)
            except Exception as e:
                print(f"Error adding logo to QR code: {e}")
        
        # Add text to QR code
        try:
            # Create a drawing context
            draw = ImageDraw.Draw(qr_img)
            
            # Try to use a nice font, fall back to default
            try:
                title_font = ImageFont.truetype("arial.ttf", 20)
                name_font = ImageFont.truetype("arial.ttf", 16)
            except:
                title_font = ImageFont.load_default()
                name_font = ImageFont.load_default()
            
            # Add company name at the bottom
            company_text = "Trinix Gaming"
            company_text_width = draw.textlength(company_text, font=title_font)
            company_text_x = (qr_img.width - company_text_width) // 2
            company_text_y = qr_img.height - 40
            
            draw.text((company_text_x, company_text_y), company_text, fill="black", font=title_font)
            
            # Add customer name if provided
            if customer_name:
                # Truncate name if too long
                if len(customer_name) > 20:
                    display_name = customer_name[:17] + "..."
                else:
                    display_name = customer_name
                    
                name_text = f"Name: {display_name}"
                name_text_width = draw.textlength(name_text, font=name_font)
                name_text_x = (qr_img.width - name_text_width) // 2
                name_text_y = qr_img.height - 20
                
                draw.text((name_text_x, name_text_y), name_text, fill="black", font=name_font)
        except Exception as e:
            print(f"Error adding text to QR code: {e}")
        
        # Save QR code with customer name in filename
        if customer_name:
            # Clean the customer name for use in a filename (remove invalid characters)
            clean_name = ''.join(c for c in customer_name if c.isalnum() or c in ' _-').strip()
            clean_name = clean_name.replace(' ', '_')
            filename = f"customer_{customer_id}_{clean_name}.png"
        else:
            filename = f"customer_{customer_id}.png"
            
        qr_path = os.path.join(self.qr_dir, filename)
        qr_img.save(qr_path)
        
        return qr_path
    
    def read_qr_code(self, image):
        """
        Read QR code from an image
        
        Args:
            image: The image containing the QR code (numpy array from OpenCV)
            
        Returns:
            The data encoded in the QR code, or None if no QR code is found
        """
        if image is None or image.size == 0:
            print("Invalid image provided to QR code reader")
            return None
            
        try:
            # Create QR code detector
            detector = cv2.QRCodeDetector()
            
            # Method 1: Standard OpenCV QR detection
            data, bbox, _ = detector.detectAndDecode(image)
            
            if bbox is not None and data:
                print(f"QR Code detected with standard method: {data}")
                return data
            
            # Method 2: Try with ZBar if available
            try:
                import pyzbar.pyzbar as pyzbar
                decoded_objects = pyzbar.decode(image)
                
                if decoded_objects:
                    # Return the first decoded QR code
                    data = decoded_objects[0].data.decode('utf-8')
                    print(f"QR Code detected with ZBar: {data}")
                    return data
            except ImportError:
                # ZBar not available, continue with other methods
                pass
            
            # Method 3: Try with grayscale image
            try:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                data, bbox, _ = detector.detectAndDecode(gray)
                
                if bbox is not None and data:
                    print(f"QR Code detected with grayscale: {data}")
                    return data
            except Exception as e:
                print(f"Error in grayscale detection: {e}")
            
            # Method 4: Try with adaptive thresholding
            try:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                thresh = cv2.adaptiveThreshold(
                    gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
                )
                data, bbox, _ = detector.detectAndDecode(thresh)
                
                if bbox is not None and data:
                    print(f"QR Code detected with adaptive threshold: {data}")
                    return data
            except Exception as e:
                print(f"Error in threshold detection: {e}")
            
            # Method 5: Try with different thresholding
            try:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
                data, bbox, _ = detector.detectAndDecode(binary)
                
                if bbox is not None and data:
                    print(f"QR Code detected with binary threshold: {data}")
                    return data
            except Exception as e:
                print(f"Error in binary threshold detection: {e}")
            
            # Method 6: Try with resized image
            try:
                resized = cv2.resize(image, (640, 480))
                data, bbox, _ = detector.detectAndDecode(resized)
                
                if bbox is not None and data:
                    print(f"QR Code detected with resized image: {data}")
                    return data
            except Exception as e:
                print(f"Error in resized detection: {e}")
                
        except Exception as e:
            print(f"Error reading QR code: {e}")
        
        return None
import qrcode
from PIL import Image, ImageDraw
import os

def create_qr_icon():
    """Create a simple QR code icon for the application"""
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    
    # Add data to QR code
    qr.add_data("Trinix Gaming QR Scanner")
    qr.make(fit=True)
    
    # Create QR code image
    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGBA')
    
    # Create a circular mask
    mask = Image.new('L', qr_img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, qr_img.size[0], qr_img.size[1]), fill=255)
    
    # Apply mask to create circular QR code
    circular_qr = Image.new('RGBA', qr_img.size, (255, 255, 255, 0))
    circular_qr.paste(qr_img, (0, 0), mask)
    
    # Save icon
    circular_qr.save("qr_icon.png")
    
    return "qr_icon.png"

if __name__ == "__main__":
    create_qr_icon()
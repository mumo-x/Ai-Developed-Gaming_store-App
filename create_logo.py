from PIL import Image, ImageDraw, ImageFont
import os

def create_logo():
    """Create a simple logo for the Trinix Gaming Shop application"""
    # Create a new image with a transparent background
    width, height = 500, 500
    logo = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(logo)
    
    # Draw a purple circle
    circle_color = (106, 27, 154, 255)  # #6a1b9a (purple)
    draw.ellipse((50, 50, width-50, height-50), fill=circle_color)
    
    # Add text
    try:
        # Try to use a nice font, fall back to default
        font = ImageFont.truetype("arial.ttf", 80)
    except:
        font = ImageFont.load_default()
    
    # Draw "TRINIX" text
    text = "TRINIX"
    text_width = draw.textlength(text, font=font)
    text_x = (width - text_width) // 2
    text_y = height // 2 - 60
    draw.text((text_x, text_y), text, fill="white", font=font)
    
    # Draw "GAMING" text
    text = "GAMING"
    text_width = draw.textlength(text, font=font)
    text_x = (width - text_width) // 2
    text_y = height // 2 + 20
    draw.text((text_x, text_y), text, fill="white", font=font)
    
    # Save logo
    logo.save("trinix_logo.png")
    
    return "trinix_logo.png"

if __name__ == "__main__":
    create_logo()
    print("Logo created successfully!")
from PIL import Image
import os

def convert_png_to_ico(png_path, ico_path, sizes=[(256,256), (128,128), (64,64), (48,48), (32,32), (16,16)]):
    """
    Convert a PNG image to ICO format with multiple sizes.
    """
    if not os.path.exists(png_path):
        print(f"PNG file not found: {png_path}")
        return False
    try:
        img = Image.open(png_path)
        img.save(ico_path, format='ICO', sizes=sizes)
        print(f"ICO file created successfully: {ico_path}")
        return True
    except Exception as e:
        print(f"Error converting PNG to ICO: {e}")
        return False

if __name__ == "__main__":
    png_file = "PS Gamers.png"
    ico_file = "PS Gamers.ico"
    convert_png_to_ico(png_file, ico_file)

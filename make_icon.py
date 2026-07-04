from PIL import Image
import os

# Automatically look for your sitter image
possible_extensions = [".png", ".jpg", ".jpeg", ".webp"]
image_path = None

for ext in possible_extensions:
    if os.path.exists(f"sitter{ext}"):
        image_path = f"sitter{ext}"
        break

if image_path:
    img = Image.open(image_path)
    # Windows icons work best at 256x256 max resolution
    img.save("sitter_icon.ico", format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print("Success! Created sitter_icon.ico")
else:
    print("Could not find your sitter image file.")
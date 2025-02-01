import os
from PIL import Image

# Input and output directories
input_dir = "."
output_dir = "."

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Iterate through BMP files and convert
for filename in os.listdir(input_dir):
    if filename.endswith(".bmp"):
        bmp_path = os.path.join(input_dir, filename)
        jpg_path = os.path.join(output_dir, os.path.splitext(filename)[0] + ".jpg")

        # Open and convert the image
        with Image.open(bmp_path) as img:
            img.convert("RGB").save(jpg_path, "JPEG")
            print(f"Converted: {bmp_path} -> {jpg_path}")

print("Batch conversion complete!")

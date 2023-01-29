import os
from pathlib import Path

def clear_all_images():
    base_dir = Path("").absolute()
    image_dir = os.path.join(base_dir, "app", "core", "resources", "images")
    for filename in os.listdir(image_dir):
        if filename not in ("test_image.json", "test_image.png"):
            file_path = os.path.join(image_dir, filename)
            os.remove(file_path)

clear_all_images()

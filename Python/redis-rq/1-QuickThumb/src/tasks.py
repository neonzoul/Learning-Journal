import os
from PIL import Image

THUMBNAIL_SIZE = (128, 128)

def resize_image(original_path: str) -> str:
    print(f"Chef says: 'Got an order to resize {original_path}'")
    try:
        os.makedirs("processed", exist_ok=True)
        filename = os.path.basename(original_path)
        processed_path = os.path.join("processed", filename)

        with Image.open(original_path) as img:
            img.thumbnail(THUMBNAIL_SIZE)
            img.save(processed_path)

        os.remove(original_path)

        print(f"Chef says: 'Order for {filename} is ready!'")
        return "Finished successfully."
    except Exception as e:
        print(f"Chef says: 'Something went wrong with this order! Error: {e}'")
        return "Failed."

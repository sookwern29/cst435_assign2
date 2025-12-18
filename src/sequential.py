import os
import time
from utils import process_image

IMAGE_DIR = "../data/waffles"
OUTPUT_DIR = "../output/serial"

images = [
    os.path.join(IMAGE_DIR, img)
    for img in os.listdir(IMAGE_DIR)
]

start_time = time.time()

for img_path in images:
    process_image(img_path, OUTPUT_DIR)

end_time = time.time()

print(f"Serial execution time: {end_time - start_time:.4f} seconds")

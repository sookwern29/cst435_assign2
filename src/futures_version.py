import os
import time
from concurrent.futures import ProcessPoolExecutor
from utils import process_image

IMAGE_DIR = "../data/waffles"
OUTPUT_DIR = "../output/futures"
NUM_WORKERS = 8   # try 1, 2, 4, 8

if __name__ == '__main__':
    images = [
        os.path.join(IMAGE_DIR, img)
        for img in os.listdir(IMAGE_DIR)
    ]

    start_time = time.time()

    with ProcessPoolExecutor(max_workers=NUM_WORKERS) as executor:
        for img in images:
            executor.submit(process_image, img, OUTPUT_DIR)

    end_time = time.time()

    print(
        f"Futures ({NUM_WORKERS} workers) "
        f"time: {end_time - start_time:.4f} seconds"
    )

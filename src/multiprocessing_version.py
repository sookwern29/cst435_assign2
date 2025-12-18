import os
import time
from multiprocessing import Pool
from utils import process_image

IMAGE_DIR = "../data/waffles"
OUTPUT_DIR = "../output/multiprocessing"
NUM_PROCESSES = 8   # try 1, 2, 4, 8

if __name__ == '__main__':
    images = [
        os.path.join(IMAGE_DIR, img)
        for img in os.listdir(IMAGE_DIR)
    ]

    args = [(img, OUTPUT_DIR) for img in images]

    start_time = time.time()

    with Pool(processes=NUM_PROCESSES) as pool:
        pool.starmap(process_image, args)

    end_time = time.time()

    print(
        f"Multiprocessing ({NUM_PROCESSES} processes) "
        f"time: {end_time - start_time:.4f} seconds"
    )

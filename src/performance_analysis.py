import os
import time
from multiprocessing import Pool
from concurrent.futures import ProcessPoolExecutor
from utils import process_image

IMAGE_DIR = os.path.join(os.path.dirname(__file__), "../data/waffles")
OUTPUT_BASE = os.path.join(os.path.dirname(__file__), "../output")

def run_sequential(images, output_dir):
    start_time = time.time()
    for img_path in images:
        process_image(img_path, output_dir)
    return time.time() - start_time

def run_multiprocessing(images, output_dir, num_processes):
    args = [(img, output_dir) for img in images]
    start_time = time.time()
    with Pool(processes=num_processes) as pool:
        pool.starmap(process_image, args)
    return time.time() - start_time

def run_futures(images, output_dir, num_workers):
    start_time = time.time()
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(process_image, img, output_dir) for img in images]
        for future in futures:
            future.result()
    return time.time() - start_time

if __name__ == '__main__':
    images = [os.path.join(IMAGE_DIR, img) for img in os.listdir(IMAGE_DIR)]

    # Run sequential
    seq_output = os.path.join(OUTPUT_BASE, "sequential")
    seq_time = run_sequential(images, seq_output)
    print(f"Sequential time: {seq_time:.4f} seconds")

    # Process counts to test
    process_counts = [1, 2, 4, 8]

    # Multiprocessing results
    mp_results = []
    for count in process_counts:
        output_dir = os.path.join(OUTPUT_BASE, f"multiprocessing_{count}")
        time_taken = run_multiprocessing(images, output_dir, count)
        speedup = seq_time / time_taken
        efficiency = speedup / count
        mp_results.append((count, time_taken, speedup, efficiency))
        print(f"Multiprocessing ({count} processes): {time_taken:.4f}s, Speedup: {speedup:.2f}, Efficiency: {efficiency:.2f}")

    # Futures results
    futures_results = []
    for count in process_counts:
        output_dir = os.path.join(OUTPUT_BASE, f"futures_{count}")
        time_taken = run_futures(images, output_dir, count)
        speedup = seq_time / time_taken
        efficiency = speedup / count
        futures_results.append((count, time_taken, speedup, efficiency))
        print(f"Futures ({count} workers): {time_taken:.4f}s, Speedup: {speedup:.2f}, Efficiency: {efficiency:.2f}")

    # Print comparison table
    print("\nComparison Table:")
    print("Method\t\tProcesses\tTime (s)\tSpeedup\tEfficiency")
    print("-" * 60)
    for count, t, s, e in mp_results:
        print(f"Multiprocessing\t{count}\t\t{t:.4f}\t{s:.2f}\t{e:.2f}")
    for count, t, s, e in futures_results:
        print(f"Futures\t\t{count}\t\t{t:.4f}\t{s:.2f}\t{e:.2f}")
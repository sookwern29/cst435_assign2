import os
import time
from multiprocessing import Pool
from concurrent.futures import ProcessPoolExecutor
from utils import process_image

def chunk_data(data, num_chunks):
    """Split data into approximately equal chunks."""
    chunk_size = len(data) // num_chunks
    remainder = len(data) % num_chunks
    chunks = []
    start = 0
    for i in range(num_chunks):
        end = start + chunk_size + (1 if i < remainder else 0)
        chunks.append(data[start:end])
        start = end
    return chunks

def process_chunk(chunk, output_dir):
    """Process a chunk of images."""
    for img_path in chunk:
        process_image(img_path, output_dir)

def data_parallelism_multiprocessing(images, output_dir, num_processes):
    """Data parallelism using multiprocessing Pool with starmap."""
    chunks = chunk_data(images, num_processes)
    args = [(chunk, output_dir) for chunk in chunks]
    start_time = time.time()
    with Pool(processes=num_processes) as pool:
        pool.starmap(process_chunk, args)
    return time.time() - start_time

def data_parallelism_futures(images, output_dir, num_workers):
    """Data parallelism using futures by manually chunking data."""
    chunks = chunk_data(images, num_workers)
    start_time = time.time()
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(process_chunk, chunk, output_dir) for chunk in chunks]
        for future in futures:
            future.result()
    return time.time() - start_time

def task_parallelism_multiprocessing(images, output_dir, num_processes):
    """Task parallelism using multiprocessing Pool with apply_async."""
    start_time = time.time()
    with Pool(processes=num_processes) as pool:
        results = [pool.apply_async(process_image, (img, output_dir)) for img in images]
        for result in results:
            result.get()
    return time.time() - start_time

def task_parallelism_futures(images, output_dir, num_workers):
    """Task parallelism using futures ProcessPoolExecutor."""
    start_time = time.time()
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(process_image, img, output_dir) for img in images]
        for future in futures:
            future.result()
    return time.time() - start_time
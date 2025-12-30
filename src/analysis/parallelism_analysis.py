import os
import time
import threading
from multiprocessing import Pool
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from utils import process_image

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

def get_core_id():
    """Get CPU core ID"""
    if HAS_PSUTIL:
        try:
            p = psutil.Process()
            return p.cpu_num()
        except:
            return "N/A"
    return "N/A"

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

def process_chunk(chunk, chunk_id, output_dir):
    """Process a chunk of images and return logging info."""
    start_time = time.time()
    
    for img_path in chunk:
        process_image(img_path, output_dir)
    
    end_time = time.time()
    core_id = get_core_id()
    pid = os.getpid()
    tid = threading.get_ident()
    
    return {
        'chunk_id': chunk_id,
        'core_id': core_id,
        'pid': pid,
        'tid': tid,
        'duration': end_time - start_time
    }

def data_parallelism_multiprocessing(images, output_dir, num_processes):
    """Data parallelism using multiprocessing Pool with starmap."""
    chunks = chunk_data(images, num_processes)
    args = [(chunk, i, output_dir) for i, chunk in enumerate(chunks, 1)]
    
    print(f"\n{'='*20} Method 2: Multiprocessing {'='*20}")
    start_time = time.time()
    
    with Pool(processes=num_processes) as pool:
        results = pool.starmap(process_chunk, args)
    
    total_duration = time.time() - start_time
    
    # Print results
    for res in results:
        print(f"[Process] Data Chunk ID: {res['chunk_id']} ---> CPU Core ID: {res['core_id']}")
        print(f"Identity Info: PID:{res['pid']} | TID:{res['tid']}")
        print(f"Time Consumed: {res['duration']:.4f}s")
        print("-" * 60)
    
    return total_duration, results

def data_parallelism_futures(images, output_dir, num_workers):
    """Data parallelism using futures with multithreading (ThreadPoolExecutor)."""
    chunks = chunk_data(images, num_workers)
    
    print(f"\n{'='*20} Method 1: Concurrent Futures (Threading) {'='*20}")
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(process_chunk, chunk, i, output_dir) for i, chunk in enumerate(chunks, 1)]
        results = [future.result() for future in futures]
    
    total_duration = time.time() - start_time
    
    # Print results
    for res in results:
        print(f"[Thread] Data Chunk ID: {res['chunk_id']} ---> CPU Core ID: {res['core_id']}")
        print(f"Identity Info: PID:{res['pid']} | TID:{res['tid']}")
        print(f"Time Consumed: {res['duration']:.4f}s")
        print("-" * 60)
    
    return total_duration, results

def task_parallelism_multiprocessing(images, output_dir, num_processes):
    """Task parallelism using multiprocessing Pool with apply_async."""
    start_time = time.time()
    with Pool(processes=num_processes) as pool:
        results = [pool.apply_async(process_image, (img, output_dir)) for img in images]
        for result in results:
            result.get()
    return time.time() - start_time

def task_parallelism_futures(images, output_dir, num_workers):
    """Task parallelism using futures with multithreading (ThreadPoolExecutor)."""
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(process_image, img, output_dir) for img in images]
        for future in futures:
            future.result()
    return time.time() - start_time
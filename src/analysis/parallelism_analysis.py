import os
import time
import threading
from multiprocessing import Pool
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from utils import process_image

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

def get_core_id(): 
    """Get CPU core ID specifically""" 
    if HAS_PSUTIL: 
        try: 
            p = psutil.Process() 
            return p.cpu_num() 
        except: 
            return "N/A" 
    return "N/A (psutil not installed)" 
 
# def get_thread_info(): 
#     """Get PID and TID""" 
#     pid = os.getpid() 
#     tid = threading.get_ident() 
#     return f"PID:{pid} | TID:{tid}"

def chunk_data(data, num_chunks, output_dir):
    """Split data into approximately equal chunks."""
    chunk_size = len(data) // num_chunks
    remainder = len(data) % num_chunks
    chunks = []
    start = 0
    for i in range(num_chunks):
        end = start + chunk_size + (1 if i < remainder else 0)
        chunks.append((data[start:end], i, output_dir))  # Include chunk_id and output_dir
        start = end
    return chunks

def process_chunk(chunk, chunk_id, output_dir):
    """Process a chunk of images and return logging info."""
    start_time = time.time()
    
    # Process images
    for img_path in chunk:
        process_image(img_path, output_dir)
    
    end_time = time.time()
    # core_id = os.getpid()
    core_id = get_core_id()
    # thread_info = get_thread_info()
    pid = os.getpid() 
    tid = threading.get_ident() 

    return {
        'chunk_id': chunk_id,
        'core_id': core_id,
        # 'thread_info': thread_info,
        'pid': pid,
        'tid': tid,
        'duration': end_time - start_time,
        'start_time': start_time,
        'end_time': end_time
    }

def data_parallelism_multiprocessing(images, output_dir, num_processes):
    """Data parallelism using multiprocessing Pool with starmap."""
    chunks = chunk_data(images, num_processes, output_dir)
    start_time = time.time()

    with Pool(processes=num_processes) as pool:
        results = pool.starmap(process_chunk, chunks)
    
    total_duration = time.time() - start_time
    
    # Collect logs
    logs = []
    for res in results:
        res['total_process'] = num_processes  # Add total process count to each log
        logs.append(res)
        
        # Print log
        print(f"[Process] Data Chunk ID: {res['chunk_id']} ---> CPU Core ID: {res['core_id']}")
        # print(f"Identity Info: {res['thread_info']}")
        print(f"Identity Info: PID:{res['pid']} | TID:{res['tid']}")
        print(f"Time Consumed: {res['duration']:.4f}s")
    
    return total_duration, logs

def data_parallelism_threading(images, output_dir, num_workers):
    """Data parallelism using futures by manually chunking data."""
    chunks = chunk_data(images, num_workers, output_dir)
    start_time = time.time()
    
    # with ThreadPoolExecutor(max_workers=num_workers) as executor:
    #     futures = [executor.submit(process_chunk, chunk, output_dir) for chunk in chunks]
    #     for future in futures:
    #         future.result()
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        # submit accepts arguments as separate items, so unpack the tuple
        futures = [
            executor.submit(process_chunk, chunk, chunk_id, output_dir)
            for chunk, chunk_id, output_dir in chunks
        ]

        logs = []
        for future in as_completed(futures): 
            res = future.result()

            # Collect logs
            res['total_workers'] = num_workers  # Add total worker count to each log
            logs.append(res)
        
            # Print log
            print(f"[Thread] Data Chunk ID: {res['chunk_id']} ---> CPU Core ID: {res['core_id']}")
            # print(f"Identity Info: {res['thread_info']}")
            print(f"Identity Info: PID:{res['pid']} | TID:{res['tid']}")
            print(f"Time Consumed: {res['duration']:.4f}s")
    
    total_duration = time.time() - start_time  
    
    return total_duration, logs

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
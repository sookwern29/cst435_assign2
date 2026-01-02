import os
import sys
import time
import zipfile
from cv2 import log
from tqdm import tqdm

# Set matplotlib backend for headless environments (GCP, servers without display)
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

# Add src directory to path for proper imports
sys.path.insert(0, os.path.dirname(__file__))

from utils import process_image
from analysis import analyze_data_parallelism, analyze_task_parallelism, print_detailed_comparison, save_results_to_excel, plot_comparison, plot_core_timeline

IMAGE_DIR = os.path.join(os.path.dirname(__file__), "../data/waffles")
OUTPUT_BASE = os.path.join(os.path.dirname(__file__), "../output")

def run_sequential(images, output_dir):
    start_time = time.time()
    for img_path in images:
        process_image(img_path, output_dir)
    return time.time() - start_time

if __name__ == '__main__':
    # Unzip data.zip if it exists
    zip_path = os.path.join(os.path.dirname(__file__), "../data.zip")
    if os.path.exists(zip_path):
        extract_to = os.path.join(os.path.dirname(__file__), "../data")
        os.makedirs(extract_to, exist_ok=True)
        print(f"Unzipping {zip_path} to {extract_to}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            for file in tqdm(file_list, desc="Unzipping", unit="file"):
                zip_ref.extract(file, extract_to)
        print("Unzipping complete.")
        print("Contents of data folder:", os.listdir(extract_to))

    # Find all image directories in data/ folder
    data_dir = os.path.join(os.path.dirname(__file__), "../data")
    image_dirs = []
    
    if os.path.exists(data_dir):
        for item in os.listdir(data_dir):
            item_path = os.path.join(data_dir, item)
            if os.path.isdir(item_path):
                # Check if it contains images
                try:
                    images_check = [f for f in os.listdir(item_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))]
                    if images_check:
                        image_dirs.append(item_path)
                except (PermissionError, FileNotFoundError):
                    continue

    if not image_dirs:
        print("No image directories found.")
        sys.exit(1)

    # Collect all images from all directories
    all_images = []
    for image_dir in image_dirs:
        folder_name = os.path.basename(image_dir)
        print(f"Found folder: {folder_name}")
        images = [os.path.join(image_dir, img) for img in os.listdir(image_dir) if img.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))]
        all_images.extend(images)
        print(f"  {len(images)} images")

    print(f"Total images: {len(all_images)}")

    if not all_images:
        print("No images found in any directory.")
        sys.exit(1)

    # Analyze data parallelism with both libraries (using 1-core as baseline)
    data_mp_results, data_futures_results, logs_mp, logs_futures = analyze_data_parallelism(all_images)
    # data_mp_results, logs_mp = analyze_data_parallelism(all_images, seq_time)

    # Analyze task parallelism with both libraries
    # task_mp_results, task_futures_results = analyze_task_parallelism(all_images, seq_time)

    # Print detailed comparison
    print_detailed_comparison(data_mp_results, data_futures_results)

    # Save results to Excel
    save_results_to_excel(data_mp_results, data_futures_results, logs_mp=logs_mp, logs_futures=logs_futures)

    # Generate comparison plots
    plot_comparison(data_mp_results, data_futures_results)
    
    # Generate timeline visualizations showing core usage (for 4 and 8 workers)
    print("\n=== Generating Timeline Visualizations ===")
    from analysis import analyze_data_parallelism
    
    # Get logs for specific worker counts
    _, _, logs_mp_8, _ = analyze_data_parallelism.__wrapped__ if hasattr(analyze_data_parallelism, '__wrapped__') else (None, None, logs_mp, logs_futures)
    
    # Plot timeline for 8 workers (most interesting to see core usage)
    # Filter logs for 8-worker runs
    logs_mp_8_workers = [log for log in logs_mp if log.get('chunk_id', -1) < 8]
    logs_mt_8_workers = [log for log in logs_futures if log.get('chunk_id', -1) < 8]
    
    if logs_mp_8_workers:
        plot_core_timeline(logs_mp_8_workers, 8, "Multiprocessing (8 Workers)")
    if logs_mt_8_workers:
        plot_core_timeline(logs_mt_8_workers, 8, "Multithreading (8 Workers)")
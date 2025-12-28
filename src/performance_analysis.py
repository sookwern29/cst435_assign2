import os
import sys
import time
import zipfile
from tqdm import tqdm

# Add src directory to path for proper imports
sys.path.insert(0, os.path.dirname(__file__))

from utils import process_image
from analysis import analyze_data_parallelism, analyze_task_parallelism, print_detailed_comparison, save_results_to_excel, plot_comparison

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
        extract_to = os.path.join(os.path.dirname(__file__), "..")
        os.makedirs(extract_to, exist_ok=True)
        print(f"Unzipping {zip_path} to {extract_to}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            for file in tqdm(file_list, desc="Unzipping", unit="file"):
                zip_ref.extract(file, extract_to)
        print("Unzipping complete.")
        print("Contents of", extract_to, ":", os.listdir(extract_to))

    # Find all image directories
    extract_to = os.path.join(os.path.dirname(__file__), "..")
    data_dir = os.path.join(extract_to, 'data')
    image_dirs = []
    if os.path.exists(data_dir):
        for item in os.listdir(data_dir):
            item_path = os.path.join(data_dir, item)
            if os.path.isdir(item_path):
                # Check if it contains images
                images_check = [f for f in os.listdir(item_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))]
                if images_check:
                    image_dirs.append(item_path)
    else:
        # Fallback
        fallback_dir = os.path.join(os.path.dirname(__file__), "../data/waffles")
        if os.path.exists(fallback_dir):
            image_dirs = [fallback_dir]

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

    # Run sequential baseline
    seq_output = os.path.join(OUTPUT_BASE, "sequential")
    seq_time = run_sequential(all_images, seq_output)
    print(f"Sequential baseline time: {seq_time:.4f} seconds")

    # Analyze data parallelism with both libraries
    data_mp_results, data_futures_results = analyze_data_parallelism(all_images, seq_time)

    # Analyze task parallelism with both libraries
    # task_mp_results, task_futures_results = analyze_task_parallelism(all_images, seq_time)

    # Print detailed comparison
    # print_detailed_comparison(data_mp_results, data_futures_results, task_mp_results, task_futures_results)
    print_detailed_comparison(data_mp_results, data_futures_results)

    # Save results to Excel
    # save_results_to_excel(seq_time, data_mp_results, data_futures_results, task_mp_results, task_futures_results)
    save_results_to_excel(seq_time, data_mp_results, data_futures_results)

    # Generate comparison plots
    # plot_comparison(seq_time, data_mp_results, data_futures_results, task_mp_results, task_futures_results)
    plot_comparison(seq_time, data_mp_results, data_futures_results)
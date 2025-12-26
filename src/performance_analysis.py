import os
import sys
import time

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
    images = [os.path.join(IMAGE_DIR, img) for img in os.listdir(IMAGE_DIR)]

    # Run sequential baseline
    seq_output = os.path.join(OUTPUT_BASE, "sequential")
    seq_time = run_sequential(images, seq_output)
    print(f"Sequential baseline time: {seq_time:.4f} seconds")

    # Analyze data parallelism with both libraries
    data_mp_results, data_futures_results = analyze_data_parallelism(images, seq_time)

    # Analyze task parallelism with both libraries
    task_mp_results, task_futures_results = analyze_task_parallelism(images, seq_time)

    # Print detailed comparison
    print_detailed_comparison(data_mp_results, data_futures_results, task_mp_results, task_futures_results)

    # Save results to Excel
    save_results_to_excel(seq_time, data_mp_results, data_futures_results, task_mp_results, task_futures_results)

    # Generate comparison plots
    plot_comparison(seq_time, data_mp_results, data_futures_results, task_mp_results, task_futures_results)
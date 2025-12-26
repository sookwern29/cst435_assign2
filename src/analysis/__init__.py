from .parallelism_analysis import (
    data_parallelism_multiprocessing,
    data_parallelism_futures,
    task_parallelism_multiprocessing,
    task_parallelism_futures
)
import os
import pandas as pd
import matplotlib.pyplot as plt

OUTPUT_BASE = os.path.join(os.path.dirname(__file__), "../../output")

def analyze_data_parallelism(images, seq_time):
    """Analyze performance for data parallelism using both multiprocessing and futures."""
    print("\n=== Data Parallelism Analysis ===")
    counts = [1, 2, 4, 8]
    results_mp = []
    results_futures = []

    for count in counts:
        # Multiprocessing
        output_dir_mp = os.path.join(OUTPUT_BASE, f"data_mp_{count}")
        time_mp = data_parallelism_multiprocessing(images, output_dir_mp, count)
        speedup_mp = seq_time / time_mp
        efficiency_mp = speedup_mp / count
        results_mp.append((count, time_mp, speedup_mp, efficiency_mp))
        print(f"Data MP ({count} processes): {time_mp:.4f}s, Speedup: {speedup_mp:.2f}, Efficiency: {efficiency_mp:.2f}")

        # Futures
        output_dir_futures = os.path.join(OUTPUT_BASE, f"data_futures_{count}")
        time_futures = data_parallelism_futures(images, output_dir_futures, count)
        speedup_futures = seq_time / time_futures
        efficiency_futures = speedup_futures / count
        results_futures.append((count, time_futures, speedup_futures, efficiency_futures))
        print(f"Data Futures ({count} workers): {time_futures:.4f}s, Speedup: {speedup_futures:.2f}, Efficiency: {efficiency_futures:.2f}")

    return results_mp, results_futures

def analyze_task_parallelism(images, seq_time):
    """Analyze performance for task parallelism using both multiprocessing and futures."""
    print("\n=== Task Parallelism Analysis ===")
    counts = [1, 2, 4, 8]
    results_mp = []
    results_futures = []

    for count in counts:
        # Multiprocessing
        output_dir_mp = os.path.join(OUTPUT_BASE, f"task_mp_{count}")
        time_mp = task_parallelism_multiprocessing(images, output_dir_mp, count)
        speedup_mp = seq_time / time_mp
        efficiency_mp = speedup_mp / count
        results_mp.append((count, time_mp, speedup_mp, efficiency_mp))
        print(f"Task MP ({count} processes): {time_mp:.4f}s, Speedup: {speedup_mp:.2f}, Efficiency: {efficiency_mp:.2f}")

        # Futures
        output_dir_futures = os.path.join(OUTPUT_BASE, f"task_futures_{count}")
        time_futures = task_parallelism_futures(images, output_dir_futures, count)
        speedup_futures = seq_time / time_futures
        efficiency_futures = speedup_futures / count
        results_futures.append((count, time_futures, speedup_futures, efficiency_futures))
        print(f"Task Futures ({count} workers): {time_futures:.4f}s, Speedup: {speedup_futures:.2f}, Efficiency: {efficiency_futures:.2f}")

    return results_mp, results_futures

def print_detailed_comparison(data_mp, data_futures, task_mp, task_futures):
    """Print a detailed comparison table."""
    print("\n=== Detailed Performance Comparison ===")
    print("Type\t\tLibrary\t\tWorkers\tTime (s)\tSpeedup\tEfficiency")
    print("-" * 80)

    for count, t, s, e in data_mp:
        print(f"Data\t\tMultiprocessing\t{count}\t{t:.4f}\t{s:.2f}\t{e:.2f}")
    for count, t, s, e in data_futures:
        print(f"Data\t\tFutures\t\t{count}\t{t:.4f}\t{s:.2f}\t{e:.2f}")
    for count, t, s, e in task_mp:
        print(f"Task\t\tMultiprocessing\t{count}\t{t:.4f}\t{s:.2f}\t{e:.2f}")
    for count, t, s, e in task_futures:
        print(f"Task\t\tFutures\t\t{count}\t{t:.4f}\t{s:.2f}\t{e:.2f}")

def save_results_to_excel(seq_time, data_mp, data_futures, task_mp, task_futures, filename="performance_results.xlsx"):
    """Save all results to an Excel file."""
    data = {
        'Workers': [1, 2, 4, 8],
        'Data_MP_Time': [t for _, t, _, _ in data_mp],
        'Data_MP_Speedup': [s for _, _, s, _ in data_mp],
        'Data_MP_Efficiency': [e for _, _, _, e in data_mp],
        'Data_Futures_Time': [t for _, t, _, _ in data_futures],
        'Data_Futures_Speedup': [s for _, _, s, _ in data_futures],
        'Data_Futures_Efficiency': [e for _, _, _, e in data_futures],
        'Task_MP_Time': [t for _, t, _, _ in task_mp],
        'Task_MP_Speedup': [s for _, _, s, _ in task_mp],
        'Task_MP_Efficiency': [e for _, _, _, e in task_mp],
        'Task_Futures_Time': [t for _, t, _, _ in task_futures],
        'Task_Futures_Speedup': [s for _, _, s, _ in task_futures],
        'Task_Futures_Efficiency': [e for _, _, _, e in task_futures],
    }
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f"\nResults saved to {filename}")

def plot_comparison(seq_time, data_mp, data_futures, task_mp, task_futures):
    """Generate line graphs comparing the methods."""
    counts = [1, 2, 4, 8]

    # Extract data
    data_mp_times = [t for _, t, _, _ in data_mp]
    data_futures_times = [t for _, t, _, _ in data_futures]
    task_mp_times = [t for _, t, _, _ in task_mp]
    task_futures_times = [t for _, t, _, _ in task_futures]

    data_mp_speedups = [s for _, _, s, _ in data_mp]
    data_futures_speedups = [s for _, _, s, _ in data_futures]
    task_mp_speedups = [s for _, _, s, _ in task_mp]
    task_futures_speedups = [s for _, _, s, _ in task_futures]

    # Plot execution times
    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.plot(counts, data_mp_times, label='Data MP', marker='o')
    plt.plot(counts, data_futures_times, label='Data Futures', marker='s')
    plt.plot(counts, task_mp_times, label='Task MP', marker='^')
    plt.plot(counts, task_futures_times, label='Task Futures', marker='d')
    plt.axhline(y=seq_time, color='r', linestyle='--', label='Sequential')
    plt.xlabel('Number of Workers/Processes')
    plt.ylabel('Execution Time (s)')
    plt.title('Execution Time Comparison')
    plt.legend()
    plt.grid(True)

    # Plot speedups
    plt.subplot(1, 2, 2)
    plt.plot(counts, data_mp_speedups, label='Data MP', marker='o')
    plt.plot(counts, data_futures_speedups, label='Data Futures', marker='s')
    plt.plot(counts, task_mp_speedups, label='Task MP', marker='^')
    plt.plot(counts, task_futures_speedups, label='Task Futures', marker='d')
    plt.xlabel('Number of Workers/Processes')
    plt.ylabel('Speedup')
    plt.title('Speedup Comparison')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig('performance_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Graph saved as performance_comparison.png")
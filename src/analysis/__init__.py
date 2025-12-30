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
    all_logs_mp = []
    all_logs_futures = []

    for count in counts:
        # Multiprocessing
        output_dir_mp = os.path.join(OUTPUT_BASE, f"data_mp_{count}")
        time_mp, logs_mp = data_parallelism_multiprocessing(images, output_dir_mp, count)
        speedup_mp = seq_time / time_mp
        efficiency_mp = speedup_mp / count
        results_mp.append((count, time_mp, speedup_mp, efficiency_mp))
        all_logs_mp.extend(logs_mp)
        print(f"Data MP ({count} processes): {time_mp:.4f}s, Speedup: {speedup_mp:.2f}, Efficiency: {efficiency_mp:.2f}")

        # Futures
        output_dir_futures = os.path.join(OUTPUT_BASE, f"data_futures_{count}")
        time_futures, logs_futures = data_parallelism_futures(images, output_dir_futures, count)
        speedup_futures = seq_time / time_futures
        efficiency_futures = speedup_futures / count
        results_futures.append((count, time_futures, speedup_futures, efficiency_futures))
        all_logs_futures.extend(logs_futures)
        print(f"Data Futures ({count} workers): {time_futures:.4f}s, Speedup: {speedup_futures:.2f}, Efficiency: {efficiency_futures:.2f}")

    return results_mp, results_futures, all_logs_mp, all_logs_futures

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

def print_detailed_comparison(data_mp, data_futures, task_mp=None, task_futures=None):
    """Print a detailed comparison table."""
    print("\n=== Detailed Performance Comparison ===")
    print("Type\t\tLibrary\t\tWorkers\tTime (s)\tSpeedup\tEfficiency")
    print("-" * 80)

    for count, t, s, e in data_mp:
        print(f"Data\t\tMultiprocessing\t{count}\t{t:.4f}\t{s:.2f}\t{e:.2f}")
    for count, t, s, e in data_futures:
        print(f"Data\t\tFutures\t\t{count}\t{t:.4f}\t{s:.2f}\t{e:.2f}")
    if task_mp and task_futures:
        for count, t, s, e in task_mp:
            print(f"Task\t\tMultiprocessing\t{count}\t{t:.4f}\t{s:.2f}\t{e:.2f}")
        for count, t, s, e in task_futures:
            print(f"Task\t\tFutures\t\t{count}\t{t:.4f}\t{s:.2f}\t{e:.2f}")

def save_results_to_excel(seq_time, data_mp, data_futures, task_mp=None, task_futures=None, logs_mp=None, logs_futures=None, filename="performance_results.xlsx"):
    """Save all results to an Excel file."""
    data = {
        'Workers': [1, 2, 4, 8],
        'Data_MP_Time': [t for _, t, _, _ in data_mp],
        'Data_MP_Speedup': [s for _, _, s, _ in data_mp],
        'Data_MP_Efficiency': [e for _, _, _, e in data_mp],
        'Data_Futures_Time': [t for _, t, _, _ in data_futures],
        'Data_Futures_Speedup': [s for _, _, s, _ in data_futures],
        'Data_Futures_Efficiency': [e for _, _, _, e in data_futures],
    }
    if task_mp and task_futures:
        data.update({
            'Task_MP_Time': [t for _, t, _, _ in task_mp],
            'Task_MP_Speedup': [s for _, _, s, _ in task_mp],
            'Task_MP_Efficiency': [e for _, _, _, e in task_mp],
            'Task_Futures_Time': [t for _, t, _, _ in task_futures],
            'Task_Futures_Speedup': [s for _, _, s, _ in task_futures],
            'Task_Futures_Efficiency': [e for _, _, _, e in task_futures],
        })
    df = pd.DataFrame(data)
    
    # Create Excel writer to save multiple sheets
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Performance', index=False)
        
        # Save logs if provided
        if logs_mp:
            logs_mp_df = pd.DataFrame(logs_mp)
            logs_mp_df.to_excel(writer, sheet_name='Logs_Multiprocessing', index=False)
        
        if logs_futures:
            logs_futures_df = pd.DataFrame(logs_futures)
            logs_futures_df.to_excel(writer, sheet_name='Logs_Threading', index=False)
    
    print(f"\nResults saved to {filename}")

def plot_comparison(seq_time, data_mp, data_futures, task_mp=None, task_futures=None):
    """Generate line graphs comparing the methods."""
    counts = [1, 2, 4, 8]

    # Extract data
    data_mp_times = [t for _, t, _, _ in data_mp]
    data_futures_times = [t for _, t, _, _ in data_futures]
    data_mp_speedups = [s for _, _, s, _ in data_mp]
    data_futures_speedups = [s for _, _, s, _ in data_futures]
    data_mp_efficiency = [e * 100 for _, _, _, e in data_mp]
    data_futures_efficiency = [e * 100 for _, _, _, e in data_futures]

    if task_mp and task_futures:
        task_mp_times = [t for _, t, _, _ in task_mp]
        task_futures_times = [t for _, t, _, _ in task_futures]
        task_mp_speedups = [s for _, _, s, _ in task_mp]
        task_futures_speedups = [s for _, _, s, _ in task_futures]
        task_mp_efficiency = [e * 100 for _, _, _, e in task_mp]
        task_futures_efficiency = [e * 100 for _, _, _, e in task_futures]

    # Create figure with 3 subplots
    plt.figure(figsize=(18, 5))

    # Plot 1: Execution Times
    plt.subplot(1, 3, 1)
    plt.plot(counts, data_mp_times, label='Data MP', marker='o', linewidth=2, markersize=8)
    plt.plot(counts, data_futures_times, label='Data Futures', marker='s', linewidth=2, markersize=8)
    if task_mp and task_futures:
        plt.plot(counts, task_mp_times, label='Task MP', marker='^', linewidth=2, markersize=8)
        plt.plot(counts, task_futures_times, label='Task Futures', marker='d', linewidth=2, markersize=8)
    plt.axhline(y=seq_time, color='r', linestyle='--', linewidth=1.5, alpha=0.7, label='Sequential')
    plt.xlabel('Number of Workers/Processes', fontsize=11)
    plt.ylabel('Execution Time (s)', fontsize=11)
    plt.title('Execution Time Comparison', fontsize=12, fontweight='bold')
    plt.legend(fontsize=9)
    plt.grid(True, alpha=0.3)
    plt.xticks(counts)

    # Plot 2: Speedup
    plt.subplot(1, 3, 2)
    plt.plot(counts, data_mp_speedups, label='Data MP', marker='o', linewidth=2, markersize=8)
    plt.plot(counts, data_futures_speedups, label='Data Futures', marker='s', linewidth=2, markersize=8)
    if task_mp and task_futures:
        plt.plot(counts, task_mp_speedups, label='Task MP', marker='^', linewidth=2, markersize=8)
        plt.plot(counts, task_futures_speedups, label='Task Futures', marker='d', linewidth=2, markersize=8)
    # Set y-axis limits based on actual data range for better visibility
    all_speedups = data_mp_speedups + data_futures_speedups
    if task_mp and task_futures:
        all_speedups += task_mp_speedups + task_futures_speedups
    min_speedup = min(all_speedups)
    max_speedup = max(all_speedups)
    y_margin = (max_speedup - min_speedup) * 0.2  # 20% margin
    plt.ylim(min_speedup - y_margin, max_speedup + y_margin)
    plt.xlabel('Number of Workers/Processes', fontsize=11)
    plt.ylabel('Speedup', fontsize=11)
    plt.title('Speedup Comparison (Tserial / Tparallel)', fontsize=12, fontweight='bold')
    plt.legend(fontsize=9)
    plt.grid(True, alpha=0.3)
    plt.xticks(counts)

    # Plot 3: Efficiency
    plt.subplot(1, 3, 3)
    plt.plot(counts, data_mp_efficiency, label='Data MP', marker='o', linewidth=2, markersize=8)
    plt.plot(counts, data_futures_efficiency, label='Data Futures', marker='s', linewidth=2, markersize=8)
    if task_mp and task_futures:
        plt.plot(counts, task_mp_efficiency, label='Task MP', marker='^', linewidth=2, markersize=8)
        plt.plot(counts, task_futures_efficiency, label='Task Futures', marker='d', linewidth=2, markersize=8)
    plt.axhline(y=100, color='k', linestyle='--', linewidth=1.5, alpha=0.5, label='Ideal (100%)')
    plt.xlabel('Number of Workers/Processes', fontsize=11)
    plt.ylabel('Efficiency (%)', fontsize=11)
    plt.title('Efficiency (Speedup / Cores × 100%)', fontsize=12, fontweight='bold')
    plt.legend(fontsize=9)
    plt.grid(True, alpha=0.3)
    plt.xticks(counts)
    plt.ylim(0, 110)

    plt.suptitle('Parallel Image Processing Performance Analysis', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('performance_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("Graph saved as performance_comparison.png")
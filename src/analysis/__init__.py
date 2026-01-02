from .parallelism_analysis import (
    data_parallelism_multiprocessing,
    data_parallelism_threading,
    task_parallelism_multiprocessing,
    task_parallelism_futures
)
import os
import pandas as pd
import matplotlib.pyplot as plt

OUTPUT_BASE = os.path.join(os.path.dirname(__file__), "../../output")

def analyze_data_parallelism(images):
    """Analyze performance for data parallelism using both multiprocessing and futures."""
    print("\n=== Data Parallelism Analysis ===")
    counts = [1, 2, 4, 8]
    results_mp = []
    results_futures = []
    all_logs_mp = []
    all_logs_futures = []
    
    # First, collect all timing data
    times_mp = []
    times_futures = []
    logs_mp_by_count = {}
    logs_futures_by_count = {}

    for count in counts:
        # Multiprocessing
        output_dir_mp = os.path.join(OUTPUT_BASE, f"data_mp_{count}")
        time_mp, logs_mp = data_parallelism_multiprocessing(images, output_dir_mp, count)
        times_mp.append(time_mp)
        logs_mp_by_count[count] = logs_mp
        print(f"Data MP ({count} processes): {time_mp:.4f}s")

    for count in counts:
        # Multithreading
        output_dir_futures = os.path.join(OUTPUT_BASE, f"data_mt_{count}")
        time_futures, logs_futures = data_parallelism_threading(images, output_dir_futures, count)
        times_futures.append(time_futures)
        logs_futures_by_count[count] = logs_futures
        print(f"Data MT ({count} threads): {time_futures:.4f}s")
    
    # Use 1-core time as baseline for speedup calculation
    baseline_mp = times_mp[0]  # 1 core time
    baseline_futures = times_futures[0]  # 1 core time
    
    print("\n=== Speedup Calculation (using 1-core as baseline) ===")
    for i, count in enumerate(counts):
        speedup_mp = baseline_mp / times_mp[i]
        efficiency_mp = speedup_mp / count
        results_mp.append((count, times_mp[i], speedup_mp, efficiency_mp))
        all_logs_mp.extend(logs_mp_by_count[count])
        print(f"Data MP ({count} processes): Speedup: {speedup_mp:.2f}, Efficiency: {efficiency_mp:.2f}")
        
        speedup_futures = baseline_futures / times_futures[i]
        efficiency_futures = speedup_futures / count
        results_futures.append((count, times_futures[i], speedup_futures, efficiency_futures))
        all_logs_futures.extend(logs_futures_by_count[count])
        print(f"Data MT ({count} threads): Speedup: {speedup_futures:.2f}, Efficiency: {efficiency_futures:.2f}")

    return results_mp, results_futures, all_logs_mp, all_logs_futures
    # return results_mp, all_logs_mp

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
# def print_detailed_comparison(data_mp, task_mp=None, task_futures=None):
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

def save_results_to_excel(data_mp, data_futures, task_mp=None, task_futures=None, logs_mp=None, logs_futures=None, filename="performance_results.xlsx"):
# def save_results_to_excel(seq_time, data_mp, task_mp=None, task_futures=None, logs_mp=None, filename="performance_results.xlsx"):
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
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Performance_Summary', index=False)
        
        if logs_mp:
            logs_df = pd.DataFrame(logs_mp)
            # Flatten counts dict if needed
            if 'counts' in logs_df.columns:
                counts_df = logs_df['counts'].apply(pd.Series)
                logs_df = pd.concat([logs_df.drop('counts', axis=1), counts_df], axis=1)
            logs_df.to_excel(writer, sheet_name='Multiprocessing_Logs', index=False)
        
        if logs_futures:
            logs_df = pd.DataFrame(logs_futures)
            # Flatten counts dict if needed
            if 'counts' in logs_df.columns:
                counts_df = logs_df['counts'].apply(pd.Series)
                logs_df = pd.concat([logs_df.drop('counts', axis=1), counts_df], axis=1)
            logs_df.to_excel(writer, sheet_name='Threading_Logs', index=False)
    
    print(f"\nResults saved to {filename}")

def plot_comparison(data_mp, data_futures, task_mp=None, task_futures=None):
# def plot_comparison(seq_time, data_mp, task_mp=None, task_futures=None):
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

def plot_core_timeline(logs, num_workers, method_name="Multiprocessing"):
    """Visualize which cores process which workers over time (Gantt chart style)."""
    if not logs:
        print("No logs available for timeline visualization")
        return
    
    # Filter out N/A core IDs and prepare data
    valid_logs = [log for log in logs if log.get('core_id') not in ['N/A', 'N/A (psutil not installed)', None]]
    
    if not valid_logs:
        print(f"No valid core ID data available for {method_name} timeline visualization")
        return
    
    # Normalize start times to start from 0
    min_start = min(log['start_time'] for log in valid_logs)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, max(6, num_workers * 0.8)))
    
    # Get unique cores and assign colors
    unique_cores = sorted(set(log['core_id'] for log in valid_logs))
    colors = plt.cm.tab10(range(len(unique_cores)))
    core_color_map = {core: colors[i % 10] for i, core in enumerate(unique_cores)}
    
    # Plot each chunk as a horizontal bar
    for log in valid_logs:
        chunk_id = log['chunk_id']
        core_id = log['core_id']
        start = log['start_time'] - min_start
        duration = log['duration']
        
        ax.barh(chunk_id, duration, left=start, height=0.8, 
                color=core_color_map[core_id], 
                edgecolor='black', linewidth=0.5,
                label=f'Core {core_id}' if core_id not in [l.get_label() for l in ax.get_children()] else "")
    
    # Formatting
    ax.set_xlabel('Time (seconds)', fontsize=12)
    ax.set_ylabel('Worker/Chunk ID', fontsize=12)
    ax.set_title(f'{method_name}: Worker Execution Timeline by CPU Core\n(Colors = Different CPU Cores)', 
                 fontsize=13, fontweight='bold')
    ax.set_yticks(range(num_workers))
    ax.set_yticklabels([f'Worker {i}' for i in range(num_workers)])
    ax.grid(True, axis='x', alpha=0.3)
    
    # Create legend with unique cores only
    handles = [plt.Rectangle((0,0),1,1, color=core_color_map[core]) for core in unique_cores]
    labels = [f'Core {core}' for core in unique_cores]
    ax.legend(handles, labels, loc='upper right', fontsize=9, title='CPU Cores')
    
    plt.tight_layout()
    filename = f'timeline_{method_name.lower().replace(" ", "_")}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.show()
    print(f"Timeline visualization saved as {filename}")

def plot_thread_core_usage(logs, num_workers, method_name="Multiprocessing"):
    """Visualize which cores each worker/thread used."""
    if not logs:
        print("No logs available for thread-core visualization")
        return
    
    # Filter out N/A core IDs
    valid_logs = [log for log in logs if log.get('core_id') not in ['N/A', 'N/A (psutil not installed)', None]]
    
    if not valid_logs:
        print(f"No valid core ID data available for {method_name} thread-core visualization")
        return
    
    # Create a dictionary: worker_id -> list of cores used
    worker_cores = {}
    for log in valid_logs:
        worker_id = log['chunk_id']
        core_id = log['core_id']
        if worker_id not in worker_cores:
            worker_cores[worker_id] = []
        if core_id not in worker_cores[worker_id]:
            worker_cores[worker_id].append(core_id)
    
    # Sort workers and get all unique cores
    workers = sorted(worker_cores.keys())
    all_cores = sorted(set(core for cores in worker_cores.values() for core in cores))
    
    # Create matrix: rows=workers, cols=cores, value=1 if worker used that core
    matrix = []
    for worker in workers:
        row = [1 if core in worker_cores[worker] else 0 for core in all_cores]
        matrix.append(row)
    
    # Create horizontal bar chart
    fig, ax = plt.subplots(figsize=(10, max(6, num_workers * 0.6)))
    
    # For each worker, create stacked bars showing which cores it used
    colors = plt.cm.Set3(range(len(all_cores)))
    core_color_map = {core: colors[i % 12] for i, core in enumerate(all_cores)}
    
    for i, worker in enumerate(workers):
        cores_used = worker_cores[worker]
        left = 0
        for core in cores_used:
            ax.barh(i, 1, left=left, height=0.8, 
                   color=core_color_map[core],
                   edgecolor='black', linewidth=0.5,
                   label=f'Core {core}' if i == 0 else '')
            # Add core label on the bar
            ax.text(left + 0.5, i, str(core), 
                   ha='center', va='center', fontsize=10, fontweight='bold')
            left += 1
    
    # Formatting
    ax.set_xlabel('Number of Different Cores Used', fontsize=12)
    ax.set_ylabel('Worker/Thread ID', fontsize=12)
    ax.set_title(f'{method_name}: Which CPU Cores Each Worker Used\n(Numbers show Core IDs)', 
                 fontsize=13, fontweight='bold')
    ax.set_yticks(range(len(workers)))
    ax.set_yticklabels([f'Worker {w}' for w in workers])
    ax.set_xlim(0, max(len(worker_cores[w]) for w in workers) + 0.5)
    ax.grid(True, axis='x', alpha=0.3)
    
    # Add text summary on the right
    for i, worker in enumerate(workers):
        num_cores = len(worker_cores[worker])
        ax.text(num_cores + 0.1, i, f'{num_cores} core(s)', 
               va='center', fontsize=9, style='italic')
    
    plt.tight_layout()
    filename = f'worker_core_usage_{method_name.lower().replace(" ", "_")}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.show()
    print(f"Worker-core usage visualization saved as {filename}")
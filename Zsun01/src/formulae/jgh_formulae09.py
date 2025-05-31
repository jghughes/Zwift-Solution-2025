from typing import  List, Tuple, Any, DefaultDict, Optional, Generator 
from collections import defaultdict
import concurrent.futures
import os
import time
import numpy as np
import itertools
from zsun_rider_item import ZsunRiderItem
from zsun_rider_pullplan_item import RiderPullPlanItem
from jgh_formulae08 import make_a_pull_plan, calculate_intensity_factor

import logging
from jgh_logging import jgh_configure_logging
jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)
logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO
logging.getLogger("numba").setLevel(logging.ERROR)
def process_chunk(
    chunk: List[Tuple[List[ZsunRiderItem], List[float], List[float],float]]
) -> List[Tuple[int, DefaultDict[ZsunRiderItem, RiderPullPlanItem], Any]]:
    """
    Processes a chunk of arguments for make_a_pull_plan in parallel execution.

    Args:
        chunk: List of argument tuples for make_a_pull_plan.

    Returns:
        List of results from make_a_pull_plan for each set of arguments.
    """
    chunk_results = []
    for args in chunk:
        try:
            result = make_a_pull_plan(args)
            if (result is None or
                not isinstance(result, tuple) or
                len(result) != 3 or
                result[1] is None or
                result[2] is None or
                not isinstance(result[1], dict)):
                logger.warning("Skipping invalid result: %s", result)
                continue
            chunk_results.append(result)
        except Exception as exc:
            logger.error("Exception in make_a_pull_plan: %s", exc)
    return chunk_results

# --- Main function to search for optimal pull plans using parallel programming chunking algorithm ---
def search_for_optimal_pull_plans_with_parallel_chunking(
    riders: List[ZsunRiderItem],
    standard_pull_periods_seconds: List[float],
    lower_bound_speed: float,
    max_exertion_intensity_factor: float = 1.0,
    chunk_size: Optional[int] = 100,
    max_workers: Optional[int] = os.cpu_count(),
    verbose: bool = True
) -> Tuple[List[Tuple[int, defaultdict[ZsunRiderItem, RiderPullPlanItem], ZsunRiderItem]],
           int,
           int,
           float]:
    """
    Alternative version with chunking and flexible worker count for benchmarking and profiling.

    Args:
        riders: List of ZsunRiderItem.
        standard_pull_periods_seconds: List of permitted pull durations.
        lower_bound_speed: Minimum speed to consider.
        chunk_size: Number of tasks per chunk. If an integer is provided, that value is used.
            If None is passed, the function will automatically determine a suitable chunk size
            based on the total number of plans and the number of workers. Default is 100.
        max_workers: Number of worker processes. If an integer is provided, that value is used.
            If None is passed, the function will use the number of CPUs available on the system.
            Default is os.cpu_count().
        verbose: Print profiling info.

    Returns:
        (solutions, total_num_of_all_pull_plan_period_schedules, total_compute_iterations, elapsed_time)

    Note:
        The use of Optional[int] for chunk_size and max_workers allows the caller to explicitly pass
        None to trigger automatic, context-sensitive defaulting logic inside the function, rather than
        always using a fixed default. This provides more flexibility for advanced use cases.
    """
    import math

    if not riders:
        raise ValueError("No riders provided to search_for_optimal_pull_plans_with_parallel_chunking.")
    if not standard_pull_periods_seconds:
        raise ValueError("No standard pull durations provided to search_for_optimal_pull_plans_with_parallel_chunking.")
    if any(d <= 0 or not np.isfinite(d) for d in standard_pull_periods_seconds):
        raise ValueError("All standard pull durations must be positive and finite.")
    if not np.isfinite(lower_bound_speed) or lower_bound_speed <= 0:
        raise ValueError("lower_bound_speed must be positive and finite.")

    start_time = time.perf_counter()

    all_conceivable_paceline_rotation_schedules = list(itertools.product(standard_pull_periods_seconds, repeat=len(riders)))
    total_num_of_all_pull_plan_period_schedules = len(all_conceivable_paceline_rotation_schedules)
    lower_bound_paceline_speed_as_array: list[float] = [lower_bound_speed] * len(riders)
    total_compute_iterations: int = 0

    if total_num_of_all_pull_plan_period_schedules > 1_000_000:
        logger.warning("Number of alternatives is very large: %d", total_num_of_all_pull_plan_period_schedules)

    # --- Chunking setup ---
    if max_workers is None:
        max_workers = os.cpu_count() or 1
    if chunk_size is None:
        # Default: divide evenly among workers, but at least 1 per chunk
        chunk_size = max(1, math.ceil(total_num_of_all_pull_plan_period_schedules / max_workers))

    # Helper to yield chunks
    def chunked_args(args_list: List[Tuple[List[ZsunRiderItem], List[float], List[float], float]], size: int
    ) -> 'Generator[List[Tuple[List[ZsunRiderItem], List[float], List[float]]], None, None]':
        for i in range(0, len(args_list), size):
            yield args_list[i:i + size]
    
    args_list = [
        (riders, standard_pull_periods_seconds, lower_bound_paceline_speed_as_array, max_exertion_intensity_factor)
        for standard_pull_periods_seconds in all_conceivable_paceline_rotation_schedules
    ]    

    chunked_args_list = list(chunked_args(args_list, chunk_size))

    if verbose:
        logger.info(f"search_for_optimal_pull_plans_with_parallel_chunking: {total_num_of_all_pull_plan_period_schedules} alternatives, "
              f"{len(chunked_args_list)} chunks, chunk_size={chunk_size}, max_workers={max_workers}")

    # --- Parallel execution ---
    solutions: List[Tuple[int, defaultdict[ZsunRiderItem, RiderPullPlanItem], ZsunRiderItem]] = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_chunk = {executor.submit(process_chunk, chunk): idx for idx, chunk in enumerate(chunked_args_list)}
        for future in concurrent.futures.as_completed(future_to_chunk):
            chunk_idx = future_to_chunk[future]
            try:
                chunk_results = future.result()
                solutions.extend(chunk_results)
                if verbose:
                    logger.info(f"Chunk {chunk_idx+1}/{len(chunked_args_list)} completed, {len(chunk_results)} results")
            except Exception as exc:
                logger.error("Exception in function process_chunk() containing function make_a_pull_plan() : %s", exc)

    end_time = time.perf_counter()
    concurrent_computational_time = end_time - start_time

    # --- Profiling and benchmarking output ---

    if verbose:
        logger.info(f"search_for_optimal_pull_plans_with_parallel_chunking completed in {concurrent_computational_time:.2f} seconds")
        logger.info(f"Total solutions: {len(solutions)}")

    # --- Post-processing (same as original) ---
    highest_speed_pull_plan_solution = None
    highest_speed: float = float('-inf')
    lowest_dispersion_pull_plan_soluton = None
    lowest_dispersion: float = float('inf')

    for compute_iterations, rider_pullplan_items, exertion_maxed_out_rider in solutions:
        total_compute_iterations += compute_iterations
        if exertion_maxed_out_rider is None or rider_pullplan_items is None or not isinstance(rider_pullplan_items, dict):
            logger.warning("Invalid result in solutions list: %s", (compute_iterations, rider_pullplan_items, exertion_maxed_out_rider))
            continue
        pull_plan_speed_limit = rider_pullplan_items[exertion_maxed_out_rider].speed_kph
        if not np.isfinite(pull_plan_speed_limit):
            logger.warning("Non-finite pull_plan_speed_limit encountered: %s", pull_plan_speed_limit)
            continue

        # Memo for fastest halted speed
        if pull_plan_speed_limit > highest_speed:
            highest_speed = pull_plan_speed_limit
            highest_speed_pull_plan_solution = (compute_iterations, rider_pullplan_items, exertion_maxed_out_rider)

        # Memo for lowest dispersion of np_intensity_factor
        np_intensity_factors = [calculate_intensity_factor(rider, plan) for rider, plan in rider_pullplan_items.items()]

        # np_intensity_factors = [answer.np_intensity_factor for answer in rider_pullplan_items.values() if hasattr(answer, "np_intensity_factor")]
        if not np_intensity_factors:
            logger.warning("No valid np_intensity_factors in rider_pullplan_items.")
            continue
        dispersion = np.std(np_intensity_factors)
        if not np.isfinite(dispersion):
            logger.warning("Non-finite dispersion encountered: %s", dispersion)
            continue
        if dispersion < lowest_dispersion:
            lowest_dispersion = dispersion
            lowest_dispersion_pull_plan_soluton = (compute_iterations, rider_pullplan_items, exertion_maxed_out_rider)

    if highest_speed_pull_plan_solution is None and lowest_dispersion_pull_plan_soluton is None:
        raise RuntimeError("search_for_optimal_pull_plans_with_parallel_chunking: No valid solution found (both highest_speed_pull_plan_solution and lowest_dispersion_pull_plan_soluton are None)")
    elif highest_speed_pull_plan_solution is None:
        raise RuntimeError("search_for_optimal_pull_plans_with_parallel_chunking: No valid solution found (highest_speed_pull_plan_solution is None)")
    elif lowest_dispersion_pull_plan_soluton is None:
        raise RuntimeError("search_for_optimal_pull_plans_with_parallel_chunking: No valid solution found (lowest_dispersion_pull_plan_soluton is None)")

    return ([highest_speed_pull_plan_solution, lowest_dispersion_pull_plan_soluton], total_num_of_all_pull_plan_period_schedules, total_compute_iterations, concurrent_computational_time)


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def main01():
    from handy_utilities import read_dict_of_zsunriderItems
    from repository_of_teams import get_team_riderIDs
    from constants import STANDARD_PULL_PERIODS_SEC
    from jgh_formulae09 import search_for_optimal_pull_plans_with_parallel_chunking
    from jgh_formulae08 import search_for_optimal_pull_plans_with_parallel_workstealing
    import time
    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt

    RIDERS_FILE_NAME = "everyone_in_club_ZsunRiderItems.json"
    DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

    save_filename_without_ext = "benchmark_results_5_riders"

    dict_of_zsunrideritems = read_dict_of_zsunriderItems(RIDERS_FILE_NAME, DATA_DIRPATH)
    riderIDs = get_team_riderIDs("betel")
    riders = [dict_of_zsunrideritems[rid] for rid in riderIDs]

    logger.info(f"Starting: benchmarking parallel processing with work-stealing (base case) versus chunking with {len(riderIDs)} riders")

    # Define parameter grid
    max_workers_list = [1, 4, 8, os.cpu_count()]
    chunk_size_list = [100, 1000, 10000]

    # Base-case run for correctness
    ref_start = time.perf_counter()
    ref_result, _, _, ref_elapsed = search_for_optimal_pull_plans_with_parallel_workstealing(riders, STANDARD_PULL_PERIODS_SEC, 30.0, 0.95)
    ref_end = time.perf_counter()
    ref_fastest_speed = ref_result[0][1][ref_result[0][2]].speed_kph
    ref_elapsed_measured = ref_end - ref_start
    logger.info(f"Base-case run compute time (reported): {ref_elapsed:.2f} seconds")
    logger.info(f"Base-case run compute time (measured): {ref_elapsed_measured:.2f} seconds")
    logger.info(f"Base-case highest_speed paceline pull plan: {ref_fastest_speed} kph\n")

    results = []
    for max_workers in max_workers_list:
        for chunk_size in chunk_size_list:
            logger.info(f"Running: max_workers={max_workers}, chunk_size={chunk_size}")
            try:
                res, total_alts, total_iters, elapsed = search_for_optimal_pull_plans_with_parallel_chunking(
                    riders, STANDARD_PULL_PERIODS_SEC, 30.0, max_exertion_intensity_factor=1.0,
                    chunk_size=chunk_size, max_workers=max_workers, verbose=False
                )
                fastest = res[0]
                highest_speed = fastest[1][fastest[2]].speed_kph
                correct = abs(highest_speed - ref_fastest_speed) < 1e-6
                results.append({
                    "max_workers": max_workers,
                    "chunk_size": chunk_size,
                    "elapsed_time": elapsed,
                    "total_num_of_all_pull_plan_period_schedules": total_alts,
                    "total_compute_iterations": total_iters,
                    "highest_speed": highest_speed,
                    "correct": correct
                })
            except Exception as e:
                results.append({
                    "max_workers": max_workers,
                    "chunk_size": chunk_size,
                    "elapsed_time": None,
                    "total_num_of_all_pull_plan_period_schedules": None,
                    "total_compute_iterations": None,
                    "highest_speed": None,
                    "correct": False,
                    "error": str(e)
                })

    # Convert to DataFrame and save to CSV
    df = pd.DataFrame(results)
    df.to_csv(f"{save_filename_without_ext}.csv", index=False)
    logger.info(df)

    # Print and save a summary report to a .txt file
    report_lines = []
    report_lines.append("Benchmark Results Summary\n")
    report_lines.append(f"Base-case run compute time (reported): {ref_elapsed:.2f} seconds\n")
    report_lines.append(f"Base-case run compute time (measured): {ref_elapsed_measured:.2f} seconds\n")
    report_lines.append(f"Base-case highest speed paceline pull plan: {ref_fastest_speed:.3f} kph\n")
    report_lines.append(f"Base-case run parameters: max_workers=1, chunk_size=1\n")
    report_lines.append(f"Number of parameter combinations tested: {len(results)}\n")
    report_lines.append("\n")
    report_lines.append(f"{'max_workers':>11} | {'chunk_size':>10} | {'compute_time':>12} | {'highest_speed_kph':>13} | {'correct':>7}\n")
    report_lines.append("-" * 65 + "\n")
    for row in results:
        report_lines.append(
            f"{str(row['max_workers']):>11} | "
            f"{str(row['chunk_size']):>10} | "
            f"{str(row['elapsed_time']) if row['elapsed_time'] is not None else 'ERR':>12} | "
            f"{str(row['highest_speed']) if row['highest_speed'] is not None else 'ERR':>13} | "
            f"{str(row['correct']):>7}\n"
        )
    report_lines.append("\n")
    report_lines.append("Note: 'ERR' indicates an error or failed run for that parameter combination.\n")

    # --- Analysis and Conclusion ---
    # Only consider successful and correct runs
    df_valid = df[(df["correct"] == True) & (df["elapsed_time"].notnull())]
    if not df_valid.empty:
        # Find the row(s) with the minimum elapsed_time
        min_time = df_valid["elapsed_time"].min()
        best_rows = df_valid[df_valid["elapsed_time"] == min_time]
        # If multiple, pick the one with the smallest max_workers, then smallest chunk_size
        best_row = best_rows.sort_values(["max_workers", "chunk_size"]).iloc[0]
        conclusion = (
            "\n"
            "==================== Benchmarking Conclusion ====================\n"
            f"Optimal configuration:\n"
            f"  max_workers = {best_row['max_workers']}\n"
            f"  chunk_size  = {best_row['chunk_size']}\n"
            f"  compute_time = {best_row['elapsed_time']:.2f} seconds\n"
            "\n"
            "How this was decided:\n"
            "  - Only runs with correct results and successful completion were considered.\n"
            "  - The configuration with the lowest compute_time was selected.\n"
            "  - If multiple runs had the same time, the one with fewer workers and smaller chunk size was preferred.\n"
            "  - This approach balances speed, correctness, and resource usage.\n"
            "===============================================================\n"
        )
    else:
        conclusion = (
            "\n"
            "==================== Benchmarking Conclusion ====================\n"
            "No valid (correct and successful) configuration was found.\n"
            "===============================================================\n"
        )

    logger.info(conclusion)
    report_lines.append(conclusion)

    # Write the report to a .txt file
    with open(f"{save_filename_without_ext}.txt", "w", encoding="utf-8") as f:
        f.writelines(report_lines)
    logger.info(f"Summary report written to {save_filename_without_ext}.txt")

    # Visualization
    plt.figure(figsize=(12, 6))
    sns.scatterplot(
        data=df,
        x="max_workers",
        y="elapsed_time",
        hue="chunk_size",
        style="correct",
        palette="tab10",         # Use a categorical palette for distinct colors
        s=150,                   # Larger marker size
        edgecolor="black",       # Black edge for contrast
        alpha=0.85               # Slight transparency
    )
    plt.title("Compute Time vs. max_cpu_workers and chunk_size")
    plt.xlabel("max_cpu_worker_processes")
    plt.ylabel("Compute Time (s)")
    plt.legend(title="chunk_size", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(f"{save_filename_without_ext}_max_workers_vs_time.png")
    plt.show()

    plt.figure(figsize=(12, 6))
    sns.scatterplot(
        data=df,
        x="chunk_size",
        y="elapsed_time",
        hue="max_workers",
        style="correct",
        palette="Set1",          # Another categorical palette
        s=150,
        edgecolor="black",
        alpha=0.85
    )
    plt.title("Compute Time vs. chunk_size and max_cpu_workers")
    plt.xlabel("chunk_size")
    plt.ylabel("Compute Time (s)")
    plt.legend(title="max_cpu_worker_processes", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(f"{save_filename_without_ext}_chunk_size_vs_time.png")
    plt.show()

        # --- Heatmap Visualization ---
    # Pivot the DataFrame for heatmap: rows=chunk_size, columns=max_workers, values=elapsed_time
    heatmap_data = df.pivot_table(
        index="chunk_size",
        columns="max_workers",
        values="elapsed_time",
        aggfunc="min"
    )

    plt.figure(figsize=(10, 7))
    sns.heatmap(
        heatmap_data,
        annot=True,
        fmt=".2f",
        cmap="YlGnBu",
        linewidths=0.5,
        cbar_kws={'label': 'Elapsed Time (s)'}
    )
    plt.title("Compute Time Heatmap (s) by max_workers and chunk_size")
    plt.xlabel("max_workers")
    plt.ylabel("chunk_size")
    plt.tight_layout()
    plt.savefig(f"{save_filename_without_ext}_heatmap.png")
    plt.show()

if __name__ == "__main__":
    main01()

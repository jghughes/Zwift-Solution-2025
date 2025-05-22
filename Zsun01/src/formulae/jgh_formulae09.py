from typing import  List, Tuple, Union, Any, DefaultDict, Optional, Generator 
from collections import defaultdict
import concurrent.futures
import os
import time
import numpy as np
import itertools
from zsun_rider_item import ZsunRiderItem
from zsun_rider_pullplan_item import RiderPullPlanItem
from jgh_formulae08 import make_a_pull_plan

import logging
from jgh_logging import jgh_configure_logging
jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)


def process_chunk(
    chunk: List[Tuple[List[ZsunRiderItem], List[float], List[float]]]
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

def search_for_optimal_pull_plansV2(riders: List[ZsunRiderItem], pull_duration_options: List[float], lower_bound_speed: float,
    chunk_size: Optional[int] = None,
    max_workers: Optional[int] = None,
    verbose: bool = True
) -> Tuple[List[Tuple[int, defaultdict[ZsunRiderItem, RiderPullPlanItem], ZsunRiderItem]],
           int,  # total_alternatives investigated
           int,  # total_iterations done
           float  # elapsed computer time in seconds
           ]:
    """
    Alternative version with chunking and flexible worker count for benchmarking and profiling.
    Args:
        riders: List of ZsunRiderItem
        pull_duration_options: List of permitted pull durations
        lower_bound_speed: Minimum speed to consider
        chunk_size: Number of tasks per chunk (default: auto)
        max_workers: Number of worker processes (default: os.cpu_count())
        verbose: Print profiling info
    Returns:
        (solutions, total_alternatives, total_iterations, elapsed_time)
    """
    import math

    if not riders:
        raise ValueError("No riders provided to search_for_optimal_pull_plansV2.")
    if not pull_duration_options:
        raise ValueError("No permitted pull durations provided to search_for_optimal_pull_plansV2.")
    if any(d <= 0 or not np.isfinite(d) for d in pull_duration_options):
        raise ValueError("All permitted pull durations must be positive and finite.")
    if not np.isfinite(lower_bound_speed) or lower_bound_speed <= 0:
        raise ValueError("lower_bound_speed must be positive and finite.")

    start_time = time.time()

    all_combinations = list(itertools.product(pull_duration_options, repeat=len(riders)))
    total_alternatives = len(all_combinations)
    seed_speed_array: list[float] = [lower_bound_speed] * len(riders)
    total_iterations: int = 0

    if total_alternatives > 1_000_000:
        logger.warning("Number of alternatives is very large: %d", total_alternatives)

    # --- Chunking setup ---
    if max_workers is None:
        max_workers = os.cpu_count() or 1
    if chunk_size is None:
        # Default: divide evenly among workers, but at least 1 per chunk
        chunk_size = max(1, math.ceil(total_alternatives / max_workers))

    # Helper to yield chunks
    def chunked_args(args_list: List[Tuple[List[ZsunRiderItem], List[float], List[float]]], size: int
    ) -> 'Generator[List[Tuple[List[ZsunRiderItem], List[float], List[float]]], None, None]':
        for i in range(0, len(args_list), size):
            yield args_list[i:i + size]
    
    args_list = [(riders, pull_durations, seed_speed_array) for pull_durations in all_combinations]
    chunked_args_list = list(chunked_args(args_list, chunk_size))

    if verbose:
        print(f"search_for_optimal_pull_plansV2: {total_alternatives} alternatives, "
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
                    print(f"Chunk {chunk_idx+1}/{len(chunked_args_list)} completed, {len(chunk_results)} results")
            except Exception as exc:
                logger.error("Exception in process_chunk: %s", exc)

    # --- Profiling and benchmarking output ---
    end_time = time.time()
    elapsed_time = end_time - start_time

    if verbose:
        print(f"search_for_optimal_pull_plansV2 completed in {elapsed_time:.2f} seconds")
        print(f"Total solutions: {len(solutions)}")

    # --- Post-processing (same as original) ---
    fastest_speed_tuple = None
    fastest_speed: float = float('-inf')
    lowest_dispersion_tuple = None
    lowest_dispersion: float = float('inf')

    for iterations, rider_pullplan_items, halted_rider in solutions:
        total_iterations += iterations
        if halted_rider is None or rider_pullplan_items is None or not isinstance(rider_pullplan_items, dict):
            logger.warning("Invalid result in solutions list: %s", (iterations, rider_pullplan_items, halted_rider))
            continue
        halted_speed = rider_pullplan_items[halted_rider].speed_kph
        if not np.isfinite(halted_speed):
            logger.warning("Non-finite halted_speed encountered: %s", halted_speed)
            continue

        # Memo for fastest halted speed
        if halted_speed > fastest_speed:
            fastest_speed = halted_speed
            fastest_speed_tuple = (iterations, rider_pullplan_items, halted_rider)

        # Memo for lowest dispersion of np_intensity_factor
        np_intensity_factors = [answer.np_intensity_factor for answer in rider_pullplan_items.values() if hasattr(answer, "np_intensity_factor")]
        if not np_intensity_factors:
            logger.warning("No valid np_intensity_factors in rider_pullplan_items.")
            continue
        dispersion = np.std(np_intensity_factors)
        if not np.isfinite(dispersion):
            logger.warning("Non-finite dispersion encountered: %s", dispersion)
            continue
        if dispersion < lowest_dispersion:
            lowest_dispersion = dispersion
            lowest_dispersion_tuple = (iterations, rider_pullplan_items, halted_rider)

    if fastest_speed_tuple is None and lowest_dispersion_tuple is None:
        raise RuntimeError("search_for_optimal_pull_plansV2: No valid solution found (both fastest_speed_tuple and lowest_dispersion_tuple are None)")
    elif fastest_speed_tuple is None:
        raise RuntimeError("search_for_optimal_pull_plansV2: No valid solution found (fastest_speed_tuple is None)")
    elif lowest_dispersion_tuple is None:
        raise RuntimeError("search_for_optimal_pull_plansV2: No valid solution found (lowest_dispersion_tuple is None)")

    return ([fastest_speed_tuple, lowest_dispersion_tuple], total_alternatives, total_iterations, elapsed_time)

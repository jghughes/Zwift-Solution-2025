from pathlib import Path
from typing import List
import os
import time

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from constants import ROTATION_SEQUENCE_UNIVERSE_SIZE_PRUNING_GOAL, STANDARD_PULL_PERIODS_SEC_AS_LIST
from jgh_formatting import format_number_with_comma_separators
from jgh_formulae02 import generate_all_paceline_rotation_sequences_in_the_total_solution_space, prune_all_sequences_of_pull_periods_in_the_total_solution_space
from jgh_formulae08 import generate_paceline_solutions_using_parallel_workstealing_algorithm, generate_paceline_solutions_using_serial_processing_algorithm
from jgh_read_write import write_lines
from storage_config import DIRPATH_RUBBISH_SCRATCHPAD, DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT, FILENAME_RIDER_BRUTE_DTO_JSON_DICT
from rider_brute_item import RiderBruteItem
from repository_of_team_rosters import RepositoryOfTeamRosters
from working_file_read_write import read_file_as_json_dict_of_RiderDTO
from working_types import PacelineIngredientsItem
from zwift_id_base import lookup_Items_by_ZwiftID

import time
import logging
from jgh_exceptions import AlertMessageError
from jgh_logging import setup_json_logging, log_event
from storage_config import DIRPATH_LOGGING




def test01():
    """
        Benchmarks and compares the compute time of serial-processing versus parallel
        processing for paceline-sequences according to the size of universe of
        paceline-sequences. The size is governed by the cross-product of the number
        of riders and the number of standard pull periods (currently 0, 30, 60, 120,
        180, 240, 300). Processing time is exponentially explosive as the number of
        sequences grows.

        The idea with this test01() is to manually increase the number of riders
        (i.e. the number of sequences) and to determine when parallel-processing
        overtakes serial-processing in terms of compute speed. I use test01() to
        empirically determine the sweet spot for the constant
        SERIAL_TO_PARALLEL_PROCESSING_THRESHOLD. This constant is subsequently
        relied upon by Brute in all scenarios. It is therefore important to get the
        constant right. The parameter is tuned for my powerful laptop. It will be
        different for a puny server with fewer cores. At the time of writing (Aug
        2025), the numbers look like this:-

        Riders  Sequences           serial-processing               parallel-processing
            1           7                  <1s                          5s 
            2          49                  <1s                          7s
            3         343                   5s                         10s
            equality  512                   9s                          9s
                      625                  11s                          9s
                      729                  15s                          9s
                    1,296                  29s                         11s
            4       2,401                  60s                         14s
            5      16,807                  11m                         80s - too tedious to run
            6     117,649                4h06m                         13m - waay too tedious to run
            7     823,543               don't even bother
            8   5,764,801               don't even bother


    This function:
      - Loads rider data and team composition from JSON and utility functions.
      - Generates all possible paceline rotation sequences for the team and standard pull periods.
      - Runs the paceline solution algorithm using both serial and parallel approaches, timing each.
      - Logs and writes a summary report comparing the compute times and time saved by parallelization.
      - Visualizes the results in a bar chart and saves the chart as a PNG file.

    The function is intended for performance analysis and does not return a value. All results are 
    logged and saved as a .png.

    Side Effects:
      - Writes a summary report to a text file.
      - Saves a bar chart visualization as a PNG file.
      - Logs progress and results using the configured logger.

    Raises:
      - Exceptions are logged if encountered during computation.

    Dependencies:
      - Expects global variables FILENAME_RIDER_BRUTE_DTO_JSON_DICT and DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT to be set.
      - Requires pandas, seaborn, matplotlib, and other project-specific modules.
    """

    paceline_ingredients = PacelineIngredientsItem(
        riders_list                   = riders,
        sequence_of_pull_periods_sec  = STANDARD_PULL_PERIODS_SEC_AS_LIST,
        pull_speeds_kph               = [30.0] * len(riders),
        max_exertion_intensity_factor = 0.95
    )

    save_filename_without_ext01 = f"{_output_filename_01_stub}{len(riders)}"

    print(f"Starting: head-to-head benchmarking of serial-processing versus parallel-processing with {len(riders)} riders, {len(STANDARD_PULL_PERIODS_SEC_AS_LIST)} pull periods, and consequently {pretty_number_of_sequences_before_pruning} paceline_rotation sequences (no solution-space pruning. all sequences evaluated).")
    print(f"\nCommencing serial processing. This could take a very long time depending on the number of sequences. Please wait....")

    # Serial run as the base case (ignore squigglies here, they are inconsequential warnings)
    s1 = time.perf_counter()
    _ = generate_paceline_solutions_using_serial_processing_algorithm(paceline_ingredients, all_conceivable_paceline_rotation_sequences)
    s2 = time.perf_counter()
    print(f"\nBase-case: serial run compute time: {round(s2 - s1, 2)} seconds")
    print(f"\nCommencing parallel processing. Please wait....")

    # Parallel run (ignore squigglies here, they are inconsequential warnings)
    p1 = time.perf_counter()
    _ = generate_paceline_solutions_using_parallel_workstealing_algorithm(paceline_ingredients, all_conceivable_paceline_rotation_sequences)
    p2 = time.perf_counter()

    print(f"\nTest-case: parallel run compute time: {round(p2 - p1,2)} seconds")

    # --- Summary Report ---
    report_lines : List[str] = []
    report_lines.append("Benchmark Summary Report\n")
    report_lines.append(f"Number of riders: {len(riders)}\n\n")
    report_lines.append(f"Number of standard pull periods: {len(STANDARD_PULL_PERIODS_SEC_AS_LIST)}\n\n")
    report_lines.append(f"Consequential number of paceline-rotation sequences: {pretty_number_of_sequences_before_pruning}\n\n")
    report_lines.append(f"Serial run: Compute time: {round(s2 - s1, 2)} seconds\n")
    report_lines.append(f"Parallel run (work-stealing): Compute time: {round(p2 - p1,2)} seconds\n")
    report_lines.append(f"Time saved by parallelisation: {round((s2 - s1) - (p2 - p1), 2)} seconds")
    report_lines.append("\n")

    print("".join(report_lines))

    write_lines(Path(DIRPATH_RUBBISH_SCRATCHPAD), f"{save_filename_without_ext01}.txt", report_lines)
    # with open(f"{save_filename_without_ext01}.txt", "w", encoding="utf-8") as f:
    #     f.writelines(report_lines)
    print(f"Summary report written to {save_filename_without_ext01}.txt")

    # --- Visualization: Bar Chart ---
    df = pd.DataFrame([
        {"Method": "Serial-processing", "Compute Time (s)": s2 - s1},
        {"Method": "Parallel-processing (work stealing)", "Compute Time (s)": p2 - p1},
    ])

    plt.figure(figsize=(8, 5))
    sns.barplot(data=df, x="Method", y="Compute Time (s)", hue="Method", palette="Blues_d", legend=False)    
    plt.title(f"Compute Time: Serial-processing vs Parallel-processing (work stealing): Paceline rotation sequences: {pretty_number_of_sequences_before_pruning}")
    plt.ylabel("Compute Time (seconds)")
    plt.xlabel("Method")
    plt.tight_layout()
    save_chart_path = os.path.join(DIRPATH_RUBBISH_SCRATCHPAD, f"{save_filename_without_ext01}.png")
    plt.savefig(save_chart_path)
    plt.show()
    print(f"Bar chart saved to {save_chart_path}")

def test02():
    """
    Identical to test01() except that it uses the pruned list of paceline-rotation
    sequences rather than the full list of conceivable sequences, so as to
    demonstrate the benefits of pruning on compute time and how it renders the
    brute-force approach feasible for larger numbers of riders. Without pruning,
    the brute-force approach becomes unfeasible very quickly as the number of
    riders increases. Even with parallel processing, it becomes impractical beyond
    4 riders. With pruning, it is excellent up to 6, which is the max size of a
    paceline in ZRL events, remains decent up to 8 riders (the max in WTRL TTT
    events), and can even be tolerable for 9 riders. The pruning heuristic 
    takes a single parameter : ROTATION_SEQUENCE_UNIVERSE_SIZE_PRUNING_GOAL. 
    For the test results shown here, this is set somewhat arbitrarily at 1,024. 
    Notice how pruning radically reduces the solution space for 4 riders and beyond. 
    At the time of writing (Aug 2025), the numbers look like this:
        
        Riders  Sequences After pruning serial-processing parallel-processing
            1           7             7       <1s               5s 
            2          49            49       <1s               7s
            3         343           343        6s               11s
            4       2,401           980       28s               10s
            5      16,807           966       42s               12s
            6     117,649           924       60s               13s
            7     823,543         1,716      126s               21s
            8   5,764,801         3,003      322s               37s    
            9  40,353,607         5,005      699s               71s         


    This function:
      - Loads rider data and team composition from JSON and utility functions.
      - Generates all possible paceline rotation sequences for the team and standard pull periods.
      - Runs the paceline solution algorithm using both serial and parallel approaches, timing each.
      - Logs and writes a summary report comparing the compute times and time saved by parallelization.
      - Visualizes the results in a bar chart and saves the chart as a PNG file.

    The function is intended for performance analysis and does not return a value. All results are 
    logged and saved as a .png.

    Side Effects:
      - Writes a summary report to a text file.
      - Saves a bar chart visualization as a PNG file.
      - Logs progress and results using the configured logger.

    Raises:
      - Exceptions are logged if encountered during computation.

    Dependencies:
      - Expects global variables FILENAME_RIDER_BRUTE_DTO_JSON_DICT and DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT, ROTATION_SEQUENCE_UNIVERSE_SIZE_PRUNING_GOAL to be set.
      - Requires pandas, seaborn, matplotlib, and other project-specific modules.
    """

    paceline_ingredients = PacelineIngredientsItem(
        riders_list                   = riders,
        sequence_of_pull_periods_sec  = STANDARD_PULL_PERIODS_SEC_AS_LIST,
        pull_speeds_kph               = [30.0] * len(riders),
        max_exertion_intensity_factor = 0.95
    )

    save_filename_without_ext02 = f"{_output_filename_02_stub}{len(riders)}"

    print(f"Starting: head-to-head benchmarking of serial-processing versus parallel-processing with {len(riders)} riders, {len(STANDARD_PULL_PERIODS_SEC_AS_LIST)} pull periods, and consequently {pretty_number_of_sequences_before_pruning} paceline_rotation sequences before pruning and {pretty_number_of_sequences_after_pruning} sequences after pruning.")
    print(f"\nCommencing serial processing. This could take a very long time depending on the number of sequences. Please wait....")

    # Serial run as the base case (ignore squigglies here, they are inconsequential warnings)
    s1 = time.perf_counter()
    _ = generate_paceline_solutions_using_serial_processing_algorithm(paceline_ingredients, reduced_paceline_rotation_sequences_after_pruning)
    s2 = time.perf_counter()
    print(f"\nBase-case: serial run compute time: {round(s2 - s1, 2)} seconds")
    print(f"\nCommencing parallel processing. Please wait....")
    # Parallel run (ignore squigglies here, they are inconsequential warnings)
    p1 = time.perf_counter()
    _ = generate_paceline_solutions_using_parallel_workstealing_algorithm(paceline_ingredients, reduced_paceline_rotation_sequences_after_pruning)
    p2 = time.perf_counter()

    print(f"\nTest-case: parallel run compute time: {round(p2 - p1,2)} seconds")

    # --- Summary Report ---
    report_lines : List[str] = []
    report_lines.append("Benchmark Summary Report\n")
    report_lines.append(f"Number of riders: {len(riders)}\n")
    report_lines.append(f"Number of standard pull periods: {len(STANDARD_PULL_PERIODS_SEC_AS_LIST)}\n")
    report_lines.append(f"Universe of all paceline-rotation sequences: {pretty_number_of_sequences_before_pruning}\n")
    report_lines.append(f"Pruning goal: {ROTATION_SEQUENCE_UNIVERSE_SIZE_PRUNING_GOAL}\n")
    report_lines.append(f"Paceline-rotation sequences after pruning: {pretty_number_of_sequences_after_pruning}\n")
    report_lines.append(f"Serial run: Compute time: {round(s2 - s1, 2)} seconds\n")
    report_lines.append(f"Parallel run (work-stealing): Compute time: {round(p2 - p1,2)} seconds\n")
    report_lines.append(f"Time saved by parallelisation: {round((s2 - s1) - (p2 - p1), 2)} seconds")
    report_lines.append("\n")

    print("".join(report_lines))

    write_lines(Path(DIRPATH_RUBBISH_SCRATCHPAD), f"{save_filename_without_ext02}.txt",report_lines )

    # with open(f"{save_filename_without_ext02}.txt", "w", encoding="utf-8") as f:
    #     f.writelines(report_lines)
    print(f"Summary report written to {save_filename_without_ext02}.txt")

    # --- Visualization: Bar Chart ---
    df = pd.DataFrame([
        {"Method": "Serial-processing", "Compute Time (s)": s2 - s1},
        {"Method": "Parallel-processing (work stealing)", "Compute Time (s)": p2 - p1},
    ])

    plt.figure(figsize=(8, 5))
    sns.barplot(data=df, x="Method", y="Compute Time (s)", hue="Method", palette="Blues_d", legend=False)    
    plt.title(f"Compute Time: Serial-processing vs Parallel-processing (work stealing): Paceline rotation sequences after pruning: {pretty_number_of_sequences_before_pruning}")
    plt.ylabel("Compute Time (seconds)")
    plt.xlabel("Method")
    plt.tight_layout()
    save_chart_path = os.path.join(DIRPATH_RUBBISH_SCRATCHPAD, f"{save_filename_without_ext02}.png")

    plt.savefig(save_chart_path)
    plt.show()
    print(f"Bar chart saved to {save_chart_path}.png")

if __name__ == "__main__":
    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    start_time = time.time()
    try:

        _output_filename_01_stub = f"compare_serial_processing_versus_parallel_processing_duration_"
        _output_filename_02_stub = f"compare_serial_processing_versus_parallel_processing_duration_after_pruning_"
        # get ready
        dict_of_all_riders = read_file_as_json_dict_of_RiderDTO(Path( DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT), FILENAME_RIDER_BRUTE_DTO_JSON_DICT)
        riderIDs = RepositoryOfTeamRosters.get_IDs_of_riders_on_a_team("scratchpad")
        riders: List[RiderBruteItem] = lookup_Items_by_ZwiftID(riderIDs, dict_of_all_riders, RiderBruteItem)
        all_conceivable_paceline_rotation_sequences = generate_all_paceline_rotation_sequences_in_the_total_solution_space(len(riders), STANDARD_PULL_PERIODS_SEC_AS_LIST)
        pretty_number_of_sequences_before_pruning = format_number_with_comma_separators(len(all_conceivable_paceline_rotation_sequences))
        reduced_paceline_rotation_sequences_after_pruning = prune_all_sequences_of_pull_periods_in_the_total_solution_space(all_conceivable_paceline_rotation_sequences, riders)
        pretty_number_of_sequences_after_pruning = format_number_with_comma_separators(len(reduced_paceline_rotation_sequences_after_pruning))
        # do tests
        # test01()
        test02()

        end_time = time.time()
        duration = end_time - start_time

        log_event(
            logger,
            message=f"Main execution completed successfully in {duration:.2f} seconds. All tests executed without error.",
            level=logging.INFO
        )
        print(f"\nSuccess: Main execution completed successfully in {duration:.2f} seconds. All tests executed without error.\n")

    except AlertMessageError as alert_err:
        log_event(
            logger,
            message=alert_err.message,
            level=logging.INFO,
            exception=alert_err
        )
        print(f"{alert_err.message}\n")

    except Exception as ex:
        log_event(
            logger,
            message=f"Unhandled Exception: {ex}",
            level=logging.ERROR,
            exception=ex  # Pass the original exception object
        )
        print(f"Unhandled Exception: {ex}\n\nPlease check the logs for details.\n\nDirpath: {DIRPATH_LOGGING}\n")



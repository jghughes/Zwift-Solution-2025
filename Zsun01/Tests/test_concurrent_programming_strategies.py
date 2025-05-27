import logging
from jgh_logging import jgh_configure_logging
jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)
logging.getLogger('matplotlib').setLevel(logging.WARNING)

save_filename_without_ext = "compare_concurrent_programming_strategies_9_riders"

def main01():
    from handy_utilities import read_dict_of_zsunriderItems
    from repository_of_teams import get_team_riderIDs
    from jgh_formulae08 import search_for_optimal_pull_plans_concurrently
    from jgh_formulae09 import search_for_optimal_pull_plans_concurrently_with_chunking
    from constants import STANDARD_PULL_PERIODS_SEC, BINARY_SEARCH_SEED_KPH, MAX_INTENSITY_FACTOR, RIDERS_FILE_NAME, DATA_DIRPATH

    import time
    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt

    dict_of_zsunrideritems = read_dict_of_zsunriderItems(RIDERS_FILE_NAME, DATA_DIRPATH)
    riderIDs = get_team_riderIDs("betel")
    riders = [dict_of_zsunrideritems[rid] for rid in riderIDs]

    results = []

    # 1. Baseline: search_for_optimal_pull_plans_concurrently
    start = time.perf_counter()
    res1 = search_for_optimal_pull_plans_concurrently(riders, STANDARD_PULL_PERIODS_SEC, BINARY_SEARCH_SEED_KPH, MAX_INTENSITY_FACTOR)
    elapsed1 = time.perf_counter() - start
    logger.info(f"search_for_optimal_pull_plans_concurrently: {elapsed1:.4f}s with work-stealing algorithm")

    # 2. Chunking with None args
    start = time.perf_counter()
    res2 = search_for_optimal_pull_plans_concurrently_with_chunking(riders, STANDARD_PULL_PERIODS_SEC, BINARY_SEARCH_SEED_KPH, chunk_size=None, max_workers=None)
    elapsed2 = time.perf_counter() - start
    logger.info(f"search_for_optimal_pull_plans_concurrently_with_chunking (None args): {elapsed2:.4f}s")

    # 3. Chunking with default args (omit chunk_size and max_workers)
    start = time.perf_counter()
    res3 = search_for_optimal_pull_plans_concurrently_with_chunking(riders, STANDARD_PULL_PERIODS_SEC, BINARY_SEARCH_SEED_KPH)
    elapsed3 = time.perf_counter() - start
    logger.info(f"search_for_optimal_pull_plans_concurrently_with_chunking (default args): {elapsed3:.4f}s")

    results.append({
        "strategy": "concurrent",
        "elapsed_sec": elapsed1
    })
    results.append({
        "strategy": "chunking_none",
        "elapsed_sec": elapsed2
    })
    results.append({
        "strategy": "chunking_default",
        "elapsed_sec": elapsed3
    })

    # Save results to CSV
    df = pd.DataFrame(results)
    csv_path = f"{save_filename_without_ext}.csv"
    df.to_csv(csv_path, index=False)
    logger.info(f"Saved benchmark data to {csv_path}")

    # Generate and save Seaborn bar chart
    plt.figure(figsize=(8, 5))
    sns.barplot(data=df, x="strategy", y="elapsed_sec")
    plt.title("Benchmark: Concurrent Programming Strategies")
    plt.ylabel("Elapsed Time (seconds)")
    plt.xlabel("Strategy")
    plt.tight_layout()
    png_path = f"{save_filename_without_ext}.png"
    plt.savefig(png_path)
    plt.show()
    logger.info(f"Saved benchmark chart to {png_path}")

    # Write report and conclusions
    best_row = df.loc[df['elapsed_sec'].idxmin()]
    report_lines = [
        "Benchmark Report: Concurrent Programming Strategies\n",
        "Tested strategies:",
        "1. search_for_optimal_pull_plans_concurrently",
        "2. search_for_optimal_pull_plans_concurrently_with_chunking (chunk_size=None, max_workers=None)",
        "3. search_for_optimal_pull_plans_concurrently_with_chunking (default args)\n",
        f"Data saved to: {csv_path}",
        f"Chart saved to: {png_path}\n",
        "Results:\n"
    ]
    for _, row in df.iterrows():
        report_lines.append(f"  {row['strategy']}: {row['elapsed_sec']:.4f} seconds")
    report_lines.append(f"\nConclusion: The fastest strategy was '{best_row['strategy']}' ({best_row['elapsed_sec']:.4f} seconds).\n")
    report_path = f"{save_filename_without_ext}.txt"
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines))
    logger.info(f"Saved benchmark report to {report_path}")

if __name__ == "__main__":
    main01()
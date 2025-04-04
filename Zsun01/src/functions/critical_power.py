from typing import List, Tuple, Dict
import numpy as np
from numpy import ndarray
from  matplotlib import pyplot as plt
from tabulate import tabulate
from datetime import datetime
import os
import logging


# formulae originate from https://pmc.ncbi.nlm.nih.gov/articles/PMC9265641/
def distill_cp_metrics_from_wattages_per_second(datapoints: List[Tuple[int, float]], cp_test_duration_specs: List[int]) -> Dict[int, float]:
    """
    Segment the data into specified durations and calculate the maximum average power for each segment.

    Args:
        datapoints (List[Tuple[int, float]]): List of power wattages recorded per second for a period of one hour.
        cp_test_duration_specs (List[int]): List of required critical power timespan in seconds.

    Returns:
        Dict[int, float]: Dictionary where key is the cp timespan (sec) and value is power (W) for the timespan.
    """
    dict_of_riders_and_their_criticalpower_curve: Dict[int, float] = {}

    for duration in cp_test_duration_specs:
        max_avg_power: float = 0.0
        num_intervals: int = 3600 - duration + 1

        # Calculate the sum of the first interval
        interval_sum: float = sum(datapoints[j][1] for j in range(duration))
        max_avg_power = interval_sum / duration

        # Use sliding window technique to calculate the sum of subsequent intervals
        for i in range(1, num_intervals):
            interval_sum = interval_sum - datapoints[i - 1][1] + datapoints[i + duration - 1][1]
            avg_power: float = interval_sum / duration
            if avg_power > max_avg_power:
                max_avg_power = avg_power

        dict_of_riders_and_their_criticalpower_curve[duration] = max_avg_power

    return dict_of_riders_and_their_criticalpower_curve



def filter_cp_interval_data(cp_interval_data: Dict[int, float]) -> Dict[int, float]:
    """
    Filter out any cp_interval_data datapoints with value=0.

    Args:
        cp_interval_data (Dict[int, float]): Dictionary of power data for one hour.

    Returns:
        Dict[int, float]: Filtered dictionary with no zero values.
    """
    return {duration: power for duration, power in cp_interval_data.items() if power != 0}


def linearize_cp_metrics(cp_interval_data: Dict[int, float]) -> Tuple[ndarray, ndarray]:
    """
    Linearize the data by plotting the average power output against the inverse of the duration.

    Args:
        cp_interval_data (Dict[int, float]): Dictionary where keys are segment durations and values are average power outputs.

    Returns:
        Tuple[ndarray, ndarray]: Arrays of inverse durations and average power outputs.
    """
    # Filter out zero values
    cp_interval_data = filter_cp_interval_data(cp_interval_data)

    # Extract durations and average powers
    durations = np.array(list(cp_interval_data.keys()), dtype=float)
    avg_powers = np.array(list(cp_interval_data.values()), dtype=float)

    # Calculate inverse durations
    inverse_durations = 1 / durations

    return inverse_durations, avg_powers

def make_bestfit_cp_model(inverse_durations: ndarray, avg_powers: ndarray) -> Tuple[float, float]:
    """
    Fit a linear model to the linearized data.

    Args:
        inverse_durations (ndarray): Array of inverse durations.
        avg_powers (ndarray): Array of average power outputs.

    Returns:
        Tuple[float, float]: Slope and intercept of the fitted line.
    """
    A: ndarray = np.vstack([inverse_durations, np.ones(len(inverse_durations))]).T
    slope: float
    intercept: float
    slope, intercept = np.linalg.lstsq(A, avg_powers, rcond=None)[0]
    return float(slope), float(intercept)


def deduce_cp_and_w_prime_from_bestfit_model(slope: float, intercept: float) -> Tuple[float, float]:
    """
    Extract CP and W' from the fitted model.

    Args:
        slope (float): Slope of the fitted line.
        intercept (float): Intercept of the fitted line.

    Returns:
        Tuple[float, float]: Estimated CP (in watts) and W' (in joules).
    """
    cp: float = intercept
    w_prime: float = slope * cp
    return cp, w_prime

def estimate_cp_and_w_prime(cp_interval_data: Dict[int, float]) -> Tuple[float, float]:
    """
    Calculate Critical Power (CP) and Work Capacity Above CP (W') for a rider.

    Args:
        cp_interval_data (List[Tuple[int, float]]): List of power cp_interval_data for one hour.
        criticalpower_timespans (List[int]): List of segment durations in seconds.
        high_intensity_threshold (float): Power output threshold for high-intensity efforts.
        moderate_intensity_threshold (float): Power output threshold for moderate efforts.
        recovery_rate (float): Rate at which fatigue is recovered during low-intensity efforts.

    Returns:
        Tuple[float, float]: Estimated CP (in watts) and W' (work capacity above CP in joules).
    """
   
    inverse_durations, avg_powers = linearize_cp_metrics(cp_interval_data)
    slope, intercept = make_bestfit_cp_model(inverse_durations, avg_powers)
    cp, w_prime = deduce_cp_and_w_prime_from_bestfit_model(slope, intercept)
    return cp, w_prime

def plot_cp_interval_data(cp_interval_data: Dict[int, float], dirpath: str, filename: str = "cp_interval_data.png") -> str:
    """
    Plot the cp_interval_data showing the relationship between durations and average powers and save the plot to a file.

    Args:
        cp_interval_data (Dict[int, float]): Dictionary of power data for one hour.
        dirpath (str): The directory path to save the plot.
        filename (str): The filename to save the plot, including the file format (e.g., 'cp_interval_data.png').

    Returns:
        str: The absolute file path of the saved plot.
    """
    durations = list(cp_interval_data.keys())
    avg_powers = list(cp_interval_data.values())

    # Create scatter plot
    plt.figure(figsize=(10, 6))
    plt.scatter(durations, avg_powers, color='blue', label='Data Points')

    # Add labels and title
    plt.xlabel('Duration (s)')
    plt.ylabel('Average Power (W)')
    plt.title('Relationship between Durations and Average Powers')
    plt.xticks(durations)  # Ensure all durations are shown on the x-axis
    plt.legend()

    # Create timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Combine dirpath and filename with timestamp
    abs_filepath = os.path.join(dirpath, f"{filename.split('.')[0]}_{timestamp}.{filename.split('.')[1]}")

    # Save plot to file
    plt.savefig(abs_filepath)
    plt.show()

    return abs_filepath

def plot_linearized_cp_metrics(inverse_durations: ndarray, avg_powers: ndarray, dirpath: str, filename: str = "linearized_cp_metrics.png") -> str:
    """
    Plot the linearized CP metrics showing the relationship between inverse durations and average powers and save the plot to a file.

    Args:
        inverse_durations (ndarray): Array of inverse durations.
        avg_powers (ndarray): Array of average power outputs.
        dirpath (str): The directory path to save the plot.
        filename (str): The filename to save the plot, including the file format (e.g., 'linearized_cp_metrics.png').

    Returns:
        str: The absolute file path of the saved plot.
    """
    # Create scatter plot
    plt.figure(figsize=(10, 6))
    plt.scatter(inverse_durations, avg_powers, color='blue', label='Data Points')

    # Add labels and title
    plt.xlabel('Inverse Duration (1/s)')
    plt.ylabel('Average Power (W)')
    plt.title('Relationship between Inverse Durations and Average Powers')
    plt.xticks(inverse_durations)  # Ensure all durations are shown on the x-axis
    plt.legend()

    # Create timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Combine dirpath and filename with timestamp
    abs_filepath = os.path.join(dirpath, f"{filename.split('.')[0]}_{timestamp}.{filename.split('.')[1]}")

    # Save plot to file
    plt.savefig(abs_filepath)
    plt.show()

    return abs_filepath

def plot_cp_relationship(cp_interval_data: Dict[int, float], dirpath: str, filename: str = "cp_relationship.png") -> str:
    """
    Visualize the relationship between inverse durations and average powers and save the plot to a file.

    Args:
        cp_interval_data (Dict[int, float]): Dictionary of power data for one hour.
        dirpath (str): The directory path to save the plot.
        filename (str): The filename to save the plot, including the file format (e.g., 'cp_relationship.png').

    Returns:
        str: The absolute file path of the saved plot.
    """
    inverse_durations, avg_powers = linearize_cp_metrics(cp_interval_data)
    slope, intercept = make_bestfit_cp_model(inverse_durations, avg_powers)

    # Create scatter plot
    plt.scatter(inverse_durations, avg_powers, color='blue', label='Data Points')

    # Create line plot for the best-fit line
    best_fit_line = slope * inverse_durations + intercept
    plt.plot(inverse_durations, best_fit_line, color='red', label='Best Fit Line')

    # Add labels and title
    plt.xlabel('Inverse Duration (1/s)')
    plt.ylabel('Average Power (W)')
    plt.title('Relationship between Inverse Durations and Average Powers')
    plt.xticks(inverse_durations)  # Ensure all durations are shown on the x-axis
    plt.legend()

    # Create timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Combine dirpath and filename with timestamp
    abs_filepath = os.path.join(dirpath, f"{filename.split('.')[0]}_{timestamp}.{filename.split('.')[1]}")

    # Save plot to file
    plt.savefig(abs_filepath)
    plt.show()

def main() -> None:
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    # Set the directory path where you want to save the plots
    dirpath = "C:/Users/johng/holding_pen"
    
    # Ensure the directory path exists
    os.makedirs(dirpath, exist_ok=True)

    tuples_of_duration_and_ave_power = {5: 546.0, 15: 434.0, 30: 425.0, 60: 348.0, 180: 293.0, 300: 292.0, 600: 268.0, 720: 264.0, 900: 255.0, 1200: 254.0, 1800: 252.0, 2400: 244.0}

    # Prepare data for table
    table_data = []
    for duration, ave_power in tuples_of_duration_and_ave_power.items():
        inverse_duration = 1 / duration
        table_data.append([round(duration), round(ave_power), round(inverse_duration,3)])

    # Log the table
    table = tabulate(table_data, headers=["Duration (s)", "Average Power (W)", "Inverse Duration (1/s)"], tablefmt="grid")
    logger.info(f"\n{table}")


    inverse_durations_ndarray, avg_powers_ndarray  = linearize_cp_metrics(tuples_of_duration_and_ave_power)

    slope, intercept = make_bestfit_cp_model(inverse_durations_ndarray, avg_powers_ndarray )

    cp, w_prime = deduce_cp_and_w_prime_from_bestfit_model(slope, intercept)

    # log the output
    logger.info(f"Slope: {round(slope)}")
    logger.info(f"Intercept: {round(intercept)}")
    logger.info(f"Critical Power (CP): {round(cp)}")
    logger.info(f"Work Capacity Above CP (W'): {round(w_prime)}")



    # Plot cp_interval_data
    cp_interval_data_filepath = plot_cp_interval_data(tuples_of_duration_and_ave_power, dirpath, "cp_interval_data.png")
    logger.info(f"CP Interval Data plot saved to: {cp_interval_data_filepath}")

    # Plot linearized CP metrics
    linearized_cp_metrics_filepath = plot_linearized_cp_metrics(inverse_durations_ndarray, avg_powers_ndarray, dirpath, "linearized_cp_metrics.png")
    logger.info(f"Linearized CP Metrics plot saved to: {linearized_cp_metrics_filepath}")

    # Visualize the relationship
    cp_relationship_filepath = plot_cp_relationship(tuples_of_duration_and_ave_power, dirpath, "cp_relationship.png")
    logger.info(f"CP Relationship plot saved to: {cp_relationship_filepath}")

if __name__ == "__main__":
    main()

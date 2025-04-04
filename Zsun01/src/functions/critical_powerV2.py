from typing import List, Tuple, Dict, Callable
import numpy as np
from numpy import ndarray
from matplotlib import pyplot as plt
from tabulate import tabulate
from datetime import datetime
import os
import logging
from sklearn.metrics import r2_score, mean_squared_error

# Function to calculate goodness-of-fit metrics
def evaluate_model_fit(observed: np.ndarray, predicted: np.ndarray) -> Dict[str, float]:
    r2 = r2_score(observed, predicted)
    rmse = np.sqrt(mean_squared_error(observed, predicted))
    return {"R-squared": r2, "RMSE": rmse}

# Linear-TW model
def calculate_cp_awc_linear_tw(tw_data: Dict[int, float]) -> Tuple[float, float]:
    durations = np.array(list(tw_data.keys()), dtype=float)
    total_work = np.array(list(tw_data.values()), dtype=float)
    A = np.vstack([durations, np.ones(len(durations))]).T
    cp, awc = np.linalg.lstsq(A, total_work, rcond=None)[0]
    return cp, awc

# Linear-P model
def calculate_cp_awc_linear_p(power_data: Dict[int, float]) -> Tuple[float, float]:
    durations = np.array(list(power_data.keys()), dtype=float)
    power_outputs = np.array(list(power_data.values()), dtype=float)
    inverse_durations = 1 / durations
    A = np.vstack([inverse_durations, np.ones(len(inverse_durations))]).T
    awc, cp = np.linalg.lstsq(A, power_outputs, rcond=None)[0]
    return cp, awc

# Exponential model
def calculate_cp_awc_exponential(tw_data: Dict[int, float]) -> Tuple[float, float]:
    durations = np.array(list(tw_data.keys()), dtype=float)
    total_work = np.array(list(tw_data.values()), dtype=float)
    log_durations = np.log(durations)
    A = np.vstack([log_durations, np.ones(len(log_durations))]).T
    cp, awc = np.linalg.lstsq(A, total_work, rcond=None)[0]
    return cp, awc

def calculate_cp_awc_2_parameter(data: Dict[int, float]) -> Tuple[float, float]:
    durations = np.array(list(data.keys()), dtype=float)
    power_outputs = np.array(list(data.values()), dtype=float)
    inverse_durations = 1 / durations
    A = np.vstack([inverse_durations, np.ones(len(inverse_durations))]).T
    w_prime, cp = np.linalg.lstsq(A, power_outputs, rcond=None)[0]
    return cp, w_prime

def calculate_cp_awc_3_parameter(data: Dict[int, float]) -> Tuple[float, float, float]:
    durations = np.array(list(data.keys()), dtype=float)
    power_outputs = np.array(list(data.values()), dtype=float)
    inverse_durations = 1 / durations
    A = np.vstack([inverse_durations, np.ones(len(inverse_durations))]).T
    w_prime, cp = np.linalg.lstsq(A, power_outputs, rcond=None)[0]
    tau = np.mean(durations)  # Example calculation for tau
    return cp, w_prime, tau

def calculate_cp_awc_hyperbolic(data: Dict[int, float]) -> Tuple[float, float]:
    durations = np.array(list(data.keys()), dtype=float)
    power_outputs = np.array(list(data.values()), dtype=float)
    A = np.vstack([1 / durations, np.ones(len(durations))]).T
    awc, cp = np.linalg.lstsq(A, power_outputs, rcond=None)[0]
    return cp, awc

def calculate_cp_awc_monod_scherrer(data: Dict[int, float]) -> Tuple[float, float]:
    durations = np.array(list(data.keys()), dtype=float)
    power_outputs = np.array(list(data.values()), dtype=float)
    A = np.vstack([1 / durations, np.ones(len(durations))]).T
    awc, cp = np.linalg.lstsq(A, power_outputs, rcond=None)[0]
    return cp, awc

def calculate_cp_awc_log_linear(data: Dict[int, float]) -> Tuple[float, float]:
    """
    Calculate Critical Power (CP) and Anaerobic Work Capacity (AWC) using the Log-Linear model.

    Args:
        data (Dict[int, float]): Dictionary where keys are time durations (in seconds) and values are power outputs (in watts).

    Returns:
        Tuple[float, float]: Estimated CP (in watts) and AWC (in joules).
    """
    durations = np.array(list(data.keys()), dtype=float)
    power_outputs = np.array(list(data.values()), dtype=float)
    log_durations = np.log(durations)

    # Linear regression to find CP and AWC
    A = np.vstack([log_durations, np.ones(len(log_durations))]).T
    cp, awc = np.linalg.lstsq(A, power_outputs, rcond=None)[0]
    return cp, awc


def calculate_cp_awc_nonlinear(data: Dict[int, float], n: float) -> Tuple[float, float]:
    """
    Calculate Critical Power (CP) and Work Capacity Above CP (W') using a Nonlinear model.

    Args:
        data (Dict[int, float]): Dictionary where keys are time durations (in seconds) and values are power outputs (in watts).
        n (float): Nonlinear parameter.

    Returns:
        Tuple[float, float]: Estimated CP (in watts) and W' (in joules).
    """
    durations = np.array(list(data.keys()), dtype=float)
    power_outputs = np.array(list(data.values()), dtype=float)
    inverse_durations_n = 1 / (durations ** n)

    # Linear regression to find CP and W'
    A = np.vstack([inverse_durations_n, np.ones(len(inverse_durations_n))]).T
    w_prime, cp = np.linalg.lstsq(A, power_outputs, rcond=None)[0]
    return cp, w_prime



def plot_cp_awc(data: Dict[int, float], cp: float, awc: float, dirpath: str, filename: str, model: Callable, tau: float = None) -> str:
    durations = np.array(list(data.keys()), dtype=float)
    values = np.array(list(data.values()), dtype=float)
    plt.figure(figsize=(10, 6))
    plt.scatter(durations, values, color='blue', label='Data Points')
    
    model_name = model.__name__ if hasattr(model, '__name__') else model.__class__.__name__
    
    if model_name == 'calculate_cp_awc_linear_tw':
        best_fit_line = awc + cp * durations
    elif model_name == 'calculate_cp_awc_linear_p':
        best_fit_line = cp + awc / durations
    elif model_name == 'calculate_cp_awc_exponential':
        best_fit_line = awc + cp * np.log(durations)
    elif model_name == 'calculate_cp_awc_2_parameter':
        best_fit_line = cp + awc / durations
    elif model_name == 'calculate_cp_awc_3_parameter':
        best_fit_line = cp + awc / (durations + tau)
    elif model_name == 'calculate_cp_awc_hyperbolic':
        best_fit_line = awc / durations + cp
    elif model_name == 'calculate_cp_awc_monod_scherrer':
        best_fit_line = awc / durations + cp
    elif model_name == 'calculate_cp_awc_log_linear':
        best_fit_line = cp + awc * np.log(durations)
    elif model_name == '<lambda>':  # For the Nonlinear model using lambda
        best_fit_line = cp + awc / (durations ** 1.5)  # Assuming n=1.5 for the Nonlinear model
    else:
        raise ValueError(f"Unsupported model: {model_name}")

    plt.plot(durations, best_fit_line, color='red', label='Best Fit Line')
    plt.xlabel('Time (s)')
    plt.ylabel('Total Work (J)' if model_name != 'calculate_cp_awc_linear_p' else 'Power (W)')
    plt.title('Total Work vs. Time' if model_name != 'calculate_cp_awc_linear_p' else 'Power vs. Inverse Time')
    plt.legend()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    abs_filepath = os.path.join(dirpath, f"{filename.split('.')[0]}_{timestamp}.{filename.split('.')[1]}")
    plt.savefig(abs_filepath)
    plt.show()
    return abs_filepath






def plot_combined_models(data: Dict[int, float], models: List[Tuple[str, Callable, Dict[int, float]]], dirpath: str, filename: str) -> str:
    durations = np.array(list(data.keys()), dtype=float)
    plt.figure(figsize=(10, 6))
    plt.scatter(durations, list(data.values()), color='blue', label='Data Points')
    
    for model_name, model_func, _ in models:
        if model_name == "3-Parameter":
            cp, awc, tau = model_func(data)
            best_fit_line = cp + awc / (durations + tau)
        elif model_name == "Nonlinear":
            cp, awc = model_func(data)
            best_fit_line = cp + awc / (durations ** 1.5)  # Assuming n=1.5 for the Nonlinear model
        else:
            cp, awc = model_func(data)
            if model_func == calculate_cp_awc_linear_tw:
                best_fit_line = awc + cp * durations
            elif model_func == calculate_cp_awc_linear_p:
                best_fit_line = cp + awc / durations
            elif model_func == calculate_cp_awc_exponential:
                best_fit_line = awc + cp * np.log(durations)
            elif model_func == calculate_cp_awc_2_parameter:
                best_fit_line = cp + awc / durations
            elif model_func == calculate_cp_awc_hyperbolic:
                best_fit_line = awc / durations + cp
            elif model_func == calculate_cp_awc_monod_scherrer:
                best_fit_line = awc / durations + cp
            elif model_func == calculate_cp_awc_log_linear:
                best_fit_line = cp + awc * np.log(durations)
            else:
                raise ValueError(f"Unsupported model: {model_name}")
        
        plt.plot(durations, best_fit_line, label=f'{model_name} Best Fit Line')
    
    plt.xlabel('Time (s)')
    plt.ylabel('Total Work (J)' if model_func != calculate_cp_awc_linear_p else 'Power (W)')
    plt.title('Comparison of Models')
    plt.legend()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    abs_filepath = os.path.join(dirpath, f"{filename.split('.')[0]}_{timestamp}.{filename.split('.')[1]}")
    plt.savefig(abs_filepath)
    plt.show()
    return abs_filepath












def main() -> None:









    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    dirpath = "C:/Users/johng/holding_pen"
    os.makedirs(dirpath, exist_ok=True)

    tuples_of_duration_and_ave_power = {5: 546.0, 15: 434.0, 30: 425.0, 60: 348.0, 180: 293.0, 300: 292.0, 600: 268.0, 720: 264.0, 900: 255.0, 1200: 254.0, 1800: 252.0, 2400: 244.0}

    table_data = []
    for duration, ave_power in tuples_of_duration_and_ave_power.items():
        inverse_duration = 1 / duration
        table_data.append([round(duration), round(ave_power), round(inverse_duration, 3)])
    table = tabulate(table_data, headers=["Duration (s)", "Average Power (W)", "Inverse Duration (1/s)"], tablefmt="grid")
    logger.info(f"\n{table}")

    models = [
        ("Linear-TW", calculate_cp_awc_linear_tw, tuples_of_duration_and_ave_power),
        ("Linear-P", calculate_cp_awc_linear_p, tuples_of_duration_and_ave_power),
        ("Exponential", calculate_cp_awc_exponential, tuples_of_duration_and_ave_power),
        ("2-Parameter", calculate_cp_awc_2_parameter, tuples_of_duration_and_ave_power),
        ("3-Parameter", calculate_cp_awc_3_parameter, tuples_of_duration_and_ave_power),
        ("Hyperbolic", calculate_cp_awc_hyperbolic, tuples_of_duration_and_ave_power),
        ("Monod-Scherrer", calculate_cp_awc_monod_scherrer, tuples_of_duration_and_ave_power),
        ("Log-Linear", calculate_cp_awc_log_linear, tuples_of_duration_and_ave_power),
        ("Nonlinear", lambda data: calculate_cp_awc_nonlinear(data, n=1.5), tuples_of_duration_and_ave_power)  # Add the Nonlinear model here with n=1.5
    ]

    summary_table = []

    for model_name, model_func, data in models:
        if model_name == "3-Parameter":
            cp, awc, tau = model_func(data)
            plot_filepath = plot_cp_awc(data, cp, awc, dirpath, f"{model_name.lower()}_cp_awc_plot.png", model_func, tau)
        else:
            cp, awc = model_func(data)
            plot_filepath = plot_cp_awc(data, cp, awc, dirpath, f"{model_name.lower()}_cp_awc_plot.png", model_func)
        
        logger.info(f"{model_name} Model - Critical Power (CP): {cp:.2f} W, Anaerobic Work Capacity (AWC): {awc:.2f} J")
        logger.info(f"{model_name} Model plot saved to: {plot_filepath}")

        summary_table.append([model_name, round(cp, 2), round(awc, 2), plot_filepath])

    summary_headers = ["Model", "Critical Power (CP) [W]", "Anaerobic Work Capacity (AWC) [J]", "Plot Filepath"]
    summary_table_str = tabulate(summary_table, headers=summary_headers, tablefmt="grid")
    logger.info(f"\n{summary_table_str}")

    combined_plot_filepath = plot_combined_models(tuples_of_duration_and_ave_power, models, dirpath, "combined_models_plot.png")
    logger.info(f"Combined models plot saved to: {combined_plot_filepath}")

if __name__ == "__main__":
    main()

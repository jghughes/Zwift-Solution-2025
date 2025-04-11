import numpy as np
from sklearn.metrics import r2_score
from scipy.optimize import curve_fit
from typing import Tuple, Dict


def linear_model(x : float, a : float, b: float):
    return a * x + b

def inverse_model(x : float, a : float, b: float):
    # this a decay function
    return a * (1/(x ** b))

def cp_w_prime_model(x: float, a: float, b: float) -> float:
    """
    Compute power as a function of CP and W' using the formula (a * x + b) / x.

    Args:
        x (float): Duration (seconds). Must be non-zero.
        a (float): Coefficient for the linear term, cp.
        b (float): Constant term, W'

    Returns:
        float: Computed power value.

    Raises:
        ValueError: If x is zero, to avoid division by zero.
    """
    return (a * x + b) / x

def do_modelling_with_cp_w_prime_model(raw_xy_data: Dict[int, float]) -> Tuple[float, float, float, Dict[int, Tuple[float, float]]]:
    """
    Estimate critical power and anaerobic work capacity from duration and power data.
    Estimate cp and w' using the formula x * y = cp * x + w'. x_axis is time in seconds and y_axis is power in watts.
    cp is the critical power, and w' is the anaerobic work capacity.

    Args:
        raw_xy_data (Dict[int, float]): Dictionary where keys are durations (seconds) and values are power (watts).

    Returns:
        Tuple[float, float, float, Dict[int, Tuple[float, float]]]: The values of cp and w', the R-squared value,
        and a dictionary combining the original data and predicted values.
    """
    # Convert keys and values of raw_xy_data to NumPy arrays
    xdata: np.ndarray = np.array(list(raw_xy_data.keys()), dtype=float)
    ydata: np.ndarray = np.array(list(raw_xy_data.values()), dtype=float)

    # Perform linear regression between duration and work using curve_fit
    # In the model, x stands for duration, and x * y is work (duration * power)
    popt, _ = curve_fit(linear_model, xdata, xdata * ydata)

    # Extract the optimal parameters: cp (critical power) and w_prime (anaerobic work capacity)
    # cp, w_prime = popt

    cp: float = float(popt[0])
    w_prime: float = float(popt[1])

    # Use the cp_w_prime_model to calculate predicted y values based on the fitted parameters
    ydata_pred: np.ndarray = cp_w_prime_model(xdata, cp, w_prime)

    # Calculate the R-squared value
    r2: float = r2_score(ydata, ydata_pred)

    # Recombine the original data and predicted values into a dictionary
    result: Dict[int, Tuple[float, float]] = {
        int(xdata[i]): (ydata[i], ydata_pred[i]) for i in range(len(xdata))
    }

    return cp, w_prime, r2, result

def do_modelling_with_inverse_model(raw_xy_data: Dict[int, float]) -> Tuple[float, float, float, Dict[int, Tuple[float, float]]]:
    """
    Perform modeling using an inverse model y = a * x^b, where b is typically negative (decay function).
    Args:
        x (List[float]): The list of x values (time in seconds).
        y (List[float]): The list of y values (power in watts).
    Returns:
        Tuple[float, float, float, List[float]]: The values of a and b, the R-squared value, and the predicted y values
        based on the best fit curve.
    """
    xdata: np.ndarray = np.array(list(raw_xy_data.keys()), dtype=float)
    ydata: np.ndarray = np.array(list(raw_xy_data.values()), dtype=float)

    # Perform curve fitting using the inverse model
    popt, _ = curve_fit(inverse_model, xdata, ydata)
    a, b = popt  # a is the coefficient, b is the exponent
    
    # Calculate the predicted y values based on the fitted parameters
    ydata_pred = inverse_model(xdata, a, b)
    
    # Calculate the R-squared value
    r2 = r2_score(ydata, ydata_pred)

    # Recombine the original data and predicted values into a dictionary
    result: Dict[int, Tuple[float, float]] = {
        int(xdata[i]): (ydata[i], ydata_pred[i]) for i in range(len(xdata))
    }
    return a, b, r2, result

# Example usage of the functions
def main():
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    from tabulate import tabulate
    import matplotlib.pyplot as plt
    logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO
    from handy_utilities import get_all_zwiftriders, get_all_zwiftriders_cp_data

    # get zwift 90-day rider data

    riders = get_all_zwiftriders()
    riders_cp_data = get_all_zwiftriders_cp_data()

    barryb ='5490373' 
    johnh ='58160'
    lynseys ='383480'
    joshn ='2508033'
    richardm ='1193'
    markb ='5530045'


    rider_id = johnh
    raw_xy_data = riders_cp_data[rider_id].export_cp_data_for_best_fitting()

    # do modelling

    cp, w_prime, r_squared, answer  = do_modelling_with_cp_w_prime_model(raw_xy_data)
    summary = f"Critical power model: CP={round(cp)}W  W'={round(w_prime/1_000)}kJ  R_squared={round(r_squared,2)}  P_1hour={round(cp_w_prime_model(60*60, cp, w_prime))}W"
    logger.info(f"\n{summary}")

    constant, exponent, r_squared2, answer2 = do_modelling_with_inverse_model(raw_xy_data)
    summary2 = f"Inverse model: c={round(constant,0)}  e={round(exponent,4)}  R_squared={round(r_squared2,2)}  P_1hour={round(inverse_model(60*60, constant, exponent))}W"
    logger.info(f"\n{summary2}")

    # Tabulate answers

    table_data = [
        [x, f"{y:.0f}", f"{y_pred_inv:.0f}", f"{y_pred_cp:.0f}"]
        for x, y, (_, y_pred_cp), (_, y_pred_inv) in zip(
            raw_xy_data.keys(), raw_xy_data.values(), answer.values(), answer2.values()
        )
    ]
    headers = ["x (s)", "y (Raw)", "y_pred (Inverse Model)", "y_pred (CP Model)"]
    logger.info("\nComparison of Predicted Values:")
    logger.info("\n" + tabulate(table_data, headers=headers, tablefmt="simple"))

    # Define xdata for predictions

    xdata_test = [60, 120, 150, 180, 300, 420, 600, 720, 900, 1200, 1800, 2400, 3000, 3600, 4500, 5400, 7200, 10800, 14400]    
    row_titles = ["1min", "2min", "90s", "3min", "5min", "7min", "10min", "12min", "15min", "20min", "30min", "40min", "50min", "60min", "75min", "90min", "2hour", "3hour", "4hour"]

    y_pred_cp_model = [cp_w_prime_model(x, cp, w_prime) for x in xdata_test]
    y_pred_inverse_model = [inverse_model(x, constant, exponent) for x in xdata_test]

    # Generate a table for the predictions
    table_data_pred = [
        [title, x, f"{y_inv:.0f}", f"{y_cp:.0f}"]
        for title, x, y_inv, y_cp in zip(row_titles, xdata_test, y_pred_inverse_model, y_pred_cp_model)
    ]
    headers_pred = ["Row Title", "x (s)", "y_pred (Inverse Model)", "y_pred (CP Model)"]

    logger.info("\nPredicted Values for Specified xdata:")
    logger.info("\n" + tabulate(table_data_pred, headers=headers_pred, tablefmt="simple"))
    logger.info("\nModelling completed. Thank you.\n")

    # Plot answers

    xdata = list(raw_xy_data.keys())
    ydata = list(raw_xy_data.values())
    ydata_pred = [value[1] for value in answer.values()]
    ydata_pred2 = [value[1] for value in answer2.values()]

    plt.figure(figsize=(10, 6))
    plt.scatter(xdata, ydata, color='blue', label='Zwift 90-day data')
    plt.plot(xdata, ydata_pred, color='red', label=summary)
    plt.plot(xdata, ydata_pred2, color='green', label=summary2)
    plt.xlabel('Duration (s)')
    plt.ylabel('Power (W)')
    plt.title(f'{riders[rider_id].name}')
    plt.xticks(xdata)  
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()

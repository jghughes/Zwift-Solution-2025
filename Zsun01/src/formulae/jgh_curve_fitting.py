from typing import Dict, Tuple

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import curve_fit  # type: ignore
from sklearn.metrics import mean_squared_error, r2_score  # type: ignore

from jgh_power_curve_fit_models import cp_w_prime_model_numpy, decay_model_numpy

def do_curve_fit_with_cp_w_prime_model(raw_xy_data_cp: Dict[int, float]) -> Tuple[float, float, float, float, Dict[int, Tuple[float, float]]]:
    """
    Estimate critical power and anaerobic work capacity from duration and power data.
    Estimate cp_watts and w' using the formula xdata * y = cp_watts * xdata + w'. x_axis is time in seconds and y_axis is power in watts.
    cp_watts is the critical power, and w' is the anaerobic work capacity.

    Args:
        raw_xy_data_cp (Dict[int, float]): Dictionary where keys are durations (seconds) and values are power (watts).

    Returns:
        Tuple[float, float, float, Dict[int, Tuple[float, float]]]: The values of cp_watts and w', the R-squared value,
        and a dictionary combining the original data and predicted values.
    """
    # Convert keys and values of raw_xy_data_cp to NumPy arrays
    xdata: NDArray[np.float64] = np.array(list(raw_xy_data_cp.keys()), dtype=float)
    ydata: NDArray[np.float64] = np.array(list(raw_xy_data_cp.values()), dtype=float)

    # Perform linear regression between duration and work using curve_fit
    # In the model, xdata stands for duration, and xdata * y is work (duration * power)
    popt, _ = curve_fit(cp_w_prime_model_numpy, xdata, ydata, p0=[250, 10_000])

    # Extract the optimal parameters: cp_watts (critical power) and critical_power_w_prime(anaerobic work capacity)
    # cp_watts, critical_power_w_prime= popt

    # print(f"Fitted parameters: {popt}")

    cp_watts: float = float(popt[0])
    anaerobic_work_capacity: float = float(popt[1])

    # Use the cp_w_prime_model to calculate predicted y values based on the fitted parameters
    ydata_pred: NDArray[np.float64] = cp_w_prime_model_numpy(xdata, cp_watts, anaerobic_work_capacity)

    # Calculate the R-squared value
    r2: float = r2_score(ydata, ydata_pred)

    # # Calculate the root mean square error (RMSE)
    rmse_cp : float = np.sqrt(mean_squared_error(ydata, ydata_pred)) 


    # Recombine the original data and predicted values into a dictionary
    result: Dict[int, Tuple[float, float]] = {
        int(xdata[i]): (ydata[i], ydata_pred[i]) for i in range(len(xdata))
    }

    return cp_watts, anaerobic_work_capacity, r2, rmse_cp, result

def do_curve_fit_with_decay_model(raw_xy_data_cp: Dict[int, float]) -> Tuple[float, float, float, float, Dict[int, Tuple[float, float]]]:
    """
    Perform modeling using an inverse model y = coefficient_ftp * xdata^exponent_ftp, where exponent_ftp is typically negative (decay function).

    Args:
        raw_xy_data_cp (Dict[int, float]): Dictionary where keys are durations (seconds) and values are power (watts).

    Returns:
        Tuple[float, float, float, float, Dict[int, Tuple[float, float]]]: The values of coefficient_ftp and exponent_ftp, the R-squared value,
        the RMSE, and coefficient_ftp dictionary combining the original data and predicted values.
    """
    # Remove all elements from the dict raw_xy_data_cp where either the key is zero or the value is zero
    raw_xy_data_cp = {k: v for k, v in raw_xy_data_cp.items() if k != 0 and v != 0}

    # Raise an error if the dict contains less than 2 elements
    if len(raw_xy_data_cp) < 2:
        raise ValueError("The input dictionary must contain at least 2 elements.")

    # Convert keys and values of raw_xy_data_cp to NumPy arrays (intrinsically floats)
    xdata: NDArray[np.float64] = np.array(list(raw_xy_data_cp.keys()))
    ydata: NDArray[np.float64] = np.array(list(raw_xy_data_cp.values()))

    # Perform curve fitting using the inverse model
    popt, _ = curve_fit(decay_model_numpy, xdata, ydata)

    coefficient_ftp: float = float(popt[0])
    exponent_ftp: float = float(popt[1])

    # Calculate the predicted y values based on the fitted parameters
    ydata_pred = decay_model_numpy(xdata, coefficient_ftp, exponent_ftp)

    # Calculate the R-squared value
    r2: float = r2_score(ydata, ydata_pred)

    # Calculate the root mean square error (RMSE)
    rmse_cp: float = np.sqrt(mean_squared_error(ydata, ydata_pred))

    # Recombine the original xdata,y data and predicted y_data values into coefficient_ftp dictionary
    result: Dict[int, Tuple[float, float]] = {
        int(xdata[i]): (ydata[i], ydata_pred[i]) for i in range(len(xdata))
    }

    return coefficient_ftp, exponent_ftp, r2, rmse_cp, result


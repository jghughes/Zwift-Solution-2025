from typing import List, Tuple, Dict, Union
import numpy as np
from numpy.typing import NDArray
from scipy.optimize import curve_fit


from zwiftrider_related_items import ZwiftRiderCriticalPowerItem

def map_dict_of_duration_and_power_to_xy_lists(cp_interval_data: Dict[int, float]) -> Tuple[List[float], List[float]]:
    """
    Map best-90 day power intervals to separate lists of duration and power.

    Args:
        cp_interval_data (Dict[int, float]): Dictionary of key=interval duration (sec) and value=power (W).

    Returns:
        Tuple[List[float], List[float]]: Lists of durations (for x-axis) and power (for y-axis).
    """
    # Strip non-zero and positive datapoints
    non_zero_dict = {duration: power for duration, power in cp_interval_data.items() if power > 0 and duration > 0}

    # Convert keys to float
    duration_seconds_x_axis: List[float] = list(map(float, non_zero_dict.keys()))
    power_watts_y_axis: List[float] = list(non_zero_dict.values())

    return duration_seconds_x_axis, power_watts_y_axis

def map_zwiftridercriticalpoweritem_to_xy_lists(rider_cp_item: ZwiftRiderCriticalPowerItem) -> Tuple[List[float], List[float]]:

     dict_of_duration_vs_power = rider_cp_item.map_to_int_float_equivalent()

     xdata, ydata = map_dict_of_duration_and_power_to_xy_lists(dict_of_duration_vs_power)

     return xdata, ydata

def inverse_model_formula(x_axis_data: Union[NDArray[np.float64], List[float]], constant: float, exponent: float
) -> NDArray[np.float64]:
    """
    By inputting x_axis_data (durations in seconds) and two coefficients, a constant
    and an exponent, we can calculate dependent y_axis_data (power values in watts).
    This is simple inverse-time formula is very close to the "power" formula that 
    gives excellent best-fit results in Excel. Empirically, this gives us a good 
    fit for Zwift 90-day power data.

    Args:
        x_axis_data (Union[NDArray[np.float64], List[float]]) : Input array or list of durations (seconds).
        constant     (float)                                  : Coefficient for the model.
        exponent     (float)                                  : Coefficient for the model.

    Returns:
        NDArray[np.float64]                                   : Computed power values (watts) for the given durations.
    """
    # Ensure x_axis_datapoints is a NumPy array
    x_axis_data = np.array(x_axis_data, dtype=np.float64)
    
    # Compute the exponential model
    y_axis_data = constant * x_axis_data ** exponent

    return y_axis_data

def linear_model(x, c, w):
    return c * x + w

def solve_for_critical_power_and_anaerobic_wok_capacity(x_axis_data: List[float], y_axis_data: List[float]) -> Tuple[float, float]:
    """
    Solve for c (critical power) and w' (anaerobic capacity) using the formula x * y = c * x + w.

    Args:
        x (List[float]): The list of x values (time in seconds).
        y (List[float]): The list of y values (power in watts).

    Returns:
        Tuple[float, float, float]: The values of c, w, and the R-squared value.
    """
    x = np.array(x_axis_data)
    y = np.array(y_axis_data)
    
    # Perform linear regression using curve_fit
    popt, _ = curve_fit(linear_model, x, x * y)
    c, w = popt

    return c, w

# def calculate_coefficients_of_best_fit_curve(input_xdata: List[float], input_ydata: List[float]) -> Tuple[float, float]:

#     def best_fit_model(x_value: np.ndarray, a: float, b: float) -> np.ndarray:
#         # this is very similar to the simple power formula that excel uses.
#         # The exponent, b, is negative, i.e. this is inverse power formula
#         # empirically this gives us a good fit for zwift 90-day power data 
#         y_value = a * x_value ** b
#         return y_value

#     # cast input data to numpy arrays
#     xdata = np.array(input_xdata)
#     ydata = np.array(input_ydata)

#     # Filter data for the duration range in a window from 60 to 2400 seconds for nice fit
#     mask = (xdata >= 60) & (xdata <= 2400)
#     xdata_filtered = xdata[mask]
#     ydata_filtered = ydata[mask]

#     # Fit the exponential model to the filtered data - this is the best fit for our purposes
#     popt_filtered, pcov_filtered = curve_fit(inverse_model_formula, xdata_filtered, ydata_filtered)

#     # popt_filtered is a tuple of the coefficients a and b

#     return popt_filtered


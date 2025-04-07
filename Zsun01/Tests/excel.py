from typing import List, Tuple, Dict
from venv import logger
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score
from handy_utilities import get_all_zwiftriders, get_all_zwiftriders_cp_data
from zwiftrider_related_items import ZwiftRiderItem, ZwiftRiderCriticalPowerItem, RiderExertionItem, RiderAnswerItem
import logging
from jgh_logging import jgh_configure_logging
jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)

# Suppress matplotlib font matching logs - NB if you don't do this matplotlib will puke all over your console
logging.getLogger('matplotlib').setLevel(logging.WARNING)

barryb ='5490373' # barryb
johnh ='58160' # johnh
lynseys ='383480' # lynseys
joshn ='2508033' # joshn
richardm ='1193' # richardm
markb ='5530045' # markb
rider_id = markb  # Change this to the desired rider ID
riders = get_all_zwiftriders()
metrics = get_all_zwiftriders_cp_data()

def cleanup_cp_interval_data(cp_interval_data: Dict[int, float]) -> Tuple[List[float], List[float]]:
    """
    Filter out any cp_interval_data datapoints with value <= 0.

    Args:
        cp_interval_data (Dict[int, float]): Dictionary of power data for one hour.

    Returns:
        Tuple[List[float], List[float]]: Filtered keys and values as lists of floats.
    """
    # Strip non-zero and positive datapoints
    non_zero_dict = {duration: power for duration, power in cp_interval_data.items() if power > 0 and duration > 0}

    # Convert keys to float
    duration_seconds_x_axis: List[float] = list(map(float, non_zero_dict.keys()))
    power_watts_y_axis: List[float] = list(non_zero_dict.values())

    return duration_seconds_x_axis, power_watts_y_axis

def exponential_model(x: np.ndarray, a: float, b: float) -> np.ndarray:
    # this is the simple power formula that excel uses, where b is negative, i.e. inverse power formula
    y = a * x ** b
    return y

def hyperbolic_model(x: np.ndarray, w_prime: float, crit_power: float) -> np.ndarray:
    y = (w_prime + crit_power * x) / x
    return y

def log_linear_model(x: np.ndarray, a: float, b: float) -> np.ndarray:
    # this is the log-linear model
    y = a * np.log(x) + b
    return y


xdata, ydata = cleanup_cp_interval_data(metrics[rider_id].map_to_int_float_equivalent())
xdata = np.array(xdata)
ydata = np.array(ydata)

# Filter data for the duration range from 180 to 300 seconds
mask = (xdata >= 60) & (xdata <= 2400)
xdata_filtered = xdata[mask]
ydata_filtered = ydata[mask]

# Fit the exponential model to the filtered data
popt_filtered, pcov_filtered = curve_fit(exponential_model, xdata_filtered, ydata_filtered)
y_pred_filtered = exponential_model(xdata_filtered, *popt_filtered)
r_squared_filtered = r2_score(ydata_filtered, y_pred_filtered)
logger.info(f"\nExponential model (filtered): {riders[rider_id].name} popt_filtered: {popt_filtered} R squared: {r_squared_filtered}")

# Fit the exponential model to the full data
popt01, pcov = curve_fit(exponential_model, xdata, ydata)  # popt01 is a tuple of the fitted parameters
y_pred01 = exponential_model(xdata, *popt01)
r_squared01 = r2_score(ydata, y_pred01)
logger.info(f"\nExponential model: {riders[rider_id].name} popt01: {popt01} R squared: {r_squared01}")

# hyperbolic_model
popt02, pcov = curve_fit(hyperbolic_model, xdata, ydata)
y_pred02 = hyperbolic_model(xdata, *popt02)
r_squared02 = r2_score(ydata, y_pred02)
logger.info(f"\nHyperbolic model: {riders[rider_id].name} popt02: {popt02} R squared: {r_squared02}")

# log_linear_model
popt04, pcov = curve_fit(log_linear_model, xdata, ydata)
y_pred04 = log_linear_model(xdata, *popt04)
r_squared04 = r2_score(ydata, y_pred04)
logger.info(f"\nLog-linear model: {riders[rider_id].name} popt04: {popt04} R squared: {r_squared04}")

plt.figure(figsize=(10, 6))
plt.scatter(xdata, ydata, color='blue', label='raw data')
plt.plot(xdata, y_pred01, color='red', label=f'exponential curve (y = a * x ** b) where a: {round(popt01[0])}, b:{round(popt01[1], 4)}, R_squared: {round(r_squared01, 2)}')
plt.plot(xdata, y_pred02, color='green', label=f'hyperbolic curve (y = (w_prime + crit_power*x)/x) where w_prime: {round(popt02[0])}, crit_power:{round(popt02[1], 4)}, R_squared: {round(r_squared02, 2)}')
plt.plot(xdata, y_pred04, color='purple', label=f'log-linear curve (y = a * log(x) + b) where a: {round(popt04[0])}, b:{round(popt04[1], 4)}, R_squared: {round(r_squared04, 2)}')
plt.plot(xdata_filtered, y_pred_filtered, color='orange', label=f'exponential curve (filtered) where a: {round(popt_filtered[0])}, b:{round(popt_filtered[1], 4)}, R_squared: {round(r_squared_filtered, 2)}')
plt.xlabel('Duration (s)')
plt.ylabel('Power (W)')
plt.title(f'{riders[rider_id].name} - 90-day power best fit curves')
plt.xticks(xdata)  
plt.legend()
plt.show()

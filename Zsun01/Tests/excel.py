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
    # this is the hyperbolic power formula that excel uses
    y = (w_prime + crit_power * x) / x
    return y

rider_id = johnh

xdata, ydata = cleanup_cp_interval_data(metrics[rider_id].map_to_int_float_equivalent())
xdata = np.array(xdata)  # Ensure xdata is a NumPy array
ydata = np.array(ydata)  # Ensure ydata is a NumPy array

# exponential_model
popt01, pcov = curve_fit(exponential_model, xdata, ydata)  # popt01 is a tuple of the fitted parameters
y_pred01 = exponential_model(xdata, *popt01)
r_squared01 = r2_score(ydata, y_pred01)
logger.info(f"\nExponential model: {riders[rider_id].name} popt01: {popt01} R squared: {r_squared01}")

# hyperbolic_model
popt02, pcov = curve_fit(hyperbolic_model, xdata, ydata)
y_pred02 = hyperbolic_model(xdata, *popt02)
r_squared02 = r2_score(ydata, y_pred02)
logger.info(f"\nHyperbolic model: {riders[rider_id].name} popt02: {popt02}\nR squared: {r_squared02}")

plt.figure(figsize=(10, 6))
plt.scatter(xdata, ydata, color='blue', label='raw data')
plt.plot(xdata, y_pred01, color='red', label=f'exponential curve (y = a * x ** b) where a: {round(popt01[0])}, b:{round(popt01[1], 4)}, R_squared: {round(r_squared01, 2)}')
plt.plot(xdata, y_pred02, color='green', label=f'hyperbolic curve (y = (w_prime + crit_power*x)/x) where w_prime: {round(popt02[0])}, crit_power:{round(popt02[1], 4)}, R_squared: {round(r_squared02, 2)}')
plt.xlabel('Duration (s)')
plt.ylabel('Power (W)')
plt.title(f'{riders[rider_id].name} - 90-day power best fit curves')
plt.xticks(xdata)  
plt.legend()
plt.show()

from typing import List, Tuple, Dict
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score

def model_func(x: float, a: float, b: float) -> float:
    return a * pow(x, b)

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

zftp_duration_power_metrics_joshn: Dict[int, float] = {
    5: 810.0, 15: 781.0, 30: 679.0, 60: 475.0, 180: 338.0, 300: 320.0, 600: 307.0, 720: 298.0, 900: 283.0, 1200: 279.0, 1800: 271.0, 2400: 261.0
}
zftp_duration_power_metrics_jgh: Dict[int, float] = {
    5: 546.0, 15: 434.0, 30: 425.0, 60: 348.0, 180: 293.0, 300: 292.0, 600: 268.0, 720: 264.0, 900: 255.0, 1200: 254.0, 1800: 252.0, 2400: 244.0
}

xdata, ydata = cleanup_cp_interval_data(zftp_duration_power_metrics_joshn)

# plt.plot(xdata, ydata, 'b-', label='zftp x=duration (s) y=power (W)')

# Create scatter plot
plt.figure(figsize=(10, 6))
plt.scatter(xdata, ydata, color='blue', label='Data Points')

# Add labels and title
plt.xlabel('Duration (s)')
plt.ylabel('CP Power (W)')
plt.title('Zwift Durations and CP Powers')
plt.xticks(xdata)  # Ensure all durations are shown on the x-axis
plt.legend()
plt.show()



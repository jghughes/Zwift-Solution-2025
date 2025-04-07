import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score
from typing import List, Tuple

def model_func(x, c, w):
    y = (w/x) + c
    return y

# def model_func(y, w, c):
#     return w / (y - c)

def non_linear_power_time(x: List[float], y: List[float]) -> Tuple[float, float, float]:
    """
    Solve for w and c using the formula x = w / (y - c) and calculate the R-squared value.

    Args:
        x (List[float]): The list of x values (time in seconds).
        y (List[float]): The list of y values (power in watts).

    Returns:
        Tuple[float, float, float]: The values of w, c, and the R-squared value.
    """
    x = np.array(x)
    y = np.array(y)
    
    # Perform non-linear regression using curve_fit
    popt, _ = curve_fit(model_func, x, y)
    w, c = popt
    
    # Calculate the predicted x values
    x_pred = model_func(x,c,w)
    
    # Calculate the R-squared value
    r2 = r2_score(x, x_pred)
    
    # Filter data for plotting range from x=15 to x=2400
    mask = (x >= 15) & (x <= 2400)
    x_filtered = x[mask]
    y_filtered = y[mask]
    x_pred_filtered = x_pred[mask]
    
    # Plot the original data points and the best fit line
    plt.figure(figsize=(10, 6))
    plt.scatter(x_filtered, y_filtered, color='blue', label='Data Points')
    plt.plot(x_filtered, x_pred_filtered, color='red', label='Best Fit Line')
    plt.xlabel('Time (s)')
    plt.ylabel('Power (W)')
    plt.title('Non-Linear Regression: x = w / (y - c) or alternatively y=(w/x) + c')
    plt.legend()
    plt.show()
    
    return w, c, r2

# Data
x = [5, 15, 30, 60, 180, 300, 600, 720, 900, 1200, 1800, 2400]
y = [546.0, 434.0, 425.0, 348.0, 293.0, 292.0, 268.0, 264.0, 255.0, 254.0, 252.0, 244.0]

# Solve for w and c and calculate R-squared
w, c, r2 = non_linear_power_time(x, y)

print(f"w: {w:.2f}, c: {c:.2f}, R-squared: {r2:.4f}")

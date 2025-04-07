
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
from scipy.optimize import curve_fit
from typing import List, Tuple

def linear_model(x, c, w):
    return c * x + w

def linear_work_time(x: List[float], y: List[float]) -> Tuple[float, float, float]:
    """
    Solve for c and w using the formula x * y = c * x + w and calculate the R-squared value.

    Args:
        x (List[float]): The list of x values (time in seconds).
        y (List[float]): The list of y values (power in watts).

    Returns:
        Tuple[float, float, float]: The values of c, w, and the R-squared value.
    """
    x = np.array(x)
    y = np.array(y)
    
    # Perform linear regression using curve_fit
    popt, _ = curve_fit(linear_model, x, x * y)
    c, w = popt
    
    # Calculate the predicted y values
    y_pred = (c * x + w) / x
    
    # Calculate the R-squared value
    r2 = r2_score(y, y_pred)
    
    # Filter data for plotting range from x=15 to x=2400
    mask = (x >= 15) & (x <= 2400)
    x_filtered = x[mask]
    y_filtered = y[mask]
    y_pred_filtered = y_pred[mask]
    
    # Plot the original data points and the best fit line
    plt.figure(figsize=(10, 6))
    plt.scatter(x_filtered, y_filtered, color='blue', label='Data Points')
    plt.plot(x_filtered, y_pred_filtered, color='red', label='Best Fit Line')
    plt.xlabel('Time (s)')
    plt.ylabel('Power (W)')
    plt.title('Linear Regression: x * y = c * x + w')
    plt.legend()
    plt.show()
    
    return c, w, r2

# Data
x = [5, 15, 30, 60, 180, 300, 600, 720, 900, 1200, 1800, 2400]
y = [546.0, 434.0, 425.0, 348.0, 293.0, 292.0, 268.0, 264.0, 255.0, 254.0, 252.0, 244.0]

# Solve for c and w and calculate R-squared
c, w, r2 = linear_work_time(x, y)

print(f"c: {c:.2f}, w: {w:.2f}, R-squared: {r2:.4f}")

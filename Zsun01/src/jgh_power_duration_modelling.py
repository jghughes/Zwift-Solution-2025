import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
from scipy.optimize import curve_fit
from typing import List, Tuple


def linear_model(x, a, b):
    return a * x + b

def cp_w_prime_model(x, a, b ):
    if x.any() == 0:
        raise ValueError("x cannot be zero for linear inverse model")
    return (a * x + b) / x

def inverse_model(x, a, b):
    # b will/must be negative because it is a decay function
    return a * x ** b

def do_modelling_with_cp_w_prime_model(x: List[float], y: List[float]) -> Tuple[float, float, float, List[float], List[float], List[float]]:
    """
    Estimate critical power and anearobic work capacity,from duration and power data.
    Estimate cp and w' using the formula x * y = cp * x + w'. x_axis is time in seconds and y_axis is power in watts.
    cp is the critical power, and w' is the anearobic work capacity.

    Args:
        x (List[float]): The list of x values (time in seconds).
        y (List[float]): The list of y values (power in watts).

    Returns:
        Tuple[float, float, float, List[float]]: The values of cp and w'. The R-squared value, and the predicted y values
        based on a best fit curve
    """
    xdata = np.array(x)
    ydata = np.array(y)
    # mask = (xdata >= 60) & (xdata <= 2400) # deal out distracting data for our purposes
    # xdata = xdata[mask]
    # ydata = ydata[mask]

    # Perform linear regression between duration and work using curve_fit.
    # In the the model, x stands for duration, and x*y is work, i.e. the product of duration and power.

    popt, _ = curve_fit(linear_model, xdata, xdata * ydata)

    # curve_fit returns the optimal values for the parameters c and w, where c is the slope and w is the intercept. 
    # The slope represents the change in power with respect to time, and the intercept represents the initial power output.
    # In the literature, slope is w_prime and intercept is cp. w_prime is anearobic work capacity and cp is critical power.
    
    cp, w_prime = popt

    # use rational function model to calculate predicted y values based on the fitted parameters
    ydata_pred = cp_w_prime_model(xdata, cp, w_prime)

    # Calculate the R-squared value
    r2 = r2_score(y, ydata_pred)

    return cp, w_prime, r2, xdata, ydata, ydata_pred

def do_modelling_with_inverse_model(x: List[float], y: List[float]) -> Tuple[float, float, float, List[float], List[float], List[float]]:
    """
    Perform modeling using an inverse model y = a * x^b, where b is typically negative (decay function).
    Args:
        x (List[float]): The list of x values (time in seconds).
        y (List[float]): The list of y values (power in watts).
    Returns:
        Tuple[float, float, float, List[float]]: The values of a and b, the R-squared value, and the predicted y values
        based on the best fit curve.
    """
    xdata = np.array(x)
    ydata = np.array(y)
    # mask = (xdata >= 60) & (xdata <= 2400) # deal out distracting data for our purposes
    # xdata = xdata[mask]
    # ydata = ydata[mask]
    
    # Perform curve fitting using the inverse model
    popt, _ = curve_fit(inverse_model, xdata, ydata)
    a, b = popt  # a is the coefficient, b is the exponent
    
    # Calculate the predicted y values based on the fitted parameters
    ydata_pred = inverse_model(xdata, a, b)
    
    # Calculate the R-squared value
    r2 = r2_score(ydata, ydata_pred)
    
    return a, b, r2, xdata, ydata, ydata_pred

# Example usage of the functions
def main():
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    from handy_utilities import get_all_zwiftriders, get_all_zwiftriders_cp_data
    from critical_power_metrics import map_zwiftridercriticalpoweritem_to_xy_lists
    import matplotlib.pyplot as plt
    logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

    barryb ='5490373' 
    johnh ='58160'
    lynseys ='383480'
    joshn ='2508033'
    richardm ='1193'
    markb ='5530045'

    riders = get_all_zwiftriders()
    riders_cp_data = get_all_zwiftriders_cp_data()

    rider_id = johnh
    zwift_xdata, zwift_ydata = map_zwiftridercriticalpoweritem_to_xy_lists(riders_cp_data[rider_id])

    cp, w, r_squared00, xdata00, ydata00, ydata_pred00  = do_modelling_with_cp_w_prime_model(zwift_xdata, zwift_ydata)
    summary00 = f"Critical power model: {riders[rider_id].name} CP: {round(cp,4)} Watts, W_prime: {round(w)} Joules, R_squared: {round(r_squared00,2)}"
    logger.info(summary00)

    constant, exponent, r_squared01, xdata01, ydata01, ydata_pred01 = do_modelling_with_inverse_model(zwift_xdata, zwift_ydata)
    summary01 = f"Inverse model: {riders[rider_id].name} const: {round(constant,4)}, exponent: {round(exponent)}, R_squared: {round(r_squared01,2)}"
    logger.info(summary01)

    # plot everything
    plt.figure(figsize=(10, 6))
    plt.scatter(zwift_xdata, zwift_ydata, color='blue', label='Zwift data')
    plt.plot(zwift_xdata, ydata_pred00, color='red', label=summary00)
    plt.plot(zwift_xdata, ydata_pred01, color='green', label=summary01)
    plt.xlabel('Duration (s)')
    plt.ylabel('Power (W)')
    plt.title(f'{riders[rider_id].name} - Zwift power data modelling')
    plt.xticks(zwift_xdata)  
    plt.legend()
    plt.show()

    # tabulate ydata compared to ydata_pred
    print("Critical power model: xdata vs ydata vs ydata_pred:")
    for i in range(len(xdata00)):
        print(f"{xdata00[i]:.2f} vs {ydata00[i]:.2f} vs {ydata_pred00[i]:.2f}")
     
    print("Inverse model: xdata vs ydata vs ydata_pred:")
    for i in range(len(xdata01)):
        print(f"{xdata01[i]:.2f} vs {ydata01[i]:.2f} vs {ydata_pred01[i]:.2f}")
     
if __name__ == "__main__":
    main()

import numpy as np
from sklearn.metrics import r2_score
from scipy.optimize import curve_fit
from typing import Tuple, Dict
from zwiftrider_related_items import ZwiftRiderCriticalPowerItem



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

    # Extract the optimal parameters: cp (critical power) and awc (anaerobic work capacity)
    # cp, awc = popt

    cp: float = float(popt[0])
    awc: float = float(popt[1])

    # Use the cp_w_prime_model to calculate predicted y values based on the fitted parameters
    ydata_pred: np.ndarray = cp_w_prime_model(xdata, cp, awc)

    # Calculate the R-squared value
    r2: float = r2_score(ydata, ydata_pred)

    # Recombine the original data and predicted values into a dictionary
    result: Dict[int, Tuple[float, float]] = {
        int(xdata[i]): (ydata[i], ydata_pred[i]) for i in range(len(xdata))
    }

    return cp, awc, r2, result

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

def generate_model_fitted_zwiftrider_cp_metrics(zwiftriders_zwift_cp_data: Dict[str, ZwiftRiderCriticalPowerItem]
) -> Dict[str, ZwiftRiderCriticalPowerItem]:
    """
    Perform model fitting on ZwiftRiderCriticalPowerItem instances to calculate critical power (CP), 
    anaerobic work capacity (W'), and parameters for the inverse model, and then populate a neew item
    the item accoridng to the fitted parameters of the inverse model. The intended purpose of this 
    function is to import the database of ZSun riders and their CP data obtained from Zwiftor ZwiftPower
    and then to generate a new database of modeled CP data for each rider. This new database serves 
    as a benchmark for comparing exertion and work rate of riders in a paceline with what they are 
    capable of achieving in a solo effort.

    Args:
        zwiftriders_zwift_cp_data (Dict[str, ZwiftRiderCriticalPowerItem]): 
            A dictionary where the key is the rider's Zwift ID (as a string) and the value is a 
            ZwiftRiderCriticalPowerItem instance containing critical power data.

    Returns:
        Dict[str, ZwiftRiderCriticalPowerItem]: 
            A new dictionary of ZwiftRiderCriticalPowerItem instances with calculated CP, W', 
            inverse model parameters, and imported predicted critical power data.
    """

    # Create a new dictionary to store the modeled data
    modeled_data : Dict[str, ZwiftRiderCriticalPowerItem] = {}

    # Iterate through each ZwiftRiderCriticalPowerItem instance in the input dictionary
    for rider_id, rider_cp_item in zwiftriders_zwift_cp_data.items():
        # Create a copy of the current rider_cp_item to avoid modifying the original
        modeled_rider_cp_item = ZwiftRiderCriticalPowerItem(
            zwiftid=rider_cp_item.zwiftid,
            name=rider_cp_item.name,
            cp_5=rider_cp_item.cp_5,
            cp_15=rider_cp_item.cp_15,
            cp_30=rider_cp_item.cp_30,
            cp_1_min=rider_cp_item.cp_1_min,
            cp_2_min=rider_cp_item.cp_2_min,
            cp_90=rider_cp_item.cp_90,
            cp_3_min=rider_cp_item.cp_3_min,
            cp_5_min=rider_cp_item.cp_5_min,
            cp_7_min=rider_cp_item.cp_7_min,
            cp_10_min=rider_cp_item.cp_10_min,
            cp_12_min=rider_cp_item.cp_12_min,
            cp_15_min=rider_cp_item.cp_15_min,
            cp_20_min=rider_cp_item.cp_20_min,
            cp_30_min=rider_cp_item.cp_30_min,
            cp_40_min=rider_cp_item.cp_40_min,
            cp_50_min=rider_cp_item.cp_50_min,
            cp_1_hour=rider_cp_item.cp_1_hour,
            cp_1h15=rider_cp_item.cp_1h15,
            cp_1h30=rider_cp_item.cp_1h30,
            cp_2_hour=rider_cp_item.cp_2_hour,
            cp_3_hour=rider_cp_item.cp_3_hour,
            cp_4_hour=rider_cp_item.cp_4_hour,
            cp=rider_cp_item.cp,
            awc=rider_cp_item.awc,
            inverse_const=rider_cp_item.inverse_const,
            inverse_exp=rider_cp_item.inverse_exp,
        )

        # Perform modeling with CP-W' model
        rider_cp_interval_data: Dict[int, float] = rider_cp_item.export_cp_data_for_best_fitting()
        cp, awc, _, _ = do_modelling_with_cp_w_prime_model(rider_cp_interval_data)
        modeled_rider_cp_item.cp = cp
        modeled_rider_cp_item.awc = awc

        # Perform modeling with inverse model
        constant, exponent, _, _ = do_modelling_with_inverse_model(rider_cp_interval_data)
        modeled_rider_cp_item.inverse_const = constant
        modeled_rider_cp_item.inverse_exp = exponent

        # Calculate the predicted y values based on the fitted parameters from the inverse model
        x_ordinates = ZwiftRiderCriticalPowerItem.export_x_ordinates()
        y_ordinates_inverse_model = [inverse_model(x_ordinate, constant, exponent) for x_ordinate in x_ordinates]

        # Zip the x_ordinates and y_pred_inverse_model together into a dict[int, float]
        generated_cp_data = dict(zip(x_ordinates, y_ordinates_inverse_model))

        # Add the y_pred_inverse_model_dict to the modeled_rider_cp_item
        modeled_rider_cp_item.import_cp_data(generated_cp_data)

        # Add the modeled rider_cp_item to the new dictionary
        modeled_data[rider_id] = modeled_rider_cp_item

    return modeled_data

# Example usage of the functions
def main():
    pass
if __name__ == "__main__":
    main()

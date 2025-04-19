import numpy as np
from numpy.typing import NDArray
from sklearn.metrics import r2_score, mean_squared_error
from scipy.optimize import curve_fit
from typing import Tuple, Dict
from zwiftrider_related_items import ZwiftRiderCriticalPowerItem


def linear_model(x : float, a : float, b: float):
    return a * x + b

def inverse_model(x: float, a: float, b: float) -> float:
    """
    A decay function that computes a * (1 / (x ** b)).
    Guards against division by zero by checking if x is zero.

    Args:
        x (float): The input value (must be non-zero).
        a (float): Coefficient.
        b (float): Exponent.

    Returns:
        float: The computed value of the decay function.

    Raises:
        ValueError: If x is zero, to avoid division by zero.
    """
    if x == 0:
        raise ValueError("Input x must be non-zero to avoid division by zero.")
    return a * (1 / (x ** b))

def inverse_model_numpy(x: NDArray[np.float64], a: float, b: float) -> NDArray[np.float64]:
    """
    A decay function that computes a * (1 / (x ** b)) for NumPy arrays.
    Handles zero values in the array by replacing them with a small epsilon value.

    Args:
        x (NDArray[np.float64]): The input array.
        a (float): Coefficient.
        b (float): Exponent.

    Returns:
        NDArray[np.float64]: The computed values of the decay function.
    """
    epsilon = 1e-10  # A small value to replace zeros
    x_safe = np.where(x == 0, epsilon, x)  # Replace zeros with epsilon
    return a * (1 / (x_safe ** b))

def inverse_model_numpy_masked(x: NDArray[np.float64], a: float, b: float) -> NDArray[np.float64]:
    """
    A decay function that computes a * (1 / (x ** b)) for NumPy arrays.
    Handles zero values in the array by masking them and computing only for non-zero values.

    Args:
        x (NDArray[np.float64]): The input array.
        a (float): Coefficient.
        b (float): Exponent.

    Returns:
        NDArray[np.float64]: The computed values of the decay function.
    """
    mask = x != 0  # Create a mask for non-zero values
    result = np.zeros_like(x, dtype=np.float64)  # Initialize result array with zeros
    result[mask] = a * (1 / (x[mask] ** b))  # Compute only for non-zero values
    return result

def cp_w_prime_model_numpy(x: NDArray[np.float64], a: float, b: float) -> NDArray[np.float64]:
    """
    Compute power as a function of CP and W' using the formula (a * x + b) / x.

    Args:
        x (float): Duration (seconds). Must be non-zero.
        a (float): Coefficient for the linear term, critical_power.
        b (float): Constant term, W'

    Returns:
        float: Computed power value.

    Raises:
        ValueError: If x is zero, to avoid division by zero.
    """
    return (a * x + b) / x

def do_modelling_with_cp_w_prime_model(raw_xy_data: Dict[int, float]) -> Tuple[float, float, float, float, Dict[int, Tuple[float, float]]]:
    """
    Estimate critical power and anaerobic work capacity from duration and power data.
    Estimate critical_power and w' using the formula x * y = critical_power * x + w'. x_axis is time in seconds and y_axis is power in watts.
    critical_power is the critical power, and w' is the anaerobic work capacity.

    Args:
        raw_xy_data (Dict[int, float]): Dictionary where keys are durations (seconds) and values are power (watts).

    Returns:
        Tuple[float, float, float, Dict[int, Tuple[float, float]]]: The values of critical_power and w', the R-squared value,
        and a dictionary combining the original data and predicted values.
    """
    # Convert keys and values of raw_xy_data to NumPy arrays
    xdata: np.ndarray = np.array(list(raw_xy_data.keys()), dtype=float)
    ydata: np.ndarray = np.array(list(raw_xy_data.values()), dtype=float)

    # Perform linear regression between duration and work using curve_fit
    # In the model, x stands for duration, and x * y is work (duration * power)
    popt, _ = curve_fit(linear_model, xdata, xdata * ydata)

    # Extract the optimal parameters: critical_power (critical power) and anaerobic_work_capacity (anaerobic work capacity)
    # critical_power, anaerobic_work_capacity = popt

    critical_power: float = float(popt[0])
    anaerobic_work_capacity: float = float(popt[1])

    # Use the cp_w_prime_model to calculate predicted y values based on the fitted parameters
    ydata_pred: np.ndarray = cp_w_prime_model(xdata, critical_power, anaerobic_work_capacity)

    # Calculate the R-squared value
    r2: float = r2_score(ydata, ydata_pred)

    # # Calculate the root mean square error (RMSE)
    rmse : float = np.sqrt(mean_squared_error(ydata, ydata_pred)) 


    # Recombine the original data and predicted values into a dictionary
    result: Dict[int, Tuple[float, float]] = {
        int(xdata[i]): (ydata[i], ydata_pred[i]) for i in range(len(xdata))
    }

    return critical_power, anaerobic_work_capacity, r2, rmse, result

def do_modelling_with_inverse_model(raw_xy_data: Dict[int, float]) -> Tuple[float, float, float, float, Dict[int, Tuple[float, float]]]:
    """
    Perform modeling using an inverse model y = a * x^b, where b is typically negative (decay function).

    Args:
        raw_xy_data (Dict[int, float]): Dictionary where keys are durations (seconds) and values are power (watts).

    Returns:
        Tuple[float, float, float, float, Dict[int, Tuple[float, float]]]: The values of a and b, the R-squared value,
        the RMSE, and a dictionary combining the original data and predicted values.
    """
    # Remove all elements from the dict raw_xy_data where either the key is zero or the value is zero
    raw_xy_data = {k: v for k, v in raw_xy_data.items() if k != 0 and v != 0}

    # Raise an error if the dict contains less than 2 elements
    if len(raw_xy_data) < 2:
        raise ValueError("The input dictionary must contain at least 2 elements.")

    # Convert keys and values of raw_xy_data to NumPy arrays (intrinsically floats)
    xdata: NDArray[np.float64] = np.array(list(raw_xy_data.keys()))
    ydata: NDArray[np.float64] = np.array(list(raw_xy_data.values()))

    # Perform curve fitting using the inverse model
    popt, _ = curve_fit(inverse_model_numpy, xdata, ydata)
    a , b = popt  # a is the coefficient, b is the exponent

    # Calculate the predicted y values based on the fitted parameters
    ydata_pred = inverse_model_numpy(xdata, a, b)

    # Calculate the R-squared value
    r2: float = r2_score(ydata, ydata_pred)

    # Calculate the root mean square error (RMSE)
    rmse: float = np.sqrt(mean_squared_error(ydata, ydata_pred))

    # Recombine the original x,y data and predicted y_data values into a dictionary
    result: Dict[int, Tuple[float, float]] = {
        int(xdata[i]): (ydata[i], ydata_pred[i]) for i in range(len(xdata))
    }

    return a, b, r2, rmse, result

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
            cp_1=rider_cp_item.cp_1,
            cp_2=rider_cp_item.cp_2,
            cp_3=rider_cp_item.cp_3,
            cp_4=rider_cp_item.cp_4,
            cp_5=rider_cp_item.cp_5,
            cp_6=rider_cp_item.cp_6,
            cp_7=rider_cp_item.cp_7,
            cp_8=rider_cp_item.cp_8,
            cp_9=rider_cp_item.cp_9,
            cp_10=rider_cp_item.cp_10,
            cp_11=rider_cp_item.cp_11,
            cp_12=rider_cp_item.cp_12,
            cp_13=rider_cp_item.cp_13,
            cp_14=rider_cp_item.cp_14,
            cp_15=rider_cp_item.cp_15,
            cp_16=rider_cp_item.cp_16,
            cp_17=rider_cp_item.cp_17,
            cp_18=rider_cp_item.cp_18,
            cp_19=rider_cp_item.cp_19,
            cp_20=rider_cp_item.cp_20,
            cp_21=rider_cp_item.cp_21,
            cp_22=rider_cp_item.cp_22,
            cp_23=rider_cp_item.cp_23,
            cp_24=rider_cp_item.cp_24,
            cp_25=rider_cp_item.cp_25,
            cp_26=rider_cp_item.cp_26,
            cp_27=rider_cp_item.cp_27,
            cp_28=rider_cp_item.cp_28,
            cp_29=rider_cp_item.cp_29,
            cp_30=rider_cp_item.cp_30,
            cp_35=rider_cp_item.cp_35,
            cp_40=rider_cp_item.cp_40,
            cp_45=rider_cp_item.cp_45,
            cp_50=rider_cp_item.cp_50,
            cp_55=rider_cp_item.cp_55,
            cp_60=rider_cp_item.cp_60,
            cp_70=rider_cp_item.cp_70,
            cp_80=rider_cp_item.cp_80,
            cp_90=rider_cp_item.cp_90,
            cp_100=rider_cp_item.cp_100,
            cp_110=rider_cp_item.cp_110,
            cp_120=rider_cp_item.cp_120,
            cp_150=rider_cp_item.cp_150,
            cp_180=rider_cp_item.cp_180,
            cp_210=rider_cp_item.cp_210,
            cp_240=rider_cp_item.cp_240,
            cp_270=rider_cp_item.cp_270,
            cp_300=rider_cp_item.cp_300,
            cp_330=rider_cp_item.cp_330,
            cp_360=rider_cp_item.cp_360,
            cp_390=rider_cp_item.cp_390,
            cp_420=rider_cp_item.cp_420,
            cp_450=rider_cp_item.cp_450,
            cp_480=rider_cp_item.cp_480,
            cp_510=rider_cp_item.cp_510,
            cp_540=rider_cp_item.cp_540,
            cp_570=rider_cp_item.cp_570,
            cp_600=rider_cp_item.cp_600,
            cp_660=rider_cp_item.cp_660,
            cp_720=rider_cp_item.cp_720,
            cp_780=rider_cp_item.cp_780,
            cp_840=rider_cp_item.cp_840,
            cp_900=rider_cp_item.cp_900,
            cp_960=rider_cp_item.cp_960,
            cp_1020=rider_cp_item.cp_1020,
            cp_1080=rider_cp_item.cp_1080,
            cp_1140=rider_cp_item.cp_1140,
            cp_1200=rider_cp_item.cp_1200,
            cp_1320=rider_cp_item.cp_1320,
            cp_1440=rider_cp_item.cp_1440,
            cp_1560=rider_cp_item.cp_1560,
            cp_1680=rider_cp_item.cp_1680,
            cp_1800=rider_cp_item.cp_1800,
            cp_1920=rider_cp_item.cp_1920,
            cp_2040=rider_cp_item.cp_2040,
            cp_2160=rider_cp_item.cp_2160,
            cp_2280=rider_cp_item.cp_2280,
            cp_2400=rider_cp_item.cp_2400,
            cp_2520=rider_cp_item.cp_2520,
            cp_2640=rider_cp_item.cp_2640,
            cp_2760=rider_cp_item.cp_2760,
            cp_2880=rider_cp_item.cp_2880,
            cp_3000=rider_cp_item.cp_3000,
            cp_3120=rider_cp_item.cp_3120,
            cp_3240=rider_cp_item.cp_3240,
            cp_3360=rider_cp_item.cp_3360,
            cp_3480=rider_cp_item.cp_3480,
            cp_3600=rider_cp_item.cp_3600,
            cp_3900=rider_cp_item.cp_3900,
            cp_4200=rider_cp_item.cp_4200,
            cp_4500=rider_cp_item.cp_4500,
            cp_4800=rider_cp_item.cp_4800,
            cp_5100=rider_cp_item.cp_5100,
            cp_5400=rider_cp_item.cp_5400,
            cp_5700=rider_cp_item.cp_5700,
            cp_6000=rider_cp_item.cp_6000,
            cp_6300=rider_cp_item.cp_6300,
            cp_6600=rider_cp_item.cp_6600,
            cp_7200=rider_cp_item.cp_7200,
            critical_power=rider_cp_item.critical_power,
            anaerobic_work_capacity=rider_cp_item.anaerobic_work_capacity,
            inverse_coefficient=rider_cp_item.inverse_coefficient,
            inverse_exponent=rider_cp_item.inverse_exponent,
            generated=rider_cp_item.generated,
            model_applied=rider_cp_item.model_applied
        )

        # Perform modeling with CP-W' model
        rider_cp_interval_data: Dict[int, float] = rider_cp_item.export_cp_data_for_best_fitting()
        critical_power, anaerobic_work_capacity, _, _ = do_modelling_with_cp_w_prime_model(rider_cp_interval_data)
        modeled_rider_cp_item.critical_power = critical_power
        modeled_rider_cp_item.anaerobic_work_capacity = anaerobic_work_capacity

        # Perform modeling with inverse model
        constant, exponent, _, _ = do_modelling_with_inverse_model(rider_cp_interval_data)
        modeled_rider_cp_item.inverse_coefficient = constant
        modeled_rider_cp_item.inverse_exponent = exponent

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

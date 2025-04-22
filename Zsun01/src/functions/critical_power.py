import numpy as np
from numpy.typing import NDArray
from sklearn.metrics import r2_score, mean_squared_error
from scipy.optimize import curve_fit
from typing import Tuple, Dict
from tabulate import tabulate

import logging
from jgh_logging import jgh_configure_logging
jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)
logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO



def cp_w_prime_model_numpy(xdata: NDArray[np.float64], a: float, b: float) -> NDArray[np.float64]:
    """
    Compute power as a function of CP and W' using the formula (a * xdata + b) / xdata.

    Args:
        xdata (NDArray[np.float64]): Duration (seconds). Must be non-zero.
        a (float): Coefficient for the linear term, cp_model_cp_watts.
        b (float): Constant term, W'

    Returns:
        NDArray[np.float64]: Computed power values.

    Raises:
        ValueError: If xdata contains zero values to avoid division by zero.
    """

    if np.any(xdata < 1):
        raise ValueError("Jgh error message: input xdata must not contain values less than 1.")

    result = (a * xdata + b) / xdata

    return result


def do_modelling_with_cp_w_prime_model(raw_xy_data_cp: Dict[int, float]) -> Tuple[float, float, float, float, Dict[int, Tuple[float, float]]]:
    """
    Estimate critical power and anaerobic work capacity from duration and power data.
    Estimate cp_model_cp_watts and w' using the formula xdata * y = cp_model_cp_watts * xdata + w'. x_axis is time in seconds and y_axis is power in watts.
    cp_model_cp_watts is the critical power, and w' is the anaerobic work capacity.

    Args:
        raw_xy_data_cp (Dict[int, float]): Dictionary where keys are durations (seconds) and values are power (watts).

    Returns:
        Tuple[float, float, float, Dict[int, Tuple[float, float]]]: The values of cp_model_cp_watts and w', the R-squared value,
        and a dictionary combining the original data and predicted values.
    """
    # Convert keys and values of raw_xy_data_cp to NumPy arrays
    xdata: NDArray[np.float64] = np.array(list(raw_xy_data_cp.keys()), dtype=float)
    ydata: NDArray[np.float64] = np.array(list(raw_xy_data_cp.values()), dtype=float)

    # Perform linear regression between duration and work using curve_fit
    # In the model, xdata stands for duration, and xdata * y is work (duration * power)
    popt, _ = curve_fit(cp_w_prime_model_numpy, xdata, ydata, p0=[250, 10_000])

    # Extract the optimal parameters: cp_model_cp_watts (critical power) and cp_model_w_prime(anaerobic work capacity)
    # cp_model_cp_watts, cp_model_w_prime= popt

    logger.debug(f"Fitted parameters: {popt}")

    cp_model_cp_watts: float = float(popt[0])
    anaerobic_work_capacity: float = float(popt[1])

    # Use the cp_w_prime_model to calculate predicted y values based on the fitted parameters
    ydata_pred: NDArray[np.float64] = cp_w_prime_model_numpy(xdata, cp_model_cp_watts, anaerobic_work_capacity)

    # Calculate the R-squared value
    r2: float = r2_score(ydata, ydata_pred)

    # # Calculate the root mean square error (RMSE)
    rmse_cp : float = np.sqrt(mean_squared_error(ydata, ydata_pred)) 


    # Recombine the original data and predicted values into a dictionary
    result: Dict[int, Tuple[float, float]] = {
        int(xdata[i]): (ydata[i], ydata_pred[i]) for i in range(len(xdata))
    }

    return cp_model_cp_watts, anaerobic_work_capacity, r2, rmse_cp, result


def decay_model_numpy(xdata: NDArray[np.float64], a: float, b: float) -> NDArray[np.float64]:
    """
    A decay function that computes a * (1 / (xdata ** b)) for NumPy arrays.
    Handles zero values in the array by replacing them with a small epsilon value.

    Args:
        xdata (NDArray[np.float64]): The input array.
        a (float): Coefficient.
        b (float): Exponent.

    Returns:
        NDArray[np.float64]: The computed values of the decay function.

    Raises:
        ValueError: If xdata contains zero values to avoid division by zero.
    """

    if np.any(xdata < 1):
        raise ValueError("Jgh error message: input xdata must not contain values less than 1.")

    result = a * (1 / (xdata ** b))

    return result


def do_modelling_with_decay_model(raw_xy_data_cp: Dict[int, float]) -> Tuple[float, float, float, float, Dict[int, Tuple[float, float]]]:
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


# def generate_model_fitted_zwiftrider_cp_metrics(zwiftriders_zwift_cp_data: Dict[str, ZwiftRiderCriticalPowerItem]
# ) -> Dict[str, ZwiftRiderCriticalPowerItem]:
#     """
#     Perform model fitting on ZwiftRiderCriticalPowerItem instances to calculate critical power (CP), 
#     anaerobic work capacity (W'), and parameters for the inverse model, and then populate a neew item
#     the item accoridng to the fitted parameters of the inverse model. The intended purpose of this 
#     function is to import the database of ZSun riders and their CP data obtained from Zwiftor ZwiftPower
#     and then to generate a new database of modeled CP data for each rider. This new database serves 
#     as a benchmark for comparing exertion and work rate of riders in a paceline with what they are 
#     capable of achieving in a solo effort.

#     Args:
#         zwiftriders_zwift_cp_data (Dict[str, ZwiftRiderCriticalPowerItem]): 
#             A dictionary where the key is the rider's Zwift ID (as a string) and the value is a 
#             ZwiftRiderCriticalPowerItem instance containing critical power data.

#     Returns:
#         Dict[str, ZwiftRiderCriticalPowerItem]: 
#             A new dictionary of ZwiftRiderCriticalPowerItem instances with calculated CP, W', 
#             inverse model parameters, and imported predicted critical power data.
#     """

#     # Create a new dictionary to store the modeled data
#     modeled_data : Dict[str, ZwiftRiderCriticalPowerItem] = {}

#     # Iterate through each ZwiftRiderCriticalPowerItem instance in the input dictionary
#     for rider_id, rider_cp_item in zwiftriders_zwift_cp_data.items():
#         # Create a copy of the current rider_cp_item to avoid modifying the original
#         modeled_rider_cp_item = ZwiftRiderCriticalPowerItem(
#             zwiftid=rider_cp_item.zwiftid,
#             name=rider_cp_item.name,
#             cp_1=rider_cp_item.cp_1,
#             cp_2=rider_cp_item.cp_2,
#             cp_3=rider_cp_item.cp_3,
#             cp_4=rider_cp_item.cp_4,
#             cp_5=rider_cp_item.cp_5,
#             cp_6=rider_cp_item.cp_6,
#             cp_7=rider_cp_item.cp_7,
#             cp_8=rider_cp_item.cp_8,
#             cp_9=rider_cp_item.cp_9,
#             cp_10=rider_cp_item.cp_10,
#             cp_11=rider_cp_item.cp_11,
#             cp_12=rider_cp_item.cp_12,
#             cp_13=rider_cp_item.cp_13,
#             cp_14=rider_cp_item.cp_14,
#             cp_15=rider_cp_item.cp_15,
#             cp_16=rider_cp_item.cp_16,
#             cp_17=rider_cp_item.cp_17,
#             cp_18=rider_cp_item.cp_18,
#             cp_19=rider_cp_item.cp_19,
#             cp_20=rider_cp_item.cp_20,
#             cp_21=rider_cp_item.cp_21,
#             cp_22=rider_cp_item.cp_22,
#             cp_23=rider_cp_item.cp_23,
#             cp_24=rider_cp_item.cp_24,
#             cp_25=rider_cp_item.cp_25,
#             cp_26=rider_cp_item.cp_26,
#             cp_27=rider_cp_item.cp_27,
#             cp_28=rider_cp_item.cp_28,
#             cp_29=rider_cp_item.cp_29,
#             cp_30=rider_cp_item.cp_30,
#             cp_35=rider_cp_item.cp_35,
#             cp_40=rider_cp_item.cp_40,
#             cp_45=rider_cp_item.cp_45,
#             cp_50=rider_cp_item.cp_50,
#             cp_55=rider_cp_item.cp_55,
#             cp_60=rider_cp_item.cp_60,
#             cp_70=rider_cp_item.cp_70,
#             cp_80=rider_cp_item.cp_80,
#             cp_90=rider_cp_item.cp_90,
#             cp_100=rider_cp_item.cp_100,
#             cp_110=rider_cp_item.cp_110,
#             cp_120=rider_cp_item.cp_120,
#             cp_150=rider_cp_item.cp_150,
#             cp_180=rider_cp_item.cp_180,
#             cp_210=rider_cp_item.cp_210,
#             cp_240=rider_cp_item.cp_240,
#             cp_270=rider_cp_item.cp_270,
#             cp_300=rider_cp_item.cp_300,
#             cp_330=rider_cp_item.cp_330,
#             cp_360=rider_cp_item.cp_360,
#             cp_390=rider_cp_item.cp_390,
#             cp_420=rider_cp_item.cp_420,
#             cp_450=rider_cp_item.cp_450,
#             cp_480=rider_cp_item.cp_480,
#             cp_510=rider_cp_item.cp_510,
#             cp_540=rider_cp_item.cp_540,
#             cp_570=rider_cp_item.cp_570,
#             cp_600=rider_cp_item.cp_600,
#             cp_660=rider_cp_item.cp_660,
#             cp_720=rider_cp_item.cp_720,
#             cp_780=rider_cp_item.cp_780,
#             cp_840=rider_cp_item.cp_840,
#             cp_900=rider_cp_item.cp_900,
#             cp_960=rider_cp_item.cp_960,
#             cp_1020=rider_cp_item.cp_1020,
#             cp_1080=rider_cp_item.cp_1080,
#             cp_1140=rider_cp_item.cp_1140,
#             cp_1200=rider_cp_item.cp_1200,
#             cp_1320=rider_cp_item.cp_1320,
#             cp_1440=rider_cp_item.cp_1440,
#             cp_1560=rider_cp_item.cp_1560,
#             cp_1680=rider_cp_item.cp_1680,
#             cp_1800=rider_cp_item.cp_1800,
#             cp_1920=rider_cp_item.cp_1920,
#             cp_2040=rider_cp_item.cp_2040,
#             cp_2160=rider_cp_item.cp_2160,
#             cp_2280=rider_cp_item.cp_2280,
#             cp_2400=rider_cp_item.cp_2400,
#             cp_2520=rider_cp_item.cp_2520,
#             cp_2640=rider_cp_item.cp_2640,
#             cp_2760=rider_cp_item.cp_2760,
#             cp_2880=rider_cp_item.cp_2880,
#             cp_3000=rider_cp_item.cp_3000,
#             cp_3120=rider_cp_item.cp_3120,
#             cp_3240=rider_cp_item.cp_3240,
#             cp_3360=rider_cp_item.cp_3360,
#             cp_3480=rider_cp_item.cp_3480,
#             cp_3600=rider_cp_item.cp_3600,
#             cp_3900=rider_cp_item.cp_3900,
#             cp_4200=rider_cp_item.cp_4200,
#             cp_4500=rider_cp_item.cp_4500,
#             cp_4800=rider_cp_item.cp_4800,
#             cp_5100=rider_cp_item.cp_5100,
#             cp_5400=rider_cp_item.cp_5400,
#             cp_5700=rider_cp_item.cp_5700,
#             cp_6000=rider_cp_item.cp_6000,
#             cp_6300=rider_cp_item.cp_6300,
#             cp_6600=rider_cp_item.cp_6600,
#             cp_7200=rider_cp_item.cp_7200,
#             cp_model_cp_watts=rider_cp_item.cp_model_cp_watts,
#             anaerobic_work_capacity=rider_cp_item.anaerobic_work_capacity,
#             ftp_model_coefficient=rider_cp_item.ftp_model_coefficient,
#             ftp_model_exponent=rider_cp_item.ftp_model_exponent,
#             timestamp=rider_cp_item.timestamp,
#             model_applied=rider_cp_item.model_applied
#         )

#         # Perform modeling with CP-W' model
#         rider_cp_interval_data: Dict[int, float] = rider_cp_item.export_zwiftpower_data_for_cp_w_prime_modelling()
#         cp_model_cp_watts, anaerobic_work_capacity, _, _, _ = do_modelling_with_cp_w_prime_model(rider_cp_interval_data)
#         modeled_rider_cp_item.cp_model_cp_watts = cp_model_cp_watts
#         modeled_rider_cp_item.cp_model_w_prime= anaerobic_work_capacity

#         # Perform modeling with inverse model
#         constant, exponent_ftp, _, _, _ = do_modelling_with_decay_model(rider_cp_interval_data)
#         modeled_rider_cp_item.ftp_model_coefficient = constant
#         modeled_rider_cp_item.ftp_model_exponent = exponent_ftp

#         # Calculate the predicted y values based on the fitted parameters from the inverse model
#         x_ordinates = np.array(ZwiftRiderCriticalPowerItem.export_zwiftpower_x_ordinates())
#         y_ordinates_inverse_model = decay_model_numpy(x_ordinates, constant, exponent_ftp)

#         # Zip the x_ordinates and y_pred_decay_model together into a dict[int, float]
#         generated_cp_data = dict(zip(x_ordinates, y_ordinates_inverse_model))

#         # Add the y_pred_inverse_model_dict to the modeled_rider_cp_item
#         modeled_rider_cp_item.import_cp_data(generated_cp_data)

#         # Add the modeled rider_cp_item to the new dictionary
#         modeled_data[rider_id] = modeled_rider_cp_item

#     return modeled_data

# tests

def test_cp_w_prime_model_numpy():

    # # a. Test with Valid Inputs (jgh)
    xdata = np.array([30, 300, 1200, 1800, 2400], dtype=np.float64)
    a = 240  # Critical power
    b = 10000  # Anaerobic work capacity
    result = cp_w_prime_model_numpy(xdata, a, b)
    logger.debug(f"\nCP-W' Model Result: y_pred\n\n{result}\n")

    # # b. Test with Zero Values in xdata

    # xdata = np.array([0, 30, 60], dtype=np.float64)
    # try:
    #     result = cp_w_prime_model_numpy(xdata, a, b)
    # except ValueError as e:
    #     logger.debug(e)     

    # # c. Test with Small Values in xdata

    # xdata = np.array([1e-10, 30, 300], dtype=np.float64)
    # result = cp_w_prime_model_numpy(xdata, a, b)
    # logger.debug(result)

def test_decay_model_numpy():

        a = 654.0 # Coefficient
        b = 0.1314 # Negative exponent_ftp

        # # a. Test with Valid Inputs (jgh)
        xdata = np.array([30, 300, 1200, 1800, 2400], dtype=np.float64)
        result = decay_model_numpy(xdata, a, b)
        logger.debug(f"\nDecay Model Result: y_pred\n\n{result}\n")

        # # b. Test with Small Values in xdata

        # xdata = np.array([1e-10, 30, 60], dtype=np.float64)
        # result = decay_model_numpy(xdata, a, b)
        # logger.debug("Inverse Model Result: small value in xdata inputs")
        # logger.debug (f"{result}")

        # # c. Test with Zero Values in xdata

        # xdata = np.array([0, 30, 60], dtype=np.float64)
        # logger.debug("Inverse Model Result: zero value in xdata inputs")
        # try:
        #     result = decay_model_numpy(xdata, a, b)
        # except ValueError as e:
        #     logger.debug(e)     

def test_do_modelling_with_decay_model():
    # Sample data
    raw_xy_data_cp = {
        30: 425.0,
        300: 292.0,
        1200: 254.0,
        1800: 252.0,
        2400: 244.0
    }

    #do work
    coefficient_ftp, exponent_ftp, r2, rmse_cp, result = do_modelling_with_decay_model(raw_xy_data_cp)
    # Prepare data for the summary table
    summary_table = [
        ["Coefficient", round(coefficient_ftp, 4)],
        ["Exponent", round(exponent_ftp, 4)],
        ["R-squared", round(r2, 2)],
        ["RMSE", round(rmse_cp)]
    ]

    # Log the summary table
    logger.info("\nSummary of Decay Model results:\n" + tabulate(summary_table, headers=["Metric", "Value"], tablefmt="simple"))

    # Prepare data for the detailed result table
    result_table = [
        [x, round(y[0]), round(y[1])]
        for x, y in result.items()
    ]
    headers = ["xdata (s)", "ydata (W)", "y_pred (W)"]

    # Log the detailed result table
    logger.info("\n" + tabulate(result_table, headers=headers, tablefmt="simple"))

def test_do_modelling_with_cp_w_prime_model():
    # Sample data
    raw_xy_data_cp = {
        30: 425.0,
        300: 292.0,
        1200: 254.0,
        1800: 252.0,
        2400: 244.0
    }

    #do work
    cp_model_cp_watts, anaerobic_work_capacity, r2, rmse_cp, result = do_modelling_with_cp_w_prime_model(raw_xy_data_cp)

    # Prepare data for the summary table
    summary_table = [
        ["Critical Power (W)", round(cp_model_cp_watts)],
        ["Anaerobic Work Capacity (kJ)", round(anaerobic_work_capacity)/1000],
        ["R-squared", round(r2, 2)],
        ["RMSE", round(rmse_cp)]
    ]

    # Log the summary table
    logger.info("\nSummary of CP_W_prime model results:\n" + tabulate(summary_table, headers=["Metric", "Value"], tablefmt="simple"))

    # Prepare data for the detailed result table
    result_table = [
        [x, round(y[0]), round(y[1])]
        for x, y in result.items()
    ]
    headers = ["xdata (s)", "ydata (W)", "y_pred (W)"]

    # Log the detailed result table
    logger.info("\n" + tabulate(result_table, headers=headers, tablefmt="simple"))

if __name__ == "__main__":
    test_decay_model_numpy()
    test_cp_w_prime_model_numpy()
    test_do_modelling_with_decay_model()
    test_do_modelling_with_cp_w_prime_model()


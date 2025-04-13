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
            cp_5_sec=rider_cp_item.cp_5_sec,
            cp_15_sec=rider_cp_item.cp_15_sec,
            cp_30_sec=rider_cp_item.cp_30_sec,
            cp_1_min=rider_cp_item.cp_1_min,
            cp_2_min=rider_cp_item.cp_2_min,
            cp_90_sec=rider_cp_item.cp_90_sec,
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
            cp_75_min=rider_cp_item.cp_75_min,
            cp_90_min=rider_cp_item.cp_90_min,
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
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    from tabulate import tabulate
    import matplotlib.pyplot as plt
    logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO
    from handy_utilities import read_dict_of_zwiftriders, read_dict_of_cpdata

    # get zwift 90-day rider data

    riders = read_dict_of_zwiftriders()
    riders_cp_data = read_dict_of_cpdata("extracted_input_cp_data_for_betel.json")

    barryb ='5490373' 
    johnh ='58160'
    lynseys ='383480'
    joshn ='2508033'
    richardm ='1193'
    markb ='5530045'
    davek="3147366"


    rider_id = davek
    raw_xy_data = riders_cp_data[rider_id].export_cp_data_for_best_fitting()

    # do modelling

    cp, awc, r_squared, answer  = do_modelling_with_cp_w_prime_model(raw_xy_data)
    summary = f"Critical power model: CP={round(cp)}W  AWC={round(awc/1_000)}kJ  R_squared={round(r_squared,2)}  P_1hour={round(cp_w_prime_model(60*60, cp, awc))}W"
    logger.info(f"\n{summary}")

    constant, exponent, r_squared2, answer2 = do_modelling_with_inverse_model(raw_xy_data)
    summary2 = f"Inverse model: c={round(constant,0)}  e={round(exponent,4)}  R_squared={round(r_squared2,2)}  P_1hour={round(inverse_model(60*60, constant, exponent))}W"
    logger.info(f"\n{summary2}")

    # Tabulate answers

    table_data = [
        [x, f"{y:.0f}", f"{y_pred_inv:.0f}", f"{y_pred_cp:.0f}"]
        for x, y, (_, y_pred_cp), (_, y_pred_inv) in zip(
            raw_xy_data.keys(), raw_xy_data.values(), answer.values(), answer2.values()
        )
    ]
    headers = ["x (s)", "y (Raw)", "y_pred (Inverse Model)", "y_pred (CP Model)"]
    logger.info("\nComparison of Predicted Values:")
    logger.info("\n" + tabulate(table_data, headers=headers, tablefmt="simple"))

    # Define xdata for predictions

    xdata_test = [30, 60, 120, 150, 180, 300, 420, 600, 720, 900, 1200, 1800, 2400, 3000, 3600, 4500, 5400, 7200, 10800, 14400]    
    row_titles = ["30s", "1min", "2min", "90s", "3min", "5min", "7min", "10min", "12min", "15min", "20min", "30min", "40min", "50min", "60min", "75min", "90min", "2hour", "3hour", "4hour"]

    y_pred_cp_model = [cp_w_prime_model(x, cp, awc) for x in xdata_test]
    y_pred_inverse_model = [inverse_model(x, constant, exponent) for x in xdata_test]

    # Generate a table for the predictions
    table_data_pred = [
        [title, x, f"{y_inv:.0f}", f"{y_cp:.0f}"]
        for title, x, y_inv, y_cp in zip(row_titles, xdata_test, y_pred_inverse_model, y_pred_cp_model)
    ]
    headers_pred = ["Row Title", "x (s)", "y_pred (Inverse Model)", "y_pred (CP Model)"]

    logger.info("\nPredicted Values for Specified xdata:")
    logger.info("\n" + tabulate(table_data_pred, headers=headers_pred, tablefmt="simple"))
    logger.info("\nModelling completed. Thank you.\n")

    # Plot answers

    xdata = list(raw_xy_data.keys())
    ydata = list(raw_xy_data.values())
    ydata_pred = [value[1] for value in answer.values()]
    ydata_pred2 = [value[1] for value in answer2.values()]

    plt.figure(figsize=(10, 6))
    plt.scatter(xdata, ydata, color='blue', label='Zwift 90-day data')
    plt.plot(xdata, ydata_pred, color='red', label=summary)
    plt.plot(xdata, ydata_pred2, color='green', label=summary2)
    plt.xlabel('Duration (s)')
    plt.ylabel('Power (W)')
    plt.title(f'{riders[rider_id].name}')
    plt.xticks(xdata)  
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()

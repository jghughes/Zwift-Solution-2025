import numpy as np
from sklearn.metrics import r2_score
from scipy.optimize import curve_fit
import logging
from tabulate import tabulate
import matplotlib.pyplot as plt
from handy_utilities import read_dict_of_zwiftriders, read_dict_of_cpdata
from power_duration_modelling import cp_w_prime_model, inverse_model, do_modelling_with_cp_w_prime_model, do_modelling_with_inverse_model
from jgh_logging import jgh_configure_logging

def main():
    """
    Perform one-off power-duration modeling for a specific Zwift rider using two models:
    the Critical Power (CP) model and the Inverse model. The script calculates
    model parameters, evaluates model performance, and generates predictions.

    The results include:
    - Model parameters (e.g., CP, AWC, constant, exponent).
    - R-squared values for model performance.
    - Predicted power values for specified durations.
    - A comparison of raw data and predicted values.
    - A plot visualizing the raw data and model predictions.

    Steps:
    1. Load Zwift rider data and critical power data.
    2. Perform modeling using the CP-W' model and the Inverse model.
    3. Log model parameters and R-squared values.
    4. Generate tables comparing raw data and predicted values.
    5. Generate predictions for specified durations.
    6. Plot raw data and model predictions.

    Note:
    - The script processes data for a specific rider, identified by their Zwift ID.
    - The Zwift ID of the rider to process is set in the `rider_id` variable.

    Dependencies:
    - Requires the `handy_utilities` module for reading rider data.
    - Uses `power_duration_modelling` for modeling functions.
    - Requires `matplotlib` for plotting and `tabulate` for table generation.

    Returns:
        None
    """
    # configure logging

    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

    # get zwift 90-day rider data

    riders = read_dict_of_zwiftriders()
    riders_cp_data = read_dict_of_cpdata("extracted_input_cp_data_for_betel.json", "C:/Users/johng/holding_pen/StuffForZsun/Betel/")

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
    row_titles = ["30s", "1min", "2min", "90s", "3min", "5min", "7min", "10min", "12min", "15min", "20min", "30min", "40min", "50min", "1hour", "75min", "90min", "2hour", "3hour", "4hour"]

    y_pred_cp_model = [cp_w_prime_model(x, cp, awc) for x in xdata_test]
    y_pred_inverse_model = [inverse_model(x, constant, exponent) for x in xdata_test]

    # Tabulate predictions
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


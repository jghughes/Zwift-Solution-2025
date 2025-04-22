import numpy as np
from sklearn.metrics import r2_score
from scipy.optimize import curve_fit
import logging
from tabulate import tabulate
import matplotlib.pyplot as plt
from handy_utilities import read_dict_of_zwiftriders, read_dict_of_cpdata
import critical_power as cp 
from jgh_logging import jgh_configure_logging

def main():
    """
    Perform one-off power-duration modeling for a selected Zwift rider using two models:
    the Critical Power (CP) model and the Inverse model. The script calculates
    model parameters, evaluates model statistical accuracy, and generates 
    predictions for illustrative purposes.

    The results include:
    - Model parameters (e.g., CP, AWC, coefficient, exponent).
    - R-squared and RMSE values for model performance.
    - Predicted power values for specified durations.
    - A comparison of raw data and predicted values.
    - A plot visualizing the raw data and model predictions.

    Steps:
    1. Load Zwift rider profiles (written manually by JGH). Load critical power data consolidated from ZwiftPower files from DaveK.
    2. Perform modeling using the CP-W' model and the Inverse model.
    3. Log model parameters and R-squared values.
    4. Generate tables comparing raw data and predicted values.
    5. Generate predictions for some selected durations for illustration.
    6. Plot raw data and model predictions.

    Note:
    - The script processes data for a specific rider, identified by their Zwift ID.
    - The Zwift ID of the rider to process is set in the variable `rider_id` below.

    Dependencies:
    - Requires the `handy_utilities` module for reading rider data.
    - Uses `critical_power` for modeling functions.
    - Requires `matplotlib` for plotting and `tabulate` for table generation.

    Returns:
        None
    """
    # configure logging

    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

    # get rider profiles

    from handy_utilities import read_dict_of_zwiftriders

    RIDERDATA_FILE_NAME = "betel_rider_profiles.json"
    ZSUN01_PROJECT_DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

    dict_of_zwiftrideritem = read_dict_of_zwiftriders(RIDERDATA_FILE_NAME, ZSUN01_PROJECT_DATA_DIRPATH)

    # get rider CP data

    riders_cp_data = read_dict_of_cpdata("extracted_input_cp_data_for_betelV4.json", "C:/Users/johng/holding_pen/StuffForZsun/Betel/")
    # riders_cp_data = read_dict_of_cpdata("extracted_input_cp_data_for_betel.json", "C:/Users/johng/holding_pen/StuffForZsun/Betel/")

    barryb ='5490373' #ftp 273
    johnh ='1884456' #ftp 240
    lynseys ='383480' #ftp 201
    joshn ='2508033' #ftp 260
    richardm ='1193' # ftp 200
    markb ='5530045' #ftp 280
    davek="3147366" #ftp 276 cp 278
    husky="5134" #ftp 268
    scottm="11526" #ftp 247
    timr= "5421258" #ftp 380
    tom_bick= "11741" #ftp 303 cp 298
    meridith_leubner ="1707548" #ftp 220
    melissa_warwick = "1657744" #ftp 213
    brandi_steeve = "991817" #ftp 196
    selena = "2682791" #ftp 214

    # choose a rider to model

    rider_id = markb


    # extract raw data for modelling

    raw_xy_data_sprint = riders_cp_data[rider_id].export_cp_data_for_best_fit_modelling_sprint()

    # do CP modelling
    
    critical_power, anaerobic_work_capacity, r_squared, rmse, answer_sprint  = cp.do_modelling_with_cp_w_prime_model(raw_xy_data_sprint)

    p5min= cp.cp_w_prime_model_numpy(np.array([5*60]), critical_power, anaerobic_work_capacity)

    summary_sprint  =  f"CP model: CP = {round(critical_power)}W  W' = {round(anaerobic_work_capacity/1_000)}kJ  R_squared = {round(r_squared,2)}  P5m = {round(p5min[0])}W"

    logger.info(f"\n{summary_sprint}")

    # do Decay modelling

    raw_xy_data_endurance = riders_cp_data[rider_id].export_cp_data_for_best_fit_modelling_endurance()

    coefficient, exponent, r_squared2, rmse2, answer_endurance = cp.do_modelling_with_decay_model(raw_xy_data_endurance)

    p1hour= cp.decay_model_numpy(np.array([60*60]), coefficient, exponent)

    summary_endurance = f"Decay model: c = {round(coefficient,0)}  e = {round(exponent,4)}  R_squared = {round(r_squared2,2)} P60m = {round(p1hour[0])}W"

    logger.info(f"\n{summary_endurance}")

    # # Tabulate answers

    table_data = [
        [x, f"{y:.0f}", f"{y_pred_decay:.0f}", f"{y_pred_cp:.0f}"]
        for x, y, (_, y_pred_cp), (_, y_pred_decay) in zip(
            raw_xy_data_sprint.keys(), raw_xy_data_sprint.values(), answer_sprint.values(), answer_endurance.values()
        )
    ]
    headers = ["x (s)", "y (Raw)", "y_pred - endurance", "y_pred - sprint"]
    logger.info(f"\nComparison of Predicted Values: {dict_of_zwiftrideritem[rider_id].name}")
    logger.info("\n" + tabulate(table_data, headers=headers, tablefmt="simple"))

    # # Define xdata for predictions

    xdata_test = np.array([30, 60, 120, 150, 180, 300, 420, 600, 720, 900, 1200, 1800, 2400, 3000, 3600, 4500, 5400, 7200, 10800, 14400])
    row_titles = ["30s", "1min", "2min", "90s", "3min", "5min", "7min", "10min", "12min", "15min", "20min", "30min", "40min", "50min", "1hour", "75min", "90min", "2hour", "3hour", "4hour"]

    y_pred_sprint_test = cp.cp_w_prime_model_numpy(xdata_test, critical_power, anaerobic_work_capacity)
    y_pred_endurance_test = cp.decay_model_numpy(xdata_test, coefficient, exponent)
    y_pred_combined_model_test = cp.combined_model_numpy(xdata_test, critical_power, anaerobic_work_capacity, coefficient, exponent)


    # # Tabulate predictions
    table_data_pred = [
        [title, x, f"{y_pred_decay:.0f}", f"{y_pred_cp:.0f}", f"{y_pred_comb:.0f}"]
        for title, x, y_pred_decay, y_pred_cp, y_pred_comb in zip(row_titles, xdata_test, y_pred_endurance_test, y_pred_sprint_test, y_pred_combined_model_test)
    ]
    headers_pred = ["Row Title", "x (s)", "y_pred (endurance)", "y_pred (sprint)", "y_pred (combined)"]

    logger.info(f"\nPredicted Values for selected xdata points: {dict_of_zwiftrideritem[rider_id].name}")
    logger.info("\n" + tabulate(table_data_pred, headers=headers_pred, tablefmt="simple"))
    logger.info("\nModelling completed. Thank you.\n")

    # # Plot answers

    xdata_sprint = list(raw_xy_data_sprint.keys())
    ydata_sprint = list(raw_xy_data_sprint.values())

    xdata_endurance = list(raw_xy_data_endurance.keys())
    ydata_endurance = list(raw_xy_data_endurance.values())

    ydata_pred_sprint = [value[1] for value in answer_sprint.values()]
    ydata_pred_endurance = [value[1] for value in answer_endurance.values()]

    xdata_combined = np.array(xdata_sprint) + np.array(xdata_endurance)
    ydata_combined = np.array(ydata_sprint) + np.array(ydata_endurance)

    y_pred_combined_model_test = cp.combined_model_numpy(np.array(xdata_sprint), critical_power, anaerobic_work_capacity, coefficient, exponent)

    ydata_pred_combined = [float(value) for value in y_pred_combined_model_test]
    r_squared_combined: float = r2_score(ydata_combined, ydata_pred_combined)
    p1hour = cp.combined_model_numpy(np.array([60*60]), critical_power, anaerobic_work_capacity, coefficient, exponent)

    plt.figure(figsize=(10, 6))
    plt.scatter(xdata_sprint, ydata_sprint, color='blue', label='ZwiftPower 90-day cp data - sprint')
    plt.scatter(xdata_endurance, ydata_endurance, color='black', label='ZwiftPower 90-day cp data - endurance')
    plt.plot(xdata_sprint, ydata_pred_sprint, color='red', label=summary_sprint)
    plt.plot(xdata_endurance, ydata_pred_endurance, color='pink', label=summary_endurance)
    plt.plot(xdata_combined, ydata_pred_combined, color='purple', label=f"Combined model : R_squared = {round(r_squared_combined,2)}  P60m = {round(p1hour[0])}W  zFTP = {dict_of_zwiftrideritem[rider_id].ftp}W")
    plt.xlabel('Duration (s)')
    plt.ylabel('Power (W)')
    plt.title(f'{dict_of_zwiftrideritem[rider_id].name}')
    plt.xticks(xdata_sprint)  
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()


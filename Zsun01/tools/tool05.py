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
    - Model parameters (e.g., CP, AWC, coefficient_ftp, exponent_ftp).
    - R-squared and RMSE values for model performance.
    - Predicted power values for specified durations.
    - A comparison of raw data and predicted values.
    - A plot visualizing the raw data and model predictions.

    Steps:
    1. Load Zwift rider profiles (written manually by JGH). Load critical power data consolidated from files from DaveK.
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
    johnh ='1884456' #ftp 240 zmap 292
    lynseys ='383480' #ftp 201
    joshn ='2508033' #ftp 260
    richardm ='1193' # ftp 200
    markb ='5530045' #ftp 280
    davek="3147366" #ftp 276 cp 278
    husky="5134" #ftp 268
    scottm="11526" #ftp 247
    timr= "5421258" #ftp 380
    tom_bick= "11741" #ftp 303 cp 298
    bryan_bumpas = "9011" #ftp 214
    matt_steeve = "1024413"
    meridith_leubner ="1707548" #ftp 220
    melissa_warwick = "1657744" #ftp 213
    brandi_steeve = "991817" #ftp 196
    selena = "2682791" #ftp 214

    # choose a rider to model

    rider_id = davek


    # determine cp and w_prime

    raw_xy_data_cp = riders_cp_data[rider_id].export_zwiftpower_90day_best_graph_for_cp_w_prime_modelling()

    critical_power, anaerobic_work_capacity, r_squared_cp, rmse_cp, answer_cp  = cp.do_modelling_with_cp_w_prime_model(raw_xy_data_cp)

    summary_cp_w_prime  =  f"Critical Power = {round(critical_power)}W  Anaerobic Work Capacity = {round(anaerobic_work_capacity/1_000)}kJ"

    logger.info(f"\n{summary_cp_w_prime}")


    # determine some sensible pull power targets

    raw_xy_data_pull = riders_cp_data[rider_id].export_zwiftpower_90day_best_graph_for_pull_zone_modelling()

    coefficient_pull, exponent_pull, r_squared_pull, rmse_pull, answer_pull = cp.do_modelling_with_decay_model(raw_xy_data_pull)

    pull_short = cp.decay_model_numpy(np.array([300]), coefficient_pull, exponent_pull)
    pull_medium = cp.decay_model_numpy(np.array([600]), coefficient_pull, exponent_pull)
    pull_long = cp.decay_model_numpy(np.array([1800]), coefficient_pull, exponent_pull)

    summary_pull = f"Pull power (30 - 60 - 120 seconds) = {round(pull_short[0])} - {round(pull_medium[0])} - {round(pull_long[0])}W"

    logger.info(f"\n{summary_pull}")


    # determine ftp

    raw_xy_data_ftp = riders_cp_data[rider_id].export_zwiftpower_90day_best_graph_for_ftp_modelling()

    coefficient_ftp, exponent_ftp, r_squared_ftp, rmse_ftp, answer_ftp = cp.do_modelling_with_decay_model(raw_xy_data_ftp)

    ftp = cp.decay_model_numpy(np.array([60*60]), coefficient_ftp, exponent_ftp)

    summary_ftp = f"Functional Threshold Power = {round(ftp[0])}W"

    logger.info(f"\n{summary_ftp}")

    logger.info("\nModelling completed. Thank you.\n")

    # Plot answers

    xdata_cp = list(raw_xy_data_cp.keys())
    ydata_cp = list(raw_xy_data_cp.values())

    xdata_pull = list(raw_xy_data_pull.keys())
    ydata_pull = list(raw_xy_data_pull.values())

    xdata_ftp = list(raw_xy_data_ftp.keys())
    ydata_ftp = list(raw_xy_data_ftp.values())

    ydata_pred_cp = [value[1] for value in answer_cp.values()]
    ydata_pred_pull = [value[1] for value in answer_pull.values()]
    ydata_pred_ftp = [value[1] for value in answer_ftp.values()]

    plt.figure(figsize=(10, 6))
    plt.scatter(xdata_cp, ydata_cp, color='grey', label='critical power range')
    plt.scatter(xdata_pull, ydata_pull, color='brown', label='pull power range')
    plt.scatter(xdata_ftp, ydata_ftp, color='black', label='functional threshold range')
    plt.plot(xdata_cp, ydata_pred_cp, color='red', label=summary_cp_w_prime)
    plt.plot(xdata_pull, ydata_pred_pull, color='orange', label=summary_pull)
    plt.plot(xdata_ftp, ydata_pred_ftp, color='green', label=summary_ftp)
    plt.xlabel('Duration (s)')
    plt.ylabel('ZwiftPower 90-day best (Watts)')
    plt.title(f'{dict_of_zwiftrideritem[rider_id].name}')
    plt.xticks(xdata_cp)  
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()


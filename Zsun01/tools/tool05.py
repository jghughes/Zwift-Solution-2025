import numpy as np
from sklearn.metrics import r2_score
from scipy.optimize import curve_fit
from datetime import datetime
from zsun_rider_item import ZsunRiderItem
from handy_utilities import read_dict_of_zsunrider_items, read_dict_of_90day_bestpower_items
import jgh_cp as cp
from tabulate import tabulate
import matplotlib.pyplot as plt


import logging
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
    - Uses `jgh_cp` for modeling functions.
    - Requires `matplotlib` for plotting and `tabulate` for table generation.

    Returns:
        None
    """
    # configure logging

    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

    # get rider profiles

    from handy_utilities import read_dict_of_zsunrider_items

    RIDERDATA_FILE_NAME = "betel_rider_profiles.json"
    ZSUN01_PROJECT_DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

    dict_of_zwiftrideritem = read_dict_of_zsunrider_items(RIDERDATA_FILE_NAME, ZSUN01_PROJECT_DATA_DIRPATH)

    # get rider CP data

    riders_cp_data = read_dict_of_90day_bestpower_items("extracted_input_cp_data_for_betelV4.json", "C:/Users/johng/holding_pen/StuffForZsun/Betel/")
    # riders_cp_data = read_dict_of_90day_bestpower_items("extracted_input_cp_data_for_betel.json", "C:/Users/johng/holding_pen/StuffForZsun/Betel/")

    barryb ='5490373' #ftp 273
    johnh ='1884456' #ftp 240 zmap 292
    lynseys ='383480' #ftp 201
    joshn ='2508033' #ftp 260
    richardm ='1193' # ftp 200
    markb ='5530045' #ftp 280
    davek="3147366" #ftp 276 jgh_cp 278
    husky="5134" #ftp 268
    scottm="11526" #ftp 247
    timr= "5421258" #ftp 380
    tom_bick= "11741" #ftp 303 jgh_cp 298
    bryan_bumpas = "9011" #ftp 214
    matt_steeve = "1024413"
    giao_nguyen = "183277" #ftp 189
    meridith_leubner ="1707548" #ftp 220
    melissa_warwick = "1657744" #ftp 213
    brandi_steeve = "991817" #ftp 196
    selena = "2682791" #ftp 214

    # choose a rider to model

    rider_id = joshn


    # model jgh_cp and w_prime

    raw_xy_data_cp = riders_cp_data[rider_id].export_x_y_ordinates_for_cp_w_prime_modelling()

    jgh_cp, anaerobic_work_capacity, r_squared_cp, rmse_cp, answer_cp  = cp.do_curve_fit_with_cp_w_prime_model(raw_xy_data_cp)

    # model pull power curve

    raw_xy_data_pull = riders_cp_data[rider_id].export_x_y_ordinates_for_pull_zone_modelling()

    coefficient_pull, exponent_pull, r_squared_pull, rmse_pull, answer_pull = cp.do_curve_fit_with_decay_model(raw_xy_data_pull)

    # model ftp curve 

    raw_xy_data_ftp = riders_cp_data[rider_id].export_x_y_ordinates_for_ftp_modelling()

    coefficient_ftp, exponent_ftp, r_squared_ftp, rmse_ftp, answer_ftp = cp.do_curve_fit_with_decay_model(raw_xy_data_ftp)

    logger.info("\nModelling completed. Thank you.\n")

    # instantiate a power item to hold the results

    pi = ZsunRiderItem(
        zwift_id=rider_id,
        name=dict_of_zwiftrideritem[rider_id].name,
        jgh_cp=jgh_cp,
        jgh_w_prime=anaerobic_work_capacity,
        jgh_ftp_curve_coefficient=coefficient_ftp,
        jgh_ftp_curve_exponent=exponent_ftp,
        jgh_pull_curve_coefficient=coefficient_pull,
        jgh_pull_curve_exponent=exponent_pull,
        jgh_when_curves_fitted=datetime.now().isoformat(),
    )

    # log pretty summaries

    summary_cp_w_prime  =  f"Critical Power = {round(pi.get_critical_power_watts())}W  Anaerobic Work Capacity = {round(pi.get_anaerobic_work_capacity_kj(), 1)}kJ"

    logger.info(f"\n{summary_cp_w_prime}")

    summary_pull = f"Pull power (30 - 60 - 120 seconds) = {round(pi.get_30sec_watts())} - {round(pi.get_1_minute_watts())} - {round(pi.get_2_minute_watts())}W  [r-squared {round(r_squared_pull, 2)}]"

    logger.info(f"\n{summary_pull}")

    summary_ftp = f"Functional Threshold Power (60 minutes watts)) = {round(pi.get_ftp_60_minute_watts())}W  [r-squared {round(r_squared_ftp, 2)}]"

    logger.info(f"\n{summary_ftp}")

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
    plt.scatter(xdata_pull, ydata_pull, color='orange', label='pull power range')
    plt.scatter(xdata_ftp, ydata_ftp, color='black', label='functional threshold range')
    plt.plot(xdata_cp, ydata_pred_cp, color='red', label=summary_cp_w_prime)
    plt.plot(xdata_pull, ydata_pred_pull, color='blue', label=summary_pull)
    plt.plot(xdata_ftp, ydata_pred_ftp, color='green', label=summary_ftp)
    plt.xlabel('Duration (s)')
    plt.ylabel('ZwiftPower 90-day best (Watts)')
    plt.title(f'{dict_of_zwiftrideritem[rider_id].name}')
    plt.xticks(xdata_cp)  
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()


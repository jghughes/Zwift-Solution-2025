import numpy as np
from sklearn.metrics import r2_score
from scipy.optimize import curve_fit
from datetime import datetime
from zsun_rider_item import ZsunRiderItem
from handy_utilities import read_dict_of_zsunrider_items, get_betel_zwift_ids, read_many_zwiftpower_bestpower_files_in_folder
import critical_power as cp
import matplotlib.pyplot as plt
from matplot_utilities import set_x_axis_ticks,set_y_axis_ticks




def main():
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

    barryb ='5490373' #ftp 273
    johnh ='1884456' #ftp 240 zmap 292
    lynseys ='383480' #ftp 201
    joshn ='2508033' #ftp 260
    richardm ='1193' # ftp 200
    markb ='5530045' #ftp 280
    davek="3147366" #ftp 276 critical_power 278
    husky="5134" #ftp 268
    scottm="11526" #ftp 247
    timr= "5421258" #ftp 380
    tom_bick= "11741" #ftp 303 critical_power 298
    bryan_bumpas = "9011" #ftp 214
    matt_steeve = "1024413"
    giao_nguyen = "183277" #ftp 189
    meridith_leubner ="1707548" #ftp 220
    melissa_warwick = "1657744" #ftp 213
    brandi_steeve = "991817" #ftp 196
    selena = "2682791" #ftp 214
    steve_seiler = "6142432" #ftp 270

    # choose a rider to model

    zwiftID = johnh


    ZSUN01_BETEL_PROFILES_FILE_NAME = "betel_rider_profiles.json"
    ZSUN01_PROJECT_DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

    OUTPUT_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/"
    ZWIFT_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwift/"
    ZWIFTRACINGAPP_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftracing-app-post/"
    ZWIFTPOWER_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/profile-page/"
    ZWIFTPOWER_GRAPHS_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/power-graph-watts/"

    dict_of_zsun01_betel_zsunrideritems = read_dict_of_zsunrider_items(ZSUN01_BETEL_PROFILES_FILE_NAME, ZSUN01_PROJECT_DATA_DIRPATH)

    betel_IDs = get_betel_zwift_ids()

    dict_of_jghbestpoweritems_for_betel = read_many_zwiftpower_bestpower_files_in_folder(betel_IDs, ZWIFTPOWER_GRAPHS_DIRPATH)

    # model critical_power and w_prime

    x_y_ordinates_for_cp_w_prime = dict_of_jghbestpoweritems_for_betel[zwiftID].export_x_y_ordinates_for_cp_w_prime_modelling()

    critical_power, anaerobic_work_capacity, r_squared_cp, rmse_cp, answer_cp  = cp.do_curve_fit_with_cp_w_prime_model(x_y_ordinates_for_cp_w_prime)

    # model pull power curve

    x_y_ordinates_for_pulling = dict_of_jghbestpoweritems_for_betel[zwiftID].export_x_y_ordinates_for_pull_zone_modelling()

    coefficient_pull, exponent_pull, r_squared_pull, rmse_pull, answer_pull = cp.do_curve_fit_with_decay_model(x_y_ordinates_for_pulling)

    # model ftp curve 

    x_y_ordinates_for_FTP_60min = dict_of_jghbestpoweritems_for_betel[zwiftID].export_x_y_ordinates_for_ftp_modelling()

    coefficient_60min, exponent_60min, r_squared_60min, rmse_60min, answer_60min = cp.do_curve_fit_with_decay_model(x_y_ordinates_for_FTP_60min)

    logger.info("\nModelling completed. Thank you.\n")

    # instantiate a power item to hold the results

    pi = ZsunRiderItem(
        zwift_id=zwiftID,
        name=dict_of_zsun01_betel_zsunrideritems[zwiftID].name,
        zsun_cp=critical_power,
        zsun_w_prime=anaerobic_work_capacity,
        zsun_ftp_curve_coefficient=coefficient_60min,
        zsun_ftp_curve_exponent=exponent_60min,
        zsun_pull_curve_coefficient=coefficient_pull,
        zsun_pull_curve_exponent=exponent_pull,
        zsun_when_curves_fitted=datetime.now().isoformat(),
    )

    # log pretty summaries

    summary_cp_w_prime  =  f"Critical Power (W) = {round(pi.get_critical_power_watts())}  Anaerobic Work Capacity = {round(pi.get_anaerobic_work_capacity_kj(), 1)}kJ"

    logger.info(f"\n{summary_cp_w_prime}")

    summary_pull = f"TTT pull power (W) (30-60-120 seconds) = {round(pi.get_30sec_pull_watts())} - {round(pi.get_1_minute_pull_watts())} - {round(pi.get_2_minute_pull_watts())}"
    # summary_pull = f"TTT pull power (W) (30-60-120 seconds) = {round(pi.get_30sec_pull_watts())} - {round(pi.get_1_minute_pull_watts())} - {round(pi.get_2_minute_pull_watts())}  [r^2 = {round(r_squared_pull, 2)}]"

    logger.info(f"\n{summary_pull}")

    summary_ftp = f"One hour power zone (W) = {round(pi.get_one_hour_watts())}"
    # summary_ftp = f"One hour power zone (W) = {round(pi.get_one_hour_watts())}  [r^2 = {round(r_squared_60min, 2)}]"

    logger.info(f"\n{summary_ftp}")

    # Plot answers

    xdata_cp = list(x_y_ordinates_for_cp_w_prime.keys())
    ydata_cp = list(x_y_ordinates_for_cp_w_prime.values())

    xdata_pull = list(x_y_ordinates_for_pulling.keys())
    ydata_pull = list(x_y_ordinates_for_pulling.values())

    xdata_ftp = list(x_y_ordinates_for_FTP_60min.keys())
    ydata_ftp = list(x_y_ordinates_for_FTP_60min.values())

    ydata_pred_cp = [value[1] for value in answer_cp.values()]
    ydata_pred_pull = [value[1] for value in answer_pull.values()]
    ydata_pred_ftp = [value[1] for value in answer_60min.values()]

    max_x = max(max(xdata_cp), max(xdata_pull), max(xdata_ftp))
    max_y = max(max(ydata_cp), max(ydata_pull), max(ydata_ftp))
    lim_x = max_x * 1.05
    lim_y = max_y * 1.05

    plt.figure(figsize=(10, 6))
    plt.scatter(xdata_cp, ydata_cp, color='grey', label='anaerobic power zone')
    plt.scatter(xdata_pull, ydata_pull, color='orange', label='TTT pull power curve fit')
    plt.scatter(xdata_ftp, ydata_ftp, color='black', label='one hour power curve fit')
    # plt.plot(xdata_cp, ydata_pred_cp, color='red', label=summary_cp_w_prime)
    plt.plot(xdata_pull, ydata_pred_pull, color='blue', label=summary_pull)
    plt.plot(xdata_ftp, ydata_pred_ftp, color='green', label=summary_ftp)
    plt.xlabel('Duration (minutes)')
    plt.ylabel('ZwiftPower 90-day best graph (Watts)')
    plt.title(f'{dict_of_zsun01_betel_zsunrideritems[zwiftID].name}')
    # Set the x-axis and y-axis limits
    plt.xlim(0, lim_x)
    plt.ylim(0, lim_y)
    ax = plt.gca()  # Get the current axes
    set_x_axis_ticks(ax, int(max_x))  # Set x-axis ticks
    set_y_axis_ticks(ax, int(max_y))  # Set y-axis ticks

    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()


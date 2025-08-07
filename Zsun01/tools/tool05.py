"""
This tool is for iterative development. It follows on from 
Tool03, assuming that the methods and functions tested
there all work correctly to generate a clean ZsunWattsItem from
ZwiftPower 90-day data from DaveK. The tool commences by repeating the steps
of Tool03, which involves reading the raw ZwiftPower 90-day best power data.

For a single rider, it uses machine learning software libraries
to do curve fitting (sklearn and scipy) to model critical_power and
w_prime, model the TTT-pull power curve, and model the one-hour power curve.
It then uses matplotlib.pyplot to display its handiwork. We take a snippet
of the plotted chart to visualise how their ZwiftPower 90-day
data is translated into the power curves used by Brute.

I used this tool iteratively to fine-tune the power curves for a small 
subset of riders, including myself and DaveK. The art of finding the 
ideal windows for datapoints for the three very-different
inverse-exponential power curves is a bit of a black art. I did it
by hand, using the chart produced by this tool hundreds of times! You can 
see the windows I finally settled on in the static methods of the 
ZsunWattsItem where x-y data is exported for each of the three 
windows. The quality of the fit is measured by the 
r-squared value, which is logged to the console. The tool logs a 
summary of the fitted parameters and displays the power-graph for a 
specified rider for visual inspection.

The script performs the following steps:
- Repeats everything that Tool03 does - thus to obtain ZsunWattsItem
  for a small predefined subset of riders.
- Selects a specific rider by Zwift ID for analysis.
- Extracts power-duration data for three modeling zones: critical power
  (CP & W'), TTT pull power, and one-hour (FTP) power.
- Fits mathematical models to each zone using curve fitting techniques to
  estimate physiological parameters such as critical power, anaerobic work
  capacity, and power curve coefficients.
- Instantiates a results object to store the fitted parameters and logs
  summary statistics for each modeled zone.
- Plots the measured and modeled power-duration curves for visual
  inspection.

This tool demonstrates data loading, machine learning for curve fitting,
and visualization for cycling performance analysis using matplotlib.
"""

# import numpy as np
from sklearn.metrics import r2_score
from scipy.optimize import curve_fit
from datetime import datetime
from zsun_rider_item import ZsunItem
from repository_of_scraped_riders import read_zwiftpower_graph_watts_files
from handy_utilities import read_json_dict_of_ZsunDTO, get_test_IDs
import critical_power as cp
import matplotlib.pyplot as plt
from matplot_utilities import set_x_axis_seconds_in_minute_ticks,set_y_axis_units_ticks
from filenames import RIDERS_FILE_NAME
from dirpaths import DATA_DIRPATH, ZWIFTPOWER_GRAPHS_DIRPATH
import logging
logger = logging.getLogger(__name__)


def main():
    zwiftID = davek # choose a rider to model

    dict_of_all_zsunriders = read_json_dict_of_ZsunDTO(RIDERS_FILE_NAME, DATA_DIRPATH)

    test_IDs = get_test_IDs()

    dict_of_zsunwatts_graphs_for_testIDs = read_zwiftpower_graph_watts_files(test_IDs, ZWIFTPOWER_GRAPHS_DIRPATH)

    # model critical_power and w_prime

    x_y_ordinates_for_cp_w_prime = dict_of_zsunwatts_graphs_for_testIDs[zwiftID].export_x_y_ordinates_for_cp_w_prime_modelling()

    critical_power, anaerobic_work_capacity, r_squared_cp, rmse_cp, answer_cp  = cp.do_curve_fit_with_cp_w_prime_model(x_y_ordinates_for_cp_w_prime)

    # model pull power curve

    x_y_ordinates_for_pulling = dict_of_zsunwatts_graphs_for_testIDs[zwiftID].export_x_y_ordinates_for_pull_zone_modelling()

    coefficient_pull, exponent_pull, r_squared_pull, rmse_pull, answer_pull = cp.do_curve_fit_with_decay_model(x_y_ordinates_for_pulling)

    # model ftp curve (one hour power)

    x_y_ordinates_for_FTP_60min = dict_of_zsunwatts_graphs_for_testIDs[zwiftID].export_x_y_ordinates_for_one_hour_zone_modelling()

    coefficient_60min, exponent_60min, r_squared_60min, rmse_60min, answer_60min = cp.do_curve_fit_with_decay_model(x_y_ordinates_for_FTP_60min)

    logger.info("\nModelling completed. Thank you.\n")

    # instantiate a power item to hold the results

    pi = ZsunItem(
        zwift_id=zwiftID,
        name=dict_of_all_zsunriders[zwiftID].name,
        zsun_CP=critical_power,
        zsun_AWC=anaerobic_work_capacity,
        zsun_one_hour_curve_coefficient=coefficient_60min,
        zsun_one_hour_curve_exponent=exponent_60min,
        zsun_TTT_pull_curve_coefficient=coefficient_pull,
        zsun_TTT_pull_curve_exponent=exponent_pull,
        zsun_when_curves_fitted=datetime.now().isoformat(),
    )

    # log pretty summaries

    summary_cp_w_prime  =  f"Critical Power (W) = {round(pi.get_critical_power_watts())}  Anaerobic Work Capacity = {round(pi.get_anaerobic_work_capacity_kj(), 1)}kJ"

    logger.info(f"\n{summary_cp_w_prime}")

    summary_pull = f"TTT pull power (W) (30-60-120-240 seconds) = {round(pi.get_standard_30sec_pull_watts())} - {round(pi.get_standard_1_minute_pull_watts())} - {round(pi.get_standard_2_minute_pull_watts())} - {round(pi.get_standard_4_minute_pull_watts())}"

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
    plt.title(f'{dict_of_all_zsunriders[zwiftID].name}')
    # Set the x-axis and y-axis limits
    plt.xlim(0, lim_x)
    plt.ylim(0, lim_y)
    ax = plt.gca()  # Get the current axes
    set_x_axis_seconds_in_minute_ticks(ax, int(max_x))  # Set x-axis ticks
    set_y_axis_units_ticks(ax, int(max_y))  # Set y-axis ticks

    plt.legend()
    plt.show()

if __name__ == "__main__":
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logging.getLogger("numba").setLevel(logging.ERROR) # numba is noisy at INFO level
    logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

    # Define the riders and their Zwift IDs - we only use one at a time in main()

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
    david_evanetich= '4945836'
    coryc = "5569057"




    main()


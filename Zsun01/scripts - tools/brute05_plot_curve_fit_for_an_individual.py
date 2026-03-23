"""
This tool is for iterative development. It follows on from 
Tool03, assuming that the methods and functions tested
there all work correctly to generate a clean ZwiftPowerFlattened90dayWattsItem from
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
ZwiftPowerFlattened90dayWattsItem where x-y data is exported for each of the three 
windows. The quality of the fit is measured by the 
r-squared value, which is logged to the console. The tool logs a 
summary of the fitted parameters and displays the power-graph for a 
specified rider for visual inspection.

The script performs the following steps:
- Repeats everything that Tool03 does - thus to obtain ZwiftPowerFlattened90dayWattsItem
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
from pathlib import Path

import critical_power as cp
import matplotlib.pyplot as plt
from matplot_utilities import set_x_axis_seconds_in_minute_ticks, set_y_axis_units_ticks
from scipy.optimize import curve_fit #ignore squiggly
from sklearn.metrics import r2_score #ignore squiggly

from constants import ZWIFTPOWER_GRAPH_WINDOW
from jgh_path_helpers import throw_if_any_dirpath_invalid_or_not_exists, throw_if_any_filename_invalid
from storage_config import FILENAME_RIDER_BRUTE_DTO_JSON_DICT, DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES, DIRPATH_RUBBISH_SCRATCHPAD, DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT
from zwiftid_file_reader_sync import read_zwiftpower90daywattsdto_files_to_item_dict_sync
from working_file_read_write import read_file_as_json_dict_of_RiderDTO
from repository_of_team_rosters import RepositoryOfTeamRosters
from rider_brute_item import RiderBruteItem

import time
import logging
from jgh_exceptions import AlertMessageError
from jgh_formatting import get_current_utc_iso8601_timestamp
from jgh_logging import setup_json_logging, log_event
from storage_config import DIRPATH_LOGGING

def plot_curve_fit_for_an_individual():

    try:
        throw_if_any_dirpath_invalid_or_not_exists([Path(DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT), Path(DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES), Path(DIRPATH_RUBBISH_SCRATCHPAD)])
    except Exception as err:
        print(err)
        return

    try:
        throw_if_any_filename_invalid([FILENAME_RIDER_BRUTE_DTO_JSON_DICT])
    except Exception as err:
        print(err)
        return

    test_IDs = RepositoryOfTeamRosters.get_IDs_of_riders_on_a_team(team_name)

    # check to confirm the chosen rider is in the team
    if chosen_zwiftID not in test_IDs:
        print(f"You made a boo-boo. You say you want to work on ZwiftID={chosen_zwiftID}, but he is not on the team you specified. '{team_name}'. We can't go any further until you fix this. ")
        return

    dict_of_zsunwatts_graphs_for_testIDs = read_zwiftpower90daywattsdto_files_to_item_dict_sync(Path(DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES),test_IDs) 

    print(f"\nRead {len(dict_of_zsunwatts_graphs_for_testIDs)} ZwiftPower {ZWIFTPOWER_GRAPH_WINDOW}-best power graph files for team {team_name}.\n")
    # model critical_power and w_prime
    x_y_ordinates_for_cp_w_prime = dict_of_zsunwatts_graphs_for_testIDs[chosen_zwiftID].export_x_y_ordinates_for_cp_w_prime_modelling()
    critical_power, anaerobic_work_capacity, r_squared_cp, rmse_cp, answer_cp  = cp.do_curve_fit_with_cp_w_prime_model(x_y_ordinates_for_cp_w_prime)

    # model pull power curve
    x_y_ordinates_for_pulling = dict_of_zsunwatts_graphs_for_testIDs[chosen_zwiftID].export_x_y_ordinates_for_pull_zone_modelling()
    coefficient_pull, exponent_pull, r_squared_pull, rmse_pull, answer_pull = cp.do_curve_fit_with_decay_model(x_y_ordinates_for_pulling)

    # model ftp curve (one hour power)
    x_y_ordinates_for_FTP_60min = dict_of_zsunwatts_graphs_for_testIDs[chosen_zwiftID].export_x_y_ordinates_for_one_hour_zone_modelling()
    coefficient_60min, exponent_60min, r_squared_60min, rmse_60min, answer_60min = cp.do_curve_fit_with_decay_model(x_y_ordinates_for_FTP_60min)

    print("\nModelling completed. Thank you.\n")

    # instantiate a power item to hold the results
    dict_of_all_zsunriders = read_file_as_json_dict_of_RiderDTO(Path(DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT),FILENAME_RIDER_BRUTE_DTO_JSON_DICT)# we need this to get the rider's name

    pi = RiderBruteItem(
        zwift_id=chosen_zwiftID,
        name=dict_of_all_zsunriders[chosen_zwiftID].name,
        jgh_60_min_curve_coefficient=coefficient_60min,
        jgh_60_min_curve_exponent=exponent_60min,
        jgh_TTT_pull_curve_coefficient=coefficient_pull,
        jgh_TTT_pull_curve_exponent=exponent_pull,
        jgh_when_curves_fitted=get_current_utc_iso8601_timestamp(),
    )

    # log pretty summaries
    summary_pull = f"TTT pull power (W) (30-60-120-240 seconds) = {round(pi.get_proxy_30sec_pull_watts())} - {round(pi.get_proxy_1_minute_pull_watts())} - {round(pi.get_proxy_2_minute_pull_watts())} - {round(pi.get_proxy_4_minute_pull_watts())}"
    print(f"\n{summary_pull}")
    summary_ftp = f"One hour power zone (W) = {round(pi.get_1_hour_curvefit_watts())}"
    print(f"\n{summary_ftp}")

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
    plt.ylabel(f'ZwiftPower {ZWIFTPOWER_GRAPH_WINDOW}-best graph (Watts)')

    plt.title(f'{dict_of_all_zsunriders[chosen_zwiftID].name}')

    # Set the x-axis and y-axis limits
    plt.xlim(0, lim_x)
    plt.ylim(0, lim_y)
    ax = plt.gca()  # Get the current axes
    set_x_axis_seconds_in_minute_ticks(ax, int(max_x))  # Set x-axis ticks
    set_y_axis_units_ticks(ax, int(max_y))  # Set y-axis ticks

    plt.legend()
    plt.show()

#test runner
if __name__ == "__main__":
    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    start_time = time.time()
    try:

        # Define the riders and their Zwift IDs - we only use one at a time. see below
        alex_shiver='2619046'
        anthony_dangelo='7712769'
        barry_b ='5490373'
        bill_henson ='5726145'
        brandi_steeve = "991817"
        bryan_bumpas = "9011"
        ceri_pritchard = '4204538'
        chris_lockwood = "6944221"
        coryc = "5569057"
        dave_k ='3147366'
        david_evanetich='4945836'
        dayton_danielson='172105'
        giao_nguyen = "183277"
        husky ='5134'
        john_h ='1884456'
        josh_n ='2508033'
        ken_chappell='1111583'
        kent_johnson='618585'
        lynsey_s ='383480'
        mark_b ='5530045'
        matt_steeve = "1024413"
        melissa_warwick = "1657744"
        meridith_leubner ="1707548"
        richard_m ='1193'
        scott_m ='11526'
        sean_o_reilly = "7160372"
        selena_shaik = "2682791"
        steve_seiler = "6142432"
        stewart_lalieu = "103825"
        tim_r ='5421258'
        tom_bick ='11741'

        # Define the riders and their Zwift IDs - we only use one at a time. see below
        chosen_zwiftID : str = stewart_lalieu # choose a rider to model
        team_name = "scratchpad" # rider must be on this team otherwise throw exception

        plot_curve_fit_for_an_individual()

        end_time = time.time()
        duration = end_time - start_time

        log_event(
            logger,
            message=f"Main execution completed successfully in {duration:.2f} seconds.",
            level=logging.INFO
        )
        print(f"\nSuccess: Main execution completed successfully in {duration:.2f} seconds.\n")

    except AlertMessageError as alert_err:
        log_event(
            logger,
            message=alert_err.message,
            level=logging.INFO,
            exception=alert_err
        )
        print(f"{alert_err.message}\n")

    except Exception as ex:
        log_event(
            logger,
            message=f"Unhandled Exception: {ex}",
            level=logging.ERROR,
            exception=ex  # Pass the original exception object
        )
        print(f"Unhandled Exception: {ex}\n\nPlease check the logs for details.\n\nDirpath: {DIRPATH_LOGGING}\n")




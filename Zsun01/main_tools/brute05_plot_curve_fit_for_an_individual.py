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
from typing import List, Dict
import matplotlib.pyplot as plt

from matplot_utilities import set_x_axis_seconds_in_minute_ticks, set_y_axis_units_ticks
from scipy.optimize import curve_fit #ignore squiggly
from sklearn.metrics import r2_score #ignore squiggly

from curve_fitting import do_curve_fit_with_cp_w_prime_model, do_curve_fit_with_decay_model 
from zwiftpower_flattened_90_day_watts_item import ZWIFTPOWER_GRAPH_90_OR_30_DAY_WINDOW
from jgh_path_helpers import throw_if_any_dirpath_invalid_or_not_exists, throw_if_any_filename_invalid
from storage_config import FILENAME_RIDER_COMPUTE_DTO_JSON_DICT, DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES, DIRPATH_RUBBISH_SCRATCHPAD, DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT
from zwiftid_file_reader_sync import read_zwiftpower90daywattsdto_files_to_item_dict_sync
from working_file_read_write import read_rider_compute_dict_from_json
from repository_of_team_rosters import RepositoryOfTeamRosters
from rider_compute_item import RiderComputeItem
from zwiftpower_flattened_90_day_watts_dto import ZwiftPowerFlattened90DayWattsDTO

import time
import logging
from jgh_exceptions import AlertMessageError
from jgh_formatting import get_current_utc_iso8601_timestamp
from jgh_logging import setup_json_logging, log_event
from storage_config import DIRPATH_LOGGING

def validate_dirpaths_and_filenames():
    """
    Prepare the environment for plotting curve fits for an individual rider.
    This function checks the validity of required directories and filenames.
    Raises:
        Exception: If any required directory or filename is invalid or does not exist.
    """
    throw_if_any_dirpath_invalid_or_not_exists([
        Path(DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT),
        Path(DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES),
        Path(DIRPATH_RUBBISH_SCRATCHPAD)
    ])
    throw_if_any_filename_invalid([FILENAME_RIDER_COMPUTE_DTO_JSON_DICT])

def validate_that_riders_are_on_team_in_repository(rider_IDs : list[str], team_name : str):
    team_IDs = RepositoryOfTeamRosters.get_IDs_of_riders_on_a_team(team_name)
    for rider in rider_IDs:
        if rider not in team_IDs:
            raise Exception(f"Rider {rider} is not on the team '{team_name}'.")

def load_dict_of_90day_best_graphs_for_team_watts(team_name: str) -> Dict[str, ZwiftPowerFlattened90DayWattsDTO]:
    team_IDs: List[str]= RepositoryOfTeamRosters.get_IDs_of_riders_on_a_team(team_name)
    item_dict =  read_zwiftpower90daywattsdto_files_to_item_dict_sync(Path(DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES), team_IDs)
    print(f"\nRead {len(item_dict)} ZwiftPower {ZWIFTPOWER_GRAPH_90_OR_30_DAY_WINDOW}-best power graph files for team {team_name}.\n")
    return item_dict

def get_rider_nick_name_from_zwiftID(team_name: str, zwiftID: str) -> str:
    nick_name = RepositoryOfTeamRosters.get_rider_nick_name(team_name,zwiftID)
    return nick_name

def plot_curve_fit_chart_for_an_individual(zwiftID: str, rider_name : str, rider_flattened_watts_graph : ZwiftPowerFlattened90DayWattsDTO):

    # model critical_power and w_prime
    x_y_ordinates_for_cp_w_prime = rider_flattened_watts_graph.export_x_y_ordinates_for_cp_w_prime_modelling()
    critical_power, anaerobic_work_capacity, r_squared_cp, rmse_cp, answer_cp  =    do_curve_fit_with_cp_w_prime_model(x_y_ordinates_for_cp_w_prime)

    # model pull power curve
    x_y_ordinates_for_pulling = rider_flattened_watts_graph.export_x_y_ordinates_for_pull_zone_modelling()
    coefficient_pull, exponent_pull, r_squared_pull, rmse_pull, answer_pull = do_curve_fit_with_decay_model(x_y_ordinates_for_pulling)

    # model ftp curve (one hour power)
    x_y_ordinates_for_FTP_60min = rider_flattened_watts_graph.export_x_y_ordinates_for_one_hour_zone_modelling()
    coefficient_60min, exponent_60min, r_squared_60min, rmse_60min, answer_60min = do_curve_fit_with_decay_model(x_y_ordinates_for_FTP_60min)

    print("\nModelling completed. Thank you.\n")

    # instatiiate rider item with modelled curve-fit data
    rider_1 = RiderComputeItem(
        zwift_id=zwiftID,
        name=rider_name,
        jgh_60_min_curve_coefficient=coefficient_60min,
        jgh_60_min_curve_exponent=exponent_60min,
        jgh_TTT_pull_curve_coefficient=coefficient_pull,
        jgh_TTT_pull_curve_exponent=exponent_pull,
        jgh_when_curves_fitted=get_current_utc_iso8601_timestamp(),
    )

    # log pretty summaries
    summary_pull = f"TTT pull power (W) (30-60-120-240 seconds) = {round(rider_1.get_proxy_30sec_pull_watts())} - {round(rider_1.get_proxy_1_minute_pull_watts())} - {round(rider_1.get_proxy_2_minute_pull_watts())} - {round(rider_1.get_proxy_4_minute_pull_watts())}"
    print(f"\n{summary_pull}")
    summary_ftp = f"One hour power (W) = {round(rider_1.get_1_hour_curvefit_watts())}"
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

    # plot scatter chart of raw data
    plt.figure(figsize=(10, 6))
    plt.scatter(xdata_cp, ydata_cp, color='grey', label='anaerobic power zone')
    plt.scatter(xdata_pull, ydata_pull, color='orange', label='TTT pull power curve fit')
    plt.scatter(xdata_ftp, ydata_ftp, color='black', label='one hour power curve fit')

    #plot fitted curves
    plt.plot(xdata_pull, ydata_pred_pull, color='blue', label=summary_pull)
    plt.plot(xdata_ftp, ydata_pred_ftp, color='green', label=summary_ftp)
    plt.xlabel('Duration (minutes)')
    plt.ylabel(f'ZwiftPower {ZWIFTPOWER_GRAPH_90_OR_30_DAY_WINDOW}-best graph (Watts)')

    plt.title(f'{rider_name}')

    # Set the x-axis and y-axis limits
    plt.xlim(0, lim_x)
    plt.ylim(0, lim_y)
    ax = plt.gca()  # Get the current axes
    set_x_axis_seconds_in_minute_ticks(ax, int(max_x))  # Set x-axis ticks
    set_y_axis_units_ticks(ax, int(max_y))  # Set y-axis ticks

    plt.legend()
    plt.show()

def plot_comparative_chart_of_curve_fits_for_list_of_riders(
    list_of_zwift_IDs: List[str],
    list_of_rider_names: List[str],
    list_of_flattened_watts_graphs: List[ZwiftPowerFlattened90DayWattsDTO]
):
    """
    Plots fitted FTP and TTT pull power curves for multiple riders on the same
    chart for side-by-side visual comparison. One colour per rider. Raw scatter
    data is omitted to keep the chart readable.
    """
    # Use a colour cycle so each rider gets a distinct colour
    colour_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']

    fig, ax = plt.subplots(figsize=(12, 7))

    all_x: List[float] = []
    all_y: List[float] = []

    for idx, (zwift_id, rider_name, flattened_watts_graph) in enumerate(
        zip(list_of_zwift_IDs, list_of_rider_names, list_of_flattened_watts_graphs)
    ):
        colour = colour_cycle[idx % len(colour_cycle)]

        # --- fit curves ---
        x_y_cp      = flattened_watts_graph.export_x_y_ordinates_for_cp_w_prime_modelling()
        x_y_pull    = flattened_watts_graph.export_x_y_ordinates_for_pull_zone_modelling()
        x_y_ftp     = flattened_watts_graph.export_x_y_ordinates_for_one_hour_zone_modelling()

        _, _, _, _, answer_cp   = do_curve_fit_with_cp_w_prime_model(x_y_cp)
        coefficient_pull, exponent_pull, _, _, answer_pull = do_curve_fit_with_decay_model(x_y_pull)
        coefficient_ftp,  exponent_ftp,  _, _, answer_ftp  = do_curve_fit_with_decay_model(x_y_ftp)

        # --- build a RiderComputeItem just for the summary labels ---
        rider_item = RiderComputeItem(
            zwift_id=zwift_id,
            name=rider_name,
            jgh_TTT_pull_curve_coefficient=coefficient_pull,
            jgh_TTT_pull_curve_exponent=exponent_pull,
            jgh_60_min_curve_coefficient=coefficient_ftp,
            jgh_60_min_curve_exponent=exponent_ftp,
            jgh_when_curves_fitted=get_current_utc_iso8601_timestamp(),
        )

        summary_ftp  = (f"{rider_name} | 1 hr = {round(rider_item.get_1_hour_curvefit_watts())} W")
        summary_pull = (f"{rider_name} | pull 30-60-120-240 s = "
                        f"{round(rider_item.get_proxy_30sec_pull_watts())} - "
                        f"{round(rider_item.get_proxy_1_minute_pull_watts())} - "
                        f"{round(rider_item.get_proxy_2_minute_pull_watts())} - "
                        f"{round(rider_item.get_proxy_4_minute_pull_watts())} W")

        # --- extract predicted y-values ---
        xdata_pull = list(x_y_pull.keys())
        xdata_ftp  = list(x_y_ftp.keys())

        ydata_pred_pull = [v[1] for v in answer_pull.values()]
        ydata_pred_ftp  = [v[1] for v in answer_ftp.values()]

        # --- plot fitted curves only (solid = FTP, dashed = pull) ---
        ax.plot(xdata_ftp,  ydata_pred_ftp,  color=colour, linestyle='-',  linewidth=2,   label=summary_ftp)
        ax.plot(xdata_pull, ydata_pred_pull,  color=colour, linestyle='--', linewidth=1.5, label=summary_pull)

        # track overall axis extents
        all_x.extend(xdata_pull + xdata_ftp)
        all_y.extend(ydata_pred_pull + ydata_pred_ftp)

    # --- axes, labels, legend ---
    max_x = max(all_x)
    max_y = max(all_y)
    ax.set_xlim(0, max_x * 1.05)
    ax.set_ylim(0, max_y * 1.05)

    set_x_axis_seconds_in_minute_ticks(ax, int(max_x))
    set_y_axis_units_ticks(ax, int(max_y))

    ax.set_xlabel('Duration (minutes)')
    ax.set_ylabel(f'ZwiftPower {ZWIFTPOWER_GRAPH_90_OR_30_DAY_WINDOW}-best graph (Watts)')
    ax.set_title('Comparative Curve Fits')
    ax.legend(fontsize=8, loc='upper right')

    plt.tight_layout()
    plt.show()

#test runner
if __name__ == "__main__":
    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    start_time = time.time()
    try:
        # Catalogue of candidate riders and their Zwift IDs for modelling
        alex_shiver='2619046'
        anthony_dangelo='7712769' # no current data on zr.app
        barry_b ='5490373'
        bill_henson ='5726145'
        brandi_steeve = "991817"
        bryan_bumpas = "9011"
        ceri_pritchard = '4204538'
        chris_lockwood = "6944221" # no current data on zr.app
        coryc = "5569057"
        dave_k ='3147366'
        david_evanetich='4945836'
        dayton_danielson='172105'
        giao_nguyen = "183277"
        husky ='5134'
        john_h ='1884456'
        josh_n ='2508033'
        ken_chappell='1111583' # no current data on zr.app
        kent_johnson='618585'
        lisa_bick = '846200'
        lynsey_s ='383480'
        mark_b ='5530045'
        matt_steeve = "1024413"
        melissa_warwick = "1657744"
        meridith_leubner ="1707548"
        richard_m ='1193' # no current data on zr.app
        scott_m ='11526'
        sean_o_reilly = "7160372" # no current data on zr.app
        selena_shaik = "2682791"  # no current data on zr.app
        steve_seiler = "6142432"
        stewart_lalieu = "103825"
        tim_r ='5421258'
        tom_bick ='11741'

        team_name = "sirius" 
        zwiftIDs_of_riders_to_model : List[str] = [coryc, john_h, melissa_warwick, meridith_leubner, lisa_bick, tom_bick] 

        validate_dirpaths_and_filenames();
        validate_that_riders_are_on_team_in_repository(zwiftIDs_of_riders_to_model, team_name)
        dict_of_90day_best_graphs_for_team_watts = load_dict_of_90day_best_graphs_for_team_watts(team_name) 

        # model a single rider
        zwiftID_rider_1 : str = zwiftIDs_of_riders_to_model[3]  
        flattened_watts_rider_1  = dict_of_90day_best_graphs_for_team_watts[zwiftID_rider_1]
        nick_name_rider_1 = get_rider_nick_name_from_zwiftID(team_name, zwiftID_rider_1)
        plot_curve_fit_chart_for_an_individual(zwiftID_rider_1,nick_name_rider_1, flattened_watts_rider_1)

        # model multiple riders on the same chart for side-by-side visual comparison
        nick_names_of_riders_to_model = [get_rider_nick_name_from_zwiftID(team_name, zwiftID) for zwiftID in zwiftIDs_of_riders_to_model]
        flattened_rider_watts_of_riders_to_model = [dict_of_90day_best_graphs_for_team_watts[zwiftID] for zwiftID in zwiftIDs_of_riders_to_model]
        plot_comparative_chart_of_curve_fits_for_list_of_riders(zwiftIDs_of_riders_to_model, nick_names_of_riders_to_model, flattened_rider_watts_of_riders_to_model)

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




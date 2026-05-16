"""
This little tool is not used directly in the Brute production pipeline.

It is a Mickey Mouse academic tool. This tool simply generates an Excel
file for a visual comparative analysis of zFTP and jgh_one_hour_power.
Thus it compares and contrasts curve-fit model-derived Zsun one-hour
power values with zFTP values from ZwiftRacingApp profiles and the
delta between them. It is of academic interest only. Wide divergence
doesn't really mean anything, it's just interesting to compare Zwift's
inscrutable zFTP with one-hour power. The percentage difference
provides a relative measure of how much the two estimates diverge,
which can be useful for identifying outliers or unusual cases. The time
at which the model curve intersects the zFTP value might or might
not provide insights. In Brute, we make no use of zFTP whatsoever, but
other TTT tools do when calculating things like Intensity Factor (IF).
Brute uses the jgh_one_hour_power as a proxy for FTP in the Intensity
Factor denominator. This tool illuminates the extent to which
divergences between Brute and third party TTT calculators are caused by
the differences highlighted here. For 265 racers in the club, the
deltas range from 28% maximum to 0% minimum, with a median of 2.0% for
the July 2025 data.

The script performs the following steps:
- Configures logging for the application.
- Loads Zwift, ZwiftPower, and ZwiftRacingApp profiles, as well as best
  power data, using a unified data repository.
- Retrieves precomputed power curve fitting results for all available
  riders.
- For each rider, calculates the predicted 40-minute power (as a proxy
  for FTP) using the model, and compares it to the velo_zpftp_watts
  value.
- Computes the absolute and percentage difference between the two FTP
  estimates, and determines the time (in minutes) at which the model
  curve reaches the velo_zpftp_watts value.
- Aggregates demographic, performance, and comparative metrics for each
  rider into a summary item.
- Exports the comparative FTP analysis for all riders to an Excel file
  for further review.

This tool demonstrates data integration, model application, and
comparative analytics for cycling performance data using Python.
"""
from dataclasses import dataclass
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

from jgh_number import safe_divide
from jgh_path_helpers import throw_if_any_dirpath_invalid_or_not_exists, throw_if_any_filename_invalid
from jgh_power_curve_fit_models import solve_decay_model_for_x_numpy
from jgh_read_write import write_dataframe_as_xlsx_file
from storage_config import DIRPATH_ZWIFT_FILES, DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES, DIRPATH_ZWIFTRACINGAPP_FILES
from storage_config import DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES, FILENAME_RIDER_COMPUTE_DTO_JSON_DICT, DIRPATH_RUBBISH_SCRATCHPAD
from working_file_read_write import *
from repository_of_riders import RepositoryOfRiders

import time
import logging
from jgh_exceptions import AlertMessageError
from jgh_logging import setup_json_logging, log_event
from storage_config import DIRPATH_LOGGING


@dataclass()
class DummyItem:

    zwift_id                   : str   = ""    # Zwift ID of the rider
    name                       : str   = ""    # Name of the rider
    gender                     : str   = ""    # Gender of the rider
    age_years                  : float = 0.0   # Age of the rider in years
    jgh_one_hour_power         : float = 0.0
    velo_zpftp_watts           : float = 0.0    #Originates in Zwiftracingapp profile
    delta                      : float = 0.0   # Difference between velo_zpftp_watts and jgh_one_hour_power
    percent                    : float = 0.0   # Percentage difference between velo_zpftp_watts and jgh_one_hour_power
    value_of_curve_x_for_zwiftracingapp_zpFTP_y : float = 0.0   # The x value of the curve fit for the y value of velo_zpftp_watts
    zwift_racing_score         : float   = 0.0     # Zwift racing score
    zwift_cat_open             : str   = ""    # A+, A, B, C, D, E
    velo_rating_30_days        : float = 0.0   # Velo score typically over 1000
    velo_cat_num_30_days       : int   = 0     # Velo rating 1 to 10
    velo_cat_name_30_days    : str   = ""    # Copper, Silver, Gold etc

def run_comparisons_of_ftp_estimates():


    try:
        throw_if_any_dirpath_invalid_or_not_exists([Path(DIRPATH_ZWIFT_FILES),Path(DIRPATH_ZWIFTRACINGAPP_FILES), Path(DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES), Path(DIRPATH_RUBBISH_SCRATCHPAD)])
    except Exception as err:
        print(err)
        return

    try:
        throw_if_any_filename_invalid([FILENAME_RIDER_COMPUTE_DTO_JSON_DICT, output_filename])
    except Exception as err:
        print(err)
        return

   
    repository : RepositoryOfRiders = RepositoryOfRiders()
    test_IDs = None # i.e. will have the effect of populating the repository with all available riders, modify as you please
    repository.populate_repository(test_IDs, DIRPATH_ZWIFT_FILES, DIRPATH_ZWIFTRACINGAPP_FILES, DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES, "") 
    dict_of_curve_fits = repository.do_curve_fitting(test_IDs)

    comparative_FTPs : list[DummyItem] = list()

    for RiderBruteItem in repository.get_dict_of_RiderBruteItem_by_ids(test_IDs).values():
        y_pred = round(RiderBruteItem.get_n_second_curvefit_y_ordinate_watts(2400)) # N.B. note the shift. the closest correlation to zFTP is our 40min
        y_actual = RiderBruteItem.velo_zwiftpower_zFTP_watts
        if y_pred == 0.0 or y_actual == 0 or RiderBruteItem.zwift_racing_score == 0 or RiderBruteItem.velo_rating_30_days == 0:
            continue
        delta = round(y_pred - y_actual)
        percent = abs(round( safe_divide(((y_pred - y_actual) * 100), y_actual)))  # percent difference between zsun one hour power and zwiftracingapp zpFTP
        curve = dict_of_curve_fits[RiderBruteItem.zwift_id]
        curve_x_ordinate = solve_decay_model_for_x_numpy(curve.sixty_min_curve_coefficient, curve.sixty_min_curve_exponent, np.array([y_actual]))
        print(f"zpFTP versus curve-fit 40-minute-power: {round(y_actual)}/{round(y_pred)} delta = {delta} ({percent}%) {RiderBruteItem.name}")

        item = DummyItem(
            zwift_id                                = RiderBruteItem.zwift_id,
            name                                    = RiderBruteItem.name,
            gender                                  = RiderBruteItem.gender,
            age_years                               = RiderBruteItem.age_years,
            jgh_one_hour_power                      = y_pred,
            velo_zpftp_watts                        = y_actual,
            delta                                   = delta,
            percent                                 = percent,
            value_of_curve_x_for_zwiftracingapp_zpFTP_y = round(safe_divide(curve_x_ordinate[0],60)),
            zwift_racing_score                      = RiderBruteItem.zwift_racing_score,
            zwift_cat_open                          = RiderBruteItem.zwift_cat_open,
            velo_rating_30_days                     = RiderBruteItem.velo_rating_30_days,
            velo_cat_num_30_days                    = RiderBruteItem.velo_cat_num_30_days,
            velo_cat_name_30_days                   = RiderBruteItem.velo_cat_name_30_days
        )
        comparative_FTPs.append(item)


    comparative_FTPs.sort(key=lambda x: (x.percent, x.name))

    df = pd.DataFrame([asdict(item) for item in comparative_FTPs])

    write_dataframe_as_xlsx_file(Path(DIRPATH_RUBBISH_SCRATCHPAD), output_filename,df)
    print(f"\n{len(comparative_FTPs)} line items saved to: {DIRPATH_RUBBISH_SCRATCHPAD}/{output_filename}\n")


#test runner
if __name__ == "__main__":
    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    start_time = time.time()
    try:
        output_filename = "comparative_zFTP_vs_zsun_40_min_curvefit_analysis.xlsx"

        run_comparisons_of_ftp_estimates()

        end_time = time.time()
        duration = end_time - start_time

        log_event(
            logger,
            message=f"Main execution completed successfully in {duration:.2f} seconds. All tests executed without error.",
            level=logging.INFO
        )
        print(f"\nSuccess: Main execution completed successfully in {duration:.2f} seconds. All tests executed without error.\n")

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






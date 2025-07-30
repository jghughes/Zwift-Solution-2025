"""
This little tool is not used directly in the Brute production pipeline.

It is a Mickey Mouse academic tool. This tool simply generates an Excel
file for a visual comparative analysis of zFTP and zsun_one_hour_power.
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
Brute uses the zsun_one_hour_power as a proxy for FTP in the Intensity
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
  for FTP) using the model, and compares it to the zwiftracingapp_zpFTP
  value.
- Computes the absolute and percentage difference between the two FTP
  estimates, and determines the time (in minutes) at which the model
  curve reaches the zwiftracingapp_zpFTP value.
- Aggregates demographic, performance, and comparative metrics for each
  rider into a summary item.
- Exports the comparative FTP analysis for all riders to an Excel file
  for further review.

This tool demonstrates data integration, model application, and
comparative analytics for cycling performance data using Python.
"""

import pandas as pd
from dataclasses import asdict
from jgh_number import safe_divide

from scraped_zwift_data_repository import RepositoryForScrapedDataFromDaveK
from handy_utilities import *
from jgh_serialization import *
from jgh_read_write import write_pandas_dataframe_as_xlsx
import numpy as np
from jgh_power_curve_fit_models import solve_decay_model_for_x_numpy

import logging
from jgh_logging import jgh_configure_logging
jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)


@dataclass()
class DummyItem:

    zwift_id                   : str   = ""    # Zwift ID of the rider
    name                       : str   = ""    # Name of the rider
    gender                     : str   = ""    # Gender of the rider
    age_years                  : float = 0.0   # Age of the rider in years
    zsun_one_hour_power         : float = 0.0
    zwiftracingapp_zpFTP       : float = 0.0    #Originates in Zwiftracingapp profile
    delta                      : float = 0.0   # Difference between zwiftracingapp_zpFTP and zsun_one_hour_power
    percent                    : float = 0.0   # Percentage difference between zwiftracingapp_zpFTP and zsun_one_hour_power
    value_of_curve_x_for_zwiftracingapp_zpFTP_y : float = 0.0   # The x value of the curve fit for the y value of zwiftracingapp_zpFTP
    zwift_zrs                  : float   = 0.0     # Zwift racing score
    zwift_cat                  : str   = ""    # A+, A, B, C, D, E
    zwiftracingapp_score       : float = 0.0   # Velo score typically over 1000
    zwiftracingapp_cat_num     : int   = 0     # Velo rating 1 to 10
    zwiftracingapp_cat_name    : str   = ""    # Copper, Silver, Gold etc

def main():
    
    OUTPUT_FILENAME = "comparative_zFTP_vs_one_hour_power_analysis.xlsx"

    OUTPUT_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK_byJgh/zsun_everything_2025-07-08/"
    ZWIFT_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-07-08/zwift/"
    ZWIFTRACINGAPP_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-07-08/zwiftracing-app-post/"
    ZWIFTPOWER_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-07-08/zwiftpower/profile-page/"
    ZWIFTPOWER_GRAPHS_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_2025-07-08/zwiftpower/power-graph-watts/"


    betel_IDs = None
    # betel_IDs = get_test_IDs()

    repository : RepositoryForScrapedDataFromDaveK = RepositoryForScrapedDataFromDaveK()
    repository.populate_repository(betel_IDs, ZWIFT_DIRPATH, ZWIFTRACINGAPP_DIRPATH, ZWIFTPOWER_DIRPATH, ZWIFTPOWER_GRAPHS_DIRPATH) 
    dict_of_curve_fits = repository.get_dict_of_CurveFittingResultItem(betel_IDs)

    comparative_FTPs : list[DummyItem] = list()

    for ZsunItem in repository.get_dict_of_ZsunItem(betel_IDs).values():
        y_pred = round(ZsunItem.get_n_second_watts(2400)) # N.B. note the shift. the closest correlation to zFTP is our 40min
        # y_pred = round(ZsunItem.get_one_hour_watts())
        y_actual = ZsunItem.zwiftracingapp_zpFTP
        if y_pred == 0.0 or y_actual == 0 or ZsunItem.zwift_zrs == 0 or ZsunItem.zwiftracingapp_score == 0:
            continue
        delta = round(y_pred - y_actual)
        percent = abs(round( safe_divide(((y_pred - y_actual) * 100), y_actual)))  # percent difference between zsun one hour power and zwiftracingapp zpFTP
        curve = dict_of_curve_fits[ZsunItem.zwift_id]
        curve_x_ordinate = solve_decay_model_for_x_numpy(curve.one_hour_curve_coefficient, curve.one_hour_curve_exponent, np.array([y_actual]))
        logger.info(f"zpFTP/Zsun one-hour_power: {round(y_actual)}/{round(y_pred)} delta = {delta} ({percent}%) {ZsunItem.name}")

        item = DummyItem(
            zwift_id                                = ZsunItem.zwift_id,
            name                                    = ZsunItem.name,
            gender                                  = ZsunItem.gender,
            age_years                               = ZsunItem.age_years,
            zsun_one_hour_power                           = y_pred,
            zwiftracingapp_zpFTP                    = y_actual,
            delta                                   = delta,
            percent                                 = percent,
            value_of_curve_x_for_zwiftracingapp_zpFTP_y = round(safe_divide(curve_x_ordinate[0],60)),
            zwift_zrs                               = ZsunItem.zwift_zrs,
            zwift_cat                               = ZsunItem.zwift_cat,
            zwiftracingapp_score                    = ZsunItem.zwiftracingapp_score,
            zwiftracingapp_cat_num                  = ZsunItem.zwiftracingapp_cat_num,
            zwiftracingapp_cat_name                 = ZsunItem.zwiftracingapp_cat_name
        )
        comparative_FTPs.append(item)

    df = pd.DataFrame([asdict(item) for item in comparative_FTPs])

    write_pandas_dataframe_as_xlsx(df, OUTPUT_FILENAME, OUTPUT_DIRPATH)
    logger.info(f"\n{len(comparative_FTPs)} line items saved to: {OUTPUT_DIRPATH}/{OUTPUT_FILENAME}\n")





if __name__ == "__main__":
    main()

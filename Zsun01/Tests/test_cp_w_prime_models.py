from typing import List, Tuple, Dict
import numpy as np
from numpy import ndarray
from critical_power import linearize_cp_metrics, make_bestfit_cp_model, deduce_cp_and_w_prime_from_bestfit_model
from tabulate import tabulate

import logging
from jgh_logging import jgh_configure_logging
jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)

tuples_of_duration_and_ave_power = {5: 546.0, 15: 434.0, 30: 425.0, 60: 348.0, 180: 293.0, 300: 292.0, 600: 268.0, 720: 264.0, 900: 255.0, 1200: 254.0, 1800: 252.0, 2400: 244.0}

# Prepare data for table
table_data = []
for duration, ave_power in tuples_of_duration_and_ave_power.items():
    inverse_duration = 1 / duration
    table_data.append([round(duration), round(ave_power), round(inverse_duration,3)])

# Log the table
table = tabulate(table_data, headers=["Duration (s)", "Average Power (W)", "Inverse Duration (1/s)"], tablefmt="grid")
logger.info(f"\n{table}")


inverse_durations_ndarray, avg_powers_ndarray  = linearize_cp_metrics(tuples_of_duration_and_ave_power)

slope, intercept = make_bestfit_cp_model(inverse_durations_ndarray, avg_powers_ndarray )

cp, w_prime = deduce_cp_and_w_prime_from_bestfit_model(slope, intercept)

# log the output
logger.info(f"Slope: {round(slope)}")
logger.info(f"Intercept: {round(intercept)}")
logger.info(f"Critical Power (CP): {round(cp)}")
logger.info(f"Work Capacity Above CP (W'): {round(w_prime)}")

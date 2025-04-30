from datetime import datetime
from tabulate import tabulate
import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray
from cp_watts import do_curve_fit_with_cp_w_prime_model, do_curve_fit_with_decay_model
from handy_utilities import read_dict_of_90day_best_cp_data, write_dict_of_90day_best_cp_data
import logging
from jgh_logging import jgh_configure_logging

def main():
    """
    Process input critical power (CP) data for Zwift riders, perform curve fitting
    using the CP-W' model and the Inverse model, and generate fully populated CP
    data for each rider.

    This script performs the following steps:
    1. Reads input CP data for Zwift riders.
    2. For each rider:
       - Exports raw CP data for curve fitting.
       - Fits the data using the CP-W' model and the Inverse model.
       - Updates the rider's CP data with model parameters (e.g., CP, AWC, constants).
       - Determines the preferred model for each rider.
       - Generates predicted CP data for specified durations.
       - Imports the predicted CP data into the rider's profile.
       - Adds a timestamp indicating when the data was .
    3. Writes the updated CP data for all riders to a JSON file.

    The output file serves as the foundation for subsequent calculations and
    analyses.

    Dependencies:
        - Requires `handy_utilities` for reading and writing CP data.
        - Uses `critical_power_models` for curve fitting and predictions.
        - Requires `matplotlib` for plotting (though not used in this script).

    Constants:
        - Input and output file paths are hardcoded in the script.

    Returns:
        None
    """
    # Configure logging

    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

    riders_cp_data = read_dict_of_90day_best_cp_data("extracted_input_cp_data_for_betelV4.json", "C:/Users/johng/holding_pen/StuffForZsun/Betel/")

    # Process each rider in the riders_cp_data dictionary
    for rider_id, rider_cp_data in riders_cp_data.items():

        # Import raw CP data for best fitting

        raw_xy_data = rider_cp_data.export_zwiftpower_data_for_cp_w_prime_modelling()

        # log pretty table of input data
        # table_data = [
        #     [x, round(y)]
        #     for x, y in raw_xy_data.items()
        # ]
        # headers = ["xdata (s)", "ydata (W)"]
        # logger.debug("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))


        # Perform CP-W' model fitting

        cp_watts, anaerobic_work_capacity, r_squared, rms, answer = do_curve_fit_with_cp_w_prime_model(raw_xy_data)

        # Perform inverse model fitting
        constant, exponent, r_squared2, rms2, answer2 = do_curve_fit_with_decay_model(raw_xy_data)

        # Update the rider's CP data with the model results
        rider_cp_data.cp_watts = cp_watts
        rider_cp_data.critical_power_w_prime= anaerobic_work_capacity
        # model_applied = "critical_power"

        rider_cp_data.ftp_curve_coefficient = constant
        rider_cp_data.ftp_curve_exponent = exponent
        model_applied = "inverse"

        rider_cp_data.model_applied = model_applied


        # Prepare data for the table
        table_data = [
            [x, round(y[0]), round(y[1])]
            for x, y in answer2.items()
        ]
        headers = ["xdata (s)", "ydata (W)", "y_pred (W)"]

        # Log the table
        logger.debug("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))

        # Convert y_pred to a dictionary and import it into the rider's CP data

        y_pred_dict = {int(x): round(y[1], 0) for x, y in answer2.items()}
        rider_cp_data.import_zwiftpower_graph_data(y_pred_dict)
        rider_cp_data. = datetime.now().isoformat()

    # Write the updated CP data for all riders to a file

    write_dict_of_90day_best_cp_data(
        riders_cp_data,
        "populated_cp_data_for_betel_rubbish.json",
        "C:/Users/johng/holding_pen/StuffForZsun/Betel/"
    )

if __name__ == "__main__":
    main()

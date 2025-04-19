from datetime import datetime
from tabulate import tabulate
import matplotlib.pyplot as plt
import numpy as np
from critical_power_models import cp_w_prime_model, inverse_model_numpy, do_modelling_with_cp_w_prime_model, do_modelling_with_inverse_model
from handy_utilities import read_dict_of_cpdata, write_dict_of_cpdata
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
       - Adds a timestamp indicating when the data was generated.
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

    riders_cp_data = read_dict_of_cpdata("input_cp_data_for_betel_from_zwiftpower.json", "C:/Users/johng/holding_pen/StuffForZsun/Betel/")

    # Process each rider in the riders_cp_data dictionary
    for rider_id, rider_cp_data in riders_cp_data.items():
        # Export raw CP data for best fitting
        raw_xy_data = rider_cp_data.export_cp_data_for_best_fit_modelling()

        # Perform CP-W' model fitting
        critical_power, anaerobic_work_capacity, r_squared, rms, answer = do_modelling_with_cp_w_prime_model(raw_xy_data)

        # Perform inverse model fitting
        constant, exponent, r_squared2, rms2, answer2 = do_modelling_with_inverse_model(raw_xy_data)

        # Update the rider's CP data with the model results
        rider_cp_data.critical_power = critical_power
        rider_cp_data.anaerobic_work_capacity = anaerobic_work_capacity
        rider_cp_data.inverse_coefficient = constant
        rider_cp_data.inverse_exponent = exponent

        model_applied = "inverse"

        rider_cp_data.model_applied = model_applied

        # Generate predictions for test x-data
        xdata_test = np.array([
            5, 15, 30, 60, 90, 120, 150, 180, 300, 420, 600, 720, 900, 1200,
            1800, 2400, 3000, 3600, 4500, 5400, 7200, 10800, 14400
        ])

        y_pred = inverse_model_numpy(xdata_test, constant, exponent)

        # Convert y_pred to a dictionary and import it into the rider's CP data
        y_pred_dict = {int(x): round(y, 0) for x, y in zip(xdata_test, y_pred)}
        rider_cp_data.import_cp_data(y_pred_dict)
        # str of timestamp in ISO format
        rider_cp_data.generated = datetime.now().isoformat()

    # Write the updated CP data for all riders to a file
    write_dict_of_cpdata(
        riders_cp_data,
        "populated_cp_data_for_betel_rubbish.json",
        "C:/Users/johng/holding_pen/StuffForZsun/Betel/"
    )

if __name__ == "__main__":
    main()

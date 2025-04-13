from datetime import datetime
from tabulate import tabulate
import matplotlib.pyplot as plt
from power_duration_modelling import cp_w_prime_model, inverse_model, do_modelling_with_cp_w_prime_model, do_modelling_with_inverse_model
from handy_utilities import read_dict_of_zwiftriders, read_dict_of_cpdata, write_dict_of_cpdata
import logging
from jgh_logging import jgh_configure_logging

jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)

logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

# get zwift 90-day rider data

riders = read_dict_of_zwiftriders()
riders_cp_data = read_dict_of_cpdata("extracted_input_cp_data_for_betel.json", "C:/Users/johng/holding_pen/StuffForZsun/Betel/")

# Process each rider in the riders_cp_data dictionary
for rider_id, rider_cp_data in riders_cp_data.items():
    # Export raw CP data for best fitting
    raw_xy_data = rider_cp_data.export_cp_data_for_best_fitting()

    # Perform CP-W' model fitting
    cp, awc, r_squared, answer = do_modelling_with_cp_w_prime_model(raw_xy_data)

    # Perform inverse model fitting
    constant, exponent, r_squared2, answer2 = do_modelling_with_inverse_model(raw_xy_data)

    # Update the rider's CP data with the model results
    rider_cp_data.cp = cp
    rider_cp_data.awc = awc
    rider_cp_data.inverse_const = constant
    rider_cp_data.inverse_exp = exponent

    # Determine the preferred model
    if rider_id == '2508033':  # Example: JoshN prefers the CP model
        model_applied = "cp"
    else:
        model_applied = "inverse"

    rider_cp_data.model_applied = model_applied

    # Generate predictions for test x-data
    xdata_test = [
        5, 15, 30, 60, 90, 120, 150, 180, 300, 420, 600, 720, 900, 1200,
        1800, 2400, 3000, 3600, 4500, 5400, 7200, 10800, 14400
    ]

    if rider_cp_data.model_applied == "cp":
        y_pred = [cp_w_prime_model(x, cp, awc) for x in xdata_test]
    else:
        y_pred = [inverse_model(x, constant, exponent) for x in xdata_test]

    # Convert y_pred to a dictionary and import it into the rider's CP data
    y_pred_dict = {int(x): round(y, 0) for x, y in zip(xdata_test, y_pred)}
    rider_cp_data.import_cp_data(y_pred_dict)
    # str of timestamp in ISO format
    rider_cp_data.generated = datetime.now().isoformat()

# Write the updated CP data for all riders to a file
write_dict_of_cpdata(
    riders_cp_data,
    "populated_cp_data_for_betel.json",
    "C:/Users/johng/holding_pen/StuffForZsun/Betel/"
)
from tabulate import tabulate
from critical_power import do_curve_fit_with_cp_w_prime_model, do_curve_fit_with_decay_model
from handy_utilities import read_dict_of_90day_bestpower_items, write_dict_of_90day_bestpower_items, read_many_zwiftpower_bestpower_files_in_folder, get_betel_zwift_ids

def main():
    # Configure logging
    import logging
    from jgh_logging import jgh_configure_logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)
    logging.getLogger('matplotlib').setLevel(logging.WARNING) #interesting messages, but not a deluge of INFO

    ZSUN01_BETEL_PROFILES_FILE_NAME = "betel_rider_profiles.json"
    ZSUN01_PROJECT_DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

    OUTPUT_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/"
    ZWIFT_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwift/"
    ZWIFTRACINGAPP_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftracing-app-post/"
    ZWIFTPOWER_PROFILES_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/profile-page/"
    ZWIFTPOWER_GRAPHS_DIRPATH = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/zsun_everything_April_2025/zwiftpower/power-graph-watts/"

    betel_IDs = get_betel_zwift_ids()

    dict_of_jghbestpoweritems_for_betel = read_many_zwiftpower_bestpower_files_in_folder(betel_IDs, ZWIFTPOWER_GRAPHS_DIRPATH)

    # Process each rider in the dict_of_jghbestpoweritems_for_betel dictionary
    for my_zwiftID, my_jghbestpoweritem in dict_of_jghbestpoweritems_for_betel.items():

        raw_xy_data = my_jghbestpoweritem.export_x_y_ordinates_for_cp_w_prime_modelling()

        cp_watts, anaerobic_work_capacity, r_squared, rms, answer = do_curve_fit_with_cp_w_prime_model(raw_xy_data)

        constant, exponent, r_squared2, rms2, answer2 = do_curve_fit_with_decay_model(raw_xy_data)

        # Update the rider's CP data with the model results
        my_jghbestpoweritem.cp_watts = cp_watts
        my_jghbestpoweritem.critical_power_w_prime= anaerobic_work_capacity
        # model_applied = "critical_power"

        my_jghbestpoweritem.ftp_curve_coefficient = constant
        my_jghbestpoweritem.ftp_curve_exponent = exponent
        model_applied = "inverse"

        my_jghbestpoweritem.model_applied = model_applied


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
        my_jghbestpoweritem.import_x_y_ordinates(y_pred_dict)

    # Write the updated CP data for all riders to a file

    write_dict_of_90day_bestpower_items(
        dict_of_jghbestpoweritems_for_betel,
        "populated_cp_data_for_betel_rubbish.json",
        "C:/Users/johng/holding_pen/StuffForZsun/Betel/"
    )

if __name__ == "__main__":
    main()

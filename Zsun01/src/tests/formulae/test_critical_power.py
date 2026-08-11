import numpy as np
from tabulate import tabulate

from jgh_curve_fitting import do_curve_fit_with_cp_w_prime_model, do_curve_fit_with_decay_model
from jgh_power_curve_fit_models import cp_w_prime_model_numpy, decay_model_numpy

import time
import logging
from jgh_exceptions import AlertMessageError
from jgh_logging import setup_json_logging, log_event
from storage_config import DIRPATH_LOGGING

def test_cp_w_prime_model_numpy():

    # # a. Test with Valid Inputs (jgh)
    xdata = np.array([30, 300, 1200, 1800, 2400], dtype=np.float64)
    a = 240  # Critical power
    b = 10000  # Anaerobic work capacity
    result = cp_w_prime_model_numpy(xdata, a, b)
    print(f"\nCP-W' Model Result: y_pred\n\n{result}\n")

    # # b. Test with Zero Values in xdata

    # xdata = np.array([0, 30, 60], dtype=np.float64)
    # try:
    #     result = cp_w_prime_model_numpy(xdata, a, b)
    # except ValueError as e:
    #     print(e)     

    # # c. Test with Small Values in xdata

    # xdata = np.array([1e-10, 30, 300], dtype=np.float64)
    # result = cp_w_prime_model_numpy(xdata, a, b)
    # print(result)

def test_decay_model_numpy():

        a = 654.0 # Coefficient
        b = 0.1314 # Negative exponent_ftp

        # # a. Test with Valid Inputs (jgh)
        xdata = np.array([30, 300, 1200, 1800, 2400], dtype=np.float64)
        result = decay_model_numpy(xdata, a, b)
        print(f"\nDecay Model Result: y_pred\n\n{result}\n")

        # # b. Test with Small Values in xdata

        # xdata = np.array([1e-10, 30, 60], dtype=np.float64)
        # result = decay_model_numpy(xdata, a, b)
        # print("Inverse Model Result: small value in xdata inputs")
        # print (f"{result}")

        # # c. Test with Zero Values in xdata

        # xdata = np.array([0, 30, 60], dtype=np.float64)
        # print("Inverse Model Result: zero value in xdata inputs")
        # try:
        #     result = decay_model_numpy(xdata, a, b)
        # except ValueError as e:
        #     print(e)     

def test_do_modelling_with_decay_model():
    # Sample data
    raw_xy_data_cp = {
        30: 425.0,
        300: 292.0,
        1200: 254.0,
        1800: 252.0,
        2400: 244.0
    }

    #do work
    coefficient_ftp, exponent_ftp, r2, rmse_cp, result = do_curve_fit_with_decay_model(raw_xy_data_cp)
    # Prepare data for the summary table
    summary_table = [
        ["Coefficient", round(coefficient_ftp, 4)],
        ["Exponent", round(exponent_ftp, 4)],
        ["R-squared", round(r2, 2)],
        ["RMSE", round(rmse_cp)]
    ]

    # Log the summary table
    print("\nSummary of Decay Model results:\n" + tabulate(summary_table, headers=["Metric", "Value"], tablefmt="simple"))

    # Prepare data for the detailed result table
    result_table = [
        [x, round(y[0]), round(y[1])]
        for x, y in result.items()
    ]
    headers = ["xdata (s)", "ydata (W)", "y_pred (W)"]

    # Log the detailed result table
    print("\n" + tabulate(result_table, headers=headers, tablefmt="simple"))

def test_do_modelling_with_cp_w_prime_model():
    # Sample data
    raw_xy_data_cp = {
        30: 425.0,
        300: 292.0,
        1200: 254.0,
        1800: 252.0,
        2400: 244.0
    }

    #do work
    cp_watts, anaerobic_work_capacity, r2, rmse_cp, result = do_curve_fit_with_cp_w_prime_model(raw_xy_data_cp)

    # Prepare data for the summary table
    summary_table = [
        ["Critical Power (W)", round(cp_watts)],
        ["Anaerobic Work Capacity (kJ)", round(anaerobic_work_capacity)/1000],
        ["R-squared", round(r2, 2)],
        ["RMSE", round(rmse_cp)]
    ]

    # Log the summary table
    print("\nSummary of CP_W_prime model results:\n" + tabulate(summary_table, headers=["Metric", "Value"], tablefmt="simple"))

    # Prepare data for the detailed result table
    result_table = [
        [x, round(y[0]), round(y[1])]
        for x, y in result.items()
    ]
    headers = ["xdata (s)", "ydata (W)", "y_pred (W)"]

    # Log the detailed result table
    print("\n" + tabulate(result_table, headers=headers, tablefmt="simple"))

#test runner
if __name__ == "__main__":
    import logging
    from jgh_exceptions import AlertMessageError
    from jgh_logging import setup_json_logging, log_event
    from storage_config import DIRPATH_LOGGING

    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    try:
        start_time = time.time()
        test_decay_model_numpy()
        test_cp_w_prime_model_numpy()
        test_do_modelling_with_decay_model()
        test_do_modelling_with_cp_w_prime_model()
        end_time = time.time()

        success_msg = f"Success: Main execution completed successfully in {end_time - start_time:.2f} seconds."
        log_event(logger, message=success_msg, level=logging.INFO)
        print(f"\n{success_msg}\n")
    except AlertMessageError as alert_err:
        log_event(logger, message=alert_err.message, level=logging.INFO, exception=alert_err)
        print(f"{alert_err.message}\n")
    except Exception as ex:
        log_event(logger, message=f"Unhandled Exception: {ex}", level=logging.ERROR, exception=ex)  # Pass the original exception object
        print(f"Unhandled Exception: {ex}\n\nPlease check the logs for details.\n\nDirpath: {DIRPATH_LOGGING}\n")

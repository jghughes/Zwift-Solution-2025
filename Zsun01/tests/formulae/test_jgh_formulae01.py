from jgh_formulae01 import solve_for_speed_from_wattage_using_binary_search

import time
import logging
from jgh_exceptions import AlertMessageError
from jgh_logging import setup_json_logging, log_event
from storage_config import DIRPATH_LOGGING


def test00():
    # ZwiftInsider https://zwiftinsider.com/tt-drafting-pd41/ and https://zwiftinsider.com/road-bike-drafting-pd41/ 
    rider_weight: float = 75.0  # kg 
    height_cm: float = 183
    power: float = 300.0  # on a road bike the speed should be 40.19 kph (TT bike 41.83 kph)
    # power: float = 400.0  # on a road bike the speed should be 44.53 kph (TT bike 46.47 kph )

    # for TTT, ZwiftInsider rode bog standard Zwift TT frame with Zipp 808 wheels (weight is a Zwift secret)
    # for road, ZwiftInsider rode bog standard Zwift Carbon road bike frames with Zwift 32mm carbon wheels (weight is a Zwift secret)

    speed_kmh: float = solve_for_speed_from_wattage_using_binary_search(power, rider_weight, height_cm, slope_pc=0.0)

    print(f"Estimated speed: {speed_kmh:.2f} km/h at {power}W on a gradient of 0.0%")

#test runner
if __name__ == "__main__":
    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    start_time = time.time()
    try:

        test00()

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




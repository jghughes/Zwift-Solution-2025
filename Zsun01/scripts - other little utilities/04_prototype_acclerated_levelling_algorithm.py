
import time
import logging

from jgh_formulae10 import calculate_projected_accelerated_level_up

from jgh_exceptions import AlertMessageError
from jgh_logging import setup_json_logging, log_event
from storage_config import DIRPATH_LOGGING


#tests
def main01():

    test_start_level : int = 101
    test_start_rider_score : int = 950_763

    end_level = calculate_projected_accelerated_level_up(test_start_level, test_start_rider_score)

    print(f"Calculated FinalEndLevel = {end_level}")

    return


#test runner
if __name__ == "__main__":
    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    start_time = time.time()
    try:

        print("Starting script...be patient, this may or may not take a while...\n")
        main01()

        end_time = time.time()
        duration = end_time - start_time

        log_event(
            logger,
            message=f"Main execution completed successfully in {duration:.2f} seconds. Script executed without error.",
            level=logging.INFO
        )
        print(f"\nSuccess: Main execution completed successfully in {duration:.2f} seconds. Script executed without error. Check the logs for possible feedback.\n")

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





from pathlib import Path

from storage_config import CONNECTION_STRING_FILENAME, CONNECTION_STRING_DIRPATH
from repository_of_connectionstrings import ConnectionStringRepository
from jgh_read_write import read_text

import time
import logging
from jgh_exceptions import AlertMessageError
from jgh_logging import setup_json_logging, log_event
from storage_config import DIRPATH_LOGGING


def main00():
    try:
        # Step 1: Try show the raw contents of the .txt file containing connection strings
        content: str = read_text(Path(CONNECTION_STRING_DIRPATH),CONNECTION_STRING_FILENAME)
        print(f"text content of {CONNECTION_STRING_FILENAME} containing connection strings: \n{content}")

        # Step 2: Try log the count of cached connection strings
        count = len(ConnectionStringRepository.get_azure_storage_account_connection_strings_for_zsun())
        print(f"\nNumber of connection strings found in {CONNECTION_STRING_FILENAME}: {count}")

        # Step 3: Try retrieve and log the connection string for "customertester"
        conn_str = ConnectionStringRepository.get_azure_storage_account_connection_string("customertester")
        print(f"\nConnection string for 'customertester': {conn_str}")

    except Exception as ex:
        print(f"Error in main00(): {ex}")

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
        main00()
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

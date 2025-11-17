import asyncio
from typing import List

from storage_config import DIRPATH_RUBBISH_SCRATCHPAD
from zwiftid_file_fetcher_async import download_many_files

import time
import logging
from jgh_exceptions import AlertMessageError
from jgh_logging import setup_json_logging, log_event
from storage_config import DIRPATH_LOGGING


# test
async def test01():
    urls: List[str] = [
        "https://data.zsunr.com/riders/json/zwiftpower/zp-club-members.json",
        "https://data.zsunr.com/riders/json/zwift/1193.json",
        "https://data.zsunr.com/riders/json/zwiftpower/power-graph-watts/1193.json",
        "https://data.zsunr.com/riders/json/zwiftracing-app-post/1193.json",
         "malformedurl://customerkelso.blob.core/rubbish/Kelso2016-mtb-Event-03.htm",
    ]
    dest_dir_path = DIRPATH_RUBBISH_SCRATCHPAD 
    dest_folder = "fetch_files_async_tests" 
    max_concurrent = 100

    await download_many_files(urls, dest_dir_path, dest_folder, max_concurrent)

#test runner
if __name__ == "__main__":
    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    start_time = time.time()
    try:

        print("\nstarting tests")
        asyncio.run(test01())
        print("\nfinished tests")

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







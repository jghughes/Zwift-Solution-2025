import asyncio
import time
import logging
from typing import List
from storage_config import DIRPATH_RUBBISH_SCRATCHPAD
from zwiftid_named_file_fetcher import download_and_save_many_files_to_hard_drive_async
from jgh_exceptions import AlertMessageError
from jgh_internet_helpers import throw_if_no_internet_connection
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

    await download_and_save_many_files_to_hard_drive_async(urls, dest_dir_path, dest_folder, max_concurrent)

#main runner
if __name__ == "__main__":
    import logging
    from jgh_exceptions import AlertMessageError
    from jgh_logging import setup_json_logging, log_event
    from storage_config import DIRPATH_LOGGING

    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    try:
        start_time = time.time()
        throw_if_no_internet_connection()

        print("\nstarting tests")
        asyncio.run(test01())
        print("\nfinished tests")
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




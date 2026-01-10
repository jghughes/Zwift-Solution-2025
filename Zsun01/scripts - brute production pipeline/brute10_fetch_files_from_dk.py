import asyncio
import json
import time
from pathlib import Path
from typing import List
from jgh_read_write import read_text, list_files_in_directory
from zwiftid_file_fetcher_async import download_and_save_many_files_to_hard_drive
from jgh_string import  make_pretty_time_from_seconds
from storage_config import URL_OF_CLUB_MEMBERSHIP_LIST, URL_ROOT_FOR_ZWIFT_FILES, URL_ROOT_FOR_ZWIFTPOWER_90_DAY_BEST_FILES, URL_ROOT_FOR_ZWIFTRACINGAPP_FILES

from storage_config import FILENAME_OF_CLUB_MEMBERSHIP_LIST
from storage_config import DIRPATH_CLUB_MEMBERSHIP_LIST, DIRPATH_ZWIFT_FILES, DIRPATH_ZWIFTRACINGAPP_FILES, DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES

# HEAP POWERFUL TOOL
async def go_fetch_thousands_of_files_from_dk_V2() -> None:
    print("\nfetch single file from daveK of active members on discord (he uses this list to scrape files from Zwift, ZwiftPower, and ZwiftRacingApp websites")
    urls_for_dummy_array_of_one_file = [URL_OF_CLUB_MEMBERSHIP_LIST]
    _ = await fetch_and_save_files(
        urls_for_dummy_array_of_one_file,
        DIRPATH_CLUB_MEMBERSHIP_LIST,
        concurrency=1
    )
    json_array_of_zwiftId = read_text( Path(DIRPATH_CLUB_MEMBERSHIP_LIST), FILENAME_OF_CLUB_MEMBERSHIP_LIST)
    array_of_cobbled_together_zwiftId: List[str] = json.loads(json_array_of_zwiftId)
    print(f"\nzwiftIds of active members: {len(array_of_cobbled_together_zwiftId)} (we use these zwiftIDs to look for Zwift, ZwiftPower90Day, and ZwiftRacingApp files on daveK server)")

    print("\nsearch for as many as possible corresponding Zwift files available on daveK server")
    urls_for_zwift_files: List[str] = [f"{URL_ROOT_FOR_ZWIFT_FILES}{id}.json" for id in array_of_cobbled_together_zwiftId]
    _ = await fetch_and_save_files(
        urls_for_zwift_files,
        DIRPATH_ZWIFT_FILES,
        concurrency=5
    )
    print("\nsearch for as many as possible corresponding 90-day best files available on daveK server")
    urls_for_zwiftpower_90_day_best_files: List[str] = [f"{URL_ROOT_FOR_ZWIFTPOWER_90_DAY_BEST_FILES}{id}.json" for id in array_of_cobbled_together_zwiftId]
    _ = await fetch_and_save_files(
        urls_for_zwiftpower_90_day_best_files,
        DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES,
        concurrency=5
    )
    print("\nsearch for as many as possible corresponding ZwiftRacingApp files available on daveK server")
    urls_for_racing_app_files: List[str] = [f"{URL_ROOT_FOR_ZWIFTRACINGAPP_FILES}{id}.json" for id in array_of_cobbled_together_zwiftId]
    _ = await fetch_and_save_files(
        urls_for_racing_app_files,
        DIRPATH_ZWIFTRACINGAPP_FILES,
        concurrency=5
    )

async def fetch_and_save_files(
    list_of_fetch_urls: List[str],
    save_dirpath: str,
    concurrency: int = 5
) -> List[Path]:
    """
    Fetches files from the given URLs and saves them to the specified directory.
    Prints summary information and returns the list of discovered files.

    Args:
        list_of_fetch_urls (List[str]): List of file URLs to download.
        save_dirpath (str): Directory path to save the files.
        save_folder_name (str): Name of the folder for display/logging purposes.
        concurrency (int, optional): Number of concurrent downloads. Defaults to 5.

    Returns:
        List[Path]: List of Path objects for the discovered files.
    """
    start_time = time.time()
    await download_and_save_many_files_to_hard_drive(list_of_fetch_urls, save_dirpath, None, concurrency)
    elapsed = time.time() - start_time

    files_in_save_destination = list_files_in_directory(Path(save_dirpath), "*.json")
    print(f"I/O duration        : {make_pretty_time_from_seconds(elapsed)}")
    print(f"files in save folder: {len(files_in_save_destination)}")
    print(f"save dirpath        : {save_dirpath}")

    return files_in_save_destination




#test runner
if __name__ == "__main__":
    import logging
    from jgh_exceptions import AlertMessageError
    from jgh_logging import setup_json_logging, log_event
    from storage_config import DIRPATH_LOGGING

    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    start_time = time.time()
    try:

        asyncio.run(go_fetch_thousands_of_files_from_dk_V2())

        end_time = time.time()
        duration = end_time - start_time

        log_event(
            logger,
            message=f"Main execution completed successfully in {duration:.2f} seconds. All fetches executed without error.",
            level=logging.INFO
        )
        print(f"\nSuccess: Main execution completed successfully in {duration:.2f} seconds. All fetches executed without error.\n")

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




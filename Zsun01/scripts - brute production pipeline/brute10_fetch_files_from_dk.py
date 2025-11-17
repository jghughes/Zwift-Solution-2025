import asyncio
import json
import time
from pathlib import Path
from typing import List
from jgh_read_write import read_text, list_files_in_directory
from zwiftid_file_fetcher_async import download_many_files
from jgh_string import  make_pretty_time_from_seconds
from storage_config import DIRPATH_ZWIFT, DIRPATH_ZWIFTRACINGAPP, DIRPATH_ZWIFTPOWER, DIRPATH_ZWIFTPOWER_PROFILE_PAGE, DIRPATH_ZWIFTPOWER_90_DAY_BEST

# HEAP POWERFUL TOOL
async def go_fetch_thousands_of_files_from_dk_V2() -> None:
    url_for_club_members_on_zwiftpower = f"https://data.zsunr.com/riders/json/zwiftpower/{_zp_club_members_filename}"
    print("\nfetch single file of club members on ZwiftPower")
    print(f"url: {url_for_club_members_on_zwiftpower}")
    start_time = time.time()
    await download_many_files([url_for_club_members_on_zwiftpower], DIRPATH_ZWIFTPOWER, None)
    elapsed = time.time() - start_time
    text = read_text( Path(DIRPATH_ZWIFTPOWER), _zp_club_members_filename)
    zwiftIDs: List[str] = json.loads(text)
    print(f"number of member IDs in file: {len(zwiftIDs)}")
    print(f"dest dir path: {DIRPATH_ZWIFTPOWER}")
    print(f"dest filename: {_zp_club_members_filename}")
    print(f"fetch complete. elapsed time: {make_pretty_time_from_seconds(elapsed)}")

    print("\nfetch Zwiftracing-app-post profiles")
    url_root_for_zwiftracingapp = "https://data.zsunr.com/riders/json/zwiftracing-app-post/"
    urls: List[str] = [f"{url_root_for_zwiftracingapp}{id}.json" for id in zwiftIDs]
    start_time = time.time()
    await download_many_files(urls, DIRPATH_ZWIFTRACINGAPP, None, 5)
    elapsed = time.time() - start_time
    print(f"dest dir path: {DIRPATH_ZWIFTRACINGAPP}")
    print(f"dest folder: zwiftracing-app-post")
    print(f"fetch complete. elapsed time: {make_pretty_time_from_seconds(elapsed)}")

    print("\nlist files in directory")
    racing_app_files = list_files_in_directory(Path(DIRPATH_ZWIFTRACINGAPP), "*.json")
    print(f"number of RacingApp files: {len(racing_app_files)}")
    zwiftIDs = [file.stem for file in racing_app_files]

    print("\nfetch Zwift profiles")
    url_root_for_zwift = "https://data.zsunr.com/riders/json/zwift/"
    urls: List[str] = [f"{url_root_for_zwift}{id}.json" for id in zwiftIDs]
    start_time = time.time()
    await download_many_files(urls, DIRPATH_ZWIFT, None)
    elapsed = time.time() - start_time
    print(f"dest dir path: {DIRPATH_ZWIFT}")
    print(f"fetch complete. elapsed time: {make_pretty_time_from_seconds(elapsed)}")

    print("\nfetch Zwiftpower profiles")
    url_root_for_zwiftpower = "https://data.zsunr.com/riders/json/zwiftpower/profile-page/"
    urls: List[str] = [f"{url_root_for_zwiftpower}{id}.json" for id in zwiftIDs]
    start_time = time.time()
    await download_many_files(urls, DIRPATH_ZWIFTPOWER_PROFILE_PAGE, None)
    elapsed = time.time() - start_time
    print(f"dest dir path: {DIRPATH_ZWIFTPOWER_PROFILE_PAGE}")
    print(f"fetch complete. elapsed time: {make_pretty_time_from_seconds(elapsed)}")


    print("\nfetch Zwiftpower 90-day best files")
    url_root_for_zwiftpower_90_day_best = "https://data.zsunr.com/riders/json/zwiftpower/power-graph-watts/"
    urls: List[str] = [f"{url_root_for_zwiftpower_90_day_best}{id}.json" for id in zwiftIDs]
    start_time = time.time()
    await download_many_files(urls, DIRPATH_ZWIFTPOWER_90_DAY_BEST, None)
    elapsed = time.time() - start_time
    print(f"dest dir path: {DIRPATH_ZWIFTPOWER_90_DAY_BEST}")
    print(f"dest folder: power-graph-watts")
    print(f"fetch complete. elapsed time: {make_pretty_time_from_seconds(elapsed)}")

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

        _zp_club_members_filename = "zp-club-members.json"
        asyncio.run(go_fetch_thousands_of_files_from_dk_V2())

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




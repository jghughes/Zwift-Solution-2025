import asyncio
import json
import time
from pathlib import Path
from typing import List
from jgh_read_write import read_text, list_files_in_directory
from zwiftid_file_fetcher_async import download_and_save_many_files_to_hard_drive
from jgh_string import  make_pretty_time_from_seconds
from storage_config import DIRPATH_ZWIFT, DIRPATH_ZWIFTRACINGAPP, DIRPATH_ZWIFTPOWER, DIRPATH_ZWIFTPOWER_PROFILE_PAGE, DIRPATH_ZWIFTPOWER_90_DAY_BEST

# HEAP POWERFUL TOOL
async def go_fetch_thousands_of_files_from_dk_V2() -> None:
    url_of_file_of_cobbled_togther_membership_list = f"https://data.zsunr.com/riders/json/zwiftpower/{_filename_of_club_membership_list_cobbled_together_by_daveK}"
    print("\nfetch cobbled-together membership-list file from daveK (which may be massively incomplete or overstated)")
    print(f"url: {url_of_file_of_cobbled_togther_membership_list}")
    start_time = time.time()
    await download_and_save_many_files_to_hard_drive([url_of_file_of_cobbled_togther_membership_list], DIRPATH_ZWIFTPOWER, None) #in this case only one file!
    elapsed = time.time() - start_time
    json_array_of_zwiftId = read_text( Path(DIRPATH_ZWIFTPOWER), _filename_of_club_membership_list_cobbled_together_by_daveK)
    array_of_cobbled_together_zwiftId: List[str] = json.loads(json_array_of_zwiftId)
    print(f"fetch complete: {make_pretty_time_from_seconds(elapsed)}")
    print(f"cobbled_together club members: {len(array_of_cobbled_together_zwiftId)}")
    print(f"cobbled_together filename: {_filename_of_club_membership_list_cobbled_together_by_daveK}")
    print(f"cobbled_together file saved to: {DIRPATH_ZWIFTPOWER}")


    print("\nsearch for as many as possible corresponding Zwift files available on daveK server")
    url_root_for_zwift = "https://data.zsunr.com/riders/json/zwift/"
    urls_for_zwift_files: List[str] = [f"{url_root_for_zwift}{id}.json" for id in array_of_cobbled_together_zwiftId]
    _ = await fetch_and_save_files(
        urls_for_zwift_files,
        DIRPATH_ZWIFT,
        "zwift",
        concurrency=5
    )
    # #NB: important shift. everywhere subsequently we filter to only those with racing app posts, this might be a mistake because many TT riders won't have racing app posts
    # zwiftIDs = [file.stem for file in discovered_racing_app_files]
    print("\nsearch for as many as possible corresponding ZwiftPower files available on daveK server")
    url_root_for_zwiftpower = "https://data.zsunr.com/riders/json/zwiftpower/profile-page/"
    urls_for_zwiftpower_files: List[str] = [f"{url_root_for_zwiftpower}{id}.json" for id in array_of_cobbled_together_zwiftId]
    _ = await fetch_and_save_files(
        urls_for_zwiftpower_files,
        DIRPATH_ZWIFTPOWER,
        "zwiftpower",
        concurrency=5
    )
    print("\nsearch for as many as possible corresponding 90-day best files available on daveK server")
    url_root_for_zwiftpower_90_day_best = "https://data.zsunr.com/riders/json/zwiftpower/power-graph-watts/"
    urls_for_zwiftpower_90_day_best_files: List[str] = [f"{url_root_for_zwiftpower_90_day_best}{id}.json" for id in array_of_cobbled_together_zwiftId]
    _ = await fetch_and_save_files(
        urls_for_zwiftpower_90_day_best_files,
        DIRPATH_ZWIFTPOWER_90_DAY_BEST,
        "power-graph-watts",
        concurrency=5
    )
    print("\nsearch for as many as possible corresponding ZwiftRacing app files available on daveK server")
    url_root_for_zwiftracingapp = "https://data.zsunr.com/riders/json/zwiftracing-app-post/"
    urls_for_racing_app_files: List[str] = [f"{url_root_for_zwiftracingapp}{id}.json" for id in array_of_cobbled_together_zwiftId]
    _ = await fetch_and_save_files(
        urls_for_racing_app_files,
        DIRPATH_ZWIFTRACINGAPP,
        "zwiftracing-app-post",
        concurrency=5
    )

async def fetch_and_save_files(
    list_of_fetch_urls: List[str],
    save_dirpath: str,
    save_folder_name: str,
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

    discovered_files = list_files_in_directory(Path(save_dirpath), "*.json")
    print(f"search complete:: {make_pretty_time_from_seconds(elapsed)}")
    print(f"files discovered: {len(discovered_files)}")
    print(f"save_folder_name: {save_folder_name}")
    print(f"save dirpath: {save_dirpath}")

    return discovered_files




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

        _filename_of_club_membership_list_cobbled_together_by_daveK = "zp-club-members.json"
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




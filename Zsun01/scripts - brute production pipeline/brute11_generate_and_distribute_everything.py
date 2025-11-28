"""
N.B. THIS CONCISE TOOL IS USED DIRECTLY IN THE BRUTE PRODUCTION
PIPELINE. It builds on all the previous tools.

Each time a batch of raw data is received from DaveK, run this generate_everything_and_save_and_upload
to generate a master JSON dictionary file of all actively racing club
members, with all relevant data aggregated in a RiderBruteItem for each
rider. A batch of raw data consists of several thousand files. 
The master JSON dictionary file for July 2025 data contains 431 riders.

Copy the JSON file manually into the data folder in Zsun01,
carefully following the naming convention there and updating
filenames.py accordingly. Older JSON files remain in the data folder
for posterity. 

This tool aggregates, models, and exports comprehensive rider data for
all eligible club members using multiple data sources and power curve
models. As long as the riders are eligible, they are included
regardless of the fidelity of their best fit curves.

The script performs the following steps:
- Configures logging for the application.
- Loads Zwift, ZwiftPower, and ZwiftRacingApp profiles, as well as best
  power data, using a unified data rider_repository.
- Identifies the set of eligible riders with complete and valid data
  across all sources.
- Retrieves and applies precomputed power curve fitting results for
  each rider.
- Constructs a unified rider data object for each member, combining
  demographic, performance, and modeled metrics.
- Filters out riders without valid curve fitting results.
- Exports the full set of rider profiles to both JSON and Excel files
  for use by Brute in production.

This tool demonstrates large-scale data integration, model application,
and dataset preparation for club-level cycling analytics and reporting.
"""
import asyncio
from pathlib import Path
from typing import Callable, Type, Dict, List, Any

import pandas as pd

from jgh_formulae09 import upload_text_to_blob_storage_in_azure
from jgh_path_helpers import throw_if_any_dirpath_invalid_or_not_exists, throw_if_any_filename_invalid
from jgh_read_write import write_excel_file, write_json_file
from jgh_string import make_pretty_count_of_bytes, make_pretty_time_from_seconds
from storage_config import (
    DIRPATH_ZWIFT, DIRPATH_ZWIFTPOWER_PROFILE_PAGE, 
    DIRPATH_ZWIFTPOWER_90_DAY_BEST, DIRPATH_ZWIFTRACINGAPP, 
    DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT,
    DIRPATH_RIDER_BRUTE_DTO,
    DIRPATH_RIDER_STATS_DTO,
    )
from storage_config import (
    FILENAME_RIDER_BRUTE_DTO_JSON_DICT, 
    FILENAME_RIDER_BRUTE_DTO_XLSX_LIST, 
    FILENAME_RIDER_BRUTE_DTO_JSON_LIST,
    FILENAME_RIDER_STATS_DTO_JSON_DICT, 
    FILENAME_RIDER_STATS_DTO_XLSX_LIST, 
    FILENAME_RIDER_STATS_DTO_JSON_LIST,
    AZURE_ACCOUNTNAME_ZSUN, 
    AZURE_CONTAINERNAME_PREPROCESSED, 
    AZURE_BLOBNAME_RIDER_BRUTE_DTO_LIST, 
    AZURE_BLOBNAME_RIDER_BRUTE_DTO_DICT,
    AZURE_BLOBNAME_RIDER_STATS_DTO_LIST, 
    AZURE_BLOBNAME_RIDER_STATS_DTO_DICT,
    )
from repository_of_riders import RepositoryOfRiders
from rider_brute_item import RiderBruteItem
from rider_brute_dto import RiderBruteDtoDictModel, RiderBruteDtoListModel
from rider_stats_item import RiderStatsItem
from rider_stats_dto import RiderStatsDtoDictModel, RiderStatsDtoListModel

import time
import logging
from jgh_exceptions import AlertMessageError

# HEAP POWERFUL TOOL
async def generate_everything_and_save_and_upload():
    print("starting script\n")
    logger = logging.getLogger()

    try:
        throw_if_any_dirpath_invalid_or_not_exists([
            Path(DIRPATH_ZWIFT),
            Path(DIRPATH_ZWIFTRACINGAPP),
            Path(DIRPATH_ZWIFTPOWER_PROFILE_PAGE),
            Path(DIRPATH_ZWIFTPOWER_90_DAY_BEST),
            Path(DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT)]
        )
    except Exception as err:
        logger.error(f"Directory validation error: {err}", exc_info=True)
        print(err)
        return
    try:
        throw_if_any_filename_invalid([
            FILENAME_RIDER_BRUTE_DTO_JSON_DICT, 
            FILENAME_RIDER_BRUTE_DTO_XLSX_LIST]
        )
    except Exception as err:
        logger.error(f"Filename validation error: {err}", exc_info=True)
        print(err)
        return
    print("dir_paths and filenames validated.")
    print("\nTHE MEAT: populate repository of riders.")
    timer_start = time.perf_counter()
    rider_repository: RepositoryOfRiders = RepositoryOfRiders()
    rider_repository.populate_repository(None, DIRPATH_ZWIFT, DIRPATH_ZWIFTRACINGAPP, DIRPATH_ZWIFTPOWER_PROFILE_PAGE, DIRPATH_ZWIFTPOWER_90_DAY_BEST) 
    timer_end = time.perf_counter()
    elapsed = timer_end - timer_start
    print(f"\nrider_repository populated in: {make_pretty_time_from_seconds(elapsed)}")
    print(f"ended up with {len(rider_repository.get_dict_of_RiderBruteItem())} bona fide racers.")

    print("\nTask #1: distributing all the RiderBruteItem records")
    await process_and_distribute_items(
        item_dict=rider_repository.get_dict_of_RiderBruteItem(),
        to_dto_func=RiderBruteItem.to_dataTransferObject,
        dict_model_cls=RiderBruteDtoDictModel,
        list_model_cls=RiderBruteDtoListModel,
        name_field="name_racingapp",
        output_dir=DIRPATH_RIDER_BRUTE_DTO,
        json_dict_filename=FILENAME_RIDER_BRUTE_DTO_JSON_DICT,
        json_list_filename=FILENAME_RIDER_BRUTE_DTO_JSON_LIST,
        excel_filename=FILENAME_RIDER_BRUTE_DTO_XLSX_LIST,
        azure_blob_dict=AZURE_BLOBNAME_RIDER_BRUTE_DTO_DICT,
        azure_blob_list=AZURE_BLOBNAME_RIDER_BRUTE_DTO_LIST,
        logger=logger,
    )

    print("\nTask #2: distributing all the RiderStatsItem records")
    await process_and_distribute_items(
        item_dict=rider_repository.get_dict_of_RiderStatsItem(),
        to_dto_func=RiderStatsItem.to_dataTransferObject,
        dict_model_cls=RiderStatsDtoDictModel,
        list_model_cls=RiderStatsDtoListModel,
        name_field="full_name",
        output_dir=DIRPATH_RIDER_STATS_DTO,
        json_dict_filename=FILENAME_RIDER_STATS_DTO_JSON_DICT,
        json_list_filename=FILENAME_RIDER_STATS_DTO_JSON_LIST,
        excel_filename=FILENAME_RIDER_STATS_DTO_XLSX_LIST,
        azure_blob_dict=AZURE_BLOBNAME_RIDER_STATS_DTO_DICT,
        azure_blob_list=AZURE_BLOBNAME_RIDER_STATS_DTO_LIST,
        logger=logger,
    )

    print("\nwork complete. consult the log files for details.\n")
    print("\nyou may close the app. thank you.\n")


async def process_and_distribute_items(
    item_dict: Dict[str, Any],
    to_dto_func: Callable[[Any], Any],
    dict_model_cls: Type[Any],
    list_model_cls: Type[Any],
    name_field: str,
    output_dir: str,
    json_dict_filename: str,
    json_list_filename: str,
    excel_filename: str,
    azure_blob_dict: str,
    azure_blob_list: str,
    logger: logging.Logger,
):
    try:
        # Serialization
        dto_as_dict_unsorted: Dict[str, Any] = {k: to_dto_func(v) for k, v in item_dict.items()}
        dto_as_dict = dict(sorted(dto_as_dict_unsorted.items(), key=lambda item: getattr(item[1], name_field) or ""))
        asDictModel = dict_model_cls(dto_as_dict)
        dto_as_dict_as_json = asDictModel.model_dump_json(exclude_none=False)

        dto_as_list: List[Any] = list(dto_as_dict.values())
        asListModel = list_model_cls(dto_as_list)
        dto_as_list_as_json = asListModel.model_dump_json(exclude_none=False)
        logger.info(f"Serialized {len(dto_as_dict)} DTOs.")
    except Exception as e:
        logger.error(f"Error during serialization: {e}", exc_info=True)
        raise

    try:
        # Write JSON files
        write_json_file(Path(output_dir), json_dict_filename, dto_as_dict_as_json)
        write_json_file(Path(output_dir), json_list_filename, dto_as_list_as_json)
        logger.info("JSON files written successfully.")
    except Exception as e:
        logger.error(f"Error writing JSON files: {e}", exc_info=True)
        raise

    try:
        # Write Excel file
        dto_dataframe_column_order = list(dto_as_list[0].model_fields.keys())
        dto_dataframe_rows = [dto.model_dump(exclude_none=False) for dto in dto_as_list]
        dto_as_dataframe = pd.DataFrame(dto_dataframe_rows, columns=dto_dataframe_column_order)
        write_excel_file(Path(output_dir), excel_filename, dto_as_dataframe)
        logger.info("Excel file written successfully.")
    except Exception as e:
        logger.error(f"Error writing Excel file: {e}", exc_info=True)
        raise

    try:
        # Upload to Azure
        url_of_uploaded_blob = await upload_text_to_blob_storage_in_azure(
            AZURE_ACCOUNTNAME_ZSUN, AZURE_CONTAINERNAME_PREPROCESSED, azure_blob_dict, dto_as_dict_as_json)
        file_size = make_pretty_count_of_bytes(len(dto_as_dict_as_json.encode('utf-8')))
        logger.info(f"Uploaded {azure_blob_dict} ({file_size}) to: {url_of_uploaded_blob}")

        url_of_uploaded_blob = await upload_text_to_blob_storage_in_azure(
            AZURE_ACCOUNTNAME_ZSUN, AZURE_CONTAINERNAME_PREPROCESSED, azure_blob_list, dto_as_list_as_json)
        file_size = make_pretty_count_of_bytes(len(dto_as_list_as_json.encode('utf-8')))
        logger.info(f"Uploaded {azure_blob_list} ({file_size}) to: {url_of_uploaded_blob}")
    except Exception as e:
        logger.error(f"Error uploading to Azure: {e}", exc_info=True)
        raise




#runner
if __name__ == "__main__":
    from jgh_logging import setup_json_logging, log_event
    from storage_config import DIRPATH_LOGGING
    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    start_time = time.time()
    try:

        asyncio.run(generate_everything_and_save_and_upload())

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



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

Important note about ordering and responsibilities:
- Sorting of domain items and mapping to DTOs is performed by the caller
  (`generate_everything_and_save_and_upload`). This function expects an
  insertion-ordered dict whose values are DTO instances (pydantic models).
- `process_and_distribute_items` is responsible only for building root models
  (dict-root and list-root), writing the JSON/XLSX files and uploading the
  JSON blobs (including dated archive copies) to Azure. It intentionally does
  not perform sorting or domain->DTO mapping; those responsibilities belong
  to the caller so ordering semantics are explicit and under caller control.

This tool demonstrates large-scale data integration, model application,
and dataset preparation for club-level cycling analytics and reporting.
"""
import asyncio
from email import message
from pathlib import Path
from typing import Type, Dict, Any

import pandas as pd
from jgh_formatting import format_timestamp_as_yyyy_mm_dd 
from jgh_formulae09 import upload_text_to_blob_storage_in_azure
from jgh_internet_helpers import throw_if_no_internet_connection
from jgh_path_helpers import throw_if_any_dirpath_invalid_or_not_exists, throw_if_any_filename_invalid
from jgh_read_write import write_dataframe_as_csv_file, write_dataframe_as_xlsx_file, write_text_with_json_file_extension
from jgh_string import make_pretty_count_of_bytes, make_pretty_time_from_seconds
from storage_config import (
    AZURE_CONTAINERNAME_ZSUN_BACK,
    DIRPATH_ZWIFT_FILES, 
    DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES, DIRPATH_ZWIFTRACINGAPP_FILES, 
    DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT,
    DIRPATH_RIDER_BRUTE_DTO,
    DIRPATH_RIDER_STATS_DTO,
    )
from storage_config import (
    FILENAME_RIDER_BRUTE_DTO_JSON_DICT, 
    FILENAME_RIDER_BRUTE_DTO_JSON_LIST,
    FILENAME_RIDER_BRUTE_DTO_XLSX_LIST, 
    FILENAME_RIDER_BRUTE_DTO_CSV_LIST,

    FILENAME_RIDER_STATS_DTO_JSON_DICT, 
    FILENAME_RIDER_STATS_DTO_JSON_LIST,
    FILENAME_RIDER_STATS_DTO_XLSX_LIST, 
    FILENAME_RIDER_STATS_DTO_CSV_LIST,

    FILEPATH_OF_SNAPSHOT_OF_DICT_OF_RIDERSTATSITEM_WHEN_ACCELERATED_LEVELLING_UP_LAUNCHED,

    AZURE_ACCOUNTNAME_ZSUN, 
    AZURE_CONTAINERNAME_ZSUN, 

    AZURE_BLOBNAME_RIDER_BRUTE_DTO_DICT,
    AZURE_BLOBNAME_RIDER_BRUTE_DTO_LIST, 
    AZURE_BLOBNAME_RIDER_BRUTE_DTO_LIST_AS_CSV,

    AZURE_BLOBNAME_RIDER_STATS_DTO_DICT,
    AZURE_BLOBNAME_RIDER_STATS_DTO_LIST, 
    AZURE_BLOBNAME_RIDER_STATS_DTO_LIST_AS_CSV
    )
from repository_of_riders import RepositoryOfRiders
from rider_dataclasses import RiderComputeItem
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
            Path(DIRPATH_ZWIFT_FILES),
            Path(DIRPATH_ZWIFTRACINGAPP_FILES),
            # Path(DIRPATH_ZWIFTPOWER_PROFILE_PAGE),
            Path(DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES),
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
    rider_repository.populate_repository(None, DIRPATH_ZWIFT_FILES, DIRPATH_ZWIFTRACINGAPP_FILES, DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES, FILEPATH_OF_SNAPSHOT_OF_DICT_OF_RIDERSTATSITEM_WHEN_ACCELERATED_LEVELLING_UP_LAUNCHED) 
    timer_end = time.perf_counter()
    elapsed = timer_end - timer_start
    print(f"\nrider_repository populated in: {make_pretty_time_from_seconds(elapsed)}")
    print(f"ended up with {len(rider_repository.get_dict_of_RiderBruteItem())} curve fitted brute riders.")

    print("\nTask #1: distributing all the RiderBruteItem records")

    items_rb = rider_repository.get_dict_of_RiderBruteItem()
    sorted_items_rb = sorted(
        items_rb.items(),
        key=lambda kv: kv[1].get_velo_zwiftpower_zFTP_wkg() if hasattr(kv[1], "get_velo_zwiftpower_zFTP_wkg") else 0.0,
        reverse=True,  # highest w/kg first
    )
    dto_dict_rb = {k: RiderComputeItem.to_dataTransferObject(v) for k, v in sorted_items_rb}
    for row_num, (_, item) in enumerate(dto_dict_rb.items(), start=1):
        item.row = row_num


    await export_and_upload_dtos(
        dto_by_key=dto_dict_rb,
        dict_model_cls=RiderBruteDtoDictModel,
        list_model_cls=RiderBruteDtoListModel,
        output_dir=DIRPATH_RIDER_BRUTE_DTO,
        json_dict_filename=FILENAME_RIDER_BRUTE_DTO_JSON_DICT,
        json_list_filename=FILENAME_RIDER_BRUTE_DTO_JSON_LIST,
        excel_list_filename=FILENAME_RIDER_BRUTE_DTO_XLSX_LIST,
        csv_list_filename=FILENAME_RIDER_BRUTE_DTO_CSV_LIST,
        json_dict_blobname=AZURE_BLOBNAME_RIDER_BRUTE_DTO_DICT,
        json_list_blobname=AZURE_BLOBNAME_RIDER_BRUTE_DTO_LIST,
        csv_list_blobname=AZURE_BLOBNAME_RIDER_BRUTE_DTO_LIST_AS_CSV,
        logger=logger,
    )

    print("\nTask #2: distributing all the RiderStatsItem records")

    def _safe_zwift_zftp_wkg(value_obj: RiderStatsItem) -> float:
        try:
            val = getattr(value_obj, "zwift_zftp_wkg", 0.0)
            if val is None:
                return 0.0
            return float(val)
        except Exception:
            return 0.0

    items_rs = rider_repository.get_dict_of_RiderStatsItem()
    sorted_items_rs = sorted(
        items_rs.items(),
        key=lambda kv: _safe_zwift_zftp_wkg(kv[1]),
        reverse=True,  # highest w/kg first
    )

    dto_dict_rs = {k: RiderStatsItem.to_dataTransferObject(v) for k, v in sorted_items_rs}
    for row_num, (_, item) in enumerate(dto_dict_rs.items(), start=1):
        item.row = row_num

    await export_and_upload_dtos(
        dto_by_key=dto_dict_rs,
        dict_model_cls=RiderStatsDtoDictModel,
        list_model_cls=RiderStatsDtoListModel,
        output_dir          =DIRPATH_RIDER_STATS_DTO,
        json_dict_filename  =FILENAME_RIDER_STATS_DTO_JSON_DICT,
        json_list_filename  =FILENAME_RIDER_STATS_DTO_JSON_LIST,
        excel_list_filename =FILENAME_RIDER_STATS_DTO_XLSX_LIST,
        csv_list_filename   =FILENAME_RIDER_STATS_DTO_CSV_LIST,
        json_dict_blobname  =AZURE_BLOBNAME_RIDER_STATS_DTO_DICT,
        json_list_blobname  =AZURE_BLOBNAME_RIDER_STATS_DTO_LIST,
        csv_list_blobname   =AZURE_BLOBNAME_RIDER_STATS_DTO_LIST_AS_CSV,
        logger=logger,
    )

    print("\nwork complete. consult the log files for details.\nyou may close the app. thank you.")

async def export_and_upload_dtos(
    dto_by_key: Dict[str, Any],
    dict_model_cls: Type[Any],
    list_model_cls: Type[Any],
    output_dir: str,
    json_dict_filename: str,
    json_list_filename: str,
    excel_list_filename: str,
    csv_list_filename : str,
    json_dict_blobname: str,
    json_list_blobname: str,
    csv_list_blobname : str,
    logger: logging.Logger,
):
    """
    Expects `dto_by_key` to be an insertion-ordered dict mapping id -> DTO (pydantic model).
    Serializes DTOs to two JSON formats (dict & list), writes an Excel file, and uploads
    both JSON blobs (and dated archive copies) to Azure.
    """
    try:
        # Basic validation
        if not isinstance(dto_by_key, dict):
            raise TypeError("dto_by_key must be a dict[str, DTO]")

        # Defensive: ensure DTOs provide the pydantic API used below
        for key, dto in dto_by_key.items():
            if not hasattr(dto, "model_dump") or not hasattr(dto, "model_fields"):
                raise TypeError(f"Value for key '{key}' is not a compatible DTO (missing model_dump/model_fields)")

        # Serialize dict-root model (preserves ordering)
        dict_model_instance = dict_model_cls(dto_by_key)
        dto_dict_json = dict_model_instance.model_dump_json(exclude_none=False)

        # Serialize list-root model
        dto_list = list(dto_by_key.values())
        list_model_instance = list_model_cls(dto_list)
        dto_list_json = list_model_instance.model_dump_json(exclude_none=False)

        logger.info(f"Serialized {len(dto_by_key)} DTOs.")
    except Exception as e:
        logger.error(f"Error during serialization: {e}", exc_info=True)
        raise

    try:
        # Write JSON files for dict and list formats
        write_text_with_json_file_extension(Path(output_dir), json_dict_filename, dto_dict_json)
        write_text_with_json_file_extension(Path(output_dir), json_list_filename, dto_list_json)
        print(f"Saved JSON file: {json_dict_filename}")
        print(f"Saved JSON file: {json_list_filename}")
        logger.info("JSON files written successfully.")
    except Exception as e:
        logger.error(f"Error writing JSON files: {e}", exc_info=True)
        raise

    dto_list_dataframe_column_order = list(dto_list[0].model_fields.keys())
    dto_list_dataframe_rows = [dto.model_dump(exclude_none=False) for dto in dto_list]
    dto_list_as_dataframe = pd.DataFrame(dto_list_dataframe_rows, columns=dto_list_dataframe_column_order)
    dto_list_as_csv = dto_list_as_dataframe.to_csv(index=False)  

    try:
        # Write Excel file for list format (dict-root doesn't lend itself to tabular format)
        write_dataframe_as_xlsx_file(Path(output_dir), excel_list_filename, dto_list_as_dataframe)
        print(f"Saved .xlsx file: {excel_list_filename}")
        logger.info("Excel file written successfully.")
    except Exception as e:
        logger.error(f"Error writing .xlsx file: {e}", exc_info=True)
        raise

    try:
        # Write csv file for list format (dict-root doesn't lend itself to tabular format)
        write_dataframe_as_csv_file(Path(output_dir), csv_list_filename, dto_list_as_dataframe)
        print(f"Saved CSV file: {csv_list_filename}")
        logger.info("CSV file written successfully.")
    except Exception as e:
        logger.error(f"Error writing CSV file: {e}", exc_info=True)
        raise

    try:
        throw_if_no_internet_connection()

        # Upload to Azure (current container for live access by all apps that use realtime data)
        url_of_uploaded_blob = await upload_text_to_blob_storage_in_azure(
            AZURE_ACCOUNTNAME_ZSUN, AZURE_CONTAINERNAME_ZSUN, json_dict_blobname, dto_dict_json)
        file_size = make_pretty_count_of_bytes(len(dto_dict_json.encode('utf-8')))
        message = f"Uploaded blob: {url_of_uploaded_blob} ({file_size})"
        print(message)
        logger.info(message)

        url_of_uploaded_blob = await upload_text_to_blob_storage_in_azure(
            AZURE_ACCOUNTNAME_ZSUN, AZURE_CONTAINERNAME_ZSUN, json_list_blobname, dto_list_json)
        file_size = make_pretty_count_of_bytes(len(dto_list_json.encode('utf-8')))
        message2 = f"Uploaded blob: {url_of_uploaded_blob} ({file_size})"
        print(message2)
        logger.info(message2)

        # Upload dated archive copies to Azure (separate container for archival storage, not used by live apps)
        date: str = format_timestamp_as_yyyy_mm_dd()
        archived_dict_blob_name = f"{date}_{json_dict_blobname}"
        archived_list_blob_name = f"{date}_{json_list_blobname}"
        archived_list_blob_as_csv_name = f"{date}_{csv_list_blobname}"

        url_of_uploaded_blob = await upload_text_to_blob_storage_in_azure(
            AZURE_ACCOUNTNAME_ZSUN, AZURE_CONTAINERNAME_ZSUN_BACK, archived_dict_blob_name, dto_dict_json)
        file_size = make_pretty_count_of_bytes(len(dto_dict_json.encode('utf-8')))
        message = f"Uploaded blob: {url_of_uploaded_blob} ({file_size})"
        print(message)
        logger.info(message)

        url_of_uploaded_blob = await upload_text_to_blob_storage_in_azure(
            AZURE_ACCOUNTNAME_ZSUN, AZURE_CONTAINERNAME_ZSUN_BACK, archived_list_blob_name, dto_list_json)
        file_size = make_pretty_count_of_bytes(len(dto_list_json.encode('utf-8')))
        message2 = f"Uploaded blob: {url_of_uploaded_blob} ({file_size})"
        print(message2)
        logger.info(message2)

        url_of_uploaded_blob = await upload_text_to_blob_storage_in_azure(
            AZURE_ACCOUNTNAME_ZSUN, AZURE_CONTAINERNAME_ZSUN_BACK, archived_list_blob_as_csv_name, dto_list_as_csv)
        file_size = make_pretty_count_of_bytes(len(dto_list_as_csv.encode('utf-8')))
        message3 = f"Uploaded blob: {url_of_uploaded_blob} ({file_size})"
        print(message3)
        logger.info(message3)



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

        message = f"Main execution completed successfully in {duration:.2f} seconds."

        log_event(
            logger,
            message=message,
            level=logging.INFO
        )
        print(f"\n{message}\n")

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
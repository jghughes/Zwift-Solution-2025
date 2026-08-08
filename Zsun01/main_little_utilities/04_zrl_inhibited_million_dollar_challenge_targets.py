import asyncio
import json
import time
import logging
from pathlib import Path
from typing import Dict, List

from jgh_azure_storage_service_client import AzureStorageServiceClient
from jgh_formulae03 import order_paceline_by_desired_order_of_riders
from jgh_formulae08 import show_table_of_standard_proxy_speeds_for_all_riders
from jgh_path_helpers import throw_if_any_dirpath_invalid_or_not_exists, throw_if_any_filename_invalid
from jgh_string import make_pretty_count_of_bytes
from repository_of_team_rosters import RepositoryOfTeamRosters
from rider_compute_dto import RiderComputeDTO, RiderComputeDtoListModel
from rider_compute_item import RiderComputeItem
from jgh_exceptions import AlertMessageError
from zwift_id_base import lookup_Items_by_ZwiftID
from storage_config import (
    FILENAME_RIDER_COMPUTE_DTO_JSON_DICT,
    DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT,
    DIRPATH_BRUTE_TTT_DOCS,
    AZURE_ACCOUNTNAME_ZSUN,
    AZURE_CONTAINERNAME_ZSUN,
    AZURE_BLOBNAME_RIDER_COMPUTE_DTO_LIST,)

# HEAP POWERFUL
async def generate_team_targets() -> None:
    print("Tool starting")

    try:
        throw_if_any_dirpath_invalid_or_not_exists([Path(DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT), Path(DIRPATH_BRUTE_TTT_DOCS)])
    except Exception as err:
        print(err)
        return

    try:
        throw_if_any_filename_invalid([FILENAME_RIDER_COMPUTE_DTO_JSON_DICT])
    except Exception as err:
        print(err)
        return

    # ===========================
    print(f"\ndownloading riderDTO from Azure Blob Storage\n   Account: {AZURE_ACCOUNTNAME_ZSUN}\n   Container: {AZURE_CONTAINERNAME_ZSUN}\n   Blob: {AZURE_BLOBNAME_RIDER_COMPUTE_DTO_LIST}")
    # ===========================

    try:
        azure_client = AzureStorageServiceClient()

        blob_as_bytes : bytes = await azure_client.download_block_blob_as_bytes_async(AZURE_ACCOUNTNAME_ZSUN, AZURE_CONTAINERNAME_ZSUN, AZURE_BLOBNAME_RIDER_COMPUTE_DTO_LIST)
        blob_size = make_pretty_count_of_bytes(len(blob_as_bytes))
        # ===========================
        print(f"\ndownloaded {blob_size}")
        # ===========================
        blob_as_text = blob_as_bytes.decode('utf-8')

        something = json.loads(blob_as_text)
        list_of_RiderDTO: List[RiderComputeDTO] = RiderComputeDtoListModel.model_validate(something, strict=True).root
        list_of_RiderItem: List[RiderComputeItem] = [
            RiderComputeItem.from_dataTransferObject(rider_compute_dto)
            for rider_compute_dto in list_of_RiderDTO]

        dict_of_RiderItem: Dict[str, RiderComputeItem] = {
            rider_dataclasses.zwift_id: rider_dataclasses
            for rider_dataclasses in list_of_RiderItem
        }    
        print(f"\ncount of riders: {len(list_of_RiderDTO)}")
    except Exception as e:
        print(f"rider data not obtained.\n - Error message: {e}")
        return

    try:
        full_team_of_riders: List[RiderComputeItem] = lookup_Items_by_ZwiftID(_riderIDs, dict_of_RiderItem, RiderComputeItem)
    except Exception as e:
        print(f"Team '{_team_name}' not found:\n - Error message:\n - {e}")
        return

    riders = order_paceline_by_desired_order_of_riders  (full_team_of_riders)

    show_table_of_standard_proxy_speeds_for_all_riders(riders)

    # ===========================
    print(f"\nTask #1: computing Million Dollar Prize 16 MINUTE 90-day best...\n")
    # ===========================

    for r in riders:
        watts  = r.get_n_second_curvefit_y_ordinate_watts(960) 
        wkg = watts / r.weight_kg if r.weight_kg > 0 else 0.0
        print(f" - {r.name:20} {r.velo_cat_name_30_days:10} {watts:3.0f}w {wkg:4.1f}w/kg")

    print("\nwork complete.\n")
    print("\nyou may close the app. thank you.\n")

if __name__ == "__main__":
    from jgh_logging import setup_json_logging, log_event
    from storage_config import DIRPATH_LOGGING
    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    start_time = time.time()
    try:

        _team_name = "inhibited" 
        _riderIDs: List[str] = RepositoryOfTeamRosters.get_IDs_of_riders_on_a_team(_team_name)

        asyncio.run(generate_team_targets())

        end_time = time.time()
        duration = end_time - start_time

        log_event(
            logger,
            message=f"Main execution completed successfully in {duration:.2f} seconds. All tests executed without error.",
            level=logging.INFO
        )
        print(f"\nSuccess: Main execution completed successfully in {duration:.2f} seconds. All work executed without error.\n")

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





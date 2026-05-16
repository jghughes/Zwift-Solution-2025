"""
Paceline Plan Generation and Analysis Tool for Cycling Teams

This module generates, analyzes, and exports detailed paceline plans for a specified cycling team,
focusing on exertion-constrained and optimal strategies for team time trial (TTT) scenarios.

Key Features:
- Loads and arranges rider data for a given team, supporting multiple rider selection and ordering strategies.
- Computes paceline plans under various pull durations (e.g., 30s, 60s) and exertion constraints.
- Generates advanced paceline solutions for full teams and reduced team sizes (e.g., strongest five or four riders).
- Applies combinatorial optimization to identify balanced, fastest, and high-intensity pacing strategies.
- Summarizes results in display objects and exports individual and consolidated HTML reports.
- Supports automated upload of summary reports to Azure Blob Storage for sharing and review.
- Provides detailed logging and error handling for robust batch execution.

This tool is intended for cycling performance analysts and coaches seeking to optimize TTT strategies
using data-driven, reproducible methods in Python.
"""
import asyncio
import json
from pathlib import Path
from typing import Dict, List

from jgh_azure_storage_service_client import AzureStorageServiceClient
from jgh_formulae02 import (
    arrange_riders_by_velo_rating,
)
from jgh_formulae08 import (
    log_speed_bounds_of_exertion_constrained_paceline_solutions,
)
from jgh_path_helpers import throw_if_any_dirpath_invalid_or_not_exists, throw_if_any_filename_invalid
from jgh_string import make_pretty_count_of_bytes

from zwift_id_base import lookup_Items_by_ZwiftID

from repository_of_team_rosters import RepositoryOfTeamRosters
from rider_brute_dto import RiderBruteDTO, RiderBruteDtoListModel
from rider_compute_item import RiderComputeItem
from storage_config import (
    FILENAME_RIDER_BRUTE_DTO_JSON_DICT,
    DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT,
    DIRPATH_BRUTE_TTT_DOCS,
    AZURE_ACCOUNTNAME_ZSUN,
    AZURE_CONTAINERNAME_ZSUN,
    AZURE_BLOBNAME_RIDER_BRUTE_DTO_LIST,)

import time
import logging
from jgh_exceptions import AlertMessageError


# HEAP POWERFUL
async def generate_team_targets() -> None:
    print("Tool starting")

    try:
        throw_if_any_dirpath_invalid_or_not_exists([Path(DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT), Path(DIRPATH_BRUTE_TTT_DOCS)])
    except Exception as err:
        print(err)
        return

    try:
        throw_if_any_filename_invalid([FILENAME_RIDER_BRUTE_DTO_JSON_DICT])
    except Exception as err:
        print(err)
        return

    # ===========================
    print(f"\ndownloading riderDTO from Azure Blob Storage\n   Account: {AZURE_ACCOUNTNAME_ZSUN}\n   Container: {AZURE_CONTAINERNAME_ZSUN}\n   Blob: {AZURE_BLOBNAME_RIDER_BRUTE_DTO_LIST}")
    # ===========================

    try:
        azure_client = AzureStorageServiceClient()

        blob_as_bytes : bytes = await azure_client.download_block_blob_as_bytes_async(AZURE_ACCOUNTNAME_ZSUN, AZURE_CONTAINERNAME_ZSUN, AZURE_BLOBNAME_RIDER_BRUTE_DTO_LIST)
        blob_size = make_pretty_count_of_bytes(len(blob_as_bytes))
        # ===========================
        print(f"\ndownloaded {blob_size}")
        # ===========================
        blob_as_text = blob_as_bytes.decode('utf-8')

        something = json.loads(blob_as_text)
        list_of_RiderDTO: List[RiderBruteDTO] = RiderBruteDtoListModel.model_validate(something, strict=True).root
        list_of_RiderItem: List[RiderComputeItem] = [
            RiderComputeItem.from_dataTransferObject(rider_brute_dto)
            for rider_brute_dto in list_of_RiderDTO]

        dict_of_RiderItem: Dict[str, RiderComputeItem] = {
            rider_compute_item.zwift_id: rider_compute_item
            for rider_compute_item in list_of_RiderItem
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

    log_speed_bounds_of_exertion_constrained_paceline_solutions(full_team_of_riders)

    # ===========================
    print(f"\nTask #1: computing Million Dollar Prize 16 MINUTE 90-day best...\n")
    # ===========================

    riders = arrange_riders_by_velo_rating(full_team_of_riders)

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





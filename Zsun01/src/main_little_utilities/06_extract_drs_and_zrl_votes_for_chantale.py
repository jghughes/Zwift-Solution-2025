import asyncio
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd
from tabulate import tabulate

from jgh_path_helpers import (
    throw_if_any_dirpath_invalid_or_not_exists,
    throw_if_any_filename_invalid,
)
from jgh_string import format_seconds_to_hh_mm_ss
import json
import time
from pathlib import Path
from typing import List
from jgh_read_write import (
    read_csv_to_dataframe,
    read_excel,
    clean_dataframe_text_column,
)
from jgh_internet_helpers import throw_if_no_internet_connection
from storage_config import (
    AZURE_ACCOUNTNAME_ZSUN,
    AZURE_CONTAINERNAME_BRUTE,
    AZURE_CONTAINERNAME_ZSUN,
    AZURE_BLOBNAME_RIDER_COMPUTE_DTO_LIST,
)
from jgh_azure_storage_service_client import AzureStorageServiceClient
from jgh_string import make_pretty_count_of_bytes
from rider_compute_dto import RiderComputeDTO, RiderComputeDtoListModel
from rider_compute_item import RiderComputeItem

from jgh_string import format_seconds_to_hh_mm_ss
import logging
from jgh_exceptions import AlertMessageError

COLUMNS_TO_KEEP: List[str] = [
    "Zwift ID",
    "Rider Name",
    # "Team_ZRL",
    # "Team_DIRT",
    "Zwift Category",
    # "Max30 vELO Number",
    "Max30 vELO Category",
    "DRS 2026 | US East",
    "DRS 2026 | US West",
    "ZRL US Votes",
    "Assigned DRS Team",
    "Assigned ZRL Team",
]

ABBREVIATED_COLUMN_HEADINGS: Dict[str, str] = {
    "Zwift ID": "ZwiftID",
    "Rider Name": "Name",
    # "Team_ZRL": "Team_ZRL",
    # "Team_DIRT": "Team_DIRT",
    "Zwift Category": "ZRL",
    # "Max30 vELO Number": "vELO_num",
    "Max30 vELO Category": "DRS",
    "DRS 2026 | US East": "..e",
    "DRS 2026 | US West": "..w",
    "ZRL US Votes": "ZRL..US",
    "Assigned DRS Team": "DRS Team",
    "Assigned ZRL Team": "ZRL Team"
}

VOTE_COLUMNS: List[str] = ["DRS 2026 | US East", "DRS 2026 | US West", "ZRL US Votes"]

def validate_dirpaths_and_filenames(dirpath: Path, filename: str, logger: logging.Logger) -> bool:
    """
    Validates that the given directory path exists and the given filename
    is valid. Logs and prints an error and returns False on the first
    failure encountered; returns True if both checks pass.
    """
    try:
        throw_if_any_dirpath_invalid_or_not_exists([Path(dirpath)])
    except Exception as err:
        logger.error(f"Directory validation error: {err}", exc_info=True)
        print(err)
        return False
    try:
        throw_if_any_filename_invalid([filename])
    except Exception as err:
        logger.error(f"Filename validation error: {err}", exc_info=True)
        print(err)
        return False
    print("local dir_paths and filenames validated.")
    return True

def load_raw_voting_poll_data_from_davek_from_csv(dirpath: Path, filename: str, vote_columns: List[str]) -> pd.DataFrame:
    """
    Reads the poll results CSV into a dataframe, cleans the "Rider Name"
    text column. Prints progress messages along the way.
    """
    print(f"\nread single file of poll results listed in: {filename}")
    input_dataframe = read_csv_to_dataframe(dirpath, filename)
    input_dataframe = clean_dataframe_text_column(input_dataframe, "Rider Name") #rinse emojis
    print(f"Total rows found in DaveK 'team builder' tab: {len(input_dataframe)}")
    for vote_column in vote_columns:
        yes_count = (input_dataframe[vote_column] == "Y").sum()
        print(f"Rows with 'Y' in '{vote_column}': {yes_count}")
    total_yes_votes = sum((input_dataframe[vote_column] == "Y").sum() for vote_column in vote_columns)
    print(f"Total count of YES votes: {total_yes_votes}")

    return input_dataframe

def make_dataframe_of_yes_votes_in_america(input_dataframe: pd.DataFrame, vote_columns: List[str], columns_to_keep: List[str]) -> pd.DataFrame:
    """
    Creates a summarized dataframe containing only the rows with "Y" in any
    of the vote columns, keeping only the specified columns, and formatting
    it for pretty printing.
    """
    is_yes_vote_mask = pd.Series(False, index=input_dataframe.index)
    for vote_column in vote_columns:
        is_yes_vote_mask = is_yes_vote_mask | (input_dataframe[vote_column] == "Y")

    answer_df = input_dataframe.loc[is_yes_vote_mask, columns_to_keep].copy()
    return answer_df

async def fetch_live_rider_compute_data() -> Dict[str, RiderComputeItem]:
    """
    Downloads the rider compute DTO list blob from Azure, deserializes it,
    and returns a dict of RiderComputeItem keyed by zwift_id.
    """
    throw_if_no_internet_connection()

    print(f"\nDownloading file from Azure\n   Account: {AZURE_ACCOUNTNAME_ZSUN}\n   Container: {AZURE_CONTAINERNAME_ZSUN}\n   Blob: {AZURE_BLOBNAME_RIDER_COMPUTE_DTO_LIST}")

    azure_client = AzureStorageServiceClient()

    blob_as_bytes: bytes = await azure_client.download_block_blob_as_bytes_async(
        AZURE_ACCOUNTNAME_ZSUN,
        AZURE_CONTAINERNAME_ZSUN,
        AZURE_BLOBNAME_RIDER_COMPUTE_DTO_LIST,
    )
    blob_size = make_pretty_count_of_bytes(len(blob_as_bytes))
    print(f"downloaded : {blob_size}")

    blob_as_text = blob_as_bytes.decode("utf-8")
    something = json.loads(blob_as_text)
    list_of_RiderDTO: List[RiderComputeDTO] = RiderComputeDtoListModel.model_validate(
        something, strict=True
    ).root
    list_of_RiderItem: List[RiderComputeItem] = [
        RiderComputeItem.from_dataTransferObject(rider_compute_dto)
        for rider_compute_dto in list_of_RiderDTO
    ]

    dict_of_RiderItem: Dict[str, RiderComputeItem] = {
        rider_dataclasses.zwift_id: rider_dataclasses
        for rider_dataclasses in list_of_RiderItem
    }
    print(f"count of riders : {len(list_of_RiderDTO)}")

    return dict_of_RiderItem

def abbreviate_column_headings(df: pd.DataFrame, abbreviated_column_headings: dict) -> pd.DataFrame:
    return df.rename(columns=abbreviated_column_headings)

def add_live_compute_item_columns(dict_of_RiderItem: Dict[str, RiderComputeItem], df: pd.DataFrame) -> pd.DataFrame:
    df[["zFTP", "zRS", "vELO_30", "vELO"]] = df["ZwiftID"].apply(lambda zwift_id: pd.Series(
        {
            "zFTP": round(dict_of_RiderItem.get(str(zwift_id), RiderComputeItem()).get_velo_zwiftpower_zFTP_wkg(), 2),
            "zRS": dict_of_RiderItem.get(str(zwift_id), RiderComputeItem()).zwift_racing_score,
            "vELO_30": dict_of_RiderItem.get(str(zwift_id), RiderComputeItem()).velo_rating_30_days,
            "vELO": dict_of_RiderItem.get(str(zwift_id), RiderComputeItem()).velo_cat_num_30_days,
        }
    ))

    def replace_nan_cells_with_blank_for_cleanlier_display(df: pd.DataFrame) -> pd.DataFrame:
        """
        Casts a dataframe to object dtype and replaces NaN/NA values with a
        single space, suitable for pretty-printing with tabulate.
        """
        return df.astype(object).where(df.notna(), " ")        
    
    # df["vELO_num"] = pd.to_numeric(df["vELO_num"], errors="coerce").astype("Int64")
    df.sort_values(by="zFTP", ascending=False)

    answer = replace_nan_cells_with_blank_for_cleanlier_display(df)
    return answer

def change_category_labels_to_series_categories(dict_of_RiderItem: Dict[str, RiderComputeItem], input_dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Looks up each row's "ZwiftID" in dict_of_RiderItem and overwrites the
    "ZRL", and "DRS" cells
    with values computed/read from the rider's get_velo_zwiftpower_zFTP_wkg(),
    and velo_cat_name_30_days respectively. Rows whose
    "ZwiftID" is not found in dict_of_RiderItem are left unchanged. Operates
    on a copy of the DataFrame; the original is left unmodified.
    """
    def compute_zrl_cat_label_from_zftp_wkg(zftp_wkg: float) -> str:
        """
        Maps a zFTP w/kg value to a Zwift Category label using the following bands:
            - "C_STD": zFTP >= 3.08 w/kg (and < 3.36 w/kg)
            - "C_DEV": 2.63 <= zFTP < 3.08 w/kg
            - "D_STD": 2.40 <= zFTP < 2.63 w/kg
            - "D_DEV": zFTP < 2.40 w/kg
        """
        if zftp_wkg >= 4.37:
            return "A_std"
        if zftp_wkg >= 4.2:
            return "A_dev"
        if zftp_wkg >= 3.74:
            return "B_std"
        if zftp_wkg >= 3.36:
            return "B_dev"
        if zftp_wkg >= 3.08:
            return "C_std"
        elif zftp_wkg >= 2.63:
            return "C_dev"
        elif zftp_wkg >= 2.40:
            return "D_std"
        else:
            return "D_dev"

    def compute_drs_cat_label_from_velo_cat_num(velo_cat_num: int) -> str:
        if velo_cat_num == 1 or velo_cat_num == 2:
            return "diamond-ruby"
        elif velo_cat_num == 3 or velo_cat_num == 4:
            return "emerald-sapphire"
        elif velo_cat_num == 5 or velo_cat_num == 6:
            return "amethyst-platinum"
        elif velo_cat_num == 7 or velo_cat_num == 8:
            return "gold-silver"
        elif velo_cat_num == 9 or velo_cat_num == 10:
            return "bronze-copper"
        else:
            return ""

    output_dataframe = input_dataframe.copy()

    for row_index, zwift_id in output_dataframe["ZwiftID"].items():
        rider_compute_item = dict_of_RiderItem.get(str(zwift_id))
        if rider_compute_item is None:
            continue
        zftp_wkg = rider_compute_item.get_velo_zwiftpower_zFTP_wkg()
        output_dataframe.at[row_index, "ZRL"] = (compute_zrl_cat_label_from_zftp_wkg(zftp_wkg))
        output_dataframe.at[row_index, "DRS"] = (compute_drs_cat_label_from_velo_cat_num(rider_compute_item.velo_cat_num_30_days))

    return output_dataframe

def print_table(title: str, df: pd.DataFrame) -> None:
    """
    Prints a title line followed by the dataframe rendered via tabulate
    using the standard "rounded_outline" format with the index shown.
    """
    df = df.copy()
    df.index = range(1, len(df) + 1)
    print(f"\n{title}")
    print(
        "\n"
        + tabulate(
            df,
            headers="keys",
            tablefmt="rounded_outline",
            showindex=True,
        )
    )

def export_dataframe_to_csv(df: pd.DataFrame, dirpath: Path, filename: str) -> None:
    filepath = Path(dirpath, filename)
    df.to_csv(filepath, index=False)
    print(f"Dataframe exported to CSV: {filepath}")

async def main_async():
    print("starting script\n")
    logger = logging.getLogger()

    if not validate_dirpaths_and_filenames(_dirpath, _csv_filename_from_dk, logger):
        return

    input_dataframe_from_dk = load_raw_voting_poll_data_from_davek_from_csv(_dirpath, _csv_filename_from_dk, VOTE_COLUMNS)

    output_frame = make_dataframe_of_yes_votes_in_america(input_dataframe_from_dk, VOTE_COLUMNS, COLUMNS_TO_KEEP)

    print_table("Voting poll data from DaveK (all yes votes for America):", output_frame)

    try:
        dict_of_RiderItem = await fetch_live_rider_compute_data()
    except Exception as e:
        print(f"rider data not obtained.\n - Error message: {e}")
        return


    output_frame = abbreviate_column_headings(output_frame, ABBREVIATED_COLUMN_HEADINGS)

    output_frame = add_live_compute_item_columns(dict_of_RiderItem, output_frame)

    output_frame = change_category_labels_to_series_categories(dict_of_RiderItem, output_frame)

    output_frame = output_frame.sort_values(by=["zFTP", "zRS", "vELO_30"], ascending=[False, False, False])

    print_table("Voting poll data with live compute item columns:", output_frame)

    export_dataframe_to_csv(output_frame, _dirpath, _csv_filename_computed_by_kgh)

# runner
if __name__ == "__main__":
    from jgh_logging import setup_json_logging, log_event
    from storage_config import DIRPATH_LOGGING

    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    try:
        _csv_filename_from_dk = "ZSUNR ZRL and DRS 2026 Polls - Team Builder.csv"
        _dirpath = Path(r"C:\Users\johng\holding_pen\StuffForZsun\2026")

        _csv_filename_computed_by_kgh = "ZSUNR_Fall_2026_teams_for_Chantale.csv"

        start_time = time.time()
        asyncio.run(main_async())
        end_time = time.time()

        success_msg = f"Success: main execution completed successfully in {end_time - start_time:.2f} seconds."
        log_event(logger, message=success_msg, level=logging.INFO)
        print(f"\n{success_msg}\n")
    except AlertMessageError as alert_err:
        log_event(
            logger, message=alert_err.message, level=logging.INFO, exception=alert_err
        )
        print(f"\n{alert_err.message}\n")
    except Exception as ex:
        log_event(
            logger,
            message=f"Unhandled Exception: {ex}",
            level=logging.ERROR,
            exception=ex,
        )  # Pass the original exception object
        print(
            f"\nUnhandled Exception: {ex}\n\nPlease check the logs for details.\n\nDirpath: {DIRPATH_LOGGING}\n\n"
        )

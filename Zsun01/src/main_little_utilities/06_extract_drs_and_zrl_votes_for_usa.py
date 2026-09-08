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
    "Team_ZRL",
    "Team_DIRT",
    "Zwift Category",
    "Max30 vELO Number",
    "Max30 vELO Category",
    # "DRS 2026 | US East",
    # "DRS 2026 | US West",
    # "ZRL US Votes",
]

ABBREVIATED_COLUMN_HEADINGS: Dict[str, str] = {
    "Zwift ID": "ZwiftID",
    "Rider Name": "Name",
    "Team_ZRL": "Team_ZRL",
    "Team_DIRT": "Team_DIRT",
    "Zwift Category": "Cat",
    "Max30 vELO Number": "vELO Num",
    "Max30 vELO Category": "vELO Cat",
    "DRS 2026 | US East": "DRS East",
    "DRS 2026 | US West": "DRS West",
    "ZRL US Votes": "ZRL",
}

VOTE_COLUMNS: List[str] = ["DRS 2026 | US East", "DRS 2026 | US West", "ZRL US Votes"]


def compute_zwift_category_from_zftp_wkg(zftp_wkg: float) -> str:
    """
    Maps a zFTP w/kg value to a Zwift Category label using the following bands:
        - "C_STD": zFTP >= 3.08 w/kg (and < 3.36 w/kg)
        - "C_DEV": 2.63 <= zFTP < 3.08 w/kg
        - "D_STD": 2.40 <= zFTP < 2.63 w/kg
        - "D_DEV": zFTP < 2.40 w/kg
    """
    if zftp_wkg >= 4.37:
        return "A_STD"
    if zftp_wkg >= 4.2:
        return "A_DEV"
    if zftp_wkg >= 3.74:
        return "B_STD"
    if zftp_wkg >= 3.36:
        return "B_DEV"
    if zftp_wkg >= 3.08:
        return "C_STD"
    elif zftp_wkg >= 2.63:
        return "C_DEV"
    elif zftp_wkg >= 2.40:
        return "D_STD"
    else:
        return "D_DEV"


def overwrite_zwift_category_column(
    dict_of_RiderItem: Dict[str, RiderComputeItem], input_dataframe: pd.DataFrame
) -> pd.DataFrame:
    """
    Looks up each row's "Zwift ID" in dict_of_RiderItem and overwrites the
    "Zwift Category", "Max30 vELO Number", and "Max30 vELO Category" cells
    with values computed/read from the rider's get_velo_zwiftpower_zFTP_wkg(),
    velo_cat_num_30_days, and velo_cat_name_30_days respectively. Rows whose
    "Zwift ID" is not found in dict_of_RiderItem are left unchanged. Operates
    on a copy of the DataFrame; the original is left unmodified.
    """
    output_dataframe = input_dataframe.copy()

    for row_index, zwift_id in output_dataframe["Zwift ID"].items():
        rider_compute_item = dict_of_RiderItem.get(str(zwift_id))
        if rider_compute_item is None:
            continue
        zftp_wkg = rider_compute_item.get_velo_zwiftpower_zFTP_wkg()
        output_dataframe.at[row_index, "Zwift Category"] = (
            compute_zwift_category_from_zftp_wkg(zftp_wkg)
        )
        output_dataframe.at[row_index, "Max30 vELO Number"] = (
            rider_compute_item.velo_cat_num_30_days
        )
        output_dataframe.at[row_index, "Max30 vELO Category"] = (
            rider_compute_item.velo_cat_name_30_days
        )

    return output_dataframe


def fill_blank_for_display(df: pd.DataFrame) -> pd.DataFrame:
    """
    Casts a dataframe to object dtype and replaces NaN/NA values with a
    single space, suitable for pretty-printing with tabulate.
    """
    return df.astype(object).where(df.notna(), " ")


def sort_by_category_and_name(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sorts a dataframe by "Zwift Category" ascending, then "Max30 vELO Number"
    descending (since "Max30 vELO Category" is a text label whose alphabetical
    order does not reflect rank), then "Rider Name" ascending.
    """
    return df.sort_values(
        by=["Zwift Category", "Max30 vELO Number", "Rider Name"],
        ascending=[True, True, True],
    )


async def fetch_dict_of_rider_compute_items() -> Dict[str, RiderComputeItem]:
    """
    Downloads the rider compute DTO list blob from Azure, deserializes it,
    and returns a dict of RiderComputeItem keyed by zwift_id.
    """
    throw_if_no_internet_connection()

    print(
        f"\nDownloading file from Azure\n   Account: {AZURE_ACCOUNTNAME_ZSUN}\n   Container: {AZURE_CONTAINERNAME_ZSUN}\n   Blob: {AZURE_BLOBNAME_RIDER_COMPUTE_DTO_LIST}"
    )

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


def finalize_for_display(
    sorted_df: pd.DataFrame, abbreviated_column_headings: Dict[str, str]
) -> pd.DataFrame:
    """
    Takes an already-sorted dataframe and prepares it for pretty-printing:
    renames columns to their abbreviated headings, resets the index to a
    1-based row number, and blanks out NaN/NA values.
    """
    renamed_df = sorted_df.rename(columns=abbreviated_column_headings).reset_index(
        drop=True
    )
    renamed_df.index = renamed_df.index + 1
    return fill_blank_for_display(renamed_df)


def print_table(title: str, df: pd.DataFrame) -> None:
    """
    Prints a title line followed by the dataframe rendered via tabulate
    using the standard "rounded_outline" format with the index shown.
    """
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


def validate_dirpath_and_filename(
    dirpath: Path, filename: str, logger: logging.Logger
) -> bool:
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
    return True


def load_and_clean_input_dataframe(dirpath: Path, filename: str) -> pd.DataFrame:
    """
    Reads the poll results CSV into a dataframe, cleans the "Rider Name"
    text column, and appends a blank "Team" text column. Prints progress
    messages along the way.
    """
    print(f"\nread single file of poll results listed in: {filename}")

    input_dataframe = read_csv_to_dataframe(dirpath, filename)
    input_dataframe = clean_dataframe_text_column(input_dataframe, "Rider Name")
    input_dataframe["Team_ZRL"] = ""
    input_dataframe["Team_DIRT"] = ""

    return input_dataframe


def print_yes_vote_counts(
    input_dataframe: pd.DataFrame, vote_columns: List[str]
) -> None:
    """
    Prints the count of "Y" values in each of the given vote columns.
    """
    for vote_column in vote_columns:
        yes_count = (input_dataframe[vote_column] == "Y").sum()
        print(f"Number of rows with 'Y' in '{vote_column}': {yes_count}")


def compute_yes_vote_masks(
    input_dataframe: pd.DataFrame, vote_columns: List[str]
) -> "tuple[pd.Series, pd.Series]":
    """
    Computes two row masks:
        - is_yes_vote_mask: rows with "Y" in any of the given vote columns
        - is_further_reduced_mask: the above, further restricted to rows in
          Zwift Category "C"/"D" or with a Max30 vELO Number between 7 and 10
    """
    velo_number_numeric = pd.to_numeric(
        input_dataframe["Max30 vELO Number"], errors="coerce"
    )

    is_yes_vote_mask = pd.Series(False, index=input_dataframe.index)
    for vote_column in vote_columns:
        is_yes_vote_mask = is_yes_vote_mask | (input_dataframe[vote_column] == "Y")

    is_low_category_or_borderline_velo = input_dataframe["Zwift Category"].isin(
        ["C", "D"]
    ) | velo_number_numeric.between(7, 10)
    is_further_reduced_mask = is_yes_vote_mask & is_low_category_or_borderline_velo

    return is_yes_vote_mask, is_further_reduced_mask


def print_basic_vote_tables(
    input_dataframe: pd.DataFrame,
    is_yes_vote_mask: pd.Series,
    is_further_reduced_mask: pd.Series,
    columns_to_keep: List[str],
    abbreviated_column_headings: Dict[str, str],
) -> None:
    """
    Builds and prints the "all yes votes" and "further reduced" display
    tables, sorted by category and rider name.
    """

    def build_display_dataframe(mask: pd.Series) -> pd.DataFrame:
        reduced = input_dataframe.loc[mask, columns_to_keep].copy()
        reduced["Max30 vELO Number"] = pd.to_numeric(
            reduced["Max30 vELO Number"], errors="coerce"
        ).astype("Int64")
        sorted_df = sort_by_category_and_name(reduced)
        return finalize_for_display(sorted_df, abbreviated_column_headings)

    print(f"Number of rows in reduced dataframe: {is_yes_vote_mask.sum()}")
    display_dataframe = build_display_dataframe(is_yes_vote_mask)
    print_table("All yes votes", display_dataframe)

    print(
        f"\nNumber of rows in further reduced dataframe: {is_further_reduced_mask.sum()}"
    )
    further_reduced_display_dataframe = build_display_dataframe(is_further_reduced_mask)
    print_table("Further reduced dataframe", further_reduced_display_dataframe)


def enrich_with_live_rider_data_and_print(
    input_dataframe: pd.DataFrame,
    is_further_reduced_mask: pd.Series,
    columns_to_keep: List[str],
    abbreviated_column_headings: Dict[str, str],
    dict_of_RiderItem: Dict[str, RiderComputeItem],
)  -> pd.DataFrame:
    """
    Appends live zFTP/zRS/vELO_30 metrics and a recomputed Zwift Category to
    the further-reduced rows, then prints the result sorted by descending
    zFTP and again sorted by descending vELO_30.
    """

    def get_live_rider_metrics_for_row(zwift_id: Any) -> pd.Series:
        rider_compute_item = dict_of_RiderItem.get(str(zwift_id))
        if rider_compute_item is None:
            return pd.Series({"zFTP": 0.0, "zRS": 0.0, "vELO_30": 0.0})
        return pd.Series(
            {
                "zFTP": round(rider_compute_item.get_velo_zwiftpower_zFTP_wkg(), 2),
                "zRS": rider_compute_item.zwift_racing_score,
                "vELO_30": rider_compute_item.velo_rating_30_days,
            }
        )

    further_reduced_sorted = input_dataframe.loc[
        is_further_reduced_mask, columns_to_keep
    ].copy()
    further_reduced_sorted["Max30 vELO Number"] = pd.to_numeric(
        further_reduced_sorted["Max30 vELO Number"], errors="coerce"
    ).astype("Int64")
    further_reduced_sorted[["zFTP", "zRS", "vELO_30"]] = further_reduced_sorted[
        "Zwift ID"
    ].apply(get_live_rider_metrics_for_row)

    further_reduced_sorted = overwrite_zwift_category_column(
        dict_of_RiderItem, further_reduced_sorted
    )

    by_zftp = further_reduced_sorted.sort_values(by="zFTP", ascending=False)
    by_zftp_display_dataframe = finalize_for_display(
        by_zftp, abbreviated_column_headings
    )
    print_table(
        f"Further reduced dataframe (sorted by descending zFTP w/kg): {is_further_reduced_mask.sum()}",
        by_zftp_display_dataframe,
    )

    by_velo_30 = further_reduced_sorted.sort_values(by="vELO_30", ascending=False)
    by_velo_30_display_dataframe = finalize_for_display(
        by_velo_30, abbreviated_column_headings
    )
    print_table(
        f"Further reduced dataframe (sorted by descending vELO_30): {is_further_reduced_mask.sum()}",
        by_velo_30_display_dataframe,
    )
    return by_velo_30_display_dataframe

def export_dataframe_to_csv(df: pd.DataFrame, dirpath: Path, filename: str) -> None:
    filepath = Path(dirpath, filename)
    df.to_csv(filepath, index=False)
    print(f"Dataframe exported to CSV: {filepath}")


async def extract_list_of_yes_votes():
    print("starting script\n")
    logger = logging.getLogger()

    if not validate_dirpath_and_filename(_dirpath, _csv_filename_from_dk, logger):
        return
    print("local dir_paths and filenames validated.")

    input_dataframe = load_and_clean_input_dataframe(_dirpath, _csv_filename_from_dk)
    print(f"Total number of rows found: {len(input_dataframe)}")

    print_yes_vote_counts(input_dataframe, VOTE_COLUMNS)

    is_yes_vote_mask, is_further_reduced_mask = compute_yes_vote_masks(
        input_dataframe, VOTE_COLUMNS
    )

    print_basic_vote_tables(
        input_dataframe,
        is_yes_vote_mask,
        is_further_reduced_mask,
        COLUMNS_TO_KEEP,
        ABBREVIATED_COLUMN_HEADINGS,
    )

    try:
        dict_of_RiderItem = await fetch_dict_of_rider_compute_items()
    except Exception as e:
        print(f"rider data not obtained.\n - Error message: {e}")
        return

    dataframe_to_export = enrich_with_live_rider_data_and_print(
        input_dataframe,
        is_further_reduced_mask,
        COLUMNS_TO_KEEP,
        ABBREVIATED_COLUMN_HEADINGS,
        dict_of_RiderItem,
    )

    export_dataframe_to_csv(dataframe_to_export, _dirpath, _csv_filename_computed_by_kgh)



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
        asyncio.run(extract_list_of_yes_votes())
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

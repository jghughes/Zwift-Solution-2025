# Diagnostic utilities for RepositoryOfRiders.
# Not used in the production pipeline. Intended for testing, exploration, and data quality checks.

from typing import Dict

import pandas as pd

from zwift_item import ZwiftItem
from zwiftracingapp_item import ZwiftRacingAppItem
from zwiftpower_flattened_90_day_watts_item import ZwiftPowerFlattened90dayWattsItem


# Column name constants shared across all diagnostic functions
COL_ZWIFT_ID                   = "zwift_id"
COL_IN_SAMPLE1                 = "in_sample1"
COL_IN_SAMPLE2                 = "in_sample2"
COL_IN_ZWIFT                   = "zwift"
COL_IN_ZWIFTPOWER              = "zwiftpower"
COL_IN_ZWIFTPOWER_WATTS_GRAPHS = "zwiftpower_90_day_watts"
COL_IN_ZWIFTRACINGAPP          = "zwiftracingapp"


def create_union_of_sets_as_dataframe(
    dict_of_ZwiftItem: Dict[str, ZwiftItem],
    dict_of_ZwiftRacingAppItem: Dict[str, ZwiftRacingAppItem],
    dict_of_ZwiftPower90dayWattsItem: Dict[str, ZwiftPowerFlattened90dayWattsItem],
    sample1: list[str],
    sample2: list[str],
) -> pd.DataFrame:
    """
    Returns a pandas DataFrame representing the union of Zwift IDs found across all main datasets
    (Zwift, ZwiftRacingApp, ZwiftPower 90-day power graphs) and the provided sample lists.

    Each row corresponds to a unique Zwift ID and indicates its presence ("y" or "n") in each dataset
    and in the sample lists.

    Args:
        dict_of_ZwiftItem (Dict[str, ZwiftItem]):
            Dictionary of ZwiftItems keyed by zwift_id.
        dict_of_ZwiftRacingAppItem (Dict[str, ZwiftRacingAppItem]):
            Dictionary of ZwiftRacingAppItems keyed by zwift_id.
        dict_of_ZwiftPower90dayWattsItem (Dict[str, ZwiftPowerFlattened90dayWattsItem]):
            Dictionary of ZwiftPowerFlattened90dayWattsItems keyed by zwift_id.
        sample1 (list[str]):
            Optional list of Zwift IDs to include in the union and mark membership.
        sample2 (list[str]):
            Optional second list of Zwift IDs to include in the union and mark membership.

    Returns:
        pd.DataFrame: DataFrame with columns for Zwift ID, sample membership, and dataset membership.
        Membership is indicated by "y" (present) or "n" (absent) for each column.
    """

    answer: list[tuple[str, str, str, str, str, str]] = []

    superset_of_zwiftID = (
        set(sample1) |
        set(sample2) |
        set(dict_of_ZwiftItem.keys()) |
        set(dict_of_ZwiftRacingAppItem.keys()) |
        set(dict_of_ZwiftPower90dayWattsItem.keys())
    )

    print(f"Total unique Zwift IDs in union: {len(superset_of_zwiftID)}")

    for key in superset_of_zwiftID:
        row = (
            key,
            "y" if key in sample1 else "n",
            "y" if key in sample2 else "n",
            "y" if key in dict_of_ZwiftItem else "n",
            "y" if key in dict_of_ZwiftRacingAppItem else "n",
            "y" if key in dict_of_ZwiftPower90dayWattsItem else "n",
        )
        answer.append(row)

    answer.sort(key=lambda x: x[0])

    return pd.DataFrame(answer, columns=[
        COL_ZWIFT_ID,
        COL_IN_SAMPLE1,
        COL_IN_SAMPLE2,
        COL_IN_ZWIFT,
        COL_IN_ZWIFTRACINGAPP,
        COL_IN_ZWIFTPOWER,
        COL_IN_ZWIFTPOWER_WATTS_GRAPHS,
    ])


def create_intersection_of_sets_as_dataframe(
    dict_of_ZwiftItem: Dict[str, ZwiftItem],
    dict_of_ZwiftRacingAppItem: Dict[str, ZwiftRacingAppItem],
    dict_of_ZwiftPower90dayWattsItem: Dict[str, ZwiftPowerFlattened90dayWattsItem],
    sample1: list[str],
    sample2: list[str],
) -> pd.DataFrame:
    """
    Returns a pandas DataFrame representing the intersection of Zwift IDs found across all main
    datasets, optionally further filtered by sample1 and sample2.

    Args:
        dict_of_ZwiftItem (Dict[str, ZwiftItem]):
            Dictionary of ZwiftItems keyed by zwift_id.
        dict_of_ZwiftRacingAppItem (Dict[str, ZwiftRacingAppItem]):
            Dictionary of ZwiftRacingAppItems keyed by zwift_id.
        dict_of_ZwiftPower90dayWattsItem (Dict[str, ZwiftPowerFlattened90dayWattsItem]):
            Dictionary of ZwiftPowerFlattened90dayWattsItems keyed by zwift_id.
        sample1 (list[str]):
            If non-empty, the intersection is further filtered to only include IDs in this list.
        sample2 (list[str]):
            If non-empty, the intersection is further filtered to only include IDs in this list.

    Returns:
        pd.DataFrame: DataFrame with columns for Zwift ID, sample membership, and dataset membership.
        Membership is indicated by "y" (present) or "n" (absent) for each column.
    """

    intersection = (
        set(dict_of_ZwiftItem.keys()) &
        set(dict_of_ZwiftRacingAppItem.keys()) &
        set(dict_of_ZwiftPower90dayWattsItem.keys())
    )

    if sample1:
        intersection = intersection & set(sample1)
    if sample2:
        intersection = intersection & set(sample2)

    answer: list[tuple[str, str, str, str, str, str]] = []
    for key in intersection:
        row = (
            key,
            "y" if key in sample1 else "n",
            "y" if key in sample2 else "n",
            "y" if key in dict_of_ZwiftItem else "n",
            "y" if key in dict_of_ZwiftRacingAppItem else "n",
            "y" if key in dict_of_ZwiftPower90dayWattsItem else "n",
        )
        answer.append(row)

    answer.sort(key=lambda x: x[0])

    return pd.DataFrame(answer, columns=[
        COL_ZWIFT_ID,
        COL_IN_SAMPLE1,
        COL_IN_SAMPLE2,
        "in_zwift_profiles",
        "in_zwiftracingapp_profiles",
        "in_zwiftpower_profiles",
        "in_zwiftpower_90daybest_graphs",
    ])


def create_union_of_sets_filtered_by_membership_as_dataframe(
    dict_of_ZwiftItem: Dict[str, ZwiftItem],
    dict_of_ZwiftRacingAppItem: Dict[str, ZwiftRacingAppItem],
    dict_of_ZwiftPower90dayWattsItem: Dict[str, ZwiftPowerFlattened90dayWattsItem],
    zwift: str,
    racingapp: str,
    zwiftpower_90day_cp: str,
) -> pd.DataFrame:
    """
    Returns a filtered DataFrame from the union of all datasets, keeping only rows that match
    the specified membership criteria for each data source.

    Each filter parameter accepts "y", "n", or "y_or_n" (meaning no filter applied for that source).

    Args:
        dict_of_ZwiftItem (Dict[str, ZwiftItem]):
            Dictionary of ZwiftItems keyed by zwift_id.
        dict_of_ZwiftRacingAppItem (Dict[str, ZwiftRacingAppItem]):
            Dictionary of ZwiftRacingAppItems keyed by zwift_id.
        dict_of_ZwiftPower90dayWattsItem (Dict[str, ZwiftPowerFlattened90dayWattsItem]):
            Dictionary of ZwiftPowerFlattened90dayWattsItems keyed by zwift_id.
        zwift (str):
            Membership filter for Zwift data. Must be "y", "n", or "y_or_n".
        racingapp (str):
            Membership filter for ZwiftRacingApp data. Must be "y", "n", or "y_or_n".
        zwiftpower_90day_cp (str):
            Membership filter for ZwiftPower 90-day watts data. Must be "y", "n", or "y_or_n".

    Returns:
        pd.DataFrame: Filtered DataFrame matching the specified membership criteria.

    Raises:
        ValueError: If any filter parameter is not one of "y", "n", or "y_or_n".
    """

    valid_values: set[str] = {"y_or_n", "y", "n"}
    invalid_params: list[str] = []

    for param_name, param_value in {
        "zwift": zwift,
        "racingapp": racingapp,
        "zwiftpower_90day_cp": zwiftpower_90day_cp,
    }.items():
        if param_value not in valid_values:
            invalid_params.append(f"{param_name}='{param_value}' (must be one of {valid_values})")

    if invalid_params:
        raise ValueError(f"Invalid parameters: {', '.join(invalid_params)}")

    df_superset = create_union_of_sets_as_dataframe(
        dict_of_ZwiftItem, dict_of_ZwiftRacingAppItem, dict_of_ZwiftPower90dayWattsItem, [], []
    )

    def matches_template(row: pd.Series, template: dict[str, str]) -> bool:
        for col, value in template.items():
            if value == "y_or_n":
                continue
            if row[col] != value:
                return False
        return True

    template = {
        COL_IN_ZWIFT          : zwift,
        COL_IN_ZWIFTRACINGAPP : racingapp,
        COL_IN_ZWIFTPOWER_WATTS_GRAPHS: zwiftpower_90day_cp,
    }

    return df_superset[df_superset.apply(lambda row: matches_template(row, template), axis=1)]


def create_intersection_of_sets_as_list(
    dict_of_ZwiftItem: Dict[str, ZwiftItem],
    dict_of_ZwiftRacingAppItem: Dict[str, ZwiftRacingAppItem],
    dict_of_ZwiftPower90dayWattsItem: Dict[str, ZwiftPowerFlattened90dayWattsItem],
    sample1: list[str],
    sample2: list[str],
) -> list[str]:
    df = create_intersection_of_sets_as_dataframe(
        dict_of_ZwiftItem, dict_of_ZwiftRacingAppItem, dict_of_ZwiftPower90dayWattsItem, sample1, sample2
    )
    return df[COL_ZWIFT_ID].tolist()


def create_union_of_sets_filtered_by_membership_as_list(
    dict_of_ZwiftItem: Dict[str, ZwiftItem],
    dict_of_ZwiftRacingAppItem: Dict[str, ZwiftRacingAppItem],
    dict_of_ZwiftPower90dayWattsItem: Dict[str, ZwiftPowerFlattened90dayWattsItem],
    zwift: str,
    racingapp: str,
    zwiftpower_90day_cp: str,
) -> list[str]:
    df = create_union_of_sets_filtered_by_membership_as_dataframe(
        dict_of_ZwiftItem, dict_of_ZwiftRacingAppItem, dict_of_ZwiftPower90dayWattsItem,
        zwift, racingapp, zwiftpower_90day_cp
    )
    return df[COL_ZWIFT_ID].tolist()

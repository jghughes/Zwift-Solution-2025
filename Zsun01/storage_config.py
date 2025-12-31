from typing import Dict

from jgh_enums import PacelinePlanTypeEnum
from jgh_formatting import format_timestamp_as_yyyy_mm_dd


URL_OF_CLUB_MEMBERSHIP_LIST = "https://data.zsunr.com/riders/json/active_members.json"
URL_ROOT_FOR_ZWIFT_FILES = "https://data.zsunr.com/riders/json/zwift/"
URL_ROOT_FOR_ZWIFTPOWER_90_DAY_BEST_FILES = "https://data.zsunr.com/riders/json/zwiftpower/power-graph-watts/"
URL_ROOT_FOR_ZWIFTRACINGAPP_FILES = "https://data.zsunr.com/riders/json/zwiftracing-app-post/"

FOLDER_NAME_OF_CLUB_MEMBERSHIP_LIST = "membership-list"
FOLDER_NAME_ZWIFT_FILES = "zwift-files"
# FOLDER_NAME_ZWIFTPOWER = "zwiftpower"
FOLDER_NAME_ZWIFTPOWER_90_DAY_BEST_FILES = "90-day-power-graph-watts-files"
FOLDER_NAME_ZWIFTRACINGAPP_FILES = "zwiftracing-app-files"

FILENAME_OF_CLUB_MEMBERSHIP_LIST = "active_members.json" # always ensure that this is identical to the filename portion of URL_OF_CLUB_MEMBERSHIP_LIST

DIRPATH_FROM_DAVEK_ROOT =f"C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK/live_data/"
_stuffByJghDirPathStem =f"C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK_byJgh/"

DIRPATH_LOGGING = f"{_stuffByJghDirPathStem}/LOGGING/"

CONNECTION_STRING_FILENAME : str = "connection_strings.txt"
CONNECTION_STRING_DIRPATH : str = f"{_stuffByJghDirPathStem}/connectionstrings/"

DIRPATH_CLUB_MEMBERSHIP_LIST = f"{DIRPATH_FROM_DAVEK_ROOT}/{FOLDER_NAME_OF_CLUB_MEMBERSHIP_LIST}/"

DIRPATH_ZWIFT_FILES = f"{DIRPATH_FROM_DAVEK_ROOT}/{FOLDER_NAME_ZWIFT_FILES}/"
DIRPATH_ZWIFTRACINGAPP_FILES = f"{DIRPATH_FROM_DAVEK_ROOT}/{FOLDER_NAME_ZWIFTRACINGAPP_FILES}/"
# DIRPATH_ZWIFTPOWER = f"{DIRPATH_FROM_DAVEK_ROOT}/{FOLDER_NAME_ZWIFTPOWER}/"
DIRPATH_ZWIFTPOWER_90_DAY_BEST_FILES = f"{DIRPATH_FROM_DAVEK_ROOT}/{FOLDER_NAME_ZWIFTPOWER_90_DAY_BEST_FILES}/"

DIRPATH_RIDER_BRUTE_DTO =f"{_stuffByJghDirPathStem}/riderBruteDTO_by_jgh/"
DIRPATH_RIDER_STATS_DTO =f"{_stuffByJghDirPathStem}/riderStatsDTO_by_jgh/"
DIRPATH_BRUTE_TTT_DOCS =f"{_stuffByJghDirPathStem}/brutePublicDocuments_by_jgh/"

DIRPATH_VISUAL_STUDIO_PYTHON_PROJECT = DIRPATH_RIDER_BRUTE_DTO
DIRPATH_RUBBISH_SCRATCHPAD = "C:/Users/johng/holding_pen/StuffForZsun/!StuffFromDaveK_byJgh/rubbish/" # scratchpad for temporary files during development and everything else temporary

_riderDtoFileNamePrefix = "rider_brute_dto"
FILENAME_RIDER_BRUTE_DTO_JSON_DICT = f"{_riderDtoFileNamePrefix}_as_dict.json"
FILENAME_RIDER_BRUTE_DTO_JSON_LIST = f"{_riderDtoFileNamePrefix}_as_list.json"
FILENAME_RIDER_BRUTE_DTO_XLSX_LIST = f"{_riderDtoFileNamePrefix}_as_list.xlsx"

_riderStatsDtoFileNamePrefix = "rider_stats_dto"
FILENAME_RIDER_STATS_DTO_JSON_DICT = f"{_riderStatsDtoFileNamePrefix}_as_dict.json"
FILENAME_RIDER_STATS_DTO_JSON_LIST = f"{_riderStatsDtoFileNamePrefix}_as_list.json"
FILENAME_RIDER_STATS_DTO_XLSX_LIST = f"{_riderStatsDtoFileNamePrefix}_as_list.xlsx"

AZURE_ACCOUNTNAME_ZSUN = "customerzsun"
AZURE_CONTAINERNAME_BRUTE = "brute"
AZURE_CONTAINERNAME_PREPROCESSED = "preprocessed"
AZURE_CONTAINERNAME_PREPROCESSED_ARCHIVE = "preprocessed-archive"
AZURE_BLOBNAME_RIDER_BRUTE_DTO_DICT = FILENAME_RIDER_BRUTE_DTO_JSON_DICT
AZURE_BLOBNAME_RIDER_BRUTE_DTO_LIST = FILENAME_RIDER_BRUTE_DTO_JSON_LIST
AZURE_BLOBNAME_RIDER_STATS_DTO_DICT = FILENAME_RIDER_STATS_DTO_JSON_DICT
AZURE_BLOBNAME_RIDER_STATS_DTO_LIST = FILENAME_RIDER_STATS_DTO_JSON_LIST

DICT_OF_SAVE_FILE_NAMES_FOR_PACELINE_PLANS : Dict[PacelinePlanTypeEnum, str] = {
    PacelinePlanTypeEnum.THIRTY_SEC_PULL:    "01_no_drop_thirty_second_pulls.html",
    PacelinePlanTypeEnum.SIXTY_SEC_PULL:     "02_no_drop_one_minute_pulls.html",
    PacelinePlanTypeEnum.BALANCED_INTENSITY: "03_no_drop_most_balanced_intensity.html",
    PacelinePlanTypeEnum.EVERYBODY_PULL_HARD:"04_no_drop_hardest_intensity.html",
    PacelinePlanTypeEnum.FASTEST:            "05_fastest_full_team.html",
    PacelinePlanTypeEnum.FASTEST_STRONGEST_FIVE:     "06_fastest_strongest_five_riders.html",
    PacelinePlanTypeEnum.FASTEST_STRONGEST_FOUR:     "07_fastest_strongest_four_riders.html",
}

def format_save_filename_for_document_of_single_paceline_plan(team_name: str, plan_type: PacelinePlanTypeEnum) -> str:
    created : str = format_timestamp_as_yyyy_mm_dd()  
    suffix = DICT_OF_SAVE_FILE_NAMES_FOR_PACELINE_PLANS.get(plan_type, "unknown_paceline_plan_type.html")
    answer = f"{created}_{team_name}_{suffix}"
    return answer



def make_filename_for_one_page_summary_html_doc(team_name: str) -> str:
    created : str = format_timestamp_as_yyyy_mm_dd()  
    return f"{created}_{team_name}.html"



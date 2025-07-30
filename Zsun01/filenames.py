from typing import Dict
from datetime import datetime
from jgh_enums import PacelinePlanTypeEnum

RIDERS_FILE_NAME = "everyone_in_club_ZsunItems_2025_07_08.json"
# RIDERS_FILE_NAME = "everyone_in_club_ZsunItems_2025_04_00.json"

DICT_OF_SAVE_FILE_NAMES_FOR_PACELINE_PLANS : Dict[PacelinePlanTypeEnum, str] = {
    PacelinePlanTypeEnum.THIRTY_SEC_PULL:    "01_no_drop_thirty_second_pulls.html",
    PacelinePlanTypeEnum.SIXTY_SEC_PULL:     "02_no_drop_sixty_second_pulls.html",
    PacelinePlanTypeEnum.BALANCED_INTENSITY: "03_no_drop_balanced_intensity.html",
    PacelinePlanTypeEnum.EVERYBODY_PULL_HARD:"04_no_drop_hardest_intensity.html",
    PacelinePlanTypeEnum.FASTEST:            "05_possible_drop_full_team.html",
    PacelinePlanTypeEnum.LAST_FIVE:          "06_possible_drop_last_five_riders.html",
    PacelinePlanTypeEnum.LAST_FOUR:          "07_possible_drop_last_four_riders.html",
}

def get_save_filename_for_single_paceline_plan(team_name: str, plan_type: PacelinePlanTypeEnum) -> str:
    suffix = DICT_OF_SAVE_FILE_NAMES_FOR_PACELINE_PLANS.get(plan_type, "unknown_paceline_plan_type.html")
    answer = f"{team_name}_{suffix}"
    return answer



def get_save_filename_for_summary_of_all_paceline_plans(team_name: str) -> str:
    return f"{team_name}_00_summary_of_all_paceline_plans.html"



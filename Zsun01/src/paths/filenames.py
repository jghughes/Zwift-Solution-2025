from typing import Dict
from datetime import datetime
from jgh_enums import PacelinePlanTypeEnum

RIDERS_FILE_NAME = "everyone_in_club_ZsunRiderItems.json"

DICT_OF_SAVE_FILE_NAMES_FOR_PACELINE_PLANS : Dict[PacelinePlanTypeEnum, str] = {
    PacelinePlanTypeEnum.THIRTY_SEC_PULL:    "1_everybody_does_thirty_second_pulls_plan.html",
    PacelinePlanTypeEnum.IDENTICAL_PULL:     "2_everybody_does_identical_pulls_plan.html",
    PacelinePlanTypeEnum.BALANCED_INTENSITY: "3_no_drop_balanced_workload_plan.html",
    PacelinePlanTypeEnum.EVERYBODY_PULL_HARD:"4_no_drop_hard_plan.html",
    PacelinePlanTypeEnum.FASTEST:            "5_race_plan_for_full_team.html",
    PacelinePlanTypeEnum.LAST_FIVE:          "6_race_plan_for_last_five_riders.html",
    PacelinePlanTypeEnum.LAST_FOUR:          "7_race_plan_for_last_four_riders.html",
}

def get_save_filename_for_single_paceline_plan(team_name: str, plan_type: PacelinePlanTypeEnum) -> str:
    suffix = DICT_OF_SAVE_FILE_NAMES_FOR_PACELINE_PLANS.get(plan_type, "unknown_paceline_plan_type.html")
    answer = f"{team_name}_{suffix}"
    return answer



def get_save_filename_for_summary_of_all_paceline_plans(team_name: str) -> str:
    return f"{team_name}_0_summary_of_all_paceline_plans.html"



from typing import List, Tuple
from jgh_enums import PacelinePlanTypeEnum


DISPLAY_ORDER_OF_SUMMARY_OF_PACELINE_PLANS = [
    PacelinePlanTypeEnum.THIRTY_SEC_PULL,
    PacelinePlanTypeEnum.IDENTICAL_PULL,
    PacelinePlanTypeEnum.BALANCED_INTENSITY,
    PacelinePlanTypeEnum.EVERYBODY_PULL_HARD,
    PacelinePlanTypeEnum.FASTEST,
    PacelinePlanTypeEnum.LAST_FIVE,
    PacelinePlanTypeEnum.LAST_FOUR,
]


LIST_OF_CAPTIONS_FOR_PACELINE_PLANS: List[Tuple[PacelinePlanTypeEnum, str, str]] = [
    (PacelinePlanTypeEnum.THIRTY_SEC_PULL,     "\n1. THIRTY-SECOND PULLS",         "everybody pulls for 30 seconds "),
    (PacelinePlanTypeEnum.IDENTICAL_PULL,      "\n2. IDENTICAL-PULLS",             "everybody pulls for same time "),
    (PacelinePlanTypeEnum.BALANCED_INTENSITY,  "\n3. NO-DROP - BALANCED-WORKLOAD", "everybody pulls "),
    (PacelinePlanTypeEnum.EVERYBODY_PULL_HARD, "\n4. NO-DROP - HARD",              "everybody pulls "),
    (PacelinePlanTypeEnum.FASTEST,             "\n5. RACE - FULL-TEAM",            "possible drop "),
    (PacelinePlanTypeEnum.LAST_FIVE,           "\n6. RACE - LAST-FIVE",            "possible drop "),
    (PacelinePlanTypeEnum.LAST_FOUR,           "\n7. RACE - LAST-FOUR",            "possible drop "),
]

def get_caption_for_summary_of_all_paceline_plans(team_name: str) -> str:
    return f"TTT paceline plans for {team_name}"



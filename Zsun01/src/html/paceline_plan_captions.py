from typing import Dict, Tuple
from collections import defaultdict
from jgh_enums import PacelinePlanTypeEnum


DISPLAY_ORDER_OF_PACELINE_PLANS = [
    PacelinePlanTypeEnum.THIRTY_SEC_PULL,
    PacelinePlanTypeEnum.SIXTY_SEC_PULL,
    PacelinePlanTypeEnum.BALANCED_INTENSITY,
    PacelinePlanTypeEnum.EVERYBODY_PULL_HARD,
    PacelinePlanTypeEnum.FASTEST,
    PacelinePlanTypeEnum.FASTEST_STRONGEST_FIVE,
    PacelinePlanTypeEnum.FASTEST_STRONGEST_FOUR,
]


DICT_OF_CAPTION_PARTS_FOREACH_PACELINE_PLAN: Dict[PacelinePlanTypeEnum, Tuple[str, str]] = defaultdict(
    lambda: ("", ""),
    {
        PacelinePlanTypeEnum.THIRTY_SEC_PULL:           ("Scenario #1:","THIRTY-SECOND PULLS"),
        PacelinePlanTypeEnum.SIXTY_SEC_PULL:            ("Scenario #2:","ONE-MINUTE PULLS"),
        PacelinePlanTypeEnum.BALANCED_INTENSITY:        ("Scenario #3:","MOST BALANCED INTENSITY"),
        PacelinePlanTypeEnum.EVERYBODY_PULL_HARD:       ("Scenario #4:","HARD, EVERYBODY PULLS, NO-DROP"),
        PacelinePlanTypeEnum.FASTEST:                   ("Scenario #5:","FASTEST (FULL-TEAM) "),
        PacelinePlanTypeEnum.FASTEST_STRONGEST_FIVE:    ("Scenario #6:","FASTEST (STRONGEST-FIVE) "),
        PacelinePlanTypeEnum.FASTEST_STRONGEST_FOUR:    ("Scenario #7:","FASTEST (STRONGEST-FOUR) "),
    }
)



def get_caption_for_consolidated_document(team_name: str) -> str:
    return f"Paceline scenarios : {team_name}"



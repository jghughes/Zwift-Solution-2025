from enum import Enum


class PacelinePlanTypeEnum(Enum):
    THIRTY_SEC_PULL = "thirty_sec_pull"
    IDENTICAL_PULL = "identical_pull"
    BALANCED_INTENSITY = "balanced_intensity"
    EVERYBODY_PULL_HARD = "everybody_pull_hard"
    FASTEST = "fastest"
    LAST_FIVE = "last_five"
    LAST_FOUR = "last_four"


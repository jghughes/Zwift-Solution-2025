from enum import Enum


class PacelinePlanTypeEnum(Enum):
    THIRTY_SEC_PULL = "thirty_sec_pull"
    SIXTY_SEC_PULL = "identical_pull"
    BALANCED_INTENSITY = "balanced_intensity"
    EVERYBODY_PULL_HARD = "everybody_pull_hard"
    FASTEST = "fastest"
    FASTEST_STRONGEST_FIVE = "last_five"
    FASTEST_STRONGEST_FOUR = "last_four"


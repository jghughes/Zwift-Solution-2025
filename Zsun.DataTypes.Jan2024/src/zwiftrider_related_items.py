from dataclasses import dataclass
from typing import Dict,
from dataclasses import dataclass, field
from zwiftrider_item import ZwiftRiderItem
from zwiftrider_cp_dto import ZwiftRiderCriticalPowerDataTransferObject


@dataclass(frozen=True, eq=True)  # immutable and hashable
class RiderWorkAssignmentItem:
    position: int = 1
    duration: float = 0
    speed: float = 0


@dataclass(frozen=True, eq=True)  # immutable and hashable
class RiderWorkItem:
    position: int = 0
    speed: float = 0
    duration: float = 0
    wattage: float = 0
    kilojoules: float = 0


@dataclass(frozen=True, eq=True)  # immutable and hashable
class RiderAggregateWorkItem:
    total_duration: float = 0
    average_speed: float = 0
    total_distance: float = 0
    weighted_average_watts: float = 0
    normalized_average_watts: float = 0
    instantaneous_peak_wattage: float = 0
    position_at_peak_wattage: int = 0
    total_kilojoules_at_weighted_watts: float = 0
    total_kilojoules_at_normalized_watts: float = 0


@dataclass
class CriticalPowerItem:
    """
    A data class representing a zwiftrider's critical power data.
    
    Attributes:
        cpw_5_sec : float  Critical power for 5 seconds.
        cpw_15_sec: float  Critical power for 15 seconds.
        cpw_30_sec: float  Critical power for 30 seconds.
        cpw_1_min : float  Critical power for 1 minute.
        cpw_2_min : float  Critical power for 2 minutes.
        cpw_3_min : float  Critical power for 3 minutes.
        cpw_5_min : float  Critical power for 5 minutes.
        cpw_10_min: float  Critical power for 10 minutes.
        cpw_12_min: float  Critical power for 12 minutes.
        cpw_15_min: float  Critical power for 15 minutes.
        cpw_20_min: float  Critical power for 20 minutes.
        cpw_30_min: float  Critical power for 30 minutes.
        cpw_40_min: float  Critical power for 40 minutes.
    """
    cpw_5_sec : float  = 0.0
    cpw_15_sec: float  = 0.0
    cpw_30_sec: float  = 0.0
    cpw_1_min : float  = 0.0
    cpw_2_min : float  = 0.0
    cpw_3_min : float  = 0.0
    cpw_5_min : float  = 0.0
    cpw_10_min: float  = 0.0
    cpw_12_min: float  = 0.0
    cpw_15_min: float  = 0.0
    cpw_20_min: float  = 0.0
    cpw_30_min: float  = 0.0
    cpw_40_min: float  = 0.0
    cp: float = 0.0
    w_prime: float = 0.0


@dataclass
class RiderCriticalPowerItem:
    """
    A data class representing a zwiftrider's critical power data.
    The object can be converted to and from a data transfer object (DTO).

    Attributes:
        zwiftid   : int    The Zwift ID of the rider.
        name      : str    The name of the rider.
        cp: CriticalPowerItem  The critical power curve data.
    """

    zwiftid: int = 0
    name: str = ""
    cp: CriticalPowerItem = field(
        default_factory=CriticalPowerItem
    )

    class Config:
        # Define the extra JSON schema for the class in the form of a dictionary of riders' power curve items
        json_schema_extra = {
            "davek": {
                "zwiftid": 3147366,
                "name": "DaveK",
                "cp": {
                    "cpw_5_sec": 0.0,
                    "cpw_15_sec": 0.0,
                    "cpw_30_sec": 0.0,
                    "cpw_1_min": 0.0,
                    "cpw_2_min": 0.0,
                    "cpw_3_min": 0.0,
                    "cpw_5_min": 0.0,
                    "cpw_10_min": 0.0,
                    "cpw_12_min": 0.0,
                    "cpw_15_min": 0.0,
                    "cpw_20_min": 0.0,
                    "cpw_30_min": 0.0,
                    "cpw_40_min": 0.0,
                },
            },
            "timr": {
                "zwiftid": 5421258,
                "name": "TimR",
                "cp": {
                    "cpw_5_sec": 0.0,
                    "cpw_15_sec": 0.0,
                    "cpw_30_sec": 0.0,
                    "cpw_1_min": 0.0,
                    "cpw_2_min": 0.0,
                    "cpw_3_min": 0.0,
                    "cpw_5_min": 0.0,
                    "cpw_10_min": 0.0,
                    "cpw_12_min": 0.0,
                    "cpw_15_min": 0.0,
                    "cpw_20_min": 0.0,
                    "cpw_30_min": 0.0,
                    "cpw_40_min": 0.0,
                },
            },
            "johnh": {
                "zwiftid": 58160,
                "name": "JohnH",
                "cp": {
                    "cpw_5_sec": 546,
                    "cpw_15_sec": 434,
                    "cpw_30_sec": 425,
                    "cpw_1_min": 348,
                    "cpw_2_min": 0,
                    "cpw_3_min": 293,
                    "cpw_5_min": 292,
                    "cpw_10_min": 268,
                    "cpw_12_min": 264,
                    "cpw_15_min": 254,
                    "cpw_20_min": 254,
                    "cpw_30_min": 252,
                    "cpw_40_min": 244,
                },
            },
        }

    @staticmethod
    def to_dataTransferObject(item: "RiderCriticalPowerItem",) -> ZwiftRiderCriticalPowerDataTransferObject:

        answer = ZwiftRiderCriticalPowerDataTransferObject(
            zwiftid=item.zwiftid,
            name=item.name,
            cpw_5_sec=item.cp.cpw_5_sec,
            cpw_15_sec=item.cp.cpw_15_sec,
            cpw_30_sec=item.cp.cpw_30_sec,
            cpw_1_min=item.cp.cpw_1_min,
            cpw_2_min=item.cp.cpw_2_min,
            cpw_3_min=item.cp.cpw_3_min,
            cpw_5_min=item.cp.cpw_5_min,
            cpw_10_min=item.cp.cpw_10_min,
            cpw_12_min=item.cp.cpw_12_min,
            cpw_15_min=item.cp.cpw_15_min,
            cpw_20_min=item.cp.cpw_20_min,
            cpw_30_min=item.cp.cpw_30_min,
            cpw_40_min=item.cp.cpw_40_min,
        )
        return answer

    @staticmethod
    def from_dataTransferObject(dto: ZwiftRiderCriticalPowerDataTransferObject) -> "RiderCriticalPowerItem":

        answer = RiderCriticalPowerItem(zwiftid=dto.zwiftid or 0, name=dto.name or "",  cp=CriticalPowerItem(
                cpw_5_sec=dto.cpw_5_sec or 0.0,
                cpw_15_sec=dto.cpw_15_sec or 0.0,
                cpw_30_sec=dto.cpw_30_sec or 0.0,
                cpw_1_min=dto.cpw_1_min or 0.0,
                cpw_2_min=dto.cpw_2_min or 0.0,
                cpw_3_min=dto.cpw_3_min or 0.0,
                cpw_5_min=dto.cpw_5_min or 0.0,
                cpw_10_min=dto.cpw_10_min or 0.0,
                cpw_12_min=dto.cpw_12_min or 0.0,
                cpw_15_min=dto.cpw_15_min or 0.0,
                cpw_20_min=dto.cpw_20_min or 0.0,
                cpw_30_min=dto.cpw_30_min or 0.0,
                cpw_40_min=dto.cpw_40_min or 0.0,
            ),
        )
        return answer

    @staticmethod
    def from_dict_of_dataTransferObjects(dict_of_zwiftrider_powercurve_dto: Dict[str, ZwiftRiderCriticalPowerDataTransferObject]) -> Dict[str, "RiderCriticalPowerItem"]:

        answer = {
            key: RiderCriticalPowerItem.from_dataTransferObject(dto)
            for key, dto in dict_of_zwiftrider_powercurve_dto.items()
        }
        return answer


@dataclass
class RiderTeamItem:
    riders_working: list[ZwiftRiderItem] = []
    riders_resting: list[ZwiftRiderItem] = []

    @staticmethod
    def create(riders: list[ZwiftRiderItem]) -> "RiderTeamItem":
        riders.sort(key=lambda x: x.calculate_strength(), reverse=True)
        # assign rank to rank attr sarting with 1
        for i, rider in enumerate(riders):
            rider.rank = i + 1
        team = RiderTeamItem(riders_working=riders, riders_resting=[])
        return team

    def sort_riders(self) -> None:
        self.riders_working.sort(key=lambda x: x.calculate_strength(), reverse=True)
        self.riders_resting.sort(key=lambda x: x.calculate_strength(), reverse=True)

    def demote_rider_from_working_to_resting(self, rider: ZwiftRiderItem) -> None:
        self.riders_resting.append(rider)
        self.riders_working.remove(rider)
        self.sort_riders()

    def promote_rider_from_resting_to_working(self, rider: ZwiftRiderItem) -> None:
        self.riders_working.append(rider)
        self.riders_resting.remove(rider)
        self.sort_riders()



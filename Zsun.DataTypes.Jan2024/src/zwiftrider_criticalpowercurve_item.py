from typing import Dict
from dataclasses import dataclass, field
from zwiftrider_criticalpower_curve_dto import *
from criticalpowercurve_item import CriticalPowerCurveItem


@dataclass
class ZwiftRiderCriticalPowerCurveItem:
    """
    A data class representing a zwiftrider's critical power curve data.
    The object can be converted to and from a data transfer object (DTO).
    
    Attributes:
        zwiftid   : int    The Zwift ID of the rider.
        name      : str    The name of the rider.
        critical_power_curve: CriticalPowerCurveItem  The critical power curve data.
    """
    zwiftid   : int    = 0
    name      : str    = ""
    critical_power_curve: CriticalPowerCurveItem = field(default_factory= CriticalPowerCurveItem)
    critical_power : float = 0.0
    w_prime : float = 0.0

    class Config:
        # Define the extra JSON schema for the class in the form of a dictionary of riders' power curve items
        json_schema_extra = {
            "davek": {
                "zwiftid": 3147366,
                "name": "DaveK",
                "critical_power_curve": {
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
                    "cpw_40_min": 0.0
                }
            },
            "timr": {
                "zwiftid": 5421258,
                "name": "TimR",
                "critical_power_curve": {
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
                    "cpw_40_min": 0.0
                }
            },
            "johnh" : {
                "zwiftid": 58160,
                "name": "JohnH",
                "critical_power_curve": {
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
                    "cpw_40_min": 244
                }
            }
        }

    @staticmethod
    def to_dataTransferObject(item: "ZwiftRiderCriticalPowerCurveItem") -> ZwiftRiderCriticalPowerCurveDataTransferObject:
        return ZwiftRiderCriticalPowerCurveDataTransferObject(
            zwiftid=item.zwiftid,
            name=item.name,
            cpw_5_sec=item.critical_power_curve.cpw_5_sec,
            cpw_15_sec=item.critical_power_curve.cpw_15_sec,
            cpw_30_sec=item.critical_power_curve.cpw_30_sec,
            cpw_1_min=item.critical_power_curve.cpw_1_min,
            cpw_2_min=item.critical_power_curve.cpw_2_min,
            cpw_3_min=item.critical_power_curve.cpw_3_min,
            cpw_5_min=item.critical_power_curve.cpw_5_min,
            cpw_10_min=item.critical_power_curve.cpw_10_min,
            cpw_12_min=item.critical_power_curve.cpw_12_min,
            cpw_15_min=item.critical_power_curve.cpw_15_min,
            cpw_20_min=item.critical_power_curve.cpw_20_min,
            cpw_30_min=item.critical_power_curve.cpw_30_min,
            cpw_40_min=item.critical_power_curve.cpw_40_min
        )

    @staticmethod
    def from_dataTransferObject(dto: ZwiftRiderCriticalPowerCurveDataTransferObject) -> "ZwiftRiderCriticalPowerCurveItem":
        return ZwiftRiderCriticalPowerCurveItem(
            zwiftid=dto.zwiftid or 0,
            name=dto.name or "",
            critical_power_curve=CriticalPowerCurveItem(
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
                cpw_40_min=dto.cpw_40_min or 0.0
            )
        )

    @staticmethod
    def from_dict_of_dataTransferObjects(dict_of_zwiftrider_powercurve_dto: Dict[str, ZwiftRiderCriticalPowerCurveDataTransferObject]) -> Dict[str, 'ZwiftRiderCriticalPowerCurveItem']:
        return {key: ZwiftRiderCriticalPowerCurveItem.from_dataTransferObject(dto) for key, dto in dict_of_zwiftrider_powercurve_dto.items()}

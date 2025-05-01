
from dataclasses import dataclass, field
from typing import Optional, Dict
from zwiftracingapp_profile_dto import ZwiftRacingAppProfileDTO


@dataclass
class ZwiftRacingAppProfileItem:
    zwift_id          : Optional[str]                                      = None
    fullname          : Optional[str]                                      = None
    gender            : Optional[str]                                      = None
    country           : Optional[str]                                      = None
    agegroup          : Optional[str]                                      = None
    height_cm         : Optional[float]                                    = None
    weight_kg         : Optional[float]                                    = None
    zp_race_category  : Optional[str]                                      = None
    zp_FTP            : Optional[float]                                    = None
    power             : Optional[ZwiftRacingAppProfileDTO.PowerDTO]        = field(default_factory=ZwiftRacingAppProfileDTO.PowerDTO)
    race              : Optional[Dict[str, ZwiftRacingAppProfileDTO.RaceDetailsDTO]] = field(default_factory=lambda: {
        "last": ZwiftRacingAppProfileDTO.RaceDetailsDTO(),
        "current": ZwiftRacingAppProfileDTO.RaceDetailsDTO(),
        "max30": ZwiftRacingAppProfileDTO.RaceDetailsDTO(),
        "max90": ZwiftRacingAppProfileDTO.RaceDetailsDTO(),
    })

    @staticmethod
    def from_dataTransferObject(dto: ZwiftRacingAppProfileDTO) -> "ZwiftRacingAppProfileItem":
        """
        Create a ZwiftRacingAppProfileItem instance from a ZwiftRacingAppProfileDTO.

        Args:
            dto (ZwiftRacingAppProfileDTO): The data transfer object to convert.

        Returns:
            ZwiftRacingAppProfileItem: The corresponding ZwiftRacingAppProfileItem instance.
        """
        return ZwiftRacingAppProfileItem(
            zwift_id         = dto.zwift_id,
            fullname         = dto.fullname,
            gender           = dto.gender,
            country          = dto.country,
            agegroup         = dto.agegroup,
            height_cm        = dto.height_cm,
            weight_kg        = dto.weight_kg,
            zp_race_category = dto.zp_race_category,
            zp_FTP           = dto.zp_FTP,
            power            = dto.power,
            race             = dto.race,
        )

    @staticmethod
    def to_dataTransferObject(item: "ZwiftRacingAppProfileItem") -> ZwiftRacingAppProfileDTO:
        """
        Convert a ZwiftRacingAppProfileItem instance to a ZwiftRacingAppProfileDTO.

        Args:
            item (ZwiftRacingAppProfileItem): The ZwiftRacingAppProfileItem instance to convert.

        Returns:
            ZwiftRacingAppProfileDTO: The corresponding data transfer object.
        """
        return ZwiftRacingAppProfileDTO(
            zwift_id         = item.zwift_id,
            fullname         = item.fullname,
            gender           = item.gender,
            country          = item.country,
            agegroup         = item.agegroup,
            height_cm        = item.height_cm,
            weight_kg        = item.weight_kg,
            zp_race_category = item.zp_race_category,
            zp_FTP           = item.zp_FTP,
            power            = item.power,
            race             = item.race,
        )

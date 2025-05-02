
from dataclasses import dataclass, field
from typing import Dict
from zwiftracingapp_profile_dto import ZwiftRacingAppProfileDTO


@dataclass
class ZwiftRacingAppProfileItem:
    zwift_id          : str  = ""
    fullname          : str  = ""
    gender            : str  = ""
    country           : str  = ""
    agegroup          : str  = ""
    height_cm         : float = 0.0
    weight_kg         : float = 0.0
    zp_race_category  : str  = ""
    zp_FTP            : float = 0.0
    powerdto             : ZwiftRacingAppProfileDTO.PowerDTO = field(default_factory=ZwiftRacingAppProfileDTO.PowerDTO)
    dict_of_racedetailsdto              : Dict[str, ZwiftRacingAppProfileDTO.RaceDetailsDTO] = field(default_factory=lambda: {
        "last": ZwiftRacingAppProfileDTO.RaceDetailsDTO(),
        "current": ZwiftRacingAppProfileDTO.RaceDetailsDTO(),
        "max30": ZwiftRacingAppProfileDTO.RaceDetailsDTO(),
        "max90": ZwiftRacingAppProfileDTO.RaceDetailsDTO(),
    })    
    
    @staticmethod
    def from_dataTransferObject(dto: ZwiftRacingAppProfileDTO) -> "ZwiftRacingAppProfileItem":
        return ZwiftRacingAppProfileItem(
            zwift_id         = dto.zwift_id or "",
            fullname         = dto.fullname or "",
            gender           = dto.gender or "",
            country          = dto.country or "",
            agegroup         = dto.agegroup or "",
            height_cm        = dto.height_cm or 0.0,
            weight_kg        = dto.weight_kg or 0.0,
            zp_race_category = dto.zp_race_category or "",
            zp_FTP           = dto.zp_FTP or 0.0,
            powerdto         = dto.powerdto if dto.powerdto is not None else ZwiftRacingAppProfileDTO.PowerDTO(),
            dict_of_racedetailsdto = dto.dict_of_racedetailsdto if dto.dict_of_racedetailsdto is not None else {
                "last": ZwiftRacingAppProfileDTO.RaceDetailsDTO(),
                "current": ZwiftRacingAppProfileDTO.RaceDetailsDTO(),
                "max30": ZwiftRacingAppProfileDTO.RaceDetailsDTO(),
                "max90": ZwiftRacingAppProfileDTO.RaceDetailsDTO(),
            },
        )
        @staticmethod
        def to_dataTransferObject(item: "ZwiftRacingAppProfileItem") -> ZwiftRacingAppProfileDTO:
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
                powerdto         = item.powerdto,
                dict_of_racedetailsdto = item.dict_of_race_detailsdto,
            )

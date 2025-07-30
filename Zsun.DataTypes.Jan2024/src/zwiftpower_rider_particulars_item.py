from dataclasses import dataclass
from zwiftpower_rider_particulars_dto import ZwiftPowerRiderParticularsDTO

@dataclass
class ZwiftPowerRiderParticularsItem:
    zwift_id               : str  = ""
    profile_url            : str  = ""
    zwift_name             : str  = ""
    race_ranking           : float = 0.0
    zwift_racing_score     : int  = 0
    zwift_racing_category  : str  = ""
    team                   : str  = ""
    zftp                   : float = 0.0
    weight                 : float = 0.0
    age_group              : str  = ""
    zpoints                : int  = 0
    country                : str  = ""
    profile_image          : str  = ""
    strava_profile         : str  = ""
    level                  : int  = 0

    @staticmethod
    def from_dataTransferObject(dto: ZwiftPowerRiderParticularsDTO) -> "ZwiftPowerRiderParticularsItem":
        return ZwiftPowerRiderParticularsItem(
            zwift_id               = dto.zwift_id or "",
            profile_url            = dto.profile_url or "",
            zwift_name             = dto.zwift_name or "",
            race_ranking           = float(dto.race_ranking) if isinstance(dto.race_ranking, (int, float, str)) and dto.race_ranking else 0.0,
            zwift_racing_score     = int(dto.zwift_racing_score) if isinstance(dto.zwift_racing_score, (int, str)) and dto.zwift_racing_score else 0,
            zwift_racing_category  = dto.zwift_racing_category or "",
            team                   = dto.team or "",
            zftp                   = float(dto.zftp) if isinstance(dto.zftp, (int, float, str)) and dto.zftp else 0.0,
            weight                 = float(dto.weight) if isinstance(dto.weight, (int, float, str)) and dto.weight else 0.0,
            age_group              = dto.age_group or "",
            zpoints                = int(dto.zpoints) if isinstance(dto.zpoints, (int, str)) and dto.zpoints else 0,
            country                = dto.country or "",
            profile_image          = dto.profile_image or "",
            strava_profile         = dto.strava_profile or "",
            level                  = int(dto.level) if isinstance(dto.level, (int, str)) and dto.level else 0
        )

    @staticmethod
    def to_dataTransferObject(item: "ZwiftPowerRiderParticularsItem") -> ZwiftPowerRiderParticularsDTO:
        return ZwiftPowerRiderParticularsDTO(
            zwift_id               = item.zwift_id,
            profile_url            = item.profile_url,
            zwift_name             = item.zwift_name,
            race_ranking           = str(item.race_ranking) if item.race_ranking else "0.0",
            zwift_racing_score     = str(item.zwift_racing_score) if item.zwift_racing_score else "0",
            zwift_racing_category  = item.zwift_racing_category,
            team                   = item.team,
            zftp                   = str(item.zftp) if item.zftp else "0.0",
            weight                 = str(item.weight) if item.weight else "0.0",
            age_group              = item.age_group,
            zpoints                = str(item.zpoints) if item.zpoints else "0",
            country                = item.country,
            profile_image          = item.profile_image,
            strava_profile         = item.strava_profile,
            level                  = str(item.level) if item.level else "0"
        )
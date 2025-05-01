from dataclasses import dataclass
from typing import Optional
from zwiftpower_profile_dto import ZwiftPowerProfileDTO

@dataclass
class ZwiftPowerProfileItem:
    zwift_id               : Optional[str]  = None  
    profile_url            : Optional[str]  = None
    zwift_name             : Optional[str]  = None
    race_ranking           : Optional[float] = None  
    zwift_racing_score     : Optional[int]  = None  
    zwift_racing_category  : Optional[str]  = None
    team                   : Optional[str]  = None
    zftp                   : Optional[float] = None  
    weight                 : Optional[float] = None 
    age_group              : Optional[str]  = None
    zpoints                : Optional[int]  = None  
    country                : Optional[str]  = None
    profile_image          : Optional[str]  = None
    strava_profile         : Optional[str]  = None
    level                  : Optional[int]  = None  

    @staticmethod
    def from_dataTransferObject(dto: ZwiftPowerProfileDTO) -> "ZwiftPowerProfileItem":
        """
        Create a ZwiftPowerProfileItem instance from a ZwiftPowerProfileDTO.

        Args:
            dto (ZwiftPowerProfileDTO): The data transfer object to convert.

        Returns:
            ZwiftPowerProfileItem: The corresponding ZwiftPowerProfileItem instance.
        """
        return ZwiftPowerProfileItem(
            zwift_id               = dto.zwift_id if dto.zwift_id is not None else "",
            profile_url            = dto.profile_url,
            zwift_name             = dto.zwift_name,
            race_ranking           = float(dto.race_ranking) if dto.race_ranking is not None else 0.0,
            zwift_racing_score     = int(dto.zwift_racing_score) if dto.zwift_racing_score is not None else 0,
            zwift_racing_category  = dto.zwift_racing_category,
            team                   = dto.team,
            zftp                   = float(dto.zftp) if dto.zftp is not None else 0.0,
            weight                 = float(dto.weight) if dto.weight is not None else 0.0,
            age_group              = dto.age_group,
            zpoints                = int(dto.zpoints) if dto.zpoints is not None else 0,
            country                = dto.country,
            profile_image          = dto.profile_image,
            strava_profile         = dto.strava_profile,
            level                  = int(dto.level) if dto.level is not None else 0
        )
    @staticmethod
    def to_dataTransferObject(item: "ZwiftPowerProfileItem") -> ZwiftPowerProfileDTO:
        """
        Convert a ZwiftPowerProfileItem instance to a ZwiftPowerProfileDTO.

        Args:
            item (ZwiftPowerProfileItem): The ZwiftPowerProfileItem instance to convert.

        Returns:
            ZwiftPowerProfileDTO: The corresponding data transfer object.
        """
        return ZwiftPowerProfileDTO(
                zwift_id               = item.zwift_id,
                profile_url            = item.profile_url,
                zwift_name             = item.zwift_name,
                race_ranking           = str(item.race_ranking) if item.race_ranking is not None else None,
                zwift_racing_score     = str(item.zwift_racing_score) if item.zwift_racing_score is not None else None,
                zwift_racing_category  = item.zwift_racing_category,
                team                   = item.team,
                zftp                   = str(item.zftp) if item.zftp is not None else None,
                weight                 = str(item.weight) if item.weight is not None else None,
                age_group              = item.age_group,
                zpoints                = str(item.zpoints) if item.zpoints is not None else None,
                country                = item.country,
                profile_image          = item.profile_image,
                strava_profile         = item.strava_profile,
                level                  = str(item.level) if item.level is not None else None
        )

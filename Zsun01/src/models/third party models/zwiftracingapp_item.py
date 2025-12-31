from typing import Optional
from dataclasses import dataclass, field
from zwift_id_base import ZwiftIdBase

from zwiftracingapp_dto import *

@dataclass
class MixedThingsItem():
    velo_cat_name   : str = ""
    velo_cat_num    : int = 0

    @staticmethod
    def from_dataTransferObject(dto: Optional[MixedThingsDTO]) -> "MixedThingsItem":
        if dto is None:
            return MixedThingsItem()
        return MixedThingsItem(
            velo_cat_name   = dto.velo_cat_name or "",
            velo_cat_num    = dto.velo_cat_num or 0,
        )
    @staticmethod
    def to_dataTransferObject(item: Optional['MixedThingsItem']) -> MixedThingsDTO:
        if item is None:
            return MixedThingsDTO()
        return MixedThingsDTO(
            velo_cat_name   = item.velo_cat_name,
            velo_cat_num    = item.velo_cat_num,
        )

@dataclass
class RacingScoreItem:
    velo_rating         : float     = 0.0 
    mixed_things_obj    : MixedThingsItem   = field(default_factory=MixedThingsItem)

    @staticmethod
    def from_dataTransferObject(dto: Optional[RatingScoreDTO]) -> "RacingScoreItem":
        if dto is None:
            return RacingScoreItem()
        return RacingScoreItem(
            velo_rating         = dto.velo_rating or 0.0,
            mixed_things_obj    = MixedThingsItem.from_dataTransferObject(dto.mixed_things_obj),
            )

    @staticmethod
    def to_dataTransferObject(item: Optional['RacingScoreItem']) -> RatingScoreDTO:
        if item is None:
            return RatingScoreDTO()
        return RatingScoreDTO(
            velo_rating         = item.velo_rating,
            mixed_things_obj    = MixedThingsItem.to_dataTransferObject(item.mixed_things_obj),
        )

@dataclass
class RaceItem:
    racing_score_max30_obj    : RacingScoreItem = field(default_factory=RacingScoreItem)
    racing_score_max90_obj    : RacingScoreItem = field(default_factory=RacingScoreItem)


    @staticmethod
    def from_dataTransferObject(dto: Optional[RaceDTO]) -> "RaceItem":
        if dto is None:
            return RaceItem()
        return RaceItem(
            racing_score_max30_obj    = RacingScoreItem.from_dataTransferObject(dto.racing_score_max30_obj),
            racing_score_max90_obj    = RacingScoreItem.from_dataTransferObject(dto.racing_score_max90_obj),
    )

    @staticmethod
    def to_dataTransferObject(item: Optional["RaceItem"]) -> RaceDTO:
        if item is None:
            return RaceDTO()
        return RaceDTO(
            racing_score_max30_obj    = RacingScoreItem.to_dataTransferObject(item.racing_score_max30_obj),
            racing_score_max90_obj    = RacingScoreItem.to_dataTransferObject(item.racing_score_max90_obj),
    )

@dataclass
class PowerItem:
    wkg_5s          : float = 0.0
    wkg_15s         : float = 0.0
    wkg_30s         : float = 0.0
    wkg_60s         : float = 0.0
    wkg_120s        : float = 0.0
    wkg_300s        : float = 0.0
    wkg_1200s       : float = 0.0
    w_5s            : float = 0.0
    w_15s           : float = 0.0
    w_30s           : float = 0.0
    w_60s           : float = 0.0
    w_120s          : float = 0.0
    w_300s          : float = 0.0
    w_1200s         : float = 0.0
    w_CP            : float = 0.0  # Critical Power
    kJ_AWC           : float = 0.0  # Anaerobic Work Capacity

    @staticmethod
    def from_dataTransferObject(dto: Optional[PowerDTO]) -> "PowerItem":
        if dto is None:
            return PowerItem()
        return PowerItem(
            wkg_5s          = dto.wkg_5s or 0.0,
            wkg_15s         = dto.wkg_15s or 0.0,
            wkg_30s         = dto.wkg_30s or 0.0,
            wkg_60s         = dto.wkg_60s or 0.0,
            wkg_120s        = dto.wkg_120s or 0.0,
            wkg_300s        = dto.wkg_300s or 0.0,
            wkg_1200s       = dto.wkg_1200s or 0.0,
            w_5s            = dto.w_5s or 0.0,
            w_15s           = dto.w_15s or 0.0,
            w_30s           = dto.w_30s or 0.0,
            w_60s           = dto.w_60s or 0.0,
            w_120s          = dto.w_120s or 0.0,
            w_300s          = dto.w_300s or 0.0,
            w_1200s         = dto.w_1200s or 0.0,
            w_CP            = dto.w_CP or 0.0,
            kJ_AWC           = dto.kJ_AWC or 0.0,
    )

    @staticmethod
    def to_dataTransferObject(item: Optional["PowerItem"]) -> PowerDTO:
        if item is None:
            return PowerDTO()
        return PowerDTO(
            wkg_5s          = item.wkg_5s,
            wkg_15s         = item.wkg_15s,
            wkg_30s         = item.wkg_30s,
            wkg_60s         = item.wkg_60s,
            wkg_120s        = item.wkg_120s,
            wkg_300s        = item.wkg_300s,
            wkg_1200s       = item.wkg_1200s,
            w_5s            = item.w_5s,
            w_15s           = item.w_15s,
            w_30s           = item.w_30s,
            w_60s           = item.w_60s,
            w_120s          = item.w_120s,
            w_300s          = item.w_300s,
            w_1200s         = item.w_1200s,
            w_CP            = item.w_CP,
            kJ_AWC           = item.kJ_AWC,
    )

@dataclass
class ZwiftRacingAppItem(ZwiftIdBase):
	full_name			: str		= ""		# Name of the rider
	gender_code			: str		= ""		# Gender of the rider
	country_code2		: str		= ""		# Country of the rider
	age_group			: str		= ""		# Age category of the rider
	height_cm			: float		= 0.0		# Height in centimeters
	weight_kg			: float		= 0.0		# Weight in kilograms
	zp_race_category	: str		= ""		# ZwiftPower category
	zp_FTP				: float		= 0.0		# ZwiftPower FTP
	poweritem			: PowerItem	= field(default_factory=PowerItem)	# Power data
	raceitem			: RaceItem	= field(default_factory=RaceItem)	# Race data

	@staticmethod
	def from_dataTransferObject(dto: Optional[ZwiftRacingAppDTO]) -> "ZwiftRacingAppItem":
		if dto is None:
			return ZwiftRacingAppItem()
		return ZwiftRacingAppItem(
			zwift_id			= dto.zwift_id			or "",
			full_name			= dto.full_name			or "",
			gender_code			= dto.gender_code		or "",
			country_code2		= dto.country_code2		or "",
			age_group			= dto.age_group			or "",
			height_cm			= dto.height_cm			or 0.0,
			weight_kg			= dto.weight_kg			or 0.0,
			zp_race_category	= dto.zp_race_category	or "",
			zp_FTP				= dto.zp_FTP			or 0.0,
			poweritem			= PowerItem.from_dataTransferObject(dto.power_obj),
			raceitem			= RaceItem.from_dataTransferObject(dto.race_obj),
		)

	@staticmethod
	def to_dataTransferObject(item: Optional["ZwiftRacingAppItem"]) -> ZwiftRacingAppDTO:
		if item is None:
			return ZwiftRacingAppDTO()
		return ZwiftRacingAppDTO(
			zwift_id			= item.zwift_id,
			full_name			= item.full_name,
			gender_code			= item.gender_code,
			country_code2		= item.country_code2,
			age_group			= item.age_group,
			height_cm			= item.height_cm,
			weight_kg			= item.weight_kg,
			zp_race_category	= item.zp_race_category,
			zp_FTP				= item.zp_FTP,
			power_obj			= PowerItem.to_dataTransferObject(item.poweritem),
			race_obj			= RaceItem.to_dataTransferObject(item.raceitem),
		)
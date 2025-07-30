
from dataclasses import dataclass, field
from typing import Optional
from zwiftracingapp_rider_particulars_dto import *

@dataclass
class MixedItem:
    category : str = ""  # Name of the velo category, e.g., "Ruby"
    number   : int = 0   # Number associated with the velo category, e.g., 4

    @staticmethod
    def from_dataTransferObject(dto: Optional[MixedDTO]) -> "MixedItem":
        if dto is None:
            return MixedItem()
        return MixedItem(
            category = dto.category or "",
            number   = dto.number or 0,
        )

    @staticmethod
    def to_dataTransferObject(item: Optional['MixedItem']) -> MixedDTO:
        if item is None:
            return MixedDTO()
        return MixedDTO(
            category = item.category,
            number   = item.number,
        )


@dataclass
class RaceDetailsItem:
    rating : float     = 0.0  # Race rating
    date   : int       = 0    # Date as a Unix timestamp
    mixed  : MixedItem = field(default_factory=MixedItem)

    @staticmethod
    def from_dataTransferObject(dto: Optional[RaceDetailsDTO]) -> "RaceDetailsItem":
        if dto is None:
            return RaceDetailsItem()
        return RaceDetailsItem(
            rating = dto.rating or 0.0,
            date   = dto.date or 0,
            mixed = MixedItem.from_dataTransferObject(dto.mixed)   
            )

    @staticmethod
    def to_dataTransferObject(item: Optional['RaceDetailsItem']) -> RaceDetailsDTO:
        if item is None:
            return RaceDetailsDTO()
        return RaceDetailsDTO(
            rating = item.rating,
            date   = item.date,
            mixed  = MixedItem.to_dataTransferObject(item.mixed),
        )


@dataclass
class RaceItem:
    last     : RaceDetailsItem = field(default_factory=RaceDetailsItem)
    current  : RaceDetailsItem = field(default_factory=RaceDetailsItem)
    max30    : RaceDetailsItem = field(default_factory=RaceDetailsItem)
    max90    : RaceDetailsItem = field(default_factory=RaceDetailsItem)
    finishes : int             = 0
    dnfs     : int             = 0
    wins     : int             = 0
    podiums  : int             = 0


    @staticmethod
    def from_dataTransferObject(dto: Optional[RaceDTO]) -> "RaceItem":
        if dto is None:
            return RaceItem()
        return RaceItem(
            last     = RaceDetailsItem.from_dataTransferObject(dto.last),
            current  = RaceDetailsItem.from_dataTransferObject(dto.current),
            max30    = RaceDetailsItem.from_dataTransferObject(dto.max30),
            max90    = RaceDetailsItem.from_dataTransferObject(dto.max90),
            finishes = dto.finishes or 0,
            dnfs     = dto.dnfs or 0,
            wins     = dto.wins or 0,
            podiums  = dto.podiums or 0,
    )

    @staticmethod
    def to_dataTransferObject(item: Optional["RaceItem"]) -> RaceDTO:
        if item is None:
            return RaceDTO()
        return RaceDTO(
            last     = RaceDetailsItem.to_dataTransferObject(item.last),
            current  = RaceDetailsItem.to_dataTransferObject(item.current),
            max30    = RaceDetailsItem.to_dataTransferObject(item.max30),
            max90    = RaceDetailsItem.to_dataTransferObject(item.max90),
            finishes = item.finishes,
            dnfs     = item.dnfs,
            wins     = item.wins,
            podiums  = item.podiums,
    )


@dataclass
class PowerItem:
    wkg5          : float = 0.0
    wkg15         : float = 0.0
    wkg30         : float = 0.0
    wkg60         : float = 0.0
    wkg120        : float = 0.0
    wkg300        : float = 0.0
    wkg1200       : float = 0.0
    w5            : float = 0.0
    w15           : float = 0.0
    w30           : float = 0.0
    w60           : float = 0.0
    w120          : float = 0.0
    w300          : float = 0.0
    w1200         : float = 0.0
    CP            : float = 0.0  # Critical Power
    AWC           : float = 0.0  # Anaerobic Work Capacity
    compoundScore : float = 0.0  # Compound score
    powerRating   : float = 0.0  # Power rating

    @staticmethod
    def from_dataTransferObject(dto: Optional[PowerDTO]) -> "PowerItem":
        if dto is None:
            return PowerItem()
        return PowerItem(
            wkg5          = dto.wkg5 or 0.0,
            wkg15         = dto.wkg15 or 0.0,
            wkg30         = dto.wkg30 or 0.0,
            wkg60         = dto.wkg60 or 0.0,
            wkg120        = dto.wkg120 or 0.0,
            wkg300        = dto.wkg300 or 0.0,
            wkg1200       = dto.wkg1200 or 0.0,
            w5            = dto.w5 or 0.0,
            w15           = dto.w15 or 0.0,
            w30           = dto.w30 or 0.0,
            w60           = dto.w60 or 0.0,
            w120          = dto.w120 or 0.0,
            w300          = dto.w300 or 0.0,
            w1200         = dto.w1200 or 0.0,
            CP            = dto.CP or 0.0,
            AWC           = dto.AWC or 0.0,
            compoundScore = dto.compoundScore or 0.0,
            powerRating   = dto.powerRating or 0.0,
    )

    @staticmethod
    def to_dataTransferObject(item: Optional["PowerItem"]) -> PowerDTO:
        if item is None:
            return PowerDTO()
        return PowerDTO(
            wkg5          = item.wkg5,
            wkg15         = item.wkg15,
            wkg30         = item.wkg30,
            wkg60         = item.wkg60,
            wkg120        = item.wkg120,
            wkg300        = item.wkg300,
            wkg1200       = item.wkg1200,
            w5            = item.w5,
            w15           = item.w15,
            w30           = item.w30,
            w60           = item.w60,
            w120          = item.w120,
            w300          = item.w300,
            w1200         = item.w1200,
            CP            = item.CP,
            AWC           = item.AWC,
            compoundScore = item.compoundScore,
            powerRating   = item.powerRating,
    )


@dataclass
class ZwiftRacingAppItem:
    zwift_id          : str  = ""
    fullname          : str  = ""
    gender            : str  = ""
    country           : str  = ""
    age_group          : str  = ""
    height_cm         : float = 0.0
    weight_kg         : float = 0.0
    zp_race_category  : str  = ""
    zp_FTP            : float = 0.0
    poweritem         : PowerItem = field(default_factory=PowerItem)
    raceitem          : RaceItem = field(default_factory=RaceItem)    
    
    @staticmethod
    def from_dataTransferObject(dto: Optional[ZwiftRacingAppDTO]) -> "ZwiftRacingAppItem":
        if dto is None:
            return ZwiftRacingAppItem()
        return ZwiftRacingAppItem(
            zwift_id         = dto.zwift_id or "",
            fullname         = dto.fullname or "",
            gender           = dto.gender or "",
            country          = dto.country or "",
            age_group         = dto.age_group or "",
            height_cm        = dto.height_cm or 0.0,
            weight_kg        = dto.weight_kg or 0.0,
            zp_race_category = dto.zp_race_category or "",
            zp_FTP           = dto.zp_FTP or 0.0,
            poweritem        = PowerItem.from_dataTransferObject(dto.power),
            raceitem         = RaceItem.from_dataTransferObject(dto.race),
        )

    @staticmethod
    def to_dataTransferObject(item: Optional["ZwiftRacingAppItem"]) -> ZwiftRacingAppDTO:
        if item is None:
            return ZwiftRacingAppDTO()
        return ZwiftRacingAppDTO(
            zwift_id         = item.zwift_id,
            fullname         = item.fullname,
            gender           = item.gender,
            country          = item.country,
            age_group         = item.age_group,
            height_cm        = item.height_cm,
            weight_kg        = item.weight_kg,
            zp_race_category = item.zp_race_category,
            zp_FTP           = item.zp_FTP,
            power            = PowerItem.to_dataTransferObject(item.poweritem),
            race             = RaceItem.to_dataTransferObject(item.raceitem),
          )
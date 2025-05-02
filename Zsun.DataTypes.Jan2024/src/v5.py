from dataclasses import dataclass, field
from typing import Dict


@dataclass
class ZwiftRacingAppProfileItem:
    zwift_id               : str  = ""
    fullname               : str  = ""
    gender                 : str  = ""
    country                : str  = ""
    agegroup               : str  = ""
    height_cm              : float = 0.0
    weight_kg              : float = 0.0
    zp_race_category       : str  = ""
    zp_FTP                 : float = 0.0

    @dataclass
    class PowerItem:
        wkg5          : float = 0.0
        wkg15         : float = 0.0
        wkg30         : float = 0.0
        wkg60         : float = 0.0
        wkg120        : float = 0.0
        wkg300        : float = 0.0
        wkg1200       : float = 0.0
        w5            : float = 0
        w15           : float = 0
        w30           : float = 0
        w60           : float = 0
        w120          : float = 0
        w300          : float = 0
        w1200         : float = 0
        CP            : float = 0.0
        AWC           : float = 0.0
        compoundScore : float = 0.0
        powerRating   : float = 0.0

        @staticmethod
        def from_dataTransferObject(dto: ZwiftRacingAppProfileDTO.PowerDTO) -> "ZwiftRacingAppProfileItem.PowerItem":
            return ZwiftRacingAppProfileItem.PowerItem(
                wkg5=dto.wkg5 or 0.0,
                wkg15=dto.wkg15 or 0.0,
                wkg30=dto.wkg30 or 0.0,
                wkg60=dto.wkg60 or 0.0,
                wkg120=dto.wkg120 or 0.0,
                wkg300=dto.wkg300 or 0.0,
                wkg1200=dto.wkg1200 or 0.0,
                w5=dto.w5 or 0,
                w15=dto.w15 or 0,
                w30=dto.w30 or 0,
                w60=dto.w60 or 0,
                w120=dto.w120 or 0,
                w300=dto.w300 or 0,
                w1200=dto.w1200 or 0,
                CP=dto.CP or 0.0,
                AWC=dto.AWC or 0.0,
                compoundScore=dto.compoundScore or 0.0,
                powerRating=dto.powerRating or 0.0,
            )

        def to_dataTransferObject(self) -> ZwiftRacingAppProfileDTO.PowerDTO:
            return ZwiftRacingAppProfileDTO.PowerDTO(
                wkg5=self.wkg5,
                wkg15=self.wkg15,
                wkg30=self.wkg30,
                wkg60=self.wkg60,
                wkg120=self.wkg120,
                wkg300=self.wkg300,
                wkg1200=self.wkg1200,
                w5=self.w5,
                w15=self.w15,
                w30=self.w30,
                w60=self.w60,
                w120=self.w120,
                w300=self.w300,
                w1200=self.w1200,
                CP=self.CP,
                AWC=self.AWC,
                compoundScore=self.compoundScore,
                powerRating=self.powerRating,
            )

    @dataclass
    class RaceDetailsItem:
        @dataclass
        class MixedItem:
            category : str = ""
            number   : int = 0

            @staticmethod
            def from_dataTransferObject(dto: ZwiftRacingAppProfileDTO.RaceDetailsDTO.MixedDTO) -> "ZwiftRacingAppProfileItem.RaceDetailsItem.MixedItem":
                return ZwiftRacingAppProfileItem.RaceDetailsItem.MixedItem(
                    category=dto.category or "",
                    number=dto.number or 0,
                )

            def to_dataTransferObject(self) -> ZwiftRacingAppProfileDTO.RaceDetailsDTO.MixedDTO:
                return ZwiftRacingAppProfileDTO.RaceDetailsDTO.MixedDTO(
                    category=self.category,
                    number=self.number,
                )

        rating : float = 0.0
        date   : int = 0
        mixed  : "ZwiftRacingAppProfileItem.RaceDetailsItem.MixedItem" = field(default_factory=lambda: ZwiftRacingAppProfileItem.RaceDetailsItem.MixedItem())

        @staticmethod
        def from_dataTransferObject(dto: ZwiftRacingAppProfileDTO.RaceDetailsDTO) -> "ZwiftRacingAppProfileItem.RaceDetailsItem":
            return ZwiftRacingAppProfileItem.RaceDetailsItem(
                rating=dto.rating or 0.0,
                date=dto.date or 0,
                mixed=ZwiftRacingAppProfileItem.RaceDetailsItem.MixedItem.from_dataTransferObject(dto.mixed),
            )

        def to_dataTransferObject(self) -> ZwiftRacingAppProfileDTO.RaceDetailsDTO:
            return ZwiftRacingAppProfileDTO.RaceDetailsDTO(
                rating=self.rating,
                date=self.date,
                mixed=self.mixed.to_dataTransferObject(),
            )

    powerdto               : PowerItem = field(default_factory=PowerItem)
    dict_of_racedetailsdto : Dict[str, RaceDetailsItem] = field(default_factory=lambda: {
        "last"   : ZwiftRacingAppProfileItem.RaceDetailsItem(),
        "current": ZwiftRacingAppProfileItem.RaceDetailsItem(),
        "max30"  : ZwiftRacingAppProfileItem.RaceDetailsItem(),
        "max90"  : ZwiftRacingAppProfileItem.RaceDetailsItem(),
    })

    @staticmethod
    def from_dataTransferObject(dto: ZwiftRacingAppProfileDTO) -> "ZwiftRacingAppProfileItem":
        return ZwiftRacingAppProfileItem(
            zwift_id               = dto.zwift_id or "",
            fullname               = dto.fullname or "",
            gender                 = dto.gender or "",
            country                = dto.country or "",
            agegroup               = dto.agegroup or "",
            height_cm              = dto.height_cm or 0.0,
            weight_kg              = dto.weight_kg or 0.0,
            zp_race_category       = dto.zp_race_category or "",
            zp_FTP                 = dto.zp_FTP or 0.0,
            powerdto               = ZwiftRacingAppProfileItem.PowerItem.from_dataTransferObject(dto.powerdto),
            dict_of_racedetailsdto = {key: ZwiftRacingAppProfileItem.RaceDetailsItem.from_dataTransferObject(value) for key, value in dto.dict_of_racedetailsdto.items()},
        )

    def to_dataTransferObject(self) -> ZwiftRacingAppProfileDTO:
        return ZwiftRacingAppProfileDTO(
            zwift_id               = self.zwift_id,
            fullname               = self.fullname,
            gender                 = self.gender,
            country                = self.country,
            agegroup               = self.agegroup,
            height_cm              = self.height_cm,
            weight_kg              = self.weight_kg,
            zp_race_category       = self.zp_race_category,
            zp_FTP                 = self.zp_FTP,
            powerdto               = self.powerdto.to_dataTransferObject(),
            dict_of_racedetailsdto = {key: value.to_dataTransferObject() for key, value in self.dict_of_racedetailsdto.items()},
        )

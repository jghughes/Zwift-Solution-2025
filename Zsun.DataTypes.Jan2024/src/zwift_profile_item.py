
from dataclasses import dataclass, field
from typing import Optional

from zwift_profile_dto import ZwiftProfileDTO, CompetitionMetricsDTO

@dataclass
class CompetitionMetricsItem:
    racingScore   : float = 0.0  # Racing score of the rider
    category      : str   = ""   # Racing category of the rider
    categoryWomen : str   = ""   # Racing category for women

    @staticmethod
    def from_dataTransferObject(dto: Optional[CompetitionMetricsDTO]) -> "CompetitionMetricsItem":
        if dto is None:
            return CompetitionMetricsItem()
        return CompetitionMetricsItem(
            racingScore=dto.racingScore or 0.0,
            category=dto.category or "",
            categoryWomen=dto.categoryWomen or "",
        )

    @staticmethod
    def to_dataTransferObject(item: Optional["CompetitionMetricsItem"]) -> CompetitionMetricsDTO:
        if item is None:
            return CompetitionMetricsDTO()
        return CompetitionMetricsDTO(
            racingScore=item.racingScore,
            category=item.category,
            categoryWomen=item.categoryWomen,
        )

@dataclass
class ZwiftProfileItem:
    zwift_id                  : str  = ""
    public_id                 : str  = ""
    first_name                : str  = ""
    last_name                 : str  = ""
    male                      : bool = False
    age_years                 : float = 0.0
    height_mm                 : float = 0.0
    weight_grams              : float = 0.0
    zftp                      : float = 0.0
    competitionMetrics        : CompetitionMetricsItem = field(default_factory=CompetitionMetricsItem)

    @staticmethod
    def from_dataTransferObject(dto: Optional[ZwiftProfileDTO]) -> "ZwiftProfileItem":
        if dto is None:
            return ZwiftProfileItem()
        return ZwiftProfileItem(
            zwift_id                  = dto.zwift_id or "",
            public_id                 = dto.public_id or "",
            first_name                = dto.first_name or "",
            last_name                 = dto.last_name or "",
            male                      = dto.male if dto.male is not None else False,
            age_years                 = dto.age_years or 0.0,
            height_mm                 = dto.height_mm or 0.0,
            weight_grams              = dto.weight_grams or 0.0,
            zftp                      = dto.ftp or 0.0,
            competitionMetrics        = CompetitionMetricsItem.from_dataTransferObject(dto.competitionMetrics),
        )

    @staticmethod
    def to_dataTransferObject(item: Optional["ZwiftProfileItem"]) -> ZwiftProfileDTO:
        if item is None:
            return ZwiftProfileDTO()
        return ZwiftProfileDTO(
            zwift_id                  = item.zwift_id,
            public_id                 = item.public_id,
            first_name                = item.first_name,
            last_name                 = item.last_name,
            male                      = item.male,
            age_years                 = item.age_years,
            height_mm                 = item.height_mm,
            weight_grams              = item.weight_grams,
            ftp                       = item.zftp,
            competitionMetrics        = CompetitionMetricsItem.to_dataTransferObject(item.competitionMetrics),
        )

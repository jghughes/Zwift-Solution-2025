
from dataclasses import dataclass, field
from zwift_id_base import ZwiftIdBase
from typing import Optional

from zwift_dto import ZwiftDTO, CompetitionMetricsDTO

@dataclass
class CompetitionMetricsItem:
    zwift_racing_score      : float = 0.0  # Racing score of the rider
    zwift_category_open     : str   = ""   # Racing zwift_category_open of the rider
    zwift_category_women    : str   = ""   # Racing zwift_category_open for women

    @staticmethod
    def from_dataTransferObject(dto: Optional[CompetitionMetricsDTO]) -> "CompetitionMetricsItem":
        if dto is None:
            return CompetitionMetricsItem()
        return CompetitionMetricsItem(
            zwift_racing_score      =   dto.zwift_racing_score or 0.0,
            zwift_category_open     =   dto.zwift_category_open or "",
            zwift_category_women    =   dto.zwift_category_women or "",
        )

    @staticmethod
    def to_dataTransferObject(item: Optional["CompetitionMetricsItem"]) -> CompetitionMetricsDTO:
        if item is None:
            return CompetitionMetricsDTO()
        return CompetitionMetricsDTO(
            zwift_racing_score      =   item.zwift_racing_score,
            zwift_category_open     =   item.zwift_category_open,
            zwift_category_women    =   item.zwift_category_women,
        )

@dataclass
class ZwiftItem(ZwiftIdBase):
    first_name              : str  = ""
    last_name               : str  = ""
    country_code3           : str  = ""
    is_male                 : bool = False
    age_years               : float = 0.0
    height_mm               : float = 0.0
    weight_grams            : float = 0.0
    ftp_on_zwift            : float = 0.0
    competition_metrics     : CompetitionMetricsItem = field(default_factory=CompetitionMetricsItem)

    @staticmethod
    def from_dataTransferObject(dto: Optional[ZwiftDTO]) -> "ZwiftItem":
        if dto is None:
            return ZwiftItem()
        return ZwiftItem(
            zwift_id            = dto.zwift_id or "",
            first_name          = dto.first_name or "",
            last_name           = dto.last_name or "",
            country_code3       = dto.country_code3 or "",
            is_male             = dto.is_male if dto.is_male is not None else False,
            age_years           = dto.age_years or 0.0,
            height_mm           = dto.height_mm or 0.0,
            weight_grams        = dto.weight_grams or 0.0,
            ftp_on_zwift        = dto.ftp_on_zwift or 0.0,
            competition_metrics = CompetitionMetricsItem.from_dataTransferObject(dto.competition_metrics),
        )

    @staticmethod
    def to_dataTransferObject(item: Optional["ZwiftItem"]) -> ZwiftDTO:
        if item is None:
            return ZwiftDTO()
        return ZwiftDTO(
            zwift_id            = item.zwift_id,
            first_name          = item.first_name,
            last_name           = item.last_name,
            country_code3       = item.country_code3,
            is_male             = item.is_male,
            age_years           = item.age_years,
            height_mm           = item.height_mm,
            weight_grams        = item.weight_grams,
            ftp_on_zwift        = item.ftp_on_zwift,
            competition_metrics = CompetitionMetricsItem.to_dataTransferObject(item.competition_metrics),
        )

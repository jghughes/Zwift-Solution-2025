
from dataclasses import dataclass
from zwift_profile_dto import ZwiftProfileDTO

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
    zwift_racing_score        : float = 0.0
    zwift_racing_category     : str  = ""
    zwift_racing_category_women: str  = ""

    @staticmethod
    def from_dataTransferObject(dto: ZwiftProfileDTO) -> "ZwiftProfileItem":
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
            zwift_racing_score        = dto.competitionMetrics.racingScore if dto.competitionMetrics and dto.competitionMetrics.racingScore is not None else 0.0,
            zwift_racing_category     = dto.competitionMetrics.category if dto.competitionMetrics and dto.competitionMetrics.category is not None else "",
            zwift_racing_category_women = dto.competitionMetrics.categoryWomen if dto.competitionMetrics and dto.competitionMetrics.categoryWomen is not None else "",
        )

    @staticmethod
    def to_dataTransferObject(item: "ZwiftProfileItem") -> ZwiftProfileDTO:
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
            competitionMetrics        = ZwiftProfileDTO.CompetitionMetricsDTO(
                racingScore           = item.zwift_racing_score,
                category              = item.zwift_racing_category,
                categoryWomen         = item.zwift_racing_category_women,
            ),
        )

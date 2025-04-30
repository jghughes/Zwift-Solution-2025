
from dataclasses import dataclass
from typing import Optional
from zwift_profile_dto import ZwiftProfileDTO


@dataclass
class ZwiftProfileItem:
    zwift_id: Optional[str] = None
    public_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    male: Optional[bool] = None
    age_years: Optional[float] = None
    height_mm: Optional[float] = None
    weight_grams: Optional[float] = None
    zftp: Optional[float] = None
    zwift_racing_score: Optional[float] = None
    zwift_racing_category: Optional[str] = None
    zwift_racing_category_women: Optional[str] = None

    @staticmethod
    def from_dataTransferObject(dto: ZwiftProfileDTO) -> "ZwiftProfileItem":
        """
        Create a ZwiftProfileItem instance from a ZwiftProfileDTO.

        Args:
            dto (ZwiftProfileDTO): The data transfer object to convert.

        Returns:
            ZwiftProfileItem: The corresponding ZwiftProfileItem instance.
        """
        return ZwiftProfileItem(
            zwift_id=dto.zwiftID,
            public_id=dto.publicId,
            first_name=dto.firstName,
            last_name=dto.lastName,
            male=dto.male,
            age_years=dto.age_years,
            height_mm=dto.height_mm,
            weight_grams=dto.weight_grams,
            zftp=dto.ftp,
            zwift_racing_score=dto.competitionMetrics.racingScore if dto.competitionMetrics else None,
            zwift_racing_category=dto.competitionMetrics.category if dto.competitionMetrics else None,
            zwift_racing_category_women=dto.competitionMetrics.categoryWomen if dto.competitionMetrics else None,
        )

    @staticmethod
    def to_dataTransferObject(item: "ZwiftProfileItem") -> ZwiftProfileDTO:
        """
        Convert a ZwiftProfileItem instance to a ZwiftProfileDTO.

        Args:
            item (ZwiftProfileItem): The ZwiftProfileItem instance to convert.

        Returns:
            ZwiftProfileDTO: The corresponding data transfer object.
        """
        return ZwiftProfileDTO(
            zwiftID=item.zwift_id,
            publicId=item.public_id,
            firstName=item.first_name,
            lastName=item.last_name,
            male=item.male,
            age_years=item.age_years,
            height_mm=item.height_mm,
            weight_grams=item.weight_grams,
            ftp=item.zftp,
            competitionMetrics=ZwiftProfileDTO.CompetitionMetricsDTO(
                racingScore=item.zwift_racing_score,
                category=item.zwift_racing_category,
                categoryWomen=item.zwift_racing_category_women,
            ),
        )

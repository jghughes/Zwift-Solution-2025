
from dataclasses import dataclass, field
from typing import Optional
from zwiftracingapp_profile_dto import ZwiftRacingAppProfileDTO


@dataclass
class RaceDetailsItem:
    rating: float = 0.0  # Race rating
    date: int = 0        # Date as a Unix timestamp

    @dataclass
    class MixedItem:
        category: str = ""  # Name of the velo category, e.g., "Ruby"
        number: int = 0     # Number associated with the velo category, e.g., 10

        @staticmethod
        def from_dataTransferObject(dto: ZwiftRacingAppProfileDTO.RaceDetailsDTO.MixedDTO) -> "RaceDetailsItem.MixedItem":
            return RaceDetailsItem.MixedItem(
                category=dto.category or "",
                number=dto.number or 0,
            )

        def to_dataTransferObject(self) -> ZwiftRacingAppProfileDTO.RaceDetailsDTO.MixedDTO:
            return ZwiftRacingAppProfileDTO.RaceDetailsDTO.MixedDTO(
                category=self.category,
                number=self.number,
            )

    mixed: MixedItem = field(default_factory=MixedItem)

    @staticmethod
    def from_dataTransferObject(dto: ZwiftRacingAppProfileDTO.RaceDetailsDTO) -> "RaceDetailsItem":
        return RaceDetailsItem(
            rating=dto.rating or 0.0,
            date=dto.date or 0,
            mixed=RaceDetailsItem.MixedItem.from_dataTransferObject(dto.mixed),
        )

    def to_dataTransferObject(self) -> ZwiftRacingAppProfileDTO.RaceDetailsDTO:
        return ZwiftRacingAppProfileDTO.RaceDetailsDTO(
            rating=self.rating,
            date=self.date,
            mixed=self.mixed.to_dataTransferObject(),
        )

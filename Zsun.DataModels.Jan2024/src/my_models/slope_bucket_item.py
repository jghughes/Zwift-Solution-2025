from dataclasses import dataclass
from typing import List

from slope_bucket_dto import SlopeBucketDTO


@dataclass() 
class SlopeBucketItem:
    bucket_description              : str = ""
    bucket_length_km                : float = 0.0 
    bucket_slope_pc                 : float = 0.0
    calculated_bucket_elevation_m  : float = 0.0
    calculated_bucket_watts        : float = 0.0
    calculated_bucket_speed_kph    : float = 0.0
    calculated_bucket_duration_sec : float = 0.0

    @staticmethod
    def from_dataTransferObject(dto: SlopeBucketDTO) -> "SlopeBucketItem":
        return SlopeBucketItem(
            bucket_description              = dto.bucket_description,
            bucket_length_km                = dto.bucket_length_km,
            bucket_slope_pc                 = dto.bucket_slope_pc,
            calculated_bucket_elevation_m  = dto.calculated_bucket_elevation_m,
            calculated_bucket_watts        = dto.calculated_bucket_watts,
            calculated_bucket_speed_kph    = dto.calculated_bucket_speed_kph,
            calculated_bucket_duration_sec = dto.calculated_bucket_duration_sec
        )

    @staticmethod
    def from_dataTransferObjectList(dto_list: List[SlopeBucketDTO]) -> List["SlopeBucketItem"]:
        return [SlopeBucketItem.from_dataTransferObject(dto) for dto in dto_list]

    @staticmethod
    def to_dataTransferObject(item: "SlopeBucketItem") -> SlopeBucketDTO:
        return SlopeBucketDTO(
            bucket_description              = item.bucket_description,
            bucket_length_km                = item.bucket_length_km,
            bucket_slope_pc                 = item.bucket_slope_pc,
            calculated_bucket_elevation_m  = item.calculated_bucket_elevation_m,
            calculated_bucket_watts        = item.calculated_bucket_watts,
            calculated_bucket_speed_kph    = item.calculated_bucket_speed_kph,
            calculated_bucket_duration_sec = item.calculated_bucket_duration_sec
        )

    @staticmethod
    def to_dataTransferObjectList(item_list: List["SlopeBucketItem"]) -> List[SlopeBucketDTO]:
        return [SlopeBucketItem.to_dataTransferObject(item) for item in item_list]



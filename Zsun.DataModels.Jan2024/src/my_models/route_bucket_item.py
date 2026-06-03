from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from route_segment_dto import RouteBucketDTO


@dataclass() 
class RouteBucketItem:
    num                 : int = 1
    bucket_description : str = ""
    bucket_length_km         : float = 0.0 
    bucket_slope_pc      : float = 0.0
    bucket_elevation_m : float = 0.0
    calculated_bucket_watts       : float = 0.0
    calculated_bucket_speed_kph   : float = 0.0
    calculated_bucket_duration_sec    : float = 0.0

    @staticmethod
    def from_dataTransferObject(dto: RouteBucketDTO) -> "RouteBucketItem":
        return RouteBucketItem(
            num                 = dto.num,
            bucket_description = dto.bucket_description,
            bucket_length_km         = dto.bucket_length_km,
            bucket_slope_pc      = dto.bucket_slope_pc,
            bucket_elevation_m = dto.bucket_elevation_m,
            calculated_bucket_watts       = dto.calculated_bucket_watts,
            calculated_bucket_speed_kph   = dto.calculated_bucket_speed_kph,
            calculated_bucket_duration_sec    = dto.calculated_bucket_duration_sec
        )

    @staticmethod
    def to_dataTransferObject(item: "RouteBucketItem") -> RouteBucketDTO:
        return RouteBucketDTO(
            num                 = item.num,
            bucket_description = item.bucket_description,
            bucket_length_km         = item.bucket_length_km,
            bucket_slope_pc      = item.bucket_slope_pc,
            bucket_elevation_m = item.bucket_elevation_m,
            calculated_bucket_watts       = item.calculated_bucket_watts,
            calculated_bucket_speed_kph   = item.calculated_bucket_speed_kph,
            calculated_bucket_duration_sec    = item.calculated_bucket_duration_sec
        )


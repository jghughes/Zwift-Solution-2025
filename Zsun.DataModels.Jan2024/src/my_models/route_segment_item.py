from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from route_segment_dto import RouteSegmentDTO


@dataclass() 
class RouteSegmentItem:
    num                 : int = 1
    distance_km         : float = 0.0 
    slope_per_cent      : float = 0.0 
    segment_watts       : float = 0.0
    segment_speed_kph   : float = 0.0
    segment_time_sec    : float = 0.0

    @staticmethod
    def from_dataTransferObject(dto: RouteSegmentDTO) -> "RouteSegmentItem":
        return RouteSegmentItem(
            num                 = dto.num,
            distance_km         = dto.distance_km,
            slope_per_cent      = dto.slope_per_cent,
            segment_watts      = dto.segment_watts,
            segment_speed_kph  = dto.segment_speed_kph,
            segment_time_sec = dto.segment_time_sec
        )

    @staticmethod
    def to_dataTransferObject(item: "RouteSegmentItem") -> RouteSegmentDTO:
        return RouteSegmentDTO(
            num                 = item.num,
            distance_km         = item.distance_km,
            slope_per_cent      = item.slope_per_cent,
            segment_watts      = item.segment_watts,
            segment_speed_kph  = item.segment_speed_kph,
            segment_time_sec = item.segment_time_sec
        )

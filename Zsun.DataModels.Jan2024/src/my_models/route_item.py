from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from route_segment_dto import RouteSegmentDTO
from route_segment_item import RouteSegmentItem
from route_dto import RouteDTO

@dataclass()
class RouteItem:
    route_name: str = ""
    route_description : str = ""
    advertised_distance_km : float = 0.0
    advertised_elevation_m : float = 0.0
    governing_intensity_factor : float = 0.0
    route_segments: List[RouteSegmentItem] = field(default_factory=list)

    @staticmethod
    def from_dataTransferObject(dto: RouteDTO) -> "RouteItem":
        return RouteItem(
            route_name = dto.route_name,
            route_description = dto.route_description,
            advertised_distance_km = dto.advertised_distance_km,
            advertised_elevation_m = dto.advertised_elevation_m,
            governing_intensity_factor = dto.governing_intensity_factor,
            route_segments = [RouteSegmentItem.from_dataTransferObject(segment_dto) for segment_dto in dto.segments]
        )

    @staticmethod
    def from_dataTransferObjectList(dto_list: List[RouteDTO]) -> List["RouteItem"]:
        return [RouteItem.from_dataTransferObject(dto) for dto in dto_list]

    @staticmethod
    def to_dataTransferObject(item: "RouteItem") -> RouteDTO:
        return RouteDTO(
            route_name = item.route_name,
            route_description = item.route_description,
            advertised_distance_km = item.advertised_distance_km,
            advertised_elevation_m = item.advertised_elevation_m,
            governing_intensity_factor = item.governing_intensity_factor,
            segments = [RouteSegmentItem.to_dataTransferObject(segment_item) for segment_item in item.route_segments]
        )

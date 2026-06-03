from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from route_segment_dto import RouteBucketDTO
from route_segment_item import RouteBucketItem
from route_dto import RouteDTO

@dataclass()
class RouteItem:
    route_name: str = ""
    zwift_world_name: str = ""
    route_description : str = ""
    route_length_km : float = 0.0
    route_elevation_m : float = 0.0
    lead_in_length_km : float = 0.0
    imposed_intensity_factor : float = 0.0
    route_buckets: List[RouteBucketItem] = field(default_factory=list)

    @staticmethod
    def from_dataTransferObject(dto: RouteDTO) -> "RouteItem":
        return RouteItem(
            route_name = dto.route_name,
            zwift_world_name = dto.zwift_world_name,
            route_description = dto.route_description,
            route_length_km = dto.route_length_km,
            route_elevation_m = dto.route_elevation_m,
            lead_in_length_km = dto.lead_in_length_km,
            imposed_intensity_factor = dto.imposed_intensity_factor,
            route_buckets = [RouteBucketItem.from_dataTransferObject(segment_dto) for segment_dto in dto.route_buckets]
        )

    @staticmethod
    def from_dataTransferObjectList(dto_list: List[RouteDTO]) -> List["RouteItem"]:
        return [RouteItem.from_dataTransferObject(dto) for dto in dto_list]

    @staticmethod
    def to_dataTransferObject(item: "RouteItem") -> RouteDTO:
        return RouteDTO(
            route_name = item.route_name,
            zwift_world_name = item.zwift_world_name,
            route_description = item.route_description,
            route_length_km = item.route_length_km,
            route_elevation_m = item.route_elevation_m,
            lead_in_length_km = item.lead_in_length_km,
            imposed_intensity_factor = item.imposed_intensity_factor,
            route_buckets = [RouteBucketItem.to_dataTransferObject(segment_item) for segment_item in item.route_buckets]
        )

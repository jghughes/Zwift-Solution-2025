from dataclasses import dataclass, field
from typing import List
from slope_bucket_item import SlopeBucketItem
from route_dto import RouteDTO
from rider_stats_item import RiderStatsItem

@dataclass()
class RouteItem:
    route_name                  : str = ""
    zwift_world_name            : str = ""
    route_description           : str = ""
    route_lead_in_km            : float = 0.0
    route_length_km             : float = 0.0
    route_elevation_m           : float = 0.0
    route_slope_buckets         : List[SlopeBucketItem] = field(default_factory=list)

    @staticmethod
    def from_dataTransferObject(dto: RouteDTO) -> "RouteItem":
        return RouteItem(
            route_name              = dto.route_name,
            zwift_world_name        = dto.zwift_world_name,
            route_description       = dto.route_description,
            route_lead_in_km        = dto.route_lead_in_km,
            route_length_km         = dto.route_length_km,
            route_elevation_m       = dto.route_elevation_m,
            route_slope_buckets     = [SlopeBucketItem.from_dataTransferObject(segment_dto) for segment_dto in dto.route_slope_buckets]
        )

    @staticmethod
    def from_dataTransferObjectList(dto_list: List[RouteDTO]) -> List["RouteItem"]:
        return [RouteItem.from_dataTransferObject(dto) for dto in dto_list]

    @staticmethod
    def to_dataTransferObject(item: "RouteItem") -> RouteDTO:
        return RouteDTO(
            route_name              = item.route_name,
            zwift_world_name        = item.zwift_world_name,
            route_description       = item.route_description,
            route_lead_in_km        = item.route_lead_in_km,
            route_length_km         = item.route_length_km,
            route_elevation_m       = item.route_elevation_m,
            route_slope_buckets     = [SlopeBucketItem.to_dataTransferObject(segment_item) for segment_item in item.route_slope_buckets]
        )

    @staticmethod
    def to_dataTransferObjectList(item_list: List["RouteItem"]) -> List[RouteDTO]:
        return [RouteItem.to_dataTransferObject(item) for item in item_list]

    @staticmethod
    def populate_riderStatsItem_with_routeItem(route_item: "RouteItem", rider_stats_item: RiderStatsItem) -> RiderStatsItem:
        rider_stats_item.route_name         = route_item.route_name
        rider_stats_item.zwift_world_name   = route_item.zwift_world_name
        rider_stats_item.route_description  = route_item.route_description
        rider_stats_item.route_lead_in_km   = route_item.route_lead_in_km
        rider_stats_item.route_length_km    = route_item.route_length_km
        rider_stats_item.route_elevation_m  = route_item.route_elevation_m
        return rider_stats_item

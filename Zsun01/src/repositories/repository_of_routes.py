from typing import List, Dict
from route_item import RouteItem
from route_segment_item import RouteSegmentItem


class RepositoryOfRoutes:
    """
    Static repository of hardcoded Zwift RouteItems, keyed by route name.

    Attributes:
        _routes_as_dict (Dict[str, RouteItem]):
            Maps route names to their corresponding RouteItem.

    Methods:
        get_RouteItems_as_dict():
            Returns the dictionary of all routes.
        get_RouteItem(name_as_key):
            Returns the RouteItem for the given route name, or raises ValueError if not found.
    """

    _routes_as_dict: Dict[str, RouteItem] = {

        "Tempus Fugit": RouteItem(
            route_name                  = "Tempus Fugit",
            zwift_map_name                    = "Watopia",
            route_description           = "A flat, fast route on Watopia's highway. Ideal for TT efforts.",
            route_length_km             = 17.1,
            route_elevation_m           = 43.0,
            lead_in_length_km           = 0.0,
            imposed_intensity_factor  = 1.0,
            route_segments              = [
                RouteSegmentItem(num=1, segment_description="Full flat loop", segment_length_km=17.1, slope_per_cent=0.0, segment_ascent_m=43.0, segment_watts=0.0, segment_speed_kph=0.0, segment_time_sec=0.0),
            ]
        ),

        "Alpe du Zwift": RouteItem(
            route_name                  = "Alpe du Zwift",
            zwift_map_name                    = "Watopia",
            route_description           = "A gruelling 21-hairpin climb modelled on Alpe d'Huez.",
            route_length_km             = 12.2,
            route_elevation_m           = 1036.0,
            lead_in_length_km           = 0.0,
            imposed_intensity_factor  = 1.0,
            route_segments              = [
                RouteSegmentItem(num=1, segment_description="Lower slopes", segment_length_km=4.0, slope_per_cent=8.5, segment_ascent_m=340.0, segment_watts=0.0, segment_speed_kph=0.0, segment_time_sec=0.0),
                RouteSegmentItem(num=2, segment_description="Mid climb",    segment_length_km=4.1, slope_per_cent=8.5, segment_ascent_m=349.0, segment_watts=0.0, segment_speed_kph=0.0, segment_time_sec=0.0),
                RouteSegmentItem(num=3, segment_description="Upper slopes", segment_length_km=4.1, slope_per_cent=8.5, segment_ascent_m=347.0, segment_watts=0.0, segment_speed_kph=0.0, segment_time_sec=0.0),
            ]
        ),

    }

    @staticmethod
    def get_RouteItems_as_dict() -> Dict[str, RouteItem]:
        return RepositoryOfRoutes._routes_as_dict

    @staticmethod
    def get_RouteItem(name_as_key: str) -> RouteItem:
        if name_as_key in RepositoryOfRoutes._routes_as_dict:
            return RepositoryOfRoutes._routes_as_dict[name_as_key]
        else:
            raise ValueError(
                f"Route '{name_as_key}' not found. Available routes: {list(RepositoryOfRoutes._routes_as_dict.keys())}"
            )
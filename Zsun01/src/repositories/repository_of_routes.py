from typing import List, Dict
from route_item import RouteItem
from slope_bucket_item import SlopeBucketItem


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

        "Tempus_Fugit": RouteItem(
            route_name                  = "Tempus Fugit",
            zwift_world_name              = "Watopia",
            route_description           = "A flat, fast route. Ideal for TT efforts.",
            route_length_km             = 17.3,
            route_elevation_m           = 103.0,
            lead_in_length_km           = 2.3,
            imposed_intensity_factor  = 1.0,
            route_slope_buckets              = [
                SlopeBucketItem(bucket_description="minus 2% bucket", bucket_length_km=0.129, bucket_slope_pc=-2.0),
                SlopeBucketItem(bucket_description="minus 1% bucket", bucket_length_km=1.520, bucket_slope_pc=-1.0),
                SlopeBucketItem(bucket_description="level 0% bucket", bucket_length_km=14.0, bucket_slope_pc=0.0),
                SlopeBucketItem(bucket_description="plus 1% bucket", bucket_length_km=1.484, bucket_slope_pc=1.0),
                SlopeBucketItem(bucket_description="plus 2% bucket", bucket_length_km=0.15, bucket_slope_pc=2.0),
            ]
        ),

        "Oh_Hill_No": RouteItem(
            route_name                  = "Oh Hill No",
            zwift_world_name              = "Watopia",
            route_description           = "The Grade (for FTP testing)",
            route_length_km             = 7.9,
            route_elevation_m           = 306,
            lead_in_length_km           = 0.2,
            imposed_intensity_factor  = 1.0,
            route_slope_buckets              = [
                SlopeBucketItem(bucket_description="minus 12% bucket", bucket_length_km=0.356, bucket_slope_pc=-12.0),
                SlopeBucketItem(bucket_description="minus 11% bucket", bucket_length_km=0.185, bucket_slope_pc=-11.0),
                SlopeBucketItem(bucket_description="minus 10% bucket", bucket_length_km=1.575, bucket_slope_pc=-10.0),
                SlopeBucketItem(bucket_description="minus 9% bucket", bucket_length_km=0.266, bucket_slope_pc=-9.0),
                SlopeBucketItem(bucket_description="minus 8% bucket", bucket_length_km=0.176, bucket_slope_pc=-8.0),
                SlopeBucketItem(bucket_description="minus 7% bucket", bucket_length_km=0.328, bucket_slope_pc=-7.0),
                SlopeBucketItem(bucket_description="minus 6% bucket", bucket_length_km=0.137, bucket_slope_pc=-6.0),
                SlopeBucketItem(bucket_description="minus 5% bucket", bucket_length_km=0.127, bucket_slope_pc=-5.0),
                SlopeBucketItem(bucket_description="minus 4% bucket", bucket_length_km=0.052, bucket_slope_pc=-4.0),
                SlopeBucketItem(bucket_description="minus 3% bucket", bucket_length_km=0.055, bucket_slope_pc=-3.0),
                SlopeBucketItem(bucket_description="minus 2% bucket", bucket_length_km=0.066, bucket_slope_pc=-2.0),
                SlopeBucketItem(bucket_description="minus 1% bucket", bucket_length_km=0.106, bucket_slope_pc=-1.0),
                SlopeBucketItem(bucket_description="level 0% bucket", bucket_length_km=0.954, bucket_slope_pc=0.0),
                SlopeBucketItem(bucket_description="plus 1% bucket", bucket_length_km=0.084, bucket_slope_pc=1.0),
                SlopeBucketItem(bucket_description="plus 2% bucket", bucket_length_km=0.062, bucket_slope_pc=2.0),
                SlopeBucketItem(bucket_description="plus 3% bucket", bucket_length_km=0.055, bucket_slope_pc=3.0),
                SlopeBucketItem(bucket_description="plus 4% bucket", bucket_length_km=0.071, bucket_slope_pc=4.0),
                SlopeBucketItem(bucket_description="plus 5% bucket", bucket_length_km=0.113, bucket_slope_pc=5.0),
                SlopeBucketItem(bucket_description="plus 6% bucket", bucket_length_km=0.183, bucket_slope_pc=6.0),
                SlopeBucketItem(bucket_description="plus 7% bucket", bucket_length_km=0.204, bucket_slope_pc=7.0),
                SlopeBucketItem(bucket_description="plus 8% bucket", bucket_length_km=0.201, bucket_slope_pc=8.0),
                SlopeBucketItem(bucket_description="plus 9% bucket", bucket_length_km=0.455, bucket_slope_pc=9.0),
                SlopeBucketItem(bucket_description="plus 10% bucket", bucket_length_km=1.240, bucket_slope_pc=10.0),
                SlopeBucketItem(bucket_description="plus 11% bucket", bucket_length_km=0.533, bucket_slope_pc=11.0),
                SlopeBucketItem(bucket_description="plus 12% bucket", bucket_length_km=0.114, bucket_slope_pc=12.0),
                SlopeBucketItem(bucket_description="plus 13% bucket", bucket_length_km=0.088, bucket_slope_pc=13.0),
            ]
        ),

        "Accelerate_to_Elevate": RouteItem(
            route_name                  = "Accelerate to Elevate",
            zwift_world_name              = "Watopia",
            route_description           = "Alpe du Zwift up and back down",
            route_length_km             = 41.0,
            route_elevation_m           = 1_153,
            lead_in_length_km           = 2.3,
            imposed_intensity_factor  = 1.0,
            route_slope_buckets              = [
                SlopeBucketItem(bucket_description="minus 3% bucket", bucket_length_km=0.734, bucket_slope_pc=-3.0),
                SlopeBucketItem(bucket_description="minus 2% bucket", bucket_length_km=1.786, bucket_slope_pc=-2.0),
                SlopeBucketItem(bucket_description="minus 1% bucket", bucket_length_km=4.282, bucket_slope_pc=-1.0),
                SlopeBucketItem(bucket_description="level 0% bucket", bucket_length_km=15_962.0, bucket_slope_pc=0.0),
                SlopeBucketItem(bucket_description="plus 1% bucket", bucket_length_km=3_170.00, bucket_slope_pc=1.0),
                SlopeBucketItem(bucket_description="plus 2% bucket", bucket_length_km=1_856.00, bucket_slope_pc=2.0),
                SlopeBucketItem(bucket_description="plus 3% bucket", bucket_length_km=728.0, bucket_slope_pc=3.0),
                SlopeBucketItem(bucket_description="plus 4% bucket", bucket_length_km=140.0, bucket_slope_pc=4.0),
                SlopeBucketItem(bucket_description="plus 5% bucket", bucket_length_km=0.629, bucket_slope_pc=5.0),
                SlopeBucketItem(bucket_description="plus 6% bucket", bucket_length_km=0.703, bucket_slope_pc=6.0),
                SlopeBucketItem(bucket_description="plus 7% bucket", bucket_length_km=1_045.0, bucket_slope_pc=7.0),
                SlopeBucketItem(bucket_description="plus 8% bucket", bucket_length_km=2_697.0, bucket_slope_pc=8.0),
                SlopeBucketItem(bucket_description="plus 9% bucket", bucket_length_km=3_566.0, bucket_slope_pc=9.0),
                SlopeBucketItem(bucket_description="plus 10% bucket", bucket_length_km=1_956.0, bucket_slope_pc=10.0),
                SlopeBucketItem(bucket_description="plus 11% bucket", bucket_length_km=1_220.0, bucket_slope_pc=11.0),
                SlopeBucketItem(bucket_description="plus 12% bucket", bucket_length_km=106.0, bucket_slope_pc=12.0), 

            ]
        ),

        # "Alpe-du-Zwift": RouteItem(
        #     route_name                  = "Alpe du Zwift",
        #     zwift_world_name              = "Watopia",
        #     route_description           = "A gruelling 21-hairpin climb modelled on Alpe d'Huez.",
        #     route_length_km             = 12.2,
        #     route_elevation_m           = 1036.0,
        #     lead_in_length_km           = 0.0,
        #     imposed_intensity_factor  = 1.0,
        #     route_slope_buckets              = [
        #         SlopeBucketItem(bucket_description="Lower slopes", bucket_length_km=4.0, bucket_slope_pc=8.5, bucket_elevation_m=340.0),
        #         SlopeBucketItem(bucket_description="Mid climb",    bucket_length_km=4.1, bucket_slope_pc=8.5, bucket_elevation_m=349.0),
        #         SlopeBucketItem(bucket_description="Upper slopes", bucket_length_km=4.1, bucket_slope_pc=8.5, bucket_elevation_m=347.0),
        #     ]
        # ),

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
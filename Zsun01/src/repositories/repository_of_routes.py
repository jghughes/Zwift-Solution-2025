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

        "Template": RouteItem(
            route_name          = "name",
            zwift_world_name    = "world",
            route_description   = "description",
            route_length_km     = 0.0,
            route_elevation_m   = 0,
            route_lead_in_km    = 0.0,
            route_slope_buckets = [
                SlopeBucketItem(bucket_description="minus 16% bucket", bucket_length_km=0.0, bucket_slope_pc=-16.0),
                SlopeBucketItem(bucket_description="minus 15% bucket", bucket_length_km=0.0, bucket_slope_pc=-15.0),
                SlopeBucketItem(bucket_description="minus 14% bucket", bucket_length_km=0.0, bucket_slope_pc=-14.0),
                SlopeBucketItem(bucket_description="minus 13% bucket", bucket_length_km=0.0, bucket_slope_pc=-13.0),
                SlopeBucketItem(bucket_description="minus 12% bucket", bucket_length_km=0.0, bucket_slope_pc=-12.0),
                SlopeBucketItem(bucket_description="minus 11% bucket", bucket_length_km=0.0, bucket_slope_pc=-11.0),
                SlopeBucketItem(bucket_description="minus 10% bucket", bucket_length_km=0.0, bucket_slope_pc=-10.0),
                SlopeBucketItem(bucket_description="minus 9% bucket", bucket_length_km=0.0, bucket_slope_pc=-9.0),
                SlopeBucketItem(bucket_description="minus 8% bucket", bucket_length_km=0.0, bucket_slope_pc=-8.0),
                SlopeBucketItem(bucket_description="minus 7% bucket", bucket_length_km=0.0, bucket_slope_pc=-7.0),
                SlopeBucketItem(bucket_description="minus 6% bucket", bucket_length_km=0.0, bucket_slope_pc=-6.0),
                SlopeBucketItem(bucket_description="minus 5% bucket", bucket_length_km=0.0, bucket_slope_pc=-5.0),
                SlopeBucketItem(bucket_description="minus 4% bucket", bucket_length_km=0.0, bucket_slope_pc=-4.0),
                SlopeBucketItem(bucket_description="minus 3% bucket", bucket_length_km=0.0, bucket_slope_pc=-3.0),
                SlopeBucketItem(bucket_description="minus 2% bucket", bucket_length_km=0.0, bucket_slope_pc=-2.0),
                SlopeBucketItem(bucket_description="minus 1% bucket", bucket_length_km=0.0, bucket_slope_pc=-1.0),
                SlopeBucketItem(bucket_description="level 0% bucket", bucket_length_km=0.0, bucket_slope_pc=0.0),
                SlopeBucketItem(bucket_description="plus 1% bucket", bucket_length_km=0.0, bucket_slope_pc=1.0),
                SlopeBucketItem(bucket_description="plus 2% bucket", bucket_length_km=0.0, bucket_slope_pc=2.0),
                SlopeBucketItem(bucket_description="plus 3% bucket", bucket_length_km=0.0, bucket_slope_pc=3.0),
                SlopeBucketItem(bucket_description="plus 4% bucket", bucket_length_km=0.0, bucket_slope_pc=4.0),
                SlopeBucketItem(bucket_description="plus 5% bucket", bucket_length_km=0.0, bucket_slope_pc=5.0),
                SlopeBucketItem(bucket_description="plus 6% bucket", bucket_length_km=0.0, bucket_slope_pc=6.0),
                SlopeBucketItem(bucket_description="plus 7% bucket", bucket_length_km=0.0, bucket_slope_pc=7.0),
                SlopeBucketItem(bucket_description="plus 8% bucket", bucket_length_km=0.0, bucket_slope_pc=8.0),
                SlopeBucketItem(bucket_description="plus 9% bucket", bucket_length_km=0.0, bucket_slope_pc=9.0),
                SlopeBucketItem(bucket_description="plus 10% bucket", bucket_length_km=0.0, bucket_slope_pc=10.0),
                SlopeBucketItem(bucket_description="plus 11% bucket", bucket_length_km=0.0, bucket_slope_pc=11.0),
                SlopeBucketItem(bucket_description="plus 12% bucket", bucket_length_km=0.0, bucket_slope_pc=12.0),
                SlopeBucketItem(bucket_description="plus 13% bucket", bucket_length_km=0.0, bucket_slope_pc=13.0),
                SlopeBucketItem(bucket_description="plus 14% bucket", bucket_length_km=0.0, bucket_slope_pc=14.0),
                SlopeBucketItem(bucket_description="plus 15% bucket", bucket_length_km=0.0, bucket_slope_pc=15.0),
                SlopeBucketItem(bucket_description="plus 16% bucket", bucket_length_km=0.0, bucket_slope_pc=16.0),
            ]
        ),

        "Alpe_d_huez": RouteItem(
            route_name          = "Alpe d'Huez",
            zwift_world_name    = "Watopia",
            route_description   = "Alpe du Zwift KOM",
            route_length_km     = 12.2,
            route_elevation_m   = 1035.0,
            route_lead_in_km    = 0.0,
            route_slope_buckets = [
                SlopeBucketItem(bucket_description="plus 3% bucket", bucket_length_km=0.05, bucket_slope_pc=3.0),
                SlopeBucketItem(bucket_description="plus 4% bucket", bucket_length_km=0.12, bucket_slope_pc=4.0),
                SlopeBucketItem(bucket_description="plus 5% bucket", bucket_length_km=0.57, bucket_slope_pc=5.0),
                SlopeBucketItem(bucket_description="plus 6% bucket", bucket_length_km=0.70, bucket_slope_pc=6.0),
                SlopeBucketItem(bucket_description="plus 7% bucket", bucket_length_km=1.26, bucket_slope_pc=7.0),
                SlopeBucketItem(bucket_description="plus 8% bucket", bucket_length_km=2.47, bucket_slope_pc=8.0),
                SlopeBucketItem(bucket_description="plus 9% bucket", bucket_length_km=3.69, bucket_slope_pc=9.0),
                SlopeBucketItem(bucket_description="plus 10% bucket", bucket_length_km=1.94, bucket_slope_pc=10.0),
                SlopeBucketItem(bucket_description="plus 11% bucket", bucket_length_km=1.24, bucket_slope_pc=11.0),
                SlopeBucketItem(bucket_description="plus 12% bucket", bucket_length_km=0.08, bucket_slope_pc=12.0),
            ]
        ),

        "Croix_de_fer": RouteItem(
            route_name          = "Col de la Croix de Fer",
            zwift_world_name    = "climb portal",
            route_description   = "description",
            route_length_km     = 27.9,
            route_elevation_m   = 1459.0,
            route_lead_in_km    = 0.0,
            route_slope_buckets = [
                SlopeBucketItem(bucket_description="minus 15% bucket", bucket_length_km=0.104, bucket_slope_pc=-15.0),
                SlopeBucketItem(bucket_description="minus 14% bucket", bucket_length_km=0.070, bucket_slope_pc=-14.0),
                SlopeBucketItem(bucket_description="minus 13% bucket", bucket_length_km=0.066, bucket_slope_pc=-13.0),
                SlopeBucketItem(bucket_description="minus 12% bucket", bucket_length_km=0.145, bucket_slope_pc=-12.0),
                SlopeBucketItem(bucket_description="minus 11% bucket", bucket_length_km=0.205, bucket_slope_pc=-11.0),
                SlopeBucketItem(bucket_description="minus 10% bucket", bucket_length_km=0.150, bucket_slope_pc=-10.0),
                SlopeBucketItem(bucket_description="minus 9% bucket", bucket_length_km=0.145, bucket_slope_pc=-9.0),
                SlopeBucketItem(bucket_description="minus 8% bucket", bucket_length_km=0.158, bucket_slope_pc=-8.0),
                SlopeBucketItem(bucket_description="minus 7% bucket", bucket_length_km=0.421, bucket_slope_pc=-7.0),
                SlopeBucketItem(bucket_description="minus 6% bucket", bucket_length_km=0.381, bucket_slope_pc=-6.0),
                SlopeBucketItem(bucket_description="minus 5% bucket", bucket_length_km=0.537, bucket_slope_pc=-5.0),
                SlopeBucketItem(bucket_description="minus 4% bucket", bucket_length_km=0.635, bucket_slope_pc=-4.0),
                SlopeBucketItem(bucket_description="minus 3% bucket", bucket_length_km=0.547, bucket_slope_pc=-3.0),
                SlopeBucketItem(bucket_description="minus 2% bucket", bucket_length_km=0.461, bucket_slope_pc=-2.0),
                SlopeBucketItem(bucket_description="minus 1% bucket", bucket_length_km=0.797, bucket_slope_pc=-1.0),
                SlopeBucketItem(bucket_description="level 0% bucket", bucket_length_km=1.224, bucket_slope_pc=0.0),
                SlopeBucketItem(bucket_description="plus 1% bucket", bucket_length_km=0.970, bucket_slope_pc=1.0),
                SlopeBucketItem(bucket_description="plus 2% bucket", bucket_length_km=0.626, bucket_slope_pc=2.0),
                SlopeBucketItem(bucket_description="plus 3% bucket", bucket_length_km=0.860, bucket_slope_pc=3.0),
                SlopeBucketItem(bucket_description="plus 4% bucket", bucket_length_km=1.279, bucket_slope_pc=4.0),
                SlopeBucketItem(bucket_description="plus 5% bucket", bucket_length_km=1.546, bucket_slope_pc=5.0),
                SlopeBucketItem(bucket_description="plus 6% bucket", bucket_length_km=2.624, bucket_slope_pc=6.0),
                SlopeBucketItem(bucket_description="plus 7% bucket", bucket_length_km=3.430, bucket_slope_pc=7.0),
                SlopeBucketItem(bucket_description="plus 8% bucket", bucket_length_km=2.893, bucket_slope_pc=8.0),
                SlopeBucketItem(bucket_description="plus 9% bucket", bucket_length_km=2.817, bucket_slope_pc=9.0),
                SlopeBucketItem(bucket_description="plus 10% bucket", bucket_length_km=2.440, bucket_slope_pc=10.0),
                SlopeBucketItem(bucket_description="plus 11% bucket", bucket_length_km=1.071, bucket_slope_pc=11.0),
                SlopeBucketItem(bucket_description="plus 12% bucket", bucket_length_km=0.600, bucket_slope_pc=12.0),
                SlopeBucketItem(bucket_description="plus 13% bucket", bucket_length_km=0.407, bucket_slope_pc=13.0),
            ]
        ),

        "Telegraphe": RouteItem(
            route_name          = "Col du Telegraphe",
            zwift_world_name    = "climb portal",
            route_description   = "description",
            route_length_km     = 12.0,
            route_elevation_m   = 634,
            route_lead_in_km    = 0.0,
            route_slope_buckets = [
                SlopeBucketItem(bucket_description="minus 1% bucket", bucket_length_km=0.048, bucket_slope_pc=-1.0),
                SlopeBucketItem(bucket_description="level 0% bucket", bucket_length_km=0.082, bucket_slope_pc=0.0),
                SlopeBucketItem(bucket_description="plus 1% bucket", bucket_length_km=0.00, bucket_slope_pc=1.0),
                SlopeBucketItem(bucket_description="plus 2% bucket", bucket_length_km=0.063, bucket_slope_pc=2.0),
                SlopeBucketItem(bucket_description="plus 3% bucket", bucket_length_km=0.128, bucket_slope_pc=3.0),
                SlopeBucketItem(bucket_description="plus 4% bucket", bucket_length_km=0.613, bucket_slope_pc=4.0),
                SlopeBucketItem(bucket_description="plus 5% bucket", bucket_length_km=1.151, bucket_slope_pc=5.0),
                SlopeBucketItem(bucket_description="plus 6% bucket", bucket_length_km=2.686, bucket_slope_pc=6.0),
                SlopeBucketItem(bucket_description="plus 7% bucket", bucket_length_km=2.893, bucket_slope_pc=7.0),
                SlopeBucketItem(bucket_description="plus 8% bucket", bucket_length_km=2.670, bucket_slope_pc=8.0),
                SlopeBucketItem(bucket_description="plus 9% bucket", bucket_length_km=1.383, bucket_slope_pc=9.0),
                SlopeBucketItem(bucket_description="plus 10% bucket", bucket_length_km=0.284, bucket_slope_pc=10.0),
                SlopeBucketItem(bucket_description="plus 11% bucket", bucket_length_km=0.108, bucket_slope_pc=11.0),
            ]
        ),

        "Galibier_valloire": RouteItem(
            route_name          = "Galibier Valloire",
            zwift_world_name    = "climb portal",
            route_description   = "Galibier from summit of Telegraphe",
            route_length_km     = 18.4,
            route_elevation_m   = 1247,
            route_lead_in_km    = 0.0,
            route_slope_buckets = [
                SlopeBucketItem(bucket_description="minus 1% bucket", bucket_length_km=0.056, bucket_slope_pc=-1.0),
                SlopeBucketItem(bucket_description="level 0% bucket", bucket_length_km=0.339, bucket_slope_pc=0.0),
                SlopeBucketItem(bucket_description="plus 1% bucket", bucket_length_km=0.466, bucket_slope_pc=1.0),
                SlopeBucketItem(bucket_description="plus 2% bucket", bucket_length_km=0.788, bucket_slope_pc=2.0),
                SlopeBucketItem(bucket_description="plus 3% bucket", bucket_length_km=1.026, bucket_slope_pc=3.0),
                SlopeBucketItem(bucket_description="plus 4% bucket", bucket_length_km=1.355, bucket_slope_pc=4.0),
                SlopeBucketItem(bucket_description="plus 5% bucket", bucket_length_km=1.263, bucket_slope_pc=5.0),
                SlopeBucketItem(bucket_description="plus 6% bucket", bucket_length_km=1.541, bucket_slope_pc=6.0),
                SlopeBucketItem(bucket_description="plus 7% bucket", bucket_length_km=3.198, bucket_slope_pc=7.0),
                SlopeBucketItem(bucket_description="plus 8% bucket", bucket_length_km=3.751, bucket_slope_pc=8.0),
                SlopeBucketItem(bucket_description="plus 9% bucket", bucket_length_km=2.474, bucket_slope_pc=9.0),
                SlopeBucketItem(bucket_description="plus 10% bucket", bucket_length_km=1.880, bucket_slope_pc=10.0),
                SlopeBucketItem(bucket_description="plus 11% bucket", bucket_length_km=0.177, bucket_slope_pc=11.0),
                SlopeBucketItem(bucket_description="plus 12% bucket", bucket_length_km=0.063, bucket_slope_pc=12.0),
            ]
        ),

        "Galibier_lauteret": RouteItem(
            route_name          = "Galibier",
            zwift_world_name    = "climb portal",
            route_description   = "Col du Galibier from Col du Lauteret (south side)",
            route_length_km     = 8.6,
            route_elevation_m   = 578,
            route_lead_in_km    = 0.0,
            route_slope_buckets = [
                SlopeBucketItem(bucket_description="plus 3% bucket", bucket_length_km=0.259, bucket_slope_pc=3.0),
                SlopeBucketItem(bucket_description="plus 4% bucket", bucket_length_km=0.285, bucket_slope_pc=4.0),
                SlopeBucketItem(bucket_description="plus 5% bucket", bucket_length_km=1.20, bucket_slope_pc=5.0),
                SlopeBucketItem(bucket_description="plus 6% bucket", bucket_length_km=2.27, bucket_slope_pc=6.0),
                SlopeBucketItem(bucket_description="plus 7% bucket", bucket_length_km=2.08, bucket_slope_pc=7.0),
                SlopeBucketItem(bucket_description="plus 8% bucket", bucket_length_km=1.84, bucket_slope_pc=8.0),
                SlopeBucketItem(bucket_description="plus 9% bucket", bucket_length_km=0.43, bucket_slope_pc=9.0),
                SlopeBucketItem(bucket_description="plus 10% bucket", bucket_length_km=0.19, bucket_slope_pc=10.0),
                SlopeBucketItem(bucket_description="plus 11% bucket", bucket_length_km=0.134, bucket_slope_pc=11.0),
            ]
        ),

        "Madeleine": RouteItem(
            route_name          = "Col de la Madeleine",
            zwift_world_name    = "climb portal",
            route_description   = "Col de la Madeleine climb",
            route_length_km     = 14.3,
            route_elevation_m   = 1118.0,
            route_lead_in_km    = 0.0,
            route_slope_buckets = [
                SlopeBucketItem(bucket_description="plus 1% bucket", bucket_length_km=0.062, bucket_slope_pc=1.0),
                SlopeBucketItem(bucket_description="plus 2% bucket", bucket_length_km=0.078, bucket_slope_pc=2.0),
                SlopeBucketItem(bucket_description="plus 3% bucket", bucket_length_km=0.071, bucket_slope_pc=3.0),
                SlopeBucketItem(bucket_description="plus 4% bucket", bucket_length_km=0.069, bucket_slope_pc=4.0),
                SlopeBucketItem(bucket_description="plus 5% bucket", bucket_length_km=0.364, bucket_slope_pc=5.0),
                SlopeBucketItem(bucket_description="plus 6% bucket", bucket_length_km=1.293, bucket_slope_pc=6.0),
                SlopeBucketItem(bucket_description="plus 7% bucket", bucket_length_km=2.830, bucket_slope_pc=7.0),
                SlopeBucketItem(bucket_description="plus 8% bucket", bucket_length_km=5.329, bucket_slope_pc=8.0),
                SlopeBucketItem(bucket_description="plus 9% bucket", bucket_length_km=3.229, bucket_slope_pc=9.0),
                SlopeBucketItem(bucket_description="plus 10% bucket", bucket_length_km=0.915, bucket_slope_pc=10.0),
            ]
        ),

        "Dummy_Descent": RouteItem(
            route_name              = "dummy descent",
            zwift_world_name        = "fantasy",
            route_description       = "4k descent @ -16%",
            route_length_km         = 4.0,
            route_elevation_m       = -200.0,
            route_lead_in_km        = 0.0,
            route_slope_buckets     = [
                SlopeBucketItem(bucket_description="minus 16% bucket", bucket_length_km=4.0, bucket_slope_pc=-16.0),
            ]
        ),

        "Tempus_Fugit": RouteItem(
            route_name          = "Tempus Fugit",
            zwift_world_name    = "Watopia",
            route_description   = "A flat, fast route. Ideal for TT efforts.",
            route_length_km     = 17.3,
            route_elevation_m   = 103.0,
            route_lead_in_km    = 2.3,
            route_slope_buckets = [
                SlopeBucketItem(bucket_description="minus 2% bucket", bucket_length_km=0.129, bucket_slope_pc=-2.0),
                SlopeBucketItem(bucket_description="minus 1% bucket", bucket_length_km=1.520, bucket_slope_pc=-1.0),
                SlopeBucketItem(bucket_description="level 0% bucket", bucket_length_km=14.0, bucket_slope_pc=0.0),
                SlopeBucketItem(bucket_description="plus 1% bucket", bucket_length_km=1.484, bucket_slope_pc=1.0),
                SlopeBucketItem(bucket_description="plus 2% bucket", bucket_length_km=0.15, bucket_slope_pc=2.0),
            ]
        ),

        "The_Grade_KOM": RouteItem(
            route_name          = "The Grade KOM",
            zwift_world_name    = "Watopia",
            route_description   = "The Grade KOM (for FTP testing)",
            route_length_km     = 3.52,
            route_elevation_m   = 305,
            route_lead_in_km    = 0.0,
            route_slope_buckets = [
                SlopeBucketItem(bucket_description="minus 1% bucket", bucket_length_km=0.010, bucket_slope_pc=-1.0),
                SlopeBucketItem(bucket_description="level 0% bucket", bucket_length_km=0.156, bucket_slope_pc=0.0),
                SlopeBucketItem(bucket_description="plus 1% bucket", bucket_length_km=0.054, bucket_slope_pc=1.0),
                SlopeBucketItem(bucket_description="plus 2% bucket", bucket_length_km=0.053, bucket_slope_pc=2.0),
                SlopeBucketItem(bucket_description="plus 3% bucket", bucket_length_km=0.047, bucket_slope_pc=3.0),
                SlopeBucketItem(bucket_description="plus 4% bucket", bucket_length_km=0.075, bucket_slope_pc=4.0),
                SlopeBucketItem(bucket_description="plus 5% bucket", bucket_length_km=0.096, bucket_slope_pc=5.0),
                SlopeBucketItem(bucket_description="plus 6% bucket", bucket_length_km=0.187, bucket_slope_pc=6.0),
                SlopeBucketItem(bucket_description="plus 7% bucket", bucket_length_km=0.213, bucket_slope_pc=7.0),
                SlopeBucketItem(bucket_description="plus 8% bucket", bucket_length_km=0.195, bucket_slope_pc=8.0),
                SlopeBucketItem(bucket_description="plus 9% bucket", bucket_length_km=0.451, bucket_slope_pc=9.0),
                SlopeBucketItem(bucket_description="plus 10% bucket", bucket_length_km=1.25, bucket_slope_pc=10.0),
                SlopeBucketItem(bucket_description="plus 11% bucket", bucket_length_km=0.528, bucket_slope_pc=11.0),
                SlopeBucketItem(bucket_description="plus 12% bucket", bucket_length_km=0.112, bucket_slope_pc=12.0),
                SlopeBucketItem(bucket_description="plus 13% bucket", bucket_length_km=0.093, bucket_slope_pc=13.0),
            ]
        ),

        "The_Grade_KOM_v2": RouteItem(
            route_name              = "The Grade KOM v2",
            zwift_world_name        = "Watopia",
            route_description       = "steady climb",
            route_length_km         = 3.52,
            route_elevation_m       = 305,
            route_lead_in_km        = 0.0,
            route_slope_buckets     = [
                SlopeBucketItem(bucket_description="minus 1% bucket", bucket_length_km=0.010, bucket_slope_pc=-1.0),
                SlopeBucketItem(bucket_description="level 0% bucket", bucket_length_km=0.156, bucket_slope_pc=0.0),
                SlopeBucketItem(bucket_description="plus 1% bucket", bucket_length_km=0.054, bucket_slope_pc=1.0),
                SlopeBucketItem(bucket_description="plus 2% bucket", bucket_length_km=0.053, bucket_slope_pc=2.0),
                SlopeBucketItem(bucket_description="plus 3% bucket", bucket_length_km=0.047, bucket_slope_pc=3.0),
                SlopeBucketItem(bucket_description="plus 4% bucket", bucket_length_km=0.075, bucket_slope_pc=4.0),
                SlopeBucketItem(bucket_description="plus 5% bucket", bucket_length_km=0.096, bucket_slope_pc=5.0),
                SlopeBucketItem(bucket_description="plus 6% bucket", bucket_length_km=0.187, bucket_slope_pc=6.0),
                SlopeBucketItem(bucket_description="plus 7% bucket", bucket_length_km=0.213, bucket_slope_pc=7.0),
                SlopeBucketItem(bucket_description="plus 8% bucket", bucket_length_km=0.195, bucket_slope_pc=8.0),
                SlopeBucketItem(bucket_description="plus 9% bucket", bucket_length_km=0.451, bucket_slope_pc=9.0),
                SlopeBucketItem(bucket_description="plus 10% bucket", bucket_length_km=1.25, bucket_slope_pc=10.0),
                SlopeBucketItem(bucket_description="plus 11% bucket", bucket_length_km=0.528, bucket_slope_pc=11.0),
                SlopeBucketItem(bucket_description="plus 12% bucket", bucket_length_km=0.112, bucket_slope_pc=12.0),
                SlopeBucketItem(bucket_description="plus 13% bucket", bucket_length_km=0.093, bucket_slope_pc=13.0),
            ]
        ),

        "Alto_de_Patios": RouteItem(
            route_name              = "Alto de Patios",
            zwift_world_name        = "Climb Portal",
            route_description       = "Alto de Patios",
            route_length_km         = 5.9,
            route_elevation_m       = 377,
            route_lead_in_km        = 0.0,
            route_slope_buckets     = [
                SlopeBucketItem(bucket_description="minus 8% bucket", bucket_length_km=0.032, bucket_slope_pc=-8.0),
                SlopeBucketItem(bucket_description="minus 7% bucket", bucket_length_km=0.025, bucket_slope_pc=-7.0),
                SlopeBucketItem(bucket_description="plus 2% bucket", bucket_length_km=0.109, bucket_slope_pc=2.0),
                SlopeBucketItem(bucket_description="plus 3% bucket", bucket_length_km=0.205, bucket_slope_pc=3.0),
                SlopeBucketItem(bucket_description="plus 4% bucket", bucket_length_km=0.226, bucket_slope_pc=4.0),
                SlopeBucketItem(bucket_description="plus 5% bucket", bucket_length_km=0.801, bucket_slope_pc=5.0),
                SlopeBucketItem(bucket_description="plus 6% bucket", bucket_length_km=1.727, bucket_slope_pc=6.0),
                SlopeBucketItem(bucket_description="plus 7% bucket", bucket_length_km=1.480, bucket_slope_pc=7.0),
                SlopeBucketItem(bucket_description="plus 8% bucket", bucket_length_km=0.623, bucket_slope_pc=8.0),
                SlopeBucketItem(bucket_description="plus 9% bucket", bucket_length_km=0.132, bucket_slope_pc=9.0),
            ]
        ),

        "Oh_Hill_No": RouteItem(
            route_name              = "Oh Hill No",
            zwift_world_name        = "Watopia",
            route_description       = "Oh Hill No (for FTP testing)",
            route_length_km         = 7.9,
            route_elevation_m       = 306,
            route_lead_in_km        = 0.2,
            route_slope_buckets     = [
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
            route_name              = "Accelerate to Elevate",
            zwift_world_name        = "Watopia",
            route_description       = "Alpe du Zwift and return",
            route_length_km         = 41.0,
            route_elevation_m       = 1153,
            route_lead_in_km        = 2.3,
            route_slope_buckets     = [
                SlopeBucketItem(bucket_description="minus 3% bucket", bucket_length_km=0.734, bucket_slope_pc=-3.0),
                SlopeBucketItem(bucket_description="minus 2% bucket", bucket_length_km=1.786, bucket_slope_pc=-2.0),
                SlopeBucketItem(bucket_description="minus 1% bucket", bucket_length_km=4.282, bucket_slope_pc=-1.0),
                SlopeBucketItem(bucket_description="level 0% bucket", bucket_length_km=15.962, bucket_slope_pc=0.0),
                SlopeBucketItem(bucket_description="plus 1% bucket", bucket_length_km=3.170, bucket_slope_pc=1.0),
                SlopeBucketItem(bucket_description="plus 2% bucket", bucket_length_km=1.856, bucket_slope_pc=2.0),
                SlopeBucketItem(bucket_description="plus 3% bucket", bucket_length_km=0.728, bucket_slope_pc=3.0),
                SlopeBucketItem(bucket_description="plus 4% bucket", bucket_length_km=1.40, bucket_slope_pc=4.0),
                SlopeBucketItem(bucket_description="plus 5% bucket", bucket_length_km=0.629, bucket_slope_pc=5.0),
                SlopeBucketItem(bucket_description="plus 6% bucket", bucket_length_km=0.703, bucket_slope_pc=6.0),
                SlopeBucketItem(bucket_description="plus 7% bucket", bucket_length_km=1.045, bucket_slope_pc=7.0),
                SlopeBucketItem(bucket_description="plus 8% bucket", bucket_length_km=2.697, bucket_slope_pc=8.0),
                SlopeBucketItem(bucket_description="plus 9% bucket", bucket_length_km=3.566, bucket_slope_pc=9.0),
                SlopeBucketItem(bucket_description="plus 10% bucket", bucket_length_km=1.956, bucket_slope_pc=10.0),
                SlopeBucketItem(bucket_description="plus 11% bucket", bucket_length_km=1.220, bucket_slope_pc=11.0),
                SlopeBucketItem(bucket_description="plus 12% bucket", bucket_length_km=0.106, bucket_slope_pc=12.0), 

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
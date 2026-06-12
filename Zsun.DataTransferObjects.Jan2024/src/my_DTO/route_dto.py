from typing import Dict, List
from pydantic import BaseModel, RootModel, Field
from slope_bucket_dto import SlopeBucketDTO

# this class belongs to me, so I don't need the paraphenalia 
# for pydantic validation_alias_choices_map, etc

class RouteDTO(BaseModel):
    route_name              : str = ""
    zwift_world_name        : str = ""
    route_description       : str = ""
    route_length_km         : float = 0.0
    route_elevation_m       : float = 0.0
    route_lead_in_length_km       : float = 0.0
    # imposed_intensity_factor : float = 0.0
    route_slope_buckets: List[SlopeBucketDTO] = Field(default_factory=list)

class RouteDTODictModel(RootModel[Dict[str, RouteDTO]]):
    pass

class RouteDTOListModel(RootModel[List[RouteDTO]]):
    pass


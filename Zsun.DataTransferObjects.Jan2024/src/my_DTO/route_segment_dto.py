from typing import Dict, List
from pydantic import BaseModel, RootModel

# this class belongs to me, so I don't need the paraphenalia 
# for pydantic validation_alias_choices_map, etc

class RouteSegmentDTO(BaseModel):
    num                 : int = 1
    distance_km         : float = 0.0 
    slope_per_cent      : float = 0.0 
    segment_watts      : float = 0.0
    segment_speed_kph  : float = 0.0
    segment_time_sec : float = 0.0

class RouteSegmentDTODictModel(RootModel[Dict[str, RouteSegmentDTO]]):
    pass

class RouteSegmentDTOListModel(RootModel[List[RouteSegmentDTO]]):
    pass


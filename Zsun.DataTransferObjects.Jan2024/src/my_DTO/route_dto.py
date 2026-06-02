from typing import Dict, List
from pydantic import BaseModel, RootModel, Field
from route_segment_dto import RouteSegmentDTO

# this class belongs to me, so I don't need the paraphenalia 
# for pydantic validation_alias_choices_map, etc

class RouteDTO(BaseModel):
    route_name: str = ""
    route_description: str = ""
    advertised_distance_km : float = 0.0
    advertised_elevation_m : float = 0.0
    governing_intensity_factor : float = 0.0
    segments: List[RouteSegmentDTO] = Field(default_factory=list)

class RouteDTODictModel(RootModel[Dict[str, RouteDTO]]):
    pass

class RouteDTOListModel(RootModel[List[RouteDTO]]):
    pass


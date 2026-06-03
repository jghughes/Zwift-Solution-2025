from typing import Dict, List
from pydantic import BaseModel, RootModel

# this class belongs to me, so I don't need the paraphenalia 
# for pydantic validation_alias_choices_map, etc

class RouteBucketDTO(BaseModel):
    num                             : int = 1
    bucket_description             : str = ""
    bucket_length_km               : float = 0.0 
    bucket_slope_pc                  : float = 0.0 
    bucket_elevation_m             : float = 0.0
    calculated_bucket_watts        : float = 0.0
    calculated_bucket_speed_kph    : float = 0.0
    calculated_bucket_duration_sec : float = 0.0

class RouteBucketDTODictModel(RootModel[Dict[str, RouteBucketDTO]]):
    pass

class RouteBucketDTOListModel(RootModel[List[RouteBucketDTO]]):
    pass


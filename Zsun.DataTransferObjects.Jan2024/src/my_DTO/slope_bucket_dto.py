from typing import Dict, List
from pydantic import BaseModel, RootModel

# this class belongs to me, so I don't need the paraphenalia 
# for pydantic validation_alias_choices_map, etc

class SlopeBucketDTO(BaseModel):
    bucket_description             : str = ""
    bucket_length_km               : float = 0.0 
    bucket_slope_pc                : float = 0.0 
    calculated_bucket_elevation_m  : float = 0.0
    calculated_bucket_watts        : float = 0.0
    calculated_bucket_speed_kph    : float = 0.0
    calculated_bucket_duration_sec : float = 0.0

class SlopeBucketDTODictModel(RootModel[Dict[str, SlopeBucketDTO]]):
    pass

class SlopeBucketDTOListModel(RootModel[List[SlopeBucketDTO]]):
    pass


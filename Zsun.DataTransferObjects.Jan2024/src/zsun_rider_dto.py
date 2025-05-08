from pydantic import BaseModel, AliasChoices, ConfigDict, AliasGenerator
from typing import Optional
from jgh_read_write import *
from jgh_serialization import *


validation_alias_choices_map: dict[str, AliasChoices] = {}

configdictV1 = ConfigDict(
        alias_generator=AliasGenerator(
            alias=None,
            validation_alias=lambda field_name: validation_alias_choices_map.get(field_name, field_name)))

preferred_config_dict = configdictV1

class ZsunRiderDTO(BaseModel):
    model_config                     = preferred_config_dict
    zwift_id                         : Optional[str]   = ""    # Zwift ID of the rider
    name                             : Optional[str]   = ""    # Name of the rider
    weight_kg                        : Optional[float] = 0.0   # Weight of the rider in kilograms
    height_cm                        : Optional[float] = 0.0   # Height of the rider in centimeters
    gender                           : Optional[str]   = ""    # Gender of the rider, m or f
    age_years                        : Optional[float] = 0.0   # Age of the rider in years
    agegroup                         : Optional[str]   = ""    # Age group of the rider
    zwift_ftp                        : Optional[float] = 0.0   # Originates in Zwift profile
    zwiftpower_zFTP                  : Optional[float] = 0.0   # Originates in Zwiftpower profile
    zwiftracingapp_zpFTP             : Optional[float] = 0.0   # Originates in Zwiftracingapp profile
    zsun_one_hour_watts              : Optional[float] = 0.0   # Calculated by JGH
    zsun_CP                          : Optional[float] = 0.0   # Critical power in watts
    zsun_AWC                         : Optional[float] = 0.0   # Critical power W' in kilojoules
    zwift_zrs                        : Optional[float] = 0.0   # Zwift racing score
    zwift_cat                        : Optional[str]   = ""    # A+, A, B, C, D, E
    zwiftracingapp_score             : Optional[float] = 0.0   # Velo score typically over 1000
    zwiftracingapp_cat_num           : Optional[int]   = 0     # Velo rating 1 to 10
    zwiftracingapp_cat_name          : Optional[str]   = ""    # Copper, Silver, Gold etc
    zwiftracingapp_CP                : Optional[float] = 0.0   # Critical power in watts
    zwiftracingapp_AWC               : Optional[float] = 0.0   # Anaerobic work capacity in kilojoules
    zsun_one_hour_curve_coefficient  : Optional[float] = 0.0   # Coefficient for FTP modeling
    zsun_one_hour_curve_exponent     : Optional[float] = 0.0   # Exponent for FTP modeling
    zsun_TTT_pull_curve_coefficient  : Optional[float] = 0.0   # Coefficient for pull modeling
    zsun_TTT_pull_curve_exponent     : Optional[float] = 0.0   # Exponent for pull modeling
    zsun_TTT_pull_curve_fit_r_squared: Optional[float] = 0.0   # R-squared value for the curve fit of the pull data
    zsun_when_curves_fitted          : Optional[str]   = ""    # Timestamp indicating when the models were fitted

def main02():
    import json

    # Simulate loading JSON data
    input_json = '''
    {
        "zwift_id": "123",
        "name": "null",
        "weight_kg": 70.5,
        "height_cm": 180,
        "gender": "m",
        "zwiftpower_zFTP": null,
    }
    '''
    data = json.loads(input_json)

    # Validate and serialize
    rider = ZsunRiderDTO(**data)
    print(rider)  # Check the validated model
    print(rider.model_dump())  # Check the serialized output

if __name__ == "__main__":
    main02()


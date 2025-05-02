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
    model_config               = preferred_config_dict
    zwift_id                   : Optional[str]   = ""    # Zwift ID of the rider
    name                       : Optional[str]   = ""    # Name of the rider
    weight_kg                  : Optional[float] = 0     # Weight of the rider in kilograms
    height_cm                  : Optional[float] = 0     # Height of the rider in centimeters
    gender                     : Optional[str]   = ""    # Gender of the rider, m or f
    age_years                  : Optional[float] = 0     # Age of the rider in years
    agegroup                   : Optional[str]   = ""    # Age group of the rider
    zwift_zftp                 : Optional[float] = 0     # Functional Threshold Power in watts
    zwift_zrs                  : Optional[float] = 0     # Zwift racing score
    zwift_cat                  : Optional[str]   = ""    # A+, A, B, C, D, E
    velo_score                 : Optional[float] = 0.0   # Velo score typically over 1000
    velo_cat_num               : Optional[int]   = 0     # Velo rating 1 to 10
    velo_cat_name              : Optional[str]   = ""    # Copper, Silver, Gold etc
    velo_cp                    : Optional[float] = 0.0   # Critical power in watts
    velo_awc                   : Optional[float] = 0.0   # Anaerobic work capacity in kilojoules
    jgh_pull_adjustment_watts  : Optional[float] = 0.0   # Adjustment watts for pulling
    jgh_cp                     : Optional[float] = 0.0   # Critical power in watts
    jgh_w_prime                : Optional[float] = 0.0   # Critical power W' in kilojoules
    jgh_ftp_curve_coefficient  : Optional[float] = 0.0   # Coefficient for FTP modeling
    jgh_ftp_curve_exponent     : Optional[float] = 0.0   # Exponent for FTP modeling
    jgh_pull_curve_coefficient : Optional[float] = 0.0   # Coefficient for pull modeling
    jgh_pull_curve_exponent    : Optional[float] = 0.0   # Exponent for pull modeling
    jgh_when_curves_fitted     : Optional[str]   = ""    # Timestamp indicating when the models were fitted

def main02():
    import json

    # Simulate loading JSON data
    input_json = '''
    {
        "zwiftid": "123",
        "name": "null",
        "weight_kg": 70.5,
        "height_cm": 180,
        "gender": "m",
        "zwift_zftp": null,
    }
    '''
    data = json.loads(input_json)

    # Validate and serialize
    rider = ZsunRiderDTO(**data)
    print(rider)  # Check the validated model
    print(rider.model_dump())  # Check the serialized output

# def main():
#     import logging
#     from jgh_logging import jgh_configure_logging
#     # Configure logging
#     jgh_configure_logging("appsettings.json")
#     logger = logging.getLogger(__name__)

#     file_name = "zwiftrider_dictionary.json"
#     directory_path = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

#     inputjson = read_text(directory_path, file_name)

#     dict_of_zwiftriders = JghSerialization.validate(inputjson, dict[str, ZsunRiderDTO])

#     # Convert the dictionary to a list of lists for tabulate
#     table_data = [
#         [key] + list(vars(rider).values()) for key, rider in dict_of_zwiftriders.items()
#     ]
#     headers = ["ZwiftID", "Name", "Weight", "Height", "Gen", "FTP", "ZRScore", "Velo Rating"]

#     # Log the table
#     logger.info("\n" + tabulate(table_data, headers=headers, tablefmt="simple"))

if __name__ == "__main__":
    main02()
    # main()


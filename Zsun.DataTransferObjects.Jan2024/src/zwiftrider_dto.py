# Local application imports
from pydantic import BaseModel, AliasChoices, ConfigDict, AliasGenerator
from typing import Optional
from tabulate import tabulate
from jgh_read_write import *
from jgh_serialization import *


# Define constants for all the serialization aliases - for now, they are the same as the attribute names
ZWIFTID_ALIAS = "zwiftid"
NAME_ALIAS = "name"
WEIGHT_ALIAS = "weight"
HEIGHT_ALIAS = "height"
GENDER_ALIAS = "gender"
FTP_ALIAS = "zftp"
ZWIFT_RACING_SCORE_ALIAS = "zwift_racing_score"
VELO_RATING_ALIAS = "velo_rating"

serialization_alias_map: dict[str, str] = {
    "zwiftid": ZWIFTID_ALIAS,
    "name": NAME_ALIAS,
    "weight": WEIGHT_ALIAS,
    "height": HEIGHT_ALIAS,
    "gender": GENDER_ALIAS,
    "zftp": FTP_ALIAS,
    "zwift_racing_score": ZWIFT_RACING_SCORE_ALIAS,
    "velo_rating": VELO_RATING_ALIAS,
}

validation_alias_choices_map: dict[str, AliasChoices] = {
    "zwiftid": AliasChoices("zwiftid", "zwift_id"),
    "name": AliasChoices("name", "zwift_name"),
    "weight": AliasChoices("weight"),
    "height": AliasChoices("height"),
    "gender": AliasChoices("gender"),
    "zftp": AliasChoices("zftp", "zftp"),
    "zwift_racing_score": AliasChoices("zwift_racing_score"),
    "velo_rating": AliasChoices("velo_rating"),
}

configdictV1 = ConfigDict(
        alias_generator=AliasGenerator(
            alias=None,
            serialization_alias=lambda field_name: serialization_alias_map.get(field_name, field_name), 
            validation_alias=lambda field_name: validation_alias_choices_map.get(field_name, field_name)))

preferred_config_dict = configdictV1

class ZwiftRiderDTO(BaseModel):
    """
    A data transfer object representing a zwiftrider's particulars. The object
    can be round-tripped to and from JSON. The values of all attributes are
    preserved in the JSON serialization and deserialization.

    This class derives from Pydantic's BaseModel, making it powerful for serialization
    and validation (deserialization). Each attribute has a serialization_alias
    and validation_alias. The serialization_alias governs the nomenclature of the
    output of serialization. The validation_alias governs the input of JSON.
    The validation_alias consists of a list of AliasChoices. The list must always
    include a string copy of the attribute name. Additional AliasChoices enable
    the data transfer object to interpret and validate (deserialize)
    any envisaged range of variations in the JSON field names in source data
    obtained from a third party. The name mapping is done in the AliasChoices list.

    Note: in Python, timestamps are in seconds since epoch. This is not the case 
    in all languages. Be aware of this when interfacing with other systems.


    Attributes:
        zwiftid            : int    The Zwift ID of the rider.
        name               : str    The name of the rider.
        weight             : float  The weight of the rider in kilograms.
        height             : float  The height of the rider in centimeters.
        gender             : Gender The gender of the rider.
        zftp                : float  Functional Threshold Power in watts.
        zwift_racing_score : int    Zwift racing score.
        velo_rating        : int    Velo rating.
    """
    model_config = preferred_config_dict
    zwiftid            : Optional[int]   = 0   # Zwift ID of the rider
    name               : Optional[str]   = ""  # Name of the rider
    weight             : Optional[float] = 0   # Weight of the rider in kilograms
    height             : Optional[float] = 0   # Height of the rider in centimeters
    gender             : Optional[str]   = ""  # Gender of the rider, m or f
    zftp               : Optional[float] = 0   # Functional Threshold Power in watts
    zwift_racing_score : Optional[int]   = 0   # Zwift racing score
    velo_rating        : Optional[int]   = 0   # Velo rating


class ZwiftRiderPowerDTO(BaseModel):
    """
    A data transfer object representing a Zwift rider's critical power data - derived from the data recorded on ZwiftPower.
    """
    model_config = preferred_config_dict

    zwiftid             : Optional[int] = 0
    name                : Optional[str] = ""
    adjustment_watts    : float = 0.0
    cp                  : float = 0.0
    cp_w_prime            : float = 0.0
    ftp_coefficient       : float = 0.0
    ftp_exponent          : float = 0.0
    pull_coefficient      : float = 0.0
    pull_exponent         : float = 0.0
    ftp_r_squared         : float = 0.0
    pull_r_squared        : float = 0.0
    when_models_fitted    : str   = "" 


def main():
    import logging
    from jgh_logging import jgh_configure_logging
    # Configure logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    file_name = "zwiftrider_dictionary.json"
    directory_path = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

    inputjson = read_text(directory_path, file_name)

    dict_of_zwiftriders = JghSerialization.validate(inputjson, dict[str, ZwiftRiderDTO])

    # Convert the dictionary to a list of lists for tabulate
    table_data = [
        [key] + list(vars(rider).values()) for key, rider in dict_of_zwiftriders.items()
    ]
    headers = ["ZwiftID", "Name", "Weight", "Height", "Gen", "FTP", "ZRScore", "Velo Rating"]

    # Log the table
    logger.info("\n" + tabulate(table_data, headers=headers, tablefmt="simple"))

if __name__ == "__main__":
    main()


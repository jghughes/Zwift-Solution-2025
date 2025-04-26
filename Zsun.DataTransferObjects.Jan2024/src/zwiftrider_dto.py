# Local application imports
from pydantic import BaseModel, AliasChoices, ConfigDict, AliasGenerator
from tabulate import tabulate
from jgh_read_write import *
from jgh_serialization import *


# Define constants for all the serialization_alias_map - for now, they are the same as the attribute names
ZWIFTID_ALIAS             = "zwiftid"
NAME_ALIAS                = "name"
WEIGHT_ALIAS              = "weight"
HEIGHT_ALIAS              = "height"
GENDER_ALIAS              = "gender"
FTP_ALIAS                 = "zftp"
ZWIFT_RACING_SCORE_ALIAS  = "zwift_racing_score"
VELO_RATING_ALIAS         = "velo_rating"
PULL_ADJUSTMENT_ALIAS     = "pull_adjustment_watts"
CP_ALIAS                  = "critical_power"
CP_W_PRIME_ALIAS          = "critical_power_w_prime"
FTP_COEFFICIENT_ALIAS     = "ftp_curve_coefficient"
FTP_EXPONENT_ALIAS        = "ftp_curve_exponent"
PULL_COEFFICIENT_ALIAS    = "pull_curve_coefficient"
PULL_EXPONENT_ALIAS       = "pull_curve_exponent"
WHEN_MODELS_FITTED_ALIAS  = "when_curves_fitted"

serialization_alias_map: dict[str, str] = {
    "zwiftid"               : ZWIFTID_ALIAS,
    "name"                  : NAME_ALIAS,
    "weight"                : WEIGHT_ALIAS,
    "height"                : HEIGHT_ALIAS,
    "gender"                : GENDER_ALIAS,
    "zftp"                  : FTP_ALIAS,
    "zwift_racing_score"    : ZWIFT_RACING_SCORE_ALIAS,
    "velo_rating"           : VELO_RATING_ALIAS,
    "pull_adjustment_watts" : PULL_ADJUSTMENT_ALIAS,
    "critical_power"        : CP_ALIAS,
    "critical_power_w_prime": CP_W_PRIME_ALIAS,
    "ftp_curve_coefficient" : FTP_COEFFICIENT_ALIAS,
    "ftp_curve_exponent"    : FTP_EXPONENT_ALIAS,
    "pull_curve_coefficient": PULL_COEFFICIENT_ALIAS,
    "pull_curve_exponent"   : PULL_EXPONENT_ALIAS,
    "when_curves_fitted"    : WHEN_MODELS_FITTED_ALIAS,
    }

validation_alias_choices_map: dict[str, AliasChoices] = {
    "zwiftid"               : AliasChoices("zwiftid", "zwift_id", "riderId"),
    "name"                  : AliasChoices("name", "zwift_name"),
    "weight"                : AliasChoices("weight"),
    "height"                : AliasChoices("height"),
    "gender"                : AliasChoices("gender"),
    "zftp"                  : AliasChoices("zftp", "zpFTP"),
    "zwift_racing_score"    : AliasChoices("zwift_racing_score"),
    "velo_rating"           : AliasChoices("velo_rating"),
    "pull_adjustment_watts" : AliasChoices("pull_adjustment_watts", "pull_adjustment"),
    "critical_power"        : AliasChoices("critical_power"),
    "critical_power_w_prime": AliasChoices("critical_power_w_prime"),
    "ftp_curve_coefficient" : AliasChoices("ftp_curve_coefficient"),
    "ftp_curve_exponent"    : AliasChoices("ftp_curve_exponent"),
    "pull_curve_coefficient": AliasChoices("pull_curve_coefficient"),
    "pull_curve_exponent"   : AliasChoices("pull_curve_exponent"),
    "when_curves_fitted"    : AliasChoices("when_curves_fitted"),
}

configdictV1 = ConfigDict(
        alias_generator=AliasGenerator(
            alias=None,
            serialization_alias=lambda field_name: serialization_alias_map.get(field_name, field_name), 
            validation_alias=lambda field_name: validation_alias_choices_map.get(field_name, field_name)))

preferred_config_dict = configdictV1

class ZwiftRiderDTO(BaseModel):
    """
    A data transfer object representing a Zwift rider's particulars. The object
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

    Note:
        In Python, timestamps are in seconds since epoch. This is not the case 
        in all languages. Be aware of this when interfacing with other systems.

    Attributes:
        zwiftid                : int     The Zwift ID of the rider.
        name                   : str     The name of the rider.
        weight                 : float   The weight of the rider in kilograms.
        height                 : float   The height of the rider in centimeters.
        gender                 : str     The gender of the rider ('m' for male, 'f' for female).
        zftp                   : float   Functional Threshold Power (FTP) in watts.
        zwift_racing_score     : int     The Zwift racing score of the rider.
        velo_rating            : int     The Velo rating of the rider.
        pull_adjustment_watts  : float   Adjustment watts for pulling.
        critical_power         : float   Critical power in watts.
        critical_power_w_prime : float   Critical power W' (work capacity above CP) in kilojoules.
        ftp_curve_coefficient  : float   Coefficient for FTP modeling.
        ftp_curve_exponent     : float   Exponent for FTP modeling.
        pull_curve_coefficient : float   Coefficient for pull modeling.
        pull_curve_exponent    : float   Exponent for pull modeling.
        when_curves_fitted     : str     Timestamp indicating when the models were fitted.
    """
    model_config           = preferred_config_dict
    zwiftid                : Optional[int]   = 0     # Zwift ID of the rider
    name                   : Optional[str]   = ""    # Name of the rider
    weight                 : Optional[float] = 0     # Weight of the rider in kilograms
    height                 : Optional[float] = 0     # Height of the rider in centimeters
    gender                 : Optional[str]   = ""    # Gender of the rider, m or f
    zftp                   : Optional[float] = 0     # Functional Threshold Power in watts
    zwift_racing_score     : Optional[int]   = 0     # Zwift racing score
    velo_rating            : Optional[int]   = 0     # Velo rating
    pull_adjustment_watts  : Optional[float] = 0.0
    critical_power         : Optional[float] = 0.0
    critical_power_w_prime : Optional[float] = 0.0
    ftp_curve_coefficient  : Optional[float] = 0.0
    ftp_curve_exponent     : Optional[float] = 0.0
    pull_curve_coefficient : Optional[float] = 0.0
    pull_curve_exponent    : Optional[float] = 0.0
    when_curves_fitted     : Optional[str]   = ""


def main02():
    import json

    # Simulate loading JSON data
    input_json = '''
    {
        "zwiftid": 123,
        "name": "null",
        "weight": 70.5,
        "height": 180,
        "gender": "m",
        "zftp": null,
        "strava_profile": null
    }
    '''
    data = json.loads(input_json)

    # Validate and serialize
    rider = ZwiftRiderDTO(**data)
    print(rider)  # Check the validated model
    print(rider.model_dump())  # Check the serialized output

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
    main02()
    # main()


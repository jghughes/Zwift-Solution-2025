# Local application imports
from pydantic import BaseModel
from typing import Optional
from tabulate import tabulate
from jgh_read_write import *
from jgh_serialization import *

# WARNING: This is a simple version.
# The object is extensible. It can be extended to handle almost infinitely 
# advanced scenarios.

class ZwiftRiderDataTransferObject(BaseModel):
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
        ftp                : float  Functional Threshold Power in watts.
        zwift_racing_score : int    Zwift racing score.
        velo_rating        : int    Velo rating.
    """
    zwiftid            : Optional[int]   = 0   # Zwift ID of the rider
    name               : Optional[str]   = ""  # Name of the rider
    weight             : Optional[float] = 0   # Weight of the rider in kilograms
    height             : Optional[float] = 0   # Height of the rider in centimeters
    gender             : Optional[str]   = ""  # Gender of the rider, m or f
    ftp                : Optional[float] = 0   # Functional Threshold Power in watts
    zwift_racing_score : Optional[int]   = 0   # Zwift racing score
    velo_rating        : Optional[int]   = 0   # Velo rating
def main():
    import logging
    from jgh_logging import jgh_configure_logging
    # Configure logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    inputjson = read_text("C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun.DataTransferObjects.Jan2024/data/", "rider_dictionary.json")

    dict_of_zwiftriders = JghSerialization.validate(inputjson, dict[str, ZwiftRiderDataTransferObject])

    # Convert the dictionary to a list of lists for tabulate
    table_data = [
        [key] + list(vars(rider).values()) for key, rider in dict_of_zwiftriders.items()
    ]
    headers = ["ZwiftID", "Name", "Weight", "Height", "Gen", "FTP", "ZRScore", "Velo Rating"]

    # Log the table
    logger.info("\n" + tabulate(table_data, headers=headers, tablefmt="simple"))

if __name__ == "__main__":
    main()

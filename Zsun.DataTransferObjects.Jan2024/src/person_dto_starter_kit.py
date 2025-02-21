# Local application imports
from pydantic import BaseModel

# Configure logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# WARNING: This is a simple version of a PersonDataTransferObject.
# The object is extensible. It can be extended to handle almost infinitely 
# advanced scenarios.

class PersonDataTransferObject(BaseModel):
    """
    A data transfer object representing a club member's particulars. The object
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
        zsun_id                    : str  The ZSUN ID of the member.
        zsun_firstname             : str  The ZSUN first name of the member.
        zsun_lastname              : str  The ZSUN last name of the member.
        zwift_id                   : int  The Zwift ID of the member.
        zwift_firstname            : str  The Zwift first name of the member.
        zwift_lastname             : str  The Zwift last name of the member.
        discord_accountusername    : str  The Discord account username of the member.
        discord_accountdisplayname : str  The Discord account display name of the member.
        discord_profiledisplayname : str  The Discord profile display name of the member.
        comment                    : str  An optional comment about the member or entry.
        database_action_enum       : str  The database action enum.
        must_ditch_originating_item: bool Indicates if the originating record must be ditched.
        is_still_to_be_backed_up   : bool Indicates if the record is still to be backed up locally.
        is_still_to_be_pushed      : bool Indicates if the record is still to be pushed to storage.
        touched_by                 : str  The user who touched the record.
        timestamp_binary_format    : int  The timestamp when created.
        when_touched_binary_format : int  The timestamp when edited.
        when_pushed_binary_format  : int  The timestamp when pushed to the database.
        originating_item_guid      : str  The GUID of the originating record.
        guid                       : str  The GUID of the record.    
        
    Properties:
        None

    Methods:
        __str__:                            Override to make a pretty string of the object.

    Functions:
        None
    """

    zsun_id: str | None = ""
    zsun_firstname: str | None = ""
    zsun_lastname: str | None = ""
    zwift_id: int | None = 0
    zwift_firstname: str | None = ""
    zwift_lastname: str | None = ""
    discord_accountusername: str | None = ""
    discord_accountdisplayname: str | None = ""
    discord_profiledisplayname: str | None = ""
    comment: str | None = ""
    click_counter: int | None = 0
    recording_mode_enum: str | None = ""
    database_action_enum: str | None = ""
    must_ditch_originating_item: bool | None = False
    is_still_to_be_backed_up: bool | None = True
    is_still_to_be_pushed: bool | None = True
    touched_by: str | None = ""
    timestamp_binary_format: int | None = 0
    when_touched_binary_format: int | None = 0
    when_pushed_binary_format: int | None = 0
    originating_item_guid: str | None = ""
    guid: str | None = ""

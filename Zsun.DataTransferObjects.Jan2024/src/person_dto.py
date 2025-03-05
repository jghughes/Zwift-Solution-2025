"""
This module defines the PersonDataTransferObject class, which is used to represent a person 
with various attributes.
"""

# Standard library imports
import json
from pydantic import BaseModel, AliasChoices, ConfigDict, AliasGenerator
from typing import Optional

# Local application imports

# Define constants for all the serialization aliases - for now, they are the same as the attribute names
ZSUN_ID = "zsun_id"
ZSUN_FIRSTNAME = "zsun_firstname"
ZSUN_LASTNAME = "zsun_lastname"
ZWIFT_ID = "zwift_id"
ZWIFT_FIRSTNAME = "zwift_firstname"
ZWIFT_LASTNAME = "zwift_lastname"
DISCORD_ACCOUNTUSERNAME = "discord_accountusername"
DISCORD_ACCOUNTDISPLAYNAME = "discord_accountdisplayname"
DISCORD_PROFILEDISPLAYNAME = "discord_profiledisplayname"
COMMENT = "comment"
CLICK_COUNTER = "click_counter"
RECORDING_MODE_ENUM = "recording_mode_enum"
DATABASE_ACTION_ENUM = "database_action_enum"
MUST_DITCH_ORIGINATING_ITEM = "must_ditch_originating_item"
IS_STILL_TO_BE_BACKED_UP = "is_still_to_be_backed_up"
IS_STILL_TO_BE_PUSHED = "is_still_to_be_pushed"
TOUCHED_BY = "touched_by"
TIMESTAMP_BINARY_FORMAT = "timestamp_binary_format"
WHEN_TOUCHED_BINARY_FORMAT = "when_touched_binary_format"
WHEN_PUSHED_BINARY_FORMAT = "when_pushed_binary_format"
ORIGINATING_ITEM_GUID = "originating_item_guid"
GUID = "guid"

# Define the serialization alias map using the constants
serialization_alias_map : dict[str,str]  = {
    "zsun_id": ZSUN_ID,
    "zsun_firstname": ZSUN_FIRSTNAME,
    "zsun_lastname": ZSUN_LASTNAME,
    "zwift_id": ZWIFT_ID,
    "zwift_firstname": ZWIFT_FIRSTNAME,
    "zwift_lastname": ZWIFT_LASTNAME,
    "discord_accountusername": DISCORD_ACCOUNTUSERNAME,
    "discord_accountdisplayname": DISCORD_ACCOUNTDISPLAYNAME,
    "discord_profiledisplayname": DISCORD_PROFILEDISPLAYNAME,
    "comment": COMMENT,
    "click_counter": CLICK_COUNTER,
    "recording_mode_enum": RECORDING_MODE_ENUM,
    "database_action_enum": DATABASE_ACTION_ENUM,
    "must_ditch_originating_item": MUST_DITCH_ORIGINATING_ITEM,
    "is_still_to_be_backed_up": IS_STILL_TO_BE_BACKED_UP,
    "is_still_to_be_pushed": IS_STILL_TO_BE_PUSHED,
    "touched_by": TOUCHED_BY,
    "timestamp_binary_format": TIMESTAMP_BINARY_FORMAT,
    "when_touched_binary_format": WHEN_TOUCHED_BINARY_FORMAT,
    "when_pushed_binary_format": WHEN_PUSHED_BINARY_FORMAT,
    "originating_item_guid": ORIGINATING_ITEM_GUID,
    "guid": GUID,
}

# Define the validation alias choices map. for now, they are only the attribute names. 
# more may added later to optionally handle JSON from varying sources with varying field names
# that mean the same thing.

validation_alias_choices_map : dict[str,AliasChoices] = {
    "zsun_id": AliasChoices("zsun_id"),
    "zsun_firstname": AliasChoices("zsun_firstname"),
    "zsun_lastname": AliasChoices("zsun_lastname"),
    "zwift_id": AliasChoices("zwift_id"),
    "zwift_firstname": AliasChoices("zwift_firstname"),
    "zwift_lastname": AliasChoices("zwift_lastname"),
    "discord_accountusername": AliasChoices("discord_accountusername"),
    "discord_accountdisplayname": AliasChoices("discord_accountdisplayname"),
    "discord_profiledisplayname": AliasChoices("discord_profiledisplayname"),
    "comment": AliasChoices("comment"),
    "click_counter": AliasChoices("click_counter"),
    "recording_mode_enum": AliasChoices("recording_mode_enum"),
    "database_action_enum": AliasChoices("database_action_enum"),
    "must_ditch_originating_item": AliasChoices("must_ditch_originating_item"),
    "is_still_to_be_backed_up": AliasChoices("is_still_to_be_backed_up"),
    "is_still_to_be_pushed": AliasChoices("is_still_to_be_pushed"),
    "touched_by": AliasChoices("touched_by"),
    "timestamp_binary_format": AliasChoices("timestamp_binary_format"),
    "when_touched_binary_format": AliasChoices("when_touched_binary_format"),
    "when_pushed_binary_format": AliasChoices("when_pushed_binary_format"),
    "originating_item_guid": AliasChoices("originating_item_guid"),
    "guid": AliasChoices("guid"),
}
# Define the Pydantic ConfigDict
configdictV1 = ConfigDict(
        alias_generator=AliasGenerator(
            alias=None,
            serialization_alias=lambda field_name: serialization_alias_map.get(field_name, field_name), 
            validation_alias=lambda field_name: validation_alias_choices_map.get(field_name, field_name)))

preferred_config_dict = configdictV1


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

    zsun_id: Optional[str] = ""
    zsun_firstname: Optional[str] = ""
    zsun_lastname: Optional[str] = ""
    zwift_id: Optional[int] = 0
    zwift_firstname: Optional[str] = ""
    zwift_lastname: Optional[str] = ""
    discord_accountusername: Optional[str] = ""
    discord_accountdisplayname: Optional[str] = ""
    discord_profiledisplayname: Optional[str] = ""
    comment: Optional[str] = ""
    click_counter: Optional[int] = 0
    recording_mode_enum: Optional[str] = ""
    database_action_enum: Optional[str] = ""
    must_ditch_originating_item: Optional[bool] = False
    is_still_to_be_backed_up: Optional[bool] = True
    is_still_to_be_pushed: Optional[bool] = True
    touched_by: Optional[str] = ""
    timestamp_binary_format: Optional[int] = 0
    when_touched_binary_format: Optional[int] = 0
    when_pushed_binary_format: Optional[int] = 0
    originating_item_guid: Optional[str] = ""
    guid: Optional[str] = ""

    model_config = preferred_config_dict

    # overridden to pretty-print JSON representation of the object with nice indentation
    def __str__(self):
        return json.dumps(self.model_dump(), indent=4)


# simple example usage of the PersonDataTransferObject class
def main():
    """
    This function creates an instance of the PersonDataTransferObject class with sample data
    and prints the JSON representation of the instance. It serves as a test
    to ensure that the PersonDataTransferObject class is working correctly and that the
    JSON serialization and deserialization are functioning as expected.
    """
    person = PersonDataTransferObject(
        zsun_id="12345",
        zsun_firstname="John",
        zsun_lastname="Doe",
        zwift_id=67890,
        zwift_firstname="Jane",
        zwift_lastname="Smith",
        discord_accountusername="john_doe",
        discord_accountdisplayname="John Doe",
        discord_profiledisplayname="Johnny",
        comment="Test comment",
        database_action_enum="INSERT",
        must_ditch_originating_item=False,
        is_still_to_be_backed_up=True,
        is_still_to_be_pushed=False,
        touched_by="admin",
        timestamp_binary_format=1633072800,
        when_touched_binary_format=1633072800,
        when_pushed_binary_format=1633072800,
        originating_item_guid="abc-123-def-456",
        guid="xyz-789-ghi-012",
    )
    print(person)


# do the examples (but not if this script is imported as a module)
if __name__ == "__main__":
    main()

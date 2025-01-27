"""
This module defines the PersonDataTransferObject class, which is used to represent a person 
with various attributes.
"""

# Standard library imports
import json

# Local application imports
from pydantic import BaseModel, Field, AliasChoices


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
    the data transfer object to effortlessly interpret and validate (deserialize)
    any envisaged range of variations in the JSON field names in the records provided 
    to it. The name mapping is done in the AliasChoices list.

    Attributes:
        zsun_id (str):                      The ZSUN ID of the member.
        zsun_firstname (str):               The ZSUN first name of the member.
        zsun_lastname (str):                The ZSUN last name of the member.
        zwift_id (int):                     The Zwift ID of the member.
        zwift_firstname (str):              The Zwift first name of the member.
        zwift_lastname (str):               The Zwift last name of the member.
        discord_accountusername (str):      The Discord account username of the member.
        discord_accountdisplayname (str):   The Discord account display name of the member.
        discord_profiledisplayname (str):   The Discord profile display name of the member.
        comment (str):                      An optional comment about the member or entry.
        database_action_enum (str):         The database action enum.
        must_ditch_originating_item (bool): Indicates if the originating record must be ditched.
        is_still_to_be_backed_up (bool):    Indicates if the record is still to be backed up locally.
        is_still_to_be_pushed (bool):       Indicates if the record is still to be pushed to storage.
        touched_by (str):                   The user who touched the record.
        timestamp_binary_format (int):      The timestamp_binary_format in seconds since epoch.
        when_touched_binary_format (int):   The when touched timestamp_binary_format in seconds since epoch.
        when_pushed_binary_format (int):    The when pushed timestamp_binary_format in seconds since epoch.
        originating_item_guid (str):        The GUID of the originating record.
        guid (str):                         The GUID of the record.

    Properties:
        None

    Methods:
        __str__:                            Override to make a pretty string of the object.

    Functions:
        None
    """

    zsun_id: str = Field(
        default="",
        serialization_alias="zsun_id",
        validation_alias=AliasChoices("zsun_id"),
    )
    zsun_firstname: str = Field(
        default="",
        serialization_alias="zsun_firstname",
        validation_alias=AliasChoices("zsun_firstname"),
    )
    zsun_lastname: str = Field(
        default="",
        serialization_alias="zsun_lastname",
        validation_alias=AliasChoices("zsun_lastname"),
    )
    zwift_id: int = Field(
        default=0,
        serialization_alias="zwift_id",
        validation_alias=AliasChoices("zwift_id"),
    )
    zwift_firstname: str = Field(
        default="",
        serialization_alias="zwift_firstname",
        validation_alias=AliasChoices("zwift_firstname"),
    )
    zwift_lastname: str = Field(
        default="",
        serialization_alias="zwift_lastname",
        validation_alias=AliasChoices("zwift_lastname"),
    )
    discord_accountusername: str = Field(
        default="",
        serialization_alias="discord_accountusername",
        validation_alias=AliasChoices("discord_accountusername"),
    )
    discord_accountdisplayname: str = Field(
        default="",
        serialization_alias="discord_accountdisplayname",
        validation_alias=AliasChoices("discord_accountdisplayname"),
    )
    discord_profiledisplayname: str = Field(
        default="",
        serialization_alias="discord_profiledisplayname",
        validation_alias=AliasChoices("discord_profiledisplayname"),
    )
    comment: str = Field(
        default="",
        serialization_alias="comment",
        validation_alias=AliasChoices("comment"),
    )
    click_counter: int = Field(
        default=0,
        serialization_alias="click_counter",
        validation_alias=AliasChoices("click_counter"),
    )
    recording_mode_enum: str = Field(
        default="",
        serialization_alias="recording_mode_enum",
        validation_alias=AliasChoices("recording_mode_enum"),
    )
    database_action_enum: str = Field(
        default="",
        serialization_alias="database_action_enum",
        validation_alias=AliasChoices("database_action_enum"),
    )
    must_ditch_originating_item: bool = Field(
        default=False,
        serialization_alias="must_ditch_originating_item",
        validation_alias=AliasChoices("must_ditch_originating_item"),
    )
    is_still_to_be_backed_up: bool = Field(
        default=True,
        serialization_alias="is_still_to_be_backed_up",
        validation_alias=AliasChoices("is_still_to_be_backed_up"),
    )
    is_still_to_be_pushed: bool = Field(
        default=True,
        serialization_alias="is_still_to_be_pushed",
        validation_alias=AliasChoices("is_still_to_be_pushed"),
    )
    touched_by: str = Field(
        default="",
        serialization_alias="touched_by",
        validation_alias=AliasChoices("touched_by"),
    )
    timestamp_binary_format: int = Field(
        default=0,
        serialization_alias="timestamp_binary_format",
        validation_alias=AliasChoices("timestamp_binary_format"),
    )
    when_touched_binary_format: int = Field(
        default=0,
        serialization_alias="when_touched_binary_format",
        validation_alias=AliasChoices("when_touched_binary_format"),
    )
    when_pushed_binary_format: int = Field(
        default=0,
        serialization_alias="when_pushed_binary_format",
        validation_alias=AliasChoices("when_pushed_binary_format"),
    )
    originating_item_guid: str = Field(
        default="",
        serialization_alias="originating_item_guid",
        validation_alias=AliasChoices("originating_item_guid"),
    )
    guid: str = Field(
        default="", serialization_alias="guid", validation_alias=AliasChoices("guid")
    )

    # Override the default Pydantic behavior so as to tolerate and ignore extra fields in any JSON input string
    class Config:
        extra = "ignore"

    # overridden to pretty-print JSON representation of the object with nice indentation
    def __str__(self):
        return json.dumps(self.model_dump(), indent=4)


# simple example usage of the PersonDataTransferObject class
def illustrative_example_usages_of_person_dto():
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
    illustrative_example_usages_of_person_dto()

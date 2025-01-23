"""
This module defines the PersonDto class, which is used to represent a person 
with various attributes.
"""

# Standard library imports
import json

# Local application imports
from pydantic import BaseModel, Field



class PersonDto(BaseModel):
    """
    A data transfer object representing a club member's particulars. The object
    can be round-tripped to and from JSON. The values of all attributes are
    preserved in the JSON serialization and deserialization.

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
        timestamp_binary_format (int):                    The timestamp_binary_format in seconds since epoch.
        when_touched_binary_format (int):                 The when touched timestamp_binary_format in seconds since epoch.
        when_pushed_binary_format (int):                  The when pushed timestamp_binary_format in seconds since epoch.
        originating_item_guid (str):        The GUID of the originating record.
        guid (str):                         The GUID of the record.

    Properties:
        None

    Methods:
        __str__:                            Override to make a pretty string of the item.

    Functions:
        None
    """

    zsun_id: str = Field(default="", serialization_alias="zsun_id")
    zsun_firstname: str = Field(default="", serialization_alias="zsun_firstname")
    zsun_lastname: str = Field(default="", serialization_alias="zsun_lastname")
    zwift_id: int = Field(default=0, serialization_alias="zwift_id")
    zwift_firstname: str = Field(default="", serialization_alias="zwift_firstname")
    zwift_lastname: str = Field(default="", serialization_alias="zwift_lastname")
    discord_accountusername: str = Field(default="", serialization_alias="discord_accountusername")
    discord_accountdisplayname: str = Field(
        default="", serialization_alias="discord_accountdisplayname"
    )
    discord_profiledisplayname: str = Field(
        default="", serialization_alias="discord_profiledisplayname"
    )
    comment: str = Field(default="", serialization_alias="comment")
    click_counter: str = Field(default="", serialization_alias="click_counter")
    recording_mode_enum: str = Field(default="", serialization_alias="recording_mode_enum")
    database_action_enum: str = Field(default="", serialization_alias="database_action_enum")
    must_ditch_originating_item: bool = Field(
        default=False, serialization_alias="must_ditch_originating_item"
    )
    is_still_to_be_backed_up: bool = Field(
        default=True, serialization_alias="is_still_to_be_backed_up"
    )
    is_still_to_be_pushed: bool = Field(default=True, serialization_alias="is_still_to_be_pushed")
    touched_by: str = Field(default="", serialization_alias="touched_by")
    timestamp_binary_format: float = Field(default=0, serialization_alias="timestamp_binary_format")
    when_touched_binary_format: float = Field(default=0, serialization_alias="when_touched_binary_format")
    when_pushed_binary_format: float = Field(default=0, serialization_alias="when_pushed_binary_format")
    originating_item_guid: str = Field(default="", serialization_alias="originating_item_guid")
    guid: str = Field(default="", serialization_alias="guid")

    # Override the default Pydantic behavior so as to tolerate and ignore extra fields in any JSON input string
    class Config:
        extra = "ignore"

    # overridden to pretty-print JSON representation of the object with nice indentation
    def __str__(self):
        return json.dumps(self.model_dump(), indent=4)


# simple example usage of the PersonDto class
def illustrative_example_usages_of_person_dto():
    """
    This function creates an instance of the PersonDto class with sample data
    and prints the JSON representation of the instance. It serves as a test
    to ensure that the PersonDto class is working correctly and that the
    JSON serialization and deserialization are functioning as expected.
    """
    person = PersonDto(
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

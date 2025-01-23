from pydantic import BaseModel, Field
import json

class PersonDataTransferObject(BaseModel):
    """
    A data transfer object representing a club member's particulars.
    The object can be round-tripped to and from JSON.
    The value of all attributes is preserved in the JSON serialization and deserialization.

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
        is_still_to_be_pushed (bool):       Indicates if the record is still to be pushed to the cloud storage.
        touched_by (str):                   The user who touched the record.
        timestamp (int):                    The timestamp in seconds since epoch.
        when_touched (int):                 The when touched timestamp in seconds since epoch.
        when_pushed (int):                  The when pushed timestamp in seconds since epoch.
        originating_item_guid (str):        The GUID of the originating record.
        guid (str):                         The GUID of the record.

    Properties:
        None

    Methods:
        __str__:                            Override to make a pretty string of the item.

    Functions:
        None
    """

    zsun_id: str = Field(default="", alias="zsun_id")
    zsun_firstname: str = Field(default="", alias="zsun_firstname")
    zsun_lastname: str = Field(default="", alias="zsun_lastname")
    zwift_id: int = Field(default=0, alias="zwift_id")
    zwift_firstname: str = Field(default="", alias="zwift_firstname")
    zwift_lastname: str = Field(default="", alias="zwift_lastname")
    discord_accountusername: str = Field(default="", alias="discord_accountusername")
    discord_accountdisplayname: str = Field(default="", alias="discord_accountdisplayname")
    discord_profiledisplayname: str = Field(default="", alias="discord_profiledisplayname")
    comment: str = Field(default="", alias="comment")
    click_counter: str = Field(default="", alias="click_counter")
    recording_mode_enum: str = Field(default="", alias="recording_mode_enum")
    database_action_enum: str = Field(default="", alias="database_action_enum")
    must_ditch_originating_item: bool = Field(default=False, alias="must_ditch_originating_item")
    is_still_to_be_backed_up: bool = Field(default=True, alias="is_still_to_be_backed_up")
    is_still_to_be_pushed: bool = Field(default=False, alias="is_still_to_be_pushed")
    touched_by: str = Field(default="", alias="touched_by")
    timestamp: float = Field(default=0, alias="timestamp")
    when_touched: float = Field(default=0, alias="when_touched")
    when_pushed: float = Field(default=0, alias="when_pushed")
    originating_item_guid: str = Field(default="", alias="originating_item_guid")
    guid: str = Field(default="", alias="guid")

    # Override the default Pydantic behavior so as to tolerate and ignore extra fields in any JSON input string
    class Config:
        extra = "ignore"

    # overridden to pretty-print
    def __str__(self): 
        return json.dumps(self.model_dump(), indent=4)

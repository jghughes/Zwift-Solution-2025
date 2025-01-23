from pydantic import AliasChoices, BaseModel, Field

class ClubMemberDto(BaseModel):
    """
    A data transfer object for a club member. The alias's are dummies for now.

    -   serialization_alias is the name of the property in exported JSON file.
    -    validation_alias is the name of the field in imported JSON file.

    The list of validation aliases must always include the actual name of the attribute.
    You can add to the list one or more candidate field names for the expected/likely/possible incoming JSON. 
    """
    primarykey: str = Field(default="", serialization_alias="primarykey", validation_alias=AliasChoices("primarykey"))
    zsun_id: str = Field(default="", serialization_alias="zsun_id", validation_alias=AliasChoices("zsun_id"))
    zsun_firstname: str = Field(default="", serialization_alias="zsun_firstname", validation_alias=AliasChoices("zsun_firstname"))
    zsun_lastname: str = Field(default="", serialization_alias="zsun_lastname", validation_alias=AliasChoices("zsun_lastname"))
    zwift_id: int = Field(default=0, serialization_alias="zwift_id", validation_alias=AliasChoices("zwift_id"))
    zwift_firstname: str = Field(default="", serialization_alias="zwift_firstname", validation_alias=AliasChoices("zwift_firstname"))
    zwift_lastname: str = Field(default="", serialization_alias="zwift_lastname", validation_alias=AliasChoices("zwift_lastname"))
    discord_accountusername: str = Field(default="", serialization_alias="discord_accountusername", validation_alias=AliasChoices("discord_accountusername"))
    discord_accountdisplayname: str = Field(default="", serialization_alias="discord_accountdisplayname", validation_alias=AliasChoices("discord_accountdisplayname"))
    discord_profiledisplayname: str = Field(default="", serialization_alias="discord_profiledisplayname", validation_alias=AliasChoices("discord_profiledisplayname"))
    when_touched: int = Field(default=0, serialization_alias="when_touched", validation_alias=AliasChoices("when_touched"))
    originating_guid: str = Field(default="", serialization_alias="originating_guid", validation_alias=AliasChoices("originating_guid"))
    comment: str = Field(default="", serialization_alias="comment", validation_alias=AliasChoices("comment"))


import datetime
from datetime import datetime, timezone
import json
import uuid
from pydantic import BaseModel, Field, PrivateAttr

from PersonDataClass import PersonDataTransferObject


class PersonItem(BaseModel):
    """
    An object representing a club member's particulars.
    The object self-sets its own GUID and timestamp upon instantiation. The setters are private.
    The object can be round-tripped to and from JSON using PersonDataTransferObject.
    Despite being private, the GUID and timestamp are preserved in a round-trip.

    Attributes:
        zsun_id (str):                      The ZSUN ID of the person.
        zsun_firstname (str):               The ZSUN first name of the person.
        zsun_lastname (str):                The ZSUN last name of the person.
        zwift_id (int):                     The Zwift ID of the person.
        zwift_firstname (str):              The Zwift first name of the person.
        zwift_lastname (str):               The Zwift last name of the person.
        discord_accountusername (str):      The Discord account username of the person.
        discord_accountdisplayname (str):   The Discord account display name of the person.
        discord_profiledisplayname (str):   The Discord profile display name of the person.
        comment (str):                      An optional comment about the person or entry.
        click_counter (str):                The click counter for the person.
        recording_mode_enum (str):          The recording mode enum.
        database_action_enum (str):         The database action enum.
        must_ditch_originating_item (bool): Indicates if the originating record must be ditched.
        is_still_to_be_backed_up (bool):    Indicates if the record is still to be backed up.
        is_still_to_be_pushed (bool):       Indicates if the record is still to be pushed.
        touched_by (str):                   The user who touched the record.
        when_touched (float):               The timestamp when the record was touched.
        when_pushed (float):                The timestamp when the record was pushed.
        originating_item_guid (str):        The originating item GUID.

    Properties:
        timestamp (float):                  The timestamp assigned upon instantiation.
        guid (str):                         A unique identifier for this instantiated object.

    Methods:
        __hash__:                           Override to make the object hashable.
        __eq__:                             Override to make the object comparable.
        __str__:                            Override to make a pretty string of the item.
        create:                             Creates a new instance of the PersonItem class.
        to_dataTransferObject:              Creates a DataTransferObject from an Item.
        from_dataTransferObject:            Creates an Item from a DataTransferObject.
        get_both_guids:                     Returns a concatenation of the originating_item_guid and the guid.
    """

    zsun_id: str = Field(default="")
    zsun_firstname: str = Field(default="")
    zsun_lastname: str = Field(default="")
    zwift_id: int = Field(default=0)
    zwift_firstname: str = Field(default="")
    zwift_lastname: str = Field(default="")
    discord_accountusername: str = Field(default="")
    discord_accountdisplayname: str = Field(default="")
    discord_profiledisplayname: str = Field(default="")
    comment: str = Field(default="")
    click_counter: str = Field(default="")
    recording_mode_enum: str = Field(default="")
    database_action_enum: str = Field(default="")
    database_action_enum: str = Field(default="")
    must_ditch_originating_item: bool = Field(default=False)
    is_still_to_be_backed_up: bool = Field(default=True)
    is_still_to_be_pushed: bool = Field(default=False)
    touched_by: str = Field(default="")
    when_touched: float = Field(default=0)
    when_pushed: float = Field(default=0)
    originating_item_guid: str = Field(default="")
    _timestamp: float = PrivateAttr(
        default_factory=lambda: datetime.now(timezone.utc).timestamp()
    )
    _guid: str = PrivateAttr(default_factory=lambda: str(uuid.uuid4()))

    @property
    def timestamp(self) -> float:
        return self._timestamp

    @property
    def guid(self) -> str:
        return self._guid

    def __hash__(self):
        return hash(
            (
                self.zsun_id,
                self.zsun_firstname,
                self.zsun_lastname,
                self.zwift_id,
                self.zwift_firstname,
                self.zwift_lastname,
                self.discord_accountusername,
                self.discord_accountdisplayname,
                self.discord_profiledisplayname,
                self.comment,
                self.click_counter,
                self.recording_mode_enum,
                self.database_action_enum,
                self.must_ditch_originating_item,
                self.is_still_to_be_backed_up,
                self.is_still_to_be_pushed,
                self.touched_by,
                self.when_touched,
                self.when_pushed,
                self.originating_item_guid,
                self._timestamp,
                self._guid,
            )
        )  # hash based on all attributes, including private attributes.

    def __eq__(self, other: object) -> bool:
        if isinstance(other, PersonItem):
            return (
                self.zsun_id == other.zsun_id
                and self.zsun_firstname == other.zsun_firstname
                and self.zsun_lastname == other.zsun_lastname
                and self.zwift_id == other.zwift_id
                and self.zwift_firstname == other.zwift_firstname
                and self.zwift_lastname == other.zwift_lastname
                and self.discord_accountusername == other.discord_accountusername
                and self.discord_accountdisplayname == other.discord_accountdisplayname
                and self.discord_profiledisplayname == other.discord_profiledisplayname
                and self.comment == other.comment
                and self.click_counter == other.click_counter
                and self.recording_mode_enum == other.recording_mode_enum
                and self.database_action_enum == other.database_action_enum
                and self.must_ditch_originating_item
                == other.must_ditch_originating_item
                and self.is_still_to_be_backed_up == other.is_still_to_be_backed_up
                and self.is_still_to_be_pushed == other.is_still_to_be_pushed
                and self.touched_by == other.touched_by
                and self.when_touched == other.when_touched
                and self.when_pushed == other.when_pushed
                and self.originating_item_guid == other.originating_item_guid
                and self._timestamp == other._timestamp
                and self._guid == other._guid
            )
        return False

    def __str__(self):
        data = self.model_dump()
        data["timestamp"] = self.timestamp
        data["guid"] = self.guid
        return json.dumps(data, indent=4)

    def get_both_guids(self) -> str:
        """
        Returns a string containing both the originating_guid and the guid.
        Returns:
            str: A string containing both the originating_guid and the guid.
        """
        return f"{self.originating_item_guid}{self._guid}"

    @staticmethod
    def create(
        zwift_id: int,
        discord_accountusername: str,
        recording_mode_enum: str,
        touched_by: str,
    ) -> "PersonItem":
        """
        Creates a new instance of the PersonItem class with the provided parameters.
        Sets when_touched to UTC now. Sets the timestamp to UTC now and initializes the GUID.

        Args:
            zwift_id (int): The Zwift ID of the member.
            discord_accountusername (str): The Discord account username of the member.
            recording_mode_enum (str): The recording mode enum.
            touched_by (str): The user who touched the record.

        Returns:
            PersonItem: A new instance of the PersonItem class.
        """
        now_utc = datetime.now(timezone.utc).timestamp()
        new_guid = str(uuid.uuid4())

        answer = PersonItem(
            zwift_id=zwift_id,
            discord_accountusername=discord_accountusername,
            recording_mode_enum=recording_mode_enum,
            touched_by=touched_by,
        )
        answer.when_touched = now_utc
        answer._timestamp = now_utc
        answer._guid = new_guid
        return answer

    @staticmethod
    def to_dataTransferObject(item: "PersonItem") -> PersonDataTransferObject:
        """
        Converts a PersonItem instance to a PersonDataTransferObject instance.
        Args:
            item (PersonItem): The PersonItem instance to convert to a PersonDataTransferObject instance.
        Returns:
            PersonDataTransferObject: A new instance of the PersonDataTransferObject class.
        """
        answer = PersonDataTransferObject(
            zsun_id=item.zsun_id,
            zsun_firstname=item.zsun_firstname,
            zsun_lastname=item.zsun_lastname,
            zwift_id=item.zwift_id,
            zwift_firstname=item.zwift_firstname,
            zwift_lastname=item.zwift_lastname,
            discord_accountusername=item.discord_accountusername,
            discord_accountdisplayname=item.discord_accountdisplayname,
            discord_profiledisplayname=item.discord_profiledisplayname,
            comment=item.comment,
            click_counter=item.click_counter,
            recording_mode_enum=item.recording_mode_enum,
            database_action_enum=item.database_action_enum,
            must_ditch_originating_item=item.must_ditch_originating_item,
            is_still_to_be_backed_up=item.is_still_to_be_backed_up,
            is_still_to_be_pushed=item.is_still_to_be_pushed,
            touched_by=item.touched_by,
            when_touched=item.when_touched,
            when_pushed=item.when_pushed,
            originating_item_guid=item.originating_item_guid,
            timestamp=item.timestamp,
            guid=item.guid,
        )
        return answer

    @staticmethod
    def from_dataTransferObject(dto: PersonDataTransferObject) -> "PersonItem":
        """
        Creates a PersonItem instance from a PersonDataTransferObject instance.

        This method captures the privately set attributes from the DataTransferObject and restores them
        to the new PersonItem instance. The private attributes include timestamp and guid.

        Args:
            dto (PersonDataTransferObject): The PersonDataTransferObject instance to create the PersonItem instance from.
        Returns:
            PersonItem: A new instance of the PersonItem class.
        """

        # capture the privately set attributes
        captured_timestamp = dto.timestamp
        captured_guid = dto.guid

        answer = PersonItem(
            zsun_id=dto.zsun_id,
            zsun_firstname=dto.zsun_firstname,
            zsun_lastname=dto.zsun_lastname,
            zwift_id=dto.zwift_id,
            zwift_firstname=dto.zwift_firstname,
            zwift_lastname=dto.zwift_lastname,
            discord_accountusername=dto.discord_accountusername,
            discord_accountdisplayname=dto.discord_accountdisplayname,
            discord_profiledisplayname=dto.discord_profiledisplayname,
            comment=dto.comment,
            click_counter=dto.click_counter,
            recording_mode_enum=dto.recording_mode_enum,
            database_action_enum=dto.database_action_enum,
            must_ditch_originating_item=dto.must_ditch_originating_item,
            is_still_to_be_backed_up=dto.is_still_to_be_backed_up,
            is_still_to_be_pushed=dto.is_still_to_be_pushed,
            touched_by=dto.touched_by,
            when_touched=dto.when_touched,
            when_pushed=dto.when_pushed,
            originating_item_guid=dto.originating_item_guid,
        )

        # restore the backing stores of the privately-set attributes
        answer._timestamp = captured_timestamp
        answer._guid = captured_guid

        return answer

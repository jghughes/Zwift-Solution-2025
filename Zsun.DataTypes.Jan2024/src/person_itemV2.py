"""
This module defines the PersonItem class, which represents an item associated with a person.
"""
# Standard library imports
import datetime
from datetime import datetime, timezone
import json
import uuid

# Local application imports
from pydantic import BaseModel, Field
from person_dto import PersonDto
from hub_item_base import HubItemBase



class PersonItem(HubItemBase):
    """
    An object representing a club member's particulars.

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

    def get_both_guids(self) -> str:
        """
        A string concatenation ofboth the originating_guid and the guid.
        """
        return f"{self.originating_item_guid}{self.guid}"

    @staticmethod
    def create(
        zwift_id: int,
        discord_accountusername: str,
        recording_mode_enum: str,
        touched_by: str,
    ) -> "PersonItem":
        """
        Creates a new instance of the PersonItem class with the provided parameters.
        Sets the timestamp and when touched to UTC now in seconds and initializes the GUID.

        Args:
            zwift_id (int): The Zwift ID of the member.
            discord_accountusername (str): The Discord account username of the member.
            recording_mode_enum (str): The recording mode enum.
            touched_by (str): The user who touched the record.

        Returns:
            PersonItem: A new instance of the PersonItem class.
        """
        answer = PersonItem(zwift_id=zwift_id,discord_accountusername=discord_accountusername, recording_mode_enum=recording_mode_enum, touched_by=touched_by)

        # answer.zwift_id=zwift_id
        # answer.discord_accountusername=discord_accountusername
        # answer.recording_mode_enum=recording_mode_enum
        # answer.touched_by=touched_by

        answer.when_touched_binary_format = int(datetime.now(timezone.utc).timestamp())
        answer.timestamp_binary_format = int(datetime.now(timezone.utc).timestamp())
        answer.guid = str(uuid.uuid4())

        return answer

    @staticmethod
    def to_dataTransferObject(item: "PersonItem") -> PersonDto:
        """
        Converts a PersonItem instance to a PersonDto instance.
        Args:
            item (PersonItem): The PersonItem instance to convert to a PersonDto instance.
        Returns:
            PersonDto: A new instance of the PersonDto class.
        """
        answer = PersonDto(
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
            when_touched=item.when,
            when_pushed=item.when_pushed,
            originating_item_guid=item.originating_item_guid,
            timestamp=item.timestamp,
            guid=item.guid,
        )
        return answer

    @staticmethod
    def from_dataTransferObject(dto: PersonDto) -> "PersonItem":
        """
        Creates a PersonItem instance from a PersonDto instance.

        This method captures the privately set attributes from the DataTransferObject and restores them
        to the new PersonItem instance. The private attributes include timestamp and guid.

        Args:
            dto (PersonDto): The PersonDto instance to create the PersonItem instance from.
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

# simple example usage of the PersonItem class

if __name__ == "__main__":
    # Create a new PersonItem instance using the create method
    person_item = PersonItem.create(
        zwift_id=12345,
        discord_accountusername="john_doe",
        recording_mode_enum="ACTIVE",
        touched_by="admin"
    )

    # Print the PersonItem instance
    print("PersonItem instance:")
    print(person_item)

    # Convert the PersonItem instance to a PersonDto instance
    person_dto = PersonItem.to_dataTransferObject(person_item)
    print("\nConverted to PersonDto:")
    print(person_dto)

    # Convert the PersonDto instance back to a PersonItem instance
    new_person_item = PersonItem.from_dataTransferObject(person_dto)
    print("\nConverted back to PersonItem:")
    print(new_person_item)

    # Check if the original and new PersonItem instances are equal
    print("\nAre the original and new PersonItem instances equal?")
    print(person_item == new_person_item)




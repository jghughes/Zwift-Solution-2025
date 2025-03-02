"""
This module defines the PersonItem class, which represents an item associated with a person.
"""
# Standard library imports
import datetime
from datetime import datetime, timezone
from typing import Any
import uuid
from dataclasses import dataclass
import logging

# Local application imports
from person_dto import PersonDataTransferObject
from hub_item_base import HubItemBase

# Helper function to write a pretty error message
def pretty_error_message(ex: Exception) -> str:
    """
    The function attempts to unpack the args attribute of the exception ex
    into code and message. If the unpacking fails (e.g., if args does not
    contain two elements), it falls back to setting code to 0 and message
    to the first and only element of args.

    If an exception ex has args like (404, "Not Found"), the function
    will return "Not Found ErrorCode=404". If an exception ex has args
    like ("An error occurred",), the function will return "An error occurred".
    """
    try:
        (code, message) = ex.args
    except:
        code = 0
        message = ex.args[0]
    if code == 0:
        return f"{str(message)}"
    return f"{str(message)} ErrorCode={str(code)}"

def assign_if_not_none(target: Any, source: Any, attribute: Any):
    try:
        if hasattr(source, attribute):
            value = getattr(source, attribute)
            if value is not None:
                setattr(target, attribute, value)
    except Exception as e:
        logging.error(f"Error assigning attribute '{attribute}': {pretty_error_message(e)}")

@dataclass
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

    zsun_id: str = ""
    zsun_firstname: str = ""
    zsun_lastname: str = ""
    zwift_id: int = 0
    zwift_firstname: str = ""
    zwift_lastname: str = ""
    discord_accountusername: str = ""
    discord_accountdisplayname: str = ""
    discord_profiledisplayname: str = ""

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

        answer = PersonItem(
            zwift_id=zwift_id,
            discord_accountusername=discord_accountusername,
            recording_mode_enum=recording_mode_enum,
            touched_by=touched_by,
            when_touched_binary_format=int(datetime.now(timezone.utc).timestamp()),
            timestamp_binary_format=int(datetime.now(timezone.utc).timestamp()),
            guid=str(uuid.uuid4())
        )

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

        answer = PersonDataTransferObject()

        for attribute in item.__dict__:
            assign_if_not_none(answer, item, attribute)

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

        answer = PersonItem()

        for attribute in dto.__dict__:
            assign_if_not_none(answer, dto, attribute)

        return answer

# simple example usage of the PersonItem class

def main():
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

    # Convert the PersonItem instance to a PersonDataTransferObject instance
    person_dto = PersonItem.to_dataTransferObject(person_item)
    print("\nConverted to PersonDataTransferObject:")
    print(person_dto)

    # Convert the PersonDataTransferObject instance back to a PersonItem instance
    new_person_item = PersonItem.from_dataTransferObject(person_dto)
    print("\nConverted back to PersonItem:")
    print(new_person_item)

    # Check if all the attributes of the pair of original and new PersonItem instances are equal
    # The __eq__ method of a dataclass ensures that the instances are equal if all their attributes are equal
    print("\nAre all the attributes of the the original and roundtripped PersonItem instances equal?")
    isequal : bool = person_item == new_person_item
    print(isequal)

if __name__ == "__main__":
    main()




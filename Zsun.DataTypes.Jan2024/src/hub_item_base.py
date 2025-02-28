"""
This module contains the HubItemBase class and provides example usage.
The HubItemBase class is designed as a base class for database entity
objects. Entity objects should derive from this class. The class is
decorated as a dataclass for basic serialisation/roundtripping to and
from local system storage. Derived classes will inherit this basic
functionality.
"""
# Standard library imports
from dataclasses import dataclass
import json


@dataclass
class HubItemBase:
    """
    A class representing an item with various attributes.

    Note: in Python, timestamps are in seconds since epoch.
    This is not the case in all languages. Be aware of this when
    interfacing with other systems.

    Attributes:
    -----------
    click_counter              : int  The counter of entries during a work session.
    recording_mode_enum        : str  The recording mode of the item.
    database_action_enum       : str  The database action associated with the item.
    must_ditch_originating_item: bool Indicates if the originating item must be ditched.
    is_still_to_be_backed_up   : bool Indicates if the item is still to be backed up.
    is_still_to_be_pushed      : bool Indicates if the item is still to be pushed.
    touched_by                 : str  The user who touched the item.
    timestamp_binary_format    : int  The timestamp when created.
    when_touched_binary_format : int  The timestamp when edited.
    when_pushed_binary_format  : int  The timestamp when pushed to the database.
    originating_item_guid      : str  The GUID of the originating item.
    guid                       : str  The GUID of the item.
    comment                    : str  A comment associated with the item.
    
    """

    click_counter: int = 0
    recording_mode_enum: str = ""
    database_action_enum: str = ""
    must_ditch_originating_item: bool = False
    is_still_to_be_backed_up: bool = True
    is_still_to_be_pushed: bool = True
    touched_by: str = ""
    timestamp_binary_format: int = 0
    when_touched_binary_format: int = 0
    when_pushed_binary_format: int = 0
    originating_item_guid: str = ""
    guid: str = ""
    comment: str = ""

    def get_both_guids(self) -> str:
        """
        Returns a concatenation of the originating item GUID and the item GUID.
        """
        return f"{self.originating_item_guid}{self.guid}"



# Example usage of HubItemBase class

def main():
    # Create test instances of HubItemBase
    item1 = HubItemBase(
        click_counter=5,
        recording_mode_enum="mode1",
        database_action_enum="action1",
        must_ditch_originating_item=True,
        is_still_to_be_backed_up=False,
        is_still_to_be_pushed=True,
        touched_by="user1",
        timestamp_binary_format=1627849923,
        when_touched_binary_format=1627849923,
        when_pushed_binary_format=1627849923,
        originating_item_guid="orig_guid1",
        guid="guid1",
        comment="This is a comment"
    )

    item2 = HubItemBase(
        click_counter=3,
        recording_mode_enum="mode2",
        database_action_enum="action2",
        must_ditch_originating_item=False,
        is_still_to_be_backed_up=True,
        is_still_to_be_pushed=False,
        touched_by="user2",
        timestamp_binary_format=1627849933,
        when_touched_binary_format=1627849933,
        when_pushed_binary_format=1627849933,
        originating_item_guid="orig_guid2",
        guid="guid2",
        comment="Another comment"
    )

    item3 = HubItemBase(
        click_counter=7,
        recording_mode_enum="mode3",
        database_action_enum="action3",
        must_ditch_originating_item=False,
        is_still_to_be_backed_up=True,
        is_still_to_be_pushed=True,
        touched_by="user3",
        timestamp_binary_format=1627849943,
        when_touched_binary_format=1627849943,
        when_pushed_binary_format=1627849943,
        originating_item_guid="orig_guid3",
        guid="guid3",
        comment="Yet another comment"
    )

    items = [item1, item2, item3]

    # Serialize item1 to JSON
    json_data = json.dumps(item1.__dict__, indent=4)
    print(f"Item1 serialized to pretty printed JSON:\n\t{json_data}\n")

    # Deserialize back from JSON
    deserialized_item = json.loads(json_data)
    print(f"\nItem1 de-serialized back from JSON to HubItemBase object:\n\n\t{deserialized_item}\n")

    # Get both GUIDs for item1
    both_guids = item1.get_both_guids()
    print(f"\nItem1 instance - both GUIDs:\n\n\t{both_guids}\n")

    # Get both GUIDs for item1
    both_guids = item2.get_both_guids()
    print(f"\nItem2 instance - both GUIDs:\n\n\t{both_guids}\n")


if __name__ == "__main__":
    main()

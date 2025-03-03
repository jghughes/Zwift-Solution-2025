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
from typing import Optional, Tuple


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
    recording_mode_enum: str | None = ""
    database_action_enum: str | None = ""
    must_ditch_originating_item: bool = False
    is_still_to_be_backed_up: bool = True
    is_still_to_be_pushed: bool  = True
    touched_by: str | None = ""
    timestamp_binary_format: int = 0
    when_touched_binary_format: int = 0
    when_pushed_binary_format: int = 0
    originating_item_guid: str = ""
    guid: str = ""
    comment: str | None = ""

    def get_both_guids(self) -> str:
        """
        Returns a concatenation of the originating item GUID and the item GUID.
        """
        return f"{self.originating_item_guid}{self.guid}"

    @staticmethod
    def is_valid_item(item: Optional['HubItemBase']) ->  Tuple[bool, str]:
        """
        Determines if the item is a minimally valid candidate for addition 
        to a repository keyed on the concatentaion of both GUIDs. 

        Null items and unpopulated "new" items are deemed invalid as are items 
        where one or both GUIDS are empty. No validity check is done on the format 
        or content of the GUID variables.

        Args:
            item (T): The item to check.

        Returns:
            bool: True if the item is valid, otherwise False with an explanatory message.
        """
        # Null checks
        if item is None:
            return False, "Item is null. Data error"

        if not item.guid.strip():
            return False, "Item Guid property not specified. Data error"

        if not item.originating_item_guid.strip():
            return False, "Item OriginatingItemGuid property not specified. Data error"

        if not item.get_both_guids().strip():
            return False, "Item BothGuids property not specified. Data error"

        if item == type(item)():
            return False, "Item is blank." # Policy is to ignore attempted additions of "blank" i.e. unpopulated "new" items

        return True, "Item is valid"



def main():
    import json
    import sys

    # Check the paths for the module     
    print("sys.path (in alphabetical order):-")
    for path in sorted(sys.path):
        print(f" - {path}")
    print("\nExplanation:\n\tThe above paths are where Python will look to find modules and imports\n\treferenced in this file. If imports fail to resolve, it is because of\n\tincorrect paths. In a Visual Studio 2022 project, right-click\n\tthe 'Search Paths' node to add a path.")


    # Create test instances of HubItemBase
    item1 = HubItemBase(
        originating_item_guid="orig_guid1",
        guid="guid1",
        comment="This is a comment"
    )

    item2 = HubItemBase(
        originating_item_guid="orig_guid2",
        guid="guid2",
        comment="Another comment"
    )

    # Serialize item1 to JSON
    json_data = json.dumps(item1.__dict__, indent=4)
    print(f"Item1 serialized to pretty printed JSON:\n\t{json_data}\n")

    # Deserialize back from JSON
    deserialized_item = json.loads(json_data)
    print(f"\nItem1 de-serialized back from JSON to HubItemBase object:\n\n\t{deserialized_item}\n")

    # Get both GUIDs for item1
    both_guids = item1.get_both_guids()
    print(f"\nItem1 instance - both GUIDs:\n\n\t{both_guids}\n")

    # Get both GUIDs for item2
    both_guids = item2.get_both_guids()
    print(f"\nItem2 instance - both GUIDs:\n\n\t{both_guids}\n")

if __name__ == "__main__":
    main()

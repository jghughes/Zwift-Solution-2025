"""
This module defines the HubItemBase class and provides example usage.
The HubItemBase class represents an item with various attributes and includes
methods for grouping items by specific attributes.
"""
# Standard library imports
from dataclasses import dataclass
import json
from typing import List

# Local application imports
# from pydantic import BaseModel, Field
from jgh_listdictionary import JghListDictionary

@dataclass
class HubItemBase:
    """
    A class representing an item with various attributes.

    Attributes:
    -----------
    click_counter : int
        The number of clicks associated with the item.
    bib : str
        The bib number of the item.
    rfid : str
        The RFID of the item.
    recording_mode_enum : str
        The recording mode of the item.
    database_action_enum : str
        The database action associated with the item.
    must_ditch_originating_item : bool
        Indicates if the originating item must be ditched.
    is_still_to_be_backed_up : bool
        Indicates if the item is still to be backed up.
    is_still_to_be_pushed : bool
        Indicates if the item is still to be pushed.
    touched_by : str
        The user who touched the item.
    timestamp_binary_format : int
        The timestamp in binary format (int seconds in Python).
    when_touched_binary_format : int
        The time when the item was touched in binary format (int seconds in Python).
    when_pushed_binary_format : int
        The time when the item was pushed in binary format (int seconds in Python).
    originating_item_guid : str
        The GUID of the originating item.
    guid : str
        The GUID of the item.
    comment : str
        A comment associated with the item.
    id : int
        The ID of the item.
    enum_string : str
        An enum string associated with the item.
    label : str
        A label associated with the item.
    """

    click_counter: int = 0
    bib: str = ""
    rfid: str = ""
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
    id: int = 0
    enum_string: str = ""
    label: str = ""

    def get_both_guids(self) -> str:
        """
        Returns a concatenation of the originating item GUID and the item GUID.
        """
        return f"{self.originating_item_guid}{self.guid}"

    @staticmethod
    def to_list_dictionary_grouped_by_bib(
        list_hub_items: List["HubItemBase"],
    ) -> JghListDictionary[str, "HubItemBase"]:
        """
        Groups a list of HubItemBase instances by their bib attribute.

        Parameters:
        -----------
        list_hub_items : List[HubItemBase]
            The list of HubItemBase instances to group.

        Returns:
        --------
        JghListDictionary[str, HubItemBase]
            A dictionary-like object grouping the items by their bib attribute.
        """
        answer: JghListDictionary[str, HubItemBase] = JghListDictionary[
            str, HubItemBase
        ]()

        sorted_items = sorted(
            (item for item in list_hub_items if item and item.bib),
            key=lambda x: (x.bib, -x.when_touched_binary_format),
        )

        for item in sorted_items:
            answer.append_value_to_key(item.bib, item)

        return answer

    @staticmethod
    def to_list_dictionary_grouped_by_originating_item_guid(
        list_hub_items: List["HubItemBase"],
    ) -> JghListDictionary[str, "HubItemBase"]:
        """
        Groups a list of HubItemBase instances by their originating_item_guid attribute.

        Parameters:
        -----------
        list_hub_items : List[HubItemBase]
            The list of HubItemBase instances to group.

        Returns:
        --------
        JghListDictionary[str, HubItemBase]
            A dictionary-like object grouping the items by their originating_item_guid attribute.
        """
        answer: JghListDictionary[str, HubItemBase] = JghListDictionary[
            str, HubItemBase
        ]()

        sorted_items = sorted(
            (
                item
                for item in list_hub_items
                if item and item.originating_item_guid.strip()
            ),
            key=lambda x: -x.when_touched_binary_format,
        )

        for item in sorted_items:
            answer.append_value_to_key(item.originating_item_guid, item)

        return answer


# Example usage of HubItemBase class

if __name__ == "__main__":
    # Create instances of HubItemBase
# Create an instance of HubItemBase with an empty constructor
    item1 = HubItemBase()
    item1.click_counter = 5
    item1.bib = "12345"
    item1.rfid = "rfid123"
    item1.recording_mode_enum = "mode1"
    item1.database_action_enum = "action1"
    item1.must_ditch_originating_item = True
    item1.is_still_to_be_backed_up = False
    item1.is_still_to_be_pushed = True
    item1.touched_by = "user1"
    item1.timestamp_binary_format = 1627849923
    item1.when_touched_binary_format = 1627849923
    item1.when_pushed_binary_format = 1627849923
    item1.originating_item_guid = "orig_guid1"
    item1.guid = "guid1"
    item1.comment = "This is a comment"
    item1.id = 1
    item1.enum_string = "enum1"
    item1.label = "label1"

    item2 = HubItemBase()
    item2.click_counter = 3
    item2.bib = "67890"
    item2.rfid = "rfid456"
    item2.recording_mode_enum = "mode2"
    item2.database_action_enum = "action2"
    item2.must_ditch_originating_item = False
    item2.is_still_to_be_backed_up = True
    item2.is_still_to_be_pushed = False
    item2.touched_by = "user2"
    item2.timestamp_binary_format = 1627849933
    item2.when_touched_binary_format = 1627849933
    item2.when_pushed_binary_format = 1627849933
    item2.originating_item_guid = "orig_guid2"
    item2.guid = "guid2"
    item2.comment = "Another comment"
    item2.id = 2
    item2.enum_string = "enum2"
    item2.label = "label2" 

    item3 = HubItemBase()
    item3.click_counter = 7
    item3.bib = "12345"
    item3.rfid = "rfid789"
    item3.recording_mode_enum = "mode3"
    item3.database_action_enum = "action3"
    item3.must_ditch_originating_item = False
    item3.is_still_to_be_backed_up = True
    item3.is_still_to_be_pushed = True
    item3.touched_by = "user3"
    item3.timestamp_binary_format = 1627849943
    item3.when_touched_binary_format = 1627849943
    item3.when_pushed_binary_format = 1627849943
    item3.originating_item_guid = "orig_guid3"
    item3.guid = "guid3"
    item3.comment = "Yet another comment"
    item3.id = 3
    item3.enum_string = "enum3"
    item3.label = "label3"

    items = [item1, item2, item3]

    # Serialize item1 to JSON
    json_data = json.dumps(item1.__dict__)
    print("Serialized item1 to JSON:\n\t", json_data)

    # Deserialize back from JSON
    deserialized_item = json.loads(json_data)
    print("\nDeserialized item1 back from JSON:\n\t", deserialized_item)

    # Group items by bib
    grouped_by_bib = HubItemBase.to_list_dictionary_grouped_by_bib(items)
    print("\nGrouped by BIB: '12345'")
    count = 0
    for hubitem in grouped_by_bib.get_values_belonging_to_key("12345"):
        count += 1
        print(f"\nHubItem {count}:\n\t{hubitem}")

    # Group items by originating_item_guid
    grouped_by_originating_item_guid = (
        HubItemBase.to_list_dictionary_grouped_by_originating_item_guid(items)
    )
    print("\nGrouped by Originating Item GUID: 'orig_guid3'")
    count = 0
    for hubitem in grouped_by_originating_item_guid.get_values_belonging_to_key(
        "orig_guid3"
    ):
        count += 1
        print(f"\nHubItem {count}:\n\t{hubitem}")

    # Get both GUIDs for item1
    both_guids = item1.get_both_guids()
    print(f"\nBoth GUIDs for item1:\n\t{both_guids}\n")

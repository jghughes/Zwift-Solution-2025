"""
This module defines the HubItemBase class and provides example usage.
The HubItemBase class represents an item with various attributes and includes
methods for grouping items by specific attributes.
"""
# Standard library imports
import json
from typing import List

# Local application imports
from pydantic import BaseModel, Field
from jgh_listdictionary import JghListDictionary


class HubItemBase(BaseModel):
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

    click_counter: int = Field(0)
    bib: str = Field("")
    rfid: str = Field("")
    recording_mode_enum: str = Field("")
    database_action_enum: str = Field("")
    must_ditch_originating_item: bool = Field(False)
    is_still_to_be_backed_up: bool = Field(True)
    is_still_to_be_pushed: bool = Field(True)
    touched_by: str = Field("")
    timestamp_binary_format: int = Field(0)
    when_touched_binary_format: int = Field(0)
    when_pushed_binary_format: int = Field(0)
    originating_item_guid: str = Field("")
    guid: str = Field("")
    comment: str = Field("")
    id: int = Field(0)
    enum_string: str = Field("")
    label: str = Field("")

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
    item1 = HubItemBase(
        click_counter=5,
        bib="12345",
        rfid="rfid123",
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
        comment="This is a comment",
        id=1,
        enum_string="enum1",
        label="label1",
    )

    item2 = HubItemBase(
        click_counter=3,
        bib="67890",
        rfid="rfid456",
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
        comment="Another comment",
        id=2,
        enum_string="enum2",
        label="label2",
    )

    item3 = HubItemBase(
        click_counter=7,
        bib="12345",
        rfid="rfid789",
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
        comment="Yet another comment",
        id=3,
        enum_string="enum3",
        label="label3",
    )

    # List of HubItemBase instances
    items = [item1, item2, item3]

    # Serialize item1 to JSON
    validDict = item1.model_dump()
    json_data = json.dumps(validDict)
    print("Serialized item1 to JSON:\n\t", json_data)

    # Deserialize back from JSON
    deserialized_item = HubItemBase.model_validate_json(json_data)
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

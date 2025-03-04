from jgh_listdictionary import JghListDictionary
from typing import TypeVar
from hub_item_base import HubItemBase
from jgh_logging import JghLogger


T = TypeVar('T', bound=HubItemBase)
def group_by_originating_guid(list_of_hubitembases: list[T]) -> JghListDictionary[str, T]:
    """
    Groups a list of HubItemBase instances (or its subclasses) by their originating_item_guid attribute.

    Parameters:
    -----------
    list_of_hubitembases : list[T]
        The list of HubItemBase instances (or its subclasses) to group.

    Returns:
    --------
    JghListDictionary[str, T]
        A dictionary-like object grouping the list_of_hubitems by their originating_item_guid attribute.
    """
    answer: JghListDictionary[str, T] = JghListDictionary[str, T]()

    sorted_list_of_hubitems = sorted(
        (
            item
            for item in list_of_hubitembases
            if item and item.originating_item_guid.strip()
        ),
        key=lambda x: -x.when_touched_binary_format,
    )

    for item in sorted_list_of_hubitems:
        answer.append_value_to_key(item.originating_item_guid, item)

    return answer

def main():
    # Create illustrative instances of HubItemBase
    item1 = HubItemBase(
        originating_item_guid="orig_guid1",
        guid="guid1",
        comment="Hello this is Tom",
    )

    item2 = HubItemBase(
        originating_item_guid="orig_guid2",
        guid="guid2",
        comment="Hello this is Dick",
    )

    item3 = HubItemBase(
        originating_item_guid="orig_guid3",
        guid="guid3",
        comment="Hello this is Harry",
    )

    item4 = HubItemBase(
        originating_item_guid="orig_guid3",
        guid="guid4",
        comment="Hello this is Sally",
)

    list_of_hubitems = [item1, item2, item3, item4]

    # Group list_of_hubitems by originating_item_guid
    my_listdict = group_by_originating_guid(list_of_hubitems)
    origGuid="orig_guid3"
    print(f"\nGrouped by Originating GUID={origGuid}")

    count = 0
    for hubitem in my_listdict.get_values(origGuid):
        count += 1
        print(f"\nHubItem {count}:\n\tOriginating GUID={hubitem.originating_item_guid}\tComment={hubitem.comment}")

        # Example usage of HubItemBase class

if __name__ == "__main__":
    main()



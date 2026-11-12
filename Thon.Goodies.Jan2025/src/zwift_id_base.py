from dataclasses import dataclass
from typing import Protocol
from collections.abc import Mapping

class HasZwiftID(Protocol):
    zwift_id: str

@dataclass(eq=True)
class ZwiftIdBase(HasZwiftID):
    zwift_id: str = ""

@dataclass(eq=True, frozen=True)
class FrozenZwiftIdBase(HasZwiftID):
    zwift_id: str = ""

def lookup_Items_by_ZwiftID[T : HasZwiftID](
    list_of_zwiftID: list[str],
    mapping_of_ZwiftIdBaseItem: Mapping[str, T],
    item_type: type[T]
) -> list[T]:
    """
    Returns a list of items of concrete type T (subclass of ZwiftIdBase) whose zwift_id is in list_of_zwiftID.
    Skips missing IDs and logs duplicates.
    """
    items: list[T] = []
    for zwift_id in list_of_zwiftID:
        if zwift_id in mapping_of_ZwiftIdBaseItem:
            item = mapping_of_ZwiftIdBaseItem[zwift_id]
            if isinstance(item, item_type):
                items.append(item)
            else:
                print(f"zwift_id '{zwift_id}' found, but item is not of type {item_type.__name__}. Skipping.")
        else:
            print(f"zwift_id '{zwift_id}' not found in mapping_of_ZwiftIdBaseItem. Skipping.")
    return items
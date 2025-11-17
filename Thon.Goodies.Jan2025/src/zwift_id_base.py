from dataclasses import dataclass
from typing import Protocol, TypeVar, List, Mapping, Type

class HasZwiftID(Protocol):
    zwift_id: str

@dataclass(eq=True)
class ZwiftIdBase(HasZwiftID):
    zwift_id: str = ""

@dataclass(eq=True, frozen=True)
class FrozenZwiftIdBase(HasZwiftID):
    zwift_id: str = ""

T = TypeVar("T", bound=HasZwiftID)
def lookup_Items_by_ZwiftID(
    list_of_zwiftID: List[str],
    mapping_of_ZwiftIdBaseItem: Mapping[str, T],
    item_type: Type[T]
) -> List[T]:
    """
    Returns a list of items of concrete type T (subclass of ZwiftIdBase) whose zwift_id is in list_of_zwiftID.
    Skips missing IDs and logs duplicates.
    """
    seen: set[str] = set()
    list_of_unique_zwiftID: List[str] = []
    duplicates: set[str] = set()
    for zwift_id in list_of_zwiftID:
        if zwift_id in seen:
            duplicates.add(zwift_id)
        else:
            seen.add(zwift_id)
            list_of_unique_zwiftID.append(zwift_id)
    if duplicates:
        print(f"Duplicate zwift_id detected and removed in input list: {sorted(duplicates)}")

    items: List[T] = []
    for zwift_id in list_of_unique_zwiftID:
        if zwift_id in mapping_of_ZwiftIdBaseItem:
            item = mapping_of_ZwiftIdBaseItem[zwift_id]
            if isinstance(item, item_type):
                items.append(item)
            else:
                print(f"zwift_id '{zwift_id}' found, but item is not of type {item_type.__name__}. Skipping.")
        else:
            print(f"zwift_id '{zwift_id}' not found in mapping_of_ZwiftIdBaseItem. Skipping.")
    return items
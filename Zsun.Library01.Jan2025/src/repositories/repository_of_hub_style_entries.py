from typing import List, Dict, TypeVar, Generic, Tuple, Optional, Iterable

T = TypeVar('T', bound='IHubItem')

class RepositoryOfHubStyleEntries(Generic[T]):
    """
    RepositoryOfHubStyleEntries is a generic class that manages a collection of hub-style entries.
    """

    def __init__(self):
        self._sequence_is_out_of_date: bool = False
        self._dictionary_of_most_recent_item_per_originating_item_guid_is_out_of_date: bool = False
        self._nasty_little_mirror: List[T] = []
        self._everything_ordered_by_descending_timestamp: List[T] = []
        self._dictionary_of_everything_keyed_by_both_guids: Dict[str, T] = {}
        self._dictionary_of_most_recent_item_keyed_by_originating_item_guid: Dict[str, T] = {}
        self.desired_height_of_short_list: int = 10  # Arbitrary default

    @property
    def sequence_is_pristine(self) -> bool:
        return not self._sequence_is_out_of_date

    @property
    def count(self) -> int:
        return len(self._dictionary_of_everything_keyed_by_both_guids)

    # methods to add/change/delete data

    def try_add_no_duplicate(self, item: T) -> Tuple[bool, str]:
        """
        Tries to add an item without duplicates.

        Args:
            item (T): The item to add.

        Returns:
            Tuple[bool, str]: A tuple containing a boolean indicating success and an error message if any.
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

        if item == T():
            return False, "Item is blank."

        # Fast insertion
        self._dictionary_of_everything_keyed_by_both_guids[item.get_both_guids()] = item  # Overwrite

        self._sequence_is_out_of_date = True
        self._dictionary_of_most_recent_item_per_originating_item_guid_is_out_of_date = True

        self.add_or_overwrite_to_dirty_little_baby_mirror(item)

        return True, ""

    def try_add_range_no_duplicates(self, items: List[T]) -> Tuple[bool, str]:
        """
        Tries to add a range of items without duplicates.

        Args:
            items (List[T]): The list of items to add.

        Returns:
            Tuple[bool, str]: A tuple containing a boolean indicating success and an error message if any.
        """
        if items is None:
            return False, "Range of items is null. Data error."

        for item in items:
            success, error_message = self.try_add_no_duplicate(item)
            if not success:
                return False, error_message

        return True, ""

    def update_entry(self, item: T):
        """
        Updates an entry.

        Args:
            item (T): The item to update.
        """
        if item is None or not item.get_both_guids().strip():
            return

        if item.get_both_guids() not in self._dictionary_of_everything_keyed_by_both_guids:
            return

        self._dictionary_of_everything_keyed_by_both_guids[item.get_both_guids()] = item  # Overwrite

        self._sequence_is_out_of_date = True
        self._dictionary_of_most_recent_item_per_originating_item_guid_is_out_of_date = True

    def remove_entry(self, both_guids_as_key: str) -> Optional[T]:
        """
        Removes an entry by both GUIDs as key.

        Args:
            both_guids_as_key (str): The key to remove the entry.

        Returns:
            Optional[T]: The removed entry if found, None otherwise.
        """
        if not both_guids_as_key.strip():
            return None

        item = self._dictionary_of_everything_keyed_by_both_guids.pop(both_guids_as_key, None)

        if item is not None:
            self._sequence_is_out_of_date = True
            self._dictionary_of_most_recent_item_per_originating_item_guid_is_out_of_date = True

        return item

    def reorder_raw_entries_by_descending_timestamp(self):
        """
        Reorders the raw entries by descending timestamp.
        """
        if self.sequence_is_pristine:
            return

        self._everything_ordered_by_descending_timestamp.clear()

        sorted_entries = sorted(
            self._dictionary_of_everything_keyed_by_both_guids.values(),
            key=lambda x: (x.timestamp_binary_format, x.when_touched_binary_format),
            reverse=True
        )

        self._everything_ordered_by_descending_timestamp.extend(sorted_entries)

        self._nasty_little_mirror.clear()

        self._nasty_little_mirror.extend(self._everything_ordered_by_descending_timestamp[:self.desired_height_of_short_list])

        self._sequence_is_out_of_date = False

    def clear_cache(self) -> int:
        """
        Clears the cache.

        Returns:
            int: The count of items cleared.
        """
        count_of_items_cleared = len(self._dictionary_of_everything_keyed_by_both_guids)

        self._everything_ordered_by_descending_timestamp.clear()
        self._dictionary_of_everything_keyed_by_both_guids.clear()
        self._dictionary_of_most_recent_item_keyed_by_originating_item_guid.clear()
        self._nasty_little_mirror.clear()

        self._sequence_is_out_of_date = True  # Handle the subsequent first-time-thru correctly
        self._dictionary_of_most_recent_item_per_originating_item_guid_is_out_of_date = True  # Ditto

        return count_of_items_cleared

    # methods to access data

    def contains_key_as_both_guids(self, both_guids_as_key: str) -> bool:
        """
        Checks if the dictionary contains the given key.

        Args:
            both_guids_as_key (str): The key to check.

        Returns:
            bool: True if the key is present, False otherwise.
        """
        return both_guids_as_key in self._dictionary_of_everything_keyed_by_both_guids

    def contains_entry_with_matching_both_guids(self, item: T) -> bool:
        """
        Checks if the dictionary contains an entry with matching both GUIDs.

        Args:
            item (T): The item to check.

        Returns:
            bool: True if the entry is present, False otherwise.
        """
        return item is not None and self.contains_key_as_both_guids(item.get_both_guids())

    def get_entry_by_both_guids_as_key(self, both_guids_as_key: str) -> Optional[T]:
        """
        Gets an entry by both GUIDs as key.

        Args:
            both_guids_as_key (str): The key to get the entry.

        Returns:
            Optional[T]: The entry if found, None otherwise.
        """
        if not both_guids_as_key.strip():
            return None

        return self._dictionary_of_everything_keyed_by_both_guids.get(both_guids_as_key)

    def get_all_entries_as_raw_data(self) -> List[T]:
        """
        Gets all entries as raw data.

        Returns:
            List[T]: A list of all entries ordered by descending timestamp.
        """
        if self.sequence_is_pristine:
            return self._everything_ordered_by_descending_timestamp

        self.reorder_raw_entries_by_descending_timestamp()

        return self._everything_ordered_by_descending_timestamp

    def get_youngest_descendent_of_each_originating_item_guid_including_ditches(self) -> List[T]:
        """
        Gets the youngest descendent of each originating item GUID, including ditches.

        Returns:
            List[T]: A list of the youngest descendents ordered by descending timestamp.
        """
        # Step 1. Update the dictionary of most recent item per OriginatingItemGuid
        self.make_dictionary_of_most_recent_item_for_each_originating_item_guid()

        # Step 2. Order nicely
        sorted_items = sorted(
            self._dictionary_of_most_recent_item_keyed_by_originating_item_guid.values(),
            key=lambda x: (x.timestamp_binary_format, x.when_touched_binary_format),
            reverse=True
        )

        return sorted_items

    def get_all_entries_as_raw_data_not_yet_pushed(self) -> List[T]:
        """
        Gets all entries as raw data that have not yet been pushed.

        Returns:
            List[T]: A list of all entries that have not yet been pushed.
        """
        return [item for item in self.get_all_entries_as_raw_data() if item and item.is_still_to_be_pushed]

    def get_quick_and_dirty_short_list_of_entries(self) -> List[T]:
        """
        Gets a quick and dirty short list of entries.

        Returns:
            List[T]: A list of entries from the nasty little mirror.
        """
        return self._nasty_little_mirror

    def get_most_recent_entry(self) -> Optional[T]:
        """
        Gets the most recent entry.

        Returns:
            Optional[T]: The most recent entry if found, None otherwise.
        """
        if not self._everything_ordered_by_descending_timestamp:
            return None

        return self._everything_ordered_by_descending_timestamp[0]

    def get_best_guess_headline_entry(self) -> Optional[T]:
        """
        Gets the best guess headline entry.

        Returns:
            Optional[T]: The best guess headline entry if found, None otherwise.
        """
        return self.get_most_recent_entry()

    def contains_key_as_both_guids(self, both_guids_as_key: str) -> bool:
        """
        Checks if the dictionary contains the given key.

        Args:
            both_guids_as_key (str): The key to check.

        Returns:
            bool: True if the key is present, False otherwise.
        """
        return both_guids_as_key in self._dictionary_of_everything_keyed_by_both_guids

    def contains_entry_with_matching_both_guids(self, item: T) -> bool:
        """
        Checks if the dictionary contains an entry with matching both GUIDs.

        Args:
            item (T): The item to check.

        Returns:
            bool: True if the entry is present, False otherwise.
        """
        return item is not None and self.contains_key_as_both_guids(item.get_both_guids())

    def get_entry_by_both_guids_as_key(self, both_guids_as_key: str) -> Optional[T]:
        """
        Gets an entry by both GUIDs as key.

        Args:
            both_guids_as_key (str): The key to get the entry.

        Returns:
            Optional[T]: The entry if found, None otherwise.
        """
        if not both_guids_as_key.strip():
            return None

        return self._dictionary_of_everything_keyed_by_both_guids.get(both_guids_as_key)

    def get_all_entries_as_raw_data(self) -> List[T]:
        """
        Gets all entries as raw data.

        Returns:
            List[T]: A list of all entries ordered by descending timestamp.
        """
        if self.sequence_is_pristine:
            return self._everything_ordered_by_descending_timestamp

        self.reorder_raw_entries_by_descending_timestamp()

        return self._everything_ordered_by_descending_timestamp

    def get_youngest_descendent_with_same_originating_item_guid(self, candidate_originating_item_guid: str) -> Optional[T]:
        """
        Gets the youngest descendent with the same originating item GUID.

        Args:
            candidate_originating_item_guid (str): The originating item GUID to search for.

        Returns:
            Optional[T]: The youngest descendent if found, None otherwise.
        """
        self.make_dictionary_of_most_recent_item_for_each_originating_item_guid()

        return self._dictionary_of_most_recent_item_keyed_by_originating_item_guid.get(candidate_originating_item_guid)

    def get_single_most_recent_item_of_this_kind_of_recording_mode_from_master_list(self, recording_mode_enum: str) -> Optional[T]:
        """
        Gets the single most recent item of this kind of recording mode from the master list.

        Args:
            recording_mode_enum (str): The recording mode enum to search for.

        Returns:
            Optional[T]: The most recent item if found, None otherwise.
        """
        if not recording_mode_enum.strip():
            return None

        return next(
            (item for item in sorted(
                (item for item in self.get_all_un_ditched_youngest_descendents_with_same_originating_item_guid_as_master_list()
                 if item and item.recording_mode_enum == recording_mode_enum),
                key=lambda x: x.when_touched_binary_format,
                reverse=True
            )),
            None
        )

    def get_dictionary_of_identifiers_with_their_most_recent_item_for_this_recording_mode_from_master_list(self, recording_mode_enum: str) -> Optional[Dict[str, T]]:
        """
        Gets a dictionary of identifiers with their most recent item for this recording mode from the master list.

        Args:
            recording_mode_enum (str): The recording mode enum to search for.

        Returns:
            Optional[Dict[str, T]]: A dictionary of identifiers with their most recent item if found, None otherwise.
        """
        if not recording_mode_enum.strip():
            return None

        items_for_this_recording_mode = [
            item for item in self.get_all_un_ditched_youngest_descendents_with_same_originating_item_guid_as_master_list()
            if item and item.recording_mode_enum == recording_mode_enum
        ]

        if not items_for_this_recording_mode:
            return {}

        hub_items_grouped_by_identifier = self.to_list_dictionary_grouped_by_bib(items_for_this_recording_mode)

        return {
            identifier: max(subgroup, key=lambda x: x.when_touched_binary_format)
            for identifier, subgroup in hub_items_grouped_by_identifier.items()
        }

    def get_dictionary_of_identifiers_with_their_multiple_items_for_this_recording_mode_from_master_list(self, recording_mode_enum: str) -> Optional[Dict[str, List[T]]]:
        """
        Gets a dictionary of identifiers with their multiple items for this recording mode from the master list.

        Args:
            recording_mode_enum (str): The recording mode enum to search for.

        Returns:
            Optional[Dict[str, List[T]]]: A dictionary of identifiers with their multiple items if found, None otherwise.
        """
        if not recording_mode_enum.strip():
            return None

        items_for_this_recording_mode = [
            item for item in self.get_all_un_ditched_youngest_descendents_with_same_originating_item_guid_as_master_list()
            if item and item.recording_mode_enum == recording_mode_enum
        ]

        return self.to_list_dictionary_grouped_by_bib(items_for_this_recording_mode)

    def is_most_recent_entry_with_same_originating_item_guid(self, candidate_most_recent_item: T) -> bool:
        """
        Checks if the candidate item is the most recent entry with the same originating item GUID.

        Args:
            candidate_most_recent_item (T): The candidate item to check.

        Returns:
            bool: True if the candidate item is the most recent, False otherwise.
        """
        if candidate_most_recent_item is None:
            return False

        self.make_dictionary_of_most_recent_item_for_each_originating_item_guid()

        actual_most_recent_item = self._dictionary_of_most_recent_item_keyed_by_originating_item_guid.get(
            candidate_most_recent_item.originating_item_guid
        )

        return actual_most_recent_item is None or candidate_most_recent_item.when_touched_binary_format >= actual_most_recent_item.when_touched_binary_format

    def flag_all_entries_as_saved(self) -> Tuple[int, int]:
        """
        Flags all entries as saved.

        Returns:
            Tuple[int, int]: A tuple containing the total number of entries and the number of new saves.
        """
        total_saves = len(self._dictionary_of_everything_keyed_by_both_guids)
        new_saves = 0

        for item in self._dictionary_of_everything_keyed_by_both_guids.values():
            if item.is_still_to_be_backed_up:
                item.is_still_to_be_backed_up = False
                new_saves += 1

        if new_saves > 0:
            self._sequence_is_out_of_date = True
            self._dictionary_of_most_recent_item_per_originating_item_guid_is_out_of_date = True

        return total_saves, new_saves

    def flag_all_entries_as_pushed(self) -> Tuple[int, int]:
        """
        Flags all entries as pushed.

        Returns:
            Tuple[int, int]: A tuple containing the total number of entries and the number of new pushes.
        """
        total_pushes = len(self._dictionary_of_everything_keyed_by_both_guids)
        new_pushes = 0

        for item in self._dictionary_of_everything_keyed_by_both_guids.values():
            if item.is_still_to_be_pushed:
                item.is_still_to_be_pushed = False
                new_pushes += 1

        if new_pushes > 0:
            self._sequence_is_out_of_date = True
            self._dictionary_of_most_recent_item_per_originating_item_guid_is_out_of_date = True

        return total_pushes, new_pushes

    def flag_incremental_entries_as_pushed(self, pushed: Iterable[T], true_if_pushed_false_if_unpushed: bool) -> int:
        """
        Flags incremental entries as pushed or unpushed.

        Args:
            pushed (Iterable[T]): The entries to flag.
            true_if_pushed_false_if_unpushed (bool): Flag as pushed if True, unpushed if False.

        Returns:
            int: The number of new pushes.
        """
        new_pushes = 0
        when_pushed = datetime.now().timestamp()

        for item in pushed:
            if item is None or not item.get_both_guids():
                continue

            discovered = self._dictionary_of_everything_keyed_by_both_guids.get(item.get_both_guids())
            if discovered is None:
                continue

            if true_if_pushed_false_if_unpushed:
                discovered.is_still_to_be_pushed = False
                discovered.when_pushed_binary_format = when_pushed
            else:
                discovered.is_still_to_be_pushed = True
                discovered.when_pushed_binary_format = 0

            new_pushes += 1

        if new_pushes > 0:
            self._sequence_is_out_of_date = True
            self._dictionary_of_most_recent_item_per_originating_item_guid_is_out_of_date = True

        return new_pushes

    # helpers

    def add_or_overwrite_to_dirty_little_baby_mirror(self, item: T):
        """
        Adds or overwrites an item in the dirty little baby mirror.

        Args:
            item (T): The item to add or overwrite.
        """
        # Null checks
        if item is None:
            return

        if not item.get_both_guids():
            return

        if item == T():
            return  # Policy is to ignore attempted additions of "blank" i.e. unpopulated "new" items

        # Fast update
        if item in self._nasty_little_mirror:
            index = self._nasty_little_mirror.index(item)
            self._nasty_little_mirror.insert(index, item)
        else:
            if self.desired_height_of_short_list < 1:
                return

            self._nasty_little_mirror.insert(0, item)  # O(n) unfortunately, so keep the list short

            if len(self._nasty_little_mirror) > self.desired_height_of_short_list:
                self._nasty_little_mirror.pop()  # Ditch the oldest one

    def make_dictionary_of_most_recent_item_for_each_originating_item_guid(self):
        """
        Makes a dictionary of the most recent item for each originating item GUID.
        """
        if not self._dictionary_of_most_recent_item_per_originating_item_guid_is_out_of_date:
            return

        # For ALL records (DatabaseActionEnum=Add and =Edit) - group them by OriginatingItemGuid
        all_hub_items = (
            item for item in self.get_all_entries_as_raw_data()
            if item.originating_item_guid
        )

        grouped_items = defaultdict(list)
        for item in all_hub_items:
            grouped_items[item.originating_item_guid].append(item)

        most_recent_items = (
            max(sub_group, key=lambda x: x.when_touched_binary_format)
            for sub_group in grouped_items.values()
            if sub_group
        )

        for hub_item in most_recent_items:
            self._dictionary_of_most_recent_item_keyed_by_originating_item_guid[hub_item.originating_item_guid] = hub_item

        self._dictionary_of_most_recent_item_per_originating_item_guid_is_out_of_date = False

    def get_all_un_ditched_youngest_descendents_with_same_originating_item_guid_as_master_list(self) -> List[T]:
        """
        Gets all unditched youngest descendents with the same originating item GUID as the master list.

        Returns:
            List[T]: A list of all unditched youngest descendents ordered by descending timestamp.
        """
        # Step 1. Update the dictionary of most recent item per OriginatingItemGuid
        self.make_dictionary_of_most_recent_item_for_each_originating_item_guid()

        # Step 2. Exclude ditches and order nicely
        unditched_items = [
            item for item in self._dictionary_of_most_recent_item_keyed_by_originating_item_guid.values()
            if not item.must_ditch_originating_item
        ]

        sorted_unditched_items = sorted(
            unditched_items,
            key=lambda x: (x.timestamp_binary_format, x.when_touched_binary_format),
            reverse=True
        )

        return sorted_unditched_items



# Example usage
if __name__ == "__main__":
    # Example usage of the RepositoryOfHubStyleEntries class
    class ExampleHubItem:
        def __init__(self, guid: str, originating_item_guid: str, timestamp_binary_format: int, when_touched_binary_format: int):
            self.guid = guid
            self.originating_item_guid = originating_item_guid
            self.timestamp_binary_format = timestamp_binary_format
            self.when_touched_binary_format = when_touched_binary_format
        
        self.GetBothGuids = lambda: f"{self.guid}{self.originating_item_guid}"

    repo = RepositoryOfHubStyleEntries[ExampleHubItem]()
    item1 = ExampleHubItem("guid1", "orig_guid1", 100, 200)
    item2 = ExampleHubItem("guid2", "orig_guid2", 150, 250)
    repo._dictionary_of_everything_keyed_by_both_guids[item1.guid] = item1
    repo._dictionary_of_everything_keyed_by_both_guids[item2.guid] = item2
    repo._sequence_is_out_of_date = True

    all_entries = repo.get_all_entries_as_raw_data()
    print("All entries:", [item.guid for item in all_entries])

    contains_key = repo.contains_key_as_both_guids("guid1-orig_guid1")
    print("Contains key 'guid1-orig_guid1':", contains_key)

    contains_entry = repo.contains_entry_with_matching_both_guids(item1)
    print("Contains entry with matching both GUIDs:", contains_entry)

    entry = repo.get_entry_by_both_guids_as_key("guid1-orig_guid1")
    print("Entry by both GUIDs as key:", entry.guid if entry else "None")

    success, error_message = repo.try_add_no_duplicate(item1)
    print("Try add no duplicate:", success, error_message)

    success, error_message = repo.try_add_range_no_duplicates([item1, item2])
    print("Try add range no duplicates:", success, error_message)

    repo.update_entry(item1)
    print("Updated entry:", repo.get_entry_by_both_guids_as_key("guid1-orig_guid1").guid)

    removed_entry = repo.remove_entry("guid1-orig_guid1")
    print("Removed entry:", removed_entry.guid if removed_entry else "None")

    count_cleared = repo.clear_cache()
    print("Count of items cleared:", count_cleared)

    youngest_descendents = repo.get_youngest_descendent_of_each_originating_item_guid_including_ditches()
    print("Youngest descendents including ditches:", [item.guid for item in youngest_descendents])

    not_yet_pushed_entries = repo.get_all_entries_as_raw_data_not_yet_pushed()
    print("Entries not yet pushed:", [item.guid for item in not_yet_pushed_entries])

    short_list_entries = repo.get_quick_and_dirty_short_list_of_entries()
    print("Quick and dirty short list of entries:", [item.guid for item in short_list_entries])

    most_recent_entry = repo.get_most_recent_entry()
    print("Most recent entry:", most_recent_entry.guid if most_recent_entry else "None")

    best_guess_headline_entry = repo.get_best_guess_headline_entry()
    print("Best guess headline entry:", best_guess_headline_entry.guid if best_guess_headline_entry else "None")
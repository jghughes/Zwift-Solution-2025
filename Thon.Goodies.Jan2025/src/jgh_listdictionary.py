"""
This module defines the JghListDictionary class, which 
provides a custom dictionary-like data structure.
"""

# Standard library imports
from typing import TypeVar, Generic
from collections import defaultdict
from typing import Callable, Tuple

TKey = TypeVar('TKey')
TValue = TypeVar('TValue')

class JghListDictionary(Generic[TKey, TValue]):
    """
    A generic dictionary-like class that maps keys to lists of values.

    This class allows you to associate multiple values with a single key,
    effectively creating a dictionary where each key maps to a list of values.
    It is useful in scenarios where you need to group multiple items under a
    single category or identifier.

    Attributes:
    -----------
    backingstore_dict : dict[TKey, list[TValue]]
        The internal dictionary that stores the keys and their corresponding lists of values.

    Methods:
    --------
    insert_key(key: TKey) -> bool:
        Adds a new key with an empty list if the key is not None.

    remove_key(key: TKey) -> list[TValue]:
        Removes the list for the given key and returns the associated list of values.

    append_value_to_list(key: TKey, value: TValue) -> None:
        Adds a value to the list associated with the given key. Overwrites existing value if any.

    remove_value_from_list(key: TKey, value: TValue) -> int:
        Removes all occurrences of the value from the list associated with the given key.

    remove_value_from_all_lists(value: TValue) -> Tuple[int, list[TKey]]:
        Removes the given value from all lists in the dictionary and returns the count of removed occurrences
        and the list of keys from which the value was removed.

    clear_all_values_from_list(key: TKey) -> int:
        Clears all values associated with the given key and returns the count of removed occurrences.

    clear_everything_everywhere() -> Tuple[int, int]:
        Clears all the entries in the dictionary and returns a tuple of the original number of keys
        and the original total number of values prior to removal.

    contains_key(key: TKey) -> bool:
        Checks if the dictionary contains the given key.

    contains_value_in_list(key: TKey, value: TValue) -> bool:
        Checks if the list associated with the given key contains the specified value.

    contains_value_in_any_list(value: TValue) -> bool:
        Checks if the dictionary contains the given value in any of the lists associated with the keys.

    get_keys() -> list[TKey]:
        Retrieves all the keys in the dictionary.

    get_keys_containing_value(value: TValue) -> list[TKey]:
        Retrieves all keys that have the given value in their list.

    get_keys_containing_selected_values(value_selector: Callable[[TValue], bool]) -> list[TKey]:
        Retrieves all keys that have values matching the given condition.

    get_value_count_for_key(key: TKey) -> int:
        Retrieves the number of values associated with the given key.

    get_values(key: TKey) -> list[TValue]:
        Retrieves the list of values associated with the given key.

    get_values_for_keys(key_selector: Callable[[TKey], bool]) -> list[TValue]:
        Retrieves all values for keys that match the given selector.

    get_values_for_all() -> list[TValue]:
        Retrieves all values in the dictionary.

    get_selected_values_from_key(key: TKey, value_selector: Callable[[TValue], bool]) -> list[TValue]:
        Retrieves all values associated with the given key that match the given selector.

    get_selected_values_from_all(value_selector: Callable[[TValue], bool]) -> list[TValue]:
        Retrieves all values that match the given selector.

    get_key_value_pairs_containing_selected_values(value_selector: Callable[[TValue], bool]) -> list[Tuple[TKey, TValue]]:
        Retrieves all key-value pairs where the values match the given condition.

    get_key_value_pairs_from_everywhere() -> list[Tuple[TKey, TValue]]:
        Retrieves all key-value pairs in the dictionary.

    Properties:
    -----------
    number_of_keys -> int:
        Retrieves the number of keys in the dictionary.

    number_of_values -> int:
        Retrieves the total number of values in the dictionary.
    """
    backingstore_dict: defaultdict[TKey, list[TValue]] = defaultdict(list)

    def insert_key(self, key: TKey) -> bool:
        """
        Adds a new key with an empty list if the key is not None.

        If the key already exists, the method will not create a new list or
        modify the existing list. It will simply return false to indicate that
        the key was not added. This ensures that the method does not modify the
        dictionary if the key already exists.

        Parameters:
        -----------
        key : TKey
            The key to add.

        Returns:
        --------
        bool
            True if the key was added, False if the specified key already exists or is None.
        """
        if key is None:
            return False
        if key in self.backingstore_dict:
            return False
        # Add with explicitly typed empty list
        self.backingstore_dict[key] = []

        return True

    def remove_key(self, key: TKey) -> list[TValue]:
        """
        Removes the list of values associated with the given key and returns it.

        If the key doesn't exist, the method returns an empty list, indicating that no key was removed.

        Parameters:
        -----------
        key : TKey
            The key to remove.

        Returns:
        --------
        list[TValue]
            The list of values associated with the removed key, or an empty list if the key does not exist.
        """
        match key:
            case None:
                return []
            case _:
                return self.backingstore_dict.pop(key, [])

    def append_value_to_list(self, key: TKey, value: TValue) -> None:
        """
        Adds a value to the list associated with the given key.

        1. The method checks if the key or value is None. If either is None, the method
           returns without making any changes.
        2. If both the key and value are not None, the method appends the value to the
           list associated with the given key in the backingstore_dict dictionary.
        3. Since the method uses the append function, it adds the value to the end of
           the list, even if the key-value pair already exists in the list. This means
           that the list can contain multiple values for the same key.

        If the key doesn't exist, the append_value_to_list method will create a new
        list for that key and then append the value to this new list.

        Parameters:
        -----------
        key : TKey
            The key to which the value should be added.
        value : TValue
            The value to add.

        Returns:
        --------
        None
        """
        if key is None or value is None:
            return None

        self.backingstore_dict[key].append(value)

        return None

    def remove_value_from_list(self, key: TKey, value: TValue) -> int:
        """
        Removes all occurrences of the value from the list associated with the given key.

        If the specified value does not exist in the list associated with the key,
        the method will leave the list unchanged. This ensures that the method only
        removes existing values and does not affect the list if the value is not present.

        Parameters:
        -----------
        key : TKey
            The key whose list should be modified.
        value : TValue
            The value to remove.

        Returns:
        --------
        int
            The number of occurrences of the value that were removed.
        """
        match (key, value):
            case (None, _) | (_, None):
                return 0
            case _ if key not in self.backingstore_dict:
                return 0
            case _:
                original_length = len(self.backingstore_dict[key])
                self.backingstore_dict[key] = [
                    v for v in self.backingstore_dict[key] if v != value
                ]
                return original_length - len(self.backingstore_dict[key])

    def remove_value_from_all_lists(self, value: TValue) -> Tuple[int, list[TKey]]:
        """
        Removes the given value from all lists in the dictionary and returns the count of removed occurrences
        and the list of keys from which the value was removed.

        Parameters:
        -----------
        value : TValue
            The value to remove.

        Returns:
        --------
        Tuple[int, list[TKey]]
            A tuple containing the total number of occurrences of the value that were removed
            and the list of keys from which the value was removed.
        """
        if value is None:
            return 0, []
        if not self.backingstore_dict.keys():
            return 0, []

        removed_count: int = 0
        keys_with_removed_value: list[TKey] = []

        for key in list(self.backingstore_dict.keys()):
            count = self.remove_value_from_list(key, value)
            if count > 0:
                removed_count += count
                keys_with_removed_value.append(key)

        return removed_count, keys_with_removed_value

    def clear_all_values_from_list(self, key: TKey) -> int:
        """
        Clears all values associated with the given key.

        If the key doesn't exist, the method will return 0, indicating that
        no values were cleared. This ensures that the method accurately reflects
        whether the specified key was present and its values were cleared.

        Parameters:
        -----------
        key : TKey
            The key for which to clear values.

        Returns:
        --------
        int
            The number of values that were cleared.
        """
        if key is None or key not in self.backingstore_dict:
            return 0

        original_count = len(self.backingstore_dict[key])
        self.backingstore_dict[key] = []
        return original_count

    def clear_everything_everywhere(self) -> Tuple[int, int]:
        """
        Clears all the entries in the dictionary and returns a tuple of the original
        number of keys and the original total number of values prior to removal.

        Returns:
        --------
        Tuple[int, int]
            A tuple containing the original number of keys and the original total
            number of values.
        """
        original_number_of_keys = self.number_of_keys
        original_number_of_values = self.number_of_values
        self.backingstore_dict.clear()
        return original_number_of_keys, original_number_of_values

    def contains_key(self, key: TKey) -> bool:
        """
        Checks if the dictionary contains the given key.

        Parameters:
        -----------
        key : TKey
            The key to check.

        Returns:
        --------
        bool
            True if the key is present, False otherwise.
        """
        return key in self.backingstore_dict

    def contains_value_in_list(self, key: TKey, value: TValue) -> bool:
        """
        Checks if the list associated with the given key contains the specified value.

        Parameters:
        -----------
        key : TKey
            The key whose list should be checked.
        value : TValue
            The value to check.

        Returns:
        --------
        bool
            True if the value is present in the list associated with
            the key, False otherwise.
        """
        if key is None or value is None:
            return False
        return value in self.backingstore_dict.get(key, [])

    def contains_value_in_any_list(self, value: TValue) -> bool:
        """
        Checks if the dictionary contains the given value in any of
        the lists associated with the keys.

        Parameters:
        -----------
        value : TValue
            The value to check.

        Returns:
        --------
        bool
            True if the value is present in any of the lists, False otherwise.
        """
        if value is None:
            return False
        return any(value in values for values in self.backingstore_dict.values())

    def get_keys(self) -> list[TKey]:
        """
        Retrieves all the keys in the dictionary.

        Returns:
        --------
        list[TKey]
            A list of all keys in the dictionary.
        """
        return list(self.backingstore_dict.keys())

    def get_keys_containing_value(self, value: TValue) -> list[TKey]:
        """
        Retrieves all keys that have the given value in their list.

        If the value exists multiple times under the same key, and multiple
        times across different keys, the get_keys_containing_value method will
        return a list of keys for each occurrence of the value. Here is a
        detailed explanation:

        1. Multiple occurrences under the same key:
            - If a value exists multiple times in the list associated with a single
              key, the method will include that key only once in the returned list.
              This is because the method checks if the value is in the list of values
              for each key, and it does not include the key multiple times for multiple
              occurrences of the value within the same list.
        2. Multiple occurrences across different keys:
            - If a value exists in the lists associated with multiple keys, the method
              will include each key where the value is found in the returned list.
              This means that if the value is present in the lists for several different
              keys, each of those keys will be included in the returned list.

        Parameters:
        -----------
        value : TValue
            The value to search for.

        Returns:
        --------
        list[TKey]
            A list of keys that have the value.
        """
        keys_with_value = [
            key for key, values in self.backingstore_dict.items() if value in values
        ]
        return keys_with_value

    def get_keys_containing_selected_values(
        self, value_selector: Callable[[TValue], bool]
    ) -> list[TKey]:
        """
        Retrieves all keys that have values matching the given condition.

        The get_keys_containing_selected_values method iterates over all keys and
        their associated lists of values. For each key, it checks if any value in
        the list matches the given condition. If a match is found, the key is added
        to the result list. This process is repeated for all keys in the dictionary.

        The method handles multiple occurrences of a value in the same list by
        adding the key only once if any value matches the condition. It handles
        multiple occurrences of a value across multiple lists by adding each key
        where the value matches the condition.

        Parameters:
        -----------
        value_selector : Callable[[TValue], bool]
            A function to selector values.

        Returns:
        --------
        list[TKey]
            A list of keys that have matching values.
        """
        keys_with_matching_values = [
            key
            for key, values in self.backingstore_dict.items()
            if any(value_selector(value) for value in values)
        ]
        return keys_with_matching_values

    def get_value_count_for_key(self, key: TKey) -> int:
        """
        Retrieves the number of values associated with the given key.

        Parameters:
        -----------
        key : TKey
            The key for which to number_of_keys the values.

        Returns:
        --------
        int
            The number of values associated with the key, or 0 if the key does not exist.
        """
        if key is None:
            return 0
        if key not in self.backingstore_dict:
            return 0
        return len(self.backingstore_dict[key])

    def get_values(self, key: TKey) -> list[TValue]:
        """
        Retrieves the list of values associated with the given key.

        Parameters:
        -----------
        key : TKey
            The key for which to retrieve values.

        Returns:
        --------
        list[TValue]
            The list of values associated with the key.
        """
        if key is None:
            raise ValueError("key cannot be None")
        return self.backingstore_dict.get(key, [])

    def get_values_for_keys(self, key_selector: Callable[[TKey], bool]) -> list[TValue]:
        """
        Retrieves all values for keys that match the given selector.

        The get_values_for_keys method iterates over all keys and
        their associated lists of values. For each key that matches the given selector,
        it collects each value in the list associated with that key. This process is
        repeated for all keys in the dictionary.

        The get_values_for_keys method handles multiple occurrences
        of a value in the same list by including each occurrence separately. It handles
        multiple occurrences of a value across multiple lists by including each
        occurrence separately for each key that matches the selector.

        Parameters:
        -----------
        key_selector : Callable[[TKey], bool]
            A function to select keys.

        Returns:
        --------
        list[TValue]
            A list of values for matching keys.
        """
        values_list: list[TValue] = []
        for key, values in self.backingstore_dict.items():
            if key_selector(key):
                values_list.extend(values)
        return values_list

    def get_values_for_all(self) -> list[TValue]:
        """
        Retrieves all values in the dictionary.

        If the dictionary contains multiple occurrences of a value under the same
        key and multiple occurrences across different keys, the get_values_for_all
        method will include each occurrence of the value in the returned list. Here
        is a detailed explanation:

        1. Multiple Occurrences Under the Same Key:
            - If a value exists multiple times in the list associated with a single key,
                the method will include each occurrence of the value. This means that if a
                value appears multiple times in the list for a key, each instance will be
                included separately.
        2. Multiple Occurrences Across Different Keys:
            - If a value exists in the lists associated with multiple keys, the method
                will include each occurrence of the value from each key. This means that if
                a value is present in the lists for several different keys, each instance
                of the value will be included.

        Returns:
        --------
        list[TValue]
            A list of all values in the dictionary.
        """
        return [value for values in self.backingstore_dict.values() for value in values]

    def get_selected_values_from_key(
        self, key: TKey, value_selector: Callable[[TValue], bool]
    ) -> list[TValue]:
        """
        Retrieves all values associated with the given key that match the given selector.

        If the list associated with the key contains multiple occurrences of a value that satisfies
        the selector, the method will include each occurrence of the value in the returned list.

        Parameters:
        -----------
        key : TKey
            The key for which to retrieve values.
        value_selector : Callable[[TValue], bool]
            A function to select values.

        Returns:
        --------
        list[TValue]
            A list of all matching values associated with the given key.
        """
        if key is None or key not in self.backingstore_dict:
            return []

        selected_values: list[TValue] = []
        for value in self.backingstore_dict[key]:
            if value_selector(value):
                selected_values.append(value)
        return selected_values

    def get_selected_values_from_all(
        self, value_selector: Callable[[TValue], bool]
    ) -> list[TValue]:
        """
        Retrieves all values that match the given selector.

        If the dictionary contains multiple occurrences of a value that satisfies
        the selector under the same key and multiple occurrences across different
        keys, the get_selected_values_from_all method will include each
        occurrence of the value in the returned list. Here is a detailed explanation:

        1. Multiple Occurrences Under the Same Key:
            - If a value exists multiple times in the list associated with a single key,
              the method will include each occurrence of the value. This means that if a
              value appears multiple times in the list for a key, each instance will be
              included separately.
        2. Multiple Occurrences Across Different Keys:
            - If a value exists in the lists associated with multiple keys, the method
              will include each occurrence of the value from each key. This means that if
              a value is present in the lists for several different keys, each instance
              of the value will be included.

        Parameters:
        -----------
        value_selector : Callable[[TValue], bool]
            A function to select values.

        Returns:
        --------
        list[TValue]
            A list of all matching values in the dictionary.
        """
        selected_values: list[TValue] = []
        for values in self.backingstore_dict.values():
            for value in values:
                if value_selector(value):
                    selected_values.append(value)
        return selected_values

    def get_key_value_pairs_containing_selected_values(
        self, value_selector: Callable[[TValue], bool]
    ) -> list[Tuple[TKey, TValue]]:
        """
        Retrieves all key-value pairs where the values match the given condition.

        The get_key_value_pairs_containing_selected_values method iterates over all
        keys and their associated lists of values. For each key, it checks if any value
        in the list matches the given condition. If a match is found, the key-value pair
        is added to the result list. This process is repeated for all keys in the dictionary.

        The method handles multiple occurrences of a value in the same list by adding
        each key-value pair separately if any value matches the condition. It handles
        multiple occurrences of a value across multiple lists by adding each key-value
        pair where the value matches the condition.

        Parameters:
        -----------
        value_selector : Callable[[TValue], bool]
            A function to select values.

        Returns:
        --------
        list[Tuple[TKey, TValue]]
            A list of key-value pairs where the values match the given condition.
        """
        key_value_pairs: list[Tuple[TKey, TValue]] = []
        for key, values in self.backingstore_dict.items():
            for value in values:
                if value_selector(value):
                    key_value_pairs.append((key, value))
        return key_value_pairs

    def get_key_value_pairs_from_everywhere(self) -> list[Tuple[TKey, TValue]]:
        """
        Retrieves all key-value pairs in the dictionary. Handles multiple repeats
        in the same list and repeats across multiple lists by treating each
        occurrence independently. All repeats are included separately.

        Returns:
        --------
        list[Tuple[TKey, TValue]]
            A list of all key-value pairs in the dictionary.
        """
        key_value_pairs: list[Tuple[TKey, TValue]] = []
        for key, values in self.backingstore_dict.items():
            for value in values:
                key_value_pairs.append((key, value))
        return key_value_pairs

    @property
    def number_of_keys(self) -> int:
        """
        Retrieves the number of keys in the dictionary.

        Returns:
        --------
        int
            The number of keys in the dictionary.
        """
        return len(self.backingstore_dict)

    @property
    def number_of_values(self) -> int:
        """
        Retrieves the total number of values in the dictionary.

        Returns:
        --------
        int
            The total number of values in the dictionary.
        """
        return sum(len(values) for values in self.backingstore_dict.values())

    def __getitem__(self, key: TKey) -> list[TValue]:
        """
        Retrieves the list of values associated with the given key.

        Parameters:
        -----------
        key : TKey
            The key for which to retrieve values.

        Returns:
        --------
        list[TValue]
            The list of values associated with the key.
        """
        if key not in self.backingstore_dict:
            self.backingstore_dict[key] = []
        return self.backingstore_dict[key]

    def __setitem__(self, key: TKey, value: list[TValue]):
        """
        Sets the list of values for the given key.

        Parameters:
        -----------
        key : TKey
            The key for which to set values.
        value : list[TValue]
            The list of values to set.
        """
        self.backingstore_dict[key] = value

 # example usage of the JghListDictionary class


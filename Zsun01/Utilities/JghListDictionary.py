from collections import defaultdict
from typing import TypeVar, Generic, List, Callable, Tuple
from pydantic import BaseModel, Field

TKey = TypeVar("TKey")
TValue = TypeVar("TValue")


class JghListDictionary(BaseModel, Generic[TKey, TValue]):
    """
    A generic dictionary-like class that maps keys to lists of values.

    This class allows you to associate multiple values with a single key, effectively creating a dictionary
    where each key maps to a list of values. It is useful in scenarios where you need to group multiple
    items under a single category or identifier.

    Attributes:
    -----------
    inner_values : Dict[TKey, List[TValue]]
        The internal dictionary that stores the keys and their corresponding lists of values.

    Methods:
    --------
    add_key(key: TKey) -> int:
        Adds a new key with an empty list if the key is not None.

    add_value_to_given_key(key: TKey, value: TValue) -> int:
        Adds a value to the list associated with the given key.

    get_value_count_for_given_key(key: TKey) -> int:
        Retrieves the number of values associated with the given key.

    remove_given_key(key: TKey) -> bool:
        Removes the entry for the given key.

    remove_value_from_given_key(key: TKey, value: TValue) -> int:
        Removes the given value from the list associated with the given key.

    remove_value_from_everywhere(value: TValue):
        Removes the given value from all lists in the dictionary.

    clear_values_for_key(key: TKey) -> bool:
        Clears all values associated with the given key.

    clear_everything_everywhere():
        Clears all the entries in the dictionary.

    contains_key(key: TKey) -> bool:
        Checks if the dictionary contains the given key.

    contains_value_in_given_key(key: TKey, value: TValue) -> bool:
        Checks if the list associated with the given key contains the specified value.

    contains_value_in_any_key(value: TValue) -> bool:
        Checks if the dictionary contains the given value in any of the lists associated with the keys.

    get_keys() -> List[TKey]:
        Retrieves all the keys in the dictionary.

    get_keys_containing_value(value: TValue) -> List[TKey]:
        Retrieves all keys that have the given value in their list.

    get_keys_containing_selected_values(value_selector: Callable[[TValue], bool]) -> List[TKey]:
        Retrieves all keys that have values matching the given condition.

    get_values_belonging_to_given_key(key: TKey) -> List[TValue]:
        Retrieves the list of values associated with the given key.

    get_values_belonging_to_selected_keys(key_selector: Callable[[TKey], bool]) -> List[TValue]:
        Retrieves all values for keys that match the given selector.

    get_values_from_everywhere() -> List[TValue]:
        Retrieves all values in the dictionary.

    get_selected_values_from_everywhere(value_selector: Callable[[TValue], bool]) -> List[TValue]:
        Retrieves all values that match the given selector.

    get_key_value_pairs_from_everywhere() -> List[Tuple[TKey, TValue]]:
        Retrieves all key-value pairs in the dictionary.

    get_key_value_pairs_containing_selected_values(value_selector: Callable[[TValue], bool]) -> List[Tuple[TKey, TValue]]:
        Retrieves all key-value pairs where the values match the given condition.

    Properties:
    -----------
    number_of_keys -> int:
        Retrieves the number of keys in the dictionary.

    number_of_values -> int:
        Retrieves the total number of values in the dictionary.
    """

    inner_values: defaultdict[TKey, List[TValue]] = Field(
        default_factory=lambda: defaultdict(list[TValue])
    )

    def add_key(self, key: TKey) -> None:
        """
        Adds a new key with an empty list if the key is not None.

        If the key already exists, the method will not create a new list or modify the existing list.

        Parameters:
        -----------
        key : TKey
            The key to add.

        Returns:
        --------
        None
        """
        if key is None:
            return None
        if key not in self.inner_values:
            self.inner_values[key] = []  # Explicitly typed empty list
        return None

    def add_value_to_given_key(self, key: TKey, value: TValue) -> None:
        """
        Adds a value to the list associated with the given key.

        1. The method checks if the key or value is None. If either is None, the method
           returns without making any changes.
        2. If both the key and value are not None, the method appends the value to the
           list associated with the given key in the inner_values dictionary.
        3. Since the method uses the append function, it adds the value to the end of
           the list, even if the key-value pair already exists in the list. This means
           that the list can contain multiple values for the same key.

        If the key doesn't exist, the add_value_to_given_key method will create a new list for that
        key and then append the value to this new list.

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
        self.inner_values[key].append(value)

    def get_value_count_for_given_key(self, key: TKey) -> int:
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
        if key not in self.inner_values:
            return 0
        return len(self.inner_values[key])

    def remove_given_key(self, key: TKey)-> None:
        """
        Removes the list for the given key.

        If the key doesn't exist, the remove_given_key method will return False, indicating
        that no key was removed. This ensures that the method accurately reflects
        whether the specified key was present and removed from the dictionary.

        Parameters:
        -----------
        key : TKey
            The key to remove.

        Returns:
        --------
        None
        """
        if key is None:
            return None

        if key not in self.inner_values:
            return None

        self.inner_values.pop(key, None)

    def remove_value_from_given_key(self, key: TKey, value: TValue) -> None:
        """
        Removes all occurrences of the value from the list associated with the given key.

        If the specified value does not exist in the list associated with a key, the
        remove_value_from_given_key method will leave the list unchanged. This ensures that the method
        only removes existing values and does not affect the list if the value is not present.

        Parameters:
        -----------
        key : TKey
            The key whose list should be modified.
        value : TValue
            The value to remove.

        Returns:
        --------
        None
        """
        if key is None or value is None:
            return None
        if key not in self.inner_values:
            return None

        if value in self.inner_values[key]:
            # Remove all occurrences. Use filter function to create a new list that excludes all occurrences of the value
            self.inner_values[key] = list(filter(lambda v: v != value, self.inner_values[key]))

        return None

    def remove_value_from_everywhere(self, value: TValue)-> None:
        """
        Removes the given value from all lists in the dictionary.

        Parameters:
        -----------
        value : TValue
            The value to remove.
        """
        for key in list(self.inner_values.keys()):
            self.remove_value_from_given_key(key, value)
            return None

    def clear_values_for_key(self, key: TKey) -> None:
        """
        Clears all values associated with the given key.

        Parameters:
        -----------
        key : TKey
            The key for which to clear values.

        Returns:
        --------
        None
        """
        if key is None or key not in self.inner_values:
            return None

        self.inner_values[key] = []
        return None

    def clear_everything_everywhere(self):
        """
        Clears all the entries in the dictionary.
        """
        self.inner_values.clear()

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
        return key in self.inner_values

    def contains_value_in_given_key(self, key: TKey, value: TValue) -> bool:
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
            True if the value is present in the list associated with the key, False otherwise.
        """
        if key is None or value is None:
            return False
        return value in self.inner_values.get(key, [])

    def contains_value_in_any_key(self, value: TValue) -> bool:
        """
        Checks if the dictionary contains the given value in any of the lists associated with the keys.

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
        return any(value in values for values in self.inner_values.values())

    def get_keys(self) -> List[TKey]:
        """
        Retrieves all the keys in the dictionary.

        Returns:
        --------
        List[TKey]
            A list of all keys in the dictionary.
        """
        return list(self.inner_values.keys())

    def get_keys_containing_value(self, value: TValue) -> List[TKey]:
        """
        Retrieves all keys that have the given value in their list.

        If the value exists multiple times under the same key, and multiple
        times across different keys, the get_keys_containing_value method will return
        a list of keys for each occurrence of the value. Here is a detailed explanation:

        1.	Multiple occurrences under the same key:
            -	If a value exists multiple times in the list associated with a single
                key, the method will include that key only once in the returned list.
                This is because the method checks if the value is in the list of values
                for each key, and it does not include the key multiple times for multiple
                occurrences of the value within the same list.
        2.	Multiple occurrences across different keys:
            -	If a value exists in the lists associated with multiple keys, the method
                will include each key where the value is found in the returned list.
                This means that if the value is present in the lists for several different
                keys, each of those keys will be included in the returned list.

        Parameters:
        -----------
        value : TValue
            The value to search for.

        Returns:
        --------
        List[TKey]
            A list of keys that have the value.
        """
        keys_with_value = [
            key for key, values in self.inner_values.items() if value in values
        ]
        return keys_with_value

    def get_keys_containing_selected_values(
        self, value_selector: Callable[[TValue], bool]
    ) -> List[TKey]:
        """
        Retrieves all keys that have values matching the given condition.

        The get_keys_containing_selected_values method iterates over all keys and their associated
        lists of values. For each key, it checks if any value in the list matches the
        given condition. If a match is found, the key is added to the result list. This process is repeated
        for all keys in the dictionary.

        The method handles multiple occurrences of a value in the same list by adding
        the key only once if any value matches the condition. It handles multiple occurrences
        of a value across multiple lists by adding each key where the value matches the condition.

        Parameters:
        -----------
        value_selector : Callable[[TValue], bool]
            A function to selector values.

        Returns:
        --------
        List[TKey]
            A list of keys that have matching values.
        """
        keys_with_matching_values = [
            key
            for key, values in self.inner_values.items()
            if any(value_selector(value) for value in values)
        ]
        return keys_with_matching_values

    def get_values_belonging_to_given_key(self, key: TKey) -> List[TValue]:
        """
        Retrieves the list of values associated with the given key.

        Parameters:
        -----------
        key : TKey
            The key for which to retrieve values.

        Returns:
        --------
        List[TValue]
            The list of values associated with the key.
        """
        if key is None:
            raise ValueError("key cannot be None")
        return self.inner_values.get(key, [])

    def get_values_belonging_to_selected_keys(
        self, key_selector: Callable[[TKey], bool]
    ) -> List[TValue]:
        """
        Retrieves all values for keys that match the given selector.

        The get_values_belonging_to_selected_keys method iterates over all keys and their associated
        lists of values. For each key that matches the given selector, it collects each
        value in the list associated with that key. This process is repeated for all
        keys in the dictionary.

        The get_values_belonging_to_selected_keys method handles multiple occurrences of a value in the same
        list by including each occurrence separately. It handles multiple occurrences of a value
        across multiple lists by including each occurrence separately for each key that matches the selector.

        Parameters:
        -----------
        key_selector : Callable[[TKey], bool]
            A function to select keys.

        Returns:
        --------
        List[TValue]
            A list of values for matching keys.
        """
        values_list = []
        for key, values in self.inner_values.items():
            if key_selector(key):
                values_list.extend(values)
        return values_list

    def get_values_from_everywhere(self) -> List[TValue]:
        """
        Retrieves all values in the dictionary.

        If the dictionary contains multiple occurrences of a value under the same
        key and multiple occurrences across different keys, the get_values_from_everywhere
        method will include each occurrence of the value in the returned list. Here is a detailed explanation:

        1. Multiple Occurrences Under the Same Key:
            - If a value exists multiple times in the list associated with a single key, the method
              will include each occurrence of the value. This means that if a value appears multiple
              times in the list for a key, each instance will be included separately.
        2. Multiple Occurrences Across Different Keys:
            - If a value exists in the lists associated with multiple keys, the method will include
              each occurrence of the value from each key. This means that if a value is present in
              the lists for several different keys, each instance of the value will be included.

        Returns:
        --------
        List[TValue]
            A list of all values in the dictionary.
        """
        values_list: List[TValue] = []
        for values in self.inner_values.values():
            values_list.extend(values)
        return values_list

    def get_selected_values_from_everywhere(
        self, value_selector: Callable[[TValue], bool]
    ) -> List[TValue]:
        """
        Retrieves all values that match the given selector.

        If the dictionary contains multiple occurrences of a value that satisfies the selector
        under the same key and multiple occurrences across different keys, the get_selected_values_from_everywhere
        method will include each occurrence of the value in the returned list. Here is a detailed explanation:

        1. Multiple Occurrences Under the Same Key:
            - If a value exists multiple times in the list associated with a single key, the method
              will include each occurrence of the value. This means that if a value appears multiple
              times in the list for a key, each instance will be included separately.
        2. Multiple Occurrences Across Different Keys:
            - If a value exists in the lists associated with multiple keys, the method will include
              each occurrence of the value from each key. This means that if a value is present in
              the lists for several different keys, each instance of the value will be included.

        Parameters:
        -----------
        value_selector : Callable[[TValue], bool]
            A function to select values.

        Returns:
        --------
        List[TValue]
            A list of all matching values in the dictionary.
        """
        selected_values: List[TValue] = []
        for values in self.inner_values.values():
            for value in values:
                if value_selector(value):
                    selected_values.append(value)
        return selected_values

    def get_key_value_pairs_containing_selected_values(self, value_selector: Callable[[TValue], bool]) -> List[Tuple[TKey, TValue]]:
        """
        Retrieves all key-value pairs where the values match the given condition.

        The get_key_value_pairs_containing_selected_values method iterates over all keys and their associated
        lists of values. For each key, it checks if any value in the list matches the
        given condition. If a match is found, the key-value pair is added to the result list. This process is repeated
        for all keys in the dictionary.

        The method handles multiple occurrences of a value in the same list by adding
        each key-value pair separately if any value matches the condition. It handles multiple occurrences
        of a value across multiple lists by adding each key-value pair where the value matches the condition.

        Parameters:
        -----------
        value_selector : Callable[[TValue], bool]
            A function to select values.

        Returns:
        --------
        List[Tuple[TKey, TValue]]
            A list of key-value pairs where the values match the given condition.
        """
        key_value_pairs: List[Tuple[TKey, TValue]] = []
        for key, values in self.inner_values.items():
            for value in values:
                if value_selector(value):
                    key_value_pairs.append((key, value))
        return key_value_pairs

    def get_key_value_pairs_from_everywhere(self) -> List[Tuple[TKey, TValue]]:
        """
        Retrieves all key-value pairs in the dictionary. Handles multiple repeats
        in the same list and repeats across multiple lists by treating each occurrence independently.
        All repeats are included separately.

        Returns:
        --------
        List[Tuple[TKey, TValue]]
            A list of all key-value pairs in the dictionary.
        """
        key_value_pairs: List[Tuple[TKey, TValue]] = []
        for key, values in self.inner_values.items():
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
        return len(self.inner_values)

    @property
    def number_of_values(self) -> int:
        """
        Retrieves the total number of values in the dictionary.

        Returns:
        --------
        int
            The total number of values in the dictionary.
        """
        return sum(len(values) for values in self.inner_values.values())

    def __getitem__(self, key: TKey) -> List[TValue]:
        """
        Retrieves the list of values associated with the given key.

        Parameters:
        -----------
        key : TKey
            The key for which to retrieve values.

        Returns:
        --------
        List[TValue]
            The list of values associated with the key.
        """
        if key not in self.inner_values:
            self.inner_values[key] = []
        return self.inner_values[key]

    def __setitem__(self, key: TKey, value: List[TValue]):
        """
        Sets the list of values for the given key.

        Parameters:
        -----------
        key : TKey
            The key for which to set values.
        value : List[TValue]
            The list of values to set.
        """
        self.inner_values[key] = value
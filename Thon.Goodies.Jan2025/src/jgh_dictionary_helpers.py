from typing import Dict, Optional, TypeVar

T = TypeVar("T")

def filter_generic_dict_by_key(source_dict: Dict[str, T], keys_to_filter_by: Optional[list[str]]) -> Dict[str, T]:
        """
        Returns a dictionary containing only the items from `source_dict` whose keys are present in `keys_to_filter_by`.

        If `keys_to_filter_by` is None or empty, all items from `source_dict` are included.
        If a key in `keys_to_filter_by` does not exist in `source_dict`, it is skipped.

        Args:
            source_dict (Dict[str, T]): The source dictionary to filter.
            keys_to_filter_by (Optional[list[str]]): List of keys to include in the result. If None or empty, include all.

        Returns:
            Dict[str, T]: A dictionary containing only the requested items.
        """

        # If keys_to_filter_by is None or empty, return a shallow copy of the entire source_dict.
        if not keys_to_filter_by:
            return dict(source_dict)

        # Convert keys_to_filter_by to a set for fast O(1) membership checks.
        set_of_keys_to_filter_by = set(keys_to_filter_by)

        # Use dictionary comprehension for efficient filtering.
        # Only include keys that exist in source_dict.
        return {key: source_dict[key] for key in set_of_keys_to_filter_by if key in source_dict}


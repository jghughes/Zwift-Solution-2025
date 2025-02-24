"""
This module contains unit tests for the JghListDictionary class.
"""
# Standard library imports
import logging
import sys
import unittest

# Local application imports
from jgh_listdictionary import JghListDictionary
from jgh_logging import jgh_configure_logging

jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)

# Define the tests
class Test_JghListdictionary(unittest.TestCase):

    def setUp(self):

        logger.info(f"\nTEST NAME: {self._testMethodName}")
        logger.info(f"-"*100)
        # Print the docstring of the test method
        test_method = getattr(self, self._testMethodName)
        if test_method.__doc__:
            logger.info(f"TEST DOCSTRING:\n\t{test_method.__doc__.strip()}")
            logger.info(f"-"*100)

    def tearDown(self):
        logger.info(f"-"*100)
        logger.info(f"TEST FINISHED: {self._testMethodName}")
        logger.info(f"="*100)
        logger.info(f"\n")

    def test_empty_dictionary(self):
        """
        This test case creates an empty instance of JghListDictionary with str keys and str values,
        then asserts that both get_keys and get_key_value_pairs_from_everywhere return empty lists.
        """
        try:
            # Instantiate JghListDictionary with str keys and str values
            dictionary = JghListDictionary[str, str]()

            # Assert that get_keys returns an empty list
            self.assertEqual(dictionary.get_keys(), [])

            # Assert that get_key_value_pairs_from_everywhere returns an empty list
            self.assertEqual(dictionary.get_key_value_pairs_from_everywhere(), [])

            logger.info(f"TEST OUTCOME: PASS:\n\tThe dictionary is empty as expected.")
        except AssertionError as e:
            logger.error(
                f"FAIL. An assertion failed in test_empty_dictionary:-\n{e}"
            )
            raise

    def test_add_value(self):
        """
        This test case creates an instance of JghListDictionary with str keys and str values,
        adds a single value using append_value_to_key, and asserts that the count of occurrences
        of the value increases by one. It uses get_selected_values_from_key to count the occurrences
        of the value before and after adding it.
        """
        try:
            # Instantiate JghListDictionary with str keys and str values
            dictionary = JghListDictionary[str, str]()

            # Compose a value to append to a key
            key = "fruits"
            value = "apple"

             # Count occurences of value before adding it
            count_value_before = len( dictionary.get_selected_values_from_key(key, lambda v: v == value))

            # append the value to the dictionary
            dictionary.append_value_to_key(key, value)

            # Count occurences of value after adding it
            count_value_after = len( dictionary.get_selected_values_from_key(key, lambda v: v == value))

            # Assert that the results are equal
            self.assertEqual(count_value_after, (count_value_before + 1))

            logger.info(
                f"TEST OUTCOME: PASS:\n\tThe value was added successfully and the counts match. Count after adding ={count_value_after}"
            )
        except AssertionError as e:
            logger.error(f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_add_value:-\n\n{e}")
            raise

    def test_add_value_to_multiple_keys(self):
        """
        This test case creates an instance of JghListDictionary with str keys and str values,
        adds a single value using append_value_to_key, and then uses the same method to add
        the same value to a different key. It then calls get_keys_containing_value, logs the
        returned answer, and asserts that the keys match what was entered.
        """
        try:
            # Instantiate JghListDictionary with str keys and str values
            dictionary = JghListDictionary[str, str]()

            # Add a single value to the dictionary under two different keys
            value = "apple"
            key1 = "fruits"
            key2 = "snacks"
            dictionary.append_value_to_key(key1, value)
            dictionary.append_value_to_key(key2, value)

            # Get the keys containing the value
            keys_containing_value = dictionary.get_keys_containing_value(value)

            # Assert that the keys match what was entered
            self.assertIn(key1, keys_containing_value)
            self.assertIn(key2, keys_containing_value)

            logger.info(
                f"TEST OUTCOME: PASS:\n\tThe value '{value}' was added to keys '{key1}' and '{key2}'.\n\tKeys containing the value: {keys_containing_value}."
            )
        except AssertionError as e:
            logger.error(
                f"FAIL. An assertion failed in test_add_value_to_multiple_keys:-\n{e}")
            raise

    def test_remove_values_from_everywhere(self):
        """
        This test case creates an instance of JghListDictionary with str keys and str values,
        adds a single value using append_value_to_key to two different keys, removes the value
        using remove_value_from_all_keys, and then asserts that the value is no longer
        present in the dictionary by calling get_values_for_all.
        """
        try:
            # Instantiate JghListDictionary with str keys and str values
            dictionary = JghListDictionary[str, str]()

            # Add a single value to the dictionary under two different keys
            value = "apple"
            key1 = "fruits"
            key2 = "snacks"
            dictionary.append_value_to_key(key1, value)
            dictionary.append_value_to_key(key2, value)

            # Get the keys containing the value
            keys_containing_value = dictionary.get_keys_containing_value(value)

            # Remove the value from everywhere in the dictionary and get the count of removed occurrences and the list of keys
            removed_count, keys_with_removed_value = dictionary.remove_value_from_all_keys(value)

            # Get all values from everywhere in the dictionary
            all_values = dictionary.get_values_for_all()

            # Assert that the value is no longer present in the dictionary
            self.assertNotIn(value, all_values)

            logger.info(
                f"TEST OUTCOME: PASS:\n\tThe value '{value}' was added to keys '{key1}' and '{key2}'.\n\tKeys containing the value: {keys_containing_value}\n\tThe value '{value}' was removed from all keys.\n\tNumber of occurrences removed: {removed_count}\n\tKeys from which the value was removed: {keys_with_removed_value}\n\tRemaining values: {all_values}"
            )
        except AssertionError as e:
            logger.error(
                f"FAIL. An assertion failed in test_remove_values_from_everywhere:-\n{e}")
            raise

    def test_get_keys_containing_selected_values(self):
        """
        This test case creates an instance of JghListDictionary with str keys and str values,
        adds values using append_value_to_key to multiple keys, and then uses
        get_keys_containing_selected_values to determine which keys contain a value
        starting with "b".
        """
        try:
            # Instantiate JghListDictionary with str keys and str values
            dictionary = JghListDictionary[str, str]()

            # Add values to the dictionary under two different keys
            value1 = "apple"
            value2 = "banana"
            key1 = "fruits"
            key2 = "snacks"
            dictionary.append_value_to_key(key1, value1)
            dictionary.append_value_to_key(key2, value1)
            dictionary.append_value_to_key(key2, value2)

            # Log the created keys and values
            logger.info(f"\tCreated keys and values: {dictionary.backingstore_dict}")

            # Get the keys containing values that start with "b"
            keys_with_b_values = dictionary.get_keys_containing_selected_values(
                lambda v: v.startswith("b")
            )

            # Log the keys containing values that start with "b"
            logger.info(
                f"\tKeys containing values starting with 'b': {keys_with_b_values}"
            )

            # Assert that key2 is in the list of keys containing values starting with "b"
            self.assertIn(key2, keys_with_b_values)

            logger.info(
                f"TEST OUTCOME: PASS:\n\tThe keys containing values starting with 'b' were identified correctly."
            )
        except AssertionError as e:
            logger.error(
                f"FAIL. An assertion failed in test_get_keys_containing_selected_values:-\n{e}")
            raise

    def test_get_key_value_pairs_containing_selected_values(self):
        """
        This test case creates an instance of JghListDictionary with str keys and str values,
        adds values using append_value_to_key to multiple keys, and then uses
        get_key_value_pairs_containing_selected_values to determine which key-value pairs
        contain a value starting with "b".
        """
        try:
            # Instantiate JghListDictionary with str keys and str values
            dictionary = JghListDictionary[str, str]()

            # Add values to the dictionary under two different keys
            value1 = "apple"
            value2 = "banana"
            key1 = "fruits"
            key2 = "snacks"
            dictionary.append_value_to_key(key1, value1)
            dictionary.append_value_to_key(key2, value1)
            dictionary.append_value_to_key(key2, value2)

            # Log the created keys and values
            logger.info(f"\tCreated keys and values: {dictionary.backingstore_dict}")

            # Get the key-value pairs containing values that start with "b"
            key_value_pairs_with_b_values = (
                dictionary.get_key_value_pairs_containing_selected_values(
                    lambda v: v.startswith("b")
                )
            )

            # Log the key-value pairs containing values that start with "b"
            logger.info(
                f"\tKey-value pairs containing values starting with 'b': {key_value_pairs_with_b_values}"
            )

            # Assert that the key-value pair (key2, value2) is in the list of key-value pairs containing values starting with "b"
            self.assertIn((key2, value2), key_value_pairs_with_b_values)

            logger.info(
                f"TEST OUTCOME: PASS:\n\tThe key-value pairs containing values starting with 'b' were identified correctly."
            )
        except AssertionError as e:
            logger.error(
                f"FAIL. An assertion failed in test_get_key_value_pairs_containing_selected_values:-\n{e}")
            raise

    def test_clear_everything_everywhere(self):
        """
        This test case creates an instance of JghListDictionary with str keys and str values,
        adds values using append_value_to_key to multiple keys, clears all entries using
        clear_everything_everywhere, and asserts that the dictionary is empty. It also logs
        the original number of keys and values before clearing.
        """
        try:
            # Instantiate JghListDictionary with str keys and str values
            dictionary = JghListDictionary[str, str]()

            # Add values to the dictionary under multiple keys
            dictionary.append_value_to_key("fruits", "apple")
            dictionary.append_value_to_key("fruits", "banana")
            dictionary.append_value_to_key("vegetables", "carrot")
            dictionary.append_value_to_key("vegetables", "broccoli")

            # Clear all entries in the dictionary and get the original counts
            original_keys_count, original_values_count = dictionary.clear_everything_everywhere()

            # Assert that the dictionary is empty
            self.assertEqual(dictionary.get_keys(), [])
            self.assertEqual(dictionary.get_key_value_pairs_from_everywhere(), [])

            logger.info(
                f"TEST OUTCOME: PASS:\n\tThe dictionary was cleared successfully.\n\tOriginal number of keys: {original_keys_count}\n\tOriginal number of values: {original_values_count}"
            )
        except AssertionError as e:
            logger.error(
                f"FAIL. An assertion failed in test_clear_everything_everywhere:-\n{e}")
            raise

# Run the tests
if __name__ == "__main__":
    print("sys.path (in alphabetical order):-")
    for path in sorted(sys.path):
        print(f" - {path}")
    print(
        "\nExplanation:\n\tThe above paths are where Python will look to find modules and imports\n\treferenced in this file. If imports fail to resolve, it is because of\n\tincorrect paths. In a Visual Studio 2022 project, right-click\n\tthe 'Search Paths' node to add a path."
    )

    unittest.main()

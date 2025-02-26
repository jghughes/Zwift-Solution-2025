"""
This module contains unit tests for the PersonDto class.
"""
# Sys library import
import sys

# Check the paths for the module     
print("sys.path (in alphabetical order):-")
for path in sorted(sys.path):
    print(f" - {path}")
print("\nExplanation:\n\tThe above paths are where Python will look to find modules and imports\n\treferenced in this file. If imports fail to resolve, it is because of\n\tincorrect paths. In a Visual Studio 2022 project, right-click\n\tthe 'Search Paths' node to add a path.")

# Standard library imports
import os
import unittest
import logging

# Local application imports
from jgh_logging import jgh_configure_logging
from jgh_serialization import JghSerialization
from person_dto import PersonDataTransferObject

# Set a custom BASE_DIR environment variable 
# This is required to be known inside jgh_configure_logging() to locate the appsettings file and the log file
os.environ['BASE_DIR'] = 'C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun.DataTransferObjects.Jan2024'

# Configure logging
jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)


# Define the tests
class Test_PersonDto(unittest.TestCase):
    """
    Unit tests for the PersonDto class.
    """

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

    def test_01serialization(self):
        """
        This test will check if the serialization process can correctly convert
        a PersonDto object to a JSON string. It will ensure that all fields are
        included in the JSON string and that the values are correctly serialized.
        """

        try:
            # Create an instance of PersonDto
            test_instance = PersonDataTransferObject(
                zsun_id="456",
                zsun_firstname="John",
                zsun_lastname="Doe",
                zwift_id=789,
                zwift_firstname="Jane",
                zwift_lastname="Doe",
                discord_accountusername="john_doe",
                discord_accountdisplayname="JohnDoe",
                discord_profiledisplayname="JohnDoeProfile",
                comment="Test comment",
                click_counter=10,
                recording_mode_enum="mode1",
                database_action_enum="action1",
                must_ditch_originating_item=True,
                is_still_to_be_backed_up=False,
                is_still_to_be_pushed=True,
                touched_by="tester",
                timestamp_binary_format=1633036800,
                when_touched_binary_format=1633036800,
                when_pushed_binary_format=1633036800,
                originating_item_guid="origin_guid",
                guid="test_guid",
            )
            # Serialize to JSON
            json_str = JghSerialization.serialise(test_instance)
            self.assertIsInstance(json_str, str)
            self.assertIn('"zsun_id": "456"', json_str)
            self.assertIn('"zsun_firstname": "John"', json_str)
            self.assertIn('"zsun_lastname": "Doe"', json_str)
            self.assertIn('"zwift_id": 789', json_str)
            self.assertIn('"zwift_firstname": "Jane"', json_str)
            self.assertIn('"zwift_lastname": "Doe"', json_str)
            self.assertIn('"discord_accountusername": "john_doe"', json_str)
            self.assertIn('"discord_accountdisplayname": "JohnDoe"', json_str)
            self.assertIn('"discord_profiledisplayname": "JohnDoeProfile"', json_str)
            self.assertIn('"comment": "Test comment"', json_str)
            self.assertIn('"click_counter": 10', json_str)
            self.assertIn('"recording_mode_enum": "mode1"', json_str)
            self.assertIn('"database_action_enum": "action1"', json_str)
            self.assertIn('"must_ditch_originating_item": true', json_str)
            self.assertIn('"is_still_to_be_backed_up": false', json_str)
            self.assertIn('"is_still_to_be_pushed": true', json_str)
            self.assertIn('"touched_by": "tester"', json_str)
            self.assertIn('"timestamp_binary_format": 1633036800', json_str)
            self.assertIn('"when_touched_binary_format": 1633036800', json_str)
            self.assertIn('"when_pushed_binary_format": 1633036800', json_str)
            self.assertIn('"originating_item_guid": "origin_guid"', json_str)
            self.assertIn('"guid": "test_guid"', json_str)
            logger.info(
                f"TEST OUTCOME: PASS:\n\tSerialization succeeded.\n\tThe JSON generated was:\n\t{json_str}"
            )
        except AssertionError as e:
            logger.error(f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_serialization:-\n{e}")
            raise

    def test_02deserialization(self):
        """
        This test will check if the deserialization process can correctly convert
        a JSON string to a PersonDto object. It will ensure that all fields are
        included in the object and that the values are correctly deserialized.
        """

        try:
            # Define a JSON string to validly represent an instance of PersonDto
            valid_test_json_str = """
            {
                "zsun_id": "456",
                "zsun_firstname": "John",
                "zsun_lastname": "Doe",
                "zwift_id": 789,
                "zwift_firstname": "Jane",
                "zwift_lastname": "Doe",
                "discord_accountusername": "john_doe",
                "discord_accountdisplayname": "JohnDoe",
                "discord_profiledisplayname": "JohnDoeProfile",
                "comment": "Test comment",
                "click_counter": 10,
                "recording_mode_enum": "mode1",
                "database_action_enum": "action1",
                "must_ditch_originating_item": true,
                "is_still_to_be_backed_up": false,
                "is_still_to_be_pushed": true,
                "touched_by": "tester",
                "timestamp_binary_format": 1633036800,
                "when_touched_binary_format": 1633036800,
                "when_pushed_binary_format": 1633036800,
                "originating_item_guid": "origin_guid",
                "guid": "test_guid"
            }
            """
            # Deserialize to object
            dto = JghSerialization.validate(valid_test_json_str, PersonDataTransferObject)
            self.assertIsInstance(dto, PersonDataTransferObject)
            self.assertEqual(dto.zsun_id, "456")
            self.assertEqual(dto.zsun_firstname, "John")
            self.assertEqual(dto.zsun_lastname, "Doe")
            self.assertEqual(dto.zwift_id, 789)
            self.assertEqual(dto.zwift_firstname, "Jane")
            self.assertEqual(dto.zwift_lastname, "Doe")
            self.assertEqual(dto.discord_accountusername, "john_doe")
            self.assertEqual(dto.discord_accountdisplayname, "JohnDoe")
            self.assertEqual(dto.discord_profiledisplayname, "JohnDoeProfile")
            self.assertEqual(dto.comment, "Test comment")
            self.assertEqual(dto.click_counter, 10)
            self.assertEqual(dto.recording_mode_enum, "mode1")
            self.assertEqual(dto.database_action_enum, "action1")
            self.assertTrue(dto.must_ditch_originating_item)
            self.assertFalse(dto.is_still_to_be_backed_up)
            self.assertTrue(dto.is_still_to_be_pushed)
            self.assertEqual(dto.touched_by, "tester")
            self.assertEqual(dto.timestamp_binary_format, 1633036800)
            self.assertEqual(dto.when_touched_binary_format, 1633036800)
            self.assertEqual(dto.when_pushed_binary_format, 1633036800)
            self.assertEqual(dto.originating_item_guid, "origin_guid")
            self.assertEqual(dto.guid, "test_guid")
            logger.info(
                f"TEST OUTCOME: PASS:\n\tDeserialization succeeded.\n\tThe object generated was:\n\t{dto}"
            )
        except AssertionError as e:
            logger.error(f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_deserialization:-\n\n{e}")
            raise

    def test_03round_trip(self):
        """
        This test will check if the serialization and deserialization processes
        can correctly convert a PersonDto object to a JSON string and back to a
        PersonDto object. It will ensure that the object remains unchanged after
        a round-trip conversion.
        """
  
        try:
            # Create an instance of PersonDto
            test_instance = PersonDataTransferObject(
                zsun_id="456",
                zsun_firstname="John",
                zsun_lastname="Doe",
                zwift_id=789,
                zwift_firstname="Jane",
                zwift_lastname="Doe",
                discord_accountusername="john_doe",
                discord_accountdisplayname="JohnDoe",
                discord_profiledisplayname="JohnDoeProfile",
                comment="Test comment",
                click_counter=10,
                recording_mode_enum="mode1",
                database_action_enum="action1",
                must_ditch_originating_item=True,
                is_still_to_be_backed_up=False,
                is_still_to_be_pushed=True,
                touched_by="tester",
                timestamp_binary_format=1633036800,
                when_touched_binary_format=1633036800,
                when_pushed_binary_format=1633036800,
                originating_item_guid="origin_guid",
                guid="test_guid",
            )
            # Serialize to JSON
            json_str = JghSerialization.serialise(test_instance)
            # Deserialize back to object
            test_instance_roundtripped = JghSerialization.validate(
                json_str, PersonDataTransferObject
            )
            self.assertEqual(test_instance, test_instance_roundtripped)
            logger.info(f"TEST OUTCOME: PASS:\n\tRound-trip succeeded.\n\tThe JSON generated was:\n\t{json_str}")
            logger.info(f"\n\tThe object generated was:\n\t{test_instance_roundtripped}")
        except AssertionError as e:
            logger.error(f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_round_trip:-\n\n{e}")
            raise

    def test_04deserialization_with_missing_and_superfluous_fields(self):
        """
        This test will check if the deserialization process can handle a JSON
        string with missing fields and superfluous fields. It will ensure that
        the PersonDto object is created correctly with the provided fields and
        that the missing fields are set to their default values.
        """
        try:
            # Define a JSON string with missing fields and superfluous fields
            invalid_test_json_str = """
            {
                "zsun_id": "456",
                "zsun_firstname": "John",
                "superfluous_field": "extra_value",
                "another_extra_field": 12345
            }
            """
            # Deserialize to object
            dto = JghSerialization.validate(invalid_test_json_str, PersonDataTransferObject)
            self.assertIsInstance(dto, PersonDataTransferObject)
            self.assertEqual(dto.zsun_id, "456")
            self.assertEqual(dto.zsun_firstname, "John")
            self.assertEqual(dto.zsun_lastname, "")
            self.assertEqual(dto.zwift_id, 0)
            self.assertEqual(dto.zwift_firstname, "")
            self.assertEqual(dto.zwift_lastname, "")
            self.assertEqual(dto.discord_accountusername, "")
            self.assertEqual(dto.discord_accountdisplayname, "")
            self.assertEqual(dto.discord_profiledisplayname, "")
            self.assertEqual(dto.comment, "")
            self.assertEqual(dto.click_counter, 0)
            self.assertEqual(dto.recording_mode_enum, "")
            self.assertEqual(dto.database_action_enum, "")
            self.assertFalse(dto.must_ditch_originating_item)
            self.assertTrue(dto.is_still_to_be_backed_up)
            self.assertTrue(dto.is_still_to_be_pushed)
            self.assertEqual(dto.touched_by, "")
            self.assertEqual(dto.timestamp_binary_format , 0)
            self.assertEqual(dto.when_touched_binary_format, 0)
            self.assertEqual(dto.when_pushed_binary_format, 0)
            self.assertEqual(dto.originating_item_guid, "")
            self.assertEqual(dto.guid, "")
            logger.info(
                f"TEST OUTCOME: PASS:\n\tDeserialization with missing and superfluous fields succeeded.\n\tThe object generated was:\n\t{dto}")
        except AssertionError as e:
            logger.error(
                f"FAIL. An assertion failed in test_deserialization_with_missing_and_superfluous_fields:-\n\n{e}")
            raise

    def test_05deserialization_with_coercible_int_and_bool_types(self):
        """
        This test will check if the deserialization process can handle JSON
        strings with invalid types, particularly if Pydantic successfully coerces 
        string values into likely integers and bools.
        """
        try:
            # Define a JSON string with invalid types (strings instead of integers and floats)
            invalid_types_json_str = """
            {
                "zsun_id": "456",
                "zsun_firstname": "John",
                "zsun_lastname": "Doe",
                "zwift_id": "789",
                "zwift_firstname": "Jane",
                "zwift_lastname": "Doe",
                "discord_accountusername": "john_doe",
                "discord_accountdisplayname": "JohnDoe",
                "discord_profiledisplayname": "JohnDoeProfile",
                "comment": "Test comment",
                "click_counter": "10",
                "recording_mode_enum": "mode1",
                "database_action_enum": "action1",
                "must_ditch_originating_item": "true",
                "is_still_to_be_backed_up": "false",
                "is_still_to_be_pushed": "true",
                "touched_by": "tester",
                "timestamp_binary_format": "1633036800",
                "when_touched_binary_format": "1633036800",
                "when_pushed_binary_format": "1633036800",
                "originating_item_guid": "origin_guid",
                "guid": "test_guid"
            }
            """
            # Deserialize to object
            dto = JghSerialization.validate(invalid_types_json_str, PersonDataTransferObject)
            self.assertIsInstance(dto, PersonDataTransferObject)
            self.assertEqual(dto.zsun_id, "456")
            self.assertEqual(dto.zsun_firstname, "John")
            self.assertEqual(dto.zsun_lastname, "Doe")
            self.assertEqual(dto.zwift_id, 789)  # Coerced to integer
            self.assertEqual(dto.zwift_firstname, "Jane")
            self.assertEqual(dto.zwift_lastname, "Doe")
            self.assertEqual(dto.discord_accountusername, "john_doe")
            self.assertEqual(dto.discord_accountdisplayname, "JohnDoe")
            self.assertEqual(dto.discord_profiledisplayname, "JohnDoeProfile")
            self.assertEqual(dto.comment, "Test comment")
            self.assertEqual(dto.click_counter, 10)  # Coerced to integer
            self.assertEqual(dto.recording_mode_enum, "mode1")
            self.assertEqual(dto.database_action_enum, "action1")
            self.assertTrue(dto.must_ditch_originating_item)  # Coerced to boolean
            self.assertFalse(dto.is_still_to_be_backed_up)  # Coerced to boolean
            self.assertTrue(dto.is_still_to_be_pushed)  # Coerced to boolean
            self.assertEqual(dto.touched_by, "tester")
            self.assertEqual(dto.timestamp_binary_format, 1633036800)  # Coerced to integer
            self.assertEqual(dto.when_touched_binary_format, 1633036800)  # Coerced to integer
            self.assertEqual(dto.when_pushed_binary_format, 1633036800)  # Coerced to integer
            self.assertEqual(dto.originating_item_guid, "origin_guid")
            self.assertEqual(dto.guid, "test_guid")
            logger.info(
                f"TEST OUTCOME: PASS:\n\tDeserialization with invalid types succeeded.\n\tThe object generated was:\n\t{dto}"
            )
        except AssertionError as e:
            logger.error(
                f"FAIL. An assertion failed in test_deserialization_with_invalid_types:-\n\n{e}"
            )
            raise

# Run the tests
if __name__ == "__main__":
    print("sys.path (in alphabetical order):-")
    for path in sorted(sys.path):
        print(f" - {path}")
    print("\nExplanation:\n\tThe above paths are where Python will look to find modules and imports\n\treferenced in this file. If imports fail to resolve, it is because of\n\tincorrect paths. In a Visual Studio 2022 project, right-click\n\tthe 'Search Paths' node to add a path.")

    unittest.main()


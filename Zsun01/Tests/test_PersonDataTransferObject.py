import unittest
import logging
import sys
import os

from PersonDataClass import PersonDataTransferObject
from JghSerialization import JghSerialization

# Get the directory of the current file
current_file_dir = os.path.dirname(__file__)
# Get the parent directory of the current file directory
parent_dir = os.path.abspath(os.path.join(current_file_dir, os.path.pardir))

# Add the parent directory to the path list just in case it's ever needed
# sys.path.append(parent_dir)
# Add the sibling folders to the path list
list_of_sibling_folders = ['','utilities', 'classes', 'repositories']

for folder in list_of_sibling_folders:
    folder_dir = os.path.abspath(os.path.join(parent_dir, folder))
    sys.path.append(folder_dir)




# Print sys.path list to verify, sorted in alphabetical order
print("sys.path (sorted):")
for path in sorted(sys.path):
    if path.startswith(parent_dir):
        print(f"  Program path: {path}")
    else:
        print(f"  Local path: {path}")

# Check if the files exist at the specified paths
person_data_class_exists = os.path.exists(os.path.join(classes_dir, 'PersonDataClass.py'))
jgh_serialization_exists = os.path.exists(os.path.join(utilities_dir, 'JghSerialization.py'))

if person_data_class_exists:
    print("PersonDataClass.py exists: True")
else:
    print("PersonDataClass.py exists: False")

if jgh_serialization_exists:
    print("JghSerialization.py exists: True")
else:
    print("JghSerialization.py exists: False")

# Import the modules if they exist
try:
    if person_data_class_exists:
        from PersonDataClass import PersonDataTransferObject
    else:
        raise ImportError("PersonDataClass.py does not exist.")
except ImportError as e:
    print(f"Error importing PersonDataClass: {e}")

try:
    if jgh_serialization_exists:
        from JghSerialization import JghSerialization
    else:
        raise ImportError("JghSerialization.py does not exist.")
except ImportError as e:
    print(f"Error importing JghSerialization: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class TestPersonDataTransferObject(unittest.TestCase):

    def setUp(self):
        logger.info("\n")
        # logger.info("\n" + "="*50)
        logger.info("TEST: %s", self._testMethodName)
        logger.info("-"*90)

    def tearDown(self):
        logger.info("-"*90)
        logger.info("FINISHED: %s", self._testMethodName)
        logger.info("="*90)
        logger.info("\n\n")

    def test_serialization(self):
        try:
            # Create an instance of PersonDataTransferObject
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
                click_counter="10",
                recording_mode_enum="mode1",
                database_action_enum="action1",
                must_ditch_originating_item=True,
                is_still_to_be_backed_up=False,
                is_still_to_be_pushed=True,
                touched_by="tester",
                timestamp=1633036800.0,
                when_touched=1633036800.0,
                when_pushed=1633036800.0,
                originating_item_guid="origin_guid",
                guid="test_guid"
            )
            # Serialize to JSON
            json_str = JghSerialization.to_json_from_object(test_instance)
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
            self.assertIn('"click_counter": "10"', json_str)
            self.assertIn('"recording_mode_enum": "mode1"', json_str)
            self.assertIn('"database_action_enum": "action1"', json_str)
            self.assertIn('"must_ditch_originating_item": true', json_str)
            self.assertIn('"is_still_to_be_backed_up": false', json_str)
            self.assertIn('"is_still_to_be_pushed": true', json_str)
            self.assertIn('"touched_by": "tester"', json_str)
            self.assertIn('"timestamp": 1633036800.0', json_str)
            self.assertIn('"when_touched": 1633036800.0', json_str)
            self.assertIn('"when_pushed": 1633036800.0', json_str)
            self.assertIn('"originating_item_guid": "origin_guid"', json_str)
            self.assertIn('"guid": "test_guid"', json_str)
            logger.info("PASS. Serialization succeeded. The JSON generated was:\n%s", json_str)
        except AssertionError as e:
            logger.error("FAIL. An assertion failed in test_serialization:-\n\n%s", e)
            raise

    def test_deserialization(self):
        try:
            # Define a JSON string to validly represent an instance of PersonDataTransferObject
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
                "click_counter": "10",
                "recording_mode_enum": "mode1",
                "database_action_enum": "action1",
                "must_ditch_originating_item": true,
                "is_still_to_be_backed_up": false,
                "is_still_to_be_pushed": true,
                "touched_by": "tester",
                "timestamp": 1633036800.0,
                "when_touched": 1633036800.0,
                "when_pushed": 1633036800.0,
                "originating_item_guid": "origin_guid",
                "guid": "test_guid"
            }
            """
            # Deserialize to object
            dto = JghSerialization.to_object_from_json(valid_test_json_str, PersonDataTransferObject)
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
            self.assertEqual(dto.click_counter, "10")
            self.assertEqual(dto.recording_mode_enum, "mode1")
            self.assertEqual(dto.database_action_enum, "action1")
            self.assertTrue(dto.must_ditch_originating_item)
            self.assertFalse(dto.is_still_to_be_backed_up)
            self.assertTrue(dto.is_still_to_be_pushed)
            self.assertEqual(dto.touched_by, "tester")
            self.assertEqual(dto.timestamp, 1633036800.0)
            self.assertEqual(dto.when_touched, 1633036800.0)
            self.assertEqual(dto.when_pushed, 1633036800.0)
            self.assertEqual(dto.originating_item_guid, "origin_guid")
            self.assertEqual(dto.guid, "test_guid")
            logger.info("PASS. Deserialization succeeded. The object generated was:\n%s", dto)
        except AssertionError as e:
            logger.error("FAIL. An assertion failed in test_deserialization:-\n\n%s", e)
            raise

    def test_round_trip(self):
        try:
            # Create an instance of PersonDataTransferObject
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
                click_counter="10",
                recording_mode_enum="mode1",
                database_action_enum="action1",
                must_ditch_originating_item=True,
                is_still_to_be_backed_up=False,
                is_still_to_be_pushed=True,
                touched_by="tester",
                timestamp=1633036800.0,
                when_touched=1633036800.0,
                when_pushed=1633036800.0,
                originating_item_guid="origin_guid",
                guid="test_guid"
            )
            # Serialize to JSON
            json_str = JghSerialization.to_json_from_object(test_instance)
            # Deserialize back to object
            test_instance_roundtripped = JghSerialization.to_object_from_json(json_str, PersonDataTransferObject)
            self.assertEqual(test_instance, test_instance_roundtripped)
            logger.info("PASS. Round-trip succeeded. The JSON generated was:\n%s", json_str)
            logger.info("The object generated was:\n%s", test_instance_roundtripped)
        except AssertionError as e:
            logger.error("FAIL. An assertion failed in test_round_trip:-\n\n%s", e)
            raise

if __name__ == '__main__':
    unittest.main()


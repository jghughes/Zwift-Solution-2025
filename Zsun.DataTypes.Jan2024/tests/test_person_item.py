"""
This module contains unit tests for the PersonItem class.
"""
# Sys library import
import sys

# Check the paths for the module     
print("sys.path (in alphabetical order):-")
for path in sorted(sys.path):
    print(f" - {path}")
print("\nExplanation:\n\tThe above paths are where Python will look to find modules and imports\n\treferenced in this file. If imports fail to resolve, it is because of\n\tincorrect paths. In a Visual Studio 2022 project, right-click\n\tthe 'Search Paths' node to add a path.")

# Standard library imports
import logging
import unittest

# Local application imports
from person_dto import PersonDto
from person_item import PersonItem

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Define the tests
class Test_PersonItem(unittest.TestCase):

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

    def test_create(self):
        """
        This test case creates an instance of PersonItem with specified attributes,
        then asserts that the created object has the expected attribute values.
        """
        try:
            item = PersonItem.create(
                zwift_id=123,
                discord_accountusername="test_user",
                recording_mode_enum="mode1",
                touched_by="tester"
            )
            self.assertIsInstance(item, PersonItem)
            self.assertEqual(item.zwift_id, 123)
            self.assertEqual(item.discord_accountusername, "test_user")
            self.assertEqual(item.recording_mode_enum, "mode1")
            self.assertEqual(item.touched_by, "tester")
            logger.info(f"TEST OUTCOME: PASS:\n\tThe object created was:-\n\n{item}")
        except AssertionError as e:
            logger.error(f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_create:-\n\n{e}")
            raise

    def test_to_dataTransferObject(self):
        """
        This test case creates an instance of PersonItem with specified attributes,
        converts it to a PersonDto object using the to_dataTransferObject method,
        and then asserts that the converted object has the expected attribute values.
        """
        try:
            item = PersonItem.create(
                zwift_id=123,
                discord_accountusername="test_user",
                recording_mode_enum="mode1",
                touched_by="tester"
            )
            dto = PersonItem.to_dataTransferObject(item)
            self.assertIsInstance(dto, PersonDto)
            self.assertEqual(dto.zwift_id, 123)
            self.assertEqual(dto.discord_accountusername, "test_user")
            self.assertEqual(dto.recording_mode_enum, "mode1")
            self.assertEqual(dto.touched_by, "tester")
            logger.info(f"TEST OUTCOME: PASS:\n\tThe input object was:-\n{item}")
            logger.info(f"\n\tThe output object generated was:-\n{dto}")
        except AssertionError as e:
            logger.error(f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_to_dataTransferObject:-\n\n{e}")
            raise

    def test_from_dataTransferObject(self):
        """
        This test case creates an instance of PersonDto with specified attributes,
        converts it to a PersonItem object using the from_dataTransferObject method,
        and then asserts that the converted object has the expected attribute values.
        """
        try:
            dto = PersonDto(
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
            item = PersonItem.from_dataTransferObject(dto)
            self.assertIsInstance(item, PersonItem)
            self.assertEqual(item.zsun_id, "456")
            self.assertEqual(item.zsun_firstname, "John")
            self.assertEqual(item.zsun_lastname, "Doe")
            self.assertEqual(item.zwift_id, 789)
            self.assertEqual(item.zwift_firstname, "Jane")
            self.assertEqual(item.zwift_lastname, "Doe")
            self.assertEqual(item.discord_accountusername, "john_doe")
            self.assertEqual(item.discord_accountdisplayname, "JohnDoe")
            self.assertEqual(item.discord_profiledisplayname, "JohnDoeProfile")
            self.assertEqual(item.comment, "Test comment")
            self.assertEqual(item.click_counter, "10")
            self.assertEqual(item.recording_mode_enum, "mode1")
            self.assertEqual(item.database_action_enum, "action1")
            self.assertTrue(item.must_ditch_originating_item)
            self.assertFalse(item.is_still_to_be_backed_up)
            self.assertTrue(item.is_still_to_be_pushed)
            self.assertEqual(item.touched_by, "tester")
            self.assertEqual(item.timestamp, 1633036800.0)
            self.assertEqual(item.when_touched, 1633036800.0)
            self.assertEqual(item.when_pushed, 1633036800.0)
            self.assertEqual(item.originating_item_guid, "origin_guid")
            self.assertEqual(item.guid, "test_guid")
            logger.info(f"TEST OUTCOME: PASS:\n\tThe input object was:-\n{dto}")
            logger.info(f"\n\tThe output object generated was:-\n{item}")
        except AssertionError as e:
            logger.error(f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_from_dataTransferObject:-\n\n{e}")
            raise

    def test_get_both_guids(self):
        """
        This test case creates an instance of PersonItem with specified attributes,
        sets the originating_item_guid attribute, retrieves both GUIDs using the
        get_both_guids method, and then asserts that both GUIDs are there.
        """
        try:
            item = PersonItem.create(
                zwift_id=123,
                discord_accountusername="test_user",
                recording_mode_enum="mode1",
                touched_by="tester"
            )
            item.originating_item_guid = "origin_guid"
            both_guids = item.get_both_guids()
            self.assertIn("origin_guid", both_guids)
            self.assertIn(item.guid, both_guids)
            logger.info(f"TEST OUTCOME: PASS:\n\tThe input object used was:-\n{item}")
            logger.info(f"\n\tBoth guids were:- '{both_guids}'")
        except AssertionError as e:
            logger.error(f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_get_both_guids:-\n\n{e}")
            raise

#    Run the tests
if __name__ == '__main__':
    print("sys.path (in alphabetical order):-")
    for path in sorted(sys.path):
        print(f" - {path}")
    print("\nExplanation:\n\tThe above paths are where Python will look to find modules and imports\n\treferenced in this file. If imports fail to resolve, it is because of\n\tincorrect paths. In a Visual Studio 2022 project, right-click\n\tthe 'Search Paths' node to add a path.")
    
    unittest.main()


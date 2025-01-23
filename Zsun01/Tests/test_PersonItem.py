import unittest
import logging
from PersonItem import PersonItem
from ClubMemberDataClass import PersonDataTransferObject

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class Test_PersonItem(unittest.TestCase):

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

    def test_create(self):
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
            logger.info("PASS. The object created was:-\n\n%s", item)
        except AssertionError as e:
            logger.error("FAIL. An assertion failed in test_create:-\n\n%s", e)
            raise

    def test_to_dataTransferObject(self):
        try:
            item = PersonItem.create(
                zwift_id=123,
                discord_accountusername="test_user",
                recording_mode_enum="mode1",
                touched_by="tester"
            )
            dto = PersonItem.to_dataTransferObject(item)
            self.assertIsInstance(dto, PersonDataTransferObject)
            self.assertEqual(dto.zwift_id, 123)
            self.assertEqual(dto.discord_accountusername, "test_user")
            self.assertEqual(dto.recording_mode_enum, "mode1")
            self.assertEqual(dto.touched_by, "tester")
            logger.info("PASS. The input object was:-\n\n%s", item)
            logger.info("\nThe output object generated was:-\n\n%s", dto)
        except AssertionError as e:
            logger.error("FAIL. An assertion failed in test_to_dataTransferObject:-\n\n%s", e)
            raise

    def test_from_dataTransferObject(self):
        try:
            dto = PersonDataTransferObject(
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
            logger.info("PASS. The input object was:-\n\n%s", dto)
            logger.info("\nThe output object generated was:-\n\n%s", item)
        except AssertionError as e:
            logger.error("FAIL. An assertion failed in test_from_dataTransferObject:-\n\n%s", e)
            raise

    def test_get_both_guids(self):
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
            logger.info("PASS. The input object used was:-\n\n%s", item)
            logger.info("\nBoth guids were:-\n\n%s", both_guids)
        except AssertionError as e:
            logger.error("FAIL. An assertion failed in test_get_both_guids:-\n\n%s", e)
            raise


if __name__ == '__main__':
    unittest.main()


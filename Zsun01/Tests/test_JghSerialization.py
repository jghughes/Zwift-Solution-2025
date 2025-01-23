import os
import unittest
import logging
from typing import TypeVar, Optional
import pydantic as pydantic
import sys
# Verify the sys.path
print("sys.path:", sys.path)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utilities')))
from JghSerialization import JghSerialization

T = TypeVar('T', bound=pydantic.BaseModel)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Define a Pydantic model for testing
class TestModel(pydantic.BaseModel):
    id: int
    name: Optional[str] = None

class Test_test_JghSerialization(unittest.TestCase):

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

    def test_to_json_from_object(self):
        try:
            # Create an instance of TestModel
            test_instance = TestModel(id=1, name="Test")
            # Serialize to JSON
            json_str = JghSerialization.to_json_from_object(test_instance)
            self.assertIsInstance(json_str, str)
            self.assertIn('"id": 1', json_str)
            self.assertIn('"name": "Test"', json_str)
            logger.info("PASS: Serialization succeeded. The JSON generated was:-\n\n%s", json_str)
        except AssertionError as e:
            logger.error("FAIL. An assertion failed in test_to_json_from_object:-\n\n%s", e)
            raise

    def test_to_object_from_json(self):
        try:
            # Valid JSON string
            valid_json = '{"id": 1, "name": "Test"}'
            obj = JghSerialization.to_object_from_json(valid_json, TestModel)
            self.assertIsInstance(obj, TestModel)
            self.assertEqual(obj.id, 1)
            self.assertEqual(obj.name, "Test")
            logger.info("PASS: Deserialization succeeded. The object generated was:-\n\n%s", obj)
        except AssertionError as e:
            logger.error("FAIL. An assertion failed in test_to_object_from_json:-\n\n%s", e)
            raise

    def test_to_object_from_json_with_missing_fields(self):
        try:
            # JSON string with missing fields
            missing_fields_json = '{"id": 1}'
            obj = JghSerialization.to_object_from_json(missing_fields_json, TestModel)
            self.assertIsInstance(obj, TestModel)
            self.assertEqual(obj.id, 1)
            self.assertIsNone(obj.name)
            logger.info("PASS: Deserialization with missing fields succeeded. The object generated was:-\n\n%s", obj)
        except AssertionError as e:
            logger.error("FAIL. An assertion failed in test_to_object_from_json_with_missing_fields:-\n\n%s", e)
            raise

    def test_to_object_from_json_with_extra_fields(self):
        try:
            # JSON string with extra superfluous fields
            extra_fields_json = '{"id": 1, "name": "Test", "extra_field": "extra_value"}'
            obj = JghSerialization.to_object_from_json(extra_fields_json, TestModel)
            self.assertIsInstance(obj, TestModel)
            self.assertEqual(obj.id, 1)
            self.assertEqual(obj.name, "Test")
            logger.info("PASS: Deserialization with extra fields succeeded. The object generated was:-\n\n%s", obj)
        except AssertionError as e:
            logger.error("FAIL. An assertion failed in test_to_object_from_json_with_extra_fields:-\n\n%s", e)
            raise

    def test_to_object_from_json_with_invalid_json(self):
        # Invalid JSON string
        invalid_json = '{"id": "one", "name": "Test"}'
        try:
            JghSerialization.to_object_from_json(invalid_json, TestModel)
        except ValueError as e:
            logger.info("PASS: Deserialization with invalid JSON correctly raised a ValueError. Error message:-\n\n%s", e)
            self.assertTrue(True)
        else:
            self.fail("FAIL: ValueError not raised")

    def test_to_object_from_json_with_empty_json(self):
        # Empty JSON string
        empty_json = ""
        try:
            JghSerialization.to_object_from_json(empty_json, TestModel)
        except ValueError as e:
            logger.info("PASS: Deserialization with empty JSON correctly raised a ValueError. Error message:-\n\n%s", e)
            self.assertTrue(True)
        else:
            self.fail("FAIL: ValueError not raised")

if __name__ == '__main__':
    unittest.main()

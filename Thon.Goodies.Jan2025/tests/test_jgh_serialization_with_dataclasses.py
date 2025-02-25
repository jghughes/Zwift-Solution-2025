
# Standard library imports
import sys
import logging
import unittest
from dataclasses import dataclass

# Local application imports
from jgh_serialization import JghSerialization
from jgh_logging import jgh_configure_logging

jgh_configure_logging("appsettings.json")
logger = logging.getLogger(__name__)


# Define some arbitrary default values for the tests
default_john: str = "john"
default_middlenames : list[str] = ["gerald", "elana", "thomas", "alexandra"]
default_jones: str = "jones"
default_false: bool = False
default_99 = 99
default_email: str = "email@zip.com"
default_eglinton: str = "eglinton"

# Helper function to write a pretty error messages for the tests
def pretty_error_message(ex: Exception) -> str:
    """
    This function writes a pretty error message to the console.
    The function attempts to unpack the args attribute of the exception ex
    into code and message. If the unpacking fails (e.g., if args does not
    contain two elements), it falls back to setting code to 0 and message
    to the first and only element of args.

    If an exception ex has args like (404, "Not Found"), the function
    will return "Not Found ErrorCode=404". If an exception ex has args
    like ("An error occurred",), the function will return "An error occurred".
    """
    try:
        (code, message) = ex.args
    except:
        code = 0
        message = ex.args[0]
    if code == 0:
        return f"{str(message)}"
    return f"{str(message)} ErrorCode={str(code)}"


# All the tests
class Test_JghSerialization(unittest.TestCase):

    def setUp(self):
        logger.info(f"\nTEST NAME: {self._testMethodName}")
        logger.info(f"-" * 100)
        test_method = getattr(self, self._testMethodName)
        if test_method.__doc__:
            logger.info(f"TEST DOCSTRING:\n\t{test_method.__doc__.strip()}")
            logger.info(f"-" * 100)

    def tearDown(self):
        logger.info(f"-" * 100)
        logger.info(f"TEST FINISHED: {self._testMethodName}")
        logger.info(f"=" * 100)
        logger.info(f"\n")

    def test_01_how_to_roundtrip_a_dataclass(self):
        """
        This test case creates an instance of dataclass (as opposed to a pydantic model),
        roundtrips it using JghSerialization.serialise, and asserts that the roundtripped 
        instance is identical.
        """
        @dataclass
        class TestModel():
            isactive: bool = default_false
            age: int = default_99

        try:
            instance = TestModel(isactive=True, age=16)
            json_str = JghSerialization.serialise(instance)
            logger.info(f"\nJSON STRING:\n\t{json_str}")
            roundtripped = JghSerialization.validate(json_str, TestModel)
            self.assertIsInstance(roundtripped, TestModel)
            self.assertEqual(roundtripped.isactive, True)
            self.assertEqual(roundtripped.age, 16)
            logger.info(
                f"TEST OUTCOME: PASS:\n\tSerialization succeeded.\nInput object:\n\t{instance}\n\tOutput string:\n\t{json_str}"
            )
        except AssertionError as e:
            logger.error(
                f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_to_json_from_object:-\n\n{pretty_error_message(e)}"
            )
            self.fail(f"ERROR OCCURRED: test_01_how_to_roundtrip_a_dataclass:\n{pretty_error_message(e)}\n")

    def test_02_import_json_with_missing_fields_for_dataclass(self):
        """
        Test to illustrate that a JSON field that is missing will be correctly assigned the default value
        by JghSerialization.validate().
        For a dataclass, the default value is assigned to the attribute.
        """
        @dataclass
        class TestModel():
            age: int = 99
            email: str = default_email

        try:
            missing_fields_json = '{"age": 16}' # Missing email field
            logger.info(f"JSON STRING:\n\t{missing_fields_json}")
            obj = JghSerialization.validate(missing_fields_json, TestModel)
            self.assertIsInstance(obj, TestModel)
            self.assertEqual(obj.age, 16)  # the crunch
            self.assertEqual(obj.email, default_email)  # the crunch
            logger.info(
                f"TEST OUTCOME: PASS:\n\tDeserialization with missing field succeeded.\n\tInput string:\n\t{missing_fields_json}\n\tOutput object:\n\t{obj}"
            )
        except AssertionError as e:
            logger.error(
                f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_02_import_json_with_missing_fields_for_dataclass:-\n{pretty_error_message(e)}"
            )
            self.fail(
                f"ERROR OCCURRED: test_02_import_json_with_missing_fields_for_dataclass:\n{pretty_error_message(e)}\n"
            )

    def test_03_import_json_with_superfluous_fields_for_dataclass(self):
        """
        Test to illustrate that superfluous fields in a JSON string will happily ignored
        when a dataclass is deserialised using JghSerialization.validate().
        """
        @dataclass
        class TestModel():
            age: int

        try:
            extra_fields_json = f'{{"age": 27, "extra_field": "extra_value", "another_extra_field": "another_extra_value"}}' # Extra fields
            logger.info(f"JSON STRING:\n\t{extra_fields_json}")
            obj = JghSerialization.validate(extra_fields_json, TestModel)
            self.assertIsInstance(obj, TestModel)
            self.assertEqual(obj.age, 27)
            logger.info(
                f"TEST OUTCOME: PASS:\n\tDeserialization with extra field succeeded.\n\tInput string:\n\t{extra_fields_json}\n\tOutput object:\n\t{obj}"
            )
        except AssertionError as e:
            logger.error(
                f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_03_import_json_with_superfluous_fields_for_dataclass:-\n{pretty_error_message(e)}"
            )
            self.fail(
                f"ERROR OCCURRED: test_03_import_json_with_superfluous_fields_for_dataclass:\n{pretty_error_message(e)}\n"
            )

    #test fails: demonstrating that dataclass is useless for catching egregious problems
    def test_04_import_json_with_unacceptible_field_value_types_in_json_for_dataclass(self):
        """
        Test to illustrate that JghSerialization.validate will raise a ValueError
        if JSON field is an invalid type for the attribute.
        """

        @dataclass
        class TestModel():
            id: int
            first: str | None = None

        # Invalid JSON string
        json_with_invalid_types = f'{{"id": "one", "first": 10}}'
        logger.info(f"JSON STRING:\n\t{json_with_invalid_types}")
        try:
            outcome = JghSerialization.validate(json_with_invalid_types, TestModel)
        except ValueError as e:
            logger.info(
                f"TEST OUTCOME: PASS:\n\tDeserialization with JSON containing invalid attribute types correctly raised a ValueError.\nError message:\n\t{pretty_error_message(e)}"
            )
            self.assertTrue(True)
        else:
            self.fail(
                f"ERROR OCCURRED:\n\t'test_04_import_json_with_unacceptible_field_value_types_in_json_for_dataclass' ValueError not raised.\n\t{outcome}"
            )

    def test_05_import_json_with_fatally_badly_formatted_json_for_dataclass(self):
        """
        Test to illustrate that JghSerialization.validate will raise a ValueError
        if JSON is garbage.
        """

        @dataclass
        class TestModel():
            first: str | None = None

        # Invalid JSON string
        rubbish_json = f'{{":rubbish:::}}'
        logger.info(f"JSON STRING:\n\t{rubbish_json}")

        try:
            JghSerialization.validate(rubbish_json, TestModel)
        except ValueError as e:
            logger.info(
                f"TEST OUTCOME: PASS:\n\tDeserialization with badly formatted JSON correctly raised a ValueError.\nError message:\n\t{pretty_error_message(e)}"
            )
            self.assertTrue(True)
        else:
            self.fail(
                f"ERROR OCCURRED:\n\t'test_05_import_json_with_fatally_badly_formatted_json_for_dataclass' ValueError not raised"
            )

    def test_06_import_json_with_empty_json_for_dataclass(self):
        """
        Test to illustrate that JghSerialization.validate with empty and therefore invalid JSON will raise a ValueError.
        """

        @dataclass
        class TestModel():
            id: int = 0

        # Empty JSON string
        empty_json = ""
        try:
            JghSerialization.validate(empty_json, TestModel)
        except ValueError as e:
            logger.info(
                f"TEST OUTCOME: PASS:\n\tDeserialization with empty and therefore invalid JSON correctly raised a ValueError.\nError message:\n\t{pretty_error_message(e)}"
            )
            self.assertTrue(True)
        else:
            self.fail(f"TEST OUTCOME FAIL:\n\tValueError not raised")

    # test fails: demonstrating that dataclass is useless for catching egregious problems
    # problem. test is failing maybe because my custom decoder isn't working
    def test_07_import_json_with_int_and_bool_represented_as_strings_for_dataclass(self):
        """
        This test will illustrate how JghSerialization.validate reacts where 
        integer, float, and boolean values are encountered as strings in the JSON
        being deserialised into a a dataclass. The test shows how JghSerialization.validate 
        raises an error because of the limited functionality of dataclasses. 
        """

        @dataclass
        class TestModel():
            isactive: bool | None
            age: int | None

        try:
            # Define a JSON string with integer and boolean values represented as strings
            json_with_strings = """
            {
                "isactive": "true",
                "age": "32"
            }
            """
            logger.info(f"JSON STRING:\n\t{json_with_strings}")
            obj = JghSerialization.validate(json_with_strings, TestModel)
            self.assertIsInstance(obj, TestModel)
            self.assertTrue(obj.isactive)  # Coerced to boolean
            self.assertEqual(obj.age, 32)  # Coerced to integer
            logger.info(
                f"TEST OUTCOME: PASS:\n\tDeserialization with integer and boolean values represented as strings succeeded.\n\tInput string:\n\t{json_with_strings}\n\tOutput object:\n\t{obj}"
            )
        except AssertionError as e:
            logger.error(
                f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_07_import_json_with_int_and_bool_represented_as_strings_for_dataclass:-\n{pretty_error_message(e)}"
            )
            self.fail(
                f"ERROR OCCURRED: test_07_import_json_with_int_and_bool_represented_as_strings_for_dataclass:\nerror_message(e)\n"
            )


# Do the tests (but not if this script is imported as a module)
if __name__ == "__main__":
    print("sys.path (in alphabetical order):-")
    for path in sorted(sys.path):
        print(f" - {path}")
    print(
        "\nExplanation:\n\tThe above paths are where Python will look to find modules and imports\n\treferenced in this file. If imports fail to resolve, it is because of\n\tincorrect paths. In a Visual Studio 2022 project, right-click\n\tthe 'Search Paths' node to add a path."
    )

    unittest.main()

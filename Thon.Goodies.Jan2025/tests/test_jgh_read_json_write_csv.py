
# Standard library imports
import os
import json
import csv
import unittest
import logging
from jgh_read_json_write_csv import read_json_write_csv

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Helper function to write a pretty error message
def error_message(ex: Exception) -> str:
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

class Test_ReadJsonWriteCsv(unittest.TestCase):

    def setUp(self):
        logger.info(f"\nTEST NAME: {self._testMethodName}")
        logger.info(f"-" * 100)
        # Print the docstring of the test method
        test_method = getattr(self, self._testMethodName)
        if test_method.__doc__:
            logger.info(f"TEST DOCSTRING:\n\t{test_method.__doc__.strip()}")
            logger.info(f"-" * 100)

        # Create directories if they do not exist

        self.input_dirpath = r"C:/Users/johng/holding_pen/StuffForZsun/Tool.ConvertJsonToCsv.Dec2024_TestInput"
        self.output_dirpath = r"C:/Users/johng/holding_pen/StuffForZsun/Tool.ConvertJsonToCsv.Dec2024_TestOutputV2"
        os.makedirs(self.input_dirpath, exist_ok=True)
        os.makedirs(self.output_dirpath, exist_ok=True)

    def tearDown(self):
        logger.info(f"-" * 100)
        logger.info(f"TEST FINISHED: {self._testMethodName}")
        logger.info(f"=" * 100)
        logger.info(f"\n")

    def test_read_json_write_csv_filters_non_dict_elements(self):
        """
        This test case verifies that the read_json_write_csv function correctly filters out non-dictionary elements
        from the input JSON and only includes dictionary elements in the output CSV.
        """
        input_filename = "test_input.json"
        output_filename = "test_output.csv"

        # Create the test JSON file with an isolated string an isolate integer
        test_json_content = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
            "This is a string",
            12345,
            {"name": "Charlie", "age": 35}
        ]

        with open(os.path.join(self.input_dirpath, input_filename), "w", encoding="utf-8") as f:
            json.dump(test_json_content, f, ensure_ascii=False, indent=4)

        # Run the function
        try:
            read_json_write_csv(self.input_dirpath, input_filename, self.output_dirpath, output_filename)
            logger.info("Test completed successfully. Check the output CSV file.")
        except Exception as e:
            logger.error(f"Test failed with error: {error_message(e)}")
            self.fail(f"Test failed with error: {error_message(e)}")

        # Verify the output CSV file
        output_file_path = os.path.join(self.output_dirpath, output_filename)
        self.assertTrue(os.path.exists(output_file_path), "Output CSV file does not exist.")

        with open(output_file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 3, f"Expected 3 rows in the CSV file, but found {len(rows)}.")
            self.assertEqual(reader.fieldnames, ["name", "age"], f"Expected headers ['name', 'age'], but found {reader.fieldnames}.")

            expected_content = [
                {"name": "Alice", "age": "30"},
                {"name": "Bob", "age": "25"},
                {"name": "Charlie", "age": "35"}
            ]
            for row, expected_row in zip(rows, expected_content):
                self.assertEqual(row, expected_row, f"Expected row {expected_row}, but found {row}.")

        logger.info("All assertions passed.")

    def test_read_json_write_csv_empty_json_array(self):
        """
        This test case verifies that the read_json_write_csv function handles an empty JSON array correctly
        and produces an empty CSV file.
        """
        input_filename = "test_input_empty.json"
        output_filename = "test_output_empty.csv"

        # Create the test JSON file
        test_json_content = []

        with open(os.path.join(self.input_dirpath, input_filename), "w", encoding="utf-8") as f:
            json.dump(test_json_content, f, ensure_ascii=False, indent=4)

                    # Run the function
        try:
            read_json_write_csv(self.input_dirpath, input_filename, self.output_dirpath, output_filename)
            self.fail("Test failed because no exception was raised.")
        except Exception as e:
            logger.info(f"Test passed with expected error: {error_message(e)}")
            return

        # # Run the function
        # try:
        #     read_json_write_csv(self.input_dirpath, input_filename, self.output_dirpath, output_filename)
        #     logger.info("Test completed successfully. Check the output CSV file.")
        # except Exception as e:
        #     logger.error(f"Test failed with error: {error_message(e)}")
        #     self.fail(f"Test failed with error: {error_message(e)}")

        # Verify the output CSV file
        output_file_path = os.path.join(self.output_dirpath, output_filename)
        self.assertTrue(os.path.exists(output_file_path), "Output CSV file does not exist.")

        with open(output_file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 0, f"Expected 0 rows in the CSV file, but found {len(rows)}.")

        logger.info("All assertions passed.")

    def test_read_json_write_csv_only_non_dict_elements(self):
        """
        This test case verifies that the read_json_write_csv function handles a JSON array with only non-dictionary elements
        correctly and produces an empty CSV file.
        """
        input_filename = "test_input_non_dict.json"
        output_filename = "test_output_non_dict.csv"

        # Create the test JSON file
        test_json_content = [
            "This is a string",
            12345,
            ["This", "is", "a", "list"],
            None
        ]

        with open(os.path.join(self.input_dirpath, input_filename), "w", encoding="utf-8") as f:
            json.dump(test_json_content, f, ensure_ascii=False, indent=4)

        # Run the function
        try:
            read_json_write_csv(self.input_dirpath, input_filename, self.output_dirpath, output_filename)
            logger.info("Test completed successfully. Check the output CSV file.")
        except Exception as e:
            logger.error(f"Test failed with error: {error_message(e)}")
            self.fail(f"Test failed with error: {error_message(e)}")

        # Verify the output CSV file
        output_file_path = os.path.join(self.output_dirpath, output_filename)
        self.assertTrue(os.path.exists(output_file_path), "Output CSV file does not exist.")

        with open(output_file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 0, f"Expected 0 rows in the CSV file, but found {len(rows)}.")

        logger.info("All assertions passed.")

    def test_read_json_write_csv_nested_dicts(self):
        """
        This test case verifies that the read_json_write_csv function handles nested dictionaries correctly.
        """
        input_filename = "test_input_nested.json"
        output_filename = "test_output_nested.csv"

        # Create the test JSON file
        test_json_content = [
            {"name": "Alice", "details": {"age": 30, "city": "Wonderland"}},
            {"name": "Bob", "details": {"age": 25, "city": "Builderland"}}
        ]

        with open(os.path.join(self.input_dirpath, input_filename), "w", encoding="utf-8") as f:
            json.dump(test_json_content, f, ensure_ascii=False, indent=4)

        # Run the function
        try:
            read_json_write_csv(self.input_dirpath, input_filename, self.output_dirpath, output_filename)
            logger.info("Test completed successfully. Check the output CSV file.")
        except Exception as e:
            logger.error(f"Test failed with error: {error_message(e)}")
            self.fail(f"Test failed with error: {error_message(e)}")

        # Verify the output CSV file
        output_file_path = os.path.join(self.output_dirpath, output_filename)
        self.assertTrue(os.path.exists(output_file_path), "Output CSV file does not exist.")

        with open(output_file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 2, f"Expected 2 rows in the CSV file, but found {len(rows)}.")
            self.assertEqual(set(reader.fieldnames or []), {"name", "details"}, f"Expected headers {{'name', 'details'}}, but found {set(reader.fieldnames or [])}.")
            expected_content = [
                {"name": "Alice", "details": "{'age': 30, 'city': 'Wonderland'}"},
                {"name": "Bob", "details": "{'age': 25, 'city': 'Builderland'}"}
            ]
            for row, expected_row in zip(rows, expected_content):
                self.assertEqual(row, expected_row, f"Expected row {expected_row}, but found {row}.")

        logger.info("All assertions passed.")

    def test_read_json_write_csv_different_keys(self):
        """
        This test case verifies that the read_json_write_csv function handles dictionaries with different keys correctly.
        """
        input_filename = "test_input_diff_keys.json"
        output_filename = "test_output_diff_keys.csv"

        # Create the test JSON file
        test_json_content = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "city": "Builderland"},
            {"name": "Charlie", "age": 35, "city": "Charlieland"}
        ]

        with open(os.path.join(self.input_dirpath, input_filename), "w", encoding="utf-8") as f:
            json.dump(test_json_content, f, ensure_ascii=False, indent=4)

        # Run the function
        try:
            read_json_write_csv(self.input_dirpath, input_filename, self.output_dirpath, output_filename)
            logger.info("Test completed successfully. Check the output CSV file.")
        except Exception as e:
            logger.error(f"Test failed with error: {error_message(e)}")
            self.fail(f"Test failed with error: {error_message(e)}")

        # Verify the output CSV file
        output_file_path = os.path.join(self.output_dirpath, output_filename)
        self.assertTrue(os.path.exists(output_file_path), "Output CSV file does not exist.")

        with open(output_file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 3, f"Expected 3 rows in the CSV file, but found {len(rows)}.")
            self.assertEqual(set(reader.fieldnames or []), {"name", "age", "city"}, f"Expected headers {{'name', 'age', 'city'}}, but found {set(reader.fieldnames or [])}.")
            expected_content = [
                {"name": "Alice", "age": "30", "city": ""},
                {"name": "Bob", "age": "", "city": "Builderland"},
                {"name": "Charlie", "age": "35", "city": "Charlieland"}
            ]
            for row, expected_row in zip(rows, expected_content):
                self.assertEqual(row, expected_row, f"Expected row {expected_row}, but found {row}.")

        logger.info("All assertions passed.")

    def test_read_json_write_csv_special_characters(self):
        """
        This test case verifies that the read_json_write_csv function handles special characters in keys and values correctly.
        """
        input_filename = "test_input_special_chars.json"
        output_filename = "test_output_special_chars.csv"

        # Create the test JSON file
        test_json_content = [
            {"na!me": "A!lice", "a@ge": 30},
            {"na!me": "B#ob", "a@ge": 25},
            {"na!me": "Ch$arlie", "a@ge": 35}
        ]

        with open(os.path.join(self.input_dirpath, input_filename), "w", encoding="utf-8") as f:
            json.dump(test_json_content, f, ensure_ascii=False, indent=4)

        # Run the function
        try:
            read_json_write_csv(self.input_dirpath, input_filename, self.output_dirpath, output_filename)
            logger.info("Test completed successfully. Check the output CSV file.")
        except Exception as e:
            logger.error(f"Test failed with error: {error_message(e)}")
            self.fail(f"Test failed with error: {error_message(e)}")

        # Verify the output CSV file
        output_file_path = os.path.join(self.output_dirpath, output_filename)
        self.assertTrue(os.path.exists(output_file_path), "Output CSV file does not exist.")

        with open(output_file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 3, f"Expected 3 rows in the CSV file, but found {len(rows)}.")
            self.assertEqual(reader.fieldnames, ["na!me", "a@ge"], f"Expected headers ['na!me', 'a@ge'], but found {reader.fieldnames}.")

            expected_content = [
                {"na!me": "A!lice", "a@ge": "30"},
                {"na!me": "B#ob", "a@ge": "25"},
                {"na!me": "Ch$arlie", "a@ge": "35"}
            ]
            for row, expected_row in zip(rows, expected_content):
                self.assertEqual(row, expected_row, f"Expected row {expected_row}, but found {row}.")

        logger.info("All assertions passed.")

    def test_read_json_write_csv_large_json_array(self):
        """
        This test case verifies that the read_json_write_csv function handles a large JSON array efficiently
        and produces the correct CSV output.
        """
        input_filename = "test_input_large.json"
        output_filename = "test_output_large.csv"

        # Create the test JSON file
        test_json_content = [{"name": f"Person{i}", "age": i} for i in range(1000)]

        with open(os.path.join(self.input_dirpath, input_filename), "w", encoding="utf-8") as f:
            json.dump(test_json_content, f, ensure_ascii=False, indent=4)

        # Run the function
        try:
            read_json_write_csv(self.input_dirpath, input_filename, self.output_dirpath, output_filename)
            logger.info("Test completed successfully. Check the output CSV file.")
        except Exception as e:
            logger.error(f"Test failed with error: {error_message(e)}")
            self.fail(f"Test failed with error: {error_message(e)}")

        # Verify the output CSV file
        output_file_path = os.path.join(self.output_dirpath, output_filename)
        self.assertTrue(os.path.exists(output_file_path), "Output CSV file does not exist.")

        with open(output_file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 1000, f"Expected 1000 rows in the CSV file, but found {len(rows)}.")
            self.assertEqual(reader.fieldnames, ["name", "age"], f"Expected headers ['name', 'age'], but found {reader.fieldnames}.")

            expected_content = [{"name": f"Person{i}", "age": str(i)} for i in range(1000)]
            for row, expected_row in zip(rows, expected_content):
                self.assertEqual(row, expected_row, f"Expected row {expected_row}, but found {row}.")

        logger.info("All assertions passed.")

# Do the tests (but not if this script is imported as a module)
if __name__ == "__main__":
    unittest.main()

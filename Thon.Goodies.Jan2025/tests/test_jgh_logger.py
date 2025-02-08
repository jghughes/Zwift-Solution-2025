# FILE CONTEXT
# File: Thon.Goodies.Jan2025/tests/test_configure_logging.py

"""
Unit tests for the jgh_configure_logging function.
"""

# Standard library imports
import os
import sys
import json
import logging
import unittest
from unittest.mock import patch, mock_open

# Local application imports
from jgh_logger import jgh_configure_logger, HANDLER_NAME_CONSOLE, HANDLER_NAME_DEBUG, HANDLER_NAME_INFO, HANDLER_NAME_WARNING, HANDLER_NAME_ERROR, HANDLER_NAME_CRITICAL

# Configure logging for the tests
# logging.basicConfig(level=logging.INFO, format="%(message)s")
# logger = logging.getLogger(__name__)

os.environ["APP_ENV"] = "test" # look for settings in 'test' file i.e. settings.test.json
os.environ["APP_ROOT"] = os.path.dirname(__file__) # jgh_configure_logger will look for settings.test.json in APP_ROOT i.e. the directory containing this file
jgh_configure_logger()
logger = logging.getLogger()

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
class Test_ConfigureLogging(unittest.TestCase):

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

    @patch("jgh_logging_config.os.getenv")
    @patch("jgh_logging_config.open", new_callable=mock_open, read_data='{"logging": {"path": "/logs", "debug_filename": "debug.log", "info_filename": "info.log", "warning_filename": "warning.log", "error_filename": "error.log", "critical_filename": "critical.log"}}')
    def test_01_configure_logging_with_valid_config(self, mock_open, mock_getenv):
        """
        Test jgh_configure_logging with a valid configuration file.
        """
        mock_getenv.side_effect = lambda key, default=None: {"APP_ENV": "test", "APP_ROOT": "/app"}.get(key, default)
        try:
            # jgh_configure_logging()
            # logger = logging.getLogger()
            handler_names = [handler.get_name() for handler in logger.handlers]
            self.assertIn(HANDLER_NAME_CONSOLE, handler_names)
            # self.assertIn(HANDLER_NAME_DEBUG, handler_names)
            # self.assertIn(HANDLER_NAME_INFO, handler_names)
            # self.assertIn(HANDLER_NAME_WARNING, handler_names)
            # self.assertIn(HANDLER_NAME_ERROR, handler_names)
            # self.assertIn(HANDLER_NAME_CRITICAL, handler_names)
            logger.info("TEST OUTCOME: PASS: Valid configuration file processed correctly.")
        except AssertionError as e:
            logger.error(
                f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_01_configure_logging_with_valid_config:-\n{pretty_error_message(e)}"
            )
            self.fail(
                f"ERROR OCCURRED: test_01_configure_logging_with_valid_config:\n {pretty_error_message(e)}\n"
            )

    @patch("jgh_logging_config.os.getenv")
    @patch("jgh_logging_config.open", new_callable=mock_open, read_data='{}')
    def test_02_configure_logging_with_missing_logging_section(self, mock_open, mock_getenv):
        """
        Test jgh_configure_logging with a configuration file missing the logging section.
        """
        mock_getenv.side_effect = lambda key, default=None: {"APP_ENV": "test", "APP_ROOT": "/app"}.get(key, default)
        try:
            with self.assertLogs(level='ERROR') as log:
                jgh_configure_logging()
                self.assertIn("ERROR: 'logging' section not found", log.output[0])
            logger.info("TEST OUTCOME: PASS: Missing logging section handled correctly.")
        except AssertionError as e:
            logger.error(
                f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_02_configure_logging_with_missing_logging_section:-\n{pretty_error_message(e)}"
            )
            self.fail(
                f"ERROR OCCURRED: test_02_configure_logging_with_missing_logging_section:\n {pretty_error_message(e)}\n"
            )

    @patch("jgh_logging_config.os.getenv")
    @patch("jgh_logging_config.open", new_callable=mock_open)
    def test_03_configure_logging_with_invalid_json(self, mock_open, mock_getenv):
        """
        Test jgh_configure_logging with an invalid JSON configuration file.
        """
        mock_open.side_effect = json.JSONDecodeError("Expecting value", "", 0)
        mock_getenv.side_effect = lambda key, default=None: {"APP_ENV": "test", "APP_ROOT": "/app"}.get(key, default)
        try:
            with self.assertLogs(level='ERROR') as log:
                jgh_configure_logging()
                self.assertIn("ERROR: Failed to load configuration", log.output[0])
            logger.info("TEST OUTCOME: PASS: Invalid JSON configuration file handled correctly.")
        except AssertionError as e:
            logger.error(
                f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_03_configure_logging_with_invalid_json:-\n{pretty_error_message(e)}"
            )
            self.fail(
                f"ERROR OCCURRED: test_03_configure_logging_with_invalid_json:\n {pretty_error_message(e)}\n"
            )

    @patch("jgh_logging_config.os.getenv")
    @patch("jgh_logging_config.open", new_callable=mock_open, read_data='{"logging": {"path": "/logs"}}')
    def test_04_configure_logging_with_missing_filenames(self, mock_open, mock_getenv):
        """
        Test jgh_configure_logging with a configuration file missing log filenames.
        """
        mock_getenv.side_effect = lambda key, default=None: {"APP_ENV": "test", "APP_ROOT": "/app"}.get(key, default)
        try:
            jgh_configure_logging()
            logger = logging.getLogger()
            handler_names = [handler.get_name() for handler in logger.handlers]
            self.assertIn(HANDLER_NAME_CONSOLE, handler_names)
            self.assertNotIn(HANDLER_NAME_DEBUG, handler_names)
            self.assertNotIn(HANDLER_NAME_INFO, handler_names)
            self.assertNotIn(HANDLER_NAME_WARNING, handler_names)
            self.assertNotIn(HANDLER_NAME_ERROR, handler_names)
            self.assertNotIn(HANDLER_NAME_CRITICAL, handler_names)
            logger.info("TEST OUTCOME: PASS: Missing log filenames handled correctly.")
        except AssertionError as e:
            logger.error(
                f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_04_configure_logging_with_missing_filenames:-\n{pretty_error_message(e)}"
            )
            self.fail(
                f"ERROR OCCURRED: test_04_configure_logging_with_missing_filenames:\n {pretty_error_message(e)}\n"
            )

    @patch("jgh_logging_config.os.getenv")
    @patch("jgh_logging_config.open", new_callable=mock_open, read_data='{"logging": {"path": "relative/path"}}')
    def test_05_configure_logging_with_relative_logfile_path(self, mock_open, mock_getenv):
        """
        Test jgh_configure_logging with a relative logfile path.
        """
        mock_getenv.side_effect = lambda key, default=None: {"APP_ENV": "test", "APP_ROOT": "/app"}.get(key, default)
        try:
            with self.assertRaises(ValueError) as context:
                jgh_configure_logging()
            self.assertIn("logfiles_folder must be an absolute path", str(context.exception))
            logger.info("TEST OUTCOME: PASS: Relative logfile path handled correctly.")
        except AssertionError as e:
            logger.error(
                f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_05_configure_logging_with_relative_logfile_path:-\n{pretty_error_message(e)}"
            )
            self.fail(
                f"ERROR OCCURRED: test_05_configure_logging_with_relative_logfile_path:\n {pretty_error_message(e)}\n"
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

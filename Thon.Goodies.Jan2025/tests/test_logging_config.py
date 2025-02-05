import logging
import os
import unittest
from jgh_logging_config import configure_logging

# # Configure logging
# configure_logging(logging.DEBUG)

# logger = logging.getLogger()  # Get the root logger
# # Get the logger
# logger = logging.getLogger(__name__)

class TestLoggingConfiguration(unittest.TestCase):

    def setUp(self):
        # Configure logging
        self.log_filenames = {
            "debug": "test_log_debug.log",
            "info": "test_log_info.log",
            "warning": "test_log_warning.log",
            "error": "test_log_error.log",
            "critical": "test_log_critical.log"
        }
        configure_logging(logging.DEBUG, self.log_filenames)
        self.logger = logging.getLogger(__name__)

    def tearDown(self):
       # Shut down logging to release file handles
        logging.shutdown()
        # Clean up log files after tests
        for log_file in self.log_filenames.values():
            if os.path.exists(log_file):
                os.remove(log_file)

    def test_log_files_creation(self):
        # Log messages at different levels
        self.logger.debug("This is a test debug message")
        self.logger.info("This is a test info message")
        self.logger.warning("This is a test warning message")
        self.logger.error("This is a test error message")
        self.logger.critical("This is a test critical message")

        # Verify that log files are created and contain the expected messages
        for level, log_file in self.log_filenames.items():
        # for level, log_file in self.log_filenames.items():
            with self.subTest(log_file=log_file):
                self.assertTrue(os.path.exists(log_file), f"{log_file} should exist")
                with open(log_file, 'r') as f:
                    content = f.read()
                    self.assertIn(f"This is a test {level} message", content, f"{log_file} should contain the {level} message")

if __name__ == "__main__":
    unittest.main(exit=False)
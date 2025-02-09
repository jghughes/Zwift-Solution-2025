
import unittest
from unittest.mock import patch, MagicMock, Mock
import logging
from jgh_logger import add_logfile_handlers, HANDLER_NAME_DEBUG, HANDLER_NAME_INFO, HANDLER_NAME_WARNING, HANDLER_NAME_ERROR, HANDLER_NAME_CRITICAL

class TestAddLogfileHandlers(unittest.TestCase):

    def setUp(self):
        self.logger = logging.getLogger("test_logger")
        self.logger.setLevel(logging.DEBUG)
        if self.logger.hasHandlers():
            for handler in self.logger.handlers:
                handler.close()
            self.logger.handlers.clear()

    def tearDown(self):
       if self.logger.hasHandlers():
            for handler in self.logger.handlers:
                handler.close()
            self.logger.handlers.clear()

    @patch("jgh_logger.read_logfile_settings")
    @patch("jgh_logger.validate_logfile_settings")
    def test_add_logfile_handlers_valid_config(self, mock_validate: Mock, mock_load: Mock):
        """
        Test that logfile handlers are added with a valid configuration.
        """
        mock_load.return_value = MagicMock(storage_dirpath=r"C:\Users\johng\holding_pen\Test_scratchpad\LogFiles")
        mock_validate.return_value = MagicMock(
            debug_filepath="debug.log",
            info_filepath="info.log",
            warning_filepath="warning.log",
            error_filepath="error.log",
            critical_filepath="critical.log"
        )

        add_logfile_handlers(self.logger)
        handler_names = [handler.get_name() for handler in self.logger.handlers]
        self.assertIn(HANDLER_NAME_DEBUG, handler_names)
        self.assertIn(HANDLER_NAME_INFO, handler_names)
        self.assertIn(HANDLER_NAME_WARNING, handler_names)
        self.assertIn(HANDLER_NAME_ERROR, handler_names)
        self.assertIn(HANDLER_NAME_CRITICAL, handler_names)

    @patch("jgh_logger.read_logfile_settings")
    def test_add_logfile_handlers_no_config(self, mock_load: Mock):
        """
        Test that no handlers are added if the configuration is missing.
        """
        mock_load.return_value = None
        add_logfile_handlers(self.logger)
        self.assertFalse(self.logger.handlers)

    @patch("jgh_logger.read_logfile_settings")
    @patch("jgh_logger.validate_logfile_settings")
    def test_add_logfile_handlers_invalid_path(self, mock_validate: Mock, mock_load: Mock):
        """
        Test that no handlers are added if the log file path is invalid.
        """
        mock_load.return_value = MagicMock(storage_dirpath="/rubbish")
        mock_validate.return_value = None
        add_logfile_handlers(self.logger)
        self.assertFalse(self.logger.handlers)

    @patch("jgh_logger.read_logfile_settings")
    @patch("jgh_logger.validate_logfile_settings")
    @patch("jgh_logger.RotatingFileHandler")
    def test_add_logfile_handlers_exception(self, mock_handler: Mock, mock_validate: Mock, mock_load: Mock) -> None:
        """
        Test that an exception is handled if adding a handler fails.
        """
        mock_load.return_value = MagicMock(storage_dirpath=r"C:\Users\johng\holding_pen\Test_scratchpad\LogFiles")
        mock_validate.return_value = MagicMock(
            debug_filepath="debug.log",
            info_filepath="info.log",
            warning_filepath="warning.log",
            error_filepath="error.log",
            critical_filepath="critical.log"
        )
        mock_handler.side_effect = OSError("Test exception")
        add_logfile_handlers(self.logger)
        self.assertFalse(self.logger.handlers)

if __name__ == "__main__":
    unittest.main(verbosity=3)

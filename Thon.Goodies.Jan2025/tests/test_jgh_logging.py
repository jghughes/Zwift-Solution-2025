import unittest
import logging
from unittest.mock import patch, mock_open, MagicMock
from jgh_logging import jgh_configure_logging

class TestConfigureLogger(unittest.TestCase):

    @patch('jgh_logging.find_filepath')
    @patch('builtins.open', new_callable=mock_open, read_data='''{
        "logging": {
            "console": {
                "loglevel": "debug",
                "messageformat": "balanced"
            },
            "file": {
                "loglevel": "critical",
                "messageformat": "informative"
            }
        }
    }''')
    def test_configure_logger_with_valid_settingsfile_loggingsection(self, mock_file: MagicMock, mock_find_path: MagicMock) -> None:
        jgh_configure_logging('appsettings.json')
        logger = logging.getLogger()
        self.assertTrue(logger.hasHandlers())
        self.assertEqual(len(logger.handlers), 2)
        console_handler = next((h for h in logger.handlers if h.name == 'console handler'), None)
        file_handler = next((h for h in logger.handlers if h.name == 'file handler'), None)
        self.assertIsNotNone(console_handler)
        self.assertIsNotNone(file_handler)
        if console_handler is not None:
            self.assertEqual(console_handler.level, logging.DEBUG)
        if file_handler is not None:
            self.assertEqual(file_handler.level, logging.CRITICAL)

    @patch('jgh_logging.find_filepath')
    @patch('builtins.open', new_callable=mock_open, read_data='')
    def test_configure_logger_with_empty_settingsfile(self, mock_file: MagicMock, mock_find_path: MagicMock) -> None:
        jgh_configure_logging( 'appsettings.json')
        logger = logging.getLogger()
        self.assertTrue(logger.hasHandlers())
        self.assertEqual(len(logger.handlers), 1)

    @patch('jgh_logging.find_filepath')
    @patch('builtins.open', new_callable=mock_open, read_data='rubbish intentionally invalid json')
    def test_configure_logger_with_invalid_settingsjson(self, mock_file: MagicMock, mock_find_path: MagicMock) -> None:
        jgh_configure_logging('appsettings.json')
        logger = logging.getLogger()
        self.assertTrue(logger.hasHandlers())
        self.assertEqual(len(logger.handlers), 1)


    @patch('jgh_logging.find_filepath')
    def test_configure_logger_with_no_settingsfile(self, mock_find_path: MagicMock) -> None:
        jgh_configure_logging('appsettings.json')
        logger = logging.getLogger()
        self.assertTrue(logger.hasHandlers())
        self.assertEqual(len(logger.handlers), 1)



    @patch('jgh_logging.find_filepath')
    @patch('builtins.open', new_callable=mock_open, read_data='''{
        "logging": {
            "console": {
                "loglevel": "debug",
                "messageformat": "balanced"
            }
        }
    }''')
    def test_configure_logger_with_consolehandler_only(self, mock_file: MagicMock, mock_find_path: MagicMock) -> None:
        jgh_configure_logging('appsettings.json')
        logger = logging.getLogger()
        self.assertTrue(logger.hasHandlers())
        self.assertEqual(len(logger.handlers), 1)
        console_handler = next((h for h in logger.handlers if h.name == 'console handler'), None)
        self.assertTrue(logger.hasHandlers())
        self.assertEqual(len(logger.handlers), 1)
        self.assertIsNotNone(console_handler)
        if console_handler is not None:
            self.assertEqual(console_handler.level, logging.DEBUG)

    @patch('jgh_logging.find_filepath')
    @patch('builtins.open', new_callable=mock_open, read_data='''{
        "logging": {
            "file": {
                "loglevel": "critical",
                "messageformat": "informative"
            }
        }
    }''')
    def test_configure_logger_with_filehandler_only(self, mock_file: MagicMock, mock_find_path: MagicMock) -> None:
        jgh_configure_logging('appsettings.json')
        logger = logging.getLogger()
        self.assertTrue(logger.hasHandlers())
        self.assertEqual(len(logger.handlers), 1)

        file_handler = next((h for h in logger.handlers if h.name == 'file handler'), None)
        self.assertTrue(logger.hasHandlers())
        self.assertEqual(len(logger.handlers), 1)
        self.assertIsNotNone(file_handler)
        if file_handler is not None:
            self.assertEqual(file_handler.level, logging.CRITICAL)



    def test_configure_logger_with_handlers_and_write_log_messages(self) -> None:
        jgh_configure_logging('appsettings.json') # This must be a valid settings file with both console and file handlers
        logger = logging.getLogger()
        self.assertTrue(logger.hasHandlers())
        self.assertEqual(len(logger.handlers), 2)
        console_handler = next((h for h in logger.handlers if h.name == 'console handler'), None)
        file_handler = next((h for h in logger.handlers if h.name == 'file handler'), None)
        self.assertTrue(logger.hasHandlers())
        self.assertEqual(len(logger.handlers), 2)
        self.assertIsNotNone(console_handler)
        self.assertIsNotNone(file_handler)
        if console_handler is not None:
            self.assertEqual(console_handler.level, logging.DEBUG)

        if file_handler is not None:
            self.assertEqual(file_handler.level, logging.CRITICAL)

        # Log some test messages
        test_message_debug = "This is a DEBUG severity message"
        logger.debug(test_message_debug)

        test_message_info = "This is a INFO severity message"
        logger.info(test_message_info)

        test_message_warning = "This is a WARNING severity message"
        logger.warning(test_message_warning)

        test_message_error = "This is a ERROR severity message"
        logger.error(test_message_error)

        test_message_critical= "This is a CRITICAL severity message"
        logger.critical(test_message_critical)


if __name__ == '__main__':
    unittest.main(verbosity=2)

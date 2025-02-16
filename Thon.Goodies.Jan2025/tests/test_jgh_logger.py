import io
import sys
import unittest
import logging
from unittest.mock import patch, mock_open, MagicMock
from jgh_logger import jgh_customise_logger

class TestConfigureLogger(unittest.TestCase):

    @patch('jgh_logger.find_filepath')
    @patch('builtins.open', new_callable=mock_open, read_data='''{
        "logging": {
            "console": {
                "loglevel": "debug",
                "messageformat": "normal"
            },
            "file": {
                "loglevel": "critical",
                "messageformat": "verbose"
            }
        }
    }''')
    def test_configure_logger_with_valid_settingsfile_loggingsection(self, mock_file: MagicMock, mock_find_path: MagicMock) -> None:
        logger = logging.getLogger()
        jgh_customise_logger(logger,'appsettings.json')
        self.assertTrue(logger.hasHandlers())
        self.assertEqual(len(logger.handlers), 2)
        console_handler = next((h for h in logger.handlers if h.name == 'customised_console_handler'), None)
        file_handler = next((h for h in logger.handlers if h.name == 'customised_logfile_handler'), None)
        self.assertIsNotNone(console_handler)
        self.assertIsNotNone(file_handler)
        self.assertEqual(console_handler.level, logging.DEBUG)
        self.assertEqual(file_handler.level, logging.CRITICAL)

    @patch('jgh_logger.find_filepath')
    @patch('builtins.open', new_callable=mock_open, read_data='')
    def test_configure_logger_with_empty_settingsfile(self, mock_file: MagicMock, mock_find_path: MagicMock) -> None:
 
        logger = logging.getLogger()
        jgh_customise_logger(logger, 'appsettings.json')
        self.assertTrue(logger.hasHandlers())
        self.assertEqual(len(logger.handlers), 1)

    @patch('jgh_logger.find_filepath')
    @patch('builtins.open', new_callable=mock_open, read_data='rubbish intentionally invalid json')
    def test_configure_logger_with_invalid_settingsjson(self, mock_file: MagicMock, mock_find_path: MagicMock) -> None:
        logger = logging.getLogger()
        jgh_customise_logger(logger,'appsettings.json')
        self.assertTrue(logger.hasHandlers())
        self.assertEqual(len(logger.handlers), 1)


    @patch('jgh_logger.find_filepath')
    def test_configure_logger_with_no_settingsfile(self, mock_find_path: MagicMock) -> None:
        logger = logging.getLogger()
        jgh_customise_logger(logger,'appsettings.json')
        self.assertTrue(logger.hasHandlers())
        self.assertEqual(len(logger.handlers), 1)



    @patch('jgh_logger.find_filepath')
    @patch('builtins.open', new_callable=mock_open, read_data='''{
        "logging": {
            "console": {
                "loglevel": "debug",
                "messageformat": "normal"
            }
        }
    }''')
    def test_configure_logger_with_consolehandler_only(self, mock_file: MagicMock, mock_find_path: MagicMock) -> None:
        logger = logging.getLogger()
        jgh_customise_logger(logger,'appsettings.json')
        self.assertTrue(logger.hasHandlers())
        self.assertEqual(len(logger.handlers), 1)

        console_handler = next((h for h in logger.handlers if h.name == 'customised_console_handler'), None)
        self.assertTrue(logger.hasHandlers())
        self.assertEqual(len(logger.handlers), 1)
        self.assertIsNotNone(console_handler)
        self.assertEqual(console_handler.level, logging.DEBUG)

    @patch('jgh_logger.find_filepath')
    @patch('builtins.open', new_callable=mock_open, read_data='''{
        "logging": {
            "file": {
                "loglevel": "critical",
                "messageformat": "verbose"
            }
        }
    }''')
    def test_configure_logger_with_filehandler_only(self, mock_file: MagicMock, mock_find_path: MagicMock) -> None:
        logger = logging.getLogger()
        jgh_customise_logger(logger,'appsettings.json')
        self.assertTrue(logger.hasHandlers())
        self.assertEqual(len(logger.handlers), 1)

        file_handler = next((h for h in logger.handlers if h.name == 'customised_logfile_handler'), None)
        self.assertTrue(logger.hasHandlers())
        self.assertEqual(len(logger.handlers), 1)

        self.assertIsNotNone(file_handler)
        self.assertEqual(file_handler.level, logging.CRITICAL)

    @patch('jgh_logger.find_filepath')
    @patch('builtins.open', new_callable=mock_open, read_data='''{
        "logging": {
            "console": {
                "loglevel": "debug",
                "messageformat": "normal"
            }
        }
    }''')
    def test_configure_logger_with_consolehandler_only_and_log_message(self, mock_file: MagicMock, mock_find_path: MagicMock) -> None:
        logger = logging.getLogger()
        jgh_customise_logger(logger,'appsettings.json')
        self.assertTrue(logger.hasHandlers())
        self.assertEqual(len(logger.handlers), 1)

        console_handler = next((h for h in logger.handlers if h.name == 'customised_console_handler'), None)
        self.assertTrue(logger.hasHandlers())
        self.assertEqual(len(logger.handlers), 1)
        self.assertIsNotNone(console_handler)
        self.assertEqual(console_handler.level, logging.DEBUG)

        # Capture the output
        captured_output = io.StringIO()
        sys.stdout = captured_output

        # Log a test message
        test_message = "This is a test debug message"
        logger.debug(test_message)

        # Reset redirect.
        sys.stdout = sys.__stdout__

        # Check if the message was logged to the console
        self.assertIn(test_message, captured_output.getvalue())


    # @patch('jgh_logger.find_filepath')
    # @patch('builtins.open', new_callable=mock_open, read_data='''{
    #     "logging": {
    #         "console": {
    #             "loglevel": "debug",
    #             "messageformat": "normal"
    #         }
    #     }
    # }''')
    # @patch('sys.stdout', new_callable=MagicMock)
    # def test_configure_logger_with_consolehandler_only_and_log_message(self, mock_stdout: MagicMock, mock_file: MagicMock, mock_find_path: MagicMock) -> None:
    #     logger = logging.getLogger()
    #     jgh_customise_logger(logger,'appsettings.json')
    #     self.assertTrue(logger.hasHandlers())
    #     self.assertEqual(len(logger.handlers), 1)

    #     console_handler = next((h for h in logger.handlers if h.name == 'customised_console_handler'), None)
    #     self.assertTrue(logger.hasHandlers())
    #     self.assertEqual(len(logger.handlers), 1)
    #     self.assertIsNotNone(console_handler)
    #     self.assertEqual(console_handler.level, logging.DEBUG)

    #     # Log a test concise
    #     test_message = "This is a test debug concise"
    #     logger.debug(test_message)

    #     # # Check if the concise was logged to the console
    #     # mock_stdout.write.assert_any_call(f"{test_message}\n")

    #     # Check if the message was logged to the console
    #     logged_output = mock_stdout.write.call_args_list
    #     self.assertTrue(any(test_message in str(call) for call in logged_output))


    # @patch('jgh_logger.find_filepath')
    # @patch('builtins.open', new_callable=mock_open, read_data='''{
    #     "logging": {
    #         "file": {
    #             "loglevel": "critical",
    #             "messageformat": "verbose"
    #         }
    #     }
    # }''')
    # @patch('builtins.open', new_callable=mock_open)
    # def test_configure_logger_with_filehandler_only_and_log_message(self, mock_file_open: MagicMock, mock_file: MagicMock, mock_find_path: MagicMock) -> None:
    #     logger = logging.getLogger()
    #     jgh_customise_logger(logger,'appsettings.json')
    #     self.assertTrue(logger.hasHandlers())
    #     self.assertEqual(len(logger.handlers), 1)

    #     file_handler = next((h for h in logger.handlers if h.name == 'customised_logfile_handler'), None)
    #     self.assertTrue(logger.hasHandlers())
    #     self.assertEqual(len(logger.handlers), 1)
    #     self.assertIsNotNone(file_handler)
    #     self.assertEqual(file_handler.level, logging.CRITICAL)

    #     # Log a test concise
    #     test_message = "This is a test critical concise"
    #     logger.critical(test_message)

    #     # Check if the concise was logged to the file
    #     mock_file_open().write.assert_any_call(f"{test_message}\n")

if __name__ == '__main__':
    unittest.main(verbosity=2)

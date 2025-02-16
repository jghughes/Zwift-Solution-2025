import unittest
import logging
from unittest.mock import patch, mock_open, MagicMock
from jgh_logger import jgh_configure_custom_logger

class TestConfigureLogger(unittest.TestCase):

    @patch('jgh_logger.find_path_to_file')
    @patch('builtins.open', new_callable=mock_open, read_data='''{
        "logging": {
            "console": {
                "loglevel": "standard",
                "messageformat": "standard"
            },
            "file": {
                "loglevel": "verbose",
                "messageformat": "verbose"
            }
        }
    }''')
    def test_configure_logger_with_valid_file(self, mock_file: MagicMock, mock_find_path: MagicMock) -> None:
        mock_find_path.return_value = 'path/to/appsettings.json'
        jgh_configure_custom_logger('appsettings.json')
        logger = logging.getLogger()
        self.assertTrue(logger.hasHandlers())
        self.assertEqual(len(logger.handlers), 2)

        console_handler = next((h for h in logger.handlers if h.name == 'console_handler'), None)
        file_handler = next((h for h in logger.handlers if h.name == 'logfile_handler'), None)

        self.assertIsNotNone(console_handler)
        self.assertIsNotNone(file_handler)
        self.assertEqual(console_handler.level, logging.DEBUG)
        self.assertEqual(file_handler.level, logging.INFO)

    # @patch('jgh_logger.find_path_to_file')
    # @patch('builtins.open', new_callable=mock_open, read_data='')
    # def test_configure_logger_with_empty_file(self, mock_file: MagicMock, mock_find_path: MagicMock) -> None:
    #     mock_find_path.return_value = 'path/to/appsettings.json'
    #     jgh_configure_custom_logger('appsettings.json')

    #     logger = logging.getLogger()
    #     self.assertTrue(logger.hasHandlers())
    #     self.assertEqual(len(logger.handlers), 1)


    # @patch('jgh_logger.find_path_to_file')
    # @patch('builtins.open', new_callable=mock_open, read_data='invalid json')
    # def test_configure_logger_with_invalid_json(self, mock_file: MagicMock, mock_find_path: MagicMock) -> None:
    #     mock_find_path.return_value = 'path/to/appsettings.json'
    #     jgh_configure_custom_logger('appsettings.json')

    #     logger = logging.getLogger()
    #     self.assertTrue(logger.hasHandlers())
    #     self.assertEqual(len(logger.handlers), 1)


    # @patch('jgh_logger.find_path_to_file')
    # def test_configure_logger_with_no_file(self, mock_find_path: MagicMock) -> None:
    #     mock_find_path.return_value = None
    #     jgh_configure_custom_logger('appsettings.json')

    #     logger = logging.getLogger()
    #     self.assertTrue(logger.hasHandlers())
    #     self.assertEqual(len(logger.handlers), 1)


    # @patch('jgh_logger.find_path_to_file')
    # @patch('builtins.open', new_callable=mock_open, read_data='''{
    #     "logging": {
    #         "console": {
    #             "loglevel": "debug",
    #             "messageformat": "standard"
    #         }
    #     }
    # }''')
    # def test_configure_logger_with_console_only(self, mock_file: MagicMock, mock_find_path: MagicMock) -> None:
    #     mock_find_path.return_value = 'path/to/appsettings.json'
    #     jgh_configure_custom_logger('appsettings.json')

    #     logger = logging.getLogger()
    #     self.assertTrue(logger.hasHandlers())
    #     self.assertEqual(len(logger.handlers), 1)

    #     console_handler = next((h for h in logger.handlers if h.name == 'console_handler'), None)
    #     self.assertIsNotNone(console_handler)
    #     self.assertEqual(console_handler.level, logging.DEBUG)

    # @patch('jgh_logger.find_path_to_file')
    # @patch('builtins.open', new_callable=mock_open, read_data='''{
    #     "logging": {
    #         "file": {
    #             "loglevel": "info",
    #             "messageformat": "verbose"
    #         }
    #     }
    # }''')
    # def test_configure_logger_with_file_only(self, mock_file: MagicMock, mock_find_path: MagicMock) -> None:
    #     mock_find_path.return_value = 'path/to/appsettings.json'
    #     jgh_configure_custom_logger('appsettings.json')

    #     logger = logging.getLogger()
    #     self.assertTrue(logger.hasHandlers())
    #     self.assertEqual(len(logger.handlers), 1)

    #     file_handler = next((h for h in logger.handlers if h.name == 'logfile_handler'), None)
    #     self.assertIsNotNone(file_handler)
    #     self.assertEqual(file_handler.level, logging.INFO)

if __name__ == '__main__':
    unittest.main(verbosity=2)

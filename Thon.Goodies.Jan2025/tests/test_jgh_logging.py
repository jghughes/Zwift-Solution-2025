import unittest
import logging
from jgh_logging import jgh_configure_logging

class TestConfigureLogger(unittest.TestCase):

    def test_configure_logger_with_valid_settingsfile_loggingsection(self) -> None:
        jgh_configure_logging('appsettingsValidConsoleAndFile.json')
        logger = logging.getLogger()
        self.assertTrue(logger.hasHandlers())
        self.assertEqual(len(logger.handlers), 2)
        console_handler = next((h for h in logger.handlers if h.name == 'consoleHandler'), None)
        file_handler = next((h for h in logger.handlers if h.name == 'fileHandler'), None)
        self.assertIsNotNone(console_handler)
        self.assertIsNotNone(file_handler)
        if console_handler is not None:
            self.assertEqual(console_handler.level, logging.DEBUG)
        if file_handler is not None:
            self.assertEqual(file_handler.level, logging.CRITICAL)


    def test_configure_logger_with_empty_settingsfile(self) -> None:
        jgh_configure_logging( 'appsettingsEmpty.json')
        logger = logging.getLogger()
        self.assertTrue(logger.hasHandlers())
        self.assertEqual(len(logger.handlers), 1)


    def test_configure_logger_with_invalid_settingsjson(self) -> None:
        jgh_configure_logging('appsettingsInvalid.json')
        logger = logging.getLogger()
        self.assertTrue(logger.hasHandlers())
        self.assertEqual(len(logger.handlers), 1)


    def test_configure_logger_with_no_settingsfile(self) -> None:
        jgh_configure_logging(None)
        logger = logging.getLogger()
        self.assertTrue(logger.hasHandlers())
        self.assertEqual(len(logger.handlers), 1)


    def test_configure_logger_with_consolehandler_only(self) -> None:
        jgh_configure_logging('appsettingsValidConsoleOnly.json')
        logger = logging.getLogger()
        self.assertTrue(logger.hasHandlers())
        self.assertEqual(len(logger.handlers), 1)
        console_handler = next((h for h in logger.handlers if h.name == 'consoleHandler'), None)
        self.assertIsNotNone(console_handler)
        if console_handler is not None:
            self.assertEqual(console_handler.level, logging.DEBUG)


    def test_configure_logger_with_filehandler_only(self) -> None:
        jgh_configure_logging('appsettingsValidFileOnly.json')
        logger = logging.getLogger()
        self.assertTrue(logger.hasHandlers())
        self.assertEqual(len(logger.handlers), 1)
        file_handler = next((h for h in logger.handlers if h.name == 'fileHandler'), None)
        self.assertIsNotNone(file_handler)
        if file_handler is not None:
            self.assertEqual(file_handler.level, logging.CRITICAL)


    def test_configure_logger_with_both_handlers_and_write_log_messages(self) -> None:
        jgh_configure_logging('appsettingsValidConsoleAndFile.json') # This test is expecting a settings file specifying a console handler and a file handler.
        logger = logging.getLogger()
        self.assertTrue(logger.hasHandlers())
        self.assertEqual(len(logger.handlers), 2)
        console_handler = next((h for h in logger.handlers if h.name == 'consoleHandler'), None)
        file_handler = next((h for h in logger.handlers if h.name == 'fileHandler'), None)
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

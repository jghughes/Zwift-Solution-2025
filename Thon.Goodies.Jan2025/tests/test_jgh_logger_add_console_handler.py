import unittest
from unittest.mock import patch, MagicMock, Mock
import logging
from jgh_logger import add_console_handler, HANDLER_NAME_CONSOLE

class TestAddConsoleHandler(unittest.TestCase):

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

    def test_add_console_handler(self):
        """
        Test that the console handler is added to the logger.
        """
        add_console_handler(self.logger)
        handler_names = [handler.get_name() for handler in self.logger.handlers]
        self.assertIn(HANDLER_NAME_CONSOLE, handler_names)

    def test_console_handler_level(self):
        """
        Test that the console handler level is set to DEBUG.
        """
        add_console_handler(self.logger)
        console_handler = next(handler for handler in self.logger.handlers if handler.get_name() == HANDLER_NAME_CONSOLE)
        self.assertEqual(console_handler.level, logging.DEBUG)

    def test_console_handler_formatter(self):
        """
        Test that the console handler formatter is set correctly.
        """
        add_console_handler(self.logger)
        console_handler = next(handler for handler in self.logger.handlers if handler.get_name() == HANDLER_NAME_CONSOLE)
        self.assertIsInstance(console_handler.formatter, logging.Formatter)
        self.assertEqual(console_handler.formatter._fmt.strip(), "%(message)s")

    @patch("jgh_logger.logging.StreamHandler", new_callable=MagicMock)
    def test_add_console_handler_exception(self, mock_stream_handler: Mock):
        """
        Test that an exception is raised if adding the console handler fails.
        """
        mock_stream_handler.side_effect = Exception("Test exception")
        with self.assertRaises(RuntimeError) as context:
            add_console_handler(self.logger)
        self.assertIn("Error configuring console logging", str(context.exception))

if __name__ == "__main__":
    unittest.main(verbosity=2)

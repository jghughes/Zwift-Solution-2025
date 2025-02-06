"""
This module provides a function to configure logging for the application.

The `configure_logging` function sets up logging handlers for different log levels and formats
for both console and file outputs. It allows customization of log filenames and logging levels.

Example usage:
    from jgh_logging_config import configure_logging
    import logging

    configure_logging(logging.DEBUG)
    logger = logging.getLogger(__name__)

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
"""

import os
import logging
from typing import Dict, Optional
from pythonjsonlogger import jsonlogger


def configure_logging(logging_level: int = logging.DEBUG, log_filenames: Optional[Dict[str, str]] = None) -> None:
    """
    Configures logging for the application. The function sets up handlers for different log 
    levels and formats for console and file outputs.

    Parameters:
    logging_level (int): The logging level to set for the root logger. Default is logging.DEBUG.
    log_filenames (Optional[Dict[str, str]]): A dictionary mapping log levels to filenames. If None, default filenames are used.

    Default log filenames:
        - "debug": "log_debug.log"
        - "info": "log_info.log"
        - "warning": "log_warning.log"
        - "error": "log_error.log"
        - "critical": "log_critical.log"

    The function sets up handlers for different log levels and formats for console and file outputs.
    """

    if log_filenames is None:
        log_filenames = {
            "debug": "log_debug.log",
            "info": "log_info.log",
            "warning": "log_warning.log",
            "error": "log_error.log",
            "critical": "log_critical.log"
        }

    # Ensure all log filenames are absolute paths
    log_filenames = {level: os.path.abspath(path) for level, path in log_filenames.items()}

    # Define logging parameters for console
    log_format_for_console = """
    %(asctime)s
        Level: %(levelname)s
        Module: %(module)s
        Function: %(funcName)s
        Line: %(lineno)d
        Message: %(message)s
    """
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  # NB. Console handler should be DEBUG
    console_handler.setFormatter(logging.Formatter(log_format_for_console))
    console_handler.set_name("jgh_logging_module_stream_handler_for_console")

    # Define logging parameters for log files
    # JSON format for file outputs
    json_log_format_for_file = jsonlogger.JsonFormatter(# type: ignore 
        json_indent=4,
        fmt='%(asctime)s %(levelname)s %(module)s %(funcName)s %(lineno)d %(pathname)s %(threadName)s %(process)d %(message)s'
        )  
    # Create separate file handlers for different severity levels
    log_filehandler_debug = logging.FileHandler(log_filenames.get("debug", "fallback_log_debug.log"))
    log_filehandler_info = logging.FileHandler(log_filenames.get("info", "fallback_log_info.log"))
    log_filehandler_warning = logging.FileHandler(log_filenames.get("warning", "fallback_log_warning.log"))
    log_filehandler_error = logging.FileHandler(log_filenames.get("error", "fallback_log_error.log"))
    log_filehandler_critical = logging.FileHandler(log_filenames.get("critical", "fallback_log_critical.log"))
    # Set level for corresponding handlers
    log_filehandler_debug.setLevel(logging.DEBUG)
    log_filehandler_info.setLevel(logging.INFO)
    log_filehandler_warning.setLevel(logging.WARNING)
    log_filehandler_error.setLevel(logging.ERROR)
    log_filehandler_critical.setLevel(logging.CRITICAL)
    # Set message format for files/console
    log_filehandler_debug.setFormatter(json_log_format_for_file)
    log_filehandler_info.setFormatter(json_log_format_for_file)
    log_filehandler_warning.setFormatter(json_log_format_for_file)
    log_filehandler_error.setFormatter(json_log_format_for_file)
    log_filehandler_critical.setFormatter(json_log_format_for_file)
    # Set some handy names
    log_filehandler_debug.set_name("jgh_logging_module_filehandler_for_debug")
    log_filehandler_info.set_name("jgh_logging_module_filehandler_for_info")
    log_filehandler_warning.set_name("jgh_logging_module_filehandler_for_warning")
    log_filehandler_error.set_name("jgh_logging_module_filehandler_for_error")
    log_filehandler_critical.set_name("jgh_logging_module_filehandler_for_critical")
 
 # Get the root logger and set its level
    logger = logging.getLogger()
    logger.setLevel(logging_level)
    # Clear existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()
    # Final step: add the handlers to the logger
    logger.addHandler(log_filehandler_debug)
    logger.addHandler(log_filehandler_info)
    logger.addHandler(log_filehandler_warning)
    logger.addHandler(log_filehandler_error)
    logger.addHandler(log_filehandler_critical)
    logger.addHandler(console_handler)


# simple illustration of using the configure_logging function

if __name__ == "__main__":

    configure_logging(logging.DEBUG)
    logger = logging.getLogger()  # Get the root logger

    def example_function() -> None:
        # Display names of handlers
        print("INFO: handlers attached to the logger:")
        for handler in logger.handlers:
            print(f"\tHandler name: {handler.get_name()}")

        # Display a list of the absolute file paths to which the file handlers will write
        log_file_paths = [handler.baseFilename for handler in logger.handlers if isinstance(handler, logging.FileHandler)]
        print(f"INFO: filepaths specified for each file handler:")
        for path in log_file_paths:
            print(f"\t{os.path.abspath(path)}")

        # Log messages at different levels
        print(f"INFO: illustrative log messages displayed on the console and simultaneously saved in the respective log files:")
        logger.debug("This is an illustrative debug message")
        logger.info("This is an illustrative info message")
        logger.warning("This is an illustrative warning message")
        logger.error("This is an illustrative error message")
        logger.critical("This is an illustrative critical message")

    # Call the example function
    example_function()

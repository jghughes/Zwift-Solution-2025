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

def configure_logging(logging_level: int = logging.DEBUG, log_filenames: Optional[Dict[str, str]] = None) -> None:
    """
    Configures logging for the application. The function sets up handlers for different log 
    levels and formats for console and file outputs.

    Parameters:
    logging_level (int): The logging level to set for the root logger. Default is logging.DEBUG.
    log_filenames (Optional[Dict[str, str]]): A dictionary mapping log levels to filenames. If None, default filenames are used.

    Default log filenames:
        - "debug": "log_debug_log.log"
        - "info": "log_info_log.log"
        - "warning": "log_warning_log.log"
        - "error": "log_error_log.log"
        - "critical": "log_critical_log.log"

    The function sets up handlers for different log levels and formats for console and file outputs.
    """

    if log_filenames is None:
        log_filenames = {
            "debug": "log_debug_log.log",
            "info": "log_info_log.log",
            "warning": "log_warning_log.log",
            "error": "log_error_log.log",
            "critical": "log_critical_log.log"
        }

    # Define different formats for console and file outputs
    log_format_for_console = """
    %(asctime)s
        Level: %(levelname)s
        Module: %(module)s
        Function: %(funcName)s
        Line: %(lineno)d
        Message: %(message)s
    """

    log_format_for_file = """
    %(asctime)s
        Level: %(levelname)s
        Module: %(module)s
        Function: %(funcName)s
        Line: %(lineno)d
        File: %(pathname)s
        Thread: %(threadName)s
        Process: %(process)d
        Message: %(message)s
    """

    # Create spearte handlers for different severity levels
    debug_handler = logging.FileHandler(log_filenames.get("debug", "fallback_debug_log.log"))
    info_handler = logging.FileHandler(log_filenames.get("info", "fallback_info_log.log"))
    warning_handler = logging.FileHandler(log_filenames.get("warning", "fallback_warning_log.log"))
    error_handler = logging.FileHandler(log_filenames.get("error", "fallback_error_log.log"))
    critical_handler = logging.FileHandler(log_filenames.get("critical", "fallback_critical_log.log"))
    console_handler = logging.StreamHandler()
    # Set level for corresponding handlers
    debug_handler.setLevel(logging.DEBUG)
    info_handler.setLevel(logging.INFO)
    warning_handler.setLevel(logging.WARNING)
    error_handler.setLevel(logging.ERROR)
    critical_handler.setLevel(logging.CRITICAL)
    console_handler.setLevel(logging.DEBUG)  # NB. Console handler should be DEBUG
    # Set message format for files/console
    debug_handler.setFormatter(logging.Formatter(log_format_for_file))
    info_handler.setFormatter(logging.Formatter(log_format_for_file))
    warning_handler.setFormatter(logging.Formatter(log_format_for_file))
    error_handler.setFormatter(logging.Formatter(log_format_for_file))
    critical_handler.setFormatter(logging.Formatter(log_format_for_file))
    console_handler.setFormatter(logging.Formatter(log_format_for_console))
    # Set some handy names
    debug_handler.set_name("jgh_logging_module_debug_handler")
    info_handler.set_name("jgh_logging_module_info_handler")
    warning_handler.set_name("jgh_logging_module_warning_handler")
    error_handler.set_name("jgh_logging_module_error_handler")
    critical_handler.set_name("jgh_logging_module_critical_handler")
    console_handler.set_name("jgh_logging_module_console")
    # Get the root logger and set its level
    logger = logging.getLogger()
    logger.setLevel(logging_level)
    # Clear existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()
    # Final step: add the handlers to the logger
    logger.addHandler(debug_handler)
    logger.addHandler(info_handler)
    logger.addHandler(warning_handler)
    logger.addHandler(error_handler)
    logger.addHandler(critical_handler)
    logger.addHandler(console_handler)


# simple illustration of using the configure_logging function

if __name__ == "__main__":
    configure_logging(logging.DEBUG)
    logger = logging.getLogger()  # Get the root logger

    def example_function() -> None:
       # Log a message at each level to ensure handlers are initialized
        # logger.debug("Initializing handlers to retrieve file paths")
        # logger.info("Initializing handlers to retrieve file paths")
        # logger.warning("Initializing handlers to retrieve file paths")
        # logger.error("Initializing handlers to retrieve file paths")
        # logger.critical("Initializing handlers to retrieve file paths")

        # Debug print to verify handlers
        print("INFO: handlers attached to the logger:")
        for handler in logger.handlers:
            print(f"\tHandler name: {handler.get_name()}")

        # Display a list of the absolute file paths to which the logger will write
        log_file_paths = [handler.baseFilename for handler in logger.handlers if isinstance(handler, logging.FileHandler)]
        print(f"INFO: filepaths specified for each file handler:")
        for path in log_file_paths:
            print(f"\t{os.path.abspath(path)}")

        # Log messages at different levels
        print(f"INFO: illustrative log messages displayed on the console and simultaneously saved in the respective log files:")
        logger.debug("This is an illustrative debug message")
        logger.info("This is an illustrativen info message")
        logger.warning("This is an illustrative warning message")
        logger.error("This is an illustrativen error message")
        logger.critical("This is an illustrative critical message")

    # Call the example function
    example_function()

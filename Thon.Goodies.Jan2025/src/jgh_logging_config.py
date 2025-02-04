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

    # Define different formats for different severity levels
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
        Message: %(message)s
    """
    # Create handlers for different severity levels
    debug_handler = logging.FileHandler(log_filenames.get("debug", "fallback_debug_log.log"))
    info_handler = logging.FileHandler(log_filenames.get("info", "fallback_info_log.log"))
    warning_handler = logging.FileHandler(log_filenames.get("warning", "fallback_warning_log.log"))
    error_handler = logging.FileHandler(log_filenames.get("error", "fallback_error_log.log"))
    critical_handler = logging.FileHandler(log_filenames.get("critical", "fallback_critical_log.log"))
    console_handler = logging.StreamHandler()

    # Set level and format for handlers
    debug_handler.setLevel(logging.DEBUG)
    info_handler.setLevel(logging.INFO)
    warning_handler.setLevel(logging.WARNING)
    error_handler.setLevel(logging.ERROR)
    critical_handler.setLevel(logging.CRITICAL)
    console_handler.setLevel(logging.DEBUG)  # NB. Console handler should be DEBUG

    debug_handler.setFormatter(logging.Formatter(log_format_for_file))
    info_handler.setFormatter(logging.Formatter(log_format_for_file))
    warning_handler.setFormatter(logging.Formatter(log_format_for_file))
    error_handler.setFormatter(logging.Formatter(log_format_for_file))
    critical_handler.setFormatter(logging.Formatter(log_format_for_file))
    console_handler.setFormatter(logging.Formatter(log_format_for_console))

    # Get the root logger and set its level
    logger = logging.getLogger()
    #   logger = logging.getLogger(__name__)
    logger.setLevel(logging_level)

       # Clear existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    # Add handlers to the logger
    logger.addHandler(debug_handler)
    logger.addHandler(info_handler)
    logger.addHandler(warning_handler)
    logger.addHandler(error_handler)
    logger.addHandler(critical_handler)
    logger.addHandler(console_handler)



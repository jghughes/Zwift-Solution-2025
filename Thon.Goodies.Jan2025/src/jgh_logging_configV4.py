import os
import json
import logging
from typing import Dict, Optional, List, Union
from dataclasses import dataclass
from pythonjsonlogger import jsonlogger

# Define constants for log levels
LOG_LEVEL_DEBUG = "debug"
LOG_LEVEL_INFO = "info"
LOG_LEVEL_WARNING = "warning"
LOG_LEVEL_ERROR = "error"
LOG_LEVEL_CRITICAL = "critical"

# Define constants for handler names
HANDLER_NAME_CONSOLE = "jgh_logging_module_stream_handler_for_console"
HANDLER_NAME_DEBUG = "jgh_logging_module_filehandler_for_debug"
HANDLER_NAME_INFO = "jgh_logging_module_filehandler_for_info"
HANDLER_NAME_WARNING = "jgh_logging_module_filehandler_for_warning"
HANDLER_NAME_ERROR = "jgh_logging_module_filehandler_for_error"
HANDLER_NAME_CRITICAL = "jgh_logging_module_filehandler_for_critical"

# Define constants for configuration keys
CONFIG_LOGGING = "logging"
LOGFILES_FOLDERPATH = "logfile_folderpath"
DEBUG_FILE_NAME = "debug"
INFO_FILE_NAME = "info"
WARNING_FILE_NAME = "warning"
ERROR_FILE_NAME = "error"
CRITICAL_FILE_NAME = "critical"

@dataclass
class LogFilePaths:
    debug: Optional[str] = None
    info: Optional[str] = None
    warning: Optional[str] = None
    error: Optional[str] = None
    critical: Optional[str] = None

@dataclass
class LogFilenames:
    """
    A dataclass to hold log filenames for different log levels.

    Attributes:
    -----------
    Name                  | Type         | Description
    ----------------------|--------------|-------------------------------------------
    logfiles_folder       | str | None   | The base directory path where log files will be stored. Must be an absolute path. Default is None.
    debug_filename        | str | None   | The filename for debug level logs. Must end with .log. Default is None.
    info_filename         | str | None   | The filename for info level logs. Must end with .log. Default is None.
    warning_filename      | str | None   | The filename for warning level logs. Must end with .log. Default is None.
    error_filename        | str | None   | The filename for error level logs. Must end with .log. Default is None.
    critical_filename     | str | None   | The filename for critical level logs. Must end with .log. Default is None.
    """

    logfiles_folder: str | None = None
    debug_filename: str | None = None
    info_filename: str | None = None
    warning_filename: str | None = None
    error_filename: str | None = None
    critical_filename: str | None = None

    def __post_init__(self):
        # Validate logfiles_folder
        if self.logfiles_folder and not os.path.isabs(self.logfiles_folder):
            raise ValueError(f"logfiles_folder must be an absolute path: {self.logfiles_folder}")

        # Validate filenames
        invalid_filenames: List[str] = []
        for level, filename in self.__dict__.items():
            if level != "logfiles_folder" and filename is not None:
                if not filename.endswith(".log"):
                    invalid_filenames.append(f"{level}: {filename}")

        if invalid_filenames:
            raise ValueError(f"The following filenames are invalid (must end with .log): {', '.join(invalid_filenames)}")

    def get_absolute_paths(self) -> Optional[LogFilePaths]:
        """
        Returns an LogFilePaths dataclass with absolute file paths for each log level.

        Returns:
        LogFilePaths: A dataclass with absolute file paths for each log level, or None if logfiles_folder is None.
        """
        if self.logfiles_folder is None:
            return None

        return LogFilePaths(
            debug=os.path.join(self.logfiles_folder, self.debug_filename) if self.debug_filename else None,
            info=os.path.join(self.logfiles_folder, self.info_filename) if self.info_filename else None,
            warning=os.path.join(self.logfiles_folder, self.warning_filename) if self.warning_filename else None,
            error=os.path.join(self.logfiles_folder, self.error_filename) if self.error_filename else None,
            critical=os.path.join(self.logfiles_folder, self.critical_filename) if self.critical_filename else None
        )


def configure_logging() -> None:
    """
    Configures logging for the application. The function sets up handlers for different log 
    levels and formats for console and file outputs.

    The function loads the appropriate settings file based on the environment (development or production).
    If the settings file cannot be loaded or does not contain the logging section, logging is configured
    to write to the console only.

    Example usage:
        from jgh_logging_config import configure_logging
        import logging

        configure_logging()
        logger = logging.getLogger(__name__)

        logger.debug("This is a debug message")
        logger.info("This is an info message")
        logger.warning("This is a warning message")
        logger.error("This is an error message")
        logger.critical("This is a critical message")
    """
    log_filenames: Optional[LogFilenames] = None
    settings_file: str = ""
    try:
        # Determine the environment (default to development)
        environment = os.getenv("APP_ENV", "development")
        # Get the root directory of the project
        root_dir = os.getenv("APP_ROOT", os.path.dirname(__file__)) # Default to the directory of this file
        # Construct the path to the settings file based on the environment
        settings_file = os.path.join(root_dir, f"settings.{environment}.json")
        # Load configuration from the appropriate settings file
        with open(settings_file, "r") as config_file:
            config = json.load(config_file)

        # Ensure the logging section exists
        if CONFIG_LOGGING in config:
            # Instantiate the LogFilenames dataclass with the loaded configuration
            log_filenames = LogFilenames(
                logfiles_folder=config[CONFIG_LOGGING].get(LOGFILES_FOLDERPATH),
                debug_filename=config[CONFIG_LOGGING].get(DEBUG_FILE_NAME),
                info_filename=config[CONFIG_LOGGING].get(INFO_FILE_NAME),
                warning_filename=config[CONFIG_LOGGING].get(WARNING_FILE_NAME),
                error_filename=config[CONFIG_LOGGING].get(ERROR_FILE_NAME),
                critical_filename=config[CONFIG_LOGGING].get(CRITICAL_FILE_NAME)
            )
        else:
            print(f"ERROR: '{CONFIG_LOGGING}' section not found in {settings_file}")

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"ERROR: Failed to load configuration from {settings_file}: {e}")

    try:
        # get the logger ready
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        if logger.hasHandlers():
            logger.handlers.clear()

        # Define logging parameters for console
        log_format_for_console = """
        %(asctime)s
            Level: %(levelname)s
            Module: %(module)s
            Function: %(funcName)s
            Line: %(lineno)d
            Message: %(message)s
        """

        # get the console ready to go
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)  # NB. Console handler should be DEBUG
        console_handler.setFormatter(logging.Formatter(log_format_for_console))
        console_handler.set_name(HANDLER_NAME_CONSOLE)
        logger.addHandler(console_handler)

        # return if log_filenames is None
        if log_filenames is None or not log_filenames.logfiles_folder:
            return

        # rephrase all log filenames as absolute paths
        absolute_log_filenames = log_filenames.get_absolute_paths()

        # JSON format for all files
        json_log_format_for_file = jsonlogger.JsonFormatter( # type: ignore
            json_indent=4,
            fmt='%(asctime)s %(levellevel)s %(module)s %(funcName)s %(lineno)d %(pathname)s %(threadName)s %(process)d %(message)s'
        )

        # add optional file handlers if the user specified filenames for them

        if absolute_log_filenames.debug:
            log_filehandler_debug = logging.FileHandler(absolute_log_filenames.debug)
            log_filehandler_debug.setLevel(logging.DEBUG)
            log_filehandler_debug.setFormatter(json_log_format_for_file)
            log_filehandler_debug.set_name(HANDLER_NAME_DEBUG)
            logger.addHandler(log_filehandler_debug)

        if absolute_log_filenames.info:
            log_filehandler_info = logging.FileHandler(absolute_log_filenames.info)
            log_filehandler_info.setLevel(logging.INFO)
            log_filehandler_info.setFormatter(json_log_format_for_file)
            log_filehandler_info.set_name(HANDLER_NAME_INFO)
            logger.addHandler(log_filehandler_info)

        if absolute_log_filenames.warning:
            log_filehandler_warning = logging.FileHandler(absolute_log_filenames.warning)
            log_filehandler_warning.setLevel(logging.WARNING)
            log_filehandler_warning.setFormatter(json_log_format_for_file)
            log_filehandler_warning.set_name(HANDLER_NAME_WARNING)
            logger.addHandler(log_filehandler_warning)

        if absolute_log_filenames.error:
            log_filehandler_error = logging.FileHandler(absolute_log_filenames.error)
            log_filehandler_error.setLevel(logging.ERROR)
            log_filehandler_error.setFormatter(json_log_format_for_file)
            log_filehandler_error.set_name(HANDLER_NAME_ERROR)
            logger.addHandler(log_filehandler_error)

        if absolute_log_filenames.critical:
            log_filehandler_critical = logging.FileHandler(absolute_log_filenames.critical)
            log_filehandler_critical.setLevel(logging.CRITICAL)
            log_filehandler_critical.setFormatter(json_log_format_for_file)
            log_filehandler_critical.set_name(HANDLER_NAME_CRITICAL)
            logger.addHandler(log_filehandler_critical)

    except Exception as e:
        raise RuntimeError(f"Error configuring logging: {e}")

# simple illustration of using the configure_logging function

if __name__ == "__main__":

    # set up environment variables manually for this mickey mouse illustration. ensure thete is a test.settings.json file is in the same folder as this file
    os.environ["APP_ENV"] = "test"
    os.environ["APP_ROOT"] = os.path.dirname(__file__) 
    
    configure_logging()
    logger = logging.getLogger()  # Get the root logger

    def example_function() -> None:
        # Display names of handlers
        print("INFO: handlers attached to the logger:")
        for handler in logger.handlers:
            print(f"\tHandler name: {handler.get_name()}")

        # Display a list of the absolute file paths to which the file handlers will write
        log_file_paths = [handler.baseFilename for handler in logger.handlers if isinstance(handler, logging.FileHandler)]
        print(f"INFO: filepaths specified for log file handlers:")
        for path in log_file_paths:
            print(f"\t{os.path.abspath(path)}")

        # Log messages at different levels
        print(f"INFO: illustrative log messages displayed on the console and respective log files if specified:")
        logger.debug("This is an illustrative debug message")
        logger.info("This is an illustrative info message")
        logger.warning("This is an illustrative warning message")
        logger.error("This is an illustrative error message")
        logger.critical("This is an illustrative critical message")

    # Call the example function
    example_function()

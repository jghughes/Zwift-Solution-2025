import os
import json
import logging
from typing import Dict
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

@dataclass
class LogFilenames:
    """
    A dataclass to hold log filenames for different log levels.

    Attributes:
    -----------
    Name          | Type         | Description
    --------------|--------------|-------------------------------------------
    base_filepath | str          | The base directory path where log files will be stored. Must be an absolute path.
    debug         | str          | The filename for debug level logs. Must end with .log.
    info          | Optional[str]| The filename for info level logs. Must end with .log. Default is None.
    warning       | Optional[str]| The filename for warning level logs. Must end with .log. Default is None.
    error         | Optional[str]| The filename for error level logs. Must end with .log. Default is None.
    critical      | Optional[str]| The filename for critical level logs. Must end with .log. Default is None.
    """

    base_filepath: str
    debug: str | None = None
    info: str | None = None
    warning: str | None = None
    error: str | None = None
    critical: str | None = None

    def __post_init__(self):
        # Validate base_filepath
        if not os.path.isabs(self.base_filepath):
            raise ValueError(f"base_filepath must be an absolute path: {self.base_filepath}")

        # Validate filenames
        invalid_filenames = []
        for level, filename in self.__dict__.items():
            if level != "base_filepath" and filename is not None:
                if not filename.endswith(".log"):
                    invalid_filenames.append(f"{level}: {filename}")

        if invalid_filenames:
            raise ValueError(f"The following filenames are invalid (must end with .log): {', '.join(invalid_filenames)}")

    def get_absolute_paths(self) -> Dict[str, str | None]:
        """
        Returns a dictionary mapping log levels to their absolute file paths.

        Returns:
        Dict[str, str | None]: A dictionary with log levels as keys and absolute file paths as values.
        """
        return {
            LOG_LEVEL_DEBUG: os.path.join(self.base_filepath, self.debug) if self.debug else None,
            LOG_LEVEL_INFO: os.path.join(self.base_filepath, self.info) if self.info else None,
            LOG_LEVEL_WARNING: os.path.join(self.base_filepath, self.warning) if self.warning else None,
            LOG_LEVEL_ERROR: os.path.join(self.base_filepath, self.error) if self.error else None,
            LOG_LEVEL_CRITICAL: os.path.join(self.base_filepath, self.critical) if self.critical else None
        }

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
    log_filenames = None
    try:
        # Determine the environment (default to development)
        environment = os.getenv("APP_ENV", "development")
        settings_file = f"settings.{environment}.json"

        # Load configuration from the appropriate settings file
        with open(settings_file, "r") as config_file:
            config = json.load(config_file)

        # Ensure the logging section exists
        if "logging" in config:
            # Instantiate the LogFilenames dataclass with the loaded configuration
            log_filenames = LogFilenames(
                base_filepath=config["logging"].get("base_filepath"),
                debug=config["logging"].get("debug"),
                info=config["logging"].get("info"),
                warning=config["logging"].get("warning"),
                error=config["logging"].get("error"),
                critical=config["logging"].get("critical")
            )
        else:
            print(f"ERROR: 'logging' section not found in {settings_file}")

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
            Level: %(levellevel)s
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
        if log_filenames is None:
            return

        # Validate that log_filenames is minimally valid with a base_filepath
        if not log_filenames.base_filepath:
            raise ValueError("base_filepath must be provided and not None.")

        # rephrase all log filenames as absolute paths
        absolute_log_filenames = log_filenames.get_absolute_paths()

        # JSON format for all files
        json_log_format_for_file = jsonlogger.JsonFormatter( # type: ignore
            json_indent=4,
            fmt='%(asctime)s %(levellevel)s %(module)s %(funcName)s %(lineno)d %(pathname)s %(threadName)s %(process)d %(message)s'
        )

        # add optional file handlers if the user specified filenames for them

        if absolute_log_filenames[LOG_LEVEL_DEBUG]:
            log_filehandler_debug = logging.FileHandler(absolute_log_filenames[LOG_LEVEL_DEBUG])
            log_filehandler_debug.setLevel(logging.DEBUG)
            log_filehandler_debug.setFormatter(json_log_format_for_file)
            log_filehandler_debug.set_name(HANDLER_NAME_DEBUG)
            logger.addHandler(log_filehandler_debug)

        if absolute_log_filenames[LOG_LEVEL_INFO]:
            log_filehandler_info = logging.FileHandler(absolute_log_filenames[LOG_LEVEL_INFO])
            log_filehandler_info.setLevel(logging.INFO)
            log_filehandler_info.setFormatter(json_log_format_for_file)
            log_filehandler_info.set_name(HANDLER_NAME_INFO)
            logger.addHandler(log_filehandler_info)

        if absolute_log_filenames[LOG_LEVEL_WARNING]:
            log_filehandler_warning = logging.FileHandler(absolute_log_filenames[LOG_LEVEL_WARNING])
            log_filehandler_warning.setLevel(logging.WARNING)
            log_filehandler_warning.setFormatter(json_log_format_for_file)
            log_filehandler_warning.set_name(HANDLER_NAME_WARNING)
            logger.addHandler(log_filehandler_warning)

        if absolute_log_filenames[LOG_LEVEL_ERROR]:
            log_filehandler_error = logging.FileHandler(absolute_log_filenames[LOG_LEVEL_ERROR])
            log_filehandler_error.setLevel(logging.ERROR)
            log_filehandler_error.setFormatter(json_log_format_for_file)
            log_filehandler_error.set_name(HANDLER_NAME_ERROR)
            logger.addHandler(log_filehandler_error)

        if absolute_log_filenames[LOG_LEVEL_CRITICAL]:
            log_filehandler_critical = logging.FileHandler(absolute_log_filenames[LOG_LEVEL_CRITICAL])
            log_filehandler_critical.setLevel(logging.CRITICAL)
            log_filehandler_critical.setFormatter(json_log_format_for_file)
            log_filehandler_critical.set_name(HANDLER_NAME_CRITICAL)
            logger.addHandler(log_filehandler_critical)

    except Exception as e:
        raise RuntimeError(f"Error configuring logging: {e}")

# simple illustration of using the configure_logging function

if __name__ == "__main__":
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

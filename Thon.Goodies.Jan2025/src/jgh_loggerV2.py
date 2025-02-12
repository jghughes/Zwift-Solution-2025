import os
import json
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional
from dataclasses import dataclass
from pythonjsonlogger import jsonlogger

from pydantic import BaseModel
import jgh_file_finder
from jgh_serialization import JghSerialization




# Constants for log levels
LOG_LEVEL_DEBUG = "debug"
LOG_LEVEL_INFO = "info"
LOG_LEVEL_WARNING = "warning"
LOG_LEVEL_ERROR = "error"
LOG_LEVEL_CRITICAL = "critical"

# Constants for handler names - cosmetic
HANDLER_NAME_CONSOLE = "stream_handler_for_console"
HANDLER_NAME_DEBUG = "filehandler_for_debug"
HANDLER_NAME_INFO = "filehandler_for_info"
HANDLER_NAME_WARNING = "filehandler_for_warning"
HANDLER_NAME_ERROR = "filehandler_for_error"
HANDLER_NAME_CRITICAL = "filehandler_for_critical"

# Constants for JSON field names - must be same as in settings files
CONFIG_LOGGING = "logging"
LOGFILES_FOLDERPATH = "path"
DEBUG_FILE_NAME = "debug_filename"
INFO_FILE_NAME = "info_filename"
WARNING_FILE_NAME = "warning_filename"
ERROR_FILE_NAME = "error_filename"
CRITICAL_FILE_NAME = "critical_filename"


@dataclass
class LogFilePathCompendium:
    debug_filepath: str | None = None
    info_filepath: str | None = None
    warning_filepath: str | None = None
    error_filepath: str | None = None
    critical_filepath: str | None = None

@dataclass
class LogFilePathSegmentCompendium:
    storage_dirpath: str | None = None
    debug_filename: str | None = None
    info_filename: str | None = None
    warning_filename: str | None = None
    error_filename: str | None = None
    critical_filename: str | None = None

def add_console_handler(logger: logging.Logger, appsettings_dto : Optional[AppSettingsDataTransferObject] = None) -> None:
    """
    Do not call this from client code.

    Adds a console handler to the provided logger.

    Args:
        logger (logging.Logger): The logger to which the console handler will be added.
    """

    try:
        log_format_for_console = """%(message)s"""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(logging.Formatter(log_format_for_console))
        console_handler.set_name(HANDLER_NAME_CONSOLE)
        logger.addHandler(console_handler)

    except Exception as e:
        raise RuntimeError(f"Error configuring console logging: {e}")

def read_logfile_settings() -> Optional[LogFilePathSegmentCompendium]:
    """
    Do not call this from client code.

    Loads logging settings from a JSON configuration file based on the environment.

    This method will look for a settings file in the root directory with the name:
    settings.{environment}.json

    The three options for {environment} are 'test', 'development', and 'production'.

    The method expects the settings file to have the following format and content:
    {
        "logging": {
            "path": "your/absolute/path/to/log/files",
            "debug_filename": "yourdebug.log",
            "info_filename": "yourinfo.log",
            "warning_filename": "yourwarning.log",
            "error_filename": "yourerror.log",
            "critical_filename": "yourcritical.log"
        }
    }

    The settings file specifies the directory path where log files will be saved, and the names of one or more desired log files.
    Log files will be created if they do not exist.

    The `storage_dirpath` must be an absolute path and must already exist. If either of these requirements
    are not satisfied, the method returns None and as a result, no logging to file will be done.

    Each log filename must end in .log and will be skipped if not. Other than this requirement, the filenames can be anything.

    Returns:
        Optional[LogFilePathSegmentCompendium]: A compendium of log file path segments if settings are found and valid, otherwise None.
    """
    try:
        environment = os.getenv("APP_ENV", "development")
        root_dir = os.getenv("APP_ROOT", os.path.dirname(__file__))
        settings_file = os.path.join(root_dir, f"settings.{environment}.json")
        with open(settings_file, "r") as config_file:
            config = json.load(config_file)

        if CONFIG_LOGGING in config:
            return LogFilePathSegmentCompendium(
                storage_dirpath=config[CONFIG_LOGGING].get(LOGFILES_FOLDERPATH),
                debug_filename=config[CONFIG_LOGGING].get(DEBUG_FILE_NAME),
                info_filename=config[CONFIG_LOGGING].get(INFO_FILE_NAME),
                warning_filename=config[CONFIG_LOGGING].get(WARNING_FILE_NAME),
                error_filename=config[CONFIG_LOGGING].get(ERROR_FILE_NAME),
                critical_filename=config[CONFIG_LOGGING].get(CRITICAL_FILE_NAME)
            )
        else:
            return None

    except (FileNotFoundError, json.JSONDecodeError) as e:
        return None

def validate_logfile_settings(segments_compendium: LogFilePathSegmentCompendium) -> Optional[LogFilePathCompendium]:
    """
    Do not call this from client code.

    Validates and constructs absolute paths for log files based on the provided segments compendium.

    Args:
        segments_compendium (LogFilePathSegmentCompendium): The segments compendium containing log file path segments.

    Returns:
        Optional[LogFilePathCompendium]: A compendium of validated log file paths if valid, otherwise None.
    """

    if segments_compendium.storage_dirpath is None:
        return None

    if segments_compendium.storage_dirpath and not os.path.isabs(segments_compendium.storage_dirpath):
        return None

    if not os.path.exists(segments_compendium.storage_dirpath):
        return None

    temp = LogFilePathCompendium(
        debug_filepath=segments_compendium.debug_filename,
        info_filepath=segments_compendium.info_filename,
        warning_filepath=segments_compendium.warning_filename,
        error_filepath=segments_compendium.error_filename,
        critical_filepath=segments_compendium.critical_filename
    )

    for level, filename in temp.__dict__.items():
        if filename is not None and not filename.endswith(".log"):
            setattr(temp, level, None)

    if all(value is None for value in temp.__dict__.values()):
        return None

    folder=segments_compendium.storage_dirpath

    return LogFilePathCompendium(
        debug_filepath=os.path.join(folder, temp.debug_filepath) if temp.debug_filepath else None,
        info_filepath=os.path.join(folder, temp.info_filepath) if temp.info_filepath else None,
        warning_filepath=os.path.join(folder, temp.warning_filepath) if temp.warning_filepath else None,
        error_filepath=os.path.join(folder, temp.error_filepath) if temp.error_filepath else None,
        critical_filepath=os.path.join(folder, temp.critical_filepath) if temp.critical_filepath else None
    )

def add_logfile_handlers(logger: logging.Logger, appsettings_dto : Optional[AppSettingsDataTransferObject] = None) -> None:
    """
    Do not call this from client code.

    Adds file handlers to the provided logger based on the logging settings.

    Args:
        logger (logging.Logger): The logger to which the file handlers will be added.
    """

    log_file_compendium = read_logfile_settings()

    if log_file_compendium is None or not log_file_compendium.storage_dirpath:
        return

    try:
        fpath = validate_logfile_settings(log_file_compendium)

        if fpath is None:
            return

        json_format = jsonlogger.JsonFormatter(  # type: ignore
            json_indent=4,
            fmt='%(asctime)s %(levellevel)s %(module)s %(funcName)s %(lineno)d %(pathname)s %(threadName)s %(process)d %(message)s'
        )

        max_bytes = 1 * 1024 * 1024  # 1MB
        backup_count = 5

        def add_handler(file_path: Optional[str], level: int, handler_name: str) -> None:
            if file_path:
                try:
                    handler = RotatingFileHandler(file_path, maxBytes=max_bytes, backupCount=backup_count)
                    handler.setLevel(level)
                    handler.setFormatter(json_format)
                    handler.set_name(handler_name)
                    logger.addHandler(handler)
                except (OSError, IOError):
                    return None

        add_handler(fpath.debug_filepath, logging.DEBUG, HANDLER_NAME_DEBUG)
        add_handler(fpath.info_filepath, logging.INFO, HANDLER_NAME_INFO)
        add_handler(fpath.warning_filepath, logging.WARNING, HANDLER_NAME_WARNING)
        add_handler(fpath.error_filepath, logging.ERROR, HANDLER_NAME_ERROR)
        add_handler(fpath.critical_filepath, logging.CRITICAL, HANDLER_NAME_CRITICAL)

    except Exception:
        return None

def jgh_configure_logger(appsettings_filename: Optional[str] = None) -> None:
    """
    This is the only function that should be called by the client code to configure logging.

    Configures the root logger by adding console and file handlers based on the logging settings file for test or
    development or production. seee further detail in doctring for read_logfile_settings().
    """

    try:
        logger = logging.getLogger() # Get the root logger, we will add handlers to this logger
        logger.setLevel(logging.DEBUG) # Set the default logging level to DEBUG, we override this in the handlers

        if logger.hasHandlers():
            logger.handlers.clear()

        settings_path = jgh_file_finder.find_path_to_file(appsettings_filename)


        try:
            if settings_path:
                with open(settings_path, "r") as file:
                    input_json = file.read()
                appsettings_dto = JghSerialization.validate(input_json, AppSettingsDataTransferObject)
            else:
                appsettings_dto = None
        except Exception:
            appsettings_dto = None



        add_console_handler(logger, appsettings_dto)
        add_logfile_handlers(logger, appsettings_dto)

    except Exception as e:
        raise RuntimeError(f"Error configuring logging: {e}")

if __name__ == "__main__":
    
    os.environ["APP_ENV"] = "test" # look for settings.test.json
    os.environ["APP_ROOT"] = os.path.dirname(__file__) # jgh_configure_logger will look for settings.test.json in APP_ROOT
    jgh_configure_logger()
    logger = logging.getLogger()

    def example_function() -> None:
        print("INFO: handlers attached to the logger:")
        for handler in logger.handlers:
            print(f"\tHandler name: {handler.get_name()}")

        log_file_paths = [handler.baseFilename for handler in logger.handlers if isinstance(handler, RotatingFileHandler)]
        print(f"INFO: filepaths specified for log file handlers:")
        for path in log_file_paths:
            print(f"\t{os.path.abspath(path)}")

        print(f"INFO: illustrative log messages displayed on the console and respective log files if specified:")
        logger.debug("This is an illustrative debug message")
        logger.info("This is an illustrative info message")
        logger.warning("This is an illustrative warning message")
        logger.error("This is an illustrative error message")
        logger.critical("This is an illustrative critical message")

    example_function()

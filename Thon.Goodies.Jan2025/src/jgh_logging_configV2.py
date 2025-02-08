import os
import json
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional
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

# Define constants for JSON configuration keys
CONFIG_LOGGING = "logging"
LOGFILES_FOLDERPATH = "path"
DEBUG_FILE_NAME = "debug_filename"
INFO_FILE_NAME = "info_filename"
WARNING_FILE_NAME = "warning_filename"
ERROR_FILE_NAME = "error_filename"
CRITICAL_FILE_NAME = "critical_filename"

@dataclass
class LogFileDescriptionsCompendium:
    debug_level_file: str | None = None
    info_level_file: str | None = None
    warning_level_file: str | None = None
    error_level_file: str | None = None
    critical_level_file: str | None = None

@dataclass
class LogFileSegmentsCompendium:
    storage_dirpath: str | None = None
    debug_filename: str | None = None
    info_filename: str | None = None
    warning_filename: str | None = None
    error_filename: str | None = None
    critical_filename: str | None = None

def add_console_handler(logger: logging.Logger) -> None:
    try:
        log_format_for_console = """
        %(asctime)s
            Level: %(levelname)s
            Module: %(module)s
            Function: %(funcName)s
            Line: %(lineno)d
            Message: %(message)s
        """

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(logging.Formatter(log_format_for_console))
        console_handler.set_name(HANDLER_NAME_CONSOLE)
        logger.addHandler(console_handler)

    except Exception as e:
        raise RuntimeError(f"Error configuring console logging: {e}")

def load_logfile_specifications() -> Optional[LogFileSegmentsCompendium]:
    try:
        environment = os.getenv("APP_ENV", "development")
        root_dir = os.getenv("APP_ROOT", os.path.dirname(__file__))
        settings_file = os.path.join(root_dir, f"settings.{environment}.json")
        with open(settings_file, "r") as config_file:
            config = json.load(config_file)

        if CONFIG_LOGGING in config:
            return LogFileSegmentsCompendium(
                storage_dirpath=config[CONFIG_LOGGING].get(LOGFILES_FOLDERPATH),
                debug_filename=config[CONFIG_LOGGING].get(DEBUG_FILE_NAME),
                info_filename=config[CONFIG_LOGGING].get(INFO_FILE_NAME),
                warning_filename=config[CONFIG_LOGGING].get(WARNING_FILE_NAME),
                error_filename=config[CONFIG_LOGGING].get(ERROR_FILE_NAME),
                critical_filename=config[CONFIG_LOGGING].get(CRITICAL_FILE_NAME)
            )
        else:
            print(f"ERROR: '{CONFIG_LOGGING}' section not found in {settings_file}")
            return None

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"ERROR: Failed to load loggin configuration. No file logging will be done to files. : {e}")
        return None

def validate_logfile_specifications(segments_compendium: LogFileSegmentsCompendium) -> Optional[LogFileDescriptionsCompendium]:
    if segments_compendium.storage_dirpath is None:
        return None

    if segments_compendium.storage_dirpath and not os.path.isabs(segments_compendium.storage_dirpath):
        print(f"Error: storage_dirpath must be an absolute path: {segments_compendium.storage_dirpath}")
        return None

    temp = LogFileDescriptionsCompendium(
        debug_level_file=segments_compendium.debug_filename,
        info_level_file=segments_compendium.info_filename,
        warning_level_file=segments_compendium.warning_filename,
        error_level_file=segments_compendium.error_filename,
        critical_level_file=segments_compendium.critical_filename
    )

    for level, filename in temp.__dict__.items():
        if filename is not None and not filename.endswith(".log"):
            print(f"Invalid filename for {level}: {filename} (must end with .log)")
            setattr(temp, level, None)

    if all(value is None for value in temp.__dict__.values()):
        return None

    folder=segments_compendium.storage_dirpath

    return LogFileDescriptionsCompendium(
        debug_level_file=os.path.join(folder, temp.debug_level_file) if temp.debug_level_file else None,
        info_level_file=os.path.join(folder, temp.info_level_file) if temp.info_level_file else None,
        warning_level_file=os.path.join(folder, temp.warning_level_file) if temp.warning_level_file else None,
        error_level_file=os.path.join(folder, temp.error_level_file) if temp.error_level_file else None,
        critical_level_file=os.path.join(folder, temp.critical_level_file) if temp.critical_level_file else None
    )

def add_logfile_handlers(logger: logging.Logger) -> None:
    log_file_compendium = load_logfile_specifications()
    if log_file_compendium is None or not log_file_compendium.storage_dirpath:
        return

    try:
        fpath = validate_logfile_specifications(log_file_compendium)
        if fpath is None:
            return

        json_format = jsonlogger.JsonFormatter( # type: ignore
            json_indent=4,
            fmt='%(asctime)s %(levellevel)s %(module)s %(funcName)s %(lineno)d %(pathname)s %(threadName)s %(process)d %(message)s'
        )

        max_bytes = 1 * 1024 * 1024  # 1MB
        backup_count = 5

        if fpath.debug_level_file:
            handler_debug = RotatingFileHandler(fpath.debug_level_file, maxBytes=max_bytes, backupCount=backup_count)
            handler_debug.setLevel(logging.DEBUG)
            handler_debug.setFormatter(json_format)
            handler_debug.set_name(HANDLER_NAME_DEBUG)
            logger.addHandler(handler_debug)

        if fpath.info_level_file:
            handler_info = RotatingFileHandler(fpath.info_level_file, maxBytes=max_bytes, backupCount=backup_count)
            handler_info.setLevel(logging.INFO)
            handler_info.setFormatter(json_format)
            handler_info.set_name(HANDLER_NAME_INFO)
            logger.addHandler(handler_info)

        if fpath.warning_level_file:
            handler_warning = RotatingFileHandler(fpath.warning_level_file, maxBytes=max_bytes, backupCount=backup_count)
            handler_warning.setLevel(logging.WARNING)
            handler_warning.setFormatter(json_format)
            handler_warning.set_name(HANDLER_NAME_WARNING)
            logger.addHandler(handler_warning)

        if fpath.error_level_file:
            handler_error = RotatingFileHandler(fpath.error_level_file, maxBytes=max_bytes, backupCount=backup_count)
            handler_error.setLevel(logging.ERROR)
            handler_error.setFormatter(json_format)
            handler_error.set_name(HANDLER_NAME_ERROR)
            logger.addHandler(handler_error)

        if fpath.critical_level_file:
            handler_critical = RotatingFileHandler(fpath.critical_level_file, maxBytes=max_bytes, backupCount=backup_count)
            handler_critical.setLevel(logging.CRITICAL)
            handler_critical.setFormatter(json_format)
            handler_critical.set_name(HANDLER_NAME_CRITICAL)
            logger.addHandler(handler_critical)

    except Exception as e:
        print(f"Error configuring file logging. No logging will be done to files: {e}")

def jgh_configure_logger() -> None:
    try:
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        if logger.hasHandlers():
            logger.handlers.clear()

        add_console_handler(logger)
        add_logfile_handlers(logger)

    except Exception as e:
        raise RuntimeError(f"Error configuring logging: {e}")

if __name__ == "__main__":
    os.environ["APP_ENV"] = "test"
    os.environ["APP_ROOT"] = os.path.dirname(__file__) 
    
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

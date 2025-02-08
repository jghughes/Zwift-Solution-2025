import os
import json
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional, List
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
class LogFilePaths:
    debug: str | None = None
    info: str | None = None
    warning: str | None = None
    error: str | None = None
    critical: str | None = None

@dataclass
class LogFileNames:
    logfiles_folder: str | None = None
    debug_filename: str | None = None
    info_filename: str | None = None
    warning_filename: str | None = None
    error_filename: str | None = None
    critical_filename: str | None = None

    def __post_init__(self):
        if self.logfiles_folder and not os.path.isabs(self.logfiles_folder):
            raise ValueError(f"logfiles_folder must be an absolute path: {self.logfiles_folder}")

        invalid_filenames: List[str] = []
        for level, filename in self.__dict__.items():
            if level != "logfiles_folder" and filename is not None:
                if not filename.endswith(".log"):
                    invalid_filenames.append(f"{level}: {filename}")

        if invalid_filenames:
            raise ValueError(f"The following filenames are invalid (must end with .log): {', '.join(invalid_filenames)}")

    def get_absolute_paths(self) -> Optional[LogFilePaths]:
        if self.logfiles_folder is None:
            return None

        return LogFilePaths(
            debug=os.path.join(self.logfiles_folder, self.debug_filename) if self.debug_filename else None,
            info=os.path.join(self.logfiles_folder, self.info_filename) if self.info_filename else None,
            warning=os.path.join(self.logfiles_folder, self.warning_filename) if self.warning_filename else None,
            error=os.path.join(self.logfiles_folder, self.error_filename) if self.error_filename else None,
            critical=os.path.join(self.logfiles_folder, self.critical_filename) if self.critical_filename else None
        )

def jgh_configure_logging() -> None:
    log_filenames: Optional[LogFileNames] = None
    settings_file: str = ""
    try:
        environment = os.getenv("APP_ENV", "development")
        root_dir = os.getenv("APP_ROOT", os.path.dirname(__file__))
        settings_file = os.path.join(root_dir, f"settings.{environment}.json")
        with open(settings_file, "r") as config_file:
            config = json.load(config_file)

        if CONFIG_LOGGING in config:
            log_filenames = LogFileNames(
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
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        if logger.hasHandlers():
            logger.handlers.clear()

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
        raise RuntimeError(f"Error configuring logging: {e}")

    try:
        if log_filenames is None or not log_filenames.logfiles_folder:
            return
        log_filepaths = log_filenames.get_absolute_paths()
        if log_filepaths is None:
            return

        json_log_format_for_file = jsonlogger.JsonFormatter( # type: ignore
            json_indent=4,
            fmt='%(asctime)s %(levellevel)s %(module)s %(funcName)s %(lineno)d %(pathname)s %(threadName)s %(process)d %(message)s'
        )

        max_bytes = 1 * 1024 * 1024  # 1MB
        backup_count = 5

        if log_filepaths.debug:
            log_filehandler_debug = RotatingFileHandler(log_filepaths.debug, maxBytes=max_bytes, backupCount=backup_count)
            log_filehandler_debug.setLevel(logging.DEBUG)
            log_filehandler_debug.setFormatter(json_log_format_for_file)
            log_filehandler_debug.set_name(HANDLER_NAME_DEBUG)
            logger.addHandler(log_filehandler_debug)

        if log_filepaths.info:
            log_filehandler_info = RotatingFileHandler(log_filepaths.info, maxBytes=max_bytes, backupCount=backup_count)
            log_filehandler_info.setLevel(logging.INFO)
            log_filehandler_info.setFormatter(json_log_format_for_file)
            log_filehandler_info.set_name(HANDLER_NAME_INFO)
            logger.addHandler(log_filehandler_info)

        if log_filepaths.warning:
            log_filehandler_warning = RotatingFileHandler(log_filepaths.warning, maxBytes=max_bytes, backupCount=backup_count)
            log_filehandler_warning.setLevel(logging.WARNING)
            log_filehandler_warning.setFormatter(json_log_format_for_file)
            log_filehandler_warning.set_name(HANDLER_NAME_WARNING)
            logger.addHandler(log_filehandler_warning)

        if log_filepaths.error:
            log_filehandler_error = RotatingFileHandler(log_filepaths.error, maxBytes=max_bytes, backupCount=backup_count)
            log_filehandler_error.setLevel(logging.ERROR)
            log_filehandler_error.setFormatter(json_log_format_for_file)
            log_filehandler_error.set_name(HANDLER_NAME_ERROR)
            logger.addHandler(log_filehandler_error)

        if log_filepaths.critical:
            log_filehandler_critical = RotatingFileHandler(log_filepaths.critical, maxBytes=max_bytes, backupCount=backup_count)
            log_filehandler_critical.setLevel(logging.CRITICAL)
            log_filehandler_critical.setFormatter(json_log_format_for_file)
            log_filehandler_critical.set_name(HANDLER_NAME_CRITICAL)
            logger.addHandler(log_filehandler_critical)

    except Exception as e:
        print(f"Error configuring file logging. No logging will be done to files: {e}")

if __name__ == "__main__":
    os.environ["APP_ENV"] = "test"
    os.environ["APP_ROOT"] = os.path.dirname(__file__) 
    
    jgh_configure_logging()
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


import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional
from jgh_file_finder import find_filepath, find_dirpath
from jgh_serialization import JghSerialization
from dataclasses import dataclass
from pydantic import BaseModel

class ConsoleHandlerDataTransferObject(BaseModel):
    loglevel: str | None = None
    messageformat: str | None = None

class LogFileHandlerDataTransferObject(BaseModel):
    loglevel: str | None = None
    messageformat: str | None = None

class LoggingHandlersDataTransferObject(BaseModel):
    console: ConsoleHandlerDataTransferObject | None = None
    file: LogFileHandlerDataTransferObject | None = None

class AppSettingsDataTransferObject(BaseModel):
    logging: LoggingHandlersDataTransferObject | None = None

@dataclass(frozen=True)
class LoggingMessageFormat:
    simpleformatstring: str = "%(message)s"
    balancedformatstring: str = "%(asctime)s %(levelname)s - %(message)s - %(exc_info)s"
    informativeformatstring: str = "%(asctime)s %(levelname)s - %(funcName)s - %(lineno)d - %(message)s - %(exc_info)s"   

    @classmethod
    def get_format_string(cls, format_name: str | None) -> str:
        match format_name:
            case "simple":
                return cls.simpleformatstring
            case "balanced":
                return cls.balancedformatstring
            case "informative":
                return cls.informativeformatstring
            case _:
                return cls.informativeformatstring

@dataclass(frozen=True)
class LogLevel:
    debuglevel: int = logging.DEBUG
    infolevel: int = logging.INFO
    warninglevel: int = logging.WARNING
    errorlevel: int = logging.ERROR
    criticallevel: int = logging.CRITICAL
    notsetlevel: int = logging.NOTSET

    @classmethod
    def get_level(cls, level_name: str | None) -> int:
        if level_name is not None:
            level_name = level_name.strip().lower()
        match level_name:
            case "debug":
                return cls.debuglevel
            case "info":
                return cls.infolevel
            case "warning":
                return cls.warninglevel
            case "error":
                return cls.errorlevel
            case "critical":
                return cls.criticallevel
            case _:
                return cls.debuglevel


def jgh_configure_logging(appsettings_filename: Optional[str] = None)-> None:
    """
    Configures a given logger based on the provided appsettings JSON filename.

    If no filename is provided, the given logger will be configured with default
    settings. If the filename is provided, the function will attempt to read the
    configuration from the specified file and set up the logger accordingly.

    jgh_configure_logging searches for the configuration file starting from the
    current folder and working its way up the directory tree until it finds the
    file or reaches the root directory.

    If the file is not found, the Python system logger will be configured with its
    normal defaults, meaning that it will print to the console. If the file is found
    but is invalid or deficient in any way, the Python logger will also be configured
    with default settings.

    The logger will be configured with the following handlers if the appsettings file
    is valid and includes the necessary logging section and contents.

    - Console handler named console handler' with the specified log level
      and message format.

    - File handler named 'file handler' with the specified log level and
      message format, and the log file will be created automatically in the same folder
      as the appsettings file with a filename of "logger.log". The log file will be
      rotated when it reaches 5MB in size, and up to 3 backup files will be kept.

    Included in the JSON settings file, the following illustrative logging section is
    expected:

        "logging": {
            "console": {
                "loglevel": "debug",
                "messageformat": "simple"
            },
            "file": {
                "loglevel": "warning",
                "messageformat": "informative"
            }
        }

    The log level can be one of the following: "debug", "info", "warning", "error", "critical".
    The message format can be one of the following: "simple, "balanced", "informative".

    Args:
        appsettings_filename (Optional[str]): The short name of the JSON file
            containing the settings for the app including logging config.
            Typically, this file is named "appsettings.json" and found
            in the root folder of the application. If None, the logger 
            will remain unconfigured and as such will fail to log 
            messages with a (low) severity of DEBUG and INFO. Only WARNING
            and higher severity messages will be logged.

    Raises:
        RuntimeError: If there is an irrecoverable error during the configuration process.
    """
    logger = logging.getLogger() #get root logger

    for handler in logger.handlers:
        handler.close()

    logger.handlers.clear()

    logging.basicConfig(level=logging.DEBUG) # this is the default config, we might or might not override it later

    try:
        if appsettings_filename is None:
            return

        settings_path : str | None = find_filepath(appsettings_filename)

        if not settings_path:
            return

        try:
            with open(settings_path, "r") as file:
                input_json = file.read()
            if not input_json:
                return None
        except Exception:
            return None

        try:
            JghSerialization.validate(input_json, AppSettingsDataTransferObject)
        except Exception as e:
            return None
        
        appsettings  = JghSerialization.validate(input_json, AppSettingsDataTransferObject)

        mustskipconsolehandler: bool = (appsettings.logging is None or appsettings.logging.console is None)

        mustskipfilehandler: bool = (appsettings.logging is None or appsettings.logging.file is None)

        if mustskipconsolehandler and mustskipfilehandler:
            return None;

        #OK we must add one or both filehandlers. start afresh

        for handler in logger.handlers:
            handler.close()

        logger.handlers.clear()

        if not(appsettings.logging is None or appsettings.logging.console is None):
            severity = LogLevel.get_level(appsettings.logging.console.loglevel)
            formatstring = LoggingMessageFormat.get_format_string(appsettings.logging.console.messageformat)
            handler01 = logging.StreamHandler()
            handler01.setLevel(severity)
            handler01.setFormatter(logging.Formatter(formatstring))
            handler01.set_name(f"console handler")
            logger.addHandler(handler01)

        if not(appsettings.logging is None or appsettings.logging.file is None):
            appsettings_folder = find_dirpath(appsettings_filename)
            log_filename = 'logger.log'
            if (appsettings_folder is not None):
                log_file_path = os.path.join(appsettings_folder, log_filename)
                severity = LogLevel.get_level(appsettings.logging.file.loglevel)
                formatstring = LoggingMessageFormat.get_format_string(appsettings.logging.file.messageformat)
                handler02 = RotatingFileHandler(log_file_path, maxBytes=5 * 1024 * 1024, backupCount=3)
                handler02.setLevel(severity)
                handler02.setFormatter(logging.Formatter(formatstring))
                handler02.set_name(f"file handler")
                logger.addHandler(handler02)

        # # Prevent log messages from being propagated to the root logger (if you omit this, messages will be printed twice)
        # customLogger.propagate = False

    except Exception as e:
        raise RuntimeError(f"Error configuring logging: {e}")


# Example usage
    # Note: the root logger is the parent of all loggers in the logging module hierarchy.
    # It is named 'root' and has no parent. The root logger is the default logger 
    # that is used by the logging module. It is the logger that is used when you 
    # call logging.getLogger() without any arguments.

if __name__ == "__main__":

    debugMsg="This is a debug message"
    infoMsg="This is an info message"
    warningMsg="This is a warning message"
    errorMsg="This is an error message"
    criticalMsg="This is a critical message"

    print("")
    print("Example 1: do nothing to configure logging system (outcome: only Warning and higher severity messages will be logged))")
    print("")
    rootlogger = logging.getLogger()
    rootlogger.debug(debugMsg)
    rootlogger.info(infoMsg)
    rootlogger.warning(warningMsg)
    rootlogger.error(errorMsg)
    rootlogger.critical(criticalMsg)

    print("")
    print("Example 2: configure logging system conventionally with basicConfig(logging.DEBUG). This example is set to log all messages from DEBUG and up (all messages will be logged)")
    print("")
    logging.basicConfig(level=logging.DEBUG) 
    rootlogger = logging.getLogger()
    rootlogger.debug(debugMsg)
    rootlogger.info(infoMsg)
    rootlogger.warning(warningMsg)
    rootlogger.error(errorMsg)
    rootlogger.critical(criticalMsg)

    print("")
    print("Example 3: Try log some messages using the logger usinf jgh_configure_logging(filename). Because the filename is a dummy placeholder, jgh_configure_logging() exits early. All it does under the hood is execute basicConfig(logging.DEBUG). it thus logs all messages,exactly the same as example 2")
    print("")
    jgh_configure_logging("nonexistantfile.rubbish")
    rootlogger = logging.getLogger()
    rootlogger.debug(debugMsg)
    rootlogger.info(infoMsg)
    rootlogger.warning(warningMsg)
    rootlogger.error(errorMsg)
    rootlogger.critical(criticalMsg)

    print("")
    print("Example 4: Try log some messages using the logger using jgh_configure_logging(filename) with a legit file. If it is working properly the logger will do whatever the file tells it to do.")    
    print("")
    jgh_configure_logging("appsettings.json")
    rootlogger = logging.getLogger()
    rootlogger.debug(debugMsg)
    rootlogger.info(infoMsg)
    rootlogger.warning(warningMsg)
    rootlogger.error(errorMsg)
    rootlogger.critical(criticalMsg)






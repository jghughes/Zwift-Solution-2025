
from csv import Error
import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional
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
    messageonlyformatstring: str = "%(message)s"
    simpleformatstring: str = "%(asctime)s : %(message)s"
    balancedformatstring: str = "%(asctime)s : %(levelname)s - %(message)s - %(exc_info)s"
    informativeformatstring: str = "%(asctime)s : %(name)s : %(module)s : line=%(lineno)d : %(funcName)s : %(levelname)s - %(message)s - exception=%(exc_info)s"

    @classmethod
    def get_format_string(cls, format_name: str | None) -> str:
        match format_name:
            case "messageonly":
                return cls.messageonlyformatstring
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

def find_directory_that_contains_file(filename: Optional[str] = None, directory: Optional[str] = None) -> str | None:
    """
    Searches for the named file everywhere in the given directory, including all subdirectories. 
    Returns the directory path of the folder containing the file. The method tries its best to 
    find the file even if the caller chooses not to specify a directory. In this case, the method 
    searches everywhere in the current working directory of the system. This is helpful
    in circumstances where the caller wishes to search the working directory but doesn't know 
    where/what it is.
    
    Args:
        filename (str): The name of the file to search for.
        directory (str): The parent directory to start the search in.
    
    Returns:
        str | None: The directory path of the folder containing the given
            file if found, otherwise None.
    """
    if not filename:
        return None

    if directory is None:
        directory = os.getcwd()  # Use current working directory if directory is not provided

    try:
        directory = os.path.abspath(directory)  # Normalize the base directory
    except Exception:
        return None

    for root, dirs, files in os.walk(directory):
        if filename in files:
            return root.replace("\\", "/")

    return None

def jgh_configure_logging(appSettingsFilename: Optional[str] = None)-> None:
    """
    Configures the root logger in the logging system from an appsettings file. Intended 
    to be called as a one-time set-up function used at the start of an application
    in function Main. Logging should not be configured in library code. The main 
    application that uses a library should configure logging. The logger should 
    merely be obtained in library code. To obtain a logger in library code, merely call 
    logger=logging.getLogger(__name__).

    For this function to work as intended, the developer must include a custom 
    key-value pair in the environment variables dictionary of the application. 
    The key must be named BASE_DIR and the value must be the (hard-coded) base 
    directory of the desktop application or the root folder of the web application 
    as the case may be.

    If this key-value pair is not manually created in the environment dictionary, 
    the function resorts to using the current system working directory instead. 
    This will normally be useless other than in a testing environment. 
    
    The base directory is normally the root folder of a web app. The way it is specified is
    platform-dependent. On Windows, it is typically something like "C:/MyApp". On Linux,
    it is typically something like "/home/myapp". To setup it manually in code, use the
    os.environ["BASE_DIR"] = "C:/MyApp" or os.environ["BASE_DIR"] = "/home/myapp".

    The function will search the obtained base directory and all its sub-directories 
    if necessary to locate the dirpath of the folder containing the "appSettingsFilename" file.

    If no filename is provided, or the file is not found, or is found but is 
    invalid or falls short in any way, the the logging system is initialised 
    with the out-of-the-box default configuration i.e. with logging to the console 
    in a message-only format.

    The logger will be configured with the following handlers if the appsettings file
    is valid and includes the necessary logging section and contents.

    - Console handler named "consoleHandler" with the specified log level
      and message format.

    - File handler named "fileHandler" with the specified log level and
      message format. The log file will be created automatically in the same folder
      as the appsettings file with a filename of "logger.log". The log file will be
      rotated when it reaches 5MB in size, and up to 3 backup files will be kept.

    Included in the appsettings file, the following logging content is
    expected (illustration):

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
    The message format can be one of the following: "messageonly", "simple, "balanced", "informative".


    Args:
        appSettingsFilename (Optional[str]): The short name of the JSON file
            containing the settings for the app including logging config.
            Typically, this file is named "appsettings.json" and found
            in the root folder of the application. If None, the logger 
            will remain unconfigured and as such will fail to log 
            messages with a (low) severity of DEBUG and INFO. Only WARNING
            and higher severity messages will be logged.

    Raises:
        Error: If there is an irrecoverable error during the configuration process.
    """
    logger = logging.getLogger() #get root logger

    for handler in logger.handlers:
        handler.close()

    logger.handlers.clear()

    logging.basicConfig(level=logging.DEBUG) # this is the fallback config, we might or might not override it later

    try:
        if appSettingsFilename is None:
            return

        parent_directory = os.getenv('BASE_DIR', os.getcwd())  # Use BASE_DIR environment variable or current working directory

        appSettingsDirPath: str | None = find_directory_that_contains_file(appSettingsFilename, parent_directory )

        if appSettingsDirPath is None:
            return None

        appSettingsFilePath: str = os.path.join(appSettingsDirPath, appSettingsFilename)

        if not appSettingsFilePath:
            return

        try:
            with open(appSettingsFilePath, "r") as file:
                inputJson = file.read()
            if not inputJson:
                return None
        except Exception:
            return None

        try:
            JghSerialization.validate(inputJson, AppSettingsDataTransferObject)
        except Exception as e:
            return None
        
        appsettings  = JghSerialization.validate(inputJson, AppSettingsDataTransferObject)

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
            formatString = LoggingMessageFormat.get_format_string(appsettings.logging.console.messageformat)
            handler01 = logging.StreamHandler()
            handler01.setLevel(severity)
            handler01.setFormatter(logging.Formatter(formatString))
            handler01.set_name(f"consoleHandler")
            logger.addHandler(handler01)

        if not(appsettings.logging is None or appsettings.logging.file is None):
            severity = LogLevel.get_level(appsettings.logging.file.loglevel)
            formatString = LoggingMessageFormat.get_format_string(appsettings.logging.file.messageformat)
            logFileName = 'logger.log'
            logFilePath = os.path.join(appSettingsDirPath, logFileName)
            handler02 = RotatingFileHandler(logFilePath, maxBytes=5 * 1024 * 1024, backupCount=3)
            handler02.setLevel(severity)
            handler02.setFormatter(logging.Formatter(formatString))
            handler02.set_name(f"fileHandler")
            logger.addHandler(handler02)

    except Exception as e:
        raise Error(f"Error configuring logging: {e}")


# Example usage

def main():
    dir_path = find_directory_that_contains_file("appsettings.json")
    if dir_path:
        print(f"Found appsettings.json at: {dir_path}")
    else:
        print("appsettings.json not found.")

def main2():

    debugMsg="This is a debug message"
    infoMsg="This is an info message"
    warningMsg="This is a warning message"
    errorMsg="This is an error message"
    criticalMsg="This is a critical message"

    print("")
    print("Example 1: do nothing to configure logging system (outcome: only Warning and higher severity messages will be logged))")
    print("")
    # do no configuration of the logging system
    rootlogger = logging.getLogger()
    rootlogger.debug(debugMsg)
    rootlogger.info(infoMsg)
    rootlogger.warning(warningMsg)
    rootlogger.error(errorMsg)
    rootlogger.critical(criticalMsg)

    print("")
    print("Example 2: call logging.basicConfig(logging.DEBUG) to initialise the logging system. All messages from DEBUG and higher will be logged")
    print("")
    logging.basicConfig(level=logging.DEBUG) 
    rootlogger = logging.getLogger()
    rootlogger.debug(debugMsg)
    rootlogger.info(infoMsg)
    rootlogger.warning(warningMsg)
    rootlogger.error(errorMsg)
    rootlogger.critical(criticalMsg)

    print("")
    print("Example 3: call jgh_configure_logging(nonexistantfile.rubbish) to initialise the logging system. Because the filename in this test is nonsensical, the method calls logging.basicConfig(logging.DEBUG) by itself.")
    print("")
    jgh_configure_logging("RubbishFileName")
    rootlogger = logging.getLogger()
    rootlogger.debug(debugMsg)
    rootlogger.info(infoMsg)
    rootlogger.warning(warningMsg)
    rootlogger.error(errorMsg)
    rootlogger.critical(criticalMsg)

    print("")
    print("Example 4: call jgh_configure_logging(appsettings.json) to initialise the logging system. The logging system will behave how the settings dictate.")    
    print("")
    jgh_configure_logging("appsettings.json")
    x = __name__
    rootlogger = logging.getLogger(__name__)
    rootlogger.debug(debugMsg)
    rootlogger.info(infoMsg)
    rootlogger.warning(warningMsg)
    rootlogger.error(errorMsg)
    rootlogger.critical(criticalMsg)

if __name__ == "__main__":
    main()
    main2()






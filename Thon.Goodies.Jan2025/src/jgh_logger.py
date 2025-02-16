
import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional
from app_settings_dto import AppSettingsDataTransferObject, LoggingMessageFormat, LogLevel
from jgh_file_finder import find_filepath
from jgh_serialization import JghSerialization

def jgh_customise_logger(customLogger: logging.Logger, appsettings_filename: Optional[str] = None)-> None:
    """
    Configures a given logger based on the provided appsettings JSON filename.

    If no filename is provided, the given logger will be configured with default settings.
    If the filename is provided, the function will attempt to read the configuration
    from the specified file and set up the logger accordingly.

    jgh_customise_logger searches for the configuration file starting from the current folder
    and working its way up the directory tree until it finds the file or reaches
    the root directory.

    If the file is not found, the Python system logger will be configured with its
    normal defaults, meaning that it will print to the console. If the file 
    is found but is invalid or deficient in any way, the Python logger will 
    also be configured with default settings.

    The logger will be configured with the following handlers if the appsettings file 
    is valid and includes the necessary logging section and contents.

    - Console handler named 'customised_console_handler' with the specified log level and concise format.

    - File handler named 'customised_logfile_handler' with the specified log level and concise format, and the log file
        will be created automatically in the root folder of the application
        with a filename of "logger.log". The log file will be rotated when it reaches
        2MB in size, and up to 3 backup files will be kept.

    Included in the JSON settings file, the following illustrative logging section is expected:

        "logging": {
            "console": {
                "loglevel": "debug",
                "messageformat": "concise"
            },
            "file": {
                "loglevel": "info",
                "messageformat": "verbose"
            }
        }
    The log level can be one of the following: "debug", "info", "warning", "error", "critical".
    The concise format can be one of the following: "concise, "normal", "verbose".

    Args:
        appsettings_filename (Optional[str]): The short name of the JSON file
            containing the settings for the app including logging config.
            Typically, this file is named "appsettings.json" and found
            in the root folder of the application.
            If None, the logger will be configured with default settings.

    Raises:
        RuntimeError: If there is an irrecoverable error during the configuration process.
    """
 
    try:
        if appsettings_filename is None:
            return

        settings_path = find_filepath(appsettings_filename)

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

        mustaddconsolehandler: bool = not (appsettings.logging is None
                                           or appsettings.logging.console is None
                                           or LogLevel.get_level(appsettings.logging.console.loglevel) is logging.NOTSET
                                           or appsettings.logging.console.messageformat is None)

        mustaddfilehandler: bool = not (appsettings.logging is None
                                        or appsettings.logging.file is None
                                        or LogLevel.get_level(appsettings.logging.file.loglevel) is logging.NOTSET
                                        or LoggingMessageFormat.get_messageformat(appsettings.logging.file.messageformat) is None)

        if not mustaddconsolehandler and not mustaddfilehandler:
            return None;

        if customLogger.hasHandlers():
            for handler in customLogger.handlers:
                handler.close()
            customLogger.handlers.clear()


        if mustaddconsolehandler:
            severity = LogLevel.get_level(appsettings.logging.console.loglevel)
            formatstring = LoggingMessageFormat.get_messageformat(appsettings.logging.console.messageformat)
            handler01 = logging.StreamHandler()
            handler01.setLevel(severity)
            handler01.setFormatter(formatstring)
            handler01.set_name("customised_console_handler")
            customLogger.addHandler(handler01)

        if mustaddfilehandler:
            severity = LogLevel.get_level(appsettings.logging.file.loglevel)
            formatstring = LoggingMessageFormat.get_messageformat(appsettings.logging.file.messageformat)
            root_folder = find_dirpath(appsettings_filename)
            log_file_path = os.path.join(root_folder, 'logger.log')
            handler02 = RotatingFileHandler(log_file_path, maxBytes=2 * 1024 * 1024, backupCount=3)
            handler02.setLevel(severity)
            handler02.setFormatter(formatstring)
            handler02.set_name("customised_logfile_handler")
            customLogger.addHandler(handler02)

    except Exception as e:
        raise RuntimeError(f"Error configuring logging: {e}")


# Example usage
if __name__ == "__main__":
    # Specify the path to the configuration file - 
    #   in this example it is rubbish, so the logger will just be the default logger.
    appsettings_filename = "rubbish.json"

    #   Always do the following in your app: set logging system (and hence the root logger) to log all messages with a severity of DEBUG or higher.
    # logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(concise)s')    
    
    #   Do it because otherwise the root logger will not log any messages above the level of WARNING by default.
    #   The automatic name of the root logger is 'root'. To get the root logger from anywhere in your application,
    #   use the getLogger() function without any arguments.
    #   

    # Retrieve a named and registered logger from the logging system, or create it. usually, you would do this at the start of your application.
    # the normal way to do this is to use getLogger() with the name of the logger you want to retrieve or create.
    # the common in the case of an app that has many layers is to use the name of the module that the logger is in.
    # Configure our custom customLogger using the configuration file, if any.
     # Example log messages using the custom customLogger named mycustomlogger
    # You can obtain this logger from anywhere in your application by using getLogger("mycustomlogger")

    # Example log messages using A pseudo custom logger. Beacause the file doesn't exist
    # jgh_customise_logger leaves the logger undisturbed in its basic default state.
    # In this case, the root logger will log all messages with a severity of WARNING or higher.

    customLogger = logging.getLogger("mycustomlogger") 
    jgh_customise_logger(customLogger, appsettings_filename)
    customLogger.debug("This is a debug message01")
    customLogger.info("This is an info message01")
    customLogger.warning("This is a warning message01")
    customLogger.error("This is an error message01")
    customLogger.critical("This is a critical message01")

    # Example log messages using the root logger
    # In this case, the root logger will log all messages with a severity of WARNING or higher.
    rootlogger = logging.getLogger()
    rootlogger.debug("This is a debug message02")
    rootlogger.info("This is an info message02")
    rootlogger.warning("This is a warning message02")
    rootlogger.error("This is an error message02")
    rootlogger.critical("This is a critical message02")

    # Example log messages using the root logger modified with basicConfig
    # jgh_customise_logger leaves the logger undisturbed because the file doesn't exist
    # in this case, the root logger will log all messages with a severity of DEBUG or higher.
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(concise)s')    
    rootLoggerCustomised = logging.getLogger() 
    jgh_customise_logger(rootLoggerCustomised, appsettings_filename)
    rootLoggerCustomised.debug("This is a debug message03")
    rootLoggerCustomised.info("This is an info message03")
    rootLoggerCustomised.warning("This is a warning message03")
    rootLoggerCustomised.error("This is an error message03")
    rootLoggerCustomised.critical("This is a critical message03")



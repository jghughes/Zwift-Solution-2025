import logging
from logging.handlers import RotatingFileHandler
from typing import Optional
from app_settings_dto import AppSettingsDataTransferObject, LoggingMessageFormat, LogLevel
from jgh_file_finder import find_path_to_file
from jgh_serialization import JghSerialization

def configure_logger(appsettings_filename: Optional[str] = None)-> None:
    """
    Configures the root logger based on the provided appsettings JSON file.

    If no filename is provided, the logger will be configured with default settings.
    If the filename is provided, the function will attempt to read the configuration
    from the specified file and set up the logger accordingly.

    The function searches for the configuration file starting from the current folder
    and then works its way up the directory tree until it finds the file or reaches
    the root directory.

    If the file is not found, the logger will be configured with default settings.
    If the file is found but is invalid or deficient in any way, the logger will also
    be configured with default settings.

    Args:
        appsettings_filename (Optional[str]): The short name of the JSON file.
            If None, the logger will be configured with default settings.

    Raises:
        RuntimeError: If there is an error during the configuration process.
    """
    try:
        # configure root logger as the default
        logger = logging.getLogger() 
        logger.setLevel(logging.DEBUG)

        if appsettings_filename is None:
            return

        settings_path = find_path_to_file(appsettings_filename)

        if not settings_path:
            return

        try:
            with open(settings_path, "r") as file:
                input_json = file.read()
            if not input_json:
                return None

            appsettings = JghSerialization.validate(input_json, AppSettingsDataTransferObject)
            if not appsettings:
                return

        except Exception:
            return None

        mustaddconsolehandler = (appsettings.logging 
                                 and appsettings.logging.console 
                                 and appsettings.logging.console.loglevel 
                                 and appsettings.logging.console.messageformat)

        mustaddfilehandler = (appsettings.logging 
                              and appsettings.logging.file 
                              and appsettings.logging.file.loglevel
                              and appsettings.logging.file.messageformat
                              and appsettings.storage 
                              and appsettings.storage.local 
                              and appsettings.storage.local.dirpathexists() 
                              and appsettings.storage.local.get_absolutefilepath())

        if not mustaddconsolehandler and not mustaddfilehandler:
            return None;

        if logger.hasHandlers():
            logger.handlers.clear()

        if mustaddconsolehandler:
            handler01 = logging.StreamHandler()
            handler01.setLevel(LogLevel.get_level(appsettings.logging.console.loglevel))
            handler01.setFormatter(logging.Formatter(LoggingMessageFormat.get_messageformat(appsettings.logging.console.messageformat)))
            handler01.set_name("console_handler")
            logger.addHandler(handler01)

        if mustaddfilehandler:
            handler02 = RotatingFileHandler(appsettings.storage.local.get_absolutefilepath(), maxBytes=1 * 1024 * 1024, backupCount=5)
            handler02.setLevel(LogLevel.get_level(appsettings.logging.file.loglevel))
            handler02.setFormatter(logging.Formatter(LoggingMessageFormat.get_messageformat(appsettings.logging.file.messageformat)))
            handler02.set_name("logfile_handler")
            logger.addHandler(handler02)

    except Exception as e:
        raise RuntimeError(f"Error configuring logging: {e}")


# Example usage
if __name__ == "__main__":
    # Specify the path to the configuration file - in this example it is non-existent, so the logger will just be the default logger.
    appsettings_filename = "path/to/appsettings.json"

    # Configure the logger using the configuration file
    configure_logger(appsettings_filename)

    # Get the logger instance
    logger = logging.getLogger()

    # Example log messages
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
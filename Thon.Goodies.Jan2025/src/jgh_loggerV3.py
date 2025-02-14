import logging
from logging.handlers import RotatingFileHandler
from typing import Optional
from app_settings_dto import AppSettingsDataTransferObject, LoggingMessageFormat, LogLevel

def configure_loggerV3(logger: logging.Logger, appsettings: AppSettingsDataTransferObject):
    if logger is None or appsettings is None:
        return

    # Configure console handler
    if appsettings.logging and appsettings.logging.console:
        console_config = appsettings.logging.console
        if console_config:
            handler01 = logging.StreamHandler()
            handler01.setLevel(LogLevel.get_level(console_config.loglevel))
            handler01.setFormatter(logging.Formatter(LoggingMessageFormat.get_messageformat(console_config.messageformat)))
            handler01.set_name("console_handler")
            logger.addHandler(handler01)

    # Configure file handler
    if appsettings.logging and appsettings.logging.file and appsettings.storage and appsettings.storage.local and appsettings.storage.local.dirpathexists():
        file_config = appsettings.logging.file
        if file_config:
            absolute_logfile_path = appsettings.storage.local.get_absolutefilepath()
            if absolute_logfile_path:
                handler02 = RotatingFileHandler(absolute_logfile_path, maxBytes=1 * 1024 * 1024, backupCount=5)
                handler02.setLevel(LogLevel.get_level(file_config.loglevel))
                handler02.setFormatter(logging.Formatter(LoggingMessageFormat.get_messageformat(file_config.messageformat)))
                handler02.set_name("logfile_handler")
                logger.addHandler(handler02)

    # Set the root logger level to the lowest level to capture all logs
    logger.setLevel(logging.DEBUG)

# Example usage
if __name__ == "__main__":
    # Load the configuration from a JSON file
    config_data = {
        "logging": {
            "console": {
                "loglevel": "debug",
                "messageformat": "message",
            },
            "file": {
                "loglevel": "information",
                "messageformat": "verbose",
            }
        }
    }

    appsettings = AppSettingsDataTransferObject(**config_data)
    logger = logging.getLogger(__name__)
    configure_loggerV3(logger, appsettings)

    # Example log messages
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

import logging
from jgh_logging_config import configure_logging

# Configure logging
configure_logging(logging.DEBUG)

# Get the logger
logger = logging.getLogger(__name__)

def example_function() -> None:
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

if __name__ == "__main__":
    example_function()
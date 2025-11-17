import logging
import os
import json
from typing import Optional, Dict, Any

class JsonFileHandler(logging.FileHandler):
    """
    Custom logging handler that writes each log record as a flat JSON object.
    Thread-safe: uses a persistent lock for all writes.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        import threading
        self._stream_lock = threading.Lock()

    def emit(self, record: logging.LogRecord) -> None:
        log_entry: Dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "name": record.name,  # Changed from 'logger' to 'name'
            "message": record.getMessage()
        }
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        # Add extra fields (flat only)
        for key, value in record.__dict__.items():
            if key not in log_entry and key not in (
                "msg", "args", "exc_info", "exc_text", "levelno", "pathname", "filename",
                "module", "funcName", "lineno", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "logger"  # Exclude 'logger'
            ):
                if not isinstance(value, (dict, list)):
                    log_entry[key] = value
                else:
                    log_entry[key] = str(value)
        with self._stream_lock:
            self.stream.write(json.dumps(log_entry) + "\n")
            self.flush()

    def formatTime(self, record: logging.LogRecord) -> str:
        from datetime import datetime, timezone
        return datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat().replace("+00:00", "Z")

    def formatException(self, exc_info) -> str:
        import traceback
        return "".join(traceback.format_exception(*exc_info))

def setup_json_logging(log_directory: str) -> None:
    """
    Set up JSON logging to two files in the specified directory:
    - info.log.json for INFO level logs
    - events.log.json for all other levels
    At the beginning of each run, clear the log files if they exist.
    """
    os.makedirs(log_directory, exist_ok=True)
    info_log_path = os.path.join(log_directory, "info.log.json")
    events_log_path = os.path.join(log_directory, "events.log.json")

    # Clear the log files if they exist
    for log_path in (info_log_path, events_log_path):
        if os.path.exists(log_path):
            with open(log_path, "w", encoding="utf-8"):
                pass  # Truncate the file

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers = []

    class InfoOnlyFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            return record.levelno == logging.INFO

    class NotInfoFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            return record.levelno != logging.INFO

    info_handler = JsonFileHandler(info_log_path, mode="a", encoding="utf-8")
    info_handler.setLevel(logging.INFO)
    info_handler.addFilter(InfoOnlyFilter())

    events_handler = JsonFileHandler(events_log_path, mode="a", encoding="utf-8")
    events_handler.setLevel(logging.DEBUG)
    events_handler.addFilter(NotInfoFilter())

    root_logger.addHandler(info_handler)
    root_logger.addHandler(events_handler)

def log_event(
    logger: logging.Logger,
    *,
    message: str,
    level: int,
    exception: Optional[Exception] = None,
    extra_fields: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log an event with required keyword-only message and level (must be a Python logging constant), plus optional exception and extra fields.
    Ensures stack traces are included in the JSON log output for exceptions.

    Parameters:
        logger (logging.Logger): The logger instance.
        message (str): The log message. (Required keyword)
        level (int): Logging level, must be one of logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL.
        exception (Exception, optional): Exception to log (if any).
        extra_fields (dict, optional): Additional flat key-value pairs to include in the log.

    Usage:
        log_event(logger, message="Debug message", level=logging.DEBUG)
        log_event(logger, message="Info message", level=logging.INFO)
        log_event(logger, message="Warning message", level=logging.WARNING)
        log_event(logger, message="Error message", level=logging.ERROR)
        log_event(logger, message="Critical message", level=logging.CRITICAL)
    """
    allowed_levels = {
        logging.DEBUG,
        logging.INFO,
        logging.WARNING,
        logging.ERROR,
        logging.CRITICAL
    }
    if level not in allowed_levels:
        raise ValueError(f"Invalid log level: {level}. Allowed levels: {allowed_levels}")

    if extra_fields is None:
        extra_fields = {}
    for key, value in list(extra_fields.items()):
        if isinstance(value, (dict, list)):
            extra_fields[key] = str(value)
    if exception is not None:
        # Pass exc_info=True to ensure stack trace is included
        logger.log(level, message, exc_info=True, extra=extra_fields)
    else:
        logger.log(level, message, extra=extra_fields)
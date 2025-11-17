from jgh_exceptions import AlertMessageError


# =========================
# I/O Utilities
# =========================
INTERNET_CHECK_HOST = ("8.8.8.8", 53)
INTERNET_CHECK_TIMEOUT = 3
import socket

def warn_if_internet_not_connected() -> str|None:
    """
    Checks for internet connectivity.
    Returns an warning message string if not connected, or None if all is good.
    """
    try:
        socket.create_connection(INTERNET_CHECK_HOST, timeout=INTERNET_CHECK_TIMEOUT)
        return None
    except OSError:
        return "Error: No internet connection."

def throw_if_no_internet_connection() -> None:
    """
    Checks for internet connectivity and raises an exception if not connected.
    :raises JghAlertMessageException: If there is no internet connection.
    """
    warning = warn_if_internet_not_connected()
    if warning:
        raise AlertMessageError(warning)


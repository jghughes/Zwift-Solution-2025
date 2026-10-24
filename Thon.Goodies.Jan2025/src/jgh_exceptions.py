from dataclasses import dataclass, field
from typing import Optional, Dict, Any, NoReturn
import json
from jgh_exception_helpers import flatten_dict

__all__ = [
    "AppErrorBase",
    "HttpAppErrorBase",
    "AlertMessageError",
    "AppSystemError",
    "AlreadyExistsError",
    "AuthenticationError",
    "NetworkError",
    "NotFoundError",
    "AppTimeoutError",
    "AppValidationError",
    "map_azure_resource_error",
    "map_azure_value_type_error",
    "map_azure_client_authentication_error",
    "map_azure_http_response_error",
    "map_azure_resource_exists_error",
    "map_azure_resource_not_found_error",
    "map_azure_service_request_error",
    "map_azure_service_response_error",
]


# Names prefixed 'App' deliberately avoid shadowing Python builtins (SystemError, TimeoutError)
# and third-party names (e.g. pydantic.ValidationError).
# eq=False keeps identity-based __eq__/__hash__ so exceptions stay hashable.

# --- Base classes ---
@dataclass(eq=False)
class AppErrorBase(Exception):
    """
    Base class for all structured application errors.

    Inherits from Exception for use in error handling and propagation.
    Provides standard fields: 'message', 'details', and 'inner_exception' for context and serialization.
    Supports exception chaining via 'inner_exception'.
    Used for logging, reporting, and structured error management.
    Does NOT inject stack trace or context; logging helpers handle that.
    """
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    inner_exception: Optional[Exception] = None

    def __post_init__(self) -> None:
        super().__init__(self.message)
        if self.details:
            self.details = flatten_dict(self.details)

    def toDict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for k, v in self.__dict__.items():
            if v not in ("", {}, None, [], ()):
                if k == "inner_exception" and isinstance(v, Exception):
                    result["inner_exception_type"] = v.__class__.__name__
                    exc_msg = str(v)
                    if exc_msg:
                        result["inner_exception_message"] = exc_msg
                else:
                    result[k] = v
        return result

    def as_json(self) -> str:
        return json.dumps(self.toDict(), indent=2, default=str)

    def __str__(self) -> str:
        return self.as_json()

@dataclass(eq=False)
class HttpAppErrorBase(AppErrorBase):
    http_status: int = 500

# --- AppError group ---
@dataclass(eq=False)
class AlertMessageError(AppErrorBase):
    def __str__(self) -> str:
        return self.message

@dataclass(eq=False)
class AppSystemError(AppErrorBase):
    pass

# --- HttpAppError group ---
@dataclass(eq=False)
class AlreadyExistsError(HttpAppErrorBase):
    http_status: int = 409
    resource_name: str = ""

@dataclass(eq=False)
class AuthenticationError(HttpAppErrorBase):
    http_status: int = 401
    user_id: str = ""
    action: str = ""

@dataclass(eq=False)
class NetworkError(HttpAppErrorBase):
    url: str = ""

@dataclass(eq=False)
class NotFoundError(HttpAppErrorBase):
    http_status: int = 404
    resource_name: str = ""

@dataclass(eq=False)
class AppTimeoutError(HttpAppErrorBase):
    operation: str = ""
    timeout_seconds: Optional[float] = None

@dataclass(eq=False)
class AppValidationError(HttpAppErrorBase):
    http_status: int = 400
    field_name: str = ""


# --- Azure helpers ---
def _status_or_default(ex: Exception, default: int) -> int:
    status_code = getattr(ex, 'status_code', None)
    return status_code if isinstance(status_code, int) else default

def _azure_details(ex: Exception, failure: str) -> Dict[str, Any]:
    details: Dict[str, Any] = {"failure": str(failure)}
    error_code = getattr(ex, 'error_code', None)
    status_code = getattr(ex, 'status_code', None)
    if error_code is not None:
        details["azure_error_code"] = str(error_code)
    if status_code is not None:
        details["status_code"] = str(status_code)
    return details

def map_azure_resource_error(
    ex: Exception, failure: str
) -> NoReturn:
    raise AppErrorBase(
        message=f"AzureMessage: {str(ex)}",
        details=_azure_details(ex, failure),
        inner_exception=ex
    ) from ex

def map_azure_value_type_error(
    ex: Exception, failure: str
) -> NoReturn:
    raise AppValidationError(
        message=f"{failure} {str(ex)}",
        details={"failure": str(failure)},
        inner_exception=ex
    ) from ex

def map_azure_client_authentication_error(
    ex: Exception, failure: str
) -> NoReturn:
    raise AuthenticationError(
        message=f"AzureMessage: {str(ex)}",
        details={"failure": str(failure)},
        inner_exception=ex,
        http_status=401
    ) from ex

def map_azure_http_response_error(
    ex: Exception, failure: str
) -> NoReturn:
    raise NetworkError(
        message=f"AzureMessage: {str(ex)}",
        details=_azure_details(ex, failure),
        inner_exception=ex,
        http_status=_status_or_default(ex, 500)
    ) from ex

def map_azure_resource_exists_error(
    ex: Exception, failure: str
) -> NoReturn:
    raise AlreadyExistsError(
        message=f"Resource already exists: {str(ex)}",
        details=_azure_details(ex, failure),
        inner_exception=ex,
        http_status=409
    ) from ex

def map_azure_resource_not_found_error(
    ex: Exception, failure: str
) -> NoReturn:
    raise NotFoundError(
        message=f"Resource not found: {str(ex)}",
        details=_azure_details(ex, failure),
        inner_exception=ex,
        http_status=404
    ) from ex

def map_azure_service_request_error(
    ex: Exception, failure: str
) -> NoReturn:
    raise NetworkError(
        message=f"Network/Connectivity error: {str(ex)}",
        details={"failure": str(failure)},
        inner_exception=ex
    ) from ex

def map_azure_service_response_error(
    ex: Exception, failure: str
) -> NoReturn:
    raise NetworkError(
        message=f"Azure server-side error: {str(ex)}",
        details={"failure": str(failure)},
        inner_exception=ex
    ) from ex


from dataclasses import dataclass, field
from typing import Optional, Dict, Any, NoReturn
from enum import Enum
import json
from jgh_exception_helpers import flatten_dict


# --- Base classes ---
@dataclass
class AppErrorBase(Exception):
    """
    Base class for all structured application errors.
    Provides standard fields and serialization for logging and reporting.
    Does NOT inject stack trace or context; logging helpers handle that.
    """
    message: str = ""
    details: Dict[str, str] = field(default_factory=dict)
    inner_exception: Optional[Exception] = None

    """
    Base class for structured application errors.

    Inherits from Exception for use in error handling and propagation.
    Provides standard fields: 'message', 'details', and 'inner_exception' for context and serialization.
    Unlike AppSuccessBase, includes error-specific logic and supports exception chaining.
    Used for logging, reporting, and structured error management.
    """

    def __post_init__(self) -> None:
        super().__init__(self.message)
        if self.details:
            self.details = flatten_dict(self.details)


    def toDict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for k, v in self.__dict__.items():
            if v not in ("", {}, None, [], ()):
                if k == "inner_exception" and isinstance(v, Exception):
                    exc_msg = str(v)
                    if exc_msg:
                        result["inner_exception_type"] = v.__class__.__name__
                        result["inner_exception_message"] = exc_msg
                else:
                    result[k] = v
        return result

    def as_json(self) -> str:
        import json
        return json.dumps(self.toDict(), indent=2)

    def __str__(self) -> str:
        return self.as_json()

@dataclass
class HttpAppErrorBase(AppErrorBase):
    http_status: int = 500

# --- AppError group ---
@dataclass
class AlertMessageError(AppErrorBase):
    exception_type: str = ""

    def __init__(self, message: str = ""):
        super().__init__(
            message=message
        )
        self.exception_type = ""

    def __str__(self) -> str:
        return self.message

@dataclass
class SystemError(AppErrorBase):
    exception_type: str = ""

# --- HttpAppError group ---
@dataclass
class AlreadyExistsError(HttpAppErrorBase):
    resource_name: str = ""
    status_code: str = ""

@dataclass
class AuthenticationError(HttpAppErrorBase):
    user_id: str = ""
    action: str = ""

@dataclass
class NetworkError(HttpAppErrorBase):
    url: str = ""
    status_code: str = ""

@dataclass
class NotFoundError(HttpAppErrorBase):
    resource_name: str = ""
    status_code: str = ""

@dataclass
class TimeoutError(HttpAppErrorBase):
    operation: str = ""
    timeout_seconds: Optional[float] = None

@dataclass
class ValidationError(HttpAppErrorBase):
    field_name: str = ""


# --- Azure helpers ---
def map_azure_resource_error(
    ex: Exception, failure: str
) -> NoReturn:
    error_code = getattr(ex, 'error_code', None)
    status_code = getattr(ex, 'status_code', None)
    raise AppErrorBase(
        message=f"AzureMessage: {str(ex)}",
        details={
            "failure": str(failure),
            "azure_error_code": str(error_code) if error_code is not None else "",
            "status_code": str(status_code) if status_code is not None else ""
        },
        inner_exception=ex
    ) from ex

def map_azure_value_type_error(
    ex: Exception, failure: str
) -> NoReturn:
    raise ValidationError(
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
        inner_exception=ex
    ) from ex

def map_azure_http_response_error(
    ex: Exception, failure: str
) -> NoReturn:
    error_code = getattr(ex, 'error_code', None)
    status_code = getattr(ex, 'status_code', None)
    raise NetworkError(
        message=f"AzureMessage: {str(ex)}",
        details={
            "failure": str(failure),
            "azure_error_code": str(error_code) if error_code is not None else "",
            "status_code": str(status_code) if status_code is not None else ""
        },
        inner_exception=ex
    ) from ex

def map_azure_resource_exists_error(
    ex: Exception, failure: str
) -> NoReturn:
    error_code = getattr(ex, 'error_code', None)
    status_code = getattr(ex, 'status_code', None)
    raise AlreadyExistsError(
        message=f"Resource already exists: {str(ex)}",
        details={
            "failure": str(failure),
            "azure_error_code": str(error_code) if error_code is not None else "",
            "status_code": str(status_code) if status_code is not None else ""
        },
        inner_exception=ex
    ) from ex

def map_azure_resource_not_found_error(
    ex: Exception, failure: str
) -> NoReturn:
    error_code = getattr(ex, 'error_code', None)
    status_code = getattr(ex, 'status_code', None)
    raise NotFoundError(
        message=f"Resource not found: {str(ex)}",
        details={
            "failure": str(failure),
            "azure_error_code": str(error_code) if error_code is not None else "",
            "status_code": str(status_code) if status_code is not None else ""
        },
        inner_exception=ex
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


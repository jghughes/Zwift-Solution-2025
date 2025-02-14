from dataclasses import dataclass
from pydantic import BaseModel
import logging
import os

@dataclass(frozen=True)
class LoggingMessageFormat:
    message: str = "%(message)s"
    standard: str = "%(asctime)s - %(levelname)s - %(message)s - %(exc_info)s"
    verbose: str = "%(asctime)s - %(levelname)s - %(process)d - %(thread)d - %(module)s - %(funcName)s - %(message)s - %(exc_info)s"
   
    @classmethod
    def get_messageformat(cls, format_name: str | None) -> str:
        match format_name:
            case "standard":
                return cls.standard
            case "verbose":
                return cls.verbose
            case _:
                return cls.message

@dataclass(frozen=True)
class LogLevel:
    debug: int = logging.DEBUG
    info: int = logging.INFO
    warning: int = logging.WARNING
    error: int = logging.ERROR
    critical: int = logging.CRITICAL

    @classmethod
    def get_level(cls, level_name: str | None) -> int:
        if level_name is not None:
            level_name = level_name.strip().lower()
        match level_name:
            case "debug":
                return cls.debug
            case "info":
                return cls.info
            case "warning":
                return cls.warning
            case "error":
                return cls.error
            case "critical":
                return cls.critical
            case _:
                return cls.info  # Default log level

class ConsoleHandlerDataTransferObject(BaseModel):
    loglevel: str | None = None
    messageformat: str | None = None

class LocalStorageSettingsDataTransferObject(BaseModel):
    relativedirpath: str | None = None

    FILENAME: str = "logger.log"

    @classmethod
    def dirpathexists(cls) -> bool:
        if cls.relativedirpath is None:
            return False
        try:
            # Check if relativedirpath is a valid relative path
            if not os.path.isabs(cls.relativedirpath):
                abs_dirpath = os.path.abspath(cls.relativedirpath)
                if not os.path.exists(abs_dirpath):
                    return False
            else:
                return False
        except (OSError, IOError):
            return False

        return True

    @classmethod
    def get_absolutefilepath(cls) -> str | None:
        if not cls.dirpathexists():
            return None
        if not cls.relativedirpath:
            return None
        abs_dirpath: str = os.path.abspath(cls.relativedirpath)
        absolute_logfile_path = os.path.join(abs_dirpath, cls.FILENAME)
        return absolute_logfile_path

class AzureStorageSettingsDataTransferObject(BaseModel):
    connectionstring: str | None = None
    container: str | None = None
    blobname: str | None = None

class AwsStorageSettingsDataTransferObject(BaseModel):
    accesskey: str | None = None
    secretkey: str | None = None
    bucket: str | None = None
    objectname: str | None = None

class OracleStorageSettingsDataTransferObject(BaseModel):
    username: str | None = None
    password: str | None = None
    bucket: str | None = None
    objectname: str | None = None

class StorageSettingsDataTransferObject(BaseModel):
    local: LocalStorageSettingsDataTransferObject | None = None
    azure: AzureStorageSettingsDataTransferObject | None = None
    aws: AwsStorageSettingsDataTransferObject | None = None
    oracle: OracleStorageSettingsDataTransferObject | None = None

class FileHandlerDataTransferObject(BaseModel):
    loglevel: str | None = None
    messageformat: str | None = None

class LoggingHandlersDataTransferObject(BaseModel):
    console: ConsoleHandlerDataTransferObject | None = None
    file: FileHandlerDataTransferObject | None = None

class RetryPolicySettingsDataTransferObject(BaseModel):
    maxretries: int | None = None
    delay: int | None = None

class DatabaseSettingsDataTransferObject(BaseModel):
    provider: str | None = None
    connectionstring: str | None = None
    timeout: int | None = None
    pooling: bool | None = None
    maxpoolsize: int | None = None
    minpoolsize: int | None = None
    retrypolicy: RetryPolicySettingsDataTransferObject | None = None

class DatabasesSettingsDataTransferObject(BaseModel):
    primary: DatabaseSettingsDataTransferObject | None = None
    secondary: DatabaseSettingsDataTransferObject | None = None

class HeadersSettingsDataTransferObject(BaseModel):
    Content_Type: str | None = None
    Accept: str | None = None
    Authorization: str | None = None
    User_Agent: str | None = None
    Cache_Control: str | None = None
    Custom_Header: str | None = None
    Accept_Encoding: str | None = None

class ApiEndpointsDataTransferObject(BaseModel):
    get: str | None = None
    create: str | None = None
    update: str | None = None
    delete: str | None = None
    getByFilter: str | None = None

class ApiSettingsDataTransferObject(BaseModel):
    baseurl: str | None = None
    apikey: str | None = None
    version: str | None = None
    timeout: int | None = None
    retrypolicy: RetryPolicySettingsDataTransferObject | None = None
    headers: HeadersSettingsDataTransferObject | None = None
    endpoints: ApiEndpointsDataTransferObject | None = None

class ApisSettingsDataTransferObject(BaseModel):
    primary: ApiSettingsDataTransferObject | None = None
    secondary: ApiSettingsDataTransferObject | None = None

class EnvironmentSettingsDataTransferObject(BaseModel):
    name: str | None = None

class AppSettingsDataTransferObject(BaseModel):
    logging: LoggingHandlersDataTransferObject | None = None
    storage: StorageSettingsDataTransferObject | None = None
    databases: DatabasesSettingsDataTransferObject | None = None
    apis: ApisSettingsDataTransferObject | None = None
    environment: EnvironmentSettingsDataTransferObject | None = None


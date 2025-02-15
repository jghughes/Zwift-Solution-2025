from dataclasses import dataclass
from pydantic import BaseModel
import logging
import os
import json

@dataclass(frozen=True)
class LoggingMessageFormat:
    message: str = "%(message)s"
    standard: str = "%(asctime)s %(levelname)s - %(message)s - %(exc_info)s"
    verbose: str = "%(asctime)s %(levelname)s - %(process)d - %(thread)d - %(module)s - %(funcName)s - %(message)s - %(exc_info)s"
   
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
        absolute_logfile_path = os.path.join(abs_dirpath, "logger.log")
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

class LogFileHandlerDataTransferObject(BaseModel):
    loglevel: str | None = None
    messageformat: str | None = None

class LoggingHandlersDataTransferObject(BaseModel):
    console: ConsoleHandlerDataTransferObject | None = None
    file: LogFileHandlerDataTransferObject | None = None

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
    environment: EnvironmentSettingsDataTransferObject | None = None
    logging: LoggingHandlersDataTransferObject | None = None
    storage: StorageSettingsDataTransferObject | None = None
    databases: DatabasesSettingsDataTransferObject | None = None
    apis: ApisSettingsDataTransferObject | None = None

if __name__ == "__main__":
    # Create an instance of AppSettingsDataTransferObject with realistic test data
    app_settings = AppSettingsDataTransferObject(
        environment=EnvironmentSettingsDataTransferObject(name="development"),
        logging=LoggingHandlersDataTransferObject(
            console=ConsoleHandlerDataTransferObject(
                loglevel="debug",
                messageformat="standard"
            ),
            file=LogFileHandlerDataTransferObject(
                loglevel="info",
                messageformat="verbose"
            )
        ),
        storage=StorageSettingsDataTransferObject(
            local=LocalStorageSettingsDataTransferObject(
                relativedirpath="logs"
            ),
            azure=AzureStorageSettingsDataTransferObject(
                connectionstring="your-azure-connection-string",
                container="your-container-name",
                blobname="your-blob-name"
            ),
            aws=AwsStorageSettingsDataTransferObject(
                accesskey="your-aws-access-key",
                secretkey="your-aws-secret-key",
                bucket="your-bucket-name",
                objectname="your-object-name"
            ),
            oracle=OracleStorageSettingsDataTransferObject(
                username="your-oracle-username",
                password="your-oracle-password",
                bucket="your-bucket-name",
                objectname="your-object-name"
            )
        ),
        databases=DatabasesSettingsDataTransferObject(
            primary=DatabaseSettingsDataTransferObject(
                provider="SQLServer",
                connectionstring="Server=myServerAddress;Database=myDataBase;User Id=myUsername;Password=myPassword;",
                timeout=30,
                pooling=True,
                maxpoolsize=100,
                minpoolsize=10,
                retrypolicy=RetryPolicySettingsDataTransferObject(
                    maxretries=3,
                    delay=2000
                )
            ),
            secondary=DatabaseSettingsDataTransferObject(
                provider="SQLServer",
                connectionstring="Server=thirdPartyServerAddress;Database=thirdPartyDataBase;User Id=thirdPartyUsername;Password=thirdPartyPassword;",
                timeout=30,
                pooling=True,
                maxpoolsize=100,
                minpoolsize=10,
                retrypolicy=RetryPolicySettingsDataTransferObject(
                    maxretries=3,
                    delay=2000
                )
            )
        ),
        apis=ApisSettingsDataTransferObject(
            primary=ApiSettingsDataTransferObject(
                baseurl="https://api.example.com",
                apikey="your-api-key-here",
                version="v1",
                timeout=30,
                retrypolicy=RetryPolicySettingsDataTransferObject(
                    maxretries=3,
                    delay=2000
                ),
                headers=HeadersSettingsDataTransferObject(
                    Content_Type="application/json",
                    Accept="application/json",
                    Authorization="Bearer your-token-here",
                    User_Agent="YourAppName/1.0",
                    Cache_Control="no-cache",
                    Custom_Header="custom-value",
                    Accept_Encoding="gzip, deflate"
                ),
                endpoints=ApiEndpointsDataTransferObject(
                    get="/users/{id}",
                    create="/users",
                    update="/users/{id}",
                    delete="/users/{id}",
                    getByFilter="/users?filter={filter}"
                )
            ),
            secondary=ApiSettingsDataTransferObject(
                baseurl="https://secondaryapi.example.com",
                apikey="another-api-key-here",
                version="v2",
                timeout=30,
                retrypolicy=RetryPolicySettingsDataTransferObject(
                    maxretries=3,
                    delay=2000
                ),
                headers=HeadersSettingsDataTransferObject(
                    Content_Type="application/json",
                    Accept="application/json",
                    Authorization="Bearer another-token-here",
                    User_Agent="YourAppName/1.0",
                    Cache_Control="no-cache",
                    Custom_Header="another-custom-value",
                    Accept_Encoding="gzip, deflate"
                ),
                endpoints=ApiEndpointsDataTransferObject(
                    get="/products?id={id}",
                    create="/products",
                    update="/products?id={id}",
                    delete="/products?id={id}",
                    getByFilter="/products?filter={filter}"
                )
            )
        )
    )

    # Serialize the instance to JSON
    app_settings_json = app_settings.model_dump_json(indent=4)
    print(app_settings_json)

        # Write some assertions
    assert app_settings.environment.name == "development"
    assert app_settings.logging.console.loglevel == "debug"
    assert app_settings.logging.console.messageformat == "standard"
    assert app_settings.logging.file.loglevel == "info"
    assert app_settings.logging.file.messageformat == "verbose"
    assert app_settings.storage.local.relativedirpath == "logs"
    assert app_settings.storage.azure.connectionstring == "your-azure-connection-string"
    assert app_settings.storage.aws.accesskey == "your-aws-access-key"
    assert app_settings.storage.oracle.username == "your-oracle-username"

    # Deserialize the JSON back to an instance of AppSettingsDataTransferObject
    app_settings = AppSettingsDataTransferObject.model_validate_json(app_settings_json)


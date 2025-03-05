from pydantic import BaseModel
import os
from typing import Optional


# Configure logging

class ConsoleHandlerDataTransferObject(BaseModel):
    loglevel: Optional[str] = None
    messageformat: Optional[str] = None

class LogFileHandlerDataTransferObject(BaseModel):
    loglevel: Optional[str] = None
    messageformat: Optional[str] = None

class LoggingHandlersDataTransferObject(BaseModel):
    console: Optional[ConsoleHandlerDataTransferObject] = None
    file: Optional[LogFileHandlerDataTransferObject] = None


class LocalStorageSettingsDataTransferObject(BaseModel):
    relativedirpath: Optional[str] = None

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
    def get_absolutefilepath(cls) -> Optional[str]:
        if not cls.dirpathexists():
            return None
        if not cls.relativedirpath:
            return None
        abs_dirpath: str = os.path.abspath(cls.relativedirpath)
        absolute_logfile_path = os.path.join(abs_dirpath, "logger.log")
        return absolute_logfile_path

class AzureStorageSettingsDataTransferObject(BaseModel):
    connectionstring: Optional[str] = None
    container: Optional[str] = None
    blobname: Optional[str] = None

class AwsStorageSettingsDataTransferObject(BaseModel):
    accesskey: Optional[str] = None
    secretkey: Optional[str] = None
    bucket: Optional[str] = None
    objectname: Optional[str] = None

class OracleStorageSettingsDataTransferObject(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    bucket: Optional[str] = None
    objectname: Optional[str] = None

class StorageSettingsDataTransferObject(BaseModel):
    local: Optional[LocalStorageSettingsDataTransferObject] = None
    azure: Optional[AzureStorageSettingsDataTransferObject] = None
    aws: Optional[AwsStorageSettingsDataTransferObject] = None
    oracle: Optional[OracleStorageSettingsDataTransferObject] = None


class RetryPolicySettingsDataTransferObject(BaseModel):
    maxretries: Optional[int] = None
    delay: Optional[int] = None

class DatabaseSettingsDataTransferObject(BaseModel):
    provider: Optional[str] = None
    connectionstring: Optional[str] = None
    timeout: Optional[int] = None
    pooling: Optional[bool] = None
    maxpoolsize: Optional[int] = None
    minpoolsize: Optional[int] = None
    retrypolicy: Optional[RetryPolicySettingsDataTransferObject] = None

class DatabasesSettingsDataTransferObject(BaseModel):
    primary: Optional[DatabaseSettingsDataTransferObject] = None
    secondary: Optional[DatabaseSettingsDataTransferObject] = None

class HeadersSettingsDataTransferObject(BaseModel):
    Content_Type: Optional[str] = None
    Accept: Optional[str] = None
    Authorization: Optional[str] = None
    User_Agent: Optional[str] = None
    Cache_Control: Optional[str] = None
    Custom_Header: Optional[str] = None
    Accept_Encoding: Optional[str] = None

class ApiEndpointsDataTransferObject(BaseModel):
    get: Optional[str] = None
    create: Optional[str] = None
    update: Optional[str] = None
    delete: Optional[str] = None
    getByFilter: Optional[str] = None

class ApiSettingsDataTransferObject(BaseModel):
    baseurl: Optional[str] = None
    apikey: Optional[str] = None
    version: Optional[str] = None
    timeout: Optional[int] = None
    retrypolicy: Optional[RetryPolicySettingsDataTransferObject] = None
    headers: Optional[HeadersSettingsDataTransferObject] = None
    endpoints: Optional[ApiEndpointsDataTransferObject] = None

class ApisSettingsDataTransferObject(BaseModel):
    primary: Optional[ApiSettingsDataTransferObject] = None
    secondary: Optional[ApiSettingsDataTransferObject] = None

class EnvironmentSettingsDataTransferObject(BaseModel):
    name: Optional[str] = None

class AppSettingsDataTransferObject(BaseModel):
    environment: Optional[EnvironmentSettingsDataTransferObject] = None
    logging: Optional[LoggingHandlersDataTransferObject] = None
    storage: Optional[StorageSettingsDataTransferObject] = None
    databases: Optional[DatabasesSettingsDataTransferObject] = None
    apis: Optional[ApisSettingsDataTransferObject] = None


def main():

    # Create an instance of AppSettingsDataTransferObject with realistic test data
    app_settings = AppSettingsDataTransferObject(
        environment=EnvironmentSettingsDataTransferObject(name="development"),
        logging=LoggingHandlersDataTransferObject(
            console=ConsoleHandlerDataTransferObject(
                loglevel="debug",
                messageformat="balanced"
            ),
            file=LogFileHandlerDataTransferObject(
                loglevel="info",
                messageformat="informative"
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
    assert app_settings.logging.console.messageformat == "balanced"
    assert app_settings.logging.file.loglevel == "info"
    assert app_settings.logging.file.messageformat == "informative"
    assert app_settings.storage.local.relativedirpath == "logs"
    assert app_settings.storage.azure.connectionstring == "your-azure-connection-string"
    assert app_settings.storage.aws.accesskey == "your-aws-access-key"
    assert app_settings.storage.oracle.username == "your-oracle-username"

    # Deserialize the JSON back to an instance of AppSettingsDataTransferObject
    app_settings = AppSettingsDataTransferObject.model_validate_json(app_settings_json)

if __name__ == "__main__":
    main()


from pydantic import BaseModel

class ConsoleHandlerDataTransferObject(BaseModel):
    loglevel: str | None = None
    formatstring: str | None = None
    handlername: str | None = None

class LocalStorageSettingsDataTransferObject(BaseModel):
    dirpath: str | None = None
    filename: str | None = None

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

class RotationSettingsDataTransferObject(BaseModel):
    when: str | None = None
    interval: int | None = None
    backupcount: int | None = None

class FileHandlerDataTransferObject(BaseModel):
    loglevel: str | None = None
    formatstring: str | None = None
    handlername: str | None = None
    maxfilesize: int | None = None
    rotation: RotationSettingsDataTransferObject | None = None
    storage: StorageSettingsDataTransferObject | None = None

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
    databases: DatabasesSettingsDataTransferObject | None = None
    apis: ApisSettingsDataTransferObject | None = None
    environment: EnvironmentSettingsDataTransferObject | None = None

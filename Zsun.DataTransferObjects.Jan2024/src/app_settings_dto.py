from pydantic import BaseModel

class ConsoleLoggingSettings(BaseModel):
    loglevel: str | None = ""
    format: str | None = ""
    simpleformat: str | None = ""
    verboseformat: str | None = ""
    jsonformat: str | None = ""

class LocalStorageSettings(BaseModel):
    path: str | None = ""

class AzureStorageSettings(BaseModel):
    connectionstring: str | None = ""
    container: str | None = ""
    blobname: str | None = ""

class AwsStorageSettings(BaseModel):
    accesskey: str | None = ""
    secretkey: str | None = ""
    bucket: str | None = ""
    objectname: str | None = ""

class OracleStorageSettings(BaseModel):
    username: str | None = ""
    password: str | None = ""
    bucket: str | None = ""
    objectname: str | None = ""

class StorageSettings(BaseModel):
    type: str | None = ""
    local: LocalStorageSettings | None = LocalStorageSettings()
    azure: AzureStorageSettings | None = AzureStorageSettings()
    aws: AwsStorageSettings | None = AwsStorageSettings()
    oracle: OracleStorageSettings | None = OracleStorageSettings()

class RotationSettings(BaseModel):
    when: str | None = ""
    interval: int | None = 0
    backupcount: int | None = 0

class FileLoggingSettings(BaseModel):
    loglevel: str | None = ""
    format: str | None = ""
    simpleformat: str | None = ""
    verboseformat: str | None = ""
    jsonformat: str | None = ""
    maxfilesize: int | None = 0
    rotation: RotationSettings | None = RotationSettings()
    storage: StorageSettings | None = StorageSettings()

class LoggingSettings(BaseModel):
    console: ConsoleLoggingSettings | None = ConsoleLoggingSettings()
    file: FileLoggingSettings | None = FileLoggingSettings()

class RetryPolicySettings(BaseModel):
    maxretries: int | None = 0
    delay: int | None = 0

class DatabaseSettings(BaseModel):
    provider: str | None = ""
    connectionstring: str | None = ""
    timeout: int | None = 0
    pooling: bool | None = False
    maxpoolsize: int | None = 0
    minpoolsize: int | None = 0
    retrypolicy: RetryPolicySettings | None = RetryPolicySettings()

class DatabasesSettings(BaseModel):
    primary: DatabaseSettings | None = DatabaseSettings()
    external: DatabaseSettings | None = DatabaseSettings()

class HeadersSettings(BaseModel):
    Content_Type: str | None = ""
    Accept: str | None = ""
    Authorization: str | None = ""
    User_Agent: str | None = ""
    Cache_Control: str | None = ""
    Custom_Header: str | None = ""
    Accept_Encoding: str | None = ""

class EndpointsSettings(BaseModel):
    get: str | None = ""
    create: str | None = ""
    update: str | None = ""
    delete: str | None = ""
    getByFilter: str | None = ""

class ApiSettings(BaseModel):
    baseurl: str | None = ""
    apikey: str | None = ""
    version: str | None = ""
    timeout: int | None = 0
    retrypolicy: RetryPolicySettings | None = RetryPolicySettings()
    headers: HeadersSettings | None = HeadersSettings()
    endpoints: EndpointsSettings | None = EndpointsSettings()

class ApisSettings(BaseModel):
    exampleapi: ApiSettings | None = ApiSettings()
    anotherapi: ApiSettings | None = ApiSettings()

class EnvironmentSettings(BaseModel):
    name: str | None = ""

class AppSettingsDataTransferObject(BaseModel):
    logging: LoggingSettings | None = LoggingSettings()
    databases: DatabasesSettings | None = DatabasesSettings()
    apis: ApisSettings | None = ApisSettings()
    environment: EnvironmentSettings | None = EnvironmentSettings()

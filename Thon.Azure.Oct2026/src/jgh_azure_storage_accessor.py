import functools
from typing import Any, Awaitable, Callable, Coroutine, List, Optional, ParamSpec, TypeVar

from azure.core.exceptions import (
    AzureError, ClientAuthenticationError, HttpResponseError, ResourceExistsError, ResourceNotFoundError,
    ServiceRequestError, ServiceResponseError
)
from azure.storage.blob import BlobProperties, ContentSettings, StorageErrorCode
from azure.storage.blob.aio import BlobServiceClient, ContainerClient

from jgh_mime_type_map import get_extension_from_name, get_mime_type
from jgh_exceptions import (
    map_azure_client_authentication_error, map_azure_http_response_error, map_azure_resource_error,
    map_azure_resource_exists_error, map_azure_resource_not_found_error, map_azure_service_request_error,
    map_azure_service_response_error, map_azure_value_type_error
)

P = ParamSpec("P")
T = TypeVar("T")


def maps_azure_exceptions(
    failureMessage: str,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Coroutine[Any, Any, T]]]:
    """
    Decorator for async methods. Translates Azure SDK exceptions into the application's own exceptions
    (see jgh_exceptions.py) so that Azure exception types never propagate to callers.
    Clause order matters: ClientAuthenticationError, ResourceNotFoundError and ResourceExistsError are
    subclasses of HttpResponseError and must be matched first. Any other AzureError is mapped to the
    generic AppErrorBase as a catch-all, so no Azure exception type ever escapes.
    """
    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Coroutine[Any, Any, T]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return await func(*args, **kwargs)
            except ClientAuthenticationError as ex:
                map_azure_client_authentication_error(ex, failureMessage)
            except ServiceRequestError as ex:
                map_azure_service_request_error(ex, failureMessage)
            except ServiceResponseError as ex:
                map_azure_service_response_error(ex, failureMessage)
            except ResourceNotFoundError as ex:
                map_azure_resource_not_found_error(ex, failureMessage)
            except ResourceExistsError as ex:
                map_azure_resource_exists_error(ex, failureMessage)
            except HttpResponseError as ex:
                map_azure_http_response_error(ex, failureMessage)
            except AzureError as ex:
                map_azure_resource_error(ex, failureMessage)
            except (ValueError, TypeError) as ex:
                map_azure_value_type_error(ex, failureMessage)
        return wrapper
    return decorator


async def _create_container_if_not_exists_async(container_client: ContainerClient) -> bool:
    """
    Creates the container. Returns False if it already existed. Only the ContainerAlreadyExists error is
    swallowed: other 409 conflicts (e.g. ContainerBeingDeleted) are re-raised.
    """
    try:
        await container_client.create_container()
        return True
    except ResourceExistsError as ex:
        if getattr(ex, "error_code", None) == StorageErrorCode.CONTAINER_ALREADY_EXISTS:
            return False
        raise


class AzureStorageAccessor():
    """
    Async accessor over Azure Blob Storage. Every public method opens its own BlobServiceClient from the
    connection string passed in, and closes it before returning.

    Error contract (applies to every public method, so the method docstrings do not repeat it):
      - Azure SDK exceptions never escape. They are translated by maps_azure_exceptions into the application's
        own exceptions (jgh_exceptions.py).
      - AuthenticationError means the credentials themselves were rejected: a wrong account key, an invalid or
        expired SAS signature. HTTP 401, or an Azure error code of AuthenticationFailed or
        InvalidAuthenticationInfo.
      - Valid credentials that lack permission for the operation are NOT reported as AuthenticationError.
        Azure answers with HTTP 403 (error codes such as AuthorizationPermissionMismatch or
        AuthorizationFailure), the SDK raises a plain HttpResponseError, and it arrives as NetworkError with
        http_status 403. Examples: a SAS token without the read, write, create, delete or list permission, an
        RBAC identity without the needed role, or a storage firewall rule blocking the caller's IP address.
        Callers who need to tell a permissions problem from a connectivity problem must check
        NetworkError.http_status (or details["status_code"]) for 403. The message and details carry the Azure
        error code.
      - Other HTTP failures (for example a 400 for an invalid name) also arrive as NetworkError, with the
        status in http_status. Unreachable or non-responding services arrive as NetworkError with no HTTP
        status. Failures that fit none of the above arrive as the generic AppErrorBase.
      - A missing blob or container is a normal answer for the get_if_*, delete_*_if_exists and
        get_absolute_uri methods, and is an error (NotFoundError) for the list and download methods.
    """

    @maps_azure_exceptions("Unable to determine if container exists.")
    async def get_if_container_exists_async(self, storage_account_connection_string: str, container_name: str) -> bool:
        """
        Returns True if the container exists, False if it does not. A missing container is a normal answer here,
        not an error, so NotFoundError is never raised by this method.

        Raises (translated by the decorator to the application's own exceptions) AppValidationError if the
        connection string or container name is malformed or empty, AuthenticationError if the credentials are
        rejected, and NetworkError if the service is unreachable, times out or returns an unexpected HTTP error.
        Any other Azure failure is raised as the generic AppErrorBase.
        """
        async with BlobServiceClient.from_connection_string(storage_account_connection_string) as blob_service_client:
            container_client = blob_service_client.get_container_client(container_name)
            return await container_client.exists()

    @maps_azure_exceptions("Unable to create container.")
    async def create_container_async(self, storage_account_connection_string: str, container_name: str) -> bool:
        """
        Returns True once the container exists, whether it was newly created or was already present. A container
        that already exists is a normal outcome, so this method is idempotent and returns True rather than raising.
        The return value therefore does not tell the caller which of the two happened.

        Raises (translated by the decorator to the application's own exceptions) AppValidationError if the
        connection string or container name is malformed or empty, AuthenticationError if the credentials are
        rejected, and NetworkError if the service is unreachable, times out, or rejects the request with an
        unexpected HTTP error (for example 400 for a container name that breaks Azure's naming rules).
        AlreadyExistsError is raised only for a conflict other than "container already exists", such as a
        container that is still being deleted. In that case the caller should wait and retry.
        Any other Azure failure is raised as the generic AppErrorBase.
        """
        async with BlobServiceClient.from_connection_string(storage_account_connection_string) as blob_service_client:
            container_client = blob_service_client.get_container_client(container_name)
            await _create_container_if_not_exists_async(container_client)
            return True  # Already exists is not an error

    @maps_azure_exceptions("Unable to list blobs.")
    async def list_blobs_in_container_async(
        self,
        storage_account_connection_string: str,
        container_name: str,
        name_starts_with: Optional[str] = None,
        name_contains: Optional[str] = None,
    ) -> List[BlobProperties]:
        """
        Returns the BlobProperties of the blobs in a container, in lexicographic order of blob name.

        Filters (both are case-sensitive, and when both are given a blob must satisfy both):

        name_starts_with  -- SERVER-SIDE filter. Matches the start of the full blob name, including 
                             any virtual folder path. Sentinels meaning "no prefix filter, consider every blob":
                               None  -- the default; the filter is not supplied.
                               ""    -- an empty prefix; every name starts with "", so it is treated as None.
                               "*"   -- treated as None, NOT as a literal asterisk. Azure has no wildcard
                                        support, so "*" is accepted only for compatibility with the old
                                        "all blobs" convention. A blob name that really starts with "*"
                                        cannot be selected with this parameter.
                             Any other value is a literal prefix. No wildcards or regular expressions are interpreted.

        name_contains     -- CLIENT-SIDE filter. Azure cannot search for a substring, so every blob that survives
                             name_starts_with is fetched and then tested with `name_contains in blob.name`.
                             Combine it with name_starts_with to reduce the number of blobs fetched.
                             Sentinels meaning "no substring filter":
                               None, "", "*"  -- exactly as for name_starts_with ("*" is not a literal here either).
                             Any other value is a literal substring, matched anywhere in the full blob name.

        Raises (translated by the decorator to the application's own exceptions) NotFoundError if the container
        does not exist, AppValidationError if the connection string or container name is malformed or empty,
        AuthenticationError if the credentials are rejected, and NetworkError if the service is unreachable,
        times out or returns an unexpected HTTP error. Any other Azure failure is raised as the generic AppErrorBase.
        """
        prefix = _normalise_filter(name_starts_with)
        substring = _normalise_filter(name_contains)

        blobs: List[BlobProperties] = []
        async with BlobServiceClient.from_connection_string(storage_account_connection_string) as blob_service_client:
            container_client = blob_service_client.get_container_client(container_name)
            async for properties_of_blob in container_client.list_blobs(name_starts_with=prefix):
                if substring is None or substring in properties_of_blob.name:
                    blobs.append(properties_of_blob)
        return blobs

    @maps_azure_exceptions("Unable to determine if blob exists.")
    async def get_if_blob_exists_async(
        self,
        storage_account_connection_string: str,
        container_name: str,
        blob_name: str
    ) -> bool:
        """
        Returns True if the blob exists, False if it does not. A missing blob is a normal answer here, not an error.
        False is also returned if the container itself does not exist, because Azure reports both as "not found".
        NotFoundError is therefore never raised by this method.

        Raises (translated by the decorator to the application's own exceptions) AppValidationError if the
        connection string, container name or blob name is malformed or empty, AuthenticationError if the
        credentials are rejected, and NetworkError if the service is unreachable, times out or returns an
        unexpected HTTP error. Any other Azure failure is raised as the generic AppErrorBase.
        """
        async with BlobServiceClient.from_connection_string(storage_account_connection_string) as blob_service_client:
            blob_client = blob_service_client.get_blob_client(container_name, blob_name)
            return await blob_client.exists()

    @maps_azure_exceptions("Unable to delete blob.")
    async def delete_blob_if_exists_async(
        self,
        storage_account_connection_string: str,
        container_name: str,
        blob_name: str
    ) -> bool:
        """
        Returns True if the blob (and its snapshots) was deleted, False if it was not found. A missing blob is a
        normal outcome, so this method is idempotent. False is also returned if the container itself does not
        exist, because Azure reports both as "not found", so the caller cannot distinguish the two cases.
        NotFoundError is therefore never raised by this method.

        Raises (translated by the decorator to the application's own exceptions) AppValidationError if the
        connection string, container name or blob name is malformed or empty, AuthenticationError if the
        credentials are rejected, and NetworkError if the service is unreachable, times out or returns an
        unexpected HTTP error. Any other Azure failure is raised as the generic AppErrorBase. See the class
        docstring for how permission failures (HTTP 403) are reported.
        """
        async with BlobServiceClient.from_connection_string(storage_account_connection_string) as blob_service_client:
            blob_client = blob_service_client.get_blob_client(container_name, blob_name)
            try:
                await blob_client.delete_blob(delete_snapshots="include")
                return True
            except ResourceNotFoundError:
                # A single round trip, and no race between an exists check and the delete.
                # Note: a missing container also raises ResourceNotFoundError and is treated as "blob not present".
                return False

    @maps_azure_exceptions("Unable to obtain uri of blob.")
    async def get_absolute_uri_of_blob_async(
        self,
        storage_account_connection_string: str,
        container_name: str,
        blob_name: str
    ) -> Optional[str]:
        """
        Returns the blob's absolute URL, or None if the blob does not exist. None is also returned if the
        container itself does not exist, because Azure reports both as "not found". A missing blob is a normal
        answer here, not an error, so NotFoundError is never raised by this method. The blob's existence is
        checked in a separate round trip, so the URL means "the blob existed a moment ago", not a guarantee
        that it still exists.

        The URL is percent-encoded, so a blob named "my file.txt" is returned as ".../my%20file.txt". This is the
        valid form and can be used directly in an HTTP request. Do not decode and re-encode it, and do not pass it
        back in as a blob_name. Use urllib.parse.unquote only for display.

        The URL carries no credentials if the connection string uses an account key, so the caller can open it
        only if the blob is publicly readable. If the connection string uses a SAS token, the token is appended
        to the URL as a query string. The URL is then a live credential and must not be logged, displayed or
        shared more widely than the token's permissions and expiry justify.

        Raises (translated by the decorator to the application's own exceptions) AppValidationError if the
        connection string, container name or blob name is malformed or empty, AuthenticationError if the
        credentials are rejected, and NetworkError if the service is unreachable, times out or returns an
        unexpected HTTP error. Any other Azure failure is raised as the generic AppErrorBase.
        """
        async with BlobServiceClient.from_connection_string(storage_account_connection_string) as blob_service_client:
            blob_client = blob_service_client.get_blob_client(container_name, blob_name)
            if not await blob_client.exists():
                return None
            return blob_client.url

    @maps_azure_exceptions("Unable to upload.")
    async def upload_string_async(
        self,
        storage_account_connection_string: str,
        container_name: str,
        blob_name: str,
        blob_contents: str,
        create_container_if_not_exist: bool,
    ) -> str:
        """
        Returns the absolute URL of the uploaded blob. The string is stored UTF-8 encoded.
        Overwrites an existing blob with the same name without warning, so AlreadyExistsError is never raised for
        the blob. If create_container_if_not_exist is True, a missing container is created first, and a
        container that already exists is not an error.

        The returned URL is percent-encoded, so a blob named "my file.txt" is returned as ".../my%20file.txt". This
        is the valid form for an HTTP request. Do not pass it back in as a blob_name. It carries no credentials with
        an account-key connection string, but includes the SAS token as a query string if the connection string
        uses one, in which case treat the URL as a secret.

        Raises (translated by the decorator to the application's own exceptions) AppValidationError if
        blob_contents is not a str, or if the connection string, container name or blob name is malformed or
        empty. NotFoundError is raised if the container does not exist and create_container_if_not_exist is
        False. AuthenticationError is raised if the credentials are rejected, and NetworkError if the service is
        unreachable, times out or returns an unexpected HTTP error. AlreadyExistsError is raised only if the
        container must be created but a conflicting operation blocks it, such as the container still being
        deleted. In that case the caller should wait and retry. Any other Azure failure is raised as the generic
        AppErrorBase. If an error is raised, the caller should not
        assume that the blob was left unchanged.
        """
        if not isinstance(blob_contents, str):
            raise TypeError(f"blob_contents must be str, not {type(blob_contents).__name__}.")
        return await self.upload_bytes_async(
            storage_account_connection_string,
            container_name,
            blob_name,
            blob_contents.encode("utf-8"),
            create_container_if_not_exist
        )

    @maps_azure_exceptions("Unable to upload.")
    async def upload_bytes_async(
        self,
        storage_account_connection_string: str,
        container_name: str,
        blob_name: str,
        blob_contents: bytes,
        create_container_if_not_exist: bool,
    ) -> str:
        """
        Returns the absolute URL of the uploaded blob. Its content type is inferred from the blob name's extension.
        Overwrites an existing blob with the same name without warning, so AlreadyExistsError is never raised for
        the blob. If create_container_if_not_exist is True, a missing container is created first, and a
        container that already exists is not an error.

        The returned URL is percent-encoded, so a blob named "my file.txt" is returned as ".../my%20file.txt". This
        is the valid form for an HTTP request. Do not pass it back in as a blob_name. It carries no credentials with
        an account-key connection string, but includes the SAS token as a query string if the connection string
        uses one, in which case treat the URL as a secret.

        Raises (translated by the decorator to the application's own exceptions) AppValidationError if
        blob_contents is not bytes, bytearray or memoryview, or if the connection string, container name or blob
        name is malformed or empty. NotFoundError is raised if the container does not exist and
        create_container_if_not_exist is False. AuthenticationError is raised if the credentials are rejected,
        and NetworkError if the service is unreachable, times out or returns an unexpected HTTP error.
        AlreadyExistsError is raised only if the container must be created but a conflicting operation blocks it,
        such as the container still being deleted. In that case the caller should wait and retry. Any other Azure
        failure is raised as the generic AppErrorBase. If an error is raised, the caller should not assume that
        the blob was left unchanged.
        """ 
        if not isinstance(blob_contents, (bytes, bytearray, memoryview)):
            raise TypeError(f"blob_contents must be bytes, bytearray or memoryview, not {type(blob_contents).__name__}.")
        async with BlobServiceClient.from_connection_string(storage_account_connection_string) as blob_service_client:
            container_client = blob_service_client.get_container_client(container_name)
            if create_container_if_not_exist:
                await _create_container_if_not_exists_async(container_client)
            blob_client = container_client.get_blob_client(blob_name)
            most_likely_mime_type_title = get_mime_type(get_extension_from_name(blob_name))
            await blob_client.upload_blob(
                blob_contents,
                overwrite=True,
                content_settings=ContentSettings(content_type=most_likely_mime_type_title)
            )
            return blob_client.url

    @maps_azure_exceptions("Unable to download blob.")
    async def download_async(
        self,
        storage_account_connection_string: str,
        container_name: str,
        blob_name: str
    ) -> bytes:
        """
        Returns the blob's full contents as bytes, read entirely into memory. This is unsuitable for very large
        blobs. An empty blob returns b"".

        Raises (translated by the decorator to the application's own exceptions) NotFoundError if the blob does
        not exist, or if the container does not exist, because Azure reports both as "not found" and the caller
        cannot distinguish them. AppValidationError is raised if the connection string, container name or blob
        name is malformed or empty. AuthenticationError is raised if the credentials are rejected, and
        NetworkError if the service is unreachable, times out or returns an unexpected HTTP error. Any other
        Azure failure is raised as the generic AppErrorBase. A failure part-way through the transfer is also
        raised, never returned as truncated data.
        """
        async with BlobServiceClient.from_connection_string(storage_account_connection_string) as blob_service_client:
            blob_client = blob_service_client.get_blob_client(container_name, blob_name)
            downloader = await blob_client.download_blob()
            return await downloader.readall()

def _normalise_filter(value: Optional[str]) -> Optional[str]:
    """
    Maps the 'no filter' sentinels (None, "" and "*") to None. Any other value is returned unchanged.
    """
    return None if value in (None, "", "*") else value
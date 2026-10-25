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

    @maps_azure_exceptions("Unable to determine if container exists.")
    async def get_if_container_exists_async(self, storage_account_connection_string: str, container_name: str) -> bool:
        """
        Returns True if the container exists, False if it does not.
        """
        async with BlobServiceClient.from_connection_string(storage_account_connection_string) as blob_service_client:
            container_client = blob_service_client.get_container_client(container_name)
            return await container_client.exists()

    @maps_azure_exceptions("Unable to create container.")
    async def create_container_async(self, storage_account_connection_string: str, container_name: str) -> bool:
        """
        Returns True once the container exists, whether newly created or already present.
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
        blob_name_filter: Optional[str] = None
    ) -> List[BlobProperties]:
        """
        Returns the BlobProperties of each blob whose name contains blob_name_filter. All blobs are returned if the filter is None, empty or "*".
        """
        blobs: List[BlobProperties] = []
        async with BlobServiceClient.from_connection_string(storage_account_connection_string) as blob_service_client:
            container_client = blob_service_client.get_container_client(container_name)
            async for properties_of_blob in container_client.list_blobs():
                if not blob_name_filter or blob_name_filter == "*" or blob_name_filter in properties_of_blob.name:
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
        Returns True if the blob exists, False if it does not.
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
        Returns True if the blob (and its snapshots) was deleted, False if it was not found, including when the container is missing.
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
        Returns the blob's absolute URL, or None if the blob does not exist.
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
        Overwrites an existing blob with the same name.
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
        Overwrites an existing blob with the same name.
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
        Returns the blob's full contents as bytes. Raises if the blob does not exist.
        """
        async with BlobServiceClient.from_connection_string(storage_account_connection_string) as blob_service_client:
            blob_client = blob_service_client.get_blob_client(container_name, blob_name)
            downloader = await blob_client.download_blob()
            return await downloader.readall()


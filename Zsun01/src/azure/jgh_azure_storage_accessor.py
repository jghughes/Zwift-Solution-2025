from abc import ABC, abstractmethod
from typing import Any, List, Optional

from azure.core.exceptions import (
    ClientAuthenticationError, HttpResponseError, ResourceExistsError, ResourceNotFoundError,
    ServiceRequestError, ServiceResponseError
)
from azure.storage.blob import BlobProperties, ContentSettings
from azure.storage.blob.aio import BlobServiceClient

from jgh_mime_type_map import get_extension_from_name, get_mime_type
from jgh_exceptions import (
    map_azure_client_authentication_error, map_azure_http_response_error, map_azure_resource_exists_error,
    map_azure_resource_not_found_error, map_azure_service_request_error, map_azure_service_response_error,
    map_azure_value_type_error
)

class IAzureStorageAccessor(ABC):
    @abstractmethod
    async def get_if_container_exists_async(
        self, storage_account_connection_string: str, container_name: str
    ) -> bool:
        pass

    @abstractmethod
    async def create_container_async(
        self, storage_account_connection_string: str, container_name: str
    ) -> bool:
        pass

    @abstractmethod
    async def list_blobs_in_container_async(
        self, storage_account_connection_string: str, container_name: str, blob_name_filter: Optional[str] = None
    ) -> List[BlobProperties]:
        pass

    @abstractmethod
    async def get_if_blob_exists_async(
        self, storage_account_connection_string: str, container_name: str, blob_name: str
    ) -> bool:
        pass

    @abstractmethod
    async def delete_blob_if_exists_async(
        self, storage_account_connection_string: str, container_name: str, blob_name: str
    ) -> bool:
        pass

    @abstractmethod
    async def get_absolute_uri_of_blob_async(
        self, storage_account_connection_string: str, container_name: str, blob_name: str
    ) -> Optional[str]:
        pass

    @abstractmethod
    async def upload_string_async(
        self, storage_account_connection_string: str, container_name: str, blob_name: str, blob_contents: str, create_container_if_not_exist: bool 
    ) -> Any:
        pass

    @abstractmethod
    async def upload_bytes_async(
        self, storage_account_connection_string: str, container_name: str, blob_name: str, blob_contents: bytes, create_container_if_not_exist: bool
    ) -> Any:
        pass

    @abstractmethod
    async def download_async(
        self, storage_account_connection_string: str, container_name: str, blob_name: str
    ) -> bytes:
        pass

class AzureStorageAccessor(IAzureStorageAccessor):

    async def get_if_container_exists_async(self, storage_account_connection_string: str, container_name: str) -> bool:
        failure = "Unable to determine if container_name exists."
        try:
            async with BlobServiceClient.from_connection_string(storage_account_connection_string) as blob_service_client:
                container_client = blob_service_client.get_container_client(container_name)
                return await container_client.exists()
        except ClientAuthenticationError as ex:
            map_azure_client_authentication_error(ex, failure)
        except ServiceRequestError as ex:
            map_azure_service_request_error(ex, failure)
        except ServiceResponseError as ex:
            map_azure_service_response_error(ex, failure)
        except ResourceNotFoundError as ex:
            map_azure_resource_not_found_error(ex, failure)
        except ResourceExistsError as ex:
            map_azure_resource_exists_error(ex, failure)
        except HttpResponseError as ex:
            map_azure_http_response_error(ex, failure)
        except (ValueError, TypeError) as ex:
            map_azure_value_type_error(ex, failure)
        except Exception as ex:
            raise

    async def create_container_async(self, storage_account_connection_string: str, container_name: str) -> bool:
        failure = "Unable to create container."
        try:
            async with BlobServiceClient.from_connection_string(storage_account_connection_string) as blob_service_client:
                container_client = blob_service_client.get_container_client(container_name)
                await container_client.create_container()
                return True
        except ResourceExistsError:
            return True  # Already exists is not an error
        except ClientAuthenticationError as ex:
            map_azure_client_authentication_error(ex, failure)
        except (ServiceRequestError, ServiceResponseError) as ex:
            map_azure_service_request_error(ex, failure)
        except ResourceNotFoundError as ex:
            map_azure_resource_not_found_error(ex, failure)
        except HttpResponseError as ex:
            map_azure_http_response_error(ex, failure)
        except (ValueError, TypeError) as ex:
            map_azure_value_type_error(ex, failure)
        except Exception as ex:
            raise    

    async def list_blobs_in_container_async(
        self,
        storage_account_connection_string: str,
        container_name: str,
        blob_name_filter: Optional[str] = None
    ) -> List[BlobProperties]:
        failure = "Unable to list blobs."
        blobs: List[BlobProperties] = []
        try:
            async with BlobServiceClient.from_connection_string(storage_account_connection_string) as blob_service_client:
                container_client = blob_service_client.get_container_client(container_name)
                async for properties_of_blob in container_client.list_blobs():
                    if not blob_name_filter or blob_name_filter == "*" or blob_name_filter in properties_of_blob.name:
                        blobs.append(properties_of_blob)
            return blobs
        except ClientAuthenticationError as ex:
            map_azure_client_authentication_error(ex, failure)
        except ServiceRequestError as ex:
            map_azure_service_request_error(ex, failure)
        except ServiceResponseError as ex:
            map_azure_service_response_error(ex, failure)
        except ResourceNotFoundError as ex:
            map_azure_resource_not_found_error(ex, failure)
        except ResourceExistsError as ex:
            map_azure_resource_exists_error(ex, failure)
        except HttpResponseError as ex:
            map_azure_http_response_error(ex, failure)
        except (ValueError, TypeError) as ex:
            map_azure_value_type_error(ex, failure)
        except Exception as ex:
            raise

    async def get_if_blob_exists_async(
        self,
        storage_account_connection_string: str,
        container_name: str,
        blob_name: str
    ) -> bool:
        failure = "Unable to determine if blob exists."
        try:
            async with BlobServiceClient.from_connection_string(storage_account_connection_string) as blob_service_client:
                blob_client = blob_service_client.get_blob_client(container_name, blob_name)
                return await blob_client.exists()
        except ClientAuthenticationError as ex:
            map_azure_client_authentication_error(ex, failure)
        except ServiceRequestError as ex:
            map_azure_service_request_error(ex, failure)
        except ServiceResponseError as ex:
            map_azure_service_response_error(ex, failure)
        except ResourceNotFoundError as ex:
            map_azure_resource_not_found_error(ex, failure)
        except ResourceExistsError as ex:
            map_azure_resource_exists_error(ex, failure)
        except HttpResponseError as ex:
            map_azure_http_response_error(ex, failure)
        except (ValueError, TypeError) as ex:
            map_azure_value_type_error(ex, failure)
        except Exception as ex:
            raise    

    async def delete_blob_if_exists_async(
        self,
        storage_account_connection_string: str,
        container_name: str,
        blob_name: str
    ) -> bool:
        failure = "Unable to delete blob."
        try:
            async with BlobServiceClient.from_connection_string(storage_account_connection_string) as blob_service_client:
                blob_client = blob_service_client.get_blob_client(container_name, blob_name)
                if await blob_client.exists():
                    await blob_client.delete_blob(delete_snapshots="include")
                    return True
                else:
                    return False
        except ResourceNotFoundError:
            return False
        except ClientAuthenticationError as ex:
            map_azure_client_authentication_error(ex, failure)
        except ServiceRequestError as ex:
            map_azure_service_request_error(ex, failure)
        except ServiceResponseError as ex:
            map_azure_service_response_error(ex, failure)
        except ResourceExistsError as ex:
            map_azure_resource_exists_error(ex, failure)
        except HttpResponseError as ex:
            map_azure_http_response_error(ex, failure)
        except (ValueError, TypeError) as ex:
            map_azure_value_type_error(ex, failure)
        except Exception as ex:
            raise    

    async def get_absolute_uri_of_blob_async(
        self,
        storage_account_connection_string: str,
        container_name: str,
        blob_name: str
    ) -> Optional[str]:
        failure = "Unable to obtain uri of blob."
        try:
            async with BlobServiceClient.from_connection_string(storage_account_connection_string) as blob_service_client:
                blob_client = blob_service_client.get_blob_client(container_name, blob_name)
                if not await blob_client.exists():
                    return None
                return blob_client.url
        except ClientAuthenticationError as ex:
            map_azure_client_authentication_error(ex, failure)
        except ServiceRequestError as ex:
            map_azure_service_request_error(ex, failure)
        except ServiceResponseError as ex:
            map_azure_service_response_error(ex, failure)
        except ResourceNotFoundError as ex:
            map_azure_resource_not_found_error(ex, failure)
        except ResourceExistsError as ex:
            map_azure_resource_exists_error(ex, failure)
        except HttpResponseError as ex:
            map_azure_http_response_error(ex, failure)
        except (ValueError, TypeError) as ex:
            map_azure_value_type_error(ex, failure)
        except Exception as ex:
            raise    

    async def upload_string_async(
        self,
        storage_account_connection_string: str,
        container_name: str,
        blob_name: str,
        blob_contents: str,
        create_container_if_not_exist: bool,
    ) -> Optional[str]:
        failure = "Unable to upload."
        try:
            async with BlobServiceClient.from_connection_string(storage_account_connection_string) as blob_service_client:
                container_client = blob_service_client.get_container_client(container_name)
                if create_container_if_not_exist:
                    await container_client.create_container()
                blob_client = container_client.get_blob_client(blob_name)
                most_likely_mime_type_title = get_mime_type(get_extension_from_name(blob_name))
                await blob_client.upload_blob(
                    blob_contents,
                    overwrite=True,
                    content_settings=ContentSettings(content_type=most_likely_mime_type_title)
                )
                if not await blob_client.exists():
                    return None
                return blob_client.url
        except ClientAuthenticationError as ex:
            map_azure_client_authentication_error(ex, failure)
        except ServiceRequestError as ex:
            map_azure_service_request_error(ex, failure)
        except ServiceResponseError as ex:
            map_azure_service_response_error(ex, failure)
        except ResourceNotFoundError as ex:
            map_azure_resource_not_found_error(ex, failure)
        except ResourceExistsError as ex:
            map_azure_resource_exists_error(ex, failure)
        except HttpResponseError as ex:
            map_azure_http_response_error(ex, failure)
        except (ValueError, TypeError) as ex:
            map_azure_value_type_error(ex, failure)
        except Exception as ex:
            raise   
            
    async def upload_bytes_async(
        self,
        storage_account_connection_string: str,
        container_name: str,
        blob_name: str,
        blob_contents: bytes,
        create_container_if_not_exist: bool,
    ) -> Optional[str]:
        failure = "Unable to upload."
        try:
            async with BlobServiceClient.from_connection_string(storage_account_connection_string) as blob_service_client:
                container_client = blob_service_client.get_container_client(container_name)
                if create_container_if_not_exist:
                    await container_client.create_container()
                blob_client = container_client.get_blob_client(blob_name)
                most_likely_mime_type_title = get_mime_type(get_extension_from_name(blob_name))
                await blob_client.upload_blob(
                    blob_contents,
                    overwrite=True,
                    content_settings=ContentSettings(content_type=most_likely_mime_type_title)
                )
                if not await blob_client.exists():
                    return None
                return blob_client.url
        except ClientAuthenticationError as ex:
            map_azure_client_authentication_error(ex, failure)
        except ServiceRequestError as ex:
            map_azure_service_request_error(ex, failure)
        except ServiceResponseError as ex:
            map_azure_service_response_error(ex, failure)
        except ResourceNotFoundError as ex:
            map_azure_resource_not_found_error(ex, failure)
        except ResourceExistsError as ex:
            map_azure_resource_exists_error(ex, failure)
        except HttpResponseError as ex:
            map_azure_http_response_error(ex, failure)
        except (ValueError, TypeError) as ex:
            map_azure_value_type_error(ex, failure)
        except Exception as ex:
            raise    

    async def download_async(
        self,
        storage_account_connection_string: str,
        container_name: str,
        blob_name: str
    ) -> bytes:
        failure = "Resource not found or unavailable."
        try:
            async with BlobServiceClient.from_connection_string(storage_account_connection_string) as blob_service_client:
                blob_client = blob_service_client.get_blob_client(container_name, blob_name)
                downloader = await blob_client.download_blob()
                return await downloader.readall()
        except ClientAuthenticationError as ex:
            map_azure_client_authentication_error(ex, failure)
        except ServiceRequestError as ex:
            map_azure_service_request_error(ex, failure)
        except ServiceResponseError as ex:
            map_azure_service_response_error(ex, failure)
        except ResourceNotFoundError as ex:
            map_azure_resource_not_found_error(ex, failure)
        except ResourceExistsError as ex:
            map_azure_resource_exists_error(ex, failure)
        except HttpResponseError as ex:
            map_azure_http_response_error(ex, failure)
        except (ValueError, TypeError) as ex:
            map_azure_value_type_error(ex, failure)
        except Exception as ex:
            raise


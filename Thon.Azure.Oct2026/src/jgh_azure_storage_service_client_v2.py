import asyncio
from datetime import datetime
from typing import Awaitable, Callable, Dict, List, Optional, TypeVar

from jgh_azure_storage_accessor import AzureStorageAccessor
from jgh_exceptions import AlertMessageError, TimeoutError as AppTimeoutError
from jgh_internet_helpers import throw_if_no_internet_connection
from jgh_path_helpers import throw_if_any_parameter_is_invalid
from jgh_string import CallTimedOut, MethodFailed, make_wait_time_msg
from repository_of_connectionstrings import ConnectionStringRepository

T = TypeVar("T")


class AzureStorageServiceClient():
	"""
	Thin service layer over AzureStorageAccessor. Each public method validates its arguments, checks
	connectivity, resolves the connection string for the named storage account, and invokes the accessor
	under a timeout.

	Error contract:
	  - Invalid arguments, a missing connection string, or no internet raise AlertMessageError.
	  - A call exceeding the timeout raises the application's TimeoutError (jgh_exceptions).
	  - Everything else (AuthenticationError, NetworkError, NotFoundError, AlreadyExistsError,
		ValidationError, ...) is raised by the accessor already translated into the application's own
		exceptions and propagates here unchanged, with its details intact.
	"""

	def __init__(self, timeout_seconds: float = 30):
		self.__accessor = AzureStorageAccessor()
		self.__timeout_seconds = timeout_seconds

	async def get_if_service_is_answering_async(self) -> bool:
		"""Not applicable for this client, which uses no external service. Always returns True."""
		return True

	async def get_service_endpoints_info_async(self) -> List[str]:
		"""Not applicable for this client, which uses no external service. Always returns an empty list."""
		return []

	async def get_if_container_exists_async(self, storage_account_name: str, container_name: str) -> bool:
		return await self.__call_accessor(
			storage_account_name, container_name, None,
			lambda connection_string: self.__accessor.get_if_container_exists_async(
				connection_string, container_name
			),
		)

	async def get_particulars_of_blobs_in_container_async(
		self,
		storage_account_name: str,
		container_name: str,
		required_substring: str,
	) -> Dict[str, int]:
		"""Returns a dict of blob name to size in bytes for blobs whose name contains required_substring."""
		list_of_blob_properties = await self.__call_accessor(
			storage_account_name, container_name, None,
			lambda connection_string: self.__accessor.list_blobs_in_container_async(
				connection_string, container_name, required_substring
			),
		)
		return {blob.name: blob.size for blob in list_of_blob_properties}

	async def get_if_blob_exists_async(self, storage_account_name: str, container_name: str, blob_name: str) -> bool:
		return await self.__call_accessor(
			storage_account_name, container_name, blob_name,
			lambda connection_string: self.__accessor.get_if_blob_exists_async(
				connection_string, container_name, blob_name
			),
		)

	async def get_absolute_uri_of_blob_async(
		self, storage_account_name: str, container_name: str, blob_name: str
	) -> Optional[str]:
		"""Returns the blob's absolute uri, or None if the blob does not exist."""
		return await self.__call_accessor(
			storage_account_name, container_name, blob_name,
			lambda connection_string: self.__accessor.get_absolute_uri_of_blob_async(
				connection_string, container_name, blob_name
			),
		)

	async def delete_block_blob_if_exists_async(
		self, storage_account_name: str, container_name: str, blob_name: str
	) -> bool:
		"""Returns True if the blob existed and was deleted, False if it did not exist."""
		return await self.__call_accessor(
			storage_account_name, container_name, blob_name,
			lambda connection_string: self.__accessor.delete_blob_if_exists_async(
				connection_string, container_name, blob_name
			),
		)

	async def upload_bytes_to_block_blob_async(
		self,
		storage_account_name: str,
		container_name: str,
		blob_name: str,
		bytes_to_upload: bytes,
		create_container_if_not_exist: bool,
	) -> str:
		"""Uploads (overwriting) and returns the url of the blob."""
		if not bytes_to_upload:
			raise AlertMessageError("Error: bytes_to_upload must be non-empty bytes or bytearray.")
		return await self.__call_accessor(
			storage_account_name, container_name, blob_name,
			lambda connection_string: self.__accessor.upload_bytes_async(
				connection_string, container_name, blob_name, bytes_to_upload, create_container_if_not_exist
			),
		)

	async def upload_string_to_block_blob_async(
		self,
		storage_account_name: str,
		container_name: str,
		blob_name: str,
		string_to_upload: str,
		create_container_if_not_exist: bool,
	) -> str:
		"""Uploads (overwriting) and returns the url of the blob."""
		if not string_to_upload:
			raise AlertMessageError("Error: string_to_upload must be a non-empty string.")
		return await self.__call_accessor(
			storage_account_name, container_name, blob_name,
			lambda connection_string: self.__accessor.upload_string_async(
				connection_string, container_name, blob_name, string_to_upload, create_container_if_not_exist
			),
		)

	async def download_block_blob_as_bytes_async(
		self,
		storage_account_name: str,
		container_name: str,
		blob_name: str
	) -> bytes:
		return await self.__call_accessor(
			storage_account_name, container_name, blob_name,
			lambda connection_string: self.__accessor.download_async(
				connection_string, container_name, blob_name
			),
		)

	async def __call_accessor(
		self,
		storage_account_name: str,
		container_name: str,
		blob_name: Optional[str],
		accessor_call: Callable[[str], Awaitable[T]],
	) -> T:
		"""
		Shared pipeline for every public method: validate, check connectivity, resolve the connection
		string, then await the accessor call under the timeout. blob_name is validated only if provided.
		"""
		start = datetime.now()
		throw_if_any_parameter_is_invalid(storage_account_name, container_name, blob_name)
		# The connectivity check does blocking socket I/O, so keep it off the event loop.
		await asyncio.to_thread(throw_if_no_internet_connection)
		connection_string = ConnectionStringRepository.get_azure_storage_account_connection_string(storage_account_name)
		try:
			return await asyncio.wait_for(accessor_call(connection_string), timeout=self.__timeout_seconds)
		except asyncio.TimeoutError as ex:
			raise AppTimeoutError(
				message=f"{MethodFailed} {CallTimedOut} {make_wait_time_msg(start)}",
				timeout_seconds=self.__timeout_seconds,
				inner_exception=ex,
			) from ex

import asyncio
from datetime import datetime
from typing import Awaitable, Callable, Dict, List, Optional, TypeVar

from jgh_azure_storage_accessor import AzureStorageAccessor
from jgh_exceptions import AlertMessageError, AppTimeoutError, NetworkError
from jgh_internet_helpers import warn_if_internet_not_connected
from jgh_path_helpers import throw_if_any_parameter_is_invalid
from jgh_string import CallTimedOut, MethodFailed, make_wait_time_msg
from repository_of_connectionstrings import ConnectionStringRepository

T = TypeVar("T")


class AzureStorageServiceClient():
	"""
	Thin service layer over AzureStorageAccessor. Each public method validates its arguments, resolves the
	connection string for the named storage account, and invokes the accessor under a timeout.

	Error contract (applies to every method that calls the accessor):
	  - AlertMessageError is raised for invalid arguments, for a storage account whose connection string
		cannot be found, and when a call times out or fails with a NetworkError while the machine is offline
		("no internet connection"). Validation happens before any network call, so AppValidationError is seen 
		only for a wrongly typed upload argument, because arguments are otherwise validated first.
	  - AppTimeoutError is raised if the call exceeds timeout_seconds and the machine is online. The timeout
		covers the whole operation, including every page of a listing and the full transfer of an upload or
		download. Cancelling on timeout means the outcome of an upload or delete is then unknown.
	  - Valid credentials without permission for the operation arrive as NetworkError with 
		http_status 403, not AuthenticationError. See AzureStorageAccessor.
	  - Everything else raised by the accessor (AuthenticationError, NetworkError, NotFoundError,
		AlreadyExistsError, AppValidationError, AppErrorBase) propagates unchanged, with its details intact.
		See the accessor's docstrings for exactly when each is raised.

	Argument rules (stricter than Azure's own):
	  - storage_account_name: 3 to 24 lowercase letters or digits.
	  - container_name: valid per Azure container naming rules.
	  - blob_name: 1 to 1024 characters, must have a file extension, and must not contain \\ ? # or %.
		Spaces are allowed. A blob that already exists in Azure under a name breaking these rules cannot be
		addressed (read, checked or deleted) through this client.
	"""

	def __init__(self, timeout_seconds: float = 30):
		self.__storage_gateway = AzureStorageAccessor()
		self.__timeout_seconds = timeout_seconds

	async def get_if_service_is_answering_async(self) -> bool:
		"""Not applicable for this client, which uses no external service. Always returns True."""
		return True

	async def get_service_endpoints_info_async(self) -> List[str]:
		"""Not applicable for this client, which uses no external service. Always returns an empty list."""
		return []

	async def get_if_container_exists_async(self, storage_account_name: str, container_name: str) -> bool:
		"""
		Returns True if the container exists, False if it does not. A missing container is a normal answer, not an
		error, so NotFoundError is never raised.

		Raises AlertMessageError if storage_account_name or container_name is invalid, if no connection string
		is found for the account, or if the call fails with a NetworkError or times out while the machine is
		offline. AppTimeoutError is raised if the call times out while online. Failures reported by the accessor,
		such as AuthenticationError or NetworkError, propagate unchanged.
		"""
		return await self.__execute_storage_operation_async(
			storage_account_name, container_name, None,
			lambda connection_string: self.__storage_gateway.get_if_container_exists_async(
				connection_string, container_name
			),
		)

	async def get_particulars_of_blobs_in_container_async(
		self,
		storage_account_name: str,
		container_name: str,
		name_starts_with: Optional[str] = None,
		name_contains: Optional[str] = None,
	) -> Dict[str, int]:
		"""
		Returns a dict of blob name to size in bytes for the blobs in the container, in lexicographic order of
		blob name. The dict is empty if no blob matches the filters, which is a normal answer, not an error.

		Filters (both are case-sensitive, and when both are given a blob must satisfy both):

		name_starts_with  -- SERVER-SIDE filter. Only blobs whose full name, including any virtual folder path,
							 starts with this literal prefix are transferred from Azure. Prefer it whenever the
							 leading part of the name is known (e.g. "2026/10/"), because it is far cheaper on
							 large containers. None, "" and "*" all mean "no prefix filter". "*" is not a
							 wildcard and not a literal asterisk.

		name_contains     -- CLIENT-SIDE filter. Azure cannot search for a substring, so every blob that survives
							 name_starts_with is fetched and then tested. Combine it with name_starts_with to
							 reduce the number of blobs fetched. None, "" and "*" all mean "no substring filter".
							 Any other value is a literal substring matched anywhere in the full blob name.

		Calling with no filters lists the whole container, which can be slow and memory-hungry for a large one,
		and must complete within the client's timeout.

		Raises AlertMessageError if storage_account_name or container_name is invalid, if no connection string
		is found for the account, or if the call fails with a NetworkError or times out while the machine is
		offline. AppTimeoutError is raised if the call times out while online. Failures reported by the accessor,
		such as NotFoundError (the container does not exist), AuthenticationError or NetworkError, propagate
		unchanged.
		"""
		list_of_blob_properties = await self.__execute_storage_operation_async(
			storage_account_name, container_name, None,
			lambda connection_string: self.__storage_gateway.list_blobs_in_container_async(
				connection_string,
				container_name,
				name_starts_with=name_starts_with,
				name_contains=name_contains,
			),
		)
		return {blob.name: blob.size for blob in list_of_blob_properties}

	async def get_if_blob_exists_async(self, storage_account_name: str, container_name: str, blob_name: str) -> bool:
		"""
		Returns True if the blob exists, False if it does not. A missing blob is a normal answer, not an error.
		False is also returned if the container itself does not exist, because Azure reports both as "not found".
		NotFoundError is therefore never raised.

		Raises AlertMessageError if storage_account_name, container_name or blob_name is invalid (blob_name must
		have a file extension and must not contain \\ ? # or %), if no connection string is found for the account,
		or if the call fails with a NetworkError or times out while the machine is offline. AppTimeoutError is
		raised if the call times out while online. Failures reported by the accessor, such as AuthenticationError
		or NetworkError, propagate unchanged.
		"""
		return await self.__execute_storage_operation_async(
			storage_account_name, container_name, blob_name,
			lambda connection_string: self.__storage_gateway.get_if_blob_exists_async(
				connection_string, container_name, blob_name
			),
		)

	async def get_absolute_uri_of_blob_async(
		self, storage_account_name: str, container_name: str, blob_name: str
	) -> Optional[str]:
		"""
		Returns the blob's absolute URL, or None if the blob does not exist. None is also returned if the
		container itself does not exist, because Azure reports both as "not found". A missing blob is a normal
		answer, not an error, so NotFoundError is never raised. The URL means "the blob existed a moment ago",
		not a guarantee that it still exists.

		The URL is percent-encoded, so a blob named "my file.txt" is returned as ".../my%20file.txt". This is the
		valid form and can be used directly in an HTTP request. Do not pass it back in as a blob_name (this
		client rejects any name containing %). Use urllib.parse.unquote only for display.

		The URL carries no credentials if the connection string uses an account key, so the caller can open it
		only if the blob is publicly readable. If the connection string uses a SAS token, the token is appended
		to the URL as a query string. The URL is then a live credential and must not be logged, displayed or
		shared more widely than the token's permissions and expiry justify.

		Raises AlertMessageError if storage_account_name, container_name or blob_name is invalid (blob_name must
		have a file extension and must not contain \\ ? # or %), if no connection string is found for the account,
		or if the call fails with a NetworkError or times out while the machine is offline. AppTimeoutError is
		raised if the call times out while online. Failures reported by the accessor, such as AuthenticationError
		or NetworkError, propagate unchanged.
		"""
		return await self.__execute_storage_operation_async(
			storage_account_name, container_name, blob_name,
			lambda connection_string: self.__storage_gateway.get_absolute_uri_of_blob_async(
				connection_string, container_name, blob_name
			),
		)

	async def delete_block_blob_if_exists_async(
		self, storage_account_name: str, container_name: str, blob_name: str
	) -> bool:
		"""
		Returns True if the blob (and its snapshots) was deleted, False if it did not exist. A missing blob is a
		normal outcome, so this method is idempotent. False is also returned if the container itself does not
		exist, because Azure reports both as "not found", so the caller cannot distinguish the two cases.
		NotFoundError is therefore never raised.

		Raises AlertMessageError if storage_account_name, container_name or blob_name is invalid (blob_name must
		have a file extension and must not contain \\ ? # or %), if no connection string is found for the account,
		or if the call fails with a NetworkError or times out while the machine is offline. AppTimeoutError is
		raised if the call times out while online. Failures reported by the accessor propagate unchanged:
		AuthenticationError if the credentials themselves are rejected, and NetworkError if the service is
		unreachable or returns an unexpected HTTP error. Note that valid credentials without permission to
		delete (for example a SAS token lacking the delete permission) are reported as NetworkError with
		http_status 403, not AuthenticationError.

		If the call times out, whether the blob was deleted is unknown. Deletion is idempotent, so the caller
		can safely retry.
		"""
		return await self.__execute_storage_operation_async(
			storage_account_name, container_name, blob_name,
			lambda connection_string: self.__storage_gateway.delete_blob_if_exists_async(
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
		return await self.__execute_storage_operation_async(
			storage_account_name, container_name, blob_name,
			lambda connection_string: self.__storage_gateway.upload_bytes_async(
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
		"""
		Uploads the string, UTF-8 encoded, as a block blob and returns the blob's absolute URL. Overwrites an
		existing blob with the same name without warning, so AlreadyExistsError is never raised for the blob.
		The content type is inferred from the blob name's extension. If create_container_if_not_exist is True,
		a missing container is created first, and a container that already exists is not an error.

		The returned URL is percent-encoded, so a blob named "my file.txt" is returned as ".../my%20file.txt".
		This is the valid form for an HTTP request. Do not pass it back in as a blob_name (this client rejects
		any name containing %). It carries no credentials with an account-key connection string, but includes
		the SAS token as a query string if the connection string uses one, in which case treat the URL as a
		secret.

		Raises AlertMessageError if string_to_upload is empty (this client refuses to upload zero-length blobs,
		although the accessor itself allows them), if storage_account_name, container_name or blob_name is
		invalid (blob_name must have a file extension and must not contain \\ ? # or %), if no connection string
		is found for the account, or if the call fails with a NetworkError or times out while the machine is
		offline. AppTimeoutError is raised if the call times out while online. Failures reported by the accessor
		propagate unchanged: AppValidationError if string_to_upload is not a str; NotFoundError if the container
		does not exist and create_container_if_not_exist is False; AuthenticationError if the credentials
		themselves are rejected; AlreadyExistsError only if the container must be created but a conflicting
		operation blocks it, such as the container still being deleted, in which case the caller should wait
		and retry; and NetworkError if the service is unreachable or returns an unexpected HTTP error. Valid
		credentials without permission to write (for example a SAS token lacking the write or create
		permission) are reported as NetworkError with http_status 403, not AuthenticationError.

		The timeout covers the whole transfer, so a large upload on a slow link can exceed the default 30
		seconds. If the call times out or fails, the caller should not assume the blob was left unchanged.
		Uploading is idempotent, so the caller can safely retry.
		"""




		if not string_to_upload:
			raise AlertMessageError("Error: string_to_upload must be a non-empty string.")
		return await self.__execute_storage_operation_async(
			storage_account_name, container_name, blob_name,
			lambda connection_string: self.__storage_gateway.upload_string_async(
				connection_string, container_name, blob_name, string_to_upload, create_container_if_not_exist
			),
		)

	async def download_block_blob_as_bytes_async(
		self,
		storage_account_name: str,
		container_name: str,
		blob_name: str
	) -> bytes:
		"""
		Returns the blob's full contents as bytes, read entirely into memory. This is unsuitable for very large
		blobs. An empty blob returns b"". Unlike get_if_blob_exists_async, a missing blob is an error, not a
		normal answer.

		Raises AlertMessageError if storage_account_name, container_name or blob_name is invalid (blob_name must
		have a file extension and must not contain \\ ? # or %), if no connection string is found for the account,
		or if the call fails with a NetworkError or times out while the machine is offline. AppTimeoutError is
		raised if the call times out while online. Failures reported by the accessor propagate unchanged:
		NotFoundError if the blob does not exist, or if the container does not exist, because Azure reports both
		as "not found" and the caller cannot distinguish them; AuthenticationError if the credentials themselves
		are rejected; and NetworkError if the service is unreachable or returns an unexpected HTTP error. Valid
		credentials without permission to read (for example a SAS token lacking the read permission) are
		reported as NetworkError with http_status 403, not AuthenticationError.

		The timeout covers the whole transfer, so a large blob on a slow link can exceed the default 30 seconds.
		A failure part-way through the transfer is raised, never returned as truncated data. Downloading is
		read-only, so the caller can safely retry.
		"""
		return await self.__execute_storage_operation_async(
			storage_account_name, container_name, blob_name,
			lambda connection_string: self.__storage_gateway.download_async(
				connection_string, container_name, blob_name
			),
		)

	async def __execute_storage_operation_async(
		self,
		storage_account_name: str,
		container_name: str,
		blob_name: Optional[str],
		storage_operation: Callable[[str], Awaitable[T]],
	) -> T:
		"""
		Shared pipeline for every public method: validate, resolve the connection string, then await the
		accessor call under the timeout. blob_name is validated only if provided. Connectivity is not checked
		up front; it is diagnosed only after a timeout or NetworkError, to report an offline machine accurately.
		"""
		start = datetime.now()
		throw_if_any_parameter_is_invalid(storage_account_name, container_name, blob_name)
		connection_string = ConnectionStringRepository.get_azure_storage_account_connection_string(storage_account_name)
		try:
			return await asyncio.wait_for(storage_operation(connection_string), timeout=self.__timeout_seconds)
		except asyncio.TimeoutError as ex:
			await self.__throw_if_offline_async(ex)
			raise AppTimeoutError(
				message=f"{MethodFailed} {CallTimedOut} {make_wait_time_msg(start)}",
				timeout_seconds=self.__timeout_seconds,
				inner_exception=ex,
			) from ex
		except NetworkError as ex:
			await self.__throw_if_offline_async(ex)
			raise

	@staticmethod
	async def __throw_if_offline_async(cause: Exception) -> None:
		# The check does blocking socket I/O, so keep it off the event loop.
		warning = await asyncio.to_thread(warn_if_internet_not_connected)
		if warning:
			raise AlertMessageError(warning) from cause

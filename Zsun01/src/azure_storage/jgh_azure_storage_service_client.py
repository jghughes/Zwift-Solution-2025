from jgh_exceptions import AppErrorBase, NetworkError, AuthenticationError, TimeoutError, ValidationError, SystemError, AlertMessageError, NotFoundError, AlreadyExistsError

from jgh_internet_helpers import throw_if_no_internet_connection
from jgh_path_helpers import throw_if_any_parameter_is_invalid

import abc
import asyncio
from collections import defaultdict
from datetime import datetime
from typing import Dict, List

from jgh_azure_storage_accessor import AzureStorageAccessor
from repository_of_connectionstrings import ConnectionStringRepository
from jgh_string import CallTimedOut, MethodFailed, make_wait_time_msg



class IServiceClientBase(abc.ABC):
    @abc.abstractmethod
    async def get_if_service_is_answering_async(self) -> bool:
        """
        Returns True or raises JghCommunicationFailureException if unable to connect to service.
        :return: bool
        :raises JghCommunicationFailureException: for communication failures.
        """
        pass

    @abc.abstractmethod
    async def get_service_endpoints_info_async(self) -> List[str]:
        """
        Returns a list of service endpoint info strings.
        :return: List[str]
        """
        pass

class IAzureStorageServiceClient(IServiceClientBase, abc.ABC):
    @abc.abstractmethod
    async def get_if_container_exists_async(self, storage_account_name: str, container_name: str) -> bool:
        """
        Returns True if the container_name exists, otherwise False.
        """
        pass

    @abc.abstractmethod
    async def get_particulars_of_blobs_in_container_async(
        self,
        storage_account_name: str,
        container_name: str,
        required_substring: str,
    ) -> Dict[str, int]:
        """
        Returns a list of blob_name names or descriptions in the specified container_name.
        """
        pass

    @abc.abstractmethod
    async def get_if_blob_exists_async(self, storage_account_name: str, container_name: str, blob_name: str) -> bool:
        """
        Returns True if the blob_name exists, otherwise False.
        """
        pass

    @abc.abstractmethod
    async def get_absolute_uri_of_blob_async(self, storage_account_name: str, container_name: str, blob_name: str) -> str|None:
        """
        Returns the absolute URI of the specified blob_name.
        """
        pass

    @abc.abstractmethod
    async def delete_block_blob_if_exists_async(self, storage_account_name: str, container_name: str, blob_name: str) -> bool:
        """
        Deletes the specified block blob_name if it exists. Returns True if deleted, otherwise False.
        """
        pass

    @abc.abstractmethod
    async def upload_bytes_to_block_blob_async(
        self,
        storage_account_name: str,
        container_name: str,
        blob_name: str,
        bytes_to_upload: bytes,
        create_container_if_not_exist: bool,
    ) -> str|None:
        """
        Uploads bytes to the specified block blob_name. Returns True if successful.
        """
        pass

    @abc.abstractmethod
    async def upload_string_to_block_blob_async(
        self,
        storage_account_name: str,
        container_name: str,
        blob_name: str,
        string_to_upload: str,
        create_container_if_not_exist: bool,
    ) -> str|None:
        """
        Uploads a string to the specified block blob_name. Returns True if successful.
        """
        pass

    @abc.abstractmethod
    async def download_block_blob_as_bytes_async(self, storage_account_name: str, container_name: str, blob_name: str) -> bytes:
        """
        Downloads the specified block blob_name as bytes.
        """
        pass

class AzureStorageServiceClient(IAzureStorageServiceClient):
    __Locus2 = "AzureStorageServiceClient"
    __Locus3 = "jgh_azure_storage_service_client"
    __timeout_seconds = 30  # Set your desired timeout here

    def __init__(self):
        self.__accessor = AzureStorageAccessor()

    async def get_if_service_is_answering_async(self) -> bool:
        """
        Not applicable for this client. It does not use an external service.
        Returns True to indicate the client is operational.
        """
        return True;

    async def get_service_endpoints_info_async(self) -> List[str]:
        """ Not applicable for this client. It does not use an external service.
        Returns True to indicate the client is operational.Returns an empty list.
        """
        return []

    async def get_if_container_exists_async(self, storage_account_name: str, container_name: str) -> bool:
        failure = MethodFailed
        start = datetime.now()
        try:
            throw_if_any_parameter_is_invalid(storage_account_name,container_name)
            throw_if_no_internet_connection()
            account_connection_string = ConnectionStringRepository.get_azure_storage_account_connection_string(storage_account_name)
            answer = await asyncio.wait_for(
                self.__accessor.get_if_container_exists_async(account_connection_string, container_name),
                timeout=self.__timeout_seconds
            )
            return answer
        except asyncio.CancelledError:
            raise
        except asyncio.TimeoutError as ex:
            msg = f"{failure} {CallTimedOut} {make_wait_time_msg(start)}"
            raise TimeoutError(message=msg, inner_exception=ex) from ex
        except AlertMessageError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AlertMessageError(message=msg) from ex
        except AuthenticationError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AuthenticationError(message=msg, inner_exception=ex) from ex
        except NetworkError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise NetworkError(message=msg, inner_exception=ex) from ex
        except NotFoundError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise NotFoundError(message=msg, inner_exception=ex) from ex
        except AlreadyExistsError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AlreadyExistsError(message=msg, inner_exception=ex) from ex
        except ValidationError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise ValidationError(message=msg, inner_exception=ex) from ex
        except SystemError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise SystemError(message=msg, inner_exception=ex) from ex
        except AppErrorBase as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AppErrorBase(message=msg) from ex

    async def get_particulars_of_blobs_in_container_async(
        self,
        storage_account_name: str,
        container_name: str,
        required_substring: str,
    ) -> Dict[str, int]:
        failure = MethodFailed
        start = datetime.now()
        try:
            throw_if_any_parameter_is_invalid(storage_account_name,container_name)
            throw_if_no_internet_connection()
            account_connection_string = ConnectionStringRepository.get_azure_storage_account_connection_string(storage_account_name)
            list_of_blob_properties = await asyncio.wait_for(
                self.__accessor.list_blobs_in_container_async(
                    account_connection_string,
                    container_name,
                    required_substring
                ),
                timeout=self.__timeout_seconds
            )
            dict_of_particulars = defaultdict(int, {blob.name: blob.size for blob in list_of_blob_properties})
            return dict_of_particulars
        except asyncio.CancelledError:
            raise
        except asyncio.TimeoutError as ex:
            msg = f"{failure} {CallTimedOut} {make_wait_time_msg(start)}"
            raise TimeoutError(message=msg, inner_exception=ex) from ex
        except AlertMessageError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AlertMessageError(message=msg) from ex
        except AuthenticationError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AuthenticationError(message=msg, inner_exception=ex) from ex
        except NetworkError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise NetworkError(message=msg, inner_exception=ex) from ex
        except NotFoundError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise NotFoundError(message=msg, inner_exception=ex) from ex
        except AlreadyExistsError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AlreadyExistsError(message=msg, inner_exception=ex) from ex
        except ValidationError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise ValidationError(message=msg, inner_exception=ex) from ex
        except SystemError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise SystemError(message=msg, inner_exception=ex) from ex
        except AppErrorBase as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AppErrorBase(message=msg) from ex

    async def get_if_blob_exists_async(self, storage_account_name: str, container_name: str, blob_name: str) -> bool:
        failure = MethodFailed
        start = datetime.now()
        try:
            throw_if_any_parameter_is_invalid(storage_account_name,container_name, blob_name)
            throw_if_no_internet_connection()
            account_connection_string = ConnectionStringRepository.get_azure_storage_account_connection_string(storage_account_name)
            answer = await asyncio.wait_for(
                self.__accessor.get_if_blob_exists_async(
                    account_connection_string,
                    container_name,
                    blob_name
                ),
                timeout=self.__timeout_seconds
            )
            return answer
        except asyncio.CancelledError:
            raise
        except asyncio.TimeoutError as ex:
            msg = f"{failure} {CallTimedOut} {make_wait_time_msg(start)}"
            raise TimeoutError(message=msg, inner_exception=ex) from ex
        except AlertMessageError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AlertMessageError(message=msg) from ex
        except AuthenticationError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AuthenticationError(message=msg, inner_exception=ex) from ex
        except NetworkError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise NetworkError(message=msg, inner_exception=ex) from ex
        except NotFoundError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise NotFoundError(message=msg, inner_exception=ex) from ex
        except AlreadyExistsError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AlreadyExistsError(message=msg, inner_exception=ex) from ex
        except ValidationError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise ValidationError(message=msg, inner_exception=ex) from ex
        except SystemError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise SystemError(message=msg, inner_exception=ex) from ex
        except AppErrorBase as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AppErrorBase(message=msg) from ex

    async def get_absolute_uri_of_blob_async(self, storage_account_name: str, container_name: str, blob_name: str) -> str | None:
        failure = MethodFailed
        start = datetime.now()
        try:
            throw_if_any_parameter_is_invalid(storage_account_name,container_name, blob_name)
            throw_if_no_internet_connection()
            account_connection_string = ConnectionStringRepository.get_azure_storage_account_connection_string(storage_account_name)
            answer = await asyncio.wait_for(
                self.__accessor.get_absolute_uri_of_blob_async(
                    account_connection_string,
                    container_name,
                    blob_name
                ),
                timeout=self.__timeout_seconds
            )
            return answer
        except asyncio.CancelledError:
            raise
        except asyncio.TimeoutError as ex:
            msg = f"{failure} {CallTimedOut} {make_wait_time_msg(start)}"
            raise TimeoutError(message=msg, inner_exception=ex) from ex
        except AlertMessageError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AlertMessageError(message=msg) from ex
        except AuthenticationError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AuthenticationError(message=msg, inner_exception=ex) from ex
        except NetworkError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise NetworkError(message=msg, inner_exception=ex) from ex
        except NotFoundError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise NotFoundError(message=msg, inner_exception=ex) from ex
        except AlreadyExistsError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AlreadyExistsError(message=msg, inner_exception=ex) from ex
        except ValidationError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise ValidationError(message=msg, inner_exception=ex) from ex
        except SystemError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise SystemError(message=msg, inner_exception=ex) from ex
        except AppErrorBase as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AppErrorBase(message=msg) from ex
    async def delete_block_blob_if_exists_async(self, storage_account_name: str, container_name: str, blob_name: str) -> bool:
        failure = MethodFailed
        start = datetime.now()
        try:
            throw_if_any_parameter_is_invalid(storage_account_name,container_name)
            throw_if_no_internet_connection()
            account_connection_string = ConnectionStringRepository.get_azure_storage_account_connection_string(storage_account_name)
            answer = await asyncio.wait_for(
                self.__accessor.delete_blob_if_exists_async(
                    account_connection_string,
                    container_name,
                    blob_name
                ),
                timeout=self.__timeout_seconds
            )
            return answer
        except asyncio.CancelledError:
            raise
        except asyncio.TimeoutError as ex:
            msg = f"{failure} {CallTimedOut} {make_wait_time_msg(start)}"
            raise TimeoutError(message=msg, inner_exception=ex) from ex
        except AlertMessageError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AlertMessageError(message=msg) from ex
        except AuthenticationError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AuthenticationError(message=msg, inner_exception=ex) from ex
        except NetworkError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise NetworkError(message=msg, inner_exception=ex) from ex
        except NotFoundError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise NotFoundError(message=msg, inner_exception=ex) from ex
        except AlreadyExistsError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AlreadyExistsError(message=msg, inner_exception=ex) from ex
        except ValidationError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise ValidationError(message=msg, inner_exception=ex) from ex
        except SystemError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise SystemError(message=msg, inner_exception=ex) from ex
        except AppErrorBase as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AppErrorBase(message=msg) from ex

    async def upload_bytes_to_block_blob_async(
        self,
        storage_account_name: str,
        container_name: str,
        blob_name: str,
        bytes_to_upload: bytes,
        create_container_if_not_exist: bool,
    ) -> str | None:
        failure = MethodFailed
        start = datetime.now()
        try:
            throw_if_any_parameter_is_invalid(storage_account_name,container_name)
            throw_if_no_internet_connection()
            if not bytes_to_upload:
                raise AlertMessageError("Error: bytes_to_upload must be non-empty bytes or bytearray.")
            account_connection_string = ConnectionStringRepository.get_azure_storage_account_connection_string(storage_account_name)
            answer = await asyncio.wait_for(
                self.__accessor.upload_bytes_async(
                    account_connection_string,
                    container_name,
                    blob_name,
                    bytes_to_upload,
                    create_container_if_not_exist
                ),
                timeout=self.__timeout_seconds
            )
            return answer
        except asyncio.CancelledError:
            raise
        except asyncio.TimeoutError as ex:
            msg = f"{failure} {CallTimedOut} {make_wait_time_msg(start)}"
            raise TimeoutError(message=msg, inner_exception=ex) from ex
        except AlertMessageError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AlertMessageError(message=msg) from ex
        except AuthenticationError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AuthenticationError(message=msg, inner_exception=ex) from ex
        except NetworkError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise NetworkError(message=msg, inner_exception=ex) from ex
        except NotFoundError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise NotFoundError(message=msg, inner_exception=ex) from ex
        except AlreadyExistsError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AlreadyExistsError(message=msg, inner_exception=ex) from ex
        except ValidationError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise ValidationError(message=msg, inner_exception=ex) from ex
        except SystemError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise SystemError(message=msg, inner_exception=ex) from ex
        except AppErrorBase as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AppErrorBase(message=msg) from ex
    async def upload_string_to_block_blob_async(
        self,
        storage_account_name: str,
        container_name: str,
        blob_name: str,
        string_to_upload: str,
        create_container_if_not_exist: bool,
    ) -> str | None:
        failure = MethodFailed
        start = datetime.now()
        try:
            throw_if_any_parameter_is_invalid(storage_account_name,container_name, blob_name)
            throw_if_no_internet_connection()
            if not string_to_upload:
                raise AlertMessageError("Error: string_to_upload must be a non-empty string.")
            account_connection_string = ConnectionStringRepository.get_azure_storage_account_connection_string(storage_account_name)
            answer = await asyncio.wait_for(
                self.__accessor.upload_string_async(
                    account_connection_string,
                    container_name,
                    blob_name,
                    string_to_upload,
                    create_container_if_not_exist
                ),
                timeout=self.__timeout_seconds
            )
            return answer
        except asyncio.CancelledError:
            raise
        except asyncio.TimeoutError as ex:
            msg = f"{failure} {CallTimedOut} {make_wait_time_msg(start)}"
            raise TimeoutError(message=msg, inner_exception=ex) from ex
        except AlertMessageError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AlertMessageError(message=msg) from ex
        except AuthenticationError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AuthenticationError(message=msg, inner_exception=ex) from ex
        except NetworkError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise NetworkError(message=msg, inner_exception=ex) from ex
        except NotFoundError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise NotFoundError(message=msg, inner_exception=ex) from ex
        except AlreadyExistsError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AlreadyExistsError(message=msg, inner_exception=ex) from ex
        except ValidationError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise ValidationError(message=msg, inner_exception=ex) from ex
        except SystemError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise SystemError(message=msg, inner_exception=ex) from ex
        except AppErrorBase as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AppErrorBase(message=msg) from ex
    async def download_block_blob_as_bytes_async(
        self,
        storage_account_name: str,
        container_name: str,
        blob_name: str
    ) -> bytes:
        failure = MethodFailed
        start = datetime.now()
        try:
            throw_if_any_parameter_is_invalid(storage_account_name,container_name, blob_name)
            throw_if_no_internet_connection()
            account_connection_string = ConnectionStringRepository.get_azure_storage_account_connection_string(storage_account_name)
            answer = await asyncio.wait_for(
                self.__accessor.download_async(account_connection_string, container_name, blob_name),
                timeout=self.__timeout_seconds
            )
            return answer
        except asyncio.CancelledError:
            raise
        except asyncio.TimeoutError as ex:
            msg = f"{failure} {CallTimedOut} {make_wait_time_msg(start)}"
            raise TimeoutError(message=msg, inner_exception=ex) from ex
        except AlertMessageError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AlertMessageError(message=msg) from ex
        except AuthenticationError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AuthenticationError(message=msg, inner_exception=ex) from ex
        except NetworkError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise NetworkError(message=msg, inner_exception=ex) from ex
        except NotFoundError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise NotFoundError(message=msg, inner_exception=ex) from ex
        except AlreadyExistsError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AlreadyExistsError(message=msg, inner_exception=ex) from ex
        except ValidationError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise ValidationError(message=msg, inner_exception=ex) from ex
        except SystemError as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise SystemError(message=msg, inner_exception=ex) from ex
        except AppErrorBase as ex:
            msg = f"{failure} {str(ex)} {make_wait_time_msg(start)}"
            raise AppErrorBase(message=msg) from ex
        # --- Tests ---

        # testing


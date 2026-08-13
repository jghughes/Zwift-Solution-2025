import asyncio
from typing import List
from jgh_azure_storage_accessor import AzureStorageAccessor
from repository_of_connectionstrings import ConnectionStringRepository

import time
import logging
from jgh_exceptions import AlertMessageError
from jgh_logging import setup_json_logging, log_event
from storage_config import DIRPATH_LOGGING


# Tests
async def test00():
        await test01()
        await test02()
        await test03()
        await test04()
        await test05()
        await test06()
        await test07()
        await test01()

async def test01():
    """
    Demonstrates listing blobs in an Azure Storage container and logs their properties.

    This function calls the _accessor's list_blobs_in_container_async method to retrieve
    all blobs in the specified container. For each blob, it logs a set of key:value
    property pairs line by line, including name, size, content type, last_name modified date,
    and other relevant metadata.

    Raises:
        Exception: Any exception raised during the listing or logging process is logged and re-raised.
    """
    try:
        result = await _accessor.list_blobs_in_container_async(_test_account_connection_str, _containername)
        print(f"_accessor.list_blobs_in_container_async() succeeded:\rn")

        answer: List[str] = []

        for blob in result:
            answer.append("BlobProperties:")
            for prop in [
                "name", "size", "content_type", "last_modified", "etag", "creation_time",
                "blob_type", "lease_status", "lease_state", "lease_duration", "server_encrypted",
                "metadata", "container", "snapshot", "version_id", "deleted", "remaining_retention_days"
            ]:
                if prop == "content_type":
                    # Always access content_type via content_settings
                    value = getattr(getattr(blob, "content_settings", None), "content_type", None)
                else:
                    value = getattr(blob, prop, None)
                answer.append(f"  {prop}: {value}")
            # Log the answer as a block
            print("\n".join(answer))

    except Exception as ex:
        print(f"_accessor.list_blobs_in_container_async() method failed:\n{ex}")
        return

async def test02():
    """
    Illustrates usage of upload_content_to_azure_blob.
    """
    try:
        result = await _accessor.upload_string_async(_test_account_connection_str, _containername, _upload_blob_name, _blob_contents_text, False)
        log_event(
            logger,
            message="method upload_content_to_azure_blob() succeeded:\rn",
            level=logging.INFO
        )
        answer = result
        log_event(
            logger,
            message=f"AbsoluteURL: {answer}",
            level=logging.INFO
        )








    except Exception as ex:
        print(f"_accessor.upload_string_async() method failed:\rn{ex}")
        return

async def test03():
    """
    Illustrates usage of get_if_blob_exists_async.
    """
    try:
        result = await _accessor.get_if_blob_exists_async(
            _test_account_connection_str, _containername, _upload_blob_name
        )
        print(f"_accessor.get_if_blob_exists_async() succeeded:\n")
        print(f"Blob exists: {result}")
    except Exception as ex:
        print(f"_accessor.get_if_blob_exists_async() method failed:\n{ex}")
        return

async def test04():
    """
    Illustrates usage of retrieving blob properties using list_blobs_in_container_async.
    Logs the properties of the specified blob if found.
    """
    try:
        result = await _accessor.list_blobs_in_container_async(
            _test_account_connection_str, _containername, blob_name_filter=_upload_blob_name
        )
        print(f"_accessor.list_blobs_in_container_async() succeeded:\n")
        if not result:
            print(f"No blob found with name: {_upload_blob_name}")
            return

        blob = result[0]
        answer: list[str] = []
        answer.append("BlobProperties:")
        for prop in [
            "name", "size", "content_type", "last_modified", "etag", "creation_time",
            "blob_type", "lease_status", "lease_state", "lease_duration", "server_encrypted",
            "metadata", "container", "snapshot", "version_id", "deleted", "remaining_retention_days"
        ]:
            if prop == "content_type":
                value = getattr(getattr(blob, "content_settings", None), "content_type", None)
            else:
                value = getattr(blob, prop, None)
            answer.append(f"  {prop}: {value}")
        print("\n".join(answer))
    except Exception as ex:
        print(f"test04() failed to retrieve blob properties:\n{ex}")
        return

async def test05():
    """
    Illustrates usage of get_absolute_uri_of_blob_async.
    """
    try:
        result = await _accessor.get_absolute_uri_of_blob_async(
            _test_account_connection_str, _containername, _upload_blob_name
        )
        print(f"_accessor.get_absolute_uri_of_blob_async() succeeded:\n")
        if result:
            print(f"Absolute URI: {result}")
        else:
            print("Blob does not exist or URI could not be retrieved.")
    except Exception as ex:
        print(f"_accessor.get_absolute_uri_of_blob_async() method failed:\n{ex}")
        return
    
async def test06():
    """
    Illustrates usage of download_async to download blob content.
    Logs the size of the downloaded content or a message if the blob does not exist.
    """
    try:
        result = await _accessor.download_async(
            _test_account_connection_str, _containername, _upload_blob_name
        )
        print(f"_accessor.download_async() succeeded:\n")
        if result is not None:
            print(f"Downloaded blob size: {len(result)} bytes")
            print(f"Content: {result.decode('utf-8')}")
        else:
            print("Blob does not exist or could not be downloaded.")
    except Exception as ex:
        print(f"_accessor.download_async() method failed:\n{ex}")
        return

async def test07():
    """
    Illustrates usage of delete_blob_if_exists_async.
    """
    try:
        result = await _accessor.delete_blob_if_exists_async(
            _test_account_connection_str, _containername, _upload_blob_name
        )
        print(f"_accessor.delete_blob_if_exists_async() succeeded:\n")
        if result:
            print(f"Blob was deleted: {_upload_blob_name}")
        else:
            print(f"Blob did not exist or could not be deleted: {_upload_blob_name}")
    except Exception as ex:
        print(f"_accessor.delete_blob_if_exists_async() method failed:\n{ex}")
        return

 #main runner

if __name__ == "__main__":
    import logging
    from jgh_exceptions import AlertMessageError
    from jgh_logging import setup_json_logging, log_event
    from storage_config import DIRPATH_LOGGING

    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    try:
        _containername = "testuploadcontainer"
        _upload_blob_name = "my_happy_little_test_blob.txt"
        _blob_contents_text = "Hello, Azure Blob Storage! testing, testing, testing"
        _accessor = AzureStorageAccessor()
        _test_account_connection_str = ConnectionStringRepository.get_azure_storage_account_connection_string("customertester")

        start_time = time.time()
        asyncio.run(test00())
        end_time = time.time()

        success_msg = f"Success: Main execution completed successfully in {end_time - start_time:.2f} seconds."
        log_event(logger, message=success_msg, level=logging.INFO)
        print(f"\n{success_msg}\n")
    except AlertMessageError as alert_err:
        log_event(logger, message=alert_err.message, level=logging.INFO, exception=alert_err)
        print(f"{alert_err.message}\n")
    except Exception as ex:
        log_event(logger, message=f"Unhandled Exception: {ex}", level=logging.ERROR, exception=ex)  # Pass the original exception object
        print(f"Unhandled Exception: {ex}\n\nPlease check the logs for details.\n\nDirpath: {DIRPATH_LOGGING}\n")



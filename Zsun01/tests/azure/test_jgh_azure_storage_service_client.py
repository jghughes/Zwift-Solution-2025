import asyncio
from jgh_azure_storage_service_client import AzureStorageServiceClient

import time
import logging
from jgh_exceptions import AlertMessageError
from jgh_logging import setup_json_logging, log_event
from storage_config import DIRPATH_LOGGING


#testing
async def main00():
    """
    Demonstrates checking if the service is answering using AzureStorageServiceClient.
    """
    try:
        result = await client.get_if_service_is_answering_async()
        print(f"client.get_if_service_is_answering_async() succeeded:\n")
        print(f"Service is answering: {result}")
    except Exception as ex:
        print(f"client.get_if_service_is_answering_async() failed:\n{ex}")
        raise

async def main000():
    """
    Demonstrates getting service endpoints info using AzureStorageServiceClient.
    """
    try:
        result = await client.get_service_endpoints_info_async()
        print(f"client.get_service_endpoints_info_async() succeeded:\n")
        print(f"Endpoints: {result}")
    except Exception as ex:
        print(f"client.get_service_endpoints_info_async() failed:\n{ex}")
        raise

async def test01():
    """
    Demonstrates listing blobs in a container using AzureStorageServiceClient and logs their properties.
    """
    try:
        result = await client.get_particulars_of_blobs_in_container_async(_test_account_name, _test_container_name, "*")
        print(f"client.get_particulars_of_blobs_in_container_async() succeeded:\n")
        for name, size in result.items():
            print(f"Blob: {name}, Size: {size}")
    except Exception as ex:
        print(f"client.get_particulars_of_blobs_in_container_async() failed:\n{ex}")
        raise

async def test02():
    """
    Demonstrates uploading a string as a blob using AzureStorageServiceClient.
    """
    try:
        result = await client.upload_string_to_block_blob_async(
            _test_account_name, _test_container_name, _upload_blob_name, _blob_contents_text, False
        )
        print(f"client.upload_string_to_block_blob_async() succeeded:\n")
        print(f"AbsoluteURL: {result}")
    except Exception as ex:
        print(f"client.upload_string_to_block_blob_async() failed:\n{ex}")
        raise

async def test03():
    """
    Demonstrates checking if a blob exists using AzureStorageServiceClient.
    """
    try:
        result = await client.get_if_blob_exists_async(
            _test_account_name, _test_container_name, _upload_blob_name
        )
        print(f"client.get_if_blob_exists_async() succeeded:\n")
        print(f"Blob exists: {result}")
    except Exception as ex:
        print(f"client.get_if_blob_exists_async() failed:\n{ex}")
        raise

async def test04():
    """
    Demonstrates retrieving the absolute URI of a blob using AzureStorageServiceClient.
    """
    try:
        result = await client.get_absolute_uri_of_blob_async(
            _test_account_name, _test_container_name, _upload_blob_name
        )
        print(f"client.get_absolute_uri_of_blob_async() succeeded:\n")
        if result:
            print(f"Absolute URI: {result}")
        else:
            print("Blob does not exist or URI could not be retrieved.")
    except Exception as ex:
        print(f"client.get_absolute_uri_of_blob_async() failed:\n{ex}")
        raise

async def test05():
    """
    Demonstrates downloading a blob as bytes using AzureStorageServiceClient.
    """
    try:
        result = await client.download_block_blob_as_bytes_async(
            _test_account_name, _test_container_name, _upload_blob_name
        )
        print(f"client.download_block_blob_as_bytes_async() succeeded:\n")
        if result is not None:
            print(f"Downloaded blob size: {len(result)} bytes")
            print(f"Content: {result.decode('utf-8')}")
        else:
            print("Blob does not exist or could not be downloaded.")
    except Exception as ex:
        print(f"client.download_block_blob_as_bytes_async() failed:\n{ex}")
        raise

async def test06():
    """
    Demonstrates deleting a blob if it exists using AzureStorageServiceClient.
    """
    try:
        result = await client.delete_block_blob_if_exists_async(
            _test_account_name, _test_container_name, _upload_blob_name
        )
        print(f"client.delete_block_blob_if_exists_async() succeeded:\n")
        if result:
            print(f"Blob was deleted: {_upload_blob_name}")
        else:
            print(f"Blob did not exist or could not be deleted: {_upload_blob_name}")
    except Exception as ex:
        print(f"client.delete_block_blob_if_exists_async() failed:\n{ex}")
        raise

async def test07():
    """
    Demonstrates uploading bytes as a blob using AzureStorageServiceClient.
    """
    try:
        result = await client.upload_bytes_to_block_blob_async(
            _test_account_name, _test_container_name, _upload_blob_name, _blob_contents_text.encode("utf-8"), False
        )
        print(f"client.upload_bytes_to_block_blob_async() succeeded:\n")
        print(f"AbsoluteURL: {result}")
    except Exception as ex:
        print(f"client.upload_bytes_to_block_blob_async() failed:\n{ex}")
        raise

async def test08():
    """
    Demonstrates checking if a container exists using AzureStorageServiceClient.
    """
    try:
        result = await client.get_if_container_exists_async(
            _test_account_name, _test_container_name
        )
        print(f"client.get_if_container_exists_async() succeeded:\n")
        print(f"Container exists: {result}")
    except Exception as ex:
        print(f"client.get_if_container_exists_async() failed:\n{ex}")
        raise

#test runner
if __name__ == "__main__":
    setup_json_logging(DIRPATH_LOGGING)
    logger = logging.getLogger()

    start_time = time.time()
    try:
        client = AzureStorageServiceClient()
        _test_account_name = "customertester"
        _test_container_name = "testuploadcontainer"
        _upload_blob_name = "my_happy_little_test_blob.txt"
        _blob_contents_text = "Hello, Azure Blob Storage! testing, testing, testing"
        asyncio.run(main00())
        asyncio.run(main000())
        asyncio.run(test01())
        asyncio.run(test02())
        asyncio.run(test03())
        asyncio.run(test04())
        asyncio.run(test05())
        asyncio.run(test06())
        asyncio.run(test07())
        asyncio.run(test08())
        asyncio.run(test01())  # List blobs again to confirm deletion
        end_time = time.time()
        duration = end_time - start_time

        log_event(
            logger,
            message=f"Main execution completed successfully in {duration:.2f} seconds. All tests executed without error.",
            level=logging.INFO
        )
        print(f"\nSuccess: Main execution completed successfully in {duration:.2f} seconds. All tests executed without error.\n")

    except AlertMessageError as alert_err:
        # Print only the error message
        print(f"{alert_err.message}\n")
        # Log the error as INFO
        log_event(
            logger,
            message=alert_err.message,
            level=logging.INFO,
            exception=alert_err
        )

    except Exception as ex:
        log_event(
            logger,
            message=f"Unhandled Exception: {ex}",
            level=logging.ERROR,
            exception=ex  # Pass the original exception object
        )
        print(f"Unhandled Exception: {ex}\n\nPlease check the logs for more details.\n\nDirpath: {DIRPATH_LOGGING}\n")




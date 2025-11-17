import asyncio
import os
from typing import List, Optional

import aiofiles
import httpx

from jgh_path_helpers import is_valid_dirpath, is_valid_foldername, is_valid_url, parse_filename

import logging
from jgh_logging import setup_json_logging, log_event
from storage_config import DIRPATH_LOGGING
setup_json_logging(DIRPATH_LOGGING)
logger = logging.getLogger()



async def _download_file(http_client: httpx.AsyncClient, url: str, dest_dir_path: str, dest_folder: Optional[str], semaphore: asyncio.Semaphore) -> None:
    # Validate inputs
    valid_url, url_msg = is_valid_url(url)
    if not valid_url:
        log_event(
            logger,
            message=url_msg,
            level=logging.ERROR,
            extra_fields={"field_name": "url"}
        )
        return
    valid_dirpath, dirpath_msg = is_valid_dirpath(dest_dir_path)
    if not valid_dirpath:
        log_event(
            logger,
            message=dirpath_msg,
            level=logging.ERROR,
            extra_fields={"field_name": "dest_dir_path"}
        )
        return

    # Validate the destination folder
    if dest_folder:
        valid_foldername, foldername_msg = is_valid_foldername(dest_folder)
        if not valid_foldername:
            log_event(
                logger,
                message=foldername_msg,
                level=logging.ERROR,
                extra_fields={"field_name": "dest_folder"}
            )
            return
        return

    # Treat None or "" as "no folder"
    if dest_folder:
        valid_foldername, foldername_msg = is_valid_foldername(dest_folder)
        if not valid_foldername:
            log_event(
                logger,
                message=foldername_msg,
                level=logging.ERROR,
                extra_fields={"field_name": "dest_folder"}
            )
            return
        dest_folder_path = os.path.join(dest_dir_path, dest_folder)
    else:
        dest_folder_path = dest_dir_path

    os.makedirs(dest_folder_path, exist_ok=True)
    filename = parse_filename(url)
    dest_path = os.path.join(dest_folder_path, filename)
    async with semaphore:
        try:
            response = await http_client.get(url, timeout=30)
            response.raise_for_status()
            async with aiofiles.open(dest_path, 'wb') as f:
                await f.write(response.content)
            file_size_bytes = os.path.getsize(dest_path)
            log_event(
                logger,
                message="File downloaded successfully.",
                level=logging.INFO,
                extra_fields={
                    "url": url,
                    "dest_path": dest_path,
                    "filename": filename,
                    "dest_folder": dest_folder_path,
                    "file_size_bytes": file_size_bytes
                }
            )
        except httpx.TimeoutException as e:
            log_event(
                logger,
                message=f"Timeout while downloading: {url}",
                level=logging.ERROR,
                exception=e,
                extra_fields={
                    "operation": "download_file",
                    "timeout_seconds": 30
                }
            )
            return
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            if status_code == 404:
                log_event(
                    logger,
                    message=f"File not found (404) for: {url}",
                    level=logging.ERROR,
                    exception=e,
                    extra_fields={
                        "resource_name": url,
                        "http_status": status_code
                    }
                )
            else:
                log_event(
                    logger,
                    message=f"HTTP error {status_code} for: {url}",
                    level=logging.ERROR,
                    exception=e,
                    extra_fields={
                        "exception_type": "HTTPStatusError",
                        "http_status": status_code
                    }
                )
            return
        except httpx.RequestError as e:
            response = getattr(e, "response", None)
            status_code = response.status_code if response is not None else ""


            log_event(
                logger,
                message=f"Network error for {url}: {e}",
                level=logging.ERROR,
                exception=e,
                extra_fields={
                    "url": url,
                    "status_code": status_code
                }
            )
            return
        except ValueError as e:
            log_event(
                logger,
                message=f"Validation error for {url}: {e}",
                level=logging.ERROR,
                exception=e,
                extra_fields={
                    "field_name": "url"
                }
            )
            return
        except Exception as e:
            log_event(
                logger,
                message=f"Unhandled exception while downloading {url}: {e}",
                level=logging.ERROR,
                exception=e,
                extra_fields={
                    "url": url
                }
            )
            return

async def download_many_files(urls: List[str], dest_dir_path: str, dest_folder: Optional[str], max_concurrent: int = 5) -> None:
    semaphore = asyncio.Semaphore(max_concurrent)
    async with httpx.AsyncClient() as http_client:
        tasks = [
            _download_file(http_client, url, dest_dir_path, dest_folder, semaphore)
            for url in urls
        ]
        await asyncio.gather(*tasks)


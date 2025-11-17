from typing import List
from pathlib import Path
from jgh_exceptions import AlertMessageError
from storage_config import CONNECTION_STRING_FILENAME, CONNECTION_STRING_DIRPATH
from jgh_read_write import read_lines


class ConnectionStringRepository:
    """
    Repository for managing Azure Storage account connection strings.

    This class provides methods to retrieve connection strings for Azure
    Storage accounts, either as a list (for brute-force or enumeration
    scenarios) or individually by account name. Connection strings are
    read from a text file located at a predefined directory path. The
    class uses an internal cache to avoid repeated file reads.

    For security reasons, a key assumption is that a text file is
    stored externally so that connection strings are not exposed on
    GitHub. This is a secure-enough way to manage connection strings in
    a development environment. In a production environment, this
    repository would obtain secrets from Azure where production
    connection strings are securely stored.

    Attributes:
        CONNECTION_STRING_FILENAME (str): The filename containing the
            connection strings.
        CONNECTION_STRING_DIRPATH (str): The directory path where the
            connection strings file is stored.
        _cache_of_connection_strings (List[str]): Internal cache of
            connection strings.

    Methods:
        get_azure_storage_account_connection_strings_for_zsun()
            -> List[str]: Returns all Azure Storage account connection
            strings from the file.

        get_azure_storage_account_connection_string(account_name: str)
            -> str: Returns the connection string for a specific Azure
            Storage account. Raises AlertMessageError if the
            account is not found.
    """    

    _cache_of_connection_strings: List[str] = []

    @classmethod
    def get_azure_storage_account_connection_strings_for_zsun(cls) -> List[str]:
        return read_lines(Path(CONNECTION_STRING_DIRPATH), CONNECTION_STRING_FILENAME)

    @classmethod
    def get_azure_storage_account_connection_string(cls, account_name: str) -> str:
        """
        Retrieves the connection string for a specific Azure Storage account. You must 
        copy these from the Azure portal and store them in a .txt file. Preferably, use 
        the secondary keys.
        Args:
            account_name (str): The name of the Azure Storage account.
        Returns:
            str: The connection string for the specified account.
        Raises:
            AlertMessageError: If the account name is not found in the cached connection strings.
        """
        if not cls._cache_of_connection_strings:
            cls._cache_of_connection_strings = cls.get_azure_storage_account_connection_strings_for_zsun()
        for conn_str in cls._cache_of_connection_strings:
            if f"AccountName={account_name};" in conn_str:
                return conn_str
        raise AlertMessageError(f"Connection string for Azure account '{account_name}' not found.")





# install ruff on your machine if you haven't already. pip install ruff
# ruff is for using in the terminal.
# type 'ruff -h' for help.
# type ruff check {filename} to check the file for errors
# type ruff fix {filename} to fix the file errors
# type ruff format {filename} to format the file beautifully
import json
from json.decoder import JSONDecodeError
from typing import Union, Dict, Any, Optional
from typing import Dict

from club_member_item import ClubMemberItem


class ClubMembershipRepository:
    """
    A database object wrapping a keyed collection of members. The data backing store
    is a dictionary with a single entry. The key of the entry is stored as a class
    constant in MEMBERSHIP_DATA_KEY.

    The value of the entry is a dictionary where the key of each entry
    is a string and the value is an instance of a ClubMemberItem. The intention is that the
    key will be the Zwift ID of the member.

    Other keys can be added to the dictionary as the database evolves.

    Entry:
        MEMBERSHIP_DATA_KEY (Dict[str, ClubMemberItem]): The entry in the backing store that
            contains a dictionary of keyed ClubMemberItem instances.

    Functions:
        __after_init__: Initializes a new instance of the backing stores for this repository.
        import_clubmembership_database: Imports a club membership database into the repository.
        import_dictionary_of_clubmembers: Imports a dictionary of ClubMemberItem instances into the repository conditionally.
        import_list_of_clubmembers: Imports a list of ClubMemberItem instances into the repository conditionally.
        import_database_from_json: Creates a ClubMembershipRepository instance from a JSON string.
        export_database_as_object: Converts the ClubMembershipRepository instance to an object suitable for serialization.
        export_database_as_json: Converts the ClubMembershipRepository instance to a JSON string.
        entry_exists: Determines if a key exists in the repository.
        write_entry: Adds or overwrites an entry in the repository.
        delete_entry: Removes a key and its associated ClubMemberItem instance from the repository.
        obtain_value: Retrieves a ClubMemberItem from the repository.
        obtain_count: Retrieves the number of items in the repository.
        obtain_all_keys: Retrieves all the keys in the repository.
        obtain_all_values: Retrieves all the ClubMembers in the repository.
        obtain_all_entries: Retrieves all the entries in the repository.
        __repr__: Reveals the underlying string representation of the repository.
        __eq__: Determines if the ClubMembershipRepository instance is equivalent to another object.
        __ne__: Determines if the ClubMembershipRepository instance is not equivalent to another object.
        __hash__: Generates a hash of the ClubMembershipRepository instance.
        __len__: Retrieves the number of items in the repository."""

    MEMBERSHIP_DATA_KEY : str = "membership_data"

    backingstore_complete_database: Dict[str, Dict[str, ClubMemberItem]] = {}

    backingstore_clubmembers: Dict[str, ClubMemberItem] = backingstore_complete_database.setdefault(MEMBERSHIP_DATA_KEY, {})

    @staticmethod
    def validate_database_of_clubmembers(
        database: dict[str, ClubMemberItem], membership_data_key: str
    ) -> bool:
        """
        Validates if the input parameter is a valid database of ClubMemberItem instances.

        This function performs the following checks:
        1. Ensures the input parameter is not None.
        2. Ensures the input parameter is a dictionary.
        3. Ensures all keys in the dictionary are strings.
        4. Ensures the membership_data_key is not None and is a string.
        5. Ensures the dictionary contains the key membership_data_key.
        6. Ensures the value of membership_data_key is a valid dictionary of ClubMemberItem instances.

        Args:
            database (dict[str, any]): The database to validate.
            membership_data_key (str): The key to validate in the database.

        Returns:
            bool: True if the input parameter is valid, False otherwise.
        """
        # Check if the database object is not None
        if database is None:
            return False

        # Check if the database object is a dictionary
        if not isinstance(database, dict):
            return False

        # Check if all keys in the dictionary are strings
        if not all(isinstance(key, str) for key in database.keys()):
            return False

        # Check if the membership_data_key is not None and is a string
        if membership_data_key is None or not isinstance(membership_data_key, str):
            return False

        # Check if the dictionary contains the key membership_data_key
        if membership_data_key not in database:
            return False

        # Check if the value of membership_data_key is a valid dictionary of ClubMembers
        if not validate_dictionary_of_clubmembers(database[membership_data_key]):
            return False

        return True

    @staticmethod
    def validate_dictionary_of_clubmembers(clubmembers: dict[str, ClubMemberItem]) -> bool:
        """
        Validates if the input parameter is a valid dictionary of ClubMemberItem instances.

        This function performs the following checks:
        1. Ensures the input parameter is not None.
        2. Ensures the input parameter is a dictionary.
        3. Ensures all keys in the dictionary are strings.
        4. Ensures all values in the dictionary are instances of ClubMemberItem.

        Args:
            clubmembers (dict[str, ClubMemberItem]): The dictionary of ClubMemberItem instances to validate.

        Returns:
            bool: True if the input parameter is valid, False otherwise.
        """
        # Check if the object is not None
        if clubmembers is None:
            return False

        # Check if the object is a dictionary
        if not isinstance(clubmembers, dict):
            return False

        # Check if all keys in the dictionary are strings
        if not all(isinstance(key, str) for key in clubmembers.keys()):
            return False

        # Check if all values in the dictionary are ClubMemberItem instances
        if not all(isinstance(value, ClubMemberItem) for value in clubmembers.values()):
            return False

        return True

    @staticmethod
    def validate_list_of_clubmembers(clubmembers: list[ClubMemberItem]) -> bool:
        """
        Validates if the input parameter is a valid list of ClubMemberItem instances.

        This function performs the following checks:
        1. Ensures the input parameter is not None.
        2. Ensures the input parameter is a list.
        3. Ensures all elements in the list are instances of ClubMemberItem.

        Args:
            clubmembers (list[ClubMemberItem]): The list of ClubMemberItem instances to validate.

        Returns:
            bool: True if the input parameter is valid, False otherwise.
        """
        # Check if the object is not None
        if clubmembers is None:
            return False

        # Check if the object is a list
        if not isinstance(clubmembers, list):
            return False

        # Check if the list only contains ClubMemberItem instances
        if not all(isinstance(member, ClubMemberItem) for member in clubmembers):
            return False

        return True

    def import_clubmembership_database(
        self, databaseobject: dict[str, dict[str, ClubMemberItem]]
    ) -> bool:
        """
        Imports a club membership database into the repository.

        This function performs the following steps:
        1. Validates the input database object using the validate_database_of_clubmembers function.
        2. If the database object is valid, it overwrites the existing backing store with the new database object.
        3. If the database object is not valid, it returns False.

        Args:
            databaseobject (dict[str, dict[str, ClubMemberItem]]): The database object to import. It should be a dictionary where the key is a string and the value is another dictionary with string keys and ClubMemberItem values.

        Returns:
            bool: True if the import is successful, False otherwise.
        """
        isvaliddatabase = self.validate_database_of_clubmembers(
            databaseobject, ClubMembershipRepository.MEMBERSHIP_DATA_KEY
        )

        if not isvaliddatabase:
            return False

        self.backingstore_complete_database = databaseobject  # overwrite

        return True

    def import_dictionary_of_clubmembers(
        self, clubmemberdictionary: dict[str, ClubMemberItem], mustreplace: bool = False
    ) -> bool:
        """
        Imports a dictionary of ClubMemberItem instances into the repository conditionally. The instances are stored in the backing store.
        The backing store is a dictionary where the key is the Zwift ID of the member and the value is the ClubMemberItem instance.

        Args:
            clubmemberdictionary (dict[str, ClubMemberItem]): The dictionary of ClubMemberItem instances to import.
            mustreplace (bool): If True, the existing backing store is overwritten. If False, the dictionary is appended to the existing backing store.

        Returns:
            bool: True if the import is successful, False otherwise.
        """
        is_valid_dictionary_of_clubmembers = validate_dictionary_of_clubmembers(
            clubmemberdictionary
        )

        if not is_valid_dictionary_of_clubmembers:
            return False

        if mustreplace:
            # Overwrite the existing backing store using the clubmemberdictionary
            self.backingstore_clubmembers = clubmemberdictionary
        else:
            # Append the clubmemberdictionary to the existing backing store
            self.backingstore_clubmembers.update(clubmemberdictionary)

        return True

    def import_list_of_clubmembers(
        self, clubmemberlist: list[ClubMemberItem], mustreplace: bool = False
    ) -> bool:
        """
        Imports a list of ClubMemberItem instances into the repository conditionally. The instances are stored in the backing store.
        The backing store is a dictionary where the key is the Zwift ID of the member and the value is the ClubMemberItem instance.

        Args:
            clubmemberlist (list[ClubMemberItem]): The list of ClubMemberItem instances to import.
            mustreplace (bool): If True, the existing backing store is overwritten. If False, the list is appended to the existing backing store.

        Returns:
            bool: True if the import is successful, False otherwise.
        """
        is_valid_list_of_clubmembers = validate_list_of_clubmembers(clubmemberlist)

        if not is_valid_list_of_clubmembers:
            return False

        if mustreplace:
            # Overwrite the existing backing store using the clubmemberlist
            self.backingstore_clubmembers = {
                member.create_key(): member for member in clubmemberlist
            }
        else:
            # Append the clubmemberlist to the existing backing store
            for member in clubmemberlist:
                self.backingstore_clubmembers[member.create_key()] = member

        return True

    def import_database_from_json(self, databasejson: str) -> bool:
        try:
            try:
                pythonobject = json.loads(databasejson)
            except JSONDecodeError as e:
                raise ValueError(
                    f"The provided input string is not valid JSON. It is malformed: {e}"
                )

            return self.import_clubmembership_database(pythonobject)
        except ValueError as e:
            raise ValueError(
                f"The attempt to populate the ClubMembershipRepository failed: {e}"
            )

    def export_database_as_object(self) -> Union[Dict[str, Dict[str, Any]], None]:
        """
        Exports the database in its entirety as a python object.

        This function performs the following steps:
        1. Checks if the complete database exists.
        2. If the complete database does not exist, it returns None.
        3. If the complete database exists, it returns the complete database.

        Returns:
            dict[str, dict[str, ClubMemberItem]]: A dictionary-of-dictionaries representation of the database.
            None: If the  database does not exist.
        """
        if not self.backingstore_complete_database:
            return None
        return self.backingstore_complete_database

    def export_database_as_json(self) -> Union[str, None]:
        """
        Exports the database in its entirety as a JSON string.

        This function performs the following steps:
        1. Checks if the database exists.
        2. If the database does not exist, it returns None.
        3. If the database exists, it returns the database as JSON.

        Returns:
            str: A JSON string representation of the repository instance
            None: If the  database does not exist.
        """

        """
        Converts the Repository instance to a JSON string.
        Use this function to return a JSON string representation of the repository.

        Returns:
            str: A JSON string representation of the repository instance or None if repository does not exist.
        """
        if not self.backingstore_complete_database:
            return None
        return json.dumps(self.backingstore_complete_database)

    def export_dictionary_of_clubmembers_as_json(self) -> Union[str, None]:
        """
        Exports the dictionary of club members as a JSON string.

        This function performs the following steps:
        1. Checks if the dictionary of club members exists.
        2. If the dictionary of club members does not exist, it returns None.
        3. If the dictionary of club members exists, it returns the dictionary as JSON.

        Returns:
            str: A JSON string representation of the dictionary of club members.
            None: If the dictionary of club members does not exist.
        """
        if not self.backingstore_clubmembers:
            return None
        return json.dumps(self.backingstore_clubmembers)

    def export_list_of_clubmembers_as_json(self) -> Union[str, None]:
        """
        Exports the list of ClubMemberItem instances as a JSON string.

        This function performs the following steps:
        1. Checks if the list of ClubMemberItem instances exists.
        2. If the list of ClubMemberItem instances does not exist, it returns None.
        3. If the list of ClubMemberItem instances exists, it returns the list as JSON.

        Returns:
            str: A JSON string representation of the list of ClubMemberItem instances.
            None: If the list of ClubMemberItem instances does not exist.
        """
        if not self.backingstore_clubmembers:
            return None
        return json.dumps(list(self.backingstore_clubmembers.values()))

    def entry_exists(self, key: str) -> bool:
        """
        Determines if a key exists.
        Args:
            key (str): The key to check for.
        Returns:
            bool: True if the key exists in the repository. False if the key argument is not a string or the key does not exist or the repository does not exist.
        """
        if not self.backingstore_clubmembers or not isinstance(key, str):
            return False
        return key in self.backingstore_clubmembers

    def write_entry(self, key: str, value: ClubMemberItem):
        """
        Adds or overwrites an entry.
        If the key already exists in the repository, the entry will be overwritten.
        Does nothing if the key argument is not a string or the value of the entry is not a ClubMemberItem instance.

        Args:
            key (str): The key for the entry.
            value (an instance of a ClubMemberItem): The associated ClubMemberItem.
        """
        if (
            isinstance(key, str)
            and isinstance(value, ClubMemberItem)
            and self.backingstore_clubmembers
        ):
            self.backingstore_clubmembers[key] = value

    def delete_entry(self, key: str):
        """
        Removes a key and its associated ClubMemberItem instance.
        Does nothing if the key argument is not a string or the key does not exist in the repository or the repository does not exist.

        Args:
            key (str): The key for the entry.
        """
        if (
            self.backingstore_clubmembers
            and isinstance(key, str)
            and key in self.backingstore_clubmembers
        ):
            del self.backingstore_clubmembers[key]

    def obtain_value(self, key: str) -> Optional[ClubMemberItem]:
        """
        Retrieves a ClubMemberItem from the repository.

        Args:
            key (str): The key for the entry.

        Returns:
            ClubMemberItem: The ClubMemberItem instance associated with the key.
            None: If the key argument is not a string or the key does not exist in the repository or the repository does not exist.
        """
        if (
            self.backingstore_clubmembers
            and isinstance(key, str)
            and key in self.backingstore_clubmembers
        ):
            return self.backingstore_clubmembers[key]
        return None

    def obtain_count(self) -> int:
        """
        Retrieves the number of items in the repository.

        Returns:
            int: The number of items in the repository or 0 if the repository does not exist or is empty.
        """
        return (
            len(self.backingstore_clubmembers) if self.backingstore_clubmembers else 0
        )

    def obtain_all_keys(self) -> list[str]:
        """
        Retrieves all the keys in the repository.
        Returns:
            list[str]: A list of all the keys in the repository or an empty list if the repository does not exist.
        """
        return (
            list(self.backingstore_clubmembers.keys())
            if self.backingstore_clubmembers
            else []
        )

    def obtain_all_values(self) -> list[ClubMemberItem]:
        """
        Retrieves all the values in the repository.

        Returns:
            list[ClubMemberItem]: A list of all the values in the repository or an empty list if the repository does not exist.
        """
        return (
            list(self.backingstore_clubmembers.values())
            if self.backingstore_clubmembers
            else []
        )

    def obtain_all_entries(self) -> list[tuple[str, ClubMemberItem]]:
        """
        Retrieves all the key-value pairs in the repository.
        Returns:
            list[tuple[str, ClubMemberItem]]: A list of all the key-value pairs in the repository or an empty list if the repository does not exist.
        """
        return (
            list(self.backingstore_clubmembers.items())
            if self.backingstore_clubmembers
            else []
        )

    def __str__(self) -> str:
        """
        Reveals the underlying string representation of the repository.

        Returns:
            str: A string representation of the repository.
        """
        return f"ClubMembershipRepository: {self.backingstore_clubmembers}"

    def __repr__(self) -> str:
        """
        Reveals the underlying string representation of the repository.
        Returns:
            str: A string representation of the repository.
        """
        return self.__str__()


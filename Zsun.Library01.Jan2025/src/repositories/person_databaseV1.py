
"""
This module defines the PersonDatabaseV1 class, which manages a database of club members.
It provides methods to import, export, and manipulate the membership data using Pydantic models.
"""

# Standard library imports
import json
from json.decoder import JSONDecodeError
from typing import Union, Dict, Any, List, Tuple

# Local application imports
from pydantic import BaseModel, PrivateAttr
from participant_item import PersonItem




class PersonDatabaseV1(BaseModel):
    """
    PersonDatabaseV1 is a class that manages a database of club members using the Pydantic BaseModel.
    It provides methods to import, export, and manipulate the membership data.

    Attributes:
        MEMBERSHIP_DATA_KEY (str): A constant key used to store membership data in the database.
        _database (Dict[str, Dict[str, PersonItem]]): A private attribute that holds the database of club members.

    Properties:
        database: Returns the database of club members.
        membership_dict: Returns the dictionary of club members.
        membership_list: Returns the list of club members as tuples of (key, PersonItem).
        count_clubmembers: Returns the count of club members.

    Methods:
        __str__(): Returns a string representation of the PersonDatabaseV1 instance.
        validate_database_of_clubmembers(database, membership_data_key): A static method to validate the database of club members.
        validate_dictionary_of_clubmembers(clubmembers): A static method to validate a dictionary of club members.
        validate_list_of_clubmembers(clubmembers): A static method to validate a list of club members.
        import_clubmembership_database(databaseobject): Imports a database of club members.
        import_dictionary_of_clubmembers(imported_dict, must_overwrite): Imports a dictionary of club members.
        import_list_of_clubmembers(clubmemberlist, must_overwrite): Imports a list of club members.
        import_database_from_json(databasejson): Imports a database of club members from a JSON string.
        export_database_as_object(): Exports the database as a Python object.
        export_database_as_json(): Exports the database as a JSON string.
        export_dictionary_of_clubmembers_as_json(): Exports the dictionary of club members as a JSON string.
        export_list_of_clubmembers_as_json(): Exports the list of club members as a JSON string.
        entry_exists(key): Checks if an entry exists in the database.
        write_entry(key, value): Writes an entry to the database.
        delete_entry(key): Deletes an entry from the database.
        retrieve_value(key): Retrieves a value from the database.
        retrieve_all_keys(): Retrieves all keys from the database.
        retrieve_all_values(): Retrieves all values from the database.
        retrieve_all_entries(): Retrieves all entries from the database.


    """
    MEMBERSHIP_DATA_KEY :str = "membership_data"

    _database: Dict[str, dict[str, PersonItem]] = PrivateAttr(
        default_factory=lambda: {PersonDatabaseV1.MEMBERSHIP_DATA_KEY: {}}
    )

    def __str__(self) -> str:
        return f"PersonDatabaseV1: {self.membership_dict}"

    @property
    def database(self) -> Dict[str, Dict[str, PersonItem]]:
        if not self._database:
            self._database = {PersonDatabaseV1.MEMBERSHIP_DATA_KEY: {}}

        if (
            PersonDatabaseV1.MEMBERSHIP_DATA_KEY
            not in PersonDatabaseV1._database
        ):
            #insert the key if it is missing
            PersonDatabaseV1._database[
                PersonDatabaseV1.MEMBERSHIP_DATA_KEY
            ] = {}

        return self._database

    @property
    def membership_dict(self) -> Dict[str, PersonItem]:
        return self.database[PersonDatabaseV1.MEMBERSHIP_DATA_KEY]

    @property
    def membership_list(self) -> list[tuple[str, PersonItem]]:
        return list(self.membership_dict.items())

    @property
    def count_clubmembers(self) -> int:

        return len(self.membership_list)

    @staticmethod
    def validate_database_of_clubmembers(
        database: dict[str, dict[str, PersonItem]], membership_data_key: str
    ) -> bool:
        # placeholder for the time-being
        return True

    @staticmethod
    def validate_dictionary_of_clubmembers(
        clubmembers: dict[str, PersonItem]
    ) -> bool:
        # placeholder for the time-being
        return True

    @staticmethod
    def validate_list_of_clubmembers(clubmembers: list[PersonItem]) -> bool:
        # placeholder for the time-being
        return True

    def import_clubmembership_database(
        self, databaseobject: dict[str, dict[str, PersonItem]]
    ) -> bool:
        isvaliddatabase = self.validate_database_of_clubmembers(
            databaseobject, PersonDatabaseV1.MEMBERSHIP_DATA_KEY
        )

        if not isvaliddatabase:
            return False

        self.backingstore_complete_database = databaseobject  # overwrite

        return True

    def import_dictionary_of_clubmembers(
        self, imported_dict: dict[str, PersonItem], must_overwrite: bool = False
    ) -> bool:

        # first validate the dictionary
        is_valid_dictionary_of_clubmembers = self.validate_dictionary_of_clubmembers(
            imported_dict
        )

        if not is_valid_dictionary_of_clubmembers:
            return False

        if must_overwrite:
            # Overwrite the existing backing store using the imported_dict
            self.backingstore_clubmembers = imported_dict
        else:
            # Append the imported_dict to the existing backing store
            self.backingstore_clubmembers.update(imported_dict)

        return True

    def import_list_of_clubmembers(
        self, clubmemberlist: list[PersonItem], must_overwrite: bool = False
    ) -> bool:
        is_valid_list_of_clubmembers = validate_list_of_clubmembers(clubmemberlist)

        if not is_valid_list_of_clubmembers:
            return False

        if must_overwrite:
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
                f"The attempt to populate the PersonDatabaseV1 failed: {e}"
            )

    def export_database_as_object(self) -> Union[Dict[str, Dict[str, Any]], None]:
        if not self.backingstore_complete_database:
            return None
        return self.backingstore_complete_database

    def export_database_as_json(self) -> Union[str, None]:
        if not self.backingstore_complete_database:
            return None
        return json.dumps(self.backingstore_complete_database)

    def export_dictionary_of_clubmembers_as_json(self) -> Union[str, None]:
        if not self.backingstore_clubmembers:
            return None
        return json.dumps(self.backingstore_clubmembers)

    def export_list_of_clubmembers_as_json(self) -> Union[str, None]:
        if not self.backingstore_clubmembers:
            return None
        return json.dumps(list(self.backingstore_clubmembers.values()))

    def entry_exists(self, key: str) -> bool:
        if not self.backingstore_clubmembers:
            return False
        return key in self.backingstore_clubmembers

    def write_entry(self, key: str, value: PersonItem):
        if self.backingstore_clubmembers:
            self.backingstore_clubmembers[key] = value

    def delete_entry(self, key: str):
        if self.backingstore_clubmembers and key in self.backingstore_clubmembers:
            del self.backingstore_clubmembers[key]

    def retrieve_value(self, key: str) -> Union[PersonItem, None]:
        if self.backingstore_clubmembers and key in self.backingstore_clubmembers:
            return self.backingstore_clubmembers[key]
        return None

    def retrieve_all_keys(self) -> list[str]:
        if not self.backingstore_clubmembers:
            return []

        return list(self.backingstore_clubmembers.keys())

    def retrieve_all_values(self) -> list[PersonItem]:
        if not self.backingstore_clubmembers:
            return []

        return list(self.backingstore_clubmembers.values())

    def retrieve_all_entries(self) -> list[tuple[str, PersonItem]]:
        if not self.backingstore_clubmembers:
            return []

        return list(self.backingstore_clubmembers.items())



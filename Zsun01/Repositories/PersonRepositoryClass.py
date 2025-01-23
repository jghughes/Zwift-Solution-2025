import json
from json.decoder import JSONDecodeError
from typing import Union, Dict, Any
from typing import Dict
from pydantic import BaseModel, Field, PrivateAttr
from PersonItem import PersonItem


class ClubMembershipRepository(BaseModel):

    MEMBERSHIP_DATA_KEY = "membership_data"

    _database: Dict[str, Dict[str, PersonItem]] = PrivateAttr(
        default_factory=lambda: {ClubMembershipRepository.MEMBERSHIP_DATA_KEY: {}}
    )

    def __str__(self) -> str:
        return f"ClubMembershipRepository: {self.membership_dict}"

    @property
    def database(self) -> Dict[str, Dict[str, PersonItem]]:
        if not self._database:
            self._database = {ClubMembershipRepository.MEMBERSHIP_DATA_KEY: {}}

        if (
            ClubMembershipRepository.MEMBERSHIP_DATA_KEY
            not in ClubMembershipRepository._database
        ):
            #insert the key if it is missing
            ClubMembershipRepository._database[
                ClubMembershipRepository.MEMBERSHIP_DATA_KEY
            ] = {}

        return self._database

    @property
    def membership_dict(self) -> Dict[str, PersonItem]:
        return self.database[ClubMembershipRepository.MEMBERSHIP_DATA_KEY]

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
            databaseobject, ClubMembershipRepository.MEMBERSHIP_DATA_KEY
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
                f"The attempt to populate the ClubMembershipRepository failed: {e}"
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


# Test cases for unit testing


def Test01():
    pass


def Test02():
    pass


def Test03():
    pass


# Run the tests
if __name__ == "__main__":
    Test01()
    Test02()
    Test03()

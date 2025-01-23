# install ruff on your machine if you haven't already. pip install ruff 
# ruff is for using in the terminal. 
# type 'ruff -h' for help. 
# type ruff check {filename} to check the file for errors
# type ruff fix {filename} to fix the file errors
# type ruff format {filename} to format the file beautifully
import sys 
import uuid
import time
import json
from json.decoder import JSONDecodeError
from datetime import datetime, timezone
from typing import Dict
from pathlib import Path
from pydantic import BaseModel
from tqdm import tqdm # For a progress bar in terminal for long running iterations. To use it, wrap the iterable with 'tqdm(iterable)'. For example: 'for i in tqdm(range(1000)):'
from rich import print
from rich.theme import Theme
from rich.console import Console
from rich.traceback import install
install(show_locals=True) # For better exception handling in the console
custom_theme = Theme( # Define a custom theme for the console
    {
        "info": "bold blue",
        "warning": "bold yellow",
        "danger": "bold red",
        "success": "bold green",
    })
console = Console(theme=custom_theme)

from ClubMemberClass import ClubMemberItem
from ClubMembershipRepositoryClass import ClubMembershipRepository

MEMBERSHIP_DATA_KEY = "membership_data"

# Example: Instantiate three sample instances of members: joe,joanna, and jill

joe = ClubMemberItem(
    zwift_id=3147366,
    zwift_firstname="joe",
    zwift_lastname="soap",
    discord_accountusername="Joe Soap",
    discord_accountdisplayname="Crusher Joe",
    discord_profiledisplayname="Joe the beast",
)

joanna = ClubMemberItem()
joanna.zwift_id = 88888888
joanna.zwift_firstname = "joanna"
joanna.zwift_lastname = "soap"
joanna.discord_accountusername = "Joanna Soap"
joanna.discord_accountdisplayname = "Sweet Joanna"
joanna.discord_profiledisplayname = "Joanna the amazon"

jill = ClubMemberItem()
jill.zwift_id = 88888888
jill.zwift_firstname = "jill"
jill.zwift_lastname = "soap"
jill.discord_accountusername = "Jill Soap"
jill.discord_accountdisplayname = "Beefy jill"
jill.discord_profiledisplayname = "Jill the ox"

# Instantiate a new ClubMembershipRepository 

repository = ClubMembershipRepository()

# Add the three members to the repository manuallly

repository.write_entry("100", joe)
repository.write_entry("200", joanna)
repository.write_entry("300", jill)

# Get a member from the repository

try:
    item = repository.obtain_value("200")
    print (f"{item.zwift_id}  {item.zwift_firstname}  {item.zwift_lastname}  {item.discord_accountusername}  {item.discord_accountdisplayname}  {item.discord_profiledisplayname}")
except KeyError as e:
    print(f"Error: {e}")

# Check if a member exists in the repository

print(repository.entry_exists("200"))
    
# Delete a member from the repository

repository.delete_entry("200")

# Try get a member that isn't in the repository

try:
    item = repository.obtain_value("200")
    print(item.__dict__)
except KeyError as e:
    print(f"Error: {e}")

# Get a count of the members in the repository

print(repository.obtain_count())

# Print the keys in the repository to the console in a vertical list

try:
    result = repository.obtain_all_keys()
    for z in result:
        print(z)
except KeyError as e:
    print(f"Error: {e}")

# Print the members in the repository to the console is a vertical list of JSON strings

try:
    result = repository.obtain_all_values()
    for z in result:
        print("")
        print(z.export_database_as_json() )
except KeyError as e:
    print(f"Error: {e}")

# Print the entries in the repository to the console in vertical list of summarised key-value pairs

try:
    result = repository.obtain_all_entries()
    for z in result:
        print(f"{z[0]} {z[1].zwift_firstname} {z[1].zwift_lastname}")
except KeyError as e:
    print(f"Error: {e}")



# Serialize the ClubMembershipRepository instance to a JSON string and print it to the console

serialisable_version_of_repository = repository.export_databaseobject()

serialised_repository = json.dumps(serialisable_version_of_repository, indent=4)

print(serialised_repository)


# Obtain a json version of a ClubMembershipRepository from somewhere, load it into a pythonobject, populate a new repository 
# with it, and write the underlying structure of the repository the console

equivalentobject_as_json = """
{
  "membership_data": 
  {
    "a": {
      "zwift_id": 3147366,
      "zwift_firstname": "joe",
      "zwift_lastname": "soap",
      "discord_accountusername": "Joe Soap",
      "discord_accountdisplayname": "Crusher Joe",
      "discord_profiledisplayname": "Joe the beast"
    },
    "b": {
      "zwift_id": 123456789,
      "zwift_firstname": "john",
      "zwift_lastname": "smith",
      "discord_accountusername": "Jonathon Smith",
      "discord_accountdisplayname": "J Smith",
      "discord_profiledisplayname": "Jonny Rotten"
    },
    "c": {
      "zwift_id": 987654321,
      "zwift_firstname": " ",
      "zwift_lastname": "doe",
      "discord_accountusername": "Jane Doe",
      "discord_accountdisplayname": "J Doe",
      "discord_profiledisplayname": "Jane the Brave"
    }
  }
}
"""


# Check if json.loads(equivalentobject_as_json) succeeds and if ClubMembershipRepository.import_databaseobject()
try:
    try:
        equivalentobject = json.loads(equivalentobject_as_json)
    except JSONDecodeError as e:
        print(f"Error: json.loads(equivalentobject_as_json) method failed. JSON format error: {e}")
        sys.exit(1)
    dummy_repository = ClubMembershipRepository.import_databaseobject(equivalentobject)
    rubbish = dummy_repository.obtain_all_keys
    rubbish2 = dummy_repository.obtain_all_values
    rubbish3 = dummy_repository.obtain_all_entries
except JSONDecodeError as e:
    print(f"Error: ClubMembershipRepository.import_databaseobject() failed. Unsure why. The structure of the originating JSON data might be wrong or the values of one or more fields in the JSON might be wrong: {e}")
    sys.exit(1)


# Convert the dictionary to a list of dictionaries
# This extracts the values from the MEMBERSHIP_DATA_KEY dictionary and converts them to a list
if MEMBERSHIP_DATA_KEY not in equivalentobject:
    print(f"Key '{MEMBERSHIP_DATA_KEY}' does not exist in the provided JSON object (which is a Dictionary).")
    sys.exit(1)

test_list = list(equivalentobject[MEMBERSHIP_DATA_KEY].values())

# Convert the list of dictionaries back to a JSON string
# This converts the list of dictionaries into a JSON-formatted string with attributes indented by 4 spaces for readinbililty
club_members = json.dumps(test_list, indent=4)

# Print the new JSON string
print(club_members)

# JSON string representing the same bunch of ClubMemberItem objects, this time in the format of a list not a dictionary
# This JSON string can be deserialized into a list of ClubMemberItem objects
serialised_dummy_array_of_members = """
[
  {
    "zwift_id": 3147366,
    "zwift_firstname": "joe",
    "zwift_lastname": "soap",
    "discord_accountusername": "Joe Soap",
    "discord_accountdisplayname": "Crusher Joe",
    "discord_profiledisplayname": "Joe the beast"
  },
  {
    "zwift_id": 123456789,
    "zwift_firstname": "john",
    "zwift_lastname": "smith",
    "discord_accountusername": "Jonathon Smith",
    "discord_accountdisplayname": "J Smith",
    "discord_profiledisplayname": "Jonny Rotten"
  },
  {
    "zwift_id": 987654321,
    "zwift_firstname": " ",
    "zwift_lastname": "doe",
    "discord_accountusername": "Jane Doe",
    "discord_accountdisplayname": "J Doe",
    "discord_profiledisplayname": "Jane the Brave"
  },
  {
    "zwift_id": 456789123,
    "zwift_firstname": "alice",
    "zwift_lastname": " ",
    "discord_accountusername": "Alice Wonderland",
    "discord_accountdisplayname": "A Wonderland",
    "discord_profiledisplayname": "Alice the Explorer"
  },
  {
    "zwift_id": 89123456,
    "zwift_firstname": "",
    "zwift_lastname": "brown",
    "discord_accountusername": "Charlie Brown",
    "discord_accountdisplayname": "C Brown",
    "discord_profiledisplayname": "Charlie the Great"
  },
  {
    "zwift_id": 321654987,
    "zwift_firstname": "bob",
    "zwift_lastname": "builder",
    "discord_accountusername": "Bob Builder",
    "discord_accountdisplayname": "B Builder",
    "discord_profiledisplayname": "Bob the Builder"
  }
]
"""

# Validate and deserialize the JSON string as a list of ClubMemberItem objects
# This converts the JSON-formatted string back into a list of ClubMemberItem objects
try:
    pythonobject = json.loads(serialised_dummy_array_of_members)
    xx = type(pythonobject);
    print(xx)
    somestring = pythonobject.__str__()
    print(somestring)
except JSONDecodeError as e:
    print(f"Error: Invalid JSON format: {e}")
    sys.exit(1)

def main():
    pass

if __name__ == "__main__":
    main()
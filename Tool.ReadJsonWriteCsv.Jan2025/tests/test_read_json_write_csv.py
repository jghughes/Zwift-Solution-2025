import os
import sys

# Add the Tool.ConvertJsonToCsvPython.Dec2024 directory to the system path
# sys.path.append(
#     os.path.abspath(
#         os.path.join(
#             os.path.dirname(__file__), "..", "Tool.ConvertJsonToCsvPython.Dec2024"
#         )
#     )
# )

from JghFileReaderWriters import read_json_write_pretty_csv

# Verify the import by printing a message
print("JghFileReaderWriters module imported successfully")

# Define the absolute paths
input_dirpath = r"C:/Users/johng/source/repos/Zwift-Solution-2024/Tool.ConvertJsonToCsvPython.Dec2024/test_json_files"
output_dirpath = r"C:/Users/johng/source/repos/Zwift-Solution-2024/Tool.ConvertJsonToCsvPython.Dec2024/test_csv_files"

# Define test cases
test_cases = [
    {
        "input_dirpath": input_dirpath,
        "input_filename": "invalid_structure.json",
        "output_dirpath": output_dirpath,
        "output_filename": "invalid_structure.csv",
        "excel_column_shortlist": ["id", "name", "email"],
        "excel_column_headers": {
            "id": "GroovyID",
            "name": "GroovyName",
            "email": "GroovyEmail",
        },
    },
    {
        "input_dirpath": input_dirpath,
        "input_filename": "valid_single_object.json",
        "output_dirpath": output_dirpath,
        "output_filename": "valid_single_object01.csv",
        "excel_column_shortlist": ["id", "name", "email"],
        "excel_column_headers": {
            "id": "GroovyID",
            "name": "GroovyName",
            "email": "GroovyEmail",
        },
    },
    {
        "input_dirpath": input_dirpath,
        "input_filename": "valid_single_object.json",
        "output_dirpath": output_dirpath,
        "output_filename": "valid_single_object02.csv",
        "excel_column_shortlist": [],
        "excel_column_headers": {},
    },
    {
        "input_dirpath": input_dirpath,
        "input_filename": "valid_single_object.json",
        "output_dirpath": output_dirpath,
        "output_filename": "valid_single_object03.csv",
        "excel_column_shortlist": [],
        "excel_column_headers": {
            "id": "GroovyID",
            "name": "GroovyName",
            "email": "GroovyEmail",
        },
    },
    {
        "input_dirpath": input_dirpath,
        "input_filename": "valid_single_object.json",
        "output_dirpath": output_dirpath,
        "output_filename": "valid_single_object04.csv",
        "excel_column_shortlist": ["id"],
        "excel_column_headers": {
            "id": "GroovyID",
            "name": "GroovyName",
            "email": "GroovyEmail",
        },
    },
    {
        "input_dirpath": input_dirpath,
        "input_filename": "valid_list_of_objects.json",
        "output_dirpath": output_dirpath,
        "output_filename": "valid_list_of_objects01.csv",
        "excel_column_shortlist": ["name", "name", "email"],
        "excel_column_headers": {
            "id": "GroovyID",
            "name": "GroovyName",
            "email": "GroovyEmail",
        },
    },
    {
        "input_dirpath": input_dirpath,
        "input_filename": "valid_list_of_objects.json",
        "output_dirpath": output_dirpath,
        "output_filename": "valid_list_of_objects02.csv",
        "excel_column_shortlist": [],
        "excel_column_headers": {},
    },
    {
        "input_dirpath": input_dirpath,
        "input_filename": "valid_list_of_objects.json",
        "output_dirpath": output_dirpath,
        "output_filename": "valid_list_of_objects03.csv",
        "excel_column_shortlist": [],
        "excel_column_headers": {
            "id": "GroovyID",
            "name": "GroovyName",
            "email": "GroovyEmail",
        },
    },
    {
        "input_dirpath": input_dirpath,
        "input_filename": "valid_list_of_objects.json",
        "output_dirpath": output_dirpath,
        "output_filename": "valid_list_of_objects04.csv",
        "excel_column_shortlist": ["name"],
        "excel_column_headers": {
            "id": "GroovyID",
            "name": "GroovyName",
            "email": "GroovyEmail",
        },
    },
    {
        "input_dirpath": input_dirpath,
        "input_filename": "valid_list_of_objects.json",
        "output_dirpath": output_dirpath,
        "output_filename": "valid_list_of_objects05.csv",
        "excel_column_shortlist": ["name", "name", "email"],
        "excel_column_headers": {
            "id": "GroovyID",
            "name": "GroovyName",
            "email": "GroovyEmail",
        },
    },
    {
        "input_dirpath": input_dirpath,
        "input_filename": "valid_list_of_objects.json",
        "output_dirpath": output_dirpath,
        "output_filename": "valid_list_of_objects06.csv",
        "excel_column_shortlist": ["email", "name", "id"],
        "excel_column_headers": {
            "id": "GroovyID",
            "name": "GroovyName",
            "email": "GroovyEmail",
        },
    },
    {
        "input_dirpath": input_dirpath,
        "input_filename": "valid_list_of_objects.json",
        "output_dirpath": output_dirpath,
        "output_filename": "valid_list_of_objects07.csv",
        "excel_column_shortlist": ["email", "name", "id"],
        "excel_column_headers": {
            "id": "GroovyID",
        },
    },
    {
        "input_dirpath": input_dirpath,
        "input_filename": "valid_list_of_objects.json",
        "output_dirpath": output_dirpath,
        "output_filename": "valid_list_of_objects08.csv",
        "excel_column_shortlist": ["email", "name", "id"],
        "excel_column_headers": {
            "rubbishid": "GroovyID",
            "rubbishname": "GroovyName",
            "rubbishemail": "GroovyEmail",
        },
    },
   {
        "input_dirpath": input_dirpath,
        "input_filename": "valid_list_of_riderKeys.json",
        "output_dirpath": output_dirpath,
        "output_filename": "valid_list_of_riderKeys.csv",
        "excel_column_shortlist": ["zwift_id", "zwift_firstname", "zwift_lastname", "discord_accountusername", "discord_accountdisplayname", "discord_profiledisplayname", "timestamp"],
        "excel_column_headers": {
            "zwift_id": "GroovyID",
            "zwift_firstname": "GroovyFirstName",
            "zwift_lastname": "GroovyLastName",
            "discord_accountusername": "GroovyEmail",
            "discord_accountdisplayname": "GroovyDiscordAccountUsername",
            "discord_profiledisplayname": "GroovyDiscordProfileDisplayName",
            "timestamp": "GroovyTimestamp",
        },
    },
       {
        "input_dirpath": input_dirpath,
        "input_filename": "valid_dict_of_riderKeys.json",
        "output_dirpath": output_dirpath,
        "output_filename": "valid_dict_of_riderKeys.csv",
        "excel_column_shortlist": ["zwift_id", "zwift_firstname", "zwift_lastname", "discord_accountusername", "discord_accountdisplayname", "discord_profiledisplayname","timestamp"],
        "excel_column_headers": {
            "zwift_id": "GroovyID",
            "zwift_firstname": "GroovyFirstName",
            "zwift_lastname": "GroovyLastName",
            "discord_accountusername": "GroovyEmail",
            "discord_accountdisplayname": "GroovyDiscordAccountUsername",
            "discord_profiledisplayname": "GroovyDiscordProfileDisplayName",
            "timestamp": "GroovyTimestamp",
        },

    },
{
        "input_dirpath": input_dirpath,
        "input_filename": "valid_list_of_zrl-season-15-race-5-rider-performance.json",
        "output_dirpath": output_dirpath,
        "output_filename": "valid_list_of_zrl-season-15-race-5-rider-performance.csv",
        "excel_column_shortlist": ["Region", "Category", "Team", "Rider", "Rank by Points", "Riders in Race","Finishing Position"],
        "excel_column_headers": {
            "Region": "GroovyRegion",
            "Category": "GroovyCategory",
            "Team": "GroovyTeam",
            "Rider": "GroovyRider",
            "Rank by Points": "GroovyRank by Points",
            "Riders in Race": "GroovyRiders in Race",
            "Finishing Position": "GroovyFinishing Position",
        },
    },
{
        "input_dirpath": input_dirpath,
        "input_filename": "valid_list_of_ZwiftPower-Profile.json",
        "output_dirpath": output_dirpath,
        "output_filename": "valid_list_of_ZwiftPower-Profile.csv",
        "excel_column_shortlist": ["zftp", "zmap", "vo2max", "cpBestEfforts", "relevantCpEfforts", "category","categoryWomen"],
        "excel_column_headers": {
            "zftp": "Groovyzftp",
            "zmap": "Groovyzmap",
            "vo2max": "Groovyvo2max",
            "cpBestEfforts": "GroovycpBestEfforts",
            "relevantCpEfforts": "GroovyrelevantCpEfforts",
            "category": "GroovyRiders in Race",
            "categoryWomen": "categoryWomen",
        },
    }
]

# Create output directory if it doesn't exist
os.makedirs(output_dirpath, exist_ok=True)

# Run test cases
for test_case in test_cases:
    try:
        read_json_write_pretty_csv(
            test_case["input_dirpath"],
            test_case["input_filename"],
            test_case["output_dirpath"],
            test_case["output_filename"],
            test_case["excel_column_shortlist"],
            test_case["excel_column_headers"],
        )
        print(f"Test passed for {test_case['input_filename']}")
    except Exception as e:
        print(f"Test failed for {test_case['input_filename']}: {e}")

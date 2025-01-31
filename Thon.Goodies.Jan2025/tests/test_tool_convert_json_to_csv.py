import os

# import sys
from typing import Any

from jgh_read_json_write_csv import read_json_write_csv_abridged

# Verify the import by printing a message
print(
    "\nfunction 'read_json_write_abridged_csv' imported successfully from module 'jgh_read_json_write_csv'\n"
)

# Define the absolute paths
input_dirpath: str = r"C:/Users/johng/holding_pen/Test_scratchpad/Tool.ConvertJsonToCsv.Dec2024/input"
output_dirpath: str =  r"C:/Users/johng/holding_pen/Test_scratchpad/Tool.ConvertJsonToCsv.Dec2024/output"


# Define the type for the test cases
TestCases: list[dict[str, Any]] = []

# Define multiple test cases. Some that should succeed and some that should fails. This mickey mouse excel serializer only handles flat files
# with no nested objects, or rather it can handle any file, but can only spit out first level fields)
# this means you probably need to do some pre-processing of the json file to flatten it out before you can use this tool
TestCases = [
    # {
    #     "input_dirpath": input_dirpath,
    #     "input_filename": "zrl-season-15-race-5-rider-performance.json", # This file should blow up outright. It has no first level objects 
    #     "output_dirpath": output_dirpath,
    #     "output_filename": "zrl-season-15-race-5-rider-performance.csv",
    #     "excel_column_shortlist": ["Region", "Team", "Rider", "Watts"],
    #     "excel_column_headers": {
    #         "Region": "REGION",
    #         "Team": "TEAM",
    #         "Rider": "NAME",
    #         "Watts": "POWER (W)",
    #     },
    # },
    {
        "input_dirpath": input_dirpath,
        "input_filename": "ZwiftPower-Profile.json", # This file should be OK. It has nested objects, but we are only interested in the first level fields
        "output_dirpath": output_dirpath,
        "output_filename": "ZwiftPower-Profile.csv",
        "excel_column_shortlist": [
            "zftp",
            "zmap",
            "weightInGrams",
            "metricsTimestamp",
        ],
        "excel_column_headers": {
            "zftp": "ZFTP",
            "zmap": "ZMAP",
            "weightInGrams": "Weight (g)",
            "metricsTimestamp": "Timestamp",
        },
    },
    # {
    #     "input_dirpath": input_dirpath,
    #     "input_filename": "Zwift-RiderProfiles.json",
    #     "output_dirpath": output_dirpath,
    #     "output_filename": "Zwift-RiderProfiles.csv",  # This file should be OK. It has nested objects, but we are only interested in the first level fields
    #     "excel_column_shortlist": [
    #         "firstName",
    #         "lastName",
    #         "age",
    #     ],
    #     "excel_column_headers": {
    #         "firstName": "First",
    #         "lastName": "Last",
    #         "age": "Years",
    #     },
    # },
]

# Create output directory if it doesn't exist
os.makedirs(output_dirpath, exist_ok=True)

# Run test cases
for test in TestCases:
    try:
        read_json_write_csv_abridged(test["input_dirpath"], test["input_filename"], test["output_dirpath"], test["output_filename"], test["excel_column_shortlist"], test["excel_column_headers"])
        print(f"\nConversion from JSON to CSV ran to completion for {test['input_filename']}\n")
    except Exception as e:
        print(f"\nConversion from JSON to CSV blew up for {test['input_filename']}:\n\t{e}\n")

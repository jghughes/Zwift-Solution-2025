import os

# import sys
from typing import Any

from jgh_read_json_write_csv import read_json_write_abridged_csv

# Verify the import by printing a message
print(
    "\nfunction 'read_json_write_abridged_csv' imported successfully from module 'jgh_read_json_write_csv'\n"
)

# Define the absolute paths
input_dirpath: str = r"C:/Users/johng/holding_pen/StuffForZsun/Tool.ConvertJsonToCsv.Dec2024_TestInput"
output_dirpath: str =  r"C:/Users/johng/holding_pen/StuffForZsun/Tool.ConvertJsonToCsv.Dec2024_TestOutputV2"


# Define the type for the test cases
TestCases: list[dict[str, Any]] = []

# Define multiple test cases for a coupe of files (this mickey mouse exccel serialiaser only handles flat files
# with no nested objects, or rather it can handle any file, but can only spit out first level fields)
# this means you probably need to do some pre-processing of the json file to flatten it out before you can use this tool
TestCases = [
    {
        "input_dirpath": input_dirpath,
        "input_filename": "zrl-season-15-race-5-rider-performance.json",
        "output_dirpath": output_dirpath,
        "output_filename": "zrl-season-15-race-5-rider-performance.csv",
        "excel_column_shortlist": ["Region", "Team", "Rider", "Watts"],
        "excel_column_headers": {
            "Region": "REGION",
            "Team": "TEAM",
            "Rider": "NAME",
            "Watts": "POWER (W)",
        },
    },
    {
        "input_dirpath": input_dirpath,
        "input_filename": "ZwiftPower-Profile.json",
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
    {
        "input_dirpath": input_dirpath,
        "input_filename": "Zwift-RiderProfiles.json",
        "output_dirpath": output_dirpath,
        "output_filename": "Zwift-RiderProfiles.csv",
        "excel_column_shortlist": [
            "firstName",
            "lastName",
            "age",
        ],
        "excel_column_headers": {
            "firstName": "First",
            "lastName": "Last",
            "age": "Years",
        },
    },
]

# Create output directory if it doesn't exist
os.makedirs(output_dirpath, exist_ok=True)

# Run test cases
for test in TestCases:
    try:
        read_json_write_abridged_csv(test["input_dirpath"], test["input_filename"], test["output_dirpath"], test["output_filename"], test["excel_column_shortlist"], test["excel_column_headers"])
        print(f"Test passed for {test['input_filename']}")
    except Exception as e:
        print(f"Test failed for {test['input_filename']}: {e}")

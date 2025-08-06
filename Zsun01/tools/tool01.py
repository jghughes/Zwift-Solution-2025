"""
This tool is used to add new properties to each rider in the zwiftrider_dictionary.json file. This was a one-off task. It does, however,
demonstrate how easy it is to read and write JSON files in Python, and how to modify existing properties in a JSON object.

The zwiftrider_dictionary.json file contains a collection of items. The format of the file is automatically interpreted by the deserializer to be a dictionary. Each key in the parent dictionary represents a rider, whose value is itself a dictionary of key-value pairs representing that rider, with keys such as 'name', 'id', 'wkg', etc.

The tool reads the JSON file, adds new key-value pairs to each rider dictionary, and writes the collection of modified rider dictionaries as JSON data back to a new file.

Deserialization (json.load) and serialization (json.dump) are used to read and write the JSON data. The dict.update() method is used to add new key-value pairs to each rider dictionary.

No DTO classes are needed or used in this simple tool.
"""
import json

# Load the JSON data from the file and deserialise it into a parent dictionary object
with open('C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/zwiftrider_dictionary.json', 'r') as file:
    dict_of_riders = json.load(file)

# Define the new key/value pairs to add to each rider_as_dict
additional_rider_dict_key_value_pairs = {
    "bp_5": 0,
    "bp_15": 0,
    "bp_30": 0,
    "cp_1_min": 0,
    "cp_2_min": 0,
    "cp_3_min": 0,
    "cp_5_min": 0,
    "cp_10_min": 0,
    "cp_12_min": 0,
    "cp_15_min": 0,
    "cp_20_min": 0,
    "cp_30_min": 0,
    "cp_40_min": 0
}

# Dynamically add the new key/value pairs to each rider_as_dict in the parent dict
for rider_as_dict in dict_of_riders.values():
    rider_as_dict.update(additional_rider_dict_key_value_pairs)

# Serialise the updated parent dict and write it as JSON data back to the file
with open('C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/zwiftrider_dictionary_v2.json', 'w') as file:
    json.dump(dict_of_riders, file, indent=4)

print("JSON file updated successfully.")

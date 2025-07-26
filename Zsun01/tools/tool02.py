"""
This tool is used to delete specific properties from each rider_as_dict in the zwiftrider_dictionary_v2.json file. It demonstrates how to read and write JSON files in Python, and how to remove selected properties from each rider_as_dict dictionary.

The zwiftrider_dictionary_v2.json file contains a dictionary where each key represents a rider_as_dict, and its value is itself a dictionary of key-value pairs representing that rider_as_dict, with keys such as 'name', 'id', 'wkg', etc.

The tool reads the JSON file, removes specified key-value pairs from each rider_as_dict dictionary, and writes the collection of modified rider_as_dict dictionaries as JSON dict_of_riders back to a new file.

Deserialization (json.load) and serialization (json.dump) are used to read and write the JSON dict_of_riders. The del statement is used to remove key-value pairs from each rider_as_dict dictionary.

No DTO classes are needed or used in this simple tool.
"""
import json

# Load the JSON dict_of_riders from the file
with open('C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/dict_of_riders/zwiftrider_dictionary_v2.json', 'r') as file:
    dict_of_riders = json.load(file)

# Define the keys to be deleted
rider_keys_to_delete = ["weight", "height", "gender", "ftp", "zwift_racing_score", "velo_rating"]

# Update each item in the JSON dict_of_riders
for rider_as_dict in dict_of_riders.values():
    for key in rider_keys_to_delete:
        if key in rider_as_dict:
            del rider_as_dict[key]

# Write the updated JSON dict_of_riders back to the file
with open('C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/dict_of_riders/zwiftrider_dictionary_v3.json', 'w') as file:
    json.dump(dict_of_riders, file, indent=4)

print("JSON file updated successfully.")

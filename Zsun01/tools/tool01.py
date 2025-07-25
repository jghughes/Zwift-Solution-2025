import json
# This tool is used to add new free-form entries to the zwiftrider_dictionary.json file. This was a one-off task. It does, however,
# demonstrate how easy it is to read and write JSON files in Python, and how to modify existing elements in a JSON file.
# The zwiftrider_dictionary.json file contains a dictionary of rider objects, each with properties such as 'name', 'id', 'wkg', etc.
# The tool reads the JSON file, adds new properties to each rider object, and writes the updated JSON data back to a new file.
# Deserialisation (json.load) and serialisation (json.dump) are used to read, modify, and write the JSON data. In Python, objects are dictionaries and properties can be added dynamically, so this is straightforward. Object.update() is used to add new properties to each rider object. 
# No DTO classes are needed or used in this simple tool.

# Load the JSON data from the file and deserialise it into a parent object
with open('C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/zwiftrider_dictionary.json', 'r') as file:
    parent_object = json.load(file)

# Define the new object properties/JSON elements to be added
list_of_new_property_kvp = {
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

# Dynamically add the new properties to each child object in the parent object
for child_object in parent_object.values():
    child_object.update(list_of_new_property_kvp)

# Serialise the updated parent object and write it as JSON data back to the file
with open('C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/zwiftrider_dictionary_v2.json', 'w') as file:
    json.dump(parent_object, file, indent=4)

print("JSON file updated successfully.")

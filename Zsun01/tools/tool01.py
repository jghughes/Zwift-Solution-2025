import json
# this tool is used to add new entries to the zwiftrider_dictionary.json file

# Load the JSON data from the file
with open('C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/zwiftrider_dictionary.json', 'r') as file:
    data = json.load(file)

# Define the new entries to be added
new_entries = {
    "cp_5": 0,
    "cp_15": 0,
    "cp_30": 0,
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

# Update each item in the JSON data
for rider in data.values():
    rider.update(new_entries)

# Write the updated JSON data back to the file
with open('C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/zwiftrider_dictionary_v2.json', 'w') as file:
    json.dump(data, file, indent=4)

print("JSON file updated successfully.")

import json

# Load the JSON data from the file
with open('C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/rider_data/rider_dictionary.json', 'r') as file:
    data = json.load(file)

# Define the new entries to be added
new_entries = {
    "cpw_5_sec": 0,
    "cpw_15_sec": 0,
    "cpw_30_sec": 0,
    "cpw_1_min": 0,
    "cpw_2_min": 0,
    "cpw_3_min": 0,
    "cpw_5_min": 0,
    "cpw_10_min": 0,
    "cpw_12_min": 0,
    "cpw_15_min": 0,
    "cpw_20_min": 0,
    "cpw_30_min": 0,
    "cpw_40_min": 0
}

# Update each item in the JSON data
for rider in data.values():
    rider.update(new_entries)

# Write the updated JSON data back to the file
with open('C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/rider_data/rider_dictionary_v2.json', 'w') as file:
    json.dump(data, file, indent=4)

print("JSON file updated successfully.")

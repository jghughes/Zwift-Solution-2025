import json

# Load the JSON data from the file
with open('C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/rider_data/rider_dictionary_v2.json', 'r') as file:
    data = json.load(file)

# Define the keys to be deleted
keys_to_delete = ["weight", "height", "gender", "ftp", "zwift_racing_score", "velo_rating"]

# Update each item in the JSON data
for rider in data.values():
    for key in keys_to_delete:
        if key in rider:
            del rider[key]

# Write the updated JSON data back to the file
with open('C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/rider_data/rider_dictionary_v3.json', 'w') as file:
    json.dump(data, file, indent=4)

print("JSON file updated successfully.")

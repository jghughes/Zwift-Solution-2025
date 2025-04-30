
import json

# File paths

file_name = "betel_cp_data.json"
dir_path = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"

# Load the JSON data
with open(dir_path + file_name, "r") as file:
    data = json.load(file)

# Modify the `zwiftid` field to be a string
for key, value in data.items():
    if "zwiftid" in value:
        value["zwiftid"] = str(value["zwiftid"])

# Save the modified JSON data
with open(dir_path + file_name, "w") as file:
    json.dump(data, file, indent=4)

print(f"Modified JSON saved to {file_name}")

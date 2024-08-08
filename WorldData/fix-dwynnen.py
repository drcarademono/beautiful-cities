import os
import json

def modify_json_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, 'r', errors='ignore') as file:
                    data = json.load(file)

                # Check if the file contains the Exterior > Buildings section
                if "Exterior" in data and "Buildings" in data["Exterior"]:
                    buildings = data["Exterior"]["Buildings"]

                    # Modify the entries with FactionId 414
                    for building in buildings:
                        if building.get("FactionId") == 414:
                            building["FactionId"] = 0
                            building["BuildingType"] = "House2"

                    # Save the modified JSON back to the file
                    with open(filepath, 'w') as file:
                        json.dump(data, file, indent=4)

            except json.JSONDecodeError as e:
                print(f"Skipping file {filename} due to JSON decode error: {e}")
            except Exception as e:
                print(f"An error occurred while processing file {filename}: {e}")

if __name__ == "__main__":
    modify_json_files(os.getcwd())


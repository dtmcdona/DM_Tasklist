import json
import os
from pathlib import Path

def clear_all_collections():
    base_dir = Path("").absolute()
    collection_dir = os.path.join(base_dir, "app", "core", "resources")
    for filename in os.listdir(collection_dir):
        if filename in ("action_collection.json", "task_collection.json", "schedule_collection.json"):
            dictionary = {}

            # Serializing json
            json_object = json.dumps(dictionary)
            file_path = os.path.join(collection_dir, filename)

            # Writing to sample.json
            with open(file_path, "w") as outfile:
                outfile.write(json_object)

clear_all_collections()
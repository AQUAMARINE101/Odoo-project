import json
import os

DATA_FILE = "fleetflow/data/fleet_data.json"

class FleetDataManager:
    def __init__(self):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        self.data = self._load_all_data()

    def _load_all_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                # Handle corrupted JSON file
                print(f"Warning: {DATA_FILE} is corrupted. Starting with empty data.")
                return {}
        return {}

    def save_all_data(self, data):
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def get_entity_data(self, entity_name, default_value=None):
        return self.data.get(entity_name, default_value if default_value is not None else {})

    def set_entity_data(self, entity_name, entity_data):
        self.data[entity_name] = entity_data
        self.save_all_data(self.data)


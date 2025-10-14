import json
from datetime import datetime
import os

class LocalStorage:
    def __init__(self, filename="sensor_data.json"):
        self.filename = filename
        self.latest_data = None  # store the last reading in memory

        # Create file if it doesn't exist
        if not os.path.exists(self.filename):
            with open(self.filename, "w") as f:
                pass

    def save_data(self, data):
        """Save sensor data to file and update memory cache."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        with open(self.filename, "a") as f:
            f.write(json.dumps(entry) + "\n")

        # update cache for real-time dashboard
        self.latest_data = data
        print(f"[Storage] Data saved locally: {entry}")

    def get_latest_data(self):
        """Return the most recent data for the dashboard."""
        # if cache exists, return immediately (fast)
        if self.latest_data:
            return self.latest_data

        # otherwise read the last saved line from file
        try:
            with open(self.filename, "r") as f:
                lines = f.readlines()
                if not lines:
                    return None
                last_entry = json.loads(lines[-1])
                return last_entry["data"]  # return the actual sensor data only
        except (FileNotFoundError, json.JSONDecodeError):
            return None

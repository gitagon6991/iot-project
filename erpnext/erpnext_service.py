import requests

class ERPNextService:
    def __init__(self, url="https://levelsensor.frappe.cloud", api_key="e1af3249c2323f1", api_secret="8e7c37095ec6df4"):
        self.url = url.rstrip("/")
        self.api_key = api_key
        self.api_secret = api_secret
        self.headers = {
            "Authorization": f"token {self.api_key}:{self.api_secret}",
            "Content-Type": "application/json"
        }
        self.doctype = "Sensor Reading"

        # Define possible field aliases across different sensors
        self.field_aliases = {
            "device_id": ["device_id", "sensor_id", "id", "dev_id"],
            "level": ["level", "level_m", "lvl", "depth", "distance"],
            "unit": ["unit", "units", "measurement_unit"],
            "battery_voltage": ["battery_voltage", "battery", "batt", "voltage", "vbat"],
            "signal_strength": ["signal_strength", "signal", "rssi", "sig"],
            "timestamp": ["timestamp", "time", "datetime"]
        }

    def find_value(self, data, possible_keys):
        """Return the first matching key's value in data."""
        for key in possible_keys:
            if key in data:
                return data[key]
        return None

    def push_to_erpnext(self, data):
        """Push sensor data into ERPNext (supports multiple sensor types)."""
        if not data or data.get("status") == "error":
            print("[ERPNext] Skipping push — invalid or missing sensor data.")
            return

        payload_data = data.get("data", data)

        # Build payload dynamically using alias matching
        payload = {
            "doctype": self.doctype,
            "device_id": self.find_value(payload_data, self.field_aliases["device_id"]),
            "level": self.find_value(payload_data, self.field_aliases["level"]),
            "unit": self.find_value(payload_data, self.field_aliases["unit"]),
            "battery_voltage": self.find_value(payload_data, self.field_aliases["battery_voltage"]),
            "signal_strength": self.find_value(payload_data, self.field_aliases["signal_strength"]),
            "timestamp": self.find_value(payload_data, self.field_aliases["timestamp"]),
        }

        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}

        try:
            response = requests.post(
                f"{self.url}/api/resource/{self.doctype}",
                json=payload,
                headers=self.headers,
                timeout=10
            )
            if response.status_code in (200, 201):
                print(f"[ERPNext] Data pushed: {payload}")
            else:
                print(f"[ERPNext] Push failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"[ERPNext] Error while pushing data: {e}")

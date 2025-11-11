import requests

class ERPNextService:
    def __init__(self, url="https://levelsensor.frappe.cloud", api_key="e1af3249c2323f1", api_secret="8e7c37095ec6df4"):
        # self.url = url
        self.url = url.rstrip("/")  # Clean URL
        self.api_key = api_key
        self.api_secret = api_secret
        self.headers = {
            "Authorization": f"token {self.api_key}:{self.api_secret}",
            "Content-Type": "application/json"
        }
        self.doctype = "Sensor Reading" 

    def push_to_erpnext(self, data):
        """
        Push Holykell V20 sensor data into ERPNext.
        The payload dynamically adapts to the fields present in the sensor output.
        """
        # Skip if connection or sensor failed
        if not data or data.get("status") == "error":
            print("[ERPNext] Skipping push — invalid or missing sensor data.")
            return

        # Extract nested data if present
        payload_data = data.get("data", data)

        # Holykell sensor keys (update based on your model/spec)
        payload = {
            "doctype": self.doctype,
            "device_id": payload_data.get("device_id"),
            "level": payload_data.get("level_m"),
            "unit": payload_data.get("unit"),
            "battery_voltage": payload_data.get("battery_voltage"),
            "signal_strength": payload_data.get("signal_strength"),
            "timestamp": payload_data.get("timestamp"),
        }

        # Remove any empty or None fields
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

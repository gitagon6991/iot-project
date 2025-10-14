import requests

class ERPNextService:
    def __init__(self, url="http://localhost:8000", api_key="your_api_key", api_secret="your_api_secret"):
        self.url = url
        self.api_key = api_key
        self.api_secret = api_secret
        self.headers = {
            "Authorization": f"token {self.api_key}:{self.api_secret}",
            "Content-Type": "application/json"
        }
        self.doctype = "Sensor Reading"  # Replace with your ERPNext Doctype

    def push_to_erpnext(self, data):
        """Push sensor data into ERPNext Doctype"""
        payload = {
            "doctype": self.doctype,
            "temperature": data["temperature"],
            "humidity": data["humidity"],
            "pressure": data["pressure"]
        }

        try:
            response = requests.post(
                f"{self.url}/api/resource/{self.doctype}",
                json=payload,
                headers=self.headers
            )
            if response.status_code == 200:
                print("[ERPNext] Data successfully pushed.")
            else:
                print(f"[ERPNext] Failed: {response.text}")
        except Exception as e:
            print(f"[ERPNext] Error: {e}")

import requests
import json

class CloudService:
    def __init__(self, endpoint="https://webhook.site/6c98dc3d-0bf8-4b9f-a9f3-3785833425cc"):
        self.endpoint = endpoint
        print(f"Cloud service initialized. Sending to {self.endpoint}")

    def upload_data(self, data):
        try:
            response = requests.post(
                self.endpoint,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            if response.status_code in (200, 201):
                print(f"[Cloud] Data uploaded successfully.")
            else:
                print(f"[Cloud] Upload failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"[Cloud] Cloud upload error: {e}")

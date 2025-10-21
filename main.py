from typing import Union
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sensor.sensor_reader import SensorReader
from storage.local_storage import LocalStorage
from cloud.cloud_service import CloudService
from erpnext.erpnext_service import ERPNextService
from ui.dashboard import Dashboard
import time
import threading
import datetime
import json

# Initialize FastAPI app
app = FastAPI(title="Holykell UE3001 Dashboard")

# Serve templates and static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize system components
sensor = SensorReader()
storage = LocalStorage()
cloud = CloudService()
erp = ERPNextService()
dashboard = Dashboard()

latest_data = {}

# ---------------- WEB ROUTES ---------------- #

@app.get("/", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Serve the live web dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/api/latest")
async def get_latest():
    """API endpoint the dashboard polls every few seconds"""
    return latest_data or {"message": "No data yet"}


@app.get("/latest-data")
def get_latest_data():
    """Keep compatibility with your old dashboard route"""
    latest = storage.get_latest_data() 
    return {"latest_data": latest or "No data yet"}

# ---------------- SYSTEM LOOP ---------------- #

def run_system_loop():
    """Continuously read, store, upload, and display sensor data."""
    global latest_data
    while True:
        data = sensor.read_data()
        print(f"[Sensor] Collected Data: {data}")

        # Save to local, cloud, ERPNext
        storage.save_data(data)
        cloud.upload_data(data)
        erp.push_to_erpnext(data)
        dashboard.display(data)

        # Update the live dashboard cache
        if data and "data" in data:
            latest_data = data["data"]
            latest_data["timestamp"] = datetime.datetime.now().isoformat()

        time.sleep(2)


# ---------------- ENTRY POINT ---------------- #

if __name__ == "__main__":
    system_thread = threading.Thread(target=run_system_loop, daemon=True)
    system_thread.start()

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

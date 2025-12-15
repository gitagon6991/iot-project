from typing import Union
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional

from sensor.sensor_reader import SensorReader
from storage.local_storage import LocalStorage
from cloud.cloud_service import CloudService
from erpnext.erpnext_service import ERPNextService
from sensor.theft_monitor import TheftMonitor
from ui.dashboard import Dashboard
import time
import threading
import datetime
import json
import random

# Initialize FastAPI app
app = FastAPI(title="Holykell Level Sensor Dashboard")

# Serve templates and static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize system components
sensor = SensorReader()
storage = LocalStorage()
cloud = CloudService()
erp = ERPNextService(
    url="your_erpnext_url",
    api_key="your_api_key",
    api_secret="your_api_sectret"
)
monitor = TheftMonitor(
    window_seconds=600,
    check_seconds=60,
    abs_drop_m=0.1,
    pct_drop=0.05,
    require_consecutive=1,
    smoothing_alpha=0.25
)

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
    """Keep compatibility with old dashboard route"""
    latest = storage.get_latest_data() 
    return {"latest_data": latest or "No data yet"}

@app.get("/api/history")
async def get_history():
    """API endpoint to retrieve full historical data from local storage."""
    # Assuming LocalStorage has a method called get_all_data() or get_recent_history(limit)
    history = storage.get_all_data() 
    return history

@app.get("/api/recent_history")
async def get_recent_history(limit: Optional[int] = 20):
    """API endpoint to retrieve a limited number of recent history points."""
    # Use the new method to get only the last 'limit' records
    history = storage.get_recent_history(limit=limit) 
    return history

# ---------------- SYSTEM LOOP ---------------- #

def run_system_loop():
    """Continuously read, store, upload, and display sensor data."""
    global latest_data

    # Mock sensor for testing
    level = 5.0  # starting level in meters (example full tank)
    decrease_rate = 0.05  # meters per cycle

    while True:
        # data = sensor.read_data()
        # Simulated data for demonstration purposes
        # In a real scenario, replace this with actual sensor reading logic --> data = sensor.read_data()
        # Gradually decrease with a bit of natural noise
        noise = random.uniform(-0.01, 0.01)
        level = max(0, level - decrease_rate + noise)

        # Test: auto refill when empty (like refilling a tank)
        if level <= 0.1:
            level = 5.0
        # Check for theft or significant drop
        alert = monitor.update(level)

        if alert: 
            # This ensures the dashboard's /api/latest receives the alert info
            latest_data["theft_alert"] = True
            latest_data["theft_info"] = alert

            print(f"[ALERT] Theft suspected! Details: {alert}")
            # Push alert to ERPNext
            erp.push_to_erpnext({
                "data": {
                    "device_id": "UE3001-Demo",
                    "level_m": level,
                    "timestamp": alert["detected_at"],
                    "theft_alert": True,
                    "theft_info": alert
                }
            })
            #Update dashboard and cloud
            dashboard.display({"alert": alert})
            cloud.upload_data({"alert": alert})

        else:
            # Important: Clear the alert status when the drop is over
            latest_data["theft_alert"] = False
            latest_data.pop("theft_info", None) # Remove the info key if present    

        # Build test data payload
        data = {
            "data": {
                "device_id": "UE3001-Demo",
                "level_m": round(level, 2),
                "unit": "m",
                "battery_voltage": round(random.uniform(12.0, 12.6), 2),
                "signal_strength": random.randint(80, 95),
                "timestamp": datetime.datetime.now().isoformat()
            }
        }

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

from typing import Union
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from sensor.sensor_reader import SensorReader
from storage.local_storage import LocalStorage
from cloud.cloud_service import CloudService
from erpnext.erpnext_service import ERPNextService
from ui.dashboard import Dashboard
import time
import threading

# Initialize FastAPI app
app = FastAPI()

# Initialize system components
sensor = SensorReader()
storage = LocalStorage()
cloud = CloudService()
erp = ERPNextService()
dashboard = Dashboard()

# FastAPI ROUTES

@app.get("/", response_class=HTMLResponse)
def dashboard_page():
    """Serve simple real-time dashboard HTML."""
    return """
    <html>
    <head>
        <title>Holykell-V20 Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                background-color: #f5f7fa;
                margin-top: 60px;
                color: #333;
            }
            h1 {
                color: #0078D7;
                margin-bottom: 20px;
            }
            #data {
                display: inline-block;
                background: #fff;
                padding: 25px 40px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                font-size: 18px;
            }
        </style>
    </head>
    <body>
        <h1>🌡 Wireless Smart Platform - Holykell V20</h1>
        <div id="data"><i>Loading sensor data...</i></div>
        <script>
        async function updateData() {
            let res = await fetch('/latest-data');
            let json = await res.json();
            let d = json.latest_data || {};
            document.getElementById('data').innerHTML = `
                <b>Temperature:</b> ${d.temperature ?? '-'} °C<br>
                <b>Humidity:</b> ${d.humidity ?? '-'} %<br>
                <b>Pressure:</b> ${d.pressure ?? '-'} hPa<br>
                <small>Updated: ${new Date().toLocaleTimeString()}</small>
            `;
        }
        setInterval(updateData, 2000);
        updateData();
        </script>
    </body>
    </html>
    """

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/latest-data")
def get_latest_data():
    """Fetch latest data from local storage or dashboard."""
    latest = storage.get_latest_data() 
    return {"latest_data": latest or "No data yet"}

# MAIN LOOP FUNCTION

def run_system_loop():
    """Continuously read, store, upload, and display sensor data."""
    while True:
        data = sensor.read_data()
        print(f"[Sensor] Collected Data: {data}")

        storage.save_data(data)
        cloud.upload_data(data)
        erp.push_to_erpnext(data)
        dashboard.display(data)

        time.sleep(2)


# ENTRY POINT 

if __name__ == "__main__":
    # Run background thread for continuous data collection
    system_thread = threading.Thread(target=run_system_loop, daemon=True)
    system_thread.start()

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

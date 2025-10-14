# 🌡 IoT Smart Sensor Dashboard (Holykell V20)

This project is a Python-based IoT system that connects to a **Holykell V20 Wireless Smart Platform** via **Modbus/TCP**, collects sensor readings, and displays them on a live **FastAPI web dashboard**.  

It also integrates with **ERPNext** for data synchronization and uses local storage as a backup when cloud or ERP connections are unavailable.

---

## ⚙️ Features

- Real-time data collection from Modbus/TCP/UDP sensors  
- Local data logging using JSON storage  
- REST API powered by FastAPI  
- Simple, clean web dashboard for live sensor display  
- ERPNext cloud integration for centralized data  
- Modular architecture (easy to extend with new sensors or protocols)

---

## 🧠 Tech Stack

- **Python 3.11+**
- **FastAPI** (for backend & dashboard)
- **pymodbus** (for Modbus/TCP communication)
- **uvicorn** (ASGI server)
- **ERPNext API** (for enterprise data push)
- **JSON file storage** (for offline caching)

---

## 🏗️ Project Structure

iot-project/
│
├── main.py # Main app entry (FastAPI + sensor loop)
├── sensor/
│ └── sensor_reader.py # Reads Modbus sensor data
├── storage/
│ └── local_storage.py # Local data storage
├── cloud/
│ └── cloud_service.py # Cloud data uploader (placeholder)
├── erpnext/
│ └── erpnext_service.py # ERPNext integration logic
└── ui/
└── dashboard.py # Web dashboard and visualization

---

## 🚀 Running Locally

```bash
# 1. Clone the repo
git clone https://github.com/gitagon6991/iot-project.git
cd iot-project

# 2. Create a virtual environment
python -m venv .venv
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the app
uvicorn main:app --reload

Then open: 👉 http://127.0.0.1:8000

🌍 Next Steps

Replace demo temperature/humidity data with real Modbus register mappings

Add geolocation mapping and alert system

Implement full ERPNext synchronization

🧑‍💻 Author

Anthony Njuguna (gitagon6991)
IoT & Automation Enthusiast
GitHub Profile: https://github.com/gitagon6991

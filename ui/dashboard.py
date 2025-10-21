class Dashboard:
    def __init__(self):
        print("[Dashboard] Initialized — ready to display Holykell UE3001 readings.")

    def display(self, data):
        """Display sensor readings in a clear console format."""
        # Handle nested data format (since sensor_reader returns {"data": {...}})
        if "data" in data:
            d = data["data"]
        else:
            d = data

        # Safely access fields
        device = d.get("device_id", "Unknown")
        level = d.get("level_m", "N/A")
        unit = d.get("unit", "")
        battery = d.get("battery_voltage", "N/A")
        signal = d.get("signal_strength", "N/A")
        timestamp = d.get("timestamp", "")

        print(f"""
[Dashboard] 📡 Holykell UE3001 Live Data
----------------------------------------
 Device ID       : {device}
 Level            : {level} {unit}
 Battery Voltage  : {battery} V
 Signal Strength  : {signal} %
 Timestamp        : {timestamp}
----------------------------------------
""")

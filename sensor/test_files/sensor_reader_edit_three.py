from pymodbus.client import ModbusTcpClient
from datetime import datetime

class SensorReader:
    def __init__(self, host="192.168.1.100", port=502, slave_id=1):
        """
        Initializes a Modbus TCP client to communicate with the Holykell UE3001.
        """
        self.client = ModbusTcpClient(host=host, port=port)
        self.slave_id = slave_id
        self.device_id = "UE3001"

        if not self.client.connect():
            print(f"[SensorReader] ⚠️ Could not connect to {host}:{port}")

    def read_data(self):
        """
        Reads the liquid level (in meters) from the Holykell UE3001 sensor via Modbus.
        The exact register address and scaling depend on the UE3001 Modbus table.
        """
        try:
            # --- This address should be adjusted based on Holykell’s register map ---
            # Eg: Register 0x0001 holds the level measurement
            rr = self.client.read_input_registers(self.slave_id, 1, 2)

            # Change read_input_registers() to read_holding_registers() if needed

            if rr.isError():
                return {"status": "error", "message": str(rr)}

            if not rr.registers:
                return {"status": "error", "message": "Empty register response"}

            # Example: interpret the first register as raw level (mm)
            raw_level = rr.registers[0]
            level_m = raw_level / 1000.0  # convert mm → m (adjust if different)

            # You can also read additional registers for temperature, voltage, etc.
            # For now we’ll just send level_m
            data = {
                "device_id": self.device_id,
                "level_m": level_m,
                "unit": "m",
                "battery_voltage": 12.5,   # placeholder 
                "signal_strength": 90,     # placeholder 
                "timestamp": datetime.now().isoformat()
            }

            print(f"[SensorReader] ✅ Level: {level_m:.3f} m (raw={raw_level})")
            return {"data": data}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def close(self):
        """Closes the Modbus connection."""
        self.client.close()


if __name__ == "__main__":
    reader = SensorReader()
    data = reader.read_data()
    print(data)
    reader.close()

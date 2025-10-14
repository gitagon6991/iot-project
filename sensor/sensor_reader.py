# sensor/sensor_reader.py
from pymodbus.client import ModbusTcpClient
import json

class SensorReader:
    def __init__(self, host="192.168.1.100", port=502):
        """Initialize connection to Holykell V20 gateway."""
        self.client = ModbusTcpClient(host=host, port=port)
        self.client.connect()

    def read_data(self):
        """Read data from the Holykell V20 Modbus registers."""
        try:
            # Example: reading first 10 holding registers
            rr = self.client.read_holding_registers(0, 10, unit=1)
            if rr.isError():
                return {"status": "error", "message": str(rr)}

            # Each Holykell V20 register mapping is in the spec:
            # You’ll adjust based on your document.
            data = {
                "device_id": rr.registers[0],
                "data_value": rr.registers[1] / 10.0,
                "unit": "kPa",  # change if needed
                "battery_voltage": rr.registers[2] / 100.0,
                "signal_strength": rr.registers[3],
            }
            return data
        except Exception as e:
            return {"status": "error", "message": str(e)}

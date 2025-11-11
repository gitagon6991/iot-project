from pymodbus.client import ModbusTcpClient
from datetime import datetime
import inspect

class SensorReader:
    def __init__(self, host="192.168.1.100", port=502, slave_id=1):
        """
        Initializes a Modbus TCP client to communicate with the Holykell UE3001.
        """
        self.client = ModbusTcpClient(host=host, port=port)
        self.slave_id = slave_id
        self.device_id = "UE3001"

        if not self.client.connect():
            print(f"[SensorReader] Could not connect to {host}:{port}")

        # Detect if 'unit' argument is supported (older pymodbus)
        self.supports_unit = "unit" in inspect.signature(self.client.read_input_registers).parameters
        print(f"[SensorReader] Using pymodbus method signature: {inspect.signature(self.client.read_input_registers)}")


    def read_data(self):
        """
        Reads the liquid level (in meters) from the Holykell UE3001 sensor via Modbus.
        # (not) Compatible with both pymodbus 2.x and 3.x versions.
        Updated for pymodbus 3.7+ which uses 'device_id' instead of 'unit' or 'slave'.
        """
        try:
            # rr = self.client.read_input_registers(1, 2, device_id=self.slave_id)
            rr = self.client.read_input_registers(address=1, count=2, device_id=self.slave_id)


            #if self.supports_unit:
                # Old pymodbus syntax
                # rr = self.client.read_input_registers(address=1, count=2, unit=self.slave_id)
            #else:
                # New pymodbus syntax (3.x+)
                # rr = self.client.read_input_registers(address=1, count=2, slave=self.slave_id)
                # rr = self.client.read_input_registers(1, 2, device_id=self.slave_id)


            if rr.isError():
                return {"status": "error", "message": str(rr)}

            if not rr.registers:
                return {"status": "error", "message": "Empty register response"}

            raw_level = rr.registers[0]
            level_m = raw_level / 1000.0  # mm → m

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

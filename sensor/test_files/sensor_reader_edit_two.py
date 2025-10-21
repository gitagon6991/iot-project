from pymodbus.client import ModbusTcpClient
from datetime import datetime

class SensorReader:
    def __init__(self, host="192.168.1.100", port=502, slave_id=1):
        self.client = ModbusTcpClient(host=host, port=port)
        self.slave_id = slave_id
        if not self.client.connect():
            print(f"[SensorReader] Warning: could not connect to {host}:{port}")

    def read_data(self):
        """Read level sensor data via Modbus registers."""
        try:
            # Try reading 4 registers starting at address 0
            rr = self.client.read_holding_registers(0, 4, slave=self.slave_id)
            if rr.isError():
                return {"status": "error", "message": str(rr)}

            regs = rr.registers  # list of ints
            if not regs:
                return {"status": "error", "message": "Empty register response"}

            # Interpret first register as level (in mm or 0.1mm units)
            level_raw = regs[0]
            level_meters = level_raw / 1000.0  # convert mm → meters (adjust scaling)

            data = {
                "device_id": self.slave_id,
                "level_m": level_meters,
                "raw_registers": regs,
                "timestamp": datetime.utcnow().isoformat()
            }

            return data

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def close(self):
        self.client.close()


if __name__ == "__main__":
    reader = SensorReader()
    data = reader.read_data()
    print(data)
    reader.close()

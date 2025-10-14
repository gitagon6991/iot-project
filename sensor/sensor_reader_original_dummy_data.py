import random

class SensorReader:
    def __init__(self):
        print("Sensor initialized (placeholder).")

    def read_data(self):
        # Placeholder values (simulate sensor output)
        return {
            "temperature": round(random.uniform(20, 30), 2),
            "humidity": round(random.uniform(40, 60), 2),
            "pressure": round(random.uniform(1000, 1025), 2)
        }

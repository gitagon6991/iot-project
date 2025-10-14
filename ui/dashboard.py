class Dashboard:
    def __init__(self):
        print("Dashboard initialized.")

    def display(self, data):
        print(f"[Dashboard] Live Data -> Temp: {data['temperature']}°C, "
              f"Humidity: {data['humidity']}%, Pressure: {data['pressure']} hPa")

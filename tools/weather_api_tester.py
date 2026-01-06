"""
Weather API Test App — Standalone PyQt6
Test OpenWeatherMap One Call API
"""

import sys
import requests
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit

API_KEY = "YOUR_API_KEY_HERE"  # Replace with your key
LAT = "40.7128"  # Example: New York
LON = "-74.0060"
UNITS = "imperial"  # metric for C

URL = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&units={UNITS}&appid={API_KEY}"

class WeatherTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weather API Test")
        self.setGeometry(100, 100, 600, 400)

        central = QWidget()
        layout = QVBoxLayout()

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Enter OpenWeatherMap API key")
        layout.addWidget(self.key_input)

        button = QPushButton("Fetch Weather")
        button.clicked.connect(self.fetch_weather)
        layout.addWidget(button)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        central.setLayout(layout)
        self.setCentralWidget(central)

    def fetch_weather(self):
        key = self.key_input.text().strip()
        if not key:
            self.output.setPlainText("Please enter API key")
            return

        try:
            response = requests.get(URL.replace("YOUR_API_KEY_HERE", key))
            response.raise_for_status()
            data = response.json()
            #self.output.setPlainText(json.dumps(data, indent=2))
        except Exception as e:
            self.output.setPlainText(f"Error: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WeatherTest()
    window.show()
    sys.exit(app.exec())
"""
weather_tile_test.py — Standalone Weather Tile Test
Version: v1.0.1
Uses WeatherAPI.com
"""

import sys
import requests
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QGridLayout
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPixmap

# === CONFIGURATION ===
API_KEY = "fff528869fbd42f69ec174849260601"
LOCATION = "Grass Valley, CA"
DAYS = 7

URL = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={LOCATION}&days={DAYS}&aqi=no&alerts=no"


class WeatherTile(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weather Tile Test — WeatherAPI.com")
        self.resize(800, 600)

        layout = QVBoxLayout(self)

        # Header
        header = QLabel("header")
        header.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #5294E2, stop:0.5 #3D6FB0, stop:1 #2B2B2B);
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
            padding: 20px;
            font-size: 20px;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title = QLabel("Weather")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout = QVBoxLayout(header)
        header_layout.addWidget(title)
        layout.addWidget(header)

        # Last updated (new)
        self.last_updated_label = QLabel("Last updated: Never")
        self.last_updated_label.setStyleSheet("font-size: 14px; color: #BBBBBB; padding-left: 20px;")
        self.last_updated_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.last_updated_label)

        # Current weather
        current = QWidget()
        current_layout = QGridLayout(current)
        current_layout.setSpacing(20)
        current_layout.setContentsMargins(20, 0, 20, 20)

        self.current_icon = QLabel()
        self.current_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.current_temp = QLabel("--°")
        self.current_temp.setStyleSheet("font-size: 48px; font-weight: bold;")
        self.current_temp.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.current_desc = QLabel("Loading...")
        self.current_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)

        current_layout.addWidget(self.current_icon, 0, 0, 2, 1)
        current_layout.addWidget(self.current_temp, 0, 1)
        current_layout.addWidget(self.current_desc, 1, 1)

        layout.addWidget(current)

        # Forecast grid
        self.forecast_grid = QGridLayout()
        self.forecast_grid.setSpacing(20)
        forecast_widget = QWidget()
        forecast_widget.setLayout(self.forecast_grid)
        layout.addWidget(forecast_widget)

        # Timer for polling
        self.timer = QTimer()
        self.timer.timeout.connect(self.fetch_weather)
        self.timer.start(900000)  # 15 minutes
        self.fetch_weather()  # Initial fetch

    def fetch_weather(self):
        try:
            response = requests.get(URL, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Update last updated
            now = datetime.now().strftime("%b %d %H:%M")
            self.last_updated_label.setText(f"Last updated: {now}")

            self.update_current(data["current"], data["location"])
            self.update_forecast(data["forecast"]["forecastday"])
        except Exception as e:
            self.current_desc.setText(f"Error: {e}")
            self.last_updated_label.setText(f"Last updated: Failed")

    def update_current(self, current, location):
        temp = current["temp_f"]
        feels = current["feelslike_f"]
        desc = current["condition"]["text"]
        self.current_temp.setText(f"{temp:.0f}°F")
        self.current_desc.setText(f"{desc}\nFeels like {feels:.0f}°F in {location['name']}")

        icon_url = "https:" + current["condition"]["icon"]
        icon_data = requests.get(icon_url).content
        pixmap = QPixmap()
        pixmap.loadFromData(icon_data)
        self.current_icon.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))

    def update_forecast(self, days):
        # Clear previous
        for i in reversed(range(self.forecast_grid.count())):
            widget = self.forecast_grid.takeAt(i).widget()
            if widget:
                widget.deleteLater()

        for i, day in enumerate(days):
            date = datetime.fromtimestamp(day["date_epoch"]).strftime("%a")
            high = day["day"]["maxtemp_f"]
            low = day["day"]["mintemp_f"]
            desc = day["day"]["condition"]["text"]
            icon_url = "https:" + day["day"]["condition"]["icon"]

            label = QLabel(f"{date}\n{high:.0f}° / {low:.0f}°\n{desc}")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("font-size: 14px;")

            icon_data = requests.get(icon_url).content
            pixmap = QPixmap()
            pixmap.loadFromData(icon_data)
            icon = QLabel()
            icon.setPixmap(pixmap.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio))
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.forecast_grid.addWidget(icon, 0, i)
            self.forecast_grid.addWidget(label, 1, i)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    tile = WeatherTile()
    tile.show()
    sys.exit(app.exec())
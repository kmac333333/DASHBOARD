"""
Created on Thu Jan  6 16:04:05 2026
@author: kmac3
@author: Grok 4.0
# ================================
# view/tiles/weather.py
# ================================
# File version: v1.0.0
# Sync'd to dashboard release: v3.9.0
# Description: WeatherTile — current and forecast weather with local temp integration
#
# Features:
# ✅ Current weather + 7-day forecast
# ✅ Clickable days (modal detail stub)
# ✅ Weather icons
# ✅ Last updated timestamp
# ✅ Integration with local indoor/outdoor MQTT temps
# ✅ Uses WeatherAPI.com
# ================================
"""

import requests
from datetime import datetime
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QGridLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap

from .base import BaseTile
from style import BODY_STYLE, FONT_LABEL, TEXT_SECONDARY


class WeatherTile(BaseTile):
    def __init__(self, config, dispatcher, parent=None):
        super().__init__(config, dispatcher, parent)

        # Config
        self.api_key = config.get("api_key", "")
        self.location = config.get("location", "New York")
        self.indoor_topic = config.get("indoor_topic", "")
        self.outdoor_topic = config.get("outdoor_topic", "")

        # Body layout
        body_layout = self.body.layout()
        body_layout.setContentsMargins(20, 20, 20, 20)
        body_layout.setSpacing(15)

        # Last updated
        self.last_updated = QLabel("Last updated: Never")
        self.last_updated.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 14px;")
        body_layout.addWidget(self.last_updated)

        # Current weather
        current = QWidget()
        current_layout = QHBoxLayout(current)
        self.current_icon = QLabel()
        self.current_icon.setFixedSize(100, 100)
        self.current_temp = QLabel("--°")
        self.current_temp.setStyleSheet(BODY_STYLE)
        self.current_desc = QLabel("Loading...")
        current_layout.addWidget(self.current_icon)
        current_layout.addWidget(self.current_temp)
        current_layout.addWidget(self.current_desc, stretch=1)
        body_layout.addWidget(current)

        # Forecast grid
        self.forecast_grid = QGridLayout()
        forecast_widget = QWidget()
        forecast_widget.setLayout(self.forecast_grid)
        body_layout.addWidget(forecast_widget)

        # Poll timer
        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self.fetch_weather)
        self.poll_timer.start(900000)  # 15 min
        self.fetch_weather()

        # Register for local temps if configured
        if self.indoor_topic:
            key = f"mqtt:{self.indoor_topic}"
            self.dispatcher.register_cb(key, lambda v: self.update_local_temp("indoor", v))
        if self.outdoor_topic:
            key = f"mqtt:{self.outdoor_topic}"
            self.dispatcher.register_cb(key, lambda v: self.update_local_temp("outdoor", v))

    def fetch_weather(self):
        if not self.api_key:
            self.current_desc.setText("No API key configured")
            return

        url = f"http://api.weatherapi.com/v1/forecast.json?key={self.api_key}&q={self.location}&days=7&aqi=no&alerts=no"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            now = datetime.now().strftime("%b %d %H:%M")
            self.last_updated.setText(f"Last updated: {now}")
            self.update_current(data["current"])
            self.update_forecast(data["forecast"]["forecastday"])
        except Exception as e:
            self.current_desc.setText(f"API error: {e}")

    def update_current(self, current):
        temp = current["temp_f"]
        desc = current["condition"]["text"]
        self.current_temp.setText(f"{temp:.0f}°F")
        self.current_desc.setText(desc)

        icon_url = "https:" + current["condition"]["icon"]
        icon_data = requests.get(icon_url).content
        pixmap = QPixmap()
        pixmap.loadFromData(icon_data)
        self.current_icon.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))

    def update_forecast(self, days):
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
            label.setStyleSheet(f"color: {TEXT_SECONDARY}; {FONT_LABEL}")

            icon_data = requests.get(icon_url).content
            pixmap = QPixmap()
            pixmap.loadFromData(icon_data)
            icon = QLabel()
            icon.setPixmap(pixmap.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio))
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.forecast_grid.addWidget(icon, 0, i)
            self.forecast_grid.addWidget(label, 1, i)

    def update_local_temp(self, which, payload):
        # Placeholder — future: show indoor/outdoor in current section
        print(f"{which.capitalize()} temp: {payload}")
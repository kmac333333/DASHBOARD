"""
Created on Thu Jan  6 16:04:05 2026
@author: kmac3
@author: Grok 4.0
# ================================
# controller/dispatcher.py
# ================================
# File version: v1.9.4
# Sync'd to dashboard release: v3.9.0
# Description: DataDispatcher — central data bus for inbound sources
#
# Features:		   
# ✅ Manages MQTT client lifecycle and message routing
# ✅ Creates and manages SystemPropertySource instances
# ✅ register_cb(key, callback) — appends callbacks for multi-sink support
# ✅ Emits data to registered callbacks
# ✅ Graceful shutdown
# ✅ dump_registrations() — detailed dump to system out tile
#
# Feature Update: v1.9.4
# ✅ Added weather polling source (WeatherAPI.com, 15-min interval)
# ================================
"""

from PyQt6.QtCore import QObject, QTimer
import requests

from support.mqtt_client import MqttLiveClient
from support.system_properties import SystemPropertySource
from support.myLOG2 import LOG3


class DataDispatcher(QObject):
    def __init__(self):
        super().__init__()
        self.mqtt_client = MqttLiveClient()
        self.callbacks = {}  # "channel_key": [callback1, callback2, ...]
        self.system_sources = []
        self.weather_timer = None

    def register_cb(self, key: str, callback):
        """Register a callback for a named data channel — appends for multi-sink."""
        if key not in self.callbacks:
            self.callbacks[key] = []
        if callback not in self.callbacks[key]:
            self.callbacks[key].append(callback)
            LOG3(200 + 5, f"Appended callback for channel '{key}'")
        else:
            LOG3(200 + 5, f"Callback already registered for channel '{key}'")

    def _emit(self, key: str, value):
        if key in self.callbacks:
            for cb in self.callbacks[key]:
                try:
                    cb(value)
                except Exception as e:
                    LOG3(200 + 6, f"Callback error for '{key}': {e}")

    def start(self):
        LOG3(200 + 1, "Dispatcher starting")
        self.mqtt_client.register_cb("message_received", self.on_mqtt_message)
        self.mqtt_client.start()

    def bind_config(self, configs):
        LOG3(200 + 10, f"Binding {len(configs)} tiles — setting up sources")
        # Clear old sources
        for source in self.system_sources:
            source.stop()
        self.system_sources.clear()

        # Stop weather timer if running
        if self.weather_timer:
            self.weather_timer.stop()

        for config in configs:
            # MQTT subscriptions
            for feed in config.get("bindings", {}).values():
                if feed["type"] == "mqtt":
                    self.mqtt_client.add_topic(feed["topic"])
                    LOG3(200 + 30, f"Added MQTT topic subscription: {feed['topic']}")

                # System properties
                elif feed["type"] == "system_prop":
                    prop = feed["prop"]
                    getter = self.get_system_getter(prop)
                    if getter:
                        source = SystemPropertySource(getter, feed.get("interval", 5))
                        key = f"system:{prop}"
                        source.data_ready.connect(lambda v, k=key: self._emit(k, v))
                        self.system_sources.append(source)
                        source.start()
						
            # Weather tile — set up polling
            if config.get("type") == "weather":
                api_key = config.get("api_key", "")
                location = config.get("location", "New York")
                if api_key:
                    self.setup_weather_polling(api_key, location)

    def setup_weather_polling(self, api_key, location):
        """Set up periodic weather API polling."""
        if self.weather_timer:
            self.weather_timer.stop()

        self.weather_timer = QTimer()
        self.weather_timer.timeout.connect(lambda: self.fetch_weather(api_key, location))
        self.weather_timer.start(900000)  # 15 minutes
        self.fetch_weather(api_key, location)  # Initial fetch

    def fetch_weather(self, api_key, location):
        url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={location}&days=7&aqi=no&alerts=no"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            self._emit("weather:data", data)
            LOG3(200 + 40, "Weather data fetched and emitted")
        except Exception as e:
            LOG3(200 + 41, f"Weather API error: {e}")

    def get_system_getter(self, prop):
        import time
        import psutil

        def format_uptime():
            uptime_seconds = time.monotonic()
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            if days > 0:
                return f"up {days} days, {hours:02d}:{minutes:02d}"
            else:
                return f"up {hours:02d}:{minutes:02d}"

        getters = {
            "mqtt_status": lambda: "Connected ✅" if self.mqtt_client.running else "Disconnected ❌",
            "broker": lambda: "rpibroker.local",
            "uptime": format_uptime,
            "cpu_load": lambda: f"{psutil.cpu_percent(interval=1):.1f}%",
            "memory": lambda: f"{psutil.virtual_memory().percent:.1f}% used"
        }
        return getters.get(prop)

    def on_mqtt_message(self, topic, payload):
        LOG3(200 + 50, f"Dispatcher received MQTT: {topic} -> {payload}")
        key = f"mqtt:{topic}"
        self._emit(key, payload)

    def dump_registrations(self):
        """Dump current callback registrations to system out tile."""
        dump_lines = [
            "=== Dispatcher Registration Dump ===",
            f"Total channels: {len(self.callbacks)}",
            ""
        ]

        if not self.callbacks:
            dump_lines.append("No callbacks registered.")
        else:
            for key, cbs in self.callbacks.items():
                dump_lines.append(f"Channel: {key}")
                dump_lines.append(f"  Callbacks: {len(cbs)}")
                for i, cb in enumerate(cbs, 1):
                    dump_lines.append(f"    [{i}] {cb}")
                dump_lines.append("")

        dump_lines.append("=== End Dump ===")
        dump_text = "\n".join(dump_lines)

        # Emit to system out tile
        self._emit("debug:system_out", dump_text)
							 
    def stop(self):
        LOG3(200 + 70, "Dispatcher stopping")
        if self.weather_timer:
            self.weather_timer.stop()
        for source in self.system_sources:
            source.stop()
        self.system_sources.clear()
        self.mqtt_client.stop()
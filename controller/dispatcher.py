"""
Created on Thu Jan  1 16:04:05 2026
@author: kmac3
@author: Grok 4.0
# ================================
# controller/dispatcher.py
# ================================
# File version: v1.6.0
# Sync'd to dashboard release: v3.6.16
# Description: DataDispatcher — central data bus for inbound sources
#
# Features:
# ✅ Manages MQTT client lifecycle and message routing
# ✅ Creates and manages SystemPropertySource instances
# ✅ register_cb(key, callback) for sink registration
# ✅ Emits data to registered callbacks
# ✅ Graceful shutdown
#
# Feature Update: v1.6.0
# ✅ Fixed MQTT formatting — dispatcher applies format string and emits ready text
# ================================
"""

from PyQt6.QtCore import QObject

from support.mqtt_client import MqttLiveClient
from support.system_properties import SystemPropertySource
from support.myLOG2 import LOG3


class DataDispatcher(QObject):
    def __init__(self):
        super().__init__()
        self.mqtt_client = MqttLiveClient()
        self.callbacks = {}
        self.system_sources = []

    def register_cb(self, key: str, callback):
        if key not in self.callbacks:
            self.callbacks[key] = []
        self.callbacks[key].append(callback)
        LOG3(200 + 5, f"Registered callback for channel '{key}'")

    def _emit(self, key: str, value: str):
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

    def bind_config(self, tile_widgets, configs):
        LOG3(200 + 10, f"Binding {len(configs)} tiles")
        for config in configs:
            tile = tile_widgets[config["id"]]

            for signal_name, feed in config.get("bindings", {}).items():
                if feed["type"] == "static":
                    pass

                elif feed["type"] == "mqtt":
                    topic = feed["topic"]
                    format_str = feed.get("format", "{}")
                    key = f"mqtt:{topic}"
                    # Register callback that applies format in dispatcher
                    callback = lambda payload, fmt=format_str: self._apply_mqtt_format(payload, fmt, key)
                    self.register_cb(key, callback)
                    self.mqtt_client.add_topic(topic)
                    LOG3(200 + 30, f"Added MQTT topic subscription: {topic}")

                elif feed["type"] == "system_prop":
                    prop = feed["prop"]
                    getter = self.get_system_getter(prop)
                    if getter:
                        source = SystemPropertySource(getter, feed.get("interval", 5))
                        if hasattr(tile, "value_labels"):
                            try:
                                line_num = int(signal_name.replace("line", ""))
                                if 1 <= line_num <= 5:
                                    source.data_ready.connect(tile.value_labels[line_num - 1].setText)
                            except ValueError:
                                pass
                        self.system_sources.append(source)
                        source.start()

    def _apply_mqtt_format(self, payload: str, format_str: str, key: str):
        try:
            fahrenheit = float(payload)
            celsius = (fahrenheit - 32) * 5 / 9
            formatted = format_str.format(fahrenheit, celsius)
        except ValueError:
            formatted = payload
        self._emit(key, formatted)

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
        self._emit(key, payload)  # Raw payload — formatting done in callback

    def stop(self):
        LOG3(200 + 70, "Dispatcher stopping")
        for source in self.system_sources:
            source.stop()
        self.mqtt_client.stop()
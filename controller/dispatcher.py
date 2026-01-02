"""
Created on Thu Jan  1 16:04:05 2026
@author: kmac3
@author: Grok 4.0
# ================================
# controller/dispatcher.py
# ================================
# File version: v1.9.2
# Sync'd to dashboard release: v3.8.6
# Description: DataDispatcher — central data bus for inbound sources
#
# Features:
# ✅ Manages MQTT client lifecycle and message routing
# ✅ Creates and manages SystemPropertySource instances
# ✅ register_cb(key, callback) — replaces existing callback for key
# ✅ Emits data to registered callbacks
# ✅ Graceful shutdown
#
# Feature Update: v1.9.2
# ✅ Fixed MQTT message flow — ensured registration in start()
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
        was_registered = key in self.callbacks
        self.callbacks[key] = [callback]
        if was_registered:
            LOG3(200 + 5, f"Replaced callback for channel '{key}'")
        else:
            LOG3(200 + 5, f"Registered callback for channel '{key}'")

    def _emit(self, key: str, value):
        if key in self.callbacks:
            for cb in self.callbacks[key]:
                try:
                    cb(value)
                except Exception as e:
                    LOG3(200 + 6, f"Callback error for '{key}': {e}")

    def start(self):
        LOG3(200 + 1, "Dispatcher starting")
        # Critical: register dispatcher for MQTT messages
        self.mqtt_client.register_cb("message_received", self.on_mqtt_message)
        LOG3(200 + 2, "Registered on_mqtt_message callback with MqttLiveClient")
        self.mqtt_client.start()

    def bind_config(self, configs):
        LOG3(200 + 10, f"Binding {len(configs)} tiles — setting up sources")
        # Clear old sources
        for source in self.system_sources:
            source.stop()
        self.system_sources.clear()

        for config in configs:
            for feed in config.get("bindings", {}).values():
                if feed["type"] == "mqtt":
                    self.mqtt_client.add_topic(feed["topic"])
                    LOG3(200 + 30, f"Added MQTT topic subscription: {feed['topic']}")

                elif feed["type"] == "system_prop":
                    prop = feed["prop"]
                    getter = self.get_system_getter(prop)
                    if getter:
                        source = SystemPropertySource(getter, feed.get("interval", 5))
                        key = f"system:{prop}"
                        source.data_ready.connect(lambda v, k=key: self._emit(k, v))
                        self.system_sources.append(source)
                        source.start()

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

    def stop(self):
        LOG3(200 + 70, "Dispatcher stopping")
        for source in self.system_sources:
            source.stop()
        self.system_sources.clear()
        self.mqtt_client.stop()
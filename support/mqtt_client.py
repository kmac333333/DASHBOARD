"""
Created on Thu Jan  1 16:04:05 2026
@author: kmac3
@author: Grok 4.0
# ================================
# support/mqtt_client.py
# ================================
# File version: v1.0.1
# Sync'd to dashboard release: v3.5.0-alpha
# Description: MqttLiveClient — robust, reconnecting MQTT client with signal-table pattern
#
# Features:
# ✅ Persistent connection with exponential backoff retry
# ✅ Automatic subscription to collected topics on connect
# ✅ Thread-safe operation (runs in daemon thread)
# ✅ Emits SIG_message_received(topic, payload) via signal_table
# ✅ Supports register_cb("message_received", callback)
# ✅ Graceful stop and disconnect
# ✅ Comprehensive LOG3 logging for connection and message events
# ================================
"""

import time
import threading
import paho.mqtt.client as mqtt

from PyQt6.QtCore import QObject, pyqtSignal

from support.myLOG2 import LOG3


class MqttLiveClient(QObject):
    SIG_message_received = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.broker = "rpibroker.local"
        self.port = 1883
        self.client = None
        self.running = False
        self.topics = set()

        self.signal_table = {
            "message_received": self.SIG_message_received
        }

    def register_cb(self, signal_name: str, callback):
        if signal_name in self.signal_table:
            self.signal_table[signal_name].connect(callback)
            return True
        LOG3(100 + 1, f"Warning: Unknown MQTT client signal '{signal_name}'")
        return False

    def add_topic(self, topic: str):
        """Add a topic to subscribe to on next connection."""
        self.topics.add(topic)

    def start(self):
        if self.running:
            return
        self.running = True
        LOG3(100 + 2, "Starting MQTT client thread")
        threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        self.running = False
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
        LOG3(100 + 3, "MQTT client stopped")

    def _run(self):
        def on_connect(client, userdata, flags, rc, properties=None):
            if rc == 0:
                LOG3(100 + 10, f"MQTT Connected to {self.broker}")
                for topic in self.topics:
                    client.subscribe(topic)
                    LOG3(100 + 12, f"Subscribed to {topic}")
            else:
                LOG3(100 + 11, f"MQTT connection failed: rc={rc}")

        def on_message(client, userdata, msg):
            try:
                payload = msg.payload.decode().strip()
                if payload:
                    LOG3(100 + 20, f"MQTT message: {msg.topic} -> {payload}")
                    self.SIG_message_received.emit(msg.topic, payload)
            except Exception as e:
                LOG3(100 + 21, f"MQTT message error: {e}")

        self.client = mqtt.Client(protocol=mqtt.MQTTv5)
        self.client.on_connect = on_connect
        self.client.on_message = on_message

        retry_delay = 2
        while self.running:
            try:
                self.client.connect(self.broker, self.port)
                self.client.loop_forever()
                break
            except Exception as e:
                LOG3(100 + 30, f"Connection attempt failed: {e}")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 30)
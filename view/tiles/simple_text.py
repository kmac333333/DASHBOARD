"""
Created on Thu Jan  4 16:04:05 2026
@author: kmac3
@author: Grok 4.0
# ================================
# view/tiles/simple_text.py
# ================================
# File version: v1.1.2
# Sync'd to dashboard release: v3.9.0
# Description: SimpleTextTile — single-value display tile with header
#
# Features:
# ✅ Displays a single value in large centered text
# ✅ Gradient header imported from style.py
# ✅ All text styling imported from style.py
# ✅ Registers MQTT callback with dispatcher for live updates
# ✅ Static initial value support
# ✅ Title editable via click		   
#
# Feature Update: v1.1.1
# ✅ Added self-naming with objectName() for debug hierarchy dump
# Feature Update: v1.1.2
# ✅ All styling now imported from style.py (HEADER_STYLE_LINE_1, HEADER_STYLE_LINE_2, BODY_STYLE)
# ✅ Now uses body container from BaseTile (consistent architecture)
# ================================
"""

from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QInputDialog
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QCursor

from support.myLOG2 import LOG3
from .base import BaseTile
from style import (
    BODY_STYLE
)

class SimpleTextTile(BaseTile):
    def __init__(self, config, dispatcher, parent=None):
        super().__init__(config, dispatcher, parent)

        body_layout = self.body.layout()
        body_layout.setSpacing(12)

        self.body_label = QLabel("—")
        self.body_label.setObjectName(f"body-{self.tile_id}")
        self.body_label.setWordWrap(True)
        self.body_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.body_label.setStyleSheet(BODY_STYLE)

        # Add to body container from BaseTile
        body_layout.addWidget(self.body_label)

        # Register MQTT callback if bound
        bindings = config.get("bindings", {})
        value_binding = bindings.get("value", {})
        if value_binding.get("type") == "mqtt":
            topic = value_binding["topic"]
            key = f"mqtt:{topic}"
            format_str = value_binding.get("format", "{}")
            def mqtt_callback(payload):
                try:
                    fahrenheit = float(payload)
                    celsius = (fahrenheit - 32) * 5 / 9
                    formatted = format_str.format(fahrenheit, celsius)
                except ValueError:
                    formatted = payload
                self.body_label.setText(formatted)
            self.dispatcher.register_cb(key, mqtt_callback)
            LOG3(400 + 30, f"SimpleTextTile registered for MQTT key: {key}")	
            
        # Static value (initial display)
        if value_binding.get("type") == "static":
            self.body_label.setText(value_binding.get("value", "—"))


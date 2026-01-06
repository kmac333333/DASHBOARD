"""
Created on Thu Jan  4 16:04:05 2026
@author: kmac3
@author: Grok 4.0
# ================================
# view/tiles/dual_text.py
# ================================
# File version: v1.0.3
# Sync'd to dashboard release: v3.9.0
# Description: DualTextTile — dual-value display tile with header
#
# Features:
# ✅ Displays two values (primary larger, secondary smaller)
# ✅ Programmable labels (e.g., "Indoor", "Outdoor")
# ✅ Value-based color (blue cold, green normal, red hot)
# ✅ Gradient header with dynamic hex ID from last field of MQTT topic
# ✅ All styling imported from style.py
# ✅ Self-naming with objectName() for debug hierarchy dump
#
# Feature Update: v1.0.2
# ✅ Added objectName() naming for tile, header, labels, values
# Feature Update: v1.0.3
# ✅ Refactored to use unified BaseTile (header handled in base)
# ✅ Only body content remains here
# ================================
"""

from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QInputDialog
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QCursor

from support.myLOG2 import LOG3
from .base import BaseTile
from style import (
    TEXT_SECONDARY,
    TEXT_PRIMARY,
    FONT_LABEL,
    FONT_VALUE,

)
	 


class DualTextTile(BaseTile):
    def __init__(self, config, dispatcher, parent=None):
        super().__init__(config, dispatcher, parent)

        # Body — dual displays
        body_layout = self.body.layout()
        body_layout.setSpacing(12)

        bindings = config.get("bindings", {})
        primary_binding = bindings.get("primary", {})
        secondary_binding = bindings.get("secondary", {})

        # Primary display
        primary_h_layout = QHBoxLayout()
        primary_h_layout.setSpacing(10)

        primary_label_text = primary_binding.get("label", "Primary")
        primary_label = QLabel(primary_label_text + ":")
        primary_label.setObjectName(f"label-{self.tile_id}-primary")
        primary_label.setStyleSheet(f"color: {TEXT_SECONDARY}; {FONT_LABEL}")
        primary_h_layout.addWidget(primary_label)

        self.primary_value = QLabel("—")
        self.primary_value.setObjectName(f"value-{self.tile_id}-primary")
        self.primary_value.setStyleSheet(f"color: {TEXT_PRIMARY}; {FONT_VALUE}")
        self.primary_value.setWordWrap(True)
        primary_h_layout.addWidget(self.primary_value, stretch=1)

        body_layout.addLayout(primary_h_layout)

        # Secondary display
        secondary_h_layout = QHBoxLayout()
        secondary_h_layout.setSpacing(10)

        secondary_label_text = secondary_binding.get("label", "Secondary")
        secondary_label = QLabel(secondary_label_text + ":")
        secondary_label.setObjectName(f"label-{self.tile_id}-secondary")
        secondary_label.setStyleSheet(f"color: {TEXT_SECONDARY}; {FONT_LABEL}")
        secondary_h_layout.addWidget(secondary_label)

        self.secondary_value = QLabel("—")
        self.secondary_value.setObjectName(f"value-{self.tile_id}-secondary")
        self.secondary_value.setStyleSheet(f"color: {TEXT_PRIMARY}; {FONT_VALUE}")
        self.secondary_value.setWordWrap(True)
        secondary_h_layout.addWidget(self.secondary_value, stretch=1)

        body_layout.addLayout(secondary_h_layout)

        body_layout.addStretch()

        # Register callbacks for primary and secondary subscriptions
        if primary_binding.get("type") == "mqtt":
            topic = primary_binding["topic"]
            key = f"mqtt:{topic}"
            format_str = primary_binding.get("format", "{}")
            def primary_callback(payload):
                try:
                    fahrenheit = float(payload)
                    celsius = (fahrenheit - 32) * 5 / 9
                    formatted = format_str.format(fahrenheit, celsius)
                    color = self.get_color(fahrenheit)
                    self.primary_value.setStyleSheet(f"color: {color}; {FONT_VALUE}")
                    self.primary_value.setText(formatted)
                    # Update hex ID from last field of topic
                    hex_id = topic.split("/")[-1]
                    self.hex_id_label.setText(hex_id)
                except ValueError:
                    self.primary_value.setText(payload)
            self.dispatcher.register_cb(key, primary_callback)

        if secondary_binding.get("type") == "mqtt":
            topic = secondary_binding["topic"]
            key = f"mqtt:{topic}"
            format_str = secondary_binding.get("format", "{}")
            def secondary_callback(payload):
                try:
                    fahrenheit = float(payload)
                    celsius = (fahrenheit - 32) * 5 / 9
                    formatted = format_str.format(fahrenheit, celsius)
                    color = self.get_color(fahrenheit)
                    self.secondary_value.setStyleSheet(f"color: {color}; {FONT_VALUE}")
                    self.secondary_value.setText(formatted)
                    # Update hex ID from last field of topic (use secondary if primary not available)
                    hex_id = topic.split("/")[-1]
                    self.hex_id_label.setText(hex_id)
                except ValueError:
                    self.secondary_value.setText(payload)
            self.dispatcher.register_cb(key, secondary_callback)

    def get_color(self, value):
        """Simple value-based coloring (blue cold, green normal, red hot)."""
        if value < 50:
            return "#3b82f6"  # Blue
        elif value < 80:
            return "#22c55e"  # Green
        else:
            return "#ef4444"  # Red

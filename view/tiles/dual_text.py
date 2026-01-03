"""
Created on Thu Jan  3 16:04:05 2026
@author: kmac3
@author: Grok 4.0
# ================================
# view/tiles/dual_text.py
# ================================
# File version: v1.0.1
# Sync'd to dashboard release: v3.7.1
# Description: DualTextTile — dual-value display tile with header
#
# Features:
# ✅ Displays two values (primary larger, secondary smaller)
# ✅ Programmable labels (e.g., "Indoor", "Outdoor")
# ✅ Value-based color (blue cold, green normal, red hot)
# ✅ Gradient header with dynamic hex ID from last field of MQTT topic
# ✅ All styling imported from style.py
#
# Feature Update: v1.0.1
# ✅ Hex ID now extracted from last field of MQTT topic
# ================================
"""

from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QInputDialog
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QCursor

from support.myLOG2 import LOG3
from .base import BaseTile
from style import (
    HEADER_GRADIENT, 
    TEXT_HEADER, 
    TEXT_SUBTITLE, 
    TEXT_PRIMARY, 
    TEXT_SECONDARY, 
    FONT_HEX_ID,                 
    FONT_LABEL, 
    FONT_TITLE, 
    FONT_VALUE, 
    FONT_BODY
)
			  


class DualTextTile(BaseTile):
    def __init__(self, config, dispatcher, parent=None):
        super().__init__(parent)
        self.config = config
        self.dispatcher = dispatcher
        self.height_tiles = config["size"][0]
        self.width_tiles = config["size"][1]

        self.setMinimumSize(QSize(self.width_tiles * 160, self.height_tiles * 160))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header — gradient from style.py
        header_container = QWidget()
        header_container.setFixedHeight(90)
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(20, 8, 20, 8)
        header_layout.setSpacing(10)

        header_container.setStyleSheet(HEADER_GRADIENT)

        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setSpacing(0)
        title_layout.setContentsMargins(0, 0, 0, 0)

        self.hex_id_label = QLabel("—")  # Will be updated from topic
        self.hex_id_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.hex_id_label.setStyleSheet(f"color: {TEXT_HEADER}; {FONT_HEX_ID}")

        self.title_label = QLabel(config["title"])
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        self.title_label.setStyleSheet(f"color: {TEXT_SUBTITLE}; {FONT_TITLE}")
        self.title_label.setWordWrap(False)
        self.title_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.title_label.mousePressEvent = self.edit_title
        self.title_label.setContentsMargins(5, 0, 0, 0)

        title_layout.addWidget(self.hex_id_label)
        title_layout.addWidget(self.title_label)

        header_layout.addWidget(title_container, stretch=1)

        layout.addWidget(header_container)

        # Body — dual displays
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(20, 20, 20, 20)
        body_layout.setSpacing(12)

        bindings = config.get("bindings", {})
        primary_binding = bindings.get("primary", {})
        secondary_binding = bindings.get("secondary", {})

        # Primary display
        primary_h_layout = QHBoxLayout()
        primary_h_layout.setSpacing(10)

        primary_label_text = primary_binding.get("label", "Primary")
        primary_label = QLabel(primary_label_text + ":")
        primary_label.setStyleSheet(f"color: {TEXT_SECONDARY}; {FONT_LABEL}")
        primary_h_layout.addWidget(primary_label)

        self.primary_value = QLabel("—")
        self.primary_value.setStyleSheet(f"color: {TEXT_PRIMARY}; {FONT_BODY}")
        self.primary_value.setWordWrap(True)
        primary_h_layout.addWidget(self.primary_value, stretch=1)

        body_layout.addLayout(primary_h_layout)

        # Secondary display
        secondary_h_layout = QHBoxLayout()
        secondary_h_layout.setSpacing(10)

        secondary_label_text = secondary_binding.get("label", "Secondary")
        secondary_label = QLabel(secondary_label_text + ":")
        secondary_label.setStyleSheet(f"color: {TEXT_SECONDARY}; {FONT_LABEL}")
        secondary_h_layout.addWidget(secondary_label)

        self.secondary_value = QLabel("—")
        self.secondary_value.setStyleSheet(f"color: {TEXT_PRIMARY}; {FONT_VALUE}")
        self.secondary_value.setWordWrap(True)
        secondary_h_layout.addWidget(self.secondary_value, stretch=1)

        body_layout.addLayout(secondary_h_layout)

        body_layout.addStretch()
        layout.addWidget(body, stretch=1)

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
                    self.primary_value.setStyleSheet(f"color: {color}; {FONT_BODY}")
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
                    # Update hex ID from last field of topic (use primary if secondary not available)
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

    def edit_title(self, event):
        new_title, ok = QInputDialog.getText(self, "Edit Title", "Title:", text=self.config["title"])
        if ok:
            self.config["title"] = new_title
            self.title_label.setText(new_title)
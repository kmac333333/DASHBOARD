"""
Created on Thu Jan  4 16:04:05 2026
@author: kmac3
@author: Grok 4.0
# ================================
# view/tiles/simple_text.py
# ================================
# File version: v1.1.1
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
# ================================
"""

from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QInputDialog
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QCursor

from support.myLOG2 import LOG3
from .base import BaseTile
from style import (
    BODY_STYLE,
    HEADER_STYLE_LINE_1, HEADER_STYLE_LINE_2,
    TEXT_SUBTITLE,
    TEXT_PRIMARY,
    FONT_TITLE,
    FONT_BODY,
    HEADER_GRADIENT
)


class SimpleTextTile(BaseTile):
    def __init__(self, config, dispatcher, parent=None):
        super().__init__(parent)
        self.config = config
        self.dispatcher = dispatcher
        self.tile_id = config["id"]
        self.height_tiles = config["size"][0]
        self.width_tiles = config["size"][1]
        self.update_geometry()
        # Self-naming for hierarchy dump
        self.setObjectName(f"tile-{self.tile_id}")
        #
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        # Header
        header_container = QWidget()
        header_container.setObjectName(f"header-{self.tile_id}")
        header_container.setFixedHeight(90)
        header_container.setStyleSheet(HEADER_GRADIENT)
        #
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(20, 8, 20, 8)
        header_layout.setSpacing(10)
        #
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setSpacing(0)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        self.hex_id_label = QLabel(config["hex_id"])
        self.hex_id_label.setObjectName(f"hex-{self.tile_id}")
        self.hex_id_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.hex_id_label.setStyleSheet(HEADER_STYLE_LINE_1)

        self.title_label = QLabel(config["title"])
        self.title_label.setObjectName(f"title-{self.tile_id}")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        self.title_label.setStyleSheet(HEADER_STYLE_LINE_2)
        self.title_label.setWordWrap(False)
        self.title_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.title_label.mousePressEvent = self.edit_title
        self.title_label.setContentsMargins(5, 0, 0, 0)

        title_layout.addWidget(self.hex_id_label)
        title_layout.addWidget(self.title_label)

        header_layout.addWidget(title_container, stretch=1)

        layout.addWidget(header_container)

        self.body_label = QLabel("—")
        self.body_label.setObjectName(f"body-{self.tile_id}")
        self.body_label.setWordWrap(True)
        self.body_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.body_label.setStyleSheet(BODY_STYLE)

        layout.addWidget(self.body_label, stretch=1)

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

    def edit_title(self, event):
        new_title, ok = QInputDialog.getText(self, "Edit Title", "Title:", text=self.config["title"])
        if ok:
            self.config["title"] = new_title
            self.title_label.setText(new_title)
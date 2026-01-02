"""
Created on Thu Jan  1 16:04:05 2026
@author: kmac3
@author: Grok 4.0
# ================================
# view/tiles/simple_text.py
# ================================
# File version: v1.0.6
# Sync'd to dashboard release: v3.6.17
# Description: SimpleTextTile — single-value display tile with header
#
# Features:
# ✅ Displays a single value in large centered text
# ✅ Gradient header with hex ID and editable title
# ✅ Inherits unified styling from DashboardView (no local styling)
# ✅ Supports "value" signal via dispatcher callback registration
# ✅ Title editable via click
#
# Feature Update: v1.0.6
# ✅ Fixed MQTT formatting — converts payload to float before applying format
# ================================
"""

from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QInputDialog
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QCursor

from support.myLOG2 import LOG3
from .base import BaseTile


class SimpleTextTile(BaseTile):
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

        # Header
        header_container = QWidget()
        header_container.setFixedHeight(90)
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(20, 8, 20, 8)
        header_layout.setSpacing(10)

        header_container.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #6366f1,
                                        stop:0.85 #4f46e5,
                                        stop:1 #1e293b);
        """)

        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setSpacing(0)
        title_layout.setContentsMargins(0, 0, 0, 0)

        self.hex_id_label = QLabel(config["hex_id"])
        self.hex_id_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.hex_id_label.setStyleSheet("color: white; font-size: 40px; font-weight: bold;")

        self.title_label = QLabel(config["title"])
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        self.title_label.setStyleSheet("color: rgba(255, 255, 255, 180); font-size: 20px;")
        self.title_label.setWordWrap(False)
        self.title_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.title_label.mousePressEvent = self.edit_title
        self.title_label.setContentsMargins(5, 0, 0, 0)

        title_layout.addWidget(self.hex_id_label)
        title_layout.addWidget(self.title_label)

        header_layout.addWidget(title_container, stretch=1)

        layout.addWidget(header_container)

        self.body_label = QLabel("—")
        self.body_label.setWordWrap(True)
        self.body_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.body_label.setStyleSheet("color: #e2e8f0; padding: 30px; font-size: 48px; font-weight: bold;")

        layout.addWidget(self.body_label, stretch=1)

        # Register MQTT callback if present
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
                    formatted = payload  # Fallback
                self.body_label.setText(formatted)
            self.dispatcher.register_cb(key, mqtt_callback)

        # Static value (initial display)
        if value_binding.get("type") == "static":
            self.body_label.setText(value_binding.get("value", "—"))

    def edit_title(self, event):
        new_title, ok = QInputDialog.getText(self, "Edit Title", "Title:", text=self.config["title"])
        if ok:
            self.config["title"] = new_title
            self.title_label.setText(new_title)
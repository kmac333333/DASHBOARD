"""
Created on Thu Jan  3 16:04:05 2026
@author: kmac3
@author: Grok 4.0
# ================================
# view/tiles/system_out.py
# ================================
# File version: v1.0.2
# Sync'd to dashboard release: v3.8.6
# Description: SystemOutTile — scrollable console-style tile for debug/system output
#
# Features:
# ✅ Multiline text display with scroll
# ✅ Auto-scroll to bottom on new content
# ✅ Registers with dispatcher for "debug:system_out" channel
# ✅ Append-only output (console-like)
# ✅ Monospace font for readability
# ✅ All styling imported from style.py
#
# Feature Update: v1.0.2
# ✅ Added timestamp prefix to each line
# ✅ Improved readability with monospace and padding
# ================================
"""

from PyQt6.QtWidgets import QVBoxLayout, QTextEdit, QWidget, QLabel
from PyQt6.QtCore import Qt, QDateTime

from support.myLOG2 import LOG3
from .base import BaseTile
from style import HEADER_GRADIENT, TEXT_HEADER, TEXT_SUBTITLE, FONT_HEX_ID, FONT_TITLE


class SystemOutTile(BaseTile):
    def __init__(self, config, dispatcher, parent=None):
        super().__init__(parent)
        self.config = config
        self.dispatcher = dispatcher
        self.height_tiles = config["size"][0]
        self.width_tiles = config["size"][1]

        self.setMinimumSize(self.width_tiles * 160, self.height_tiles * 160)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header_container = QWidget()
        header_container.setFixedHeight(90)
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(20, 8, 20, 8)
        header_layout.setSpacing(10)

        header_container.setStyleSheet(HEADER_GRADIENT)

        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setSpacing(0)
        title_layout.setContentsMargins(0, 0, 0, 0)

        self.hex_id_label = QLabel("DEBUG")
        self.hex_id_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.hex_id_label.setStyleSheet(f"color: {TEXT_HEADER}; {FONT_HEX_ID}")

        self.title_label = QLabel(config.get("title", "System Out"))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        self.title_label.setStyleSheet(f"color: {TEXT_SUBTITLE}; {FONT_TITLE}")
        self.title_label.setWordWrap(False)

        title_layout.addWidget(self.hex_id_label)
        title_layout.addWidget(self.title_label)

        header_layout.addWidget(title_container)

        layout.addWidget(header_container)

        # Body — scrollable text output
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("""
            background-color: #1e1e1e;
            color: #d4d4d4;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            padding: 10px;
        """)
        self.text_edit.setPlainText("System output ready...\n")

        layout.addWidget(self.text_edit, stretch=1)

        # Register for debug output
        key = "debug:system_out"
        def output_callback(message: str):
            timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
            formatted = f"[{timestamp}] {message}"
            self.append_output(formatted)
        self.dispatcher.register_cb(key, output_callback)

    def append_output(self, message: str):
        """Append message with timestamp and auto-scroll."""
        self.text_edit.append(message)
        self.text_edit.ensureCursorVisible()
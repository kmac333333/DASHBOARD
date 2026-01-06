"""
Created on Thu Jan  4 16:04:05 2026
@author: kmac3
@author: Grok 4.0
# ================================
# view/tiles/system_out.py
# ================================
# File version: v1.0.4
# Sync'd to dashboard release: v3.9.0
# Description: SystemOutTile — scrollable console-style tile for debug/system output
#
# Features:
# ✅ Multiline text display with scroll
# ✅ Auto-scroll to bottom on new content
# ✅ Registers with dispatcher for "debug:system_out" channel
# ✅ Append-only output (console-like)
# ✅ Monospace font for readability
# ✅ All styling imported from style.py
# ✅ Self-naming with objectName() for debug hierarchy dump
#
# Feature Update: v1.0.3
# ✅ Added objectName() naming for tile, header, console
# Feature Update: v1.0.4
# ✅ Refactored to use unified BaseTile (header in base, only body content here)													 
# ================================
"""

from PyQt6.QtWidgets import QVBoxLayout, QTextEdit, QWidget, QLabel
from PyQt6.QtCore import Qt

from support.myLOG2 import LOG3
from .base import BaseTile
from style import (
    BODY_STYLE,
    HEADER_STYLE_LINE_1, HEADER_STYLE_LINE_2,
    TEXT_HEADER, TEXT_SUBTITLE, 
    FONT_HEX_ID, FONT_TITLE,
    HEADER_GRADIENT
 )


class SystemOutTile(BaseTile):
    def __init__(self, config, dispatcher, parent=None):
        super().__init__(config, dispatcher, parent)

        # Body — scrollable text output
        body_layout = self.body.layout()
        body_layout.setContentsMargins(10, 10, 10, 10)
        self.text_edit = QTextEdit()
        self.text_edit.setObjectName(f"console-{self.tile_id}")
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("""
            background-color: #1e1e1e;
            color: #d4d4d4;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            padding: 10px;
        """)
        self.text_edit.setPlainText("System output ready...\n")

        body_layout.addWidget(self.text_edit, stretch=1)

        # Register for debug output
        key = "debug:system_out"
        def output_callback(message: str):
																		
												  
            self.append_output(message)
        self.dispatcher.register_cb(key, output_callback)

    def append_output(self, message: str):
        """Append message and auto-scroll to bottom."""
        self.text_edit.append(message)
        self.text_edit.ensureCursorVisible()
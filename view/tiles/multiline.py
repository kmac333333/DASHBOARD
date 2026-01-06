"""
Created on Thu Jan  4 16:04:05 2026
@author: kmac3
@author: Grok 4.0
# ================================
# view/tiles/multiline.py
# ================================
# File version: v1.1.6
# Sync'd to dashboard release: v3.9.0
# Description: MultilineTile — sink tile for up to 5 lines of labeled data
#
# Features:
# ✅ Supports 5 lines with auto-generated labels from bound prop
# ✅ Label + value layout with spacing and alignment
# ✅ Gradient header imported from style.py
# ✅ All text styling imported from style.py
# ✅ Inherits unified styling from DashboardView
# ✅ Title editable via click
# ✅ Registers callbacks with dispatcher for data updates (sink pattern)
# ✅ Self-naming with objectName() for debug hierarchy dump
#
# Feature Update: v1.1.5
# ✅ Added objectName() for tile, header, labels, values (debug readability)
# Feature Update: v1.1.6
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
    TEXT_SECONDARY, TEXT_PRIMARY,
    FONT_LABEL, FONT_VALUE
)


class MultilineTile(BaseTile):
    def __init__(self, config, dispatcher, parent=None):
        super().__init__(config, dispatcher, parent)
        
        # Body — 5 lines with label:value
        body_layout = self.body.layout()
        body_layout.setSpacing(12)

        self.value_labels = []

        bindings = config.get("bindings", {})
        props = [bindings.get(f"line{i}", {}).get("prop", "") for i in range(1, 6)]

        for i in range(5):
            h_layout = QHBoxLayout()
            h_layout.setSpacing(10)

            prop = props[i]
            label_text = prop.replace("_", " ").title() if prop else f"Line {i+1}"
            label = QLabel(label_text + ":")
            label.setObjectName(f"label-{self.tile_id}-line{i+1}")
            label.setStyleSheet(f"color: {TEXT_SECONDARY}; {FONT_LABEL}")
            h_layout.addWidget(label)

            value = QLabel("—")
            value.setObjectName(f"value-{self.tile_id}-line{i+1}")
            value.setStyleSheet(f"color: {TEXT_PRIMARY}; {FONT_VALUE}")
            value.setWordWrap(True)
            h_layout.addWidget(value, stretch=1)

            body_layout.addLayout(h_layout)
            self.value_labels.append(value)

        body_layout.addStretch()

        # Register callbacks with dispatcher
        for line_num in range(1, 6):
            prop = props[line_num - 1]
            if prop:
                key = f"system:{prop}"
                callback = lambda v, idx=line_num - 1: self.value_labels[idx].setText(v)
                self.dispatcher.register_cb(key, callback)


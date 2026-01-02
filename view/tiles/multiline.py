"""
Created on Thu Jan  1 16:04:05 2026
@author: kmac3
@author: Grok 4.0
# ================================
# view/tiles/multiline.py
# ================================
# File version: v1.1.2
# Sync'd to dashboard release: v3.7.1
# Description: MultilineTile — sink tile for up to 5 lines of labeled data
#
# Features:
# ✅ Supports 5 lines with auto-generated labels from bound prop
# ✅ Label + value layout with spacing and alignment
# ✅ Gradient header with hex ID and editable title
# ✅ Inherits styling from DashboardView
# ✅ Title editable via click
# ✅ Registers callbacks with dispatcher for data updates (sink pattern)
#
# Feature Update: v1.1.2
# ✅ Fixed version bump and minor cleanup
# ================================
"""

from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QInputDialog
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QCursor

from support.myLOG2 import LOG3
from .base import BaseTile


class MultilineTile(BaseTile):
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

        # Body
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(20, 20, 20, 20)
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
            label.setStyleSheet("color: #94a3b8; font-size: 20px; font-weight: bold;")
            h_layout.addWidget(label)

            value = QLabel("—")
            value.setStyleSheet("color: #e2e8f0; font-size: 22px;")
            value.setWordWrap(True)
            h_layout.addWidget(value, stretch=1)

            body_layout.addLayout(h_layout)
            self.value_labels.append(value)

        body_layout.addStretch()
        layout.addWidget(body, stretch=1)

        # Register callbacks with dispatcher
        for line_num in range(1, 6):
            prop = props[line_num - 1]
            if prop:
                key = f"system:{prop}"
                callback = lambda v, idx=line_num - 1: self.value_labels[idx].setText(v)
                self.dispatcher.register_cb(key, callback)

    def edit_title(self, event):
        new_title, ok = QInputDialog.getText(self, "Edit Title", "Title:", text=self.config["title"])
        if ok:
            self.config["title"] = new_title
            self.title_label.setText(new_title)
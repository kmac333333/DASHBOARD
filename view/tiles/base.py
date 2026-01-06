"""
Created on Thu Jan  5 16:04:05 2026
@author: kmac3
@author: Grok 4.0
# ================================
# view/tiles/base.py
# ================================
# File version: v1.0.3
# Sync'd to dashboard release: v3.9.0
# Description: BaseTile — common header and initialization for all tiles
#
# Feature Update: v1.0.3
# ✅ Moved header (container, hex_id, title) into BaseTile
# ================================
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QInputDialog
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QCursor

from style import (
    HEADER_GRADIENT, 
    HEADER_STYLE_LINE_1, HEADER_STYLE_LINE_2, BODY_STYLE
)

class BaseTile(QWidget):
    def __init__(self, config, dispatcher, parent=None):
        super().__init__(parent)
        self.config = config
        self.dispatcher = dispatcher
        self.tile_id = config["id"]
        self.height_tiles = config["size"][0]
        self.width_tiles = config["size"][1]

        # Naming and styling
        self.setObjectName(f"tile-{self.tile_id}")
        #self.setStyleSheet(UNIFIED_TILE_STYLE)
        self.setMinimumSize(QSize(self.width_tiles * 160, self.height_tiles * 160))

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header — common to all tiles
        self.header_container = QWidget()
        self.header_container.setObjectName(f"header-{self.tile_id}")
        self.header_container.setFixedHeight(90)
        header_layout = QHBoxLayout(self.header_container)
        header_layout.setContentsMargins(20, 8, 20, 8)
        header_layout.setSpacing(10)

        self.header_container.setStyleSheet(HEADER_GRADIENT)

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

        title_layout.addWidget(self.hex_id_label)
        title_layout.addWidget(self.title_label)

        header_layout.addWidget(title_container, stretch=1)

        layout.addWidget(self.header_container)

        # Body placeholder — concrete tiles add their body here
        self.body = QWidget()
        self.body.setObjectName(f"body-{self.tile_id}")
        self.body.setStyleSheet(BODY_STYLE)
        body_layout = QVBoxLayout(self.body)
        body_layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(self.body, stretch=1)

    def edit_title(self, event):
        new_title, ok = QInputDialog.getText(self, "Edit Title", "Title:", text=self.config["title"])
        if ok:
            self.config["title"] = new_title
            self.title_label.setText(new_title)
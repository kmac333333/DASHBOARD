"""
Created on Thu Jan  1 16:04:05 2026
@author: kmac3
@author: Grok 4.0
# ================================
# view/dashboard_view.py
# ================================
# File version: v1.1.3
# Sync'd to dashboard release: v3.6.10
# Description: DashboardView — manages tile layout and unified styling
#
# Features:
# ✅ Centralized unified styling for all tiles (background, border, hover)
# ✅ Scrollable grid layout with automatic tile placement
# ✅ Tile factory for easy extension of new tile types
# ✅ Safe loading and clearing of tiles from configuration
# ✅ Responsive row stretching for clean bottom alignment
#
# Feature Update: v1.1.3
# ✅ Tile factory now passes dispatcher to all tiles (required for MQTT sinks)
# ================================
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QGridLayout
from PyQt6.QtCore import QSize

from support.myLOG2 import LOG3
from view.tiles.simple_text import SimpleTextTile
from view.tiles.multiline import MultilineTile


# Tile factory — pass dispatcher to all tiles
def create_tile(config, dispatcher):
    tile_type = config.get("type", "simple_text")
    if tile_type == "simple_text":
        return SimpleTextTile(config, dispatcher)
    elif tile_type == "multiline":
        return MultilineTile(config, dispatcher)
    else:
        LOG3(400 + 50, f"Unknown tile type: {tile_type} — falling back to simple_text")
        return SimpleTextTile(config, dispatcher)


class DashboardView(QWidget):
    def __init__(self, dispatcher):
        super().__init__()
        self.dispatcher = dispatcher
        self.setStyleSheet("""
            background-color: #0f172a;

            SimpleTextTile, MultilineTile {
                background: #1e293b;
                border-radius: 18px;
                border: 1px solid #334155;
            }
            SimpleTextTile:hover, MultilineTile:hover {
                border: 1px solid #6366f1;
                background: #232e41;
            }
        """)
        self.tiles = {}

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        layout.addWidget(self.scroll_area)

        self.container = QWidget()
        self.grid = QGridLayout(self.container)
        self.grid.setSpacing(30)
        self.grid.setContentsMargins(30, 30, 30, 30)
        self.scroll_area.setWidget(self.container)

    def load_config(self, configs):
        LOG3(400 + 1, f"Loading {len(configs)} tiles")
        self._clear_layout()
        self.tiles.clear()

        for config in configs:
            tile = create_tile(config, self.dispatcher)
            self.tiles[config["id"]] = tile

        self._layout_tiles()

    def _clear_layout(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item and item.widget():
                item.widget().setParent(None)
                item.widget().deleteLater()

    def _layout_tiles(self):
        self._clear_layout()
        occupied = []
        max_rows = 0

        for tile in self.tiles.values():
            h = tile.height_tiles
            w = tile.width_tiles
            placed = False
            r = 0
            while not placed:
                while len(occupied) < r + h:
                    occupied.append([False] * 8)
                for c in range(8 - w + 1):
                    if all(
                        not occupied[r + dr][c + dc]
                        for dr in range(h)
                        for dc in range(w)
                    ):
                        self.grid.addWidget(tile, r, c, h, w)
                        for dr in range(h):
                            for dc in range(w):
                                occupied[r + dr][c + dc] = True
                        placed = True
                        max_rows = max(max_rows, r + h)
                        break
                if not placed:
                    r += 1

        self.grid.setRowStretch(max_rows, 1)
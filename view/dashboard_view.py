"""
Created on Thu Jan  3 16:04:05 2026
@author: kmac3
@author: Grok 4.0
# ================================
# view/dashboard_view.py
# ================================
# File version: v1.3.3
# Sync'd to dashboard release: v3.8.7
# Description: DashboardView — manages tile layout and unified styling
#
# Features:
# ✅ Centralized unified styling for all tiles (imported from style.py)
# ✅ Scrollable grid layout with automatic tile placement
# ✅ Tile factory for easy extension of new tile types
# ✅ Safe loading and clearing of tiles from configuration
# ✅ Responsive row stretching for clean bottom alignment
# ✅ Handles external layout change prompt from controller
#
# Feature Update: v1.3.3
# ✅ Added support for 'system_out' tile type in factory
# ================================
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QGridLayout, QMessageBox
from PyQt6.QtCore import QSize

from support.myLOG2 import LOG3
from view.tiles.simple_text import SimpleTextTile
from view.tiles.multiline import MultilineTile
from view.tiles.dual_text import DualTextTile
from view.tiles.system_out import SystemOutTile  # ← New import
from config import load_config
from style import DASHBOARD_STYLE, UNIFIED_TILE_STYLE, SCROLL_AREA_STYLE


# Tile factory — now supports system_out
def create_tile(config, dispatcher):
    tile_type = config.get("type", "simple_text")
    if tile_type == "simple_text":
        return SimpleTextTile(config, dispatcher)
    elif tile_type == "multiline":
        return MultilineTile(config, dispatcher)
    elif tile_type == "dual_text":
        return DualTextTile(config, dispatcher)
    elif tile_type == "system_out":
        return SystemOutTile(config, dispatcher)
    else:
        LOG3(400 + 50, f"Unknown tile type: {tile_type} — falling back to simple_text")
        return SimpleTextTile(config, dispatcher)


class DashboardView(QWidget):
    def __init__(self, dispatcher):
        super().__init__()
        self.dispatcher = dispatcher

        # All styling from style.py
        self.setStyleSheet(DASHBOARD_STYLE + UNIFIED_TILE_STYLE)

        self.tiles = {}

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(SCROLL_AREA_STYLE)
        layout.addWidget(self.scroll_area)

        self.container = QWidget()
        self.grid = QGridLayout(self.container)
        self.grid.setSpacing(30)
        self.grid.setContentsMargins(30, 30, 30, 30)
        self.scroll_area.setWidget(self.container)

    def on_external_layout_change(self):
        """Called by controller when external change detected."""
        LOG3(400 + 61, "External layout change detected — prompting user")
        reply = QMessageBox.question(
            self,
            "Layout Changed",
            "The layout file has been modified externally.\n\nReload layout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        if reply == QMessageBox.StandardButton.Yes:
            LOG3(400 + 62, "User confirmed reload — rebinding tiles")
            new_config = load_config()
            self.load_config(new_config)

    def load_config(self, configs):
        LOG3(400 + 1, f"Loading {len(configs)} tiles — rebinding in progress")
        self._clear_layout()
        self.tiles.clear()

        for config in configs:
            tile = create_tile(config, self.dispatcher)
            self.tiles[config["id"]] = tile

        self._layout_tiles()
        LOG3(400 + 2, "Rebinding complete — layout reloaded")

    def export_current_config(self):
        """Return a list of current tile configurations for saving."""
        current = []
        for tile_id, tile in self.tiles.items():
            config = tile.config.copy()
            config["id"] = tile_id
            current.append(config)
        return current

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
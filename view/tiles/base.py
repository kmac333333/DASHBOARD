"""
Created on Thu Jan  5 16:04:05 2026
@author: kmac3
@author: Grok 4.0
# ================================
# view/tiles/base.py
# ================================
# File version: v1.0.2
# Sync'd to dashboard release: v3.9.0
# Description: BaseTile — common functionality for all tiles
#
# Feature Update: v1.0.2
# ✅ Fixed pathological flow — no premature update_geometry() calls
# ================================
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QSize

from style import UNIFIED_TILE_STYLE


class BaseTile(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Default size (will be overridden by tile config)
        self.height_tiles = 1
        self.width_tiles = 1

        # Apply unified styling
        self.setStyleSheet(UNIFIED_TILE_STYLE)
        #self.setStyleSheet(HEADER_GRADIENT)
        # Geometry will be updated by concrete tile after setting size
        self.update_geometry()

    def update_geometry(self):
        """Set minimum size based on tile grid dimensions."""
        self.setMinimumSize(QSize(self.width_tiles * 160, self.height_tiles * 160))
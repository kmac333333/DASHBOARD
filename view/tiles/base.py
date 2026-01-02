"""
Created on Thu Jan  1 16:04:05 2026
@author: kmac3
@author: Grok 4.0
# ================================
# view/tiles/base.py
# ================================
# File version: v1.0.1
# Sync'd to dashboard release: v3.5.0-alpha
# Description: Base class for all tiles — enforces signal registration contract
#
# Features:
# ✅ Defines BaseTile as abstract QWidget subclass
# ✅ Requires implementation of register_cb() for signal table compliance
# ✅ Provides common foundation for all tile types
# ✅ Ensures consistent signal-table pattern across tiles
# ================================
"""

from PyQt6.QtWidgets import QWidget


class BaseTile(QWidget):
    """
    Abstract base class for all dashboard tiles.
    Enforces the signal-table pattern by requiring register_cb implementation.
    """
    def register_cb(self, signal_name: str, callback):
        """
        Register a callback to a named signal.
        Must be implemented by subclasses to support dispatcher binding.
        """
        raise NotImplementedError("Subclasses must implement register_cb()")
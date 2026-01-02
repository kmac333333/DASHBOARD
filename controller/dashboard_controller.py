"""
Created on Thu Jan  1 16:04:05 2026
@author: kmac3
@author: Grok 4.0
# ================================
# controller/dashboard_controller.py
# ================================
# File version: v1.0.1
# Sync'd to dashboard release: v3.6.4
# Description: DashboardController — orchestrates startup, config loading, and shutdown
#
# Features:
# ✅ Initializes the dashboard on startup
# ✅ Loads configuration (via config.py) with fallback to defaults
# ✅ Creates and starts the DataDispatcher
# ✅ Binds tiles to dispatcher (via view)
# ✅ Handles graceful shutdown (stops dispatcher)
#
# Feature Update: v1.0.1
# ✅ Simplified — no longer needs main_window reference
# ================================
"""

from PyQt6.QtCore import QObject

from config import load_config
from support.myLOG2 import LOG3
from view.dashboard_view import DashboardView
from .dispatcher import DataDispatcher


class DashboardController(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # View created here so we can pass dispatcher
        self.dispatcher = DataDispatcher()
        self.view = DashboardView(self.dispatcher)

    def initialize(self):
        LOG3(300 + 1, "Controller initializing")
        self.load_layout()
        self.dispatcher.start()
        self.dispatcher.bind_config(self.view.tiles, load_config())

    def load_layout(self):
        config = load_config()
        LOG3(300 + 10, f"Loaded {len(config)} tiles")
        self.view.load_config(config)

    def shutdown(self):
        LOG3(300 + 20, "Controller shutting down")
        self.dispatcher.stop()
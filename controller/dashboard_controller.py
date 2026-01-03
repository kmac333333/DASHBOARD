"""
Created on Thu Jan  1 16:04:05 2026
@author: kmac3
@author: Grok 4.0
# ================================
# controller/dashboard_controller.py
# ================================
# File version: v1.0.6
# Sync'd to dashboard release: v3.8.0
# Description: DashboardController — orchestrates startup, config loading, file watching, and shutdown
#
# Features:
# ✅ Initializes the dashboard on startup
# ✅ Loads configuration with fallback to defaults
# ✅ Creates and starts the DataDispatcher
# ✅ Binds sources from config (configs only signature)
# ✅ Watches layout.json for external changes (controller domain)
# ✅ Prompts view for reload on change
# ✅ Handles graceful shutdown
#
# Feature Update: v1.0.6
# ✅ Added stop_file_watcher() to cleanly stop watcher after Force Default
# ================================
"""

from PyQt6.QtCore import QObject, QFileSystemWatcher
from pathlib import Path

from config import load_config, CONFIG_FILE
from support.myLOG2 import LOG3
from view.dashboard_view import DashboardView
from .dispatcher import DataDispatcher


class DashboardController(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # Dispatcher first
        self.dispatcher = DataDispatcher()

        # View — pass dispatcher
        self.view = DashboardView(self.dispatcher)

        # File watcher in controller domain
        self.setup_file_watcher()

    def initialize(self):
        LOG3(300 + 1, "Controller initializing")
        self.load_layout()
        self.dispatcher.start()
        self.dispatcher.bind_config(load_config())  # Correct signature — configs only

    def load_layout(self):
        config = load_config()
        LOG3(300 + 10, f"Loaded {len(config)} tiles")
        self.view.load_config(config)

    def setup_file_watcher(self):
        self.watcher = QFileSystemWatcher()
        config_path = Path(CONFIG_FILE)
        if config_path.exists():
            self.watcher.addPath(str(config_path.absolute()))
            self.watcher.fileChanged.connect(self.on_file_changed)
            LOG3(300 + 60, f"QFileSystemWatcher active on {CONFIG_FILE}")

    def stop_file_watcher(self):
        """Stop the file watcher to prevent duplicate triggers after Force Default."""
        if hasattr(self, 'watcher'):
            try:
                self.watcher.fileChanged.disconnect()
            except TypeError:
                pass  # Already disconnected
            paths = self.watcher.files()
            if paths:
                self.watcher.removePaths(paths)
            LOG3(300 + 63, "File watcher stopped after Force Default")

    def on_file_changed(self, path):
        LOG3(300 + 61, "External change detected in layout.json")
        self.view.on_external_layout_change()

    def shutdown(self):
        LOG3(300 + 20, "Controller shutting down")
        self.dispatcher.stop()
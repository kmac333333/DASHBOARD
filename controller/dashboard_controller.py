"""
Created on Thu Jan  3 16:04:05 2026
@author: kmac3
@author: Grok 4.0
# ================================
# controller/dashboard_controller.py
# ================================
# File version: v1.0.8
# Sync'd to dashboard release: v3.8.0
# Description: DashboardController — orchestrates startup, config loading, file watching, and shutdown
#
# Feature Update: v1.0.8
# ✅ Fixed QFileSystemWatcher reliability on Windows (pass path as list to constructor)
# ================================
"""

from PyQt6.QtCore import QObject, QFileSystemWatcher, QTimer
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
        self.dispatcher.bind_config(load_config())

    def load_layout(self):
        config = load_config()
        LOG3(300 + 10, f"Loaded {len(config)} tiles")
        self.view.load_config(config)

    def setup_file_watcher(self):
        config_path = Path(CONFIG_FILE)
        if config_path.exists():
            # Critical fix: pass path as list to constructor for Windows reliability
            self.watcher = QFileSystemWatcher([str(config_path.absolute())])
            self.watcher.fileChanged.connect(self.on_file_changed)
            LOG3(300 + 60, f"QFileSystemWatcher active on {CONFIG_FILE} (Windows-reliable mode)")
        else:
            LOG3(300 + 61, f"Config file {CONFIG_FILE} not found — watcher not started")

       # Debounce timer to merge rapid changes
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.setInterval(500)  # 500ms debounce
        self.debounce_timer.timeout.connect(self.on_file_changed_debounced)

    def trigger_debounce(self):
        """Start/restart debounce timer on file change."""
        self.debounce_timer.start()

    def on_file_changed_debounced(self):
        """Only prompt once after rapid changes settle."""
        LOG3(300 + 61, "External change detected in layout.json (debounced)")
        self.view.on_external_layout_change()

    def stop_file_watcher(self):
        """Stop watcher and timer."""
        if hasattr(self, 'debounce_timer'):
            self.debounce_timer.stop()
        """Stop the file watcher to prevent duplicate triggers after Force Default."""
        if hasattr(self, 'watcher'):
            try:
                self.watcher.fileChanged.disconnect()
            except TypeError:
                pass
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
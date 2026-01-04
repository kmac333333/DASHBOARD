"""
Created on Thu Jan  3 16:04:05 2026
@author: kmac3
@author: Grok 4.0
# ================================
# controller/dashboard_controller.py
# ================================
# File version: v1.0.10
# Sync'd to dashboard release: v3.9.0
# Description: DashboardController — orchestrates startup, config loading, file watching, and shutdown
#
# Feature Update: v1.0.10
# ✅ Auto-reload now instant by default with "Don't ask again" checkbox
# ✅ Preference stored in preferences.json
# ✅ Preserved on_file_changed method from v1.0.8
# ================================
"""

from PyQt6.QtCore import QObject, QFileSystemWatcher, QTimer
from pathlib import Path
from PyQt6.QtWidgets import QCheckBox, QMessageBox

from config import load_config, CONFIG_FILE
from support.myLOG2 import LOG3
from support.preferences import load_prefs, save_prefs
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

        # Preferences
        self.prefs = load_prefs()

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
            # Reliable Windows mode
            self.watcher = QFileSystemWatcher([str(config_path.absolute())])
            self.watcher.fileChanged.connect(self.trigger_debounce)
            LOG3(300 + 60, f"QFileSystemWatcher active on {CONFIG_FILE} (Windows-reliable mode)")
			 
																						  

        # Debounce timer
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.setInterval(500)
        self.debounce_timer.timeout.connect(self.on_file_changed_debounced)

    def trigger_debounce(self):
														  
        self.debounce_timer.start()

    def on_file_changed_debounced(self):
														  
        LOG3(300 + 61, "External change detected in layout.json (debounced)")
        if self.prefs.get("auto_reload_no_prompt", False):
            LOG3(300 + 62, "Auto-reloading (no prompt)")
            new_config = load_config()
            self.view.load_config(new_config)
        else:
            self.prompt_reload()

    def prompt_reload(self):
        checkbox = QCheckBox("Don't ask again")
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText("The layout file has been modified externally.\n\nReload layout?")
        msg.setWindowTitle("Layout Changed")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.Yes)
        msg.setCheckBox(checkbox)

        reply = msg.exec()
        if reply == QMessageBox.StandardButton.Yes:
            LOG3(300 + 62, "User confirmed reload")
            if checkbox.isChecked():
                self.prefs["auto_reload_no_prompt"] = True
                save_prefs(self.prefs)
                LOG3(300 + 63, "Auto-reload prompt disabled")
            new_config = load_config()
            self.view.load_config(new_config)

    def on_file_changed(self, path):
        """Preserved from v1.0.8 — routes to debounce"""
        LOG3(300 + 61, "External change detected in layout.json")
        self.trigger_debounce()

    def stop_file_watcher(self):
									 
        if hasattr(self, 'debounce_timer'):
            self.debounce_timer.stop()
																					  
        if hasattr(self, 'watcher'):
            try:
                self.watcher.fileChanged.disconnect()
            except TypeError:
                pass
            paths = self.watcher.files()
            if paths:
                self.watcher.removePaths(paths)
            LOG3(300 + 63, "File watcher stopped after Force Default")

									
																 
											 

    def shutdown(self):
        LOG3(300 + 20, "Controller shutting down")
        self.dispatcher.stop()
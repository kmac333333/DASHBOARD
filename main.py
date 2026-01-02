"""
Created on Thu Jan  1 16:04:05 2026
@author: kmac3
@author: Grok 4.0
# ================================
# main.py
# ================================
# File version: v1.7.0
# Sync'd to dashboard release: v3.6.7
# Description: Application entry point — bootstraps the dashboard
#
# Features:
# ✅ Minimal bootstrap: creates QApplication, sets dark palette
# ✅ Instantiates DashboardController
# ✅ Builds menu: Exit, About, Save Layout, Add Static Tile, Force Default Layout
# ✅ Starts controller initialization
# ✅ Handles graceful shutdown
#
# Feature Update: v1.7.0
# ✅ Restored "Force Default Layout" menu item (Ctrl+D) — deletes layout.json
# ================================
"""

import sys
import time
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox,
    QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QDialogButtonBox
)
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

from controller.dashboard_controller import DashboardController
from config import save_config, load_config, CONFIG_FILE


class AddTileDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Static Tile")

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Title:"))
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("e.g., New Status")
        layout.addWidget(self.title_edit)

        layout.addWidget(QLabel("Body text:"))
        self.body_edit = QLineEdit()
        self.body_edit.setPlaceholderText("e.g., All systems operational")
        layout.addWidget(self.body_edit)

        layout.addWidget(QLabel("Tile size:"))
        self.size_combo = QComboBox()
        self.size_combo.addItems([
            "1×1", "1×2", "1×3", "1×4",
            "2×1", "2×2", "2×3", "2×4"
        ])
        layout.addWidget(self.size_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_config(self):
        if self.exec() == QDialog.DialogCode.Accepted:
            size_str = self.size_combo.currentText()
            height = int(size_str[0])
            width = int(size_str[2])
            return {
                "id": f"static-{int(time.time())}",
                "type": "simple_text",
                "hex_id": "NEW",
                "title": self.title_edit.text().strip() or "New Tile",
                "size": [height, width],
                "bindings": {
                    "value": {
                        "type": "static",
                        "value": self.body_edit.text().strip() or "—"
                    }
                }
            }
        return None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Dynamic Indexed MQTT Dashboard – v3.6.7 – January 01, 2026")
        self.setGeometry(100, 100, 1600, 1000)

        self.controller = DashboardController(self)

        self.view = self.controller.view

        self.setCentralWidget(self.view)

        self.menu_bar = self.menuBar()
        self.create_menu()

        self.controller.initialize()

    def create_menu(self):
        self.menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: #1e293b;
                color: white;
                padding: 8px;
                border-bottom: 1px solid #334155;
            }
            QMenuBar::item { padding: 8px 20px; }
            QMenuBar::item:selected { background-color: #6366f1; border-radius: 6px; }
            QMenu { background-color: #1e293b; color: white; border: 1px solid #334155; }
            QMenu::item:selected { background-color: #6366f1; }
        """)

        file_menu = self.menu_bar.addMenu("File")

        save_action = file_menu.addAction("Save Layout")
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_layout)

        force_default_action = file_menu.addAction("Force Default Layout")
        force_default_action.setShortcut("Ctrl+D")
        force_default_action.triggered.connect(self.force_default_layout)

        file_menu.addSeparator()

        exit_action = file_menu.addAction("Exit")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)

        tile_menu = self.menu_bar.addMenu("Tile")
        add_action = tile_menu.addAction("Add Static Tile")
        add_action.triggered.connect(self.add_static_tile)

        help_menu = self.menu_bar.addMenu("Help")
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about)

    def save_layout(self):
        current_config = self.view.export_current_config()
        save_config(current_config)
        QMessageBox.information(self, "Saved", "Current layout saved to layout.json")

    def force_default_layout(self):
        reply = QMessageBox.question(
            self,
            "Force Default Layout",
            "This will delete layout.json and reload the built-in default layout on next start.\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if os.path.exists(CONFIG_FILE):
                    os.remove(CONFIG_FILE)
                    QMessageBox.information(self, "Reset", "layout.json deleted — defaults will load on restart")
                else:
                    QMessageBox.information(self, "Reset", "No layout.json found — already using defaults")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete layout.json:\n{e}")

    def add_static_tile(self):
        dialog = AddTileDialog(self)
        new_config = dialog.get_config()
        if new_config:
            current = load_config()
            current.append(new_config)
            save_config(current)
            self.view.load_config(current)
            QMessageBox.information(self, "Added", f"Tile '{new_config['title']}' added and saved")

    def show_about(self):
        QMessageBox.information(
            self,
            "About",
            "Dynamic MQTT Dashboard\nv3.6.7\nForce Default Layout restored"
        )

    def closeEvent(self, event):
        self.controller.shutdown()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(15, 23, 42))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(30, 41, 59))
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(30, 41, 59))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Highlight, QColor(99, 102, 241))
    app.setPalette(palette)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
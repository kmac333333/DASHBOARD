"""
File Watcher Test App — Standalone PyQt6
File version: v1.0.0
Description: Simple PyQt6 app to test QFileSystemWatcher reliability
Features:
- Watches 'test.txt' in current directory
- Prints timestamped messages on file change
- Handles file creation/deletion
- Runs until window closed
"""

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton
from PyQt6.QtCore import QFileSystemWatcher, QDateTime
import sys
import os

class FileWatcherTest(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 File Watcher Test")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.status_label = QLabel("Watching for changes to 'test.txt'...")
        layout.addWidget(self.status_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        test_button = QPushButton("Create test.txt (if missing)")
        test_button.clicked.connect(self.create_test_file)
        layout.addWidget(test_button)

        self.setLayout(layout)

        # Setup watcher
        self.watcher = QFileSystemWatcher()
        self.file_path = "c:\proj2\ply_view_dev\test.txt"

        if os.path.exists(self.file_path):
            self.watcher.addPath(self.file_path)
            self.log("Watcher started — monitoring 'test.txt'")

        self.watcher.fileChanged.connect(self.on_file_changed)

    def create_test_file(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                f.write("Test file created\n")
            self.log("Created 'test.txt'")
        else:
            self.log("'test.txt' already exists")

    def on_file_changed(self, path):
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.log(f"[{timestamp}] File changed: {path}")

        # Re-add path in case it was deleted/recreated
        if not self.watcher.files():
            if os.path.exists(path):
                self.watcher.addPath(path)
                self.log(f"Re-added path to watcher: {path}")

    def log(self, message):
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.log_text.append(f"[{timestamp}] {message}")
        self.log_text.ensureCursorVisible()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileWatcherTest()
    window.show()
    sys.exit(app.exec())
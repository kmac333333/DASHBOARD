import sys
import time
from PyQt6 import QtCore, QtWidgets

class FileWatcherApp(QtWidgets.QWidget):
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.initUI()
        self.initFileWatcher()

    def initUI(self):
        self.setWindowTitle("PyQt6 QFileSystemWatcher Example")
        self.setGeometry(100, 100, 400, 100)
        layout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel(f"Monitoring file: {self.file_path}\nLast modified: N/A", self)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def initFileWatcher(self):
        # Create a QFileSystemWatcher instance
        self.watcher = QtCore.QFileSystemWatcher([self.file_path])

        # Connect the fileChanged signal to a custom slot (method)
        self.watcher.fileChanged.connect(self.on_file_changed)

        print(f"Watcher initialized for: {self.file_path}")

    @QtCore.pyqtSlot(str)
    def on_file_changed(self, path):
        """Slot to handle the fileChanged signal."""
        print(f"File changed signal received for: {path}")
        # Update the UI with the new modification time
        self.update_file_status()

    def update_file_status(self):
        """Helper to get the current file modification time and update the label."""
        file_info = QtCore.QFileInfo(self.file_path)
        if file_info.exists():
            last_modified = file_info.lastModified().toString("yyyy-MM-dd hh:mm:ss")
            self.label.setText(f"Monitoring file: {self.file_path}\nLast modified: {last_modified}")
        else:
            self.label.setText(f"File no longer exists: {self.file_path}")

def main():
    app = QtWidgets.QApplication(sys.argv)

    # 1. Create a dummy file to monitor (for demonstration purposes)
    temp_file_path = "watched_file.txt"
    with open(temp_file_path, "w") as f:
        f.write("Initial content")
    print(f"Created dummy file: {temp_file_path}")

    # 2. Instantiate the application with the file path
    ex = FileWatcherApp(temp_file_path)
    ex.show()

    # 3. Modify the file after the app starts to trigger the watcher
    # Using a QTimer to simulate an external change after a short delay
    #QtCore.QTimer.singleShot(2000, lambda: modify_file(temp_file_path))
    #QtCore.QTimer.singleShot(4000, lambda: modify_file(temp_file_path, "Second change"))

    sys.exit(app.exec())

def modify_file(path, content="Updated content"):
    """Function to simulate an external program modifying the file."""
    with open(path, "a") as f:
        f.write(f"\n{content} at {time.ctime()}")
    print(f"--- Externally modified file: {path} ---")

if __name__ == '__main__':
    main()

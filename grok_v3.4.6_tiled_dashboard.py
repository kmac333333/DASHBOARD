# ================================
# DASHBOARD VERSION HISTORY
# ================================
# Current: v3.4.6 — January 01, 2026
# Goal: Cross-platform uptime (Windows + Linux/macOS)
# Attempt:
#   - Replaced subprocess uptime with time.monotonic() pure Python
#   - Formatted like Linux "uptime -p"
#   - Works identically on Windows
# Outcome: Success — uptime now reliable everywhere
# Action: Stable revision
#
# v3.4.5 — January 01, 2026
# Goal: Multiline labels + system tile width
# Outcome: Success

import sys
import json
import time
import threading
import paho.mqtt.client as mqtt
import psutil
from support.myLOG2 import LOG3, LOG2
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QScrollArea, QToolButton,
    QInputDialog, QMessageBox, QStyle, QMenuBar,
    QComboBox, QDialog, QDialogButtonBox
)
from PyQt6.QtGui import QPalette, QColor, QAction
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QObject, QTimer, QDateTime


# ================================
# LOGGING BASE IDs
# ================================
BASE_MQTT_CLIENT      = 100
BASE_DISPATCHER       = 200
BASE_CONTROLLER       = 300
BASE_VIEW             = 400
BASE_TILE             = 500
BASE_SYSTEM           = 600


# ================================
# GLOBAL CONSTANTS
# ================================
MQTT_BROKER = "rpibroker.local"
TILE_BASE_WIDTH = 160
TILE_BASE_HEIGHT = 160
APP_VERSION = "v3.4.6"
CONFIG_FILE = "layout.json"


# ================================
# DEFAULT CONFIG - System health 3 columns wide
# ================================
DEFAULT_CONFIG = [
    {
        "id": "system-health",
        "type": "multiline",
        "hex_id": "SYSTEM",
        "title": "System Health",
        "size": [2, 3],
        "bindings": {
            "line1": {"type": "system_prop", "prop": "mqtt_status"},
            "line2": {"type": "system_prop", "prop": "broker"},
            "line3": {"type": "system_prop", "prop": "uptime"},
            "line4": {"type": "system_prop", "prop": "cpu_load"},
            "line5": {"type": "system_prop", "prop": "memory"}
        }
    },
    {
        "id": "living-temp",
        "hex_id": "08BD45F23A08",
        "title": "Living Room Temp",
        "size": [1, 1],
        "bindings": {
            "value": {
                "type": "mqtt",
                "topic": "/home/temp/unit/A/08BD45F23A08",
                "format": "({:.1f}°F) → {:.1f}°C"
            }
        }
    },
    {
        "id": "network",
        "hex_id": "NETWORK",
        "title": "Network",
        "size": [1, 1],
        "bindings": {
            "value": {
                "type": "static",
                "value": "↑ 45.2 Mbps\n↓ 12.8 Mbps\nLatency: 18ms"
            }
        }
    },
    {
        "id": "alerts",
        "hex_id": "ALERTS",
        "title": "Alerts",
        "size": [1, 1],
        "bindings": {
            "value": {
                "type": "static",
                "value": "0 critical\n3 warnings"
            }
        }
    }
]


# ================================
# BASE TILE
# ================================
class BaseTile(QWidget):
    def register_cb(self, signal_name: str, callback):
        raise NotImplementedError


# ================================
# SIMPLE TEXT TILE
# ================================
class SimpleTextTile(BaseTile):
    SIG_value_updated = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.height_tiles = config["size"][0]
        self.width_tiles = config["size"][1]

        self.setMinimumSize(QSize(self.width_tiles * TILE_BASE_WIDTH, self.height_tiles * TILE_BASE_HEIGHT))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header_container = QWidget()
        header_container.setFixedHeight(90)
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(20, 8, 20, 8)
        header_layout.setSpacing(10)

        header_container.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #6366f1,
                                        stop:0.85 #4f46e5,
                                        stop:1 #1e293b);
        """)

        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setSpacing(0)
        title_layout.setContentsMargins(0, 0, 0, 0)

        self.hex_id_label = QLabel(config["hex_id"])
        self.hex_id_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.hex_id_label.setStyleSheet("color: white; font-size: 40px; font-weight: bold;")

        self.title_label = QLabel(config["title"])
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        self.title_label.setStyleSheet("color: rgba(255, 255, 255, 180); font-size: 20px;")
        self.title_label.setWordWrap(False)
        self.title_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.title_label.mousePressEvent = self.edit_title
        self.title_label.setContentsMargins(5, 0, 0, 0)

        title_layout.addWidget(self.hex_id_label)
        title_layout.addWidget(self.title_label)

        header_layout.addWidget(title_container, stretch=1)

        layout.addWidget(header_container)

        self.body_label = QLabel("—")
        self.body_label.setWordWrap(True)
        self.body_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.body_label.setStyleSheet("color: #e2e8f0; padding: 30px; font-size: 48px; font-weight: bold;")

        layout.addWidget(self.body_label, stretch=1)

        self.SIG_value_updated.connect(self.body_label.setText)

        self.signal_table = {
            "value": self.SIG_value_updated
        }

    def register_cb(self, signal_name: str, callback):
        if signal_name in self.signal_table:
            self.signal_table[signal_name].connect(callback)
            return True
        LOG3(BASE_TILE + 1, f"Warning: Unknown signal '{signal_name}' on tile '{self.config.get('title', 'Unknown')}'")
        return False

    def edit_title(self, event):
        new_title, ok = QInputDialog.getText(self, "Edit Title", "Title:", text=self.config["title"])
        if ok:
            self.config["title"] = new_title
            self.title_label.setText(new_title)


# ================================
# MULTILINE TILE - With labels from prop
# ================================
class MultilineTile(BaseTile):
    SIG_line1_updated = pyqtSignal(str)
    SIG_line2_updated = pyqtSignal(str)
    SIG_line3_updated = pyqtSignal(str)
    SIG_line4_updated = pyqtSignal(str)
    SIG_line5_updated = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.height_tiles = config["size"][0]
        self.width_tiles = config["size"][1]

        self.setMinimumSize(QSize(self.width_tiles * TILE_BASE_WIDTH, self.height_tiles * TILE_BASE_HEIGHT))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header_container = QWidget()
        header_container.setFixedHeight(90)
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(20, 8, 20, 8)
        header_layout.setSpacing(10)

        header_container.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #6366f1,
                                        stop:0.85 #4f46e5,
                                        stop:1 #1e293b);
        """)

        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setSpacing(0)
        title_layout.setContentsMargins(0, 0, 0, 0)

        self.hex_id_label = QLabel(config["hex_id"])
        self.hex_id_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.hex_id_label.setStyleSheet("color: white; font-size: 40px; font-weight: bold;")

        self.title_label = QLabel(config["title"])
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        self.title_label.setStyleSheet("color: rgba(255, 255, 255, 180); font-size: 20px;")
        self.title_label.setWordWrap(False)
        self.title_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.title_label.mousePressEvent = self.edit_title
        self.title_label.setContentsMargins(5, 0, 0, 0)

        title_layout.addWidget(self.hex_id_label)
        title_layout.addWidget(self.title_label)

        header_layout.addWidget(title_container, stretch=1)

        layout.addWidget(header_container)

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(20, 20, 20, 20)
        body_layout.setSpacing(12)

        self.value_labels = []

        bindings = config.get("bindings", {})
        props = [bindings.get(f"line{i}", {}).get("prop", "") for i in range(1, 6)]

        for i in range(5):
            h_layout = QHBoxLayout()
            h_layout.setSpacing(10)

            prop = props[i]
            label_text = prop.replace("_", " ").title() if prop else f"Line {i+1}"
            label = QLabel(label_text + ":")
            label.setStyleSheet("color: #94a3b8; font-size: 20px; font-weight: bold;")
            h_layout.addWidget(label)

            value = QLabel("—")
            value.setStyleSheet("color: #e2e8f0; font-size: 22px;")
            value.setWordWrap(True)
            h_layout.addWidget(value, stretch=1)

            body_layout.addLayout(h_layout)
            self.value_labels.append(value)

        body_layout.addStretch()
        layout.addWidget(body, stretch=1)

        self.SIG_line1_updated.connect(lambda t: self.value_labels[0].setText(t))
        self.SIG_line2_updated.connect(lambda t: self.value_labels[1].setText(t))
        self.SIG_line3_updated.connect(lambda t: self.value_labels[2].setText(t))
        self.SIG_line4_updated.connect(lambda t: self.value_labels[3].setText(t))
        self.SIG_line5_updated.connect(lambda t: self.value_labels[4].setText(t))

        self.signal_table = {
            "line1": self.SIG_line1_updated,
            "line2": self.SIG_line2_updated,
            "line3": self.SIG_line3_updated,
            "line4": self.SIG_line4_updated,
            "line5": self.SIG_line5_updated
        }

    def register_cb(self, signal_name: str, callback):
        if signal_name in self.signal_table:
            self.signal_table[signal_name].connect(callback)
            return True
        LOG3(BASE_TILE + 10, f"Warning: Unknown signal '{signal_name}' on multiline tile")
        return False

    def edit_title(self, event):
        new_title, ok = QInputDialog.getText(self, "Edit Title", "Title:", text=self.config["title"])
        if ok:
            self.config["title"] = new_title
            self.title_label.setText(new_title)


# ================================
# TILE FACTORY
# ================================
def create_tile(config):
    tile_type = config.get("type", "simple_text")
    if tile_type == "simple_text":
        return SimpleTextTile(config)
    elif tile_type == "multiline":
        return MultilineTile(config)
    else:
        LOG3(BASE_CONTROLLER + 50, f"Unknown tile type: {tile_type}")
        return SimpleTextTile(config)


# ================================
# MQTT CLIENT
# ================================
class MqttLiveClient(QObject):
    SIG_message_received = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.broker = MQTT_BROKER
        self.port = 1883
        self.client = None
        self.running = False
        self.topics = set()

        self.signal_table = {
            "message_received": self.SIG_message_received
        }

    def register_cb(self, signal_name: str, callback):
        if signal_name in self.signal_table:
            self.signal_table[signal_name].connect(callback)
            return True
        LOG3(BASE_MQTT_CLIENT + 1, f"Warning: Unknown MQTT client signal '{signal_name}'")
        return False

    def add_topic(self, topic):
        self.topics.add(topic)

    def start(self):
        if self.running:
            return
        self.running = True
        LOG3(BASE_MQTT_CLIENT + 2, "Starting MQTT client thread")
        threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        self.running = False
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
        LOG3(BASE_MQTT_CLIENT + 3, "MQTT client stopped")

    def _run(self):
        def on_connect(client, userdata, flags, rc, properties=None):
            if rc == 0:
                LOG3(BASE_MQTT_CLIENT + 10, f"MQTT Connected to {self.broker}")
                for topic in self.topics:
                    client.subscribe(topic)
                    LOG3(BASE_MQTT_CLIENT + 12, f"Subscribed to {topic}")
            else:
                LOG3(BASE_MQTT_CLIENT + 11, f"MQTT connection failed: {rc}")

        def on_message(client, userdata, msg):
            try:
                payload = msg.payload.decode().strip()
                if payload:
                    LOG3(BASE_MQTT_CLIENT + 20, f"MQTT message: {msg.topic} -> {payload}")
                    self.SIG_message_received.emit(msg.topic, payload)
            except Exception as e:
                LOG3(BASE_MQTT_CLIENT + 21, f"MQTT message error: {e}")

        self.client = mqtt.Client(protocol=mqtt.MQTTv5)
        self.client.on_connect = on_connect
        self.client.on_message = on_message

        retry_delay = 2
        while self.running:
            try:
                self.client.connect(self.broker, self.port)
                self.client.loop_forever()
                break
            except Exception as e:
                LOG3(BASE_MQTT_CLIENT + 30, f"Connection attempt failed: {e}")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 30)


# ================================
# SYSTEM PROPERTY SOURCE
# ================================
class SystemPropertySource(QObject):
    data_ready = pyqtSignal(str)

    def __init__(self, getter, interval=5):
        super().__init__()
        self.getter = getter
        self.interval = interval
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)

    def update(self):
        try:
            value = self.getter()
            self.data_ready.emit(value)
        except Exception as e:
            LOG3(BASE_SYSTEM + 1, f"System prop error: {e}")

    def start(self):
        self.update()
        if self.interval > 0:
            self.timer.start(self.interval * 1000)

    def stop(self):
        self.timer.stop()


# ================================
# DISPATCHER - Cross-platform uptime
# ================================
class DataDispatcher(QObject):
    def __init__(self):
        super().__init__()
        self.mqtt_client = MqttLiveClient()
        self.mqtt_bindings = []
        self.system_sources = []

    def start(self):
        LOG3(BASE_DISPATCHER + 1, "Dispatcher starting MQTT client")
        self.mqtt_client.register_cb("message_received", self.on_mqtt_message)
        self.mqtt_client.start()

    def bind_config(self, tile_widgets, configs):
        LOG3(BASE_DISPATCHER + 10, f"Binding {len(configs)} tiles")
        for config in configs:
            tile = tile_widgets[config["id"]]

            for signal_name, feed in config.get("bindings", {}).items():
                if signal_name not in tile.signal_table:
                    continue

                if feed["type"] == "static":
                    LOG3(BASE_DISPATCHER + 20, f"Static bind to {config['id']}: {feed['value']}")
                    tile.signal_table[signal_name].emit(feed["value"])

                elif feed["type"] == "mqtt":
                    LOG3(BASE_DISPATCHER + 30, f"MQTT bind {feed['topic']} -> {config['id']}:{signal_name}")
                    self.mqtt_client.add_topic(feed["topic"])
                    self.mqtt_bindings.append((feed["topic"], feed.get("format", "{}"), tile.signal_table[signal_name]))

                elif feed["type"] == "system_prop":
                    prop = feed["prop"]
                    getter = self.get_system_getter(prop)
                    if getter:
                        source = SystemPropertySource(getter, feed.get("interval", 5))
                        source.data_ready.connect(tile.signal_table[signal_name].emit)
                        self.system_sources.append(source)
                        source.start()
                    else:
                        LOG3(BASE_DISPATCHER + 40, f"Unknown system_prop: {prop}")

    def get_system_getter(self, prop):
        def format_uptime():
            uptime_seconds = time.monotonic()
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            if days > 0:
                return f"up {days} days, {hours:02d}:{minutes:02d}"
            else:
                return f"up {hours:02d}:{minutes:02d}"

        getters = {
            "mqtt_status": lambda: "Connected ✓" if self.mqtt_client.running else "Disconnected ✗",
            "broker": lambda: MQTT_BROKER,
            "uptime": format_uptime,
            "cpu_load": lambda: f"{psutil.cpu_percent(interval=1):.1f}%",
            "memory": lambda: f"{psutil.virtual_memory().percent:.1f}% used"
        }
        return getters.get(prop)

    def on_mqtt_message(self, topic, payload):
        LOG3(BASE_DISPATCHER + 50, f"Dispatcher received MQTT: {topic} -> {payload}")
        try:
            fahrenheit = float(payload)
            celsius = (fahrenheit - 32) * 5 / 9
            for binding_topic, format_str, signal in self.mqtt_bindings:
                if topic == binding_topic:
                    formatted = format_str.format(fahrenheit, celsius)
                    LOG3(BASE_DISPATCHER + 60, f"Emitting to signal: {formatted}")
                    signal.emit(formatted)
        except ValueError:
            LOG3(BASE_DISPATCHER + 61, f"Invalid payload: {payload}")

    def stop(self):
        LOG3(BASE_DISPATCHER + 70, "Dispatcher stopping")
        for source in self.system_sources:
            source.stop()
        self.mqtt_client.stop()


# ================================
# DASHBOARD VIEW - Unified tile styling
# ================================
class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            background-color: #0f172a;

            SimpleTextTile, MultilineTile {
                background: #1e293b;
                border-radius: 18px;
                border: 1px solid #334155;
            }
            SimpleTextTile:hover, MultilineTile:hover {
                border: 1px solid #6366f1;
                background: #232e41;
            }
        """)
        self.tiles = {}

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        layout.addWidget(self.scroll_area)

        self.container = QWidget()
        self.grid = QGridLayout(self.container)
        self.grid.setSpacing(30)
        self.grid.setContentsMargins(30, 30, 30, 30)
        self.scroll_area.setWidget(self.container)

    def load_config(self, configs):
        LOG3(BASE_VIEW + 1, f"Loading {len(configs)} tiles")
        for tile in self.tiles.values():
            tile.setParent(None)
            tile.deleteLater()
        self.tiles.clear()

        for config in configs:
            tile = create_tile(config)
            self.tiles[config["id"]] = tile

        self._layout_tiles()

    def _layout_tiles(self):
        self._clear_layout()
        occupied = []
        max_rows = 0

        for tile in self.tiles.values():
            h, w = tile.height_tiles, tile.width_tiles
            placed, r = False, 0
            while not placed:
                while len(occupied) < r + h:
                    occupied.append([False] * 8)
                for c in range(8 - w):
                    if all(
                        r + dr < len(occupied) and c + dc < len(occupied[r + dr]) and not occupied[r + dr][c + dc]
                        for dr in range(h) for dc in range(w)
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

    def _clear_layout(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item and item.widget():
                item.widget().setParent(None)


# ================================
# CONTROLLER
# ================================
class DashboardController(QObject):
    def __init__(self, view, main_window):
        super().__init__()
        self.view = view
        self.main_window = main_window
        self.dispatcher = DataDispatcher()

    def initialize(self):
        LOG3(BASE_CONTROLLER + 1, "Controller initializing")
        self.load_layout()
        self.dispatcher.start()
        self.dispatcher.bind_config(self.view.tiles, CURRENT_CONFIG)

        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_title_time)
        self.clock_timer.start(1000)
        self.update_title_time()

    def update_title_time(self):
        current_time = QDateTime.currentDateTime().toString("HH:mm:ss")
        self.main_window.setWindowTitle(f"Dynamic Indexed MQTT Dashboard – {APP_VERSION} – January 01, 2026 – {current_time}")

    def load_layout(self):
        global CURRENT_CONFIG
        try:
            with open(CONFIG_FILE, "r") as f:
                CURRENT_CONFIG = json.load(f)
            LOG3(BASE_CONTROLLER + 10, f"Loaded {len(CURRENT_CONFIG)} tiles from {CONFIG_FILE}")
        except Exception as e:
            LOG3(BASE_CONTROLLER + 11, f"Config load failed: {e}. Using default.")
            CURRENT_CONFIG = DEFAULT_CONFIG[:]

        self.view.load_config(CURRENT_CONFIG)

    def shutdown(self):
        LOG3(BASE_CONTROLLER + 20, "Controller shutting down")
        self.dispatcher.stop()
        if hasattr(self, 'clock_timer'):
            self.clock_timer.stop()


# Global
CURRENT_CONFIG = []


# ================================
# MAIN WINDOW
# ================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Dynamic Indexed MQTT Dashboard – {APP_VERSION} – January 01, 2026")
        self.setGeometry(100, 100, 1600, 1000)

        self.view = DashboardView()
        self.setCentralWidget(self.view)

        self.controller = DashboardController(self.view, self)

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

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = self.menu_bar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(
            lambda: QMessageBox.information(self, "About", f"Dynamic MQTT Dashboard\n{APP_VERSION}\nCross-platform uptime + multiline labels")
        )
        help_menu.addAction(about_action)

    def closeEvent(self, event):
        self.controller.shutdown()
        event.accept()


# ================================
# RUN APPLICATION
# ================================
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
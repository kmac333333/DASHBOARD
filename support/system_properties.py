"""
Created on Thu Jan  1 16:04:05 2026
@author: kmac3
@author: Grok 4.0
# ================================
# support/system_properties.py
# ================================
# File version: v1.0.1
# Sync'd to dashboard release: v3.5.0-alpha
# Description: SystemPropertySource — polling wrapper for system metrics
#
# Features:
# ✅ Generic polling source for any system property getter
# ✅ Configurable update interval (seconds)
# ✅ Emits data_ready(str) signal with formatted value
# ✅ Safe start/stop for timer management
# ✅ Used by dispatcher for live system stats (uptime, CPU, memory, etc.)
# ================================
"""

from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class SystemPropertySource(QObject):
    """
    Polls a getter function at regular intervals and emits the result.
    Used for live system properties like uptime, CPU load, memory usage.
    """
    data_ready = pyqtSignal(str)

    def __init__(self, getter, interval=5):
        """
        :param getter: Callable that returns a string value
        :param interval: Update interval in seconds (0 = one-shot)
        """
        super().__init__()
        self.getter = getter
        self.interval = interval
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)

    def update(self):
        """Fetch current value and emit it."""
        try:
            value = self.getter()
            self.data_ready.emit(value)
        except Exception as e:
            # Avoid circular import with LOG3 — simple print fallback
            print(f"[ERROR] System property getter failed: {e}")

    def start(self):
        """Start polling — immediate update + timed if interval > 0."""
        self.update()
        if self.interval > 0:
            self.timer.start(self.interval * 1000)

    def stop(self):
        """Stop polling."""
        self.timer.stop()
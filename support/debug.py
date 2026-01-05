"""
Created on Thu Jan  4 16:04:05 2026
@author: kmac3
@author: Grok 4.0
# ================================
# support/debug.py
# ================================
# File version: v1.0.1
# Sync'd to dashboard release: v3.9.0
# Description: Debug utilities for the dashboard
#
# Feature Update: v1.0.1
# ✅ dump_object_hierarchy now starts from MainWindow (full UI tree)
# ✅ Includes className and objectName
# ================================
"""

import json
from PyQt6.QtWidgets import QApplication
from support.myLOG2 import LOG3


def dump_object_hierarchy():
    """Dump Qt object hierarchy starting from MainWindow to object_hierarchy.json."""
    app = QApplication.instance()
    if not app:
        LOG3(300 + 100, "No QApplication instance found")
        return

    # Find the MainWindow (our UI root)
    main_window = None
    for widget in app.topLevelWidgets():
        if widget.__class__.__name__ == "MainWindow":
            main_window = widget
            break

    if not main_window:
        LOG3(300 + 100, "MainWindow not found")
        return

    hierarchy = _traverse_hierarchy(main_window)

    file_path = "object_hierarchy.json"
    try:
        with open(file_path, "w") as f:
            json.dump(hierarchy, f, indent=2)
        LOG3(300 + 100, f"Full object hierarchy dumped to {file_path}")
    except Exception as e:
        LOG3(300 + 101, f"Failed to dump hierarchy: {e}")

def _traverse_hierarchy(obj):
    """Recursive traversal of Qt object tree."""
    info = {
        "objectName": obj.objectName() or "<unnamed>",
        "className": obj.metaObject().className(),
        "isWidget": obj.isWidgetType(),
        "children": []
    }
    for child in obj.children():
        info["children"].append(_traverse_hierarchy(child))
    return info
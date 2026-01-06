"""
Created on Thu Jan  6 16:04:05 2026
@author: kmac3
@author: Grok 4.0
# ================================
# config.py
# ================================
# File version: v1.0.4
# Sync'd to dashboard release: v3.9.0
# Description: Default configuration and config file handling
#
# Features:
# ✅ Holds DEFAULT_CONFIG with all current tiles (including system_out)
# ✅ Provides load_config() with safe fallback to defaults
# ✅ Provides save_config() for "Save Layout" functionality
# ✅ Handles missing/invalid layout.json gracefully
#
# Feature Update: v1.0.4
# ✅ Added default weather tile to DEFAULT_CONFIG
# ================================
"""

import json
import os

# Default configuration (fallback if layout.json missing or invalid)
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
        "id": "dual-temp",
        "type": "dual_text",
        "hex_id": "DUAL",
        "title": "Indoor / Outdoor",
        "size": [1, 2],
        "bindings": {
            "primary": {
                "type": "mqtt",
                "topic": "/home/temp/unit/A/08BD45F23A08",
                "format": "{:.1f}°F → {:.1f}°C",
                "label": "Indoor"
            },
            "secondary": {
                "type": "mqtt",
                "topic": "/home/temp/unit/B/08BD45F23A08",
                "format": "{:.1f}°F → {:.1f}°C",
                "label": "Outdoor"
            }
        }
    },
    {
        "id": "weather",
        "type": "weather",
        "hex_id": "WX",
        "title": "Weather",
        "size": [2, 4],  # 2 rows high, 4 columns wide
        "api_key": "fff528869fbd42f69ec174849260601",  # User must replace
        "location": "Grass Valley, CA",
        "indoor_topic": "/home/temp/unit/A/08BD45F23A08",
        "outdoor_topic": "/home/temp/unit/B/08BD45F23A08"
    },
    {
        "id": "system-out",
        "type": "system_out",
        "hex_id": "DEBUG",
        "title": "System Output",
        "size": [2, 8],  # Full width at bottom
        "bindings": {}
    }
]

CONFIG_FILE = "layout.json"

def load_config():
    """Load configuration from layout.json, fall back to DEFAULT_CONFIG on error."""
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG[:]

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
		  # Basic validation — ensure it's a list										 
        if isinstance(config, list):
            return config
        else:
            print(f"[WARN] {CONFIG_FILE} is not a list — using default config")
            return DEFAULT_CONFIG[:]
    except Exception as e:
        print(f"[ERROR] Failed to load {CONFIG_FILE}: {e} — using default config")
        return DEFAULT_CONFIG[:]

def save_config(config):
    """Save current configuration to layout.json."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        print(f"[INFO] Configuration saved to {CONFIG_FILE}")
    except Exception as e:
        print(f"[ERROR] Failed to save {CONFIG_FILE}: {e}")
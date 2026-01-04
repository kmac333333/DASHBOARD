"""
Created on Thu Jan  3 16:04:05 2026
@author: kmac3
@author: Grok 4.0
# ================================
# support/preferences.py
# ================================
# File version: v1.0.0
# Sync'd to dashboard release: v3.9.0
# Description: Simple persistent preferences storage (JSON file)
#
# Features:
# ✅ Loads and saves user preferences (e.g., auto_reload_no_prompt)
# ✅ Defaults to safe values if file missing or invalid
# ✅ Minimal, self-contained
# ================================
"""

import json
import os
from pathlib import Path

PREF_FILE = "preferences.json"

DEFAULT_PREFS = {
    "auto_reload_no_prompt": False
}

def load_prefs():
    """Load preferences from preferences.json, fall back to defaults on error."""
    if not os.path.exists(PREF_FILE):
        return DEFAULT_PREFS.copy()

    try:
        with open(PREF_FILE, "r", encoding="utf-8") as f:
            prefs = json.load(f)
        # Merge with defaults to handle missing keys
        merged = DEFAULT_PREFS.copy()
        merged.update(prefs)
        return merged
    except Exception as e:
        print(f"[ERROR] Failed to load preferences: {e} — using defaults")
        return DEFAULT_PREFS.copy()

def save_prefs(prefs):
    """Save preferences to preferences.json."""
    try:
        with open(PREF_FILE, "w", encoding="utf-8") as f:
            json.dump(prefs, f, indent=2, ensure_ascii=False)
        print(f"[INFO] Preferences saved to {PREF_FILE}")
    except Exception as e:
        print(f"[ERROR] Failed to save preferences: {e}")
"""
Created on Thu Jan  3 16:04:05 2026
@author: kmac3
@author: Grok 4.0
# ================================
# style.py
# ================================
# File version: v1.0.2
# Sync'd to dashboard release: v3.7.1
# Description: Single source of truth for all visual styling
#
# Features:
# ✅ Dashboard background
# ✅ Unified tile base style (background, border, hover)
# ✅ Header gradient
# ✅ Menu bar styling
# ✅ Text colors (header, subtitle, primary, secondary)
# ✅ Font specifications (family, sizes, weights for all elements)
# ================================
"""

# Font family (system-safe)
FONT_FAMILY = "Segoe UI, Arial, sans-serif"

# Dashboard background
DASHBOARD_BG = "#0f172a"

# Unified tile base
TILE_BG = "#1e293b"
TILE_BORDER = "#334155"
TILE_HOVER_BORDER = "#6366f1"
TILE_HOVER_BG = "#232e41"
TILE_RADIUS = "18px"

# Header gradient
HEADER_GRADIENT = """
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #6366f1,
                                stop:0.85 #4f46e5,
                                stop:1 #1e293b);
"""

# Menu bar style
MENU_BAR_STYLE = """
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
"""

# Scroll area style (transparent)
SCROLL_AREA_STYLE = "QScrollArea { border: none; background: transparent; }"

# Text colors
TEXT_HEADER = "white"                          # Hex ID
TEXT_SUBTITLE = "rgba(255, 255, 255, 180)"     # Title
TEXT_PRIMARY = "#e2e8f0"                       # Main values (body)
TEXT_SECONDARY = "#94a3b8"                     # Labels (e.g., "Uptime:", "Indoor:")

# Font styles (combined for easy use)
FONT_HEX_ID = f"font-size: 40px; font-weight: bold; font-family: {FONT_FAMILY};"
FONT_TITLE = f"font-size: 20px; font-family: {FONT_FAMILY};"
FONT_BODY = f"font-size: 48px; font-weight: bold; font-family: {FONT_FAMILY}; padding: 30px;"
FONT_LABEL = f"font-size: 20px; font-weight: bold; font-family: {FONT_FAMILY};"
FONT_VALUE = f"font-size: 22px; font-family: {FONT_FAMILY};"

# Unified tile stylesheet (applied in DashboardView)
UNIFIED_TILE_STYLE = f"""
    SimpleTextTile, MultilineTile {{
        background: {TILE_BG};
        border-radius: {TILE_RADIUS};
        border: 1px solid {TILE_BORDER};
    }}
    SimpleTextTile:hover, MultilineTile:hover {{
        border: 1px solid {TILE_HOVER_BORDER};
        background: {TILE_HOVER_BG};
    }}
"""

# Dashboard stylesheet
DASHBOARD_STYLE = f"background-color: {DASHBOARD_BG};"
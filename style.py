"""
Created on Thu Jan  5 16:04:05 2026
@author: kmac3
@author: Grok 4.0
# ================================
# style.py
# ================================
# File version: v1.0.6
# Sync'd to dashboard release: v3.9.0
# Description: Single source of truth for all visual styling
#
# Feature Update: v1.0.4
# ✅ Header ribbon now has rounded top corners only (bottom square)
# ================================
"""

# Font family (system-safe, Spyder-like)
FONT_FAMILY = "Consolas, 'Courier New', monospace"

# Spyder Dark palette
DASHBOARD_BG = "#19232D"
TILE_BG = "#2B2B2B"
#TILE_BORDER = "#404040"
TILE_BORDER = "#5294E2"
TILE_HOVER_BORDER = "#5294E2"
TILE_HOVER_BG = "#3A3A3A"
TILE_RADIUS = "5px"
# Header gradient — top corners rounded only
HEADER_GRADIENT = f"""
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #5294E2,
                                stop:0.5 #3D6FB0,
                                stop:1 #2B2B2B);
    border-top-left-radius: {TILE_RADIUS};
    border-top-right-radius: {TILE_RADIUS};
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
    overflow: hidden;
    border-bottom: 1px solid {TILE_BORDER};
"""

# Header label styles
HEADER_STYLE_LINE_1 = f"color: #FFFFFF; font-size: 40px; font-weight: bold; font-family: {FONT_FAMILY};"
HEADER_STYLE_LINE_2 = f"color: rgba(255, 255, 255, 180); font-size: 20px; font-family: {FONT_FAMILY};"

# Body style
BODY_STYLE = f"color: #FFFFFF; font-size: 48px; font-weight: bold; font-family: {FONT_FAMILY}; padding: 5px;"
# Text colors
TEXT_HEADER = "#FFFFFF"
TEXT_SUBTITLE = "#BBBBBB"
TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#BBBBBB"

# Font styles
FONT_HEX_ID = f"font-size: 40px; font-weight: bold; font-family: {FONT_FAMILY};"
FONT_TITLE = f"font-size: 20px; font-family: {FONT_FAMILY};"
FONT_BODY = f"font-size: 48px; font-weight: bold; font-family: {FONT_FAMILY}; padding: 30px;"
FONT_LABEL = f"font-size: 20px; font-weight: bold; font-family: {FONT_FAMILY};"
FONT_VALUE = f"font-size: 22px; font-family: {FONT_FAMILY};"

# hex-id
HEADER_STYLE_LINE_1 = f"""
    color: {TEXT_HEADER}; {FONT_HEX_ID};
    background: {TILE_BG};
    border: 0;
"""
# title
HEADER_STYLE_LINE_2 = f"""
    color: {TEXT_SUBTITLE}; {FONT_TITLE};
    background: {TILE_BG};
    border: 0;
    border-radius : 0;
"""

# Menu bar style
MENU_BAR_STYLE = """
    QMenuBar {
        background-color: #19232D;
        color: #DDDDDD;
        padding: 6px;
        border-bottom: 1px solid #404040;
    }
    QMenuBar::item {
        padding: 6px 18px;
        background: transparent;
    }
    QMenuBar::item:selected {
        background-color: #5294E2;
        border-radius: 6px;
        color: white;
    }
    QMenu {
        background-color: #2B2B2B;
        color: #DDDDDD;
        border: 1px solid #404040;
    }
    QMenu::item {
        padding: 6px 30px 6px 36px;
    }
    QMenu::item:selected {
        background-color: #5294E2;
        color: white;
    }
"""
# Scroll area
SCROLL_AREA_STYLE = "QScrollArea { border: none; background: transparent; }"

# Unified tile stylesheet
#UNIFIED_TILE_STYLE = f"""
#    SimpleTextTile, MultilineTile, DualTextTile, SystemOutTile {{
#        background: {TILE_BG};
#        border-radius: {TILE_RADIUS};
#        border: 1px solid {TILE_BORDER};
#    }}
#    SimpleTextTile:hover, MultilineTile:hover, DualTextTile:hover, SystemOutTile:hover {{
#        border: 1px solid {TILE_HOVER_BORDER};
#        background: {TILE_HOVER_BG};
#    }}
#"""

# Dashboard stylesheet
#DASHBOARD_STYLE = f"background-color: {DASHBOARD_BG}; border: 2px solid blue;"
DASHBOARD_STYLE = f"background-color: {DASHBOARD_BG}; border: 0px"
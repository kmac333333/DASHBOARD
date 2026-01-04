# Dynamic Indexed MQTT Dashboard

A modern, responsive PyQt6-based dashboard for visualizing MQTT data, system metrics, and custom tiles.

**Version**: v3.8.6 (January 2026)  
**Author**: kmac3 (with assistance from Grok 4.0)

## Overview

This dashboard provides a flexible, grid-based UI for monitoring real-time data from:
- MQTT topics (e.g., temperature sensors)
- System properties (uptime, CPU, memory)
- Custom static or dynamic tiles

Tiles are defined in `layout.json` and automatically laid out in an 8-column responsive grid.

## Features

- **Live MQTT Updates** – Subscribe to any topic with optional F→C conversion
- **System Health Tile** – Shows MQTT status, uptime, CPU, memory
- **Dual Text Tile** – Indoor/outdoor temp comparison with value-based coloring
- **System Out Tile** – Console-style debug output
- **Auto-Reload** – Detects external changes to `layout.json` with debounced prompt
- **Save / Force Default Layout** – Persist or reset configuration
- **Add Static Tile** – Quick tile creation via dialog
- **Editable Titles** – Click any tile title to rename
- **Centralized Styling** – All colors, fonts, gradients in `style.py`

## Requirements

- Python 3.9+
- PyQt6
- paho-mqtt
- psutil

Install dependencies:
```bash
pip install PyQt6 paho-mqtt psutil
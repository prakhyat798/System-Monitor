# NEXUS System Monitor

A modern, real-time hardware monitoring application for Windows — built with Python and CustomTkinter.

![NEXUS Monitor](https://img.shields.io/badge/platform-Windows-blue) ![Python](https://img.shields.io/badge/python-3.10%2B-brightgreen) ![License](https://img.shields.io/badge/license-MIT-purple)

## Features

- **CPU** — Load gauge, clock speed, core count, temperature & wattage
- **GPU** — Temperature, power draw, utilization %, core clock (NVIDIA RTX via LHM)
- **RAM** — Usage gauge with GB breakdown
- **Battery** — Charge gauge, charging status, time remaining
- **Floating Overlay** — Always-on-top compact bar showing all key stats at a glance
- **System Tray** — Runs silently in the background; right-click to show/quit
- **PERF Toggle** — Expandable GPU performance panel (utilization + clock speed)
- **Live refresh** every 500 ms

## Screenshots

> Modern dark-navy UI with 4-layer neon glow arc gauges

## Requirements

| Dependency | Purpose |
|---|---|
| Python 3.10+ | Runtime |
| `customtkinter` | Modern UI framework |
| `psutil` | CPU / RAM / Battery readings |
| `pythonnet` | .NET bridge for LibreHardwareMonitor |
| `pystray` | System tray icon |
| `Pillow` | Tray icon image generation |
| `LibreHardwareMonitorLib.dll` | Hardware sensor access (included) |

## Installation

```bash
pip install customtkinter psutil pythonnet pystray Pillow
```

## Usage

> **Admin privileges are required** to read hardware sensors via LibreHardwareMonitor.

### Option A — Double-click launcher (recommended)
Run **`Start Monitor.vbs`** — it auto-elevates to admin and starts the app in the background.

### Option B — Manual
```bash
# Run as Administrator in PowerShell / CMD
python status_monitor.py
```

## Project Structure

```
system-monitor/
├── status_monitor.py          # Main application
├── Start Monitor.vbs          # Auto-elevate launcher
├── LibreHardwareMonitor/      # LHM DLL (required for GPU/CPU sensors)
│   └── LibreHardwareMonitorLib.dll
└── monitor_error.log          # Runtime log (auto-generated)
```

## How it works

- **Sensor polling** runs in a background thread via `LibreHardwareMonitor`, updating shared caches protected by `threading.Lock()`
- **UI** is built with `CustomTkinter` (`CTkFrame`, `CTkLabel`, `CTkSwitch`) on a `ctk.CTk()` root
- **Arc gauges** are drawn on a `tk.Canvas` with 4-layer neon glow (widths 30→24→18→10 px)
- **Overlay** is a `tk.Toplevel` with `wm_overrideredirect(True)` — always on top, draggable
- **Tray icon** runs in its own thread via `pystray`

## Notes

- GPU prioritizes **NVIDIA** hardware; Intel UHD integrated graphics is ignored
- Closing the window hides it to tray — use tray → Quit to exit fully
- The `.vbs` launcher uses `pythonw.exe` so no console window appears

## License

MIT

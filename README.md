# ⚡ NEXUS System Monitor

A modern, real-time hardware monitoring application for Windows — built with Python and CustomTkinter. Features a sleek dark-navy UI with neon glow arc gauges, a floating overlay widget, and system tray integration.

![Platform](https://img.shields.io/badge/platform-Windows-blue) ![Python](https://img.shields.io/badge/python-3.10%2B-brightgreen) ![License](https://img.shields.io/badge/license-MIT-purple) ![UI](https://img.shields.io/badge/UI-CustomTkinter-blueviolet)

---

## ✨ Features

| Feature | Description |
|---|---|
| **CPU Monitoring** | Load gauge, clock speed (GHz), core count, temperature & wattage |
| **GPU Monitoring** | Temperature, power draw (W), utilization %, core clock (NVIDIA / AMD / Intel via LHM) |
| **RAM Usage** | Real-time usage gauge with GB breakdown (used / total) |
| **Battery** | Charge gauge, charging/discharging status, estimated time remaining |
| **Floating Overlay** | Always-on-top compact draggable bar showing all key stats at a glance |
| **System Tray** | Runs silently in background with live CPU temp icon; right-click to show/quit |
| **PERF Toggle** | Expandable GPU performance panel (utilization + clock speed) |
| **Auto-Elevation** | Automatically requests admin privileges via UAC on launch |
| **Auto-Install** | First-time setup automatically installs missing Python dependencies |
| **Live Refresh** | All stats update every 500 ms |

---

## 🎨 UI Highlights

- Dark-navy themed interface (`#0f1023` base)
- **4-layer neon glow** arc gauges (widths 30→24→18→10 px)
- Color-coded temperature warnings: 🟢 Green (<60°C) → 🟡 Amber (<85°C) → 🔴 Red (≥85°C)
- Draggable floating overlay with right-click context menu
- System tray icon dynamically updates with live CPU temperature

---

## 📦 Requirements

| Dependency | Purpose |
|---|---|
| Python 3.10+ | Runtime |
| `customtkinter` | Modern dark-themed UI framework |
| `psutil` | CPU / RAM / Battery readings |
| `pythonnet` | .NET bridge for LibreHardwareMonitor |
| `pystray` | System tray icon |
| `Pillow` | Tray icon image generation |
| `wmi` | WMI-based sensor fallback |
| `pywin32` | Windows API access |
| `LibreHardwareMonitorLib.dll` | Hardware sensor access (included in repo) |

---

## 🚀 Installation

### Quick Setup (Recommended)
```bash
git clone https://github.com/prakhyat798/System-Monitor.git
cd System-Monitor
```
Then simply double-click **`Start Monitor.vbs`** — it will auto-elevate to admin and install any missing dependencies on first run.

### Manual Setup
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install customtkinter psutil pythonnet pystray pillow wmi pywin32
```

---

## ▶️ Usage

> **Admin privileges are required** to read hardware sensors via LibreHardwareMonitor.

### Option A — Double-click launcher (Recommended)
Run **`Start Monitor.vbs`** — it auto-elevates to admin and starts the app in the background (no console window).

### Option B — Manual
```powershell
# Run as Administrator in PowerShell / CMD
python status_monitor.py
```

### Option C — Setup script
```powershell
# Run setup.bat to install dependencies and configure
setup.bat
```

---

## 📁 Project Structure

```
System-Monitor/
├── status_monitor.py              # Main application (1180+ lines)
├── Start Monitor.vbs              # Auto-elevate VBS launcher
├── setup.bat                      # Dependency installer script
├── requirements.txt               # Python dependencies
├── System Monitor.spec            # PyInstaller build spec
├── diag_lhm.py                    # LHM diagnostic utility
├── diag_output.txt                # Diagnostic output log
├── test_err.py                    # Error testing script
├── .gitignore                     # Git ignore rules
├── LibreHardwareMonitor/          # LHM binaries (included)
│   ├── LibreHardwareMonitorLib.dll
│   ├── LibreHardwareMonitor.exe
│   └── ... (support DLLs)
└── monitor_error.log              # Runtime log (auto-generated)
```

---

## ⚙️ How It Works

### Sensor Polling
- Runs in a **background thread** via `LibreHardwareMonitor`
- Uses a **3-tier fallback system**:
  1. **LHM WMI namespace** — fastest, bypasses pythonnet quirks
  2. **LHM via pythonnet** (.NET CLR bridge) — full per-core sensor access
  3. **ACPI WMI** — basic thermal zone fallback
- Shared caches protected by `threading.Lock()` for thread safety
- Automatic **GPU priority**: NVIDIA > AMD > Intel
- Auto-reinitializes LHM after consecutive sensor errors

### UI Layer
- Built with **CustomTkinter** (`CTkFrame`, `CTkLabel`, `CTkSwitch`) on a `ctk.CTk()` root
- **Arc gauges** drawn on `tk.Canvas` with 4-layer neon glow effect
- **Floating overlay** is a `tk.Toplevel` with `wm_overrideredirect(True)` — always on top, draggable
- **System tray icon** runs in its own thread via `pystray`, with live temperature display

---

## 📝 Notes

- GPU monitoring prioritizes **NVIDIA** GPUs; AMD is second priority; Intel integrated is lowest
- Closing the main window **hides it to system tray** — use Tray → Quit to exit fully
- The `.vbs` launcher uses `pythonw.exe` so no console window appears
- If CPU temperature shows `--`, check if **Core Isolation / Memory Integrity (HVCI)** is enabled in Windows Security — it can block the LHM kernel driver
- Runtime logs are written to `monitor_error.log` for debugging

---

## 🛠️ Building Executable

To build a standalone `.exe` using PyInstaller:
```bash
pip install pyinstaller
pyinstaller "System Monitor.spec"
```

The output will be in the `dist/` folder.

---

## 📄 License

MIT

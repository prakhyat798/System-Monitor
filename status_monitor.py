"""
System Monitor â€” self-elevating, standalone, no third-party tools running.
On first launch it requests admin via UAC (needed for CPU temp).
After that it opens fully with live CPU/RAM/Battery/Temp.
"""

import sys, os, ctypes, subprocess, pathlib, traceback

# â”€â”€â”€ Self-elevation â€” runs BEFORE any UI or heavy imports â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def _is_admin():
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False

if not _is_admin():
    # Show a friendly message â€” use "Start Monitor.vbs" to launch with admin
    import tkinter as tk
    from tkinter import messagebox
    _r = tk.Tk(); _r.withdraw()
    messagebox.showwarning(
        "Admin Required",
        "Please launch via  'Start Monitor.vbs'  for full temperature reading.\n\n"
        "Double-click it in the same folder as this script."
    )
    _r.destroy()
    sys.exit(0)


# â”€â”€â”€ From here we are guaranteed to be running as Administrator â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_REQUIRED_PACKAGES = ["customtkinter", "psutil", "pystray", "pillow", "wmi", "pywin32", "pythonnet"]

def _ensure_dependencies():
    missing = []
    for pkg_import, pkg_pip in [
        ("customtkinter", "customtkinter"),
        ("psutil", "psutil"),
        ("pystray", "pystray"),
        ("PIL", "pillow"),
        ("wmi", "wmi"),
        ("win32api", "pywin32"),
        ("pythonnet", "pythonnet")
    ]:
        try:
            __import__(pkg_import)
        except ImportError:
            missing.append(pkg_pip)
            
    if not missing:
        return

    try:
        import tkinter as _tk
        from tkinter import ttk as _ttk
        root = _tk.Tk()
        root.title("System Monitor — First-Time Setup")
        root.geometry("440x190")
        root.resizable(False, False)
        root.configure(bg="#0f1023")

        # Center window on screen
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry(f"440x190+{(sw-440)//2}+{(sh-190)//2}")

        lbl = _tk.Label(
            root,
            text="Setting up System Monitor for first-time use...\nInstalling required libraries automatically. Please wait.",
            fg="#e8eeff", bg="#0f1023", font=("Segoe UI", 10, "bold"), justify="center"
        )
        lbl.pack(pady=(25, 15))

        pbar = _ttk.Progressbar(root, mode="indeterminate", length=320)
        pbar.pack(pady=10)
        pbar.start(10)

        status_lbl = _tk.Label(
            root,
            text=f"Installing: {', '.join(missing)}...",
            fg="#64748b", bg="#0f1023", font=("Segoe UI", 8)
        )
        status_lbl.pack(pady=5)

        def _do_install():
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install"] + missing,
                    check=True,
                    creationflags=0x08000000 if os.name == 'nt' else 0
                )
            except Exception:
                pass
            root.after(0, root.destroy)

        import threading
        threading.Thread(target=_do_install, daemon=True).start()
        root.mainloop()
    except Exception:
        pass

_ensure_dependencies()

try:
    import platform, threading, datetime, tkinter as tk
    import customtkinter as ctk
    import psutil
    import win32gui, win32con, win32api
except ImportError as _err:
    import tkinter as _tk
    from tkinter import messagebox as _mb
    _r = _tk.Tk(); _r.withdraw()
    _mb.showerror(
        "Missing Python Package",
        f"System Monitor could not start because a Python dependency is missing:\n\n{_err}\n\n"
        "Please run this command in Terminal/PowerShell to fix it:\n"
        "pip install customtkinter psutil pystray pillow wmi pywin32 pythonnet"
    )
    _r.destroy()
    sys.exit(1)

# Earliest possible log write â€” confirms elevated process reached this point
try:
    with open(pathlib.Path(__file__).parent / "monitor_error.log", "a") as _f:
        _f.write(f"[{datetime.datetime.now()}] Elevated process started â€” imports OK\n")
except Exception:
    pass

# â”€â”€â”€ Logging â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_LOG = pathlib.Path(__file__).parent / "monitor_error.log"

def _write_log(msg):
    try:
        with open(_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now()}] {msg}\n")
    except Exception:
        pass

# â”€â”€â”€ Color Palette â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
BG_DARK   = "#0f1023"   # main window
CARD_BG   = "#141726"   # card surface
CARD_BD   = "#1d2545"   # card border
C_INDIGO  = "#818cf8"   # CPU gauge  (indigo)
C_EMERALD = "#34d399"   # Battery    (emerald)
C_AMBER   = "#f59e0b"   # CPU temp   (amber)
C_PINK    = "#f472b6"   # GPU        (pink)
C_PURPLE  = "#a78bfa"   # RAM        (violet)
C_CYAN    = "#22d3ee"   # header accent
T_BRIGHT  = "#e8eeff"   # primary text
T_MID     = "#64748b"   # secondary text
T_DIM     = "#2a3650"   # dimmed
# â”€ backward-compat aliases (used by OverlayBar + tray code) â”€
BG_CARD      = CARD_BG
BORDER_COLOR = CARD_BD
ACCENT_BLUE  = C_INDIGO
ACCENT_GREEN = C_EMERALD
ACCENT_YELLOW= C_AMBER
ACCENT_RED   = "#ef4444"
ACCENT_PURPLE= C_PURPLE
ACCENT_CYAN  = C_CYAN
ACCENT_AMBER = "#e2a84b"
GPU_BLUE     = C_PINK
TEXT_PRIMARY = T_BRIGHT
TEXT_MUTED   = T_MID

# â”€â”€â”€ Sensor caches â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_temp_cache  = {"value": None, "status": "Reading...", "lock": threading.Lock()}
_gpu_cache   = {"value": None, "status": "Reading...", "lock": threading.Lock()}
_power_cache = {"cpu_w": None, "gpu_w": None,          "lock": threading.Lock()}
_gpu_perf    = {"load": None, "clock": None,            "lock": threading.Lock()}
_lhm_process = None

def _safe_iter(dotnet_collection, label=""):
    """Safely iterate a .NET collection that pythonnet may return as PropertyObject.

    After a system restart the CLR interop layer sometimes hands back a
    non-iterable proxy instead of a real IEnumerable.  We try several
    strategies:
      1. list()           – works when __iter__ is defined
      2. indexed access   – works for IList / array-like objects
      3. GetEnumerator()  – works for raw IEnumerable
    Returns a plain Python list (possibly empty, never raises).
    """
    if dotnet_collection is None:
        return []

    result = None

    # Strategy 1 – normal iteration
    try:
        result = list(dotnet_collection)
        if result:
            return result
    except Exception:
        pass

    # Strategy 2 – index-based access (Count / Length)
    try:
        n = getattr(dotnet_collection, "Count", None)
        if n is None:
            n = getattr(dotnet_collection, "Length", None)
        if n is not None and n > 0:
            result = [dotnet_collection[i] for i in range(n)]
            if result:
                return result
    except Exception:
        pass

    # Strategy 3 – raw .NET enumerator
    try:
        enum = dotnet_collection.GetEnumerator()
        items = []
        while enum.MoveNext():
            items.append(enum.Current)
        if items:
            return items
    except Exception:
        pass

    # If Strategy 1 returned an empty-but-valid list, return that
    if result is not None:
        return result

    if label:
        _write_log(f"_safe_iter({label}): all strategies failed, "
                   f"type={type(dotnet_collection)}")
    return []


def _temp_loop():
    import time, gc

    if getattr(sys, 'frozen', False):
        _BASE = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(sys.executable)))
    else:
        _BASE = os.path.dirname(os.path.abspath(__file__))
    LHM_DIR = os.path.join(_BASE, "LibreHardwareMonitor")
    LHM_DLL = os.path.join(LHM_DIR, "LibreHardwareMonitorLib.dll")
    LHM_EXE = os.path.join(LHM_DIR, "LibreHardwareMonitor.exe")

    # ── Hack: Open LibreHardwareMonitor.exe as SYSTEM (100% hidden) ───────
    if os.path.exists(LHM_EXE):
        try:
            import subprocess
            task_name = "SysMon_LHM_Hidden"
            subprocess.run(f'schtasks /create /tn "{task_name}" /tr "\\"{LHM_EXE}\\"" /sc once /st 00:00 /ru SYSTEM /rl HIGHEST /f', shell=True, capture_output=True, creationflags=0x08000000)
            subprocess.run(f'schtasks /run /tn "{task_name}"', shell=True, capture_output=True, creationflags=0x08000000)
            subprocess.run(f'schtasks /delete /tn "{task_name}" /f', shell=True, capture_output=True, creationflags=0x08000000)
            _write_log("Hack: Launched LibreHardwareMonitor.exe via Task Scheduler (SYSTEM) for complete invisibility")
            time.sleep(3)
        except Exception as e:
            _write_log(f"Hack failed: {e}")

    # ── Try WMI LibreHardwareMonitor first (Bypasses pythonnet bugs) ──────
    try:
        import pythoncom, wmi
        pythoncom.CoInitialize()
        w = wmi.WMI(namespace=r"root\LibreHardwareMonitor")
        sensors = w.Sensor()
        if len(sensors) > 0:
            _write_log("Using LibreHardwareMonitor WMI namespace")
            while True:
                try:
                    cpu_t = None
                    gpu_t = None
                    cpu_w = None
                    gpu_w = None
                    gpu_load = None
                    gpu_clock = None
                    
                    for s in w.Sensor():
                        if s.SensorType == "Temperature":
                            if s.Name == "CPU Package" or s.Name == "Core Average": cpu_t = s.Value
                            elif "GPU Core" in s.Name: gpu_t = s.Value
                        elif s.SensorType == "Power":
                            if "CPU Package" in s.Name: cpu_w = s.Value
                            elif "GPU Package" in s.Name: gpu_w = s.Value
                        elif s.SensorType == "Load":
                            if "GPU Core" in s.Name: gpu_load = s.Value
                        elif s.SensorType == "Clock":
                            if "GPU Core" in s.Name: gpu_clock = s.Value
                            
                    with _temp_cache["lock"]:
                        if cpu_t is not None:
                            _temp_cache["value"] = cpu_t
                            _temp_cache["status"] = "LHM · CPU (WMI)"
                        else:
                            _temp_cache["value"] = None
                            _temp_cache["status"] = "No CPU Temp (WMI)"
                    with _gpu_cache["lock"]:
                        _gpu_cache["value"] = gpu_t
                        _gpu_cache["status"] = "GPU (WMI)"
                    with _power_cache["lock"]:
                        _power_cache["cpu_w"] = cpu_w
                        _power_cache["gpu_w"] = gpu_w
                    with _gpu_perf["lock"]:
                        _gpu_perf["load"] = gpu_load
                        _gpu_perf["clock"] = gpu_clock
                except Exception as e:
                    _write_log(f"LHM WMI poll error: {e}")
                time.sleep(1)
    except Exception as e:
        _write_log(f"LHM WMI namespace not available: {e}")

    # ── Primary: LHM via pythonnet – real per-core, 1 s ─────────────────────
    if os.path.exists(LHM_DLL):
        try:
            import pythonnet
            pythonnet.load("netfx")
            import clr
            if LHM_DIR not in sys.path:
                sys.path.append(LHM_DIR)
            clr.AddReference("LibreHardwareMonitorLib")
            from LibreHardwareMonitor.Hardware import Computer, HardwareType, SensorType

            def _open_computer():
                """Create and open a fresh LHM Computer instance."""
                c = Computer()
                c.IsCpuEnabled = True
                c.IsGpuEnabled = True
                c.IsMotherboardEnabled = True
                c.Open()
                return c

            computer = _open_computer()
            _write_log("LHM opened – per-core temps active")

            # ── Find best GPU (NVIDIA > AMD > Intel) ─────────────────────────
            _GPU_PRIORITY = {
                HardwareType.GpuNvidia: 0,
                HardwareType.GpuAmd:    1,
                HardwareType.GpuIntel:  2,
            }
            _GPU_TYPES = tuple(_GPU_PRIORITY)

            def _find_best_gpu():
                """Search top-level and SubHardware; return highest-priority GPU."""
                candidates = []
                for _hw in _safe_iter(computer.Hardware):
                    if _hw.HardwareType in _GPU_TYPES:
                        candidates.append(_hw)
                    for _sub in _safe_iter(_hw.SubHardware):
                        if _sub.HardwareType in _GPU_TYPES:
                            candidates.append(_sub)
                candidates.sort(key=lambda h: _GPU_PRIORITY.get(h.HardwareType, 9))
                if candidates:
                    _write_log(f"GPUs found: {[h.Name for h in candidates]}")
                    return candidates[0]
                return None

            _gpu_hw = _find_best_gpu()
            _consecutive_errors = 0
            _MAX_ERRORS_BEFORE_REINIT = 5

            while True:
                try:
                    hw_list = _safe_iter(computer.Hardware, "computer.Hardware")
                    # One-shot: log hardware enumeration results
                    if not hasattr(_temp_loop, '_hw_diag_done'):
                        _temp_loop._hw_diag_done = True
                        _write_log(f"Hardware list: {len(hw_list)} items, "
                                   f"type(computer.Hardware)={type(computer.Hardware)}")
                        for _h in hw_list:
                            _write_log(f"  HW: {_h.Name} type={_h.HardwareType}")
                        if not hw_list:
                            _write_log("WARNING: computer.Hardware returned EMPTY! "
                                       "Sensors will not be read.")
                    # We will collect CPU-related sensors from all hardware
                    # (CPU itself, or Motherboard/SuperIO fallbacks)
                    cpu_temp_sensors = []
                    cpu_power_sensors = []

                    for hw in hw_list:
                        hw.Update()
                        # Gather sensors from this hardware
                        all_sensors = []
                        all_sensors.extend(_safe_iter(hw.Sensors))
                        for subhw in _safe_iter(hw.SubHardware):
                            subhw.Update()
                            all_sensors.extend(_safe_iter(subhw.Sensors))
                        
                        # One-shot diagnostic for ALL hardware
                        if not hasattr(_temp_loop, '_diag_done'):
                            if hw == hw_list[0]:
                                _write_log("--- FULL SENSOR DUMP ---")
                            _write_log(f"HW: {hw.Name} ({hw.HardwareType}) gave {len(all_sensors)} total sensors")
                            for _s in all_sensors:
                                try:
                                    _write_log(f"  sensor: type={_s.SensorType} "
                                               f"name={_s.Name} val={_s.Value}")
                                except Exception as _se:
                                    pass
                            if hw == hw_list[-1]:
                                _temp_loop._diag_done = True
                                _write_log("--- END SENSOR DUMP ---")

                        for _s in all_sensors:
                            if _s.SensorType == SensorType.Temperature:
                                # If it's on the CPU, or it's on the Mobo and named CPU
                                if hw.HardwareType == HardwareType.Cpu or "CPU" in _s.Name.upper():
                                    if _s.Value is not None and "Distance" not in _s.Name:
                                        cpu_temp_sensors.append(_s)
                            elif _s.SensorType == SensorType.Power:
                                if hw.HardwareType == HardwareType.Cpu or "CPU" in _s.Name.upper():
                                    if _s.Value is not None:
                                        cpu_power_sensors.append(_s)

                    # Evaluate best CPU Temp
                    pkg_t = next((float(s.Value) for s in cpu_temp_sensors if "Package" in s.Name), None)
                    avg_t = next((float(s.Value) for s in cpu_temp_sensors if "Average" in s.Name), None)
                    any_t = next((float(s.Value) for s in cpu_temp_sensors), None)
                    
                    val = pkg_t or avg_t or any_t
                    src = ""
                    if val is not None:
                        src = "LHM · CPU Package" if pkg_t else "LHM · CPU Average" if avg_t else "LHM · CPU Socket"
                    else:
                        # Check if Memory Integrity (HVCI) is blocking the driver
                        try:
                            import winreg
                            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity")
                            enabled, _ = winreg.QueryValueEx(key, "Enabled")
                            winreg.CloseKey(key)
                            if enabled == 1:
                                src = "Blocked by Core Isolation"
                            else:
                                src = "No CPU Temp Sensor"
                        except Exception:
                            src = "No CPU Temp Sensor"

                    with _temp_cache["lock"]:
                        _temp_cache["value"] = val
                        _temp_cache["status"] = src

                    # Evaluate best CPU Power
                    cpu_w = next((float(s.Value) for s in cpu_power_sensors if "Package" in s.Name), None)
                    if cpu_w is None:
                        cpu_w = next((float(s.Value) for s in cpu_power_sensors), None)
                    with _power_cache["lock"]:
                        _power_cache["cpu_w"] = cpu_w

                    # GPU - read from preferred GPU hardware object
                    if _gpu_hw is not None:
                        gpu_sensors = _safe_iter(_gpu_hw.Sensors)
                        gpu_t = next(
                            (float(s.Value) for s in gpu_sensors
                             if s.SensorType == SensorType.Temperature
                             and s.Value is not None),
                            None
                        )
                        gpu_w = next(
                            (float(s.Value) for s in gpu_sensors
                             if s.SensorType == SensorType.Power
                             and s.Value is not None),
                            None
                        )
                        gpu_load = next(
                            (float(s.Value) for s in gpu_sensors
                             if s.SensorType == SensorType.Load
                             and "Core" in s.Name and s.Value is not None),
                            None
                        )
                        gpu_clock = next(
                            (float(s.Value) for s in gpu_sensors
                             if s.SensorType == SensorType.Clock
                             and "Core" in s.Name and s.Value is not None),
                            None
                        )
                        with _gpu_cache["lock"]:
                            _gpu_cache["value"]  = gpu_t
                            _gpu_cache["status"] = (_gpu_hw.Name or "GPU")[:30]
                        with _power_cache["lock"]:
                            _power_cache["gpu_w"] = gpu_w
                        with _gpu_perf["lock"]:
                            _gpu_perf["load"]  = gpu_load
                            _gpu_perf["clock"] = gpu_clock
                    else:
                        # Try re-discovering GPU (may power on later)
                        _gpu_hw = _find_best_gpu()

                    # Successful poll – reset error counter
                    _consecutive_errors = 0

                except Exception as e:
                    _consecutive_errors += 1
                    import traceback; _write_log(f"LHM poll error ({_consecutive_errors}): {e}\n{traceback.format_exc()}")

                    # After several consecutive failures, re-init the Computer
                    # object — this recovers from stale .NET proxies after reboot
                    if _consecutive_errors >= _MAX_ERRORS_BEFORE_REINIT:
                        _write_log("Too many consecutive errors – re-initialising LHM…")
                        try:
                            computer.Close()
                        except Exception:
                            pass
                        try:
                            time.sleep(2)
                            computer = _open_computer()
                            _gpu_hw = _find_best_gpu()
                            _consecutive_errors = 0
                            _write_log("LHM re-initialised successfully")
                        except Exception as re_err:
                            _write_log(f"LHM re-init failed: {re_err}")
                            time.sleep(5)

                time.sleep(1)
            return   # never reached if LHM stays alive
        except Exception as e:
            _write_log(f"LHM init failed, falling back to ACPI: {e}")

    # â”€â”€ Fallback: ACPI WMI â€” 2 s â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    while True:
        try:
            import pythoncom, wmi, io
            pythoncom.CoInitialize()
            try:
                w     = wmi.WMI(namespace="root\\wmi")
                zones = w.MSAcpi_ThermalZoneTemperature()
                if zones:
                    best = max((z.CurrentTemperature / 10.0) - 273.15 for z in zones)
                    with _temp_cache["lock"]:
                        _temp_cache["value"]  = best
                        _temp_cache["status"] = "ACPI thermal zone"
                else:
                    with _temp_cache["lock"]:
                        _temp_cache["value"]  = None
                        _temp_cache["status"] = "No ACPI zones"
                zones = None; w = None
            finally:
                gc.collect()
                _old, sys.stderr = sys.stderr, io.StringIO()
                try:    pythoncom.CoUninitialize()
                finally: sys.stderr = _old
        except Exception as e:
            with _temp_cache["lock"]:
                _temp_cache["value"]  = None
                _temp_cache["status"] = "ACPI error"
        time.sleep(2)

def get_cpu_temp():
    with _temp_cache["lock"]:
        return _temp_cache["value"], _temp_cache["status"]

def get_gpu_temp():
    with _gpu_cache["lock"]:
        return _gpu_cache["value"], _gpu_cache["status"]

def get_power():
    with _power_cache["lock"]:
        return _power_cache["cpu_w"], _power_cache["gpu_w"]

def get_gpu_perf():
    with _gpu_perf["lock"]:
        return _gpu_perf["load"], _gpu_perf["clock"]



# â”€â”€â”€ System Tray Icon â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
try:
    import pystray
    from PIL import Image as PilImage, ImageDraw, ImageFont
    _PYSTRAY_OK = True
except ImportError:
    _PYSTRAY_OK = False

_tray_icon = None

_FONT_CACHE = {}
def _get_font(size=26):
    if size not in _FONT_CACHE:
        for path in [
            r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\verdana.ttf",
        ]:
            try:
                _FONT_CACHE[size] = ImageFont.truetype(path, size)
                break
            except Exception:
                pass
        if size not in _FONT_CACHE:
            _FONT_CACHE[size] = ImageFont.load_default()
    return _FONT_CACHE[size]

def _make_tray_img(cpu_val, gpu_val):
    """Render CPU temp as a 64Ã—64 tray icon image."""
    img  = PilImage.new("RGBA", (64, 64), (15, 17, 23, 255))
    draw = ImageDraw.Draw(img)
    if cpu_val is not None:
        t = int(cpu_val)
        if t < 60:   col = (61,  219, 161, 255)
        elif t < 85: col = (247, 201,  72, 255)
        else:        col = (247,  88,  79, 255)
        text = str(t)
        font = _get_font(26 if t < 100 else 22)
        try:
            bb = draw.textbbox((0, 0), text, font=font)
            tw, th = bb[2]-bb[0], bb[3]-bb[1]
        except Exception:
            tw, th = 30, 26
        draw.text(((64-tw)//2, (64-th)//2 - 2), text, fill=col, font=font)
        draw.text((0, 48), "CPU", fill=(107, 114, 128, 200),
                  font=_get_font(12))
    else:
        draw.text((16, 18), "--", fill=(107, 114, 128, 255), font=_get_font(26))
    return img

def _tray_tooltip(cpu_val, gpu_val, cpu_pct):
    parts = ["System Monitor"]
    if cpu_val  is not None: parts.append(f"CPU Temp: {cpu_val:.0f}°C")
    if gpu_val  is not None: parts.append(f"GPU Temp: {gpu_val:.0f}°C")
    if cpu_pct  is not None: parts.append(f"CPU Load: {cpu_pct:.0f}%")
    return "  |  ".join(parts)

def start_tray(app):
    """Launch pystray in a background daemon thread."""
    if not _PYSTRAY_OK:
        return
    global _tray_icon

    def _on_show(icon, item):
        app.root.after(0, app.show_window)

    def _on_toggle_overlay(icon, item):
        app.root.after(0, app.overlay.toggle)

    def _on_quit(icon, item):
        icon.stop()
        app.root.after(0, app.quit_app)

    menu = pystray.Menu(
        pystray.MenuItem("Show / Hide Monitor", _on_show, default=True),
        pystray.MenuItem("Toggle Floating Widget", _on_toggle_overlay),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", _on_quit),
    )
    _tray_icon = pystray.Icon(
        "system_monitor",
        _make_tray_img(None, None),
        "System Monitor",
        menu,
    )
    threading.Thread(target=_tray_icon.run, daemon=True).start()

def update_tray(cpu_val, gpu_val, cpu_pct):
    if _tray_icon is None or not _PYSTRAY_OK:
        return
    try:
        _tray_icon.icon  = _make_tray_img(cpu_val, gpu_val)
        _tray_icon.title = _tray_tooltip(cpu_val, gpu_val, cpu_pct)
    except Exception:
        pass

# ─── Floating Overlay Bar ──────────────────────────────────────────────────────────
class OverlayBar:
    """Compact draggable always-on-top stats overlay, supporting HUD and Widget styles."""

    def __init__(self, root, on_show_main, on_quit):
        self._on_show = on_show_main
        self._on_quit = on_quit
        self.root = root
        
        self.win = tk.Toplevel(root)
        self.win.overrideredirect(True)          # no title bar
        self.win.wm_attributes("-topmost", True)
        
        # Default settings (can be modified by status monitor UI)
        self.style_mode = "MSI Afterburner (HUD)"
        self.bg_mode = "Translucent Dark"
        self.opacity = 0.93
        self.font_size_name = "Medium"
        self.locked = False
        
        # Border and inner frame
        self.border = tk.Frame(self.win, bg="#1e2130", padx=1, pady=1)
        self.border.pack(fill="both", expand=True)
        self.inner = tk.Frame(self.border, bg="#0d0f14")
        self.inner.pack(fill="both", expand=True)
        
        self.lbl = {}
        self._all_widgets = []
        
        # Initial build
        self.rebuild_layout(self.style_mode, self.bg_mode, self.opacity, self.font_size_name)
        
        # Context menu
        self._build_menu(root)
        
        # Register default geometry
        self.win.update_idletasks()
        self.reset_position()

    def rebuild_layout(self, style_mode, bg_mode, opacity, font_size_name):
        self.style_mode = style_mode
        self.bg_mode = bg_mode
        self.opacity = opacity
        self.font_size_name = font_size_name
        
        # Clear existing widgets in the inner frame
        for widget in self.inner.winfo_children():
            widget.destroy()
            
        self.lbl = {}
        self._all_widgets = [self.win, self.border, self.inner]
        
        # Define background colors
        if bg_mode == "Fully Transparent":
            bg_color = "#010101" # transparent color key
            self.win.wm_attributes("-transparentcolor", "#010101")
            self.win.configure(bg=bg_color)
            self.border.configure(bg=bg_color, padx=0, pady=0)
            self.inner.configure(bg=bg_color, padx=5, pady=5)
        else: # Translucent Dark
            bg_color = "#090a12"
            self.win.wm_attributes("-transparentcolor", "") # clear transparent color key
            self.win.configure(bg=bg_color)
            self.border.configure(bg="#1d2545", padx=1, pady=1)
            self.inner.configure(bg=bg_color, padx=12, pady=6)
            
        self.win.wm_attributes("-alpha", opacity)
        
        # Determine sizes
        sizes = {
            "Small": (8, 9),
            "Medium": (10, 11),
            "Large": (12, 13),
            "Extra Large": (14, 16)
        }
        lbl_sz, val_sz = sizes.get(font_size_name, (10, 11))
        
        font_lbl = ("Segoe UI", lbl_sz, "bold")
        font_val = ("Segoe UI", val_sz, "bold")
        font_mono_val = ("Consolas", val_sz, "bold")
        
        def row(parent):
            f = tk.Frame(parent, bg=bg_color)
            f.pack(fill="x")
            self._all_widgets.append(f)
            return f
            
        if style_mode == "MSI Afterburner (HUD)":
            # 1. CPU line
            r_cpu = row(self.inner)
            lbl_cpu = tk.Label(r_cpu, text="CPU  ", bg=bg_color, fg=C_CYAN, font=font_lbl)
            lbl_cpu.pack(side="left")
            self._all_widgets.append(lbl_cpu)
            
            self.lbl["cpu_t"] = tk.Label(r_cpu, text="--°C", bg=bg_color, fg=ACCENT_YELLOW, font=font_mono_val)
            self.lbl["cpu_t"].pack(side="left")
            self._all_widgets.append(self.lbl["cpu_t"])
            
            d1 = tk.Label(r_cpu, text=" | ", bg=bg_color, fg="#374151", font=font_lbl)
            d1.pack(side="left")
            self._all_widgets.append(d1)
            
            self.lbl["cpu_p"] = tk.Label(r_cpu, text="--%", bg=bg_color, fg=C_EMERALD, font=font_mono_val)
            self.lbl["cpu_p"].pack(side="left")
            self._all_widgets.append(self.lbl["cpu_p"])
            
            d2 = tk.Label(r_cpu, text=" | ", bg=bg_color, fg="#374151", font=font_lbl)
            d2.pack(side="left")
            self._all_widgets.append(d2)
            
            self.lbl["cpu_w"] = tk.Label(r_cpu, text="--W", bg=bg_color, fg=C_AMBER, font=font_mono_val)
            self.lbl["cpu_w"].pack(side="left")
            self._all_widgets.append(self.lbl["cpu_w"])
            
            d3 = tk.Label(r_cpu, text=" | ", bg=bg_color, fg="#374151", font=font_lbl)
            d3.pack(side="left")
            self._all_widgets.append(d3)
            
            self.lbl["freq"] = tk.Label(r_cpu, text="--GHz", bg=bg_color, fg=T_MID, font=font_mono_val)
            self.lbl["freq"].pack(side="left")
            self._all_widgets.append(self.lbl["freq"])
            
            # 2. GPU line
            r_gpu = row(self.inner)
            lbl_gpu = tk.Label(r_gpu, text="GPU  ", bg=bg_color, fg=C_PINK, font=font_lbl)
            lbl_gpu.pack(side="left")
            self._all_widgets.append(lbl_gpu)
            
            self.lbl["gpu_t"] = tk.Label(r_gpu, text="--°C", bg=bg_color, fg=ACCENT_BLUE, font=font_mono_val)
            self.lbl["gpu_t"].pack(side="left")
            self._all_widgets.append(self.lbl["gpu_t"])
            
            d4 = tk.Label(r_gpu, text=" | ", bg=bg_color, fg="#374151", font=font_lbl)
            d4.pack(side="left")
            self._all_widgets.append(d4)
            
            self.lbl["gpu_p"] = tk.Label(r_gpu, text="--%", bg=bg_color, fg=C_EMERALD, font=font_mono_val)
            self.lbl["gpu_p"].pack(side="left")
            self._all_widgets.append(self.lbl["gpu_p"])
            
            d5 = tk.Label(r_gpu, text=" | ", bg=bg_color, fg="#374151", font=font_lbl)
            d5.pack(side="left")
            self._all_widgets.append(d5)
            
            self.lbl["gpu_w"] = tk.Label(r_gpu, text="--W", bg=bg_color, fg="#7baef7", font=font_mono_val)
            self.lbl["gpu_w"].pack(side="left")
            self._all_widgets.append(self.lbl["gpu_w"])
            
            d6 = tk.Label(r_gpu, text=" | ", bg=bg_color, fg="#374151", font=font_lbl)
            d6.pack(side="left")
            self._all_widgets.append(d6)
            
            self.lbl["gpu_c"] = tk.Label(r_gpu, text="--MHz", bg=bg_color, fg=C_PURPLE, font=font_mono_val)
            self.lbl["gpu_c"].pack(side="left")
            self._all_widgets.append(self.lbl["gpu_c"])
            
            # 3. RAM line
            r_ram = row(self.inner)
            lbl_ram = tk.Label(r_ram, text="MEM  ", bg=bg_color, fg=C_PURPLE, font=font_lbl)
            lbl_ram.pack(side="left")
            self._all_widgets.append(lbl_ram)
            
            self.lbl["ram"] = tk.Label(r_ram, text="--GB / --GB", bg=bg_color, fg=C_PURPLE, font=font_mono_val)
            self.lbl["ram"].pack(side="left")
            self._all_widgets.append(self.lbl["ram"])
            
            # 4. Battery line
            r_bat = row(self.inner)
            lbl_bat = tk.Label(r_bat, text="BAT  ", bg=bg_color, fg=C_EMERALD, font=font_lbl)
            lbl_bat.pack(side="left")
            self._all_widgets.append(lbl_bat)
            
            self.lbl["bat"] = tk.Label(r_bat, text="--%", bg=bg_color, fg=C_EMERALD, font=font_mono_val)
            self.lbl["bat"].pack(side="left")
            self._all_widgets.append(self.lbl["bat"])
            
        else: # Compact Widget Bar
            def metric(parent, key, abbr, val_color, unit=""):
                a = tk.Label(parent, text=abbr, bg=bg_color, fg="#5c6a85", font=font_lbl)
                a.pack(side="left")
                v = tk.Label(parent, text="--"+unit, bg=bg_color, fg=val_color, font=font_mono_val)
                v.pack(side="left", padx=(2, 10))
                self.lbl[key] = (v, unit)
                self._all_widgets += [a, v]
                
            r1 = row(self.inner)
            metric(r1, "cpu_t", "CPU",  ACCENT_YELLOW, "°")
            metric(r1, "cpu_w", "W",    "#e2a84b",     "W")
            metric(r1, "gpu_t", "GPU",  ACCENT_BLUE,   "°")
            metric(r1, "gpu_w", "W",    "#7baef7",     "W")
            metric(r1, "cpu_p", "LOAD", ACCENT_GREEN,  "%")
            
            sep = tk.Frame(self.inner, bg="#1c2545" if bg_mode != "Fully Transparent" else bg_color, height=1)
            sep.pack(fill="x", pady=2)
            self._all_widgets.append(sep)
            
            r2 = row(self.inner)
            metric(r2, "ram",  "RAM",  ACCENT_PURPLE, "G")
            metric(r2, "bat",  "BAT",  ACCENT_GREEN,  "%")
            metric(r2, "freq", "GHz",  T_MID,         "")

        # Re-apply window bindings and locks
        self._bind_drag()
        self.set_lock(self.locked)

    def _set(self, key, value, color=None):
        if self.style_mode == "Compact Widget Bar":
            lbl, unit = self.lbl[key]
            lbl.config(text=f"{value}{unit}")
            if color:
                lbl.config(fg=color)
        else:
            lbl = self.lbl.get(key)
            if lbl:
                lbl.config(text=str(value))
                if color:
                    lbl.config(fg=color)

    def _tc(self, v):
        if v is None: return T_MID
        if v < 60:    return C_EMERALD
        if v < 85:    return C_AMBER
        return "#ef4444"

    def update(self, cpu_t, gpu_t, cpu_p, ram_gb, bat_pct, freq_ghz,
               cpu_w=None, gpu_w=None, gpu_load=None, gpu_clock=None):
        
        if self.style_mode == "MSI Afterburner (HUD)":
            # CPU Temp
            if cpu_t is not None:
                self.lbl["cpu_t"].config(text=f"{cpu_t:.0f}°C", fg=self._tc(cpu_t))
            else:
                self.lbl["cpu_t"].config(text="--°C", fg=T_MID)
                
            # CPU Load
            if cpu_p is not None:
                self.lbl["cpu_p"].config(text=f"{cpu_p:.0f}%", fg=self._tc(cpu_p))
            else:
                self.lbl["cpu_p"].config(text="--%", fg=T_MID)
                
            # CPU Power
            if cpu_w is not None:
                self.lbl["cpu_w"].config(text=f"{cpu_w:.0f}W", fg=C_AMBER)
            else:
                self.lbl["cpu_w"].config(text="--W", fg=T_MID)
                
            # CPU Clock
            if freq_ghz is not None:
                self.lbl["freq"].config(text=f"{freq_ghz:.2f}GHz", fg=T_MID)
            else:
                self.lbl["freq"].config(text="--GHz", fg=T_MID)
                
            # GPU Temp
            if gpu_t is not None:
                self.lbl["gpu_t"].config(text=f"{gpu_t:.0f}°C", fg=self._tc(gpu_t))
            else:
                self.lbl["gpu_t"].config(text="--°C", fg=T_MID)
                
            # GPU Load
            if gpu_load is not None:
                self.lbl["gpu_p"].config(text=f"{gpu_load:.0f}%", fg=self._tc(gpu_load))
            else:
                self.lbl["gpu_p"].config(text="--%", fg=T_MID)
                
            # GPU Power
            if gpu_w is not None:
                self.lbl["gpu_w"].config(text=f"{gpu_w:.0f}W", fg="#7baef7")
            else:
                self.lbl["gpu_w"].config(text="--W", fg=T_MID)
                
            # GPU Clock
            if gpu_clock is not None:
                self.lbl["gpu_c"].config(
                    text=f"{gpu_clock/1000:.2f}GHz" if gpu_clock >= 1000 else f"{gpu_clock:.0f}MHz",
                    fg=C_PURPLE
                )
            else:
                self.lbl["gpu_c"].config(text="--MHz", fg=T_MID)
                
            # RAM
            if ram_gb is not None:
                total_ram = psutil.virtual_memory().total / (1024**3)
                self.lbl["ram"].config(text=f"{ram_gb:.1f}GB / {total_ram:.1f}GB")
            else:
                self.lbl["ram"].config(text="--GB / --GB")
                
            # Battery
            if bat_pct is not None:
                self.lbl["bat"].config(text=f"{bat_pct:.0f}%")
            else:
                self.lbl["bat"].config(text="--%")
                
        else: # Compact Widget Bar
            if cpu_t is not None: self._set("cpu_t", f"{cpu_t:.0f}",  self._tc(cpu_t))
            else:                  self._set("cpu_t", "--",           T_MID)
            if cpu_w is not None: self._set("cpu_w", f"{cpu_w:.0f}",  "#e2a84b")
            else:                  self._set("cpu_w", "--",           T_MID)
            if gpu_t is not None: self._set("gpu_t", f"{gpu_t:.0f}",  self._tc(gpu_t))
            else:                  self._set("gpu_t", "--",           T_MID)
            if gpu_w is not None: self._set("gpu_w", f"{gpu_w:.0f}",  "#7baef7")
            else:                  self._set("gpu_w", "--",           T_MID)
            if cpu_p is not None: self._set("cpu_p", f"{cpu_p:.0f}",  self._tc(cpu_p))
            else:                  self._set("cpu_p", "--",           T_MID)
            if ram_gb is not None: self._set("ram",   f"{ram_gb:.1f}", C_PURPLE)
            else:                  self._set("ram",   "--",           T_MID)
            if bat_pct is not None:
                bc = C_EMERALD if bat_pct > 20 else "#ef4444"
                self._set("bat", f"{bat_pct:.0f}", bc)
            else:
                self._set("bat", "--", T_MID)
            if freq_ghz is not None: self._set("freq", f"{freq_ghz:.2f}", T_MID)
            else:                     self._set("freq", "--",              T_MID)
    # â”€â”€ Drag â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _bind_drag(self):
        self._dx = self._dy = 0
        for w in self._all_widgets:
            w.bind("<ButtonPress-1>", self._drag_start)
            w.bind("<B1-Motion>",     self._drag_move)

    def _drag_start(self, e):
        self._dx = e.x_root - self.win.winfo_x()
        self._dy = e.y_root - self.win.winfo_y()

    def _drag_move(self, e):
        self.win.geometry(f"+{e.x_root-self._dx}+{e.y_root-self._dy}")

    def reset_position(self):
        """Place the overlay above the taskbar in the bottom-right corner."""
        self.win.update_idletasks()
        margin = 20
        screen_width = self.win.winfo_screenwidth()
        screen_height = self.win.winfo_screenheight()
        window_width = self.win.winfo_reqwidth()
        window_height = self.win.winfo_reqheight()
        x = max(margin, screen_width - window_width - margin)
        y = max(margin, screen_height - window_height - 60)
        self.win.geometry(f"+{x}+{y}")


    def set_lock(self, locked: bool):
        """Lock/unlock the overlay position. When locked, dragging is disabled."""
        self.locked = locked
        if locked:
            for w in self._all_widgets:
                w.unbind('<ButtonPress-1>')
                w.unbind('<B1-Motion>')
        else:
            self._bind_drag()

    # â”€â”€ Context menu â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _build_menu(self, root):
        m = tk.Menu(root, tearoff=0, bg=BG_CARD, fg=TEXT_PRIMARY,
                    activebackground=ACCENT_BLUE,
                    activeforeground=TEXT_PRIMARY, bd=0)
        m.add_command(label="Show Monitor",  command=self._on_show)
        m.add_separator()
        m.add_command(label="Quit",          command=self._on_quit)
        def _popup(e):
            m.tk_popup(e.x_root, e.y_root)
        for w in self._all_widgets:
            w.bind("<Button-3>", _popup)

    def show(self):
        self.win.deiconify()
        self.win.lift()

    def hide(self):
        self.win.withdraw()

    def toggle(self, state=None):
        if state is True:
            self.show()
        elif state is False:
            self.hide()
        else:
            if self.win.winfo_viewable():
                self.hide()
            else:
                self.show()

# ─── UI Helpers ──────────────────────────────────────────────────────────────────
def _dim_hex(color: str, factor: float) -> str:
    """Return a darker copy of a hex colour (for glow layers)."""
    r = max(0, min(255, int(int(color[1:3], 16) * factor)))
    g = max(0, min(255, int(int(color[3:5], 16) * factor)))
    b = max(0, min(255, int(int(color[5:7], 16) * factor)))
    return f"#{r:02x}{g:02x}{b:02x}"

def arc_color(pct: float) -> str:
    if pct < 60:  return C_EMERALD
    if pct < 85:  return C_AMBER
    return "#ef4444"

def draw_gauge(canvas, value, color, size=114):
    """240° speedometer arc with 4-layer neon glow."""
    canvas.delete("all")
    cx = cy = size // 2
    r = cx - 16
    # Background track
    canvas.create_arc(cx-r, cy-r, cx+r, cy+r,
                      start=225, extent=-240,
                      style="arc", outline="#111826", width=17)
    if value > 0:
        ext = -(value / 100) * 240
        # Glow layers — wide+dim  →  narrow+bright
        for w, fac in ((30, 0.15), (24, 0.35), (18, 0.60)):
            canvas.create_arc(cx-r, cy-r, cx+r, cy+r,
                              start=225, extent=ext, style="arc",
                              outline=_dim_hex(color, fac), width=w)
        # Crisp bright arc on top
        canvas.create_arc(cx-r, cy-r, cx+r, cy+r,
                          start=225, extent=ext, style="arc",
                          outline=color, width=10)
    canvas.create_text(cx, cy - 7, text=f"{int(value)}",
                       fill=T_BRIGHT, font=("Segoe UI", 22, "bold"))
    canvas.create_text(cx, cy + 14, text="%",
                       fill=T_MID, font=("Segoe UI", 9))

draw_ring = draw_gauge   # keep alias for any remaining references


# \u2500\u2500\u2500 Main App \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
def _hotkey_loop(app):
    import ctypes
    from ctypes import wintypes
    import win32con
    
    user32 = ctypes.windll.user32
    
    # MOD_CONTROL = 0x0002, MOD_SHIFT = 0x0004
    MOD_CTRL_SHIFT = 0x0002 | 0x0004
    
    # Register hotkeys
    # ID 1: Ctrl+Shift+O (Show/Hide)
    # ID 2: Ctrl+Shift+L (Lock/Unlock)
    # ID 3: Ctrl+Shift+R (Reset position)
    user32.RegisterHotKey(None, 1, MOD_CTRL_SHIFT, 0x4F) # O
    user32.RegisterHotKey(None, 2, MOD_CTRL_SHIFT, 0x4C) # L
    user32.RegisterHotKey(None, 3, MOD_CTRL_SHIFT, 0x52) # R
    
    try:
        msg = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
            if msg.message == win32con.WM_HOTKEY:
                hk_id = msg.wParam
                if hk_id == 1:
                    app.root.after(0, app.toggle_osd_visibility_from_hotkey)
                elif hk_id == 2:
                    app.root.after(0, app.toggle_osd_lock_from_hotkey)
                elif hk_id == 3:
                    app.root.after(0, app.overlay.reset_position)
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
    except Exception as e:
        _write_log(f"Hotkey loop crash: {e}")
    finally:
        user32.UnregisterHotKey(None, 1)
        user32.UnregisterHotKey(None, 2)
        user32.UnregisterHotKey(None, 3)


class StatusMonitor:
    def __init__(self, root):
        self.root = root
        root.title("⚡ System Monitor")
        root.configure(fg_color=BG_DARK)
        root.resizable(False, False)
        w, h = 540, 680
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        
        self.overlay = OverlayBar(root, self.show_window, self.quit_app)
        self._build_ui()
        
        # Sync initial overlay options
        self._osd_rebuild()
        
        start_tray(self)
        threading.Thread(target=_temp_loop, daemon=True).start()
        threading.Thread(target=_hotkey_loop, args=(self,), daemon=True).start()
        
        self._update_stats()
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)

    def _build_ui(self):
        # Persistent Header
        hdr = ctk.CTkFrame(self.root, fg_color="transparent")
        hdr.pack(fill="x", padx=20, pady=(18, 6))

        lft = ctk.CTkFrame(hdr, fg_color="transparent")
        lft.pack(side="left")
        ctk.CTkLabel(lft, text="⚡", text_color=C_CYAN,
                     font=ctk.CTkFont("Segoe UI", 24)).pack(side="left")
        ctk.CTkLabel(lft, text=" SYSTEM", text_color=T_BRIGHT,
                     font=ctk.CTkFont("Segoe UI", 17, "bold")).pack(side="left")
        ctk.CTkLabel(lft, text=" MONITOR", text_color=C_INDIGO,
                     font=ctk.CTkFont("Segoe UI", 17, "bold")).pack(side="left")

        rgt = ctk.CTkFrame(hdr, fg_color="transparent")
        rgt.pack(side="right")
        self.time_lbl = ctk.CTkLabel(rgt, text="",
                                      text_color=T_MID,
                                      font=ctk.CTkFont("Segoe UI", 9))
        self.time_lbl.pack(anchor="e")
        bdg = ctk.CTkFrame(rgt, fg_color="transparent")
        bdg.pack(anchor="e", pady=(2, 0))
        ctk.CTkLabel(bdg, text="● LIVE", text_color=C_EMERALD,
                     font=ctk.CTkFont("Segoe UI", 7, "bold")).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(bdg, text="🛡 ADMIN", text_color=C_CYAN,
                     font=ctk.CTkFont("Segoe UI", 7, "bold")).pack(side="left")

        ctk.CTkFrame(self.root, height=1, fg_color=CARD_BD).pack(fill="x", padx=16)

        # Tab view
        self.tabview = ctk.CTkTabview(
            self.root,
            fg_color="transparent",
            segmented_button_fg_color=CARD_BG,
            segmented_button_selected_color=CARD_BD,
            text_color=T_BRIGHT,
        )
        self.tabview.pack(fill="both", expand=True, padx=10, pady=(5, 5))
        
        self.tab_dash = self.tabview.add("DASHBOARD")
        self.tab_osd = self.tabview.add("OSD OVERLAY")

        # --- Tab 1: DASHBOARD ---
        top = ctk.CTkFrame(self.tab_dash, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(10, 0))
        for i in range(3):
            top.columnconfigure(i, weight=1)

        self.cpu_canvas, self.cpu_sub = self._gauge_card(top, 0, "CPU  LOAD",  C_INDIGO)
        self.ram_canvas, self.ram_sub = self._gauge_card(top, 1, "MEMORY",     C_PURPLE)
        self.bat_canvas, self.bat_sub = self._gauge_card(top, 2, "BATTERY",    C_EMERALD)

        bot = ctk.CTkFrame(self.tab_dash, fg_color="transparent")
        bot.pack(fill="both", expand=True, padx=10, pady=(8, 10))
        bot.columnconfigure(0, weight=1)
        bot.columnconfigure(1, weight=1)
        bot.rowconfigure(0, weight=1)
        
        self._cpu_temp_card(bot)
        self._gpu_card(bot)

        # --- Tab 2: OSD OVERLAY ---
        self._build_osd_tab()

        # Persistent Status Bar
        bar = ctk.CTkFrame(self.root, fg_color="#090c18", corner_radius=0, height=26)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)
        ctk.CTkFrame(bar, width=5, fg_color=C_EMERALD, corner_radius=0).pack(side="left", fill="y")
        ctk.CTkLabel(bar, text="Live  •  0.5 s refresh  •  LHM powered", text_color=T_MID, font=ctk.CTkFont("Segoe UI", 8)).pack(side="left", padx=8)
        ctk.CTkLabel(bar, text=f"{platform.system()} {platform.release()}", text_color=T_MID, font=ctk.CTkFont("Segoe UI", 8)).pack(side="right", padx=10)

    def _build_osd_tab(self):
        container = ctk.CTkScrollableFrame(self.tab_osd, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # OSD Controls Card
        card_ctrl = ctk.CTkFrame(container, fg_color=CARD_BG, border_width=1, border_color=CARD_BD, corner_radius=12)
        card_ctrl.pack(fill="x", pady=(5, 10), padx=5)
        
        ctk.CTkLabel(card_ctrl, text="OSD CONTROL & LOCK", text_color=C_CYAN,
                     font=ctk.CTkFont("Segoe UI", 9, "bold")).pack(anchor="w", padx=15, pady=(12, 8))
                     
        ctrl_grid = ctk.CTkFrame(card_ctrl, fg_color="transparent")
        ctrl_grid.pack(fill="x", padx=15, pady=(0, 12))
        
        self._osd_enable_var = ctk.BooleanVar(value=True)
        self._osd_enable_sw = ctk.CTkSwitch(
            ctrl_grid, text="Enable OSD Overlay", variable=self._osd_enable_var,
            text_color=T_BRIGHT, font=ctk.CTkFont("Segoe UI", 11, "bold"),
            button_color=C_INDIGO, progress_color=C_INDIGO,
            command=self._on_osd_enable_toggle
        )
        self._osd_enable_sw.pack(side="left", expand=True, fill="x", padx=5)
        
        self._osd_lock_var = ctk.BooleanVar(value=False)
        self._osd_lock_sw = ctk.CTkSwitch(
            ctrl_grid, text="Lock (Click-Through)", variable=self._osd_lock_var,
            text_color=T_BRIGHT, font=ctk.CTkFont("Segoe UI", 11, "bold"),
            button_color=C_EMERALD, progress_color=C_EMERALD,
            command=self._on_osd_lock_toggle
        )
        self._osd_lock_sw.pack(side="left", expand=True, fill="x", padx=5)

        # OSD Customization Card
        card_custom = ctk.CTkFrame(container, fg_color=CARD_BG, border_width=1, border_color=CARD_BD, corner_radius=12)
        card_custom.pack(fill="x", pady=10, padx=5)
        
        ctk.CTkLabel(card_custom, text="OSD APPEARANCE & CUSTOMIZATION", text_color=C_INDIGO,
                     font=ctk.CTkFont("Segoe UI", 9, "bold")).pack(anchor="w", padx=15, pady=(12, 10))
        
        grid = ctk.CTkFrame(card_custom, fg_color="transparent")
        grid.pack(fill="x", padx=15, pady=(0, 12))
        
        # Row 1: Style
        r1 = ctk.CTkFrame(grid, fg_color="transparent")
        r1.pack(fill="x", pady=5)
        ctk.CTkLabel(r1, text="Overlay Style:", text_color=T_MID, font=ctk.CTkFont("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 10))
        self._osd_style_menu = ctk.CTkOptionMenu(
            r1, values=["MSI Afterburner (HUD)", "Compact Widget Bar"],
            fg_color=CARD_BD, button_color=CARD_BD, button_hover_color=C_INDIGO,
            font=ctk.CTkFont("Segoe UI", 10), dropdown_font=ctk.CTkFont("Segoe UI", 10),
            command=self._on_osd_style_change
        )
        self._osd_style_menu.set("MSI Afterburner (HUD)")
        self._osd_style_menu.pack(side="left", fill="x", expand=True)
        
        # Row 2: BG Mode
        r2 = ctk.CTkFrame(grid, fg_color="transparent")
        r2.pack(fill="x", pady=5)
        ctk.CTkLabel(r2, text="BG Mode:     ", text_color=T_MID, font=ctk.CTkFont("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 10))
        self._osd_bg_menu = ctk.CTkOptionMenu(
            r2, values=["Translucent Dark", "Fully Transparent"],
            fg_color=CARD_BD, button_color=CARD_BD, button_hover_color=C_INDIGO,
            font=ctk.CTkFont("Segoe UI", 10), dropdown_font=ctk.CTkFont("Segoe UI", 10),
            command=self._on_osd_bg_change
        )
        self._osd_bg_menu.set("Translucent Dark")
        self._osd_bg_menu.pack(side="left", fill="x", expand=True)

        # Row 3: Font Size
        r3 = ctk.CTkFrame(grid, fg_color="transparent")
        r3.pack(fill="x", pady=5)
        ctk.CTkLabel(r3, text="Font Size:   ", text_color=T_MID, font=ctk.CTkFont("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 10))
        self._osd_fs_menu = ctk.CTkOptionMenu(
            r3, values=["Small", "Medium", "Large", "Extra Large"],
            fg_color=CARD_BD, button_color=CARD_BD, button_hover_color=C_INDIGO,
            font=ctk.CTkFont("Segoe UI", 10), dropdown_font=ctk.CTkFont("Segoe UI", 10),
            command=self._on_osd_fs_change
        )
        self._osd_fs_menu.set("Medium")
        self._osd_fs_menu.pack(side="left", fill="x", expand=True)
        
        # Row 4: Opacity slider
        r4 = ctk.CTkFrame(grid, fg_color="transparent")
        r4.pack(fill="x", pady=10)
        ctk.CTkLabel(r4, text="Opacity:", text_color=T_MID, font=ctk.CTkFont("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 15))
        self._osd_opacity_slider = ctk.CTkSlider(
            r4, from_=0.3, to=1.0, number_of_steps=70,
            button_color=C_INDIGO, progress_color=C_INDIGO,
            command=self._on_osd_opacity_change
        )
        self._osd_opacity_slider.set(0.93)
        self._osd_opacity_slider.pack(side="left", fill="x", expand=True)
        
        self.op_val_lbl = ctk.CTkLabel(r4, text="93%", text_color=T_BRIGHT, font=ctk.CTkFont("Segoe UI", 10, "bold"))
        self.op_val_lbl.pack(side="right", padx=(10, 0))

        # Position reset
        reset_btn = ctk.CTkButton(
            card_custom, text="Reset Overlay Position",
            fg_color=CARD_BD, hover_color=C_PURPLE,
            font=ctk.CTkFont("Segoe UI", 10, "bold"),
            command=self.overlay.reset_position
        )
        reset_btn.pack(fill="x", padx=15, pady=(5, 12))

        # Hotkeys Card
        card_info = ctk.CTkFrame(container, fg_color="#181a30", border_width=1, border_color=CARD_BD, corner_radius=12)
        card_info.pack(fill="x", pady=(10, 5), padx=5)
        
        ctk.CTkLabel(card_info, text="⌨️  OSD KEYBOARD SHORTCUTS", text_color=C_EMERALD,
                     font=ctk.CTkFont("Segoe UI", 9, "bold")).pack(anchor="w", padx=15, pady=(12, 4))
                     
        shortcuts = (
            "• Ctrl + Shift + O : Toggle OSD visibility (Show/Hide)\n"
            "• Ctrl + Shift + L : Toggle Click-through lock (Lock/Unlock)\n"
            "• Ctrl + Shift + R : Reset overlay position to default corner"
        )
        info_lbl = ctk.CTkLabel(card_info, text=shortcuts, text_color=T_MID,
                                font=ctk.CTkFont("Segoe UI", 9), justify="left")
        info_lbl.pack(anchor="w", padx=15, pady=(0, 12))

    def _on_osd_enable_toggle(self):
        if self._osd_enable_var.get():
            self.overlay.show()
        else:
            self.overlay.hide()
            
    def _on_osd_lock_toggle(self):
        self.overlay.set_lock(self._osd_lock_var.get())
        
    def _on_osd_style_change(self, value):
        self._osd_rebuild()
        self.overlay.reset_position()
        
    def _on_osd_bg_change(self, value):
        self._osd_rebuild()
        
    def _on_osd_fs_change(self, value):
        self._osd_rebuild()
        
    def _on_osd_opacity_change(self, value):
        opacity = float(value)
        self.op_val_lbl.configure(text=f"{int(opacity * 100)}%")
        self.overlay.win.wm_attributes("-alpha", opacity)
        
    def _osd_rebuild(self):
        style = self._osd_style_menu.get()
        bg = self._osd_bg_menu.get()
        opacity = self._osd_opacity_slider.get()
        fs = self._osd_fs_menu.get()
        locked = self._osd_lock_var.get()
        
        self.overlay.locked = locked
        self.overlay.rebuild_layout(style, bg, opacity, fs)

    def toggle_osd_lock_from_hotkey(self):
        new_state = not self._osd_lock_var.get()
        self._osd_lock_var.set(new_state)
        if new_state:
            self._osd_lock_sw.select()
        else:
            self._osd_lock_sw.deselect()
        self.overlay.set_lock(new_state)

    def toggle_osd_visibility_from_hotkey(self):
        new_state = not self._osd_enable_var.get()
        self._osd_enable_var.set(new_state)
        if new_state:
            self._osd_enable_sw.select()
        else:
            self._osd_enable_sw.deselect()
        self.overlay.toggle()

    # \u2500\u2500 Gauge card \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
    def _gauge_card(self, parent, col, title, color):
        card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=16,
                             border_width=1, border_color=CARD_BD)
        card.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(card, text=title, text_color=T_MID,
                      font=ctk.CTkFont("Segoe UI", 8, "bold")).pack(pady=(14, 0))
        canvas = tk.Canvas(card, width=114, height=114, bg=CARD_BG,
                            highlightthickness=0)
        canvas.pack(pady=(4, 0))
        draw_gauge(canvas, 0, color)
        sub = ctk.CTkLabel(card, text="", text_color=T_MID,
                            font=ctk.CTkFont("Segoe UI", 8))
        sub.pack(pady=(3, 14))
        return canvas, sub

    # \u2500\u2500 CPU Temp card \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
    def _cpu_temp_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=16,
                             border_width=1, border_color=CARD_BD)
        card.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(card, text="\ud83c\udf21  CPU TEMP", text_color=T_MID,
                      font=ctk.CTkFont("Segoe UI", 8, "bold")).pack(
                      anchor="w", padx=20, pady=(18, 2))
        self.temp_big = ctk.CTkLabel(card, text="--", text_color=C_AMBER,
                                      font=ctk.CTkFont("Segoe UI", 54, "bold"))
        self.temp_big.pack(anchor="w", padx=20, pady=(0, 0))
        ur = ctk.CTkFrame(card, fg_color="transparent")
        ur.pack(anchor="w", padx=20)
        self.temp_unit = ctk.CTkLabel(ur, text="\u00b0C", text_color=T_MID,
                                       font=ctk.CTkFont("Segoe UI", 15))
        self.temp_unit.pack(side="left")
        self.cpu_w_lbl = ctk.CTkLabel(ur, text="  -- W", text_color=C_AMBER,
                                       font=ctk.CTkFont("Segoe UI", 14, "bold"))
        self.cpu_w_lbl.pack(side="left")
        self.temp_sub = ctk.CTkLabel(card, text="Reading...", text_color=T_DIM,
                                      font=ctk.CTkFont("Segoe UI", 7),
                                      wraplength=180, justify="left")
        self.temp_sub.pack(anchor="w", padx=20, pady=(6, 18))

    # \u2500\u2500 GPU card \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
    # -- GPU card --
    def _gpu_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=16,
                             border_width=1, border_color=CARD_BD)
        card.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        # Title row with PERF toggle on the right
        tr = ctk.CTkFrame(card, fg_color="transparent")
        tr.pack(fill="x", padx=20, pady=(18, 4))
        ctk.CTkLabel(tr, text="🎮  GPU", text_color=T_MID,
                      font=ctk.CTkFont("Segoe UI", 8, "bold")).pack(side="left")
        self.gpu_sub = ctk.CTkLabel(tr, text="Detecting...", text_color=T_DIM,
                                     font=ctk.CTkFont("Segoe UI", 7), wraplength=80)
        self.gpu_sub.pack(side="left", padx=(6, 0))

        # PERF toggle switch
        self._perf_var = ctk.BooleanVar(value=False)
        self._perf_sw  = ctk.CTkSwitch(
            tr, text="PERF", variable=self._perf_var,
            text_color=T_MID, font=ctk.CTkFont("Segoe UI", 7, "bold"),
            button_color=C_INDIGO, button_hover_color=C_PURPLE,
            progress_color=C_INDIGO, switch_width=28, switch_height=14,
            command=self._toggle_perf)
        self._perf_sw.pack(side="right")

        # Temperature
        tg = ctk.CTkFrame(card, fg_color="transparent")
        tg.pack(anchor="w", padx=20)
        ctk.CTkLabel(tg, text="TEMP", text_color=T_DIM,
                      font=ctk.CTkFont("Segoe UI", 7, "bold")).pack(anchor="w")
        gn = ctk.CTkFrame(tg, fg_color="transparent")
        gn.pack(anchor="w")
        self.gpu_big = ctk.CTkLabel(gn, text="--", text_color=C_PINK,
                                     font=ctk.CTkFont("Segoe UI", 44, "bold"))
        self.gpu_big.pack(side="left")
        ctk.CTkLabel(gn, text="°C", text_color=T_MID,
                      font=ctk.CTkFont("Segoe UI", 15)).pack(side="left", pady=(0, 10))

        # Divider
        ctk.CTkFrame(card, height=1, fg_color=CARD_BD).pack(fill="x", padx=20, pady=(6, 8))

        # Power
        pg = ctk.CTkFrame(card, fg_color="transparent")
        pg.pack(anchor="w", padx=20, pady=(0, 6))
        ctk.CTkLabel(pg, text="POWER", text_color=T_DIM,
                      font=ctk.CTkFont("Segoe UI", 7, "bold")).pack(anchor="w")
        self.gpu_w_lbl = ctk.CTkLabel(pg, text="-- W", text_color=C_PINK,
                                       font=ctk.CTkFont("Segoe UI", 32, "bold"))
        self.gpu_w_lbl.pack(anchor="w")

        # --- PERF panel (hidden by default) ---
        self._perf_frame = ctk.CTkFrame(card, fg_color="transparent")
        # Not packed yet; _toggle_perf shows/hides it

        ctk.CTkFrame(self._perf_frame, height=1, fg_color=CARD_BD).pack(
            fill="x", padx=20, pady=(4, 8))

        perf_row = ctk.CTkFrame(self._perf_frame, fg_color="transparent")
        perf_row.pack(fill="x", padx=20, pady=(0, 14))

        # GPU Utilization block
        util_blk = ctk.CTkFrame(perf_row, fg_color="transparent")
        util_blk.pack(side="left")
        ctk.CTkLabel(util_blk, text="UTIL", text_color=T_DIM,
                      font=ctk.CTkFont("Segoe UI", 7, "bold")).pack(anchor="w")
        self.gpu_util_lbl = ctk.CTkLabel(util_blk, text="--%", text_color=C_INDIGO,
                                          font=ctk.CTkFont("Segoe UI", 18, "bold"))
        self.gpu_util_lbl.pack(anchor="w")

        ctk.CTkFrame(perf_row, width=1, fg_color=CARD_BD).pack(
            side="left", fill="y", padx=10)

        # GPU Clock block
        clk_blk = ctk.CTkFrame(perf_row, fg_color="transparent")
        clk_blk.pack(side="left")
        ctk.CTkLabel(clk_blk, text="CLOCK", text_color=T_DIM,
                      font=ctk.CTkFont("Segoe UI", 7, "bold")).pack(anchor="w")
        self.gpu_clk_lbl = ctk.CTkLabel(clk_blk, text="-- MHz", text_color=C_PURPLE,
                                         font=ctk.CTkFont("Segoe UI", 18, "bold"))
        self.gpu_clk_lbl.pack(anchor="w")


    def _toggle_perf(self):
        if self._perf_var.get():
            self._perf_frame.pack(fill="x")
        else:
            self._perf_frame.pack_forget()


    # \u2500\u2500 Window management \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
    def show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def hide_window(self):
        self.root.withdraw()

    def quit_app(self):
        try:
            import subprocess
            subprocess.run('taskkill /f /im LibreHardwareMonitor.exe', shell=True, capture_output=True, creationflags=0x08000000)
        except Exception:
            pass
        try:
            if _tray_icon:
                _tray_icon.stop()
        except Exception:
            pass
        self.root.destroy()

    # \u2500\u2500 Live update loop \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
    def _update_stats(self):
        self.time_lbl.configure(
            text=datetime.datetime.now().strftime("%H:%M:%S"))

        # CPU
        cpu = psutil.cpu_percent(interval=None)
        draw_gauge(self.cpu_canvas, cpu, arc_color(cpu))
        freq = psutil.cpu_freq()
        self.cpu_sub.configure(
            text=(f"{freq.current/1000:.2f} GHz  \u2022  {psutil.cpu_count()} cores"
                  if freq else ""))

        # RAM
        mem = psutil.virtual_memory()
        draw_gauge(self.ram_canvas, mem.percent, arc_color(mem.percent))
        self.ram_sub.configure(
            text=f"{mem.used/1024**3:.1f} / {mem.total/1024**3:.1f} GB")

        # Battery
        bat = psutil.sensors_battery()
        if bat:
            draw_gauge(self.bat_canvas, bat.percent,
                       C_EMERALD if bat.power_plugged else arc_color(bat.percent))
            s = "\u26a1 Charging" if bat.power_plugged else "\ud83d\udd0b Discharging"
            secs = bat.secsleft
            if (secs not in (psutil.POWER_TIME_UNKNOWN, psutil.POWER_TIME_UNLIMITED)
                    and secs > 0):
                h, m = divmod(secs // 60, 60)
                s += f"  \u2022  {h}h {m:02d}m"
            self.bat_sub.configure(text=s)
        else:
            draw_gauge(self.bat_canvas, 0, T_MID)
            self.bat_sub.configure(text="No battery")

        # CPU Temperature
        temp_val, temp_status = get_cpu_temp()
        if temp_val is not None:
            col = arc_color(temp_val)
            self.temp_big.configure(text=f"{temp_val:.0f}", text_color=col)
            self.temp_unit.configure(text_color=col)
        else:
            self.temp_big.configure(text="--", text_color=T_MID)
            self.temp_unit.configure(text_color=T_MID)
        self.temp_sub.configure(text=temp_status)

        # GPU Temperature
        gpu_val, gpu_status = get_gpu_temp()
        if gpu_val is not None:
            self.gpu_big.configure(
                text=f"{gpu_val:.0f}", text_color=arc_color(gpu_val))
        else:
            self.gpu_big.configure(text="--", text_color=T_MID)
        self.gpu_sub.configure(text=gpu_status)

        # Wattage
        cpu_w, gpu_w = get_power()
        self.cpu_w_lbl.configure(
            text=f"  {cpu_w:.0f} W" if cpu_w is not None else "  -- W",
            text_color=C_AMBER if cpu_w is not None else T_MID)
        self.gpu_w_lbl.configure(
            text=f"{gpu_w:.0f} W" if gpu_w is not None else "-- W",
            text_color=C_PINK if gpu_w is not None else T_MID)

        # GPU Perf (util + clock)
        gpu_load, gpu_clock = get_gpu_perf()
        if gpu_load is not None:
            self.gpu_util_lbl.configure(
                text=f"{gpu_load:.0f}%", text_color=arc_color(gpu_load))
        else:
            self.gpu_util_lbl.configure(text="--%", text_color=T_MID)
        if gpu_clock is not None:
            mhz = gpu_clock
            self.gpu_clk_lbl.configure(
                text=(f"{mhz/1000:.2f} GHz" if mhz >= 1000 else f"{mhz:.0f} MHz"),
                text_color=C_PURPLE)
        else:
            self.gpu_clk_lbl.configure(text="-- MHz", text_color=T_MID)

        # Overlay + tray
        freq_ghz = (freq.current / 1000) if freq else None
        ram_gb   = mem.used / 1024**3
        bat_pct  = bat.percent if bat else None
        update_tray(temp_val, gpu_val, cpu)
        self.overlay.update(temp_val, gpu_val, cpu, ram_gb, bat_pct,
                            freq_ghz, cpu_w=cpu_w, gpu_w=gpu_w,
                            gpu_load=gpu_load, gpu_clock=gpu_clock)

        self.root.after(500, self._update_stats)


# \u2500\u2500\u2500 Entry \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
if __name__ == "__main__":
    try:
        _write_log(f"Starting as admin \u2014 Python {sys.version.split()[0]}")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        root = ctk.CTk()
        StatusMonitor(root)
        root.mainloop()
        _write_log("Exited normally")
    except Exception as e:
        _write_log(f"CRASH: {e}\n{traceback.format_exc()}")
        try:
            import tkinter as _tk
            from tkinter import messagebox as _mb
            _r = _tk.Tk(); _r.withdraw()
            _mb.showerror("System Monitor Error", f"System Monitor encountered an error:\n\n{e}\n\nCheck monitor_error.log for details.")
            _r.destroy()
        except Exception:
            pass
        raise



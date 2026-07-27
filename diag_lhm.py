"""Quick LHM diagnostic — run elevated to see what sensors are available."""
import sys, os

_BASE   = os.path.dirname(os.path.abspath(__file__))
LHM_DIR = os.path.join(_BASE, "LibreHardwareMonitor")
LHM_DLL = os.path.join(LHM_DIR, "LibreHardwareMonitorLib.dll")
OUT     = os.path.join(_BASE, "diag_output.txt")

lines = []
def p(msg=""):
    lines.append(str(msg))
    print(msg)

try:
    p(f"LHM DLL exists: {os.path.exists(LHM_DLL)}")

    import pythonnet
    pythonnet.load("netfx")
    import clr
    if LHM_DIR not in sys.path:
        sys.path.append(LHM_DIR)
    clr.AddReference("LibreHardwareMonitorLib")
    from LibreHardwareMonitor.Hardware import Computer, HardwareType, SensorType

    computer = Computer()
    computer.IsCpuEnabled = True
    computer.IsGpuEnabled = True
    computer.Open()

    p(f"\n=== Hardware enumeration ===")
    p(f"computer.Hardware type: {type(computer.Hardware)}")

    # Try different iteration approaches
    hw_list = None
    try:
        hw_list = list(computer.Hardware)
        p(f"list() worked: {len(hw_list)} items")
    except Exception as e:
        p(f"list() FAILED: {e}")
        try:
            n = computer.Hardware.Count
            hw_list = [computer.Hardware[i] for i in range(n)]
            p(f"index access worked: {n} items")
        except Exception as e2:
            p(f"index access FAILED: {e2}")
            try:
                enum = computer.Hardware.GetEnumerator()
                hw_list = []
                while enum.MoveNext():
                    hw_list.append(enum.Current)
                p(f"GetEnumerator worked: {len(hw_list)} items")
            except Exception as e3:
                p(f"GetEnumerator FAILED: {e3}")

    if hw_list:
        for hw in hw_list:
            p(f"\n--- {hw.Name} (Type: {hw.HardwareType}) ---")
            hw.Update()

            # Check SubHardware
            try:
                subs = list(hw.SubHardware)
                for sub in subs:
                    sub.Update()
                    p(f"  SubHW: {sub.Name} ({sub.HardwareType})")
            except Exception as e:
                p(f"  SubHardware iteration failed: {e}")

            # Check Sensors
            try:
                sensors = list(hw.Sensors)
                p(f"  Sensor count: {len(sensors)}")
            except Exception as e:
                p(f"  list(Sensors) failed: {e}")
                sensors = []

            for s in sensors:
                if s.Value is not None:
                    p(f"    {s.SensorType}: {s.Name} = {s.Value}")
                    
    # Also test: iterate TWICE to check exhaustion
    p("\n=== Second iteration test ===")
    try:
        hw_list2 = list(computer.Hardware)
        p(f"Second list() worked: {len(hw_list2)} items")
        for hw in hw_list2:
            hw.Update()
            sensors2 = list(hw.Sensors)
            p(f"  {hw.Name}: {len(sensors2)} sensors on 2nd pass")
    except Exception as e:
        p(f"Second iteration FAILED: {e}")

    computer.Close()
    p("\nDone.")

except Exception as e:
    import traceback
    p(f"FATAL: {e}")
    p(traceback.format_exc())

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"\nOutput saved to {OUT}")

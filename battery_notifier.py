import ctypes
import time
import winsound

class SYSTEM_POWER_STATUS(ctypes.Structure):
    _fields_ = [
        ("ACLineStatus", ctypes.c_byte),
        ("BatteryFlag", ctypes.c_byte),
        ("BatteryLifePercent", ctypes.c_byte),
        ("Reserved1", ctypes.c_byte),
        ("BatteryLifeTime", ctypes.c_ulong),
        ("BatteryFullLifeTime", ctypes.c_ulong),
    ]

def get__battery_percent():
    status = SYSTEM_POWER_STATUS()
    ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(status))
    return status.BatteryLifePercent

last_percent = get__battery_percent()
print(f"Battery monitor startedat {last_percent}%")

while True:
    time.sleep(30)
    current = get__battery_percent()

    if current == last_percent - 1:
        print(f"Battery dropped to {current}%")
        winsound.Beep(1000,500)
        last_percent = current
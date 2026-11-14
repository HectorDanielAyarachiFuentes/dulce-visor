import ctypes
from ctypes import wintypes
import threading
import time

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

HAS_NVIDIA = False
nvidia_handle = None
try:
    import pynvml
    pynvml.nvmlInit()
    if pynvml.nvmlDeviceGetCount() > 0:
        HAS_NVIDIA = True
        nvidia_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
except Exception:
    HAS_NVIDIA = False

class MemoryStatus(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]

_mem_stat = MemoryStatus()
_mem_stat.dwLength = ctypes.sizeof(MemoryStatus)

# Lector de temperatura de CPU nativo en memoria (WMI COM in-process)
cpu_temp_cache = 30

def _cpu_temp_worker():
    global cpu_temp_cache
    wmi_obj = None
    try:
        import win32com.client
        import pythoncom
        pythoncom.CoInitialize()
        wmi_obj = win32com.client.GetObject("winmgmts:root/cimv2")
    except Exception:
        wmi_obj = None

    while True:
        try:
            if wmi_obj:
                items = wmi_obj.ExecQuery("SELECT Temperature FROM Win32_PerfFormattedData_Counters_ThermalZoneInformation")
                temps = [item.Temperature for item in items if item.Temperature]
                if temps:
                    max_k = max(temps)
                    celsius = round(max_k - 273.15)
                    if 15 < celsius < 115:
                        cpu_temp_cache = celsius
        except Exception:
            pass
        time.sleep(2)

_temp_thread = threading.Thread(target=_cpu_temp_worker, daemon=True)
_temp_thread.start()

def get_cpu_temp():
    return cpu_temp_cache

def get_ram_usage():
    if HAS_PSUTIL:
        return int(psutil.virtual_memory().percent)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(_mem_stat))
    return int(_mem_stat.dwMemoryLoad)

def get_cpu_usage():
    if HAS_PSUTIL:
        return int(psutil.cpu_percent(interval=None))
    return 10

def get_gpu_info():
    if HAS_NVIDIA and nvidia_handle:
        try:
            temp = pynvml.nvmlDeviceGetTemperature(nvidia_handle, pynvml.NVML_TEMPERATURE_GPU)
            util = pynvml.nvmlDeviceGetUtilizationRates(nvidia_handle).gpu
            return temp, util
        except Exception:
            pass
    return 29, 0

def clean_memory():
    """Optimiza la memoria RAM liberando páginas de trabajo (Working Set) del sistema."""
    try:
        h = ctypes.windll.kernel32.GetCurrentProcess()
        ctypes.windll.psapi.EmptyWorkingSet(h)
        if HAS_PSUTIL:
            for proc in psutil.process_iter(['pid']):
                try:
                    hp = ctypes.windll.kernel32.OpenProcess(0x001F0FFF, False, proc.info['pid'])
                    if hp:
                        ctypes.windll.psapi.EmptyWorkingSet(hp)
                        ctypes.windll.kernel32.CloseHandle(hp)
                except Exception:
                    pass
    except Exception:
        pass

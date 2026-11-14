import ctypes
from ctypes import wintypes
import gc

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Win32 Constants
GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_NOACTIVATE = 0x08000000
HWND_TOPMOST = wintypes.HWND(-1)

SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040
SWP_FLAGS = SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW

TPM_RIGHTBUTTON = 0x0002
TPM_RETURNCMD = 0x0100
TPM_BOTTOMALIGN = 0x0020
MF_STRING = 0x0000
MF_POPUP = 0x0010
MF_SEPARATOR = 0x0800
MF_CHECKED = 0x0008
MF_UNCHECKED = 0x0000

# 64-bit type signatures
user32.SetWindowPos.argtypes = [
    wintypes.HWND,
    wintypes.HWND,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_uint
]
user32.SetWindowPos.restype = wintypes.BOOL

user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
user32.GetWindowLongW.restype = ctypes.c_long

user32.SetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_long]
user32.SetWindowLongW.restype = ctypes.c_long

user32.CreatePopupMenu.restype = wintypes.HMENU
user32.AppendMenuW.argtypes = [wintypes.HMENU, ctypes.c_uint, ctypes.c_size_t, wintypes.LPCWSTR]
user32.AppendMenuW.restype = wintypes.BOOL

class RECT(ctypes.Structure):
    _fields_ = [
        ('left', ctypes.c_long),
        ('top', ctypes.c_long),
        ('right', ctypes.c_long),
        ('bottom', ctypes.c_long)
    ]

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

def enable_dpi_awareness():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            user32.SetProcessDPIAware()
        except Exception:
            pass

def get_dpi_scale():
    try:
        hdc = user32.GetDC(0)
        dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)
        user32.ReleaseDC(0, hdc)
        return dpi / 96.0
    except Exception:
        return 1.0

def get_taskbar_pos():
    hwnd = user32.FindWindowW("Shell_TrayWnd", None)
    if hwnd:
        rect = RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        return rect.left, rect.top, rect.right, rect.bottom
    return None

def is_foreground_fullscreen(screen_w, screen_h):
    try:
        fg = user32.GetForegroundWindow()
        if not fg:
            return False
        cls_buf = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(fg, cls_buf, 256)
        if cls_buf.value in ("Progman", "WorkerW", "Shell_TrayWnd", ""):
            return False
        rect = RECT()
        user32.GetWindowRect(fg, ctypes.byref(rect))
        return rect.left <= 0 and rect.top <= 0 and rect.right >= screen_w and rect.bottom >= screen_h
    except Exception:
        return False

def apply_topmost_toolwindow(hwnd):
    try:
        h = wintypes.HWND(hwnd)
        ex_style = user32.GetWindowLongW(h, GWL_EXSTYLE)
        user32.SetWindowLongW(h, GWL_EXSTYLE, ex_style | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE)
        user32.SetWindowPos(h, HWND_TOPMOST, 0, 0, 0, 0, SWP_FLAGS)
    except Exception:
        pass

def reassert_topmost(hwnd):
    try:
        h = wintypes.HWND(hwnd)
        user32.SetWindowPos(h, HWND_TOPMOST, 0, 0, 0, 0, SWP_FLAGS)
    except Exception:
        pass

def show_native_context_menu(hwnd, current_skin_id, skins_dict, banderas_dict,
                             on_clean_cb, on_recenter_cb, on_change_skin_cb, on_close_cb):
    """Muestra menú contextual nativo con submenús de Skins y Banderas."""
    try:
        h = wintypes.HWND(hwnd)
        hmenu = user32.CreatePopupMenu()
        menu_skins = user32.CreatePopupMenu()
        menu_banderas = user32.CreatePopupMenu()

        cmd_map = {}

        # 1. Submenú de Skins (1001+)
        skin_id_start = 1001
        for idx, (s_key, s_data) in enumerate(skins_dict.items()):
            c_id = skin_id_start + idx
            cmd_map[c_id] = s_key
            flags = MF_STRING | (MF_CHECKED if s_key == current_skin_id else MF_UNCHECKED)
            user32.AppendMenuW(menu_skins, flags, c_id, s_data["name"])

        # 2. Submenú de Banderas (2001+)
        bandera_id_start = 2001
        for idx, (b_key, b_data) in enumerate(banderas_dict.items()):
            c_id = bandera_id_start + idx
            cmd_map[c_id] = b_key
            flags = MF_STRING | (MF_CHECKED if b_key == current_skin_id else MF_UNCHECKED)
            user32.AppendMenuW(menu_banderas, flags, c_id, b_data["name"])

        # Elementos principales
        user32.AppendMenuW(hmenu, MF_STRING, 101, "⚡ Optimizar Memoria RAM")
        user32.AppendMenuW(hmenu, MF_STRING, 102, "📌 Re-centrar en la barra")
        user32.AppendMenuW(hmenu, MF_SEPARATOR, 0, None)

        # Agregar los dos submenús
        user32.AppendMenuW(hmenu, MF_POPUP, ctypes.cast(menu_skins, ctypes.c_void_p).value, "🎨 Temas y Skins (10)")
        user32.AppendMenuW(hmenu, MF_POPUP, ctypes.cast(menu_banderas, ctypes.c_void_p).value, "🚩 Banderas de Países (10)")

        user32.AppendMenuW(hmenu, MF_SEPARATOR, 0, None)
        user32.AppendMenuW(hmenu, MF_STRING, 103, "❌ Cerrar Dulce-Visor")

        pt = POINT()
        user32.GetCursorPos(ctypes.byref(pt))
        user32.SetForegroundWindow(h)

        cmd = user32.TrackPopupMenu(
            hmenu, TPM_RIGHTBUTTON | TPM_RETURNCMD | TPM_BOTTOMALIGN,
            pt.x, pt.y, 0, h, None
        )

        user32.DestroyMenu(menu_skins)
        user32.DestroyMenu(menu_banderas)
        user32.DestroyMenu(hmenu)

        if cmd == 101:
            on_clean_cb()
        elif cmd == 102:
            on_recenter_cb()
        elif cmd == 103:
            on_close_cb()
        elif cmd in cmd_map:
            on_change_skin_cb(cmd_map[cmd])

    except Exception:
        pass

def trim_process_memory():
    try:
        gc.collect()
        h = kernel32.GetCurrentProcess()
        ctypes.windll.psapi.EmptyWorkingSet(h)
    except Exception:
        pass

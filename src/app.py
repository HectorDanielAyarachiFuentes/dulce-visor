import tkinter as tk
import ctypes
from collections import deque

from .config import LOGICAL_WIDTH, LOGICAL_HEIGHT, HISTORY_LEN, COLORS, load_config, save_config
from .window import (
    enable_dpi_awareness, get_dpi_scale, get_taskbar_pos,
    is_foreground_fullscreen, apply_topmost_toolwindow,
    reassert_topmost, show_native_context_menu, trim_process_memory
)
from .metrics import (
    get_ram_usage, get_cpu_usage, get_cpu_temp,
    get_gpu_info, clean_memory
)
from .renderer import VisorRenderer

class DulceVisor(tk.Tk):
    def __init__(self):
        enable_dpi_awareness()
        super().__init__()

        self.overrideredirect(True)
        self.attributes('-topmost', True)

        self.dpi = get_dpi_scale()
        self.screen_w = self.winfo_screenwidth()
        self.screen_h = self.winfo_screenheight()

        self.logical_w = LOGICAL_WIDTH
        self.logical_h = LOGICAL_HEIGHT
        self.width = int(self.logical_w * self.dpi)
        self.height = int(self.logical_h * self.dpi)

        self.trans_color = COLORS["trans"]
        self.wm_attributes('-transparentcolor', self.trans_color)
        self.config(bg=self.trans_color)

        self.is_hovered = False
        self.is_cleaning = False
        self.is_hidden_for_game = False

        self.cpu_history = deque([10] * HISTORY_LEN, maxlen=HISTORY_LEN)
        self.gpu_history = deque([5] * HISTORY_LEN, maxlen=HISTORY_LEN)

        self.canvas = tk.Canvas(
            self, width=self.width, height=self.height,
            bg=self.trans_color, highlightthickness=0
        )
        self.canvas.pack(fill='both', expand=True)

        self.renderer = VisorRenderer(self.dpi)
        self.position_on_taskbar()

        self._drag_x = 0
        self._drag_y = 0
        self.canvas_img_item = None
        self.current_tk_img = None
        self.hwnd = None

        self.canvas.bind('<Enter>', self.on_enter)
        self.canvas.bind('<Leave>', self.on_leave)
        self.canvas.bind('<Button-1>', self.start_drag)
        self.canvas.bind('<B1-Motion>', self.do_drag)
        self.canvas.bind('<ButtonRelease-1>', self.end_drag)
        self.canvas.bind('<Button-3>', lambda e: self.show_context_menu())

        self.after(50, self.setup_win32)
        self.update_metrics_and_render()
        self.after(250, self.guardian_loop)
        self.after(2000, trim_process_memory)

    def position_on_taskbar(self):
        saved = load_config()
        if "x" in saved and "y" in saved:
            self.geometry(f"{self.width}x{self.height}+{saved['x']}+{saved['y']}")
            return

        tb = get_taskbar_pos()
        if tb:
            tb_left, tb_top, tb_right, tb_bottom = tb
            tb_h = tb_bottom - tb_top
            target_h = min(self.height, tb_h - 4)
            y = tb_top + max(2, (tb_h - target_h) // 2)
            x = tb_left + int(12 * self.dpi)
            self.geometry(f"{self.width}x{self.height}+{x}+{y}")
        else:
            self.geometry(f"{self.width}x{self.height}+12+{self.screen_h - 48}")

    def setup_win32(self):
        try:
            self.hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            if not self.hwnd:
                self.hwnd = self.winfo_id()
            apply_topmost_toolwindow(self.hwnd)
        except Exception:
            pass

    def guardian_loop(self):
        """Mantiene el widget anclado sobre la barra y lo oculta automáticamente en juegos a pantalla completa."""
        try:
            if self.hwnd:
                if is_foreground_fullscreen(self.screen_w, self.screen_h):
                    if not self.is_hidden_for_game:
                        self.withdraw()
                        self.is_hidden_for_game = True
                else:
                    if self.is_hidden_for_game:
                        self.deiconify()
                        self.is_hidden_for_game = False
                    reassert_topmost(self.hwnd)
        except Exception:
            pass
        self.after(250, self.guardian_loop)

    def on_enter(self, event):
        self.is_hovered = True
        self.render_frame()

    def on_leave(self, event):
        self.is_hovered = False
        self.render_frame()

    def on_clean_click(self):
        self.is_cleaning = True
        self.render_frame()
        clean_memory()
        self.after(300, self.finish_cleaning)

    def finish_cleaning(self):
        self.is_cleaning = False
        trim_process_memory()
        self.render_frame()

    def start_drag(self, event):
        threshold = int(40 * self.dpi)
        if event.x <= threshold:
            self.on_clean_click()
            return
        self._drag_x = event.x
        self._drag_y = event.y

    def do_drag(self, event):
        threshold = int(40 * self.dpi)
        if event.x <= threshold:
            return
        dx = event.x - self._drag_x
        dy = event.y - self._drag_y
        x = self.winfo_x() + dx
        y = self.winfo_y() + dy
        self.geometry(f"+{x}+{y}")

    def end_drag(self, event):
        save_config({"x": self.winfo_x(), "y": self.winfo_y()})

    def show_context_menu(self):
        hwnd = self.hwnd or self.winfo_id()
        show_native_context_menu(
            hwnd,
            on_clean_cb=self.on_clean_click,
            on_recenter_cb=self.recenter_on_taskbar,
            on_close_cb=self.destroy
        )

    def recenter_on_taskbar(self):
        tb = get_taskbar_pos()
        if tb:
            tb_left, tb_top, tb_right, tb_bottom = tb
            tb_h = tb_bottom - tb_top
            target_h = min(self.height, tb_h - 4)
            y = tb_top + max(2, (tb_h - target_h) // 2)
            x = tb_left + int(12 * self.dpi)
            self.geometry(f"{self.width}x{self.height}+{x}+{y}")
            save_config({"x": x, "y": y})

    def render_frame(self):
        ram = getattr(self, 'current_ram', 20)
        cpu = getattr(self, 'current_cpu', 10)
        cpu_temp = get_cpu_temp()
        gpu_temp, gpu_util = getattr(self, 'current_gpu', (29, 0))

        self.current_tk_img = self.renderer.render(
            ram=ram, cpu=cpu, cpu_temp=cpu_temp,
            gpu_util=gpu_util, gpu_temp=gpu_temp,
            cpu_history=self.cpu_history, gpu_history=self.gpu_history,
            is_hovered=self.is_hovered, is_cleaning=self.is_cleaning
        )

        if not self.canvas_img_item:
            self.canvas_img_item = self.canvas.create_image(0, 0, image=self.current_tk_img, anchor='nw')
        else:
            self.canvas.itemconfig(self.canvas_img_item, image=self.current_tk_img)

    def update_metrics_and_render(self):
        self.current_ram = get_ram_usage()
        self.current_cpu = get_cpu_usage()
        self.cpu_history.append(self.current_cpu)

        gpu_temp, gpu_util = get_gpu_info()
        self.current_gpu = (gpu_temp, gpu_util)
        self.gpu_history.append(gpu_util)

        self.render_frame()
        self.after(1000, self.update_metrics_and_render)

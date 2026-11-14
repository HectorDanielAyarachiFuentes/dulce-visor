import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

# Dimensiones base lógicas (se multiplican por DPI)
LOGICAL_WIDTH = 425
LOGICAL_HEIGHT = 38
HISTORY_LEN = 16

# Paleta de colores Obsidian / Fluent Cyberpunk
COLORS = {
    "trans": "#020304",
    "card_bg": (24, 27, 34, 255),
    "card_bg_hover": (34, 38, 48, 255),
    "card_border": (40, 46, 58, 255),
    "card_border_hover": (54, 62, 78, 255),
    "btn_bg": (26, 30, 39, 255),
    "btn_halo": (45, 53, 68, 255),
    "btn_halo_active": (37, 99, 235, 255),
    "bolt_idle": (148, 163, 184, 255),
    "bolt_active": (255, 255, 255, 255),
    "led": (16, 185, 129, 255),
    "led_halo": (16, 185, 129, 90),
    "text_label": (156, 163, 175, 255),
    "ram_text": (96, 165, 250, 255),
    "ram_bar_bg": (35, 48, 62, 255),
    "ram_bar_fill": (96, 165, 250, 255),
    "divider": (55, 65, 81, 200),
    "cpu_text": (56, 189, 248, 255),
    "cpu_temp": (45, 212, 191, 255),
    "cpu_wave_line": (45, 212, 191, 255),
    "cpu_wave_fill": (56, 189, 248, 45),
    "gpu_text": (192, 132, 252, 255),
    "gpu_temp": (232, 121, 249, 255),
    "gpu_wave_line": (217, 70, 239, 255),
    "gpu_wave_fill": (217, 70, 239, 40),
    "dots": (100, 116, 139, 255),
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_config(data):
    try:
        current = load_config()
        current.update(data)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(current, f, indent=2)
    except Exception:
        pass

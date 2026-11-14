from PIL import Image, ImageDraw, ImageTk, ImageFont
from .config import LOGICAL_WIDTH, LOGICAL_HEIGHT, COLORS

class VisorRenderer:
    def __init__(self, dpi_scale, render_scale=2):
        self.dpi = dpi_scale
        self.render_scale = render_scale
        self.s = self.dpi * self.render_scale

        self.width = int(LOGICAL_WIDTH * self.dpi)
        self.height = int(LOGICAL_HEIGHT * self.dpi)

        self.canvas_w = int(LOGICAL_WIDTH * self.s)
        self.canvas_h = int(LOGICAL_HEIGHT * self.s)

        self.raw_img = Image.new("RGBA", (self.canvas_w, self.canvas_h), (2, 3, 4, 255))
        self.draw = ImageDraw.Draw(self.raw_img)

        font_size_main = int(11.5 * self.s)
        font_size_title = int(10.5 * self.s)
        try:
            self.font_main = ImageFont.truetype("seguisb.ttf", font_size_main)
            self.font_title = ImageFont.truetype("seguisb.ttf", font_size_title)
        except Exception:
            self.font_main = ImageFont.load_default()
            self.font_title = ImageFont.load_default()

    def render(self, ram, cpu, cpu_temp, gpu_util, gpu_temp,
               cpu_history, gpu_history, is_hovered, is_cleaning):
        s = self.s
        W = self.canvas_w
        H = self.canvas_h
        draw = self.draw

        # Fondo transparente de corte
        draw.rectangle([0, 0, W, H], fill=(2, 3, 4, 255))

        pad_x = 4 * s
        pad_y = 2 * s
        pill_h = H - 2 * pad_y
        r = pill_h // 2

        # Cápsula Obsidian
        card_fill = COLORS["card_bg_hover"] if is_hovered else COLORS["card_bg"]
        border_col = COLORS["card_border_hover"] if is_hovered else COLORS["card_border"]

        draw.rounded_rectangle(
            [pad_x, pad_y, W - pad_x, H - pad_y],
            radius=r, fill=card_fill, outline=border_col, width=max(1, int(1.4 * s))
        )

        # Botón Rayo con halo y LED
        btn_cx = int(22 * s)
        btn_cy = int((LOGICAL_HEIGHT / 2) * s)
        btn_r = int(13.5 * s)

        halo_col = COLORS["btn_halo_active"] if is_cleaning else COLORS["btn_halo"]
        draw.ellipse([btn_cx - btn_r, btn_cy - btn_r, btn_cx + btn_r, btn_cy + btn_r],
                     fill=COLORS["btn_bg"], outline=halo_col, width=max(1, int(1.5 * s)))

        cx, cy = btn_cx, btn_cy
        bolt_points = [
            (cx + 1.2 * s, cy - 7 * s),
            (cx - 4.5 * s, cy - 0.5 * s),
            (cx, cy - 0.5 * s),
            (cx - 2.5 * s, cy + 7 * s),
            (cx + 4.5 * s, cy - 0 * s),
            (cx + 0.5 * s, cy - 0 * s),
        ]
        bolt_col = COLORS["bolt_active"] if (is_cleaning or is_hovered) else COLORS["bolt_idle"]
        draw.polygon(bolt_points, fill=bolt_col)

        # LED Verde
        led_x = btn_cx + int(9.5 * s)
        led_y = btn_cy + int(9.5 * s)
        led_r = int(3.6 * s)
        draw.ellipse([led_x - led_r, led_y - led_r, led_x + led_r, led_y + led_r], fill=COLORS["led"])
        draw.ellipse([led_x - led_r - 2*s, led_y - led_r - 2*s, led_x + led_r + 2*s, led_y + led_r + 2*s],
                     outline=COLORS["led_halo"], width=int(1.4 * s))

        # RAM
        draw.text((int(48 * s), int(7 * s)), "RAM", fill=COLORS["text_label"], font=self.font_title)
        draw.text((int(82 * s), int(7 * s)), f"{ram}%", fill=COLORS["ram_text"], font=self.font_main)

        ram_bar_w = int(58 * s)
        ram_bar_fill = int((ram / 100.0) * ram_bar_w)
        draw.rounded_rectangle([int(50 * s), int(27 * s), int(50 * s) + ram_bar_w, int(29 * s)],
                               radius=1*s, fill=COLORS["ram_bar_bg"])
        draw.rounded_rectangle([int(50 * s), int(27 * s), int(50 * s) + ram_bar_fill, int(29 * s)],
                               radius=1*s, fill=COLORS["ram_bar_fill"])

        # Divisor 1
        x_div1 = int(126 * s)
        for y_dot in range(int(8 * s), int((LOGICAL_HEIGHT - 8) * s), int(4 * s)):
            draw.point((x_div1, y_dot), fill=COLORS["divider"])

        # CPU + Onda
        draw.text((int(140 * s), int(6 * s)), "CPU", fill=COLORS["text_label"], font=self.font_title)
        draw.text((int(175 * s), int(6 * s)), f"{cpu}%", fill=COLORS["cpu_text"], font=self.font_main)
        draw.text((int(215 * s), int(6 * s)), f"{cpu_temp}°", fill=COLORS["cpu_temp"], font=self.font_main)

        history_len = len(cpu_history)
        wave1_pts = []
        w_start_x = int(140 * s)
        w_width = int(100 * s)
        w_base_y = int(30 * s)
        step = w_width / max(1, history_len - 1)
        for i, val in enumerate(cpu_history):
            px = w_start_x + i * step
            py = w_base_y - (val / 100.0) * 10 * s - (2 * s if i % 2 == 1 else 0)
            wave1_pts.append((px, py))

        if len(wave1_pts) >= 2:
            fill_poly = [(wave1_pts[0][0], w_base_y)] + wave1_pts + [(wave1_pts[-1][0], w_base_y)]
            draw.polygon(fill_poly, fill=COLORS["cpu_wave_fill"])
            draw.line(wave1_pts, fill=COLORS["cpu_wave_line"], width=max(1, int(1.8 * s)))

        # Divisor 2
        x_div2 = int(258 * s)
        for y_dot in range(int(8 * s), int((LOGICAL_HEIGHT - 8) * s), int(4 * s)):
            draw.point((x_div2, y_dot), fill=COLORS["divider"])

        # GPU + Onda
        draw.text((int(272 * s), int(6 * s)), "GPU", fill=COLORS["text_label"], font=self.font_title)
        draw.text((int(308 * s), int(6 * s)), f"{gpu_util}%", fill=COLORS["gpu_text"], font=self.font_main)
        draw.text((int(344 * s), int(6 * s)), f"{gpu_temp}°", fill=COLORS["gpu_temp"], font=self.font_main)

        wave2_pts = []
        w2_start_x = int(272 * s)
        w2_width = int(100 * s)
        w2_base_y = int(30 * s)
        step2 = w2_width / max(1, len(gpu_history) - 1)
        for i, val in enumerate(gpu_history):
            px = w2_start_x + i * step2
            py = w2_base_y - (val / 100.0) * 10 * s - (1.5 * s if i % 2 == 1 else 0)
            wave2_pts.append((px, py))

        if len(wave2_pts) >= 2:
            fill2_poly = [(wave2_pts[0][0], w2_base_y)] + wave2_pts + [(wave2_pts[-1][0], w2_base_y)]
            draw.polygon(fill2_poly, fill=COLORS["gpu_wave_fill"])
            draw.line(wave2_pts, fill=COLORS["gpu_wave_line"], width=max(1, int(1.8 * s)))

        # Tres puntos
        more_x = int((LOGICAL_WIDTH - 26) * s)
        draw.ellipse([more_x, 12 * s, more_x + 2.5*s, 14.5 * s], fill=COLORS["dots"])
        draw.ellipse([more_x, 18 * s, more_x + 2.5*s, 20.5 * s], fill=COLORS["dots"])
        draw.ellipse([more_x, 24 * s, more_x + 2.5*s, 26.5 * s], fill=COLORS["dots"])

        final_img = self.raw_img.resize((self.width, self.height), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(final_img)

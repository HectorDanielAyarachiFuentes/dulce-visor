from PIL import Image, ImageDraw, ImageTk, ImageFont
import math
from .config import LOGICAL_WIDTH, LOGICAL_HEIGHT

def bezier_cubic(p0, p1, p2, p3, steps=32):
    """Calcula puntos a lo largo de una curva de Bézier cúbica de alta resolución."""
    pts = []
    for i in range(steps + 1):
        t = i / float(steps)
        u = 1.0 - t
        tt = t * t
        uu = u * u
        x = (uu * u) * p0[0] + (3 * uu * t) * p1[0] + (3 * u * tt) * p2[0] + (tt * t) * p3[0]
        y = (uu * u) * p0[1] + (3 * uu * t) * p1[1] + (3 * u * tt) * p2[1] + (tt * t) * p3[1]
        pts.append((x, y))
    return pts

def draw_smooth_stroke(draw, points, width, color, tip_color=None, tip_radius=None):
    """Traza un camino hiper-suave con extremos y juntas redondeadas sin quiebres ni polígonos toscos."""
    r = width / 2.0
    for p in points:
        draw.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=color)
    draw.line(points, fill=color, width=max(1, int(width)))
    if tip_color and tip_radius and len(points) > 0:
        tip_p = points[-1]
        draw.ellipse([tip_p[0] - tip_radius, tip_p[1] - tip_radius,
                      tip_p[0] + tip_radius, tip_p[1] + tip_radius], fill=tip_color)

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

        # Contador de animación para la colita
        self.tail_anim_frame = 0

    def draw_animal_accessories(self, draw, s, W, H, pad_left, pad_top, pill_h, r, pill_x1, skin):
        animal_type = skin.get("animal")
        if not animal_type:
            return

        self.tail_anim_frame = (self.tail_anim_frame + 1) % 60
        # Movimiento oscilante suave para la colita
        sway = math.sin(self.tail_anim_frame * (2 * math.pi / 30)) * (2.2 * s)

        # -----------------------------------------------------------------
        # 1. COLA (Curva Bézier cúbica continua, fluida y orgánica)
        # -----------------------------------------------------------------
        tail_col = skin.get("tail_color", (244, 114, 182, 255))
        tail_tip_col = skin.get("tail_tip", (255, 255, 255, 255))

        if animal_type == "gato":
            # Colita de gato premium: curva suave en S con punta de algodón
            tail_start = (pill_x1 - 4 * s, pad_top + pill_h // 2 + 2 * s)
            ctrl1 = (pill_x1 + 13 * s + sway * 0.4, pad_top + pill_h // 2 + 1 * s)
            ctrl2 = (pill_x1 + 14 * s + sway * 0.7, pad_top - 0.5 * s)
            tip = (pill_x1 + 4.5 * s + sway, pad_top - 3.5 * s)

            cat_tail_pts = bezier_cubic(tail_start, ctrl1, ctrl2, tip, steps=36)
            draw_smooth_stroke(draw, cat_tail_pts, width=5.0 * s, color=tail_col,
                               tip_color=tail_tip_col, tip_radius=4.2 * s)

        elif animal_type == "perro":
            # Colita de perro peluda y alegre con curva continua
            tail_start = (pill_x1 - 4 * s, pad_top + pill_h // 2 + 3 * s)
            ctrl1 = (pill_x1 + 10 * s + sway * 0.5, pad_top + pill_h // 2 - 2 * s)
            ctrl2 = (pill_x1 + 15 * s + sway * 0.8, pad_top + 2.5 * s)
            tip = (pill_x1 + 10.5 * s + sway * 1.2, pad_top - 1.5 * s)

            dog_tail_pts = bezier_cubic(tail_start, ctrl1, ctrl2, tip, steps=36)
            draw_smooth_stroke(draw, dog_tail_pts, width=5.6 * s, color=tail_col,
                               tip_color=tail_tip_col, tip_radius=4.5 * s)

        elif animal_type == "elefante":
            # Colita curva de elefante con mechón
            tail_start = (pill_x1 - 4 * s, pad_top + pill_h // 2 + 1 * s)
            ctrl1 = (pill_x1 + 6 * s, pad_top + pill_h // 2 + 3 * s + sway * 0.3)
            ctrl2 = (pill_x1 + 9 * s, pad_top + pill_h // 2 + 8 * s + sway * 0.6)
            tip = (pill_x1 + 8 * s, pad_top + pill_h // 2 + 12 * s + sway)

            ele_tail_pts = bezier_cubic(tail_start, ctrl1, ctrl2, tip, steps=30)
            draw_smooth_stroke(draw, ele_tail_pts, width=3.5 * s, color=tail_col,
                               tip_color=tail_tip_col, tip_radius=3.5 * s)

        # -----------------------------------------------------------------
        # 2. OREJAS Y DETALLES EN LA CABECITA (Izquierda, sobre el botón)
        # -----------------------------------------------------------------
        head_cx = pad_left + int(18 * s)
        ear_col = skin.get("ear_color", (32, 26, 36, 255))
        ear_inner = skin.get("ear_inner", (244, 114, 182, 255))
        ear_border = skin.get("ear_border", (244, 114, 182, 200))
        top_y = pad_top + 1 * s

        if animal_type == "gato":
            # Orejas de gato estilizadas con curvas suaves y puntas pulidas
            for side in [-1, 1]:
                cx_ear = head_cx + side * 7.5 * s
                ear_poly = [
                    (cx_ear - side * 5.5 * s, top_y + 1.5 * s),
                    (cx_ear, top_y - 8.2 * s),
                    (cx_ear + side * 5.5 * s, top_y + 1.5 * s)
                ]
                draw.polygon(ear_poly, fill=ear_col, outline=ear_border)
                ear_inner_poly = [
                    (cx_ear - side * 3.5 * s, top_y + 0.5 * s),
                    (cx_ear, top_y - 5.8 * s),
                    (cx_ear + side * 3.5 * s, top_y + 0.5 * s)
                ]
                draw.polygon(ear_inner_poly, fill=ear_inner)
                # Suavizar la punta superior redondeada
                draw.ellipse([cx_ear - 1.2 * s, top_y - 8.6 * s, cx_ear + 1.2 * s, top_y - 6.2 * s], fill=ear_border)

        elif animal_type == "perro":
            # Orejitas caídas sedosas con esquinas redondeadas naturales
            draw.rounded_rectangle([head_cx - 15 * s, top_y - 3 * s, head_cx - 5 * s, top_y + 13 * s],
                                   radius=int(5 * s), fill=ear_col, outline=ear_border, width=int(1.2 * s))
            draw.rounded_rectangle([head_cx - 13 * s, top_y + 0 * s, head_cx - 7 * s, top_y + 11 * s],
                                   radius=int(3 * s), fill=ear_inner)

            draw.rounded_rectangle([head_cx + 5 * s, top_y - 3 * s, head_cx + 15 * s, top_y + 13 * s],
                                   radius=int(5 * s), fill=ear_col, outline=ear_border, width=int(1.2 * s))
            draw.rounded_rectangle([head_cx + 7 * s, top_y + 0 * s, head_cx + 13 * s, top_y + 11 * s],
                                   radius=int(3 * s), fill=ear_inner)

        elif animal_type == "elefante":
            # Grandes orejas redondeadas de elefante
            draw.ellipse([head_cx - 17 * s, top_y - 4 * s, head_cx - 1 * s, top_y + 16 * s],
                         fill=ear_col, outline=ear_border, width=int(1.2 * s))
            draw.ellipse([head_cx - 14 * s, top_y - 1 * s, head_cx - 4 * s, top_y + 13 * s],
                         fill=ear_inner)

            draw.ellipse([head_cx + 1 * s, top_y - 4 * s, head_cx + 17 * s, top_y + 16 * s],
                         fill=ear_col, outline=ear_border, width=int(1.2 * s))
            draw.ellipse([head_cx + 4 * s, top_y - 1 * s, head_cx + 14 * s, top_y + 13 * s],
                         fill=ear_inner)

            # Trompita con curva Bézier cúbica suave y redondeada
            trunk_p0 = (head_cx - 8 * s, pad_top + pill_h // 2 + 5 * s)
            trunk_p1 = (head_cx - 15 * s, pad_top + pill_h // 2 + 9 * s)
            trunk_p2 = (head_cx - 18 * s, pad_top + pill_h // 2 - 2 * s)
            trunk_p3 = (head_cx - 12 * s, pad_top + pill_h // 2 - 3 * s)
            trunk_pts = bezier_cubic(trunk_p0, trunk_p1, trunk_p2, trunk_p3, steps=30)
            draw_smooth_stroke(draw, trunk_pts, width=4.5 * s, color=ear_border,
                               tip_color=(56, 189, 248, 255), tip_radius=2.2 * s)

    def render(self, ram, cpu, cpu_temp, gpu_util, gpu_temp,
               cpu_history, gpu_history, is_hovered, is_cleaning, skin):
        s = self.s
        W = self.canvas_w
        H = self.canvas_h
        draw = self.draw

        # Fondo transparente de corte
        draw.rectangle([0, 0, W, H], fill=(2, 3, 4, 255))

        # Márgenes seguros para que las orejitas y la colita nunca se recorten
        pad_left = 18 * s
        pad_right = 26 * s
        pad_top = 9 * s
        pad_bottom = 3 * s

        pill_x0 = pad_left
        pill_y0 = pad_top
        pill_x1 = W - pad_right
        pill_y1 = H - pad_bottom
        pill_h = pill_y1 - pill_y0
        r = pill_h // 2

        # Cápsula con color de la skin seleccionada
        card_fill = skin["card_bg_hover"] if is_hovered else skin["card_bg"]
        border_col = skin["card_border_hover"] if is_hovered else skin["card_border"]

        draw.rounded_rectangle(
            [pill_x0, pill_y0, pill_x1, pill_y1],
            radius=r, fill=card_fill, outline=border_col, width=max(1, int(1.4 * s))
        )

        # Accesorios animales: orejitas, trompa y colita con animación viva dentro del lienzo
        self.draw_animal_accessories(draw, s, W, H, pad_left, pad_top, pill_h, r, pill_x1, skin)

        # Botón Rayo con halo y LED
        btn_cx = pill_x0 + int(18 * s)
        btn_cy = pill_y0 + int(pill_h / 2)
        btn_r = int(12.5 * s)

        halo_col = skin["btn_halo_active"] if is_cleaning else skin["btn_halo"]
        draw.ellipse([btn_cx - btn_r, btn_cy - btn_r, btn_cx + btn_r, btn_cy + btn_r],
                     fill=skin["btn_bg"], outline=halo_col, width=max(1, int(1.5 * s)))

        cx, cy = btn_cx, btn_cy
        bolt_points = [
            (cx + 1.2 * s, cy - 6.5 * s),
            (cx - 4.2 * s, cy - 0.5 * s),
            (cx, cy - 0.5 * s),
            (cx - 2.2 * s, cy + 6.5 * s),
            (cx + 4.2 * s, cy - 0 * s),
            (cx + 0.5 * s, cy - 0 * s),
        ]
        bolt_col = skin["bolt_active"] if (is_cleaning or is_hovered) else skin["bolt_idle"]
        draw.polygon(bolt_points, fill=bolt_col)

        # LED indicador
        led_x = btn_cx + int(8.8 * s)
        led_y = btn_cy + int(8.8 * s)
        led_r = int(3.3 * s)
        draw.ellipse([led_x - led_r, led_y - led_r, led_x + led_r, led_y + led_r], fill=skin["led"])
        draw.ellipse([led_x - led_r - 1.8*s, led_y - led_r - 1.8*s, led_x + led_r + 1.8*s, led_y + led_r + 1.8*s],
                     outline=skin["led_halo"], width=int(1.3 * s))

        # Posiciones relativas a pill_x0 y pill_y0
        offset_y = pill_y0

        # RAM
        draw.text((pill_x0 + int(40 * s), offset_y + int(4.5 * s)), "RAM", fill=skin["text_label"], font=self.font_title)
        draw.text((pill_x0 + int(73 * s), offset_y + int(4.5 * s)), f"{ram}%", fill=skin["ram_text"], font=self.font_main)

        ram_bar_w = int(54 * s)
        ram_bar_fill = int((ram / 100.0) * ram_bar_w)
        draw.rounded_rectangle([pill_x0 + int(41 * s), offset_y + int(23 * s), pill_x0 + int(41 * s) + ram_bar_w, offset_y + int(25 * s)],
                               radius=1*s, fill=skin["ram_bar_bg"])
        draw.rounded_rectangle([pill_x0 + int(41 * s), offset_y + int(23 * s), pill_x0 + int(41 * s) + ram_bar_fill, offset_y + int(25 * s)],
                               radius=1*s, fill=skin["ram_bar_fill"])

        # Divisor 1
        x_div1 = pill_x0 + int(112 * s)
        for y_dot in range(int(offset_y + 6 * s), int(offset_y + pill_h - 6 * s), int(4 * s)):
            draw.point((x_div1, y_dot), fill=skin["divider"])

        # CPU + Onda
        draw.text((pill_x0 + int(124 * s), offset_y + int(4 * s)), "CPU", fill=skin["text_label"], font=self.font_title)
        draw.text((pill_x0 + int(158 * s), offset_y + int(4 * s)), f"{cpu}%", fill=skin["cpu_text"], font=self.font_main)
        draw.text((pill_x0 + int(196 * s), offset_y + int(4 * s)), f"{cpu_temp}°", fill=skin["cpu_temp"], font=self.font_main)

        history_len = len(cpu_history)
        wave1_pts = []
        w_start_x = pill_x0 + int(124 * s)
        w_width = int(98 * s)
        w_base_y = offset_y + int(26 * s)
        step = w_width / max(1, history_len - 1)
        for i, val in enumerate(cpu_history):
            px = w_start_x + i * step
            py = w_base_y - (val / 100.0) * 9 * s - (1.8 * s if i % 2 == 1 else 0)
            wave1_pts.append((px, py))

        if len(wave1_pts) >= 2:
            fill_poly = [(wave1_pts[0][0], w_base_y)] + wave1_pts + [(wave1_pts[-1][0], w_base_y)]
            draw.polygon(fill_poly, fill=skin["cpu_wave_fill"])
            draw.line(wave1_pts, fill=skin["cpu_wave_line"], width=max(1, int(1.8 * s)))

        # Divisor 2
        x_div2 = pill_x0 + int(236 * s)
        for y_dot in range(int(offset_y + 6 * s), int(offset_y + pill_h - 6 * s), int(4 * s)):
            draw.point((x_div2, y_dot), fill=skin["divider"])

        # GPU + Onda
        draw.text((pill_x0 + int(248 * s), offset_y + int(4 * s)), "GPU", fill=skin["text_label"], font=self.font_title)
        draw.text((pill_x0 + int(283 * s), offset_y + int(4 * s)), f"{gpu_util}%", fill=skin["gpu_text"], font=self.font_main)
        draw.text((pill_x0 + int(318 * s), offset_y + int(4 * s)), f"{gpu_temp}°", fill=skin["gpu_temp"], font=self.font_main)

        wave2_pts = []
        w2_start_x = pill_x0 + int(248 * s)
        w2_width = int(98 * s)
        w2_base_y = offset_y + int(26 * s)
        step2 = w2_width / max(1, len(gpu_history) - 1)
        for i, val in enumerate(gpu_history):
            px = w2_start_x + i * step2
            py = w2_base_y - (val / 100.0) * 9 * s - (1.5 * s if i % 2 == 1 else 0)
            wave2_pts.append((px, py))

        if len(wave2_pts) >= 2:
            fill2_poly = [(wave2_pts[0][0], w2_base_y)] + wave2_pts + [(wave2_pts[-1][0], w2_base_y)]
            draw.polygon(fill2_poly, fill=skin["gpu_wave_fill"])
            draw.line(wave2_pts, fill=skin["gpu_wave_line"], width=max(1, int(1.8 * s)))

        # Tres puntos
        more_x = pill_x1 - int(18 * s)
        draw.ellipse([more_x, offset_y + 9 * s, more_x + 2.5*s, offset_y + 11.5 * s], fill=skin["dots"])
        draw.ellipse([more_x, offset_y + 15 * s, more_x + 2.5*s, offset_y + 17.5 * s], fill=skin["dots"])
        draw.ellipse([more_x, offset_y + 21 * s, more_x + 2.5*s, offset_y + 23.5 * s], fill=skin["dots"])

        final_img = self.raw_img.resize((self.width, self.height), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(final_img)

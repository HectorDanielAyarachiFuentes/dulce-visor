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

        # -----------------------------------------------------------------
        # OREJITAS KAWAII CURVAS Y ORGÁNICAS (Izquierda, sobre la cabecita)
        # -----------------------------------------------------------------
        head_cx = pad_left + int(18 * s)
        ear_col = skin.get("ear_color", (32, 26, 36, 255))
        ear_inner = skin.get("ear_inner", (244, 114, 182, 255))
        ear_border = skin.get("ear_border", (244, 114, 182, 220))
        top_y = pad_top + 1 * s

        if animal_type == "gato":
            # Orejitas kawaii de gato con curva orgánica cóncava natural
            for side in [-1, 1]:
                p_base_out = (head_cx + side * 14.5 * s, top_y + 3.0 * s)
                p_tip = (head_cx + side * 9.0 * s, top_y - 7.5 * s)
                p_base_in = (head_cx + side * 2.0 * s, top_y)

                outer_edge = bezier_cubic(p_base_out, (head_cx + side * 14.0 * s, top_y - 2.0 * s),
                                          (head_cx + side * 11.5 * s, top_y - 6.0 * s), p_tip, 15)
                inner_edge = bezier_cubic(p_tip, (head_cx + side * 6.5 * s, top_y - 5.0 * s),
                                          (head_cx + side * 3.5 * s, top_y - 2.0 * s), p_base_in, 15)
                draw.polygon(outer_edge + inner_edge, fill=ear_col, outline=ear_border)

                # Interior rosado con curvatura a juego
                p_tip_in = (head_cx + side * 9.0 * s, top_y - 5.5 * s)
                outer_in = bezier_cubic((head_cx + side * 12.5 * s, top_y + 1.0 * s),
                                        (head_cx + side * 12.0 * s, top_y - 2.0 * s),
                                        (head_cx + side * 10.5 * s, top_y - 4.5 * s), p_tip_in, 10)
                inner_in = bezier_cubic(p_tip_in, (head_cx + side * 7.0 * s, top_y - 4.0 * s),
                                        (head_cx + side * 4.5 * s, top_y - 1.0 * s),
                                        (head_cx + side * 4.0 * s, top_y), 10)
                draw.polygon(outer_in + inner_in, fill=ear_inner)

        elif animal_type == "perro":
            # Orejitas caídas suaves estilo cachorro (Puppy) a ambos lados
            for side in [-1, 1]:
                p0 = (head_cx + side * 4.0 * s, top_y - 3.5 * s)
                p1 = (head_cx + side * 14.0 * s, top_y - 4.5 * s)
                p2 = (head_cx + side * 17.5 * s, top_y + 11.0 * s)
                p3 = (head_cx + side * 11.5 * s, top_y + 14.5 * s)
                p4 = (head_cx + side * 5.0 * s, top_y + 8.0 * s)

                edge1 = bezier_cubic(p0, p1, (head_cx + side * 18.0 * s, top_y + 3.0 * s), p2, 15)
                edge2 = bezier_cubic(p2, (head_cx + side * 16.5 * s, top_y + 16.0 * s),
                                     (head_cx + side * 13.5 * s, top_y + 16.5 * s), p3, 10)
                edge3 = bezier_cubic(p3, (head_cx + side * 8.0 * s, top_y + 12.0 * s),
                                     p4, (head_cx + side * 3.5 * s, top_y + 2.0 * s), 15)
                draw.polygon(edge1 + edge2 + edge3, fill=ear_col, outline=ear_border)

                # Interior acaramelado
                in1 = bezier_cubic((head_cx + side * 7.0 * s, top_y + 0.0 * s),
                                   (head_cx + side * 13.0 * s, top_y + 0.0 * s),
                                   (head_cx + side * 14.5 * s, top_y + 6.0 * s),
                                   (head_cx + side * 12.0 * s, top_y + 10.5 * s), 12)
                in2 = bezier_cubic((head_cx + side * 12.0 * s, top_y + 10.5 * s),
                                   (head_cx + side * 9.5 * s, top_y + 11.5 * s),
                                   (head_cx + side * 7.0 * s, top_y + 7.0 * s),
                                   (head_cx + side * 6.5 * s, top_y + 3.0 * s), 12)
                draw.polygon(in1 + in2, fill=ear_inner)

        elif animal_type == "elefante":
            # Orejotas majestuosas grandes y redondas de elefante
            for side in [-1, 1]:
                ox = head_cx + side * 11.0 * s
                oy = top_y + 4.5 * s
                draw.ellipse([ox - 8.5 * s, oy - 9.5 * s, ox + 8.5 * s, oy + 9.5 * s],
                             fill=ear_col, outline=ear_border, width=max(1, int(1.3 * s)))
                draw.ellipse([ox - 5.5 * s, oy - 6.5 * s, ox + 5.5 * s, oy + 6.5 * s], fill=ear_inner)

        elif animal_type == "jirafa":
            # Jirafa: Osíconos (cuernitos con pompón) + Orejas largas en forma de hoja
            for side in [-1, 1]:
                # Osíconos
                ox = head_cx + side * 4.5 * s
                draw.line([(ox, top_y + 2.0 * s), (ox, top_y - 6.5 * s)], fill=ear_border, width=max(1, int(2.8 * s)))
                draw.ellipse([ox - 2.6 * s, top_y - 9.0 * s, ox + 2.6 * s, top_y - 4.5 * s],
                             fill=(217, 119, 6, 255), outline=ear_border)

                # Orejas laterales alargadas en forma de hoja
                p_base = (head_cx + side * 7.0 * s, top_y + 1.0 * s)
                p_tip = (head_cx + side * 17.0 * s, top_y + 3.0 * s)
                p_low = (head_cx + side * 10.0 * s, top_y + 8.5 * s)

                top_curve = bezier_cubic(p_base, (head_cx + side * 10.0 * s, top_y - 1.5 * s),
                                         (head_cx + side * 14.5 * s, top_y + 0.5 * s), p_tip, 15)
                bottom_curve = bezier_cubic(p_tip, (head_cx + side * 14.0 * s, top_y + 7.0 * s),
                                            p_low, (head_cx + side * 6.0 * s, top_y + 4.0 * s), 15)
                draw.polygon(top_curve + bottom_curve, fill=ear_col, outline=ear_border)

                # Interior cálido
                in_top = bezier_cubic((head_cx + side * 8.5 * s, top_y + 1.5 * s),
                                      (head_cx + side * 11.5 * s, top_y + 0.5 * s),
                                      (head_cx + side * 14.0 * s, top_y + 2.0 * s),
                                      (head_cx + side * 15.0 * s, top_y + 3.2 * s), 10)
                in_bottom = bezier_cubic((head_cx + side * 15.0 * s, top_y + 3.2 * s),
                                         (head_cx + side * 13.0 * s, top_y + 5.5 * s),
                                         (head_cx + side * 10.0 * s, top_y + 6.0 * s),
                                         (head_cx + side * 8.0 * s, top_y + 3.5 * s), 10)
                draw.polygon(in_top + in_bottom, fill=ear_inner)

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

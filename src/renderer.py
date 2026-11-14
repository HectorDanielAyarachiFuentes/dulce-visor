from PIL import Image, ImageDraw, ImageTk, ImageFont
import math
from .config import LOGICAL_WIDTH, LOGICAL_HEIGHT

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
        sway = math.sin(self.tail_anim_frame * (2 * math.pi / 30)) * (2.5 * s)

        # -----------------------------------------------------------------
        # 1. COLA (A la derecha de la barra, curvada hacia arriba/adentro)
        # -----------------------------------------------------------------
        tail_start_x = pill_x1 - 4 * s
        tail_start_y = pad_top + pill_h // 2
        tail_col = skin.get("tail_color", (244, 114, 182, 255))
        tail_tip_col = skin.get("tail_tip", (255, 255, 255, 255))

        if animal_type == "gato":
            # Colita de gato elegante curvándose suavemente con pompón en la punta
            c1_x = pill_x1 + 8 * s
            c1_y = tail_start_y - 4 * s + sway * 0.4
            c2_x = pill_x1 + 10 * s + sway * 0.6
            c2_y = pad_top + 2 * s
            tip_x = pill_x1 + 3 * s + sway
            tip_y = pad_top - 2 * s

            tail_points = [
                (tail_start_x, tail_start_y),
                (c1_x, c1_y),
                (c2_x, c2_y),
                (tip_x, tip_y)
            ]
            draw.line(tail_points, fill=tail_col, width=max(2, int(4.5 * s)), joint="curve")
            draw.ellipse([tip_x - 3.5 * s, tip_y - 3.5 * s, tip_x + 3.5 * s, tip_y + 3.5 * s], fill=tail_tip_col)

        elif animal_type == "perro":
            # Colita alegre de perro moviéndose felizmente hacia arriba
            c1_x = pill_x1 + 7 * s + sway * 0.5
            c1_y = tail_start_y - 8 * s
            tip_x = pill_x1 + 11 * s + sway
            tip_y = pad_top - 1 * s

            draw.line([(tail_start_x, tail_start_y + 2 * s), (c1_x, c1_y), (tip_x, tip_y)],
                      fill=tail_col, width=max(2, int(5.5 * s)), joint="curve")
            draw.ellipse([tip_x - 4 * s, tip_y - 4 * s, tip_x + 4 * s, tip_y + 4 * s], fill=tail_tip_col)

        elif animal_type == "elefante":
            # Colita de elefante con mechón
            c1_x = pill_x1 + 6 * s
            c1_y = tail_start_y + 3 * s + sway * 0.3
            tip_x = pill_x1 + 8 * s + sway * 0.6
            tip_y = tail_start_y + 10 * s

            draw.line([(tail_start_x, tail_start_y), (c1_x, c1_y), (tip_x, tip_y)],
                      fill=tail_col, width=max(2, int(3.5 * s)), joint="curve")
            draw.ellipse([tip_x - 3 * s, tip_y - 1 * s, tip_x + 3 * s, tip_y + 5 * s], fill=tail_tip_col)

        # -----------------------------------------------------------------
        # 2. OREJAS Y DETALLES EN LA CABECITA (Izquierda, sobre el botón)
        # -----------------------------------------------------------------
        head_cx = pad_left + int(18 * s)
        ear_col = skin.get("ear_color", (32, 26, 36, 255))
        ear_inner = skin.get("ear_inner", (244, 114, 182, 255))
        ear_border = skin.get("ear_border", (244, 114, 182, 200))
        top_y = pad_top + 1 * s

        if animal_type == "gato":
            # Orejitas puntiagudas de gato
            ear_h = 7.5 * s
            e1 = [(head_cx - 12 * s, top_y + 2 * s),
                  (head_cx - 7 * s, top_y - ear_h),
                  (head_cx - 2 * s, top_y)]
            draw.polygon(e1, fill=ear_col, outline=ear_border)
            e1_in = [(head_cx - 10 * s, top_y + 1 * s),
                     (head_cx - 7 * s, top_y - ear_h + 2.5 * s),
                     (head_cx - 3.5 * s, top_y)]
            draw.polygon(e1_in, fill=ear_inner)

            e2 = [(head_cx + 2 * s, top_y),
                  (head_cx + 7 * s, top_y - ear_h),
                  (head_cx + 12 * s, top_y + 2 * s)]
            draw.polygon(e2, fill=ear_col, outline=ear_border)
            e2_in = [(head_cx + 3.5 * s, top_y),
                     (head_cx + 7 * s, top_y - ear_h + 2.5 * s),
                     (head_cx + 10 * s, top_y + 1 * s)]
            draw.polygon(e2_in, fill=ear_inner)

        elif animal_type == "perro":
            # Orejitas caídas y redondeadas a los lados
            draw.rounded_rectangle([head_cx - 15 * s, top_y - 2 * s, head_cx - 6 * s, top_y + 12 * s],
                                   radius=int(4 * s), fill=ear_col, outline=ear_border)
            draw.rounded_rectangle([head_cx - 13 * s, top_y + 1 * s, head_cx - 8 * s, top_y + 10 * s],
                                   radius=int(3 * s), fill=ear_inner)

            draw.rounded_rectangle([head_cx + 6 * s, top_y - 2 * s, head_cx + 15 * s, top_y + 12 * s],
                                   radius=int(4 * s), fill=ear_col, outline=ear_border)
            draw.rounded_rectangle([head_cx + 8 * s, top_y + 1 * s, head_cx + 13 * s, top_y + 10 * s],
                                   radius=int(3 * s), fill=ear_inner)

        elif animal_type == "elefante":
            # Grandes orejas redondeadas de elefante
            draw.ellipse([head_cx - 18 * s, top_y - 3 * s, head_cx - 2 * s, top_y + 17 * s],
                         fill=ear_col, outline=ear_border)
            draw.ellipse([head_cx - 15 * s, top_y - 0 * s, head_cx - 5 * s, top_y + 14 * s],
                         fill=ear_inner)

            draw.ellipse([head_cx + 2 * s, top_y - 3 * s, head_cx + 18 * s, top_y + 17 * s],
                         fill=ear_col, outline=ear_border)
            draw.ellipse([head_cx + 5 * s, top_y - 0 * s, head_cx + 15 * s, top_y + 14 * s],
                         fill=ear_inner)

            # Trompita curvada hacia arriba a la izquierda del botón
            trunk_pts = [
                (head_cx - 8 * s, pad_top + pill_h // 2 + 5 * s),
                (head_cx - 13 * s, pad_top + pill_h // 2 + 8 * s),
                (head_cx - 16 * s, pad_top + pill_h // 2 + 3 * s),
                (head_cx - 14 * s, pad_top + pill_h // 2 - 2 * s)
            ]
            draw.line(trunk_pts, fill=ear_col, width=max(2, int(4 * s)), joint="curve")

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
        pad_top = 8 * s
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

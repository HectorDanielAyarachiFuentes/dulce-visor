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

    def draw_animal_accessories(self, draw, s, W, H, pad_x, pad_y, pill_h, r, skin):
        animal_type = skin.get("animal")
        if not animal_type:
            return

        self.tail_anim_frame = (self.tail_anim_frame + 1) % 60
        # Movimiento oscilante suave para la colita
        sway = math.sin(self.tail_anim_frame * (2 * math.pi / 30)) * (3 * s)

        # -----------------------------------------------------------------
        # 1. COLA (A la derecha de la barra)
        # -----------------------------------------------------------------
        tail_start_x = W - pad_x - 3 * s
        tail_start_y = H // 2
        tail_col = skin.get("tail_color", (244, 114, 182, 255))
        tail_tip_col = skin.get("tail_tip", (255, 255, 255, 255))

        if animal_type == "gato":
            # Colita de gato con curva elegante hacia arriba y pompón suave
            c1_x = tail_start_x + 10 * s
            c1_y = tail_start_y - 2 * s + sway
            c2_x = tail_start_x + 6 * s + sway
            c2_y = pad_y - 12 * s
            tip_x = tail_start_x - 2 * s + sway
            tip_y = pad_y - 14 * s

            # Dibujar trazo curvo de la cola
            tail_points = [
                (tail_start_x, tail_start_y),
                (c1_x, c1_y),
                (c2_x, c2_y),
                (tip_x, tip_y)
            ]
            draw.line(tail_points, fill=tail_col, width=max(2, int(4.5 * s)), joint="curve")
            # Punta blanca de la colita
            draw.ellipse([tip_x - 3.5 * s, tip_y - 3.5 * s, tip_x + 3.5 * s, tip_y + 3.5 * s], fill=tail_tip_col)

        elif animal_type == "perro":
            # Colita de perro peluda y alegre meneándose hacia arriba
            c1_x = tail_start_x + 12 * s + sway
            c1_y = tail_start_y - 10 * s
            tip_x = tail_start_x + 16 * s + sway * 1.5
            tip_y = pad_y - 10 * s

            draw.line([(tail_start_x, tail_start_y + 2*s), (c1_x, c1_y), (tip_x, tip_y)],
                      fill=tail_col, width=max(2, int(5.5 * s)), joint="curve")
            draw.ellipse([tip_x - 4 * s, tip_y - 4 * s, tip_x + 4 * s, tip_y + 4 * s], fill=tail_tip_col)

        elif animal_type == "elefante":
            # Colita pequeña de elefante con mechoncito al final
            c1_x = tail_start_x + 8 * s
            c1_y = tail_start_y + 6 * s + sway * 0.5
            tip_x = tail_start_x + 10 * s
            tip_y = tail_start_y + 14 * s + sway

            draw.line([(tail_start_x, tail_start_y), (c1_x, c1_y), (tip_x, tip_y)],
                      fill=tail_col, width=max(2, int(3.5 * s)), joint="curve")
            # Mechón oscuro
            draw.ellipse([tip_x - 3 * s, tip_y - 1 * s, tip_x + 3 * s, tip_y + 5 * s], fill=tail_tip_col)

        # -----------------------------------------------------------------
        # 2. OREJAS Y DETALLES EN LA CABECITA (Izquierda, sobre el botón)
        # -----------------------------------------------------------------
        head_cx = int(22 * s)
        ear_col = skin.get("ear_color", (32, 26, 36, 255))
        ear_inner = skin.get("ear_inner", (244, 114, 182, 255))
        ear_border = skin.get("ear_border", (244, 114, 182, 200))

        if animal_type == "gato":
            # Orejitas puntiagudas de gato arriba del botón
            ear_w = 7 * s
            ear_h = 9 * s
            top_y = pad_y + 1 * s

            # Oreja izquierda
            e1 = [(head_cx - 13 * s, top_y + 3 * s),
                  (head_cx - 8 * s, top_y - ear_h),
                  (head_cx - 2 * s, top_y)]
            draw.polygon(e1, fill=ear_col, outline=ear_border)
            e1_in = [(head_cx - 11 * s, top_y + 2 * s),
                     (head_cx - 8 * s, top_y - ear_h + 3 * s),
                     (head_cx - 4 * s, top_y)]
            draw.polygon(e1_in, fill=ear_inner)

            # Oreja derecha
            e2 = [(head_cx + 2 * s, top_y),
                  (head_cx + 8 * s, top_y - ear_h),
                  (head_cx + 13 * s, top_y + 3 * s)]
            draw.polygon(e2, fill=ear_col, outline=ear_border)
            e2_in = [(head_cx + 4 * s, top_y),
                     (head_cx + 8 * s, top_y - ear_h + 3 * s),
                     (head_cx + 11 * s, top_y + 2 * s)]
            draw.polygon(e2_in, fill=ear_inner)

        elif animal_type == "perro":
            # Orejitas caídas y redondeadas a los lados
            top_y = pad_y + 2 * s
            # Oreja izquierda caída
            draw.rounded_rectangle([head_cx - 15 * s, top_y - 2 * s, head_cx - 6 * s, top_y + 12 * s],
                                   radius=int(4 * s), fill=ear_col, outline=ear_border)
            draw.rounded_rectangle([head_cx - 13 * s, top_y + 1 * s, head_cx - 8 * s, top_y + 10 * s],
                                   radius=int(3 * s), fill=ear_inner)

            # Oreja derecha caída
            draw.rounded_rectangle([head_cx + 6 * s, top_y - 2 * s, head_cx + 15 * s, top_y + 12 * s],
                                   radius=int(4 * s), fill=ear_col, outline=ear_border)
            draw.rounded_rectangle([head_cx + 8 * s, top_y + 1 * s, head_cx + 13 * s, top_y + 10 * s],
                                   radius=int(3 * s), fill=ear_inner)

        elif animal_type == "elefante":
            # Grandes orejas redondas de elefante
            top_y = pad_y
            draw.ellipse([head_cx - 19 * s, top_y - 2 * s, head_cx - 3 * s, top_y + 18 * s],
                         fill=ear_col, outline=ear_border)
            draw.ellipse([head_cx - 16 * s, top_y + 1 * s, head_cx - 6 * s, top_y + 15 * s],
                         fill=ear_inner)

            draw.ellipse([head_cx + 3 * s, top_y - 2 * s, head_cx + 19 * s, top_y + 18 * s],
                         fill=ear_col, outline=ear_border)
            draw.ellipse([head_cx + 6 * s, top_y + 1 * s, head_cx + 16 * s, top_y + 15 * s],
                         fill=ear_inner)

            # Trompita curvada hacia arriba a la izquierda del botón
            trunk_pts = [
                (head_cx - 8 * s, H // 2 + 6 * s),
                (head_cx - 14 * s, H // 2 + 10 * s),
                (head_cx - 18 * s, H // 2 + 4 * s),
                (head_cx - 16 * s, H // 2 - 1 * s)
            ]
            draw.line(trunk_pts, fill=ear_col, width=max(2, int(4 * s)), joint="curve")
            draw.ellipse([head_cx - 18 * s, H // 2 - 3 * s, head_cx - 14 * s, H // 2 + 1 * s],
                         fill=ear_border)

    def render(self, ram, cpu, cpu_temp, gpu_util, gpu_temp,
               cpu_history, gpu_history, is_hovered, is_cleaning, skin):
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

        # Cápsula con color de la skin seleccionada
        card_fill = skin["card_bg_hover"] if is_hovered else skin["card_bg"]
        border_col = skin["card_border_hover"] if is_hovered else skin["card_border"]

        draw.rounded_rectangle(
            [pad_x, pad_y, W - pad_x, H - pad_y],
            radius=r, fill=card_fill, outline=border_col, width=max(1, int(1.4 * s))
        )

        # Accesorios animales: orejitas, trompa y colita con animación viva
        self.draw_animal_accessories(draw, s, W, H, pad_x, pad_y, pill_h, r, skin)

        # Botón Rayo con halo y LED
        btn_cx = int(22 * s)
        btn_cy = int((LOGICAL_HEIGHT / 2) * s)
        btn_r = int(13.5 * s)

        halo_col = skin["btn_halo_active"] if is_cleaning else skin["btn_halo"]
        draw.ellipse([btn_cx - btn_r, btn_cy - btn_r, btn_cx + btn_r, btn_cy + btn_r],
                     fill=skin["btn_bg"], outline=halo_col, width=max(1, int(1.5 * s)))

        cx, cy = btn_cx, btn_cy
        bolt_points = [
            (cx + 1.2 * s, cy - 7 * s),
            (cx - 4.5 * s, cy - 0.5 * s),
            (cx, cy - 0.5 * s),
            (cx - 2.5 * s, cy + 7 * s),
            (cx + 4.5 * s, cy - 0 * s),
            (cx + 0.5 * s, cy - 0 * s),
        ]
        bolt_col = skin["bolt_active"] if (is_cleaning or is_hovered) else skin["bolt_idle"]
        draw.polygon(bolt_points, fill=bolt_col)

        # LED indicador
        led_x = btn_cx + int(9.5 * s)
        led_y = btn_cy + int(9.5 * s)
        led_r = int(3.6 * s)
        draw.ellipse([led_x - led_r, led_y - led_r, led_x + led_r, led_y + led_r], fill=skin["led"])
        draw.ellipse([led_x - led_r - 2*s, led_y - led_r - 2*s, led_x + led_r + 2*s, led_y + led_r + 2*s],
                     outline=skin["led_halo"], width=int(1.4 * s))

        # RAM
        draw.text((int(48 * s), int(7 * s)), "RAM", fill=skin["text_label"], font=self.font_title)
        draw.text((int(82 * s), int(7 * s)), f"{ram}%", fill=skin["ram_text"], font=self.font_main)

        ram_bar_w = int(58 * s)
        ram_bar_fill = int((ram / 100.0) * ram_bar_w)
        draw.rounded_rectangle([int(50 * s), int(27 * s), int(50 * s) + ram_bar_w, int(29 * s)],
                               radius=1*s, fill=skin["ram_bar_bg"])
        draw.rounded_rectangle([int(50 * s), int(27 * s), int(50 * s) + ram_bar_fill, int(29 * s)],
                               radius=1*s, fill=skin["ram_bar_fill"])

        # Divisor 1
        x_div1 = int(126 * s)
        for y_dot in range(int(8 * s), int((LOGICAL_HEIGHT - 8) * s), int(4 * s)):
            draw.point((x_div1, y_dot), fill=skin["divider"])

        # CPU + Onda
        draw.text((int(140 * s), int(6 * s)), "CPU", fill=skin["text_label"], font=self.font_title)
        draw.text((int(175 * s), int(6 * s)), f"{cpu}%", fill=skin["cpu_text"], font=self.font_main)
        draw.text((int(215 * s), int(6 * s)), f"{cpu_temp}°", fill=skin["cpu_temp"], font=self.font_main)

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
            draw.polygon(fill_poly, fill=skin["cpu_wave_fill"])
            draw.line(wave1_pts, fill=skin["cpu_wave_line"], width=max(1, int(1.8 * s)))

        # Divisor 2
        x_div2 = int(258 * s)
        for y_dot in range(int(8 * s), int((LOGICAL_HEIGHT - 8) * s), int(4 * s)):
            draw.point((x_div2, y_dot), fill=skin["divider"])

        # GPU + Onda
        draw.text((int(272 * s), int(6 * s)), "GPU", fill=skin["text_label"], font=self.font_title)
        draw.text((int(308 * s), int(6 * s)), f"{gpu_util}%", fill=skin["gpu_text"], font=self.font_main)
        draw.text((int(344 * s), int(6 * s)), f"{gpu_temp}°", fill=skin["gpu_temp"], font=self.font_main)

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
            draw.polygon(fill2_poly, fill=skin["gpu_wave_fill"])
            draw.line(wave2_pts, fill=skin["gpu_wave_line"], width=max(1, int(1.8 * s)))

        # Tres puntos
        more_x = int((LOGICAL_WIDTH - 26) * s)
        draw.ellipse([more_x, 12 * s, more_x + 2.5*s, 14.5 * s], fill=skin["dots"])
        draw.ellipse([more_x, 18 * s, more_x + 2.5*s, 20.5 * s], fill=skin["dots"])
        draw.ellipse([more_x, 24 * s, more_x + 2.5*s, 26.5 * s], fill=skin["dots"])

        final_img = self.raw_img.resize((self.width, self.height), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(final_img)

import pygame
import random
from src.settings import COLORS
from src.network import NetworkManager

# ─── Contenido educativo por tipo de caso ────────────────────────────────────
# Mapeado por case_id (int) → dict con tema, definición y consejo.
CASE_EDUCATION = {
    1: {
        "tema": "Acoso con Cuentas Anónimas",
        "info": (
            "Las cuentas anónimas se usan para acosar sin revelar la identidad. "
            "El anonimato no es protección: las plataformas y autoridades pueden "
            "rastrear la actividad."
        ),
        "consejo": (
            "¿Qué hacer? Bloquea la cuenta, guarda capturas como evidencia "
            "y repórtala a la plataforma. Nunca respondas: el silencio les quita poder."
        ),
    },
    2: {
        "tema": "Phishing",
        "info": (
            "El phishing es un engaño donde el acosador envía enlaces falsos "
            "para robar contraseñas o datos personales, haciéndose pasar por "
            "servicios conocidos o prometiendo premios."
        ),
        "consejo": (
            "¿Qué hacer? Nunca hagas clic en enlaces sospechosos. "
            "Verifica siempre la URL antes de ingresar datos. "
            "Si tienes dudas, entra directamente al sitio oficial."
        ),
    },
    3: {
        "tema": "Suplantación de Identidad",
        "info": (
            "La suplantación ocurre cuando alguien crea perfiles falsos con "
            "el nombre o fotos de otra persona para dañar su reputación "
            "o engañar a sus conocidos."
        ),
        "consejo": (
            "¿Qué hacer? Reporta el perfil falso a la plataforma con "
            "pruebas de identidad. Avisa a tus contactos para que no "
            "interactúen con la cuenta falsa."
        ),
    },
    4: {
        "tema": "Filtración de Datos Privados",
        "info": (
            "La filtración de datos ocurre cuando alguien comparte "
            "información privada (fotos, contraseñas, dirección) sin "
            "consentimiento, como forma de control o venganza."
        ),
        "consejo": (
            "¿Qué hacer? Cambia tus contraseñas de inmediato y activa "
            "la autenticación en dos pasos. Denuncia ante la policía "
            "y a la plataforma; compartir datos privados es delito."
        ),
    },
    5: {
        "tema": "Difusión de Rumores Online",
        "info": (
            "Los rumores digitales se propagan a gran velocidad y pueden "
            "dañar la reputación de una persona de forma permanente. "
            "Compartir un rumor falso también es una forma de ciberacoso."
        ),
        "consejo": (
            "¿Qué hacer? No compartas información sin verificarla. "
            "Si eres víctima, documenta los posts y denúncialos. "
            "Habla con un adulto de confianza o un orientador."
        ),
    },
    6: {
        "tema": "Sextorsión y Chantaje Digital",
        "info": (
            "La sextorsión es cuando alguien amenaza con publicar "
            "contenido íntimo o comprometedor para extorsionar a la víctima "
            "con dinero, favores o más imágenes."
        ),
        "consejo": (
            "¿Qué hacer? No pagues ni cedas: pagar empeora la situación. "
            "Guarda evidencia, bloquea al acosador y denuncia a las "
            "autoridades. Nunca estás solo/a."
        ),
    },
    7: {
        "tema": "Exclusión Digital (Ostracismo)",
        "info": (
            "La exclusión digital es ignorar, bloquear o apartar a alguien "
            "de grupos online de forma deliberada para aislarla socialmente. "
            "Aunque no hay palabras hirientes, el daño emocional es real."
        ),
        "consejo": (
            "¿Qué hacer? Busca otros grupos y comunidades donde te valoren. "
            "Habla con alguien de confianza. Si ocurre en el colegio, "
            "infórmalo a un docente o consejero."
        ),
    },
    8: {
        "tema": "Toxicidad en Videojuegos Online",
        "info": (
            "El acoso en juegos (insultos, trolling, sabotaje) afecta "
            "la salud mental de los jugadores. Los juegos deben ser "
            "espacios seguros para todos."
        ),
        "consejo": (
            "¿Qué hacer? Usa la función de silenciar y reportar dentro "
            "del juego. Guarda capturas del chat. No respondas con "
            "más insultos: bloquear es la jugada ganadora."
        ),
    },
    9: {
        "tema": "Memes Humillantes",
        "info": (
            "Crear o compartir memes con fotos reales de una persona "
            "sin su permiso para ridiculizarla es ciberacoso. "
            "El 'solo es un chiste' no justifica el daño causado."
        ),
        "consejo": (
            "¿Qué hacer? Reporta el contenido en la plataforma para "
            "su eliminación. Guarda evidencia. Usar imagen ajena sin "
            "consentimiento puede tener consecuencias legales."
        ),
    },
    10: {
        "tema": "Ataques a Clases Virtuales (Zoombombing)",
        "info": (
            "El Zoombombing es la intrusión no autorizada en reuniones "
            "virtuales para interrumpir, insultar o difundir contenido "
            "inapropiado. Afecta el derecho a la educación."
        ),
        "consejo": (
            "¿Qué hacer? Los docentes deben usar salas de espera y "
            "contraseñas en sus clases. Si ocurre, reporta al "
            "administrador de la plataforma y a las autoridades educativas."
        ),
    },
}

DEFAULT_EDUCATION = {
    "tema": "Ciberacoso",
    "info": (
        "El ciberacoso es el uso de tecnología para hostigar, amenazar "
        "o humillar a otra persona. Puede ocurrir en redes sociales, "
        "juegos, chats y correos electrónicos."
    ),
    "consejo": (
        "¿Qué hacer? Documenta, bloquea y reporta. Habla con un adulto "
        "de confianza. Recuerda: pedir ayuda es un acto de valentía, no de debilidad."
    ),
}


class ResultsScreen:
    def __init__(self, game):
        self.game = game
        self.font_title  = pygame.font.SysFont("courier new", 48, bold=True)
        self.font_text   = pygame.font.SysFont("courier new", 24)
        self.font_small  = pygame.font.SysFont("courier new", 14)
        self.font_medium = pygame.font.SysFont("courier new", 17)
        self.font_panel  = pygame.font.SysFont("courier new", 20, bold=True)

        self.btn_menu    = pygame.Rect(390, 500, 230, 55)
        self.btn_details = pygame.Rect(660, 500, 230, 55)
        self.result_type = "neutral"

        # ── Panel educativo ────────────────────────────────────────────────
        self.show_details = False
        self.panel_rect   = pygame.Rect(190, 120, 900, 480)

        # ── Rain/Matrix particles (victoria) ────────────────────────────────
        self._rain_drops = []
        self._rain_initialized = False

        # ── Glitch state (derrota) ───────────────────────────────────────────
        self._glitch_timer  = 0
        self._glitch_offset = 0
        self._glitch_lines  = []

        self._enter_time = 0

    # ─── ANIMACIONES ─────────────────────────────────────────────────────────

    def _reset_animation(self):
        self._rain_drops = []
        self._rain_initialized = False
        self._glitch_timer  = 0
        self._glitch_offset = 0
        self._glitch_lines  = []
        self._enter_time    = pygame.time.get_ticks()
        self.show_details   = False

    def _init_rain(self):
        if self._rain_initialized:
            return
        chars = "01ABCDEF@#<>[]!?abcdef①②③④⑤"
        for _ in range(80):
            self._rain_drops.append({
                "x": random.randint(0, 1280),
                "y": random.uniform(-600, 0),
                "speed": random.uniform(3, 9),
                "len": random.randint(5, 18),
                "chars": [random.choice(chars) for _ in range(20)],
                "alpha": random.randint(120, 255),
            })
        self._rain_initialized = True

    def _update_rain(self):
        chars = "01ABCDEF@#<>[]!?abcdef"
        for d in self._rain_drops:
            d["y"] += d["speed"]
            if d["y"] > 720 + 200:
                d["y"] = random.uniform(-200, 0)
                d["x"] = random.randint(0, 1280)
            if random.random() < 0.1:
                d["chars"][0] = random.choice(chars)

    def _draw_rain(self, screen):
        for d in self._rain_drops:
            for i, ch in enumerate(d["chars"][:d["len"]]):
                y = int(d["y"]) - i * 18
                if y < -20 or y > 740:
                    continue
                alpha = max(0, d["alpha"] - i * 14)
                surf = self.font_small.render(ch, True, (0, max(60, 255 - i * 10), 80))
                surf.set_alpha(alpha)
                screen.blit(surf, (d["x"], y))

    def _update_glitch(self):
        self._glitch_timer += 1
        if self._glitch_timer % 20 == 0:
            self._glitch_lines = []
            for _ in range(random.randint(3, 8)):
                self._glitch_lines.append({
                    "y":      random.randint(0, 720),
                    "h":      random.randint(2, 18),
                    "offset": random.randint(-40, 40),
                    "alpha":  random.randint(80, 200),
                    "color":  random.choice([(255, 0, 50), (0, 200, 255), (200, 0, 255)]),
                })
        self._glitch_offset = random.randint(-6, 6) if self._glitch_timer % 5 == 0 else 0

    def _draw_glitch(self, screen):
        for gl in self._glitch_lines:
            surf = pygame.Surface((1280, gl["h"]), pygame.SRCALPHA)
            surf.fill((*gl["color"], gl["alpha"]))
            screen.blit(surf, (gl["offset"], gl["y"]))

    # ─── PANEL EDUCATIVO ─────────────────────────────────────────────────────

    def _get_education(self):
        case_id = self.game.case_manager.active_case.get("case_id", 0)
        return CASE_EDUCATION.get(case_id, DEFAULT_EDUCATION)

    def _draw_wrapped(self, screen, text, font, color, rect, line_height=None):
        """Dibuja texto ajustado dentro de un Rect. Retorna la Y final usada."""
        if line_height is None:
            line_height = font.get_linesize() + 2
        words = text.split()
        lines = []
        cur = ""
        for w in words:
            test = (cur + " " + w).strip()
            if font.size(test)[0] <= rect.width:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)

        y = rect.y
        for line in lines:
            if y + line_height > rect.bottom:
                break
            surf = font.render(line, True, color)
            screen.blit(surf, (rect.x, y))
            y += line_height
        return y

    def _draw_education_panel(self, screen):
        edu = self._get_education()

        # Fondo semitransparente global
        overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Panel principal
        pr = self.panel_rect
        pygame.draw.rect(screen, (15, 22, 40), pr, border_radius=10)
        pygame.draw.rect(screen, COLORS["neon_blue"], pr, 2, border_radius=10)

        # Encabezado
        header_rect = pygame.Rect(pr.x, pr.y, pr.width, 52)
        pygame.draw.rect(screen, (0, 50, 80), header_rect,
                         border_top_left_radius=10, border_top_right_radius=10)
        pygame.draw.line(screen, COLORS["neon_blue"],
                         (pr.x, pr.y + 52), (pr.x + pr.width, pr.y + 52), 2)

        title_surf = self.font_panel.render("📋  DETALLES DEL CASO", True, COLORS["neon_blue"])
        screen.blit(title_surf, (pr.x + 20, pr.y + 14))

        # Nombre del caso
        case_title = self.game.case_manager.active_case.get("title", "Caso Desconocido")
        ct_surf = self.font_panel.render(f"Caso: {case_title}", True, COLORS["white"])
        screen.blit(ct_surf, (pr.x + 20, pr.y + 72))

        # Separador
        pygame.draw.line(screen, (40, 60, 80),
                         (pr.x + 20, pr.y + 100), (pr.x + pr.width - 20, pr.y + 100), 1)

        # Tema
        tema_surf = self.font_panel.render(f"Tema: {edu['tema']}", True, (255, 220, 60))
        screen.blit(tema_surf, (pr.x + 20, pr.y + 112))

        # Separador fino
        pygame.draw.line(screen, (40, 60, 80),
                         (pr.x + 20, pr.y + 140), (pr.x + pr.width - 20, pr.y + 140), 1)

        # ¿Qué es?
        que_surf = self.font_medium.render("¿Qué es?", True, COLORS["neon_blue"])
        screen.blit(que_surf, (pr.x + 20, pr.y + 152))
        info_rect = pygame.Rect(pr.x + 20, pr.y + 175, pr.width - 40, 140)
        y_after = self._draw_wrapped(screen, edu["info"], self.font_medium,
                                     COLORS["white"], info_rect)

        # Separador
        sep_y = y_after + 12
        pygame.draw.line(screen, (40, 60, 80),
                         (pr.x + 20, sep_y), (pr.x + pr.width - 20, sep_y), 1)

        # Consejo
        cons_surf = self.font_medium.render("Consejo de seguridad", True, COLORS["success_green"])
        screen.blit(cons_surf, (pr.x + 20, sep_y + 10))
        cons_rect = pygame.Rect(pr.x + 20, sep_y + 35, pr.width - 40, 140)
        self._draw_wrapped(screen, edu["consejo"], self.font_medium,
                           (200, 255, 200), cons_rect)

        # Separador antes del botón
        pygame.draw.line(screen, COLORS["neon_blue"],
                         (pr.x, pr.bottom - 58), (pr.x + pr.width, pr.bottom - 58), 1)

        # Botón cerrar
        btn_close = pygame.Rect(pr.centerx - 100, pr.bottom - 48, 200, 36)
        mouse_pos = pygame.mouse.get_pos()
        self._draw_btn(screen, btn_close, "✕  CERRAR", mouse_pos, alert=False)
        return btn_close

    # ─── BOTONES ─────────────────────────────────────────────────────────────

    def _draw_btn(self, screen, rect, text, mouse_pos, alert=False):
        is_hovered   = rect.collidepoint(mouse_pos)
        if alert:
            border_color = (255, 180, 0) if is_hovered else (200, 140, 0)
            bg_color     = (60, 40, 0)   if is_hovered else (30, 20, 0)
        else:
            border_color = COLORS["neon_blue_hover"] if is_hovered else COLORS["neon_blue"]
            bg_color     = (20, 60, 90)               if is_hovered else COLORS["panel"]
        pygame.draw.rect(screen, bg_color, rect, border_radius=6)
        pygame.draw.rect(screen, border_color, rect, 2, border_radius=6)
        text_color = COLORS["white"] if is_hovered else COLORS["gray_text"]
        label = self.font_medium.render(text, True, text_color)
        screen.blit(label, label.get_rect(center=rect.center))

    # ─── EVENTOS ─────────────────────────────────────────────────────────────

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            if self.show_details:
                # El panel está abierto — solo el botón CERRAR importa
                btn_close = pygame.Rect(self.panel_rect.centerx - 100,
                                        self.panel_rect.bottom - 48, 200, 36)
                if btn_close.collidepoint(pos):
                    self.show_details = False
                return  # Bloquear clics detrás del panel

            if self.btn_menu.collidepoint(pos):
                if hasattr(self.game, 'sound_manager'):
                    self.game.sound_manager.play("button_click")
                self.game.network.stop()
                self.game.network = NetworkManager()
                self.game.role = "detective"
                self.game.host_ip = ""
                self.game.connection_error = ""
                self.game.current_screen = "menu"
                self._reset_animation()

            elif self.btn_details.collidepoint(pos):
                if hasattr(self.game, 'sound_manager'):
                    self.game.sound_manager.play("button_click")
                self.show_details = True

        # ESC cierra el panel educativo si está abierto
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.show_details:
                self.show_details = False

    # ─── DRAW ─────────────────────────────────────────────────────────────────

    def draw(self, screen):
        if self._enter_time == 0:
            self._reset_animation()

        screen.fill(COLORS["background"])

        # Determinar resultado
        is_victory = False
        is_defeat  = False

        if self.game.role == "detective":
            if self.result_type == "good":
                color = COLORS["success_green"]; msg = "Has identificado correctamente al acosador."
                is_victory = True
            elif self.result_type == "bad":
                color = COLORS["alert_red"]; msg = "Has acusado a la persona equivocada."
                is_defeat = True
            elif self.result_type == "timeout":
                color = COLORS["alert_red"]; msg = "El tiempo se agotó. La víctima abandonó la escuela."
                is_defeat = True
            else:
                color = COLORS["gray_text"]; msg = "Investigación inconclusa."
        else:
            if self.result_type == "good":
                color = COLORS["alert_red"]; msg = "El detective te atrapó. Has perdido."
                is_defeat = True
            elif self.result_type == "bad":
                color = COLORS["success_green"]; msg = "Has engañado al detective. Has ganado."
                is_victory = True
            elif self.result_type == "timeout":
                color = COLORS["success_green"]; msg = "El detective no resolvió el caso a tiempo. Has ganado."
                is_victory = True
            else:
                color = COLORS["gray_text"]; msg = "Investiga el próximo caso."

        # Cinemáticas de fondo
        if is_victory:
            self._init_rain()
            self._update_rain()
            self._draw_rain(screen)
        elif is_defeat:
            self._update_glitch()
            self._draw_glitch(screen)

        ox = self._glitch_offset if is_defeat else 0

        title = self.font_title.render("CASO CERRADO", True, color)
        screen.blit(title, title.get_rect(center=(640 + ox, 190)))

        desc = self.font_text.render(msg, True, COLORS["white"])
        screen.blit(desc, desc.get_rect(center=(640 + ox, 285)))

        if is_victory:
            extra = self.font_text.render("¡El ciberacoso no tiene lugar aquí!", True, (180, 255, 180))
            screen.blit(extra, extra.get_rect(center=(640, 340)))
        elif is_defeat:
            extra = self.font_text.render("¡No te rindas! El detective sigue en pie.", True, (255, 180, 180))
            extra.set_alpha(180)
            screen.blit(extra, extra.get_rect(center=(640 + ox, 340)))

        # Pequeña pista bajo los mensajes
        hint = self.font_small.render(
            "Pulsa  'Detalles del Caso'  para aprender sobre este tipo de ciberacoso  →",
            True, (100, 160, 200))
        screen.blit(hint, hint.get_rect(center=(640, 455)))

        mouse_pos = pygame.mouse.get_pos()
        self._draw_btn(screen, self.btn_menu,    "VOLVER AL MENÚ",   mouse_pos)
        self._draw_btn(screen, self.btn_details, "Detalles del Caso", mouse_pos, alert=True)

        # Panel educativo encima de todo
        if self.show_details:
            self._draw_education_panel(screen)

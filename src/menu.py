import pygame
import math
import random
from src.settings import COLORS

# ── Cuántos botones tiene el menú principal ──────────────────────────────────
_BUTTON_COUNT = 6

class Menu:
    def __init__(self, game):
        self.game = game
        self.font_title    = pygame.font.SysFont("courier new", 72, bold=True)
        self.font_subtitle = pygame.font.SysFont("courier new", 28)
        self.font_button   = pygame.font.SysFont("courier new", 32, bold=True)
        self.font_input    = pygame.font.SysFont("courier new", 28)

        self.single_button = pygame.Rect(490, 280, 300, 50)
        self.host_button   = pygame.Rect(490, 340, 300, 50)
        self.join_button   = pygame.Rect(490, 400, 300, 50)
        self.help_button   = pygame.Rect(490, 460, 300, 50)
        self.exit_button   = pygame.Rect(490, 520, 300, 50)
        self.mute_button   = pygame.Rect(490, 580, 300, 50)

        self.joining      = False
        self.ip_text      = ""
        self.connect_button = pygame.Rect(490, 420, 300, 60)
        self.back_button    = pygame.Rect(490, 500, 300, 60)

        # ── Animación de entrada de botones ─────────────────────────────────
        # Cada botón "cae" desde arriba. _btn_anim[i] va de 0→1 (progreso)
        self._btn_anim   = [0.0] * _BUTTON_COUNT
        self._btn_delay  = [i * 6 for i in range(_BUTTON_COUNT)]   # frames de retardo escalonado
        self._btn_offset = [-120.0] * _BUTTON_COUNT                 # desplazamiento Y inicial

        # ── Glitch del título ────────────────────────────────────────────────
        self._glitch_timer    = 0
        self._glitch_interval = 200   # frames entre glitches
        self._glitch_active   = False
        self._glitch_frames   = 0
        self._glitch_x        = 0

        # ── Cursor parpadeante en subtítulo ─────────────────────────────────
        self._cursor_visible  = True
        self._cursor_timer    = 0
        self._cursor_interval = 30    # frames de parpadeo

        # ── Partículas de fondo ──────────────────────────────────────────────
        self._particles = []
        for _ in range(60):
            self._particles.append({
                "x":     random.uniform(0, 1280),
                "y":     random.uniform(0, 720),
                "vx":    random.uniform(-0.3, 0.3),
                "vy":    random.uniform(-0.4, -0.1),
                "r":     random.randint(1, 3),
                "alpha": random.randint(40, 140),
            })

    # ─── LÓGICA DE ANIMACIONES ────────────────────────────────────────────────

    def _update_animations(self):
        # Entrada de botones (easing out-bounce suave)
        for i in range(_BUTTON_COUNT):
            if self._btn_delay[i] > 0:
                self._btn_delay[i] -= 1
                continue
            if self._btn_anim[i] < 1.0:
                self._btn_anim[i] = min(1.0, self._btn_anim[i] + 0.07)
                # easing out-elastic ligero
                t = self._btn_anim[i]
                ease = 1 - (1 - t) ** 3
                self._btn_offset[i] = -120 * (1 - ease)

        # Glitch del título
        self._glitch_timer += 1
        if self._glitch_active:
            self._glitch_frames -= 1
            if self._glitch_frames <= 0:
                self._glitch_active = False
                self._glitch_x      = 0
        elif self._glitch_timer >= self._glitch_interval:
            self._glitch_timer    = 0
            self._glitch_interval = random.randint(140, 280)
            self._glitch_active   = True
            self._glitch_frames   = random.randint(4, 10)
            self._glitch_x        = random.choice([-8, -5, 5, 8, -12, 12])

        # Cursor parpadeante
        self._cursor_timer += 1
        if self._cursor_timer >= self._cursor_interval:
            self._cursor_timer   = 0
            self._cursor_visible = not self._cursor_visible

        # Partículas flotantes
        for p in self._particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if p["y"] < -5:
                p["y"]     = 725
                p["x"]     = random.uniform(0, 1280)
                p["alpha"] = random.randint(40, 140)
            if p["x"] < 0:   p["x"] = 1280
            if p["x"] > 1280: p["x"] = 0

    # ─── DIBUJO DE PARTÍCULAS ────────────────────────────────────────────────

    def _draw_particles(self, screen):
        for p in self._particles:
            surf = pygame.Surface((p["r"] * 2, p["r"] * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*COLORS["neon_blue"], p["alpha"]),
                               (p["r"], p["r"]), p["r"])
            screen.blit(surf, (int(p["x"]) - p["r"], int(p["y"]) - p["r"]))

    # ─── BOTÓN ANIMADO ───────────────────────────────────────────────────────

    def _animated_rect(self, base_rect, btn_index):
        """Devuelve el Rect desplazado según el progreso de la animación."""
        off = int(self._btn_offset[btn_index])
        return pygame.Rect(base_rect.x, base_rect.y + off, base_rect.width, base_rect.height)

    def draw_button(self, screen, rect, text, mouse_pos, btn_index=0, alpha=255):
        anim_rect = self._animated_rect(rect, btn_index)
        is_hovered   = anim_rect.collidepoint(mouse_pos)
        border_color = COLORS["neon_blue_hover"] if is_hovered else COLORS["neon_blue"]
        bg_color     = (20, 60, 90) if is_hovered else COLORS["panel"]

        # Superficie con alpha para fade-in suave
        t     = self._btn_anim[btn_index]
        alpha = int(255 * min(1.0, t * 2))

        btn_surf = pygame.Surface((anim_rect.width, anim_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(btn_surf, (*bg_color, alpha),
                         (0, 0, anim_rect.width, anim_rect.height), border_radius=5)
        pygame.draw.rect(btn_surf, (*border_color, alpha),
                         (0, 0, anim_rect.width, anim_rect.height), 2, border_radius=5)

        text_color = COLORS["white"] if is_hovered else COLORS["gray_text"]
        label = self.font_button.render(text, True, text_color)
        label.set_alpha(alpha)
        btn_surf.blit(label, label.get_rect(center=(anim_rect.width // 2, anim_rect.height // 2)))

        screen.blit(btn_surf, anim_rect.topleft)
        return anim_rect   # regresamos el rect animado para hit-testing

    # ─── EVENTOS ─────────────────────────────────────────────────────────────

    def handle_event(self, event):
        # Recalcular rects animados para hit-testing correcto
        btns = [
            self._animated_rect(self.single_button, 0),
            self._animated_rect(self.host_button,   1),
            self._animated_rect(self.join_button,   2),
            self._animated_rect(self.help_button,   3),
            self._animated_rect(self.exit_button,   4),
            self._animated_rect(self.mute_button,   5),
        ]

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.joining:
                if btns[0].collidepoint(event.pos):
                    self._sfx()
                    self.game.role = "detective"
                    self.game.start_new_investigation()
                    self.game.start_transition("investigation")
                elif btns[1].collidepoint(event.pos):
                    self._sfx(); self.game.host_game()
                elif btns[2].collidepoint(event.pos):
                    self._sfx(); self.joining = True; self.ip_text = ""
                elif btns[3].collidepoint(event.pos):
                    self._sfx(); self.game.show_help = True
                elif btns[4].collidepoint(event.pos):
                    self._sfx(); self.game.running = False
                elif btns[5].collidepoint(event.pos):
                    self._sfx()
                    if hasattr(self.game, 'sound_manager'):
                        self.game.sound_manager.toggle_mute()
            else:
                if self.connect_button.collidepoint(event.pos):
                    self._sfx(); self.game.join_game(self.ip_text)
                elif self.back_button.collidepoint(event.pos):
                    self._sfx(); self.joining = False

        elif event.type == pygame.KEYDOWN and self.joining:
            if event.key == pygame.K_BACKSPACE:
                self.ip_text = self.ip_text[:-1]
            elif event.key == pygame.K_RETURN:
                self.game.join_game(self.ip_text)
            else:
                if len(self.ip_text) < 15 and (event.unicode.isdigit() or event.unicode == '.'):
                    self.ip_text += event.unicode

    def _sfx(self):
        if hasattr(self.game, 'sound_manager'):
            self.game.sound_manager.play("button_click")

    # ─── DRAW ────────────────────────────────────────────────────────────────

    def draw(self, screen):
        self._update_animations()

        screen.fill(COLORS["background"])

        # Grid de fondo (igual que antes)
        for i in range(0, 1280, 40):
            pygame.draw.line(screen, (15, 25, 40), (i, 0), (i, 720))
        for i in range(0, 720, 40):
            pygame.draw.line(screen, (15, 25, 40), (0, i), (1280, i))

        # Partículas flotantes
        self._draw_particles(screen)

        # ── Título con glitch ─────────────────────────────────────────────
        title_text = "BEHIND THE SCREEN"
        title_surf = self.font_title.render(title_text, True, COLORS["neon_blue"])
        title_rect = title_surf.get_rect(center=(640, 150))

        if self._glitch_active:
            # Capa roja desplazada (canal izquierdo)
            r_surf = self.font_title.render(title_text, True, (255, 30, 80))
            r_surf.set_alpha(160)
            screen.blit(r_surf, (title_rect.x + self._glitch_x + 3, title_rect.y))
            # Capa cyan desplazada (canal derecho)
            c_surf = self.font_title.render(title_text, True, (0, 255, 220))
            c_surf.set_alpha(160)
            screen.blit(c_surf, (title_rect.x - self._glitch_x - 3, title_rect.y + 2))
            # Líneas de ruido horizontal aleatoria durante glitch
            for _ in range(random.randint(2, 5)):
                gy = random.randint(title_rect.top, title_rect.bottom)
                gh = random.randint(2, 6)
                gsurf = pygame.Surface((title_rect.width + 20, gh), pygame.SRCALPHA)
                gsurf.fill((200, 0, 255, random.randint(60, 140)))
                screen.blit(gsurf, (title_rect.x - 10, gy))

        screen.blit(title_surf, title_rect)

        # ── Subtítulo con cursor parpadeante ─────────────────────────────
        cursor_char = "_" if self._cursor_visible else " "
        sub_text = f"> SYSTEM.LOGIN() :: CYBER DETECTIVE{cursor_char}"
        subtitle  = self.font_subtitle.render(sub_text, True, COLORS["white"])
        screen.blit(subtitle, subtitle.get_rect(center=(640, 225)))

        mouse_pos = pygame.mouse.get_pos()

        if not self.joining:
            mute_label = "UNMUTE" if hasattr(self.game, 'sound_manager') and self.game.sound_manager.muted else "MUTE"
            labels = ["SINGLE PLAYER", "HOST GAME", "JOIN GAME", "AYUDA", "SALIR", mute_label]
            rects  = [self.single_button, self.host_button, self.join_button,
                      self.help_button,   self.exit_button, self.mute_button]
            for i, (rect, label) in enumerate(zip(rects, labels)):
                self.draw_button(screen, rect, label, mouse_pos, btn_index=i)

            if self.game.network and self.game.network.is_server and not self.game.network.connected:
                msg = self.font_input.render(
                    f"Esperando jugador en IP: {self.game.host_ip} ...", True, COLORS["neon_blue"])
                screen.blit(msg, msg.get_rect(center=(640, 655)))
                start_msg = self.font_input.render(
                    "(Puedes empezar en Single Player si no hay conexión)", True, COLORS["gray_text"])
                screen.blit(start_msg, start_msg.get_rect(center=(640, 690)))
        else:
            prompt = self.font_input.render("Ingresa la IP del Host:", True, COLORS["white"])
            screen.blit(prompt, prompt.get_rect(center=(640, 300)))

            input_rect = pygame.Rect(490, 340, 300, 50)
            pygame.draw.rect(screen, COLORS["panel"], input_rect)
            pygame.draw.rect(screen, COLORS["neon_blue"], input_rect, 2)

            ip_surf = self.font_input.render(self.ip_text + "_", True, COLORS["neon_blue"])
            screen.blit(ip_surf, (input_rect.x + 10, input_rect.y + 10))

            self.draw_button(screen, self.connect_button, "CONECTAR", mouse_pos, btn_index=0)
            self.draw_button(screen, self.back_button,    "VOLVER",   mouse_pos, btn_index=1)

            if hasattr(self.game, 'connection_error') and self.game.connection_error:
                err = self.font_input.render(self.game.connection_error, True, COLORS["alert_red"])
                screen.blit(err, err.get_rect(center=(640, 600)))

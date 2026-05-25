import pygame
import math
from src.settings import COLORS

class InvestigationScreen:

    def __init__(self, game):
        self.game = game
        self.font_title = pygame.font.SysFont("courier new", 24, bold=True)
        self.font_text  = pygame.font.SysFont("courier new", 18)

        # Paneles
        self.panel_suspects = pygame.Rect(20,  20,  300, 680)
        self.panel_chat     = pygame.Rect(340, 20,  500, 680)
        self.panel_clues    = pygame.Rect(860, 20,  400, 500)
        self.panel_actions  = pygame.Rect(860, 540, 400, 160)

        # Botones
        self.btn_graph    = pygame.Rect(880, 550, 360, 40)
        self.btn_interview= pygame.Rect(880, 600, 360, 40)
        self.btn_accuse   = pygame.Rect(880, 650, 360, 40)

        # Lógica de juego
        self.selected_suspect = None
        self.suspect_rects    = {}

        # ── Efecto de tipeo en pistas ────────────────────────────────────────
        # Guardamos el texto "conocido" y cuántos chars se han revelado por pista
        self._clue_revealed   = {}   # clue_text → chars revealed (int)
        self._clue_timer      = 0
        self._clue_speed      = 2    # frames por carácter

        # ── Highlight flash en pista nueva ──────────────────────────────────
        self._new_clue_flash  = {}   # clue_text → frames restantes de flash
        self._prev_clues      = []   # snapshot anterior para detectar nuevas

    # ─── TIPEO ───────────────────────────────────────────────────────────────

    def _update_typing(self):
        current_clues = list(self.game.case_manager.get_clues())

        # Detectar pistas nuevas
        for clue in current_clues:
            if clue not in self._clue_revealed:
                self._clue_revealed[clue]  = 0
                self._new_clue_flash[clue] = 45   # 0.75s de flash

        # Avanzar caracteres
        self._clue_timer += 1
        if self._clue_timer >= self._clue_speed:
            self._clue_timer = 0
            for clue in current_clues:
                if self._clue_revealed.get(clue, 0) < len(clue):
                    self._clue_revealed[clue] += 1

        # Tick flash
        for clue in list(self._new_clue_flash.keys()):
            self._new_clue_flash[clue] -= 1
            if self._new_clue_flash[clue] <= 0:
                del self._new_clue_flash[clue]

        # Limpiar pistas borradas
        for key in list(self._clue_revealed.keys()):
            if key not in current_clues:
                del self._clue_revealed[key]
                self._new_clue_flash.pop(key, None)

        self._prev_clues = current_clues

    def _clue_display(self, clue):
        """Texto a mostrar para una pista (puede estar incompleto)."""
        revealed = self._clue_revealed.get(clue, len(clue))
        return clue[:revealed]

    # ─── EVENTOS ─────────────────────────────────────────────────────────────

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.current_screen = "menu"

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for suspect, rect in self.suspect_rects.items():
                    if rect.collidepoint(event.pos):
                        self.selected_suspect = suspect

                if self.btn_graph.collidepoint(event.pos):
                    self._sfx(); self.game.start_transition("graph")
                elif self.btn_interview.collidepoint(event.pos):
                    if self.selected_suspect:
                        self._sfx()
                        self.game.interview_screen.start_interview(self.selected_suspect)
                        self.game.start_transition("interview")
                elif self.btn_accuse.collidepoint(event.pos):
                    if self.selected_suspect:
                        self._sfx()
                        bully = self.game.case_manager.active_case.get("bully")
                        if self.selected_suspect == bully:
                            self.game.results_screen.result_type = "good"
                            if hasattr(self.game, "sound_manager"):
                                self.game.sound_manager.play("success")
                        else:
                            self.game.results_screen.result_type = "bad"
                            if hasattr(self.game, "sound_manager"):
                                self.game.sound_manager.play("error")
                    else:
                        self.game.results_screen.result_type = "neutral"
                    self.game.start_transition("results")

    def _sfx(self):
        if hasattr(self.game, "sound_manager"):
            self.game.sound_manager.play("button_click")

    # ─── HELPERS DE DIBUJO ───────────────────────────────────────────────────

    def draw_panel(self, screen, rect, title):
        pygame.draw.rect(screen, COLORS["panel"], rect, border_radius=8)
        pygame.draw.rect(screen, COLORS["neon_blue"], rect, 1, border_radius=8)
        title_surf = self.font_title.render(title, True, COLORS["neon_blue"])
        screen.blit(title_surf, (rect.x + 15, rect.y + 15))
        pygame.draw.line(screen, COLORS["neon_blue"],
                         (rect.x, rect.y + 50), (rect.x + rect.width, rect.y + 50))

    def draw_button(self, screen, rect, text, mouse_pos, alert=False):
        is_hovered   = rect.collidepoint(mouse_pos)
        base_color   = COLORS["alert_red"]      if alert else COLORS["neon_blue"]
        hover_color  = (255, 100, 100)           if alert else COLORS["neon_blue_hover"]
        border_color = hover_color if is_hovered else base_color
        bg_color     = (80, 20, 20) if alert and is_hovered else (20, 60, 90) if is_hovered else COLORS["background"]
        pygame.draw.rect(screen, bg_color, rect, border_radius=5)
        pygame.draw.rect(screen, border_color, rect, 2, border_radius=5)
        text_color = COLORS["white"] if is_hovered else COLORS["gray_text"]
        label = self.font_title.render(text, True, text_color)
        screen.blit(label, label.get_rect(center=rect.center))

    def draw_wrapped_text(self, screen, text, font, color, x, y, max_width):
        words = text.split(' ')
        lines, current_line = [], []
        for word in words:
            test = ' '.join(current_line + [word])
            if font.size(test)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line: lines.append(' '.join(current_line))
                current_line = [word]
        if current_line: lines.append(' '.join(current_line))
        y_pos = y
        for line in lines:
            surf = font.render(line, True, color)
            screen.blit(surf, (x, y_pos))
            y_pos += font.get_linesize()
        return y_pos - y

    # ─── DRAW ─────────────────────────────────────────────────────────────────

    def draw(self, screen):
        self._update_typing()

        screen.fill(COLORS["background"])

        self.draw_panel(screen, self.panel_suspects, "PERFILES & SOSPECHOSOS")
        self.draw_panel(screen, self.panel_chat,     "MENSAJES INTERCEPTADOS")
        self.draw_panel(screen, self.panel_clues,    "PISTAS RECOLECTADAS")

        pygame.draw.rect(screen, COLORS["panel"],    self.panel_actions, border_radius=8)
        pygame.draw.rect(screen, COLORS["neon_blue"],self.panel_actions, 1, border_radius=8)

        mouse_pos = pygame.mouse.get_pos()
        self.draw_button(screen, self.btn_graph,    "ANALIZAR RED",      mouse_pos)
        self.draw_button(screen, self.btn_interview,"ENTREVISTAR",       mouse_pos)
        self.draw_button(screen, self.btn_accuse,   "ACUSAR SOSPECHOSO", mouse_pos, alert=True)

        # Timer
        rem_ms  = self.game.case_manager.get_remaining_time()
        mins    = int(rem_ms // 60000)
        secs    = int((rem_ms % 60000) // 1000)
        t_color = COLORS["alert_red"] if mins < 2 else COLORS["neon_blue"]
        t_surf  = self.font_title.render(f"TIEMPO: {mins:02d}:{secs:02d}", True, t_color)
        screen.blit(t_surf, (860, 510))

        # ── Sospechosos ───────────────────────────────────────────────────
        y_offset = 70
        self.suspect_rects.clear()
        for suspect in self.game.case_manager.get_suspects():
            color  = COLORS["neon_blue"] if self.selected_suspect == suspect else COLORS["white"]
            prefix = "[x]" if self.selected_suspect == suspect else ">"
            surf   = self.font_text.render(f"{prefix} {suspect}", True, color)
            rect   = surf.get_rect(topleft=(self.panel_suspects.x + 15,
                                            self.panel_suspects.y + y_offset))
            click_rect = pygame.Rect(rect.x, rect.y - 5,
                                     self.panel_suspects.width - 30, rect.height + 10)
            self.suspect_rects[suspect] = click_rect
            if self.selected_suspect == suspect:
                pygame.draw.rect(screen, (20, 60, 90), click_rect, border_radius=4)
            screen.blit(surf, rect.topleft)
            y_offset += 40

        # ── Mensajes ──────────────────────────────────────────────────────
        y_offset = 70
        max_chat = self.panel_chat.width - 30
        for msg in self.game.case_manager.get_messages():
            clase = self.game.decision_tree.classify_message_automatic(msg)
            c_msg = COLORS["alert_red"] if clase in ["Mensaje ofensivo", "Mensaje grave", "Cyberbullying"] else COLORS["white"]
            used  = self.draw_wrapped_text(screen, f"[*] {msg}", self.font_text,
                                           COLORS["white"],
                                           self.panel_chat.x + 15,
                                           self.panel_chat.y + y_offset, max_chat)
            s_cls = self.font_text.render(f"-> [{clase}]", True, c_msg)
            screen.blit(s_cls, (self.panel_chat.x + 15,
                                self.panel_chat.y + y_offset + used + 5))
            y_offset += used + 35

        # ── Pistas con efecto de tipeo ────────────────────────────────────
        y_offset  = 70
        max_clue  = self.panel_clues.width - 30
        now_ticks = pygame.time.get_ticks()

        for clue in self.game.case_manager.get_clues():
            displayed = self._clue_display(clue)
            text_draw = f"- {displayed}"

            # Color: flash amarillo si es nueva, azul si ya se reveló completa
            if clue in self._new_clue_flash:
                flash_t = self._new_clue_flash[clue] / 45.0
                r = int(0   + (255 - 0)   * flash_t)
                g = int(200 + (220 - 200) * flash_t)
                b = int(255 * (1 - flash_t))
                clue_color = (r, g, b)
            else:
                clue_color = COLORS["neon_blue"]

            used = self.draw_wrapped_text(screen, text_draw, self.font_text,
                                          clue_color,
                                          self.panel_clues.x + 15,
                                          self.panel_clues.y + y_offset, max_clue)

            # Cursor de tipeo si aún no se reveló completo
            if self._clue_revealed.get(clue, len(clue)) < len(clue):
                # Calcular posición aproximada del cursor al final del texto
                last_line_w = self.font_text.size(text_draw.split('\n')[-1])[0]
                cx = self.panel_clues.x + 15 + min(last_line_w, max_clue)
                cy = self.panel_clues.y + y_offset + used - self.font_text.get_linesize()
                if (now_ticks // 250) % 2 == 0:
                    c_surf = self.font_text.render("▌", True, COLORS["neon_blue"])
                    screen.blit(c_surf, (cx, cy))

            y_offset += used + 15

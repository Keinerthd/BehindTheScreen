import pygame
from src.settings import COLORS

class InvestigationScreen:

    def __init__(self, game):
        self.game = game
        self.font_title = pygame.font.SysFont("courier new", 24, bold=True)
        self.font_text = pygame.font.SysFont("courier new", 18)
        
        # Paneles
        self.panel_suspects = pygame.Rect(20, 20, 300, 680)
        self.panel_chat = pygame.Rect(340, 20, 500, 680)
        self.panel_clues = pygame.Rect(860, 20, 400, 500)
        self.panel_actions = pygame.Rect(860, 540, 400, 160)

        # Botones
        self.btn_graph = pygame.Rect(880, 550, 360, 40)
        self.btn_interview = pygame.Rect(880, 600, 360, 40)
        self.btn_accuse = pygame.Rect(880, 650, 360, 40)
        
        # Lógica de juego
        self.selected_suspect = None
        self.suspect_rects = {} # suspect_name: rect

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.current_screen = "menu"
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Seleccionar sospechoso
                for suspect, rect in self.suspect_rects.items():
                    if rect.collidepoint(event.pos):
                        self.selected_suspect = suspect
                        
                if self.btn_graph.collidepoint(event.pos):
                    self.game.current_screen = "graph"
                elif self.btn_interview.collidepoint(event.pos):
                    if self.selected_suspect:
                        self.game.interview_screen.start_interview(self.selected_suspect)
                        self.game.current_screen = "interview"
                elif self.btn_accuse.collidepoint(event.pos):
                    if self.selected_suspect:
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
                        
                    self.game.current_screen = "results"

    def draw_panel(self, screen, rect, title):
        pygame.draw.rect(screen, COLORS["panel"], rect, border_radius=8)
        pygame.draw.rect(screen, COLORS["neon_blue"], rect, 1, border_radius=8)
        
        # Título del panel
        title_surf = self.font_title.render(title, True, COLORS["neon_blue"])
        screen.blit(title_surf, (rect.x + 15, rect.y + 15))
        
        # Línea separadora
        pygame.draw.line(screen, COLORS["neon_blue"], (rect.x, rect.y + 50), (rect.x + rect.width, rect.y + 50))

    def draw_button(self, screen, rect, text, mouse_pos, alert=False):
        is_hovered = rect.collidepoint(mouse_pos)
        base_color = COLORS["alert_red"] if alert else COLORS["neon_blue"]
        hover_color = (255, 100, 100) if alert else COLORS["neon_blue_hover"]
        
        border_color = hover_color if is_hovered else base_color
        bg_color = (80, 20, 20) if alert and is_hovered else (20, 60, 90) if is_hovered else COLORS["background"]
        
        pygame.draw.rect(screen, bg_color, rect, border_radius=5)
        pygame.draw.rect(screen, border_color, rect, 2, border_radius=5)

        text_color = COLORS["white"] if is_hovered else COLORS["gray_text"]
        label = self.font_title.render(text, True, text_color)
        screen.blit(label, label.get_rect(center=rect.center))

    def draw_wrapped_text(self, screen, text, font, color, x, y, max_width):
        words = text.split(' ')
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            width, _ = font.size(test_line)
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    current_line = []
        if current_line:
            lines.append(' '.join(current_line))
            
        y_pos = y
        for line in lines:
            surf = font.render(line, True, color)
            screen.blit(surf, (x, y_pos))
            y_pos += font.get_linesize()
            
        return y_pos - y


    def draw(self, screen):
        screen.fill(COLORS["background"])

        self.draw_panel(screen, self.panel_suspects, "PERFILES & SOSPECHOSOS")
        self.draw_panel(screen, self.panel_chat, "MENSAJES INTERCEPTADOS")
        self.draw_panel(screen, self.panel_clues, "PISTAS RECOLECTADAS")
        
        # Panel de acciones sin título estándar
        pygame.draw.rect(screen, COLORS["panel"], self.panel_actions, border_radius=8)
        pygame.draw.rect(screen, COLORS["neon_blue"], self.panel_actions, 1, border_radius=8)

        mouse_pos = pygame.mouse.get_pos()
        self.draw_button(screen, self.btn_graph, "ANALIZAR RED", mouse_pos)
        self.draw_button(screen, self.btn_interview, "ENTREVISTAR", mouse_pos)
        self.draw_button(screen, self.btn_accuse, "ACUSAR SOSPECHOSO", mouse_pos, alert=True)

        # Dibujar Timer
        rem_ms = self.game.case_manager.get_remaining_time()
        mins = int(rem_ms // 60000)
        secs = int((rem_ms % 60000) // 1000)
        time_str = f"TIEMPO: {mins:02d}:{secs:02d}"
        t_color = COLORS["alert_red"] if mins < 2 else COLORS["neon_blue"]
        t_surf = self.font_title.render(time_str, True, t_color)
        screen.blit(t_surf, (860, 510))

        # Dibujar Datos del Caso Activo
        y_offset = 70
        self.suspect_rects.clear()
        for suspect in self.game.case_manager.get_suspects():
            color = COLORS["neon_blue"] if self.selected_suspect == suspect else COLORS["white"]
            prefix = "[x]" if self.selected_suspect == suspect else ">"
            
            surf = self.font_text.render(f"{prefix} {suspect}", True, color)
            rect = surf.get_rect(topleft=(self.panel_suspects.x + 15, self.panel_suspects.y + y_offset))
            
            # Hacer el area clickeable un poco mas grande
            click_rect = pygame.Rect(rect.x, rect.y - 5, self.panel_suspects.width - 30, rect.height + 10)
            self.suspect_rects[suspect] = click_rect
            
            if self.selected_suspect == suspect:
                pygame.draw.rect(screen, (20, 60, 90), click_rect, border_radius=4)
                
            screen.blit(surf, rect.topleft)
            y_offset += 40

        y_offset = 70
        max_chat_width = self.panel_chat.width - 30
        for msg in self.game.case_manager.get_messages():
            # Clasificar mensaje
            clase_msg = self.game.decision_tree.classify_message_automatic(msg)
            color_msg = COLORS["alert_red"] if clase_msg in ["Mensaje ofensivo", "Mensaje grave", "Cyberbullying"] else COLORS["white"]
            
            text_to_draw = f"[*] {msg}"
            used_height = self.draw_wrapped_text(screen, text_to_draw, self.font_text, COLORS["white"], self.panel_chat.x + 15, self.panel_chat.y + y_offset, max_chat_width)
            
            surf_class = self.font_text.render(f"-> [{clase_msg}]", True, color_msg)
            screen.blit(surf_class, (self.panel_chat.x + 15, self.panel_chat.y + y_offset + used_height + 5))
            
            y_offset += used_height + 35

        y_offset = 70
        max_clue_width = self.panel_clues.width - 30
        for clue in self.game.case_manager.get_clues():
            text_to_draw = f"- {clue}"
            used_height = self.draw_wrapped_text(screen, text_to_draw, self.font_text, COLORS["neon_blue"], self.panel_clues.x + 15, self.panel_clues.y + y_offset, max_clue_width)
            y_offset += used_height + 15
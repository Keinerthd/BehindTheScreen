import pygame
from src.settings import COLORS
from src.network import NetworkManager
import random

class BullyScreen:
    def __init__(self, game):
        self.game = game
        self.font_title = pygame.font.SysFont("courier new", 24, bold=True)
        self.font_text = pygame.font.SysFont("courier new", 18)
        
        # Paneles
        self.panel_chat = pygame.Rect(20, 20, 600, 680)
        self.panel_clues = pygame.Rect(640, 20, 620, 500)
        self.panel_status = pygame.Rect(640, 520, 620, 220)

        # Botones de sabotaje
        self.btn_sabotage_clue = pygame.Rect(660, 540, 280, 50)
        self.btn_sabotage_msg = pygame.Rect(960, 540, 280, 50)
        self.btn_fake_clue = pygame.Rect(660, 605, 620, 50)
        
        self.sabotage_cooldown_clue = 0
        self.sabotage_cooldown_msg = 0
        self.sabotage_cooldown_fake = 0
        self.clues_removed = 0
        self.msgs_removed = 0
        self.max_clues_removed = 2
        self.max_msgs_removed = 2
        self.suspicion = 0
        self.detected_reported = False
        self.fake_clues = [
            "Paco estuvo conectado durante el incidente.",
            "Hugo compartió el meme primero.",
            "Luis usó una IP sospechosa.",
            "Daniela envió un mensaje desde una cuenta falsa.",
            "Noah obtuvo privilegios especiales en el grupo."
        ]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.current_screen = "menu"
                self.game.network.stop()
                self.game.network = NetworkManager()
                self.game.role = "detective"
                self.game.host_ip = ""
                self.game.connection_error = ""
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.btn_sabotage_clue.collidepoint(event.pos) and self.clues_removed < self.max_clues_removed and self.sabotage_cooldown_clue <= 0:
                    if hasattr(self.game, 'sound_manager'):
                        self.game.sound_manager.play("button_click")
                    clues = self.game.case_manager.get_clues()
                    if clues:
                        clue_to_remove = random.choice(clues)
                        self.game.network.send_message({
                            "type": "sabotage_clue",
                            "clue": clue_to_remove
                        })
                        self.clues_removed += 1
                        self.suspicion += 12
                        self.sabotage_cooldown_clue = 720  # 12 segundos a 60 FPS
                elif self.btn_sabotage_msg.collidepoint(event.pos) and self.msgs_removed < self.max_msgs_removed and self.sabotage_cooldown_msg <= 0:
                    if hasattr(self.game, 'sound_manager'):
                        self.game.sound_manager.play("button_click")
                    msgs = self.game.case_manager.get_messages()
                    if msgs:
                        msg_to_remove = random.choice(msgs)
                        self.game.network.send_message({
                            "type": "sabotage_message",
                            "message": msg_to_remove
                        })
                        self.msgs_removed += 1
                        self.suspicion += 8
                        self.sabotage_cooldown_msg = 600  # 10 segundos a 60 FPS
                elif self.btn_fake_clue.collidepoint(event.pos) and self.sabotage_cooldown_fake <= 0:
                    if hasattr(self.game, 'sound_manager'):
                        self.game.sound_manager.play("button_click")
                    available_fakes = [f for f in self.fake_clues if f not in self.game.case_manager.get_clues()]
                    if available_fakes:
                        fake_clue = random.choice(available_fakes)
                        self.game.network.send_message({
                            "type": "create_fake_clue",
                            "clue": fake_clue
                        })
                        self.suspicion += 15
                        self.sabotage_cooldown_fake = 900  # 15 segundos a 60 FPS
                self._check_detection()

    def draw_panel(self, screen, rect, title, alert=False):
        pygame.draw.rect(screen, COLORS["panel"], rect, border_radius=8)
        border = COLORS["alert_red"] if alert else COLORS["neon_blue"]
        pygame.draw.rect(screen, border, rect, 1, border_radius=8)
        
        title_surf = self.font_title.render(title, True, border)
        screen.blit(title_surf, (rect.x + 15, rect.y + 15))
        pygame.draw.line(screen, border, (rect.x, rect.y + 50), (rect.x + rect.width, rect.y + 50))

    def draw_button(self, screen, rect, text, mouse_pos, disabled=False):
        is_hovered = rect.collidepoint(mouse_pos) and not disabled
        base_color = (100, 100, 100) if disabled else COLORS["alert_red"]
        hover_color = (255, 100, 100)
        
        border_color = hover_color if is_hovered else base_color
        bg_color = (80, 20, 20) if is_hovered else COLORS["background"]
        
        pygame.draw.rect(screen, bg_color, rect, border_radius=5)
        pygame.draw.rect(screen, border_color, rect, 2, border_radius=5)

        text_color = COLORS["gray_text"] if disabled else (COLORS["white"] if is_hovered else COLORS["alert_red"])
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

    def update(self):
        if self.sabotage_cooldown_clue > 0:
            self.sabotage_cooldown_clue -= 1
        if self.sabotage_cooldown_msg > 0:
            self.sabotage_cooldown_msg -= 1
        if self.sabotage_cooldown_fake > 0:
            self.sabotage_cooldown_fake -= 1

    def draw(self, screen):
        self.update() # Update cooldowns
        screen.fill(COLORS["background"])

        self.draw_panel(screen, self.panel_chat, "MENSAJES EN LA RED", alert=True)
        self.draw_panel(screen, self.panel_clues, "PISTAS DEL DETECTIVE", alert=True)
        
        # Panel de acciones
        pygame.draw.rect(screen, COLORS["panel"], self.panel_status, border_radius=8)
        pygame.draw.rect(screen, COLORS["alert_red"], self.panel_status, 1, border_radius=8)

        mouse_pos = pygame.mouse.get_pos()
        
        disabled_clue = self.sabotage_cooldown_clue > 0 or self.clues_removed >= self.max_clues_removed
        disabled_msg = self.sabotage_cooldown_msg > 0 or self.msgs_removed >= self.max_msgs_removed
        disabled_fake = self.sabotage_cooldown_fake > 0

        self.draw_button(screen, self.btn_sabotage_clue, f"BORRAR PISTA ({self.clues_removed}/{self.max_clues_removed})", mouse_pos, disabled_clue)
        self.draw_button(screen, self.btn_sabotage_msg, f"BORRAR MENSAJE ({self.msgs_removed}/{self.max_msgs_removed})", mouse_pos, disabled_msg)
        self.draw_button(screen, self.btn_fake_clue, "CREAR PISTA FALSA", mouse_pos, disabled_fake)
        
        y_info = self.btn_fake_clue.bottom + 10
        if disabled_clue:
            cd_text = self.font_text.render(f"Cooldown Pista: {self.sabotage_cooldown_clue // 60}s", True, COLORS["alert_red"])
            screen.blit(cd_text, (self.panel_status.x + 15, y_info))
            y_info += 30
        if disabled_msg:
            cd_text = self.font_text.render(f"Cooldown Mensaje: {self.sabotage_cooldown_msg // 60}s", True, COLORS["alert_red"])
            screen.blit(cd_text, (self.panel_status.x + 15, y_info))
            y_info += 30
        if disabled_fake:
            cd_text = self.font_text.render(f"Cooldown Falso: {self.sabotage_cooldown_fake // 60}s", True, COLORS["alert_red"])
            screen.blit(cd_text, (self.panel_status.x + 15, y_info))
            y_info += 30

        # Mostrar el riesgo de detección siempre debajo de los cooldown
        risk_y = max(self.panel_status.y + self.panel_status.height - 80, y_info + 10)
        suspicion_text = self.font_text.render(f"RIESGO DE DETECCIÓN: {min(self.suspicion, 100)}%", True, COLORS["alert_red"])
        screen.blit(suspicion_text, (self.panel_status.x + 15, risk_y))

        bar_width = 520
        bar_x = self.panel_status.centerx - bar_width // 2
        bar_y = risk_y + 25
        if bar_y + 20 > self.panel_status.bottom - 15:
            bar_y = self.panel_status.bottom - 35
        pygame.draw.rect(screen, COLORS["gray_text"], (bar_x, bar_y, bar_width, 20), border_radius=5)
        pygame.draw.rect(screen, COLORS["alert_red"], (bar_x, bar_y, int((bar_width / 100) * min(self.suspicion, 100)), 20), border_radius=5)
        
        if not (disabled_clue or disabled_msg or disabled_fake):
            status_text = self.font_text.render("SABOTAJE LISTO", True, COLORS["success_green"])
            screen.blit(status_text, status_text.get_rect(center=(self.panel_status.centerx, self.panel_status.bottom - 15)))

        # Dibujar mensajes
        y_offset = 70
        max_chat_width = self.panel_chat.width - 30
        for msg in self.game.case_manager.get_messages():
            text_to_draw = f"[*] {msg}"
            used_height = self.draw_wrapped_text(screen, text_to_draw, self.font_text, COLORS["white"], self.panel_chat.x + 15, self.panel_chat.y + y_offset, max_chat_width)
            y_offset += used_height + 15

        # Dibujar pistas
        y_offset = 70
        max_clue_width = self.panel_clues.width - 30
        for clue in self.game.case_manager.get_clues():
            text_to_draw = f"- {clue}"
            used_height = self.draw_wrapped_text(screen, text_to_draw, self.font_text, COLORS["neon_blue"], self.panel_clues.x + 15, self.panel_clues.y + y_offset, max_clue_width)
            y_offset += used_height + 15

    def _check_detection(self):
        if self.suspicion >= 100 and not self.detected_reported and self.game.network.connected and not self.game.network.is_server:
            self.game.network.send_message({
                "type": "hacker_detected"
            })
            self.detected_reported = True

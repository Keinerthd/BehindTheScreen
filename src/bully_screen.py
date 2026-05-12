import pygame
from src.settings import COLORS
import random

class BullyScreen:
    def __init__(self, game):
        self.game = game
        self.font_title = pygame.font.SysFont("courier new", 24, bold=True)
        self.font_text = pygame.font.SysFont("courier new", 18)
        
        # Paneles
        self.panel_chat = pygame.Rect(20, 20, 600, 680)
        self.panel_clues = pygame.Rect(640, 20, 620, 500)
        self.panel_status = pygame.Rect(640, 540, 620, 160)

        # Botones de sabotaje
        self.btn_sabotage_clue = pygame.Rect(660, 560, 280, 50)
        self.btn_sabotage_msg = pygame.Rect(960, 560, 280, 50)
        
        self.sabotage_cooldown = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.current_screen = "menu"
                self.game.network.stop()
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.sabotage_cooldown <= 0:
                    if self.btn_sabotage_clue.collidepoint(event.pos):
                        if hasattr(self.game, 'sound_manager'):
                            self.game.sound_manager.play("button_click")
                        clues = self.game.case_manager.get_clues()
                        if clues:
                            clue_to_remove = random.choice(clues)
                            self.game.network.send_message({
                                "type": "sabotage_clue",
                                "clue": clue_to_remove
                            })
                            self.sabotage_cooldown = 180 # 3 segundos a 60 FPS
                    elif self.btn_sabotage_msg.collidepoint(event.pos):
                        if hasattr(self.game, 'sound_manager'):
                            self.game.sound_manager.play("button_click")
                        msgs = self.game.case_manager.get_messages()
                        if msgs:
                            msg_to_remove = random.choice(msgs)
                            self.game.network.send_message({
                                "type": "sabotage_message",
                                "message": msg_to_remove
                            })
                            self.sabotage_cooldown = 180

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
        if self.sabotage_cooldown > 0:
            self.sabotage_cooldown -= 1

    def draw(self, screen):
        self.update() # Update cooldowns
        screen.fill(COLORS["background"])

        self.draw_panel(screen, self.panel_chat, "MENSAJES EN LA RED", alert=True)
        self.draw_panel(screen, self.panel_clues, "PISTAS DEL DETECTIVE", alert=True)
        
        # Panel de acciones
        pygame.draw.rect(screen, COLORS["panel"], self.panel_status, border_radius=8)
        pygame.draw.rect(screen, COLORS["alert_red"], self.panel_status, 1, border_radius=8)

        mouse_pos = pygame.mouse.get_pos()
        
        disabled = self.sabotage_cooldown > 0
        self.draw_button(screen, self.btn_sabotage_clue, "BORRAR PISTA", mouse_pos, disabled)
        self.draw_button(screen, self.btn_sabotage_msg, "BORRAR MENSAJE", mouse_pos, disabled)
        
        if disabled:
            cd_text = self.font_text.render(f"Cooldown: {self.sabotage_cooldown // 60}s", True, COLORS["alert_red"])
            screen.blit(cd_text, cd_text.get_rect(center=(self.panel_status.centerx, 650)))
        else:
            status_text = self.font_text.render("SABOTAJE LISTO", True, COLORS["success_green"])
            screen.blit(status_text, status_text.get_rect(center=(self.panel_status.centerx, 650)))

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

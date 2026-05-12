import pygame
from src.settings import COLORS

class ResultsScreen:
    def __init__(self, game):
        self.game = game
        self.font_title = pygame.font.SysFont("courier new", 48, bold=True)
        self.font_text = pygame.font.SysFont("courier new", 24)
        
        self.btn_menu = pygame.Rect(490, 500, 300, 60)
        self.result_type = "neutral" # Puede ser "good", "bad", "neutral"

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.btn_menu.collidepoint(event.pos):
                    if hasattr(self.game, 'sound_manager'):
                        self.game.sound_manager.play("button_click")
                    self.game.current_screen = "menu"

    def draw_button(self, screen, rect, text, mouse_pos):
        is_hovered = rect.collidepoint(mouse_pos)
        border_color = COLORS["neon_blue_hover"] if is_hovered else COLORS["neon_blue"]
        bg_color = (20, 60, 90) if is_hovered else COLORS["panel"]
        
        pygame.draw.rect(screen, bg_color, rect, border_radius=5)
        pygame.draw.rect(screen, border_color, rect, 2, border_radius=5)

        text_color = COLORS["white"] if is_hovered else COLORS["gray_text"]
        label = self.font_text.render(text, True, text_color)
        screen.blit(label, label.get_rect(center=rect.center))

    def draw(self, screen):
        screen.fill(COLORS["background"])
        
        title_text = "CASO CERRADO"
        color = COLORS["white"]
        
        if self.result_type == "good":
            color = COLORS["success_green"]
            msg = "Has identificado correctamente al acosador."
        elif self.result_type == "bad":
            color = COLORS["alert_red"]
            msg = "Has acusado a la persona equivocada."
        elif self.result_type == "timeout":
            color = COLORS["alert_red"]
            msg = "El tiempo se agotó. La víctima abandonó la escuela."
        else:
            color = COLORS["gray_text"]
            msg = "Investigación inconclusa."

        title = self.font_title.render(title_text, True, color)
        screen.blit(title, title.get_rect(center=(640, 200)))
        
        desc = self.font_text.render(msg, True, COLORS["white"])
        screen.blit(desc, desc.get_rect(center=(640, 300)))

        mouse_pos = pygame.mouse.get_pos()
        self.draw_button(screen, self.btn_menu, "VOLVER AL MENÚ", mouse_pos)

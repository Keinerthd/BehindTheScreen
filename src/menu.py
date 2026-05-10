import pygame
from src.settings import COLORS

class Menu:
    def __init__(self, game):
        self.game = game
        self.font_title = pygame.font.SysFont("courier new", 72, bold=True)
        self.font_subtitle = pygame.font.SysFont("courier new", 28)
        self.font_button = pygame.font.SysFont("courier new", 32, bold=True)

        self.start_button = pygame.Rect(490, 300, 300, 60)
        self.help_button = pygame.Rect(490, 380, 300, 60)
        self.exit_button = pygame.Rect(490, 460, 300, 60)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left click
                if self.start_button.collidepoint(event.pos):
                    self.game.current_screen = "investigation"
                elif self.help_button.collidepoint(event.pos):
                    print("Mostrar Ayuda")
                elif self.exit_button.collidepoint(event.pos):
                    self.game.running = False

    def draw_button(self, screen, rect, text, mouse_pos):
        is_hovered = rect.collidepoint(mouse_pos)
        
        # Color del borde
        border_color = COLORS["neon_blue_hover"] if is_hovered else COLORS["neon_blue"]
        # Color del fondo del botón
        bg_color = (20, 60, 90) if is_hovered else COLORS["panel"]
        
        pygame.draw.rect(screen, bg_color, rect, border_radius=5)
        pygame.draw.rect(screen, border_color, rect, 2, border_radius=5)

        text_color = COLORS["white"] if is_hovered else COLORS["gray_text"]
        label = self.font_button.render(text, True, text_color)
        label_rect = label.get_rect(center=rect.center)
        screen.blit(label, label_rect)

    def draw(self, screen):
        screen.fill(COLORS["background"])
        
        # Grid lineas de fondo para dar estilo hacker/cyberpunk (opcional, simple)
        for i in range(0, 1280, 40):
            pygame.draw.line(screen, (15, 25, 40), (i, 0), (i, 720))
        for i in range(0, 720, 40):
            pygame.draw.line(screen, (15, 25, 40), (0, i), (1280, i))

        title = self.font_title.render("BEHIND THE SCREEN", True, COLORS["neon_blue"])
        subtitle = self.font_subtitle.render("> SYSTEM.LOGIN() :: CYBER DETECTIVE_", True, COLORS["white"])

        screen.blit(title, title.get_rect(center=(640, 150)))
        screen.blit(subtitle, subtitle.get_rect(center=(640, 220)))

        mouse_pos = pygame.mouse.get_pos()

        self.draw_button(screen, self.start_button, "INICIAR", mouse_pos)
        self.draw_button(screen, self.help_button, "AYUDA", mouse_pos)
        self.draw_button(screen, self.exit_button, "SALIR", mouse_pos)
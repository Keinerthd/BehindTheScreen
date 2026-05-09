import pygame

class Menu:
    def __init__(self, game):
        self.game = game
        self.font_title = pygame.font.SysFont("arial", 64, bold=True)
        self.font_button = pygame.font.SysFont("arial", 32)

        self.start_button = pygame.Rect(490, 300, 300, 60)
        self.help_button = pygame.Rect(490, 380, 300, 60)
        self.exit_button = pygame.Rect(490, 460, 300, 60)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.start_button.collidepoint(event.pos):
                self.game.current_screen = "investigation"

            elif self.help_button.collidepoint(event.pos):
                print("Ayuda")

            elif self.exit_button.collidepoint(event.pos):
                self.game.running = False

    def draw_button(self, screen, rect, text):
        pygame.draw.rect(screen, (40, 80, 140), rect, border_radius=12)
        pygame.draw.rect(screen, (120, 180, 255), rect, 2, border_radius=12)

        label = self.font_button.render(text, True, (255, 255, 255))
        label_rect = label.get_rect(center=rect.center)
        screen.blit(label, label_rect)

    def draw(self, screen):
        title = self.font_title.render("BEHIND THE SCREEN", True, (255, 255, 255))
        subtitle = self.font_button.render("Cyber Detective", True, (150, 200, 255))

        screen.blit(title, title.get_rect(center=(640, 150)))
        screen.blit(subtitle, subtitle.get_rect(center=(640, 220)))

        self.draw_button(screen, self.start_button, "Iniciar")
        self.draw_button(screen, self.help_button, "Ayuda")
        self.draw_button(screen, self.exit_button, "Salir")
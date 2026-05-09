import pygame

class InvestigationScreen:

    def __init__(self, game):

        self.game = game

        self.font = pygame.font.SysFont("arial", 40)

    def handle_event(self, event):

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                self.game.current_screen = "menu"

    def draw(self, screen):

        screen.fill((20, 20, 30))

        title = self.font.render("Pantalla de Investigación", True, (255,255,255))

        screen.blit(title, (350, 100))
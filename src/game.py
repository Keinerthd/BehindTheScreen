import pygame
from config import WIDTH, HEIGHT, FPS
from src.menu import Menu
from src.investigation_screen import InvestigationScreen

class Game:

    def __init__(self):

        self.investigation_screen = InvestigationScreen(self)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Behind The Screen")

        self.clock = pygame.time.Clock()

        self.running = True

        self.current_screen = "menu"

        self.menu = Menu(self)

    def run(self):

        while self.running:

            self.clock.tick(FPS)

            self.handle_events()
            self.update()
            self.draw()

    def handle_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.running = False

            if self.current_screen == "menu":
                self.menu.handle_event(event)
            if self.current_screen == "investigation":
                self.investigation_screen.handle_event(event)

    def update(self):
        pass

    def draw(self):

        self.screen.fill((15, 18, 30))

        if self.current_screen == "menu":
            self.menu.draw(self.screen)
        if self.current_screen == "investigation":
            self.investigation_screen.draw(self.screen)

        pygame.display.flip()
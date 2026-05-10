import pygame
from config import WIDTH, HEIGHT, FPS
from src.menu import Menu
from src.investigation_screen import InvestigationScreen
from src.graph_screen import GraphScreen
from src.results_screen import ResultsScreen
from src.case_manager import CaseManager
from src.decision_tree import DecisionTree
from src.graph_manager import GraphManager

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Behind The Screen - Cyber Detective")

        self.clock = pygame.time.Clock()
        self.running = True
        self.current_screen = "menu"

        # Inicializar y cargar el caso 1
        self.case_manager = CaseManager()
        self.case_manager.select_case(1)
        
        # Inicializar árbol de decisiones
        self.decision_tree = DecisionTree()

        # Inicializar y construir el grafo
        self.graph_manager = GraphManager()
        self.graph_manager.build_case_graph(
            self.case_manager.get_suspects(), 
            self.case_manager.active_case.get("bully", "ShadowUser")
        )

        self.menu = Menu(self)
        self.investigation_screen = InvestigationScreen(self)
        self.graph_screen = GraphScreen(self)
        self.results_screen = ResultsScreen(self)


    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

    def handle_events(self):
        from src.settings import toggle_high_contrast
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    toggle_high_contrast()
                elif event.key == pygame.K_h:
                    self.show_help = not getattr(self, 'show_help', False)

            if getattr(self, 'show_help', False):
                # Si la ayuda está abierta, no pasamos eventos a las pantallas
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.show_help = False
                continue

            if self.current_screen == "menu":
                self.menu.handle_event(event)
            elif self.current_screen == "investigation":
                self.investigation_screen.handle_event(event)
            elif self.current_screen == "graph":
                self.graph_screen.handle_event(event)
            elif self.current_screen == "results":
                self.results_screen.handle_event(event)

    def update(self):
        pass

    def draw(self):
        from src.settings import COLORS
        # El fill ya lo hace cada pantalla en su propio draw, pero por seguridad:
        self.screen.fill(COLORS["background"])

        if self.current_screen == "menu":
            self.menu.draw(self.screen)
        elif self.current_screen == "investigation":
            self.investigation_screen.draw(self.screen)
        elif self.current_screen == "graph":
            self.graph_screen.draw(self.screen)
        elif self.current_screen == "results":
            self.results_screen.draw(self.screen)

        # Dibujar overlay de ayuda si está activo
        if getattr(self, 'show_help', False):
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            font = pygame.font.SysFont("courier new", 24, bold=True)
            help_text = [
                "--- CONTROLES DE AYUDA ---",
                "",
                "[C] - Alternar Modo Alto Contraste",
                "[H] - Mostrar/Ocultar esta ventana de ayuda",
                "[ESC] - Volver atrás / Cerrar ventanas",
                "",
                "Objetivo: Lee los mensajes, revisa las pistas,",
                "y usa el analizador de red para identificar",
                "al verdadero acosador (ShadowUser).",
                "",
                "Selecciona un nombre en la lista de sospechosos",
                "y presiona ACUSAR SOSPECHOSO para decidir."
            ]
            
            y = 150
            for line in help_text:
                surf = font.render(line, True, COLORS["white"])
                self.screen.blit(surf, surf.get_rect(center=(WIDTH // 2, y)))
                y += 35

        pygame.display.flip()
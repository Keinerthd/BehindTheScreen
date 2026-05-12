import pygame
from config import WIDTH, HEIGHT, FPS
from src.menu import Menu
from src.investigation_screen import InvestigationScreen
from src.graph_screen import GraphScreen
from src.results_screen import ResultsScreen
from src.case_manager import CaseManager
from src.decision_tree import DecisionTree
from src.graph_manager import GraphManager
from src.network import NetworkManager
from src.bully_screen import BullyScreen
from src.interview_screen import InterviewScreen
from src.sound_manager import SoundManager
from src.sound_manager import SoundManager

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Behind The Screen - Cyber Detective")

        self.clock = pygame.time.Clock()
        self.running = True
        self.current_screen = "menu"

        # Inicializar y cargar un caso aleatorio
        self.case_manager = CaseManager()
        self.case_manager.select_random_case()
        
        # Inicializar árbol de decisiones
        self.decision_tree = DecisionTree()

        # Inicializar y construir el grafo
        self.graph_manager = GraphManager()
        self.graph_manager.build_case_graph(
            self.case_manager.active_case.get("victim", "Emma"),
            self.case_manager.get_suspects(), 
            self.case_manager.active_case.get("bully", "ShadowUser")
        )

        self.menu = Menu(self)
        self.investigation_screen = InvestigationScreen(self)
        self.graph_screen = GraphScreen(self)
        self.results_screen = ResultsScreen(self)
        self.bully_screen = BullyScreen(self)
        self.interview_screen = InterviewScreen(self)
        
        self.network = NetworkManager()
        self.host_ip = ""
        self.connection_error = ""
        self.role = "detective"
        
        self.sound_manager = SoundManager()


    def host_game(self):
        success, msg = self.network.host_game()
        if success:
            self.host_ip = msg
            self.role = "detective"
            self.connection_error = ""
        else:
            self.connection_error = f"Error: {msg}"

    def join_game(self, ip):
        success, msg = self.network.join_game(ip)
        if success:
            self.role = "bully"
            self.connection_error = ""
        else:
            self.connection_error = f"Error: {msg}"

    def start_new_investigation(self):
        self.case_manager.select_random_case()
        self.graph_manager.build_case_graph(
            self.case_manager.active_case.get("victim", "Emma"),
            self.case_manager.get_suspects(), 
            self.case_manager.active_case.get("bully", "ShadowUser")
        )
        if hasattr(self, 'investigation_screen'):
            self.investigation_screen.selected_suspect = None
            
        # Enviar estado inicial si somos el servidor
        if self.network.is_server and self.network.connected:
            self.sync_state()

    def sync_state(self):
        state = {
            "type": "sync",
            "victim": self.case_manager.active_case.get("victim", "Emma"),
            "bully": self.case_manager.active_case.get("bully", "ShadowUser"),
            "suspects": self.case_manager.get_suspects(),
            "messages": self.case_manager.get_messages(),
            "clues": self.case_manager.get_clues()
        }
        self.network.send_message(state)


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
            elif self.current_screen == "interview":
                self.interview_screen.handle_event(event)
            elif self.current_screen == "bully":
                self.bully_screen.handle_event(event)
            elif self.current_screen == "graph":
                self.graph_screen.handle_event(event)
            elif self.current_screen == "results":
                self.results_screen.handle_event(event)

    def update(self):
        # Transición cuando el server conecta con el cliente
        if self.current_screen == "menu" and self.network.connected:
            if self.network.is_server:
                self.start_new_investigation()
                self.current_screen = "investigation"
            elif self.network.is_client:
                self.current_screen = "bully"

        # Check timer game over
        if self.current_screen in ["investigation", "interview", "graph"]:
            if self.case_manager.get_remaining_time() <= 0:
                self.results_screen.result_type = "timeout"
                self.current_screen = "results"

        # Procesar mensajes de red
        for msg in self.network.get_messages():
            msg_type = msg.get("type")
            if msg_type == "sync":
                # Sincronizar estado (Cliente recibe del Servidor)
                self.case_manager.active_case["victim"] = msg["victim"]
                self.case_manager.active_case["bully"] = msg["bully"]
                self.case_manager.active_case["suspects"] = msg["suspects"]
                self.case_manager.active_case["messages"] = msg["messages"]
                self.case_manager.unlocked_clues = msg["clues"]
                self.graph_manager.build_case_graph(msg["victim"], msg["suspects"], msg["bully"])
            elif msg_type == "sabotage_clue":
                clue = msg["clue"]
                if clue in self.case_manager.get_clues():
                    self.case_manager.get_clues().remove(clue)
                    self.sound_manager.play("sabotage")
                    self.graph_manager.sabotage_graph()
                    self.sync_state() # Resync
            elif msg_type == "sabotage_message":
                m = msg["message"]
                if m in self.case_manager.get_messages():
                    self.case_manager.get_messages().remove(m)
                    self.sound_manager.play("sabotage")
                    self.graph_manager.sabotage_graph()
                    self.sync_state() # Resync

    def draw(self):
        from src.settings import COLORS
        # El fill ya lo hace cada pantalla en su propio draw, pero por seguridad:
        self.screen.fill(COLORS["background"])

        if self.current_screen == "menu":
            self.menu.draw(self.screen)
        elif self.current_screen == "investigation":
            self.investigation_screen.draw(self.screen)
        elif self.current_screen == "interview":
            self.interview_screen.draw(self.screen)
        elif self.current_screen == "bully":
            self.bully_screen.draw(self.screen)
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
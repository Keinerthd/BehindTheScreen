import pygame
from src.settings import COLORS

class GraphScreen:
    def __init__(self, game):
        self.game = game
        self.font_title = pygame.font.SysFont("courier new", 28, bold=True)
        self.font_text = pygame.font.SysFont("courier new", 18)
        
        self.btn_back = pygame.Rect(20, 20, 150, 40)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.current_screen = "investigation"
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.btn_back.collidepoint(event.pos):
                    self.game.current_screen = "investigation"

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
        
        # Efecto de grid para la pantalla de red
        for i in range(0, 1280, 50):
            pygame.draw.line(screen, (20, 30, 45), (i, 0), (i, 720))
        for i in range(0, 720, 50):
            pygame.draw.line(screen, (20, 30, 45), (0, i), (1280, i))

        mouse_pos = pygame.mouse.get_pos()
        self.draw_button(screen, self.btn_back, "< VOLVER", mouse_pos)

        title = self.font_title.render("ANÁLISIS DE RED SOCIAL", True, COLORS["neon_blue"])
        screen.blit(title, (200, 25))
        
        graph_manager = self.game.graph_manager
        positions = graph_manager.get_nodes_positions()
        edges = graph_manager.get_edges()

        # Dibujar aristas
        for edge in edges:
            node_a, node_b = edge
            if node_a in positions and node_b in positions:
                pygame.draw.line(screen, COLORS["edge_color"], positions[node_a], positions[node_b], 2)

        victim_name = self.game.case_manager.active_case.get("victim", "Emma")
        # Dibujar nodos
        for node, pos in positions.items():
            # Destacar a la víctima y a la cuenta anónima
            if node == victim_name:
                color = COLORS["success_green"]
            elif node == "ShadowUser":
                color = COLORS["alert_red"]
            else:
                color = COLORS["node_color"]

            pygame.draw.circle(screen, color, pos, 30)
            
            # Texto del nodo
            text_surf = self.font_text.render(node, True, COLORS["white"])
            screen.blit(text_surf, text_surf.get_rect(center=pos))

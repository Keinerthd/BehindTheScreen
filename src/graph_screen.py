import pygame
from src.settings import COLORS

class GraphScreen:
    def __init__(self, game):
        self.game = game
        self.font_title = pygame.font.SysFont("courier new", 28, bold=True)
        self.font_text = pygame.font.SysFont("courier new", 18)
        
        self.btn_back = pygame.Rect(20, 20, 150, 40)
        self.btn_bfs = pygame.Rect(900, 100, 350, 40)
        self.btn_centrality = pygame.Rect(900, 160, 350, 40)
        self.btn_dijkstra = pygame.Rect(900, 220, 350, 40)
        
        self.algorithm_result = ""
        self.highlighted_nodes = []
        self.highlighted_edges = []

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.current_screen = "investigation"
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.btn_back.collidepoint(event.pos):
                    self.game.current_screen = "investigation"
                elif self.btn_bfs.collidepoint(event.pos):
                    self.game.case_manager.reduce_time(15000)
                    victim = self.game.case_manager.active_case.get("victim", "Emma")
                    nodes = self.game.graph_manager.bfs_traversal(victim)
                    self.highlighted_nodes = nodes
                    self.highlighted_edges = []
                    self.algorithm_result = f"BFS: Propagación desde {victim}"
                elif self.btn_centrality.collidepoint(event.pos):
                    self.game.case_manager.reduce_time(15000)
                    centrality = self.game.graph_manager.get_centrality()
                    if centrality:
                        max_node = max(centrality, key=centrality.get)
                        self.highlighted_nodes = [max_node]
                        self.algorithm_result = f"Más Influyente: {max_node} ({centrality[max_node]:.2f})"
                    self.highlighted_edges = []
                elif self.btn_dijkstra.collidepoint(event.pos):
                    self.game.case_manager.reduce_time(15000)
                    victim = self.game.case_manager.active_case.get("victim", "Emma")
                    try:
                        path = self.game.graph_manager.shortest_path_dijkstra("ShadowUser", victim)
                        self.highlighted_nodes = path
                        self.highlighted_edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
                        self.algorithm_result = f"Dijkstra Ruta: {' -> '.join(path)}"
                    except:
                        self.algorithm_result = "No hay ruta de ShadowUser a la víctima"


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
        self.draw_button(screen, self.btn_bfs, "BFS (-15s)", mouse_pos)
        self.draw_button(screen, self.btn_centrality, "Centralidad (-15s)", mouse_pos)
        self.draw_button(screen, self.btn_dijkstra, "Dijkstra (-15s)", mouse_pos)

        title = self.font_title.render("ANÁLISIS DE RED SOCIAL", True, COLORS["neon_blue"])
        screen.blit(title, (200, 25))
        
        if self.algorithm_result:
            words = self.algorithm_result.split(' ')
            lines = []
            if words:
                current_line = words[0]
                for word in words[1:]:
                    if self.font_text.size(current_line + " " + word)[0] < 360:
                        current_line += " " + word
                    else:
                        lines.append(current_line)
                        current_line = word
                lines.append(current_line)
                
                y_offset = 280
                for line in lines:
                    res_surf = self.font_text.render(line, True, COLORS["alert_red"])
                    screen.blit(res_surf, (900, y_offset))
                    y_offset += 25
        
        graph_manager = self.game.graph_manager
        positions = graph_manager.get_nodes_positions()
        edges = graph_manager.get_edges()

        # Dibujar aristas
        for edge in edges:
            node_a, node_b = edge
            if node_a in positions and node_b in positions:
                is_highlighted = (node_a, node_b) in self.highlighted_edges or (node_b, node_a) in self.highlighted_edges
                color = COLORS["alert_red"] if is_highlighted else COLORS["edge_color"]
                width = 4 if is_highlighted else 2
                pygame.draw.line(screen, color, positions[node_a], positions[node_b], width)

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
                
            radius = 30
            if node in self.highlighted_nodes:
                pygame.draw.circle(screen, COLORS["neon_blue_hover"], pos, radius + 5)
                color = (255, 200, 0) # Amarillo para destacados

            pygame.draw.circle(screen, color, pos, radius)
            
            # Texto del nodo
            text_surf = self.font_text.render(node, True, COLORS["white"])
            screen.blit(text_surf, text_surf.get_rect(center=pos))

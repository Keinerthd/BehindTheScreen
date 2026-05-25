import pygame
import math
import random
from src.settings import COLORS

# Velocidad de los "paquetes de datos" que viajan por el grafo
_PACKET_SPEED = 2.0

class DataPacket:
    """Pequeño punto de luz de neón que viaja por una arista del grafo."""
    def __init__(self, start_pos, end_pos, color):
        self.start = start_pos
        self.end   = end_pos
        self.color = color
        self.t     = 0.0       # 0.0 = inicio, 1.0 = fin
        self.alpha = 255
        self.radius = random.randint(3, 5)

    @property
    def pos(self):
        x = self.start[0] + (self.end[0] - self.start[0]) * self.t
        y = self.start[1] + (self.end[1] - self.start[1]) * self.t
        return (int(x), int(y))

    def update(self, edge_len):
        step = _PACKET_SPEED / max(edge_len, 1)
        self.t += step
        return self.t >= 1.0   # True = llegó al destino → borrar

class GraphScreen:
    def __init__(self, game):
        self.game = game
        self.font_title = pygame.font.SysFont("courier new", 28, bold=True)
        self.font_text  = pygame.font.SysFont("courier new", 18)

        self.btn_back       = pygame.Rect(20, 20, 150, 40)
        self.btn_bfs        = pygame.Rect(900, 100, 350, 40)
        self.btn_centrality = pygame.Rect(900, 160, 350, 40)
        self.btn_dijkstra   = pygame.Rect(900, 220, 350, 40)
        # Botón verificar pista (detective)
        self.btn_verify     = pygame.Rect(900, 290, 350, 40)
        self.verify_cooldown = 0   # frames de cooldown

        self.algorithm_result  = ""
        self.highlighted_nodes = []
        self.highlighted_edges = []

        # Sistema de paquetes de datos animados
        self._packets: list[DataPacket] = []
        self._spawn_timer = 0
        self._spawn_interval = 25   # frames entre spawns

    # ─── EVENTOS ─────────────────────────────────────────────────────────────

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.current_screen = "investigation"

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                pos = event.pos
                if self.btn_back.collidepoint(pos):
                    self._sfx()
                    self.game.current_screen = "investigation"

                elif self.btn_bfs.collidepoint(pos):
                    self._sfx()
                    self.game.case_manager.reduce_time(15000)
                    victim = self.game.case_manager.active_case.get("victim", "Emma")
                    nodes = self.game.graph_manager.bfs_traversal(victim)
                    self.highlighted_nodes = nodes
                    self.highlighted_edges = []
                    self.algorithm_result = f"BFS: Propagación desde {victim}"
                    self._burst_packets(highlighted=True)

                elif self.btn_centrality.collidepoint(pos):
                    self._sfx()
                    self.game.case_manager.reduce_time(15000)
                    centrality = self.game.graph_manager.get_centrality()
                    if centrality:
                        max_node = max(centrality, key=centrality.get)
                        self.highlighted_nodes = [max_node]
                        self.algorithm_result = f"Más Influyente: {max_node} ({centrality[max_node]:.2f})"
                    self.highlighted_edges = []
                    self._burst_packets()

                elif self.btn_dijkstra.collidepoint(pos):
                    self._sfx()
                    self.game.case_manager.reduce_time(15000)
                    victim = self.game.case_manager.active_case.get("victim", "Emma")
                    try:
                        path = self.game.graph_manager.shortest_path_dijkstra("ShadowUser", victim)
                        self.highlighted_nodes = path
                        self.highlighted_edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
                        self.algorithm_result = f"Dijkstra Ruta: {' -> '.join(path)}"
                    except Exception:
                        self.algorithm_result = "No hay ruta de ShadowUser a la víctima"
                    self._burst_packets(highlighted=True)

                elif self.btn_verify.collidepoint(pos) and self.verify_cooldown <= 0:
                    # Detective gasta 20 segundos para verificar la pista más reciente
                    self._sfx()
                    clues = self.game.case_manager.get_clues()
                    if clues:
                        suspect_clue = clues[-1]
                        self.game.case_manager.reduce_time(20000)
                        fake_texts = self.game._get_fake_clue_texts()
                        is_fake = suspect_clue in fake_texts
                        if is_fake:
                            self.game.case_manager.get_clues().remove(suspect_clue)
                            # Eliminar nodo falso asociado si existe
                            if self.game._fake_graph_nodes:
                                fn = self.game._fake_graph_nodes.pop()
                                if fn in self.game.graph_manager.graph:
                                    self.game.graph_manager.graph.remove_node(fn)
                                    self.game.graph_manager.positions.pop(fn, None)
                            self.game.add_notification("✓ PISTA FALSA ELIMINADA (-20s)", COLORS["success_green"])
                        else:
                            self.game.add_notification("✓ PISTA REAL (-20s)", COLORS["neon_blue"])
                        self.verify_cooldown = 180   # 3 segundos de cooldown

    def _sfx(self):
        if hasattr(self.game, 'sound_manager'):
            self.game.sound_manager.play("button_click")

    # ─── PAQUETES ANIMADOS ────────────────────────────────────────────────────

    def _edge_length(self, p1, p2):
        return math.hypot(p2[0]-p1[0], p2[1]-p1[1])

    def _spawn_packet(self, edge=None, highlighted=False):
        positions = self.game.graph_manager.get_nodes_positions()
        edges     = list(self.game.graph_manager.get_edges())
        if not edges or not positions:
            return
        if edge is None:
            edge = random.choice(edges)
        a, b = edge
        if a not in positions or b not in positions:
            return
        if random.random() < 0.5:
            a, b = b, a
        color = (0, 255, 180) if not highlighted else (255, 220, 0)
        # Variar ligeramente el color
        color = (
            max(0, min(255, color[0] + random.randint(-20, 20))),
            max(0, min(255, color[1] + random.randint(-20, 20))),
            max(0, min(255, color[2] + random.randint(-20, 20))),
        )
        self._packets.append(DataPacket(positions[a], positions[b], color))

    def _burst_packets(self, highlighted=False):
        """Genera un ráfaga de paquetes al ejecutar un algoritmo."""
        edges = list(self.game.graph_manager.get_edges())
        for edge in edges[:min(6, len(edges))]:
            self._spawn_packet(edge=edge, highlighted=highlighted)

    def _update_packets(self):
        positions = self.game.graph_manager.get_nodes_positions()
        edges     = list(self.game.graph_manager.get_edges())
        if not edges or not positions:
            return

        self._spawn_timer += 1
        if self._spawn_timer >= self._spawn_interval:
            self._spawn_timer = 0
            self._spawn_packet()

        alive = []
        for pkt in self._packets:
            # Calcular longitud real de la arista
            length = self._edge_length(pkt.start, pkt.end)
            if not pkt.update(length):
                alive.append(pkt)
        self._packets = alive

    # ─── DIBUJO ───────────────────────────────────────────────────────────────

    def draw_button(self, screen, rect, text, mouse_pos, disabled=False):
        is_hovered = rect.collidepoint(mouse_pos) and not disabled
        border_color = COLORS["neon_blue_hover"] if is_hovered else (80, 80, 80) if disabled else COLORS["neon_blue"]
        bg_color = (20, 60, 90) if is_hovered else COLORS["panel"]
        pygame.draw.rect(screen, bg_color, rect, border_radius=5)
        pygame.draw.rect(screen, border_color, rect, 2, border_radius=5)
        text_color = COLORS["white"] if is_hovered else (80, 80, 80) if disabled else COLORS["gray_text"]
        label = self.font_text.render(text, True, text_color)
        screen.blit(label, label.get_rect(center=rect.center))

    def _draw_packets(self, screen):
        for pkt in self._packets:
            surf = pygame.Surface((pkt.radius * 2 + 4, pkt.radius * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*pkt.color, pkt.alpha), (pkt.radius + 2, pkt.radius + 2), pkt.radius)
            screen.blit(surf, (pkt.pos[0] - pkt.radius - 2, pkt.pos[1] - pkt.radius - 2))

    def draw(self, screen):
        screen.fill(COLORS["background"])

        # Grid de fondo
        for i in range(0, 1280, 50):
            pygame.draw.line(screen, (20, 30, 45), (i, 0), (i, 720))
        for i in range(0, 720, 50):
            pygame.draw.line(screen, (20, 30, 45), (0, i), (1280, i))

        self._update_packets()

        mouse_pos = pygame.mouse.get_pos()
        self.draw_button(screen, self.btn_back, "< VOLVER", mouse_pos)
        self.draw_button(screen, self.btn_bfs,        "BFS (-15s)",         mouse_pos)
        self.draw_button(screen, self.btn_centrality, "Centralidad (-15s)", mouse_pos)
        self.draw_button(screen, self.btn_dijkstra,   "Dijkstra (-15s)",    mouse_pos)
        verify_label = f"VERIFICAR PISTA (-20s)" if self.verify_cooldown <= 0 else f"VERIFICAR... {self.verify_cooldown//60}s"
        self.draw_button(screen, self.btn_verify, verify_label, mouse_pos,
                         disabled=self.verify_cooldown > 0)
        if self.verify_cooldown > 0:
            self.verify_cooldown -= 1

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
                y_offset = 360
                for line in lines:
                    res_surf = self.font_text.render(line, True, COLORS["alert_red"])
                    screen.blit(res_surf, (900, y_offset))
                    y_offset += 25

        graph_manager = self.game.graph_manager
        positions     = graph_manager.get_nodes_positions()
        edges         = graph_manager.get_edges()

        # Aristas
        for edge in edges:
            node_a, node_b = edge
            if node_a in positions and node_b in positions:
                is_highlighted = ((node_a, node_b) in self.highlighted_edges or
                                  (node_b, node_a) in self.highlighted_edges)
                color = COLORS["alert_red"] if is_highlighted else COLORS["edge_color"]
                width = 4 if is_highlighted else 2
                pygame.draw.line(screen, color, positions[node_a], positions[node_b], width)

        # Paquetes de datos animados (encima de aristas, debajo de nodos)
        self._draw_packets(screen)

        victim_name  = self.game.case_manager.active_case.get("victim", "Emma")
        fake_nodes   = self.game._fake_graph_nodes
        now_ms       = pygame.time.get_ticks()

        # Nodos
        for node, pos in positions.items():
            is_fake = node in fake_nodes
            if node == victim_name:
                color = COLORS["success_green"]
            elif node == "ShadowUser":
                color = COLORS["alert_red"]
            elif is_fake:
                color = (180, 50, 200)
            else:
                color = COLORS["node_color"]

            radius = 30

            # Pulso suave constante en todos los nodos (distinto phase por nodo)
            phase  = hash(node) % 628 / 100.0      # fase única por nombre
            pulse  = 0.5 + 0.5 * math.sin(now_ms / 600.0 + phase)
            glow_r = radius + 4 + int(4 * pulse)
            glow_a = int(40 + 40 * pulse)
            glow_surf = pygame.Surface((glow_r * 2 + 4, glow_r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*color, glow_a),
                               (glow_r + 2, glow_r + 2), glow_r)
            screen.blit(glow_surf, (pos[0] - glow_r - 2, pos[1] - glow_r - 2))

            if node in self.highlighted_nodes:
                pygame.draw.circle(screen, COLORS["neon_blue_hover"], pos, radius + 5)
                color = (255, 200, 0)

            # Pulso extra en nodo falso
            if is_fake:
                pulse_r = radius + 8 + int(4 * math.sin(now_ms / 200))
                pygame.draw.circle(screen, (220, 0, 255), pos, pulse_r, 2)

            pygame.draw.circle(screen, color, pos, radius)
            text_surf = self.font_text.render(node, True, COLORS["white"])
            screen.blit(text_surf, text_surf.get_rect(center=pos))

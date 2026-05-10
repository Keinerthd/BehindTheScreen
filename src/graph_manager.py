import networkx as nx
import math

class GraphManager:
    def __init__(self):
        self.graph = nx.Graph()
        self.positions = {}
        
    def build_case_graph(self, suspects, bully):
        # Limpiar grafo previo
        self.graph.clear()
        
        # Añadir nodos principales
        self.graph.add_node("Emma")
        self.graph.add_node("ShadowUser")
        
        for suspect in suspects:
            self.graph.add_node(suspect)
            
        # Añadir conexiones (aristas) - Simulación de relaciones
        self.graph.add_edge("Emma", "Mia", weight=1)
        self.graph.add_edge("Mia", "Lucas", weight=3)
        self.graph.add_edge("Lucas", "Noah", weight=2)
        self.graph.add_edge("Noah", "ShadowUser", weight=1) # Pista fuerte
        
        # Generar posiciones visuales (Spring layout) 
        # para que Pygame sepa dónde dibujarlos
        self.positions = nx.spring_layout(self.graph, center=(640, 360), scale=200)
        
        # Networkx spring layout devuelve floats entre -1 y 1 (o basados en el center y scale)
        # Aseguramos que sean ints para pygame
        for node, pos in self.positions.items():
            self.positions[node] = (int(pos[0]), int(pos[1]))

    def get_nodes_positions(self):
        return self.positions
        
    def get_edges(self):
        return self.graph.edges()

    # --- ALGORITMOS SOLICITADOS ---

    def bfs_traversal(self, start_node):
        if start_node not in self.graph:
            return []
        return list(nx.bfs_tree(self.graph, start_node).nodes())

    def dfs_traversal(self, start_node):
        if start_node not in self.graph:
            return []
        return list(nx.dfs_tree(self.graph, start_node).nodes())

    def shortest_path_dijkstra(self, source, target):
        try:
            return nx.dijkstra_path(self.graph, source, target)
        except nx.NetworkXNoPath:
            return []

    def get_centrality(self):
        # Grado de centralidad para detectar nodos influyentes
        return nx.degree_centrality(self.graph)

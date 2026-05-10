import networkx as nx
import math

class GraphManager:
    def __init__(self):
        self.graph = nx.Graph()
        self.positions = {}
        
    def build_case_graph(self, victim, suspects, bully):
        # Limpiar grafo previo
        self.graph.clear()
        
        # Añadir nodos principales
        self.graph.add_node(victim)
        self.graph.add_node("ShadowUser")
        
        for suspect in suspects:
            self.graph.add_node(suspect)
            
        import random
        # Usamos una semilla basada en la victima para que el layout sea consistente en un mismo caso
        random.seed(hash(victim))
        
        # Añadir conexiones (aristas) - Simulación de relaciones
        if suspects:
            self.graph.add_edge(victim, suspects[0], weight=1)
            if len(suspects) > 1:
                self.graph.add_edge(suspects[0], suspects[1], weight=3)
            if len(suspects) > 2:
                self.graph.add_edge(suspects[1], suspects[2], weight=2)
            
        # Conectar al bully con el ShadowUser
        if bully in suspects:
            self.graph.add_edge(bully, "ShadowUser", weight=1) # Pista fuerte
            
        # Agregar algunas aristas extra al azar para simular una red
        for _ in range(2):
            if suspects:
                s1 = random.choice(suspects)
                s2 = random.choice([victim] + suspects)
                if s1 != s2:
                    self.graph.add_edge(s1, s2, weight=random.randint(1, 3))
        
        # Generar posiciones visuales (Spring layout) 
        # para que Pygame sepa dónde dibujarlos
        # Aumentamos scale y k para que no se amontonen
        self.positions = nx.spring_layout(self.graph, center=(640, 360), scale=250, k=0.5, iterations=50)
        
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

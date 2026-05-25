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
            
        # Conectar al ShadowUser con varios sospechosos para ofuscar (ruido)
        for s in suspects:
            if s == bully:
                self.graph.add_edge(s, "ShadowUser", weight=1) # Conexión real, fuerte
            else:
                # Conexiones falsas con peso aleatorio mayor o igual para despistar
                if random.random() > 0.3: # 70% de probabilidad de tener conexión falsa
                    self.graph.add_edge(s, "ShadowUser", weight=random.randint(2, 5))
            
        # Agregar algunas aristas extra al azar entre sospechosos para simular una red y afectar la centralidad
        for _ in range(4): # Aumentado a 4 para más ruido
            if suspects:
                s1 = random.choice(suspects)
                s2 = random.choice([victim] + suspects)
                if s1 != s2:
                    # Si la arista ya existe, podríamos sobreescribir el peso, lo cual está bien
                    self.graph.add_edge(s1, s2, weight=random.randint(1, 3))
                    
        # Generar posiciones visuales (Spring layout) 
        # para que Pygame sepa dónde dibujarlos
        self.positions = nx.spring_layout(self.graph, center=(640, 360), scale=250, k=0.5, iterations=50)
        
        for node, pos in self.positions.items():
            self.positions[node] = (int(pos[0]), int(pos[1]))

    def sabotage_graph(self):
        """Modifica el grafo añadiendo ruido y alterando pesos para confundir los algoritmos."""
        import random
        nodes = list(self.graph.nodes())
        if len(nodes) >= 2:
            # Añadir 2 aristas aleatorias
            for _ in range(2):
                n1 = random.choice(nodes)
                n2 = random.choice(nodes)
                if n1 != n2:
                    self.graph.add_edge(n1, n2, weight=random.randint(1, 3))
            
            # Modificar el peso de una arista existente
            if self.graph.edges:
                edge_to_mod = random.choice(list(self.graph.edges()))
                self.graph[edge_to_mod[0]][edge_to_mod[1]]['weight'] = random.randint(1, 5)
                
        # Opcional: recalcular posiciones si queremos que el grafo "tiemble" o se reajuste con el ruido
        self.positions = nx.spring_layout(self.graph, center=(640, 360), scale=250, k=0.5, iterations=50)
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

    def inject_fake_node(self, label):
        """Añade un nodo falso con conexiones espurias para confundir el análisis."""
        import random
        nodes = list(self.graph.nodes())
        self.graph.add_node(label)
        # Conectar el nodo falso con 1-2 nodos existentes aleatorios
        for _ in range(random.randint(1, 2)):
            if nodes:
                target = random.choice(nodes)
                self.graph.add_edge(label, target, weight=random.randint(2, 5))
        # Recalcular posiciones
        self.positions = nx.spring_layout(self.graph, center=(640, 360), scale=250, k=0.5, iterations=50)
        for node, pos in self.positions.items():
            self.positions[node] = (int(pos[0]), int(pos[1]))

    def get_centrality(self):
        # Grado de centralidad para detectar nodos influyentes
        return nx.degree_centrality(self.graph)

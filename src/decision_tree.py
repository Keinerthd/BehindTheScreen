import json
import os

class DecisionTreeNode:
    def __init__(self, data):
        # Un nodo puede ser una pregunta (tiene question, yes, no)
        # o un resultado (tiene result)
        self.question = data.get("question")
        self.result = data.get("result")
        
        self.yes_branch = None
        self.no_branch = None

        if "yes" in data:
            self.yes_branch = DecisionTreeNode(data["yes"])
        if "no" in data:
            self.no_branch = DecisionTreeNode(data["no"])

    def is_leaf(self):
        return self.result is not None

class DecisionTree:
    def __init__(self, data_path=None):
        if data_path is None:
            # Construir la ruta relativa al archivo actual
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.data_path = os.path.join(base_dir, "data", "decision_tree.json")
        else:
            self.data_path = data_path
            
        self.root = None
        self.load_tree()

    def load_tree(self):
        if not os.path.exists(self.data_path):
            print(f"Error: Archivo de árbol de decisión no encontrado en {self.data_path}")
            return
            
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.root = DecisionTreeNode(data)
        except Exception as e:
            print(f"Error al cargar el árbol de decisiones: {e}")

    def classify_message_automatic(self, message):
        """
        Clasifica automáticamente un mensaje basado en palabras clave, 
        simulando el recorrido del árbol.
        """
        msg_lower = message.lower()
        insultos = ["tonto", "estupido", "idiota", "burlando", "peor", "odio", "soporta", "inútil", "malísimo", "asco"]
        amenazas = ["golpear", "matar", "cuidado", "amenaza", "publicar", "contraseñas", "suspendida", "págame", "transferir", "monedas", "foto vergonzosa", "peor"]
        rumores = ["dicen", "rumor", "verdad que", "editada", "publicó", "link", "fotos", "dirección", "escucharon", "diamantes gratis", "meme", "compártanlo", "grupo nuevo", "música fuerte"]

        # Recorrer el árbol
        node = self.root
        while node and not node.is_leaf():
            if node.question == "¿Contiene insulto?":
                answer = any(word in msg_lower for word in insultos)
            elif node.question == "¿Contiene amenaza?":
                answer = any(word in msg_lower for word in amenazas)
            elif node.question == "¿Difunde rumor?":
                answer = any(word in msg_lower for word in rumores)
            else:
                answer = False # default

            if answer:
                node = node.yes_branch
            else:
                node = node.no_branch

        if node and node.is_leaf():
            return node.result
        return "Clasificación Desconocida"
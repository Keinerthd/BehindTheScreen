import json
import os

class CaseManager:
    def __init__(self, data_path="data/cases.json"):
        self.data_path = data_path
        self.cases = []
        self.active_case = None
        self.load_cases()

    def load_cases(self):
        if not os.path.exists(self.data_path):
            print(f"Error: Archivo de casos no encontrado en {self.data_path}")
            return
            
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.cases = data.get("cases", [])
        except Exception as e:
            print(f"Error al cargar los casos: {e}")

    def select_case(self, case_id):
        for case in self.cases:
            if case["case_id"] == case_id:
                self.active_case = case
                return True
        return False

    def get_suspects(self):
        if self.active_case:
            return self.active_case.get("suspects", [])
        return []

    def get_messages(self):
        if self.active_case:
            return self.active_case.get("messages", [])
        return []

    def get_clues(self):
        if self.active_case:
            clues = list(self.active_case.get("clues", []))
            # Elemento aleatorio (Fase 6)
            import random
            random.shuffle(clues)
            return clues
        return []

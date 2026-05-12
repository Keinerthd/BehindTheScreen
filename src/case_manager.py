import json
import os

class CaseManager:
    def __init__(self, data_path=None):
        if data_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.data_path = os.path.join(base_dir, "data", "cases.json")
        else:
            self.data_path = data_path
        self.cases = []
        self.active_case = None
        self.all_clues = []
        self.unlocked_clues = []
        self.start_ticks = 0
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
        import random
        import pygame
        for case in self.cases:
            if case["case_id"] == case_id:
                self.active_case = case
                self.all_clues = list(self.active_case.get("clues", []))
                self.unlocked_clues = []
                self.start_ticks = pygame.time.get_ticks()
                return True
        return False

    def select_random_case(self):
        import random
        import pygame
        if self.cases:
            self.active_case = random.choice(self.cases)
            self.all_clues = list(self.active_case.get("clues", []))
            self.unlocked_clues = []
            self.start_ticks = pygame.time.get_ticks()
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
        return self.unlocked_clues

    def unlock_clue(self, index):
        if 0 <= index < len(self.all_clues):
            clue = self.all_clues[index]
            if clue not in self.unlocked_clues:
                self.unlocked_clues.append(clue)
                return True
        return False

    def get_remaining_time(self):
        import pygame
        if not self.active_case:
            return 0
        limit_ms = self.active_case.get("time_limit_minutes", 10) * 60 * 1000
        elapsed = pygame.time.get_ticks() - self.start_ticks
        return max(0, limit_ms - elapsed)

    def reduce_time(self, ms):
        """Reduce el tiempo restante restando ms al reloj (alejando start_ticks hacia el pasado)"""
        self.start_ticks -= ms

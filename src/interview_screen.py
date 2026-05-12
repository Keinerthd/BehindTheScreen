import pygame
import json
import os
from src.settings import COLORS
from config import WIDTH, HEIGHT


class InterviewScreen:
    def __init__(self, game):
        self.game = game
        self.font_title = pygame.font.SysFont("courier new", 28, bold=True)
        self.font_text = pygame.font.SysFont("courier new", 18)
        self.font_option = pygame.font.SysFont("courier new", 16)
        self.font_hint = pygame.font.SysFont("courier new", 14)

        self.btn_back = pygame.Rect(20, 20, 150, 40)

        self.dialogues = {}
        self.load_dialogues()

        self.current_suspect = None
        self.current_node = "start"
        self.dialogue_history = []

        self.option_rects = []
        self.option_scroll_offset = 0
        self.last_option_area = None

    def load_dialogues(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base_dir, "data", "dialogues.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self.dialogues = json.load(f)

    def start_interview(self, suspect_name):
        self.current_suspect = suspect_name
        self.current_node = "start"
        self.dialogue_history = []
        self.option_scroll_offset = 0

        case_id = str(self.game.case_manager.active_case.get("case_id"))
        if case_id in self.dialogues and suspect_name in self.dialogues[case_id]:
            self.add_history(suspect_name, self.dialogues[case_id][suspect_name]["start"]["text"])
        else:
            self.add_history(suspect_name, "No tengo nada que decir.")

    def add_history(self, speaker, text):
        self.dialogue_history.append({"speaker": speaker, "text": text})

    def get_current_options(self):
        case_id = str(self.game.case_manager.active_case.get("case_id"))
        if case_id in self.dialogues and self.current_suspect in self.dialogues[case_id]:
            node_data = self.dialogues[case_id][self.current_suspect].get(self.current_node, {})
            return node_data.get("options", [])
        return []

    def get_option_layout(self, options_count, history_end_y):
        option_height = 40
        option_gap = 10
        top_margin = 25
        bottom_margin = 20

        area_top = max(history_end_y + top_margin, 380)
        area_height = HEIGHT - area_top - bottom_margin
        content_height = 0
        if options_count > 0:
            content_height = options_count * option_height + max(0, options_count - 1) * option_gap

        max_scroll = max(0, content_height - area_height)
        self.option_scroll_offset = max(0, min(self.option_scroll_offset, max_scroll))

        return {
            "top": area_top,
            "height": area_height,
            "content_height": content_height,
            "option_height": option_height,
            "option_gap": option_gap,
            "max_scroll": max_scroll,
        }

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.current_screen = "investigation"
            elif event.key == pygame.K_DOWN:
                self.option_scroll_offset += 50
            elif event.key == pygame.K_UP:
                self.option_scroll_offset -= 50

        elif event.type == pygame.MOUSEWHEEL:
            self.option_scroll_offset -= event.y * 40

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.btn_back.collidepoint(event.pos):
                    self.game.current_screen = "investigation"
                    return

                # Check visible options only
                for rect, opt in self.option_rects:
                    if rect.collidepoint(event.pos):
                        self.add_history("Tú", opt["text"])
                        self.game.case_manager.reduce_time(5000)  # Cuesta 5 segundos preguntar

                        if "unlock_clue_index" in opt:
                            unlocked = self.game.case_manager.unlock_clue(opt["unlock_clue_index"])
                            if unlocked:
                                if hasattr(self.game, 'sound_manager'):
                                    self.game.sound_manager.play("success")
                                self.game.sync_state()

                        self.current_node = opt["next"]
                        self.option_scroll_offset = 0

                        case_id = str(self.game.case_manager.active_case.get("case_id"))
                        next_data = self.dialogues[case_id][self.current_suspect].get(self.current_node, {})
                        if "text" in next_data:
                            self.add_history(self.current_suspect, next_data["text"])
                        break

            # Compatibilidad con rueda antigua en algunos sistemas
            elif event.button == 4:
                self.option_scroll_offset -= 40
            elif event.button == 5:
                self.option_scroll_offset += 40

    def draw_button(self, screen, rect, text, mouse_pos):
        is_hovered = rect.collidepoint(mouse_pos)
        border_color = COLORS["neon_blue_hover"] if is_hovered else COLORS["neon_blue"]
        bg_color = (20, 60, 90) if is_hovered else COLORS["panel"]
        pygame.draw.rect(screen, bg_color, rect, border_radius=5)
        pygame.draw.rect(screen, border_color, rect, 2, border_radius=5)
        label = self.font_text.render(text, True, COLORS["white"] if is_hovered else COLORS["gray_text"])
        screen.blit(label, label.get_rect(center=rect.center))

    def draw_wrapped_text(self, screen, text, font, color, x, y, max_width):
        words = text.split(' ')
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            width, _ = font.size(test_line)
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    current_line = []
        if current_line:
            lines.append(' '.join(current_line))

        y_pos = y
        for line in lines:
            surf = font.render(line, True, color)
            screen.blit(surf, (x, y_pos))
            y_pos += font.get_linesize()
        return y_pos - y

    def draw_option_text(self, screen, text, rect):
        prefix = "> "
        available_width = rect.width - 30
        words = (prefix + text).split(' ')
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            width, _ = self.font_option.size(test_line)
            if width <= available_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))

        max_lines = 2
        lines = lines[:max_lines]
        y = rect.y + 6
        for line in lines:
            surf = self.font_option.render(line, True, COLORS["white"])
            screen.blit(surf, (rect.x + 15, y))
            y += self.font_option.get_linesize()

    def draw(self, screen):
        screen.fill(COLORS["background"])

        mouse_pos = pygame.mouse.get_pos()
        self.draw_button(screen, self.btn_back, "< VOLVER", mouse_pos)

        title = self.font_title.render(f"INTERROGATORIO: {self.current_suspect}", True, COLORS["neon_blue"])
        screen.blit(title, (200, 25))

        # Draw history
        y_offset = 100
        max_width = 800
        x_base = 240

        for item in self.dialogue_history[-6:]:  # Show only last 6 entries to reduce overflow
            speaker = item["speaker"]
            text = item["text"]

            if speaker == "Tú":
                color_name = COLORS["success_green"]
                color_text = COLORS["white"]
            else:
                color_name = COLORS["alert_red"]
                color_text = COLORS["gray_text"]

            name_surf = self.font_text.render(f"{speaker}:", True, color_name)
            screen.blit(name_surf, (x_base, y_offset))

            used_h = self.draw_wrapped_text(screen, text, self.font_text, color_text, x_base + 100, y_offset, max_width - 100)
            y_offset += used_h + 20

        # Draw options in a scrollable area
        options = self.get_current_options()
        self.option_rects = []
        layout = self.get_option_layout(len(options), y_offset)
        self.last_option_area = pygame.Rect(200, layout["top"], 880, layout["height"])

        if options:
            # Subtle panel behind the options area
            pygame.draw.rect(screen, (12, 24, 45), self.last_option_area, border_radius=6)
            pygame.draw.rect(screen, COLORS["neon_blue"], self.last_option_area, 1, border_radius=6)

            previous_clip = screen.get_clip()
            screen.set_clip(self.last_option_area)

            start_y = layout["top"] - self.option_scroll_offset
            for opt in options:
                rect = pygame.Rect(200, start_y, 880, layout["option_height"])

                # Only draw visible options
                if rect.bottom >= self.last_option_area.top and rect.top <= self.last_option_area.bottom:
                    self.option_rects.append((rect, opt))
                    is_hovered = rect.collidepoint(mouse_pos)
                    bg = (30, 70, 100) if is_hovered else COLORS["panel"]
                    pygame.draw.rect(screen, bg, rect, border_radius=5)
                    pygame.draw.rect(screen, COLORS["neon_blue"], rect, 1, border_radius=5)
                    self.draw_option_text(screen, opt['text'], rect)

                start_y += layout["option_height"] + layout["option_gap"]

            screen.set_clip(previous_clip)

            # Scroll hint / indicator
            if layout["max_scroll"] > 0:
                hint = self.font_hint.render("Usa la rueda del mouse o las flechas ↑ ↓ para ver más preguntas", True, COLORS["gray_text"])
                screen.blit(hint, (200, max(layout["top"] - 18, 0)))

                # Simple scrollbar
                scrollbar_x = self.last_option_area.right - 8
                scrollbar_rect = pygame.Rect(scrollbar_x, self.last_option_area.top + 4, 4, self.last_option_area.height - 8)
                pygame.draw.rect(screen, (40, 50, 70), scrollbar_rect, border_radius=3)

                thumb_h = max(30, int((self.last_option_area.height / layout["content_height"]) * scrollbar_rect.height))
                if layout["max_scroll"] > 0:
                    thumb_y = scrollbar_rect.y + int((self.option_scroll_offset / layout["max_scroll"]) * (scrollbar_rect.height - thumb_h))
                else:
                    thumb_y = scrollbar_rect.y
                thumb_rect = pygame.Rect(scrollbar_x, thumb_y, 4, thumb_h)
                pygame.draw.rect(screen, COLORS["neon_blue"], thumb_rect, border_radius=3)

import os
import pygame
import random
from config import WIDTH, HEIGHT, FPS
from src.menu import Menu
from src.investigation_screen import InvestigationScreen
from src.graph_screen import GraphScreen
from src.results_screen import ResultsScreen
from src.case_manager import CaseManager
from src.decision_tree import DecisionTree
from src.graph_manager import GraphManager
from src.network import NetworkManager
from src.bully_screen import BullyScreen
from src.interview_screen import InterviewScreen
from src.sound_manager import SoundManager

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Behind The Screen - Cyber Detective")

        self.clock = pygame.time.Clock()
        self.running = True
        self.current_screen = "menu"

        # Inicializar árbol de decisiones
        self.case_manager = CaseManager()
        self.case_manager.select_random_case()
        self.decision_tree = DecisionTree()

        # Inicializar y construir el grafo
        self.graph_manager = GraphManager()
        self.graph_manager.build_case_graph(
            self.case_manager.active_case.get("victim", "Emma"),
            self.case_manager.get_suspects(),
            self.case_manager.active_case.get("bully", "ShadowUser")
        )

        self.menu = Menu(self)
        self.investigation_screen = InvestigationScreen(self)
        self.graph_screen = GraphScreen(self)
        self.results_screen = ResultsScreen(self)
        self.bully_screen = BullyScreen(self)
        self.interview_screen = InterviewScreen(self)

        self.network = NetworkManager()
        self.host_ip = ""
        self.connection_error = ""
        self.role = "detective"
        self.last_time_warning = None
        self.game_over_sent = False
        self.sound_manager = SoundManager()
        self.clock_icon = self._load_clock_icon()
        self._time_alert_shown_at = None

        # ── Soporte de mando / Joystick ──────────────────────────────────────
        pygame.joystick.init()
        self.joystick = None
        self._init_joystick()
        self.cursor_x = WIDTH // 2
        self.cursor_y = HEIGHT // 2
        self.cursor_visible = False  # Solo mostrar si hay mando conectado

        # ── Transición de pantalla (terminal) ────────────────────────────────
        self._transition_active = False
        self._transition_alpha = 0          # 0-255
        self._transition_direction = "in"   # "in" = oscurecer, "out" = aclarar
        self._transition_target = None      # pantalla destino
        self._transition_speed = 12         # px por frame
        self._terminal_lines = []           # texto "hacker" que desfila
        self._terminal_timer = 0

        # ── Micro-notificaciones flotantes ───────────────────────────────────
        self._notifications = []            # lista de {text, x, y, alpha, dy, color}

        # ── Fake-clue visual: nodo falso inyectado en grafo ──────────────────
        self._fake_graph_nodes = []         # nombres de nodos falsos

    # ─────────────────────── JOYSTICK ────────────────────────────────────────

    def _init_joystick(self):
        count = pygame.joystick.get_count()
        if count > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.cursor_visible = True

    def _update_joystick_cursor(self):
        if self.joystick is None:
            return
        # Eje 0 = horizontal, Eje 1 = vertical (estándar Xbox/PS/genérico)
        dead_zone = 0.15
        speed = 8
        ax = self.joystick.get_axis(0)
        ay = self.joystick.get_axis(1)
        if abs(ax) > dead_zone:
            self.cursor_x = max(0, min(WIDTH,  self.cursor_x + int(ax * speed)))
        if abs(ay) > dead_zone:
            self.cursor_y = max(0, min(HEIGHT, self.cursor_y + int(ay * speed)))

    def _inject_mouse_event(self, button=1):
        """Simula un click de ratón en la posición del cursor virtual."""
        pygame.event.post(pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"pos": (self.cursor_x, self.cursor_y), "button": button}
        ))
        pygame.event.post(pygame.event.Event(
            pygame.MOUSEBUTTONUP,
            {"pos": (self.cursor_x, self.cursor_y), "button": button}
        ))

    def draw_joystick_cursor(self):
        if not self.cursor_visible or self.joystick is None:
            return
        x, y = self.cursor_x, self.cursor_y
        color = (0, 255, 200)
        # Mira: cruz + círculo exterior
        pygame.draw.circle(self.screen, color, (x, y), 14, 2)
        pygame.draw.line(self.screen, color, (x - 20, y), (x - 6,  y), 2)
        pygame.draw.line(self.screen, color, (x + 6,  y), (x + 20, y), 2)
        pygame.draw.line(self.screen, color, (x, y - 20), (x, y - 6),  2)
        pygame.draw.line(self.screen, color, (x, y + 6),  (x, y + 20), 2)
        # Pequeño punto central
        pygame.draw.circle(self.screen, color, (x, y), 3)

    # ─────────────────────── TRANSICIÓN ──────────────────────────────────────

    def start_transition(self, target_screen):
        """Inicia la cinemática de terminal hacia target_screen."""
        if self._transition_active:
            return
        self._transition_target = target_screen
        self._transition_active = True
        self._transition_direction = "in"
        self._transition_alpha = 0
        self._terminal_lines = []
        self._terminal_timer = 0

    def _update_transition(self):
        if not self._transition_active:
            return

        self._transition_timer_inner = getattr(self, "_transition_timer_inner", 0) + 1

        if self._transition_direction == "in":
            self._transition_alpha = min(255, self._transition_alpha + self._transition_speed)
            # Añadir texto de terminal verde cada cierto tiempo
            if self._transition_timer_inner % 4 == 0:
                lines_pool = [
                    "> CONECTANDO AL SERVIDOR...",
                    "> CARGANDO CASO #{}...".format(random.randint(100, 999)),
                    "> AUTENTICANDO DETECTIVE...",
                    "> ENCRIPTANDO CANAL...",
                    "> ACCESO CONCEDIDO",
                    "> RASTREANDO IP...",
                    "> ANALIZANDO RED SOCIAL...",
                    "> EXTRAYENDO METADATOS...",
                ]
                if len(self._terminal_lines) < 8:
                    self._terminal_lines.append(random.choice(lines_pool))
            if self._transition_alpha >= 255:
                # Cambiar pantalla y empezar a "abrir"
                self.current_screen = self._transition_target
                self._transition_direction = "out"
        else:
            self._transition_alpha = max(0, self._transition_alpha - self._transition_speed)
            if self._transition_alpha <= 0:
                self._transition_active = False
                self._transition_timer_inner = 0

    def draw_transition(self):
        if not self._transition_active:
            return
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(self._transition_alpha)
        self.screen.blit(overlay, (0, 0))

        if self._transition_alpha > 60:
            font = pygame.font.SysFont("courier new", 16)
            y = 200
            for line in self._terminal_lines[-10:]:
                surf = font.render(line, True, (0, 220, 80))
                surf.set_alpha(min(255, self._transition_alpha * 2))
                self.screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))
                y += 22

    # ─────────────────────── NOTIFICACIONES FLOTANTES ────────────────────────

    def add_notification(self, text, color=None, x=None, y=None):
        """Añade una micro-notificación flotante en pantalla."""
        from src.settings import COLORS
        if color is None:
            color = COLORS["neon_blue"]
        if x is None:
            x = random.randint(300, 700)
        if y is None:
            y = random.randint(200, 500)
        self._notifications.append({
            "text": text,
            "x": float(x), "y": float(y),
            "alpha": 255,
            "dy": -1.2,
            "color": color,
        })

    def _update_notifications(self):
        for n in self._notifications:
            n["y"] += n["dy"]
            n["alpha"] -= 3
        self._notifications = [n for n in self._notifications if n["alpha"] > 0]

    def draw_notifications(self):
        font = pygame.font.SysFont("courier new", 20, bold=True)
        for n in self._notifications:
            surf = font.render(n["text"], True, n["color"])
            surf.set_alpha(max(0, int(n["alpha"])))
            self.screen.blit(surf, (int(n["x"]) - surf.get_width() // 2, int(n["y"])))

    # ─────────────────────── HELPERS ─────────────────────────────────────────

    def _load_clock_icon(self):
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets", "images", "clock_icon.png",
        )
        try:
            image = pygame.image.load(icon_path).convert_alpha()
            return pygame.transform.smoothscale(image, (64, 64))
        except Exception:
            return None

    def host_game(self):
        success, msg = self.network.host_game()
        if success:
            self.host_ip = msg
            self.role = "detective"
            self.connection_error = ""
        else:
            self.connection_error = f"Error: {msg}"

    def join_game(self, ip):
        success, msg = self.network.join_game(ip)
        if success:
            self.role = "bully"
            self.connection_error = ""
        else:
            self.connection_error = f"Error: {msg}"

    def start_new_investigation(self):
        self.case_manager.select_random_case()
        self.graph_manager.build_case_graph(
            self.case_manager.active_case.get("victim", "Emma"),
            self.case_manager.get_suspects(),
            self.case_manager.active_case.get("bully", "ShadowUser")
        )
        self._fake_graph_nodes.clear()
        if hasattr(self, 'investigation_screen'):
            self.investigation_screen.selected_suspect = None
        self.last_time_warning = None
        self.game_over_sent = False
        if self.network.is_server and self.network.connected:
            self.sync_state()

    def sync_state(self):
        state = {
            "type": "sync",
            "victim": self.case_manager.active_case.get("victim", "Emma"),
            "bully": self.case_manager.active_case.get("bully", "ShadowUser"),
            "suspects": self.case_manager.get_suspects(),
            "messages": self.case_manager.get_messages(),
            "clues": self.case_manager.get_clues()
        }
        self.network.send_message(state)

    def _recover_random_clue(self):
        available = [c for c in self.case_manager.all_clues if c not in self.case_manager.unlocked_clues]
        if available:
            clue = random.choice(available)
            self.case_manager.unlocked_clues.append(clue)
            return clue
        return None

    def update_music(self):
        if not hasattr(self, 'sound_manager') or not self.sound_manager.enabled:
            return
        track = None
        if self.current_screen == "menu":
            track = "menu"
        elif self.current_screen in ["investigation", "interview", "graph"]:
            track = "investigation_bully" if self.role == "bully" else "investigation_detective"
        elif self.current_screen == "bully":
            track = "investigation_bully"
        elif self.current_screen == "results":
            track = "result_winner" if self.results_screen.result_type == "good" else "result_gameover"
        if track:
            self.sound_manager.play_music(track)

    # ─────────────────────── MAIN LOOP ───────────────────────────────────────

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

    def handle_events(self):
        from src.settings import toggle_high_contrast

        # Actualizar posición del cursor por joystick
        self._update_joystick_cursor()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # ── Joystick: detectar conexión/desconexión en caliente ──
            if event.type == pygame.JOYDEVICEADDED:
                self._init_joystick()
            if event.type == pygame.JOYDEVICEREMOVED:
                self.joystick = None
                self.cursor_visible = False

            # ── Botón A (0) del mando → click virtual ──
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:   # A / Cruz
                    self._inject_mouse_event(1)
                elif event.button == 1:  # B / Círculo → Escape
                    pygame.event.post(pygame.event.Event(
                        pygame.KEYDOWN,
                        {"key": pygame.K_ESCAPE, "mod": 0, "unicode": ""}
                    ))

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    toggle_high_contrast()
                elif event.key == pygame.K_h:
                    self.show_help = not getattr(self, 'show_help', False)
                elif event.key == pygame.K_m:
                    if hasattr(self, 'sound_manager'):
                        self.sound_manager.toggle_mute()

            if getattr(self, 'show_help', False):
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.show_help = False
                continue

            if self._transition_active:
                continue  # Bloquear input durante transición

            if self.current_screen == "menu":
                self.menu.handle_event(event)
            elif self.current_screen == "investigation":
                self.investigation_screen.handle_event(event)
            elif self.current_screen == "interview":
                self.interview_screen.handle_event(event)
            elif self.current_screen == "bully":
                self.bully_screen.handle_event(event)
            elif self.current_screen == "graph":
                self.graph_screen.handle_event(event)
            elif self.current_screen == "results":
                self.results_screen.handle_event(event)

    def update(self):
        self.update_music()
        self._update_transition()
        self._update_notifications()

        # Transición cuando el server conecta con el cliente
        if self.current_screen == "menu" and self.network.connected:
            if self.network.is_server:
                self.start_new_investigation()
                self.start_transition("investigation")
            elif self.network.is_client:
                self.start_transition("bully")

        # Check timer game over
        if self.current_screen in ["investigation", "interview", "graph"]:
            remaining = self.case_manager.get_remaining_time()
            total_time = self.case_manager.active_case.get("time_limit_minutes", 10) * 60 * 1000
            half_threshold = total_time // 2
            low_threshold = 120000 if total_time >= 240000 else total_time // 3

            warning = None
            if remaining <= low_threshold:
                warning = "low"
            elif remaining <= half_threshold:
                warning = "half"

            now = pygame.time.get_ticks()
            if warning == "low" and self.last_time_warning != "low":
                self.sound_manager.play("low_time")
                self.last_time_warning = "low"
                self._time_alert_shown_at = now
            elif warning == "half" and self.last_time_warning != "half":
                self.sound_manager.play("half_time")
                self.last_time_warning = "half"
                self._time_alert_shown_at = now

            if self._time_alert_shown_at is not None and now - self._time_alert_shown_at > 2000:
                self._time_alert_shown_at = None

            if remaining <= 0:
                self.results_screen.result_type = "timeout"
                self.start_transition("results")

        if self.current_screen == "results" and self.network.is_server and self.network.connected and not self.game_over_sent:
            self.network.send_message({
                "type": "game_over",
                "result": self.results_screen.result_type
            })
            self.game_over_sent = True

        # Procesar mensajes de red
        from src.settings import COLORS
        for msg in self.network.get_messages():
            msg_type = msg.get("type")
            if msg_type == "sync":
                self.case_manager.active_case["victim"] = msg["victim"]
                self.case_manager.active_case["bully"] = msg["bully"]
                self.case_manager.active_case["suspects"] = msg["suspects"]
                self.case_manager.active_case["messages"] = msg["messages"]
                self.case_manager.unlocked_clues = msg["clues"]
                self.graph_manager.build_case_graph(msg["victim"], msg["suspects"], msg["bully"])
            elif msg_type == "sabotage_clue":
                clue = msg["clue"]
                if clue in self.case_manager.get_clues():
                    self.case_manager.get_clues().remove(clue)
                    self.sound_manager.play("sabotage")
                    self.graph_manager.sabotage_graph()
                    self.add_notification("⚠ PISTA ELIMINADA", COLORS["alert_red"])
                    self.sync_state()
            elif msg_type == "sabotage_message":
                m = msg["message"]
                if m in self.case_manager.get_messages():
                    self.case_manager.get_messages().remove(m)
                    self.sound_manager.play("sabotage")
                    self.graph_manager.sabotage_graph()
                    self.add_notification("⚠ MENSAJE BORRADO", COLORS["alert_red"])
                    self.sync_state()
            elif msg_type == "create_fake_clue":
                clue = msg.get("clue")
                if clue and clue not in self.case_manager.get_clues():
                    self.case_manager.unlocked_clues.append(clue)
                    # Inyectar nodo falso en el grafo
                    fake_label = "???" + str(random.randint(10, 99))
                    self._fake_graph_nodes.append(fake_label)
                    self.graph_manager.inject_fake_node(fake_label)
                    self.add_notification("⚠ PISTA SOSPECHOSA", (255, 200, 0))
                    self.sync_state()
            elif msg_type == "verify_clue":
                # El detective verificó una pista — costará tiempo
                clue = msg.get("clue", "")
                is_fake = clue in [fc for fc in self.case_manager.get_clues()
                                   if any(clue == fc for fc in self._get_fake_clue_texts())]
                self.network.send_message({"type": "verify_result", "clue": clue, "is_fake": is_fake})
            elif msg_type == "verify_result":
                clue = msg.get("clue", "")
                is_fake = msg.get("is_fake", False)
                if is_fake and clue in self.case_manager.get_clues():
                    self.case_manager.get_clues().remove(clue)
                    self.add_notification("✓ PISTA FALSA ELIMINADA", COLORS["success_green"])
                else:
                    self.add_notification("✓ PISTA VERIFICADA — REAL", COLORS["neon_blue"])
            elif msg_type == "hacker_detected":
                recovered = self._recover_random_clue()
                if recovered:
                    self.add_notification("+PISTA RECUPERADA", COLORS["success_green"])
                    self.sync_state()
            elif msg_type == "game_over":
                self.results_screen.result_type = msg.get("result", "neutral")
                self.start_transition("results")
                self.game_over_sent = True

    def _get_fake_clue_texts(self):
        """Retorna la lista de textos de pistas falsas conocidos."""
        if hasattr(self, 'bully_screen'):
            return self.bully_screen.fake_clues
        return []

    def draw_time_alert_icon(self):
        if self.current_screen not in ["investigation", "interview", "graph"]:
            return
        if self._time_alert_shown_at is None or self.clock_icon is None:
            return
        margin = 20
        pos = (WIDTH - self.clock_icon.get_width() - margin, margin)
        self.screen.blit(self.clock_icon, pos)

    def draw(self):
        from src.settings import COLORS
        self.screen.fill(COLORS["background"])

        if self.current_screen == "menu":
            self.menu.draw(self.screen)
        elif self.current_screen == "investigation":
            self.investigation_screen.draw(self.screen)
        elif self.current_screen == "interview":
            self.interview_screen.draw(self.screen)
        elif self.current_screen == "bully":
            self.bully_screen.draw(self.screen)
        elif self.current_screen == "graph":
            self.graph_screen.draw(self.screen)
        elif self.current_screen == "results":
            self.results_screen.draw(self.screen)

        self.draw_time_alert_icon()
        self.draw_notifications()
        self.draw_transition()
        self.draw_joystick_cursor()

        # Overlay de ayuda
        if getattr(self, 'show_help', False):
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            font = pygame.font.SysFont("courier new", 24, bold=True)
            help_text = [
                "--- CONTROLES DE AYUDA ---",
                "",
                "[C] - Alternar Modo Alto Contraste",
                "[H] - Mostrar/Ocultar esta ventana de ayuda",
                "[ESC] - Volver atrás / Cerrar ventanas",
                "[M] - Silenciar/Activar música",
                "",
                "Mando: Palanca izquierda = Cursor | A = Click | B = Escape",
                "",
                "Objetivo: Lee los mensajes, revisa las pistas,",
                "y usa el analizador de red para identificar",
                "al verdadero acosador (ShadowUser).",
                "",
                "Selecciona un nombre en la lista de sospechosos",
                "y presiona ACUSAR SOSPECHOSO para decidir."
            ]

            y = 130
            for line in help_text:
                surf = font.render(line, True, COLORS["white"])
                self.screen.blit(surf, surf.get_rect(center=(WIDTH // 2, y)))
                y += 35

        pygame.display.flip()

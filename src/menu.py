import pygame
from src.settings import COLORS

class Menu:
    def __init__(self, game):
        self.game = game
        self.font_title = pygame.font.SysFont("courier new", 72, bold=True)
        self.font_subtitle = pygame.font.SysFont("courier new", 28)
        self.font_button = pygame.font.SysFont("courier new", 32, bold=True)
        self.font_input = pygame.font.SysFont("courier new", 28)

        self.single_button = pygame.Rect(490, 280, 300, 50)
        self.host_button = pygame.Rect(490, 340, 300, 50)
        self.join_button = pygame.Rect(490, 400, 300, 50)
        self.help_button = pygame.Rect(490, 460, 300, 50)
        self.exit_button = pygame.Rect(490, 520, 300, 50)
        self.mute_button = pygame.Rect(490, 580, 300, 50)
        
        self.joining = False
        self.ip_text = ""
        self.connect_button = pygame.Rect(490, 420, 300, 60)
        self.back_button = pygame.Rect(490, 500, 300, 60)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left click
                if not self.joining:
                    if self.single_button.collidepoint(event.pos):
                        if hasattr(self.game, 'sound_manager'):
                            self.game.sound_manager.play("button_click")
                        self.game.role = "detective"
                        self.game.start_new_investigation()
                        self.game.current_screen = "investigation"
                    elif self.host_button.collidepoint(event.pos):
                        if hasattr(self.game, 'sound_manager'):
                            self.game.sound_manager.play("button_click")
                        self.game.host_game()
                    elif self.join_button.collidepoint(event.pos):
                        if hasattr(self.game, 'sound_manager'):
                            self.game.sound_manager.play("button_click")
                        self.joining = True
                        self.ip_text = ""
                    elif self.help_button.collidepoint(event.pos):
                        if hasattr(self.game, 'sound_manager'):
                            self.game.sound_manager.play("button_click")
                        self.game.show_help = True
                    elif self.exit_button.collidepoint(event.pos):
                        if hasattr(self.game, 'sound_manager'):
                            self.game.sound_manager.play("button_click")
                        self.game.running = False
                    elif self.mute_button.collidepoint(event.pos):
                        if hasattr(self.game, 'sound_manager'):
                            self.game.sound_manager.play("button_click")
                            self.game.sound_manager.toggle_mute()
                else:
                    if self.connect_button.collidepoint(event.pos):
                        if hasattr(self.game, 'sound_manager'):
                            self.game.sound_manager.play("button_click")
                        self.game.join_game(self.ip_text)
                    elif self.back_button.collidepoint(event.pos):
                        if hasattr(self.game, 'sound_manager'):
                            self.game.sound_manager.play("button_click")
                        self.joining = False
                        
        elif event.type == pygame.KEYDOWN and self.joining:
            if event.key == pygame.K_BACKSPACE:
                self.ip_text = self.ip_text[:-1]
            elif event.key == pygame.K_RETURN:
                self.game.join_game(self.ip_text)
            else:
                if len(self.ip_text) < 15 and (event.unicode.isdigit() or event.unicode == '.'):
                    self.ip_text += event.unicode

    def draw_button(self, screen, rect, text, mouse_pos):
        is_hovered = rect.collidepoint(mouse_pos)
        
        # Color del borde
        border_color = COLORS["neon_blue_hover"] if is_hovered else COLORS["neon_blue"]
        # Color del fondo del botón
        bg_color = (20, 60, 90) if is_hovered else COLORS["panel"]
        
        pygame.draw.rect(screen, bg_color, rect, border_radius=5)
        pygame.draw.rect(screen, border_color, rect, 2, border_radius=5)

        text_color = COLORS["white"] if is_hovered else COLORS["gray_text"]
        label = self.font_button.render(text, True, text_color)
        label_rect = label.get_rect(center=rect.center)
        screen.blit(label, label_rect)

    def draw(self, screen):
        screen.fill(COLORS["background"])
        
        # Grid lineas de fondo
        for i in range(0, 1280, 40):
            pygame.draw.line(screen, (15, 25, 40), (i, 0), (i, 720))
        for i in range(0, 720, 40):
            pygame.draw.line(screen, (15, 25, 40), (0, i), (1280, i))

        title = self.font_title.render("BEHIND THE SCREEN", True, COLORS["neon_blue"])
        subtitle = self.font_subtitle.render("> SYSTEM.LOGIN() :: CYBER DETECTIVE_", True, COLORS["white"])

        screen.blit(title, title.get_rect(center=(640, 150)))
        screen.blit(subtitle, subtitle.get_rect(center=(640, 220)))

        mouse_pos = pygame.mouse.get_pos()

        if not self.joining:
            self.draw_button(screen, self.single_button, "SINGLE PLAYER", mouse_pos)
            self.draw_button(screen, self.host_button, "HOST GAME", mouse_pos)
            self.draw_button(screen, self.join_button, "JOIN GAME", mouse_pos)
            self.draw_button(screen, self.help_button, "AYUDA", mouse_pos)
            self.draw_button(screen, self.exit_button, "SALIR", mouse_pos)
            mute_label = "UNMUTE" if hasattr(self.game, 'sound_manager') and self.game.sound_manager.muted else "MUTE"
            self.draw_button(screen, self.mute_button, mute_label, mouse_pos)
            
            if self.game.network and self.game.network.is_server and not self.game.network.connected:
                msg = self.font_input.render(f"Esperando jugador en IP: {self.game.host_ip} ...", True, COLORS["neon_blue"])
                screen.blit(msg, msg.get_rect(center=(640, 600)))
                
                start_msg = self.font_input.render("(Puedes empezar en Single Player si no hay conexión)", True, COLORS["gray_text"])
                screen.blit(start_msg, start_msg.get_rect(center=(640, 640)))
        else:
            prompt = self.font_input.render("Ingresa la IP del Host:", True, COLORS["white"])
            screen.blit(prompt, prompt.get_rect(center=(640, 300)))
            
            input_rect = pygame.Rect(490, 340, 300, 50)
            pygame.draw.rect(screen, COLORS["panel"], input_rect)
            pygame.draw.rect(screen, COLORS["neon_blue"], input_rect, 2)
            
            ip_surf = self.font_input.render(self.ip_text + "_", True, COLORS["neon_blue"])
            screen.blit(ip_surf, (input_rect.x + 10, input_rect.y + 10))
            
            self.draw_button(screen, self.connect_button, "CONECTAR", mouse_pos)
            self.draw_button(screen, self.back_button, "VOLVER", mouse_pos)
            
            if hasattr(self.game, 'connection_error') and self.game.connection_error:
                err = self.font_input.render(self.game.connection_error, True, COLORS["alert_red"])
                screen.blit(err, err.get_rect(center=(640, 600)))


# Definición de colores principales (Estilo Cyberpunk / Hacker)

COLORS = {
    "background": (10, 15, 30),
    "panel": (30, 35, 45),
    "neon_blue": (0, 200, 255),
    "neon_blue_hover": (50, 230, 255),
    "white": (255, 255, 255),
    "gray_text": (150, 160, 180),
    "alert_red": (255, 50, 50),
    "success_green": (50, 255, 100),
    "node_color": (0, 150, 255),
    "edge_color": (0, 80, 150)
}

HIGH_CONTRAST = False

def toggle_high_contrast():
    global HIGH_CONTRAST
    HIGH_CONTRAST = not HIGH_CONTRAST
    if HIGH_CONTRAST:
        COLORS["background"] = (0, 0, 0)
        COLORS["panel"] = (0, 0, 0)
        COLORS["neon_blue"] = (255, 255, 0) # Amarillo de alto contraste
        COLORS["neon_blue_hover"] = (255, 255, 255)
        COLORS["white"] = (255, 255, 255)
        COLORS["gray_text"] = (200, 200, 200)
        COLORS["alert_red"] = (255, 0, 0)
        COLORS["success_green"] = (0, 255, 0)
        COLORS["node_color"] = (255, 255, 0)
        COLORS["edge_color"] = (255, 255, 255)
    else:
        COLORS["background"] = (10, 15, 30)
        COLORS["panel"] = (30, 35, 45)
        COLORS["neon_blue"] = (0, 200, 255)
        COLORS["neon_blue_hover"] = (50, 230, 255)
        COLORS["white"] = (255, 255, 255)
        COLORS["gray_text"] = (150, 160, 180)
        COLORS["alert_red"] = (255, 50, 50)
        COLORS["success_green"] = (50, 255, 100)
        COLORS["node_color"] = (0, 150, 255)
        COLORS["edge_color"] = (0, 80, 150)


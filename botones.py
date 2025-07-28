import asyncio
import platform
import pygame

if hasattr(pygame, 'init'):
    pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Juego de Cartas")

# Colores
GREEN_BUTTON = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (50, 50, 50)

# Fuente
font = pygame.font.Font(None, 36)

# Clase para los botones
class Button:
    def __init__(self, x, y, width, height, text, color=GREEN_BUTTON):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_surface = font.render(text, True, BLACK)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=20)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=20)
        text_rect = self.text_surface.get_rect(center=self.rect.center)
        surface.blit(self.text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Crear botones
buttons = [
    Button(50, 50, 150, 60, "Modo Automático"),
    Button(50, 120, 150, 60, "Modo Manual"),
    Button(50, 190, 150, 60, "Instrucciones"),
    Button(50, 260, 150, 60, "Reiniciar"),
    Button(50, 330, 150, 60, "Repartir"),
    Button(50, 400, 150, 60, "Mezclar"),
    Button(50, 470, 150, 60, "Jugar")
]

# Estado inicial
current_mode = "Manual"
instructions_visible = False

def setup():
    screen.fill(DARK_GRAY)

def update_loop():
    screen.fill(DARK_GRAY)
    for button in buttons:
        button.draw(screen)
    if instructions_visible:
        instructions_text = font.render("Presiona los botones para interactuar. Usa Modo Automático para juego automático.", True, WHITE)
        screen.blit(instructions_text, (250, 50))
    pygame.display.flip()

async def main():
    global instructions_visible, current_mode
    setup()
    running = True
    QUIT = getattr(pygame, "QUIT", 256)
    MOUSEBUTTONDOWN = getattr(pygame, "MOUSEBUTTONDOWN", 1025)
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for button in buttons:
                    if button.is_clicked(pos):
                        if button.text == "Instrucciones":
                            instructions_visible = not instructions_visible
                        elif button.text == "Modo Automático":
                            current_mode = "Automático"
                        elif button.text == "Modo Manual":
                            current_mode = "Manual"
                        elif button.text == "Reiniciar":
                            setup()  # Reinicia el juego
                        elif button.text == "Repartir":
                            print("Repartiendo cartas...")
                        elif button.text == "Mezclar":
                            print("Mezclando cartas...")
                        elif button.text == "Jugar":
                            print(f"Jugando en modo {current_mode}...")
        update_loop()
        await asyncio.sleep(1.0 / 60)  # Control de FPS

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
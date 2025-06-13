import pygame
import sys
import json

# ---------- Ship Class ----------
class Ship:
    def __init__(self, name, positions):
        self.name = name
        self.positions = positions
        self.length = len(positions)

def load_ships(filename):
    ships = []
    with open(filename, 'r') as file:
        data = json.load(file)
        for ship_data in data["ships"]:
            ship = Ship(ship_data["name"], ship_data["positions"])
            ships.append(ship)
    return ships

ships = load_ships('./src/ships.json')

# ---------- Initialize Pygame ----------
pygame.init()
pygame.mixer.init()
BOOM_SOUND = pygame.mixer.Sound("./src/boom.mp3")
BOOM_SOUND.set_volume(1.0)
PEW_SOUND = pygame.mixer.Sound("./src/pew.mp3")

# ---------- Constants ----------
GRID_SIZE = 20
PLAYING_ROWS = 10
PLAYING_COLS = 10
SCREEN_WIDTH = (PLAYING_COLS * 2 + 4) * GRID_SIZE  # space for 2 grids + padding
SCREEN_HEIGHT = 24 * GRID_SIZE
TOP_BORDER_THICKNESS = GRID_SIZE * 2
BG_COLOR = (0, 0, 0)
BORDER_COLOR = (255, 0, 0)
TEXT_COLOR = (255, 255, 255)
GRID_COLOR = (0, 255, 0)
RED_GRID_COLOR = (255, 0, 0)
ORANGE_GRID_COLOR = (255, 165, 0)
CURSOR_COLOR = (255, 255, 0)

# ---------- Screen Setup ----------
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Battle Ship")
font = pygame.font.SysFont(None, 36)

# ---------- Grid Start Positions ----------
left_grid_x = SCREEN_WIDTH // 4 - (PLAYING_COLS * GRID_SIZE) // 2
right_grid_x = 3 * SCREEN_WIDTH // 4 - (PLAYING_COLS * GRID_SIZE) // 2
start_y = SCREEN_HEIGHT // 2 - (PLAYING_ROWS * GRID_SIZE) // 2

# ---------- Player Class ----------
class Player:
    def __init__(self, name):
        self.name = name
        self.moves = []

player1 = Player("Player 1")
player2 = Player("Player 2")
current_player = 1  # 1 = player1, 2 = player2
sunk_ships = set()

# ---------- Cursor Position ----------
cursor_row = 0
cursor_col = 0

# ---------- Generate Grid ----------
grid_squares = [{"Row": row, "Column": col} for row in range(PLAYING_ROWS) for col in range(PLAYING_COLS)]

# ---------- Drawing Functions ----------
def draw_grid_squares(player, offset_x, current_time, cursor_pos=None):
    completed_ship_positions = set()
    partial_ship_positions = set()

    for ship in ships:
        ship_tuples = [tuple(pos) for pos in ship.positions]
        hits = [pos for pos in ship_tuples if pos in player.moves]
        if len(hits) == len(ship_tuples) and hits:
            completed_ship_positions.update(ship_tuples)
        elif len(hits) > 0:
            partial_ship_positions.update(hits)

    for square in grid_squares:
        row = square["Row"]
        col = square["Column"]
        x = offset_x + col * GRID_SIZE
        y = start_y + row * GRID_SIZE

        if (row, col) in completed_ship_positions:
            pygame.draw.rect(screen, RED_GRID_COLOR, (x, y, GRID_SIZE, GRID_SIZE))
        elif (row, col) in partial_ship_positions:
            pygame.draw.rect(screen, ORANGE_GRID_COLOR, (x, y, GRID_SIZE, GRID_SIZE))
        elif (row, col) in player.moves:
            pygame.draw.rect(screen, GRID_COLOR, (x, y, GRID_SIZE, GRID_SIZE), 2)
            pygame.draw.line(screen, RED_GRID_COLOR, (x, y), (x + GRID_SIZE, y + GRID_SIZE), 3)
            pygame.draw.line(screen, RED_GRID_COLOR, (x + GRID_SIZE, y), (x, y + GRID_SIZE), 3)
        else:
            pygame.draw.rect(screen, GRID_COLOR, (x, y, GRID_SIZE, GRID_SIZE), 2)

    if cursor_pos and cursor_pos not in player.moves:
        r, c = cursor_pos
        x = offset_x + c * GRID_SIZE
        y = start_y + r * GRID_SIZE
        if (current_time // 300) % 2 == 0:
            pygame.draw.rect(screen, CURSOR_COLOR, (x + 2, y + 2, GRID_SIZE - 4, GRID_SIZE - 4))

def draw_elements():
    screen.fill(BG_COLOR)
    pygame.draw.rect(screen, BORDER_COLOR, (0, 0, SCREEN_WIDTH, TOP_BORDER_THICKNESS))  # Top Border

    current_time = pygame.time.get_ticks()
    draw_grid_squares(player1, left_grid_x, current_time, (cursor_row, cursor_col) if current_player == 1 else None)
    draw_grid_squares(player2, right_grid_x, current_time, (cursor_row, cursor_col) if current_player == 2 else None)

    # Turn Display
    label = font.render(f"{'Player 1' if current_player == 1 else 'Player 2'}'s Turn", True, TEXT_COLOR)
    screen.blit(label, (SCREEN_WIDTH // 2 - label.get_width() // 2, 20))

    pygame.display.flip()

# ---------- Main Loop ----------
def main():
    global cursor_row, cursor_col, current_player
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    cursor_row = max(0, cursor_row - 1)
                elif event.key == pygame.K_DOWN:
                    cursor_row = min(PLAYING_ROWS - 1, cursor_row + 1)
                elif event.key == pygame.K_LEFT:
                    cursor_col = max(0, cursor_col - 1)
                elif event.key == pygame.K_RIGHT:
                    cursor_col = min(PLAYING_COLS - 1, cursor_col + 1)
                elif event.key == pygame.K_RETURN:
                    current = player1 if current_player == 1 else player2
                    if (cursor_row, cursor_col) not in current.moves:
                        current.moves.append((cursor_row, cursor_col))
                        print(f"{current.name} played: {(cursor_row, cursor_col)}")

                        played_pew = False
                        for idx, ship in enumerate(ships):
                            ship_tuples = [tuple(pos) for pos in ship.positions]
                            if idx not in sunk_ships and all(pos in current.moves for pos in ship_tuples):
                                BOOM_SOUND.play()
                                sunk_ships.add(idx)
                                played_pew = True
                        if not played_pew:
                            for ship in ships:
                                if (cursor_row, cursor_col) in [tuple(p) for p in ship.positions]:
                                    PEW_SOUND.play()
                                    break

                        current_player = 2 if current_player == 1 else 1  # Switch turn

        draw_elements()
        clock.tick(60)

# ---------- Start Game ----------
main()
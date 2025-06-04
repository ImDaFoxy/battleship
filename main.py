import pygame
import sys
import json

# Ship Class
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

ships = load_ships('ships.json')

# Initialize Pygame
pygame.init()
pygame.mixer.init()
BOOM_SOUND = pygame.mixer.Sound("boom.mp3")
PEW_SOUND = pygame.mixer.Sound("pew.mp3")

#---------- Constants ---------- 
GRID_SIZE = 20
SCREEN_WIDTH = 32 * GRID_SIZE
SCREEN_HEIGHT = 24 * GRID_SIZE
TOP_BORDER_THICKNESS = GRID_SIZE * 2
SIDE_BORDER_THICKNESS = GRID_SIZE
BG_COLOR = (0, 0, 0)
BORDER_COLOR = (255, 0, 0)
TEXT_COLOR = (255, 255, 255)
GRID_COLOR = (0, 255, 0)
RED_GRID_COLOR = (255, 0, 0)
ORANGE_GRID_COLOR = (255, 165, 0)  # Orange for partial ship hit
CURSOR_COLOR = (255, 255, 0)
SHIP_COLOR = (0, 0, 255)
PLAYING_ROWS = 10
PLAYING_COLS = 10
start_x = SCREEN_WIDTH // 2 - (PLAYING_COLS * GRID_SIZE) // 2
start_y = SCREEN_HEIGHT // 2 - (PLAYING_ROWS * GRID_SIZE) // 2

cursor_row = 0
cursor_col = 0

# Set up display and fonts
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Battle Ship")
font = pygame.font.SysFont(None, 36)

# Player1 Class
class Player1():
    def __init__(self, name, moves=None, score=0):
        self.name = name
        self.moves = moves if moves is not None else []
        self.score = score

player1 = Player1("Player 1")

# Track which ships have already been sunk (by index)
sunk_ships = set()

# Generation of Grid
grid_squares = []
for row in range(PLAYING_ROWS):
    for col in range(PLAYING_COLS):
        square = {"Row": row, "Column": col}
        grid_squares.append(square)

def draw_blinking_cursor(row, col, current_time):
    # Only draw cursor if current square is not already selected
    if (row, col) in player1.moves:
        return
    if (current_time // 300) % 2 == 0:
        x = start_x + col * GRID_SIZE
        y = start_y + row * GRID_SIZE
        pygame.draw.rect(screen, CURSOR_COLOR, (x + 2, y + 2, GRID_SIZE - 4, GRID_SIZE - 4))

def draw_grid_squares(current_time):
    # Find all ship positions that are fully hit (whole ship found)
    completed_ship_positions = set()
    # Find all ship positions that are partially hit (part of ship found)
    partial_ship_positions = set()
    for ship in ships:
        ship_tuples = [tuple(pos) for pos in ship.positions]
        hits = [pos for pos in ship_tuples if pos in player1.moves]
        if len(hits) == len(ship_tuples) and hits:
            # All parts found: whole ship sunk
            completed_ship_positions.update(ship_tuples)
        elif len(hits) > 0:
            # Some parts found: partial hit
            partial_ship_positions.update(hits)

    for square in grid_squares:
        row = square["Row"]
        col = square["Column"]
        x = start_x + col * GRID_SIZE
        y = start_y + row * GRID_SIZE

        if (row, col) in completed_ship_positions:
            # Draw the whole square red if the ship is sunk
            pygame.draw.rect(screen, RED_GRID_COLOR, (x, y, GRID_SIZE, GRID_SIZE))
        elif (row, col) in partial_ship_positions:
            # Draw the square orange if it's a hit but not all parts found
            pygame.draw.rect(screen, ORANGE_GRID_COLOR, (x, y, GRID_SIZE, GRID_SIZE))
        elif (row, col) in player1.moves:
            pygame.draw.rect(screen, GRID_COLOR, (x, y, GRID_SIZE, GRID_SIZE), 2)
            pygame.draw.line(screen, RED_GRID_COLOR, (x, y), (x + GRID_SIZE, y + GRID_SIZE), 3)
            pygame.draw.line(screen, RED_GRID_COLOR, (x + GRID_SIZE, y), (x, y + GRID_SIZE), 3)
        else:
            pygame.draw.rect(screen, GRID_COLOR, (x, y, GRID_SIZE, GRID_SIZE), 2)  # green outline

    # Only draw blinking cursor if current square is not already selected
    if (cursor_row, cursor_col) not in player1.moves:
        draw_blinking_cursor(cursor_row, cursor_col, current_time)
    # Draw ships as blue squares
    # for ship in ships:
    #     for pos in ship.positions:
    #         sx = start_x + pos[1] * GRID_SIZE
    #         sy = start_y + pos[0] * GRID_SIZE
    #         pygame.draw.rect(screen, SHIP_COLOR, (sx + 4, sy + 4, GRID_SIZE - 8, GRID_SIZE - 8))

def draw_elements():
    """Draw the game border, score, and grid squares."""
    screen.fill(BG_COLOR)
    # Draw borders
    pygame.draw.rect(screen, BORDER_COLOR, (0, 0, SCREEN_WIDTH, TOP_BORDER_THICKNESS))  # Top
    pygame.draw.rect(screen, BORDER_COLOR, (0, 0, SIDE_BORDER_THICKNESS, SCREEN_HEIGHT))  # Left
    pygame.draw.rect(screen, BORDER_COLOR, (0, SCREEN_HEIGHT - SIDE_BORDER_THICKNESS, SCREEN_WIDTH, SIDE_BORDER_THICKNESS))  # Bottom
    pygame.draw.rect(screen, BORDER_COLOR, (SCREEN_WIDTH - SIDE_BORDER_THICKNESS, 0, SIDE_BORDER_THICKNESS, SCREEN_HEIGHT))  # Right
    # Draw grid and cursor
    current_time = pygame.time.get_ticks()
    draw_grid_squares(current_time)
    pygame.display.flip()

def main():
    global cursor_row, cursor_col
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
                    if (cursor_row, cursor_col) not in player1.moves:
                        player1.moves.append((cursor_row, cursor_col))
                        print(player1.moves)  # Print the list of selected squares

                        played_pew = False
                        # Play boom sound if a ship is newly sunk
                        for idx, ship in enumerate(ships):
                            ship_tuples = [tuple(pos) for pos in ship.positions]
                            if idx not in sunk_ships and all(pos in player1.moves for pos in ship_tuples):
                                BOOM_SOUND.play()
                                sunk_ships.add(idx)
                                played_pew = True  # Don't play pew if boom is played
                        # Play pew sound if the move is a hit but not a sunk ship
                        if not played_pew:
                            for ship in ships:
                                ship_tuples = [tuple(pos) for pos in ship.positions]
                                if (cursor_row, cursor_col) in ship_tuples:
                                    PEW_SOUND.play()
                                    break
        draw_elements()
        clock.tick(60)

# Start the game
main()
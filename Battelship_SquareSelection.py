import pygame
import sys
import json

# Ship Class
class Ship:
    def _init_(self, name, positions):
        self.name = name
        self.positions = positions
        self.length = len(positions)

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

#---------- Constants ---------- 
# Pop Up 
GRID_SIZE = 20                              # Pixel Size of each grid
SCREEN_WIDTH = 32 * GRID_SIZE               # Screen width
SCREEN_HEIGHT = 24 * GRID_SIZE              # Screen height
TOP_BORDER_THICKNESS = GRID_SIZE * 2        # Border thickness
SIDE_BORDER_THICKNESS = GRID_SIZE           # Border thickness
BG_COLOR = (0, 0, 0)                        # Background Color
BORDER_COLOR = (255, 0, 0)                  # Border Color
TEXT_COLOR = (255, 255, 255)                # Text Color

# Playing Board
GRID_COLOR = (0, 255, 0)                    # Color for Grid
PLAYING_ROWS = 10                            # Playing Board Rows
PLAYING_COLS = 10                            # Playing Board Collumn
start_x = SCREEN_WIDTH/2 - (PLAYING_COLS*GRID_SIZE/2)      # Position of Grid x
start_y = SCREEN_HEIGHT/2 - (PLAYING_ROWS*GRID_SIZE/2)     # Position of Grid y

# Cursor 
CURSOR_COLOR = (255, 255, 0)                # Color for Cursor Blinking
cursor_row = 0                              # Cursor starting position horizontally
cursor_col = 0                              # Cursor starting position vertically
#--------------------------------

# Set up display and fonts
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Battle Ship")
font = pygame.font.SysFont(None, 36)

#Class Player1
class Player1():
    def __init__(self, name, moves=None, score=0) :
        self.name = name
        self.moves = moves if moves is not None else []
        self.score = score
    
# Create a Player1 instance
player1 = Player1("Player 1")

# Generation of Grid
grid_squares = []
for row in range(PLAYING_ROWS):
    for col in range(PLAYING_COLS):
        square = {"Row": row, "Column": col}
        grid_squares.append(square)

def draw_blinking_cursor(row, col, current_time):
    """Draw a blinking square at the given row and column."""
    if (current_time // 300) % 2 == 0:  # Blink on/off every 300 ms
        x = start_x + col * GRID_SIZE
        y = start_y + row * GRID_SIZE
        pygame.draw.rect(screen, CURSOR_COLOR, (x + 2, y + 2, GRID_SIZE - 4, GRID_SIZE - 4))

def draw_grid_squares(current_time):
    for square in grid_squares:
        row = square["Row"]
        col = square["Column"]
        x = start_x + col * GRID_SIZE
        y = start_y + row * GRID_SIZE
        # Draw a red X if this square is in player1.moves, else green outline
        if (row, col) in player1.moves:
            pygame.draw.rect(screen, GRID_COLOR, (x, y, GRID_SIZE, GRID_SIZE), 2)
            pygame.draw.line(screen, RED_GRID_COLOR, (x, y), (x + GRID_SIZE, y + GRID_SIZE), 3)
            pygame.draw.line(screen, RED_GRID_COLOR, (x + GRID_SIZE, y), (x, y + GRID_SIZE), 3)
        else:
            pygame.draw.rect(screen, GRID_COLOR, (x, y, GRID_SIZE, GRID_SIZE), 2)  # green outline
    # Only draw blinking cursor if current square is not already selected
    if (cursor_row, cursor_col) not in player1.moves:
        draw_blinking_cursor(cursor_row, cursor_col, current_time)

      # Draw ships
    for ship in ships:
        for pos in ship.positions:
            x = start_x + pos[1] * GRID_SIZE
            y = start_y + pos[0] * GRID_SIZE
            pygame.draw.rect(screen, (0, 0, 255), (x + 4, y + 4, GRID_SIZE - 8, GRID_SIZE - 8))


def draw_elements():
    """Draw the game border, score, and grid squares."""
    screen.fill(BG_COLOR)
    
    # Draw borders
    pygame.draw.rect(screen, BORDER_COLOR, (0, 0, SCREEN_WIDTH, TOP_BORDER_THICKNESS))  # Top
    pygame.draw.rect(screen, BORDER_COLOR, (0, 0, SIDE_BORDER_THICKNESS, SCREEN_HEIGHT))  # Left
    pygame.draw.rect(screen, BORDER_COLOR, (0, SCREEN_HEIGHT - SIDE_BORDER_THICKNESS, SCREEN_WIDTH, SIDE_BORDER_THICKNESS))  # Bottom
    pygame.draw.rect(screen, BORDER_COLOR, (SCREEN_WIDTH - SIDE_BORDER_THICKNESS, 0, SIDE_BORDER_THICKNESS, SCREEN_HEIGHT))  # Right

    # Display score
    # score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
    # screen.blit(score_text, (10, 5))

    # Draw grid and cursor
    current_time = pygame.time.get_ticks()
    draw_grid_squares(current_time)

    pygame.display.flip()

# ...existing code...

RED_GRID_COLOR = (255, 0, 0)  # Red color for locked square

square_locked = False
locked_row = None
locked_col = None

def draw_blinking_cursor(row, col, current_time):
    # Only draw cursor if current square is not already selected
    if (row, col) in player1.moves:
        return
    if (current_time // 300) % 2 == 0:
        x = start_x + col * GRID_SIZE
        y = start_y + row * GRID_SIZE
        pygame.draw.rect(screen, CURSOR_COLOR, (x + 2, y + 2, GRID_SIZE - 4, GRID_SIZE - 4))

def draw_grid_squares(current_time):
    for square in grid_squares:
        row = square["Row"]
        col = square["Column"]
        x = start_x + col * GRID_SIZE
        y = start_y + row * GRID_SIZE
        # Draw a red X if this square is in player1.moves, else green outline
        if (row, col) in player1.moves:
            pygame.draw.rect(screen, GRID_COLOR, (x, y, GRID_SIZE, GRID_SIZE), 2)
            pygame.draw.line(screen, RED_GRID_COLOR, (x, y), (x + GRID_SIZE, y + GRID_SIZE), 3)
            pygame.draw.line(screen, RED_GRID_COLOR, (x + GRID_SIZE, y), (x, y + GRID_SIZE), 3)
        else:
            pygame.draw.rect(screen, GRID_COLOR, (x, y, GRID_SIZE, GRID_SIZE), 2)  # green outline
    # Only draw blinking cursor if current square is not already selected
    if (cursor_row, cursor_col) not in player1.moves:
        draw_blinking_cursor(cursor_row, cursor_col, current_time)

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
                    # Add the selected square to player1.moves if not already selected
                    if (cursor_row, cursor_col) not in player1.moves:
                        player1.moves.append((cursor_row, cursor_col))
                        print(player1.moves) 
                        
        draw_elements()
        clock.tick(60)



# Start the game
main()



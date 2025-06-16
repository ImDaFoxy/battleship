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
SCREEN_WIDTH = (PLAYING_COLS * 2 + 10) * GRID_SIZE  # space for 2 grids + padding
SCREEN_HEIGHT = 24 * GRID_SIZE
TOP_BORDER_THICKNESS = 0
BG_COLOR = (0, 0, 0)
BORDER_COLOR = (255, 0, 0)
TEXT_COLOR = (255, 255, 255)
GRID_COLOR = (255, 204, 229)
RED_GRID_COLOR = (255, 0, 0)
ORANGE_GRID_COLOR = (255, 165, 0)
CURSOR_COLOR = (255, 255, 0)
BUTTON_COLOR = (40, 40, 120)
BUTTON_HOVER_COLOR = (80, 80, 200)
BUTTON_TEXT_COLOR = (255, 255, 255)

# ---------- Screen Setup ----------
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Battle Ship")
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 64)

icon = pygame.image.load("./src/BG.png")
pygame.display.set_icon(icon)
background_img = pygame.image.load("./src/BG.png")
background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
bg_main_img = pygame.image.load("./src/bg_main.png")
bg_main_img = pygame.transform.scale(bg_main_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

# ---------- Grid Start Positions ----------
left_grid_x = SCREEN_WIDTH // 4 - (PLAYING_COLS * GRID_SIZE) // 2
right_grid_x = 3 * SCREEN_WIDTH // 4 - (PLAYING_COLS * GRID_SIZE) // 2
start_y = SCREEN_HEIGHT // 2 - (PLAYING_ROWS * GRID_SIZE) // 2

# ---------- Player Classes ----------
class Player1:
    def __init__(self):
        self.name = "Player 1"
        self.moves = []
        self.ships = []

class Player2:
    def __init__(self):
        self.name = "Player 2"
        self.moves = []
        self.ships = []

player1 = Player1()
player2 = Player2()
current_player = 1  # 1 = player1, 2 = player2

# Track sunk ships for each player
sunk_ships_p1 = set()  # Ships of player 1 sunk by player 2
sunk_ships_p2 = set()  # Ships of player 2 sunk by player 1

# ---------- Cursor Position ----------
cursor_row = 0
cursor_col = 0

# ---------- Generate Grid ----------
grid_squares = [{"Row": row, "Column": col} for row in range(PLAYING_ROWS) for col in range(PLAYING_COLS)]

# ---------- Game States ----------
MENU, PLACEMENT, PLAY = 0, 1, 2
game_state = MENU

# For placement phase
placement_player = 1
placement_index = 0
placement_ships = [Ship(ship.name, [[0, i] for i in range(ship.length)]) for ship in ships]

# ---------- Drawing Functions ----------
def draw_grid_squares(player, ships, offset_x, current_time, cursor_pos=None):
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

def draw_ship_placement(ships, offset_x, highlight_idx=None):
    for idx, ship in enumerate(ships):
        color = (0, 255, 0) if idx == highlight_idx else (0, 128, 255)
        for pos in ship.positions:
            row, col = pos
            x = offset_x + col * GRID_SIZE
            y = start_y + row * GRID_SIZE
            pygame.draw.rect(screen, color, (x, y, GRID_SIZE, GRID_SIZE))

def draw_label_with_bg(label, y):
    label_rect = label.get_rect(center=(SCREEN_WIDTH // 2, y))
    pygame.draw.rect(screen, (30, 30, 30), (label_rect.x - 10, label_rect.y - 5, label_rect.width + 20, label_rect.height + 10))
    screen.blit(label, label_rect)

def draw_menu():
    screen.blit(bg_main_img, (0, 0))
    #draw_label_with_bg(title, 120) RERMOVE

    # Draw Start Button
    button_w, button_h = 200, 40
    button_x = SCREEN_WIDTH // 2 - button_w // 2
    button_y = 400
    mouse_pos = pygame.mouse.get_pos()
    button_rect = pygame.Rect(button_x, button_y, button_w, button_h)
    hovering = button_rect.collidepoint(mouse_pos)
    color = BUTTON_HOVER_COLOR if hovering else BUTTON_COLOR
    pygame.draw.rect(screen, color, button_rect, border_radius=12)
    pygame.draw.rect(screen, (255, 255, 255), button_rect, 3, border_radius=12)
    btn_label = font.render("START", True, BUTTON_TEXT_COLOR)
    btn_label_rect = btn_label.get_rect(center=button_rect.center)
    screen.blit(btn_label, btn_label_rect)
    pygame.display.flip()
    return button_rect

def draw_elements():
    screen.blit(background_img, (0, 0))
    pygame.draw.rect(screen, BORDER_COLOR, (0, 0, SCREEN_WIDTH, TOP_BORDER_THICKNESS))
    current_time = pygame.time.get_ticks()

    label_y = 70
    if game_state == PLACEMENT:
        label = font.render(f"Player {placement_player} - Place Your Ships", True, TEXT_COLOR)
        draw_label_with_bg(label, label_y)
        offset_x = left_grid_x if placement_player == 1 else right_grid_x
        if placement_player == 1:
            draw_grid_squares(player1, player1.ships, offset_x, current_time)
        else:
            draw_grid_squares(player2, player2.ships, offset_x, current_time)
        draw_ship_placement(placement_ships, offset_x, placement_index)
    else:
        label = font.render(f"{'Player 1' if current_player == 1 else 'Player 2'}'s Turn", True, TEXT_COLOR)
        draw_label_with_bg(label, label_y)
        draw_grid_squares(player1, player1.ships, left_grid_x, current_time, (cursor_row, cursor_col) if current_player == 1 else None)
        draw_grid_squares(player2, player2.ships, right_grid_x, current_time, (cursor_row, cursor_col) if current_player == 2 else None)

    pygame.display.flip()

def move_ship(ship, dr, dc):
    for pos in ship.positions:
        pos[0] += dr
        pos[1] += dc

def is_valid_position(ship, placed_ships):
    for pos in ship.positions:
        r, c = pos
        if not (0 <= r < PLAYING_ROWS and 0 <= c < PLAYING_COLS):
            return False
        for other in placed_ships:
            if [r, c] in other.positions:
                return False
    return True

def rotate_ship(ship):
    # Rotate ship horizontally/vertically around first cell
    base = ship.positions[0]
    if all(pos[0] == base[0] for pos in ship.positions):  # horizontal -> vertical
        ship.positions = [[base[0] + i, base[1]] for i in range(ship.length)]
    else:  # vertical -> horizontal
        ship.positions = [[base[0], base[1] + i] for i in range(ship.length)]

def main():
    global cursor_row, cursor_col, current_player, game_state
    global placement_player, placement_index, placement_ships

    clock = pygame.time.Clock()

    while True:
        if game_state == MENU:
            button_rect = draw_menu()
        else:
            draw_elements()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif game_state == MENU:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if button_rect.collidepoint(event.pos):
                        # Start the game, go to placement phase
                        game_state = PLACEMENT
                        placement_player = 1
                        placement_index = 0
                        placement_ships[:] = [Ship(ship.name, [[0, i] for i in range(ship.length)]) for ship in ships]
                        player1.ships = []
                        player2.ships = []
                        player1.moves = []
                        player2.moves = []
                        sunk_ships_p1.clear()
                        sunk_ships_p2.clear()
                        cursor_row, cursor_col = 0, 0
            elif event.type == pygame.KEYDOWN:
                if game_state == PLACEMENT:
                    ship = placement_ships[placement_index]
                    if event.key == pygame.K_UP:
                        move_ship(ship, -1, 0)
                    elif event.key == pygame.K_DOWN:
                        move_ship(ship, 1, 0)
                    elif event.key == pygame.K_LEFT:
                        move_ship(ship, 0, -1)
                    elif event.key == pygame.K_RIGHT:
                        move_ship(ship, 0, 1)
                    elif event.key == pygame.K_TAB:
                        placement_index = (placement_index + 1) % len(placement_ships)
                    elif event.key == pygame.K_r:
                        rotate_ship(ship)
                    elif event.key == pygame.K_RETURN:
                        # Confirm placement if valid and move to next ship
                        if is_valid_position(ship, placement_ships[:placement_index] + placement_ships[placement_index+1:]):
                            if placement_index == len(placement_ships) - 1:
                                # Save ships for player
                                if placement_player == 1:
                                    player1.ships = [Ship(s.name, [p[:] for p in s.positions]) for s in placement_ships]
                                    placement_player = 2
                                    placement_index = 0
                                    placement_ships = [Ship(ship.name, [[0, i] for i in range(ship.length)]) for ship in ships]
                                else:
                                    player2.ships = [Ship(s.name, [p[:] for p in s.positions]) for s in placement_ships]
                                    game_state = PLAY
                                    placement_index = 0
                                    placement_ships = []
                                    cursor_row, cursor_col = 0, 0
                            else:
                                placement_index += 1
                elif game_state == PLAY:
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
                        opponent = player2 if current_player == 1 else player1
                        opponent_ships = opponent.ships
                        sunk_ships = sunk_ships_p2 if current_player == 1 else sunk_ships_p1
                        if (cursor_row, cursor_col) not in current.moves:
                            current.moves.append((cursor_row, cursor_col))
                            print(f"{current.name} played: {(cursor_row, cursor_col)}")

                            played_pew = False
                            for idx, ship in enumerate(opponent_ships):
                                ship_tuples = [tuple(pos) for pos in ship.positions]
                                if idx not in sunk_ships and all(pos in current.moves for pos in ship_tuples):
                                    BOOM_SOUND.play()
                                    sunk_ships.add(idx)
                                    played_pew = True
                            if not played_pew:
                                for ship in opponent_ships:
                                    if (cursor_row, cursor_col) in [tuple(p) for p in ship.positions]:
                                        PEW_SOUND.play()
                                        break

                            current_player = 2 if current_player == 1 else 1  # Switch turn

        clock.tick(60)

main()
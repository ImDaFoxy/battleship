import pygame
import sys
import json
import pickle
import os

# Hallo

#-------- Save -------------
class SaveLoadSystem:
    def __init__(self, file_extension, save_folder):
        self.file_extension = file_extension
        self.save_folder = save_folder
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

    def save_data(self, data, name):
        with open(os.path.join(self.save_folder, name + self.file_extension), "wb") as data_file:
            pickle.dump(data, data_file)

    def load_data(self, name):
        with open(os.path.join(self.save_folder, name + self.file_extension), "rb") as data_file:
            data = pickle.load(data_file)
        return data

    def check_for_file(self, name):
        return os.path.exists(os.path.join(self.save_folder, name + self.file_extension))

    def load_game_data(self, files_to_load, default_data):
        variables = []
        for index, file in enumerate(files_to_load):
            if self.check_for_file(file):
                variables.append(self.load_data(file))
            else:
                variables.append(default_data[index])

        if len(variables) > 1:
            return tuple(variables)
        else:
            return variables[0]

    def save_game_data(self, data_to_save, file_names):
        for index, file in enumerate(data_to_save):
            self.save_data(file, file_names[index])

#=--Save--
SAVE_FOLDER = "./src/save_data"
SAVE_EXTENSION = ".save"
save_system = SaveLoadSystem(SAVE_EXTENSION, SAVE_FOLDER)

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
BG_COLOR = (0, 0, 0)
BORDER_COLOR = (255, 0, 0)
TEXT_COLOR = (255, 255, 255)
GRID_COLOR = (255, 204, 229)
RED_GRID_COLOR = (255, 0, 0)
ORANGE_GRID_COLOR = (255, 165, 0)
CURSOR_COLOR = (255, 255, 0)
BUTTON_COLOR = (0, 0, 120)
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

# ---------- Player Class ----------
class Player:
    def __init__(self, name):
        self.name = name
        self.moves = []
        self.ships = []
        self.sunk_ships = set()
        self.cursor_row = 0
        self.cursor_col = 0

    def reset(self):
        self.moves = []
        self.ships = []
        self.sunk_ships.clear()
        self.cursor_row = 0
        self.cursor_col = 0

player1 = Player("Player 1")
player2 = Player("Player 2")
current_player = 1  # 1 = player1, 2 = player2

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
def draw_grid_squares(player, ships, offset_x, current_time, moves, sunk_ships, cursor_pos=None):
    completed_ship_positions = set()
    partial_ship_positions = set()

    for idx, ship in enumerate(ships):
        ship_tuples = [tuple(pos) for pos in ship.positions]
        hits = [pos for pos in ship_tuples if pos in moves]
        if idx in sunk_ships and hits:
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
        elif (row, col) in moves:
            pygame.draw.rect(screen, GRID_COLOR, (x, y, GRID_SIZE, GRID_SIZE), 2)
            pygame.draw.line(screen, RED_GRID_COLOR, (x, y), (x + GRID_SIZE, y + GRID_SIZE), 3)
            pygame.draw.line(screen, RED_GRID_COLOR, (x + GRID_SIZE, y), (x, y + GRID_SIZE), 3)
        else:
            pygame.draw.rect(screen, GRID_COLOR, (x, y, GRID_SIZE, GRID_SIZE), 2)

    if cursor_pos and cursor_pos not in moves:
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

def get_game_state_data():
    # Prepare all necessary data for saving
    return {
        "player1": player1.__dict__,
        "player2": player2.__dict__,
        "current_player": current_player,
        "game_state": game_state,
        "placement_player": placement_player,
        "placement_index": placement_index,
        "placement_ships": [[ship.name, [p[:] for p in ship.positions]] for ship in placement_ships] if placement_ships else [],
        "cursor_row": cursor_row,
        "cursor_col": cursor_col
    }

def set_game_state_data(data):
    global player1, player2, current_player, game_state
    global placement_player, placement_index, placement_ships, cursor_row, cursor_col

    player1.__dict__.update(data["player1"])
    player2.__dict__.update(data["player2"])
    current_player = data["current_player"]
    game_state = data["game_state"]
    placement_player = data["placement_player"]
    placement_index = data["placement_index"]
    placement_ships.clear()
    for ship_data in data["placement_ships"]:
        placement_ships.append(Ship(ship_data[0], [p[:] for p in ship_data[1]]))
    cursor_row = data["cursor_row"]
    cursor_col = data["cursor_col"]

def draw_menu():
    screen.blit(bg_main_img, (0, 0))

    # Draw New Game Button
    button_w, button_h = 180, 40
    button_x = SCREEN_WIDTH // 2 - button_w // 2
    button_y = 365
    mouse_pos = pygame.mouse.get_pos()
    new_game_rect = pygame.Rect(button_x, button_y, button_w, button_h)
    hovering_new = new_game_rect.collidepoint(mouse_pos)
    color_new = BUTTON_HOVER_COLOR if hovering_new else BUTTON_COLOR
    pygame.draw.rect(screen, color_new, new_game_rect, border_radius=12)
    pygame.draw.rect(screen, (255, 255, 255), new_game_rect, 3, border_radius=12)
    btn_label_new = font.render("NEW GAME", True, BUTTON_TEXT_COLOR)
    btn_label_rect_new = btn_label_new.get_rect(center=new_game_rect.center)
    screen.blit(btn_label_new, btn_label_rect_new)

    # Draw Load Game Button
    load_game_rect = pygame.Rect(button_x, button_y + button_h + 10, button_w, button_h)
    hovering_load = load_game_rect.collidepoint(mouse_pos)
    color_load = BUTTON_HOVER_COLOR if hovering_load else BUTTON_COLOR
    pygame.draw.rect(screen, color_load, load_game_rect, border_radius=12)
    pygame.draw.rect(screen, (255, 255, 255), load_game_rect, 3, border_radius=12)
    btn_label_load = font.render("LOAD GAME", True, BUTTON_TEXT_COLOR)
    btn_label_rect_load = btn_label_load.get_rect(center=load_game_rect.center)
    screen.blit(btn_label_load, btn_label_rect_load)

    pygame.display.flip()
    return new_game_rect, load_game_rect

def draw_save_button():
    button_w, button_h = 120, 40
    button_x = SCREEN_WIDTH - button_w - 30
    button_y = 400
    mouse_pos = pygame.mouse.get_pos()
    save_rect = pygame.Rect(button_x, button_y, button_w, button_h)
    hovering = save_rect.collidepoint(mouse_pos)
    color = BUTTON_HOVER_COLOR if hovering else BUTTON_COLOR
    pygame.draw.rect(screen, color, save_rect, border_radius=8)
    pygame.draw.rect(screen, (255, 255, 255), save_rect, 2, border_radius=8)
    btn_label = font.render("SAVE", True, BUTTON_TEXT_COLOR)
    btn_label_rect = btn_label.get_rect(center=save_rect.center)
    screen.blit(btn_label, btn_label_rect)
    return save_rect

def draw_elements():
    screen.blit(background_img, (0, 0))
    current_time = pygame.time.get_ticks()

    label_y = 70
    save_rect = None
    if game_state == PLACEMENT:
        label = font.render(f"Player {placement_player} - Place Your Ships", True, TEXT_COLOR)
        draw_label_with_bg(label, label_y)
        offset_x = left_grid_x if placement_player == 1 else right_grid_x
        if placement_player == 1:
            draw_grid_squares(player1, player1.ships, offset_x, current_time, [], set())
        else:
            draw_grid_squares(player2, player2.ships, offset_x, current_time, [], set())
        draw_ship_placement(placement_ships, offset_x, placement_index)
        save_rect = draw_save_button()
    elif game_state == PLAY:
        # LEFT: Player 1's moves checked against Player 2's ships (Player 1's attack board)
        draw_grid_squares(
            player2, player2.ships, left_grid_x, current_time,
            player1.moves, player1.sunk_ships,
            (cursor_row, cursor_col) if current_player == 1 else None
        )
        # RIGHT: Player 2's moves checked against Player 1's ships (Player 2's attack board)
        draw_grid_squares(
            player1, player1.ships, right_grid_x, current_time,
            player2.moves, player2.sunk_ships,
            (cursor_row, cursor_col) if current_player == 2 else None
        )
        label = font.render(f"{'Player 1' if current_player == 1 else 'Player 2'}'s Turn", True, TEXT_COLOR)
        draw_label_with_bg(label, label_y)
        save_rect = draw_save_button()
    else:
        save_rect = None

    pygame.display.flip()
    return save_rect


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
            new_game_rect, load_game_rect = draw_menu()
        else:
            save_rect = draw_elements()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif game_state == MENU:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if new_game_rect.collidepoint(event.pos):
                        # Start new game
                        game_state = PLACEMENT
                        placement_player = 1
                        placement_index = 0
                        placement_ships[:] = [Ship(ship.name, [[0, i] for i in range(ship.length)]) for ship in ships]
                        player1.reset()
                        player2.reset()
                        cursor_row, cursor_col = 0, 0
                    elif load_game_rect.collidepoint(event.pos):
                        # Load game
                        if save_system.check_for_file("battleship_save"):
                            data = save_system.load_data("battleship_save")
                            set_game_state_data(data)
                        else:
                            # No save found, start new game
                            game_state = PLACEMENT
                            placement_player = 1
                            placement_index = 0
                            placement_ships[:] = [Ship(ship.name, [[0, i] for i in range(ship.length)]) for ship in ships]
                            player1.reset()
                            player2.reset()
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
                        if is_valid_position(ship, placement_ships[:placement_index] + placement_ships[placement_index+1:]):
                            if placement_index == len(placement_ships) - 1:
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
                    current = player1 if current_player == 1 else player2
                    opponent = player2 if current_player == 1 else player1
                    current.cursor_row = cursor_row
                    current.cursor_col = cursor_col

                    if event.key == pygame.K_UP:
                        cursor_row = max(0, cursor_row - 1)
                    elif event.key == pygame.K_DOWN:
                        cursor_row = min(PLAYING_ROWS - 1, cursor_row + 1)
                    elif event.key == pygame.K_LEFT:
                        cursor_col = max(0, cursor_col - 1)
                    elif event.key == pygame.K_RIGHT:
                        cursor_col = min(PLAYING_COLS - 1, cursor_col + 1)
                    elif event.key == pygame.K_RETURN:
                        if (cursor_row, cursor_col) not in current.moves:
                            current.moves.append((cursor_row, cursor_col))
                            print(f"{current.name} played: {(cursor_row, cursor_col)}")

                            hit = False
                            sunk = False
                            for idx, ship in enumerate(opponent.ships):
                                ship_tuples = [tuple(pos) for pos in ship.positions]
                                if (cursor_row, cursor_col) in ship_tuples:
                                    hit = True
                                    if idx not in current.sunk_ships and all(pos in current.moves for pos in ship_tuples):
                                        sunk = True
                                        current.sunk_ships.add(idx)
                                    break

                            if hit:
                                PEW_SOUND.play()
                            if sunk:
                                BOOM_SOUND.play()

                            current_player = 2 if current_player == 1 else 1
                            next_player = player1 if current_player == 1 else player2
                            cursor_row = next_player.cursor_row
                            cursor_col = next_player.cursor_col
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state in (PLACEMENT, PLAY) and save_rect and save_rect.collidepoint(event.pos):
                    # Save game
                    data = get_game_state_data()
                    save_system.save_data(data, "battleship_save")

        clock.tick(60)

main()
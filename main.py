import pygame
import sys
import time
import random

pygame.init()

WIDTH, HEIGHT = 800, 800
LINE_WIDTH = 5
SMALL_BOARD_SIZE = WIDTH // 3
SQUARE_SIZE = SMALL_BOARD_SIZE // 3

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_BLUE = (173, 216, 230)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Ultimate Tic Tac Toe')
pygame.font.init()
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 24)

class Button:
    def __init__(self, x, y, width, height, text, color=LIGHT_BLUE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover = False

    def draw(self):
        color = (min(self.color[0] + 20, 255), min(self.color[1] + 20, 255), min(self.color[2] + 20, 255)) if self.hover else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            if self.rect.collidepoint(event.pos):
                return True
        return False

def draw_menu():
    screen.fill(WHITE)
    title = large_font.render("Ultimate Tic Tac Toe", True, BLACK)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    
    buttons = [
        Button(WIDTH//4, 300, WIDTH//2, 60, "Player vs Player"),
        Button(WIDTH//4, 400, WIDTH//2, 60, "Player vs Easy AI"),
        Button(WIDTH//4, 500, WIDTH//2, 60, "Player vs Hard AI"),
        Button(WIDTH//4, 600, WIDTH//2, 60, "Exit")
    ]
    
    for button in buttons:
        button.draw()
    
    return buttons

def create_game_boards():
    small_boards = [[['' for _ in range(3)] for _ in range(3)] for _ in range(9)]
    big_board = [['' for _ in range(3)] for _ in range(3)]
    return small_boards, big_board

def draw_grid():
    # Draw thick lines for big board
    for i in range(1, 3):
        pygame.draw.line(screen, BLACK, (i * SMALL_BOARD_SIZE, 0), (i * SMALL_BOARD_SIZE, HEIGHT), LINE_WIDTH)
        pygame.draw.line(screen, BLACK, (0, i * SMALL_BOARD_SIZE), (WIDTH, i * SMALL_BOARD_SIZE), LINE_WIDTH)
    # Draw thin lines for small boards
    for i in range(1, 9):
        if i % 3 == 0:
            continue
        pygame.draw.line(screen, BLACK, (i * SQUARE_SIZE, 0), (i * SQUARE_SIZE, HEIGHT), 1)
        pygame.draw.line(screen, BLACK, (0, i * SQUARE_SIZE), (WIDTH, i * SQUARE_SIZE), 1)

def show_active_board(active_pos):
    if active_pos != (-1, -1):
        row, col = active_pos
        overlay = pygame.Surface((SMALL_BOARD_SIZE, SMALL_BOARD_SIZE), pygame.SRCALPHA)
        overlay.fill((0, 255, 0, 50))  # Semi-transparent green
        screen.blit(overlay, (col * SMALL_BOARD_SIZE, row * SMALL_BOARD_SIZE))

def draw_moves(small_boards, big_board):
    for i in range(3):
        for j in range(3):
            board_num = i * 3 + j
            if big_board[i][j] in ['X', 'O']:
                show_won_board(i, j, big_board[i][j])
            for x in range(3):
                for y in range(3):
                    if small_boards[board_num][x][y] == 'X':
                        draw_x(i, j, x, y)
                    elif small_boards[board_num][x][y] == 'O':
                        draw_o(i, j, x, y)

def get_random_move(small_boards, big_board, active_pos):
    possible_moves = get_possible_moves(small_boards, big_board, active_pos)
    return random.choice(possible_moves) if possible_moves else None

def get_best_move(small_boards, big_board, active_pos, current_player):
    possible_moves = get_possible_moves(small_boards, big_board, active_pos)
    best_score = float('-inf')
    best_move = None
    
    for move in possible_moves:
        board_row, board_col, cell_row, cell_col = move
        board_num = board_row * 3 + board_col
        
        small_boards[board_num][cell_row][cell_col] = current_player
        move_score = calculate_move_score(small_boards, big_board, (cell_row, cell_col), 
                                        'X' if current_player == 'O' else 'O', False, 3)
        small_boards[board_num][cell_row][cell_col] = ''
        
        if move_score > best_score:
            best_score = move_score
            best_move = move
    
    return best_move

def calculate_move_score(small_boards, big_board, active_pos, current_player, is_max_player, depth):
    if depth == 0:
        return evaluate_position(big_board)
    
    possible_moves = get_possible_moves(small_boards, big_board, active_pos)
    if not possible_moves:
        return 0
    
    if is_max_player:
        best_score = float('-inf')
        for move in possible_moves:
            board_row, board_col, cell_row, cell_col = move
            board_num = board_row * 3 + board_col
            small_boards[board_num][cell_row][cell_col] = current_player
            score = calculate_move_score(small_boards, big_board, (cell_row, cell_col), 
                                      'X' if current_player == 'O' else 'O', False, depth - 1)
            small_boards[board_num][cell_row][cell_col] = ''
            best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for move in possible_moves:
            board_row, board_col, cell_row, cell_col = move
            board_num = board_row * 3 + board_col
            small_boards[board_num][cell_row][cell_col] = current_player
            score = calculate_move_score(small_boards, big_board, (cell_row, cell_col), 
                                      'X' if current_player == 'O' else 'O', True, depth - 1)
            small_boards[board_num][cell_row][cell_col] = ''
            best_score = min(score, best_score)
        return best_score

def evaluate_position(board):
    score = 0
    for i in range(3):
        for j in range(3):
            if board[i][j] == 'X':
                score -= 1
            elif board[i][j] == 'O':
                score += 1
    return score

def show_game_over(winner, buttons=None):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((128, 128, 128, 180))
    screen.blit(overlay, (0,0))
    
    if winner in ['X', 'O']:
        msg = f"Player {winner} Wins!"
    else:
        msg = "It's a Draw!"
    
    text = large_font.render(msg, True, BLACK)
    text_pos = text.get_rect(center=(WIDTH/2, HEIGHT/2 - 50))
    screen.blit(text, text_pos)
    
    if buttons:
        for btn in buttons:
            btn.draw()

def get_possible_moves(small_boards, big_board, active_pos):
    moves = []
    if active_pos == (-1, -1):
        for i in range(3):
            for j in range(3):
                board_num = i * 3 + j
                if big_board[i][j] == '':
                    for x in range(3):
                        for y in range(3):
                            if small_boards[board_num][x][y] == '':
                                moves.append((i, j, x, y))
    else:
        i, j = active_pos
        board_num = i * 3 + j
        if big_board[i][j] == '':
            for x in range(3):
                for y in range(3):
                    if small_boards[board_num][x][y] == '':
                        moves.append((i, j, x, y))
    return moves

def draw_x(board_i, board_j, x, y):
    start_x = board_j * SMALL_BOARD_SIZE + y * SQUARE_SIZE
    start_y = board_i * SMALL_BOARD_SIZE + x * SQUARE_SIZE
    pygame.draw.line(screen, RED, 
                    (start_x + SQUARE_SIZE//4, start_y + SQUARE_SIZE//4),
                    (start_x + 3*SQUARE_SIZE//4, start_y + 3*SQUARE_SIZE//4), LINE_WIDTH)
    pygame.draw.line(screen, RED,
                    (start_x + 3*SQUARE_SIZE//4, start_y + SQUARE_SIZE//4),
                    (start_x + SQUARE_SIZE//4, start_y + 3*SQUARE_SIZE//4), LINE_WIDTH)

def draw_o(board_i, board_j, x, y):
    center_x = board_j * SMALL_BOARD_SIZE + y * SQUARE_SIZE + SQUARE_SIZE//2
    center_y = board_i * SMALL_BOARD_SIZE + x * SQUARE_SIZE + SQUARE_SIZE//2
    pygame.draw.circle(screen, BLUE, (center_x, center_y), SQUARE_SIZE//3, LINE_WIDTH)

def show_won_board(i, j, winner):
    color = RED if winner == 'X' else BLUE
    start_x = j * SMALL_BOARD_SIZE
    start_y = i * SMALL_BOARD_SIZE
    s = pygame.Surface((SMALL_BOARD_SIZE, SMALL_BOARD_SIZE), pygame.SRCALPHA)
    s.fill((color[0], color[1], color[2], 128))
    screen.blit(s, (start_x, start_y))

def make_move(boards, main_board, move, player):
    board_row, board_col, cell_row, cell_col = move
    board_num = board_row * 3 + board_col
    boards[board_num][cell_row][cell_col] = player
    
    if check_win(boards[board_num], player):
        main_board[board_row][board_col] = player
    elif check_full(boards[board_num]):
        main_board[board_row][board_col] = 'D'
    
    # Return the next board position
    return (cell_row, cell_col)

def check_win(board, player):
    # Check rows
    for row in board:
        if all(cell == player for cell in row):
            return True
    
    # Check columns
    for col in range(3):
        if all(board[row][col] == player for row in range(3)):
            return True
    
    # Check diagonals
    if all(board[i][i] == player for i in range(3)):
        return True
    if all(board[i][2-i] == player for i in range(3)):
        return True
    
    return False

def check_full(board):
    return all(cell != '' for row in board for cell in row)

def check_game_over(board):
    # Check if someone won
    for player in ['X', 'O']:
        if check_win(board, player):
            return True
    
    # Check if it's a draw (all cells filled)
    return check_full(board)

def main():
    game_state = "menu"
    game_mode = None
    restart_button = Button(WIDTH//4, HEIGHT//2 + 50, WIDTH//2, 60, "Play Again")
    menu_button = Button(WIDTH//4, HEIGHT//2 + 130, WIDTH//2, 60, "Main Menu")
    buttons = []
    
    while True:
        if game_state == "menu":
            screen.fill(WHITE)
            title = large_font.render("Ultimate Tic Tac Toe", True, BLACK)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
            
            # Create menu buttons if they don't exist
            if not buttons:
                buttons = [
                    Button(WIDTH//4, 300, WIDTH//2, 60, "Player vs Player"),
                    Button(WIDTH//4, 400, WIDTH//2, 60, "Player vs Easy AI"),
                    Button(WIDTH//4, 500, WIDTH//2, 60, "Player vs Hard AI"),
                    Button(WIDTH//4, 600, WIDTH//2, 60, "Exit")
                ]
            
            # Draw all buttons
            for button in buttons:
                button.draw()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Update button hover states
                mouse_pos = pygame.mouse.get_pos()
                for button in buttons:
                    if button.rect.collidepoint(mouse_pos):
                        button.hover = True
                    else:
                        button.hover = False
                
                # Handle button clicks
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for i, button in enumerate(buttons):
                        if button.rect.collidepoint(event.pos):
                            if i == 3:  # Exit button
                                pygame.quit()
                                sys.exit()
                            else:
                                game_mode = ["pvp", "easy_ai", "hard_ai"][i]
                                game_state = "playing"
                                boards, main_board = create_game_boards()
                                player = 'X'
                                current_board = (-1, -1)
                                game_over = False
                                last_move_time = time.time()
                                buttons = []  # Clear menu buttons
        
        elif game_state == "playing":
            screen.fill(WHITE)
            draw_grid()
            show_active_board(current_board)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN and not game_over and time.time() - last_move_time >= 0.5:
                    if player == 'X' or game_mode == "pvp":
                        mouseX, mouseY = event.pos
                        row = mouseY // SQUARE_SIZE
                        col = mouseX // SQUARE_SIZE
                        main_row, main_col = row // 3, col // 3
                        sub_row, sub_col = row % 3, col % 3
                        
                        valid_moves = get_possible_moves(boards, main_board, current_board)
                        if (main_row, main_col, sub_row, sub_col) in valid_moves:
                            # Update current_board based on the move
                            current_board = make_move(boards, main_board, (main_row, main_col, sub_row, sub_col), player)
                            last_move_time = time.time()
                            
                            # If the next board is already won or full, allow play anywhere
                            if main_board[current_board[0]][current_board[1]] != '':
                                current_board = (-1, -1)
                            
                            if check_game_over(main_board):
                                game_over = True
                                game_state = "game_over"
                            else:
                                player = 'O' if player == 'X' else 'X'
            
            if not game_over and player == 'O' and game_mode != "pvp":
                if time.time() - last_move_time >= 0.5:
                    ai_func = get_best_move if game_mode == "hard_ai" else get_random_move
                    move = ai_func(boards, main_board, current_board, player)
                    
                    if move:
                        # Update current_board for AI moves too
                        current_board = make_move(boards, main_board, move, player)
                        last_move_time = time.time()
                        
                        # If the next board is already won or full, allow play anywhere
                        if main_board[current_board[0]][current_board[1]] != '':
                            current_board = (-1, -1)
                        
                        if check_game_over(main_board):
                            game_over = True
                            game_state = "game_over"
                        else:
                            player = 'X'
            
            draw_moves(boards, main_board)
            
        elif game_state == "game_over":
            draw_moves(boards, main_board)
            show_game_over(player, [restart_button, menu_button])
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if restart_button.handle_event(event):
                    game_state = "playing"
                    boards, main_board = create_game_boards()
                    player = 'X'
                    current_board = (-1, -1)
                    game_over = False
                    last_move_time = time.time()
                
                elif menu_button.handle_event(event):
                    game_state = "menu"
        
        pygame.display.update()

if __name__ == "__main__":
    main()

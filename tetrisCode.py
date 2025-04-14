import pygame
import random
import sys

pygame.init()
pygame.display.set_caption("Tetris Ni Jeff")

WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 720
COLUMNS, ROWS = 10, 17
GRID_SIZE = 30
BOARD_WIDTH = COLUMNS * GRID_SIZE
BOARD_HEIGHT = ROWS * GRID_SIZE
BOARD1_X, BOARD1_Y = 100, 150
BOARD2_X, BOARD2_Y = 600, 150
PREVIEW_SIZE = 120

BG_COLOR = (20, 20, 20)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BORDER_COLOR = (200, 200, 200)
BUTTON_COLOR = (50, 150, 50)
BUTTON_HOVER = (70, 170, 70)
COLORS = [
    (0, 255, 255), (0, 0, 255), (255, 165, 0),
    (255, 255, 0), (0, 255, 0), (128, 0, 128), (255, 0, 0)
]

SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1, 1], [0, 1, 0]],
    [[1, 1], [1, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]]
]

def create_board():
    return [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]

def draw_board(screen, board, offset_x, offset_y):
    pygame.draw.rect(screen, BORDER_COLOR, (offset_x, offset_y, BOARD_WIDTH, BOARD_HEIGHT), 2)
    for y in range(ROWS):
        for x in range(COLUMNS):
            if board[y][x] != BLACK:
                rect = pygame.Rect(offset_x + x * GRID_SIZE, offset_y + y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(screen, board[y][x], rect)
                pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

def draw_preview(screen, piece, x, y):
    pygame.draw.rect(screen, BORDER_COLOR, (x, y, PREVIEW_SIZE, PREVIEW_SIZE), 2)
    shape = piece.shape
    piece_width = len(shape[0])
    piece_height = len(shape)
    offset_x = x + (PREVIEW_SIZE - piece_width * GRID_SIZE) // 2
    offset_y = y + (PREVIEW_SIZE - piece_height * GRID_SIZE) // 2
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                rect = pygame.Rect(offset_x + j * GRID_SIZE, offset_y + i * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(screen, piece.color, rect)
                pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

class Tetrimino:
    def __init__(self, x, board):
        self.shape = random.choice(SHAPES)
        self.color = random.choice(COLORS)
        self.x = x
        self.y = 0
        self.board = board

    def move(self, dx):
        if self.valid_move(self.x + dx, self.y):
            self.x += dx

    def rotate(self):
        rotated = [list(row) for row in zip(*self.shape[::-1])]
        if self.valid_move(self.x, self.y, rotated):
            self.shape = rotated

    def fall(self):
        if self.valid_move(self.x, self.y + 1):
            self.y += 1
        else:
            self.lock()
            return True
        return False

    def drop(self):
        while self.valid_move(self.x, self.y + 1):
            self.y += 1
        self.lock()
        return True

    def valid_move(self, x, y, shape=None):
        if shape is None:
            shape = self.shape
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    if x + j < 0 or x + j >= COLUMNS or y + i >= ROWS:
                        return False
                    if y + i >= 0 and self.board[y + i][x + j] != BLACK:
                        return False
        return True

    def lock(self):
        for i, row in enumerate(self.shape):
            for j, cell in enumerate(row):
                if cell and self.y + i >= 0:
                    self.board[self.y + i][self.x + j] = self.color

    def draw(self, screen, offset_x, offset_y):
        for i, row in enumerate(self.shape):
            for j, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(offset_x + (self.x + j) * GRID_SIZE,
                                       offset_y + (self.y + i) * GRID_SIZE,
                                       GRID_SIZE, GRID_SIZE)
                    pygame.draw.rect(screen, self.color, rect)
                    pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

def clear_lines(board):
    full_rows = [y for y in range(ROWS) if all(board[y][x] != BLACK for x in range(COLUMNS))]
    for row in full_rows:
        del board[row]
        board.insert(0, [BLACK for _ in range(COLUMNS)])
    return len(full_rows)

def game_over(board):
    return any(board[0][x] != BLACK for x in range(COLUMNS))

def run_game(screen, clock, font):
    board1 = create_board()
    board2 = create_board()
    piece1 = Tetrimino(3, board1)
    piece2 = Tetrimino(3, board2)
    next_piece1 = Tetrimino(3, board1)
    next_piece2 = Tetrimino(3, board2)
    
    score1, score2 = 0, 0
    fall_time1 = fall_time2 = 0
    normal_speed = 250
    accelerated_speed = 40

    running = True
    while running:
        screen.fill(BG_COLOR)
        dt = clock.tick(30)
        fall_time1 += dt
        fall_time2 += dt
        
        keys = pygame.key.get_pressed()
        speed1 = accelerated_speed if keys[pygame.K_s] else normal_speed
        speed2 = accelerated_speed if keys[pygame.K_DOWN] else normal_speed

        if fall_time1 > speed1:
            if piece1.fall():
                score1 += clear_lines(board1)
                if game_over(board1):
                    running = False
                else:
                    piece1 = next_piece1
                    next_piece1 = Tetrimino(3, board1)
            fall_time1 = 0

        if fall_time2 > speed2:
            if piece2.fall():
                score2 += clear_lines(board2)
                if game_over(board2):
                    running = False
                else:
                    piece2 = next_piece2
                    next_piece2 = Tetrimino(3, board2)
            fall_time2 = 0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    piece1.move(-1)
                elif event.key == pygame.K_d:
                    piece1.move(1)
                elif event.key == pygame.K_w:
                    piece1.rotate()
                elif event.key == pygame.K_LEFT:
                    piece2.move(-1)
                elif event.key == pygame.K_RIGHT:
                    piece2.move(1)
                elif event.key == pygame.K_UP:
                    piece2.rotate()
        
        title_text = font.render("2-Player Tetris", True, WHITE)
        screen.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, 20))
        title_text = font.render("By Edjay's and his Friend", True, WHITE)
        screen.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, 50))
        
        draw_board(screen, board1, BOARD1_X, BOARD1_Y)
        piece1.draw(screen, BOARD1_X, BOARD1_Y)
        preview1_x = BOARD1_X + (BOARD_WIDTH - PREVIEW_SIZE) // 2
        preview1_y = BOARD1_Y - PREVIEW_SIZE - 20
        draw_preview(screen, next_piece1, preview1_x, preview1_y)
        score_text1 = font.render(f"P1: {score1}", True, WHITE)
        score1_x = BOARD1_X + (BOARD_WIDTH - score_text1.get_width()) // 2
        score1_y = BOARD1_Y + BOARD_HEIGHT + 20
        screen.blit(score_text1, (score1_x, score1_y))
        
        draw_board(screen, board2, BOARD2_X, BOARD2_Y)
        piece2.draw(screen, BOARD2_X, BOARD2_Y)
        preview2_x = BOARD2_X + (BOARD_WIDTH - PREVIEW_SIZE) // 2
        preview2_y = BOARD2_Y - PREVIEW_SIZE - 20
        draw_preview(screen, next_piece2, preview2_x, preview2_y)
        score_text2 = font.render(f"P2: {score2}", True, WHITE)
        score2_x = BOARD2_X + (BOARD_WIDTH - score_text2.get_width()) // 2
        score2_y = BOARD2_Y + BOARD_HEIGHT + 20
        screen.blit(score_text2, (score2_x, score2_y))
        
        pygame.display.flip()
    
    return score1, score2

def display_game_over(screen, winner_text, score1, score2, font):
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    font_large = pygame.font.Font(None, 72)
    font_medium = pygame.font.Font(None, 48)
    font_small = pygame.font.Font(None, 36)
    
    game_over_text = font_large.render("GAME OVER", True, WHITE)
    winner_surface = font_medium.render(winner_text, True, WHITE)
    score_text = font_medium.render(f"P1: {score1}   P2: {score2}", True, WHITE)
    
    screen.blit(game_over_text, (WINDOW_WIDTH//2 - game_over_text.get_width()//2, WINDOW_HEIGHT//2 - 200))
    screen.blit(winner_surface, (WINDOW_WIDTH//2 - winner_surface.get_width()//2, WINDOW_HEIGHT//2 - 120))
    screen.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, WINDOW_HEIGHT//2 - 50))
    
    button_rect = pygame.Rect(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 50, 200, 60)
    button_color = BUTTON_COLOR
    pygame.draw.rect(screen, button_color, button_rect, border_radius=10)
    pygame.draw.rect(screen, BORDER_COLOR, button_rect, 3, border_radius=10)
    button_text = font_small.render("Play Again", True, WHITE)
    screen.blit(button_text, (button_rect.centerx - button_text.get_width()//2,
                                button_rect.centery - button_text.get_height()//2))
    
    quit_text = font_small.render("Press ESC to Quit", True, WHITE)
    screen.blit(quit_text, (WINDOW_WIDTH//2 - quit_text.get_width()//2, WINDOW_HEIGHT//2 + 130))
    
    pygame.display.flip()
    
    waiting = True
    play_again = False
    while waiting:
        mouse_pos = pygame.mouse.get_pos()
        if button_rect.collidepoint(mouse_pos):
            current_button = BUTTON_HOVER
        else:
            current_button = BUTTON_COLOR
        pygame.draw.rect(screen, current_button, button_rect, border_radius=10)
        pygame.draw.rect(screen, BORDER_COLOR, button_rect, 3, border_radius=10)
        screen.blit(button_text, (button_rect.centerx - button_text.get_width()//2,
                                    button_rect.centery - button_text.get_height()//2))
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
                play_again = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    play_again = True
                    waiting = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting = False
                    play_again = False
        pygame.time.delay(100)
    return play_again

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("2-Player Tetris")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    
    while True:
        score1, score2 = run_game(screen, clock, font)
        winner = "Player 1 Wins!" if score1 > score2 else "Player 2 Wins!" if score2 > score1 else "It's a Draw!"
        if not display_game_over(screen, winner, score1, score2, font):
            break

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

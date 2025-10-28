import pygame
import chess
from engine import ChessEngine
import time

engine = ChessEngine()

# Cấu hình hiển thị 
pygame.init()
BOARD_SIZE = 460
SIDEBAR_WIDTH = 240
WIDTH = BOARD_SIZE + SIDEBAR_WIDTH
HEIGHT = 460
SQ_SIZE = BOARD_SIZE // 8
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cờ vua 2 người")
clock = pygame.time.Clock()
TIMELIMIT = 3

# Màu sắc 
BROWN = (240, 217, 181)
WHITE = (181, 136, 99)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BG_COLOR = (30, 30, 30)
SIDEBAR_BG = (45, 45, 45)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER = (100, 160, 210)

# Font
font_large = pygame.font.SysFont(None, 32)
font_medium = pygame.font.SysFont(None, 24)
font_small = pygame.font.SysFont(None, 20)

# Load ảnh quân cờ 
pieces_img = {}
for color in ['w', 'b']:
    for piece in ['p', 'r', 'n', 'b', 'q', 'k']:
        img = pygame.image.load(f"images/{color}{piece}.png")
        img = pygame.transform.scale(img, (SQ_SIZE, SQ_SIZE))
        pieces_img[color + piece] = img

# Bàn cờ 
board = chess.Board()

# Thời gian
white_time = 0
black_time = 0
game_start_time = None

# Chọn màu người chơi 
button_white = pygame.Rect(WIDTH // 4 - 60, HEIGHT // 2 - 25, 120, 50)
button_black = pygame.Rect(3 * WIDTH // 4 - 60, HEIGHT // 2 - 25, 120, 50)

def draw_selection_screen():
    screen.fill(BG_COLOR)
    title = font_large.render("Choose Your Color", True, TEXT_COLOR)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 3)))
    
    pygame.draw.rect(screen, (255, 255, 255), button_white)
    pygame.draw.rect(screen, (50, 50, 50), button_black)
    pygame.draw.rect(screen, (200, 200, 200), button_black, 2)
    
    white_text = font_medium.render("Play White", True, (0, 0, 0))
    black_text = font_medium.render("Play Black", True, (255, 255, 255))
    screen.blit(white_text, white_text.get_rect(center=button_white.center))
    screen.blit(black_text, black_text.get_rect(center=button_black.center))
    pygame.display.flip()

player_color = None
flipped = False
choosing = True
while choosing:
    draw_selection_screen()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_white.collidepoint(event.pos):
                player_color = chess.WHITE
                flipped = False
                choosing = False
                game_start_time = time.time()
            elif button_black.collidepoint(event.pos):
                player_color = chess.BLACK
                flipped = True
                choosing = False
                game_start_time = time.time()

#  Hàm hỗ trợ
def get_square_under_mouse():
    mx, my = pygame.mouse.get_pos()
    if mx >= BOARD_SIZE:  # Click vào sidebar
        return None
    if flipped:
        mx = BOARD_SIZE - mx
        my = HEIGHT - my
    col, row = mx // SQ_SIZE, my // SQ_SIZE
    board_row = 7 - row
    board_col = col
    if 0 <= board_col < 8 and 0 <= board_row < 8:
        return chess.square(board_col, board_row)
    return None

def format_time(seconds):
    """Định dạng thời gian thành mm:ss"""
    mins = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{mins:02d}:{secs:02d}"

def draw_sidebar():
    """Vẽ thanh sidebar bên phải"""
    sidebar_rect = pygame.Rect(BOARD_SIZE, 0, SIDEBAR_WIDTH, HEIGHT)
    pygame.draw.rect(screen, SIDEBAR_BG, sidebar_rect)
    
    y_offset = 20
    
    # Hiển thị người chơi Trắng
    white_label = "Player" if player_color == chess.WHITE else "Computer"
    white_text = font_medium.render("White: " + white_label, True, TEXT_COLOR)
    screen.blit(white_text, (BOARD_SIZE + 20, y_offset))
    y_offset += 35
    
    # Thời gian Trắng
    white_time_text = font_small.render(f"Time: {format_time(white_time)}", True, TEXT_COLOR)
    screen.blit(white_time_text, (BOARD_SIZE + 20, y_offset))
    y_offset += 60
    
    # Đường phân cách
    pygame.draw.line(screen, GRAY, (BOARD_SIZE + 20, y_offset), (WIDTH - 20, y_offset), 2)
    y_offset += 20
    
    # Hiển thị người chơi Đen
    black_label = "Player" if player_color == chess.BLACK else "Computer"
    black_text = font_medium.render("Black: " + black_label, True, TEXT_COLOR)
    screen.blit(black_text, (BOARD_SIZE + 20, y_offset))
    y_offset += 35
    
    # Thời gian Đen
    black_time_text = font_small.render(f"Time: {format_time(black_time)}", True, TEXT_COLOR)
    screen.blit(black_time_text, (BOARD_SIZE + 20, y_offset))
    y_offset += 60
    
    # Đường phân cách
    pygame.draw.line(screen, GRAY, (BOARD_SIZE + 20, y_offset), (WIDTH - 20, y_offset), 2)
    y_offset += 30
    
    # Hiển thị lượt đi
    turn_text = "Turn: " + ("White" if board.turn == chess.WHITE else "Black")
    turn_surface = font_medium.render(turn_text, True, TEXT_COLOR)
    screen.blit(turn_surface, (BOARD_SIZE + 20, y_offset))
    y_offset += 40
    
    # Số nước đi
    move_count = font_small.render(f"Moves: {len(board.move_stack)}", True, TEXT_COLOR)
    screen.blit(move_count, (BOARD_SIZE + 20, y_offset))

# Vẽ bàn cờ 
def draw_board(selected_square=None):
    for r in range(8):
        for c in range(8):
            board_row = 7 - r if not flipped else r
            board_col = c if not flipped else 7 - c

            color = WHITE if (board_row + board_col) % 2 == 0 else BROWN
            rect = pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            pygame.draw.rect(screen, color, rect)

            piece = board.piece_at(chess.square(board_col, board_row))
            if piece:
                key = ('w' if piece.color == chess.WHITE else 'b') + piece.symbol().lower()
                screen.blit(pieces_img[key], rect)

    # Tô sáng ô được chọn
    if selected_square is not None:
        rank, file = chess.square_rank(selected_square), chess.square_file(selected_square)
        draw_rank = 7 - rank if not flipped else rank
        draw_file = file if not flipped else 7 - file
        pygame.draw.rect(screen, YELLOW,
                         (draw_file * SQ_SIZE, draw_rank * SQ_SIZE, SQ_SIZE, SQ_SIZE), 4)

    # Nước đi hợp lệ
    if selected_square is not None:
        for move in board.legal_moves:
            if move.from_square == selected_square:
                to = move.to_square
                tr = 7 - chess.square_rank(to) if not flipped else chess.square_rank(to)
                tc = chess.square_file(to) if not flipped else 7 - chess.square_file(to)
                center = (tc * SQ_SIZE + SQ_SIZE // 2, tr * SQ_SIZE + SQ_SIZE // 2)
                pygame.draw.circle(screen, GRAY, center, 8)

    # Nước đi cuối
    if board.move_stack:
        last = board.move_stack[-1]
        for sq in [last.from_square, last.to_square]:
            sr = 7 - chess.square_rank(sq) if not flipped else chess.square_rank(sq)
            sc = chess.square_file(sq) if not flipped else 7 - chess.square_file(sq)
            pygame.draw.rect(screen, GREEN,
                             (sc * SQ_SIZE, sr * SQ_SIZE, SQ_SIZE, SQ_SIZE), 3)

    # Chiếu hết
    if board.is_checkmate():
        king_sq = board.king(board.turn)
        if king_sq is not None:
            kr = 7 - chess.square_rank(king_sq) if not flipped else chess.square_rank(king_sq)
            kc = chess.square_file(king_sq) if not flipped else 7 - chess.square_file(king_sq)
            pygame.draw.rect(screen, RED,
                             (kc * SQ_SIZE, kr * SQ_SIZE, SQ_SIZE, SQ_SIZE), 4)
    return True

def draw_game_over_screen():
    """Vẽ màn hình kết thúc game"""
    # Vẽ overlay mờ
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # Xác định kết quả
    if board.is_checkmate():
        winner = "White" if board.turn == chess.BLACK else "Black"
        result_text = f"Checkmate! {winner} wins!"
        color = (255, 215, 0)  # Vàng gold
    elif board.is_stalemate():
        result_text = "Stalemate! Draw!"
        color = TEXT_COLOR
    elif board.is_insufficient_material():
        result_text = "Draw! Insufficient material"
        color = TEXT_COLOR
    else:
        result_text = "Game Over!"
        color = TEXT_COLOR
    
    # Hiển thị kết quả
    result_surface = font_large.render(result_text, True, color)
    result_rect = result_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
    screen.blit(result_surface, result_rect)
    
    # Hiển thị thời gian
    time_info = font_medium.render(f"White: {format_time(white_time)} | Black: {format_time(black_time)}", 
                                   True, TEXT_COLOR)
    time_rect = time_info.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10))
    screen.blit(time_info, time_rect)
    
    # Nút chơi lại
    play_again_button = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 + 40, 160, 50)
    mouse_pos = pygame.mouse.get_pos()
    button_col = BUTTON_HOVER if play_again_button.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, button_col, play_again_button, border_radius=5)
    
    play_text = font_medium.render("Play Again", True, TEXT_COLOR)
    play_rect = play_text.get_rect(center=play_again_button.center)
    screen.blit(play_text, play_rect)
    
    pygame.display.flip()
    return play_again_button

# Game loop
selected_square = None
running = True
engine_thinking = False
game_over = False
last_turn = board.turn
turn_start_time = time.time()

while running:
    current_time = time.time()
    
    # Cập nhật thời gian
    if not game_over and game_start_time:
        if board.turn != last_turn:
            last_turn = board.turn
            turn_start_time = current_time
        
        if board.turn == chess.WHITE:
            white_time = current_time - game_start_time
        else:
            black_time = current_time - game_start_time
    
    # Kiểm tra kết thúc game
    if board.is_game_over() and not game_over:
        game_over = True
    
    if not game_over:
        draw_board(selected_square)
        draw_sidebar()
        pygame.display.flip()
        clock.tick(60)

        if board.turn == player_color:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    sq = get_square_under_mouse()
                    if sq is None:
                        continue

                    piece = board.piece_at(sq)
                    if selected_square is None:
                        if piece and piece.color == board.turn:
                            selected_square = sq
                    else:
                        move = chess.Move(selected_square, sq)

                        # Phong cấp
                        from_piece = board.piece_at(selected_square)
                        if (from_piece is not None and
                            from_piece.piece_type == chess.PAWN and
                            (chess.square_rank(sq) == 7 or chess.square_rank(sq) == 0)):
                            move = chess.Move(selected_square, sq, promotion=chess.QUEEN)

                        if move in board.legal_moves:
                            board.push(move)

                        selected_square = None
        else:
            if not engine_thinking:
                engine_thinking = True
                move = engine.run(board, time_limit=TIMELIMIT)
                if move is not None and move in board.legal_moves:
                    board.push(move)
                    selected_square = move.from_square
                engine_thinking = False
            
            # Xử lý sự kiện quit khi máy đang suy nghĩ
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
    else:
        # Màn hình kết thúc
        draw_board(selected_square)
        draw_sidebar()
        play_again_button = draw_game_over_screen()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_button.collidepoint(event.pos):
                    # Reset game
                    board.reset()
                    selected_square = None
                    game_over = False
                    white_time = 0
                    black_time = 0
                    game_start_time = time.time()
                    last_turn = board.turn
                    turn_start_time = time.time()

pygame.quit()
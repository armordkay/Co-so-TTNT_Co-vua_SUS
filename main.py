import pygame
import chess

# Cấu hình hiển thị 
pygame.init()
WIDTH, HEIGHT = 460, 460
SQ_SIZE = WIDTH // 8
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cờ vua 2 người")
clock = pygame.time.Clock()

# Màu sắc 
BROWN = (240, 217, 181)
WHITE = (181, 136, 99)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BG_COLOR = (30, 30, 30)

# Load ảnh quân cờ 
pieces_img = {}
for color in ['w', 'b']:
    for piece in ['p', 'r', 'n', 'b', 'q', 'k']:
        img = pygame.image.load(f"images/{color}{piece}.png")
        img = pygame.transform.scale(img, (SQ_SIZE, SQ_SIZE))
        pieces_img[color + piece] = img

# Bàn cờ 
board = chess.Board()

# Chọn màu người chơi 
font = pygame.font.SysFont(None, 28)
button_white = pygame.Rect(WIDTH // 4 - 60, HEIGHT // 2 - 25, 120, 50)
button_black = pygame.Rect(3 * WIDTH // 4 - 60, HEIGHT // 2 - 25, 120, 50)

def draw_selection_screen():
    screen.fill(BG_COLOR)
    pygame.draw.rect(screen, (255, 255, 255), button_white)
    pygame.draw.rect(screen, (0, 0, 0), button_black)
    white_text = font.render("Play White", True, (0, 0, 0))
    black_text = font.render("Play Black", True, (255, 255, 255))
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
            elif button_black.collidepoint(event.pos):
                player_color = chess.BLACK
                flipped = True
                choosing = False

# Lật bàn cờ theo góc nhìn 

#  Hàm hỗ trợ
def get_square_under_mouse():
    mx, my = pygame.mouse.get_pos()
    # Nếu lật bàn: đảo lại vị trí chuột
    if flipped:
        mx = WIDTH - mx
        my = HEIGHT - my
    col, row = mx // SQ_SIZE, my // SQ_SIZE
    board_row = 7 - row
    board_col = col
    if 0 <= board_col < 8 and 0 <= board_row < 8:
        return chess.square(board_col, board_row)
    return None

# Vẽ bàn cờ 
def draw_board(selected_square=None):
    for r in range(8):
        for c in range(8):
            # Tính vị trí thực tế trên bàn cờ logic
            board_row = 7 - r if not flipped else r
            board_col = c if not flipped else 7 - c

            # Màu ô dựa trên tọa độ thật để khi lật vẫn đúng màu
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

# Game loop
selected_square = None
running = True
while running:
    draw_board(selected_square)
    pygame.display.flip()
    clock.tick(60)

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

pygame.quit()

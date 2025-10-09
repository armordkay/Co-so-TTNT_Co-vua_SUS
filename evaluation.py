import chess
from piece_values import PieceSquareTables as pst

class Evaluation:
    PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING = 0, 1, 2, 3, 4, 5
    WHITE, BLACK = 0, 1

    WHITE_PAWN   = 2 * PAWN   + WHITE
    BLACK_PAWN   = 2 * PAWN   + BLACK
    WHITE_KNIGHT = 2 * KNIGHT + WHITE
    BLACK_KNIGHT = 2 * KNIGHT + BLACK
    WHITE_BISHOP = 2 * BISHOP + WHITE
    BLACK_BISHOP = 2 * BISHOP + BLACK
    WHITE_ROOK   = 2 * ROOK   + WHITE
    BLACK_ROOK   = 2 * ROOK   + BLACK
    WHITE_QUEEN  = 2 * QUEEN  + WHITE
    BLACK_QUEEN  = 2 * QUEEN  + BLACK
    WHITE_KING   = 2 * KING   + WHITE
    BLACK_KING   = 2 * KING   + BLACK
    EMPTY        = BLACK_KING + 1

    mg_value = [82, 337, 365, 477, 1025, 0]
    eg_value = [94, 281, 297, 512, 936, 0]

    mg_pst_tables = [pst.mg_pawn, pst.mg_knight, pst.mg_bishop, pst.mg_rook, pst.mg_queen, pst.mg_king]
    eg_pst_tables = [pst.eg_pawn, pst.eg_knight, pst.eg_bishop, pst.eg_rook, pst.eg_queen, pst.eg_king]

    gamephaseInc = [0, 0, 1, 1, 1, 1, 2, 2, 4, 4, 0, 0]

    mg_table = [[0] * 64 for _ in range(12)]
    eg_table = [[0] * 64 for _ in range(12)] 

    def __init__(self):
        self.pst = pst()

        def FLIP(sq):
            return sq ^ 56
        
        pc = self.WHITE_PAWN
        for p in range(self.PAWN, self.KING + 1):
            for sq in range(64):
                self.mg_table[pc][sq] = self.mg_value[p] + self.mg_pst_tables[p][sq]
                self.eg_table[pc][sq] = self.eg_value[p] + self.eg_pst_tables[p][sq]
                self.mg_table[pc + 1][sq] = self.mg_value[p] + self.mg_pst_tables[p][FLIP(sq)]
                self.eg_table[pc + 1][sq] = self.eg_value[p] + self.eg_pst_tables[p][FLIP(sq)]
            pc += 2

    def evaluate(self, board: chess.Board) -> int:
        if board.is_checkmate():
            return -100000 if board.turn else 100000
        if board.is_stalemate() or board.is_insufficient_material():
            return 0
        
        mg = [0, 0] 
        eg = [0, 0] 
        gamePhase = 0

        # Lặp qua tất cả các quân cờ trên bàn
        for sq, piece in board.piece_map().items():
            p = piece.piece_type - 1
            color = self.WHITE if piece.color else self.BLACK
            pc = 2 * p + color

            # Cộng dồn điểm MG và EG cho mỗi bên
            mg[color] += self.mg_table[pc][sq]
            eg[color] += self.eg_table[pc][sq]
            
            # Cập nhật game phase
            gamePhase += self.gamephaseInc[pc]

        # Tapered Eval
        side2move = self.WHITE if board.turn else self.BLACK
        other_side = self.BLACK if board.turn else self.WHITE

        mgScore = mg[side2move] - mg[other_side]
        egScore = eg[side2move] - eg[other_side]

        mgPhase = min(gamePhase, 24)
        egPhase = 24 - mgPhase

        final_score = (mgScore * mgPhase + egScore * egPhase) / 24
        
        return int(final_score)
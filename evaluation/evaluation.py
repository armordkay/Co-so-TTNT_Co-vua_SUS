import chess
from evaluation.piece_values import PieceSquareTables as PST

class EvaluationData:
    """Lưu trữ các thành phần điểm đánh giá cho một bên."""
    def __init__(self):
        self.material_score: int = 0
        self.mop_up_score: int = 0
        self.piece_square_score: int = 0
        self.pawn_score: int = 0
        self.pawn_shield_score: int = 0

    def sum(self) -> int:
        """Tính tổng tất cả các thành phần điểm."""
        return (self.material_score + self.mop_up_score + 
                self.piece_square_score + self.pawn_score + self.pawn_shield_score)

class MaterialInfo:
    """
    Lưu trữ thông tin về chất và cấu trúc bàn cờ cho một bên.
    """
    def __init__(self, material_score, num_pawns, num_majors, num_minors, 
                 num_bishops, num_queens, num_rooks, pawns, enemy_pawns, endgame_t):
        self.material_score = material_score
        self.num_pawns = num_pawns
        self.num_majors = num_majors
        self.num_minors = num_minors
        self.num_bishops = num_bishops
        self.num_queens = num_queens
        self.num_rooks = num_rooks
        self.pawns = pawns
        self.enemy_pawns = enemy_pawns
        self.endgame_t = endgame_t

class Evaluation:
    # --- Giá trị chất của quân cờ ---
    PAWN_VALUE = 100
    KNIGHT_VALUE = 300
    BISHOP_VALUE = 320
    ROOK_VALUE = 500
    QUEEN_VALUE = 900
    
    PIECE_VALUES = {
        chess.PAWN: PAWN_VALUE,
        chess.KNIGHT: KNIGHT_VALUE,
        chess.BISHOP: BISHOP_VALUE,
        chess.ROOK: ROOK_VALUE,
        chess.QUEEN: QUEEN_VALUE,
        chess.KING: 0 
    }
    
    # --- Các hằng số thưởng/phạt ---
    PASSED_PAWN_BONUSES = [0, 120, 80, 50, 30, 15, 15]
    ISOLATED_PAWN_PENALTY_BY_COUNT = [0, -10, -25, -50, -75, -75, -75, -75, -75]
    KING_PAWN_SHIELD_SCORES = [4, 7, 4, 3, 6, 3]

    ENDGAME_MATERIAL_START = ROOK_VALUE * 2 + BISHOP_VALUE + KNIGHT_VALUE
    
    def __init__(self):
        self.board: chess.Board = None
        self.white_eval: EvaluationData = None
        self.black_eval: EvaluationData = None

    def evaluate(self, board: chess.Board) -> int:
        self.board = board
        self.white_eval = EvaluationData()
        self.black_eval = EvaluationData()

        white_material = self.get_material_info(chess.WHITE)
        black_material = self.get_material_info(chess.BLACK)

        # 1. Điểm chất
        self.white_eval.material_score = white_material.material_score
        self.black_eval.material_score = black_material.material_score

        # 2. Điểm vị trí quân cờ (PST)
        self.white_eval.piece_square_score = self.evaluate_piece_square_tables(chess.WHITE, black_material.endgame_t)
        self.black_eval.piece_square_score = self.evaluate_piece_square_tables(chess.BLACK, white_material.endgame_t)

        # 3. Điểm "dọn dẹp" (Mop-up) trong tàn cuộc thắng thế
        self.white_eval.mop_up_score = self.mop_up_eval(chess.WHITE, white_material, black_material)
        self.black_eval.mop_up_score = self.mop_up_eval(chess.BLACK, black_material, white_material)

        # 4. Đánh giá cấu trúc tốt
        # self.white_eval.pawn_score = self.evaluate_pawns(chess.WHITE)
        # self.black_eval.pawn_score = self.evaluate_pawns(chess.BLACK)
        
        # 5. Điểm lá chắn tốt cho Vua
        # self.white_eval.pawn_shield_score = self.king_pawn_shield(chess.WHITE, black_material, self.black_eval.piece_square_score)
        # self.black_eval.pawn_shield_score = self.king_pawn_shield(chess.BLACK, white_material, self.white_eval.piece_square_score)
        
        # Tính toán tổng điểm và trả về theo góc nhìn
        eval_sum = self.white_eval.sum() - self.black_eval.sum()
        perspective = 1 if self.board.turn == chess.WHITE else -1
        
        return eval_sum * perspective
        # return eval_sum
    
    def get_material_info(self, color: chess.Color) -> MaterialInfo:
        num_pawns = len(self.board.pieces(chess.PAWN, color))
        num_knights = len(self.board.pieces(chess.KNIGHT, color))
        num_bishops = len(self.board.pieces(chess.BISHOP, color))
        num_rooks = len(self.board.pieces(chess.ROOK, color))
        num_queens = len(self.board.pieces(chess.QUEEN, color))

        pawns = self.board.pieces_mask(chess.PAWN, color)
        enemy_pawns = self.board.pieces_mask(chess.PAWN, not color)

        material_score = (
            num_pawns * self.PAWN_VALUE + num_knights * self.KNIGHT_VALUE +
            num_bishops * self.BISHOP_VALUE + num_rooks * self.ROOK_VALUE +
            num_queens * self.QUEEN_VALUE
        )
        
        num_majors = num_rooks + num_queens
        num_minors = num_bishops + num_knights

        QUEEN_ENDGAME_WEIGHT = 45
        ROOK_ENDGAME_WEIGHT = 20
        BISHOP_ENDGAME_WEIGHT = 10
        KNIGHT_ENDGAME_WEIGHT = 10

        ENDGAME_START_WEIGHT = (2 * ROOK_ENDGAME_WEIGHT + 2 * BISHOP_ENDGAME_WEIGHT + 
                                2 * KNIGHT_ENDGAME_WEIGHT + QUEEN_ENDGAME_WEIGHT)

        endgame_weight_sum = (
            num_queens * QUEEN_ENDGAME_WEIGHT + num_rooks * ROOK_ENDGAME_WEIGHT +
            num_bishops * BISHOP_ENDGAME_WEIGHT + num_knights * KNIGHT_ENDGAME_WEIGHT
        )
        
        endgame_t = 1 - min(1, endgame_weight_sum / ENDGAME_START_WEIGHT)

        return MaterialInfo(
            material_score, num_pawns, num_majors, num_minors, num_bishops, num_queens,
            num_rooks, pawns, enemy_pawns, endgame_t
        )
    
    def evaluate_piece_square_tables(self, color: chess.Color, endgame_t: float) -> int:
        score = 0
        pawn_early = 0
        pawn_end = 0
        king_early = 0
        king_end = 0

        for piece_type in self.PIECE_VALUES.keys():
            pieces = self.board.pieces(piece_type, color)
            for square in pieces:
                if color == chess.WHITE:
                    pst_index = square
                else:
                    pst_index = chess.square_mirror(square)
                
                if piece_type == chess.PAWN:
                    pawn_early += PST.pawn_start[pst_index]
                    pawn_end += PST.pawn_end[pst_index]
                elif piece_type == chess.KNIGHT:
                    score += PST.knight[pst_index]
                elif piece_type == chess.BISHOP:
                    score += PST.bishop[pst_index]
                elif piece_type == chess.ROOK:
                    score += PST.rook[pst_index]
                elif piece_type == chess.QUEEN:
                    score += PST.queen[pst_index]
                elif piece_type == chess.KING:
                    king_early += PST.king_start[pst_index]
                    king_end += PST.king_end[pst_index]

        score += int(pawn_early * (1 - endgame_t) + pawn_end * endgame_t)
        score += int(king_early * (1 - endgame_t) + king_end * endgame_t)
        
        return score
    
    def centre_manhattan_distance(self, square: chess.Square) -> int:
        file = chess.square_file(square)
        rank = chess.square_rank(square)

        dist_file_from_edge = min(file, 7 - file) 
        dist_rank_from_edge = min(rank, 7 - rank)

        return 3 - dist_file_from_edge + 3 - dist_rank_from_edge
    
    def mop_up_eval(self, color: chess.Color, my_material: MaterialInfo, enemy_material: MaterialInfo) -> int:
        """
        Tính điểm thưởng "dọn dẹp" khi có lợi thế lớn trong tàn cuộc.
        """
        if my_material.material_score > enemy_material.material_score + self.PAWN_VALUE * 2 and enemy_material.endgame_t > 0:
            mop_up_score = 0
            
            my_king_square = self.board.king(color)
            enemy_king_square = self.board.king(not color)

            dist_kings = chess.square_distance(my_king_square, enemy_king_square)
            mop_up_score += (14 - dist_kings) * 4

            dist_enemy_king_to_centre = self.centre_manhattan_distance(enemy_king_square)
            mop_up_score += dist_enemy_king_to_centre * 10
            
            return int(mop_up_score * enemy_material.endgame_t)
            
        return 0
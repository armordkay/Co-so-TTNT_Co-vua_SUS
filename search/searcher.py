import chess
from chess import polyglot
import time
from typing import Optional, Tuple
from search.transposition_table import TranspositionTable


class Searcher:
    """Iterative Deepening + Alpha-Beta + TT + Quiescence Search"""

    def __init__(self, evaluation, tt: TranspositionTable):
        self.evaluation = evaluation
        self.tt = tt
        self.nodes = 0
        self.start_time = 0
        self.time_limit = 0

    def is_time_up(self) -> bool:
        return (time.time() - self.start_time) >= self.time_limit

    def order_moves(self, board: chess.Board, tt_move: Optional[chess.Move]) -> list:
        """Ưu tiên TT move, sau đó capture move (MVV-LVA)."""
        moves = list(board.legal_moves)

        def move_score(move):
            score = 0
            if tt_move and move == tt_move:
                score += 100000  # TT move được ưu tiên nhất
            if board.is_capture(move):
                attacker = board.piece_at(move.from_square)
                victim = board.piece_at(move.to_square)
                if attacker and victim:
                    score += victim.piece_type * 10 - attacker.piece_type
            return score

        moves.sort(key=move_score, reverse=True)
        return moves

    def quiescence_search(self, board: chess.Board, alpha: int, beta: int, ply: int) -> int:
        """Mở rộng các nước động (captures, checks) để tránh horizon effect."""
        self.nodes += 1

        # Dừng nếu hết thời gian
        if (self.nodes & 2047) == 0 and self.is_time_up():
            raise TimeoutError

        zobrist_key = polyglot.zobrist_hash(board)

        # Dùng lại từ TT nếu có
        tt_val = self.tt.lookup_evaluation(0, ply, alpha, beta, zobrist_key)
        if tt_val != self.tt.LOOKUP_FAILED:
            return tt_val

        stand_pat = self.evaluation.evaluate(board)

        if stand_pat >= beta:
            self.tt.store_evaluation(0, ply, stand_pat, self.tt.LOWER_BOUND, None, zobrist_key)
            return beta
        if stand_pat > alpha:
            alpha = stand_pat

        for move in board.legal_moves:
            if not (board.is_capture(move) or board.gives_check(move)):
                continue

            board.push(move)
            score = -self.quiescence_search(board, -beta, -alpha, ply + 1)
            board.pop()

            if score >= beta:
                self.tt.store_evaluation(0, ply, score, self.tt.LOWER_BOUND, move, zobrist_key)
                return beta
            if score > alpha:
                alpha = score

        self.tt.store_evaluation(0, ply, alpha, self.tt.EXACT, None, zobrist_key)
        return alpha

    def alpha_beta(self, board: chess.Board, depth: int,
                   alpha: int, beta: int, ply: int) -> Tuple[int, Optional[chess.Move]]:
        """Alpha-Beta search với Transposition Table và QS ở đáy."""
        self.nodes += 1

        # Kiểm tra timeout
        if (self.nodes & 2047) == 0 and self.is_time_up():
            raise TimeoutError

        zobrist_key = polyglot.zobrist_hash(board)

        # TT lookup
        val = self.tt.lookup_evaluation(depth, ply, alpha, beta, zobrist_key)
        if val != self.tt.LOOKUP_FAILED:
            return val, self.tt.get_stored_move(zobrist_key)

        if board.is_checkmate():
            return -self.evaluation.CHECKMATE_SCORE + ply, None
        
        if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_draw():
            return 0, None
            
        # Leaf node
        if depth == 0:
            score = self.quiescence_search(board, alpha, beta, ply)
            self.tt.store_evaluation(0, ply, score, self.tt.EXACT, None, zobrist_key)
            return score, None
        

        best_move = None
        best_score = -999999
        alpha_orig = alpha

        tt_move = self.tt.get_stored_move(zobrist_key)
        moves = self.order_moves(board, tt_move)

        for move in moves:
            board.push(move)
            score, _ = self.alpha_beta(board, depth - 1, -beta, -alpha, ply + 1)
            score = -score
            board.pop()

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, score)
            if alpha >= beta:
                break  # Beta cutoff

        # Ghi kết quả vào TT
        if best_score <= alpha_orig:
            bound = self.tt.UPPER_BOUND
        elif best_score >= beta:
            bound = self.tt.LOWER_BOUND
        else:
            bound = self.tt.EXACT

        self.tt.store_evaluation(depth, ply, best_score, bound, best_move, zobrist_key)
        return best_score, best_move

    def ids(self, board: chess.Board, time_limit: float = 2.0) -> Optional[chess.Move]:
        """Tìm move tốt nhất bằng iterative deepening."""
        self.start_time = time.time()
        self.time_limit = time_limit
        self.nodes = 0

        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None

        best_move = legal_moves[0]
        last_completed_move = best_move

        for depth in range(1, 64):  # tối đa 64 ply
            try:
                score, move = self.alpha_beta(board, depth, -999999, 999999, 0)
                if move:
                    best_move = move
                    last_completed_move = move
                print(f"Depth {depth}: score {score}, move {move}, nodes {self.nodes}")
            except TimeoutError:
                print(f"Search stopped at depth {depth} due to timeout.")
                break

        return last_completed_move
import chess
from chess import polyglot
import time
from typing import Optional, Tuple
from search.transposition_table import TranspositionTable

class IterativeDeepeningSearch:
    def __init__(self, evaluation, tt: TranspositionTable):
        self.evaluation = evaluation
        self.tt = tt
        self.nodes = 0
        self.start_time = 0
        self.time_limit = 0

    def is_time_up(self) -> bool:
        return (time.time() - self.start_time) >= self.time_limit

    def order_moves(self, board: chess.Board, tt_move: Optional[chess.Move]) -> list:
        """Sắp xếp move: TT move trước, sau đó các capture."""
        moves = list(board.legal_moves)

        def move_score(m):
            score = 0
            if tt_move and m == tt_move:
                score += 100000
            if board.is_capture(m):
                attacker = board.piece_at(m.from_square)
                victim = board.piece_at(m.to_square)
                if attacker and victim:
                    score += victim.piece_type * 10 - attacker.piece_type
            return score

        moves.sort(key=move_score, reverse=True)
        return moves

    def alpha_beta(self, board: chess.Board, depth: int,
                   alpha: int, beta: int, ply: int) -> Tuple[int, Optional[chess.Move]]:
        self.nodes += 1
        if (self.nodes & 2047) == 0 and self.is_time_up():
            raise TimeoutError

        zobrist_key = polyglot.zobrist_hash(board)

        # Probe TT
        val = self.tt.lookup_evaluation(depth, ply, alpha, beta, zobrist_key)
        if val != self.tt.LOOKUP_FAILED:
            return val, self.tt.get_stored_move(zobrist_key)

        # Leaf node or game over
        if depth == 0 or board.is_game_over():
            score = self.evaluation.evaluate(board)
            self.tt.store_evaluation(depth, ply, score, self.tt.EXACT, None, zobrist_key)
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

        # Store result in TT
        if best_score <= alpha_orig:
            bound = self.tt.UPPER_BOUND
        elif best_score >= beta:
            bound = self.tt.LOWER_BOUND
        else:
            bound = self.tt.EXACT

        self.tt.store_evaluation(depth, ply, best_score, bound, best_move, zobrist_key)
        return best_score, best_move

    def search(self, board: chess.Board, time_limit: float = 2.0) -> Optional[chess.Move]:
        self.start_time = time.time()
        self.time_limit = time_limit
        self.nodes = 0

        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None

        best_move = legal_moves[0]
        last_completed_move = best_move

        for depth in range(1, 64):  # search up to 64 plies
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
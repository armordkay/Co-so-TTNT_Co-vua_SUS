import chess
from evaluation.evaluation import Evaluation
from search.searcher import Searcher, TranspositionTable

class ChessEngine:
    def __init__(self):
        self.evaluator = Evaluation()
        self.tt = TranspositionTable(size_mb=64)
        self.searcher = Searcher(self.evaluator, self.tt)
    
    def run(self, board: chess.Board, time_limit: float) -> chess.Move:
        """Tìm nước đi tốt nhất trong giới hạn thời gian."""
        best_move = self.searcher.ids(board.copy(), time_limit)
        return best_move
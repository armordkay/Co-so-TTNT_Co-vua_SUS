import chess
from evaluation import Evaluation

class ChessEngine:
    def __init__(self):
        self.evaluator = Evaluation()

    def alphabeta(self, board: chess.Board, depth, alpha, beta, maximizing):
        if depth == 0 or board.is_game_over():
            return self.evaluator.evaluate(board)
        if maximizing:
            value = -float('inf')
            for move in board.legal_moves:
                board.push(move)
                value = max(value, self.alphabeta(board, depth - 1, alpha, beta, False))
                board.pop()
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:
            value = float('inf')
            for move in board.legal_moves:
                board.push(move)
                value = min(value, self.alphabeta(board, depth - 1, alpha, beta, True))
                board.pop()
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value
    
    def find_best_move(self, board: chess.Board, depth, maximizing):
        best_move = None
        best_value = -float('inf') if board.turn == chess.WHITE else float('inf')
        for move in board.legal_moves:
            board.push(move)
            value = self.alphabeta(board, depth-1, -float('inf'), float('inf'), maximizing)
            board.pop()
            if board.turn == chess.WHITE and value > best_value:
                best_value = value
                best_move = move
            elif board.turn == chess.BLACK and value < best_value:
                best_value = value
                best_move = move
        return best_move
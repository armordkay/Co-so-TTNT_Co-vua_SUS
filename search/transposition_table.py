class Entry:
    def __init__(self):
        self.key = 0
        self.value = 0
        self.depth = 0
        self.bound = 0 
        self.move = None


class TranspositionTable:
    EXACT = 0
    LOWER_BOUND = 1
    UPPER_BOUND = 2
    LOOKUP_FAILED = -999999
    
    def __init__(self, size_mb: int = 32):
        entry_size = 32 
        self.size = (size_mb * 1024 * 1024) // entry_size
        self.entries = [Entry() for _ in range(self.size)]
        self.enabled = True
    
    def index(self, zobrist_key: int) -> int:
        return zobrist_key % self.size
    
    def lookup_evaluation(self, depth: int, ply_from_root: int, alpha: int, beta: int, zobrist_key: int) -> int:
        if not self.enabled:
            return self.LOOKUP_FAILED
        
        entry = self.entries[self.index(zobrist_key)]
        
        if entry.key != zobrist_key:
            return self.LOOKUP_FAILED
        
        if entry.depth < depth:
            return self.LOOKUP_FAILED
        
        corrected_score = entry.value
        if abs(corrected_score) > 90000:
            sign = 1 if corrected_score > 0 else -1
            corrected_score -= sign * ply_from_root
        
        if entry.bound == self.EXACT:
            return corrected_score
        elif entry.bound == self.LOWER_BOUND and corrected_score >= beta:
            return corrected_score
        elif entry.bound == self.UPPER_BOUND and corrected_score <= alpha:
            return corrected_score
        
        return self.LOOKUP_FAILED
    
    def store_evaluation(self, depth: int, ply_from_root: int, evaluation: int, 
                        bound: int, move, zobrist_key: int):
        if not self.enabled:
            return
        
        entry = self.entries[self.index(zobrist_key)]
        
        corrected_score = evaluation
        if abs(evaluation) > 90000:
            sign = 1 if evaluation > 0 else -1
            corrected_score += sign * ply_from_root
        
        entry.key = zobrist_key
        entry.value = corrected_score
        entry.depth = depth
        entry.bound = bound
        entry.move = move
    
    def get_stored_move(self, zobrist_key: int):
        entry = self.entries[self.index(zobrist_key)]
        if entry.key == zobrist_key:
            return entry.move
        return None
    
    def clear(self):
        self.entries = [Entry() for _ in range(self.size)]
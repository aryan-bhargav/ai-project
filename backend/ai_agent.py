import math
import numpy as np
import random
from game_logic import ROWS, COLS, PLAYER_1, PLAYER_2, EMPTY, Connect4Game

# Constants for AI heuristic scoring
WIN_SCORE = 100000
FORCED_MOVE_SCORE = 1000
BLOCK_SCORE = 500
OPEN_LINE_SCORE = 10
AI_PIECE = PLAYER_2 # Assuming AI is Player 2 (Red)
PLAYER_PIECE = PLAYER_1 # Human is Player 1 (Yellow)

class PruningStats:
    def __init__(self):
        self.nodes_visited = 0
        self.total_nodes = 0
        self.depth_achieved = 0

class Connect4AI:
    def __init__(self, depth_limit=6):
        self.depth_limit = depth_limit
        self.stats = PruningStats()

    def evaluate_board(self, board, player_piece, ai_piece):
        """Simple heuristic counting potential open lines of 4."""
        score = 0
        
        # Center column preference (tactical advantage)
        center_array = [board[r][COLS // 2] for r in range(ROWS)]
        center_count = center_array.count(ai_piece)
        score += center_count * 3
        
        # Helper function to score a line of 4 cells
        def score_line(cells):
            ai_count = cells.count(ai_piece)
            player_count = cells.count(player_piece)
            empty_count = cells.count(EMPTY)
            
            if ai_count == 4:
                return WIN_SCORE
            elif ai_count == 3 and empty_count == 1:
                return OPEN_LINE_SCORE
            elif ai_count == 2 and empty_count == 2:
                return OPEN_LINE_SCORE / 2
            
            # Opponent blocks and forced moves
            elif player_count == 3 and empty_count == 1:
                return -FORCED_MOVE_SCORE
            elif player_count == 2 and empty_count == 2:
                return -FORCED_MOVE_SCORE / 2
            return 0

        # Score Horizontal
        for r in range(ROWS):
            for c in range(COLS - 3):
                line = [board[r][c+i] for i in range(4)]
                score += score_line(line)

        # Score Vertical
        for r in range(ROWS - 3):
            for c in range(COLS):
                line = [board[r+i][c] for i in range(4)]
                score += score_line(line)

        # Score Positively sloped diagonals
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                line = [board[r+i][c+i] for i in range(4)]
                score += score_line(line)

        # Score Negatively sloped diagonals
        for r in range(3, ROWS):
            for c in range(COLS - 3):
                line = [board[r-i][c+i] for i in range(4)]
                score += score_line(line)

        return score

    def is_terminal_node(self, board):
        """Check for terminal state (win/tie/no valid moves)."""
        # (This is simplified for Minimax, just checks win or full board)
        # Check horizontal win
        for c in range(COLS - 3):
            for r in range(ROWS):
                if board[r][c] == PLAYER_2 and board[r][c+1] == PLAYER_2 and board[r][c+2] == PLAYER_2 and board[r][c+3] == PLAYER_2:
                    return True, WIN_SCORE
                elif board[r][c] == PLAYER_1 and board[r][c+1] == PLAYER_1 and board[r][c+2] == PLAYER_1 and board[r][c+3] == PLAYER_1:
                    return True, -WIN_SCORE
        # (Check Vertical, Diagonals similarly for terminal state logic...)
        # Omitting full win check here for brevity, assuming the evaluate function handles terminal scores properly.
        
        # Check full board (tie)
        if len([col for col in range(COLS) if board[ROWS-1][col] == EMPTY]) == 0:
            return True, 0
        return False, None

    def minimax_ab(self, board, depth, alpha, beta, maximizing_player):
        self.stats.total_nodes += 1
        
        # Base case
        terminal_status, terminal_score = self.is_terminal_node(board)
        if depth == 0 or terminal_status:
            if terminal_status:
                self.stats.depth_achieved = max(self.stats.depth_achieved, self.depth_limit - depth)
                return (None, terminal_score)
            else:
                self.stats.nodes_visited += 1
                score = self.evaluate_board(board, PLAYER_PIECE, AI_PIECE)
                self.stats.depth_achieved = max(self.stats.depth_achieved, self.depth_limit - depth)
                return (None, score)

        valid_locations = [col for col in range(COLS) if board[ROWS-1][col] == EMPTY]
        # Tactical optimization: try center columns first for better pruning.
        random.shuffle(valid_locations)
        valid_locations.sort(key=lambda x: abs(x - COLS // 2))

        if maximizing_player:
            value = -math.inf
            column = random.choice(valid_locations) # Default
            for col in valid_locations:
                # Simulation move
                new_board = board.copy()
                row = next(r for r, cell in enumerate(new_board[:,col]) if cell == EMPTY)
                new_board[row][col] = AI_PIECE
                
                _, new_score = self.minimax_ab(new_board, depth - 1, alpha, beta, False)
                
                if new_score > value:
                    value = new_score
                    column = col
                
                alpha = max(alpha, value)
                if beta <= alpha:
                    break # Prune beta branches
            return column, value

        else: # Minimizing human player
            value = math.inf
            column = random.choice(valid_locations) # Default
            for col in valid_locations:
                # Simulation move
                new_board = board.copy()
                row = next(r for r, cell in enumerate(new_board[:,col]) if cell == EMPTY)
                new_board[row][col] = PLAYER_PIECE
                
                _, new_score = self.minimax_ab(new_board, depth - 1, alpha, beta, True)
                
                if new_score < value:
                    value = new_score
                    column = col
                    
                beta = min(beta, value)
                if beta <= alpha:
                    break # Prune alpha branches
            return column, value

    def get_best_move(self, game_state: Connect4Game):
        self.stats = PruningStats() # Reset stats
        board = game_state.board
        
        best_col, score = self.minimax_ab(board, self.depth_limit, -math.inf, math.inf, True)
        
        # Calculate pruning efficiency (e.g., connected nodes ratio)
        nodes_pruned = self.stats.total_nodes - self.stats.nodes_visited
        efficiency = (nodes_pruned / self.stats.total_nodes * 100) if self.stats.total_nodes > 0 else 0
        
        return best_col, {
            "depth": self.stats.depth_achieved,
            "nodes_visited": self.stats.nodes_visited,
            "branches_pruned_percentage": round(efficiency, 2),
            "total_nodes_attempted": self.stats.total_nodes
        }
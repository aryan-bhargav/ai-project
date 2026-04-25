import numpy as np

ROWS = 6
COLS = 7
PLAYER_1 = 1
PLAYER_2 = 2
EMPTY = 0

class Connect4Game:
    def __init__(self):
        self.board = np.zeros((ROWS, COLS), dtype=int)
        self.current_player = PLAYER_1
        self.game_over = False
        self.winner = None

    def get_valid_locations(self):
        valid_locations = []
        for col in range(COLS):
            if self.is_valid_move(col):
                valid_locations.append(col)
        return valid_locations

    def is_valid_move(self, col):
        return self.board[ROWS - 1][col] == EMPTY

    def get_next_open_row(self, col):
        for r in range(ROWS):
            if self.board[r][col] == EMPTY:
                return r

    def drop_piece(self, col, player=None):
        if player is None:
            player = self.current_player
            
        row = self.get_next_open_row(col)
        if row is not None:
            self.board[row][col] = player
            self.check_game_over(row, col, player)
            
            if not self.game_over:
                self.current_player = PLAYER_1 if self.current_player == PLAYER_2 else PLAYER_2

    def check_game_over(self, row, col, player):
        # Check horizontal locations for win
        for c in range(COLS - 3):
            if all(self.board[row][c+i] == player for i in range(4)):
                self.game_over = True
                self.winner = player
                return

        # Check vertical locations for win
        for r in range(ROWS - 3):
            if all(self.board[r+i][col] == player for i in range(4)):
                self.game_over = True
                self.winner = player
                return

        # Check positively sloped diagonals
        for c in range(COLS - 3):
            for r in range(ROWS - 3):
                if all(self.board[r+i][c+i] == player for i in range(4)):
                    self.game_over = True
                    self.winner = player
                    return

        # Check negatively sloped diagonals
        for c in range(COLS - 3):
            for r in range(3, ROWS):
                if all(self.board[r-i][c+i] == player for i in range(4)):
                    self.game_over = True
                    self.winner = player
                    return

        # Check for tie
        if len(self.get_valid_locations()) == 0:
            self.game_over = True
            self.winner = 0 # Tie

    def get_board_as_list(self):
        """Converts NumPy board to a standard list of lists for JSON serializing."""
        return self.board.tolist()[::-1] # Reverse rows for display (row 0 at bottom)

    def reset(self):
        self.__init__()
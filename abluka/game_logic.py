class Board:
    def __init__(self):
        self.size = 7
        self.grid = [[None for _ in range(self.size)] for _ in range(self.size)]
        # Initialize starting positions
        self.black_pos = (0, self.size // 2)  # Black starts at top middle
        self.white_pos = (self.size - 1, self.size // 2)  # White starts at bottom middle
        self.grid[self.black_pos[0]][self.black_pos[1]] = 'B'
        self.grid[self.white_pos[0]][self.white_pos[1]] = 'W'
        self.obstacles = []  # List to keep track of obstacles

    def is_valid_move(self, piece, start_pos, end_pos):
        """Check if a move is valid for a given piece"""
        # Check if destination is within board bounds
        if not (0 <= end_pos[0] < self.size and 0 <= end_pos[1] < self.size):
            return False
        
        # Check if destination is empty
        if self.grid[end_pos[0]][end_pos[1]] is not None:
            return False
        
        # Check if move is one step in any direction (horizontal, vertical, diagonal)
        dx = abs(end_pos[0] - start_pos[0])
        dy = abs(end_pos[1] - start_pos[1])
        if dx > 1 or dy > 1:
            return False
        
        return True

    def get_valid_moves(self, piece):
        """Get all valid moves for a piece"""
        if piece == 'B':
            start_pos = self.black_pos
        else:
            start_pos = self.white_pos
        
        valid_moves = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue  # Skip the current position
                
                end_pos = (start_pos[0] + dx, start_pos[1] + dy)
                if self.is_valid_move(piece, start_pos, end_pos):
                    valid_moves.append(end_pos)
        
        return valid_moves

    def move_piece(self, piece, end_pos):
        """Move a piece to a new position"""
        if piece == 'B':
            start_pos = self.black_pos
            self.grid[start_pos[0]][start_pos[1]] = None
            self.grid[end_pos[0]][end_pos[1]] = 'B'
            self.black_pos = end_pos
        else:
            start_pos = self.white_pos
            self.grid[start_pos[0]][start_pos[1]] = None
            self.grid[end_pos[0]][end_pos[1]] = 'W'
            self.white_pos = end_pos
        
        return True

    def place_obstacle(self, pos):
        """Place an obstacle on the board"""
        if not (0 <= pos[0] < self.size and 0 <= pos[1] < self.size):
            return False
        
        if self.grid[pos[0]][pos[1]] is not None:
            return False
        
        self.grid[pos[0]][pos[1]] = 'R'  # 'R' for red obstacle
        self.obstacles.append(pos)
        return True

    def is_abluka(self, piece):
        """Check if a piece is blocked (abluka)"""
        return len(self.get_valid_moves(piece)) == 0

    def __str__(self):
        """String representation of the board"""
        result = "  " + " ".join(str(i) for i in range(self.size)) + "\n"
        for i, row in enumerate(self.grid):
            result += f"{i} "
            for cell in row:
                if cell is None:
                    result += ". "
                else:
                    result += f"{cell} "
            result += "\n"
        return result


class Game:
    def __init__(self):
        self.board = Board()
        self.current_player = 'B'  # Black starts
        self.game_over = False
        self.winner = None
        self.turn_count = 0

    def switch_player(self):
        """Switch the current player"""
        self.current_player = 'W' if self.current_player == 'B' else 'B'

    def make_move(self, move_pos, obstacle_pos):
        """Make a complete move: move piece and place obstacle"""
        # First move the piece
        if not self.board.move_piece(self.current_player, move_pos):
            return False
        
        # Then place an obstacle
        if not self.board.place_obstacle(obstacle_pos):
            # If obstacle placement fails, roll back the piece movement
            # (This is a simplified version, in a real game you might want
            # more sophisticated error handling)
            return False
        
        self.turn_count += 1
        
        # Check if the opponent is in abluka after this move
        opponent = 'W' if self.current_player == 'B' else 'B'
        if self.board.is_abluka(opponent):
            self.game_over = True
            self.winner = self.current_player
            return True
        
        # Switch to the next player
        self.switch_player()
        
        # Check if the current player (after switching) is in abluka
        if self.board.is_abluka(self.current_player):
            self.game_over = True
            self.winner = opponent
            return True
        
        return True

    def get_game_state(self):
        """Get the current state of the game"""
        return {
            'board': self.board,
            'current_player': self.current_player,
            'game_over': self.game_over,
            'winner': self.winner,
            'turn_count': self.turn_count,
            'valid_moves': self.board.get_valid_moves(self.current_player)
        } 
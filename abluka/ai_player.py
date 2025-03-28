import random
import math

class AIPlayer:
    def __init__(self, difficulty='normal'):
        self.difficulty = difficulty  # 'easy', 'normal', or 'hard'
        
        # Adjust depth based on difficulty - daha derin arama
        if difficulty == 'hard':
            self.max_depth = 9  # Çok daha derin analiz
        elif difficulty == 'normal':
            self.max_depth = 6  # Daha fazla ileriye görüş
        else:  # easy
            self.max_depth = 3  # Kolay modda da iyileştirilmiş derinlik
        
        # AI kişiliği için emoji ve mesajlar
        self.emojis = {
            'happy': ['😊', '😄', '😁', '🙂', '😎'],
            'thinking': ['🤔', '🧐', '🤨', '🧠', '💭'],
            'worried': ['😟', '😬', '😨', '😓', '😰'],
            'excited': ['🤩', '😆', '🎉', '👏', '🎊'],
            'smug': ['😏', '😌', '🙄', '😤', '💪'],
            'surprised': ['😮', '😲', '😱', '😯', '😵']
        }
        
        self.messages = {
            'good_move': [
                "İyi hamle!",
                "Etkileyici!",
                "Hmm, akıllıca...",
                "Bunu düşünmemiştim",
                "İyi oynuyorsun!"
            ],
            'thinking': [
                "Hmm, düşüneyim...",
                "İlginç bir durum...",
                "Bunu analiz etmeliyim...",
                "Stratejik düşünme zamanı...",
                "Beni zorluyorsun..."
            ],
            'worried': [
                "Eyvah, bu zor olacak",
                "Sıkıştım galiba...",
                "Çıkış yolu bulmalıyım!",
                "Bu pek iyi görünmüyor...",
                "Tehlikedeyim!"
            ],
            'confident': [
                "Bu hamleyi gördün mü?",
                "İşte benim stilim!",
                "Bu oyunu seviyorum",
                "Planım işliyor...",
                "Şah mat yakın!"
            ],
            'trapped': [
                "Beni ablukaya mı alıyorsun?!",
                "Ahh, kapana kısıldım!",
                "Ustalıkla oynadın...",
                "Çevrildim galiba!",
                "Kaçış yok mu?"
            ]
        }
        
        # AI durum takibi
        self.last_freedom = None
        self.cornered = False
        self.current_message = None
    
    def choose_move(self, game_state):
        """Choose a move for the AI player based on the current game state"""
        board = game_state['board']
        piece = game_state['current_player']
        valid_moves = board.get_valid_moves(piece)
        
        if not valid_moves:
            return None, None  # No valid moves
        
        # AI'ın board durumu değerlendirmesi
        board_assessment = self._assess_board_situation(board, piece)
        self.current_message = self._generate_reaction(board_assessment, piece)
        
        if self.difficulty == 'easy':
            return self._easy_strategy(board, piece, valid_moves)
        elif self.difficulty == 'hard':
            return self._hard_strategy(board, piece, valid_moves, board_assessment)
        else:  # 'normal' difficulty or fallback
            return self._normal_strategy(board, piece, valid_moves, board_assessment)
    
    def get_reaction(self):
        """AI'ın tepkisini döndürür - GUI tarafından çağrılır"""
        return self.current_message
    
    def _assess_board_situation(self, board, piece):
        """Tahtadaki durumu değerlendirir ve AI'ın duygusal durumunu belirler"""
        opponent = 'W' if piece == 'B' else 'B'
        
        # Hareket özgürlüğü hesapla
        current_freedom = len(board.get_valid_moves(piece))
        opponent_freedom = len(board.get_valid_moves(opponent))
        
        # Orta kontrol
        player_pos = board.black_pos if piece == 'B' else board.white_pos
        center_distance = abs(player_pos[0] - 3) + abs(player_pos[1] - 3)
        
        # Kenar yakınlığı
        edge_distance = min(player_pos[0], board.size - 1 - player_pos[0], 
                           player_pos[1], board.size - 1 - player_pos[1])
        
        # Sıkışıklık tespiti
        is_cornered = edge_distance <= 1 and current_freedom <= 3
        
        # Önceki durumla karşılaştırma
        freedom_decreased = self.last_freedom is not None and current_freedom < self.last_freedom
        self.last_freedom = current_freedom
        
        # Durum değerlendirmesi
        situation = {
            'current_freedom': current_freedom,
            'opponent_freedom': opponent_freedom,
            'center_distance': center_distance,
            'edge_distance': edge_distance,
            'is_cornered': is_cornered,
            'freedom_decreased': freedom_decreased,
            'winning_chance': current_freedom > opponent_freedom + 2,
            'losing_risk': current_freedom < opponent_freedom - 2,
            'almost_trapped': current_freedom <= 2
        }
        
        # Önceki cornered durumunu güncelle
        self.cornered = is_cornered
        
        return situation
    
    def _generate_reaction(self, situation, piece):
        """Duruma göre emoji ve mesaj üretir"""
        if situation['almost_trapped']:
            emoji = random.choice(self.emojis['worried'])
            message = random.choice(self.messages['trapped'])
            return f"{emoji} {message}"
        
        elif situation['is_cornered']:
            emoji = random.choice(self.emojis['worried'])
            message = random.choice(self.messages['worried'])
            return f"{emoji} {message}"
        
        elif situation['winning_chance']:
            emoji = random.choice(self.emojis['smug'])
            message = random.choice(self.messages['confident'])
            return f"{emoji} {message}"
        
        elif situation['freedom_decreased']:
            emoji = random.choice(self.emojis['thinking'])
            message = random.choice(self.messages['thinking'])
            return f"{emoji} {message}"
        
        elif random.random() < 0.3:  # Bazen rastgele mesaj göster
            emoji = random.choice(self.emojis['happy'])
            message = random.choice(self.messages['thinking'])
            return f"{emoji} {message}"
        
        return None  # Bazen hiçbir şey gösterme
    
    def _easy_strategy(self, board, piece, valid_moves):
        """Easy modunda geliştirilmiş rastgele strateji"""
        # Abluka fırsatlarını kontrol et
        opponent = 'W' if piece == 'B' else 'B'
        
        for move in valid_moves:
            # Hamleyi dene
            temp_board = self._clone_board(board)
            temp_board.move_piece(piece, move)
            
            # Boş konumları bul
            empty_positions = []
            for i in range(board.size):
                for j in range(board.size):
                    if temp_board.grid[i][j] is None:
                        empty_positions.append((i, j))
            
            # Engelleri dene
            for obstacle_pos in empty_positions:
                obs_board = self._clone_board(temp_board)
                obs_board.place_obstacle(obstacle_pos)
                
                # Rakibi ablukaya alabilir miyiz?
                if obs_board.is_abluka(opponent):
                    return move, obstacle_pos
        
        # Rastgele seçim (ama daha akıllıca)
        scored_moves = []
        
        for move in valid_moves:
            # Clone the board with this move
            temp_board = self._clone_board(board)
            temp_board.move_piece(piece, move)
            
            # Simple scoring - prefer not being near edges
            row, col = move
            edge_dist = min(row, board.size - 1 - row, col, board.size - 1 - col)
            center_dist = abs(row - 3) + abs(col - 3)
            
            score = edge_dist * 2 - center_dist + random.randint(0, 3)
            
            # Avoid spaces with few exit paths
            exit_paths = len(temp_board.get_valid_moves(piece))
            score += exit_paths
            
            scored_moves.append((move, score))
        
        # Sort by score, highest first
        scored_moves.sort(key=lambda x: x[1], reverse=True)
        
        # Choose from top 40% of moves
        top_count = max(1, len(scored_moves) // 3)
        chosen_move = scored_moves[random.randint(0, top_count - 1)][0]
        
        # Place obstacle in a somewhat strategic position
        temp_board = self._clone_board(board)
        temp_board.move_piece(piece, chosen_move)
        
        opponent_pos = temp_board.black_pos if opponent == 'B' else temp_board.white_pos
        opponent_moves = temp_board.get_valid_moves(opponent)
        
        # Find empty positions
        empty_positions = []
        for i in range(board.size):
            for j in range(board.size):
                if temp_board.grid[i][j] is None and (i, j) != chosen_move:
                    # Favor positions that are close to the opponent
                    dist_to_opponent = abs(i - opponent_pos[0]) + abs(j - opponent_pos[1])
                    score = 10 - dist_to_opponent
                    
                    # Extra points for positions that block opponent's moves
                    if (i, j) in opponent_moves:
                        score += 5
                        
                    empty_positions.append(((i, j), score))
        
        if not empty_positions:
            return chosen_move, None
        
        # Sort by score and add randomness
        empty_positions.sort(key=lambda x: x[1] + random.randint(0, 4), reverse=True)
        obstacle_pos = empty_positions[0][0]
        
        return chosen_move, obstacle_pos
    
    def _normal_strategy(self, board, piece, valid_moves, board_assessment=None):
        """Improved strategy for normal difficulty with deeper search"""
        # Create a scoring system for moves
        scored_moves = []
        opponent = 'W' if piece == 'B' else 'B'
        
        # Check for immediate winning moves
        for move in valid_moves:
            temp_board = self._clone_board(board)
            temp_board.move_piece(piece, move)
            
            empty_positions = []
            for i in range(board.size):
                for j in range(board.size):
                    if temp_board.grid[i][j] is None:
                        empty_positions.append((i, j))
            
            # Try each obstacle to see if it traps opponent
            for obstacle_pos in empty_positions:
                obstacle_board = self._clone_board(temp_board)
                obstacle_board.place_obstacle(obstacle_pos)
                
                # Check if this traps the opponent
                if obstacle_board.is_abluka(opponent):
                    return move, obstacle_pos
        
        for move in valid_moves:
            # Test this move on a clone board
            temp_board = self._clone_board(board)
            temp_board.move_piece(piece, move)
            
            # Evaluate board with more advanced scoring and deeper lookahead
            score = self._evaluate_position(temp_board, piece, 2)  # Lookahead of 2 moves
            scored_moves.append((move, score))
        
        # Sort moves by score, highest first
        scored_moves.sort(key=lambda x: x[1], reverse=True)
        
        # Add some randomness - choose from top moves
        top_n = min(3, len(scored_moves))
        chosen_move = scored_moves[random.randint(0, top_n-1)][0]
        
        # Simulate the move to get the new board state
        sim_board = self._clone_board(board)
        sim_board.move_piece(piece, chosen_move)
        
        # Use minimax to find the best obstacle placement
        best_obstacle = None
        best_obstacle_score = float('-inf')
        
        empty_positions = []
        for i in range(board.size):
            for j in range(board.size):
                if sim_board.grid[i][j] is None:
                    empty_positions.append((i, j))
        
        # Use a subset for performance if there are too many options
        if len(empty_positions) > 15:
            empty_positions = random.sample(empty_positions, 15)
        
        for obs_pos in empty_positions:
            obs_board = self._clone_board(sim_board)
            obs_board.place_obstacle(obs_pos)
            
            # Check for immediate win
            if obs_board.is_abluka(opponent):
                return chosen_move, obs_pos
            
            # Use minimax to evaluate this obstacle placement
            score = self._minimax(obs_board, 2, False, piece, float('-inf'), float('inf'))
            
            if score > best_obstacle_score:
                best_obstacle_score = score
                best_obstacle = obs_pos
        
        return chosen_move, best_obstacle
    
    def _hard_strategy(self, board, piece, valid_moves, board_assessment=None):
        """Advanced strategy for hard difficulty using deep minimax with adaptive search"""
        opponent = 'W' if piece == 'B' else 'B'
        
        # First check if we can immediately trap the opponent
        for move in valid_moves:
            # Try each move
            temp_board = self._clone_board(board)
            temp_board.move_piece(piece, move)
            
            # Get empty spots for obstacles
            empty_positions = []
            for i in range(board.size):
                for j in range(board.size):
                    if temp_board.grid[i][j] is None:
                        empty_positions.append((i, j))
            
            # Try each obstacle to see if it traps opponent
            for obstacle_pos in empty_positions:
                obstacle_board = self._clone_board(temp_board)
                obstacle_board.place_obstacle(obstacle_pos)
                
                # Check if this traps the opponent
                if obstacle_board.is_abluka(opponent):
                    return move, obstacle_pos  # Found a winning move!
        
        # Enhanced adaptive search
        # If in danger, focus on increasing freedom
        adaptive_depth = self.max_depth
        if board_assessment and (board_assessment['is_cornered'] or board_assessment['almost_trapped']):
            # Prioritize freedom when cornered
            return self._defensive_strategy(board, piece, valid_moves)
        
        # If we have many options, we may need to reduce search depth for performance
        if len(valid_moves) > 10:
            # Pre-filter moves to reduce search space
            filtered_moves = self._pre_filter_moves(board, piece, valid_moves)
            valid_moves = filtered_moves[:8]  # Limit to top 8 moves
            adaptive_depth = max(5, self.max_depth - 2)  # Reduce depth slightly
        
        # If no immediate win, use enhanced minimax with adaptive depth
        best_score = float('-inf')
        best_move = None
        best_obstacle = None
        
        # Alpha-beta pruning initial values
        alpha = float('-inf')
        beta = float('inf')
        
        # Try each possible move with deeper search
        for move in valid_moves:
            # Clone the board with this move
            temp_board = self._clone_board(board)
            temp_board.move_piece(piece, move)
            
            # Get all possible obstacle placements after this move
            empty_positions = []
            for i in range(board.size):
                for j in range(board.size):
                    if temp_board.grid[i][j] is None:
                        empty_positions.append((i, j))
            
            # Try each obstacle placement (or sample if too many)
            sample_size = min(len(empty_positions), 12)  # More focused sample
            obstacle_sample = random.sample(empty_positions, sample_size) if len(empty_positions) > sample_size else empty_positions
            
            for obstacle_pos in obstacle_sample:
                obstacle_board = self._clone_board(temp_board)
                obstacle_board.place_obstacle(obstacle_pos)
                
                # Evaluate with deeper minimax
                score = self._minimax(obstacle_board, adaptive_depth, False, piece, alpha, beta)
                
                if score > best_score:
                    best_score = score
                    best_move = move
                    best_obstacle = obstacle_pos
                
                # Alpha-beta pruning
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break
            
            if beta <= alpha:
                break
        
        # If we couldn't find a good move with minimax, fallback to a defensive strategy
        if best_move is None:
            return self._defensive_strategy(board, piece, valid_moves)
        
        return best_move, best_obstacle
    
    def _defensive_strategy(self, board, piece, valid_moves):
        """When in danger, focus on maximizing freedom and distance from edges"""
        scored_moves = []
        opponent = 'W' if piece == 'B' else 'B'
        
        for move in valid_moves:
            temp_board = self._clone_board(board)
            temp_board.move_piece(piece, move)
            
            # Calculate freedom after move
            future_freedom = len(temp_board.get_valid_moves(piece))
            
            # Calculate edge distance (staying away from edges is crucial)
            row, col = move
            edge_distance = min(row, board.size - 1 - row, col, board.size - 1 - col)
            
            # Calculate center control
            center_control = 8 - (abs(row - 3) + abs(col - 3))
            
            # Calculate distance from opponent (may want to keep distance when defensive)
            opponent_pos = board.black_pos if opponent == 'B' else board.white_pos
            opponent_distance = abs(row - opponent_pos[0]) + abs(col - opponent_pos[1])
            
            # Defensive scoring - prioritize freedom and edge distance
            score = future_freedom * 10 + edge_distance * 8 + center_control * 3 + opponent_distance
            
            scored_moves.append((move, score))
        
        # Sort by score and pick the best move
        scored_moves.sort(key=lambda x: x[1], reverse=True)
        best_move = scored_moves[0][0]
        
        # For obstacle placement, focus on blocking opponent's paths
        temp_board = self._clone_board(board)
        temp_board.move_piece(piece, best_move)
        
        opponent_moves = temp_board.get_valid_moves(opponent)
        
        if not opponent_moves:
            # No opponent moves to block, place randomly
            empty_positions = []
            for i in range(board.size):
                for j in range(board.size):
                    if temp_board.grid[i][j] is None:
                        empty_positions.append((i, j))
            
            if not empty_positions:
                obstacle_pos = None
            else:
                obstacle_pos = random.choice(empty_positions)
        else:
            # Find which opponent move has the highest freedom
            opponent_freedom = []
            for opp_move in opponent_moves:
                test_board = self._clone_board(temp_board)
                test_board.move_piece(opponent, opp_move)
                freedom = len(test_board.get_valid_moves(opponent))
                opponent_freedom.append((opp_move, freedom))
            
            # Sort by freedom and block the move that gives opponent most freedom
            opponent_freedom.sort(key=lambda x: x[1], reverse=True)
            obstacle_pos = opponent_freedom[0][0]
        
        return best_move, obstacle_pos
    
    def _pre_filter_moves(self, board, piece, valid_moves):
        """Pre-filter moves to reduce search space for deep search"""
        scored_moves = []
        
        for move in valid_moves:
            # Quick evaluation without deep search
            temp_board = self._clone_board(board)
            temp_board.move_piece(piece, move)
            
            # Calculate basic metrics
            row, col = move
            edge_distance = min(row, board.size - 1 - row, col, board.size - 1 - col)
            center_control = 8 - (abs(row - 3) + abs(col - 3))
            future_freedom = len(temp_board.get_valid_moves(piece))
            
            # Quick score based on these metrics
            score = future_freedom * 5 + edge_distance * 3 + center_control * 2
            
            scored_moves.append((move, score))
        
        # Sort by score and return
        scored_moves.sort(key=lambda x: x[1], reverse=True)
        return [move for move, _ in scored_moves]
    
    def _minimax(self, board, depth, is_maximizing, original_piece, alpha, beta):
        """Minimax algorithm with alpha-beta pruning and enhanced evaluation"""
        # Determine current player
        current_piece = original_piece if is_maximizing else ('W' if original_piece == 'B' else 'B')
        opponent = 'W' if current_piece == 'B' else 'B'
        
        # Check terminal conditions
        if depth == 0:
            return self._evaluate_board(board, original_piece)
        
        if board.is_abluka(current_piece):
            return -100000 if is_maximizing else 100000  # Huge penalty/reward for being in abluka
        
        valid_moves = board.get_valid_moves(current_piece)
        if not valid_moves:
            return -100000 if is_maximizing else 100000  # No valid moves means abluka
        
        # Adaptive sampling - reduce search space for deeper levels
        if depth <= 2:
            sample_size = min(len(valid_moves), 8)
        elif depth <= 4:
            sample_size = min(len(valid_moves), 5)
        else:
            sample_size = min(len(valid_moves), 3)
        
        if len(valid_moves) > sample_size:
            # Pre-score moves and select the most promising ones
            scored_moves = []
            for move in valid_moves:
                test_board = self._clone_board(board)
                test_board.move_piece(current_piece, move)
                quick_score = self._quick_evaluate(test_board, current_piece)
                scored_moves.append((move, quick_score))
            
            scored_moves.sort(key=lambda x: x[1], reverse=is_maximizing)
            valid_moves = [move for move, _ in scored_moves[:sample_size]]
        
        # Recursive minimax
        if is_maximizing:
            max_eval = float('-inf')
            for move in valid_moves:
                # Make move
                new_board = self._clone_board(board)
                new_board.move_piece(current_piece, move)
                
                # Get obstacle placement options
                empty_positions = []
                for i in range(board.size):
                    for j in range(board.size):
                        if new_board.grid[i][j] is None:
                            empty_positions.append((i, j))
                
                # Further limit obstacle samples based on depth
                obstacle_sample_size = min(len(empty_positions), 5 if depth <= 3 else 3)
                if len(empty_positions) > obstacle_sample_size:
                    obstacle_sample = random.sample(empty_positions, obstacle_sample_size)
                else:
                    obstacle_sample = empty_positions
                
                for obstacle_pos in obstacle_sample:
                    obstacle_board = self._clone_board(new_board)
                    obstacle_board.place_obstacle(obstacle_pos)
                    
                    # Check if opponent is now in abluka (win)
                    if obstacle_board.is_abluka(opponent):
                        return 100000  # Immediate win
                    
                    # Recursive call with the opposing player
                    eval = self._minimax(obstacle_board, depth - 1, False, original_piece, alpha, beta)
                    max_eval = max(max_eval, eval)
                    
                    # Alpha-beta pruning
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
                
                if beta <= alpha:
                    break
            
            return max_eval
        else:
            min_eval = float('inf')
            for move in valid_moves:
                # Make move
                new_board = self._clone_board(board)
                new_board.move_piece(current_piece, move)
                
                # Get obstacle placement options
                empty_positions = []
                for i in range(board.size):
                    for j in range(board.size):
                        if new_board.grid[i][j] is None:
                            empty_positions.append((i, j))
                
                # Further limit obstacle samples based on depth
                obstacle_sample_size = min(len(empty_positions), 5 if depth <= 3 else 3)
                if len(empty_positions) > obstacle_sample_size:
                    obstacle_sample = random.sample(empty_positions, obstacle_sample_size)
                else:
                    obstacle_sample = empty_positions
                
                for obstacle_pos in obstacle_sample:
                    obstacle_board = self._clone_board(new_board)
                    obstacle_board.place_obstacle(obstacle_pos)
                    
                    # Check if original player is now in abluka (loss)
                    if obstacle_board.is_abluka(original_piece):
                        return -100000  # Immediate loss
                    
                    # Recursive call with the original player
                    eval = self._minimax(obstacle_board, depth - 1, True, original_piece, alpha, beta)
                    min_eval = min(min_eval, eval)
                    
                    # Alpha-beta pruning
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
                
                if beta <= alpha:
                    break
            
            return min_eval
    
    def _quick_evaluate(self, board, piece):
        """Quick evaluation function for move filtering"""
        opponent = 'W' if piece == 'B' else 'B'
        
        # Count mobility (number of valid moves)
        player_mobility = len(board.get_valid_moves(piece))
        opponent_mobility = len(board.get_valid_moves(opponent))
        
        if player_mobility == 0:
            return -10000  # Worst case
        
        if opponent_mobility == 0:
            return 10000  # Best case
        
        # Calculate center control
        player_pos = board.black_pos if piece == 'B' else board.white_pos
        opponent_pos = board.black_pos if opponent == 'B' else board.white_pos
        
        player_center = 8 - (abs(player_pos[0] - 3) + abs(player_pos[1] - 3))
        opponent_center = 8 - (abs(opponent_pos[0] - 3) + abs(opponent_pos[1] - 3))
        
        # Edge avoidance
        player_edge = min(player_pos[0], board.size - 1 - player_pos[0], 
                         player_pos[1], board.size - 1 - player_pos[1])
        
        # Mobility difference is most important
        return player_mobility * 10 - opponent_mobility * 8 + player_center * 2 - opponent_center + player_edge * 3
    
    def _evaluate_position(self, board, piece, depth):
        """Evaluate a position with limited depth search"""
        if depth == 0:
            return self._evaluate_board(board, piece)
        
        opponent = 'W' if piece == 'B' else 'B'
        valid_moves = board.get_valid_moves(piece)
        
        if not valid_moves:
            return -10000  # Worst position
        
        # If in an excellent position with many options, return early
        if len(valid_moves) >= 6:
            return self._evaluate_board(board, piece)
        
        # For each valid move, evaluate the resulting position
        best_score = float('-inf')
        
        for move in valid_moves:
            # Make the move
            temp_board = self._clone_board(board)
            temp_board.move_piece(piece, move)
            
            # Get empty spaces for obstacle
            empty_positions = []
            for i in range(board.size):
                for j in range(board.size):
                    if temp_board.grid[i][j] is None:
                        empty_positions.append((i, j))
            
            # Try a sample of obstacles (or all if few)
            sample_size = min(len(empty_positions), 4)
            sample = random.sample(empty_positions, sample_size) if len(empty_positions) > sample_size else empty_positions
            
            for obstacle_pos in sample:
                obs_board = self._clone_board(temp_board)
                obs_board.place_obstacle(obstacle_pos)
                
                # Check if opponent is in abluka
                if obs_board.is_abluka(opponent):
                    return 10000  # Best position
                
                # Simulate opponent's best response
                opponent_score = self._evaluate_position_for_opponent(obs_board, opponent, depth - 1)
                
                # Our score is inverse of opponent's best score
                score = -opponent_score
                best_score = max(best_score, score)
        
        return best_score
    
    def _evaluate_position_for_opponent(self, board, opponent, depth):
        """Evaluate opponent's best response"""
        if depth == 0:
            return self._evaluate_board(board, opponent)
        
        piece = 'W' if opponent == 'B' else 'B'
        valid_moves = board.get_valid_moves(opponent)
        
        if not valid_moves:
            return -10000  # Worst for opponent
        
        # Opponent tries their best move
        best_score = float('-inf')
        
        for move in valid_moves:
            # Make the move
            temp_board = self._clone_board(board)
            temp_board.move_piece(opponent, move)
            
            # Get empty spaces for obstacle
            empty_positions = []
            for i in range(board.size):
                for j in range(board.size):
                    if temp_board.grid[i][j] is None:
                        empty_positions.append((i, j))
            
            # Try a sample of obstacles
            sample_size = min(len(empty_positions), 3)
            sample = random.sample(empty_positions, sample_size) if len(empty_positions) > sample_size else empty_positions
            
            for obstacle_pos in sample:
                obs_board = self._clone_board(temp_board)
                obs_board.place_obstacle(obstacle_pos)
                
                # Check if we are in abluka
                if obs_board.is_abluka(piece):
                    return 10000  # Best for opponent
                
                score = self._evaluate_board(obs_board, opponent)
                best_score = max(best_score, score)
        
        return best_score
    
    def _evaluate_board(self, board, piece):
        """Enhanced evaluation function for the board position"""
        opponent = 'W' if piece == 'B' else 'B'
        
        # Count mobility (number of valid moves)
        player_mobility = len(board.get_valid_moves(piece))
        opponent_mobility = len(board.get_valid_moves(opponent))
        
        if player_mobility == 0:
            return -100000  # We're in abluka, worst case
        
        if opponent_mobility == 0:
            return 100000  # Opponent in abluka, best case
        
        # Calculate center control
        player_pos = board.black_pos if piece == 'B' else board.white_pos
        opponent_pos = board.black_pos if opponent == 'B' else board.white_pos
        
        player_center_control = 8 - (abs(player_pos[0] - 3) + abs(player_pos[1] - 3))
        opponent_center_control = 8 - (abs(opponent_pos[0] - 3) + abs(opponent_pos[1] - 3))
        
        # Evaluate freedom of movement in key directions
        player_freedom = self._calculate_freedom(board, piece)
        opponent_freedom = self._calculate_freedom(board, opponent)
        
        # Evaluate control of key areas
        player_area_control = self._calculate_area_control(board, piece)
        opponent_area_control = self._calculate_area_control(board, opponent)
        
        # Evaluate edge avoidance (staying away from edges is good)
        player_edge_penalty = self._calculate_edge_penalty(board, piece)
        opponent_edge_penalty = self._calculate_edge_penalty(board, opponent)
        
        # Path finding - evaluate escape routes
        player_paths = self._evaluate_path_options(board, piece)
        opponent_paths = self._evaluate_path_options(board, opponent)
        
        # Territory control - evaluate how much of the board can be reached
        player_territory = self._calculate_territory(board, piece)
        opponent_territory = self._calculate_territory(board, opponent)
        
        # Combine factors with weights
        mobility_diff = (player_mobility - opponent_mobility) * 20  # Mobility is critical
        center_control_diff = (player_center_control - opponent_center_control) * 5
        freedom_diff = (player_freedom - opponent_freedom) * 10
        area_control_diff = (player_area_control - opponent_area_control) * 5
        edge_penalty_diff = (opponent_edge_penalty - player_edge_penalty) * 8  # Keep opponent at edge
        path_diff = (player_paths - opponent_paths) * 7
        territory_diff = (player_territory - opponent_territory) * 6
        
        score = (mobility_diff + center_control_diff + freedom_diff + 
                area_control_diff + edge_penalty_diff + path_diff + territory_diff)
        
        # Add small random factor to prevent loops
        score += random.uniform(-0.5, 0.5)
        
        return score
    
    def _calculate_freedom(self, board, piece):
        """Calculate how much freedom a piece has in different directions"""
        pos = board.black_pos if piece == 'B' else board.white_pos
        row, col = pos
        
        # Check all 8 directions
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        freedom = 0
        for d_row, d_col in directions:
            new_row, new_col = row + d_row, col + d_col
            if (0 <= new_row < board.size and 
                0 <= new_col < board.size and 
                board.grid[new_row][new_col] is None):
                freedom += 1
                
                # Check one step further
                next_row, next_col = new_row + d_row, new_col + d_col
                if (0 <= next_row < board.size and 
                    0 <= next_col < board.size and 
                    board.grid[next_row][next_col] is None):
                    freedom += 0.5  # Add extra value for having more space in this direction
                    
                    # Check a third step
                    third_row, third_col = next_row + d_row, next_col + d_col
                    if (0 <= third_row < board.size and
                        0 <= third_col < board.size and
                        board.grid[third_row][third_col] is None):
                        freedom += 0.25  # Even more value for long-range freedom
        
        return freedom
    
    def _calculate_area_control(self, board, piece):
        """Calculate how much of the board a piece controls"""
        pos = board.black_pos if piece == 'B' else board.white_pos
        row, col = pos
        
        # Define key areas of the board
        center_area = [(2, 2), (2, 3), (2, 4), (3, 2), (3, 3), (3, 4), (4, 2), (4, 3), (4, 4)]
        
        # Check how many of the key areas are accessible
        control = 0
        for area_row, area_col in center_area:
            # If we're already in this position
            if (row, col) == (area_row, area_col):
                control += 2
                continue
                
            # Check if we can reach this position
            can_reach = False
            # Simplified path checking - can improve this for actual path finding
            if abs(row - area_row) <= 2 and abs(col - area_col) <= 2:
                # If the path is relatively clear
                obstacle_count = 0
                for r in range(min(row, area_row), max(row, area_row) + 1):
                    for c in range(min(col, area_col), max(col, area_col) + 1):
                        if board.grid[r][c] not in [None, piece]:
                            obstacle_count += 1
                
                if obstacle_count <= 2:  # Allow some obstacles but not too many
                    can_reach = True
            
            if can_reach:
                control += 1
        
        return control
    
    def _calculate_edge_penalty(self, board, piece):
        """Calculate penalty for being close to the edge"""
        pos = board.black_pos if piece == 'B' else board.white_pos
        row, col = pos
        
        # Calculate distance from edges
        edge_distance = min(row, board.size - 1 - row, col, board.size - 1 - col)
        
        # Higher penalty for being closer to edge
        if edge_distance == 0:  # On the edge
            return 10  # Increased penalty
        elif edge_distance == 1:  # One step from edge
            return 5
        elif edge_distance == 2:  # Two steps from edge
            return 2
        else:
            return 0  # No penalty for being far from edge
    
    def _evaluate_path_options(self, board, piece):
        """Evaluate how many different path options are available"""
        pos = board.black_pos if piece == 'B' else board.white_pos
        row, col = pos
        
        # Look for paths to key areas (center and opposite sides)
        key_targets = [(3, 3)]  # Center
        
        # Add targets on opposite sides
        if row < 3:  # If in upper half, add targets in lower half
            key_targets.extend([(5, 1), (5, 3), (5, 5)])
        else:  # If in lower half, add targets in upper half
            key_targets.extend([(1, 1), (1, 3), (1, 5)])
            
        if col < 3:  # If in left half, add targets in right half
            key_targets.extend([(1, 5), (3, 5), (5, 5)])
        else:  # If in right half, add targets in left half
            key_targets.extend([(1, 1), (3, 1), (5, 1)])
        
        # Check for potential paths to these targets
        path_score = 0
        visited = set([(row, col)])
        
        # Use BFS to find paths
        for target_row, target_col in key_targets:
            if self._check_path(board, piece, row, col, target_row, target_col, visited):
                path_score += 2
        
        return path_score + len(board.get_valid_moves(piece))
    
    def _check_path(self, board, piece, start_row, start_col, target_row, target_col, visited, depth=0):
        """Check if there's a clear path to the target"""
        if depth > 5:  # Limit recursion depth
            return False
            
        if start_row == target_row and start_col == target_col:
            return True
            
        # Check all 8 directions
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        for d_row, d_col in directions:
            new_row, new_col = start_row + d_row, start_col + d_col
            
            if ((0 <= new_row < board.size) and 
                (0 <= new_col < board.size) and 
                (new_row, new_col) not in visited and
                board.grid[new_row][new_col] is None):
                
                visited.add((new_row, new_col))
                if self._check_path(board, piece, new_row, new_col, target_row, target_col, visited, depth + 1):
                    return True
        
        return False
    
    def _calculate_territory(self, board, piece):
        """Calculate how much territory is controlled/reachable"""
        pos = board.black_pos if piece == 'B' else board.white_pos
        
        # Start BFS from current position
        queue = [pos]
        visited = set([pos])
        territory = 1  # Count current position
        
        while queue:
            row, col = queue.pop(0)
            
            # Check all 8 directions
            directions = [
                (-1, -1), (-1, 0), (-1, 1),
                (0, -1),           (0, 1),
                (1, -1),  (1, 0),  (1, 1)
            ]
            
            for d_row, d_col in directions:
                new_row, new_col = row + d_row, col + d_col
                
                if ((0 <= new_row < board.size) and 
                    (0 <= new_col < board.size) and 
                    (new_row, new_col) not in visited and
                    board.grid[new_row][new_col] is None):
                    
                    queue.append((new_row, new_col))
                    visited.add((new_row, new_col))
                    territory += 1
        
        return territory
    
    def _clone_board(self, board):
        """Create a copy of the board for simulation"""
        from abluka.game_logic import Board
        
        clone = Board()
        clone.size = board.size
        clone.grid = [row[:] for row in board.grid]
        clone.black_pos = board.black_pos
        clone.white_pos = board.white_pos
        clone.obstacles = board.obstacles.copy()
        
        return clone 
import pygame
import sys
import os
import random
import time
import math
from abluka.game_logic import Game
from abluka.ai_player import AIPlayer
from abluka.sound_manager import SoundManager

class AblukaGUI:
    # Colors - Premium color scheme
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (220, 53, 69)
    LIGHT_RED = (255, 150, 150)
    GRAY = (240, 240, 245)
    DARK_GRAY = (52, 58, 64)
    LIGHT_BLUE = (13, 110, 253)
    GREEN = (40, 167, 69)
    YELLOW = (255, 193, 7)
    MENU_BG = (33, 37, 41)
    BUTTON_COLOR = (52, 58, 64)
    BUTTON_HOVER = (73, 80, 87)
    GOLD = (255, 215, 0)
    SILVER = (192, 192, 192)
    BRONZE = (205, 127, 50)
    BOARD_BG = (240, 240, 240)
    BOARD_LINES = (52, 58, 64)
    TRANSPARENT_WHITE = (255, 255, 255, 180)
    
    def __init__(self, width=700, height=700):
        pygame.init()
        pygame.display.set_caption("Abluka PC-  Ubden® Akademi PC Zeka Oyunu")
        
        # Set up display
        self.width = width
        self.height = height
        
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        
        # Load fonts
        try:
            # Try to load a nicer font if available
            self.font = pygame.font.Font(None, 28)
            self.big_font = pygame.font.Font(None, 42)
            self.small_font = pygame.font.Font(None, 20)
            self.title_font = pygame.font.Font(None, 60)
        except:
            # Fallback to system font
            self.font = pygame.font.SysFont('Arial', 24)
            self.big_font = pygame.font.SysFont('Arial', 36)
            self.small_font = pygame.font.SysFont('Arial', 18)
            self.title_font = pygame.font.SysFont('Arial', 48)
        
        # Initialize sound manager
        self.sound_manager = SoundManager()
        
        # Game state
        self.game = None
        self.ai_player = None
        self.mode = None
        self.difficulty = 'normal'
        self.show_menu = True
        self.show_how_to_play = False
        self.human_piece = None  # Will be randomly assigned for AI mode
        
        # Navigation buttons
        self.show_nav_buttons = True
        
        # Animation variables
        self.animation_active = False
        self.animation_start = None
        self.animation_end = None
        self.animation_piece = None
        self.animation_progress = 0
        self.animation_speed = 0.3  # seconds
        self.animation_timer = 0
        
        # Visual effects
        self.hover_button = None
        self.pulsating = 0
        self.pulsate_direction = 1
        
        # Obstacle preview
        self.obstacle_preview_pos = None
        
        # Obstacle counts - separate for each player
        self.black_obstacles = 24
        self.white_obstacles = 24
        
        # Animated message
        self.fade_message = None
        self.fade_timer = 0
        self.fade_duration = 2.0  # seconds
        
        # AI thinking flag to prevent multiple moves
        self.ai_thinking = False
    
    def initialize_game(self, mode, difficulty='normal'):
        """Initialize a new game with the given mode and difficulty"""
        self.sound_manager.play('game_start')
        
        self.mode = mode
        self.difficulty = difficulty
        self.game = Game()
        self.show_menu = False
        
        # Square size based on board dimensions
        self.board_size = self.game.board.size
        self.square_size = min(self.width, self.height) // (self.board_size + 2)  # +2 for margins
        
        # Board position (centered)
        self.board_left = (self.width - self.square_size * self.board_size) // 2
        self.board_top = (self.height - self.square_size * self.board_size) // 2
        
        # Game state tracking
        self.selected_pos = None
        self.valid_moves = []
        self.move_made = False
        self.obstacle_placement_phase = False
        self.highlighted_square = None
        self.obstacle_preview_pos = None
        self.ai_thinking = False
        
        # For human vs AI, randomly assign player color
        if mode == 'human_vs_ai':
            self.ai_player = AIPlayer(difficulty)
            self.human_piece = random.choice(['B', 'W'])
            
            # Display which piece the player is using
            piece_text = "Siyah" if self.human_piece == 'B' else "Beyaz"
            self.fade_message = f"Siz {piece_text} taşsınız!"
            self.fade_timer = pygame.time.get_ticks()
            
            # If AI goes first (player is white), trigger AI move
            if self.human_piece == 'W':
                # Small delay before AI's first move
                pygame.time.delay(500)
                self.ai_thinking = True
        else:
            self.ai_player = None
            self.human_piece = None
            self.fade_message = "Oyun başladı! Siyah oyuncu başlar."
            self.fade_timer = pygame.time.get_ticks()
            
        # Game status
        self.status_message = "Siyah oyuncu başlar."
        self.winner_message = ""
        
        # Reset obstacle count
        self.black_obstacles = 24
        self.white_obstacles = 24
    
    def return_to_menu(self):
        """Return to the main menu"""
        self.show_menu = True
        self.game = None
        self.ai_player = None
        self.animation_active = False
        self.obstacle_placement_phase = False
    
    def restart_game(self):
        """Restart the game with the same settings"""
        self.initialize_game(self.mode, self.difficulty)
    
    def run(self):
        running = True
        
        while running:
            current_time = pygame.time.get_ticks()
            
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if self.show_menu:
                    self._handle_menu_event(event)
                elif not self.game.game_over and not self.animation_active:
                    self._handle_event(event)
                elif self.game.game_over:
                    # Handle events when game is over
                    self._handle_game_over_event(event)
            
            # AI move if it's AI's turn and no animation is in progress
            if (self.mode == 'human_vs_ai' and 
                self.game and 
                self.game.current_player != self.human_piece and 
                not self.game.game_over and 
                not self.animation_active and
                self.ai_thinking):
                self._make_ai_move()
            
            # Update animation
            if self.animation_active:
                # Calculate progress based on elapsed time
                elapsed = (current_time - self.animation_timer) / 1000.0  # Convert to seconds
                self.animation_progress = min(elapsed / self.animation_speed, 1.0)
                
                if self.animation_progress >= 1.0:
                    # Animation complete
                    self.animation_active = False
                    # Complete the move
                    if self.animation_piece and self.animation_end:
                        piece = self.animation_piece
                        self.game.board.move_piece(piece, self.animation_end)
                        self.move_made = True
                        self.obstacle_placement_phase = True
                        self.selected_pos = None
                        self.valid_moves = []
                        self.status_message = "Engel taşı yerleştirin."
            
            # Draw the game
            if self.show_menu:
                if self.show_how_to_play:
                    self._draw_how_to_play()
                else:
                    self._draw_menu()
            else:
                self._draw()
            
            # Update the display
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()
    
    def _handle_menu_event(self, event):
        """Handle events on the menu screen"""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Check for button hover
        hvai_rect = pygame.Rect(self.width // 2 - 150, self.height // 2 - 60, 300, 50)
        hvh_rect = pygame.Rect(self.width // 2 - 150, self.height // 2 + 10, 300, 50)
        how_to_play_rect = pygame.Rect(self.width // 2 - 150, self.height // 2 + 80, 300, 40)
        easy_rect = pygame.Rect(self.width // 2 - 150, self.height // 2 + 140, 90, 30)
        normal_rect = pygame.Rect(self.width // 2 - 45, self.height // 2 + 140, 90, 30)
        hard_rect = pygame.Rect(self.width // 2 + 60, self.height // 2 + 140, 90, 30)
        exit_rect = pygame.Rect(self.width - 100, 20, 80, 30)
        sound_rect = pygame.Rect(self.width - 100, 60, 80, 30)
        
        # Track previous hover state to play sound only when first hovering
        prev_hover = self.hover_button
        self.hover_button = None
        
        if hvai_rect.collidepoint(mouse_x, mouse_y):
            self.hover_button = "hvai"
        elif hvh_rect.collidepoint(mouse_x, mouse_y):
            self.hover_button = "hvh"
        elif how_to_play_rect.collidepoint(mouse_x, mouse_y):
            self.hover_button = "how_to_play"
        elif easy_rect.collidepoint(mouse_x, mouse_y):
            self.hover_button = "easy"
        elif normal_rect.collidepoint(mouse_x, mouse_y):
            self.hover_button = "normal"
        elif hard_rect.collidepoint(mouse_x, mouse_y):
            self.hover_button = "hard"
        elif exit_rect.collidepoint(mouse_x, mouse_y):
            self.hover_button = "exit"
        elif sound_rect.collidepoint(mouse_x, mouse_y):
            self.hover_button = "sound"
            
        # Play hover sound if newly hovering a button
        if self.hover_button != prev_hover and self.hover_button is not None:
            self.sound_manager.play('menu_hover')
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                # Play click sound
                self.sound_manager.play('click')
                
                # Check if human vs AI button is clicked
                if hvai_rect.collidepoint(mouse_x, mouse_y):
                    self.sound_manager.play('menu_select')
                    self.initialize_game('human_vs_ai', self.difficulty)
                
                # Check if human vs human button is clicked
                elif hvh_rect.collidepoint(mouse_x, mouse_y):
                    self.sound_manager.play('menu_select')
                    self.initialize_game('human_vs_human')
                
                # Check if how to play button is clicked
                elif how_to_play_rect.collidepoint(mouse_x, mouse_y):
                    self.sound_manager.play('menu_select')
                    self.show_how_to_play = True
                
                # Check difficulty buttons
                elif easy_rect.collidepoint(mouse_x, mouse_y):
                    self.difficulty = 'easy'
                    self.sound_manager.play('click')
                    print(f"Difficulty set to: {self.difficulty}")
                
                elif normal_rect.collidepoint(mouse_x, mouse_y):
                    self.difficulty = 'normal'
                    self.sound_manager.play('click')
                    print(f"Difficulty set to: {self.difficulty}")
                
                elif hard_rect.collidepoint(mouse_x, mouse_y):
                    self.difficulty = 'hard'
                    self.sound_manager.play('click')
                    print(f"Difficulty set to: {self.difficulty}")
                
                # Check sound toggle button
                elif sound_rect.collidepoint(mouse_x, mouse_y):
                    muted = self.sound_manager.toggle_mute()
                    if not muted:
                        self.sound_manager.play('click')
                
                # Check exit button
                elif exit_rect.collidepoint(mouse_x, mouse_y):
                    pygame.quit()
                    sys.exit()
        
        # Handle "Escape" key to exit how to play screen
        if event.type == pygame.KEYDOWN and self.show_how_to_play:
            if event.key == pygame.K_ESCAPE:
                self.show_how_to_play = False
                self.sound_manager.play('click')
    
    def _handle_game_over_event(self, event):
        """Handle events when the game is over"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                # Check for main menu, restart and exit buttons
                menu_rect = pygame.Rect(self.width // 2 - 120, self.height // 2 + 40, 70, 30)
                restart_rect = pygame.Rect(self.width // 2 - 30, self.height // 2 + 40, 70, 30)
                exit_rect = pygame.Rect(self.width // 2 + 60, self.height // 2 + 40, 70, 30)
                
                if menu_rect.collidepoint(mouse_x, mouse_y):
                    self.sound_manager.play('click')
                    self.return_to_menu()
                elif restart_rect.collidepoint(mouse_x, mouse_y):
                    self.sound_manager.play('click')
                    self.restart_game()
                elif exit_rect.collidepoint(mouse_x, mouse_y):
                    self.sound_manager.play('click')
                    pygame.quit()
                    sys.exit()
    
    def _handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                # Check for navigation buttons
                menu_rect = pygame.Rect(self.width - 280, 20, 80, 30)
                restart_rect = pygame.Rect(self.width - 180, 20, 80, 30)
                exit_rect = pygame.Rect(self.width - 80, 20, 80, 30)
                
                if menu_rect.collidepoint(mouse_x, mouse_y):
                    self.return_to_menu()
                    return
                elif restart_rect.collidepoint(mouse_x, mouse_y):
                    self.restart_game()
                    return
                elif exit_rect.collidepoint(mouse_x, mouse_y):
                    pygame.quit()
                    sys.exit()
                
                # Game board interactions
                board_x, board_y = self._screen_to_board(mouse_x, mouse_y)
                
                if 0 <= board_x < self.board_size and 0 <= board_y < self.board_size:
                    if not self.obstacle_placement_phase:
                        # Piece movement phase
                        if ((self.mode == 'human_vs_human') or 
                            (self.mode == 'human_vs_ai' and self.game.current_player == self.human_piece)):
                            self._handle_piece_selection(board_x, board_y)
                    else:
                        # Obstacle placement phase
                        self._handle_obstacle_placement(board_x, board_y)
        
        elif event.type == pygame.MOUSEMOTION:
            # Update obstacle preview position when in obstacle placement phase
            if self.obstacle_placement_phase:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                board_x, board_y = self._screen_to_board(mouse_x, mouse_y)
                
                if (0 <= board_x < self.board_size and 
                    0 <= board_y < self.board_size and 
                    self.game.board.grid[board_y][board_x] is None):
                    self.obstacle_preview_pos = (board_y, board_x)
                else:
                    self.obstacle_preview_pos = None
    
    def _screen_to_board(self, screen_x, screen_y):
        """Convert screen coordinates to board coordinates"""
        board_x = (screen_x - self.board_left) // self.square_size
        board_y = (screen_y - self.board_top) // self.square_size
        return board_x, board_y
    
    def _board_to_screen(self, board_x, board_y):
        """Convert board coordinates to screen coordinates"""
        screen_x = self.board_left + board_x * self.square_size
        screen_y = self.board_top + board_y * self.square_size
        return screen_x, screen_y
    
    def _handle_piece_selection(self, board_x, board_y):
        """Handle piece selection during movement phase"""
        clicked_pos = (board_y, board_x)  # Convert to (row, col) for the game logic
        
        # Check if selecting own piece
        if self.game.board.grid[board_y][board_x] == self.game.current_player:
            self.sound_manager.play('click')
            self.selected_pos = clicked_pos
            self.valid_moves = self.game.board.get_valid_moves(self.game.current_player)
            self.status_message = f"{'Siyah' if self.game.current_player == 'B' else 'Beyaz'} taşı seçildi."
        
        # Check if selecting a valid move destination
        elif self.selected_pos and clicked_pos in self.valid_moves:
            self.sound_manager.play('move')
            # Start animation
            self.animation_active = True
            self.animation_start = self.selected_pos
            self.animation_end = clicked_pos
            self.animation_piece = self.game.current_player
            self.animation_progress = 0
            self.animation_timer = pygame.time.get_ticks()
        else:
            # Invalid move
            self.sound_manager.play('error')
    
    def _handle_obstacle_placement(self, board_x, board_y):
        """Handle obstacle placement"""
        obstacle_pos = (board_y, board_x)  # Convert to (row, col)
        
        # Check if the position is valid for placing an obstacle
        if self.game.board.grid[board_y][board_x] is None:
            # Place the obstacle
            self.sound_manager.play('place_obstacle')
            self.game.board.place_obstacle(obstacle_pos)
            
            # Decrease obstacle count (visual only)
            if self.game.current_player == 'B':
                self.black_obstacles -= 1
            else:
                self.white_obstacles -= 1
            
            # Check if game is over
            opponent = 'W' if self.game.current_player == 'B' else 'B'
            if self.game.board.is_abluka(opponent):
                self.game.game_over = True
                self.game.winner = self.game.current_player
                self.winner_message = f"{'Siyah' if self.game.current_player == 'B' else 'Beyaz'} oyuncu kazandı!"
                self.status_message = "Oyun sona erdi!"
                self.sound_manager.play('game_win')
            else:
                # Switch turn
                self.game.switch_player()
                
                # Check if the new current player is in abluka
                if self.game.board.is_abluka(self.game.current_player):
                    self.game.game_over = True
                    self.game.winner = opponent
                    self.winner_message = f"{'Siyah' if opponent == 'B' else 'Beyaz'} oyuncu kazandı!"
                    self.status_message = "Oyun sona erdi!"
                    self.sound_manager.play('game_win')
                else:
                    self.status_message = f"{'Siyah' if self.game.current_player == 'B' else 'Beyaz'} oyuncunun sırası."
                    
                    # Signal AI to make a move if it's its turn
                    if (self.mode == 'human_vs_ai' and 
                        self.game.current_player != self.human_piece):
                        self.ai_thinking = True
            
            # Reset for next turn
            self.obstacle_placement_phase = False
            self.move_made = False
            self.obstacle_preview_pos = None
        else:
            # Invalid placement
            self.sound_manager.play('error')
    
    def _make_ai_move(self):
        """Make a move for the AI player"""
        if not self.obstacle_placement_phase and self.ai_thinking:  # Only make a move if not in obstacle placement phase
            # Set flag to prevent multiple AI moves
            self.ai_thinking = False
            
            game_state = self.game.get_game_state()
            move_pos, obstacle_pos = self.ai_player.choose_move(game_state)
            
            # AI'dan mesaj alıp göster (emoji ve metin)
            ai_message = self.ai_player.get_reaction()
            if ai_message:
                self.fade_message = ai_message
                self.fade_timer = pygame.time.get_ticks()
                self.fade_duration = 3.0  # Biraz daha uzun göster
            
            if move_pos and obstacle_pos:
                # Start animation for AI move
                piece = self.game.current_player
                start_pos = self.game.board.black_pos if piece == 'B' else self.game.board.white_pos
                
                # Simulate piece movement with animation
                self.animation_active = True
                self.animation_start = start_pos
                self.animation_end = move_pos
                self.animation_piece = piece
                self.animation_progress = 0
                self.animation_timer = pygame.time.get_ticks()
                
                # Wait for animation to complete
                while self.animation_active:
                    current_time = pygame.time.get_ticks()
                    elapsed = (current_time - self.animation_timer) / 1000.0
                    self.animation_progress = min(elapsed / self.animation_speed, 1.0)
                    
                    if self.animation_progress >= 1.0:
                        self.animation_active = False
                        self.game.board.move_piece(piece, move_pos)
                    
                    # Update display during waiting
                    self._draw()
                    pygame.display.flip()
                    self.clock.tick(60)
                
                # Delay before placing obstacle
                pygame.time.delay(300)
                
                # Place the obstacle
                self.game.board.place_obstacle(obstacle_pos)
                
                # Decrease obstacle count (visual only)
                if piece == 'B':
                    self.black_obstacles -= 1
                else:
                    self.white_obstacles -= 1
                
                # Check if game is over
                opponent = 'W' if piece == 'B' else 'B'
                if self.game.board.is_abluka(opponent):
                    self.game.game_over = True
                    self.game.winner = piece
                    self.winner_message = f"{'Siyah' if piece == 'B' else 'Beyaz'} oyuncu (AI) kazandı!"
                    self.status_message = "Oyun sona erdi!"
                else:
                    # Switch turn
                    self.game.switch_player()
                    
                    # Check if the new current player is in abluka
                    if self.game.board.is_abluka(self.game.current_player):
                        self.game.game_over = True
                        self.game.winner = opponent
                        self.winner_message = f"{'Siyah' if opponent == 'B' else 'Beyaz'} oyuncu kazandı!"
                        self.status_message = "Oyun sona erdi!"
                    else:
                        self.status_message = f"{'Siyah' if self.game.current_player == 'B' else 'Beyaz'} oyuncunun sırası."
    
    def _draw_menu(self):
        """Draw the menu screen with premium UI"""
        # Fill the background
        self.screen.fill(self.MENU_BG)
        
        # Draw decorative pattern
        for i in range(0, self.width, 40):
            for j in range(0, self.height, 40):
                size = random.randint(2, 4)
                alpha = random.randint(10, 30)
                color = (255, 255, 255, alpha)
                s = pygame.Surface((size, size), pygame.SRCALPHA)
                s.fill(color)
                self.screen.blit(s, (i + random.randint(-10, 10), j + random.randint(-10, 10)))
        
        # Pulsate effect for title
        self.pulsating += 0.05 * self.pulsate_direction
        if self.pulsating > 1.0:
            self.pulsating = 1.0
            self.pulsate_direction = -1
        elif self.pulsating < 0.0:
            self.pulsating = 0.0
            self.pulsate_direction = 1
        
        title_size = 48 + int(10 * self.pulsating)
        title_font = pygame.font.SysFont('Arial', title_size)
        
        # Draw game title with shadow
        title_shadow = title_font.render("ABLUKA", True, self.BLACK)
        title_shadow_rect = title_shadow.get_rect(center=(self.width // 2 + 4, 104))
        self.screen.blit(title_shadow, title_shadow_rect)
        
        title_text = title_font.render("ABLUKA", True, self.GOLD)
        title_rect = title_text.get_rect(center=(self.width // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # Draw subtitle with gradient effect
        subtitle_text = self.font.render("Ubden® Akademi Abluka PC Oyunu", True, self.SILVER)
        subtitle_rect = subtitle_text.get_rect(center=(self.width // 2, 150))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Draw divider line
        pygame.draw.line(self.screen, self.GOLD, 
                         (self.width // 2 - 150, 180), 
                         (self.width // 2 + 150, 180), 2)
        
        # Get mouse position for button hover effects
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Draw elegant panels behind buttons
        panel_rect = pygame.Rect(self.width // 2 - 180, self.height // 2 - 90, 360, 280)
        s = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        s.fill((30, 30, 30, 200))
        self.screen.blit(s, panel_rect)
        pygame.draw.rect(self.screen, self.GOLD, panel_rect, 2)
        
        # Human vs AI button
        hvai_rect = pygame.Rect(self.width // 2 - 150, self.height // 2 - 60, 300, 50)
        hvai_color = self.BUTTON_HOVER if hvai_rect.collidepoint(mouse_x, mouse_y) else self.BUTTON_COLOR
        
        # Draw button with gradient and shadow
        pygame.draw.rect(self.screen, self.BLACK, pygame.Rect(hvai_rect.x + 3, hvai_rect.y + 3, hvai_rect.width, hvai_rect.height))
        pygame.draw.rect(self.screen, hvai_color, hvai_rect)
        pygame.draw.rect(self.screen, self.GOLD if hvai_rect.collidepoint(mouse_x, mouse_y) else self.SILVER, hvai_rect, 2)
        
        hvai_text = self.font.render("İnsan vs Bilgisayar", True, self.WHITE)
        hvai_text_rect = hvai_text.get_rect(center=hvai_rect.center)
        self.screen.blit(hvai_text, hvai_text_rect)
        
        # Human vs Human button
        hvh_rect = pygame.Rect(self.width // 2 - 150, self.height // 2 + 10, 300, 50)
        hvh_color = self.BUTTON_HOVER if hvh_rect.collidepoint(mouse_x, mouse_y) else self.BUTTON_COLOR
        
        pygame.draw.rect(self.screen, self.BLACK, pygame.Rect(hvh_rect.x + 3, hvh_rect.y + 3, hvh_rect.width, hvh_rect.height))
        pygame.draw.rect(self.screen, hvh_color, hvh_rect)
        pygame.draw.rect(self.screen, self.GOLD if hvh_rect.collidepoint(mouse_x, mouse_y) else self.SILVER, hvh_rect, 2)
        
        hvh_text = self.font.render("İnsan vs İnsan", True, self.WHITE)
        hvh_text_rect = hvh_text.get_rect(center=hvh_rect.center)
        self.screen.blit(hvh_text, hvh_text_rect)
        
        # How to Play button
        how_to_play_rect = pygame.Rect(self.width // 2 - 150, self.height // 2 + 80, 300, 40)
        how_to_play_color = self.BUTTON_HOVER if how_to_play_rect.collidepoint(mouse_x, mouse_y) else self.BUTTON_COLOR
        
        pygame.draw.rect(self.screen, self.BLACK, pygame.Rect(how_to_play_rect.x + 3, how_to_play_rect.y + 3, how_to_play_rect.width, how_to_play_rect.height))
        pygame.draw.rect(self.screen, how_to_play_color, how_to_play_rect)
        pygame.draw.rect(self.screen, self.GOLD if how_to_play_rect.collidepoint(mouse_x, mouse_y) else self.SILVER, how_to_play_rect, 2)
        
        how_to_play_text = self.font.render("Nasıl Oynanır?", True, self.WHITE)
        how_to_play_text_rect = how_to_play_text.get_rect(center=how_to_play_rect.center)
        self.screen.blit(how_to_play_text, how_to_play_text_rect)
        
        # Difficulty selection (for AI games)
        diff_text = self.font.render("AI Zorluğu:", True, self.SILVER)
        diff_text_rect = diff_text.get_rect(center=(self.width // 2, self.height // 2 + 130))
        self.screen.blit(diff_text, diff_text_rect)
        
        # Difficulty buttons
        easy_rect = pygame.Rect(self.width // 2 - 150, self.height // 2 + 140, 90, 30)
        normal_rect = pygame.Rect(self.width // 2 - 45, self.height // 2 + 140, 90, 30)
        hard_rect = pygame.Rect(self.width // 2 + 60, self.height // 2 + 140, 90, 30)
        
        # Change color based on selection and hover
        easy_color = self.BUTTON_HOVER if easy_rect.collidepoint(mouse_x, mouse_y) else (
            self.GREEN if self.difficulty == 'easy' else self.BUTTON_COLOR)
        normal_color = self.BUTTON_HOVER if normal_rect.collidepoint(mouse_x, mouse_y) else (
            self.GREEN if self.difficulty == 'normal' else self.BUTTON_COLOR)
        hard_color = self.BUTTON_HOVER if hard_rect.collidepoint(mouse_x, mouse_y) else (
            self.GREEN if self.difficulty == 'hard' else self.BUTTON_COLOR)
        
        # Draw buttons with shadow effect
        for rect, color in [(easy_rect, easy_color), (normal_rect, normal_color), (hard_rect, hard_color)]:
            pygame.draw.rect(self.screen, self.BLACK, pygame.Rect(rect.x + 2, rect.y + 2, rect.width, rect.height))
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, self.SILVER, rect, 1)
        
        easy_text = self.small_font.render("Kolay", True, self.WHITE)
        normal_text = self.small_font.render("Normal", True, self.WHITE)
        hard_text = self.small_font.render("Zor", True, self.WHITE)
        
        self.screen.blit(easy_text, easy_text.get_rect(center=easy_rect.center))
        self.screen.blit(normal_text, normal_text.get_rect(center=normal_rect.center))
        self.screen.blit(hard_text, hard_text.get_rect(center=hard_rect.center))
        
        # Exit button
        exit_rect = pygame.Rect(self.width - 100, 20, 80, 30)
        exit_color = self.BUTTON_HOVER if exit_rect.collidepoint(mouse_x, mouse_y) else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, self.BLACK, pygame.Rect(exit_rect.x + 2, exit_rect.y + 2, exit_rect.width, exit_rect.height))
        pygame.draw.rect(self.screen, exit_color, exit_rect)
        pygame.draw.rect(self.screen, self.WHITE, exit_rect, 1)
        
        exit_text = self.small_font.render("Çıkış", True, self.WHITE)
        exit_text_rect = exit_text.get_rect(center=exit_rect.center)
        self.screen.blit(exit_text, exit_text_rect)
        
        # Sound toggle button
        sound_rect = pygame.Rect(self.width - 100, 60, 80, 30)
        sound_color = self.BUTTON_HOVER if sound_rect.collidepoint(mouse_x, mouse_y) else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, self.BLACK, pygame.Rect(sound_rect.x + 2, sound_rect.y + 2, sound_rect.width, sound_rect.height))
        pygame.draw.rect(self.screen, sound_color, sound_rect)
        pygame.draw.rect(self.screen, self.WHITE, sound_rect, 1)
        
        sound_text = self.small_font.render("Ses " + ("Kapalı" if self.sound_manager.is_muted() else "Açık"), True, self.WHITE)
        sound_text_rect = sound_text.get_rect(center=sound_rect.center)
        self.screen.blit(sound_text, sound_text_rect)
    
    def _draw_how_to_play(self):
        """Draw the how to play screen"""
        # Fill the background
        self.screen.fill(self.MENU_BG)
        
        # Draw decorative pattern
        for i in range(0, self.width, 40):
            for j in range(0, self.height, 40):
                size = random.randint(2, 4)
                alpha = random.randint(10, 30)
                color = (255, 255, 255, alpha)
                s = pygame.Surface((size, size), pygame.SRCALPHA)
                s.fill(color)
                self.screen.blit(s, (i + random.randint(-10, 10), j + random.randint(-10, 10)))
        
        # Draw title
        title_text = self.big_font.render("NASIL OYNANIR?", True, self.GOLD)
        title_rect = title_text.get_rect(center=(self.width // 2, 60))
        
        # Draw title shadow
        title_shadow = self.big_font.render("NASIL OYNANIR?", True, self.BLACK)
        shadow_rect = title_shadow.get_rect(center=(self.width // 2 + 3, 63))
        self.screen.blit(title_shadow, shadow_rect)
        
        self.screen.blit(title_text, title_rect)
        
        # Draw panel for rules
        panel_rect = pygame.Rect(self.width // 2 - 300, 100, 600, 490)
        s = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        s.fill((20, 20, 30, 220))
        self.screen.blit(s, panel_rect)
        pygame.draw.rect(self.screen, self.GOLD, panel_rect, 2)
        
        # Rules text
        rules = [
            "Abluka, Türkiye Akıl ve Zeka Oyunları'ndan stratejik bir oyundur.",
            "",
            "OYUN KURALLARI:",
            "",
            "1. Oyun 7x7 bir tahta üzerinde oynanır.",
            "",
            "2. Her oyuncunun bir taşı ve 24 engel taşı vardır.",
            "",
            "3. Siyah oyuncu her zaman başlar.",
            "",
            "4. Her tur iki aşamadan oluşur:",
            "   a) Taşınızı komşu bir kareye hareket ettirin",
            "   b) Bir engel taşı yerleştirin",
            "",
            "5. Taşlar sadece boş karelere hareket edebilir ve çapraz",
            "   hareketler de geçerlidir.",
            "",
            "6. Engeller herhangi bir boş kareye yerleştirilebilir.",
            "",
            "7. ABLUKA: Eğer bir oyuncu hareket edebileceği hiçbir yer",
            "   kalmadığında, ablukaya alınmış olur ve oyunu kaybeder.",
            "",
            "8. Amacınız rakibinizi ablukaya alarak hareketsiz bırakmaktır.",
            "",
            "Kolay = AI rastgele hamleler yapar",
            "Normal = AI stratejik hamleler yapar",
            "Zor = AI 5 hamle ileriye bakar ve kazanmak için oynar",
            "",
            "Ubden® Akademi",
            "Çıkmak için ESC tuşuna basın."
        ]
        
        y_offset = 120
        for line in rules:
            if line.startswith("OYUN KURALLARI:") or line.startswith("ABLUKA:"):
                text = self.font.render(line, True, self.GOLD)
            elif line.startswith("Kolay") or line.startswith("Normal") or line.startswith("Zor"):
                text = self.small_font.render(line, True, self.SILVER)
            elif line == "":
                text = self.small_font.render(line, True, self.WHITE)
                y_offset += 5  # Add a little extra space for empty lines
            else:
                text = self.small_font.render(line, True, self.WHITE)
            
            text_rect = text.get_rect(midleft=(self.width // 2 - 270, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 20
        
        # Draw back instruction
        back_text = self.font.render("ESC tuşuna basarak ana menüye dönebilirsiniz", True, self.WHITE)
        back_rect = back_text.get_rect(center=(self.width // 2, self.height - 40))
        self.screen.blit(back_text, back_rect)
    
    def _draw(self):
        """Draw the game state"""
        # Fill the background
        self.screen.fill(self.GRAY)
        
        # Draw the board
        self._draw_board()
        
        # Draw obstacle stacks
        self._draw_obstacle_stacks()
        
        # Draw the pieces and obstacles
        self._draw_pieces_and_obstacles()
        
        # Draw the highlighted squares
        self._draw_highlights()
        
        # Draw obstacle preview
        self._draw_obstacle_preview()
        
        # Draw status and winner messages
        self._draw_status()
        
        # Draw navigation buttons
        self._draw_navigation_buttons()
        
        # Draw fade message if active
        self._draw_fade_message()
        
        # Draw game over screen if game is over
        if self.game and self.game.game_over:
            self._draw_game_over()
    
    def _draw_board(self):
        """Draw the game board with premium styling"""
        # Draw the board background with subtle gradient
        board_width = self.square_size * self.board_size
        board_height = self.square_size * self.board_size
        
        # Create a surface for the board background
        board_surface = pygame.Surface((board_width + 20, board_height + 20))
        
        # Draw gradient background
        for y in range(board_height + 20):
            # Gradient from dark gray to light gray
            color_value = 230 + (y / (board_height + 20)) * 15
            pygame.draw.line(board_surface, (color_value, color_value, color_value), 
                            (0, y), (board_width + 20, y))
        
        # Draw the board outline
        board_rect = pygame.Rect(0, 0, board_width + 10, board_height + 10)
        pygame.draw.rect(board_surface, self.BLACK, board_rect, 5)
        
        # Add board shadow
        self.screen.blit(board_surface, (self.board_left - 10, self.board_top - 10))
        
        # Draw the actual playing surface
        play_surface = pygame.Surface((board_width, board_height))
        play_surface.fill(self.BOARD_BG)
        self.screen.blit(play_surface, (self.board_left, self.board_top))
        
        # Draw the grid lines
        for i in range(self.board_size + 1):
            # Vertical lines
            pygame.draw.line(
                self.screen, 
                self.BOARD_LINES, 
                (self.board_left + i * self.square_size, self.board_top),
                (self.board_left + i * self.square_size, self.board_top + board_height),
                1
            )
            # Horizontal lines
            pygame.draw.line(
                self.screen, 
                self.BOARD_LINES, 
                (self.board_left, self.board_top + i * self.square_size),
                (self.board_left + board_width, self.board_top + i * self.square_size),
                1
            )
        
        # Draw accent marks at grid intersections
        for i in range(self.board_size + 1):
            for j in range(self.board_size + 1):
                x = self.board_left + i * self.square_size
                y = self.board_top + j * self.square_size
                
                # Draw small dot at each intersection
                pygame.draw.circle(self.screen, self.DARK_GRAY, (x, y), 2)
                
        # Draw special markers at key positions (e.g., center, corners)
        center_x = self.board_left + (self.board_size // 2) * self.square_size
        center_y = self.board_top + (self.board_size // 2) * self.square_size
        pygame.draw.circle(self.screen, self.GOLD, (center_x, center_y), 4)
        
        # Draw corner markers
        corner_positions = [
            (self.board_left, self.board_top),
            (self.board_left + board_width, self.board_top),
            (self.board_left, self.board_top + board_height),
            (self.board_left + board_width, self.board_top + board_height)
        ]
        
        for pos in corner_positions:
            pygame.draw.circle(self.screen, self.DARK_GRAY, pos, 4)
    
    def _draw_navigation_buttons(self):
        """Draw navigation buttons (menu, restart, exit)"""
        if not self.game:
            return
            
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Menu button
        menu_rect = pygame.Rect(self.width - 280, 20, 80, 30)
        menu_color = self.BUTTON_HOVER if menu_rect.collidepoint(mouse_x, mouse_y) else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, menu_color, menu_rect)
        pygame.draw.rect(self.screen, self.BLACK, menu_rect, 2)
        
        menu_text = self.small_font.render("Ana Menü", True, self.WHITE)
        menu_text_rect = menu_text.get_rect(center=menu_rect.center)
        self.screen.blit(menu_text, menu_text_rect)
        
        # Restart button
        restart_rect = pygame.Rect(self.width - 180, 20, 80, 30)
        restart_color = self.BUTTON_HOVER if restart_rect.collidepoint(mouse_x, mouse_y) else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, restart_color, restart_rect)
        pygame.draw.rect(self.screen, self.BLACK, restart_rect, 2)
        
        restart_text = self.small_font.render("Yeniden", True, self.WHITE)
        restart_text_rect = restart_text.get_rect(center=restart_rect.center)
        self.screen.blit(restart_text, restart_text_rect)
        
        # Exit button
        exit_rect = pygame.Rect(self.width - 80, 20, 80, 30)
        exit_color = self.BUTTON_HOVER if exit_rect.collidepoint(mouse_x, mouse_y) else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, exit_color, exit_rect)
        pygame.draw.rect(self.screen, self.BLACK, exit_rect, 2)
        
        exit_text = self.small_font.render("Çıkış", True, self.WHITE)
        exit_text_rect = exit_text.get_rect(center=exit_rect.center)
        self.screen.blit(exit_text, exit_text_rect)
    
    def _draw_game_over(self):
        """Draw game over overlay with premium styling"""
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw gradient overlay
        for y in range(self.height):
            alpha = 180 - (abs(y - self.height // 2) / (self.height // 2)) * 50
            pygame.draw.line(overlay, (0, 0, 0, int(alpha)), (0, y), (self.width, y))
        
        self.screen.blit(overlay, (0, 0))
        
        # Create a fancy panel for game over message
        panel_rect = pygame.Rect(self.width // 2 - 200, self.height // 2 - 100, 400, 200)
        panel = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        
        # Draw panel with gradient
        for y in range(panel_rect.height):
            alpha = 220 - (y / panel_rect.height) * 40
            pygame.draw.line(panel, (20, 20, 30, int(alpha)), 
                            (0, y), (panel_rect.width, y))
        
        # Add panel outline with gold border
        pygame.draw.rect(panel, self.GOLD, pygame.Rect(0, 0, panel_rect.width, panel_rect.height), 3)
        
        # Add inner border
        pygame.draw.rect(panel, self.SILVER, pygame.Rect(5, 5, panel_rect.width - 10, panel_rect.height - 10), 1)
        
        # Blit panel to screen
        self.screen.blit(panel, panel_rect)
        
        # Draw game over message with shadow
        game_over_shadow = self.big_font.render("OYUN SONA ERDİ", True, self.BLACK)
        game_over_rect_shadow = game_over_shadow.get_rect(center=(self.width // 2 + 3, self.height // 2 - 53))
        self.screen.blit(game_over_shadow, game_over_rect_shadow)
        
        game_over_text = self.big_font.render("OYUN SONA ERDİ", True, self.GOLD)
        game_over_rect = game_over_text.get_rect(center=(self.width // 2, self.height // 2 - 50))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Draw decorative line
        pygame.draw.line(self.screen, self.GOLD, 
                        (self.width // 2 - 150, self.height // 2 - 20),
                        (self.width // 2 + 150, self.height // 2 - 20), 2)
        
        # Draw winner message with glow effect
        winner_text = self.font.render(self.winner_message, True, self.WHITE)
        
        # Add glow effect (multiple layers of progressively more transparent text)
        for offset in range(1, 6, 2):
            glow_text = self.font.render(self.winner_message, True, (200, 200, 50))
            glow_text.set_alpha(100 - offset * 20)
            glow_rect = glow_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(glow_text, (glow_rect.x - offset, glow_rect.y - offset))
            self.screen.blit(glow_text, (glow_rect.x + offset, glow_rect.y - offset))
            self.screen.blit(glow_text, (glow_rect.x - offset, glow_rect.y + offset))
            self.screen.blit(glow_text, (glow_rect.x + offset, glow_rect.y + offset))
        
        winner_rect = winner_text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(winner_text, winner_rect)
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Draw buttons with improved styling
        menu_rect = pygame.Rect(self.width // 2 - 120, self.height // 2 + 40, 70, 30)
        restart_rect = pygame.Rect(self.width // 2 - 30, self.height // 2 + 40, 70, 30)
        exit_rect = pygame.Rect(self.width // 2 + 60, self.height // 2 + 40, 70, 30)
        
        button_rects = [menu_rect, restart_rect, exit_rect]
        button_texts = ["Ana Menü", "Yeniden", "Çıkış"]
        
        for i, (rect, text) in enumerate(zip(button_rects, button_texts)):
            is_hovered = rect.collidepoint(mouse_x, mouse_y)
            color = self.BUTTON_HOVER if is_hovered else self.BUTTON_COLOR
            
            # Button shadow
            shadow_rect = rect.copy()
            shadow_rect.x += 2
            shadow_rect.y += 2
            pygame.draw.rect(self.screen, (0, 0, 0, 150), shadow_rect)
            
            # Button background
            pygame.draw.rect(self.screen, color, rect)
            
            # Button border
            border_color = self.GOLD if is_hovered else self.SILVER
            pygame.draw.rect(self.screen, border_color, rect, 2)
            
            # Button text
            btn_text = self.small_font.render(text, True, self.WHITE)
            
            if is_hovered:
                # Add glow to text when hovered
                glow_surf = pygame.Surface((btn_text.get_width() + 10, btn_text.get_height() + 10), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (255, 255, 200, 30), (0, 0, glow_surf.get_width(), glow_surf.get_height()))
                glow_rect = glow_surf.get_rect(center=rect.center)
                self.screen.blit(glow_surf, glow_rect)
            
            btn_text_rect = btn_text.get_rect(center=rect.center)
            self.screen.blit(btn_text, btn_text_rect)
    
    def _draw_obstacle_stacks(self):
        """Draw stacks of red obstacle pieces on sides of the board"""
        # Calculate positions for the obstacle stacks
        left_stack_x = self.board_left - self.square_size - 10
        right_stack_x = self.board_left + self.board_size * self.square_size + 10
        stack_y = self.board_top + (self.board_size * self.square_size - 200) // 2
        
        # Draw outlines for obstacle stacks
        stack_rect_left = pygame.Rect(left_stack_x, stack_y, self.square_size, 200)
        stack_rect_right = pygame.Rect(right_stack_x, stack_y, self.square_size, 200)
        
        pygame.draw.rect(self.screen, self.BLACK, stack_rect_left, 2)
        pygame.draw.rect(self.screen, self.WHITE, stack_rect_left, 1)  # Inner border
        pygame.draw.rect(self.screen, self.BLACK, stack_rect_right, 2)
        pygame.draw.rect(self.screen, self.WHITE, stack_rect_right, 1)  # Inner border
        
        # Add stack labels
        black_label = self.small_font.render("Siyah", True, self.BLACK)
        white_label = self.small_font.render("Beyaz", True, self.BLACK)
        
        self.screen.blit(black_label, (left_stack_x + 5, stack_y - 25))
        self.screen.blit(white_label, (right_stack_x + 5, stack_y - 25))
        
        # Draw obstacles on left side for BLACK player
        for i in range(min(10, self.black_obstacles)):
            y_offset = stack_y + 10 + (i * 15)
            rect = pygame.Rect(
                left_stack_x + 5,
                y_offset,
                self.square_size - 10,
                10
            )
            pygame.draw.rect(self.screen, self.RED, rect)
            pygame.draw.rect(self.screen, (150, 0, 0), rect, 1)  # Border
        
        # If more than 10 obstacles, show numbers
        if self.black_obstacles > 10:
            remaining_text = self.small_font.render(f"+{self.black_obstacles - 10}", True, self.BLACK)
            self.screen.blit(remaining_text, (left_stack_x + 10, stack_y + 170))
        
        # Draw obstacles on right side for WHITE player
        for i in range(min(10, self.white_obstacles)):
            y_offset = stack_y + 10 + (i * 15)
            rect = pygame.Rect(
                right_stack_x + 5,
                y_offset,
                self.square_size - 10,
                10
            )
            pygame.draw.rect(self.screen, self.RED, rect)
            pygame.draw.rect(self.screen, (150, 0, 0), rect, 1)  # Border
        
        # If more than 10 obstacles, show numbers
        if self.white_obstacles > 10:
            remaining_text = self.small_font.render(f"+{self.white_obstacles - 10}", True, self.BLACK)
            self.screen.blit(remaining_text, (right_stack_x + 10, stack_y + 170))
        
        # Draw obstacle count text
        count_text = self.small_font.render(f"Engel Taşları", True, self.BLACK)
        self.screen.blit(count_text, (self.width // 2 - 45, self.height - 60))
        
        # Draw individual counts
        black_count = self.small_font.render(f"Siyah: {self.black_obstacles}", True, self.BLACK)
        white_count = self.small_font.render(f"Beyaz: {self.white_obstacles}", True, self.BLACK)
        
        self.screen.blit(black_count, (self.width // 2 - 100, self.height - 30))
        self.screen.blit(white_count, (self.width // 2 + 20, self.height - 30))
    
    def _draw_pieces_and_obstacles(self):
        """Draw the pieces and obstacles with premium styling"""
        for row in range(self.board_size):
            for col in range(self.board_size):
                cell = self.game.board.grid[row][col]
                if cell:
                    screen_x, screen_y = self._board_to_screen(col, row)
                    center_x = screen_x + self.square_size // 2
                    center_y = screen_y + self.square_size // 2
                    
                    # Skip drawing a piece if it's currently being animated
                    if (self.animation_active and 
                        ((cell == 'B' and self.animation_piece == 'B' and (row, col) == self.animation_start) or
                        (cell == 'W' and self.animation_piece == 'W' and (row, col) == self.animation_start))):
                        continue
                    
                    if cell == 'B':  # Black piece
                        # Draw shadow
                        pygame.draw.circle(self.screen, (50, 50, 50), (center_x + 3, center_y + 3), self.square_size // 3)
                        
                        # Draw the piece with gradient effect
                        radius = self.square_size // 3
                        for r in range(radius, 0, -1):
                            # Gradient from dark gray to black
                            color = max(0, 50 - r)
                            pygame.draw.circle(self.screen, (color, color, color), (center_x, center_y), r)
                        
                        # Draw highlight
                        highlight_pos = (center_x - radius // 3, center_y - radius // 3)
                        pygame.draw.circle(self.screen, (100, 100, 100), highlight_pos, radius // 4)
                        
                        # Draw rim
                        pygame.draw.circle(self.screen, (70, 70, 70), (center_x, center_y), radius, 2)
                        
                    elif cell == 'W':  # White piece
                        # Draw shadow
                        pygame.draw.circle(self.screen, (50, 50, 50), (center_x + 3, center_y + 3), self.square_size // 3)
                        
                        # Draw the piece with gradient effect
                        radius = self.square_size // 3
                        for r in range(radius, 0, -1):
                            # Gradient from light gray to white
                            color = min(255, 200 + r)
                            pygame.draw.circle(self.screen, (color, color, color), (center_x, center_y), r)
                        
                        # Draw outer rim
                        pygame.draw.circle(self.screen, self.BLACK, (center_x, center_y), radius, 2)
                        
                        # Draw inner rim
                        pygame.draw.circle(self.screen, (150, 150, 150), (center_x, center_y), radius - 3, 1)
                        
                        # Draw highlight
                        highlight_pos = (center_x - radius // 3, center_y - radius // 3)
                        pygame.draw.circle(self.screen, (255, 255, 255), highlight_pos, radius // 4)
                        
                    elif cell == 'R':  # Red obstacle
                        # Draw a more elaborate obstacle with shadow and gradient
                        rect_size = self.square_size // 2
                        rect_x = screen_x + self.square_size // 4
                        rect_y = screen_y + self.square_size // 4
                        
                        # Draw shadow
                        shadow_rect = pygame.Rect(rect_x + 3, rect_y + 3, rect_size, rect_size)
                        pygame.draw.rect(self.screen, (50, 20, 20), shadow_rect)
                        
                        # Draw base with gradient
                        obstacle_rect = pygame.Rect(rect_x, rect_y, rect_size, rect_size)
                        
                        for y_offset in range(rect_size):
                            # Gradient from dark red to bright red
                            red_value = 170 + (y_offset / rect_size) * 50
                            pygame.draw.line(self.screen, (int(red_value), 20, 20), 
                                           (rect_x, rect_y + y_offset), 
                                           (rect_x + rect_size, rect_y + y_offset))
                        
                        # Draw border
                        pygame.draw.rect(self.screen, (100, 0, 0), obstacle_rect, 2)
                        
                        # Draw highlight
                        highlight_size = rect_size // 3
                        highlight_rect = pygame.Rect(rect_x + 2, rect_y + 2, highlight_size, highlight_size)
                        
                        # Create a highlight effect
                        s = pygame.Surface((highlight_size, highlight_size), pygame.SRCALPHA)
                        s.fill((255, 100, 100, 100))  # Semi-transparent lighter red
                        self.screen.blit(s, highlight_rect)
        
        # Draw animated piece if active
        if self.animation_active and self.animation_start and self.animation_end:
            start_x, start_y = self.animation_start
            end_x, end_y = self.animation_end
            
            # Calculate current position based on animation progress
            current_x = start_x + (end_x - start_x) * self.animation_progress
            current_y = start_y + (end_y - start_y) * self.animation_progress
            
            # Convert to screen coordinates
            screen_x, screen_y = self._board_to_screen(current_y, current_x)
            center_x = screen_x + self.square_size // 2
            center_y = screen_y + self.square_size // 2
            
            # Draw animated piece with premium effects
            radius = self.square_size // 3
            
            if self.animation_piece == 'B':  # Black piece
                # Draw shadow that follows the piece
                pygame.draw.circle(self.screen, (30, 30, 30, 150), (center_x + 4, center_y + 4), radius)
                
                # Draw the piece with gradient
                for r in range(radius, 0, -1):
                    color = max(0, 50 - r)
                    pygame.draw.circle(self.screen, (color, color, color), (center_x, center_y), r)
                
                # Add highlight
                highlight_pos = (center_x - radius // 3, center_y - radius // 3)
                pygame.draw.circle(self.screen, (100, 100, 100), highlight_pos, radius // 4)
                
                # Add rim
                pygame.draw.circle(self.screen, (70, 70, 70), (center_x, center_y), radius, 2)
                
                # Add motion trail (semi-transparent circles behind the piece)
                trail_length = 5
                for i in range(1, trail_length + 1):
                    # Calculate trail position (further back in the movement path)
                    trail_progress = max(0, self.animation_progress - (i * 0.15))
                    trail_x = start_x + (end_x - start_x) * trail_progress
                    trail_y = start_y + (end_y - start_y) * trail_progress
                    
                    trail_screen_x, trail_screen_y = self._board_to_screen(trail_y, trail_x)
                    trail_center_x = trail_screen_x + self.square_size // 2
                    trail_center_y = trail_screen_y + self.square_size // 2
                    
                    # Draw trail with decreasing opacity
                    trail_alpha = int(100 - (i * 20))
                    if trail_alpha > 0:
                        trail_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                        pygame.draw.circle(trail_surf, (50, 50, 50, trail_alpha), (radius, radius), radius)
                        self.screen.blit(trail_surf, (trail_center_x - radius, trail_center_y - radius))
                
            else:  # White piece
                # Draw shadow
                pygame.draw.circle(self.screen, (30, 30, 30, 150), (center_x + 4, center_y + 4), radius)
                
                # Draw the piece with gradient
                for r in range(radius, 0, -1):
                    color = min(255, 200 + r)
                    pygame.draw.circle(self.screen, (color, color, color), (center_x, center_y), r)
                
                # Draw rims
                pygame.draw.circle(self.screen, self.BLACK, (center_x, center_y), radius, 2)
                pygame.draw.circle(self.screen, (150, 150, 150), (center_x, center_y), radius - 3, 1)
                
                # Draw highlight
                highlight_pos = (center_x - radius // 3, center_y - radius // 3)
                pygame.draw.circle(self.screen, (255, 255, 255), highlight_pos, radius // 4)
                
                # Add motion trail
                trail_length = 5
                for i in range(1, trail_length + 1):
                    # Calculate trail position
                    trail_progress = max(0, self.animation_progress - (i * 0.15))
                    trail_x = start_x + (end_x - start_x) * trail_progress
                    trail_y = start_y + (end_y - start_y) * trail_progress
                    
                    trail_screen_x, trail_screen_y = self._board_to_screen(trail_y, trail_x)
                    trail_center_x = trail_screen_x + self.square_size // 2
                    trail_center_y = trail_screen_y + self.square_size // 2
                    
                    # Draw trail with decreasing opacity
                    trail_alpha = int(100 - (i * 20))
                    if trail_alpha > 0:
                        trail_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                        pygame.draw.circle(trail_surf, (200, 200, 200, trail_alpha), (radius, radius), radius)
                        self.screen.blit(trail_surf, (trail_center_x - radius, trail_center_y - radius))
    
    def _draw_highlights(self):
        """Draw highlighted squares for valid moves"""
        # Highlight the selected piece
        if self.selected_pos and not self.animation_active:
            row, col = self.selected_pos
            screen_x, screen_y = self._board_to_screen(col, row)
            rect = pygame.Rect(screen_x, screen_y, self.square_size, self.square_size)
            pygame.draw.rect(self.screen, self.YELLOW, rect, 3)
        
        # Highlight valid moves
        for pos in self.valid_moves:
            row, col = pos
            screen_x, screen_y = self._board_to_screen(col, row)
            rect = pygame.Rect(screen_x, screen_y, self.square_size, self.square_size)
            pygame.draw.rect(self.screen, self.GREEN, rect, 3)
    
    def _draw_obstacle_preview(self):
        """Draw obstacle preview with premium styling"""
        if self.obstacle_placement_phase and self.obstacle_preview_pos:
            row, col = self.obstacle_preview_pos
            screen_x, screen_y = self._board_to_screen(col, row)
            
            # Draw a more sophisticated semi-transparent red obstacle
            rect_size = self.square_size // 2
            rect_x = screen_x + self.square_size // 4
            rect_y = screen_y + self.square_size // 4
            
            # Create a surface with alpha for the main shape
            s = pygame.Surface((rect_size, rect_size), pygame.SRCALPHA)
            
            # Draw gradient in the surface
            for y_offset in range(rect_size):
                # Gradient from dark red to light red (all semi-transparent)
                red_value = 200 + (y_offset / rect_size) * 55
                alpha = 128 + (y_offset / rect_size) * 30
                pygame.draw.line(s, (int(red_value), 40, 40, int(alpha)), 
                               (0, y_offset), 
                               (rect_size, y_offset))
            
            # Draw border
            pygame.draw.rect(s, (255, 100, 100, 200), pygame.Rect(0, 0, rect_size, rect_size), 2)
            
            # Add pulsating effect
            pulse_value = (math.sin(pygame.time.get_ticks() * 0.01) + 1) / 2  # Value between 0 and 1
            scale_factor = 1.0 + pulse_value * 0.1  # Scale between 1.0 and 1.1
            
            # Scale the surface
            scaled_size = int(rect_size * scale_factor)
            offset = (scaled_size - rect_size) // 2
            scaled_s = pygame.transform.scale(s, (scaled_size, scaled_size))
            
            # Blit to screen with adjusted position for scaling
            self.screen.blit(scaled_s, (rect_x - offset, rect_y - offset))
            
            # Add a highlight effect
            highlight_size = rect_size // 3
            highlight_rect = pygame.Rect(rect_x + 2, rect_y + 2, highlight_size, highlight_size)
            
            h = pygame.Surface((highlight_size, highlight_size), pygame.SRCALPHA)
            h.fill((255, 255, 255, int(70 + pulse_value * 30)))  # Pulsating highlight
            self.screen.blit(h, highlight_rect)
            
            # Add a subtle glow around the preview
            glow_size = rect_size + 10
            glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            
            # Create radial gradient for glow
            for radius in range(glow_size // 2, 0, -1):
                alpha = int(40 * (radius / (glow_size / 2)) * pulse_value)
                pygame.draw.circle(glow_surface, (255, 100, 100, alpha), 
                                 (glow_size // 2, glow_size // 2), radius)
            
            # Blit glow behind the obstacle
            glow_x = rect_x + rect_size // 2 - glow_size // 2
            glow_y = rect_y + rect_size // 2 - glow_size // 2
            self.screen.blit(glow_surface, (glow_x, glow_y))
    
    def _draw_status(self):
        """Draw status and winner messages"""
        # Status message
        status_text = self.font.render(self.status_message, True, self.BLACK)
        self.screen.blit(status_text, (20, 20))
        
        # Current phase if game is not over
        if not self.game.game_over:
            phase_text = self.small_font.render(
                "Engel yerleştirme aşaması" if self.obstacle_placement_phase else "Taş hareket aşaması", 
                True, self.BLACK
            )
            self.screen.blit(phase_text, (20, self.height - 30))
            
            # Current player
            player_text = self.small_font.render(
                f"Sıra: {'Siyah' if self.game.current_player == 'B' else 'Beyaz'} oyuncu", 
                True, self.BLACK
            )
            self.screen.blit(player_text, (self.width - 300, self.height - 30))
        
        # Add indicator if playing against AI
        if self.mode == 'human_vs_ai':
            human_text = self.small_font.render(
                f"Siz: {'Siyah' if self.human_piece == 'B' else 'Beyaz'} taşsınız", 
                True, self.BLACK
            )
            self.screen.blit(human_text, (20, 60))
    
    def _draw_fade_message(self):
        """Draw a message that fades out over time"""
        if self.fade_message:
            # Calculate fade alpha based on time
            current_time = pygame.time.get_ticks()
            elapsed = (current_time - self.fade_timer) / 1000.0  # seconds
            
            if elapsed < self.fade_duration:
                # Start fully opaque and fade out
                alpha = 255 * (1 - elapsed / self.fade_duration)
                
                # Create text surface
                message_text = self.big_font.render(self.fade_message, True, self.BLACK)
                message_rect = message_text.get_rect(center=(self.width // 2, self.height // 2))
                
                # Determine if this is an AI message (contains emoji)
                is_ai_message = any(char in self.fade_message for char in "😊😄😁🙂😎🤔🧐🤨🧠💭😟😬😨😓😰🤩😆🎉👏🎊😏😌🙄😤💪😮😲😱😯😵")
                
                if is_ai_message:
                    # For AI messages, show at the top with speech bubble style
                    message_rect = message_text.get_rect(center=(self.width // 2, 100))
                    
                    # Create a speech bubble
                    bubble_padding = 20
                    bubble_rect = pygame.Rect(
                        message_rect.x - bubble_padding,
                        message_rect.y - bubble_padding,
                        message_rect.width + bubble_padding * 2,
                        message_rect.height + bubble_padding * 2
                    )
                    
                    # Draw bubble background
                    s = pygame.Surface((bubble_rect.width, bubble_rect.height), pygame.SRCALPHA)
                    s.fill((240, 240, 255, int(alpha * 0.9)))
                    pygame.draw.rect(s, (100, 100, 200, int(alpha * 0.8)), 
                                    pygame.Rect(0, 0, bubble_rect.width, bubble_rect.height), 3)
                    
                    # Add a pointer to indicate it's from the AI
                    pointer_points = [
                        (bubble_rect.width // 2 - 10, bubble_rect.height),
                        (bubble_rect.width // 2, bubble_rect.height + 15),
                        (bubble_rect.width // 2 + 10, bubble_rect.height)
                    ]
                    pygame.draw.polygon(s, (240, 240, 255, int(alpha * 0.9)), pointer_points)
                    pygame.draw.polygon(s, (100, 100, 200, int(alpha * 0.8)), pointer_points, 2)
                    
                    self.screen.blit(s, (bubble_rect.x, bubble_rect.y))
                    
                    # Add a pulsating effect for AI messages
                    pulse = (1 + math.sin(pygame.time.get_ticks() * 0.005)) / 2
                    pulse_scale = 1.0 + pulse * 0.05
                    
                    # Scale the message text slightly
                    scaled_width = int(message_text.get_width() * pulse_scale)
                    scaled_height = int(message_text.get_height() * pulse_scale)
                    scaled_text = pygame.transform.scale(message_text, (scaled_width, scaled_height))
                    scaled_text.set_alpha(int(alpha))
                    
                    scaled_rect = scaled_text.get_rect(center=message_rect.center)
                    self.screen.blit(scaled_text, scaled_rect)
                else:
                    # Standard message display (non-AI messages)
                    # Create a surface with alpha for the message
                    s = pygame.Surface((message_text.get_width() + 20, message_text.get_height() + 20), pygame.SRCALPHA)
                    s.fill((255, 255, 255, int(alpha * 0.7)))  # Semi-transparent white background
                    self.screen.blit(s, (message_rect.x - 10, message_rect.y - 10))
                    
                    # Adjust text alpha
                    message_text.set_alpha(int(alpha))
                    self.screen.blit(message_text, message_rect)
            else:
                # Message duration has passed
                self.fade_message = None 
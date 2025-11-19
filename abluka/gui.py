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
    # Colors - Modern Premium Color Scheme
    WHITE = (255, 255, 255)
    BLACK = (15, 15, 25)
    RED = (239, 68, 68)  # Modern kırmızı
    LIGHT_RED = (252, 165, 165)
    GRAY = (243, 244, 246)
    DARK_GRAY = (31, 41, 55)
    LIGHT_BLUE = (59, 130, 246)
    GREEN = (34, 197, 94)  # Canlı yeşil
    YELLOW = (251, 191, 36)
    MENU_BG = (17, 24, 39)  # Daha koyu ve modern
    BUTTON_COLOR = (55, 65, 81)
    BUTTON_HOVER = (75, 85, 99)
    GOLD = (251, 191, 36)  # Daha modern altın
    SILVER = (203, 213, 225)
    BRONZE = (180, 83, 9)
    BOARD_BG = (249, 250, 251)  # Daha açık tahta
    BOARD_LINES = (71, 85, 105)
    TRANSPARENT_WHITE = (255, 255, 255, 180)
    
    # Yeni renkler
    ACCENT_PRIMARY = (99, 102, 241)  # İndigo
    ACCENT_SECONDARY = (139, 92, 246)  # Mor
    SUCCESS = (16, 185, 129)
    WARNING = (245, 158, 11)
    DANGER = (239, 68, 68)
    
    def __init__(self, width=1000, height=950):
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
        self.animation_speed = 0.25  # Daha hızlı animasyon (0.25 saniye)
        self.animation_timer = 0
        self.animation_easing = 'ease_out'  # Animasyon easing tipi
        
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
        
        # AI'nın engel yerleştirme pozisyonu
        self.ai_obstacle_pos = None
        
        # AI düşünme animasyonu için değişkenler
        self.thinking_dots = 0
        self.thinking_timer = 0
        self.thinking_dots_update_interval = 400  # ms
    
    def initialize_game(self, mode, difficulty='normal'):
        """Initialize a new game with the given mode and difficulty"""
        self.sound_manager.play('game_start')
        
        self.mode = mode
        self.difficulty = difficulty
        self.game = Game()
        self.show_menu = False
        
        # Tahta boyutunu belirle
        self.board_size = self.game.board.size
        # Daha büyük bir tahta için daha küçük bölücü
        self.square_size = int(min(self.width, self.height) // (self.board_size + 1.8))  # Tahtayı büyüt
        
        # Tahtayı status panel altına yerleştir, ama daha aşağıda
        self.board_left = (self.width - self.square_size * self.board_size) // 2
        self.board_top = 80  # Üst bilgi paneli için daha fazla alan
        
        # Game state tracking
        self.selected_pos = None
        self.valid_moves = []
        self.move_made = False
        self.obstacle_placement_phase = False
        self.highlighted_square = None
        self.obstacle_preview_pos = None
        self.ai_thinking = False
        self.ai_obstacle_pos = None
        
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
                # AI hamlesi için zamanlayıcı ile tetikle
                pygame.time.set_timer(pygame.USEREVENT, 500)  # 500ms sonra
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
                
                # Özel olay: AI hamlesi için
                elif event.type == pygame.USEREVENT:
                    pygame.time.set_timer(pygame.USEREVENT, 0)  # Timer'ı sıfırla
                    self.ai_thinking = True  # AI düşünmeyi başlat
                
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
                raw_progress = min(elapsed / self.animation_speed, 1.0)
                
                # Easing function - ease out cubic için daha yumuşak hareket
                if self.animation_easing == 'ease_out':
                    self.animation_progress = 1 - (1 - raw_progress) ** 3
                elif self.animation_easing == 'ease_in_out':
                    if raw_progress < 0.5:
                        self.animation_progress = 4 * raw_progress ** 3
                    else:
                        self.animation_progress = 1 - (-2 * raw_progress + 2) ** 3 / 2
                else:  # linear
                    self.animation_progress = raw_progress
                
                if self.animation_progress >= 1.0:
                    # Animation complete
                    self.animation_active = False
                    # Complete the move
                    if self.animation_piece and self.animation_end:
                        piece = self.animation_piece
                        self.game.board.move_piece(piece, self.animation_end)
                        
                        # AI hamlesi ise engel yerleştirmeyi de hemen yap
                        if hasattr(self, 'ai_obstacle_pos') and self.ai_obstacle_pos and self.mode == 'human_vs_ai' and piece != self.human_piece:
                            obstacle_pos = self.ai_obstacle_pos
                            self.ai_obstacle_pos = None
                            
                            # Engeli yerleştir
                            self.game.board.place_obstacle(obstacle_pos)
                            self.sound_manager.play('place_obstacle')
                            
                            # Obstacle sayısını azalt
                            if piece == 'B':
                                self.black_obstacles -= 1
                            else:
                                self.white_obstacles -= 1
                                
                            # Oyun durumunu kontrol et
                            opponent = 'W' if piece == 'B' else 'B'
                            if self.game.board.is_abluka(opponent):
                                self.game.game_over = True
                                self.game.winner = piece
                                self.winner_message = f"{'Siyah' if piece == 'B' else 'Beyaz'} oyuncu (AI) kazandı!"
                                self.status_message = "Oyun sona erdi!"
                                self.sound_manager.play('game_win')
                            else:
                                # Sırayı değiştir
                                self.game.switch_player()
                                
                                # Yeni oyuncu ablukada mı kontrol et
                                if self.game.board.is_abluka(self.game.current_player):
                                    self.game.game_over = True
                                    self.game.winner = opponent
                                    self.winner_message = f"{'Siyah' if opponent == 'B' else 'Beyaz'} oyuncu kazandı!"
                                    self.status_message = "Oyun sona erdi!"
                                    self.sound_manager.play('game_win')
                                else:
                                    self.status_message = f"{'Siyah' if self.game.current_player == 'B' else 'Beyaz'}'ın sırası."
                                    
                            # Engel fazını atla, direk insan oyuncunun sırası
                            self.obstacle_placement_phase = False
                        else:
                            # Normal insan oyuncunun hamlesi
                            self.move_made = True
                            self.obstacle_placement_phase = True
                            self.status_message = "Engel taşı yerleştirin."
                            
                        self.selected_pos = None
                        self.valid_moves = []
            
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
                button_width = 80
                button_height = 30
                button_spacing = 10
                button_top = 10
                
                menu_rect = pygame.Rect(self.width - 3*button_width - 2*button_spacing - 20, button_top, button_width, button_height)
                restart_rect = pygame.Rect(self.width - 2*button_width - button_spacing - 20, button_top, button_width, button_height)
                exit_rect = pygame.Rect(self.width - button_width - 20, button_top, button_width, button_height)
                
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
            # Place the obstacle - HEMEN YERLEŞTİR
            self.sound_manager.play('place_obstacle')
            self.game.board.place_obstacle(obstacle_pos)
            
            # Decrease obstacle count (visual only)
            if self.game.current_player == 'B':
                self.black_obstacles -= 1
            else:
                self.white_obstacles -= 1
            
            # İnsan oyuncunun hamlesini detaylı logla
            human_player = self.game.current_player
            human_move = (self.animation_end[0], self.animation_end[1]) if self.animation_end else None
            
            # Konsolda insan hamlesini logla
            print(f"\n[INSAN] {human_player} oyuncusu (İnsan) hamle yaptı:")
            print(f"[INSAN] Taş hareketi: {human_move}, Engel: {obstacle_pos}")
            
            # Eğer AI varsa tahta durumunu ve istatistikleri yazdır
            if self.ai_player:
                # Mevcut tahtayı değerlendir
                opponent = 'W' if human_player == 'B' else 'B'
                
                # İnsan ve AI'nın hamle sayılarını yazdır
                human_moves = len(self.game.board.get_valid_moves(human_player))
                ai_moves = len(self.game.board.get_valid_moves(opponent))
                print(f"[INSAN] Hamleden sonra hamle sayısı: {human_moves}")
                print(f"[INSAN] AI'nın hamle sayısı: {ai_moves}")
                
                # İnsan hamlesi sonrası kazanma olasılığını hesapla
                win_prob = self.ai_player._calculate_win_probability(self.game.board, human_player)
                print(f"[INSAN] Tahmini kazanma olasılığı: %{win_prob:.1f}")
                
                # Etrafındaki engel sayısını göster
                human_pos = self.game.board.black_pos if human_player == 'B' else self.game.board.white_pos
                ai_pos = self.game.board.black_pos if opponent == 'B' else self.game.board.white_pos
                
                human_obstacles = self.ai_player._count_surrounding_obstacles(self.game.board, human_pos)
                ai_obstacles = self.ai_player._count_surrounding_obstacles(self.game.board, ai_pos)
                
                print(f"[INSAN] Etraftaki engeller: İnsan: {human_obstacles}, AI: {ai_obstacles}")
                
                # Log dosyasına kaydet
                self.ai_player._log_move('Human', human_move, obstacle_pos, 
                                       f"İnsan oyuncu hamlesi - Kazanma olasılığı: %{win_prob:.1f}", 
                                       self.game.board)
            
            # Check if game is over
            opponent = 'W' if self.game.current_player == 'B' else 'B'
            if self.game.board.is_abluka(opponent):
                self.game.game_over = True
                self.game.winner = self.game.current_player
                self.winner_message = f"{'Siyah' if self.game.current_player == 'B' else 'Beyaz'} oyuncu kazandı!"
                self.status_message = "Oyun sona erdi!"
                self.sound_manager.play('game_win')
                
                # Oyun sonucunu logla
                print(f"\n[OYUN SONUCU] {self.game.current_player} oyuncu (İnsan) kazandı!")
                
                # AI öğrenmesi için game_over olayı gönder
                if self.ai_player and hasattr(self.ai_player, 'game_over_update'):
                    ai_player = opponent  # AI'nın taşı
                    self.ai_player.game_over_update(self.game.winner, ai_player)
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
                    
                    # Oyun sonucunu logla
                    print(f"\n[OYUN SONUCU] {opponent} oyuncu ({'İnsan' if self.human_piece == opponent else 'AI'}) kazandı!")
                    
                    # AI öğrenmesi için game_over olayı gönder
                    if self.ai_player and hasattr(self.ai_player, 'game_over_update'):
                        ai_player = self.game.current_player if self.human_piece != self.game.current_player else opponent
                        self.ai_player.game_over_update(self.game.winner, ai_player)
                else:
                    self.status_message = f"{'Siyah' if self.game.current_player == 'B' else 'Beyaz'}'ın sırası."
                    
                    # AI hamlesini kısa bir beklemeden sonra yap
                    if (self.mode == 'human_vs_ai' and 
                        self.game.current_player != self.human_piece):
                        # Çok kısa bir süre sonra AI'yı tetikle
                        pygame.time.set_timer(pygame.USEREVENT, 300)  # 300ms bekle
            
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
            # AI hamlesini almadan önce düşünme animasyonunu göster
            self.screen.fill(self.MENU_BG)
            self._draw()
            pygame.display.flip()
            
            # Get AI's move
            game_state = self.game.get_game_state()
            move_pos, obstacle_pos = self.ai_player.choose_move(game_state)
            
            # AI'dan mesaj alıp göster (emoji ve metin)
            ai_message = self.ai_player.get_reaction()
            if ai_message:
                self.fade_message = ai_message
                self.fade_timer = pygame.time.get_ticks()
                self.fade_duration = 3.0  # Biraz daha uzun göster
            
            if move_pos and obstacle_pos:
                # Set AI thinking to false after getting move
                self.ai_thinking = False
                
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
                
                # Engel yerleştirme bilgisini sakla, taş hareketi tamamlanınca kullanılacak
                self.ai_obstacle_pos = obstacle_pos
            else:
                # AI couldn't make a move
                self.ai_thinking = False
                self.game.game_over = True
                self.game.winner = self.human_piece
                self.winner_message = f"{'Siyah' if self.human_piece == 'B' else 'Beyaz'} oyuncu (İnsan) kazandı!"
                self.status_message = "AI hamle yapamadı!"
                self.sound_manager.play('game_win')
    
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
            "Developer: Ubden®"
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
        """Draw the game screen"""
        self.screen.fill(self.MENU_BG)
        
        # Draw navigational buttons at top - first so they don't overlap
        if self.show_nav_buttons:
            self._draw_navigation_buttons()
            
        # Draw the board background
        self._draw_board()
        
        # Draw obstacles and pieces
        self._draw_obstacle_stacks()
        self._draw_pieces_and_obstacles()
        
        # Draw highlighted squares and valid moves
        self._draw_highlights()
        
        # Draw obstacle preview
        if self.obstacle_placement_phase:
            self._draw_obstacle_preview()
        
        # Draw Status - after everything else
        self._draw_status()
        
        
        # Draw AI thinking animation
        if self.ai_thinking and not self.animation_active:
            self._draw_thinking_animation()
        
        # Draw game over message
        if self.game.game_over:
            self._draw_game_over()
        
        # Draw fading message if exists
        if self.fade_message:
            self._draw_fade_message()
            
    
    def _draw_thinking_animation(self):
        """Draw AI thinking animation in the center of the screen"""
        current_time = pygame.time.get_ticks()
        
        # Update thinking dots animation
        if current_time - self.thinking_timer > self.thinking_dots_update_interval:
            self.thinking_dots = (self.thinking_dots + 1) % 4
            self.thinking_timer = current_time
        
        # Create thinking text with animated dots
        dots = "." * self.thinking_dots
        thinking_text = f"AI Düşünüyor{dots}"
        
        # Create a semi-transparent background for the thinking indicator
        indicator_width = 200
        indicator_height = 50
        indicator_x = (self.width - indicator_width) // 2
        indicator_y = (self.height - indicator_height) // 2
        
        # Draw semi-transparent overlay for entire screen
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 50))
        self.screen.blit(overlay, (0, 0))
        
        # Draw thinking panel with glow effect
        panel_glow_surf = pygame.Surface((indicator_width + 20, indicator_height + 20), pygame.SRCALPHA)
        glow_alpha = int(150 + 100 * (math.sin(current_time / 300) * 0.5 + 0.5))  # Pulsating glow
        panel_glow_surf.fill((self.GOLD[0], self.GOLD[1], self.GOLD[2], 40))
        panel_glow_rect = panel_glow_surf.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(panel_glow_surf, panel_glow_rect)
        
        # Draw main panel
        s = pygame.Surface((indicator_width, indicator_height), pygame.SRCALPHA)
        s.fill((30, 30, 30, 220))
        self.screen.blit(s, (indicator_x, indicator_y))
        pygame.draw.rect(self.screen, self.GOLD, (indicator_x, indicator_y, indicator_width, indicator_height), 2)
        
        # Draw the thinking text
        text_surface = self.font.render(thinking_text, True, self.WHITE)
        text_rect = text_surface.get_rect(center=(indicator_x + indicator_width // 2, indicator_y + indicator_height // 2))
        self.screen.blit(text_surface, text_rect)
        
        # Draw animated spinner
        spinner_radius = 15
        spinner_center = (indicator_x + indicator_width // 2, indicator_y + indicator_height + 25)
        
        # Draw spinner background
        spinner_bg = pygame.Surface((spinner_radius * 2 + 10, spinner_radius * 2 + 10), pygame.SRCALPHA)
        spinner_bg.fill((30, 30, 30, 180))
        pygame.draw.circle(spinner_bg, self.GOLD, (spinner_radius + 5, spinner_radius + 5), spinner_radius + 5, 1)
        spinner_bg_rect = spinner_bg.get_rect(center=spinner_center)
        self.screen.blit(spinner_bg, spinner_bg_rect)
        
        # Draw spinning dots
        for i in range(8):
            dot_angle = (current_time / 100) + (i * math.pi / 4)
            dot_x = spinner_center[0] + int(spinner_radius * math.cos(dot_angle))
            dot_y = spinner_center[1] + int(spinner_radius * math.sin(dot_angle))
            
            # Fade the dots based on their position in the rotation
            alpha = 255 - (i * 30)
            alpha = max(50, min(255, alpha))
            
            # Draw glow
            glow_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (self.GOLD[0], self.GOLD[1], self.GOLD[2], 50), (5, 5), 5)
            self.screen.blit(glow_surf, (dot_x - 5, dot_y - 5))
            
            # Draw dot
            pygame.draw.circle(self.screen, self.GOLD, (dot_x, dot_y), 3)
    
    def _draw_board(self):
        """Modern ve şık tahta çizimi"""
        # Calculate board size and position (centered)
        board_width = self.board_size * self.square_size
        board_height = board_width
        
        # Daha belirgin gölge efekti
        shadow_offset = 10
        shadow_rect = pygame.Rect(
            self.board_left - 25 + shadow_offset, 
            self.board_top - 25 + shadow_offset, 
            board_width + 50, 
            board_height + 50
        )
        
        # Çok katmanlı gölge (depth effect)
        for i in range(3):
            offset = shadow_offset - i * 3
            alpha = 60 - i * 15
            s_rect = pygame.Rect(
                self.board_left - 25 + offset,
                self.board_top - 25 + offset,
                board_width + 50,
                board_height + 50
            )
            s = pygame.Surface((s_rect.width, s_rect.height), pygame.SRCALPHA)
            s.fill((10, 10, 20, alpha))
            self.screen.blit(s, s_rect)
        
        # Ana tahta çerçevesi - gradient background
        board_bg_rect = pygame.Rect(
            self.board_left - 25, 
            self.board_top - 25, 
            board_width + 50, 
            board_height + 50
        )
        
        # Modern gradient - koyu kenarlardan açık merkeze
        gradient_surf = pygame.Surface((board_bg_rect.width, board_bg_rect.height))
        for y in range(board_bg_rect.height):
            # Radial gradient effect simülasyonu
            center_dist = abs(y - board_bg_rect.height / 2) / (board_bg_rect.height / 2)
            color_val = int(45 + (1 - center_dist) * 35)
            pygame.draw.line(gradient_surf, (color_val, color_val, color_val + 10), 
                            (0, y), (board_bg_rect.width, y))
        
        self.screen.blit(gradient_surf, board_bg_rect)
        
        # Modern çerçeve - çift kenarlık
        pygame.draw.rect(self.screen, self.GOLD, board_bg_rect, 3, border_radius=8)
        inner_rect = pygame.Rect(
            board_bg_rect.x + 4,
            board_bg_rect.y + 4,
            board_bg_rect.width - 8,
            board_bg_rect.height - 8
        )
        pygame.draw.rect(self.screen, self.DARK_GRAY, inner_rect, 1, border_radius=6)
        
        # Dekoratif köşe aksentleri - daha büyük ve belirgin
        corner_size = 20
        corner_thickness = 4
        corners = [
            (board_bg_rect.left, board_bg_rect.top),
            (board_bg_rect.right, board_bg_rect.top),
            (board_bg_rect.left, board_bg_rect.bottom),
            (board_bg_rect.right, board_bg_rect.bottom)
        ]
        
        for i, (x, y) in enumerate(corners):
            if i == 0:  # Top-left
                pygame.draw.line(self.screen, self.ACCENT_PRIMARY, 
                               (x, y + corner_size), (x, y), corner_thickness)
                pygame.draw.line(self.screen, self.ACCENT_PRIMARY, 
                               (x, y), (x + corner_size, y), corner_thickness)
            elif i == 1:  # Top-right
                pygame.draw.line(self.screen, self.ACCENT_PRIMARY, 
                               (x - corner_size, y), (x, y), corner_thickness)
                pygame.draw.line(self.screen, self.ACCENT_PRIMARY, 
                               (x, y), (x, y + corner_size), corner_thickness)
            elif i == 2:  # Bottom-left
                pygame.draw.line(self.screen, self.ACCENT_PRIMARY, 
                               (x, y - corner_size), (x, y), corner_thickness)
                pygame.draw.line(self.screen, self.ACCENT_PRIMARY, 
                               (x, y), (x + corner_size, y), corner_thickness)
            else:  # Bottom-right
                pygame.draw.line(self.screen, self.ACCENT_PRIMARY, 
                               (x - corner_size, y), (x, y), corner_thickness)
                pygame.draw.line(self.screen, self.ACCENT_PRIMARY, 
                               (x, y - corner_size), (x, y), corner_thickness)
        
        # Oyun tahtası yüzeyi - daha açık ve modern
        board_rect = pygame.Rect(
            self.board_left, 
            self.board_top, 
            board_width, 
            board_height
        )
        
        # Alternatif karo deseni (satranç tahtası tarzı) - çok subtle
        for row in range(self.board_size):
            for col in range(self.board_size):
                x = self.board_left + col * self.square_size
                y = self.board_top + row * self.square_size
                
                # Alternatif renk (çok hafif fark)
                if (row + col) % 2 == 0:
                    color = (249, 250, 251)
                else:
                    color = (243, 244, 246)
                
                pygame.draw.rect(self.screen, color, 
                               (x, y, self.square_size, self.square_size))
        
        # Grid çizgileri - ince ve modern
        for i in range(self.board_size + 1):
            # Dış çizgiler daha kalın
            line_width = 2 if i == 0 or i == self.board_size else 1
            line_color = self.BOARD_LINES if line_width == 1 else self.DARK_GRAY
            
            # Dikey çizgiler
            start_pos = (self.board_left + i * self.square_size, self.board_top)
            end_pos = (self.board_left + i * self.square_size, self.board_top + board_height)
            pygame.draw.line(self.screen, line_color, start_pos, end_pos, line_width)
            
            # Yatay çizgiler
            start_pos = (self.board_left, self.board_top + i * self.square_size)
            end_pos = (self.board_left + board_width, self.board_top + i * self.square_size)
            pygame.draw.line(self.screen, line_color, start_pos, end_pos, line_width)
        
        # Merkez noktası vurgusu
        center = self.board_size // 2
        center_x = self.board_left + center * self.square_size + self.square_size // 2
        center_y = self.board_top + center * self.square_size + self.square_size // 2
        
        # Merkez işareti - ışıldayan efekt
        for radius in [6, 4, 2]:
            alpha = 255 - (6 - radius) * 40
            glow = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*self.ACCENT_SECONDARY[:3], alpha), 
                             (radius + 2, radius + 2), radius)
            self.screen.blit(glow, (center_x - radius - 2, center_y - radius - 2))
        
        # Koordinat işaretleri - modern font
        for i in range(self.board_size):
            # Sütun numaraları
            text = self.small_font.render(str(i), True, self.SILVER)
            text_rect = text.get_rect(center=(
                self.board_left + i * self.square_size + self.square_size // 2,
                self.board_top - 15
            ))
            self.screen.blit(text, text_rect)
            
            # Satır harfleri
            text = self.small_font.render(chr(65 + i), True, self.SILVER)
            text_rect = text.get_rect(center=(
                self.board_left - 15,
                self.board_top + i * self.square_size + self.square_size // 2
            ))
            self.screen.blit(text, text_rect)
    
    def _draw_navigation_buttons(self):
        """Draw navigation buttons (menu, restart, exit)"""
        if not self.game:
            return
            
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Position buttons at the top right corner
        button_width = 80
        button_height = 30
        button_spacing = 10
        button_top = 10
        
        # Menu button
        menu_rect = pygame.Rect(self.width - 3*button_width - 2*button_spacing - 20, button_top, button_width, button_height)
        menu_color = self.BUTTON_HOVER if menu_rect.collidepoint(mouse_x, mouse_y) else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, menu_color, menu_rect)
        pygame.draw.rect(self.screen, self.BLACK, menu_rect, 2)
        
        menu_text = self.small_font.render("Ana Menü", True, self.WHITE)
        menu_text_rect = menu_text.get_rect(center=menu_rect.center)
        self.screen.blit(menu_text, menu_text_rect)
        
        # Restart button
        restart_rect = pygame.Rect(self.width - 2*button_width - button_spacing - 20, button_top, button_width, button_height)
        restart_color = self.BUTTON_HOVER if restart_rect.collidepoint(mouse_x, mouse_y) else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, restart_color, restart_rect)
        pygame.draw.rect(self.screen, self.BLACK, restart_rect, 2)
        
        restart_text = self.small_font.render("Yeniden", True, self.WHITE)
        restart_text_rect = restart_text.get_rect(center=restart_rect.center)
        self.screen.blit(restart_text, restart_text_rect)
        
        # Exit button
        exit_rect = pygame.Rect(self.width - button_width - 20, button_top, button_width, button_height)
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
        
        # AI Öğrenme istatistikleri (eğer varsa)
        if self.mode == 'human_vs_ai' and self.difficulty == 'hard' and self.ai_player and hasattr(self.ai_player, 'get_learning_stats'):
            learning_stats = self.ai_player.get_learning_stats()
            if learning_stats.get("enabled", False):
                self._draw_game_over_learning_stats(learning_stats)
        
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
    
    def _draw_game_over_learning_stats(self, learning_stats):
        """Oyun sonu ekranında öğrenme istatistiklerini gösteren panel"""
        # Panel pozisyonu ve boyutu - ana panelin altında
        panel_width = 400
        panel_height = 120
        panel_x = self.width // 2 - panel_width // 2
        panel_y = self.height // 2 + 100  # Ana panelin altında
        
        # Arkaplan paneli
        s = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        s.fill((30, 30, 40, 200))  # Biraz daha koyu
        self.screen.blit(s, (panel_x, panel_y))
        pygame.draw.rect(self.screen, self.SILVER, (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Başlık
        title_text = self.font.render("Makine Öğrenimi Sonuçları", True, self.GOLD)
        title_rect = title_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 20))
        self.screen.blit(title_text, title_rect)
        
        # Ayırıcı çizgi
        pygame.draw.line(self.screen, self.SILVER, 
                       (panel_x + 20, panel_y + 40), 
                       (panel_x + panel_width - 20, panel_y + 40), 1)
        
        # İstatistikler
        col1_x = panel_x + 30
        col2_x = panel_x + panel_width // 2 + 20
        y_offset = panel_y + 55
        line_height = 22
        
        # Sol kolon istatistikleri
        stats_text = self.small_font.render(f"Toplam Durum Sayısı: {learning_stats['total_states']}", True, self.WHITE)
        self.screen.blit(stats_text, (col1_x, y_offset))
        
        stats_text = self.small_font.render(f"Bu Oyundaki Durumlar: {learning_stats['current_game_states']}", True, self.WHITE)
        self.screen.blit(stats_text, (col1_x, y_offset + line_height))
        
        stats_text = self.small_font.render(f"Son Oyunda Öğrenilen: {len(self.ai_player.q_table) - learning_stats['total_states']}", True, self.WHITE)
        self.screen.blit(stats_text, (col1_x, y_offset + line_height * 2))
        
        # Sağ kolon istatistikleri
        stats_text = self.small_font.render(f"Öğrenme Oranı: {learning_stats['learning_rate']:.2f}", True, self.WHITE)
        self.screen.blit(stats_text, (col2_x, y_offset))
        
        stats_text = self.small_font.render(f"Keşif Oranı: {learning_stats['exploration_rate']:.2f}", True, self.WHITE)
        self.screen.blit(stats_text, (col2_x, y_offset + line_height))
        
        # Hafıza bilgisini göster
        if hasattr(self.ai_player, 'memory_file'):
            memory_text = f"Hafıza: {self.ai_player.memory_file}"
            stats_text = self.small_font.render(memory_text, True, self.SILVER)
            self.screen.blit(stats_text, (col2_x, y_offset + line_height * 2))
    
    def _draw_obstacle_stacks(self):
        """Draw stacks of red obstacle pieces on sides of the board"""
        # Calculate positions for the obstacle stacks - move them further from the board
        stack_width = self.square_size - 5
        stack_height = 300
        
        # Yanlardaki engel pozisyonları - daha da dışa taşı
        left_stack_x = 10  # Daha da sol
        right_stack_x = self.width - stack_width - 10  # Daha da sağ
        
        # Stack height should be centered but not exceed the board bottom
        stack_y = max(130, (self.height - stack_height) // 2)  # Keep distance from top status panel
        
        # Draw stylish panels for obstacle stacks
        for stack_x, player, count in [
            (left_stack_x, 'B', self.black_obstacles),
            (right_stack_x, 'W', self.white_obstacles)
        ]:
            # Draw panel background with gradient
            panel = pygame.Surface((stack_width, stack_height))
            for y in range(stack_height):
                color_val = 30 + int(y / stack_height * 20)
                pygame.draw.line(panel, (color_val, color_val, color_val + 5), 
                               (0, y), (stack_width, y))
            self.screen.blit(panel, (stack_x, stack_y))
            
            # Draw panel border
            pygame.draw.rect(self.screen, self.GOLD, (stack_x, stack_y, stack_width, stack_height), 2)
            pygame.draw.rect(self.screen, self.DARK_GRAY, (stack_x + 2, stack_y + 2, stack_width - 4, stack_height - 4), 1)
            
            # Player label at top
            label_text = "Siyah" if player == 'B' else "Beyaz"
            label = self.font.render(label_text, True, self.WHITE)
            label_rect = label.get_rect(center=(stack_x + stack_width // 2, stack_y + 20))
            
            # Draw label with shadow
            label_shadow = self.font.render(label_text, True, self.BLACK)
            self.screen.blit(label_shadow, (label_rect.x + 1, label_rect.y + 1))
            self.screen.blit(label, label_rect)
            
            # Draw count at bottom
            count_text = f"{count}"
            count_label = self.big_font.render(count_text, True, self.RED)
            count_rect = count_label.get_rect(center=(stack_x + stack_width // 2, stack_y + stack_height - 30))
            
            # Draw count with glow effect
            glow_surf = pygame.Surface((count_label.get_width() + 10, count_label.get_height() + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (255, 100, 100, 30), (0, 0, glow_surf.get_width(), glow_surf.get_height()))
            glow_rect = glow_surf.get_rect(center=count_rect.center)
            self.screen.blit(glow_surf, glow_rect)
            self.screen.blit(count_label, count_rect)
            
            # Draw obstacles visually
            max_display = 15
            display_count = min(max_display, count)
            obstacle_height = 12
            spacing = (stack_height - 100) // max(max_display, 1)
            
            for i in range(display_count):
                y_pos = stack_y + 50 + (i * spacing)
                
                # Obstacle rect
                obs_width = stack_width - 14
                obs_x = stack_x + 7
                
                # Draw obstacle with gradient
                obs_surf = pygame.Surface((obs_width, obstacle_height))
                for y in range(obstacle_height):
                    red_val = 180 + int(y / obstacle_height * 75)
                    pygame.draw.line(obs_surf, (red_val, 20, 20), 
                                   (0, y), (obs_width, y))
                
                self.screen.blit(obs_surf, (obs_x, y_pos))
                pygame.draw.rect(self.screen, (100, 0, 0), (obs_x, y_pos, obs_width, obstacle_height), 1)
                
                # Add highlight
                highlight_width = obs_width // 3
                highlight_height = obstacle_height // 2
                highlight_surf = pygame.Surface((highlight_width, highlight_height), pygame.SRCALPHA)
                highlight_surf.fill((255, 150, 150, 100))
                self.screen.blit(highlight_surf, (obs_x + 2, y_pos + 1))
        
        # "Engel Taşları" başlığını çiz - tablonun alt kısmına
        # Tahtanın altında görünecek şekilde ama daha yukarıda
        board_bottom = self.board_top + (self.board_size * self.square_size)
        title_y = board_bottom + 25  # Tahtanın altında ama yeterince yukarıda
        
        title_text = self.font.render("Engel Taşları", True, self.WHITE)
        title_rect = title_text.get_rect(center=(self.width // 2, title_y))
        
        # Draw title background
        title_bg = pygame.Surface((title_text.get_width() + 20, title_text.get_height() + 10), pygame.SRCALPHA)
        title_bg.fill((30, 30, 30, 180))
        title_bg_rect = title_bg.get_rect(center=title_rect.center)
        pygame.draw.rect(title_bg, self.GOLD, (0, 0, title_bg.get_width(), title_bg.get_height()), 2)
        
        self.screen.blit(title_bg, title_bg_rect)
        self.screen.blit(title_text, title_rect)
    
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
                    
                    if cell == 'B':  # Black piece - Modern 3D tasarım
                        radius = self.square_size // 3
                        
                        # Çok katmanlı gölge (depth)
                        for i in range(3):
                            shadow_offset = 4 - i
                            shadow_alpha = 100 - i * 25
                            shadow_surf = pygame.Surface((radius * 2 + 10, radius * 2 + 10), pygame.SRCALPHA)
                            pygame.draw.circle(shadow_surf, (0, 0, 0, shadow_alpha), 
                                             (radius + 5, radius + 5), radius)
                            self.screen.blit(shadow_surf, 
                                           (center_x - radius - 5 + shadow_offset, 
                                            center_y - radius - 5 + shadow_offset))
                        
                        # Ana taş - realistik gradient
                        for r in range(radius, 0, -1):
                            # Radyal gradient - merkez daha açık
                            progress = r / radius
                            # Koyu siyah dış, biraz açık iç
                            color_val = int(25 + (1 - progress) * 15)
                            pygame.draw.circle(self.screen, (color_val, color_val, color_val), 
                                             (center_x, center_y), r)
                        
                        # Işık efekti (highlight) - üst sol
                        highlight_x = center_x - radius // 3
                        highlight_y = center_y - radius // 3
                        
                        # Çok katmanlı highlight (glow)
                        for i in range(3, 0, -1):
                            h_radius = radius // 4 + i
                            h_alpha = 180 - i * 40
                            h_surf = pygame.Surface((h_radius * 2 + 4, h_radius * 2 + 4), pygame.SRCALPHA)
                            pygame.draw.circle(h_surf, (255, 255, 255, h_alpha), 
                                             (h_radius + 2, h_radius + 2), h_radius)
                            self.screen.blit(h_surf, (highlight_x - h_radius - 2, highlight_y - h_radius - 2))
                        
                        # Dış çerçeve - metalik görünüm
                        pygame.draw.circle(self.screen, (90, 90, 100), (center_x, center_y), radius, 3)
                        pygame.draw.circle(self.screen, (50, 50, 60), (center_x, center_y), radius - 1, 1)
                        
                    elif cell == 'W':  # White piece - Modern 3D tasarım
                        radius = self.square_size // 3
                        
                        # Çok katmanlı gölge
                        for i in range(3):
                            shadow_offset = 4 - i
                            shadow_alpha = 100 - i * 25
                            shadow_surf = pygame.Surface((radius * 2 + 10, radius * 2 + 10), pygame.SRCALPHA)
                            pygame.draw.circle(shadow_surf, (0, 0, 0, shadow_alpha), 
                                             (radius + 5, radius + 5), radius)
                            self.screen.blit(shadow_surf, 
                                           (center_x - radius - 5 + shadow_offset, 
                                            center_y - radius - 5 + shadow_offset))
                        
                        # Ana taş - parlak gradient
                        for r in range(radius, 0, -1):
                            progress = r / radius
                            # Parlak beyaz
                            color_val = int(255 - progress * 25)
                            pygame.draw.circle(self.screen, (color_val, color_val, color_val), 
                                             (center_x, center_y), r)
                        
                        # Işık efekti - çok parlak
                        highlight_x = center_x - radius // 3
                        highlight_y = center_y - radius // 3
                        
                        for i in range(4, 0, -1):
                            h_radius = radius // 3 + i
                            h_alpha = 220 - i * 40
                            h_surf = pygame.Surface((h_radius * 2 + 4, h_radius * 2 + 4), pygame.SRCALPHA)
                            pygame.draw.circle(h_surf, (255, 255, 255, h_alpha), 
                                             (h_radius + 2, h_radius + 2), h_radius)
                            self.screen.blit(h_surf, (highlight_x - h_radius - 2, highlight_y - h_radius - 2))
                        
                        # Dış çerçeveler - kaliteli görünüm
                        pygame.draw.circle(self.screen, self.DARK_GRAY, (center_x, center_y), radius, 3)
                        pygame.draw.circle(self.screen, (180, 180, 190), (center_x, center_y), radius - 2, 1)
                        pygame.draw.circle(self.screen, (200, 200, 210), (center_x, center_y), radius - 4, 1)
                        
                    elif cell == 'R':  # Red obstacle - Modern ve dikkat çekici
                        rect_size = self.square_size // 2
                        rect_x = screen_x + self.square_size // 4
                        rect_y = screen_y + self.square_size // 4
                        
                        # Güçlü gölge
                        for i in range(3):
                            shadow_offset = 5 - i
                            shadow_alpha = 120 - i * 30
                            shadow_surf = pygame.Surface((rect_size + 10, rect_size + 10), pygame.SRCALPHA)
                            shadow_surf.fill((20, 0, 0, shadow_alpha))
                            self.screen.blit(shadow_surf, 
                                           (rect_x - 5 + shadow_offset, rect_y - 5 + shadow_offset))
                        
                        # Ana engel - gradient kırmızı
                        for y_offset in range(rect_size):
                            progress = y_offset / rect_size
                            # Koyu kırmızıdan parlak kırmızıya
                            red_val = int(180 + progress * 75)
                            green_val = int(20 + progress * 50)
                            blue_val = int(20 + progress * 50)
                            pygame.draw.line(self.screen, (red_val, green_val, blue_val), 
                                           (rect_x, rect_y + y_offset), 
                                           (rect_x + rect_size, rect_y + y_offset))
                        
                        # Parlama efekti (highlight)
                        highlight_size = rect_size // 2
                        highlight_surf = pygame.Surface((highlight_size, highlight_size), pygame.SRCALPHA)
                        for y in range(highlight_size):
                            for x in range(highlight_size):
                                # Radyal parlama
                                dist = ((x - highlight_size/2)**2 + (y - highlight_size/2)**2)**0.5
                                max_dist = highlight_size / 2
                                if dist < max_dist:
                                    alpha = int(180 * (1 - dist / max_dist))
                                    highlight_surf.set_at((x, y), (255, 180, 180, alpha))
                        
                        self.screen.blit(highlight_surf, (rect_x + 3, rect_y + 3))
                        
                        # Kalın çerçeve - tehlike işareti
                        pygame.draw.rect(self.screen, (120, 0, 0), 
                                       (rect_x, rect_y, rect_size, rect_size), 3)
                        pygame.draw.rect(self.screen, (200, 50, 50), 
                                       (rect_x + 2, rect_y + 2, rect_size - 4, rect_size - 4), 1)
        
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
                trail_length = 6  # Daha uzun trail
                for i in range(1, trail_length + 1):
                    # Calculate trail position (further back in the movement path)
                    trail_progress = max(0, self.animation_progress - (i * 0.12))
                    trail_x = start_x + (end_x - start_x) * trail_progress
                    trail_y = start_y + (end_y - start_y) * trail_progress
                    
                    trail_screen_x, trail_screen_y = self._board_to_screen(trail_y, trail_x)
                    trail_center_x = trail_screen_x + self.square_size // 2
                    trail_center_y = trail_screen_y + self.square_size // 2
                    
                    # Draw trail with decreasing opacity and size
                    trail_alpha = int(120 - (i * 18))
                    trail_size = int(radius * (1 - i * 0.08))
                    
                    if trail_alpha > 0 and trail_size > 0:
                        trail_surf = pygame.Surface((trail_size * 2 + 4, trail_size * 2 + 4), pygame.SRCALPHA)
                        # Gradient trail
                        for r in range(trail_size, 0, -1):
                            alpha_r = int(trail_alpha * (r / trail_size))
                            pygame.draw.circle(trail_surf, (50, 50, 50, alpha_r), 
                                             (trail_size + 2, trail_size + 2), r)
                        self.screen.blit(trail_surf, 
                                       (trail_center_x - trail_size - 2, 
                                        trail_center_y - trail_size - 2))
                
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
                
                # Add motion trail - parlak beyaz trail
                trail_length = 6
                for i in range(1, trail_length + 1):
                    # Calculate trail position
                    trail_progress = max(0, self.animation_progress - (i * 0.12))
                    trail_x = start_x + (end_x - start_x) * trail_progress
                    trail_y = start_y + (end_y - start_y) * trail_progress
                    
                    trail_screen_x, trail_screen_y = self._board_to_screen(trail_y, trail_x)
                    trail_center_x = trail_screen_x + self.square_size // 2
                    trail_center_y = trail_screen_y + self.square_size // 2
                    
                    # Draw trail with decreasing opacity and size
                    trail_alpha = int(140 - (i * 20))
                    trail_size = int(radius * (1 - i * 0.08))
                    
                    if trail_alpha > 0 and trail_size > 0:
                        trail_surf = pygame.Surface((trail_size * 2 + 4, trail_size * 2 + 4), pygame.SRCALPHA)
                        # Parlak beyaz gradient trail
                        for r in range(trail_size, 0, -1):
                            alpha_r = int(trail_alpha * (r / trail_size))
                            pygame.draw.circle(trail_surf, (230, 230, 240, alpha_r), 
                                             (trail_size + 2, trail_size + 2), r)
                        self.screen.blit(trail_surf, 
                                       (trail_center_x - trail_size - 2, 
                                        trail_center_y - trail_size - 2))
    
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
        """Modern ve kompakt durum paneli"""
        # Ana bilgi paneli - daha kompakt ve şık
        main_panel_width = self.width - 340
        main_panel_height = 40  # Daha yüksek ama daha şık
        main_panel_x = 20
        main_panel_y = 10
        
        # Modern gradient arkaplan
        s = pygame.Surface((main_panel_width, main_panel_height), pygame.SRCALPHA)
        
        # Gradient dolgusu
        for y in range(main_panel_height):
            progress = y / main_panel_height
            r = int(25 + progress * 10)
            g = int(30 + progress * 10)
            b = int(45 + progress * 15)
            alpha = 220
            pygame.draw.line(s, (r, g, b, alpha), (0, y), (main_panel_width, y))
        
        self.screen.blit(s, (main_panel_x, main_panel_y))
        
        # Modern çift çerçeve
        pygame.draw.rect(self.screen, self.ACCENT_PRIMARY, 
                        (main_panel_x, main_panel_y, main_panel_width, main_panel_height), 
                        2, border_radius=6)
        pygame.draw.rect(self.screen, self.GOLD, 
                        (main_panel_x + 2, main_panel_y + 2, main_panel_width - 4, main_panel_height - 4), 
                        1, border_radius=5)
        
        # İçerik - daha iyi düzenlenmiş
        if self.mode == 'human_vs_ai':
            # 3 bölüm: Durum | Oyuncu | Faz
            section_width = main_panel_width // 3
            
            # Ayırıcı çizgiler - gradient
            for i in range(1, 3):
                x = main_panel_x + section_width * i
                # Gradient line
                for y in range(8, main_panel_height - 8):
                    progress = (y - 8) / (main_panel_height - 16)
                    alpha = int(100 + progress * 100 - abs(progress - 0.5) * 100)
                    pygame.draw.line(self.screen, (*self.ACCENT_SECONDARY[:3], alpha), 
                                   (x, main_panel_y + y), (x, main_panel_y + y))
            
            # 1. DURUM (sol)
            status_icon = "●" if self.game.current_player == 'B' else "○"
            player_name = "Siyah" if self.game.current_player == 'B' else "Beyaz"
            status_full = f"{status_icon} {player_name}'ın sırası"
            
            if self.game.game_over:
                status_full = "🏆 Oyun Bitti!"
            
            status_text = self.small_font.render(status_full, True, self.WHITE)
            status_rect = status_text.get_rect(
                center=(main_panel_x + section_width // 2, main_panel_y + main_panel_height // 2)
            )
            self.screen.blit(status_text, status_rect)
            
            # 2. OYUNCU BİLGİSİ (orta)
            piece_icon = "●" if self.human_piece == 'B' else "○"
            piece_name = "Siyah" if self.human_piece == 'B' else "Beyaz"
            human_info = f"{piece_icon} Siz: {piece_name}"
            
            human_text = self.small_font.render(human_info, True, self.GOLD)
            human_rect = human_text.get_rect(
                center=(main_panel_x + section_width + section_width // 2, 
                       main_panel_y + main_panel_height // 2)
            )
            self.screen.blit(human_text, human_rect)
            
            # 3. OYUN FAZI (sağ)
            if not self.game.game_over:
                if self.obstacle_placement_phase:
                    phase_text = "🔴 Engel Yerleştir"
                    phase_color = self.RED
                else:
                    phase_text = "♟ Taş Hareket"
                    phase_color = self.GREEN
            else:
                phase_text = "✓ Tamamlandı"
                phase_color = self.SUCCESS
            
            phase_surface = self.small_font.render(phase_text, True, phase_color)
            phase_rect = phase_surface.get_rect(
                center=(main_panel_x + section_width * 2 + section_width // 2, 
                       main_panel_y + main_panel_height // 2)
            )
            self.screen.blit(phase_surface, phase_rect)
            
        else:
            # İnsan vs İnsan modu - basitleştirilmiş
            # İki bölüm: Durum | Faz
            divider_x = main_panel_x + main_panel_width * 0.6
            
            # Ayırıcı çizgi
            for y in range(8, main_panel_height - 8):
                progress = (y - 8) / (main_panel_height - 16)
                alpha = int(100 + progress * 100 - abs(progress - 0.5) * 100)
                pygame.draw.line(self.screen, (*self.ACCENT_SECONDARY[:3], alpha), 
                               (int(divider_x), main_panel_y + y), 
                               (int(divider_x), main_panel_y + y))
            
            # Durum
            status_icon = "●" if self.game.current_player == 'B' else "○"
            player_name = "Siyah" if self.game.current_player == 'B' else "Beyaz"
            status_text = self.small_font.render(f"{status_icon} {player_name}'ın sırası", 
                                                True, self.WHITE)
            status_rect = status_text.get_rect(
                center=(main_panel_x + main_panel_width * 0.3, 
                       main_panel_y + main_panel_height // 2)
            )
            self.screen.blit(status_text, status_rect)
            
            # Faz
            if not self.game.game_over:
                if self.obstacle_placement_phase:
                    phase_str = "🔴 Engel Yerleştir"
                    p_color = self.RED
                else:
                    phase_str = "♟ Taş Hareket"
                    p_color = self.GREEN
            else:
                phase_str = "✓ Oyun Bitti"
                p_color = self.SUCCESS
            
            phase_text = self.small_font.render(phase_str, True, p_color)
            phase_rect = phase_text.get_rect(
                center=(main_panel_x + main_panel_width * 0.8, 
                       main_panel_y + main_panel_height // 2)
            )
            self.screen.blit(phase_text, phase_rect)
    
    def _draw_fade_message(self):
        """Draw fading message that appears temporarily"""
        current_time = pygame.time.get_ticks()
        elapsed = (current_time - self.fade_timer) / 1000.0
        
        if elapsed < self.fade_duration:
            # Calculate alpha based on elapsed time
            if elapsed < self.fade_duration * 0.3:
                # Fade in
                alpha = int(255 * (elapsed / (self.fade_duration * 0.3)))
            elif elapsed > self.fade_duration * 0.7:
                # Fade out
                alpha = int(255 * (1 - (elapsed - self.fade_duration * 0.7) / (self.fade_duration * 0.3)))
            else:
                # Stay fully visible
                alpha = 255
            
            # Create a semi-transparent panel for the message
            panel_width = min(500, self.width - 40)
            panel_height = 60
            panel_x = (self.width - panel_width) // 2
            panel_y = self.height - panel_height - 20
            
            s = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
            s.fill((30, 30, 30, min(200, alpha)))
            self.screen.blit(s, (panel_x, panel_y))
            
            # Draw golden border that pulses
            pulse_intensity = math.sin(current_time / 200) * 0.5 + 0.5  # 0.0 to 1.0
            border_color = (
                self.GOLD[0],
                int(self.GOLD[1] * (0.7 + 0.3 * pulse_intensity)),
                int(self.GOLD[2] * (0.7 + 0.3 * pulse_intensity)),
                alpha
            )
            pygame.draw.rect(self.screen, border_color, (panel_x, panel_y, panel_width, panel_height), 2)
            
            # Draw the message text with shadow effect
            text = self.font.render(self.fade_message, True, (255, 255, 255, alpha))
            text_rect = text.get_rect(center=(self.width // 2, panel_y + panel_height // 2))
            
            # Draw text shadow
            shadow_surface = self.font.render(self.fade_message, True, (0, 0, 0, alpha))
            shadow_rect = shadow_surface.get_rect(center=(text_rect.centerx + 2, text_rect.centery + 2))
            self.screen.blit(shadow_surface, shadow_rect)
            
            # Draw actual text
            self.screen.blit(text, text_rect)
        else:
            # Message duration expired
            self.fade_message = None
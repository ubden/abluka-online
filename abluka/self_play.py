import sys
import os
import time
import pygame
import random
import datetime
import argparse
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import numpy as np

from abluka.game_logic import Game, Board
from abluka.ai_player import AIPlayer

class AblukaSelfPlay:
    """
    Abluka AI Self-Play Eğitim Modülü (hard => Q-learning).
    Rastgele açılış + ilk renk => daha dengeli öğrenme.
    """

    # Renkler
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (100, 100, 100)
    DARK_GRAY = (50, 50, 50)
    LIGHT_GRAY = (150, 150, 150)
    GOLD = (212, 175, 55)
    SILVER = (192, 192, 192)
    GREEN = (0, 180, 0)
    RED = (180, 0, 0)
    BLUE = (0, 0, 180)
    
    def __init__(self, width=800, height=600, game_count=100):
        """Abluka Self-Play Arayüzü."""
        self.width = width
        self.height = height
        self.game_count = game_count
        self.running = False
        self.paused = False
        
        # Pygame başlat
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Abluka AI Self-Play Eğitimi")
        self.clock = pygame.time.Clock()
        
        # Fontlar
        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 16)
        self.large_font = pygame.font.SysFont('Arial', 32)
        
        # AI oyuncusu (hard => Q-learning)
        self.ai_player = AIPlayer(difficulty='hard')
        
        # İstatistikler
        self.stats = {
            'game_count': 0,           # Kaç maç oynandı
            'total_games': self.game_count,
            'black_wins': 0,
            'white_wins': 0,
            'q_values': [],            # Ort. Q kaydı
            'states_count': [],        # Q tablo boyutu
            'new_states': [],
            'win_rates': [],
            'started_at': time.time(),
            'games_per_sec': 0,
            'eta': 0,
            'exploration_history': []  # Her raporda exploration
        }
        
        # Grafikler
        self.last_plot_update = 0
        self.plot_interval = 5  # her 5sn grafiği güncelle
        self.q_values_plot = None
        self.states_plot = None
        self.winrate_plot = None
        
        # Eğitim kontrol
        self.training_thread = None
        self.log_messages = []
        
    def run(self):
        """Self-play arayüzünü çalıştır."""
        self.running = True
        self.start_training()  # Eğitim thread'ini başlat
        
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(30)
            
        pygame.quit()
        
    def _handle_events(self):
        """Kullanıcı etkileşimlerini ele al."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._stop_training()
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._stop_training()
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pass
    
    def _update(self):
        """Her frame çağrılır, arayüz mantığı."""
        current_time = time.time()
        
        # Belirli aralıkla grafikleri güncelle
        if current_time - self.last_plot_update > self.plot_interval:
            self._update_plots()
            self.last_plot_update = current_time
        
        # ETA hesaplama
        if self.stats['game_count'] > 0:
            elapsed = current_time - self.stats['started_at']
            self.stats['games_per_sec'] = self.stats['game_count'] / max(1, elapsed)
            remaining_games = self.stats['total_games'] - self.stats['game_count']
            self.stats['eta'] = remaining_games / max(0.1, self.stats['games_per_sec'])
    
    def _draw(self):
        """Arayüzü çiz."""
        self.screen.fill(self.DARK_GRAY)
        
        # Başlık
        title = self.large_font.render("Abluka AI Self-Play Eğitimi", True, self.GOLD)
        title_rect = title.get_rect(center=(self.width // 2, 30))
        self.screen.blit(title, title_rect)
        
        # İlerleme çubuğu
        progress_rect = pygame.Rect(50, 70, self.width - 100, 20)
        pygame.draw.rect(self.screen, self.BLACK, progress_rect, 1)
        
        if self.stats['total_games'] > 0:
            progress = self.stats['game_count'] / self.stats['total_games']
            fill_width = int((self.width - 100) * progress)
            fill_rect = pygame.Rect(50, 70, fill_width, 20)
            pygame.draw.rect(self.screen, self.GREEN, fill_rect)
        
        # Bilgiler
        stats_y = 100
        
        # Oyun sayısı
        game_text = self.font.render(
            f"Oyun: {self.stats['game_count']}/{self.stats['total_games']} "
            f"({(self.stats['game_count'] / max(1, self.stats['total_games']) * 100):.1f}%)", 
            True, self.WHITE
        )
        self.screen.blit(game_text, (50, stats_y))
        stats_y += 30
        
        # Durum sayısı
        if self.ai_player.learning_enabled:
            states_text = self.font.render(
                f"Q-Tablosu: {len(self.ai_player.q_table)} durum  "
                f"Yeni: {self.stats['new_states'][-1] if self.stats['new_states'] else 0}",
                True, self.WHITE
            )
            self.screen.blit(states_text, (50, stats_y))
            stats_y += 30
        
        # Kazanma oranları
        total_games = self.stats['black_wins'] + self.stats['white_wins']
        black_rate = self.stats['black_wins'] / max(1, total_games) * 100
        white_rate = self.stats['white_wins'] / max(1, total_games) * 100
        
        wins_text = self.font.render(
            f"Siyah Kazanma: {self.stats['black_wins']} ({black_rate:.1f}%)  "
            f"Beyaz Kazanma: {self.stats['white_wins']} ({white_rate:.1f}%)", 
            True, self.WHITE
        )
        self.screen.blit(wins_text, (50, stats_y))
        stats_y += 30
        
        # Hız & ETA
        speed_text = self.font.render(
            f"Hız: {self.stats['games_per_sec']:.2f} oyun/sn  "
            f"Kal. Süre: {self.stats['eta']/60:.1f} dk", 
            True, self.WHITE
        )
        self.screen.blit(speed_text, (50, stats_y))
        stats_y += 30

        # Ek ML verileri (Exploration, Q vs.)
        if self.ai_player.learning_enabled:
            # Son Q değeri
            last_q = self.stats['q_values'][-1] if self.stats['q_values'] else 0.0
            # Q farkı
            q_diff = 0.0
            if len(self.stats['q_values'])>1:
                q_diff = last_q - self.stats['q_values'][-2]
            
            # Son exploration
            current_expl = self.ai_player.exploration_rate
            # 2 decimal
            exploration_text = self.font.render(f"Exploration: {current_expl:.2f}", True, self.WHITE)
            self.screen.blit(exploration_text, (50, stats_y))
            stats_y += 25

            q_str = f"Ortalama Q: {last_q:.2f}  (Delta: {q_diff:+.2f})"
            q_text = self.font.render(q_str, True, self.WHITE)
            self.screen.blit(q_text, (50, stats_y))
            stats_y += 30
        
        stats_y += 20
        
        # Grafikler (Q-values, states, winrates)
        if self.q_values_plot:
            qx, qy = 50, stats_y
            w = (self.width - 100)//2
            h = 200
            self.screen.blit(self.q_values_plot, (qx,qy))
            
            if self.states_plot:
                sx = qx + w + 10
                sy = qy
                self.screen.blit(self.states_plot, (sx,sy))
            stats_y += h+10
        
        if self.winrate_plot:
            wx = 50
            wy = stats_y
            w2 = self.width-100
            h2 = 200
            self.screen.blit(self.winrate_plot, (wx,wy))
        
        # Log panel
        log_y = self.height - 150
        log_rect = pygame.Rect(50, log_y, self.width - 100, 140)
        pygame.draw.rect(self.screen, self.BLACK, log_rect)
        pygame.draw.rect(self.screen, self.GOLD, log_rect, 2)
        
        log_title = self.font.render("Eğitim Kayıtları", True, self.GOLD)
        self.screen.blit(log_title, (60, log_y + 5))
        
        log_y += 35
        for i, msg in enumerate(self.log_messages[-5:]):
            log_text = self.small_font.render(msg, True, self.WHITE)
            self.screen.blit(log_text, (60, log_y + i*20))
        
        if self.paused:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0,0,0,128))
            self.screen.blit(overlay,(0,0))
            
            pause_text = self.large_font.render("DURAKLATILDI (SPACE ile devam et)",True,self.WHITE)
            pause_rect = pause_text.get_rect(center=(self.width//2,self.height//2))
            self.screen.blit(pause_text,pause_rect)
        
        pygame.display.flip()
    
    def _update_plots(self):
        """Matplotlib ile grafikleri oluşturup pygame surface'lerine dönüştürür."""
        if not self.ai_player.learning_enabled:
            return
        
        games = list(range(1, len(self.stats['q_values']) + 1))
        q_values = self.stats['q_values']
        states_count = self.stats['states_count']
        new_states = self.stats['new_states']
        
        min_len = min(len(games), len(states_count), len(new_states), len(q_values))
        if min_len==0:
            return
        
        games = games[:min_len]
        q_values = q_values[:min_len]
        states_count = states_count[:min_len]
        new_states = new_states[:min_len]
        
        bg_color = tuple(c/255 for c in self.DARK_GRAY)
        
        # Q Değerleri
        if q_values:
            fig1 = Figure(figsize=(5,3), dpi=80, facecolor=bg_color)
            ax1 = fig1.add_subplot(111)
            ax1.plot(games, q_values, color='green', linewidth=2)
            ax1.set_title("Ortalama Q Değerleri", color='white')
            ax1.set_facecolor(bg_color)
            ax1.tick_params(colors='white')
            for spine in ax1.spines.values():
                spine.set_color('white')
            canvas = FigureCanvasAgg(fig1)
            canvas.draw()
            renderer = canvas.get_renderer()
            raw_data = renderer.tostring_argb()
            size = canvas.get_width_height()
            surf = pygame.image.frombuffer(raw_data, size, "ARGB")
            self.q_values_plot = surf
        
        # Durum sayıları
        if states_count:
            fig2 = Figure(figsize=(5,3), dpi=80, facecolor=bg_color)
            ax2 = fig2.add_subplot(111)
            ax2.plot(games, states_count, color='blue', linewidth=2, label='Toplam Durum')
            ax2.plot(games, new_states, color='orange', linewidth=2, label='Yeni Durum')
            ax2.set_title("Durum Sayıları", color='white')
            ax2.set_facecolor(bg_color)
            ax2.tick_params(colors='white')
            ax2.legend(facecolor=bg_color, labelcolor='white')
            for spine in ax2.spines.values():
                spine.set_color('white')
            canvas = FigureCanvasAgg(fig2)
            canvas.draw()
            renderer = canvas.get_renderer()
            raw_data = renderer.tostring_argb()
            size = canvas.get_width_height()
            surf = pygame.image.frombuffer(raw_data, size, "ARGB")
            self.states_plot = surf
        
        # Kazanma oranları
        if self.stats['win_rates']:
            fig3 = Figure(figsize=(10,3), dpi=80, facecolor=bg_color)
            ax3 = fig3.add_subplot(111)
            
            win_rates = self.stats['win_rates']
            black_rates = [wr[0] for wr in win_rates]
            white_rates = [wr[1] for wr in win_rates]
            x = np.arange(len(win_rates))
            width = 0.35
            ax3.bar(x - width/2, black_rates, width, label='Siyah %', color='black')
            ax3.bar(x + width/2, white_rates, width, label='Beyaz %', color='white')
            ax3.set_title("Kazanma Oranları", color='white')
            ax3.set_facecolor(bg_color)
            ax3.tick_params(colors='white')
            ax3.legend(facecolor=bg_color, labelcolor='white')
            for spine in ax3.spines.values():
                spine.set_color('white')
            
            canvas = FigureCanvasAgg(fig3)
            canvas.draw()
            renderer = canvas.get_renderer()
            raw_data = renderer.tostring_argb()
            size = canvas.get_width_height()
            surf = pygame.image.frombuffer(raw_data, size, "ARGB")
            self.winrate_plot = surf
    
    def _log(self, message):
        """Log (konsol + panel)."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        self.log_messages.append(log_msg)
        if len(self.log_messages)>100:
            self.log_messages = self.log_messages[-100:]
    
    def start_training(self):
        """Self-play eğitimini başlat."""
        if self.training_thread is None or not self.training_thread.is_alive():
            self.training_thread = threading.Thread(target=self._training_process)
            self.training_thread.daemon = True
            self.training_thread.start()
            self._log("Eğitim başlatıldı...")
    
    def _stop_training(self):
        """Eğitimi durdur."""
        if self.training_thread and self.training_thread.is_alive():
            self.running = False
            self.training_thread.join(timeout=1.0)
            self._log("Eğitim durduruldu.")
    
    def _training_process(self):
        """Asıl self-play döngüsü."""
        self._log(f"Toplam {self.game_count} oyun için self-play başlıyor...")

        # Self-play => exploration aç
        # (BUNLARI EKLEDİK: Kod self-play süresince `_in_self_play` & expl > 0)
        self.ai_player._in_self_play = True
        self.ai_player.exploration_rate = 0.46  # Örneğin 0.3

        # Mevcut durum sayısı
        initial_states = len(self.ai_player.q_table) if self.ai_player.learning_enabled else 0
        self.stats['states_count'].append(initial_states)
        self.stats['new_states'].append(0)
        
        # Ortalama Q
        avg_q = self._calculate_average_q()
        self.stats['q_values'].append(avg_q)
        
        for i in range(self.game_count):
            if not self.running:
                break
            while self.paused and self.running:
                time.sleep(0.1)
            
            # Tek maç
            winner = self._simulate_game()
            self.stats['game_count'] += 1
            if winner=='B':
                self.stats['black_wins']+=1
            else:
                self.stats['white_wins']+=1
            
            # Her 5 oyunda bir rapor
            if (i+1)%5==0 or i==self.game_count-1:
                avg_q = self._calculate_average_q()
                self.stats['q_values'].append(avg_q)
                curr_st = len(self.ai_player.q_table) if self.ai_player.learning_enabled else 0
                new_states = curr_st - initial_states
                self.stats['states_count'].append(curr_st)
                self.stats['new_states'].append(new_states)
                
                done = self.stats['game_count']
                b_rate = (self.stats['black_wins']/max(1,done))*100
                w_rate = (self.stats['white_wins']/max(1,done))*100
                self.stats['win_rates'].append((b_rate,w_rate))
                
                self.stats['exploration_history'].append(self.ai_player.exploration_rate)
                
                self._log(f"Oyun {i+1}/{self.game_count} tamam. Q:{avg_q:.2f}, "
                          f"Durum:{curr_st}, Expl:{self.ai_player.exploration_rate:.2f}")
        
        self._log("Eğitim tamamlandı.")

        # Self-play bitti => exploration sıfırla
        self.ai_player._in_self_play = False
        self.ai_player.exploration_rate = 0.0

        if self.ai_player.learning_enabled:
            self.ai_player.save_model()
            self._log(f"Model kaydedildi. Toplam durum:{len(self.ai_player.q_table)}")
    
    def _simulate_game(self):
        """Bir oyunu simüle et, kazananı döndür."""
        game = Game()

        # Rastgele hangi renk başlasın
        if random.random()<0.5:
            game.current_player='W'
        else:
            game.current_player='B'

        # 0-3 açılış hamlesi
        opening_moves = random.randint(0,3)
        for _ in range(opening_moves):
            if game.game_over:
                break
            cp = game.current_player
            val_moves = game.board.get_valid_moves(cp)
            if not val_moves:
                break
            mv = random.choice(val_moves)
            tmp_board = Board()
            tmp_board.size = game.board.size
            tmp_board.grid = [row[:] for row in game.board.grid]
            tmp_board.black_pos = game.board.black_pos
            tmp_board.white_pos = game.board.white_pos
            tmp_board.obstacles = game.board.obstacles.copy()
            
            tmp_board.move_piece(cp, mv)
            empties = []
            for r in range(tmp_board.size):
                for c in range(tmp_board.size):
                    if tmp_board.grid[r][c] is None:
                        empties.append((r,c))
            if empties:
                obs = random.choice(empties)
                game.make_move(mv,obs)

        move_count=0
        while not game.game_over and move_count<50:
            cp=game.current_player
            move, obstacle = self.ai_player._choose_move_ultra_ml(
                game.board, cp, 1.0, time.time()
            )
            
            if not move or not obstacle:
                game.game_over=True
                game.winner=('W' if cp=='B' else 'B')
                break
            
            game.make_move(move,obstacle)
            move_count+=1

        # 50 hamleyi doldurdu => rastgele kazanan
        if not game.game_over:
            game.game_over=True
            game.winner=random.choice(['B','W'])

        # Oyun sonu => siyah ve beyaz öğrenimi
        self.ai_player.game_over_update(game.winner, 'B')
        self.ai_player.current_game_states=[]
        self.ai_player.current_game_rewards=[]
        self.ai_player.current_game_moves=[]
        self.ai_player.game_over_update(game.winner, 'W')
        
        return game.winner
    
    def _calculate_average_q(self):
        """Q tablosunun ortalama değerini döndür."""
        if not self.ai_player.learning_enabled or not self.ai_player.q_table:
            return 0.0
        total = sum(self.ai_player.q_table.values())
        return total/len(self.ai_player.q_table)

def main():
    """Komut satırından self-play başlat."""
    parser = argparse.ArgumentParser(description="Abluka AI Self-Play Eğitim Modülü")
    parser.add_argument('--width', type=int, default=1000, help='Pencere genişliği')
    parser.add_argument('--height', type=int, default=800, help='Pencere yüksekliği')
    parser.add_argument('--games', type=int, default=200, help='Oynatılacak oyun sayısı')
    
    args = parser.parse_args()
    
    trainer = AblukaSelfPlay(
        width=args.width,
        height=args.height,
        game_count=args.games
    )
    
    print(f"Abluka AI Self-Play Eğitimi Başlatılıyor - {args.games} oyun")
    trainer.run()

if __name__ == "__main__":
    main()

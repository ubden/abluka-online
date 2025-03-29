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
    """Abluka AI Self-Play Eğitim Modülü"""
    
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
        """Abluka Self-Play Modülünü başlat"""
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
        
        # AI oyuncuları oluştur
        self.ai_player = AIPlayer(difficulty='hard')
        
        # İstatistikler
        self.stats = {
            'game_count': 0,
            'total_games': self.game_count,
            'black_wins': 0,
            'white_wins': 0,
            'q_values': [],
            'states_count': [],
            'new_states': [],
            'win_rates': [],
            'started_at': time.time(),
            'games_per_sec': 0,
            'eta': 0
        }
        
        # Grafikler
        self.last_plot_update = 0
        self.plot_interval = 5  # her 5 saniyede bir grafiği güncelle
        self.q_values_plot = None
        self.states_plot = None
        self.winrate_plot = None
        
        # Eğitim başlatma
        self.training_thread = None
        self.log_messages = []
        
    def run(self):
        """Self-play arayüzünü çalıştır"""
        self.running = True
        self.start_training()
        
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(30)
            
        pygame.quit()
        
    def _handle_events(self):
        """Kullanıcı olaylarını işle"""
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
                # Düğme tıklamaları
                mouse_pos = pygame.mouse.get_pos()
                # Burada düğmeleri kontrol et...
    
    def _update(self):
        """Güncelleme işlemleri"""
        # Grafikleri güncelle
        current_time = time.time()
        if current_time - self.last_plot_update > self.plot_interval:
            self._update_plots()
            self.last_plot_update = current_time
        
        # ETA hesapla
        if self.stats['game_count'] > 0:
            elapsed = current_time - self.stats['started_at']
            self.stats['games_per_sec'] = self.stats['game_count'] / max(1, elapsed)
            remaining_games = self.stats['total_games'] - self.stats['game_count']
            self.stats['eta'] = remaining_games / max(0.1, self.stats['games_per_sec'])
    
    def _draw(self):
        """Arayüzü çiz"""
        # Arkaplan
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
        
        # İstatistikler
        stats_y = 100
        
        # Oyun sayısı
        game_text = self.font.render(
            f"Oyun: {self.stats['game_count']}/{self.stats['total_games']} " +
            f"({'%.1f' % (self.stats['game_count'] / max(1, self.stats['total_games']) * 100)}%)", 
            True, self.WHITE
        )
        self.screen.blit(game_text, (50, stats_y))
        stats_y += 30
        
        # Durum sayısı
        if self.ai_player.learning_enabled:
            states_text = self.font.render(
                f"Toplam Durum: {len(self.ai_player.q_table)}  " +
                f"Yeni Durum: {self.stats['new_states'][-1] if self.stats['new_states'] else 0}",
                True, self.WHITE
            )
            self.screen.blit(states_text, (50, stats_y))
            stats_y += 30
        
        # Kazanma oranları
        total_games = self.stats['black_wins'] + self.stats['white_wins']
        black_rate = self.stats['black_wins'] / max(1, total_games) * 100
        white_rate = self.stats['white_wins'] / max(1, total_games) * 100
        
        wins_text = self.font.render(
            f"Siyah Kazanma: {self.stats['black_wins']} ({'%.1f' % black_rate}%)  " +
            f"Beyaz Kazanma: {self.stats['white_wins']} ({'%.1f' % white_rate}%)", 
            True, self.WHITE
        )
        self.screen.blit(wins_text, (50, stats_y))
        stats_y += 30
        
        # Hız ve ETA
        speed_text = self.font.render(
            f"Hız: {'%.2f' % self.stats['games_per_sec']} oyun/sn  " +
            f"Tahmini süre: {'%.1f' % (self.stats['eta'] / 60)} dakika", 
            True, self.WHITE
        )
        self.screen.blit(speed_text, (50, stats_y))
        stats_y += 50
        
        # Grafikler
        if self.q_values_plot:
            q_plot_x = 50
            q_plot_y = stats_y
            q_plot_width = (self.width - 100) // 2
            q_plot_height = 200
            self.screen.blit(self.q_values_plot, (q_plot_x, q_plot_y))
            
            if self.states_plot:
                s_plot_x = q_plot_x + q_plot_width + 10
                s_plot_y = q_plot_y
                self.screen.blit(self.states_plot, (s_plot_x, s_plot_y))
            
            stats_y += q_plot_height + 10
        
        if self.winrate_plot:
            w_plot_x = 50
            w_plot_y = stats_y
            w_plot_width = self.width - 100
            w_plot_height = 200
            self.screen.blit(self.winrate_plot, (w_plot_x, w_plot_y))
        
        # Log mesajları
        log_y = self.height - 150
        log_rect = pygame.Rect(50, log_y, self.width - 100, 140)
        pygame.draw.rect(self.screen, self.BLACK, log_rect)
        pygame.draw.rect(self.screen, self.GOLD, log_rect, 2)
        
        log_title = self.font.render("Eğitim Kayıtları", True, self.GOLD)
        self.screen.blit(log_title, (60, log_y + 5))
        
        log_y += 35
        for i, msg in enumerate(self.log_messages[-5:]):
            log_text = self.small_font.render(msg, True, self.WHITE)
            self.screen.blit(log_text, (60, log_y + i * 20))
        
        if self.paused:
            pause_overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pause_overlay.fill((0, 0, 0, 128))
            self.screen.blit(pause_overlay, (0, 0))
            
            pause_text = self.large_font.render("DURAKLATILDI (SPACE ile devam et)", True, self.WHITE)
            pause_rect = pause_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(pause_text, pause_rect)
        
        pygame.display.flip()
    
    def _update_plots(self):
        """Grafikleri oluştur/güncelle"""
        if not self.ai_player.learning_enabled:
            return
            
        # Veriler
        games = list(range(1, len(self.stats['q_values']) + 1))
        q_values = self.stats['q_values']
        states_count = self.stats['states_count']
        new_states = self.stats['new_states']
        
        # Veri boyutlarının eşit olduğundan emin ol
        min_len = min(len(games), len(states_count), len(new_states), len(q_values))
        if min_len == 0:
            return
            
        games = games[:min_len]
        q_values = q_values[:min_len]
        states_count = states_count[:min_len]
        new_states = new_states[:min_len]
        
        # Matplotlib için renk değerlerini normalleştir (0-255 -> 0-1)
        bg_color = tuple(c/255 for c in self.DARK_GRAY)
        
        # 1. Q-değerleri grafiği
        if q_values:
            fig1 = Figure(figsize=(5, 3), dpi=80, facecolor=bg_color)
            ax1 = fig1.add_subplot(111)
            ax1.plot(games, q_values, color='green', linewidth=2)
            ax1.set_title('Ortalama Q Değerleri', color='white')
            ax1.set_facecolor(bg_color)
            ax1.tick_params(colors='white')
            for spine in ax1.spines.values():
                spine.set_color('white')
            
            # Grafiği surface'e dönüştür
            canvas = FigureCanvasAgg(fig1)
            canvas.draw()
            renderer = canvas.get_renderer()
            raw_data = renderer.tostring_argb()
            size = canvas.get_width_height()
            
            # ARGB -> RGB dönüşümü
            surf = pygame.image.frombuffer(raw_data, size, "ARGB")
            self.q_values_plot = surf
        
        # 2. Durum sayıları grafiği
        if states_count:
            fig2 = Figure(figsize=(5, 3), dpi=80, facecolor=bg_color)
            ax2 = fig2.add_subplot(111)
            ax2.plot(games, states_count, color='blue', linewidth=2, label='Toplam Durum')
            ax2.plot(games, new_states, color='orange', linewidth=2, label='Yeni Durum')
            ax2.set_title('Durum Sayıları', color='white')
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
            
            # ARGB -> RGB dönüşümü
            surf = pygame.image.frombuffer(raw_data, size, "ARGB")
            self.states_plot = surf
        
        # 3. Kazanma oranları grafiği
        if self.stats['win_rates']:
            fig3 = Figure(figsize=(10, 3), dpi=80, facecolor=bg_color)
            ax3 = fig3.add_subplot(111)
            
            win_rates = self.stats['win_rates']
            black_rates = [wr[0] for wr in win_rates]
            white_rates = [wr[1] for wr in win_rates]
            
            x = np.arange(len(win_rates))
            width = 0.35
            
            ax3.bar(x - width/2, black_rates, width, label='Siyah Kazanma %', color='black')
            ax3.bar(x + width/2, white_rates, width, label='Beyaz Kazanma %', color='white')
            
            ax3.set_title('Kazanma Oranları', color='white')
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
            
            # ARGB -> RGB dönüşümü
            surf = pygame.image.frombuffer(raw_data, size, "ARGB")
            self.winrate_plot = surf
    
    def _log(self, message):
        """Loglama yap"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        self.log_messages.append(log_msg)
        
        # Max 100 log mesajı tut
        if len(self.log_messages) > 100:
            self.log_messages = self.log_messages[-100:]
    
    def start_training(self):
        """Eğitim thread'ini başlat"""
        if self.training_thread is None or not self.training_thread.is_alive():
            self.training_thread = threading.Thread(target=self._training_process)
            self.training_thread.daemon = True
            self.training_thread.start()
            self._log("Eğitim başlatıldı...")
    
    def _stop_training(self):
        """Eğitimi durdur"""
        if self.training_thread and self.training_thread.is_alive():
            self.running = False
            self.training_thread.join(timeout=1.0)
            self._log("Eğitim durduruldu.")
    
    def _training_process(self):
        """Asıl eğitim işlemini gerçekleştir"""
        self._log(f"Toplam {self.game_count} oyun için self-play başlıyor...")
        
        # Başlangıç durum sayısı
        initial_states = len(self.ai_player.q_table) if self.ai_player.learning_enabled else 0
        self.stats['states_count'].append(initial_states)
        self.stats['new_states'].append(0)
        
        # Başlangıç Q değerleri
        avg_q = self._calculate_average_q()
        self.stats['q_values'].append(avg_q)
        
        # Eğitim döngüsü
        for i in range(self.game_count):
            # Eğer durdurulmuşsa çık
            if not self.running:
                break
                
            # Eğer duraklatılmışsa bekle
            while self.paused and self.running:
                time.sleep(0.1)
            
            # Oyun simüle et
            winner = self._simulate_game()
            
            # İstatistikleri güncelle
            self.stats['game_count'] += 1
            if winner == 'B':
                self.stats['black_wins'] += 1
            else:
                self.stats['white_wins'] += 1
            
            # Her 5 oyunda bir detaylı istatistikler
            if (i + 1) % 5 == 0 or i == self.game_count - 1:
                # Q değerleri ortalaması
                avg_q = self._calculate_average_q()
                self.stats['q_values'].append(avg_q)
                
                # Durum sayıları
                current_states = len(self.ai_player.q_table) if self.ai_player.learning_enabled else 0
                new_states = current_states - initial_states
                self.stats['states_count'].append(current_states)
                self.stats['new_states'].append(new_states)
                
                # Kazanma oranları
                black_rate = (self.stats['black_wins'] / max(1, self.stats['game_count'])) * 100
                white_rate = (self.stats['white_wins'] / max(1, self.stats['game_count'])) * 100
                self.stats['win_rates'].append((black_rate, white_rate))
                
                # Loglama
                self._log(f"Oyun {i+1}/{self.game_count} tamamlandı. " +
                         f"Q-değeri: {avg_q:.2f}, Durum sayısı: {current_states}")
        
        self._log("Eğitim tamamlandı!")
        
        # Modeli kaydet
        if self.ai_player.learning_enabled:
            self.ai_player.save_model()
            self._log(f"Model kaydedildi. Toplam durum sayısı: {len(self.ai_player.q_table)}")
    
    def _simulate_game(self):
        """Bir oyunu simüle et ve kazananı döndür"""
        game = Game()
        move_count = 0
        
        while not game.game_over and move_count < 50:  # Sonsuz döngüleri önle
            current_player = game.current_player
            
            # AI hamlesi
            move, obstacle = self.ai_player._choose_move_ultra_ml(
                game.board, current_player, 1.0, time.time()
            )
            
            if move is None or obstacle is None:
                # Geçerli hamle bulunamadı
                game.game_over = True
                game.winner = 'W' if current_player == 'B' else 'B'
                break
            
            # Hamleyi uygula
            game.make_move(move, obstacle)
            move_count += 1
        
        # Oyun sonunu öğren
        if game.winner is None:
            # 50 hamle limiti aşıldı - beraberlik sayılmaz, rastgele kazanan
            game.winner = random.choice(['B', 'W'])
        
        # Öğrenme güncellemesi
        self.ai_player.game_over_update(game.winner, 'B')  # Siyah oyuncu olarak öğren
        
        # Beyaz oyuncu olarak da öğren
        self.ai_player.current_game_states = []
        self.ai_player.current_game_moves = []
        self.ai_player.current_game_rewards = []
        self.ai_player.game_over_update(game.winner, 'W')
        
        return game.winner
    
    def _calculate_average_q(self):
        """Tüm Q değerlerinin ortalamasını hesapla"""
        if not self.ai_player.learning_enabled or not self.ai_player.q_table:
            return 0.0
            
        q_sum = sum(self.ai_player.q_table.values())
        return q_sum / len(self.ai_player.q_table)


def main():
    """Self-play modülünü başlat"""
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
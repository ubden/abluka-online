import time
import random
import math
import os
import datetime
from copy import deepcopy

class AIPlayer:
    """
    Abluka AI - Revize Edilmiş Versiyon
    - easy  : önceki 'normal' strateji
    - normal: önceki 'hard' strateji
    - hard  : ultra seviye, makine öğrenmesi entegre edilebilir iskelet
    """

    def __init__(self, difficulty='normal', max_time=5.0):
        self.difficulty = difficulty
        self.max_time = float(max_time)  # her hamlede düşünme süresi (saniye)
        
        # Bu modlar, önceki koda göre yer değiştirdi:
        # easy   => önceki normal
        # normal => önceki hard
        # hard   => makine öğrenmesi iskeleti
        
        # Aşağıda base_depth gibi parametreleri zorluklara göre yeniden tanımlıyoruz:
        if self.difficulty == 'easy':
            # EASY: önceki normal modun temel parametreleri
            # Yani sabit derinlik 3-4 civarında Minimax + AlphaBeta
            self.base_depth = 3  # normalde 3
            self.max_time = max(self.max_time, 2.0)
            
        elif self.difficulty == 'normal':
            # NORMAL: önceki hard mantığı - iterative deepening
            self.base_depth = 5  # önceki Hard mod 4 veya 5
            self.max_time = max(self.max_time, 3.0)

        else:  # 'hard'
            # HARD: Ultra seviye -> RL / ML iskeleti
            # Tekrar da bir base_depth tutalım, eğer fallback minimax istersen
            self.base_depth = 6
            self.max_time = max(self.max_time, 4.0)

        # Loglama
        self.log_enabled = True
        self.game_log = []
        self.log_file = self._create_log_file()

        # Duygusal tepkiler
        self.emojis = {
            'happy': [':-)', ':D', ':)', '(:', '8-)'],
            'thinking': [':-/', ':-?', ':-\\', '8-|', '*-*'],
            'worried': [':-O', ':-o', ':-S', ':-s', ':-*'],
            'excited': [':-D', '8-D', 'B-)', '>-)', '=D'],
            'smug': [':-P', ';-)', ':->', ':-<', 'B-)'],
            'surprised': [':-O', ':-0', 'WOW', 'OMG', '!-!']
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
                "Zafer kokusu alıyorum!"
            ],
            'trapped': [
                "Beni ablukaya mı alıyorsun?!",
                "Ahh, kapana kısıldım!",
                "Ustalıkla oynadın...",
                "Çevrildim galiba!",
                "Kaçış yok mu?"
            ]
        }
        self.current_message = None
        self.last_mobility = None
        self.move_counter = 0
        
        # Son hamledeki strateji açıklaması
        self.last_move_reasoning = ""

        # Öğrenme sistemi için gerekli veri yapıları
        self.learning_enabled = difficulty == 'hard'  # Sadece hard modda öğrenme aktif
        
        # Öğrenme için gerekli değişkenler
        if self.learning_enabled:
            self._init_learning_system()

    def _create_log_file(self):
        """Log dosyası oluştur."""
        if not self.log_enabled:
            return None
        log_dir = "logs"
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except:
                print("Log dizini oluşturulamadı, loglama devre dışı.")
                self.log_enabled = False
                return None
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{log_dir}/abluka_game_{timestamp}.log"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Abluka AI Log - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Mod (Difficulty): {self.difficulty}\n")
                f.write("------------------------------------------------\n")
            return filename
        except:
            print("Log dosyası oluşturulamadı, loglama devre dışı.")
            self.log_enabled = False
            return None

    def _log_move(self, player, move, obstacle, strategy, board_state=None):
        """Hamleyi logla."""
        if not self.log_enabled or not self.log_file:
            return
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"\nHamle #{len(self.game_log) + 1}\n")
                f.write(f"Oyuncu: {'AI' if player != 'Human' else 'İnsan'} ({player})\n")
                f.write(f"Taş Hamlesi: {move}\n")
                f.write(f"Engel: {obstacle}\n")
                f.write(f"Strateji: {strategy}\n")

                if board_state:
                    f.write("Tahta Durumu:\n")
                    size = board_state.size
                    for r in range(size):
                        row_txt = []
                        for c in range(size):
                            cell = board_state.grid[r][c]
                            if cell == 'B':
                                row_txt.append('B')
                            elif cell == 'W':
                                row_txt.append('W')
                            elif cell in ('X', 'R'):
                                row_txt.append('X')
                            else:
                                row_txt.append('.')
                        f.write(' '.join(row_txt) + '\n')
                f.write("------------------------------------------------\n")
            
            self.game_log.append({
                'player': player,
                'move': move,
                'obstacle': obstacle,
                'strategy': strategy
            })
        except:
            print("Log yazma hatası.")

    def choose_move(self, game_state):
        """
        Tüm zorluk seviyelerine göre en iyi (move, obstacle) döndürür.
        move = (r, c), obstacle = (r, c)
        """
        start_time = time.time()
        board = game_state['board']
        player = game_state['current_player']

        valid_moves = board.get_valid_moves(player)
        if not valid_moves:
            self.current_message = self._random_reaction(
                self.emojis['worried'], self.messages['trapped']
            )
            return None, None

        self.move_counter += 1
        self._assess_emotion(board, player)  # duygusal tepki için

        print(f"\n[AI] {player} oyuncusu (AI) hamle yapıyor - Zorluk: {self.difficulty}")
        print(f"[AI] Siyah taş: {board.black_pos}, Beyaz taş: {board.white_pos}")
        print(f"[AI] Siyah hamle sayısı: {len(board.get_valid_moves('B'))}, "
              f"Beyaz hamle sayısı: {len(board.get_valid_moves('W'))}")

        # Kazanma tahmini
        win_probability = self._calculate_win_probability(board, player)
        print(f"[AI] {player} için kazanma olasılığı: %{win_probability:.1f}")

        time_limit = self.max_time

        # Anında kazanma kontrolü
        immediate_win = self._check_immediate_win(board, player)
        if immediate_win:
            mv, obs = immediate_win
            elapsed = time.time() - start_time
            self.current_message = self._random_reaction(
                self.emojis['excited'], self.messages['confident']
            )
            self.last_move_reasoning = "Anında kazanma - rakip ablukaya alındı"
            self._log_move(player, mv, obs, self.last_move_reasoning, board)
            if elapsed < 0.5:
                time.sleep(0.5 - elapsed)
            return mv, obs

        # Mod seçimine göre hamle fonksiyonu
        if self.difficulty == 'easy':
            # EASY => ÖNCEKİ NORMAL
            move, obstacle = self._choose_move_old_normal(board, player, time_limit, start_time)

        elif self.difficulty == 'normal':
            # NORMAL => ÖNCEKİ HARD
            move, obstacle = self._choose_move_old_hard(board, player, time_limit, start_time)

        else:
            # HARD => Makine Öğrenmesi iskeleti
            move, obstacle = self._choose_move_ultra_ml(board, player, time_limit, start_time)

        elapsed = time.time() - start_time
        print(f"[AI] Seviye: {self.difficulty}, Süre: {elapsed:.2f} sn -> "
              f"Hamle: {move}, Engel: {obstacle}")
        print(f"[AI] STRATEJİ: {self.last_move_reasoning}")

        if move and obstacle:
            temp_board = self._clone_board(board)
            temp_board.move_piece(player, move)
            temp_board.place_obstacle(obstacle)
            future_win_prob = self._calculate_win_probability(temp_board, player)
            opponent = 'W' if player == 'B' else 'B'
            op_moves_after = len(temp_board.get_valid_moves(opponent))
            my_moves_after = len(temp_board.get_valid_moves(player))

            print(f"[AI] Hamle sonrası kazanma olasılığı: %{future_win_prob:.1f}")
            print(f"[AI] Rakip hamle sayısı: {op_moves_after}, Kendi hamle sayım: {my_moves_after}")

        self._log_move(player, move, obstacle, self.last_move_reasoning, board)
        if elapsed < 0.8:
            time.sleep(0.8 - elapsed)

        return move, obstacle

    def get_reaction(self):
        """En son üretilen duygu / tepki mesajı."""
        return self.current_message

    # -------------------------------------------------------------------------
    # EASY => ÖNCEKİ NORMAL
    # -------------------------------------------------------------------------
    def _choose_move_old_normal(self, board, player, time_limit, start_time):
        """
        Daha önce 'normal' olarak kullanılan mantık:
          - Sabit derinlik (3-4)
          - Minimax + alpha-beta
          - Kısmen budama
        """
        # Benzer mantığı barındıran fonksiyon
        best_move = None
        best_obstacle = None
        best_score = float('-inf')

        depth = self.base_depth  # genelde 3-4
        valid_moves = board.get_valid_moves(player)

        # Rastgelelik çok düşük
        if random.random() < 0.15:  # %15 rastgele
            random.shuffle(valid_moves)
            for mv in valid_moves:
                temp_brd = self._clone_board(board)
                temp_brd.move_piece(player, mv)
                empties = self._get_empty_positions(temp_brd)
                random.shuffle(empties)
                for obs in empties:
                    test_brd = self._clone_board(temp_brd)
                    test_brd.place_obstacle(obs)
                    if not test_brd.is_abluka(player) and len(test_brd.get_valid_moves(player)) > 0:
                        self.last_move_reasoning = "EasyMod(RastgeleElleme)"
                        return mv, obs

        # Minimax
        alpha = float('-inf')
        beta = float('inf')

        # Sıralama
        valid_moves = sorted(
            valid_moves,
            key=lambda m: self._evaluate_move(board, player, m),
            reverse=True
        )
        # En iyi 5 hamleyi incele
        top_moves = valid_moves[:5]

        for mv in top_moves:
            if time.time() - start_time > time_limit:
                break
            temp_brd = self._clone_board(board)
            temp_brd.move_piece(player, mv)

            empties = self._get_empty_positions(temp_brd)
            if len(empties) > 6:
                empties = self._prune_obstacles(temp_brd, empties, player, top_k=6)

            for obs in empties:
                if time.time() - start_time > time_limit:
                    break
                test_brd = self._clone_board(temp_brd)
                test_brd.place_obstacle(obs)
                if test_brd.is_abluka(player):
                    continue
                score = self._minimax_evaluation(
                    test_brd, depth, True, player, alpha, beta
                )
                if score > best_score:
                    best_score = score
                    best_move = mv
                    best_obstacle = obs
        if best_move is None:
            # fallback
            self.last_move_reasoning = "Easy fallback => random"
            if valid_moves:
                return valid_moves[0], self._get_empty_positions(board)[0]
            return None, None
        self.last_move_reasoning = "Easy => (previously normal) Minimax"
        return best_move, best_obstacle

    def _minimax_evaluation(self, board, depth, maximizing_player, main_player, alpha, beta):
        """
        Kısa bir minimax (derinliğe kadar) - zaman kontrolü YOK (easy).
        """
        if depth == 0:
            return self._evaluate_board(board, main_player)
        current = main_player if maximizing_player else ('W' if main_player == 'B' else 'B')
        if board.is_abluka(current):
            return -999999 if current == main_player else 999999
        valid_moves = board.get_valid_moves(current)
        if not valid_moves:
            return -999999 if current == main_player else 999999

        if maximizing_player:
            value = float('-inf')
            for mv in valid_moves[:4]:  # en fazla 4 hamleyi dene
                new_brd = self._clone_board(board)
                new_brd.move_piece(current, mv)
                empties = self._get_empty_positions(new_brd)
                if empties:
                    obs_pos = empties[0]
                    new_brd.place_obstacle(obs_pos)
                sc = self._minimax_evaluation(
                    new_brd, depth - 1, not maximizing_player, main_player, alpha, beta
                )
                value = max(value, sc)
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return value
        else:
            value = float('inf')
            for mv in valid_moves[:4]:
                new_brd = self._clone_board(board)
                new_brd.move_piece(current, mv)
                empties = self._get_empty_positions(new_brd)
                if empties:
                    obs_pos = empties[0]
                    new_brd.place_obstacle(obs_pos)
                sc = self._minimax_evaluation(
                    new_brd, depth - 1, not maximizing_player, main_player, alpha, beta
                )
                value = min(value, sc)
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value

    # -------------------------------------------------------------------------
    # NORMAL => ÖNCEKİ HARD
    # -------------------------------------------------------------------------
    def _choose_move_old_hard(self, board, player, time_limit, start_time):
        """
        Önceki 'hard' algoritma (iterative deepening + alpha-beta vb.)
        """
        best_move = None
        best_obstacle = None
        best_score = float('-inf')

        valid_moves = board.get_valid_moves(player)
        opponent = 'W' if player == 'B' else 'B'

        # Hızlı kazanma
        for mv in valid_moves:
            tmpb = self._clone_board(board)
            tmpb.move_piece(player, mv)
            empties = self._get_empty_positions(tmpb)
            for obs in empties:
                testb = self._clone_board(tmpb)
                testb.place_obstacle(obs)
                if testb.is_abluka(opponent) and not testb.is_abluka(player):
                    self.last_move_reasoning = "Normal: Hızlı abluka"
                    return mv, obs

        # Iterative deepening
        base_d = self.base_depth
        max_depth = base_d + 2
        for d in range(base_d, max_depth + 1):
            if time.time() - start_time > time_limit * 0.8:
                break
            mv_, obs_, score_ = self._search_best_move(board, player, d, start_time, time_limit)
            if mv_ is not None and score_ > best_score:
                best_move = mv_
                best_obstacle = obs_
                best_score = score_
            if score_ > 900000:
                break

        if best_move is None:
            self.last_move_reasoning = "Normal fallback => Easy"
            return self._choose_move_old_normal(board, player, time_limit, start_time)

        # Kendini abluka?
        tmpb = self._clone_board(board)
        tmpb.move_piece(player, best_move)
        tmpb.place_obstacle(best_obstacle)
        if tmpb.is_abluka(player):
            self.last_move_reasoning = "Normal => Engelle kendini kısıtlıyor => easy fallback"
            return self._choose_move_old_normal(board, player, time_limit, start_time)

        # Engel rakibe etki etmedi mi?
        op_moves_before = len(board.get_valid_moves(opponent))
        t2 = self._clone_board(board)
        t2.move_piece(player, best_move)
        t2.place_obstacle(best_obstacle)
        op_moves_after = len(t2.get_valid_moves(opponent))
        if op_moves_before == op_moves_after and op_moves_before > 0:
            empties2 = self._get_empty_positions(t2)
            if len(empties2) > 1:
                obstacles2 = self._prune_obstacles(t2, empties2, player, 3)
                if obstacles2 and obstacles2[0] != best_obstacle:
                    best_obstacle = obstacles2[0]
                    self.last_move_reasoning += " + Engel revize"

        self.last_move_reasoning = "Normal => (iterative deepening) Hard mantığı"
        return best_move, best_obstacle

    def _search_best_move(self, board, player, depth, start_time, time_limit):
        """
        ÖNCEKİ HARD modun alt fonksiyonu: alpha-beta araması
        """
        best_move = None
        best_obstacle = None
        best_score = float('-inf')

        valid_moves = board.get_valid_moves(player)
        if not valid_moves:
            return None, None, -999999
        # budama
        if len(valid_moves) > 6 and depth >= 3:
            valid_moves = self._prune_moves(board, player, valid_moves, 6)

        alpha = float('-inf')
        beta = float('inf')
        opponent = 'W' if player == 'B' else 'B'

        for mv in valid_moves:
            if time.time() - start_time > time_limit * 0.9:
                break
            tmpb = self._clone_board(board)
            tmpb.move_piece(player, mv)
            empties = self._get_empty_positions(tmpb)
            if depth >= 3 and len(empties) > 6:
                empties = self._prune_obstacles(tmpb, empties, player, 6)
            for obs in empties:
                if time.time() - start_time > time_limit:
                    break
                testb = self._clone_board(tmpb)
                testb.place_obstacle(obs)
                if testb.is_abluka(player):
                    continue
                if testb.is_abluka(opponent):
                    return mv, obs, 999999
                score = self._alpha_beta_minimax(
                    testb, depth, False, player, alpha, beta, start_time, time_limit
                )
                if score > best_score:
                    best_score = score
                    best_move = mv
                    best_obstacle = obs
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break
        return best_move, best_obstacle, best_score

    def _alpha_beta_minimax(self, board, depth, maximizing, main_player,
                            alpha, beta, start_time, time_limit):
        if time.time() - start_time > time_limit:
            return self._evaluate_board(board, main_player)
        if depth == 0:
            return self._evaluate_board(board, main_player)

        current_player = main_player if maximizing else ('W' if main_player == 'B' else 'B')
        opponent = 'W' if current_player == 'B' else 'B'

        if board.is_abluka(current_player):
            return -999999 if current_player == main_player else 999999
        valid_moves = board.get_valid_moves(current_player)
        if not valid_moves:
            return -999999 if current_player == main_player else 999999

        if maximizing:
            value = float('-inf')
            for mv in valid_moves:
                if time.time() - start_time > time_limit:
                    break
                tb = self._clone_board(board)
                tb.move_piece(current_player, mv)
                empties = self._get_empty_positions(tb)
                if len(empties) > 6:
                    empties = self._prune_obstacles(tb, empties, current_player, 6)
                for obs in empties:
                    if time.time() - start_time > time_limit:
                        break
                    tb2 = self._clone_board(tb)
                    tb2.place_obstacle(obs)
                    if tb2.is_abluka(current_player):
                        continue
                    if tb2.is_abluka(opponent):
                        return 999999
                    sc = self._alpha_beta_minimax(
                        tb2, depth - 1, False, main_player, alpha, beta, start_time, time_limit
                    )
                    value = max(value, sc)
                    alpha = max(alpha, value)
                    if beta <= alpha:
                        break
                if beta <= alpha:
                    break
            return value
        else:
            value = float('inf')
            for mv in valid_moves:
                if time.time() - start_time > time_limit:
                    break
                tb = self._clone_board(board)
                tb.move_piece(current_player, mv)
                empties = self._get_empty_positions(tb)
                if len(empties) > 6:
                    empties = self._prune_obstacles(tb, empties, current_player, 6)
                for obs in empties:
                    if time.time() - start_time > time_limit:
                        break
                    tb2 = self._clone_board(tb)
                    tb2.place_obstacle(obs)
                    if tb2.is_abluka(current_player):
                        continue
                    if tb2.is_abluka(main_player):
                        return -999999
                    sc = self._alpha_beta_minimax(
                        tb2, depth - 1, True, main_player, alpha, beta, start_time, time_limit
                    )
                    value = min(value, sc)
                    beta = min(beta, value)
                    if beta <= alpha:
                        break
                if beta <= alpha:
                    break
            return value

    # -------------------------------------------------------------------------
    # HARD => ULTRA / MACHINE LEARNING
    # -------------------------------------------------------------------------
    def _init_learning_system(self):
        """Öğrenme sistemini başlat"""
        import os
        import pickle
        import numpy as np
        
        self.memory_file = "abluka_memory.pkl"
        
        # State değerlerini saklamak için Q-Table (sözlük yapısında)
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'rb') as f:
                    self.q_table = pickle.load(f)
                print("[RL] Mevcut öğrenme modeli yüklendi, toplam durum sayısı:", len(self.q_table))
            except Exception as e:
                print("[RL] Model yüklenirken hata:", e)
                self.q_table = {}
        else:
            self.q_table = {}
        
        # Öğrenme parametreleri
        self.learning_rate = 0.1      # Alfa - ne kadar hızlı öğrenecek
        self.discount_factor = 0.95   # Gamma - gelecekteki ödülleri ne kadar değerli görecek
        self.exploration_rate = 0.5   # Epsilon - keşif oranı (0.3'ten 0.5'e yükseltildi)
        self.min_exploration_rate = 0.01  # Minimum keşif oranı 
        self.exploration_decay = 0.995  # Her oyundan sonra keşif oranını azalt
        
        # Oyun hafızası
        self.current_game_states = []  # Bu oyun için durum geçmişi
        self.current_game_moves = []   # Bu oyun için hamle geçmişi
        self.current_game_rewards = [] # Bu oyun için ödül geçmişi
        
        # Son oyundaki öğrenme bilgisini kaydet
        self.learned_move_count = 0
        self.current_state = None
        
        print("[RL] Öğrenme sistemi başlatıldı.")

    def save_model(self):
        """Q-table'ı diske kaydet"""
        if not self.learning_enabled:
            return
            
        import pickle
        try:
            with open(self.memory_file, 'wb') as f:
                pickle.dump(self.q_table, f)
            print(f"[RL] Model kaydedildi. Toplam durum sayısı: {len(self.q_table)}")
        except Exception as e:
            print(f"[RL] Model kaydedilirken hata: {e}")

    def _state_to_features(self, board, player):
        """
        Tahta durumundan öğrenilebilir özellikler çıkar.
        Daha detaylı bir durum temsili kullanarak öğrenmeyi iyileştir.
        """
        opponent = 'W' if player == 'B' else 'B'
        
        # Taşların konumlarını al
        my_pos = board.black_pos if player == 'B' else board.white_pos
        op_pos = board.black_pos if opponent == 'B' else board.white_pos
        
        # Temel mobilite
        my_moves = len(board.get_valid_moves(player))
        op_moves = len(board.get_valid_moves(opponent))
        
        # Oyun alanının kaçta kaçı engelli?
        obstacle_ratio = min(9, len(board.obstacles) // (board.size * board.size // 10))
        
        # Taşların birbirine olan mesafesi (Manhattan)
        distance = abs(my_pos[0] - op_pos[0]) + abs(my_pos[1] - op_pos[1])
        
        # Taşların kuadrantı (0-1-2-3 şeklinde)
        my_quad = (1 if my_pos[0] >= board.size // 2 else 0) + (2 if my_pos[1] >= board.size // 2 else 0)
        op_quad = (1 if op_pos[0] >= board.size // 2 else 0) + (2 if op_pos[1] >= board.size // 2 else 0)
        
        # YENİ: Taşların tahta üzerindeki konumlarını normalize et (0-4 arası değerler)
        # Daha hassas pozisyon bilgisi için
        norm_my_row = min(4, my_pos[0] * 5 // board.size)  
        norm_my_col = min(4, my_pos[1] * 5 // board.size)
        norm_op_row = min(4, op_pos[0] * 5 // board.size)
        norm_op_col = min(4, op_pos[1] * 5 // board.size)
        
        # YENİ: Taşların etrafındaki engel sayıları
        my_obstacles = min(7, self._count_surrounding_obstacles(board, my_pos))
        op_obstacles = min(7, self._count_surrounding_obstacles(board, op_pos))
        
        # YENİ: Merkeze olan uzaklık farkı
        center = board.size // 2
        my_center_dist = abs(my_pos[0] - center) + abs(my_pos[1] - center)
        op_center_dist = abs(op_pos[0] - center) + abs(op_pos[1] - center)
        center_diff = min(3, max(-3, op_center_dist - my_center_dist))
        
        # YENİ: Rakibin ne kadar sıkıştırıldığı (çevreleme oranı)
        encirclement = min(9, int(self._calculate_encirclement(board, opponent) / 10))
        
        # YENİ: Köşelerle ilişki (köşelere ne kadar yakın?)
        edge_distance = min(3, min(
            my_pos[0], 
            my_pos[1], 
            board.size - 1 - my_pos[0], 
            board.size - 1 - my_pos[1]
        ))
        
        # Geliştirilmiş durum temsili - daha fazla özellik içeriyor
        state = (
            norm_my_row,         # 0-4 arası (5 değer) - kesin konum bilgisi
            norm_my_col,         # 0-4 arası (5 değer)
            norm_op_row,         # 0-4 arası (5 değer) 
            norm_op_col,         # 0-4 arası (5 değer)
            min(8, my_moves),    # 0-8 arası (9 değer)
            min(8, op_moves),    # 0-8 arası (9 değer)
            min(4, distance//2), # 0-4 arası (5 değer)
            my_obstacles,        # 0-7 arası (8 değer)
            op_obstacles,        # 0-7 arası (8 değer)
            center_diff + 3,     # 0-6 arası (7 değer) (-3 ile +3 arası)
            encirclement,        # 0-9 arası (10 değer)
            edge_distance,       # 0-3 arası (4 değer)
            obstacle_ratio       # 0-9 arası (10 değer)
        )
        
        # Bu durum tanımı daha zengin bilgiler içeriyor ama hala yönetilebilir boyutta
        return state

    def _get_reward(self, board, player, move, obstacle, prev_state, new_state):
        """Bir hamle için ödül hesapla"""
        opponent = 'W' if player == 'B' else 'B'
        
        # Ana ödül bileşenleri
        reward = 0
        
        # Rakibi ablukaya aldı mı? (kazandı mı?)
        if board.is_abluka(opponent):
            return 100  # Kazanma durumu, maksimum ödül
        
        # Kendini ablukaya aldı mı? (kaybetti mi?)  
        if board.is_abluka(player):
            return -80  # Kaybetme durumu cezası -50'den -80'e yükseltildi
        
        # Şu anki durum bilgileri
        prev_my_moves = prev_state[2]  # kendi hareketleri
        prev_op_moves = prev_state[3]  # rakip hareketleri
        new_my_moves = new_state[2]    # hamleden sonra kendi hareketleri
        new_op_moves = new_state[3]    # hamleden sonra rakip hareketleri
        
        # Önceki mesafe ve yeni mesafe
        prev_distance = prev_state[4] * 2  # state'te //2 yapmıştık, geri çevir
        new_distance = new_state[4] * 2
        
        # Ödül 1: Kendi hareket alanı arttıysa
        if new_my_moves > prev_my_moves:
            reward += 1
        
        # Ödül 2: Rakibin hareket sayısı azaldıysa
        if new_op_moves < prev_op_moves:
            reward += 2
        
        # Ceza 1: Kendi etrafını daraltıyorsa
        if new_my_moves < prev_my_moves:
            reward -= 3
        
        # Ödül 3: Rakibi köşeye sıkıştırma - (baskı etkisi)
        # Etrafındaki doluluk oranına bakalım
        my_pos = board.black_pos if player == 'B' else board.white_pos
        op_pos = board.black_pos if opponent == 'B' else board.white_pos
        
        # Rakibin etrafındaki engel sayısını hesapla
        op_obstacles = self._count_surrounding_obstacles(board, op_pos)
        
        # Rakibin köşeye/duvara yakın olması durumu
        edge_dist = min(
            op_pos[0], 
            op_pos[1], 
            board.size - 1 - op_pos[0], 
            board.size - 1 - op_pos[1]
        )
        
        if edge_dist <= 1 and op_obstacles >= 2:  # Köşede ve sıkışık
            reward += 2
            
        # Ödül 4: Rakibe yaklaşmak (özellikle ilk hamleler)
        # Move_counter'ı kullanarak ilk hamlelerde daha yüksek ödül ver
        move_bonus = 1.0
        if self.move_counter <= 10:  # İlk 10 hamlede bonus
            move_bonus = 1.5
            
        if new_distance < prev_distance:
            reward += 1 * move_bonus
            
        # Ödül/Ceza 5: Engel taşı stratejik mi yoksa boşa mı yerleştirildi?
        if obstacle:
            # Stratejik engel kontrolü: Rakibin önünü kapatan engel
            # Rakibin yönüne doğru bakış
            rakip_yonu = (
                op_pos[0] - my_pos[0],
                op_pos[1] - my_pos[1]
            )
            
            # Engelin rakip yönünde olup olmadığını kontrol et
            engel_yonu = (
                obstacle[0] - my_pos[0],
                obstacle[1] - my_pos[1]
            )
            
            # İki vektör arasındaki yön benzerliği (dot product işareti)
            ayni_yon = (rakip_yonu[0] * engel_yonu[0] + rakip_yonu[1] * engel_yonu[1]) > 0
            
            # Engel rakip ile arasında mı?
            engel_mesafe = abs(obstacle[0] - my_pos[0]) + abs(obstacle[1] - my_pos[1])
            rakip_mesafe = abs(op_pos[0] - my_pos[0]) + abs(op_pos[1] - my_pos[1])
            
            # Rakibin önünü kapatan engel
            if ayni_yon and engel_mesafe < rakip_mesafe:
                # Doğrudan rakibin önünde ve yakınındaki engeller
                op_engel_mesafe = abs(obstacle[0] - op_pos[0]) + abs(obstacle[1] - op_pos[1])
                if op_engel_mesafe <= 2:  # Rakibe yakın engeller
                    reward += 10  # Stratejik engel bonusu
            
            # Engelin boşa yerleştirilip yerleştirilmediğini kontrol et
            # Hiçbir oyuncunun alanını etkilemiyorsa
            eski_benim = prev_my_moves
            eski_rakip = prev_op_moves
            
            # Engel yokmuş gibi hesapla
            temp_board = self._clone_board(board)
            temp_board.grid[obstacle[0]][obstacle[1]] = None
            # Engeli obstacles listesinden kaldırmaya çalışırken hata kontrolü yap
            if obstacle in temp_board.obstacles:
                temp_board.obstacles.remove(obstacle)
            
            benim_alan_engelsiz = len(temp_board.get_valid_moves(player))
            rakip_alan_engelsiz = len(temp_board.get_valid_moves(opponent))
            
            if benim_alan_engelsiz == eski_benim and rakip_alan_engelsiz == eski_rakip:
                reward -= 2  # Boşa yerleştirilen engel cezası
        
        # Nihai ödül
        return reward

    def _choose_move_ultra_ml(self, board, player, time_limit, start_time):
        """
        Hard mod: Makine öğrenmesi entegre edilmiş gelişmiş strateji.
        Bu fonksiyon öğrendikçe daha da güçlenecektir.
        """
        if not self.learning_enabled:
            self.last_move_reasoning = "Hard: Learning disabled, using fallback"
            return self._choose_move_old_hard(board, player, time_limit, start_time)
            
        # Şu anki durumu çıkar
        current_state = self._state_to_features(board, player)
        self.current_state = current_state
        
        # Anında kazanma kontrolü - her zaman öncelikli
        immediate_win = self._check_immediate_win(board, player)
        if immediate_win:
            self.last_move_reasoning = "Hard-ML: Anında kazanma hamlesi!"
            return immediate_win
        
        # Geçerli hamleleri al
        valid_moves = board.get_valid_moves(player)
        opponent = 'W' if player == 'B' else 'B'
        
        # Hamle seçimi - epsilon-greedy politikası
        # Self-play ve normal oyun ayrımı: 
        # Self-play sırasında normal exploration rate kullan
        # Normal insan oyununda exploration_rate = 0 (pure exploitation)
        import random
        import math
        
        # İnsan karşısında exploration yok (self_play metodunda çağrılmıyorsa)
        actual_exploration_rate = 0.0 if not hasattr(self, '_in_self_play') else self.exploration_rate
        
        is_exploration = random.random() < actual_exploration_rate
        
        if is_exploration:
            # Keşif modu - rastgele ama akıllıca
            self.last_move_reasoning = "Hard-ML: Keşif modu (epsilon-greedy)"
            
            # Tamamen rastgele değil, daha akıllı keşif
            # Hamleleri değerlendir ve top %70'ini seç
            scored_moves = []
            for move in valid_moves:
                score = self._evaluate_move(board, player, move)
                scored_moves.append((move, score))
                
            # Hamleleri sırala ve en iyi %70'ini al
            scored_moves.sort(key=lambda x: x[1], reverse=True)
            exploration_pool = scored_moves[:max(1, int(len(scored_moves) * 0.7))]
            
            # Bu havuzdan rastgele seç
            selected_move, _ = random.choice(exploration_pool)
            
            # Şimdi engelleri değerlendir
            move_board = self._clone_board(board)
            move_board.move_piece(player, selected_move)
            
            # Engel konumlarını al
            empties = self._get_empty_positions(move_board)
            
            if not empties:
                return self._choose_move_old_hard(board, player, time_limit, start_time)
            
            # Kendini ablukaya almayan hamle bul
            for move in empties:
                move_board = self._clone_board(board)
                move_board.place_obstacle(move)
                
                # Kendimizi ablukaya almadığından emin ol
                if move_board.is_abluka(player) or len(move_board.get_valid_moves(player)) == 0:
                    continue
                    
                # Rakibi ablukaya alıyorsa hemen seç
                if move_board.is_abluka(opponent):
                    self.last_move_reasoning = "Hard-ML: Keşif sırasında abluka!"
                    return selected_move, move
            
            # Güvenli hamle bulunamadıysa fallback
            return self._choose_move_old_hard(board, player, time_limit, start_time)
        
        # Exploitation - öğrenilen bilgileri kullan
        self.last_move_reasoning = "Hard-ML: Öğrenilen bilgileri kullanma"
        
        best_move = None
        best_obstacle = None
        best_value = float('-inf')
        best_state = None
        
        # Bütün olası hamleleri dene ve değerlendir
        for move in valid_moves:
            move_board = self._clone_board(board)
            move_board.move_piece(player, move)
            
            # Engel konumlarını al
            empties = self._get_empty_positions(move_board)
            
            # Çok fazla engel varsa budalım
            if len(empties) > 8:
                empties = self._prune_obstacles(move_board, empties, player, 8)
            
            # Engelleri değerlendir
            for obs_pos in empties:
                test_board = self._clone_board(move_board)
                test_board.place_obstacle(obs_pos)
                
                # Kendimizi ablukaya almadığından emin ol
                if test_board.is_abluka(player) or len(test_board.get_valid_moves(player)) == 0:
                    continue
                    
                # Rakibi ablukaya alıyorsa hemen seç
                if test_board.is_abluka(opponent):
                    self.last_move_reasoning = "Hard-ML: Abluka hamlesi!"
                    return move, obs_pos
                
                # Bu hareketin durumunu hesapla
                new_state = self._state_to_features(test_board, player)
                
                # Q değerini sözlükten bul veya varsayılan değeri kullan
                state_value = self.q_table.get(new_state, 0)
                
                # Biraz da heuristic değerlendirme ekle (hibrit yaklaşım)
                heuristic_value = self._evaluate_board(test_board, player) / 1000  # Normalize et
                
                # Toplam değer
                total_value = state_value + heuristic_value
                
                # En iyi hamleyi güncelle
                if total_value > best_value:
                    best_value = total_value
                    best_move = move
                    best_obstacle = obs_pos
                    best_state = new_state
        
        # Eğer iyi bir hamle bulunamadıysa, fallback stratejileri kullan
        if best_move is None or best_obstacle is None:
            self.last_move_reasoning = "Hard-ML: Uygun hamle bulunamadı, fallback"
            return self._choose_move_old_hard(board, player, time_limit, start_time)
        
        # Hamleyi kaydet (sonradan öğrenmek için)
        if self.current_state and best_state:
            self.current_game_states.append(self.current_state)
            self.current_game_moves.append((best_move, best_obstacle))
            
            # Hamle öncesi durumu ve sonrası durumu karşılaştırarak bir ödül hesapla
            reward = self._get_reward(board, player, best_move, best_obstacle, 
                                    self.current_state, best_state)
            self.current_game_rewards.append(reward)
            
            # Hamlenin öğrenme puanını güncelle
            self._update_q_value(self.current_state, best_state, reward)
            
            self.learned_move_count += 1
            
            # Modeli belirli aralıklarla kaydet
            if self.learned_move_count % 5 == 0:
                self.save_model()
                
        # En iyi hamleyi döndür
        value_text = f"{best_value:.2f}" if best_value != float('-inf') else "N/A"
        self.last_move_reasoning += f" (Değer: {value_text}, Öğrenilen toplam durum: {len(self.q_table)})"
        
        return best_move, best_obstacle

    def _update_q_value(self, state, next_state, reward):
        """Q değerini güncelle - Q-learning algoritması"""
        if not self.learning_enabled:
            return
            
        # Mevcut değeri al (yoksa 0)
        current_q = self.q_table.get(state, 0)
        
        # Bir sonraki durumun değerini al (yoksa 0)
        next_q = self.q_table.get(next_state, 0)
        
        # Q öğrenme formülü: Q(s,a) = Q(s,a) + alpha * (reward + gamma * max(Q(s',a')) - Q(s,a))
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * next_q - current_q)
        
        # Q tablosunu güncelle
        self.q_table[state] = new_q

    def game_over_update(self, winner, player):
        """Oyun bittiğinde öğrenme güncellemelerini yap"""
        if not self.learning_enabled or len(self.current_game_states) == 0:
            return
            
        print(f"\n[RL] Oyun sonu öğrenmesi başlıyor...")
        print(f"[RL] Öğrenilen durumlar: {len(self.current_game_states)}")
        print(f"[RL] Kazanan oyuncu: {'AI' if winner == player else 'Rakip'}")
        
        # Öğrenilecek durum sayısını hatırla
        old_state_count = len(self.q_table)
            
        # Kazanma/kaybetme durumuna göre son hamlenin ödülünü ayarla
        final_reward = 200 if winner == player else -50
        
        # Son hamleyi güncelle
        if len(self.current_game_states) > 0:
            self.current_game_rewards[-1] = final_reward
        
        # Tüm oyun geçmişini geriye doğru güncelleyerek öğren (Temporal Difference Learning)
        cumulative_reward = final_reward
        
        # Hamleleri sondan başa doğru değerlendir
        for i in range(len(self.current_game_states) - 1, -1, -1):
            state = self.current_game_states[i]
            next_state = self.current_game_states[i] if i == len(self.current_game_states) - 1 else self.current_game_states[i + 1]
            
            # Önceki Q değerini al
            old_q = self.q_table.get(state, 0)
            
            # Q değerini güncelle
            current_q = self.q_table.get(state, 0)
            next_q = self.q_table.get(next_state, 0)
            new_q = current_q + self.learning_rate * (cumulative_reward + self.discount_factor * next_q - current_q)
            self.q_table[state] = new_q
            
            # Log düşelim
            if i % 5 == 0:  # Her 5 durumda bir log (çok fazla log olmaması için)
                print(f"[RL] Durum #{i}: Q değeri {old_q:.2f} -> {new_q:.2f} (değişim: {new_q-old_q:.2f})")
            
            # Ödülü her adımda azalt (geriye doğru)
            cumulative_reward *= self.discount_factor
        
        # Yeni öğrenilen toplam durum sayısı
        new_states_count = len(self.q_table) - old_state_count
        
        print(f"[RL] Oyun sonucu öğrenme tamamlandı!")
        print(f"[RL] Toplam durum sayısı: {len(self.q_table)} (bu oyunda öğrenilen yeni durumlar: {new_states_count})")
        
        # Öğrenilen bilgiyi kaydet
        self.save_model()
        
        # Yeni oyun için sıfırla
        self.current_game_states = []
        self.current_game_moves = []
        self.current_game_rewards = []
        
        # Keşif oranını azalt (dinamik keşif)
        self.exploration_rate = max(self.min_exploration_rate, 
                                   self.exploration_rate * self.exploration_decay)
        print(f"[RL] Yeni keşif oranı: {self.exploration_rate:.4f}")

    def get_learning_stats(self):
        """Öğrenme istatistiklerini dön"""
        if not self.learning_enabled:
            return {"enabled": False}
            
        return {
            "enabled": True,
            "total_states": len(self.q_table),
            "current_game_states": len(self.current_game_states),
            "learning_rate": self.learning_rate,
            "exploration_rate": self.exploration_rate,
            "last_move_reasoning": self.last_move_reasoning
        }

    # -------------------------------------------------------------------------
    # Yardımcı Metotlar
    # -------------------------------------------------------------------------
    def _check_immediate_win(self, board, player):
        """Rakibi hemen ablukaya alacak hamle varsa onu döndür."""
        opp = 'W' if player == 'B' else 'B'
        valid_moves = board.get_valid_moves(player)
        for mv in valid_moves:
            tb = self._clone_board(board)
            tb.move_piece(player, mv)
            empties = self._get_empty_positions(tb)
            for obs in empties:
                testb = self._clone_board(tb)
                testb.place_obstacle(obs)
                if not testb.is_abluka(player) and testb.is_abluka(opp):
                    return (mv, obs)
        return None

    def _evaluate_board(self, board, main_player):
        """
        Genel (iyileştirilmiş) heuristik: 
        - Mobilite
        - BFS alan farkı
        - Çevreleme
        - Engeller
        - vs.
        """
        my_moves = board.get_valid_moves(main_player)
        if not my_moves:
            return -999999

        opponent = 'W' if main_player == 'B' else 'B'
        op_moves = board.get_valid_moves(opponent)
        if not op_moves:
            return 999999

        # mobilite
        mobil_score = (len(my_moves)*10) - (len(op_moves)*6)

        # BFS alan
        my_area = self._flood_fill_area(board, main_player)
        op_area = self._flood_fill_area(board, opponent)
        area_score = (my_area - op_area)*4

        # Çevreleme
        encirc = self._calculate_encirclement(board, opponent)
        enc_score = encirc*8

        # Merkeze yakınlık vs.
        mp = board.black_pos if main_player=='B' else board.white_pos
        op = board.black_pos if opponent=='B' else board.white_pos
        center = board.size // 2
        my_center_dist = abs(mp[0]-center) + abs(mp[1]-center)
        op_center_dist = abs(op[0]-center) + abs(op[1]-center)
        center_diff = (op_center_dist - my_center_dist)*2

        # Etraftaki engel farkı
        my_obs = self._count_surrounding_obstacles(board, mp)
        op_obs = self._count_surrounding_obstacles(board, op)
        obs_diff = (op_obs - my_obs)*5

        return mobil_score + area_score + enc_score + center_diff + obs_diff

    def _calculate_win_probability(self, board, player):
        # Basit oransal yaklaşım
        opp = 'W' if player=='B' else 'B'
        my_moves = len(board.get_valid_moves(player))
        op_moves = len(board.get_valid_moves(opp))
        if my_moves == 0:
            return 5.0
        if op_moves == 0:
            return 95.0
        ratio = my_moves / max(1, op_moves)
        ratio = min(ratio, 3.0)
        prob = 50 + (ratio-1)*20  # oransal kabaca
        return max(5, min(95, prob))

    def _flood_fill_area(self, board, player):
        start = board.black_pos if player=='B' else board.white_pos
        visited = set()
        stack = [start]
        count = 0
        while stack:
            r, c = stack.pop()
            if (r, c) in visited:
                continue
            visited.add((r, c))
            cell = board.grid[r][c]
            if cell is None or cell == player:
                count += 1
                # 8 yön
                for dr, dc in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)]:
                    rr = r+dr
                    cc = c+dc
                    if 0 <= rr < board.size and 0 <= cc < board.size:
                        if (rr, cc) not in visited:
                            cell2 = board.grid[rr][cc]
                            if cell2 is None or cell2 == player:
                                stack.append((rr, cc))
        return count

    def _calculate_encirclement(self, board, opponent):
        op_pos = board.black_pos if opponent=='B' else board.white_pos
        reachable = self._flood_fill_area(board, opponent)
        total = board.size*board.size - len(board.obstacles)
        enc = 1.0 - (reachable / max(1, total))
        return enc*100

    def _count_surrounding_obstacles(self, board, pos):
        """Bir pozisyonun çevresindeki 8 hücrede engel sayısı."""
        r, c = pos
        cnt = 0
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)]:
            rr = r+dr
            cc = c+dc
            if 0<=rr<board.size and 0<=cc<board.size:
                cell = board.grid[rr][cc]
                if cell == 'X' or cell == 'R':
                    cnt += 1
        return cnt

    def _get_empty_positions(self, board):
        empties = []
        for r in range(board.size):
            for c in range(board.size):
                if board.grid[r][c] is None:
                    empties.append((r,c))
        return empties

    def _prune_moves(self, board, player, moves, limit):
        scored = []
        for mv in moves:
            tempb = self._clone_board(board)
            tempb.move_piece(player, mv)
            sc = self._evaluate_board(tempb, player)
            scored.append((mv, sc))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [m for m,_ in scored[:limit]]

    def _prune_obstacles(self, board, empties, player, top_k=6):
        scored = []
        opponent = 'W' if player=='B' else 'B'
        op_moves = len(board.get_valid_moves(opponent))
        for e in empties:
            tb = self._clone_board(board)
            tb.place_obstacle(e)
            if tb.is_abluka(player):
                continue
            sc = self._evaluate_board(tb, player)
            # rakibin mobilitesini ne kadar düşürüyor
            op_m_after = len(tb.get_valid_moves(opponent))
            diff = op_moves - op_m_after
            sc += diff*15
            scored.append((e, sc))
        if not scored:
            return empties[:top_k]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [pos for pos,_ in scored[:top_k]]

    def _clone_board(self, board):
        from abluka.game_logic import Board
        clone = Board()
        clone.size = board.size
        clone.grid = [row[:] for row in board.grid]
        clone.black_pos = board.black_pos
        clone.white_pos = board.white_pos
        clone.obstacles = board.obstacles.copy()
        return clone

    def _evaluate_move(self, board, player, move):
        """Hızlı tek hamle değerlendirmesi."""
        tb = self._clone_board(board)
        tb.move_piece(player, move)
        return self._evaluate_board(tb, player)

    def _random_reaction(self, emoji_list, msg_list):
        return f"{random.choice(emoji_list)} {random.choice(msg_list)}"

    def _assess_emotion(self, board, player):
        opp = 'W' if player=='B' else 'B'
        my_mob = len(board.get_valid_moves(player))
        op_mob = len(board.get_valid_moves(opp))
        if self.last_mobility is not None and my_mob < self.last_mobility:
            self.current_message = self._random_reaction(
                self.emojis['worried'], self.messages['worried']
            )
        elif op_mob == 0:
            self.current_message = self._random_reaction(
                self.emojis['smug'], self.messages['confident']
            )
        elif my_mob == 1:
            self.current_message = self._random_reaction(
                self.emojis['worried'], self.messages['trapped']
            )
        else:
            if random.random() < 0.2:
                self.current_message = self._random_reaction(
                    self.emojis['thinking'], self.messages['thinking']
                )
            else:
                self.current_message = None
        self.last_mobility = my_mob

    # Yeni self-play metotları
    def do_self_play(self, game_count=10):
        """AI'ın kendi kendine oynayarak öğrenmesi"""
        import time
        from abluka.game_logic import Game
        
        print(f"\n[RL] Self-play başlatılıyor: {game_count} oyun...")
        start_time = time.time()
        
        # Self-play modunu belirle
        self._in_self_play = True
        
        # Başlangıç durum sayısı
        old_state_count = len(self.q_table)
        
        # Self-play döngüsü
        for i in range(game_count):
            # Yeni oyun oluştur
            game = Game()
            
            # Oyun bitene kadar devam et
            while not game.is_game_over:
                current_player = game.current_player
                
                # Sıra siyah oyuncuda - exploration'ı arttır
                if current_player == 'B':
                    temp_exploration = self.exploration_rate
                    self.exploration_rate = min(0.7, self.exploration_rate * 1.2)  # Daha fazla keşif
                    move, obstacle = self._choose_move_ultra_ml(game.board, current_player, 1.0, time.time())
                    self.exploration_rate = temp_exploration  # Geri al
                else:
                    move, obstacle = self._choose_move_ultra_ml(game.board, current_player, 1.0, time.time())
                
                # Hamleyi uygula
                game.make_move(move, obstacle)
            
            # Oyun sonu öğrenimi
            winner = game.winner
            self.game_over_update(winner, 'B')  # Siyah oyuncu olarak analiz et
            
            # Beyaz oyuncu olarak da öğren
            self.current_game_states = []
            self.current_game_moves = []
            self.current_game_rewards = []
            self.game_over_update(winner, 'W')  # Beyaz oyuncu olarak analiz et
            
            # İlerleme bilgisi
            if (i+1) % 5 == 0 or i == game_count-1:
                elapsed = time.time() - start_time
                print(f"[RL] {i+1}/{game_count} oyun tamamlandı ({elapsed:.1f}s), durum sayısı: {len(self.q_table)}")
        
        # Self-play modunu kapat
        self._in_self_play = False
        
        # Öğrenme sonuçları
        new_states_count = len(self.q_table) - old_state_count
        print(f"\n[RL] Self-play tamamlandı!")
        print(f"[RL] Toplam durum sayısı: {len(self.q_table)} (öğrenilen yeni durumlar: {new_states_count})")
        
        # Öğrenilen bilgiyi kaydet
        self.save_model()
        return new_states_count

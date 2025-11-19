import time
import random
import math
import os
import datetime
from copy import deepcopy

class AIPlayer:
    """
    Geliştirilmiş Abluka AI
    - easy   : Sabit derinlikli Minimax/Alphabeta
    - normal : Iterative deepening + budamalı Minimax
    - hard   : Q-learning tabanlı self-play öğrenmesi + sabit Q-tablo kullanımı

    self-play sırasında:
      - exploration yüksek,
      - hamleler Q + heuristik ile seçilir,
      - geriye dönük ödül güncellemesi yapılır.

    gerçek oyunda (ör. insanla oynarken):
      - exploration=0,
      - Q tablosu sadece “en iyi bilinen” hamleyi seçmek için kullanılır,
      - ek eğitim (update) yapılmaz.
    """

    def __init__(self, difficulty='normal', max_time=5.0):
        self.difficulty = difficulty
        self.max_time = float(max_time)  # her hamlede düşünülecek max süre (saniye)

        # Minimax parametreleri - ULTRA İYİLEŞTİRİLMİŞ zorluk seviyeleri
        if self.difficulty == 'easy':
            self.base_depth = 2  # Daha basit düşünme
            self.max_time = max(self.max_time, 1.5)
            self.ml_usage_factor = 0.0  # Kolay modda ML yok
            self.randomness = 0.35  # %35 rastgele hamle
            self.min_safe_moves = 1  # Çok esnek - riske girer
            self.future_turns_check = 1  # 1 tur ilerisini kontrol et
            self.aggression = 0.3  # %30 saldırgan
        elif self.difficulty == 'normal':
            self.base_depth = 5  # Daha derin düşünme (4→5)
            self.max_time = max(self.max_time, 3.0)
            self.ml_usage_factor = 0.5  # Orta ML kullan (0.3→0.5)
            self.randomness = 0.08  # %8 rastgele hamle (15→8)
            self.min_safe_moves = 2  # Daha esnek (3→2)
            self.future_turns_check = 2  # 2 tur ilerisini kontrol et
            self.aggression = 0.65  # %65 saldırgan
        else:  # 'hard'
            self.base_depth = 6  # Çok derin düşünme (5→6)
            self.max_time = max(self.max_time, 4.0)
            self.ml_usage_factor = 1.0  # Tam kapasite ML
            self.randomness = 0.0  # Hiç rastgele yok (5→0)
            self.min_safe_moves = 2  # Dengeli risk (3→2)
            self.future_turns_check = 3  # 3 tur ilerisini kontrol et (2→3)
            self.aggression = 0.85  # %85 saldırgan - çok agresif!

        # Log / kayıt
        self.log_enabled = True
        self.game_log = []
        self.log_file = self._create_log_file()

        # Duygusal tepkiler (opsiyonel)
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
        self.last_move_reasoning = ""  # Debug amaçlı

        # ML sadece 'hard' modda gerçek anlamda aktif
        self.learning_enabled = (self.difficulty == 'hard')

        if self.learning_enabled:
            self._init_learning_system()
        else:
            # Hard dışındaki modlarda Q tablosu devreye girmeyecek
            self.q_table = {}
            self.learning_rate = 0.1
            self.discount_factor = 0.95
            self.exploration_rate = 0.0
            self.min_exploration_rate = 0.01
            self.exploration_decay = 0.99985

    def _create_log_file(self):
        """Log dosyası oluştur."""
        if not self.log_enabled:
            return None
        log_dir = "logs"
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except:
                print("Log klasörü oluşturulamadı, log devredışı.")
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
            print("Log dosyası oluşturulamadı, log devredışı.")
            self.log_enabled = False
            return None

    def _log_move(self, player, move, obstacle, strategy, board_state=None):
        if not self.log_enabled or not self.log_file:
            return
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"\nHamle #{len(self.game_log)+1}\n")
                f.write(f"Oyuncu: {'AI' if player!='Human' else 'İnsan'} ({player})\n")
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
                            elif cell in ('X','R'):
                                row_txt.append('X')
                            else:
                                row_txt.append('.')
                        f.write(' '.join(row_txt)+'\n')
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
        İyileştirilmiş hamle seçimi
        - Zorluk seviyesine göre gerçekçi davranış
        - İnsan benzeri "hatalar" (kolay/normal)
        - Stratejik düşünme (zor)
        """
        start_time = time.time()
        board = game_state['board']
        player = game_state['current_player']

        valid_moves = board.get_valid_moves(player)
        if not valid_moves:
            self.current_message = self._random_reaction(self.emojis['worried'], self.messages['trapped'])
            return None, None

        self.move_counter += 1
        self._assess_emotion(board, player)

        print(f"\n[AI] {player} (AI) hamle yapıyor. Zorluk: {self.difficulty}")
        print(f"[AI] Siyah: {board.black_pos}, Beyaz: {board.white_pos}")
        print(f"[AI] Siyah hamleleri: {len(board.get_valid_moves('B'))}, "
              f"Beyaz hamleleri: {len(board.get_valid_moves('W'))}")

        # Tahmini kazanma
        win_prob = self._calculate_win_probability(board, player)
        print(f"[AI] Kazanma olasılığı: %{win_prob:.1f}")

        # Direkt kazanma kontrolü (tüm zorluklar için)
        immediate = self._check_immediate_win(board, player)
        if immediate:
            mv, obs = immediate
            
            # KOLAY modda bazen belirgin kazanmayı kaçır (insan gibi)
            if self.difficulty == 'easy' and random.random() < 0.30:
                print("[AI] Kolay mod: Kazanma fırsatını gördü ama kaçırdı (insan hatası)")
                self.current_message = self._random_reaction(self.emojis['thinking'], self.messages['thinking'])
                # Normal hamle yap
                pass
            else:
                elapsed = time.time() - start_time
                self.current_message = self._random_reaction(self.emojis['excited'], self.messages['confident'])
                self.last_move_reasoning = "Direkt kazanma fırsatı!"
                self._log_move(player, mv, obs, self.last_move_reasoning, board)
                if elapsed < 0.5:
                    time.sleep(0.5 - elapsed)
                return mv, obs

        # İnsan benzeri düşünme süresi simülasyonu
        # Zor durumlarda daha uzun düşün
        my_moves_count = len(valid_moves)
        if my_moves_count <= 3:
            # Sıkışıktayım, daha uzun düşün
            min_think_time = 0.8 if self.difficulty == 'easy' else 1.2
        elif my_moves_count >= 6:
            # Rahatım, hızlı karar ver
            min_think_time = 0.4 if self.difficulty == 'easy' else 0.6
        else:
            min_think_time = 0.5 if self.difficulty == 'easy' else 0.8

        # Zorluk moduna göre hamle seç
        if self.difficulty == 'easy':
            mv, obs = self._choose_move_old_normal(board, player, self.max_time, start_time)
        elif self.difficulty == 'normal':
            mv, obs = self._choose_move_old_hard(board, player, self.max_time, start_time)
        else:
            mv, obs = self._choose_move_ultra_ml(board, player, self.max_time, start_time)

        elapsed = time.time() - start_time
        print(f"[AI] Süre: {elapsed:.2f} sn => Hamle: {mv}, Engel: {obs}")
        print(f"[AI] Strateji: {self.last_move_reasoning}")

        if mv and obs:
            temp_b = self._clone_board(board)
            temp_b.move_piece(player, mv)
            temp_b.place_obstacle(obs)
            fut_prob = self._calculate_win_probability(temp_b, player)
            opponent = ('W' if player == 'B' else 'B')
            opp_m = len(temp_b.get_valid_moves(opponent))
            my_m = len(temp_b.get_valid_moves(player))
            print(f"[AI] Sonrası kazanma: %{fut_prob:.1f}")
            print(f"[AI] Rakip hamle: {opp_m}, Benim hamle: {my_m}")
            
            # Hamleden sonra duygusal tepki
            if fut_prob > 70:
                self.current_message = self._random_reaction(self.emojis['smug'], self.messages['confident'])
            elif fut_prob < 30:
                self.current_message = self._random_reaction(self.emojis['worried'], self.messages['worried'])

        self._log_move(player, mv, obs, self.last_move_reasoning, board)
        
        # Minimum düşünme süresini garantile (gerçekçi görünmek için)
        if elapsed < min_think_time:
            time.sleep(min_think_time - elapsed)
        
        return mv, obs

    def get_reaction(self):
        return self.current_message

    # -------------------------------
    # EASY => Sabit Derinlikli
    # -------------------------------
    def _choose_move_old_normal(self, board, player, time_limit, start_time):
        """
        İYİLEŞTİRİLMİŞ KOLAY mod:
        - GÜVENLİK + BASİT STRATEJİ
        - Bazen rastgele, bazen akıllı
        - Çok basit pozisyon değerlendirmesi
        - İnsan gibi hata yapar ama tamamen rastgele değil
        """
        valid_moves = board.get_valid_moves(player)
        if not valid_moves:
            return None, None
        
        opponent = 'W' if player == 'B' else 'B'
        
        print(f"[AI-KOLAY] {len(valid_moves)} hamle değerlendiriliyor...")
        
        # ÖNCE GÜVENLİ HAMLELERİ TOPLA
        safe_moves = []
        
        for mv in valid_moves:
            tmpb = self._clone_board(board)
            tmpb.move_piece(player, mv)
            empties = self._get_empty_positions(tmpb)
            
            # Engel sayısını sınırla (hız için)
            if len(empties) > 15:
                empties = self._prune_obstacles(tmpb, empties, player, 15)
            
            # Her hamle için güvenli engelleri bul
            for obs in empties:
                is_safe, reason = self._is_safe_move(board, player, mv, obs)
                
                if is_safe:
                    tb2 = self._clone_board(tmpb)
                    tb2.place_obstacle(obs)
                    
                    # Basit skor hesaplama
                    my_moves_after = len(tb2.get_valid_moves(player))
                    opp_moves_after = len(tb2.get_valid_moves(opponent))
                    
                    # Basit: Benim hamlem çok, rakibin az
                    simple_score = my_moves_after * 15 - opp_moves_after * 10
                    
                    # Kaçış yolları bonusu
                    escape = self._get_escape_routes(tb2, player)
                    simple_score += escape / 15
                    
                    # Rakibi ablukaya aldık mı? (bunu görebilir)
                    if tb2.is_abluka(opponent):
                        simple_score += 10000  # Kazanma hamlesini görür
                    
                    safe_moves.append((mv, obs, simple_score))
        
        print(f"[AI-KOLAY] {len(safe_moves)} güvenli hamle bulundu")
        
        if not safe_moves:
            print("[AI-KOLAY] UYARI: Güvenli hamle yok! Rastgele deniyorum")
            # Acil durum: Rastgele güvenli hamle dene
            for _ in range(10):
                mv = random.choice(valid_moves)
                tmpb = self._clone_board(board)
                tmpb.move_piece(player, mv)
                empties = self._get_empty_positions(tmpb)
                if empties:
                    obs = random.choice(empties[:10])
                    tb = self._clone_board(tmpb)
                    tb.place_obstacle(obs)
                    if not tb.is_abluka(player):
                        self.last_move_reasoning = "Kolay => Rastgele acil hamle"
                        return mv, obs
            return None, None
        
        # Güvenli hamleler arasından seç
        safe_moves.sort(key=lambda x: x[2], reverse=True)
        
        # Rastgele hamle oranı: %35
        if random.random() < self.randomness:
            # En iyi %60'lık dilimden rastgele seç (insan gibi)
            top_portion = max(5, int(len(safe_moves) * 0.6))
            choice = random.choice(safe_moves[:top_portion])
            self.last_move_reasoning = f"Kolay => Rastgele güvenli (skor: {choice[2]:.0f})"
            return choice[0], choice[1]
        
        # En iyi hamleyi seç
        best = safe_moves[0]
        self.last_move_reasoning = f"Kolay => En iyi güvenli (skor: {best[2]:.0f})"
        return best[0], best[1]

    def _minimax_evaluation(self, board, depth, maximizing, main_player, alpha, beta):
        if depth==0:
            return self._evaluate_board(board, main_player)
        current = main_player if maximizing else ('W' if main_player=='B' else 'B')
        if board.is_abluka(current):
            return -999999 if current==main_player else 999999
        val_moves = board.get_valid_moves(current)
        if not val_moves:
            return -999999 if current==main_player else 999999

        if maximizing:
            value = float('-inf')
            for mv in val_moves[:4]:
                b2 = self._clone_board(board)
                b2.move_piece(current, mv)
                empties = self._get_empty_positions(b2)
                if empties:
                    b2.place_obstacle(empties[0])
                sc = self._minimax_evaluation(b2, depth-1, False, main_player, alpha, beta)
                value = max(value, sc)
                alpha = max(alpha, value)
                if beta<=alpha:
                    break
            return value
        else:
            value = float('inf')
            for mv in val_moves[:4]:
                b2 = self._clone_board(board)
                b2.move_piece(current, mv)
                empties = self._get_empty_positions(b2)
                if empties:
                    b2.place_obstacle(empties[0])
                sc = self._minimax_evaluation(b2, depth-1, True, main_player, alpha, beta)
                value = min(value, sc)
                beta = min(beta, value)
                if beta<=alpha:
                    break
            return value

    # -------------------------------
    # NORMAL => Iterative Deepening
    # -------------------------------
    def _choose_move_old_hard(self, board, player, time_limit, start_time):
        """
        ULTRA İYİLEŞTİRİLMİŞ NORMAL mod:
        - AGRESYF + AKILLI STRATEJİ
        - Gelecek turları simüle eder
        - Çok iyi pozisyon değerlendirmesi
        - Rakibi ezmeye odaklanır
        - Minimax + heuristic
        """
        valid_moves = board.get_valid_moves(player)
        opponent = ('W' if player=='B' else 'B')
        
        print(f"[AI-NORMAL] {len(valid_moves)} hamle değerlendiriliyor...")

        # 1. HIZLI KAZANÇ KONTROL ET (ve güvenli olsun)
        for mv in valid_moves:
            tb = self._clone_board(board)
            tb.move_piece(player, mv)
            empties = self._get_empty_positions(tb)
            
            for obs in empties[:15]:  # 10→15 daha fazla kontrol
                is_safe, _ = self._is_safe_move(board, player, mv, obs)
                if not is_safe:
                    continue
                
                testb = self._clone_board(tb)
                testb.place_obstacle(obs)
                
                if testb.is_abluka(opponent):
                    self.last_move_reasoning = "Normal => Güvenli direkt kazanç!"
                    return mv, obs
        
        # 2. GÜVENLİ VE AGRESYF HAMLELERİ TOPLA
        safe_moves = []
        
        for mv in valid_moves:
            if time.time() - start_time > time_limit * 0.85:
                break
            
            tmpb = self._clone_board(board)
            tmpb.move_piece(player, mv)
            empties = self._get_empty_positions(tmpb)
            
            # Engel seçimini optimize et - daha fazla kontrol
            if len(empties) > 15:
                empties = self._prune_obstacles(tmpb, empties, player, 15)  # 10→15
            
            for obs in empties:
                if time.time() - start_time > time_limit * 0.9:
                    break
                
                # Güvenlik kontrolü
                is_safe, reason = self._is_safe_move(board, player, mv, obs)
                if not is_safe:
                    continue
                
                testb = self._clone_board(tmpb)
                testb.place_obstacle(obs)
                
                # POZİSYON DEĞERLENDİRMESİ - Çok detaylı
                score = self._evaluate_board(testb, player)
                
                # Kaçış yolları bonusu
                escape = self._get_escape_routes(testb, player)
                score += escape * 1.2  # 1.0→1.2 daha önemli
                
                # RAKİBE VERİLEN ZARAR - ULTRA BONUS
                opp_moves_before = len(board.get_valid_moves(opponent))
                opp_moves_after = len(testb.get_valid_moves(opponent))
                damage = opp_moves_before - opp_moves_after
                
                if damage > 0:
                    score += damage * 80  # Her azalan hamle için dev bonus
                
                # Rakibi çok sınırladıysak ekstra bonus
                if opp_moves_after <= 3:
                    score += 500  # Rakip neredeyse ablukada!
                elif opp_moves_after <= 5:
                    score += 250  # Rakip zorlanıyor
                
                # Minimax değerlendirmesi (hafif, çünkü zaman alıyor)
                if time.time() - start_time < time_limit * 0.7:
                    minimax_score = self._minimax_evaluation(testb, 2, True, player, 
                                                             float('-inf'), float('inf'))
                    score += minimax_score / 5.0  # Minimax'ı da dikkate al
                
                safe_moves.append((mv, obs, score))
        
        print(f"[AI-NORMAL] {len(safe_moves)} güvenli hamle bulundu")
        
        if not safe_moves:
            print("[AI-NORMAL] UYARI: Güvenli hamle yok! Esnek modda deniyorum")
            # Esnek mod: Daha az kısıtlı güvenlik
            for mv in valid_moves[:8]:  # 5→8 daha fazla dene
                tmpb = self._clone_board(board)
                tmpb.move_piece(player, mv)
                empties = self._get_empty_positions(tmpb)
                
                if len(empties) > 15:
                    empties = self._prune_obstacles(tmpb, empties, player, 15)
                
                for obs in empties[:15]:  # 10→15 daha fazla
                    tb = self._clone_board(tmpb)
                    tb.place_obstacle(obs)
                    
                    # Daha esnek güvenlik: En azından abluka olmamalı
                    if not tb.is_abluka(player) and len(tb.get_valid_moves(player)) >= 2:
                        score = self._evaluate_board(tb, player)
                        safe_moves.append((mv, obs, score))
            
            if not safe_moves:
                # Hala yok, kolay moda düş
                print("[AI-NORMAL] Son çare: Kolay mod stratejisi")
                return self._choose_move_old_normal(board, player, time_limit, start_time)
        
        # En iyi hamleyi seç
        safe_moves.sort(key=lambda x: x[2], reverse=True)
        
        # Çok az rastgelelik: %8
        if random.random() < self.randomness and len(safe_moves) > 8:
            # En iyi %20'lik dilimden seç (çok dar - neredeyse en iyisi)
            top_portion = max(3, int(len(safe_moves) * 0.2))  # 0.3→0.2
            choice = random.choice(safe_moves[:top_portion])
            self.last_move_reasoning = f"Normal => Üst seviye hamle (skor: {choice[2]:.0f})"
            return choice[0], choice[1]
        
        best = safe_moves[0]
        self.last_move_reasoning = f"Normal => Optimal hamle (skor: {best[2]:.0f})"
        return best[0], best[1]

    def _search_best_move(self, board, player, depth, start_time, time_limit):
        best_mv = None
        best_obs = None
        best_score = float('-inf')

        val_moves = board.get_valid_moves(player)
        if not val_moves:
            return None, None, -999999
        if len(val_moves)>6 and depth>=3:
            val_moves = self._prune_moves(board, player, val_moves, 6)

        alpha = float('-inf')
        beta = float('inf')
        opponent = ('W' if player=='B' else 'B')

        for mv in val_moves:
            if time.time()-start_time>time_limit*0.9:
                break
            tmpb = self._clone_board(board)
            tmpb.move_piece(player, mv)
            empties = self._get_empty_positions(tmpb)
            if depth>=3 and len(empties)>6:
                empties = self._prune_obstacles(tmpb, empties, player, 6)
            for obs in empties:
                if time.time()-start_time>time_limit:
                    break
                testb = self._clone_board(tmpb)
                testb.place_obstacle(obs)
                if testb.is_abluka(player):
                    continue
                if testb.is_abluka(opponent):
                    return mv, obs, 999999
                sc = self._alpha_beta_minimax(testb, depth, False, player, alpha, beta, start_time, time_limit)
                if sc>best_score:
                    best_score = sc
                    best_mv = mv
                    best_obs = obs
                alpha = max(alpha, best_score)
                if beta<=alpha:
                    break
        return best_mv, best_obs, best_score

    def _alpha_beta_minimax(self, board, depth, maximizing, main_player, alpha, beta, start_time, time_limit):
        if time.time()-start_time>time_limit:
            return self._evaluate_board(board, main_player)
        if depth==0:
            return self._evaluate_board(board, main_player)

        current = main_player if maximizing else ('W' if main_player=='B' else 'B')
        opp = ('W' if current=='B' else 'B')

        if board.is_abluka(current):
            return -999999 if current==main_player else 999999
        val_moves = board.get_valid_moves(current)
        if not val_moves:
            return -999999 if current==main_player else 999999

        if maximizing:
            value = float('-inf')
            for mv in val_moves:
                if time.time()-start_time>time_limit: break
                b2 = self._clone_board(board)
                b2.move_piece(current, mv)
                empties = self._get_empty_positions(b2)
                if len(empties)>6:
                    empties = self._prune_obstacles(b2, empties, current, 6)
                for obs in empties:
                    if time.time()-start_time>time_limit: break
                    b3 = self._clone_board(b2)
                    b3.place_obstacle(obs)
                    if b3.is_abluka(current):
                        continue
                    if b3.is_abluka(opp):
                        return 999999
                    sc = self._alpha_beta_minimax(b3, depth-1, False, main_player, alpha, beta, start_time, time_limit)
                    value = max(value, sc)
                    alpha = max(alpha, value)
                    if beta<=alpha:
                        break
                if beta<=alpha:
                    break
            return value
        else:
            value = float('inf')
            for mv in val_moves:
                if time.time()-start_time>time_limit: break
                b2 = self._clone_board(board)
                b2.move_piece(current, mv)
                empties = self._get_empty_positions(b2)
                if len(empties)>6:
                    empties = self._prune_obstacles(b2, empties, current, 6)
                for obs in empties:
                    if time.time()-start_time>time_limit: break
                    b3 = self._clone_board(b2)
                    b3.place_obstacle(obs)
                    if b3.is_abluka(current):
                        continue
                    if b3.is_abluka(main_player):
                        return -999999
                    sc = self._alpha_beta_minimax(b3, depth-1, True, main_player, alpha, beta, start_time, time_limit)
                    value = min(value, sc)
                    beta = min(beta, value)
                    if beta<=alpha:
                        break
                if beta<=alpha:
                    break
            return value

    # -------------------------------
    # HARD => Q-learning
    # -------------------------------
    def _init_learning_system(self):
        import pickle
        self.memory_file = "abluka_qtable.pkl"

        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'rb') as f:
                    self.q_table = pickle.load(f)
                print("[ML] Q tablosu yüklendi. Durum sayısı:", len(self.q_table))
            except:
                self.q_table = {}
                print("[ML] Q tablosu yüklenemedi, sıfırdan başlıyor.")
        else:
            self.q_table = {}

        # Parametreler
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.exploration_rate = 0.0  # İnsanla oynarken 0, self-play'de arttırılacak
        self.min_exploration_rate = 0.0
        self.exploration_decay = 0.99985

        # Hafıza
        self.current_game_states = []
        self.current_game_rewards = []
        self.current_game_moves = []
        self.learned_move_count = 0
        self.current_state = None

        print("[ML] Q-learning sistemi başlatıldı.")

    def save_model(self):
        if not self.learning_enabled:
            return
        import pickle
        try:
            with open(self.memory_file, 'wb') as f:
                pickle.dump(self.q_table, f)
            print(f"[ML] Q tablosu kaydedildi. Durum sayısı: {len(self.q_table)}")
        except Exception as e:
            print("[ML] Kayıt hatası:", e)

    def _choose_move_ultra_ml(self, board, player, time_limit, start_time):
        """
        ULTRA İYİLEŞTİRİLMİŞ Q-learning + Heuristic (HARD MOD)
        
        - GÜVENLİK + AGRESYON dengesi
        - Q-learning bilgisi
        - Gelişmiş heuristic
        - Rakibi ezmeye odaklı
        - Hiç rastgelelik yok (insanla oynarken)
        """
        if not self.learning_enabled:
            self.last_move_reasoning = "Hard disabled => fallback normal"
            return self._choose_move_old_hard(board, player, time_limit, start_time)

        # Durum
        st = self._state_to_features(board, player)
        self.current_state = st

        # 1. Hızlı abluka kontrolü (ama güvenli)
        immediate = self._check_immediate_win(board, player)
        if immediate:
            mv, obs = immediate
            is_safe, _ = self._is_safe_move(board, player, mv, obs)
            if is_safe:
                self.last_move_reasoning = "ML => Güvenli ani kazanma"
                return immediate
            else:
                print("[AI-ZOR] Kazanma hamlesi güvenli değil ama kontrol ediyorum...")
                # Bazen riskli de olsa kazanma hamlesi yapılmalı!
                test_b = self._clone_board(board)
                test_b.move_piece(player, mv)
                test_b.place_obstacle(obs)
                if not test_b.is_abluka(player):
                    # Kendim abluka olmazsam, yap!
                    self.last_move_reasoning = "ML => Riskli ama kazandıran hamle!"
                    return immediate

        val_moves = board.get_valid_moves(player)
        if not val_moves:
            return None, None
        
        opponent = 'W' if player == 'B' else 'B'

        # Self-play varsa explor, yoksa 0
        actual_expl = self.exploration_rate if hasattr(self,'_in_self_play') and self._in_self_play else 0.0
        is_explore = (random.random()<actual_expl)

        print(f"[AI-ZOR] {len(val_moves)} hamle değerlendiriliyor (exploration: {actual_expl:.3f})...")

        # 2. TÜM GÜVENLİ HAMLELERİ TOPLA VE DEĞERLENDİR
        safe_moves = []
        
        for mv in val_moves:
            if time.time() - start_time > time_limit * 0.85:
                break
            
            tmpb = self._clone_board(board)
            tmpb.move_piece(player, mv)
            empties = self._get_empty_positions(tmpb)
            
            # Engel sayısını optimize et (zor modda daha fazla kontrol)
            if len(empties) > 18:
                empties = self._prune_obstacles(tmpb, empties, player, 18)  # 12→18
            
            for obs in empties:
                if time.time() - start_time > time_limit * 0.92:
                    break
                
                # Güvenlik kontrolü
                is_safe, reason = self._is_safe_move(board, player, mv, obs)
                if not is_safe:
                    continue
                
                tb2 = self._clone_board(tmpb)
                tb2.place_obstacle(obs)
                
                # Rakibi ablukaya aldık mı?
                if tb2.is_abluka(opponent):
                    self.last_move_reasoning = "ML => Güvenli direkt abluka"
                    return mv, obs
                
                # Q-value
                nxt = self._state_to_features(tb2, player)
                qv = self.q_table.get(nxt, 0)
                
                # Heuristic - çok detaylı
                heur = self._evaluate_board(tb2, player) / 1500.0  # 2000→1500 daha etkili
                
                # Kaçış yolları bonusu
                escape = self._get_escape_routes(tb2, player)
                escape_bonus = escape / 80.0  # 100→80 daha etkili
                
                # RAKİBE ZARAR - ULTRA ÖNEMLİ
                opp_moves_before = len(board.get_valid_moves(opponent))
                opp_moves_after = len(tb2.get_valid_moves(opponent))
                damage = opp_moves_before - opp_moves_after
                damage_bonus = damage * 0.15  # Her azalan hamle için bonus
                
                # Rakip çok sıkışıyorsa ekstra
                if opp_moves_after <= 3:
                    damage_bonus += 0.5  # Dev bonus
                elif opp_moves_after <= 5:
                    damage_bonus += 0.3  # İyi bonus
                
                # TOPLAM DEĞER - Dengeli ağırlıklar
                val = (qv * 1.8 +           # Q-learning (1.5→1.8)
                       heur +                # Heuristic
                       escape_bonus +        # Kaçış yolları
                       damage_bonus)         # Rakibe zarar
                
                safe_moves.append((mv, obs, val, nxt, qv, heur, damage))
        
        print(f"[AI-ZOR] {len(safe_moves)} güvenli hamle bulundu")
        
        if not safe_moves:
            print("[AI-ZOR] UYARI: Güvenli hamle yok! Esnek modda deniyorum")
            # Esnek güvenlik - zor modda biraz risk alınabilir
            for mv in val_moves[:10]:
                tmpb = self._clone_board(board)
                tmpb.move_piece(player, mv)
                empties = self._get_empty_positions(tmpb)
                
                if len(empties) > 18:
                    empties = self._prune_obstacles(tmpb, empties, player, 18)
                
                for obs in empties[:18]:
                    tb2 = self._clone_board(tmpb)
                    tb2.place_obstacle(obs)
                    
                    # Esnek: En azından abluka olmamalı ve 2+ hamle kalmalı
                    if not tb2.is_abluka(player) and len(tb2.get_valid_moves(player)) >= 2:
                        nxt = self._state_to_features(tb2, player)
                        qv = self.q_table.get(nxt, 0)
                        heur = self._evaluate_board(tb2, player) / 1500.0
                        val = qv + heur
                        safe_moves.append((mv, obs, val, nxt, qv, heur, 0))
            
            if not safe_moves:
                # Hala yok, normal moda düş
                print("[AI-ZOR] Son çare: Normal mod stratejisi")
                return self._choose_move_old_hard(board, player, time_limit, start_time)
        
        # Sıralama - en iyi hamle en üstte
        safe_moves.sort(key=lambda x: x[2], reverse=True)
        
        # Exploration (sadece self-play'de)
        if is_explore and len(safe_moves) > 5:
            # En iyi %40'lık dilimden seç
            self.last_move_reasoning = "ML => Epsilon-greedy güvenli exploration"
            top_portion = max(3, int(len(safe_moves) * 0.4))  # 0.5→0.4 daha dar
            best_move, best_obs, best_value, best_state, q_val, h_val, dmg = random.choice(safe_moves[:top_portion])
        else:
            # En iyi hamle - kesinkes!
            best_move, best_obs, best_value, best_state, q_val, h_val, dmg = safe_moves[0]
            self.last_move_reasoning = "ML => Optimal Q + heuristic"
        
        # Öğrenme (sadece self-play'de)
        if self.current_state and best_state:
            rew = self._get_reward(board, player, best_move, best_obs, self.current_state, best_state)
            self.current_game_states.append(self.current_state)
            self.current_game_rewards.append(rew)
            if hasattr(self,'_in_self_play') and self._in_self_play:
                self._update_q_value(self.current_state, best_state, rew)
                self.learned_move_count += 1
                if self.learned_move_count % 5 == 0:
                    self.save_model()
        
        # Debug bilgisi
        val_s = f"{best_value:.3f} (Q:{q_val:.2f}, H:{h_val:.2f}, Dmg:{dmg})"
        self.last_move_reasoning += f" => {val_s}, Qsize={len(self.q_table)}"
        
        # En iyi 3 hamleyi logla
        if len(safe_moves) >= 3:
            print(f"[AI-ZOR] En iyi 3 skor: {safe_moves[0][2]:.3f}, {safe_moves[1][2]:.3f}, {safe_moves[2][2]:.3f}")
        
        return best_move, best_obs

    def _update_q_value(self, s0, s1, reward):
        oldq = self.q_table.get(s0,0)
        nextq = self.q_table.get(s1,0)
        newq = oldq + self.learning_rate*(reward + self.discount_factor*nextq - oldq)
        newq = max(-2000, min(2000, newq))
        self.q_table[s0] = newq

    def game_over_update(self, winner, player):
        """Oyun bitince geriye dönük update."""
        if not self.learning_enabled or not self.current_game_states:
            return
        print("[ML] Oyun sonu öğrenimi başlıyor...")
        print(f"[ML] Bu oyunda durum sayısı: {len(self.current_game_states)}. Kazanan: {winner} / Biz: {player}")

        old_count = len(self.q_table)
        if winner=='B':
            win_reward=150
            lose_penalty=-50
        else:
            win_reward=300
            lose_penalty=-100

        final_r = win_reward if winner==player else lose_penalty
        self.current_game_rewards[-1] = final_r
        cum = final_r
        random_factor = 0.05 if winner==player else 0.0

        for i in range(len(self.current_game_states)-1, -1, -1):
            st = self.current_game_states[i]
            nxt_st = (st if i==len(self.current_game_states)-1 else self.current_game_states[i+1])
            oldq = self.q_table.get(st,0)
            nxtq = self.q_table.get(nxt_st,0)
            import random
            if winner==player and random.random()<random_factor:
                noise = (random.random()-0.5)*5
                cum += noise
            new_q = oldq + self.learning_rate*(cum + self.discount_factor*nxtq - oldq)
            new_q = max(-2000, min(2000, new_q))
            self.q_table[st] = new_q
            if i%5==0:
                print(f"[ML] Durum {i}: Q {oldq:.2f}->{new_q:.2f}")

            cum*=self.discount_factor

        new_states = len(self.q_table)-old_count
        print(f"[ML] Oyun sonu öğrenme tamam. Q tablo size={len(self.q_table)}, bu oyunda +{new_states}")
        self.save_model()

        self.current_game_states=[]
        self.current_game_rewards=[]
        self.current_game_moves=[]

        # exploration azalt
        self.exploration_rate = max(self.min_exploration_rate,self.exploration_rate*self.exploration_decay)
        print(f"[ML] exploration => {self.exploration_rate:.4f}")

    # -------------------------------------
    # Yardımcı Metotlar
    # -------------------------------------
    def _check_immediate_win(self, board, player):
        opp = ('W' if player=='B' else 'B')
        moves = board.get_valid_moves(player)
        for mv in moves:
            tmp = self._clone_board(board)
            tmp.move_piece(player, mv)
            empties = self._get_empty_positions(tmp)
            for obs in empties:
                tb2 = self._clone_board(tmp)
                tb2.place_obstacle(obs)
                if not tb2.is_abluka(player) and tb2.is_abluka(opp):
                    return (mv,obs)
        return None

    def _evaluate_board(self, board, main_player):
        """
        ULTRA İYİLEŞTİRİLMİŞ tahta değerlendirme fonksiyonu
        Agresif ve dengeli strateji - rakibi ezmeye odaklı
        """
        my_moves = board.get_valid_moves(main_player)
        if not my_moves:
            return -999999
        opp = ('W' if main_player=='B' else 'B')
        op_moves = board.get_valid_moves(opp)
        if not op_moves:
            return 999999

        # 1. MOBİLİTE (Hareket özgürlüğü) - REBALANCED
        # RAKİBİ SINIRLAMAK daha önemli, kendini korumak da önemli ama daha az
        mobility_score = (len(my_moves) * 30) - (len(op_moves) * 45)  # Rakip daha ağır!
        
        # Kritik durum: Rakibi çok sınırlandır - DEV BONUS
        if len(op_moves) <= 2:
            mobility_score += 400  # Rakip neredeyse ablukada (200→400)
        elif len(op_moves) <= 3:
            mobility_score += 250  # Rakip çok zorlanıyor (yeni)
        elif len(op_moves) <= 5:
            mobility_score += 120   # Rakip zorlanıyor (80→120)
        
        # Kendi durumum kritik mi? - DAHA TOLERANSlı
        if len(my_moves) <= 2:
            mobility_score -= 100  # Tehlike ama daha az ceza (150→100)
        elif len(my_moves) <= 3:
            mobility_score -= 30   # Hafif dikkat (50→30)

        # 2. ALAN KONTROLÜ - BFS ile erişilebilir alan - DAHA ÖNEMLİ
        my_area = self._flood_fill_area(board, main_player)
        op_area = self._flood_fill_area(board, opp)
        area_score = (my_area - op_area) * 12  # 8→12
        
        # Alan avantajı büyükse bonus
        if my_area > op_area * 1.5:
            area_score += 80  # 50→80
        
        # Rakibi çok sınırladıysak DEV BONUS
        if op_area < 8:
            area_score += 150  # Rakibin alanı küçük!

        # 3. ÇEVRELEME (Rakibi sınırlama) - ULTRA BONUS
        encirclement = self._calculate_encirclement(board, opp) * 18  # 12→18
        
        # Rakip iyice çevriliyorsa büyük bonus
        if encirclement > 60:
            encirclement += 200  # 100→200
        elif encirclement > 40:
            encirclement += 100  # Yeni ara kademe

        # 4. MERKEZ KONTROLÜ - Stratejik pozisyon (dinamik)
        mp = board.black_pos if main_player=='B' else board.white_pos
        op = board.black_pos if opp=='B' else board.white_pos
        c = board.size // 2
        
        # Merkeze olan uzaklık (Manhattan distance)
        my_center_dist = abs(mp[0] - c) + abs(mp[1] - c)
        op_center_dist = abs(op[0] - c) + abs(op[1] - c)
        
        # Oyun başında merkez önemli, sonda daha az
        game_progress = len(board.obstacles) / 50.0  # 0 ile 1 arası
        center_weight = 20 * (1 - game_progress * 0.6)  # 15→20, Oyun ilerledikçe azal
        center_score = (op_center_dist - my_center_dist) * center_weight

        # 5. ENGEL STRATEJİSİ - REBALANCED
        my_obstacles = self._count_surrounding_obstacles(board, mp)
        op_obstacles = self._count_surrounding_obstacles(board, op)
        
        # Rakibin etrafında engel iyi, kendi etrafımda kötü
        obstacle_score = (op_obstacles - my_obstacles) * 25  # 18→25
        
        # Çok fazla engel kendimi köşeye sıkıştırabilir - AMA DAHA TOLERANSlı
        if my_obstacles >= 6:
            obstacle_score -= 120  # 100→120 ama 5'ten 6'ya çıktı
        elif my_obstacles >= 5:
            obstacle_score -= 40  # Yeni - hafif ceza
        
        # Rakip köşede ve etrafı engellerle doluysa çok iyi - ULTRA BONUS
        if op_obstacles >= 5 and len(op_moves) <= 4:
            obstacle_score += 180  # 120→180
        elif op_obstacles >= 4 and len(op_moves) <= 5:
            obstacle_score += 90  # Yeni ara kademe

        # 6. KÖŞE VE KENAR CEZASI - REBALANCED
        # Köşelerde sıkışmak kötü ama mutlak değil
        corner_penalty = 0
        edges = [0, board.size - 1]
        if mp[0] in edges and mp[1] in edges:
            # Köşedeyim - hamle sayısına göre ceza
            if len(my_moves) <= 3:
                corner_penalty -= 100  # Köşede VE az hamle = kötü
            else:
                corner_penalty -= 40   # Köşede ama hamle var = idare eder
        elif mp[0] in edges or mp[1] in edges:
            corner_penalty -= 15  # Kenarda olmak biraz kötü (25→15)
        
        # Rakip köşedeyse ULTRA İYİ
        if op[0] in edges and op[1] in edges:
            if len(op_moves) <= 3:
                corner_penalty += 100  # Rakip köşede ve sıkışık!
            else:
                corner_penalty += 50   # Rakip köşede
        elif op[0] in edges or op[1] in edges:
            corner_penalty += 25  # Rakip kenarda (20→25)

        # 7. TAKTİKSEL MESAFE - AGRESYONA GÖRE
        # Oyun sonuna doğru rakibe yakın olmak agresif oyunda iyi!
        distance = abs(mp[0] - op[0]) + abs(mp[1] - op[1])
        distance_score = 0
        
        # Aggression faktörü kullan
        aggression = getattr(self, 'aggression', 0.5)
        
        if aggression > 0.6:  # Agresif mod
            if distance <= 3 and len(my_moves) >= len(op_moves):
                distance_score += 40  # Yakınım ve avantajlıyım - iyi!
            elif distance >= 6:
                distance_score -= 20  # Çok uzak - rakibe yetişemem
        else:  # Savunmacı mod
            if distance <= 2 and len(my_moves) < len(op_moves):
                distance_score -= 30  # Yakınım ama dezavantajlıyım
            elif distance >= 5 and len(op_moves) <= 3:
                distance_score += 40  # Uzaktayım ve rakip sıkışık

        # 8. YENİ - KAZANMA POTANSYEL: Sonuca ne kadar yakınım?
        win_potential = 0
        
        # Rakibin durumu kötüyse bonus
        if len(op_moves) <= 3:
            win_potential += 150
        elif len(op_moves) <= 5:
            win_potential += 70
        
        # Benim durumum iyiyse bonus
        if len(my_moves) >= 8:
            win_potential += 50
        
        # Hamle farkı büyükse bonus
        move_diff = len(my_moves) - len(op_moves)
        if move_diff >= 4:
            win_potential += 100
        elif move_diff >= 2:
            win_potential += 40

        # TOPLAM SKOR - YENİ AĞIRLIKLAR
        total = (
            mobility_score * 1.2 +    # En önemli (1.0→1.2)
            area_score * 1.1 +        # Çok önemli (1.0→1.1)
            encirclement * 1.15 +     # Çok önemli (1.0→1.15)
            center_score * 0.8 +      # Orta önemli (1.0→0.8)
            obstacle_score * 1.0 +    # Önemli
            corner_penalty * 0.9 +    # Orta önemli (1.0→0.9)
            distance_score * 0.7 +    # Az önemli (1.0→0.7)
            win_potential * 1.3       # ÇOK ÖNEMLİ - yeni!
        )
        
        return total

    def _calculate_win_probability(self, board, player):
        opp = 'W' if player=='B' else 'B'
        mym = len(board.get_valid_moves(player))
        opm = len(board.get_valid_moves(opp))
        if mym==0: return 5.0
        if opm==0: return 95.0
        ratio = mym/max(1,opm)
        ratio = min(ratio,3.0)
        prob = 50+(ratio-1)*20
        return max(5,min(95,prob))

    def _state_to_features(self, board, player):
        opp = ('W' if player=='B' else 'B')
        my_pos = board.black_pos if player=='B' else board.white_pos
        op_pos = board.black_pos if opp=='B' else board.white_pos

        my_moves = len(board.get_valid_moves(player))
        op_moves = len(board.get_valid_moves(opp))
        dist = abs(my_pos[0]-op_pos[0]) + abs(my_pos[1]-op_pos[1])
        obstacle_ratio = min(9, len(board.obstacles)//(board.size*board.size//10))

        my_obs = self._count_surrounding_obstacles(board,my_pos)
        op_obs = self._count_surrounding_obstacles(board,op_pos)

        c = board.size//2
        my_c = abs(my_pos[0]-c)+abs(my_pos[1]-c)
        op_c = abs(op_pos[0]-c)+abs(op_pos[1]-c)
        center_diff = min(3,max(-3,op_c-my_c))
        enc = min(9,int(self._calculate_encirclement(board,opp)/10))

        edge_dist = min(my_pos[0],my_pos[1],board.size-1-my_pos[0],board.size-1-my_pos[1])
        edge_dist = min(3,edge_dist)

        nr_my_r = min(4,my_pos[0]*5//board.size)
        nr_my_c = min(4,my_pos[1]*5//board.size)
        nr_op_r = min(4,op_pos[0]*5//board.size)
        nr_op_c = min(4,op_pos[1]*5//board.size)

        # self-play esnasında ufak random (opsiyonel)
        if hasattr(self,'_in_self_play') and random.random()<0.03:
            if random.random()<0.5 and nr_my_r>0:
                nr_my_r-=1

        # Oyuncu kim => 0/1
        player_id = 0 if player=='B' else 1

        return (
            player_id,
            nr_my_r,nr_my_c,
            nr_op_r,nr_op_c,
            min(8,my_moves), min(8,op_moves),
            min(4,dist//2),
            min(7,my_obs),min(7,op_obs),
            center_diff+3,
            enc,
            edge_dist,
            obstacle_ratio
        )

    def _get_reward(self, board, player, move, obs, s0, s1):
        # Basit reward
        opp = ('W' if player=='B' else 'B')
        if board.is_abluka(opp):
            return 100
        if board.is_abluka(player):
            return -80
        return 0  # Ara ödüller opsiyonel

    def do_self_play(self, game_count=10):
        """Kendi kendine oyun oynayıp Q tablosu eğitimi."""
        if not self.learning_enabled:
            print("[ML] Self play sadece hard modda.")
            return
        from abluka.game_logic import Game

        print("[ML] Self-play başlıyor... Oyun sayısı:", game_count)
        start_time = time.time()
        self._in_self_play = True

        # Self-play modunda exploration açalım (ör: 0.3)
        old_exp = self.exploration_rate
        self.exploration_rate = 0.5

        old_size = len(self.q_table)

        black_wins=0
        white_wins=0

        for i in range(game_count):
            game = Game()
            # Rastgele açılış
            if random.random()<0.5:
                # 1-3 rastgele hamle
                pre = random.randint(1,3)
                for _ in range(pre):
                    if game.game_over: break
                    cp = game.current_player
                    mv_list = game.board.get_valid_moves(cp)
                    if not mv_list: break
                    mv = random.choice(mv_list)
                    tmpb = self._clone_board(game.board)
                    tmpb.move_piece(cp, mv)
                    empties = self._get_empty_positions(tmpb)
                    if empties:
                        ob = random.choice(empties)
                        game.make_move(mv, ob)

            mv_count=0
            while not game.game_over and mv_count<50:
                mv_count+=1
                cp = game.current_player
                # normalde siyah/beyaz exploration'ı ayarlayabilirsiniz
                move, obstacle = self._choose_move_ultra_ml(game.board, cp, 1.0, time.time())
                if not move or not obstacle:
                    game.game_over=True
                    game.winner=('W' if cp=='B' else 'B')
                else:
                    game.make_move(move, obstacle)

            if game.winner=='B':
                black_wins+=1
            elif game.winner=='W':
                white_wins+=1

            final_w = game.winner if game.winner else random.choice(['B','W'])
            self.game_over_update(final_w,'B')
            self.current_game_states=[]
            self.current_game_rewards=[]
            self.current_game_moves=[]
            self.game_over_update(final_w,'W')

        self._in_self_play=False
        self.exploration_rate = old_exp

        new_size = len(self.q_table)-old_size
        print(f"[ML] Self-play bitti. Eklenen durum: {new_size}, Siyah={black_wins}, Beyaz={white_wins}")
        self.save_model()

        return new_size

    # ----------------------------------------------------
    # Yardımcı
    # ----------------------------------------------------
    def _flood_fill_area(self, board, player):
        start = board.black_pos if player=='B' else board.white_pos
        visited=set()
        stack=[start]
        cnt=0
        while stack:
            r,c = stack.pop()
            if (r,c) in visited:
                continue
            visited.add((r,c))
            cell = board.grid[r][c]
            if cell is None or cell==player:
                cnt+=1
                for dr,dc in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)]:
                    rr=r+dr
                    cc=c+dc
                    if 0<=rr<board.size and 0<=cc<board.size:
                        if (rr,cc) not in visited:
                            c2 = board.grid[rr][cc]
                            if c2 is None or c2==player:
                                stack.append((rr,cc))
        return cnt

    def _calculate_encirclement(self, board, opponent):
        opp_pos = board.black_pos if opponent=='B' else board.white_pos
        reach = self._flood_fill_area(board, opponent)
        total_free = board.size*board.size - len(board.obstacles)
        enc = 1.0 - (reach/max(1,total_free))
        return enc*100

    def _count_surrounding_obstacles(self, board, pos):
        r,c = pos
        cnt=0
        for dr,dc in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)]:
            rr=r+dr
            cc=c+dc
            if 0<=rr<board.size and 0<=cc<board.size:
                cell = board.grid[rr][cc]
                if cell=='X' or cell=='R':
                    cnt+=1
        return cnt

    def _get_empty_positions(self, board):
        em=[]
        for r in range(board.size):
            for c in range(board.size):
                if board.grid[r][c] is None:
                    em.append((r,c))
        return em

    def _prune_moves(self, board, player, moves, limit):
        scored=[]
        for mv in moves:
            tb = self._clone_board(board)
            tb.move_piece(player,mv)
            sc = self._evaluate_board(tb,player)
            scored.append((mv,sc))
        scored.sort(key=lambda x:x[1], reverse=True)
        return [x[0] for x in scored[:limit]]

    def _prune_obstacles(self, board, empties, player, top_k=6):
        """
        ULTRA İYİLEŞTİRİLMİŞ STRATEJİK engel seçimi
        RAKİBİ EZMEye odaklı - çok agresif ve akıllı
        """
        scored = []
        opp = ('W' if player == 'B' else 'B')
        base_opm = len(board.get_valid_moves(opp))
        opp_pos = board.black_pos if opp == 'B' else board.white_pos
        my_pos = board.black_pos if player == 'B' else board.white_pos
        
        # Maksimum stratejik mesafe - zorluk seviyesine göre
        if self.difficulty == 'hard':
            MAX_STRATEGIC_DISTANCE = 5  # Zor mod: 5 kare (daha geniş)
        elif self.difficulty == 'normal':
            MAX_STRATEGIC_DISTANCE = 4  # Normal: 4 kare
        else:
            MAX_STRATEGIC_DISTANCE = 3  # Kolay: 3 kare (daha dar)
        
        for e in empties:
            # Rakibe olan mesafe
            dist_to_opp = abs(e[0] - opp_pos[0]) + abs(e[1] - opp_pos[1])
            
            # ÇOK UZAKSA REDDET
            if dist_to_opp > MAX_STRATEGIC_DISTANCE:
                continue
            
            tb = self._clone_board(board)
            tb.place_obstacle(e)
            
            # Kendimi ablukaya sokuyorum mu?
            if tb.is_abluka(player):
                continue
            
            score = 0
            
            # 1. RAKİBİN HAMLE SAYISINI AZALT - ULTRA ÖNEMLİ
            after_op = len(tb.get_valid_moves(opp))
            mobility_reduction = base_opm - after_op
            score += mobility_reduction * 200  # 150→200 DAHA YÜKSEK!
            
            # Rakibi çok sınırladıysak MEGA BONUS
            if after_op == 0:
                score += 10000  # Ablukaya aldık!
            elif after_op == 1:
                score += 800  # 1 hamle kaldı
            elif after_op == 2:
                score += 500  # 2 hamle kaldı (300→500)
            elif after_op <= 4 and mobility_reduction > 0:
                score += 250  # İyi sınırlama (150→250)
            elif after_op <= 6 and mobility_reduction > 0:
                score += 120  # Orta sınırlama (yeni)
            
            # 2. RAKİBE YAKINLIK - ULTRA BONUS
            if dist_to_opp == 1:
                score += 250  # Hemen yanı (200→250)
            elif dist_to_opp == 2:
                score += 150  # Çok yakın (120→150)
            elif dist_to_opp == 3:
                score += 80   # Yakın (60→80)
            elif dist_to_opp == 4:
                score += 35   # Orta mesafe (20→35)
            elif dist_to_opp == 5:
                score += 10   # Uzak ama kabul edilebilir (yeni)
            
            # 3. BENDEN UZAK engeller tercih et - REBALANCED
            dist_to_me = abs(e[0] - my_pos[0]) + abs(e[1] - my_pos[1])
            if dist_to_me >= 4:
                score += 60  # Benden çok uzak (40→60)
            elif dist_to_me >= 3:
                score += 40  # Benden uzak (eskiden yoktu)
            elif dist_to_me == 2:
                score += 10  # İdare eder (yeni)
            elif dist_to_me <= 1:
                # Kendime çok yakın - ama stratejik olabilir!
                if mobility_reduction >= 2:
                    score -= 30  # Rakibe çok zarar veriyorsam az ceza (-80→-30)
                else:
                    score -= 60  # Pek fayda yoksa orta ceza
            
            # 4. RAKİBİN KAÇIŞ YOLLARINI KES - ULTRA ÖNEMLİ
            blocking_value = 0
            
            # Rakibin olası hamle pozisyonlarını kontrol et
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    
                    target_r = opp_pos[0] + dr
                    target_c = opp_pos[1] + dc
                    
                    if (0 <= target_r < board.size and 
                        0 <= target_c < board.size):
                        dist_to_target = abs(e[0] - target_r) + abs(e[1] - target_c)
                        if dist_to_target == 0:
                            blocking_value += 100  # Direkt hamle pozisyonunu tıkıyoruz!
                        elif dist_to_target <= 1:
                            blocking_value += 60  # Bu hamle yolunu tıkıyor (50→60)
            
            score += blocking_value
            
            # 5. KÖŞEYE İTMEK - AGRESYF
            corners = [(0, 0), (0, board.size-1), (board.size-1, 0), (board.size-1, board.size-1)]
            best_corner_push = 0
            
            for corner in corners:
                corner_dist_opp = abs(opp_pos[0] - corner[0]) + abs(opp_pos[1] - corner[1])
                
                # Rakip köşeye yakınsa
                if corner_dist_opp <= 5:  # 4→5 daha geniş
                    corner_dist_obs = abs(e[0] - corner[0]) + abs(e[1] - corner[1])
                    
                    # Engel, rakiple köşe arasındaysa
                    if corner_dist_obs < corner_dist_opp:
                        push_value = 120 - (corner_dist_opp * 12)  # 80→120, daha değerli
                        best_corner_push = max(best_corner_push, push_value)
            
            score += best_corner_push
            
            # 6. GEÇİT KAPATMA - ULTRA BONUS
            if dist_to_opp <= 4:  # 3→4 daha geniş
                neighbors_with_obstacles = 0
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = e[0] + dr, e[1] + dc
                    if 0 <= nr < board.size and 0 <= nc < board.size:
                        if board.grid[nr][nc] in ('X', 'R'):
                            neighbors_with_obstacles += 1
                
                if neighbors_with_obstacles >= 3:
                    score += 180  # Çok dar geçit! (yeni)
                elif neighbors_with_obstacles >= 2:
                    score += 120  # Dar geçit kapatma (100→120)
                elif neighbors_with_obstacles == 1:
                    score += 50   # Duvar oluşturma (40→50)
            
            # 7. MERKEZ KONTROLÜ - Dinamik
            total_obstacles = len(board.obstacles)
            if total_obstacles < 20:  # Oyun başı/ortası (15→20)
                center = board.size // 2
                opp_to_center = abs(opp_pos[0] - center) + abs(opp_pos[1] - center)
                
                if opp_to_center > 3:
                    # Rakip merkeze uzak, merkezi kontrol et
                    obs_to_center = abs(e[0] - center) + abs(e[1] - center)
                    if obs_to_center <= 2:
                        score += 40  # Merkezi kontrol et (30→40)
                    elif obs_to_center <= 3:
                        score += 20  # Merkeze yakın (yeni)
                else:
                    # Rakip merkezdeyse, onu sıkıştır (merkeze engel koyma)
                    obs_to_center = abs(e[0] - center) + abs(e[1] - center)
                    if obs_to_center >= 3:
                        score += 30  # Merkezden uzak engel, rakibi daralt
            
            # 8. YENİ - ALAN BÖLME STRATEJİSİ
            # Tahtayı bölerek rakibi küçük alana hapsedebilir miyiz?
            if total_obstacles >= 10:  # Oyun ilerlediyse
                # Engel tahtayı kritik noktada mı böler?
                # Basit heuristik: Merkeze yakın ve rakibe yakın
                center = board.size // 2
                obs_to_center = abs(e[0] - center) + abs(e[1] - center)
                
                if obs_to_center <= 2 and dist_to_opp <= 3:
                    # Bu engel tahtayı bölme potansiyeli var
                    score += 100  # Alan bölme bonusu
            
            # 9. YENİ - RAKİBİN ALAN ERİŞİMİNİ AZALT
            # Bu engelden sonra rakibin erişebileceği alan ne kadar azalıyor?
            opp_area_before = self._flood_fill_area(board, opp)
            opp_area_after = self._flood_fill_area(tb, opp)
            area_reduction = opp_area_before - opp_area_after
            
            if area_reduction > 0:
                score += area_reduction * 15  # Her kare için bonus (yeni!)
            
            # 10. GENEL POZİSYON DEĞERLENDİRMESİ - Az etki
            general_eval = self._evaluate_board(tb, player)
            score += general_eval / 40.0  # 30→40, daha az etki
            
            scored.append((e, score))
        
        if not scored:
            # Hiç stratejik engel yok
            print(f"[ENGEL] UYARI: Stratejik engel yok! En yakın {top_k} engel seçiliyor")
            close_empties = sorted(empties, 
                                  key=lambda pos: abs(pos[0] - opp_pos[0]) + abs(pos[1] - opp_pos[1]))
            return close_empties[:top_k]
        
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # Debug: En iyi 3 engelin skorunu göster
        if len(scored) >= 3:
            print(f"[ENGEL] En iyi 3: {scored[0][1]:.0f}, {scored[1][1]:.0f}, {scored[2][1]:.0f}")
        elif len(scored) >= 1:
            print(f"[ENGEL] En iyi: {scored[0][1]:.0f}")
        
        return [x[0] for x in scored[:top_k]]

    def _clone_board(self, board):
        from abluka.game_logic import Board
        clone = Board()
        clone.size = board.size
        clone.grid = [row[:] for row in board.grid]
        clone.black_pos = board.black_pos
        clone.white_pos = board.white_pos
        clone.obstacles = board.obstacles.copy()
        return clone
    
    def _is_corner_position(self, pos, board_size):
        """Köşe pozisyonu mu kontrol et"""
        row, col = pos
        return (row in [0, board_size - 1]) and (col in [0, board_size - 1])
    
    def _is_edge_position(self, pos, board_size):
        """Kenar pozisyonu mu kontrol et"""
        row, col = pos
        return row in [0, board_size - 1] or col in [0, board_size - 1]
    
    def _is_safe_move(self, board, player, move_pos, obstacle_pos):
        """
        ULTRA İYİLEŞTİRİLMİŞ güvenlik kontrolü
        
        Agresif ama akıllı:
        1. Direkt abluka kontrolü
        2. Minimum hamle kontrolü (zorluk seviyesine göre)
        3. Köşe/kenar risk analizi
        4. Gelecek turları simüle et (akıllıca)
        5. Risk-getiri dengesi
        """
        # Hamleyi simüle et
        test_board = self._clone_board(board)
        test_board.move_piece(player, move_pos)
        test_board.place_obstacle(obstacle_pos)
        
        opponent = 'W' if player == 'B' else 'B'
        
        # 1. Direkt abluka kontrolü - HER ZAMAN GEÇERLİ
        if test_board.is_abluka(player):
            return False, "Direkt abluka"
        
        # 2. Minimum hamle sayısı kontrolü - ZORLUK SEVİYESİNE GÖRE
        my_moves = test_board.get_valid_moves(player)
        
        # Çok kritik durum: 0 hamle = kesinlikle ret
        if len(my_moves) == 0:
            return False, "Hiç hamle kalmıyor"
        
        # Minimum hamle kontrolü (zorluk seviyesine göre)
        if len(my_moves) < self.min_safe_moves:
            # AMA: Eğer rakibi ablukaya alıyorsam, kabul et!
            opp_moves_after = test_board.get_valid_moves(opponent)
            if len(opp_moves_after) <= 2:
                # Rakip çok sıkışık, riski göze al
                pass  # Kabul et
            else:
                return False, f"Çok az hamle ({len(my_moves)} < {self.min_safe_moves})"
        
        # 3. AKILLI köşe/kenar risk analizi
        # Köşe tehlikesi - ama hamle sayısına bağlı
        if self._is_corner_position(move_pos, board.size):
            corner_moves = len(my_moves)
            
            # Zor modda daha agresif, kolay modda daha temkinli
            if self.difficulty == 'hard':
                threshold = 2  # Zor mod: 2+ hamle yeterli
            elif self.difficulty == 'normal':
                threshold = 3  # Normal mod: 3+ hamle
            else:
                threshold = 4  # Kolay mod: 4+ hamle
            
            if corner_moves < threshold:
                # AMA: Eğer rakibi de köşeye sıkıştırıyorsam...
                opp_pos = test_board.black_pos if opponent == 'B' else test_board.white_pos
                if self._is_corner_position(opp_pos, board.size):
                    opp_moves_after = len(test_board.get_valid_moves(opponent))
                    if opp_moves_after < corner_moves:
                        pass  # Rakip daha kötü durumda, kabul et
                    else:
                        return False, f"Köşe tehlikesi (sadece {corner_moves} hamle)"
                else:
                    return False, f"Köşe tehlikesi (sadece {corner_moves} hamle)"
        
        # 4. Kenar risk analizi - DAHA ESNEK
        if self._is_edge_position(move_pos, board.size):
            edge_threshold = 3 if self.difficulty == 'hard' else 4
            
            if len(my_moves) < edge_threshold:
                # Rakibin durumunu kontrol et
                opp_moves_after = len(test_board.get_valid_moves(opponent))
                if opp_moves_after <= 4:
                    pass  # Rakip de zorlanıyor, kabul et
                else:
                    return False, f"Kenar tehlikesi (sadece {len(my_moves)} hamle)"
        
        # 5. Kendime çok yakın engel kontrolü - DAHA TOLERANSlı
        my_pos = move_pos
        dist_to_obstacle = abs(my_pos[0] - obstacle_pos[0]) + abs(my_pos[1] - obstacle_pos[1])
        
        if dist_to_obstacle <= 1:
            # Hemen yanıma engel koyuyorum
            surrounding_obstacles = self._count_surrounding_obstacles(test_board, my_pos)
            
            # Zorluk seviyesine göre tolerans
            if self.difficulty == 'hard':
                max_surrounding = 7  # Zor mod: 7'ye kadar kabul (çok agresif!)
            elif self.difficulty == 'normal':
                max_surrounding = 6  # Normal mod: 6'ya kadar
            else:
                max_surrounding = 5  # Kolay mod: 5'e kadar
            
            if surrounding_obstacles >= max_surrounding:
                return False, f"Etrafım çok engelli ({surrounding_obstacles}/8)"
        
        # 6. Gelecek turları simüle et - AKILLICA
        # Zorluk seviyesine göre kontrol sayısı
        check_turns = self.future_turns_check
        
        for future_turn in range(check_turns):
            # Rakibin en kötü hamlesini simüle et
            opp_moves = test_board.get_valid_moves(opponent)
            if not opp_moves:
                break  # Rakip ablukada, harika!
            
            # Rakibin beni en çok sıkıştıran hamlesini bul
            worst_case_my_moves = len(my_moves)
            worst_scenario_board = None
            
            # İlk N hamleyi kontrol et (zorluk seviyesine göre)
            check_count = min(len(opp_moves), 3 if self.difficulty == 'easy' else 5)
            
            for opp_move in opp_moves[:check_count]:
                temp_b = self._clone_board(test_board)
                temp_b.move_piece(opponent, opp_move)
                empties = self._get_empty_positions(temp_b)
                
                # İlk 8 engeli kontrol et
                for obs in empties[:8]:
                    temp_b2 = self._clone_board(temp_b)
                    temp_b2.place_obstacle(obs)
                    
                    future_my_moves = len(temp_b2.get_valid_moves(player))
                    
                    if future_my_moves < worst_case_my_moves:
                        worst_case_my_moves = future_my_moves
                        worst_scenario_board = temp_b2
                        
                        # Eğer ablukaya giriyorsam direkt ret
                        if worst_case_my_moves == 0:
                            # AMA: Rakip de ablukaya giriyorsa?
                            if temp_b2.is_abluka(opponent):
                                continue  # Berabere, devam et
                            return False, f"Gelecek tur {future_turn + 1}'de abluka riski"
            
            # Gelecek turda çok az hamlem kalıyor mu?
            # Zorluk seviyesine göre minimum
            future_min = max(1, self.min_safe_moves - 1)
            
            if worst_case_my_moves < future_min:
                # Rakibin durumunu da kontrol et
                if worst_scenario_board:
                    opp_future_moves = len(worst_scenario_board.get_valid_moves(opponent))
                    
                    # Eğer rakip de sıkışıyorsa kabul et
                    if opp_future_moves <= worst_case_my_moves + 1:
                        pass  # Rakip benimle aynı durumda veya daha kötü
                    else:
                        return False, f"Gelecek tur {future_turn + 1}'de risk ({worst_case_my_moves} hamle)"
            
            # Bir sonraki tur için tahtayı güncelle
            if worst_scenario_board:
                test_board = worst_scenario_board
                my_moves = test_board.get_valid_moves(player)
                if not my_moves:
                    return False, f"Gelecek tur {future_turn + 1}'de abluka"
        
        # 7. YENİ - RİSK-GETİRİ ANALİZİ
        # Bu hamle riskli ama rakibe çok zarar veriyorsa kabul et
        opp_moves_before = len(board.get_valid_moves(opponent))
        opp_moves_after = len(test_board.get_valid_moves(opponent))
        damage_to_opponent = opp_moves_before - opp_moves_after
        
        # Eğer rakibe 3+ hamle kaybettiriyorsam ve benim 2+ hamlem varsa
        # Risk kabul edilebilir
        if damage_to_opponent >= 3 and len(my_moves) >= 2:
            return True, f"Agresif hamle (Rakip: -{damage_to_opponent}, Ben: {len(my_moves)})"
        
        # Tüm kontroller geçildi
        return True, "Güvenli"
    
    def _get_escape_routes(self, board, player):
        """
        Kaçış yollarını değerlendir - açık alanlara giden yollar
        """
        my_pos = board.black_pos if player == 'B' else board.white_pos
        center = board.size // 2
        
        escape_value = 0
        
        # Merkeze açık yol var mı?
        if abs(my_pos[0] - center) <= 2 and abs(my_pos[1] - center) <= 2:
            escape_value += 50  # Merkezdeyiz, iyi
        
        # Her yöne kaç adım gidebilirim?
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]
        
        for dr, dc in directions:
            steps = 0
            r, c = my_pos
            
            for _ in range(3):  # 3 adım ileriye bak
                r += dr
                c += dc
                
                if 0 <= r < board.size and 0 <= c < board.size:
                    if board.grid[r][c] is None:
                        steps += 1
                    else:
                        break
                else:
                    break
            
            escape_value += steps * 10
        
        return escape_value

    def _evaluate_move(self, board, player, move):
        tb = self._clone_board(board)
        tb.move_piece(player, move)
        return self._evaluate_board(tb,player)

    def _random_reaction(self, emo_list, msg_list):
        return f"{random.choice(emo_list)} {random.choice(msg_list)}"

    def _assess_emotion(self, board, player):
        opp = ('W' if player=='B' else 'B')
        my_m = len(board.get_valid_moves(player))
        op_m = len(board.get_valid_moves(opp))
        if self.last_mobility is not None and my_m<self.last_mobility:
            self.current_message = self._random_reaction(self.emojis['worried'], self.messages['worried'])
        elif op_m==0:
            self.current_message = self._random_reaction(self.emojis['smug'], self.messages['confident'])
        elif my_m==1:
            self.current_message = self._random_reaction(self.emojis['worried'], self.messages['trapped'])
        else:
            if random.random()<0.2:
                self.current_message = self._random_reaction(self.emojis['thinking'], self.messages['thinking'])
            else:
                self.current_message = None
        self.last_mobility = my_m

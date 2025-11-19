class Board:
    """
    Abluka oyununda 7x7 tahtayı yöneten sınıf.
    - 'B' = Siyah taş
    - 'W' = Beyaz taş
    - 'R' = Engel taşı
    - None = Boş kare
    """

    def __init__(self):
        self.size = 7
        self.grid = [[None for _ in range(self.size)] for _ in range(self.size)]
        
        # Başlangıçta siyah en üst ortada, beyaz en alt ortada
        self.black_pos = (0, self.size // 2)  
        self.white_pos = (self.size - 1, self.size // 2)
        
        # Tahtada bu konumları işaretle
        self.grid[self.black_pos[0]][self.black_pos[1]] = 'B'
        self.grid[self.white_pos[0]][self.white_pos[1]] = 'W'
        
        # Engel taşlarının konumlarını da saklayan liste
        self.obstacles = []

    def is_valid_move(self, piece, start_pos, end_pos):
        """
        Taşın start_pos'tan end_pos'a geçişi kurallara uygun mu?
          1) end_pos tahtada olmalı,
          2) end_pos boş (None) olmalı,
          3) hareket en fazla 1 adım (yatay/dikey/çapraz) olmalı
        """
        if not (0 <= end_pos[0] < self.size and 0 <= end_pos[1] < self.size):
            return False
        
        if self.grid[end_pos[0]][end_pos[1]] is not None:
            return False
        
        dx = abs(end_pos[0] - start_pos[0])
        dy = abs(end_pos[1] - start_pos[1])
        if dx > 1 or dy > 1:
            return False
        
        return True

    def get_valid_moves(self, piece):
        """
        Bir taşın (Siyah/Beyaz) mevcut konumundan yapabileceği tüm geçerli hamleleri döndürür.
        """
        if piece == 'B':
            start_pos = self.black_pos
        else:
            start_pos = self.white_pos
        
        valid_moves = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                end_pos = (start_pos[0] + dx, start_pos[1] + dy)
                if self.is_valid_move(piece, start_pos, end_pos):
                    valid_moves.append(end_pos)
        return valid_moves

    def move_piece(self, piece, end_pos):
        """
        Taşı (piece) end_pos konumuna götürür.
        Geriye True/False döndürür.
        """
        if piece == 'B':
            start_pos = self.black_pos
        else:
            start_pos = self.white_pos

        # Geçerli mi diye tekrar kontrol (istenirse devre dışı bırakılabilir)
        if not self.is_valid_move(piece, start_pos, end_pos):
            return False
        
        # Tahtadan eski konumu temizle
        self.grid[start_pos[0]][start_pos[1]] = None
        
        # Yeni konuma taşı yerleştir
        self.grid[end_pos[0]][end_pos[1]] = piece
        
        # Parça konumunu güncelle
        if piece == 'B':
            self.black_pos = end_pos
        else:
            self.white_pos = end_pos
        
        return True

    def place_obstacle(self, pos):
        """
        pos konumuna 'R' (engel) bırakır.
        Başarılıysa True, aksi halde False.
        """
        # Tahta sınırı
        if not (0 <= pos[0] < self.size and 0 <= pos[1] < self.size):
            return False
        
        # orada zaten taş veya engel var mı?
        if self.grid[pos[0]][pos[1]] is not None:
            return False
        
        self.grid[pos[0]][pos[1]] = 'R'
        self.obstacles.append(pos)
        return True

    def is_abluka(self, piece):
        """
        İlgili taşın hiç hamlesi yoksa abluka (kilitlenme) var demektir.
        True/False döndürür.
        """
        return (len(self.get_valid_moves(piece)) == 0)

    def __str__(self):
        """
        Tahtanın metinsel gösterimi.
        Örn:
          0 1 2 3 4 5 6
        0 B . . . . . .
        1 . . . . . . .
        ...
        """
        result = "   " + " ".join(str(i) for i in range(self.size)) + "\n"
        for i, row in enumerate(self.grid):
            result += f"{i}  "
            for cell in row:
                if cell is None:
                    result += ". "
                else:
                    result += f"{cell} "
            result += "\n"
        return result


class Game:
    """
    Tek bir Abluka oyunu yönetir:
      - Board nesnesi
      - current_player
      - game_over / winner
      - turn_count
      - make_move vb.
    """
    def __init__(self):
        self.board = Board()
        self.current_player = 'B'  # varsayılan: Siyah başlasın
        self.game_over = False
        self.winner = None
        self.turn_count = 0

    def switch_player(self):
        """Sıradaki oyuncuyu değiştir."""
        self.current_player = 'W' if self.current_player == 'B' else 'B'

    def make_move(self, move_pos, obstacle_pos):
        """
        Tek hamle:
          1) current_player'ın taşını move_pos'a taşı
          2) obstacle_pos'a engel koy
        Başarılı ise True, hata varsa False.
        
        Eğer hamle rakibi ablukada bırakırsa game_over ve winner güncellenir.
        Eğer hamleden sonra (player switch) yeni oyuncu ablukadaysa, yine game_over.
        """
        # 1) Taşı ilerlet
        if not self.board.move_piece(self.current_player, move_pos):
            return False
        
        # 2) Engel koy
        if not self.board.place_obstacle(obstacle_pos):
            # Engel koyma başarısızsa => rollback
            # Basit rollback: taşı geri al
            if self.current_player == 'B':
                self.board.grid[move_pos[0]][move_pos[1]] = None
                self.board.grid[self.board.black_pos[0]][self.board.black_pos[1]] = 'B'
            else:
                self.board.grid[move_pos[0]][move_pos[1]] = None
                self.board.grid[self.board.white_pos[0]][self.board.white_pos[1]] = 'W'
            return False
        
        self.turn_count += 1
        
        # Rakip abluka mı?
        opponent = 'W' if self.current_player == 'B' else 'B'
        if self.board.is_abluka(opponent):
            self.game_over = True
            self.winner = self.current_player
            return True
        
        # Sıra değiş
        self.switch_player()
        
        # Yeni oyuncu ablukadaysa
        if self.board.is_abluka(self.current_player):
            self.game_over = True
            self.winner = opponent
            return True
        
        return True

    def get_game_state(self):
        """Oyun durumunu döndürür (AI ya da GUI kullanabilir)."""
        return {
            'board': self.board,
            'current_player': self.current_player,
            'game_over': self.game_over,
            'winner': self.winner,
            'turn_count': self.turn_count,
            'valid_moves': self.board.get_valid_moves(self.current_player)
        }

# Abluka - Türkiye Akıl ve Zeka Oyunları

Abluka, Türkiye Akıl ve Zeka Oyunları Turnuvası'nda oynanan stratejik bir masa oyununun Python ile gerçekleştirilmiş versiyonudur.

## Oyun Kuralları

1. Abluka oyunu 7x7 tahta üzerinde 49 kareden oluşan bir oyun alanında oynanır.
2. Oyunda biri siyah biri beyaz olmak üzere iki ana taş ve oyun akışında kullanılacak olan kırmızı renkte engel taşları bulunmaktadır.
3. İki ana taş, başlangıç sıralarının tam ortasına gelecek şekilde tahtaya yerleştirilir. Oyuna siyah taşa sahip oyuncu başlar.
4. Her oyuncu kendi sırası geldiğinde birbirini izleyen iki hamle yapar:
   - Önce taşını, taşına komşu boş bir kareye yerleştirir.
   - Ardından tahtadaki boş karelerden birini, engel taşlarından biri ile kapatır.
5. Oyuncu taşını ileri, geri, sağa, sola ya da çapraz bir kare hareket ettirebilir.
6. Taşlar birbirinin ve engel taşlarının üzerinden atlayamaz.
7. Engel taşları konulduğu yerden hiçbir şekilde kaldırılamaz.
8. Sırası geldiğinde taşını hareket ettiremeyen oyuncu oyunu kaybeder.
9. Yapılan son hamle ile her iki taraf da ablukaya alınıyorsa, son hamleyi yapan oyuncu o seti kazanmış sayılır.

## Gereksinimler

- Python 3.6 veya üzeri
- Pygame kütüphanesi

## Kurulum

1. Gerekli Python kütüphanelerini yükleyin:
```
pip install pygame
```

2. Oyunu klonlayın veya indirin:
```
git clone <repo_url>
cd abluka-online
```

## Oyun Özellikleri

- **Menü Sistemi**: Oyun başlangıcında insan vs. bilgisayar veya insan vs. insan oyun modu seçilebilir
- **Zorluk Seviyeleri**: Bilgisayara karşı oynamak için kolay, normal ve zor seviyeleri mevcuttur
- **Rastgele Taraf Seçimi**: İnsan vs. bilgisayar modunda oyuncu rastgele olarak siyah veya beyaz taş ile oynar
- **Animasyonlar**: Taş hareketleri ve hamle geçişleri için akıcı animasyonlar
- **Görsel Geri Bildirimler**: Geçerli hamleler yeşil, seçilen taş sarı olarak vurgulanır
- **Engel Önizleme**: Engel taşı yerleştirirken, fare ile işaretlenen kare yarı saydam kırmızı renkte gösterilir
- **Engel Taşı Gösterimi**: Tahta kenarlarında kalan engel taşları görsel olarak gösterilir

## Oyunu Çalıştırma

Ana dizindeyken aşağıdaki komutu kullanarak oyunu başlatabilirsiniz:

```
python -m abluka.main
```

Veya Windows'ta:

```
run_abluka.bat
```

### Komut Satırı Parametreleri

- `--width`: Pencere genişliği. Varsayılan: 800
- `--height`: Pencere yüksekliği. Varsayılan: 800

Örnek:
```
python -m abluka.main --width=900 --height=900
```

## Oyun Kontrolleri

- **Fare Sol Tık**: 
  - Menüde oyun modu ve zorluk seviyesi seçmek için
  - Taşınızı seçmek ve hareket ettirmek için
  - Engel taşı yerleştirmek için
- **Fare Hareketi**: Engel yerleştirme aşamasında, fareyi boş kareler üzerinde gezdirerek engelin nereye yerleşeceğini önizleyebilirsiniz

## Bilgisayar Zorluk Seviyeleri

- **Kolay**: Basit strateji, güvenlik odaklı, %40 rastgelelik
- **Normal**: Gelişmiş strateji, 2 tur ilerisi simülasyon, %15 rastgelelik  
- **Zor**: Q-learning AI, maksimum strateji, %5 rastgelelik

### AI Özellikleri

✅ **Kendini Koruma**
- Asla kendini ablukaya sokmaz
- Köşe/kenar tehlikelerinden kaçınır
- Gelecek turları simüle eder
- Minimum hamle garantisi

✅ **Stratejik Engel Yerleştirme**
- Sadece 4 kare mesafede engel koyar
- Rakibi sınırlamaya odaklanır
- Kaçış yollarını keser
- Koridorları tıkar

✅ **Gerçekçi Oyun**
- İnsan benzeri hatalar (zorluk seviyesine göre)
- Dinamik düşünme süresi
- Duygusal tepkiler

## EXE Build (Standalone Uygulaması)

### Windows
```bash
build_exe.bat
```

### Linux/Mac
```bash
chmod +x build_exe.sh
./build_exe.sh
```

Build sonrası: `dist/Abluka.exe` veya `dist/Abluka`

### GitHub Actions ile Otomatik Build

Repository'ye tag push ederseniz otomatik olarak Windows ve Linux için executable'lar oluşturulur:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Release'ler GitHub Releases sayfasında görünecektir.

## Dosya Yapısı

```
abluka-online/
├── abluka/
│   ├── assets/
│   │   └── sounds/       # Oyun sesleri
│   ├── main.py           # Ana giriş noktası
│   ├── gui.py            # Grafik arayüz
│   ├── game_logic.py     # Oyun mantığı
│   ├── ai_player.py      # AI sistemi
│   └── sound_manager.py  # Ses yönetimi
├── logs/                 # Oyun logları (git'de değil)
├── .github/
│   └── workflows/
│       └── build.yml     # Otomatik build
├── build_exe.bat         # Windows build
├── build_exe.sh          # Linux/Mac build
├── requirements.txt      # Gerekli paketler
└── README.md

İgnore edilen:
- logs/                   # Oyun logları
- __pycache__/           # Python cache
- *.pkl                  # AI öğrenme dosyaları
- build/, dist/          # Build çıktıları
```

## Geliştirme

### Yeni Özellikler

**v2.0 (Mevcut)**
- ✅ Modern UI tasarımı
- ✅ Gelişmiş AI sistemi
- ✅ Güvenlik odaklı hamle seçimi
- ✅ Stratejik engel yerleştirme
- ✅ Otomatik build sistemi

Detaylı değişiklikler için:
- `DEGISIKLIKLER.md` - Tasarım ve AI genel iyileştirmeleri
- `AI_GUVENLIK_IYILESTIRMELERI.md` - AI güvenlik sistemi
- `ENGEL_YERLESTIRME_IYILESTIRMELERI.md` - Engel stratejisi

### Test

```bash
python -m abluka.main
```

Konsolu izleyerek AI kararlarını görebilirsiniz:
```
[AI-ZOR] 15 hamle değerlendiriliyor...
[ENGEL] En iyi 3: 520, 470, 380
[AI-ZOR] 11 güvenli hamle bulundu
```

## Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing`)
3. Commit edin (`git commit -m 'feat: amazing özellik'`)
4. Push edin (`git push origin feature/amazing`)
5. Pull Request açın

## Lisans

Bu proje eğitim amaçlı geliştirilmiştir.

## Geliştirici

**Ubden® Akademi**

---

⭐ Beğendiyseniz yıldız vermeyi unutmayın!
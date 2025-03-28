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

- **Easy (Kolay)**: Bilgisayar rastgele hamleler yapar.
- **Normal**: Bilgisayar temel bir strateji kullanır, açık alanlara doğru hareket etmeye çalışır.
- **Hard (Zor)**: Bilgisayar daha gelişmiş stratejiler kullanır, merkezi kontrol etmeye çalışır ve rakibin hareket kabiliyetini kısıtlamaya odaklanır. 
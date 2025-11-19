# Engel Yerleştirme İyileştirmeleri

## 🎯 Sorun
AI (özellikle zor modda) stratejik olmayan, alakasız yerlere engel koyuyordu:
- Rakipten çok uzak yerlere engel
- Hiç etkisi olmayan pozisyonlar
- Kendi alanını gereksiz daraltma

## ✅ Çözüm

### 1. Maksimum Stratejik Mesafe Limiti

```python
MAX_STRATEGIC_DISTANCE = 4  # Manhattan distance
```

**Artık AI:**
- Rakipten 4'ten uzak yerlere engel koymaz
- Sadece stratejik değeri olan pozisyonları değerlendirir
- Alakasız engelleri direkt reddeder

### 2. Yeniden Tasarlanmış Skor Sistemi

#### Öncelik Sırası (Ağırlıklarla):

| Kriter | Ağırlık | Açıklama |
|--------|---------|----------|
| **Mobilite Azaltma** | ×150 | Rakibin hamle sayısını azalt (EN ÖNEMLİ) |
| **Rakibe Yakınlık (1 kare)** | +200 | Hemen yanında |
| **Rakibe Yakınlık (2 kare)** | +120 | Çok yakın |
| **Rakibe Yakınlık (3 kare)** | +60 | Yakın |
| **Rakibe Yakınlık (4 kare)** | +20 | Orta mesafe |
| **Hamle Yolu Kesme** | +50 | Her kesilen yol için |
| **Geçit Kapatma** | +100 | Dar geçitleri kapat |
| **Köşeye İtme** | +80 | Rakibi köşeye sıkıştır |

#### Özel Bonuslar:

```python
# Rakibi çok sınırladıysak
if rakip_hamle <= 3 and azalma > 0:
    bonus += 300  # Dev bonus!
elif rakip_hamle <= 5 and azalma > 0:
    bonus += 150  # İyi sınırlama
```

### 3. Strateji Odaklı Değerlendirme

#### A) Hamle Yolu Kesme
```python
# Rakibin gidebileceği 8 yönü kontrol et
for her_yon in 8_yon:
    hedef = rakip_pos + yon
    if engel.yakınında(hedef):
        bonus += 50  # Bu yolu tıkıyoruz!
```

#### B) Köşeye İtme
```python
# Rakip köşeye yakınsa (<= 4 kare)
if rakip_köşeye_yakın:
    if engel_arada:
        bonus = 80 - (mesafe * 10)
        # Daha yakınsa daha değerli
```

#### C) Geçit Kapatma
```python
# Engelin etrafında 2+ engel varsa
if komşu_engeller >= 2:
    bonus += 100  # Dar geçit kapatıyoruz!
```

### 4. Esnek Güvenlik Parametreleri

#### Minimum Hamle Sayısı (Daha Esnek):
- **Kolay**: 2 hamle (eskiden 3)
- **Normal**: 3 hamle (eskiden 4)  
- **Zor**: 3 hamle (eskiden 4)

#### Yakın Engel Toleransı:
```python
# Eski: 4+ komşu engel = reddet
# Yeni: 6+ komşu engel = reddet

if etraf_engel >= 6:  # Çok daha esnek!
    return False
# 5 komşu engel bile olsa 3 yön açık demektir
```

#### Gelecek Tur Kontrolü:
- **Kolay**: 1 tur
- **Normal**: 2 tur
- **Zor**: 2 tur (eskiden 3 - daha hızlı karar)

### 5. Debug Loglama

```python
# Hiç stratejik engel yoksa uyarı
if not scored:
    print("[ENGEL] UYARI: Stratejik engel yok!")
    return en_yakınları()

# En iyi 3 engelin skorunu göster
print(f"[ENGEL] En iyi 3: {skor1}, {skor2}, {skor3}")
```

## 📊 Karşılaştırma

### Eski Sistem:
```
Engel mesafesi: 7 kare
Skor: 180
Neden: "Genel pozisyon iyi görünüyor"
Sonuç: ❌ Rakipten çok uzak, etkisiz
```

### Yeni Sistem:
```
Engel mesafesi: 2 kare
Skor: 520
Neden: "Rakip hamle: 8→5 (-3×150=450), 
        Yakınlık: +120, Yol kesme: +50"
Sonuç: ✅ Çok etkili, rakibi sınırlıyor
```

## 🎮 Davranış Değişiklikleri

### Artık AI:

1. ✅ **Sadece stratejik yerlere engel koyar**
   - Maksimum 4 kare mesafe
   - Rakibe yakın pozisyonlar öncelikli

2. ✅ **Rakibi agresif sınırlar**
   - Hamle sayısını azaltmaya odaklanır
   - Kaçış yollarını keser
   - Köşelere iter

3. ✅ **Dar geçitleri kapatır**
   - Koridorları tıkar
   - Duvarlar oluşturur
   - Alanı böler

4. ✅ **Daha esnek güvenlik**
   - Az hamle bile kabul edilebilir
   - Yakın engel koyabilir
   - Agresif oynayabilir

5. ✅ **Anlık geri bildirim**
   - Engel skorları loglanır
   - Stratejik kararlar görünür
   - Debug kolaylaşır

## 🧪 Test Senaryoları

### Senaryo 1: Rakip Merkezdeyken
**Öncesi**: AI kenarlara engel koyuyor ❌
**Sonrası**: AI rakibin etrafına engel koyuyor ✅

### Senaryo 2: Rakip Köşede
**Öncesi**: AI rastgele yerlere engel koyuyor ❌
**Sonrası**: AI çıkış yollarını kapatıyor ✅

### Senaryo 3: Açık Koridor
**Öncesi**: AI koridoru görmüyor ❌
**Sonrası**: AI koridoru kapatıyor ✅

### Senaryo 4: Oyun Sonu
**Öncesi**: AI hala uzak yerlere engel koyuyor ❌
**Sonrası**: AI rakibi ablukaya alıyor ✅

## 📈 Performans İyileştirmeleri

- **Daha Az Değerlendirme**: Uzak engeller reddediliyor
- **Daha Hızlı Karar**: 2 tur yerine 3 tur kontrolü
- **Daha Akıllı Seçim**: Ağırlıklı skor sistemi
- **Daha İyi Oyun**: Stratejik ve etkili hamleler

## 🎯 Sonuç

Artık AI engel yerleştirirken:
- ✅ **Hiç alakasız yere engel koymaz**
- ✅ **Rakibi sınırlamaya odaklanır**  
- ✅ **Stratejik pozisyonları hedefler**
- ✅ **Agresif ve etkili oynar**
- ✅ **Güvenlik-strateji dengesi kurar**

## 🚀 Kullanım

```bash
python -m abluka.main
```

Zor modda şimdi çok daha stratejik engel yerleştirme göreceksiniz!

### Konsol Çıktısı Örneği:
```
[ENGEL] En iyi 3: 520, 470, 380
[AI-ZOR] 11 güvenli hamle bulundu
[AI-ZOR] ML => Q + heuristic + safety => 1.45
```

Her engelin neden seçildiğini görebilirsiniz! 🎮


# Deployment ve Build Sistemi Kurulumu

## ✅ Tamamlanan İşler

### 1. 🔇 Sesler
**Durum:** ✅ Sesler zaten mevcut!

Konum: `abluka/assets/sounds/`
- ✅ `click.wav` - Tıklama sesi
- ✅ `error.wav` - Hata sesi
- ✅ `game_lose.wav` - Kaybetme sesi
- ✅ `game_start.wav` - Oyun başlangıcı
- ✅ `game_win.wav` - Kazanma sesi
- ✅ `menu_hover.wav` - Menü hover
- ✅ `menu_select.wav` - Menü seçim
- ✅ `move.wav` - Taş hareketi
- ✅ `place_obstacle.wav` - Engel yerleştirme

**Not:** Sesler `sound_manager.py` tarafından yönetiliyor.

### 2. 📦 Otomatik Build Sistemi

#### GitHub Actions Workflow
✅ **Dosya:** `.github/workflows/build.yml`

**Özellikler:**
- Windows ve Linux için otomatik build
- Tag push'ta otomatik release
- Manuel tetikleme desteği
- Artifact yükleme

**Kullanım:**
```bash
# Release oluştur
git tag v1.0.0
git push origin v1.0.0

# Otomatik olarak:
# 1. Windows EXE oluşturulur
# 2. Linux binary oluşturulur
# 3. GitHub Releases'e yüklenir
```

#### Yerel Build Scriptleri

✅ **Windows:** `build_exe.bat`
```bash
build_exe.bat
# Çıktı: dist/Abluka.exe
```

✅ **Linux/Mac:** `build_exe.sh`
```bash
chmod +x build_exe.sh
./build_exe.sh
# Çıktı: dist/Abluka
```

✅ **PyInstaller Spec:** `abluka.spec`
- Manuel build için
- Özelleştirilebilir konfigürasyon

### 3. 🚫 .gitignore

✅ **Dosya:** `.gitignore`

**İgnore Edilen:**

**Build çıktıları:**
- `build/`
- `dist/`
- `*.exe`
- `*.spec`

**Oyun verileri:**
- `logs/` - Tüm log dosyaları
- `*.log` - Tek log dosyaları
- `*.pkl` - AI öğrenme dosyaları
- `abluka_qtable.pkl`

**Geliştirme:**
- `__pycache__/`
- `*.pyc`, `*.pyo`
- `.vscode/`, `.idea/`
- `venv/`, `env/`

**Temporary:**
- `*.tmp`, `*.temp`
- `*.bak`, `*.cache`
- `*.orig`

**OS:**
- `.DS_Store` (Mac)
- `Thumbs.db`, `Desktop.ini` (Windows)

### 4. 📚 Dokümantasyon

✅ **README.md** - Güncellenmiş
- Build talimatları
- GitHub Actions açıklaması
- Dosya yapısı
- Yeni özellikler

✅ **BUILD_DEPLOYMENT.md** - Yeni
- Detaylı build rehberi
- CI/CD workflow açıklaması
- Troubleshooting
- Best practices

## 🚀 Hızlı Başlangıç

### Development
```bash
# Klonla
git clone <repo>
cd abluka-online

# Gerekli paketleri yükle
pip install -r requirements.txt

# Çalıştır
python -m abluka.main
```

### Yerel Build
```bash
# Windows
build_exe.bat

# Linux/Mac
./build_exe.sh
```

### Release Oluştur
```bash
# Değişiklikleri commit et
git add .
git commit -m "feat: yeni özellik"
git push

# Tag oluştur ve push et
git tag v1.0.0
git push origin v1.0.0

# GitHub Actions otomatik olarak:
# - Build yapar
# - Release oluşturur
# - EXE'leri yükler
```

## 📋 Workflow Özeti

### Geliştirme Döngüsü
```
1. Kod yaz
2. Test et (python -m abluka.main)
3. Commit & Push
4. Tag oluştur (isteğe bağlı)
5. GitHub Actions build yapar
6. Release yayınlanır
```

### Build Pipeline
```
GitHub Push
    ↓
Actions Trigger
    ↓
┌─────────────┬─────────────┐
│   Windows   │    Linux    │
│   Build     │    Build    │
└─────────────┴─────────────┘
    ↓               ↓
Artifacts       Artifacts
    ↓               ↓
    └───────┬───────┘
            ↓
       Release
```

## 🎯 Sonraki Adımlar

### Kullanım
1. ✅ `.gitignore` ayarlandı → `git add .gitignore`
2. ✅ Build scriptleri hazır → Test edin
3. ✅ GitHub Actions hazır → Tag push'layın
4. ✅ Dokümantasyon hazır → README'yi okuyun

### İlk Release
```bash
# Her şey hazır!
git add .
git commit -m "chore: build ve deployment sistemi eklendi"
git push

# İlk release için
git tag v1.0.0
git push origin v1.0.0
```

## 📊 Dosya Değişiklikleri

### Yeni Dosyalar
- ✅ `.gitignore` - Git ignore kuralları
- ✅ `build_exe.bat` - Windows build script
- ✅ `build_exe.sh` - Linux/Mac build script
- ✅ `abluka.spec` - PyInstaller config
- ✅ `BUILD_DEPLOYMENT.md` - Build dokümantasyonu
- ✅ `DEPLOYMENT_KURULUM.md` - Bu dosya

### Güncellenen Dosyalar
- ✅ `.github/workflows/build.yml` - Actions workflow
- ✅ `README.md` - Build talimatları eklendi

### Mevcut Dosyalar (Değişmedi)
- ✅ `requirements.txt` - Bağımlılıklar
- ✅ `abluka/assets/sounds/` - Ses dosyaları

## 🎮 Test Senaryoları

### 1. Local Build Test
```bash
# Windows'ta
build_exe.bat
dist\Abluka.exe

# Linux'ta
./build_exe.sh
./dist/Abluka
```

### 2. GitHub Actions Test
```bash
# Test tag oluştur
git tag v0.0.1-test
git push origin v0.0.1-test

# Actions'ı izle
# GitHub → Actions sekmesi

# Test release'i sil (isteğe bağlı)
git tag -d v0.0.1-test
git push origin :refs/tags/v0.0.1-test
```

### 3. Full Release Test
```bash
# Production release
git tag v1.0.0
git push origin v1.0.0

# Release'i kontrol et
# GitHub → Releases

# EXE'leri indir ve test et
```

## 🔧 Sorun Giderme

### Build Hatası
```bash
# Temiz build
rm -rf build dist
python -m PyInstaller abluka.spec
```

### GitHub Actions Hatası
- Repository Settings → Actions → Read & Write
- Workflow logs'u incele
- Local'de build test et

### Ses Dosyaları
Sesler zaten mevcut! Eğer yeni ses eklemek isterseniz:
- `abluka/assets/sounds/` klasörüne ekleyin
- `sound_manager.py`'de tanımlayın

## ✨ Özet

Artık projenizde:
- ✅ Ses dosyaları hazır
- ✅ Otomatik build sistemi aktif
- ✅ .gitignore yapılandırılmış
- ✅ Yerel build scriptleri hazır
- ✅ Dokümantasyon tamamlandı

**Tek yapmanız gereken:**
```bash
git add .
git commit -m "chore: deployment sistemi"
git push
```

Ve ilk release için:
```bash
git tag v1.0.0
git push origin v1.0.0
```

🎉 **Hazırsınız!**


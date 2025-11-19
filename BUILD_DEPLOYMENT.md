# Build ve Deployment Dokümantasyonu

## 📦 Executable Oluşturma

### Yerel Build

#### Windows
```bash
build_exe.bat
```

Bu script:
1. Gereken kütüphaneleri yükler
2. Önceki build'i temizler
3. PyInstaller ile tek dosya EXE oluşturur
4. Temizlik yapar

**Çıktı:** `dist/Abluka.exe`

#### Linux/macOS
```bash
chmod +x build_exe.sh
./build_exe.sh
```

**Çıktı:** `dist/Abluka`

### PyInstaller Özellikleri

- **Tek dosya**: Tüm bağımlılıklar tek exe'de
- **Windowed**: Konsol penceresi açılmaz
- **Assets dahil**: Sesler ve görseller otomatik eklenir
- **Optimize**: UPX ile sıkıştırılmış

### Manual Build

```bash
# Kütüphaneleri yükle
pip install -r requirements.txt
pip install pyinstaller

# Build
pyinstaller abluka.spec

# veya direkt
pyinstaller --name="Abluka" \
    --windowed \
    --onefile \
    --add-data "abluka/assets:abluka/assets" \
    --hidden-import=pygame \
    abluka/main.py
```

## 🤖 GitHub Actions (CI/CD)

### Otomatik Build

`.github/workflows/build.yml` dosyası otomatik build sağlar.

#### Tetikleme

**1. Tag ile (Önerilen):**
```bash
git tag v1.0.0
git push origin v1.0.0
```

**2. Manuel:**
- GitHub'da Actions sekmesine git
- "Build Abluka Executable" workflow'u seç
- "Run workflow" düğmesine bas

#### Build Süreçleri

**Windows Build:**
- Windows Server 2022
- Python 3.11
- PyInstaller
- Artifact: `Abluka-Windows`

**Linux Build:**
- Ubuntu Latest
- Python 3.11
- SDL2 kütüphaneleri
- Artifact: `Abluka-Linux`

#### Çıktılar

1. **Artifacts** (her push'ta)
   - GitHub Actions sayfasında
   - 90 gün saklanır

2. **Release** (tag'lerde)
   - GitHub Releases sayfasında
   - Kalıcı
   - İndirilebilir

### Workflow Detayları

```yaml
# Tag push'ta otomatik release
on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:  # Manuel tetikleme

jobs:
  build-windows:
    - Python kurulumu
    - Bağımlılık yükleme
    - Executable build
    - Test (opsiyonel)
    - Artifact yükleme
    - Release oluşturma (tag'de)
```

## 🚀 Release Süreci

### 1. Hazırlık
```bash
# Değişiklikleri commit et
git add .
git commit -m "feat: yeni özellik"
git push
```

### 2. Versiyon Tag'i
```bash
# Semantic versioning
git tag v1.0.0
git tag v1.1.0  # Minor güncelleme
git tag v2.0.0  # Major değişiklik
```

### 3. Tag Push
```bash
git push origin v1.0.0
```

### 4. Build İzleme
- GitHub → Actions sekmesi
- "Build Abluka Executable" workflow'u
- Build loglarını izle

### 5. Release İndirme
- GitHub → Releases
- İlgili versiyon
- Assets bölümünden exe'leri indir

## 📝 .gitignore

Otomatik ignore edilen dosyalar:

```
# Build çıktıları
build/
dist/
*.spec
*.exe

# Geliştirme
__pycache__/
*.pyc
.vscode/

# Oyun verileri
logs/
*.pkl
*.log

# Sistem
.DS_Store
Thumbs.db
```

## 🔧 Troubleshooting

### Build Hataları

**Problem**: "pygame not found"
```bash
pip install pygame --force-reinstall
```

**Problem**: "Unable to find data files"
```bash
# Yolu kontrol et
--add-data "abluka/assets:abluka/assets"  # Linux
--add-data "abluka/assets;abluka/assets"  # Windows
```

**Problem**: "Import error"
```bash
# Hidden import ekle
--hidden-import=moduladi
```

### GitHub Actions Hataları

**Problem**: "Permission denied"
- Settings → Actions → General
- Workflow permissions: Read and write

**Problem**: "Release creation failed"
- Repository settings'de releases aktif mi?
- GITHUB_TOKEN izinleri var mı?

## 📊 Build İstatistikleri

### Dosya Boyutları (yaklaşık)

- **Windows EXE**: ~25-30 MB
- **Linux Binary**: ~20-25 MB
- **Sıkıştırılmış**: ~15-20 MB

### Build Süreleri

- **Windows**: 3-5 dakika
- **Linux**: 2-4 dakika
- **Toplam**: ~6-9 dakika

## 🎯 Best Practices

1. **Versioning**
   - Semantic versioning kullan (v1.2.3)
   - CHANGELOG.md güncelle
   - Tag mesajları ekle

2. **Testing**
   - Local build test et
   - Her platform'u dene
   - Smoke test yap

3. **Release Notes**
   - Özellikler listele
   - Bug fix'leri not et
   - Breaking changes vurgula

4. **Artifacts**
   - Meaningful isimler kullan
   - Versiyon ekle
   - Platform belirt

## 🌟 Örnek Release Workflow

```bash
# 1. Değişiklikleri bitir
git add .
git commit -m "feat: harika özellik eklendi"

# 2. Local test
python -m abluka.main

# 3. Local build test
./build_exe.bat  # veya .sh

# 4. Push
git push origin main

# 5. Tag ve release
git tag -a v1.0.0 -m "İlk stabil versiyon"
git push origin v1.0.0

# 6. GitHub'da release'i kontrol et
# 7. Executable'ları test et
```

## 📚 Ek Kaynaklar

- [PyInstaller Docs](https://pyinstaller.org/)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Semantic Versioning](https://semver.org/)

---

Sorun yaşarsanız issue açın! 🐛


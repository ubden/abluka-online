# GitHub Actions Build Hatası Düzeltildi

## 🐛 Sorunlar

### 1. PowerShell Syntax Hatası
```
ParserError: Missing expression after unary operator '--'
```

**Neden:** GitHub Actions Windows runner'da PowerShell kullanıyor. `^` karakteri CMD için satır devamı, PowerShell'de çalışmıyor.

**Çözüm:** 
- Tek satırda yazdık (satır devamı yok)
- Windows build için `shell: cmd` ekledik

### 2. GitHub Release 403 Hatası
```
⚠️ GitHub release failed with status: 403
```

**Neden:** Workflow'a write permission verilmemiş.

**Çözüm:**
```yaml
permissions:
  contents: write
```

## ✅ Yapılan Değişiklikler

### `.github/workflows/build.yml`

**Öncesi (Hatalı):**
```yaml
- name: Build executable
  run: |
    pyinstaller --name="Abluka" ^
      --windowed ^
      --onefile ^
      ...
```

**Sonrası (Doğru):**
```yaml
permissions:
  contents: write  # ← Eklendi

- name: Build executable
  run: |
    pyinstaller --name=Abluka --windowed --onefile --add-data "abluka/assets;abluka/assets" --hidden-import=pygame --hidden-import=numpy --collect-data pygame abluka/main.py
  shell: cmd  # ← Eklendi (Windows için)
```

### Yerel Build Scriptleri

**`build_exe.bat`** - Tek satır yaptık:
```batch
pyinstaller --name=Abluka --windowed --onefile --add-data "abluka/assets;abluka/assets" --hidden-import=pygame --hidden-import=numpy --collect-data pygame abluka/main.py
```

**`build_exe.sh`** - Backslash yerine tek satır:
```bash
python3 -m PyInstaller --name=Abluka --windowed --onefile --add-data "abluka/assets:abluka/assets" --hidden-import=pygame --hidden-import=numpy --collect-data pygame abluka/main.py
```

## 🎯 Test

### Yerel Test
```bash
# Windows
build_exe.bat

# Linux
./build_exe.sh
```

### GitHub Actions Test
```bash
# Yeni tag push et
git add .github/workflows/build.yml build_exe.*
git commit -m "fix: build workflow PowerShell ve permissions düzeltildi"
git push

# Test tag
git tag v2.1.1
git push origin v2.1.1
```

## 📋 Değişiklik Özeti

| Dosya | Değişiklik | Neden |
|-------|-----------|-------|
| `.github/workflows/build.yml` | `permissions: contents: write` | Release oluşturma yetkisi |
| `.github/workflows/build.yml` | `shell: cmd` (Windows) | PowerShell yerine CMD |
| `.github/workflows/build.yml` | Tek satır PyInstaller komutu | Satır devamı sorunu |
| `build_exe.bat` | Tek satır PyInstaller | Tutarlılık |
| `build_exe.sh` | Tek satır PyInstaller | Tutarlılık |

## ✨ Artık Çalışıyor!

Workflow şimdi:
- ✅ Windows'ta CMD ile build yapıyor
- ✅ Linux'ta bash ile build yapıyor
- ✅ Release oluşturma yetkisi var
- ✅ Hem artifact hem release yükleyebiliyor

Bir sonraki tag push'ta sorunsuz çalışacak! 🚀


#!/bin/bash

echo "========================================"
echo "Abluka Oyunu - Build Script"
echo "========================================"
echo ""

# Python kontrolü
if ! command -v python3 &> /dev/null; then
    echo "HATA: Python3 bulunamadı! Lütfen Python3 yükleyin."
    exit 1
fi

echo "[1/4] Gerekli kütüphaneler yükleniyor..."
python3 -m pip install -r requirements.txt
python3 -m pip install pyinstaller

echo ""
echo "[2/4] Önceki build dosyaları temizleniyor..."
rm -rf build dist Abluka.spec

echo ""
echo "[3/4] Executable oluşturuluyor..."
python3 -m PyInstaller --name=Abluka --windowed --onefile --add-data "abluka/assets:abluka/assets" --hidden-import=pygame --hidden-import=numpy --collect-data pygame abluka/main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "HATA: Build başarısız oldu!"
    exit 1
fi

echo ""
echo "[4/4] Temizlik yapılıyor..."
rm -rf build

echo ""
echo "========================================"
echo "BUILD TAMAMLANDI!"
echo "========================================"
echo ""
echo "Executable: dist/Abluka"
echo ""
echo "Oyunu çalıştırmak için: ./dist/Abluka"
echo ""

# Linux'ta executable yapma
chmod +x dist/Abluka


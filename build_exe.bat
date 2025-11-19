@echo off
echo ========================================
echo Abluka Oyunu - EXE Build Script
echo ========================================
echo.

REM Python ve pip kontrolü
python --version >nul 2>&1
if errorlevel 1 (
    echo HATA: Python bulunamadi! Lutfen Python yukleyin.
    pause
    exit /b 1
)

echo [1/4] Gerekli kutuphaneler yukleniyor...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo [2/4] Onceki build dosyalari temizleniyor...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist Abluka.spec del Abluka.spec

echo.
echo [3/4] EXE dosyasi olusturuluyor...
pyinstaller --name="Abluka" ^
    --windowed ^
    --onefile ^
    --add-data "abluka/assets;abluka/assets" ^
    --hidden-import=pygame ^
    --hidden-import=numpy ^
    --collect-data pygame ^
    abluka/main.py

if errorlevel 1 (
    echo.
    echo HATA: Build basarisiz oldu!
    pause
    exit /b 1
)

echo.
echo [4/4] Temizlik yapiliyor...
if exist build rmdir /s /q build

echo.
echo ========================================
echo BUILD TAMAMLANDI!
echo ========================================
echo.
echo EXE dosyasi: dist\Abluka.exe
echo.
echo Oyunu calistirmak icin: dist\Abluka.exe
echo.
pause


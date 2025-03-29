@echo off
echo Abluka Self-Play Eğitimi YENİDEN Başlatılıyor...
echo NOT: Bu işlem Q tablosunu sıfırlayacak ve sıfırdan eğitim yapacak!
echo Devam etmek için bir tuşa basın...
pause >nul

echo.
echo Eski model siliniyor...
if exist abluka_memory.pkl del abluka_memory.pkl

echo.
echo Self-play eğitimi başlatılıyor (1000 oyun)...
python -m abluka.self_play --games 1000 --width 1200 --height 800
echo Eğitim tamamlandı! 
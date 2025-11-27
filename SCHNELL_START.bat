@echo off
echo ===========================================
echo    RHINOPLASTIK-ANWENDUNG SCHNELL-START
echo ===========================================
echo.

echo 1. Python-Version prüfen...
python --version
if %errorlevel% neq 0 (
    echo FEHLER: Python nicht gefunden! Bitte Python 3.8+ installieren.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo 2. Abhängigkeiten installieren...
pip install PySide6 pandas matplotlib openpyxl
pip install PyYAML psutil fuzzywuzzy pyotp qrcode[pil] atomicwrites

echo.
echo 3. Anwendung kompilieren...
pyinstaller rhinoplastik_windows.spec

echo.
echo 4. Anwendung starten...
cd dist\Rhinoplastik_App
start "" Rhinoplastik_App.exe

echo.
echo ===========================================
echo    INSTALLATION ABGESCHLOSSEN!
echo    Rhinoplastik_App wurde gestartet
echo ===========================================
echo.
pause
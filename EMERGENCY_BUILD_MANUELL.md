# 🚨 NOTFALL: Manueller Build-Schritt-für-Schritt

## Schritt 1: Python 3.12 testen
```cmd
python --version
pip --version
```
✅ **Erwartet**: Python 3.12.x

## Schritt 2: Manueller PyInstaller Build
```cmd
cd rhinoplastik_app
pip install pyinstaller
pyinstaller rhinoplastik_app.spec
```

## Schritt 3: Prüfen ob es funktioniert hat
- Suche nach: `dist\Rhinoplastik_App\Rhinoplastik_App.exe`
- Wenn vorhanden: ✅ **ERFOLG!**

## Typische Fixes

### Problem: "pyinstaller: command not found"
**Lösung**:
```cmd
python -m pip install pyinstaller
python -m PyInstaller rhinoplastik_app.spec
```

### Problem: "Permission denied"
**Lösung**: Als Administrator ausführen

### Problem: "Could not find rhinoplastik_app.spec"
**Lösung**: Im `rhinoplastik_app` Ordner sein

### Problem: "PyInstaller" wird blockiert
**Lösung**: Antivirus temporär deaktivieren

### Problem: Internet-Probleme bei Paket-Download
**Lösung**:
```cmd
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org pyinstaller
```

## Ziel: `dist\Rhinoplastik_App\Rhinoplastik_App.exe`
- Dateigröße: ~150-200 MB
- Typ: PE32+ executable
- Startbar: Doppelklick!

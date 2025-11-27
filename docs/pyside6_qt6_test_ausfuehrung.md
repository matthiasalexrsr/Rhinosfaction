# PySide6/Qt6 Integration Tests - Ausführungsanleitung

## Schnellstart

### 1. Grundlegende Test-Ausführung
```bash
# Direkte Test-Ausführung
cd /workspace
python pyside6_qt6_integration_test.py
```

### 2. Mit pytest (erweitert)
```bash
# Installiere pytest-qt
pip install pytest pytest-qt

# Führe Tests mit pytest aus
pytest pyside6_qt6_integration_test.py -v

# Mit Coverage
pytest pyside6_qt6_integration_test.py --cov=ui --cov-report=html
```

## Test-Dateien

### Haupt-Test-Datei
- `pyside6_qt6_integration_test.py` - Praktische Test-Ausführung

### pytest-Konfiguration
- `conftest_pytest.py` - pytest-Fixtures und Konfiguration

### Dokumentation
- `docs/pyside6_qt6_integration_tests.md` - Umfassende Test-Spezifikation
- `docs/pyside6_qt6_integration_test_bericht.md` - Detaillierter Ergebnisbericht

## Test-Kategorien

### 1. Import- und Kompatibilitäts-Tests
```bash
# Teste nur Import-Kompatibilität
python -c "
import sys; sys.path.append('/workspace/rhinoplastik_app')
from ui.main_window import MainWindow
print('✅ Import-Test erfolgreich')
"
```

### 2. Widget-Erstellungs-Tests
```bash
# Führe nur Widget-Tests aus
python -c "
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
from PySide6.QtWidgets import QApplication
app = QApplication([])
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
w = QWidget(); l = QLabel('Test'); print('✅ Widget-Test erfolgreich')
"
```

### 3. Signal-Slot-Tests
```bash
# Teste Signal-Slot-Mechanismus
python -c "
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal
app = QApplication([])
class TestObj(QObject): sig = Signal(str)
t = TestObj(); t.sig.connect(lambda x: print('Signal OK'))
t.sig.emit('test'); print('✅ Signal-Slot-Test erfolgreich')
"
```

## Test-Optionen

### Headless-Modus (Standard)
```bash
# Tests laufen automatisch headless
QT_QPA_PLATFORM=offscreen python pyside6_qt6_integration_test.py
```

### Mit Display
```bash
# Für GUI-Tests mit echtem Display
python pyside6_qt6_integration_test.py
```

### Debug-Modus
```bash
# Mit erweiterten Debug-Informationen
python -u pyside6_qt6_integration_test.py
```

## Test-Anpassungen

### Performance-Schwellenwerte ändern
In `pyside6_qt6_integration_test.py` anpassen:
```python
# Zeile ~315: Widget-Performance
assert creation_time < 3.0, f"Widget-Erstellung zu langsam: {creation_time:.3f}s"

# Zeile ~325: Signal-Slot-Performance  
assert signal_time < 2.0, f"Signal-Slot-Verarbeitung zu langsam: {signal_time:.3f}s"
```

### Test-Daten anpassen
```python
# In test_performance_metrics(): Anzahl der Test-Widgets ändern
for i in range(50):  # Ändern zu gewünschter Anzahl
```

### Mock-Daten erweitern
```python
# In MockConfig, MockSession, MockPatient Klassen
# Zusätzliche Mock-Methoden hinzufügen
```

## CI/CD Integration

### GitHub Actions
```yaml
name: PySide6 Qt6 Integration Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        pip install PySide6 pytest pytest-qt
    - name: Run integration tests
      run: |
        python pyside6_qt6_integration_test.py
```

### Docker Integration
```dockerfile
FROM python:3.9-slim
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libegl1-mesa \
    libxcb-xinerama0 \
    libxcb-cursor0
COPY . /app
WORKDIR /app
RUN pip install PySide6 pytest
CMD ["python", "pyside6_qt6_integration_test.py"]
```

## Erweiterte Tests

### Langzeit-Stabilität
```python
def test_ui_stability_extended():
    """Erweiterter Stabilitäts-Test"""
    for round in range(100):  # 100 Runden
        # Intensive UI-Interaktionen
        pass
```

### Memory-Leak-Tests
```python
def test_memory_leaks():
    """Memory-Leak-Erkennung"""
    import gc
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # Erstelle viele Widgets
    for i in range(1000):
        widget = QWidget()
        # ... Widget-Konfiguration
    
    gc.collect()  # Garbage Collection
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # Prüfe Memory-Increase
    assert memory_increase < 50 * 1024 * 1024, "Memory-Leak erkannt"
```

## Troubleshooting

### Häufige Probleme

1. **"No Qt platform plugin could be initialized"**
   ```bash
   export QT_QPA_PLATFORM=offscreen
   ```

2. **"ImportError: No module named 'PySide6'"**
   ```bash
   pip install PySide6>=6.5.0
   ```

3. **Tests hängen bei GUI-Operationen**
   ```bash
   # Verwende immer Headless-Modus für Tests
   export QT_QPA_PLATFORM=offscreen
   ```

4. **Performance-Tests zu langsam**
   - Reduziere Test-Datenmenge
   - Prüfe System-Resources
   - Optimiere Test-Loop

### Debug-Modus
```python
# Am Anfang der Test-Datei hinzufügen
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Qualitäts-Metriken

### Erfolgs-Kriterien
- ✅ Alle 9 Tests bestanden
- ✅ Erfolgsrate: 100%
- ✅ Performance innerhalb Schwellenwerte
- ✅ Keine Memory-Leaks
- ✅ Cross-Platform kompatibel

### Performance-Ziele
- Widget-Erstellung: < 50ms pro Widget
- Tab-Navigation: < 100ms
- Signal-Slot: < 2ms pro Signal
- Dialog-Erstellung: < 10ms

---

**Letzte Aktualisierung**: 2025-11-06 20:28:53  
**Version**: 1.0  
**Kompatibilität**: PySide6 >= 6.5.0, Qt 6.x

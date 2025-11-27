#!/usr/bin/env python3
"""
GUI-Analyse Test
Einfacher Test zur Überprüfung der PySide6-Integration
"""

import sys
import os
import tempfile
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QTabWidget

# Set up paths
sys.path.insert(0, '/workspace/rhinoplastik_app')

def test_pyside6_basic():
    """Testet grundlegende PySide6-Funktionalität"""
    print("🧪 Teste PySide6-Integration...")
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Einfaches Test-Fenster
    window = QMainWindow()
    window.setWindowTitle("GUI-Analyse Test")
    window.setGeometry(100, 100, 800, 600)
    
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    layout = QVBoxLayout()
    central_widget.setLayout(layout)
    
    # Test 1: Label
    label = QLabel("PySide6 erfolgreich geladen")
    label.setStyleSheet("font-size: 16px; color: green;")
    layout.addWidget(label)
    
    # Test 2: Tab-Widget (wie in MainWindow)
    tab_widget = QTabWidget()
    tab_widget.addTab(QLabel("Tab 1 Inhalt"), "Tab 1")
    tab_widget.addTab(QLabel("Tab 2 Inhalt"), "Tab 2")
    layout.addWidget(tab_widget)
    
    # Test 3: Button
    button = QPushButton("Test Button")
    button.setStyleSheet("""
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
    """)
    layout.addWidget(button)
    
    # Fenster anzeigen
    window.show()
    
    print("✅ PySide6-Fenster erfolgreich erstellt")
    return window, app

def test_ui_module_imports():
    """Testet UI-Modul-Imports"""
    print("\n🧪 Teste UI-Modul-Imports...")
    
    try:
        from config.app_config import AppConfig
        print("✅ AppConfig Import erfolgreich")
    except Exception as e:
        print(f"❌ AppConfig Import fehlgeschlagen: {e}")
    
    try:
        from ui.login_dialog import LoginDialog
        print("✅ LoginDialog Import erfolgreich")
    except Exception as e:
        print(f"❌ LoginDialog Import fehlgeschlagen: {e}")
    
    try:
        from ui.dashboard_widget import DashboardWidget
        print("✅ DashboardWidget Import erfolgreich")
    except Exception as e:
        print(f"❌ DashboardWidget Import fehlgeschlagen: {e}")
    
    try:
        from ui.patients_list_widget import PatientsListWidget
        print("✅ PatientsListWidget Import erfolgreich")
    except Exception as e:
        print(f"❌ PatientsListWidget Import fehlgeschlagen: {e}")

def test_app_config():
    """Testet AppConfig für UI-Einstellungen"""
    print("\n🧪 Teste AppConfig für UI-Einstellungen...")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            config = AppConfig(Path(temp_dir))
            
            # UI-Konfiguration testen
            window_size = config.get('ui.window_size', (1200, 800))
            print(f"✅ Fenstergröße: {window_size}")
            
            min_size = config.get('ui.window_min_size', (1000, 600))
            print(f"✅ Mindestgröße: {min_size}")
            
            theme = config.get('ui.theme', 'default')
            print(f"✅ Theme: {theme}")
            
            return True
    except Exception as e:
        print(f"❌ AppConfig Test fehlgeschlagen: {e}")
        return False

if __name__ == "__main__":
    print("🔍 GUI-Komponenten-Analyse")
    print("=" * 50)
    
    # Imports testen
    test_ui_module_imports()
    
    # AppConfig testen
    test_app_config()
    
    # PySide6 testen
    window, app = test_pyside6_basic()
    
    print("\n" + "=" * 50)
    print("🎉 Grundlegende GUI-Tests abgeschlossen")
    print("Hinweis: In einer echten Analyse würde die Anwendung mit echten Daten gestartet")
    
    # App im Hintergrund laufen lassen
    sys.exit(app.exec())
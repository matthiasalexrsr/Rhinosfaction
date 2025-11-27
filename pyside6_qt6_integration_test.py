#!/usr/bin/env python3
"""
PySide6/Qt6 Integration Test - Praktische Ausführung
Führt umfassende Tests der Qt6-Integration durch
"""

import sys
import os
import time
import traceback
from pathlib import Path

# Füge rhinoplastik_app zum Python-Pfad hinzu
current_dir = Path(__file__).parent
rhinoplastik_path = current_dir / "rhinoplastik_app"
sys.path.insert(0, str(rhinoplastik_path))

# Mock-Klassen für Tests
class MockConfig:
    def get(self, key, default=None):
        defaults = {
            'ui.window_size': (1200, 800),
            'ui.window_min_size': (1000, 600),
            'app_dir': str(rhinoplastik_path)
        }
        return defaults.get(key, default)

class MockSession:
    def get_user_info(self):
        return {"username": "test", "role": "user"}
    
    def is_admin(self):
        return True
    
    def can_edit(self):
        return True
    
    def validate_session(self):
        return True

class MockPatient:
    def get_patient(self, patient_id):
        return None

def test_qt6_imports():
    """Testet PySide6/Qt6-Imports"""
    print("🔍 Teste PySide6/Qt6-Imports...")
    
    try:
        from PySide6.QtWidgets import (
            QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
            QTabWidget, QLabel, QPushButton, QMessageBox, QDialog,
            QDialogButtonBox, QMenuBar, QStatusBar, QFrame
        )
        from PySide6.QtCore import Qt, QTimer, Signal, QObject
        from PySide6.QtGui import QFont, QAction, QPixmap, QIcon
        
        print("   ✅ Alle PySide6-Qt6-Module erfolgreich importiert")
        return True
    except ImportError as e:
        print(f"   ❌ Import-Fehler: {e}")
        return False

def test_qt_version():
    """Testet Qt-Version"""
    print("🔍 Teste Qt-Version...")
    
    try:
        from PySide6.QtCore import qVersion
        from PySide6 import __version__ as pyside_version
        
        qt_version = qVersion()
        if qt_version.startswith("6."):
            print(f"   ✅ Qt-Version: {qt_version}")
        else:
            print(f"   ⚠️  Qt-Version: {qt_version} (erwartet: 6.x)")
            
        print(f"   ✅ PySide6-Version: {pyside_version}")
        return True
    except Exception as e:
        print(f"   ❌ Versions-Check fehlgeschlagen: {e}")
        return False

def test_ui_module_structure():
    """Testet UI-Modul-Struktur"""
    print("🔍 Teste UI-Modul-Struktur...")
    
    ui_path = rhinoplastik_path / "ui"
    required_modules = [
        "main_window.py",
        "dashboard_widget.py",
        "patients_list_widget.py",
        "search_widget.py",
        "patient_editor_widget.py",
        "image_manager_widget.py",
        "export_widget.py",
        "backup_widget.py",
        "statistics_widget.py",
        "login_dialog.py"
    ]
    
    missing_modules = []
    for module in required_modules:
        module_path = ui_path / module
        if module_path.exists():
            print(f"   ✅ {module}")
        else:
            print(f"   ❌ {module} - FEHLT")
            missing_modules.append(module)
    
    if not missing_modules:
        print("   ✅ Alle UI-Module vorhanden")
        return True
    else:
        print(f"   ❌ Fehlende Module: {missing_modules}")
        return False

def test_widget_creation():
    """Testet Widget-Erstellung"""
    print("🔍 Teste Widget-Erstellung...")
    
    try:
        # Mock QApplication für Headless-Tests
        from PySide6.QtWidgets import QApplication
        if not QApplication.instance():
            app = QApplication([])
        
        from PySide6.QtWidgets import (
            QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
            QLabel, QPushButton, QTabWidget, QFrame
        )
        
        # Teste verschiedene Widgets
        widgets_created = 0
        
        # Basic Widgets
        widget = QWidget()
        widgets_created += 1
        
        # Layouts
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        grid = QGridLayout()
        widgets_created += 3
        
        # UI Components
        label = QLabel("Test Label")
        button = QPushButton("Test Button")
        frame = QFrame()
        tab_widget = QTabWidget()
        widgets_created += 4
        
        print(f"   ✅ {widgets_created} Widgets erfolgreich erstellt")
        return True
        
    except Exception as e:
        print(f"   ❌ Widget-Erstellung fehlgeschlagen: {e}")
        return False

def test_signal_slot_framework():
    """Testet Signal-Slot-Framework"""
    print("🔍 Teste Signal-Slot-Framework...")
    
    try:
        from PySide6.QtWidgets import QApplication
        if not QApplication.instance():
            app = QApplication([])
        
        from PySide6.QtCore import QObject, Signal
        
        class TestObject(QObject):
            test_signal = Signal(str)
            
            def __init__(self):
                super().__init__()
                self.signal_received = False
                self.test_signal.connect(self.on_signal)
            
            def on_signal(self, data):
                self.signal_received = True
                self.received_data = data
        
        # Test Signal-Slot-Verbindung
        test_obj = TestObject()
        test_obj.test_signal.emit("test_data")
        
        if test_obj.signal_received and test_obj.received_data == "test_data":
            print("   ✅ Signal-Slot-Verbindung funktional")
            return True
        else:
            print("   ❌ Signal nicht empfangen")
            return False
            
    except Exception as e:
        print(f"   ❌ Signal-Slot-Test fehlgeschlagen: {e}")
        return False

def test_tab_widget_functionality():
    """Testet Tab-Widget-Funktionalität"""
    print("🔍 Teste Tab-Widget-Funktionalität...")
    
    try:
        from PySide6.QtWidgets import QApplication
        if not QApplication.instance():
            app = QApplication([])
        
        from PySide6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QLabel
        
        # Tab-Widget erstellen
        tab_widget = QTabWidget()
        
        # Tabs hinzufügen
        for i in range(5):
            tab = QWidget()
            layout = QVBoxLayout()
            label = QLabel(f"Tab {i+1} Content")
            layout.addWidget(label)
            tab.setLayout(layout)
            tab_widget.addTab(tab, f"Tab {i+1}")
        
        # Tab-Funktionalität prüfen
        if tab_widget.count() == 5:
            print("   ✅ 5 Tabs erfolgreich erstellt")
            
            # Tab-Wechsel testen
            for i in range(5):
                tab_widget.setCurrentIndex(i)
                if tab_widget.currentIndex() == i:
                    continue
                else:
                    print(f"   ❌ Tab-Wechsel zu Index {i} fehlgeschlagen")
                    return False
            
            print("   ✅ Tab-Wechsel funktional")
            return True
        else:
            print(f"   ❌ Falsche Tab-Anzahl: {tab_widget.count()}")
            return False
            
    except Exception as e:
        print(f"   ❌ Tab-Widget-Test fehlgeschlagen: {e}")
        return False

def test_dialog_creation():
    """Testet Dialog-Erstellung"""
    print("🔍 Teste Dialog-Erstellung...")
    
    try:
        from PySide6.QtWidgets import QApplication
        if not QApplication.instance():
            app = QApplication([])
        
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox
        
        # Dialog erstellen
        dialog = QDialog()
        dialog.setWindowTitle("Test Dialog")
        dialog.setModal(True)
        
        # Dialog-Layout
        layout = QVBoxLayout()
        label = QLabel("Test Dialog Content")
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        
        layout.addWidget(label)
        layout.addWidget(button_box)
        dialog.setLayout(layout)
        
        # Dialog-Eigenschaften prüfen
        if (dialog.windowTitle() == "Test Dialog" and 
            dialog.isModal() and
            dialog.layout() is not None):
            print("   ✅ Dialog erfolgreich erstellt")
            print("   ✅ Dialog-Eigenschaften korrekt")
            return True
        else:
            print("   ❌ Dialog-Eigenschaften falsch")
            return False
            
    except Exception as e:
        print(f"   ❌ Dialog-Test fehlgeschlagen: {e}")
        return False

def test_stylesheet_support():
    """Testet StyleSheet-Unterstützung"""
    print("🔍 Teste StyleSheet-Unterstützung...")
    
    try:
        from PySide6.QtWidgets import QApplication
        if not QApplication.instance():
            app = QApplication([])
        
        from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
        
        # Widget mit StyleSheet erstellen
        widget = QWidget()
        button = QPushButton("Styled Button")
        label = QLabel("Styled Label")
        
        layout = QVBoxLayout()
        layout.addWidget(button)
        layout.addWidget(label)
        widget.setLayout(layout)
        
        # StyleSheet anwenden
        style_sheet = """
            QWidget {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QLabel {
                color: #333;
                font-size: 14px;
            }
        """
        
        widget.setStyleSheet(style_sheet)
        
        if widget.styleSheet() == style_sheet:
            print("   ✅ StyleSheet korrekt angewendet")
            return True
        else:
            print("   ❌ StyleSheet nicht korrekt angewendet")
            return False
            
    except Exception as e:
        print(f"   ❌ StyleSheet-Test fehlgeschlagen: {e}")
        return False

def test_performance_metrics():
    """Testet Performance-Metriken"""
    print("🔍 Teste Performance-Metriken...")
    
    try:
        from PySide6.QtWidgets import QApplication
        if not QApplication.instance():
            app = QApplication([])
        
        from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
        from PySide6.QtCore import QTimer
        
        # Widget-Erstellungs-Performance
        start_time = time.time()
        
        widgets = []
        for i in range(50):
            widget = QWidget()
            layout = QVBoxLayout()
            
            # Füge Widgets hinzu
            for j in range(3):
                label = QLabel(f"Label {j}")
                button = QPushButton(f"Button {j}")
                layout.addWidget(label)
                layout.addWidget(button)
            
            widget.setLayout(layout)
            widgets.append(widget)
        
        creation_time = time.time() - start_time
        avg_creation_time = creation_time / 50 * 1000  # ms pro Widget
        
        print(f"   ✅ Widget-Erstellung: {creation_time:.3f}s für 50 Widgets")
        print(f"   ✅ Durchschnitt: {avg_creation_time:.2f}ms pro Widget")
        
        # Performance-Schwellenwerte prüfen
        if creation_time < 3.0:  # 3 Sekunden für 50 Widgets
            print("   ✅ Widget-Erstellung performant")
        else:
            print(f"   ⚠️  Widget-Erstellung langsam: {creation_time:.3f}s")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Performance-Test fehlgeschlagen: {e}")
        return False

def run_comprehensive_tests():
    """Führt alle Tests aus"""
    print("🚀 Starte PySide6/Qt6 Integration-Tests")
    print("=" * 60)
    
    test_results = []
    
    # Test-Suite
    tests = [
        ("Qt6 Imports", test_qt6_imports),
        ("Qt Version", test_qt_version),
        ("UI Modul-Struktur", test_ui_module_structure),
        ("Widget-Erstellung", test_widget_creation),
        ("Signal-Slot-Framework", test_signal_slot_framework),
        ("Tab-Widget", test_tab_widget_functionality),
        ("Dialog-Erstellung", test_dialog_creation),
        ("StyleSheet-Unterstützung", test_stylesheet_support),
        ("Performance-Metriken", test_performance_metrics)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            if result:
                test_results.append((test_name, "PASS", None))
                passed += 1
            else:
                test_results.append((test_name, "FAIL", "Test fehlgeschlagen"))
                failed += 1
        except Exception as e:
            test_results.append((test_name, "ERROR", str(e)))
            failed += 1
            print(f"   💥 Unerwarteter Fehler: {e}")
            traceback.print_exc()
    
    # Zusammenfassung
    print("\n" + "=" * 60)
    print("📊 TEST-ZUSAMMENFASSUNG")
    print("=" * 60)
    
    for test_name, status, error in test_results:
        if status == "PASS":
            print(f"✅ {test_name:<25} {status}")
        elif status == "FAIL":
            print(f"❌ {test_name:<25} {status} - {error}")
        else:  # ERROR
            print(f"💥 {test_name:<25} {status} - {error}")
    
    print("-" * 60)
    print(f"📈 Gesamt: {len(test_results)} Tests")
    print(f"✅ Bestanden: {passed}")
    print(f"❌ Fehlgeschlagen: {failed}")
    print(f"📊 Erfolgsrate: {passed/len(test_results)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 Alle Tests erfolgreich bestanden!")
        print("🔧 PySide6/Qt6-Integration funktional")
    else:
        print(f"\n⚠️  {failed} Test(s) fehlgeschlagen")
        print("🔧 PySide6/Qt6-Integration überprüfen")
    
    return failed == 0

if __name__ == "__main__":
    try:
        # QApplication für Headless-Tests initialisieren mit Offscreen-Platform
        from PySide6.QtWidgets import QApplication
        
        # Setze Offscreen-Platform für Headless-Tests
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        
        if not QApplication.instance():
            app = QApplication([])
        
        # Tests ausführen
        success = run_comprehensive_tests()
        
        # Exit-Code basierend auf Testergebnissen
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"💥 Kritischer Fehler bei Test-Ausführung: {e}")
        traceback.print_exc()
        sys.exit(1)

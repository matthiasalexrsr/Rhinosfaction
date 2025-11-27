#!/usr/bin/env python3
"""
Hauptfenster-Integration und UI-Architektur Tests

Testet die Integration der Qt-Komponenten ohne GUI-Ausführung
"""

import sys
import os
import importlib.util
import logging
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, List, Any

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UIArchitectureValidator:
    """Validiert die UI-Architektur und Komponenten-Integration"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.test_results = {}
        self.ui_components = {}
        
    def validate_project_structure(self) -> Dict[str, bool]:
        """Validiert die Projektstruktur für UI-Komponenten"""
        logger.info("🏗️ Validiere Projektstruktur...")
        
        structure_check = {
            'main_file_exists': (self.project_root / "app.py").exists(),
            'ui_directory_exists': (self.project_root / "ui").exists(),
            'config_directory_exists': (self.project_root / "config").exists(),
            'core_directory_exists': (self.project_root / "core").exists(),
            'assets_directory_exists': (self.project_root / "assets").exists()
        }
        
        # UI-Komponenten finden
        ui_dir = self.project_root / "ui"
        if ui_dir.exists():
            ui_files = list(ui_dir.glob("*.py"))
            self.ui_components = {
                'main_window': 'main_window.py',
                'login_dialog': 'login_dialog.py', 
                'dashboard_widget': 'dashboard_widget.py',
                'patients_list_widget': 'patients_list_widget.py',
                'search_widget': 'search_widget.py',
                'patient_editor_widget': 'patient_editor_widget.py',
                'export_widget': 'export_widget.py',
                'backup_widget': 'backup_widget.py',
                'statistics_widget': 'statistics_widget.py'
            }
            
            for component, filename in self.ui_components.items():
                structure_check[f'{component}_exists'] = any(
                    f.name == filename for f in ui_files
                )
        
        self.test_results['project_structure'] = structure_check
        return structure_check
    
    def validate_qapplication_initialization(self) -> Dict[str, Any]:
        """Validiert QApplication-Initialisierung in main.py"""
        logger.info("🔧 Validiere QApplication-Initialisierung...")
        
        main_file = self.project_root / "app.py"
        if not main_file.exists():
            return {'error': 'app.py nicht gefunden'}
            
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        validation_results = {
            'qapplication_import': 'QApplication' in content,
            'qapplication_creation': 'QApplication(' in content,
            'application_metadata_set': all([
                'setApplicationName' in content,
                'setApplicationVersion' in content,
                'setOrganizationName' in content
            ]),
            'high_dpi_support': 'AA_UseHighDpiPixmaps' in content,
            'exception_handling': 'handle_exception' in content,
            'sys_excepthook': 'sys.excepthook = handle_exception' in content
        }
        
        # Spezifische Zeilen prüfen
        lines = content.split('\n')
        qapp_creation_line = None
        for i, line in enumerate(lines):
            if 'QApplication(' in line and not line.strip().startswith('#'):
                qapp_creation_line = i + 1
                break
        
        if qapp_creation_line:
            validation_results['qapp_creation_line'] = qapp_creation_line
        
        self.test_results['qapplication_initialization'] = validation_results
        return validation_results
    
    def validate_main_window_setup(self) -> Dict[str, Any]:
        """Validiert QMainWindow-Setup und CentralWidget-Integration"""
        logger.info("🪟 Validiere Hauptfenster-Setup...")
        
        main_window_file = self.project_root / "ui" / "main_window.py"
        if not main_window_file.exists():
            return {'error': 'main_window.py nicht gefunden'}
            
        with open(main_window_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        validation_results = {
            'qmainwindow_inheritance': 'class MainWindow(QMainWindow)' in content,
            'central_widget_setup': 'setCentralWidget' in content,
            'tab_widget_integration': 'QTabWidget' in content,
            'window_title_set': 'setWindowTitle' in content,
            'window_size_config': 'resize(' in content and 'window_size' in content,
            'minimum_size_set': 'setMinimumSize' in content,
            'styles_defined': 'setStyleSheet' in content,
            'accessibility_support': 'setAccessibleName' in content and 'setAccessibleDescription' in content
        }
        
        # Tab-Struktur analysieren
        tab_methods = [line for line in content.split('\n') if 'def create_' in line and '_tab(' in line]
        validation_results['tab_methods_count'] = len(tab_methods)
        validation_results['tab_methods'] = [method.strip() for method in tab_methods]
        
        self.test_results['main_window_setup'] = validation_results
        return validation_results
    
    def validate_menubar_toolbar(self) -> Dict[str, Any]:
        """Prüft Menubar und Toolbar-Implementation"""
        logger.info("📋 Validiere Menüleiste und Toolbar...")
        
        main_window_file = self.project_root / "ui" / "main_window.py"
        if not main_window_file.exists():
            return {'error': 'main_window.py nicht gefunden'}
            
        with open(main_window_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        validation_results = {
            'menubar_created': 'menuBar()' in content,
            'file_menu': 'menubar.addMenu("Datei")' in content or 'addMenu("Datei")' in content,
            'view_menu': 'Ansicht' in content and 'addMenu' in content,
            'help_menu': 'Hilfe' in content and 'addMenu' in content,
            'tools_menu': 'Extras' in content and 'addMenu' in content
        }
        
        # Shortcuts analysieren
        shortcuts = []
        lines = content.split('\n')
        for line in lines:
            if 'setShortcut(' in line:
                shortcut = line.split('setShortcut(')[1].split(')')[0].strip('"\'')
                shortcuts.append(shortcut)
        
        validation_results['shortcuts_defined'] = shortcuts
        validation_results['shortcut_count'] = len(shortcuts)
        
        self.test_results['menubar_toolbar'] = validation_results
        return validation_results
    
    def validate_tab_integration(self) -> Dict[str, Any]:
        """Validiert Tab-Bar-Integration und Multi-View-Management"""
        logger.info("📑 Validiere Tab-Integration...")
        
        main_window_file = self.project_root / "ui" / "main_window.py"
        if not main_window_file.exists():
            return {'error': 'main_window.py nicht gefunden'}
            
        with open(main_window_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Tabs analysieren
        tab_widget_calls = []
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'addTab(' in line:
                # Extrahiere Tab-Name
                tab_line = line.strip()
                if 'addTab(' in tab_line:
                    try:
                        # Finde den Tab-Namen in der addTab-Zeile
                        start = tab_line.find('addTab(') + 7
                        # Finde das Ende der Parameter
                        if ',"' in tab_line:
                            end = tab_line.find('",', start)
                            tab_name = tab_line[start:end].strip().strip('"')
                            tab_widget_calls.append({
                                'line': i + 1,
                                'tab_name': tab_name
                            })
                    except:
                        pass
        
        validation_results = {
            'tab_widget_created': 'self.tab_widget = QTabWidget()' in content,
            'tab_widget_configured': all([
                'setAccessibleName' in content,
                'setAccessibleDescription' in content
            ]),
            'tabs_added': len(tab_widget_calls) > 0,
            'tab_count': len(tab_widget_calls),
            'tabs_list': [tab['tab_name'] for tab in tab_widget_calls]
        }
        
        self.test_results['tab_integration'] = validation_results
        return validation_results
    
    def validate_statusbar_integration(self) -> Dict[str, Any]:
        """Testet QStatusBar-Integration und Progress-Bar-Updates"""
        logger.info("📊 Validiere StatusBar-Integration...")
        
        main_window_file = self.project_root / "ui" / "main_window.py"
        if not main_window_file.exists():
            return {'error': 'main_window.py nicht gefunden'}
            
        with open(main_window_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        validation_results = {
            'statusbar_created': 'statusBar()' in content,
            'status_messages': 'showMessage(' in content,
            'user_status_label': 'user_status_label' in content,
            'statusbar_methods': {
                'show_message': 'showMessage(' in content,
                'add_permanent_widget': 'addPermanentWidget' in content,
                'clear_message': 'clearMessage' in content
            }
        }
        
        # Status-Nachrichten analysieren
        status_messages = []
        lines = content.split('\n')
        for line in lines:
            if 'showMessage(' in line:
                message = line.split('showMessage(')[1].split(')')[0].strip('"\'')
                status_messages.append(message)
        
        validation_results['status_messages_defined'] = status_messages
        
        self.test_results['statusbar_integration'] = validation_results
        return validation_results
    
    def validate_window_state_management(self) -> Dict[str, Any]:
        """Prüft Window-State-Management (Minimieren, Maximieren, Schließen)"""
        logger.info("🔄 Validiere Window-State-Management...")
        
        main_window_file = self.project_root / "ui" / "main_window.py"
        if not main_window_file.exists():
            return {'error': 'main_window.py nicht gefunden'}
            
        with open(main_window_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        validation_results = {
            'close_event_overridden': 'def closeEvent(' in content,
            'session_cleanup': 'session_manager.clear_session()' in content,
            'window_size_configurable': 'window_size' in content,
            'min_size_configurable': 'window_min_size' in content,
            'resize_method_used': 'self.resize(' in content,
            'setMinimumSize_used': 'self.setMinimumSize(' in content
        }
        
        # Spezielle Events suchen
        event_handlers = []
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith('def on_') and '_action' in line:
                event_handlers.append(line.strip())
        
        validation_results['action_handlers'] = event_handlers
        
        self.test_results['window_state_management'] = validation_results
        return validation_results
    
    def validate_shortcut_definitions(self) -> Dict[str, Any]:
        """Validiert Shortcut-Definitionen und Key-Bindings"""
        logger.info("⌨️ Validiere Shortcut-Definitionen...")
        
        main_window_file = self.project_root / "ui" / "main_window.py"
        if not main_window_file.exists():
            return {'error': 'main_window.py nicht gefunden'}
            
        with open(main_window_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Shortcuts sammeln
        shortcuts = []
        shortcut_mappings = {}
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if 'setShortcut(' in line:
                try:
                    # Extrahiere Action-Name und Shortcut
                    action_start = line.rfind('QAction(') + 8
                    action_end = line.find(')', action_start)
                    if action_start > 7 and action_end > action_start:
                        action_name = line[action_start:action_end].strip('"\'')
                    
                    shortcut_start = line.find('setShortcut(') + 13
                    shortcut_end = line.find(')', shortcut_start)
                    if shortcut_start > 12 and shortcut_end > shortcut_start:
                        shortcut = line[shortcut_start:shortcut_end].strip('"\'')
                        shortcuts.append(shortcut)
                        shortcut_mappings[shortcut] = action_name
                except:
                    pass
        
        # Standard-Shortcuts validieren
        standard_shortcuts = {
            'Ctrl+N': 'Neu/New Patient',
            'Ctrl+O': 'Öffnen/Open',
            'Ctrl+S': 'Speichern/Save',
            'Ctrl+F': 'Suchen/Search',
            'Ctrl+Q': 'Beenden/Quit'
        }
        
        validation_results = {
            'shortcut_count': len(shortcuts),
            'shortcuts_defined': shortcuts,
            'shortcut_mappings': shortcut_mappings,
            'standard_shortcuts': {
                name: shortcut in shortcuts 
                for name, shortcut in standard_shortcuts.items()
            }
        }
        
        self.test_results['shortcut_definitions'] = validation_results
        return validation_results
    
    def validate_ui_responsiveness(self) -> Dict[str, Any]:
        """Testet UI-Responsiveness und Event-Handling"""
        logger.info("⚡ Validiere UI-Responsiveness...")
        
        main_window_file = self.project_root / "ui" / "main_window.py"
        if not main_window_file.exists():
            return {'error': 'main_window.py nicht gefunden'}
            
        with open(main_window_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        validation_results = {
            'timers_used': 'QTimer' in content,
            'session_validation_timer': 'session_timer' in content,
            'signal_slot_connections': 'connect(' in content,
            'async_operations': any(keyword in content for keyword in [
                'thread', 'worker', 'async', 'QThread'
            ]),
            'progress_indicators': 'progress' in content.lower(),
            'error_handling': 'try:' in content and 'except' in content,
            'logging_integration': 'logger' in content
        }
        
        # Event-Handler analysieren
        event_handlers = []
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith('def on_') and '(' in line:
                event_handlers.append(line.strip().replace('def ', '').split('(')[0])
        
        validation_results['event_handlers'] = event_handlers
        validation_results['event_handler_count'] = len(event_handlers)
        
        self.test_results['ui_responsiveness'] = validation_results
        return validation_results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Führt alle Tests aus und sammelt Ergebnisse"""
        logger.info("🚀 Starte Hauptfenster-Integration-Tests...")
        
        # Alle Validierungstests ausführen
        self.validate_project_structure()
        self.validate_qapplication_initialization()
        self.validate_main_window_setup()
        self.validate_menubar_toolbar()
        self.validate_tab_integration()
        self.validate_statusbar_integration()
        self.validate_window_state_management()
        self.validate_shortcut_definitions()
        self.validate_ui_responsiveness()
        
        # Zusammenfassung erstellen
        summary = {
            'total_tests': len(self.test_results),
            'passed_tests': sum(1 for result in self.test_results.values() 
                              if isinstance(result, dict) and not result.get('error')),
            'failed_tests': sum(1 for result in self.test_results.values() 
                               if isinstance(result, dict) and result.get('error')),
            'test_categories': list(self.test_results.keys()),
            'detailed_results': self.test_results
        }
        
        logger.info(f"✅ Tests abgeschlossen: {summary['passed_tests']}/{summary['total_tests']} erfolgreich")
        return summary


def main():
    """Hauptfunktion für Tests"""
    project_root = "/workspace/rhinoplastik_app"
    
    validator = UIArchitectureValidator(project_root)
    results = validator.run_all_tests()
    
    return results


if __name__ == "__main__":
    results = main()
    print(f"\n📋 Test-Zusammenfassung:")
    print(f"Gesamt: {results['total_tests']}")
    print(f"Erfolgreich: {results['passed_tests']}")
    print(f"Fehlgeschlagen: {results['failed_tests']}")
    print(f"Kategorien: {results['test_categories']}")
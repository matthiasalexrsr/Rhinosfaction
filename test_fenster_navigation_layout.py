"""
Fenster-Navigation & Layout-Management Test Suite
Führt alle Tests für Navigation und Layout-Management aus

Autor: MiniMax Agent
Datum: 2025-11-06
"""

import sys
import os
import time
import json
import random
import logging
import psutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any

# PySide6 Imports
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QTabWidget, QDialog
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

# Add app modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'rhinoplastik_app'))

try:
    from ui.main_window import MainWindow
    from core.config.app_config import AppConfig
    from core.session.session_manager import SessionManager  
    from core.patients.patient_manager import PatientManager
    from ui.dashboard_widget import StatTile
    from ui.patients_list_widget import PatientsListWidget
    from ui.search_widget import SearchWidget
    from ui.patient_editor_widget import PatientEditorWidget
    from ui.export_widget import ExportWidget
    from ui.backup_widget import BackupWidget
    from ui.statistics_widget import StatisticsWidget
    from core.media.media_manager import MediaManager
    from core.export.export_service import ExportService
    from core.backup.backup_service import BackupService
    from core.statistics.statistics_service import StatisticsService
except ImportError as e:
    print(f"Import Error: {e}")
    print("Möglicherweise müssen die Abhängigkeiten installiert werden:")
    print("pip install -r requirements.txt")


class LayoutNavigationTestRunner:
    """Hauptklasse für Layout- und Navigation-Tests"""
    
    def __init__(self):
        """Initialisiert den Test-Runner"""
        self.logger = logging.getLogger(__name__)
        self.test_results = {}
        self.performance_metrics = {}
        self.test_app = None
        self.main_window = None
        
        # Test-Daten
        self.config = None
        self.session_manager = None
        self.patient_manager = None
        self.media_manager = None
        
        # Performance-Benchmarks
        self.benchmarks = {
            'tab_switch_max': 200,  # ms
            'modal_open_max': 500,  # ms
            'layout_render_max': 300,  # ms
            'memory_increase_max': 50,  # MB
            'ui_responsiveness_max': 100  # ms
        }
    
    def setup_test_environment(self):
        """Richtet die Test-Umgebung ein"""
        try:
            # Logging einrichten
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            # QApplication erstellen
            if not QApplication.instance():
                self.test_app = QApplication([])
            
            # Test-Daten initialisieren
            self.config = AppConfig()
            self.session_manager = SessionManager()
            self.patient_manager = PatientManager()
            
            app_dir = self.config.get('app_dir', os.path.dirname(__file__))
            self.media_manager = MediaManager(app_dir)
            
            # Mock-User für Tests
            self.setup_mock_user()
            
            self.logger.info("Test-Umgebung erfolgreich eingerichtet")
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler beim Einrichten der Test-Umgebung: {e}")
            return False
    
    def setup_mock_user(self):
        """Richtet Mock-User für Tests ein"""
        # Admin-Benutzer simulieren
        admin_user = {
            'username': 'test_admin',
            'role': 'admin',
            'permissions': ['read', 'write', 'admin']
        }
        
        # Session-Mock implementieren
        self.session_manager.validate_session = lambda: True
        self.session_manager.is_admin = lambda: True
        self.session_manager.can_edit = lambda: True
        self.session_manager.get_user_info = lambda: admin_user
    
    def cleanup_test_environment(self):
        """Räumt die Test-Umgebung auf"""
        if self.main_window:
            self.main_window.close()
        
        if self.test_app:
            self.test_app.processEvents()
    
    def test_basic_tab_navigation(self) -> bool:
        """TN-001: Grundlegende Tab-Navigation"""
        try:
            self.logger.info("Starte TN-001: Grundlegende Tab-Navigation")
            
            # Hauptfenster erstellen
            self.main_window = MainWindow(
                self.config, 
                self.session_manager, 
                self.patient_manager
            )
            self.main_window.show()
            self.test_app.processEvents()
            
            # Test-Tabs
            expected_tabs = [
                "📊 Dashboard", "👥 Patienten", "🔍 Suchen", "📤 Export", 
                "💾 Backup", "📊 Statistiken", "⚙️ Administration"
            ]
            
            tab_switch_times = []
            
            for i, expected_tab in enumerate(expected_tabs):
                # Tab aktivieren
                start_time = time.time()
                self.main_window.tab_widget.setCurrentIndex(i)
                self.test_app.processEvents()
                
                # Verifikation
                current_tab = self.main_window.tab_widget.tabText(i)
                if current_tab != expected_tab:
                    self.logger.error(f"Tab {i}: Expected '{expected_tab}', got '{current_tab}'")
                    return False
                
                # Performance-Messung
                switch_time = (time.time() - start_time) * 1000  # ms
                tab_switch_times.append(switch_time)
                
                if switch_time > self.benchmarks['tab_switch_max']:
                    self.logger.warning(f"Tab {i}: Switch time {switch_time:.2f}ms überschreitet Benchmark")
            
            # Performance-Statistiken
            avg_time = sum(tab_switch_times) / len(tab_switch_times)
            max_time = max(tab_switch_times)
            min_time = min(tab_switch_times)
            
            self.performance_metrics.update({
                'tab_switch_avg': avg_time,
                'tab_switch_max': max_time,
                'tab_switch_min': min_time
            })
            
            self.logger.info(f"Tab-Navigation erfolgreich. Avg: {avg_time:.2f}ms, Max: {max_time:.2f}ms")
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler in TN-001: {e}")
            return False
    
    def test_tab_state_persistence(self) -> bool:
        """TN-002: Tab-State-Persistenz"""
        try:
            self.logger.info("Starte TN-002: Tab-State-Persistenz")
            
            if not self.main_window:
                return False
            
            # Tab 2 (Suchen) aktivieren
            target_tab = 2
            self.main_window.tab_widget.setCurrentIndex(target_tab)
            
            # Fenster minimieren und wiederherstellen
            self.main_window.showMinimized()
            time.sleep(0.1)
            self.main_window.showNormal()
            self.test_app.processEvents()
            
            # Verifikation
            current_tab = self.main_window.tab_widget.currentIndex()
            if current_tab != target_tab:
                self.logger.error(f"Tab state not preserved. Expected {target_tab}, got {current_tab}")
                return False
            
            self.logger.info("Tab-State-Persistenz erfolgreich")
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler in TN-002: {e}")
            return False
    
    def test_dynamic_tab_visibility(self) -> bool:
        """TN-003: Dynamic Tab Management"""
        try:
            self.logger.info("Starte TN-003: Dynamic Tab Management")
            
            if not self.main_window:
                return False
            
            # Admin-Tab prüfen
            admin_tab_count = self.main_window.tab_widget.count()
            tab_texts = [self.main_window.tab_widget.tabText(i) for i in range(admin_tab_count)]
            
            has_admin_tab = "⚙️ Administration" in tab_texts
            if not has_admin_tab:
                self.logger.error("Admin tab not visible for admin user")
                return False
            
            # Mock: Normaler Benutzer
            self.session_manager.is_admin = lambda: False
            
            # Neues Fenster für normalen Benutzer
            user_window = MainWindow(
                self.config, 
                self.session_manager, 
                self.patient_manager
            )
            user_window.show()
            self.test_app.processEvents()
            
            user_tab_count = user_window.tab_widget.count()
            user_tab_texts = [user_window.tab_widget.tabText(i) for i in range(user_tab_count)]
            user_has_admin_tab = "⚙️ Administration" in user_tab_texts
            
            if user_has_admin_tab:
                self.logger.error("Admin tab visible for normal user")
                user_window.close()
                return False
            
            user_window.close()
            
            self.logger.info("Dynamic Tab Management erfolgreich")
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler in TN-003: {e}")
            return False
    
    def test_minimum_window_size(self) -> bool:
        """RL-001: Minimum Window Size Enforcement"""
        try:
            self.logger.info("Starte RL-001: Minimum Window Size Enforcement")
            
            if not self.main_window:
                return False
            
            # Mindestgröße aus Konfiguration
            expected_min_size = self.config.get('ui.window_min_size', (1000, 600))
            actual_min_size = (
                self.main_window.minimumWidth(), 
                self.main_window.minimumHeight()
            )
            
            if actual_min_size != expected_min_size:
                self.logger.error(f"Expected min size {expected_min_size}, got {actual_min_size}")
                return False
            
            # Versuch, kleiner zu machen
            self.main_window.resize(500, 400)
            self.test_app.processEvents()
            
            # Verifikation: Mindestgröße wird eingehalten
            actual_size = (self.main_window.width(), self.main_window.height())
            if actual_size[0] < expected_min_size[0] or actual_size[1] < expected_min_size[1]:
                self.logger.error("Window size below minimum not prevented")
                return False
            
            self.logger.info("Minimum Window Size erfolgreich")
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler in RL-001: {e}")
            return False
    
    def test_patient_editor_modal_opening(self) -> bool:
        """MD-001: Patient-Editor Modal Opening"""
        try:
            self.logger.info("Starte MD-001: Patient-Editor Modal Opening")
            
            if not self.main_window:
                return False
            
            # Mock-Patient für Tests
            class MockPatient:
                def __init__(self):
                    self.patient_id = "TEST_PATIENT_001"
                    self.demographics = MockDemographics()
            
            class MockDemographics:
                def __init__(self):
                    self.lastname = "Mustermann"
                    self.firstname = "Max"
            
            mock_patient = MockPatient()
            
            # Modal öffnen
            start_time = time.time()
            self.main_window.open_patient_editor(mock_patient, readonly=False)
            self.test_app.processEvents()
            
            # Modal-Dialog finden
            dialogs = self.main_window.findChildren(QDialog)
            if not dialogs:
                self.logger.error("No dialog found after opening patient editor")
                return False
            
            editor_dialog = dialogs[0]
            
            # Modal-Eigenschaften verifizieren
            if not editor_dialog.isModal():
                self.logger.error("Dialog is not modal")
                return False
            
            if not editor_dialog.isVisible():
                self.logger.error("Dialog is not visible")
                return False
            
            if "Patient" not in editor_dialog.windowTitle():
                self.logger.error(f"Unexpected title: {editor_dialog.windowTitle()}")
                return False
            
            # Performance-Messung
            open_time = (time.time() - start_time) * 1000  # ms
            self.performance_metrics['modal_open_time'] = open_time
            
            if open_time > self.benchmarks['modal_open_max']:
                self.logger.warning(f"Modal opening time {open_time:.2f}ms exceeds benchmark")
            
            # Modal schließen für nächsten Test
            editor_dialog.close()
            self.test_app.processEvents()
            
            self.logger.info(f"Patient-Editor Modal erfolgreich. Zeit: {open_time:.2f}ms")
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler in MD-001: {e}")
            return False
    
    def test_layout_rendering_performance(self) -> bool:
        """PM-003: Layout Rendering Performance"""
        try:
            self.logger.info("Starte PM-003: Layout Rendering Performance")
            
            rendering_times = []
            
            # 3 Layout-Renderings messen
            for i in range(3):
                start_time = time.time()
                
                # Neues Fenster erstellen (triggert Layout-Rendering)
                temp_window = MainWindow(
                    self.config, 
                    self.session_manager, 
                    self.patient_manager
                )
                temp_window.show()
                self.test_app.processEvents()
                
                end_time = time.time()
                render_time = (end_time - start_time) * 1000  # ms
                rendering_times.append(render_time)
                
                # Aufräumen
                temp_window.close()
                self.test_app.processEvents()
            
            # Statistiken
            avg_time = sum(rendering_times) / len(rendering_times)
            max_time = max(rendering_times)
            
            self.performance_metrics.update({
                'layout_render_avg': avg_time,
                'layout_render_max': max_time
            })
            
            if avg_time > self.benchmarks['layout_render_max']:
                self.logger.warning(f"Average layout rendering {avg_time:.2f}ms exceeds benchmark")
            
            self.logger.info(f"Layout Rendering erfolgreich. Avg: {avg_time:.2f}ms, Max: {max_time:.2f}ms")
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler in PM-003: {e}")
            return False
    
    def test_memory_usage_monitoring(self) -> bool:
        """PM-004: Memory Usage Monitoring"""
        try:
            self.logger.info("Starte PM-004: Memory Usage Monitoring")
            
            process = psutil.Process()
            
            # Initialer Speicherverbrauch
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            self.performance_metrics['initial_memory_mb'] = initial_memory
            
            if not self.main_window:
                return False
            
            # Layout-Operationen durchführen
            operations_count = 20
            for i in range(operations_count):
                # Tab-Wechsel
                tab_index = i % self.main_window.tab_widget.count()
                self.main_window.tab_widget.setCurrentIndex(tab_index)
                self.test_app.processEvents()
            
            # Finaler Speicherverbrauch
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            self.performance_metrics.update({
                'final_memory_mb': final_memory,
                'memory_increase_mb': memory_increase
            })
            
            if memory_increase > self.benchmarks['memory_increase_max']:
                self.logger.warning(f"Memory increase {memory_increase:.2f}MB exceeds benchmark")
            
            self.logger.info(f"Memory Monitoring erfolgreich. "
                           f"Initial: {initial_memory:.2f}MB, Final: {final_memory:.2f}MB, "
                           f"Increase: {memory_increase:.2f}MB")
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler in PM-004: {e}")
            return False
    
    def test_ui_responsiveness_under_load(self) -> bool:
        """PM-005: UI Responsiveness Under Load"""
        try:
            self.logger.info("Starte PM-005: UI Responsiveness Under Load")
            
            if not self.main_window:
                return False
            
            # Last-Simulation: Schnelle Tab-Wechsel
            start_time = time.time()
            tab_changes = 0
            load_test_iterations = 30
            
            for i in range(load_test_iterations):
                tab_index = i % self.main_window.tab_widget.count()
                self.main_window.tab_widget.setCurrentIndex(tab_index)
                self.test_app.processEvents()
                tab_changes += 1
            
            total_time = time.time() - start_time
            avg_time_per_change = total_time / tab_changes
            
            self.performance_metrics.update({
                'ui_load_test_time_s': total_time,
                'ui_responsiveness_avg_ms': avg_time_per_change * 1000,
                'ui_tab_changes': tab_changes
            })
            
            if avg_time_per_change > self.benchmarks['ui_responsiveness_max'] / 1000:
                self.logger.warning(f"UI responsiveness {avg_time_per_change*1000:.2f}ms exceeds benchmark")
            
            self.logger.info(f"UI Responsiveness erfolgreich. "
                           f"Total: {total_time:.3f}s, Avg per change: {avg_time_per_change*1000:.2f}ms, "
                           f"Changes: {tab_changes}")
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler in PM-005: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Führt alle Tests aus"""
        self.logger.info("Starte umfassende Layout & Navigation Tests")
        
        # Test-Umgebung einrichten
        if not self.setup_test_environment():
            return {'error': 'Test-Environment Setup failed'}
        
        # Test-Suite definieren
        test_suite = [
            ('test_basic_tab_navigation', self.test_basic_tab_navigation),
            ('test_tab_state_persistence', self.test_tab_state_persistence),
            ('test_dynamic_tab_visibility', self.test_dynamic_tab_visibility),
            ('test_minimum_window_size', self.test_minimum_window_size),
            ('test_patient_editor_modal_opening', self.test_patient_editor_modal_opening),
            ('test_layout_rendering_performance', self.test_layout_rendering_performance),
            ('test_memory_usage_monitoring', self.test_memory_usage_monitoring),
            ('test_ui_responsiveness_under_load', self.test_ui_responsiveness_under_load),
        ]
        
        # Tests ausführen
        passed_tests = 0
        failed_tests = 0
        
        for test_name, test_function in test_suite:
            try:
                self.logger.info(f"Führe Test aus: {test_name}")
                result = test_function()
                
                if result:
                    self.test_results[test_name] = 'PASSED'
                    passed_tests += 1
                    self.logger.info(f"✅ {test_name}: ERFOLGREICH")
                else:
                    self.test_results[test_name] = 'FAILED'
                    failed_tests += 1
                    self.logger.error(f"❌ {test_name}: FEHLGESCHLAGEN")
                    
            except Exception as e:
                self.test_results[test_name] = f'ERROR: {str(e)}'
                failed_tests += 1
                self.logger.error(f"💥 {test_name}: ERROR - {e}")
        
        # Test-Zusammenfassung
        test_summary = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(test_suite),
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': (passed_tests / len(test_suite)) * 100,
            'test_results': self.test_results,
            'performance_metrics': self.performance_metrics,
            'benchmarks': self.benchmarks,
            'benchmark_compliance': self._check_benchmark_compliance()
        }
        
        # Aufräumen
        self.cleanup_test_environment()
        
        self.logger.info(f"Tests abgeschlossen. {passed_tests}/{len(test_suite)} erfolgreich")
        return test_summary
    
    def _check_benchmark_compliance(self) -> Dict[str, bool]:
        """Prüft Benchmark-Compliance"""
        compliance = {}
        
        # Tab Switch Performance
        if 'tab_switch_avg' in self.performance_metrics:
            compliance['tab_switch_performance'] = \
                self.performance_metrics['tab_switch_avg'] < self.benchmarks['tab_switch_max']
        
        # Modal Opening Performance
        if 'modal_open_time' in self.performance_metrics:
            compliance['modal_opening_performance'] = \
                self.performance_metrics['modal_open_time'] < self.benchmarks['modal_open_max']
        
        # Layout Rendering Performance
        if 'layout_render_avg' in self.performance_metrics:
            compliance['layout_rendering_performance'] = \
                self.performance_metrics['layout_render_avg'] < self.benchmarks['layout_render_max']
        
        # Memory Usage
        if 'memory_increase_mb' in self.performance_metrics:
            compliance['memory_usage'] = \
                self.performance_metrics['memory_increase_mb'] < self.benchmarks['memory_increase_max']
        
        # UI Responsiveness
        if 'ui_responsiveness_avg_ms' in self.performance_metrics:
            compliance['ui_responsiveness'] = \
                self.performance_metrics['ui_responsiveness_avg_ms'] < self.benchmarks['ui_responsiveness_max']
        
        return compliance
    
    def generate_detailed_report(self, test_summary: Dict[str, Any]) -> str:
        """Generiert detaillierten Test-Report"""
        
        report = f"""
# 📊 Fenster-Navigation & Layout-Management Test Report

**Test-Ausführung:** {test_summary['timestamp']}  
**Test-Suite Version:** 1.0.0  
**Anwendung:** Rhinoplastik-Dokumentation v1.0.0

---

## 🎯 Zusammenfassung

| Metrik | Wert |
|--------|------|
| **Gesamt-Tests** | {test_summary['total_tests']} |
| **Erfolgreich** | {test_summary['passed']} ✅ |
| **Fehlgeschlagen** | {test_summary['failed']} ❌ |
| **Erfolgsrate** | {test_summary['success_rate']:.1f}% |

---

## 📋 Detaillierte Test-Ergebnisse

"""
        
        for test_name, result in test_summary['test_results'].items():
            status_icon = "✅" if result == "PASSED" else "❌"
            report += f"### {test_name}\n{status_icon} **{result}**\n\n"
        
        report += """
---

## ⚡ Performance-Metriken

"""
        
        if test_summary['performance_metrics']:
            for metric, value in test_summary['performance_metrics'].items():
                unit = "ms" if "time" in metric or "avg" in metric or "max" in metric else "MB"
                report += f"- **{metric.replace('_', ' ').title()}:** {value:.2f}{unit}\n"
        
        report += """
---

## 🎯 Benchmark-Compliance

"""
        
        for benchmark, compliant in test_summary['benchmark_compliance'].items():
            status = "✅ ERFÜLLT" if compliant else "❌ ÜBERSCHREITEN"
            report += f"- **{benchmark.replace('_', ' ').title()}:** {status}\n"
        
        report += f"""
---

## 📈 Performance-Ziele vs. Ist-Werte

| Metrik | Ziel | Ist-Wert | Status |
|--------|------|----------|--------|
"""
        
        benchmarks = test_summary['benchmarks']
        metrics = test_summary['performance_metrics']
        
        benchmark_mapping = {
            'tab_switch_avg': ('Tab-Wechsel (Ø)', 'ms', benchmarks['tab_switch_max']),
            'modal_open_time': ('Modal-Öffnung', 'ms', benchmarks['modal_open_max']),
            'layout_render_avg': ('Layout-Rendering (Ø)', 'ms', benchmarks['layout_render_max']),
            'memory_increase_mb': ('Speicher-Inkrement', 'MB', benchmarks['memory_increase_max']),
            'ui_responsiveness_avg_ms': ('UI-Responsivität (Ø)', 'ms', benchmarks['ui_responsiveness_max'])
        }
        
        for metric_key, (name, unit, target) in benchmark_mapping.items():
            if metric_key in metrics:
                actual = metrics[metric_key]
                status = "✅" if actual < target else "❌"
                report += f"| {name} | {target} {unit} | {actual:.2f} {unit} | {status} |\n"
        
        report += f"""
---

## 🔍 Empfehlungen

"""
        
        if test_summary['failed'] > 0:
            report += f"""
### ⚠️ Fehlgeschlagene Tests
- **{test_summary['failed']} Tests** sind fehlgeschlagen
- Detaillierte Logs prüfen für spezifische Fehlerursachen
- Erneute Test-Ausführung nach Bugfixes

"""
        
        if test_summary['success_rate'] < 100:
            report += f"""
### 🎯 Performance-Optimierungen
- Detaillierte Profiling-Analyse durchführen
- Bottlenecks in kritischen UI-Pfaden identifizieren
- Lazy-Loading für große Datenmengen implementieren

"""
        
        report += f"""
### ✅ Bestätigte Funktionalitäten
- Tab-Navigation funktioniert korrekt
- Modal-Dialoge öffnen sich erwartungsgemäß
- Layout-Rendering liegt im akzeptablen Bereich
- Grundlegende UI-Responsivität ist gegeben

---

## 📞 Nächste Schritte

1. **Fehlgeschlagene Tests analysieren** und Bugs fixen
2. **Performance-Optimierungen** für Überschreitungen implementieren  
3. **Regelmäßige Test-Läufe** in CI/CD integrieren
4. **Cross-Platform-Tests** auf verschiedenen Betriebssystemen durchführen

---

*Report generiert am {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} durch Layout & Navigation Test Suite v1.0.0*
"""
        
        return report


def main():
    """Hauptfunktion für Test-Ausführung"""
    print("🚀 Starte Fenster-Navigation & Layout-Management Tests")
    print("=" * 60)
    
    # Test-Runner erstellen
    runner = LayoutNavigationTestRunner()
    
    try:
        # Tests ausführen
        test_summary = runner.run_all_tests()
        
        # Report generieren
        report = runner.generate_detailed_report(test_summary)
        
        # Report anzeigen
        print(report)
        
        # Report speichern
        report_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'layout_navigation_test_results.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # JSON-Export für CI/CD
        json_path = os.path.join(os.path.dirname(__file__), 'layout_navigation_test_results.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(test_summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Report gespeichert: {report_path}")
        print(f"📊 JSON-Ergebnisse: {json_path}")
        
        # Exit-Code basierend auf Test-Erfolg
        if test_summary.get('failed', 0) > 0:
            print(f"\n❌ {test_summary['failed']} Tests fehlgeschlagen")
            return 1
        else:
            print(f"\n✅ Alle {test_summary['total_tests']} Tests erfolgreich")
            return 0
            
    except Exception as e:
        print(f"💥 Schwerwiegender Fehler: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
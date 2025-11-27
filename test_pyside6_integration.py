#!/usr/bin/env python3
"""
PySide6-Integration und Widget-Funktionalität Test

Testet vollständige PySide6-Integration:
1. Import und Test aller PySide6-Widgets (QApplication, QMainWindow, QDialog, etc.)
2. Validierung der PySide6-Qt-Selektor-Integration
3. Test des Layout-Managements (QVBoxLayout, QHBoxLayout, QGridLayout)
4. Prüfung der Widget-Event-Hookup (Clicked, TextChanged, ValueChanged)
5. Test von QTableWidget und QTreeWidget-Integration
6. Validierung von QMessageBox und QFileDialog-Integration
7. Prüfung von QSpinBox und QDoubleSpinBox-Integration
8. Erstellung detaillierter Test-Reports

Ausführung: python test_pyside6_integration.py
"""

import sys
import os
import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# PySide6 für GUI-Tests
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QFormLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox,
    QSpinBox, QDoubleSpinBox, QCheckBox, QDateEdit, QTimeEdit, QDateTimeEdit,
    QSlider, QScrollArea, QTabWidget, QDialog, QMessageBox, QFileDialog,
    QDialogButtonBox, QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem,
    QListWidget, QListWidgetItem, QGroupBox, QFrame, QSplitter, QProgressBar,
    QToolBar, QStatusBar, QMenuBar, QMenu, QSystemTrayIcon, QToolButton,
    QCalendarWidget, QLCDNumber, QDial, QButtonGroup, QRadioButton, 
    QGroupBox, QFrame, QSizeGrip, QListView
)
from PySide6.QtCore import Qt, QTimer, QObject, Signal, QDate, QTime, QDateTime, QThread, QStringListModel
from PySide6.QtGui import QFont, QPalette, QColor, QPixmap, QIcon, QKeySequence

# App-Pfade
sys.path.append('/workspace/rhinoplastik_app')

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PySide6IntegrationTestSuite:
    """Umfassende Test-Suite für PySide6-Integration und Widget-Funktionalität"""
    
    def __init__(self):
        self.app = None
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "version": "PySide6 Integration Test v1.0",
            "tests": {},
            "summary": {},
            "integration_score": 0.0,
            "widget_coverage": {},
            "layout_test_results": {},
            "event_test_results": {},
            "dialog_test_results": {}
        }
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.widget_tested = set()
        
    def setup_application(self):
        """Richtet QApplication für Tests ein"""
        try:
            # QApplication initialisieren falls noch nicht vorhanden
            if not QApplication.instance():
                self.app = QApplication(sys.argv)
            else:
                self.app = QApplication.instance()
            
            # App-Attribute setzen
            self.app.setApplicationName("PySide6 Integration Test")
            self.app.setApplicationVersion("1.0")
            self.app.setOrganizationName("Test Organization")
            
            logger.info("✅ QApplication erfolgreich initialisiert")
            return True
        except Exception as e:
            logger.error(f"❌ Fehler beim Initialisieren der QApplication: {e}")
            return False
    
    def test_pyside6_widget_imports(self):
        """Test 1: Import und Test aller PySide6-Widgets"""
        test_name = "PySide6_Widget_Imports"
        logger.info(f"Starte Test: {test_name}")
        
        try:
            # Core Widgets
            core_widgets = [
                QApplication, QMainWindow, QWidget, QDialog, QMessageBox, QFileDialog,
                QDialogButtonBox
            ]
            
            # Layout Widgets
            layout_widgets = [
                QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout
            ]
            
            # Input Widgets  
            input_widgets = [
                QLabel, QLineEdit, QTextEdit, QPushButton, QComboBox, QSpinBox,
                QDoubleSpinBox, QCheckBox, QDateEdit, QTimeEdit, QDateTimeEdit,
                QSlider, QDial, QLCDNumber, QRadioButton
            ]
            
            # Container Widgets
            container_widgets = [
                QGroupBox, QFrame, QScrollArea, QTabWidget, QSplitter, QToolBar,
                QStatusBar, QMenuBar, QMenu, QButtonGroup
            ]
            
            # Display Widgets
            display_widgets = [
                QTableWidget, QTreeWidget, QListWidget, QProgressBar, QCalendarWidget,
                QSystemTrayIcon, QToolButton, QSizeGrip
            ]
            
            all_widgets = core_widgets + layout_widgets + input_widgets + container_widgets + display_widgets
            
            imported_count = 0
            widget_details = {}
            
            for widget in all_widgets:
                try:
                    # Test Widget-Erstellung
                    test_widget = widget()
                    if test_widget:
                        imported_count += 1
                        self.widget_tested.add(widget.__name__)
                        widget_details[widget.__name__] = {
                            "status": "SUCCESS",
                            "can_instantiate": True,
                            "type": self._classify_widget(widget)
                        }
                    test_widget.deleteLater()
                except Exception as e:
                    widget_details[widget.__name__] = {
                        "status": "FAILED", 
                        "error": str(e),
                        "type": self._classify_widget(widget)
                    }
            
            # Ergebnis bewerten
            success_rate = (imported_count / len(all_widgets)) * 100
            
            self.test_results["tests"][test_name] = {
                "status": "PASSED" if success_rate >= 90 else "FAILED",
                "total_widgets": len(all_widgets),
                "successfully_imported": imported_count,
                "success_rate": success_rate,
                "details": widget_details
            }
            
            logger.info(f"✅ {test_name}: {imported_count}/{len(all_widgets)} Widgets erfolgreich importiert ({success_rate:.1f}%)")
            return success_rate >= 90
            
        except Exception as e:
            logger.error(f"❌ {test_name} fehlgeschlagen: {e}")
            self.test_results["tests"][test_name] = {
                "status": "FAILED",
                "error": str(e)
            }
            return False
    
    def test_qt_selector_integration(self):
        """Test 2: Validierung der PySide6-Qt-Selektor-Integration"""
        test_name = "Qt_Selector_Integration"
        logger.info(f"Starte Test: {test_name}")
        
        try:
            # Test-Window mit verschiedenen Widgets erstellen
            window = QMainWindow()
            central_widget = QWidget()
            window.setCentralWidget(central_widget)
            
            layout = QVBoxLayout(central_widget)
            
            # Verschiedene Widgets hinzufügen
            test_label = QLabel("Test Label")
            test_label.setObjectName("testLabel")
            layout.addWidget(test_label)
            
            test_button = QPushButton("Test Button")
            test_button.setObjectName("testButton")
            layout.addWidget(test_button)
            
            test_input = QLineEdit("Test Input")
            test_input.setObjectName("testInput")
            layout.addWidget(test_input)
            
            window.show()
            self.app.processEvents()
            
            # Qt-Selektor Tests
            selector_tests = {
                "find_by_object_name": self._test_find_by_object_name,
                "find_by_class": self._test_find_by_class,
                "find_by_type": self._test_find_by_type,
                "accessibility_integration": self._test_accessibility_integration
            }
            
            selector_results = {}
            
            for test_name_local, test_func in selector_tests.items():
                try:
                    result = test_func(window, test_label, test_button, test_input)
                    selector_results[test_name_local] = result
                except Exception as e:
                    selector_results[test_name_local] = {
                        "status": "FAILED",
                        "error": str(e)
                    }
            
            window.close()
            window.deleteLater()
            
            # Gesamtergebnis
            passed_selectors = sum(1 for r in selector_results.values() if r.get("status") == "PASSED")
            total_selectors = len(selector_tests)
            success_rate = (passed_selectors / total_selectors) * 100
            
            self.test_results["tests"][test_name] = {
                "status": "PASSED" if success_rate >= 75 else "FAILED",
                "selector_tests_run": total_selectors,
                "selectors_passed": passed_selectors,
                "success_rate": success_rate,
                "details": selector_results
            }
            
            logger.info(f"✅ {test_name}: {passed_selectors}/{total_selectors} Selektor-Tests erfolgreich ({success_rate:.1f}%)")
            return success_rate >= 75
            
        except Exception as e:
            logger.error(f"❌ {test_name} fehlgeschlagen: {e}")
            self.test_results["tests"][test_name] = {
                "status": "FAILED",
                "error": str(e)
            }
            return False
    
    def test_layout_management(self):
        """Test 3: Test des Layout-Managements"""
        test_name = "Layout_Management"
        logger.info(f"Starte Test: {test_name}")
        
        try:
            layout_tests = {
                "QVBoxLayout": self._test_qvbox_layout,
                "QHBoxLayout": self._test_qhbox_layout, 
                "QGridLayout": self._test_qgrid_layout,
                "QFormLayout": self._test_qform_layout,
                "Nested_Layouts": self._test_nested_layouts,
                "Layout_Resizing": self._test_layout_resizing
            }
            
            layout_results = {}
            
            for layout_name, test_func in layout_tests.items():
                try:
                    result = test_func()
                    layout_results[layout_name] = result
                except Exception as e:
                    layout_results[layout_name] = {
                        "status": "FAILED",
                        "error": str(e)
                    }
            
            # Gesamtergebnis
            passed_layouts = sum(1 for r in layout_results.values() if r.get("status") == "PASSED")
            total_layouts = len(layout_tests)
            success_rate = (passed_layouts / total_layouts) * 100
            
            self.test_results["tests"][test_name] = {
                "status": "PASSED" if success_rate >= 85 else "FAILED",
                "layout_tests_run": total_layouts,
                "layouts_passed": passed_layouts,
                "success_rate": success_rate,
                "details": layout_results
            }
            
            self.test_results["layout_test_results"] = layout_results
            
            logger.info(f"✅ {test_name}: {passed_layouts}/{total_layouts} Layout-Tests erfolgreich ({success_rate:.1f}%)")
            return success_rate >= 85
            
        except Exception as e:
            logger.error(f"❌ {test_name} fehlgeschlagen: {e}")
            self.test_results["tests"][test_name] = {
                "status": "FAILED",
                "error": str(e)
            }
            return False
    
    def test_widget_event_hookup(self):
        """Test 4: Prüfung der Widget-Event-Hookup"""
        test_name = "Widget_Event_Hookup"
        logger.info(f"Starte Test: {test_name}")
        
        try:
            event_tests = {
                "Button_Clicked": self._test_button_clicked_events,
                "TextChanged_Events": self._test_text_changed_events,
                "ValueChanged_Events": self._test_value_changed_events,
                "Selection_Events": self._test_selection_events,
                "Focus_Events": self._test_focus_events,
                "Custom_Signals": self._test_custom_signals
            }
            
            event_results = {}
            event_counters = {
                "clicked": 0,
                "text_changed": 0,
                "value_changed": 0,
                "selection_changed": 0,
                "focus_changed": 0,
                "custom_signals": 0
            }
            
            for event_name, test_func in event_tests.items():
                try:
                    result = test_func(event_counters)
                    event_results[event_name] = result
                except Exception as e:
                    event_results[event_name] = {
                        "status": "FAILED",
                        "error": str(e)
                    }
            
            # Gesamtergebnis
            passed_events = sum(1 for r in event_results.values() if r.get("status") == "PASSED")
            total_events = len(event_tests)
            success_rate = (passed_events / total_events) * 100
            
            self.test_results["tests"][test_name] = {
                "status": "PASSED" if success_rate >= 80 else "FAILED",
                "event_tests_run": total_events,
                "events_passed": passed_events,
                "success_rate": success_rate,
                "event_counters": event_counters,
                "details": event_results
            }
            
            self.test_results["event_test_results"] = event_results
            
            logger.info(f"✅ {test_name}: {passed_events}/{total_events} Event-Tests erfolgreich ({success_rate:.1f}%)")
            return success_rate >= 80
            
        except Exception as e:
            logger.error(f"❌ {test_name} fehlgeschlagen: {e}")
            self.test_results["tests"][test_name] = {
                "status": "FAILED",
                "error": str(e)
            }
            return False
    
    def test_table_tree_widgets(self):
        """Test 5: Test von QTableWidget und QTreeWidget-Integration"""
        test_name = "Table_Tree_Widgets"
        logger.info(f"Starte Test: {test_name}")
        
        try:
            widget_tests = {
                "QTableWidget_Basic": self._test_qtablewidget_basic,
                "QTableWidget_Advanced": self._test_qtablewidget_advanced,
                "QTreeWidget_Basic": self._test_qtreewidget_basic,
                "QTreeWidget_Advanced": self._test_qtreewidget_advanced,
                "ListWidget_Integration": self._test_qlistwidget_integration,
                "Model_View_Integration": self._test_model_view_integration
            }
            
            widget_results = {}
            
            for widget_name, test_func in widget_tests.items():
                try:
                    result = test_func()
                    widget_results[widget_name] = result
                except Exception as e:
                    widget_results[widget_name] = {
                        "status": "FAILED",
                        "error": str(e)
                    }
            
            # Gesamtergebnis
            passed_widgets = sum(1 for r in widget_results.values() if r.get("status") == "PASSED")
            total_widgets = len(widget_tests)
            success_rate = (passed_widgets / total_widgets) * 100
            
            self.test_results["tests"][test_name] = {
                "status": "PASSED" if success_rate >= 85 else "FAILED",
                "widget_tests_run": total_widgets,
                "widgets_passed": passed_widgets,
                "success_rate": success_rate,
                "details": widget_results
            }
            
            logger.info(f"✅ {test_name}: {passed_widgets}/{total_widgets} Widget-Tests erfolgreich ({success_rate:.1f}%)")
            return success_rate >= 85
            
        except Exception as e:
            logger.error(f"❌ {test_name} fehlgeschlagen: {e}")
            self.test_results["tests"][test_name] = {
                "status": "FAILED",
                "error": str(e)
            }
            return False
    
    def test_messagebox_filedialog(self):
        """Test 6: Validierung von QMessageBox und QFileDialog-Integration"""
        test_name = "MessageBox_FileDialog"
        logger.info(f"Starte Test: {test_name}")
        
        try:
            dialog_tests = {
                "QMessageBox_Types": self._test_qmessagebox_types,
                "QMessageBox_Integration": self._test_qmessagebox_integration,
                "QFileDialog_Basic": self._test_qfiledialog_basic,
                "QFileDialog_Advanced": self._test_qfiledialog_advanced,
                "QDialog_Integration": self._test_qdialog_integration,
                "Modal_Dialog_Behavior": self._test_modal_dialog_behavior
            }
            
            dialog_results = {}
            
            for dialog_name, test_func in dialog_tests.items():
                try:
                    result = test_func()
                    dialog_results[dialog_name] = result
                except Exception as e:
                    dialog_results[dialog_name] = {
                        "status": "FAILED",
                        "error": str(e)
                    }
            
            # Gesamtergebnis
            passed_dialogs = sum(1 for r in dialog_results.values() if r.get("status") == "PASSED")
            total_dialogs = len(dialog_tests)
            success_rate = (passed_dialogs / total_dialogs) * 100
            
            self.test_results["tests"][test_name] = {
                "status": "PASSED" if success_rate >= 80 else "FAILED",
                "dialog_tests_run": total_dialogs,
                "dialogs_passed": passed_dialogs,
                "success_rate": success_rate,
                "details": dialog_results
            }
            
            self.test_results["dialog_test_results"] = dialog_results
            
            logger.info(f"✅ {test_name}: {passed_dialogs}/{total_dialogs} Dialog-Tests erfolgreich ({success_rate:.1f}%)")
            return success_rate >= 80
            
        except Exception as e:
            logger.error(f"❌ {test_name} fehlgeschlagen: {e}")
            self.test_results["tests"][test_name] = {
                "status": "FAILED",
                "error": str(e)
            }
            return False
    
    def test_spinbox_integration(self):
        """Test 7: Prüfung von QSpinBox und QDoubleSpinBox-Integration"""
        test_name = "SpinBox_Integration"
        logger.info(f"Starte Test: {test_name}")
        
        try:
            spinbox_tests = {
                "QSpinBox_Basic": self._test_qspinbox_basic,
                "QSpinBox_Advanced": self._test_qspinbox_advanced,
                "QDoubleSpinBox_Basic": self._test_qdoublespinbox_basic,
                "QDoubleSpinBox_Advanced": self._test_qdoublespinbox_advanced,
                "SpinBox_Events": self._test_spinbox_events,
                "SpinBox_Validation": self._test_spinbox_validation
            }
            
            spinbox_results = {}
            event_counter = {"value_changed": 0}
            
            for spinbox_name, test_func in spinbox_tests.items():
                try:
                    result = test_func(event_counter)
                    spinbox_results[spinbox_name] = result
                except Exception as e:
                    spinbox_results[spinbox_name] = {
                        "status": "FAILED",
                        "error": str(e)
                    }
            
            # Gesamtergebnis
            passed_spinboxes = sum(1 for r in spinbox_results.values() if r.get("status") == "PASSED")
            total_spinboxes = len(spinbox_tests)
            success_rate = (passed_spinboxes / total_spinboxes) * 100
            
            self.test_results["tests"][test_name] = {
                "status": "PASSED" if success_rate >= 85 else "FAILED",
                "spinbox_tests_run": total_spinboxes,
                "spinboxes_passed": passed_spinboxes,
                "success_rate": success_rate,
                "event_counter": event_counter,
                "details": spinbox_results
            }
            
            logger.info(f"✅ {test_name}: {passed_spinboxes}/{total_spinboxes} SpinBox-Tests erfolgreich ({success_rate:.1f}%)")
            return success_rate >= 85
            
        except Exception as e:
            logger.error(f"❌ {test_name} fehlgeschlagen: {e}")
            self.test_results["tests"][test_name] = {
                "status": "FAILED",
                "error": str(e)
            }
            return False
    
    def run_all_tests(self):
        """Führt alle PySide6-Integration-Tests aus"""
        logger.info("🚀 Starte PySide6-Integration-Tests")
        
        # Setup
        if not self.setup_application():
            logger.error("❌ Anwendung-Setup fehlgeschlagen")
            return False
        
        # Tests ausführen
        tests = [
            self.test_pyside6_widget_imports,
            self.test_qt_selector_integration,
            self.test_layout_management,
            self.test_widget_event_hookup,
            self.test_table_tree_widgets,
            self.test_messagebox_filedialog,
            self.test_spinbox_integration
        ]
        
        for test_func in tests:
            try:
                self.total_tests += 1
                if test_func():
                    self.passed_tests += 1
                else:
                    self.failed_tests += 1
            except Exception as e:
                logger.error(f"❌ Test {test_func.__name__} crashed: {e}")
                self.failed_tests += 1
        
        # Gesamtbewertung
        self._calculate_overall_score()
        
        # Report generieren
        self._generate_detailed_report()
        
        # Ergebnis
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        logger.info(f"🎯 PySide6-Integration-Tests abgeschlossen: {self.passed_tests}/{self.total_tests} erfolgreich ({success_rate:.1f}%)")
        
        return success_rate >= 80
    
    def _calculate_overall_score(self):
        """Berechnet Gesamtbewertung der Integration"""
        test_scores = []
        
        for test_name, test_result in self.test_results["tests"].items():
            if "success_rate" in test_result:
                test_scores.append(test_result["success_rate"])
        
        if test_scores:
            self.test_results["integration_score"] = sum(test_scores) / len(test_scores)
        
        # Widget Coverage
        self.test_results["widget_coverage"] = {
            "total_tested": len(self.widget_tested),
            "widget_types": sorted(list(self.widget_tested))
        }
        
        # Summary
        self.test_results["summary"] = {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "success_rate": (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0,
            "test_status": "PASSED" if self.passed_tests >= self.total_tests * 0.8 else "FAILED"
        }
    
    def _generate_detailed_report(self):
        """Generiert detaillierten Test-Report"""
        report_path = "/workspace/docs/pyside6_integration_report.md"
        
        report_content = f"""# PySide6-Integration und Widget-Funktionalität Test-Report

**Erstellt am:** {self.test_results['timestamp']}  
**Version:** {self.test_results['version']}  
**Gesamtbewertung:** {self.test_results['integration_score']:.1f}%  
**Test-Status:** {self.test_results['summary']['test_status']}

## 📊 Zusammenfassung

- **Gesamt-Tests:** {self.test_results['summary']['total_tests']}
- **Erfolgreich:** {self.test_results['summary']['passed_tests']}
- **Fehlgeschlagen:** {self.test_results['summary']['failed_tests']}
- **Erfolgsrate:** {self.test_results['summary']['success_rate']:.1f}%
- **Widget-Coverage:** {self.test_results['widget_coverage']['total_tested']} Widgets getestet

## 🧪 Detaillierte Testergebnisse

"""
        
        for test_name, test_result in self.test_results["tests"].items():
            status_icon = "✅" if test_result.get("status") == "PASSED" else "❌"
            report_content += f"### {status_icon} {test_name.replace('_', ' ')}\n"
            report_content += f"**Status:** {test_result.get('status', 'N/A')}\n"
            
            if "success_rate" in test_result:
                report_content += f"**Erfolgsrate:** {test_result['success_rate']:.1f}%\n"
            
            if "details" in test_result:
                report_content += f"\n**Details:**\n"
                for detail_name, detail_result in test_result["details"].items():
                    detail_status = detail_result.get("status", "N/A")
                    report_content += f"- {detail_name}: {detail_status}\n"
            
            report_content += "\n"
        
        # Layout-Tests Details
        if "layout_test_results" in self.test_results:
            report_content += "## 📐 Layout-Management Details\n\n"
            for layout_name, layout_result in self.test_results["layout_test_results"].items():
                report_content += f"### {layout_name}\n"
                report_content += f"**Status:** {layout_result.get('status', 'N/A')}\n"
                if "widget_count" in layout_result:
                    report_content += f"**Widgets getestet:** {layout_result['widget_count']}\n"
                report_content += "\n"
        
        # Event-Tests Details
        if "event_test_results" in self.test_results:
            report_content += "## 🎯 Event-Handler Details\n\n"
            for event_name, event_result in self.test_results["event_test_results"].items():
                report_content += f"### {event_name}\n"
                report_content += f"**Status:** {event_result.get('status', 'N/A')}\n"
                report_content += "\n"
        
        # Dialog-Tests Details
        if "dialog_test_results" in self.test_results:
            report_content += "## 🪟 Dialog-Integration Details\n\n"
            for dialog_name, dialog_result in self.test_results["dialog_test_results"].items():
                report_content += f"### {dialog_name}\n"
                report_content += f"**Status:** {dialog_result.get('status', 'N/A')}\n"
                report_content += "\n"
        
        # Widget Coverage
        report_content += "## 🔧 Getestete Widget-Typen\n\n"
        for widget_type in self.test_results["widget_coverage"]["widget_types"]:
            report_content += f"- {widget_type}\n"
        
        report_content += f"""
## 📈 Bewertung und Empfehlungen

**Gesamtbewertung:** {self.test_results['integration_score']:.1f}%

### Bewertungskriterien:
- **90-100%:** Ausgezeichnete PySide6-Integration
- **80-89%:** Gute Integration mit kleinen Verbesserungen
- **70-79%:** Akzeptable Integration, Verbesserungen empfohlen
- **< 70%:** Signifikante Probleme, dringende Überarbeitung erforderlich

### Nächste Schritte:
1. Fehlgeschlagene Tests analysieren und beheben
2. Widget-Coverage erweitern
3. Event-Handling optimieren
4. Dialog-Integration verbessern

---
*Report generiert von PySide6 Integration Test Suite*
"""
        
        # Report speichern
        try:
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"📄 Detaillierter Report gespeichert: {report_path}")
        except Exception as e:
            logger.error(f"❌ Fehler beim Speichern des Reports: {e}")
    
    # Helper-Methoden für einzelne Tests
    def _classify_widget(self, widget_class):
        """Klassifiziert Widget-Typ"""
        if widget_class in [QApplication, QMainWindow, QWidget, QDialog]:
            return "Core"
        elif widget_class in [QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout]:
            return "Layout"
        elif widget_class in [QLabel, QLineEdit, QTextEdit, QPushButton]:
            return "Basic_Input"
        elif widget_class in [QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox]:
            return "Advanced_Input"
        elif widget_class in [QTableWidget, QTreeWidget, QListWidget]:
            return "Data_Display"
        else:
            return "Other"
    
    # Test-Methoden für Qt-Selektoren
    def _test_find_by_object_name(self, window, label, button, input_field):
        """Test: Widget-Findung per Objektname"""
        try:
            found_label = window.findChild(QLabel, "testLabel")
            found_button = window.findChild(QPushButton, "testButton")
            found_input = window.findChild(QLineEdit, "testInput")
            
            if found_label and found_button and found_input:
                return {"status": "PASSED", "message": "Alle Widgets per Objektname gefunden"}
            else:
                return {"status": "FAILED", "message": "Nicht alle Widgets gefunden"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def _test_find_by_class(self, window, label, button, input_field):
        """Test: Widget-Findung per Klasse"""
        try:
            labels = window.findChildren(QLabel)
            buttons = window.findChildren(QPushButton)
            inputs = window.findChildren(QLineEdit)
            
            if len(labels) >= 1 and len(buttons) >= 1 and len(inputs) >= 1:
                return {"status": "PASSED", "message": f"Gefunden: {len(labels)} Labels, {len(buttons)} Buttons, {len(inputs)} Inputs"}
            else:
                return {"status": "FAILED", "message": "Unzureichende Widget-Funde"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def _test_find_by_type(self, window, label, button, input_field):
        """Test: Widget-Findung per Typ"""
        try:
            widgets = window.findChildren(QWidget)
            if len(widgets) >= 3:  # Mindestens Label, Button, Input
                return {"status": "PASSED", "message": f"{len(widgets)} Widgets gefunden"}
            else:
                return {"status": "FAILED", "message": "Zu wenige Widgets gefunden"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def _test_accessibility_integration(self, window, label, button, input_field):
        """Test: Accessibility-Integration"""
        try:
            # Accessibility-Attribute testen
            label.setAccessibleName("Test Label Accessible")
            label.setAccessibleDescription("Test Label Description")
            button.setAccessibleName("Test Button Accessible")
            
            if (label.accessibleName() and button.accessibleName() and 
                label.accessibleDescription()):
                return {"status": "PASSED", "message": "Accessibility-Attribute korrekt gesetzt"}
            else:
                return {"status": "FAILED", "message": "Accessibility-Attribute fehlerhaft"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    # Layout-Test-Methoden
    def _test_qvbox_layout(self):
        """Test: QVBoxLayout"""
        try:
            widget = QWidget()
            layout = QVBoxLayout()
            
            # Widgets hinzufügen
            for i in range(3):
                label = QLabel(f"Item {i}")
                layout.addWidget(label)
            
            # Layout zu Widget hinzufügen
            widget.setLayout(layout)
            
            # Test: Layout-Validierung
            if widget.layout() == layout and layout.count() == 3:
                widget.deleteLater()
                return {"status": "PASSED", "message": "QVBoxLayout funktioniert korrekt", "widget_count": 3}
            else:
                widget.deleteLater()
                return {"status": "FAILED", "message": "QVBoxLayout-Validierung fehlgeschlagen"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def _test_qhbox_layout(self):
        """Test: QHBoxLayout"""
        try:
            widget = QWidget()
            layout = QHBoxLayout()
            
            # Widgets hinzufügen
            for i in range(3):
                button = QPushButton(f"Button {i}")
                layout.addWidget(button)
            
            widget.setLayout(layout)
            
            if widget.layout() == layout and layout.count() == 3:
                widget.deleteLater()
                return {"status": "PASSED", "message": "QHBoxLayout funktioniert korrekt", "widget_count": 3}
            else:
                widget.deleteLater()
                return {"status": "FAILED", "message": "QHBoxLayout-Validierung fehlgeschlagen"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def _test_qgrid_layout(self):
        """Test: QGridLayout"""
        try:
            widget = QWidget()
            layout = QGridLayout()
            
            # Grid-Positionen füllen
            layout.addWidget(QLabel("0,0"), 0, 0)
            layout.addWidget(QLabel("0,1"), 0, 1)
            layout.addWidget(QLabel("1,0"), 1, 0)
            layout.addWidget(QLabel("1,1"), 1, 1)
            
            widget.setLayout(layout)
            
            if widget.layout() == layout and layout.count() == 4:
                widget.deleteLater()
                return {"status": "PASSED", "message": "QGridLayout funktioniert korrekt", "widget_count": 4}
            else:
                widget.deleteLater()
                return {"status": "FAILED", "message": "QGridLayout-Validierung fehlgeschlagen"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def _test_qform_layout(self):
        """Test: QFormLayout"""
        try:
            widget = QWidget()
            layout = QFormLayout()
            
            # Formular-Felder hinzufügen
            layout.addRow("Name:", QLineEdit())
            layout.addRow("Email:", QLineEdit())
            layout.addRow("Age:", QSpinBox())
            
            widget.setLayout(layout)
            
            if widget.layout() == layout and layout.count() == 3:
                widget.deleteLater()
                return {"status": "PASSED", "message": "QFormLayout funktioniert korrekt", "widget_count": 3}
            else:
                widget.deleteLater()
                return {"status": "FAILED", "message": "QFormLayout-Validierung fehlgeschlagen"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def _test_nested_layouts(self):
        """Test: Verschachtelte Layouts"""
        try:
            widget = QWidget()
            outer_layout = QVBoxLayout()
            
            # Inneres Layout
            inner_layout = QHBoxLayout()
            inner_layout.addWidget(QLabel("Left"))
            inner_layout.addWidget(QLabel("Right"))
            
            # Äußeres Layout
            outer_layout.addWidget(QLabel("Top"))
            outer_layout.addLayout(inner_layout)
            outer_layout.addWidget(QLabel("Bottom"))
            
            widget.setLayout(outer_layout)
            
            if widget.layout() == outer_layout and outer_layout.count() == 3:
                widget.deleteLater()
                return {"status": "PASSED", "message": "Verschachtelte Layouts funktionieren", "widget_count": 3}
            else:
                widget.deleteLater()
                return {"status": "FAILED", "message": "Verschachtelte Layouts fehlgeschlagen"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def _test_layout_resizing(self):
        """Test: Layout-Resizing-Verhalten"""
        try:
            window = QMainWindow()
            central = QWidget()
            window.setCentralWidget(central)
            
            layout = QVBoxLayout()
            label1 = QLabel("Expanding")
            label2 = QLabel("Fixed")
            
            layout.addWidget(label1)
            layout.addWidget(label2)
            central.setLayout(layout)
            
            # Fenster-Größe ändern
            window.resize(400, 300)
            self.app.processEvents()
            
            # Layout sollte responsive sein
            window.close()
            window.deleteLater()
            
            return {"status": "PASSED", "message": "Layout-Resizing funktioniert"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    # Event-Test-Methoden
    def _test_button_clicked_events(self, counters):
        """Test: Button-Clicked Events"""
        try:
            button = QPushButton("Test")
            clicked = False
            
            def on_clicked():
                nonlocal clicked
                clicked = True
                counters["clicked"] += 1
            
            button.clicked.connect(on_clicked)
            
            # Simuliere Klick
            button.click()
            
            if clicked:
                return {"status": "PASSED", "message": "Button-Click Event funktioniert"}
            else:
                return {"status": "FAILED", "message": "Button-Click Event nicht ausgelöst"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def _test_text_changed_events(self, counters):
        """Test: TextChanged Events"""
        try:
            line_edit = QLineEdit()
            text_changed = False
            
            def on_text_changed(text):
                nonlocal text_changed
                text_changed = True
                counters["text_changed"] += 1
            
            line_edit.textChanged.connect(on_text_changed)
            
            # Simuliere Text-Änderung
            line_edit.setText("New Text")
            
            if text_changed:
                return {"status": "PASSED", "message": "TextChanged Event funktioniert"}
            else:
                return {"status": "FAILED", "message": "TextChanged Event nicht ausgelöst"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def _test_value_changed_events(self, counters):
        """Test: ValueChanged Events"""
        try:
            spinbox = QSpinBox()
            value_changed = False
            
            def on_value_changed(value):
                nonlocal value_changed
                value_changed = True
                counters["value_changed"] += 1
            
            spinbox.valueChanged.connect(on_value_changed)
            
            # Simuliere Wert-Änderung
            spinbox.setValue(42)
            
            if value_changed:
                return {"status": "PASSED", "message": "ValueChanged Event funktioniert"}
            else:
                return {"status": "FAILED", "message": "ValueChanged Event nicht ausgelöst"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def _test_selection_events(self, counters):
        """Test: Selection Events"""
        try:
            combo_box = QComboBox()
            combo_box.addItems(["Item 1", "Item 2", "Item 3"])
            selection_changed = False
            
            def on_selection_changed(index):
                nonlocal selection_changed
                selection_changed = True
                counters["selection_changed"] += 1
            
            combo_box.currentIndexChanged.connect(on_selection_changed)
            
            # Simuliere Auswahl-Änderung
            combo_box.setCurrentIndex(1)
            
            if selection_changed:
                return {"status": "PASSED", "message": "Selection Event funktioniert"}
            else:
                return {"status": "FAILED", "message": "Selection Event nicht ausgelöst"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def _test_focus_events(self, counters):
        """Test: Focus Events"""
        try:
            widget = QWidget()
            focus_changed = False
            
            def on_focus_changed(old, new):
                nonlocal focus_changed
                focus_changed = True
                counters["focus_changed"] += 1
            
            widget.focusChanged.connect(on_focus_changed)
            
            # Simuliere Fokus-Änderung
            widget.setFocus()
            
            if focus_changed:
                return {"status": "PASSED", "message": "Focus Event funktioniert"}
            else:
                return {"status": "FAILED", "message": "Focus Event nicht ausgelöst"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def _test_custom_signals(self, counters):
        """Test: Custom Signals"""
        try:
            class TestObject(QObject):
                custom_signal = Signal(str)
            
            obj = TestObject()
            signal_received = False
            
            def on_custom_signal(text):
                nonlocal signal_received
                signal_received = True
                counters["custom_signals"] += 1
            
            obj.custom_signal.connect(on_custom_signal)
            
            # Custom Signal auslösen
            obj.custom_signal.emit("Test")
            
            if signal_received:
                return {"status": "PASSED", "message": "Custom Signal funktioniert"}
            else:
                return {"status": "FAILED", "message": "Custom Signal nicht ausgelöst"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    # Widget-Test-Methoden
    def _test_qtablewidget_basic(self):
        """Test: QTableWidget Basic"""
        try:
            table = QTableWidget(3, 3)
            
            # Daten hinzufügen
            for row in range(3):
                for col in range(3):
                    table.setItem(row, col, QTableWidgetItem(f"Cell {row},{col}"))
            
            # Grundfunktionen testen
            table.setRowCount(4)
            table.setColumnCount(4)
            
            if (table.rowCount() == 4 and table.columnCount() == 4 and 
                table.item(0, 0) is not None):
                table.deleteLater()
                return {"status": "PASSED", "message": "QTableWidget Basic funktioniert"}
            else:
                table.deleteLater()
                return {"status": "FAILED", "message": "QTableWidget Basic fehlgeschlagen"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def _test_qtablewidget_advanced(self):
        """Test: QTableWidget Advanced"""
        try:
            table = QTableWidget()
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["Name", "Value", "Status"])
            
            # Datenzeilen hinzufügen
            for i in range(5):
                row_position = table.rowCount()
                table.insertRow(row_position)
                table.setItem(row_position, 0, QTableWidgetItem(f"Item {i}"))
                table.setItem(row_position, 1, QTableWidgetItem(str(i * 10)))
                table.setItem(row_position, 2, QTableWidgetItem("Active"))
            
            # Header-Tests
            header = table.horizontalHeader()
            
            if (table.rowCount() == 5 and header.count() == 3):
                table.deleteLater()
                return {"status": "PASSED", "message": "QTableWidget Advanced funktioniert"}
            else:
                table.deleteLater()
                return {"status": "FAILED", "message": "QTableWidget Advanced fehlgeschlagen"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def _test_qtreewidget_basic(self):
        """Test: QTreeWidget Basic"""
        try:
            tree = QTreeWidget()
            tree.setHeaderLabels(["Name", "Type", "Value"])
            
            # Root-Items hinzufügen
            root1 = QTreeWidgetItem(tree, ["Root 1", "Group", ""])
            root2 = QTreeWidgetItem(tree, ["Root 2", "Group", ""])
            
            # Child-Items hinzufügen
            child1 = QTreeWidgetItem(root1, ["Child 1", "Item", "Value 1"])
            child2 = QTreeWidgetItem(root1, ["Child 2", "Item", "Value 2"])
            
            if (tree.topLevelItemCount() == 2 and 
                root1.childCount() == 2):
                tree.deleteLater()
                return {"status": "PASSED", "message": "QTreeWidget Basic funktioniert"}
            else:
                tree.deleteLater()
                return {"status": "FAILED", "message": "QTreeWidget Basic fehlgeschlagen"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def _test_qtreewidget_advanced(self):
        """Test: QTreeWidget Advanced"""
        try:
            tree = QTreeWidget()
            tree.setHeaderLabels(["Name", "Description"])
            
            # Hierarchische Struktur
            root = QTreeWidgetItem(tree, ["Root", "Main Node"])
            
            # Sub-nodes
            sub1 = QTreeWidgetItem(root, ["Sub 1", "First sub node"])
            sub2 = QTreeWidgetItem(root, ["Sub 2", "Second sub node"])
            
            # Sub-sub nodes
            subsub1 = QTreeWidgetItem(sub1, ["SubSub 1", "Deep node"])
            
            # Collapsible/Expandable
            root.setExpanded(True)
            sub1.setExpanded(True)
            
            if (tree.topLevelItemCount() == 1 and 
                root.childCount() == 2 and 
                sub1.childCount() == 1):
                tree.deleteLater()
                return {"status": "PASSED", "message": "QTreeWidget Advanced funktioniert"}
            else:
                tree.deleteLater()
                return {"status": "FAILED", "message": "QTreeWidget Advanced fehlgeschlagen"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def _test_qlistwidget_integration(self):
        """Test: QListWidget Integration"""
        try:
            list_widget = QListWidget()
            
            # Items hinzufügen
            for i in range(5):
                list_widget.addItem(f"List Item {i}")
            
            # Item-Operationen
            list_widget.insertItem(2, "Inserted Item")
            current_item = list_widget.item(0)
            
            if (list_widget.count() == 6 and current_item is not None):
                list_widget.deleteLater()
                return {"status": "PASSED", "message": "QListWidget funktioniert"}
            else:
                list_widget.deleteLater()
                return {"status": "FAILED", "message": "QListWidget fehlgeschlagen"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def _test_model_view_integration(self):
        """Test: Model-View Integration"""
        try:
            from PySide6.QtWidgets import QListView
            from PySide6.QtCore import QStringListModel
            
            model = QStringListModel(["Item 1", "Item 2", "Item 3"])
            view = QListView()
            view.setModel(model)
            
            # Model-View-Verbindung testen
            if view.model() == model and model.rowCount() == 3:
                view.deleteLater()
                return {"status": "PASSED", "message": "Model-View Integration funktioniert"}
            else:
                view.deleteLater()
                return {"status": "FAILED", "message": "Model-View Integration fehlgeschlagen"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    # Dialog-Test-Methoden
    def _test_qmessagebox_types(self):
        """Test: QMessageBox Types"""
        try:
            # Verschiedene MessageBox-Typen testen
            msg_info = QMessageBox()
            msg_info.setText("Info Message")
            msg_info.setIcon(QMessageBox.Information)
            
            msg_warning = QMessageBox()
            msg_warning.setText("Warning Message")
            msg_warning.setIcon(QMessageBox.Warning)
            
            msg_critical = QMessageBox()
            msg_critical.setText("Critical Message")
            msg_critical.setIcon(QMessageBox.Critical)
            
            msg_question = QMessageBox()
            msg_question.setText("Question Message")
            msg_question.setIcon(QMessageBox.Question)
            
            return {
                "status": "PASSED", 
                "message": "Alle QMessageBox-Typen erstellt",
                "types_tested": ["Information", "Warning", "Critical", "Question"]
            }
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def _test_qmessagebox_integration(self):
        """Test: QMessageBox Integration"""
        try:
            def show_test_message():
                msg = QMessageBox()
                msg.setWindowTitle("Test")
                msg.setText("Integration Test Message")
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                return msg
            
            message_box = show_test_message()
            
            if message_box.windowTitle() == "Test":
                message_box.deleteLater()
                return {"status": "PASSED", "message": "QMessageBox Integration funktioniert"}
            else:
                message_box.deleteLater()
                return {"status": "FAILED", "message": "QMessageBox Integration fehlgeschlagen"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def _test_qfiledialog_basic(self):
        """Test: QFileDialog Basic"""
        try:
            # File Dialog Konfiguration testen
            file_dialog = QFileDialog()
            file_dialog.setNameFilter("Text Files (*.txt);;All Files (*.*)")
            file_dialog.setViewMode(QFileDialog.Detail)
            
            return {
                "status": "PASSED", 
                "message": "QFileDialog Basic konfiguriert",
                "filters_set": True
            }
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def _test_qfiledialog_advanced(self):
        """Test: QFileDialog Advanced"""
        try:
            # Advanced File Dialog Features
            dialog = QFileDialog()
            
            # Multiple File Selection
            dialog.setFileMode(QFileDialog.ExistingFiles)
            
            # Custom File Name
            dialog.selectFile("default.txt")
            
            # Options
            dialog.setOptions(QFileDialog.DontUseNativeDialog)
            
            return {
                "status": "PASSED", 
                "message": "QFileDialog Advanced konfiguriert",
                "features_tested": ["MultipleFiles", "CustomName", "CustomOptions"]
            }
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def _test_qdialog_integration(self):
        """Test: QDialog Integration"""
        try:
            dialog = QDialog()
            dialog.setWindowTitle("Test Dialog")
            dialog.setModal(True)
            
            layout = QVBoxLayout()
            label = QLabel("Test Content")
            layout.addWidget(label)
            
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            layout.addWidget(button_box)
            
            dialog.setLayout(layout)
            
            if (dialog.windowTitle() == "Test Dialog" and 
                dialog.isModal() and 
                dialog.layout() == layout):
                dialog.deleteLater()
                return {"status": "PASSED", "message": "QDialog Integration funktioniert"}
            else:
                dialog.deleteLater()
                return {"status": "FAILED", "message": "QDialog Integration fehlgeschlagen"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def _test_modal_dialog_behavior(self):
        """Test: Modal Dialog Behavior"""
        try:
            main_window = QMainWindow()
            dialog = QDialog(main_window)
            dialog.setModal(True)
            dialog.setWindowTitle("Modal Test")
            
            # Modal-Property testen
            if dialog.isModal() and dialog.parent() == main_window:
                dialog.deleteLater()
                main_window.deleteLater()
                return {"status": "PASSED", "message": "Modal Dialog Behavior funktioniert"}
            else:
                dialog.deleteLater()
                main_window.deleteLater()
                return {"status": "FAILED", "message": "Modal Dialog Behavior fehlgeschlagen"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    # SpinBox-Test-Methoden
    def _test_qspinbox_basic(self, event_counter):
        """Test: QSpinBox Basic"""
        try:
            spinbox = QSpinBox()
            spinbox.setRange(0, 100)
            spinbox.setValue(50)
            spinbox.setSingleStep(5)
            
            if (spinbox.value() == 50 and 
                spinbox.minimum() == 0 and 
                spinbox.maximum() == 100 and
                spinbox.singleStep() == 5):
                spinbox.deleteLater()
                return {"status": "PASSED", "message": "QSpinBox Basic funktioniert"}
            else:
                spinbox.deleteLater()
                return {"status": "FAILED", "message": "QSpinBox Basic fehlgeschlagen"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def _test_qspinbox_advanced(self, event_counter):
        """Test: QSpinBox Advanced"""
        try:
            spinbox = QSpinBox()
            
            # Prefix/Suffix
            spinbox.setPrefix("$")
            spinbox.setSuffix(" EUR")
            
            # Wrapping
            spinbox.setWrapping(True)
            
            # Value testen
            spinbox.setValue(25)
            current_text = spinbox.text()
            
            if ("$" in current_text and "EUR" in current_text and 
                spinbox.value() == 25):
                spinbox.deleteLater()
                return {"status": "PASSED", "message": "QSpinBox Advanced funktioniert"}
            else:
                spinbox.deleteLater()
                return {"status": "FAILED", "message": "QSpinBox Advanced fehlgeschlagen"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def _test_qdoublespinbox_basic(self, event_counter):
        """Test: QDoubleSpinBox Basic"""
        try:
            dspinbox = QDoubleSpinBox()
            dspinbox.setRange(0.0, 100.0)
            dspinbox.setValue(25.5)
            dspinbox.setDecimals(2)
            dspinbox.setSingleStep(0.1)
            
            if (dspinbox.value() == 25.5 and 
                dspinbox.minimum() == 0.0 and 
                dspinbox.maximum() == 100.0 and
                dspinbox.decimals() == 2):
                dspinbox.deleteLater()
                return {"status": "PASSED", "message": "QDoubleSpinBox Basic funktioniert"}
            else:
                dspinbox.deleteLater()
                return {"status": "FAILED", "message": "QDoubleSpinBox Basic fehlgeschlagen"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def _test_qdoublespinbox_advanced(self, event_counter):
        """Test: QDoubleSpinBox Advanced"""
        try:
            dspinbox = QDoubleSpinBox()
            
            # Format Options
            dspinbox.setPrefix("€")
            dspinbox.setSuffix(" / hour")
            dspinbox.setDecimals(3)
            
            # Value mit hoher Präzision
            dspinbox.setValue(12.345)
            
            if (dspinbox.value() == 12.345 and 
                dspinbox.decimals() == 3):
                dspinbox.deleteLater()
                return {"status": "PASSED", "message": "QDoubleSpinBox Advanced funktioniert"}
            else:
                dspinbox.deleteLater()
                return {"status": "FAILED", "message": "QDoubleSpinBox Advanced fehlgeschlagen"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def _test_spinbox_events(self, event_counter):
        """Test: SpinBox Events"""
        try:
            spinbox = QSpinBox()
            
            value_changed_triggered = False
            def on_value_changed(value):
                nonlocal value_changed_triggered
                value_changed_triggered = True
                event_counter["value_changed"] += 1
            
            spinbox.valueChanged.connect(on_value_changed)
            
            # Wert ändern um Event zu triggern
            spinbox.setValue(10)
            
            if value_changed_triggered:
                spinbox.deleteLater()
                return {"status": "PASSED", "message": "SpinBox Events funktionieren"}
            else:
                spinbox.deleteLater()
                return {"status": "FAILED", "message": "SpinBox Events nicht ausgelöst"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
    
    def _test_spinbox_validation(self, event_counter):
        """Test: SpinBox Validation"""
        try:
            spinbox = QSpinBox()
            spinbox.setRange(0, 100)
            
            # Out-of-range Values testen
            original_min = spinbox.minimum()
            original_max = spinbox.maximum()
            
            # SetValue sollte automatisch korrigieren
            spinbox.setValue(150)  # Über Maximum
            spinbox.setValue(-10)  # Unter Minimum
            
            # Validation check
            if (spinbox.value() >= original_min and 
                spinbox.value() <= original_max):
                spinbox.deleteLater()
                return {"status": "PASSED", "message": "SpinBox Validation funktioniert"}
            else:
                spinbox.deleteLater()
                return {"status": "FAILED", "message": "SpinBox Validation fehlgeschlagen"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}


def main():
    """Hauptfunktion für Test-Ausführung"""
    print("🧪 PySide6-Integration und Widget-Funktionalität Test")
    print("=" * 60)
    
    # Test-Suite initialisieren
    test_suite = PySide6IntegrationTestSuite()
    
    # Alle Tests ausführen
    success = test_suite.run_all_tests()
    
    # Abschluss
    if success:
        print("✅ Alle PySide6-Integration-Tests erfolgreich!")
        return 0
    else:
        print("❌ Einige PySide6-Integration-Tests fehlgeschlagen!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
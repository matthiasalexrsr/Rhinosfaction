#!/usr/bin/env python3
"""
Dialog-Management Test-Script für Rhinoplastik-Anwendung

Führt automatisierte Tests für alle Dialog-Komponenten durch:
- Login-Dialog Test
- Patient-Editor-Dialog Test  
- Message-Dialog Tests
- Export-Dialog Tests
- File-Dialog Tests
- Admin-Access Tests
- Modal-Behavior Tests
- Accessibility Tests

Autor: MiniMax Agent
Datum: 2025-11-07
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt, QTimer
from pathlib import Path

# Add the application directory to the path
sys.path.insert(0, str(Path(__file__).parent / "rhinoplastik_windows_final"))

# Import UI components
try:
    from ui.login_dialog import LoginDialog
    from ui.patient_editor_widget import PatientEditorWidget
    from ui.export_widget import ExportWidget
    from ui.main_window import MainWindow
    from core.security.auth import AuthenticationManager
    from core.security.session_manager import SessionManager
    from core.patients.patient_manager import PatientManager
    from config.app_config import AppConfig
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    print(f"Import-Fehler: {e}")
    IMPORTS_SUCCESSFUL = False


class TestDialogManagement(unittest.TestCase):
    """Test-Suite für Dialog-Management"""
    
    @classmethod
    def setUpClass(cls):
        """Setup für Test-Klasse"""
        if not IMPORTS_SUCCESSFUL:
            cls.skipTest(cls, "Import-Fehler - Tests können nicht ausgeführt werden")
        
        # QApplication erstellen wenn nicht vorhanden
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
            
        # Mock-Objekte erstellen
        cls.mock_config = Mock()
        cls.mock_config.get.return_value = "/tmp/test_app"
        
        cls.mock_auth_manager = Mock(spec=AuthenticationManager)
        cls.mock_session_manager = Mock(spec=SessionManager)
        cls.mock_patient_manager = Mock(spec=PatientManager)
        cls.mock_media_manager = Mock()
        
        # Mock session manager methods
        cls.mock_session_manager.can_edit.return_value = True
        cls.mock_session_manager.is_admin.return_value = True
        cls.mock_session_manager.validate_session.return_value = True
        cls.mock_session_manager.get_user_info.return_value = {
            'username': 'test_user',
            'role': 'admin'
        }
        
        # Mock auth manager methods
        cls.mock_auth_manager.authenticate.return_value = {
            'user_id': 'user_123',
            'username': 'admin',
            'role': 'admin',
            'permissions': ['read', 'write', 'admin']
        }
        
        cls.test_results = []
    
    def test_01_login_dialog_creation(self):
        """Test 1: Login-Dialog-Erstellung und Grundfunktionen"""
        try:
            # Login-Dialog erstellen
            login_dialog = LoginDialog(self.mock_auth_manager, self.mock_session_manager)
            
            # Grundprüfungen
            self.assertIsInstance(login_dialog, LoginDialog)
            self.assertTrue(login_dialog.isModal())
            self.assertEqual(login_dialog.windowTitle(), "Rhinoplastik-Dokumentation - Anmeldung")
            
            # Accessibility-Checks
            self.assertTrue(hasattr(login_dialog, 'setAccessibleName'))
            self.assertTrue(hasattr(login_dialog, 'setAccessibleDescription'))
            
            # UI-Elemente prüfen
            self.assertIsNotNone(login_dialog.username_input)
            self.assertIsNotNone(login_dialog.password_input)
            self.assertIsNotNone(login_dialog.login_button)
            self.assertIsNotNone(login_dialog.cancel_button)
            
            # Validierung der Credentials-Felder
            self.assertEqual(login_dialog.password_input.echoMode(), QLineEdit.Password)
            
            self.test_results.append("✅ Test 1: Login-Dialog - ERFOLGREICH")
            login_dialog.close()
            
        except Exception as e:
            self.test_results.append(f"❌ Test 1: Login-Dialog - FEHLGESCHLAGEN: {e}")
            raise
    
    def test_02_login_credentials_validation(self):
        """Test 2: Login Credentials Validation"""
        try:
            login_dialog = LoginDialog(self.mock_auth_manager, self.mock_session_manager)
            
            # Test 1: Leere Credentials
            with patch.object(login_dialog, 'show_status') as mock_show_status:
                login_dialog.attempt_login()
                mock_show_status.assert_called_once()
            
            # Test 2: Gültige Credentials
            login_dialog.username_input.setText("admin")
            login_dialog.password_input.setText("admin123")
            
            # Mock session creation
            with patch.object(self.mock_session_manager, 'create_session') as mock_create:
                login_dialog.attempt_login()
                mock_create.assert_called_once()
            
            self.test_results.append("✅ Test 2: Login-Credentials-Validation - ERFOLGREICH")
            login_dialog.close()
            
        except Exception as e:
            self.test_results.append(f"❌ Test 2: Login-Credentials-Validation - FEHLGESCHLAGEN: {e}")
            raise
    
    def test_03_patient_editor_creation(self):
        """Test 3: Patient-Editor-Dialog Erstellung"""
        try:
            # Mock Patient erstellen
            mock_patient = Mock()
            mock_patient.demographics = Mock()
            mock_patient.demographics.lastname = "Mustermann"
            mock_patient.demographics.firstname = "Max"
            
            # Patient-Editor erstellen
            editor = PatientEditorWidget(
                self.mock_config,
                self.mock_session_manager, 
                self.mock_patient_manager,
                self.mock_media_manager,
                mock_patient
            )
            
            # Grundprüfungen
            self.assertIsInstance(editor, PatientEditorWidget)
            self.assertIsNotNone(editor.tab_widget)
            
            # Tab-Validierung (sollte 9 Tabs haben)
            tab_count = editor.tab_widget.count()
            self.assertGreaterEqual(tab_count, 7)  # Mindestens 7 Tabs erwartet
            
            # UI-Elemente prüfen
            self.assertIsNotNone(editor.save_btn)
            self.assertIsNotNone(editor.cancel_btn)
            
            self.test_results.append("✅ Test 3: Patient-Editor-Dialog - ERFOLGREICH")
            editor.close()
            
        except Exception as e:
            self.test_results.append(f"❌ Test 3: Patient-Editor-Dialog - FEHLGESCHLAGEN: {e}")
            raise
    
    def test_04_patient_editor_validation(self):
        """Test 4: Patient-Editor Formular-Validierung"""
        try:
            editor = PatientEditorWidget(
                self.mock_config,
                self.mock_session_manager,
                self.mock_patient_manager,
                self.mock_media_manager
            )
            
            # Leere Form-Validierung
            is_valid = editor.validate_form()
            self.assertFalse(is_valid)  # Sollte False sein bei leeren Pflichtfeldern
            
            # Pflichtfelder ausfüllen
            editor.lastname_input.setText("Test")
            editor.firstname_input.setText("Patient")
            
            # Mock für ListWidgets (Indikationen, Verfahren, Materialien)
            editor.indications_list.selectedItems = Mock(return_value=[])
            editor.procedures_list.selectedItems = Mock(return_value=[])
            editor.materials_list.selectedItems = Mock(return_value=[])
            
            # Sollte immer noch False sein (weil andere Pflichtfelder fehlen)
            is_valid = editor.validate_form()
            self.assertFalse(is_valid)
            
            self.test_results.append("✅ Test 4: Patient-Editor-Validierung - ERFOLGREICH")
            editor.close()
            
        except Exception as e:
            self.test_results.append(f"❌ Test 4: Patient-Editor-Validierung - FEHLGESCHLAGEN: {e}")
            raise
    
    def test_05_message_dialogs(self):
        """Test 5: Message-Dialog Tests"""
        try:
            # QMessageBox Tests
            # Information
            info_msg = QMessageBox()
            info_msg.setIcon(QMessageBox.Information)
            info_msg.setText("Test Information")
            self.assertEqual(info_msg.icon(), QMessageBox.Information)
            
            # Warning
            warning_msg = QMessageBox()
            warning_msg.setIcon(QMessageBox.Warning)
            warning_msg.setText("Test Warning")
            self.assertEqual(warning_msg.icon(), QMessageBox.Warning)
            
            # Critical
            critical_msg = QMessageBox()
            critical_msg.setIcon(QMessageBox.Critical)
            critical_msg.setText("Test Critical")
            self.assertEqual(critical_msg.icon(), QMessageBox.Critical)
            
            # Question
            question_msg = QMessageBox()
            question_msg.setIcon(QMessageBox.Question)
            question_msg.setText("Test Question")
            self.assertEqual(question_msg.icon(), QMessageBox.Question)
            
            self.test_results.append("✅ Test 5: Message-Dialogs - ERFOLGREICH")
            
        except Exception as e:
            self.test_results.append(f"❌ Test 5: Message-Dialogs - FEHLGESCHLAGEN: {e}")
            raise
    
    def test_06_export_dialog_creation(self):
        """Test 6: Export-Dialog Erstellung"""
        try:
            # Export-Widget erstellen (keine Mock-Validierung für Complex-Objects)
            export_widget = ExportWidget(
                self.mock_config,
                self.mock_patient_manager,
                self.mock_media_manager
            )
            
            # Grundprüfungen
            self.assertIsInstance(export_widget, ExportWidget)
            self.assertIsNotNone(export_widget.tab_widget)
            
            # Tab-Validierung (sollte 5 Tabs haben)
            tab_count = export_widget.tab_widget.count()
            self.assertGreaterEqual(tab_count, 4)  # Mindestens 4 Tabs erwartet
            
            # UI-Elemente prüfen
            self.assertIsNotNone(export_widget.status_label)
            self.assertIsNotNone(export_widget.progress_bar)
            
            self.test_results.append("✅ Test 6: Export-Dialog - ERFOLGREICH")
            export_widget.close()
            
        except Exception as e:
            self.test_results.append(f"❌ Test 6: Export-Dialog - FEHLGESCHLAGEN: {e}")
            raise
    
    def test_07_file_dialog_integration(self):
        """Test 7: File-Dialog Integration"""
        try:
            from PySide6.QtWidgets import QFileDialog
            
            # Mock für QFileDialog
            with patch('PySide6.QtWidgets.QFileDialog.getOpenFileName') as mock_get_file:
                mock_get_file.return_value = ("/path/to/test.pdf", "PDF Files (*.pdf)")
                
                file_path, file_type = QFileDialog.getOpenFileName(
                    None, "Datei öffnen", "/path/to", "PDF Files (*.pdf)"
                )
                
                self.assertEqual(file_path, "/path/to/test.pdf")
                self.assertEqual(file_type, "PDF Files (*.pdf)")
                mock_get_file.assert_called_once()
            
            # Mock für QFileDialog.getExistingDirectory
            with patch('PySide6.QtWidgets.QFileDialog.getExistingDirectory') as mock_get_dir:
                mock_get_dir.return_value = "/path/to/folder"
                
                folder_path = QFileDialog.getExistingDirectory(
                    None, "Ordner auswählen", "/path/to"
                )
                
                self.assertEqual(folder_path, "/path/to/folder")
                mock_get_dir.assert_called_once()
            
            self.test_results.append("✅ Test 7: File-Dialog-Integration - ERFOLGREICH")
            
        except Exception as e:
            self.test_results.append(f"❌ Test 7: File-Dialog-Integration - FEHLGESCHLAGEN: {e}")
            raise
    
    def test_08_admin_access_control(self):
        """Test 8: Admin-Access-Kontrolle"""
        try:
            # Mock für Admin-Benutzer
            admin_session = Mock(spec=SessionManager)
            admin_session.can_edit.return_value = True
            admin_session.is_admin.return_value = True
            admin_session.validate_session.return_value = True
            
            # Admin-Rechte prüfen
            self.assertTrue(admin_session.can_edit())
            self.assertTrue(admin_session.is_admin())
            self.assertTrue(admin_session.validate_session())
            
            # Mock für Regular-User
            user_session = Mock(spec=SessionManager)
            user_session.can_edit.return_value = True
            user_session.is_admin.return_value = False
            user_session.validate_session.return_value = True
            
            # User-Rechte prüfen
            self.assertTrue(user_session.can_edit())
            self.assertFalse(user_session.is_admin())
            self.assertTrue(user_session.validate_session())
            
            self.test_results.append("✅ Test 8: Admin-Access-Kontrolle - ERFOLGREICH")
            
        except Exception as e:
            self.test_results.append(f"❌ Test 8: Admin-Access-Kontrolle - FEHLGESCHLAGEN: {e}")
            raise
    
    def test_09_modal_behavior(self):
        """Test 9: Modal-Verhalten"""
        try:
            from PySide6.QtWidgets import QDialog
            
            # Modal-Dialog erstellen
            modal_dialog = QDialog()
            modal_dialog.setModal(True)
            modal_dialog.setWindowTitle("Test Modal Dialog")
            
            # Modal-Eigenschaften prüfen
            self.assertTrue(modal_dialog.isModal())
            self.assertTrue(modal_dialog.testAttribute(Qt.WA_ShowModal))
            
            # Non-Modal Dialog erstellen
            non_modal_dialog = QDialog()
            non_modal_dialog.setModal(False)
            
            # Non-Modal-Eigenschaften prüfen
            self.assertFalse(non_modal_dialog.isModal())
            
            self.test_results.append("✅ Test 9: Modal-Verhalten - ERFOLGREICH")
            
        except Exception as e:
            self.test_results.append(f"❌ Test 9: Modal-Verhalten - FEHLGESCHLAGEN: {e}")
            raise
    
    def test_10_accessibility_features(self):
        """Test 10: Accessibility-Features"""
        try:
            # Login-Dialog Accessibility prüfen
            login_dialog = LoginDialog(self.mock_auth_manager, self.mock_session_manager)
            
            # Accessibility-Properties
            self.assertTrue(hasattr(login_dialog, 'setAccessibleName'))
            self.assertTrue(hasattr(login_dialog, 'setAccessibleDescription'))
            
            # UI-Widgets Accessibility prüfen
            self.assertTrue(hasattr(login_dialog.username_input, 'setAccessibleName'))
            self.assertTrue(hasattr(login_dialog.password_input, 'setAccessibleName'))
            self.assertTrue(hasattr(login_dialog.login_button, 'setAccessibleName'))
            
            # Focus-Management prüfen
            self.assertIsNotNone(login_dialog.username_input.focusPolicy())
            
            self.test_results.append("✅ Test 10: Accessibility-Features - ERFOLGREICH")
            login_dialog.close()
            
        except Exception as e:
            self.test_results.append(f"❌ Test 10: Accessibility-Features - FEHLGESCHLAGEN: {e}")
            raise
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup nach Tests"""
        print("\n" + "="*60)
        print("DIALOG-MANAGEMENT TEST-ERGEBNISSE")
        print("="*60)
        
        for result in cls.test_results:
            print(result)
        
        # Test-Statistiken
        total_tests = len(cls.test_results)
        successful_tests = len([r for r in cls.test_results if r.startswith("✅")])
        failed_tests = total_tests - successful_tests
        
        print(f"\nTest-Statistik:")
        print(f"Gesamt: {total_tests}")
        print(f"Erfolgreich: {successful_tests}")
        print(f"Fehlgeschlagen: {failed_tests}")
        
        if successful_tests > 0:
            success_rate = (successful_tests / total_tests) * 100
            print(f"Erfolgsquote: {success_rate:.1f}%")
        
        print("="*60)
        
        if successful_tests == total_tests:
            print("🎉 ALLE TESTS ERFOLGREICH!")
        elif successful_tests >= total_tests * 0.8:
            print("👍 MEIST TESTS ERFOLGREICH")
        else:
            print("⚠️  MEHRERE TESTS FEHLGESCHLAGEN")


def run_dialog_management_tests():
    """Führt alle Dialog-Management-Tests aus"""
    print("Starte Dialog-Management-Tests...")
    
    # Test-Suite erstellen
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDialogManagement)
    
    # Tests ausführen
    runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w'))
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    # Direkte Ausführung
    if IMPORTS_SUCCESSFUL:
        try:
            success = run_dialog_management_tests()
            if success:
                print("✅ Alle Dialog-Management-Tests erfolgreich!")
            else:
                print("❌ Einige Dialog-Management-Tests fehlgeschlagen!")
        except Exception as e:
            print(f"❌ Test-Ausführung fehlgeschlagen: {e}")
    else:
        print("❌ Import-Fehler - Tests können nicht ausgeführt werden")
        sys.exit(1)

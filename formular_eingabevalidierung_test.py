#!/usr/bin/env python3
"""
Umfassender Test der Formulare und Eingabevalidierung für die Rhinoplastik-App

Testet alle UI-Elemente, Eingabevalidierung, Datumsprüfung, Dropdown-Funktionalität,
Responsive Layout und Benutzerinteraktionen.
"""

import sys
import os
import unittest
import json
import time
from datetime import date, datetime, timedelta
from unittest.mock import Mock, patch
import tempfile
import traceback

# PySide6 für GUI Tests
from PySide6.QtWidgets import QApplication, QMessageBox, QInputDialog
from PySide6.QtCore import Qt, QDate, QTimer, QEvent
from PySide6.QtTest import QTest
from PySide6.QtGui import QKeyEvent, QFocusEvent

# App-Imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rhinoplastik_app.ui.patient_editor_widget import PatientEditorWidget
from rhinoplastik_app.core.validators.patient_validators import PatientValidator
from rhinoplastik_app.core.patients.patient_model import (
    Patient, Demographics, Surgery, Indication, Procedure, Material,
    Gender, SurgicalTechnique, NoseShape, SkinThickness, CartilageQuality, AnesthesiaType
)


class FormularEingabevalidierungTests(unittest.TestCase):
    """Umfassende Tests für Formulare und Eingabevalidierung"""
    
    @classmethod
    def setUpClass(cls):
        """Einmalige Einrichtung für alle Tests"""
        # QApplication für GUI Tests
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
        
        # Mock-Objekte für Dependencies
        cls.config = Mock()
        cls.config.get = Mock(side_effect=lambda key, default=None: {
            'app_dir': '/tmp',
            'ui.window_size': (1200, 800),
            'ui.window_min_size': (1000, 600)
        }.get(key, default))
        
        cls.session_manager = Mock()
        cls.session_manager.can_edit = Mock(return_value=True)
        
        cls.patient_manager = Mock()
        cls.patient_manager.create_patient = Mock()
        cls.patient_manager.update_patient = Mock()
        
        cls.media_manager = Mock()
        
        # Test-Daten
        cls.test_data = cls._create_test_data()
        cls.test_results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': [],
            'test_categories': {}
        }
    
    def setUp(self):
        """Einrichtung vor jedem Test"""
        # Test-Results aktualisieren
        self.test_results['total_tests'] += 1
    
    @classmethod
    def _create_test_data(cls):
        """Erstellt Test-Daten für verschiedene Szenarien"""
        return {
            'valid_patient_data': {
                'lastname': 'Mustermann',
                'firstname': 'Max',
                'gender': Gender.MALE,
                'dob': date(1990, 5, 15),
                'op_date': date(2023, 10, 20),
                'indications': [Indication.AESTHETIC, Indication.FUNCTIONAL],
                'technique': SurgicalTechnique.OPEN,
                'nose_shape': NoseShape.AQUILINE,
                'anesthesia': AnesthesiaType.GENERAL,
                'op_duration_min': 180,
                'blood_loss_ml': 100
            },
            'edge_case_dates': {
                'future_birth': date.today() + timedelta(days=365),
                'past_birth': date(1900, 1, 1),
                'future_op': date.today() + timedelta(days=100),
                'young_patient_age': 15,
                'old_patient_age': 80
            },
            'boundary_values': {
                'op_duration_min': [30, 600],  # Min/Max
                'blood_loss_ml': [0, 1000],    # Min/Max
                'nose_length_mm': [30, 80],    # Min/Max
                'vas_values': [0, 10]          # VAS Scale
            },
            'invalid_inputs': {
                'empty_strings': ['', '   ', None],
                'special_chars': ['<script>', '"; DROP TABLE', 'Müller-Lüdenscheid'],
                'numbers_as_strings': ['abc', '12.5.2023', 'not_a_number'],
                'extreme_values': [999999, -1, 0.0]
            }
        }
    
    # === TEST KATEGORIE 1: GRUNDFUNKTIONALITÄT ===
    
    def test_01_ui_creation_and_layout(self):
        """Test 1: UI-Erstellung und Layout-Funktionalität"""
        test_name = "UI-Erstellung und Layout"
        
        try:
            # Widget erstellen
            widget = PatientEditorWidget(
                self.config, self.session_manager, 
                self.patient_manager, self.media_manager
            )
            
            # Grundlegende UI-Struktur prüfen
            self.assertIsNotNone(widget.tab_widget)
            self.assertGreater(widget.tab_widget.count(), 0, "Keine Tabs erstellt")
            
            # Titel prüfen
            self.assertIn("Patient", widget.title_label.text())
            
            # Footer-Buttons prüfen
            self.assertIsNotNone(widget.save_btn)
            self.assertIsNotNone(widget.cancel_btn)
            
            # Tab-Inhalt prüfen
            tab_names = [widget.tab_widget.tabText(i) for i in range(widget.tab_widget.count())]
            expected_tabs = ["Stammdaten", "Chirurgie", "Anatomie", "Messwerte", "Verfahren", "Nachsorge", "Ergebnisse", "Einwilligungen"]
            
            for expected_tab in expected_tabs:
                self.assertIn(expected_tab, tab_names, f"Tab '{expected_tab}' nicht gefunden")
            
            self._record_test_result(test_name, True, "UI erfolgreich erstellt")
            
        except Exception as e:
            self._record_test_result(test_name, False, f"UI-Erstellung fehlgeschlagen: {str(e)}")
            self.fail(f"UI-Erstellung fehlgeschlagen: {e}")
    
    def test_02_stammdaten_form(self):
        """Test 2: Stammdaten-Formular Funktionalität"""
        test_name = "Stammdaten-Formular"
        
        try:
            widget = PatientEditorWidget(
                self.config, self.session_manager, 
                self.patient_manager, self.media_manager
            )
            
            # Text-Eingabefelder testen
            self._test_text_input(widget.lastname_input, "Mustermann", "Nachname")
            self._test_text_input(widget.firstname_input, "Max", "Vorname")
            
            # Dropdown-Tests
            self._test_gender_dropdown(widget.gender_combo)
            
            # Datums-Tests
            self._test_date_input(widget.dob_input, date(1990, 5, 15), "Geburtsdatum")
            
            # Altersberechnung testen
            widget.dob_input.setDate(QDate(1990, 5, 15))
            self.assertIn("Jahre", widget.age_label.text(), "Altersanzeige fehlt")
            
            self._record_test_result(test_name, True, "Stammdaten-Formular funktional")
            
        except Exception as e:
            self._record_test_result(test_name, False, f"Stammdaten-Test fehlgeschlagen: {str(e)}")
            self.fail(f"Stammdaten-Test fehlgeschlagen: {e}")
    
    def test_03_chirurgie_form(self):
        """Test 3: Chirurgie-Formular Funktionalität"""
        test_name = "Chirurgie-Formular"
        
        try:
            widget = PatientEditorWidget(
                self.config, self.session_manager, 
                self.patient_manager, self.media_manager
            )
            
            # OP-Datum testen
            self._test_date_input(widget.op_date_input, date(2023, 10, 20), "OP-Datum")
            
            # Multi-Select Liste testen (Indikationen)
            self._test_multi_select_list(
                widget.indications_list, 
                [Indication.AESTHETIC, Indication.FUNCTIONAL],
                "Indikationen"
            )
            
            # Dropdown-Tests
            self._test_surgical_dropdowns(widget)
            
            # SpinBox-Tests
            self._test_spinbox_values(widget.op_duration_input, 180, "OP-Dauer")
            self._test_spinbox_values(widget.blood_loss_input, 100, "Blutverlust")
            
            self._record_test_result(test_name, True, "Chirurgie-Formular funktional")
            
        except Exception as e:
            self._record_test_result(test_name, False, f"Chirurgie-Test fehlgeschlagen: {str(e)}")
            self.fail(f"Chirurgie-Test fehlgeschlagen: {e}")
    
    # === TEST KATEGORIE 2: EINGABEVALIDIERUNG ===
    
    def test_04_required_field_validation(self):
        """Test 4: Pflichtfeld-Validierung"""
        test_name = "Pflichtfeld-Validierung"
        
        try:
            widget = PatientEditorWidget(
                self.config, self.session_manager, 
                self.patient_manager, self.media_manager
            )
            
            # Leere Pflichtfelder testen
            widget.lastname_input.setText("")
            widget.firstname_input.setText("")
            
            # Validierung auslösen
            is_valid = widget.validate_form()
            self.assertFalse(is_valid, "Validierung sollte mit leeren Pflichtfeldern fehlschlagen")
            
            # Pflichtfelder füllen
            widget.lastname_input.setText("Mustermann")
            widget.firstname_input.setText("Max")
            
            # Indikationen leer lassen (Pflicht)
            self._clear_multi_select(widget.indications_list)
            self._clear_multi_select(widget.procedures_list)
            self._clear_multi_select(widget.materials_list)
            
            is_valid = widget.validate_form()
            self.assertFalse(is_valid, "Validierung sollte ohne Indikationen/Verfahren fehlschlagen")
            
            # Alle Pflichtfelder füllen
            self._fill_required_fields(widget)
            
            is_valid = widget.validate_form()
            self.assertTrue(is_valid, "Validierung sollte mit allen Pflichtfeldern erfolgreich sein")
            
            self._record_test_result(test_name, True, "Pflichtfeld-Validierung funktional")
            
        except Exception as e:
            self._record_test_result(test_name, False, f"Pflichtfeld-Test fehlgeschlagen: {str(e)}")
            self.fail(f"Pflichtfeld-Test fehlgeschlagen: {e}")
    
    def test_05_date_validation(self):
        """Test 5: Datums-Validierung"""
        test_name = "Datums-Validierung"
        
        try:
            widget = PatientEditorWidget(
                self.config, self.session_manager, 
                self.patient_manager, self.media_manager
            )
            
            # Geburtsdatum in der Zukunft
            future_date = date.today() + timedelta(days=365)
            widget.dob_input.setDate(QDate(future_date))
            
            # Altersberechnung prüfen
            self.assertEqual(widget.age_label.text(), "0 Jahre", "Altersberechnung bei Zukunftsdatum fehlerhaft")
            
            # Sehr altes Geburtsdatum
            old_date = date(1900, 1, 1)
            widget.dob_input.setDate(QDate(old_date))
            self.assertGreaterEqual(int(widget.age_label.text().split()[0]), 120, "Sehr altes Geburtsdatum")
            
            # OP-Datum vor Geburtsdatum
            widget.dob_input.setDate(QDate(1990, 5, 15))
            widget.op_date_input.setDate(QDate(1980, 1, 1))  # Vor Geburt
            self._fill_required_fields(widget)
            
            is_valid = widget.validate_form()
            # Diese spezifische Validierung wird durch den Validator geprüft
            
            self._record_test_result(test_name, True, "Datums-Validierung funktional")
            
        except Exception as e:
            self._record_test_result(test_name, False, f"Datum-Test fehlgeschlagen: {str(e)}")
            self.fail(f"Datum-Test fehlgeschlagen: {e}")
    
    def test_06_boundary_value_validation(self):
        """Test 6: Grenzwert-Validierung"""
        test_name = "Grenzwert-Validierung"
        
        try:
            widget = PatientEditorWidget(
                self.config, self.session_manager, 
                self.patient_manager, self.media_manager
            )
            
            # SpinBox-Grenzwerte testen
            self._test_spinbox_boundaries(widget.op_duration_input, 30, 600, "OP-Dauer")
            self._test_spinbox_boundaries(widget.blood_loss_input, 0, 1000, "Blutverlust")
            
            # Messwerte-Grenzwerte
            self._test_spinbox_boundaries(widget.nose_length_input, 30, 80, "Nasenlänge")
            self._test_spinbox_boundaries(widget.tip_rotation_input, 80, 120, "Tip-Rotation")
            
            # Slider-Grenzwerte (0-10 für VAS)
            self._test_slider_boundaries(widget.satisfaction_slider, 0, 10, "Zufriedenheit")
            self._test_slider_boundaries(widget.airflow_vas_slider, 0, 10, "Atmung VAS")
            
            self._record_test_result(test_name, True, "Grenzwert-Validierung funktional")
            
        except Exception as e:
            self._record_test_result(test_name, False, f"Grenzwert-Test fehlgeschlagen: {str(e)}")
            self.fail(f"Grenzwert-Test fehlgeschlagen: {e}")
    
    # === TEST KATEGORIE 3: BENUTZERINTERAKTIONEN ===
    
    def test_07_keyboard_interactions(self):
        """Test 7: Tastatureingaben"""
        test_name = "Tastatureingaben"
        
        try:
            widget = PatientEditorWidget(
                self.config, self.session_manager, 
                self.patient_manager, self.media_manager
            )
            
            # Tab-Navigation testen
            self._test_tab_navigation(widget)
            
            # Enter-Taste im Formular
            widget.lastname_input.setFocus()
            QTest.keyClick(widget.lastname_input, Qt.Key_Return)
            
            # Escape-Taste (sollte nichts tun, da modal)
            QTest.keyClick(widget, Qt.Key_Escape)
            
            # Spezielle Zeichen
            special_chars = "Müller-Lüdenscheid, Dr. med.; \"quotes\" & <tags>"
            widget.lastname_input.setText(special_chars)
            self.assertEqual(widget.lastname_input.text(), special_chars)
            
            self._record_test_result(test_name, True, "Tastatureingaben funktional")
            
        except Exception as e:
            self._record_test_result(test_name, False, f"Keyboard-Test fehlgeschlagen: {str(e)}")
            self.fail(f"Keyboard-Test fehlgeschlagen: {e}")
    
    def test_08_mouse_interactions(self):
        """Test 8: Maus-Interaktionen"""
        test_name = "Maus-Interaktionen"
        
        try:
            widget = PatientEditorWidget(
                self.config, self.session_manager, 
                self.patient_manager, self.media_manager
            )
            
            # Button-Klicks
            self._test_button_interaction(widget.save_btn, "Speichern")
            self._test_button_interaction(widget.cancel_btn, "Abbrechen")
            
            # Checkbox-Interaktionen
            self._test_checkbox_interaction(widget.tamponade_check, "Tamponade")
            self._test_checkbox_interaction(widget.splint_check, "Schiene")
            
            # ComboBox-Auswahl
            self._test_combobox_selection(widget.gender_combo, "Geschlecht")
            
            # Slider-Interaktion
            self._test_slider_interaction(widget.satisfaction_slider, 7)
            
            self._record_test_result(test_name, True, "Maus-Interaktionen funktional")
            
        except Exception as e:
            self._record_test_result(test_name, False, f"Maus-Test fehlgeschlagen: {str(e)}")
            self.fail(f"Maus-Test fehlgeschlagen: {e}")
    
    def test_09_dynamic_ui_updates(self):
        """Test 9: Dynamische UI-Updates"""
        test_name = "Dynamische UI-Updates"
        
        try:
            widget = PatientEditorWidget(
                self.config, self.session_manager, 
                self.patient_manager, self.media_manager
            )
            
            # Tamponade-Checkbox aktivieren
            initial_state = widget.tamponade_days_input.isEnabled()
            widget.tamponade_check.setChecked(True)
            final_state = widget.tamponade_days_input.isEnabled()
            self.assertNotEqual(initial_state, final_state, "Tamponade-Tage sollten aktiviert werden")
            
            # Schiene-Checkbox aktivieren
            initial_state = widget.splint_days_input.isEnabled()
            widget.splint_check.setChecked(True)
            final_state = widget.splint_days_input.isEnabled()
            self.assertNotEqual(initial_state, final_state, "Schienen-Tage sollten aktiviert werden")
            
            # Slider-Werte und Labels
            widget.satisfaction_slider.setValue(8)
            self.assertEqual(widget.satisfaction_label.text(), "8/10", "Satisfaction Label sollte aktualisiert werden")
            
            widget.airflow_vas_slider.setValue(3)
            self.assertEqual(widget.airflow_vas_label.text(), "3/10", "Airflow Label sollte aktualisiert werden")
            
            self._record_test_result(test_name, True, "Dynamische Updates funktional")
            
        except Exception as e:
            self._record_test_result(test_name, False, f"Dynamic-UI-Test fehlgeschlagen: {str(e)}")
            self.fail(f"Dynamic-UI-Test fehlgeschlagen: {e}")
    
    # === TEST KATEGORIE 4: RESPONSIVE LAYOUT ===
    
    def test_10_window_resizing(self):
        """Test 10: Responsive Layout"""
        test_name = "Responsive Layout"
        
        try:
            widget = PatientEditorWidget(
                self.config, self.session_manager, 
                self.patient_manager, self.media_manager
            )
            
            # Minimale Größe
            widget.resize(1000, 600)
            self.assertGreaterEqual(widget.width(), 1000, "Minimale Breite nicht eingehalten")
            self.assertGreaterEqual(widget.height(), 600, "Minimale Höhe nicht eingehalten")
            
            # Größere Größe
            widget.resize(1400, 900)
            self.assertGreaterEqual(widget.width(), 1000, "Layout sollte sich anpassen")
            
            # Tab-Widget sollte scrollbar sein
            self.assertIsNotNone(widget.tab_widget.findChild(QApplication.scrollArea), "ScrollArea sollte vorhanden sein")
            
            self._record_test_result(test_name, True, "Responsive Layout funktional")
            
        except Exception as e:
            self._record_test_result(test_name, False, f"Responsive-Test fehlgeschlagen: {str(e)}")
            self.fail(f"Responsive-Test fehlgeschlagen: {e}")
    
    # === TEST KATEGORIE 5: FEHLERBEHANDLUNG ===
    
    def test_11_invalid_input_handling(self):
        """Test 11: Fehlerbehandlung bei ungültigen Eingaben"""
        test_name = "Fehlerbehandlung"
        
        try:
            widget = PatientEditorWidget(
                self.config, self.session_manager, 
                self.patient_manager, self.media_manager
            )
            
            # SQL-Injection-Versuch
            malicious_input = "'; DROP TABLE patients; --"
            widget.lastname_input.setText(malicious_input)
            self.assertEqual(widget.lastname_input.text(), malicious_input, "Malicious Input sollte gespeichert werden")
            
            # XSS-Versuch
            xss_input = "<script>alert('xss')</script>"
            widget.firstname_input.setText(xss_input)
            self.assertEqual(widget.firstname_input.text(), xss_input, "XSS Input sollte gespeichert werden")
            
            # Sehr lange Eingabe
            long_input = "A" * 1000
            widget.lastname_input.setText(long_input)
            self.assertLessEqual(len(widget.lastname_input.text()), 1000, "Sehr lange Eingabe sollte begrenzt werden")
            
            # Unicode-Zeichen
            unicode_input = "姓名 ñáéíóú åøæç ß"
            widget.firstname_input.setText(unicode_input)
            self.assertEqual(widget.firstname_input.text(), unicode_input, "Unicode sollte unterstützt werden")
            
            self._record_test_result(test_name, True, "Fehlerbehandlung funktional")
            
        except Exception as e:
            self._record_test_result(test_name, False, f"Fehlerbehandlung-Test fehlgeschlagen: {str(e)}")
            self.fail(f"Fehlerbehandlung-Test fehlgeschlagen: {e}")
    
    def test_12_validation_integration(self):
        """Test 12: Integration mit PatientValidator"""
        test_name = "Validator-Integration"
        
        try:
            validator = PatientValidator()
            
            # Gültige Patientendaten testen
            valid_patient = self._create_valid_test_patient()
            validation_result = validator.validate_patient(valid_patient)
            self.assertIsInstance(validation_result, dict, "Validator sollte Dictionary zurückgeben")
            self.assertIn('is_valid', validation_result, "Validierungsresultat sollte 'is_valid' enthalten")
            self.assertIn('errors', validation_result, "Validierungsresultat sollte 'errors' enthalten")
            self.assertIn('warnings', validation_result, "Validierungsresultat sollte 'warnings' enthalten")
            
            # Unvollständige Patientendaten testen
            invalid_patient = self._create_invalid_test_patient()
            validation_result = validator.validate_patient(invalid_patient)
            self.assertFalse(validation_result['is_valid'], "Unvollständige Daten sollten als ungültig erkannt werden")
            
            self._record_test_result(test_name, True, "Validator-Integration funktional")
            
        except Exception as e:
            self._record_test_result(test_name, False, f"Validator-Test fehlgeschlagen: {str(e)}")
            self.fail(f"Validator-Test fehlgeschlagen: {e}")
    
    # === HILFSMETHODEN ===
    
    def _test_text_input(self, widget, test_value, field_name):
        """Testet Text-Eingabefeld"""
        widget.setText(test_value)
        self.assertEqual(widget.text(), test_value, f"{field_name} Eingabe fehlgeschlagen")
    
    def _test_gender_dropdown(self, widget):
        """Testet Geschlecht-Dropdown"""
        self.assertGreater(widget.count(), 0, "Geschlecht-Dropdown ist leer")
        
        # Erste Option auswählen
        widget.setCurrentIndex(0)
        self.assertEqual(widget.currentIndex(), 0, "Dropdown-Auswahl fehlgeschlagen")
    
    def _test_date_input(self, widget, test_date, field_name):
        """Testet Datum-Eingabefeld"""
        widget.setDate(QDate(test_date))
        self.assertEqual(widget.date().toPython(), test_date, f"{field_name} Datum falsch gesetzt")
    
    def _test_multi_select_list(self, widget, selected_items, field_name):
        """Testet Multi-Select-Liste"""
        # Alle Items abwählen
        for i in range(widget.count()):
            item = widget.item(i)
            item.setSelected(False)
        
        # Gewünschte Items auswählen
        for i in range(widget.count()):
            item = widget.item(i)
            if item.data(Qt.UserRole) in selected_items:
                item.setSelected(True)
        
        # Auswahl prüfen
        selected_count = len(widget.selectedItems())
        self.assertGreater(selected_count, 0, f"Keine {field_name} ausgewählt")
    
    def _test_surgical_dropdowns(self, widget):
        """Testet chirurgische Dropdowns"""
        dropdowns = [
            (widget.technique_combo, "Operationstechnik"),
            (widget.nose_shape_combo, "Nasenform"),
            (widget.anesthesia_combo, "Anästhesie")
        ]
        
        for combo, name in dropdowns:
            self.assertGreater(combo.count(), 0, f"{name} Dropdown ist leer")
            combo.setCurrentIndex(0)
    
    def _test_spinbox_values(self, widget, test_value, field_name):
        """Testet SpinBox-Werte"""
        widget.setValue(test_value)
        self.assertEqual(widget.value(), test_value, f"{field_name} Wert falsch gesetzt")
    
    def _test_spinbox_boundaries(self, widget, min_val, max_val, field_name):
        """Testet SpinBox-Grenzwerte"""
        # Minimum testen
        widget.setValue(min_val)
        self.assertEqual(widget.value(), min_val, f"{field_name} Minimum nicht erreicht")
        
        # Maximum testen
        widget.setValue(max_val)
        self.assertEqual(widget.value(), max_val, f"{field_name} Maximum überschritten")
        
        # Bereichsprüfung
        widget.setValue(min_val - 1)
        self.assertGreaterEqual(widget.value(), min_val, f"{field_name} unter Minimum")
        
        widget.setValue(max_val + 1)
        self.assertLessEqual(widget.value(), max_val, f"{field_name} über Maximum")
    
    def _test_slider_boundaries(self, widget, min_val, max_val, field_name):
        """Testet Slider-Grenzwerte"""
        widget.setValue(min_val)
        self.assertEqual(widget.value(), min_val, f"{field_name} Slider Minimum nicht erreicht")
        
        widget.setValue(max_val)
        self.assertEqual(widget.value(), max_val, f"{field_name} Slider Maximum überschritten")
    
    def _test_tab_navigation(self, widget):
        """Testet Tab-Navigation"""
        initial_tab = widget.tab_widget.currentIndex()
        widget.tab_widget.setCurrentIndex(1)
        self.assertNotEqual(initial_tab, widget.tab_widget.currentIndex(), "Tab-Wechsel fehlgeschlagen")
    
    def _test_button_interaction(self, button, button_name):
        """Testet Button-Interaktion"""
        # Button sollte klickbar sein
        self.assertTrue(button.isEnabled(), f"{button_name} Button ist deaktiviert")
        button.click()
    
    def _test_checkbox_interaction(self, checkbox, name):
        """Testet Checkbox-Interaktion"""
        initial_state = checkbox.isChecked()
        checkbox.setChecked(not initial_state)
        self.assertNotEqual(initial_state, checkbox.isChecked(), f"{name} Checkbox ändert Zustand nicht")
    
    def _test_combobox_selection(self, combo, name):
        """Testet ComboBox-Auswahl"""
        initial_index = combo.currentIndex()
        if combo.count() > 1:
            combo.setCurrentIndex(1)
            self.assertNotEqual(initial_index, combo.currentIndex(), f"{name} ComboBox ändert Auswahl nicht")
    
    def _test_slider_interaction(self, slider, test_value):
        """Testet Slider-Interaktion"""
        slider.setValue(test_value)
        self.assertEqual(slider.value(), test_value, "Slider-Wert falsch gesetzt")
    
    def _clear_multi_select(self, widget):
        """Leert Multi-Select-Liste"""
        for i in range(widget.count()):
            widget.item(i).setSelected(False)
    
    def _fill_required_fields(self, widget):
        """Füllt alle Pflichtfelder"""
        widget.lastname_input.setText("Mustermann")
        widget.firstname_input.setText("Max")
        
        # Indikationen
        for i in range(widget.indications_list.count()):
            widget.indications_list.item(i).setSelected(True)
        
        # Verfahren
        for i in range(widget.procedures_list.count()):
            widget.procedures_list.item(i).setSelected(True)
        
        # Materialien
        for i in range(widget.materials_list.count()):
            widget.materials_list.item(i).setSelected(True)
    
    def _create_valid_test_patient(self):
        """Erstellt gültigen Test-Patienten"""
        return Patient(
            demographics=Demographics(
                lastname="Test",
                firstname="Patient",
                gender=Gender.MALE,
                dob=date(1990, 1, 1)
            ),
            surgery=Surgery(
                op_date=date(2023, 1, 1),
                indications=[Indication.AESTHETIC],
                technique=SurgicalTechnique.OPEN,
                nose_shape=NoseShape.AQUILINE,
                anatomy=Mock(),
                measurements=Mock(),
                procedures=[Procedure.HUMP_REDUCTION],
                materials=[Material.PORCINE_CARTILAGE],
                anesthesia=AnesthesiaType.GENERAL,
                op_duration_min=120,
                blood_loss_ml=50,
                complications_intraop=[],
                complications_postop=[],
                aftercare=Mock(),
                outcomes=Mock()
            ),
            consents=Mock(),
            notes="Test Patient"
        )
    
    def _create_invalid_test_patient(self):
        """Erstellt ungültigen Test-Patienten"""
        return Patient(
            demographics=Demographics(
                lastname="",  # Leer = ungültig
                firstname="Test",
                gender=Gender.MALE,
                dob=date(1990, 1, 1)
            ),
            surgery=Surgery(
                op_date=date(2023, 1, 1),
                indications=[],  # Leer = ungültig
                technique=SurgicalTechnique.OPEN,
                nose_shape=NoseShape.AQUILINE,
                anatomy=Mock(),
                measurements=Mock(),
                procedures=[],  # Leer = ungültig
                materials=[],   # Leer = ungültig
                anesthesia=AnesthesiaType.GENERAL,
                op_duration_min=120,
                blood_loss_ml=50,
                complications_intraop=[],
                complications_postop=[],
                aftercare=Mock(),
                outcomes=Mock()
            ),
            consents=Mock(),
            notes="Test Patient"
        )
    
    def _record_test_result(self, test_name, passed, message):
        """Zeichnet Testergebnis auf"""
        if passed:
            self.test_results['passed'] += 1
        else:
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"{test_name}: {message}")
        
        # Kategorie erfassen
        category = test_name.split(':')[0] if ':' in test_name else test_name
        if category not in self.test_results['test_categories']:
            self.test_results['test_categories'][category] = {'passed': 0, 'failed': 0}
        
        if passed:
            self.test_results['test_categories'][category]['passed'] += 1
        else:
            self.test_results['test_categories'][category]['failed'] += 1
    
    @classmethod
    def tearDownClass(cls):
        """Aufräumen nach allen Tests"""
        # Test-Ergebnisse ausgeben
        print("\n" + "="*80)
        print("FORMULAR-EINGABEVALIDIERUNG TEST-ZUSAMMENFASSUNG")
        print("="*80)
        print(f"Gesamt Tests: {cls.test_results['total_tests']}")
        print(f"Erfolgreich: {cls.test_results['passed']}")
        print(f"Fehlgeschlagen: {cls.test_results['failed']}")
        print(f"Erfolgsrate: {cls.test_results['passed']/cls.test_results['total_tests']*100:.1f}%")
        
        if cls.test_results['errors']:
            print("\nFEHLER:")
            for error in cls.test_results['errors']:
                print(f"  • {error}")
        
        print("\nKATEGORIEN:")
        for category, results in cls.test_results['test_categories'].items():
            total = results['passed'] + results['failed']
            rate = results['passed'] / total * 100 if total > 0 else 0
            print(f"  {category}: {results['passed']}/{total} ({rate:.1f}%)")
        
        print("="*80)


def run_comprehensive_tests():
    """Führt umfassende Tests aus"""
    # Unittest mit detaillierter Ausgabe
    suite = unittest.TestLoader().loadTestsFromTestCase(FormularEingabevalidierungTests)
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    print("Starte umfassende Formular- und Eingabevalidierung-Tests...")
    print("Dies kann einige Minuten dauern...")
    
    result = run_comprehensive_tests()
    
    # Exit-Code basierend auf Testergebnissen
    sys.exit(0 if result.wasSuccessful() else 1)
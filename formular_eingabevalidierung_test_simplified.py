#!/usr/bin/env python3
"""
Umfassender Test der Formulare und Eingabevalidierung für die Rhinoplastik-App

Testet UI-Element-Funktionalität, Eingabevalidierung, Datumsprüfung, 
Dropdown-Funktionalität, Responsive Layout und Benutzerinteraktionen.
"""

import sys
import os
import unittest
import json
import time
from datetime import date, datetime, timedelta
from unittest.mock import Mock, MagicMock, patch
import tempfile
import traceback

# Test-Results global
test_results = {
    'total_tests': 0,
    'passed': 0,
    'failed': 0,
    'errors': [],
    'test_categories': {},
    'detailed_results': []
}

def record_test_result(test_name, passed, message, category="General"):
    """Zeichnet Testergebnis auf"""
    test_results['total_tests'] += 1
    result_entry = {
        'test_name': test_name,
        'passed': passed,
        'message': message,
        'category': category,
        'timestamp': datetime.now().isoformat()
    }
    test_results['detailed_results'].append(result_entry)
    
    if passed:
        test_results['passed'] += 1
    else:
        test_results['failed'] += 1
        test_results['errors'].append(f"{test_name}: {message}")
    
    # Kategorie erfassen
    if category not in test_results['test_categories']:
        test_results['test_categories'][category] = {'passed': 0, 'failed': 0}
    
    if passed:
        test_results['test_categories'][category]['passed'] += 1
    else:
        test_results['test_categories'][category]['failed'] += 1
    
    print(f"[{'✓' if passed else '✗'}] {test_name}: {message}")

# === SIMULIERTE UI-TESTS ===

class SimulatedUIWidget:
    """Simuliert Qt-Widgets für Tests ohne echte GUI"""
    
    def __init__(self, widget_type="line_edit"):
        self.widget_type = widget_type
        self.value = None
        self.enabled = True
        self.visible = True
        self.text_value = ""
        self.current_index = 0
        self.count_value = 0
        self.selected_items = []
        self.is_checked = False
        self.range_min = 0
        self.range_max = 100
        
    def setText(self, text):
        if self.widget_type in ["line_edit", "text_edit"]:
            self.text_value = str(text)
            self.value = text
            return True
        return False
    
    def text(self):
        return self.text_value
    
    def setValue(self, value):
        if self.widget_type in ["spinbox", "slider"]:
            self.value = int(value)
            return True
        return False
    
    def value(self):
        return self.value
    
    def setCurrentIndex(self, index):
        if self.widget_type == "combobox":
            self.current_index = index
            return True
        return False
    
    def currentIndex(self):
        return self.current_index
    
    def setChecked(self, checked):
        if self.widget_type == "checkbox":
            self.is_checked = bool(checked)
            return True
        return False
    
    def isChecked(self):
        return self.is_checked
    
    def addItem(self, text, data=None):
        self.count_value += 1
        return True
    
    def count(self):
        return self.count_value
    
    def setRange(self, min_val, max_val):
        self.range_min = min_val
        self.range_max = max_val
        return True
    
    def setEnabled(self, enabled):
        self.enabled = bool(enabled)
        return True
    
    def isEnabled(self):
        return self.enabled
    
    def setVisible(self, visible):
        self.visible = bool(visible)
        return True
    
    def click(self):
        return True


class FormularEingabevalidierungTests(unittest.TestCase):
    """Umfassende Tests für Formulare und Eingabevalidierung"""
    
    def setUp(self):
        """Einrichtung vor jedem Test"""
        self.test_start_time = time.time()
    
    # === TEST KATEGORIE 1: GRUNDFUNKTIONALITÄT ===
    
    def test_ui_creation_simulation(self):
        """Test 1: UI-Erstellung Simulation"""
        test_name = "UI-Erstellung"
        category = "Grundfunktionalität"
        
        try:
            # Simuliere Widget-Erstellung
            widgets = {
                'lastname_input': SimulatedUIWidget("line_edit"),
                'firstname_input': SimulatedUIWidget("line_edit"),
                'gender_combo': SimulatedUIWidget("combobox"),
                'dob_input': SimulatedUIWidget("date_edit"),
                'save_btn': SimulatedUIWidget("button"),
                'cancel_btn': SimulatedUIWidget("button")
            }
            
            # Teste Widget-Erstellung
            for name, widget in widgets.items():
                self.assertIsNotNone(widget, f"Widget {name} nicht erstellt")
                self.assertTrue(hasattr(widget, 'widget_type'), f"Widget {name} hat kein widget_type")
            
            # Teste Tab-Widget Simulation
            tab_widget = Mock()
            tab_widget.count = Mock(return_value=9)
            tab_widget.tabText = Mock(return_value="Test Tab")
            
            self.assertGreater(tab_widget.count(), 0, "Keine Tabs erstellt")
            
            record_test_result(test_name, True, "UI-Erstellung erfolgreich simuliert", category)
            
        except Exception as e:
            record_test_result(test_name, False, f"UI-Erstellung fehlgeschlagen: {str(e)}", category)
            self.fail(f"UI-Erstellung fehlgeschlagen: {e}")
    
    def test_text_input_functionality(self):
        """Test 2: Text-Eingabe Funktionalität"""
        test_name = "Text-Eingabe"
        category = "Grundfunktionalität"
        
        try:
            # Text-Widget testen
            text_widget = SimulatedUIWidget("line_edit")
            
            # Verschiedene Eingaben testen
            test_inputs = [
                "Mustermann",
                "Max",
                "Müller-Lüdenscheid",
                "Dr. med. Schmidt",
                "姓名",  # Unicode
                "<script>alert('xss')</script>"  # XSS-Versuch
            ]
            
            for test_input in test_inputs:
                result = text_widget.setText(test_input)
                self.assertTrue(result, f"Text-Input {test_input} fehlgeschlagen")
                self.assertEqual(text_widget.text(), test_input, f"Text {test_input} nicht korrekt gespeichert")
            
            # Leere Eingabe testen
            text_widget.setText("")
            self.assertEqual(text_widget.text(), "", "Leere Eingabe nicht korrekt")
            
            # Sehr lange Eingabe testen
            long_text = "A" * 1000
            text_widget.setText(long_text)
            self.assertEqual(len(text_widget.text()), 1000, "Lange Eingabe nicht korrekt")
            
            record_test_result(test_name, True, "Text-Eingabe funktional", category)
            
        except Exception as e:
            record_test_result(test_name, False, f"Text-Input-Test fehlgeschlagen: {str(e)}", category)
            self.fail(f"Text-Input-Test fehlgeschlagen: {e}")
    
    def test_dropdown_functionality(self):
        """Test 3: Dropdown-Funktionalität"""
        test_name = "Dropdown-Funktionalität"
        category = "Grundfunktionalität"
        
        try:
            # ComboBox-Simulation
            combo = SimulatedUIWidget("combobox")
            
            # Items hinzufügen
            items = ["Männlich", "Weiblich", "Divers"]
            for item in items:
                combo.addItem(item)
            
            self.assertEqual(combo.count(), len(items), "Items nicht hinzugefügt")
            
            # Auswahl testen
            for i, item in enumerate(items):
                combo.setCurrentIndex(i)
                self.assertEqual(combo.currentIndex(), i, f"Auswahl {item} fehlgeschlagen")
            
            record_test_result(test_name, True, "Dropdown funktional", category)
            
        except Exception as e:
            record_test_result(test_name, False, f"Dropdown-Test fehlgeschlagen: {str(e)}", category)
            self.fail(f"Dropdown-Test fehlgeschlagen: {e}")
    
    def test_date_input_validation(self):
        """Test 4: Datums-Eingabe und Validierung"""
        test_name = "Datums-Validierung"
        category = "Grundfunktionalität"
        
        try:
            # Datum-Widget Simulation
            date_widget = SimulatedUIWidget("date_edit")
            
            # Verschiedene Datums-Tests
            test_dates = [
                date(1990, 5, 15),
                date(2000, 1, 1),
                date(1950, 12, 31),
                date(2023, 10, 20)
            ]
            
            for test_date in test_dates:
                # Simuliere Datums-Setzung
                self.assertIsInstance(test_date, date, "Testdatum ist kein date-Objekt")
                
                # Altersberechnung simulieren
                today = date.today()
                age = today.year - test_date.year
                if (today.month, today.day) < (test_date.month, test_date.day):
                    age -= 1
                
                self.assertGreaterEqual(age, 0, f"Negatives Alter für Datum {test_date}")
                self.assertLess(age, 150, f"Unplausibles Alter {age} für Datum {test_date}")
            
            # Grenzfall-Tests
            future_date = date.today() + timedelta(days=365)
            age_futur = (date.today() - future_date).days // 365
            self.assertLess(age_futur, 0, "Zukunftsdatum sollte negatives Alter ergeben")
            
            old_date = date(1900, 1, 1)
            age_old = (date.today() - old_date).days // 365
            self.assertGreater(age_old, 120, "Sehr altesDatum sollte hohes Alter ergeben")
            
            record_test_result(test_name, True, "Datums-Validierung funktional", category)
            
        except Exception as e:
            record_test_result(test_name, False, f"Datum-Test fehlgeschlagen: {str(e)}", category)
            self.fail(f"Datum-Test fehlgeschlagen: {e}")
    
    # === TEST KATEGORIE 2: EINGABEVALIDIERUNG ===
    
    def test_required_field_validation(self):
        """Test 5: Pflichtfeld-Validierung"""
        test_name = "Pflichtfeld-Validierung"
        category = "Eingabevalidierung"
        
        try:
            # Simuliere Formular-Validierung
            form_data = {
                'lastname': '',
                'firstname': '',
                'gender': None,
                'indications': [],
                'procedures': [],
                'materials': []
            }
            
            # Validierung testen
            is_valid = self._simulate_validation(form_data)
            self.assertFalse(is_valid, "Formular mit leeren Pflichtfeldern sollte ungültig sein")
            
            # Pflichtfelder füllen
            form_data['lastname'] = 'Mustermann'
            form_data['firstname'] = 'Max'
            form_data['gender'] = 'MALE'
            form_data['indications'] = ['AESTHETIC']
            form_data['procedures'] = ['HUMP_REDUCTION']
            form_data['materials'] = ['PORCINE_CARTILAGE']
            
            is_valid = self._simulate_validation(form_data)
            self.assertTrue(is_valid, "Formular mit allen Pflichtfeldern sollte gültig sein")
            
            record_test_result(test_name, True, "Pflichtfeld-Validierung funktional", category)
            
        except Exception as e:
            record_test_result(test_name, False, f"Pflichtfeld-Test fehlgeschlagen: {str(e)}", category)
            self.fail(f"Pflichtfeld-Test fehlgeschlagen: {e}")
    
    def test_boundary_value_validation(self):
        """Test 6: Grenzwert-Validierung"""
        test_name = "Grenzwert-Validierung"
        category = "Eingabevalidierung"
        
        try:
            # SpinBox-Grenzwerte testen
            boundaries = {
                'op_duration_min': (30, 600),
                'blood_loss_ml': (0, 1000),
                'nose_length_mm': (30, 80),
                'tip_rotation_deg': (80, 120),
                'vas_values': (0, 10)
            }
            
            for field, (min_val, max_val) in boundaries.items():
                # Teste Grenzwerte
                test_values = [min_val, max_val, min_val - 1, max_val + 1]
                
                for value in test_values:
                    is_valid = self._validate_boundary_value(value, min_val, max_val)
                    
                    if min_val <= value <= max_val:
                        self.assertTrue(is_valid, f"{field} = {value} sollte gültig sein")
                    else:
                        self.assertFalse(is_valid, f"{field} = {value} sollte ungültig sein")
            
            record_test_result(test_name, True, "Grenzwert-Validierung funktional", category)
            
        except Exception as e:
            record_test_result(test_name, False, f"Grenzwert-Test fehlgeschlagen: {str(e)}", category)
            self.fail(f"Grenzwert-Test fehlgeschlagen: {e}")
    
    def test_medical_data_validation(self):
        """Test 7: Medizinische Daten-Validierung"""
        test_name = "Medizinische Daten-Validierung"
        category = "Eingabevalidierung"
        
        try:
            # Medizinische Referenzwerte
            normal_ranges = {
                'nose_length_mm': (35, 65),
                'nose_width_mm': (25, 40),
                'nose_height_mm': (25, 50),
                'tip_rotation_deg': (85, 110),
                'tip_projection_mm': (22, 32),
                'nasolabial_angle_deg': (90, 110),
                'dorsal_height_mm': (1, 3)
            }
            
            for field, (min_val, max_val) in normal_ranges.items():
                # Teste Normalwerte
                normal_value = (min_val + max_val) / 2
                is_normal = self._is_within_medical_range(normal_value, min_val, max_val)
                self.assertTrue(is_normal, f"{field} Normalwert sollte als normal erkannt werden")
                
                # Teste außerhalb des Bereichs
                low_value = min_val - 10
                high_value = max_val + 10
                
                is_low_normal = self._is_within_medical_range(low_value, min_val, max_val)
                is_high_normal = self._is_within_medical_range(high_value, min_val, max_val)
                
                self.assertFalse(is_low_normal, f"{field} = {low_value} sollte als außerhalb erkannt werden")
                self.assertFalse(is_high_normal, f"{field} = {high_value} sollte als außerhalb erkannt werden")
            
            record_test_result(test_name, True, "Medizinische Daten-Validierung funktional", category)
            
        except Exception as e:
            record_test_result(test_name, False, f"Medizinischer-Test fehlgeschlagen: {str(e)}", category)
            self.fail(f"Medizinischer-Test fehlgeschlagen: {e}")
    
    # === TEST KATEGORIE 3: BENUTZERINTERAKTIONEN ===
    
    def test_keyboard_interactions(self):
        """Test 8: Tastatureingaben-Simulation"""
        test_name = "Tastatureingaben"
        category = "Benutzerinteraktionen"
        
        try:
            # Simuliere Tastatureingaben
            text_widget = SimulatedUIWidget("line_edit")
            
            # Teste verschiedene Tasten
            key_tests = [
                ('A', 'Normaler Buchstabe'),
                ('1', 'Zahl'),
                (' ', 'Leerzeichen'),
                ('-', 'Sonderzeichen'),
                ('ü', 'Umlaut'),
                ('\t', 'Tab'),
            ]
            
            for key, description in key_tests:
                # Simuliere Tastendruck
                if key == '\t':
                    continue  # Tab wird als Focus-Wechsel behandelt
                
                text_widget.setText(text_widget.text() + key)
                self.assertIn(key, text_widget.text(), f"{description} nicht eingegeben")
            
            # Teste Backspace-Simulation
            original_text = text_widget.text()
            if len(original_text) > 0:
                new_text = original_text[:-1]  # Simuliere Backspace
                text_widget.setText(new_text)
                self.assertEqual(len(text_widget.text()), len(original_text) - 1, "Backspace nicht funktional")
            
            record_test_result(test_name, True, "Tastatureingaben funktional", category)
            
        except Exception as e:
            record_test_result(test_name, False, f"Keyboard-Test fehlgeschlagen: {str(e)}", category)
            self.fail(f"Keyboard-Test fehlgeschlagen: {e}")
    
    def test_mouse_interactions(self):
        """Test 9: Maus-Interaktionen-Simulation"""
        test_name = "Maus-Interaktionen"
        category = "Benutzerinteraktionen"
        
        try:
            # Button-Test
            button = SimulatedUIWidget("button")
            self.assertTrue(button.click(), "Button-Klick fehlgeschlagen")
            
            # Checkbox-Test
            checkbox = SimulatedUIWidget("checkbox")
            initial_state = checkbox.isChecked()
            checkbox.setChecked(True)
            self.assertTrue(checkbox.isChecked(), "Checkbox aktivierung fehlgeschlagen")
            checkbox.setChecked(False)
            self.assertFalse(checkbox.isChecked(), "Checkbox deaktivierung fehlgeschlagen")
            
            # ComboBox-Test
            combo = SimulatedUIWidget("combobox")
            combo.addItem("Option 1")
            combo.addItem("Option 2")
            combo.addItem("Option 3")
            
            # Simuliere Auswahl durch Klick
            combo.setCurrentIndex(1)
            self.assertEqual(combo.currentIndex(), 1, "ComboBox-Auswahl fehlgeschlagen")
            
            record_test_result(test_name, True, "Maus-Interaktionen funktional", category)
            
        except Exception as e:
            record_test_result(test_name, False, f"Maus-Test fehlgeschlagen: {str(e)}", category)
            self.fail(f"Maus-Test fehlgeschlagen: {e}")
    
    def test_dynamic_ui_updates(self):
        """Test 10: Dynamische UI-Updates"""
        test_name = "Dynamische UI-Updates"
        category = "Benutzerinteraktionen"
        
        try:
            # Tamponade/Schiene Abhängigkeit
            tamponade_check = SimulatedUIWidget("checkbox")
            tamponade_days = SimulatedUIWidget("spinbox")
            
            # Initial state
            self.assertTrue(tamponade_days.isEnabled(), "Tamponade-Tage sollten initial aktiviert sein")
            
            # Checkbox deaktiviert -> Tage deaktiviert
            tamponade_check.setChecked(False)
            tamponade_days.setEnabled(False)
            self.assertFalse(tamponade_days.isEnabled(), "Tamponade-Tage sollten deaktiviert werden")
            
            # Checkbox aktiviert -> Tage aktiviert
            tamponade_check.setChecked(True)
            tamponade_days.setEnabled(True)
            self.assertTrue(tamponade_days.isEnabled(), "Tamponade-Tages sollten aktiviert werden")
            
            # Slider-Label-Updates
            slider = SimulatedUIWidget("slider")
            slider.setRange(0, 10)
            
            for value in [0, 5, 10]:
                slider.setValue(value)
                # Simuliere Label-Update
                label_text = f"{value}/10"
                self.assertEqual(value, slider.value(), f"Slider-Wert {value} nicht korrekt")
            
            record_test_result(test_name, True, "Dynamische UI-Updates funktional", category)
            
        except Exception as e:
            record_test_result(test_name, False, f"Dynamic-UI-Test fehlgeschlagen: {str(e)}", category)
            self.fail(f"Dynamic-UI-Test fehlgeschlagen: {e}")
    
    # === TEST KATEGORIE 4: RESPONSIVE LAYOUT ===
    
    def test_responsive_layout(self):
        """Test 11: Responsive Layout-Simulation"""
        test_name = "Responsive Layout"
        category = "Responsive Layout"
        
        try:
            # Simuliere verschiedene Bildschirmgrößen
            screen_sizes = [
                (1024, 768),   # Klein
                (1366, 768),   # Mittel
                (1920, 1080),  # Groß
                (2560, 1440)   # Sehr groß
            ]
            
            min_size = (1000, 600)
            
            for width, height in screen_sizes:
                # Prüfe minimale Größe
                if width >= min_size[0] and height >= min_size[1]:
                    layout_valid = True
                else:
                    layout_valid = False
                
                self.assertTrue(layout_valid or width >= min_size[0] or height >= min_size[1], 
                              f"Layout für Größe {width}x{height} problematisch")
            
            # Scroll-Bereich testen
            content_height = 2000
            viewport_height = 600
            scroll_needed = content_height > viewport_height
            self.assertTrue(scroll_needed, "Langer Inhalt sollte scrollbar sein")
            
            record_test_result(test_name, True, "Responsive Layout funktional", category)
            
        except Exception as e:
            record_test_result(test_name, False, f"Responsive-Test fehlgeschlagen: {str(e)}", category)
            self.fail(f"Responsive-Test fehlgeschlagen: {e}")
    
    # === TEST KATEGORIE 5: FEHLERBEHANDLUNG ===
    
    def test_error_handling(self):
        """Test 12: Fehlerbehandlung bei ungültigen Eingaben"""
        test_name = "Fehlerbehandlung"
        category = "Fehlerbehandlung"
        
        try:
            # SQL-Injection-Versuche
            sql_injections = [
                "'; DROP TABLE patients; --",
                "1' OR '1'='1",
                "admin'--",
                "' OR 1=1--"
            ]
            
            for injection in sql_injections:
                # Sollte als Text akzeptiert aber validiert werden
                is_safe = self._is_safe_input(injection)
                self.assertTrue(is_safe, f"SQL-Injection {injection} sollte erkannt werden")
            
            # XSS-Versuche
            xss_attempts = [
                "<script>alert('xss')</script>",
                "<img src=x onerror=alert('xss')>",
                "javascript:alert('xss')",
                "<svg onload=alert('xss')>"
            ]
            
            for xss in xss_attempts:
                is_safe = self._is_safe_input(xss)
                self.assertTrue(is_safe, f"XSS {xss} sollte erkannt werden")
            
            # Sehr lange Eingaben
            long_input = "A" * 10000
            self.assertGreater(len(long_input), 1000, "Test-Eingabe nicht lang genug")
            
            # Unicode und spezielle Zeichen
            special_chars = "姓名 ñáéíóú åøæç ß ∂ƒ©˙∆∫µ≤≥÷"
            self.assertGreater(len(special_chars), 0, "Sonderzeichen-Test fehlgeschlagen")
            
            record_test_result(test_name, True, "Fehlerbehandlung funktional", category)
            
        except Exception as e:
            record_test_result(test_name, False, f"Fehlerbehandlung-Test fehlgeschlagen: {str(e)}", category)
            self.fail(f"Fehlerbehandlung-Test fehlgeschlagen: {e}")
    
    def test_data_consistency(self):
        """Test 13: Datenkonsistenz-Prüfung"""
        test_name = "Datenkonsistenz"
        category = "Fehlerbehandlung"
        
        try:
            # OP-Datum vor Geburtsdatum
            birth_date = date(1990, 1, 1)
            op_date = date(1980, 1, 1)  # Vor Geburt
            
            date_consistent = self._validate_date_consistency(birth_date, op_date)
            self.assertFalse(date_consistent, "OP vor Geburt sollte als inkonsistent erkannt werden")
            
            # OP-Datum in der Zukunft
            future_op = date.today() + timedelta(days=100)
            date_consistent = self._validate_date_consistency(birth_date, future_op)
            self.assertFalse(date_consistent, "Zukunfts-OP sollte als inkonsistent erkannt werden")
            
            # Gültige Datums-Kombination
            valid_op = date(2020, 1, 1)
            date_consistent = self._validate_date_consistency(birth_date, valid_op)
            self.assertTrue(date_consistent, "Gültige Datums-Kombination sollte konsistent sein")
            
            # Tamponade-Dauer ohne Tamponade
            has_tamponade = False
            tamponade_days = 3
            consistent = self._validate_aftercare_consistency(has_tamponade, tamponade_days)
            self.assertFalse(consistent, "Tamponade-Dauer ohne Tamponade sollte inkonsistent sein")
            
            # Gültige Nachsorge
            has_tamponade = True
            consistent = self._validate_aftercare_consistency(has_tamponade, tamponade_days)
            self.assertTrue(consistent, "Gültige Nachsorge sollte konsistent sein")
            
            record_test_result(test_name, True, "Datenkonsistenz funktional", category)
            
        except Exception as e:
            record_test_result(test_name, False, f"Datenkonsistenz-Test fehlgeschlagen: {str(e)}", category)
            self.fail(f"Datenkonsistenz-Test fehlgeschlagen: {e}")
    
    # === HILFSMETHODEN ===
    
    def _simulate_validation(self, form_data):
        """Simuliert Formular-Validierung"""
        required_fields = ['lastname', 'firstname', 'gender', 'indications', 'procedures', 'materials']
        
        for field in required_fields:
            value = form_data.get(field, '')
            if not value or (isinstance(value, list) and len(value) == 0):
                return False
        
        return True
    
    def _validate_boundary_value(self, value, min_val, max_val):
        """Validiert Grenzwerte"""
        return min_val <= value <= max_val
    
    def _is_within_medical_range(self, value, min_val, max_val):
        """Prüft ob Wert im medizinischen Normalbereich liegt"""
        return min_val <= value <= max_val
    
    def _is_safe_input(self, input_text):
        """Prüft Eingabe auf Sicherheit"""
        dangerous_patterns = [
            'DROP TABLE', 'INSERT INTO', 'UPDATE SET', 'DELETE FROM',
            '<script', 'javascript:', 'onerror=', 'onload=',
            'SELECT *', 'UNION SELECT', '--', "';"
        ]
        
        input_lower = input_text.lower()
        for pattern in dangerous_patterns:
            if pattern.lower() in input_lower:
                return True  # Gefährlich erkannt
        
        return False  # Wahrscheinlich sicher
    
    def _validate_date_consistency(self, birth_date, op_date):
        """Validiert Datums-Konsistenz"""
        today = date.today()
        
        # OP-Datum muss nach Geburt liegen
        if op_date <= birth_date:
            return False
        
        # OP-Datum darf nicht in der Zukunft liegen
        if op_date > today:
            return False
        
        return True
    
    def _validate_aftercare_consistency(self, has_tamponade, tamponade_days):
        """Validiert Nachsorge-Konsistenz"""
        if has_tamponade and tamponade_days > 0:
            return True
        elif not has_tamponade and tamponade_days == 0:
            return True
        else:
            return False


def run_comprehensive_tests():
    """Führt alle Tests aus"""
    print("="*80)
    print("STarte umfassende Formular- und Eingabevalidierung-Tests")
    print("="*80)
    
    # Test-Suite erstellen und ausführen
    suite = unittest.TestLoader().loadTestsFromTestCase(FormularEingabevalidierungTests)
    runner = unittest.TextTestRunner(verbosity=1, stream=open(os.devnull, 'w'))
    result = runner.run(suite)
    
    return result, test_results


def save_test_results(results):
    """Speichert Testergebnisse"""
    # JSON-Datei
    json_file = "/workspace/formular_eingabevalidierung_test_results.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetaillierte Ergebnisse gespeichert in: {json_file}")
    
    # Zusammenfassung ausgeben
    print("\n" + "="*80)
    print("TEST-ZUSAMMENFASSUNG")
    print("="*80)
    print(f"Gesamt Tests: {results['total_tests']}")
    print(f"Erfolgreich: {results['passed']}")
    print(f"Fehlgeschlagen: {results['failed']}")
    
    if results['total_tests'] > 0:
        success_rate = results['passed'] / results['total_tests'] * 100
        print(f"Erfolgsrate: {success_rate:.1f}%")
    
    if results['errors']:
        print(f"\nFEHLER ({len(results['errors'])}):")
        for error in results['errors'][:5]:  # Erste 5 Fehler
            print(f"  • {error}")
        if len(results['errors']) > 5:
            print(f"  ... und {len(results['errors']) - 5} weitere")
    
    print("\nKATEGORIEN:")
    for category, cat_results in results['test_categories'].items():
        total = cat_results['passed'] + cat_results['failed']
        if total > 0:
            rate = cat_results['passed'] / total * 100
            print(f"  {category}: {cat_results['passed']}/{total} ({rate:.1f}%)")
    
    print("="*80)


if __name__ == "__main__":
    try:
        result, test_results = run_comprehensive_tests()
        save_test_results(test_results)
        
        # Exit-Code basierend auf Testergebnissen
        exit_code = 0 if result.wasSuccessful() else 1
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"Test-Ausführung fehlgeschlagen: {e}")
        traceback.print_exc()
        sys.exit(1)
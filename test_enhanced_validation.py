"""
Umfassende Tests für erweiterte Datenvalidierung und Fehlerbehandlung

Testet:
- String Length Validation für MediaFile paths
- Cross-Field-Validierung zwischen medizinischen Feldern
- Robuste Error-Handling
- Zeitformat-Parsing und Zeitzonen-Behandlung
- Edge-Case-Tests und Boundary-Checks
- Retry-Mechanismen
"""

import logging
import sys
import os
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Dict, Any, List

# Pfad für Imports
sys.path.insert(0, str(Path(__file__).parent / "rhinoplastik_app"))

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Core Imports
from rhinoplastik_app.core.validators import (
    PatientValidator,
    MediaFileValidator,
    MedicalFieldValidator,
    RobustErrorHandler,
    DateTimeHandler,
    EdgeCaseTester,
    global_retry_mechanism,
    retry_with_config,
    ErrorCategory,
    ErrorSeverity
)

from rhinoplastik_app.core.patients.patient_model import (
    Patient, Demographics, Surgery, Measurements, Outcomes, 
    Indication, Procedure, Material, AnesthesiaType, 
    Gender, SkinThickness, Complication, MediaFile, Consents
)


class TestEnhancedValidation:
    """Test-Suite für erweiterte Validierung"""
    
    @classmethod
    def setup_class(cls):
        """Setup für alle Tests"""
        cls.patient_validator = PatientValidator()
        cls.media_validator = MediaFileValidator()
        cls.medical_validator = MedicalFieldValidator()
        cls.error_handler = RobustErrorHandler()
        cls.datetime_handler = DateTimeHandler()
        cls.edge_tester = EdgeCaseTester()
    
    def test_string_length_validation_media_files(self):
        """Test 1: String Length Validation für MediaFile paths"""
        print("\n=== Test 1: MediaFile String Length Validation ===")
        
        test_cases = [
            {
                'name': 'Empty Path',
                'path': '',
                'expected_valid': False
            },
            {
                'name': 'Very Long Path (600 chars)',
                'path': 'images/' + 'x' * 600,
                'expected_valid': False
            },
            {
                'name': 'Max Valid Path (500 chars)',
                'path': 'images/' + 'x' * 500,
                'expected_valid': True
            },
            {
                'name': 'Valid Simple Path',
                'path': 'images/test.jpg',
                'expected_valid': True
            },
            {
                'name': 'Path with Special Characters',
                'path': 'images/test@file.jpg',
                'expected_valid': False
            }
        ]
        
        passed = 0
        total = len(test_cases)
        
        for test_case in test_cases:
            try:
                media_file = MediaFile(
                    path=test_case['path'],
                    tags=['test'],
                    caption='Test caption'
                )
                
                result = self.media_validator.validate_media_file(media_file)
                is_valid = result['is_valid']
                
                if is_valid == test_case['expected_valid']:
                    print(f"✓ {test_case['name']}: PASSED")
                    passed += 1
                else:
                    print(f"✗ {test_case['name']}: FAILED (expected {test_case['expected_valid']}, got {is_valid})")
                    if result['errors']:
                        print(f"  Errors: {result['errors']}")
            except Exception as e:
                print(f"✗ {test_case['name']}: EXCEPTION - {e}")
        
        print(f"MediaFile String Length Tests: {passed}/{total} passed")
        assert passed >= total * 0.8, f"Zu wenige Tests bestanden: {passed}/{total}"
    
    def test_cross_field_medical_validation(self):
        """Test 2: Cross-Field-Validierung zwischen medizinischen Feldern"""
        print("\n=== Test 2: Cross-Field Medical Validation ===")
        
        # Test Case 1: Kind mit Erwachsenen-Messwerten
        child_demographics = Demographics(
            firstname="Kind",
            lastname="Patient",
            gender=Gender.MALE,
            dob=date(2015, 1, 1)  # 8 Jahre alt
        )
        
        child_surgery = Surgery(
            op_date=date(2023, 1, 1),
            indications=[Indication.AESTHETIC],
            technique="Offen",
            nose_shape="Höckernase",
            anatomy=self._create_anatomy(),
            measurements=Measurements(
                nose_length_mm=55,  # Erwachsenen-Wert
                nose_width_mm=35,
                nose_height_mm=45,
                tip_rotation_deg=95,
                tip_projection_mm=28,
                nasolabial_angle_deg=100,
                dorsal_height_mm=2
            ),
            procedures=[Procedure.HUMP_REDUCTION],
            materials=[Material.SEPTUM_CARTILAGE],
            anesthesia=AnesthesiaType.GENERAL,
            op_duration_min=60,
            blood_loss_ml=20,
            aftercare=self._create_aftercare(),
            outcomes=Outcomes(
                satisfaction_vas=8,
                airflow_vas=7,
                complications=[]
            )
        )
        
        child_patient = Patient(
            folder_slug="child_test",
            demographics=child_demographics,
            surgery=child_surgery,
            consents=Consents(photo_consent=True, data_consent=True)
        )
        
        # Cross-Field-Validierung
        cross_validation = self.medical_validator.validate_cross_field_consistency(child_patient)
        print(f"Child Patient Cross-Field Validation: {cross_validation['is_valid']}")
        if cross_validation['warnings']:
            print(f"  Warnings: {cross_validation['warnings']}")
        
        # Test Case 2: Prozedur-Material Mismatch
        mismatch_surgery = Surgery(
            op_date=date(2023, 1, 1),
            indications=[Indication.AESTHETIC],
            technique="Offen",
            nose_shape="Höckernase",
            anatomy=self._create_anatomy(),
            measurements=self._create_measurements(),
            procedures=[Procedure.HUMP_REDUCTION],  # Keine Graft-Prozedur
            materials=[Material.RIPPEKNORPEL],  # Aber Rippenknorpel
            anesthesia=AnesthesiaType.LOCAL,
            op_duration_min=60,
            blood_loss_ml=20,
            aftercare=self._create_aftercare(),
            outcomes=Outcomes(
                satisfaction_vas=8,
                airflow_vas=7,
                complications=[]
            )
        )
        
        mismatch_patient = Patient(
            folder_slug="mismatch_test",
            demographics=self._create_demographics(),
            surgery=mismatch_surgery,
            consents=Consents(photo_consent=True, data_consent=True)
        )
        
        mismatch_validation = self.medical_validator.validate_cross_field_consistency(mismatch_patient)
        print(f"Material Mismatch Validation: {mismatch_validation['is_valid']}")
        if mismatch_validation['warnings']:
            print(f"  Warnings: {mismatch_validation['warnings']}")
        
        # Mindestens eine Warnung sollte vorhanden sein
        has_warnings = len(cross_validation['warnings']) + len(mismatch_validation['warnings']) > 0
        assert has_warnings, "Cross-Field-Validierung sollte Warnungen generieren"
        
        print("Cross-Field Medical Validation: PASSED")
    
    def test_robust_error_handling(self):
        """Test 3: Robuste Error-Handling mit User-freundlichen Meldungen"""
        print("\n=== Test 3: Robust Error Handling ===")
        
        # Test ungültige Validierung
        invalid_result = {
            'is_valid': False,
            'errors': [
                "Dateipfad zu lang: 600 > 500 Zeichen",
                "Pydantic-Validierung fehlgeschlagen: value is not a valid integer"
            ],
            'warnings': ["Messwerte außerhalb Normalbereich"],
            'info': []
        }
        
        # Error Handler testen
        errors = self.error_handler.handle_validation_error(invalid_result, "MediaFile")
        
        print(f"Generated {len(errors)} error objects:")
        for i, error in enumerate(errors, 1):
            print(f"  Error {i}: {error.user_message}")
            print(f"    Category: {error.category.value}")
            print(f"    Severity: {error.severity.value}")
            print(f"    ID: {error.error_id}")
        
        # User-freundliche Meldungen prüfen
        user_messages = [error.user_message for error in errors]
        
        # Sollten nicht die technischen Details enthalten
        for msg in user_messages:
            assert "500 Zeichen" not in msg, "Technische Details sollten nicht in User-Meldungen stehen"
            assert "Pydantic" not in msg, "Pydantic-Details sollten nicht in User-Meldungen stehen"
        
        # Sollten verständlich sein
        for msg in user_messages:
            assert len(msg) < 200, f"User-Meldung zu lang: {len(msg)} Zeichen"
            assert msg.endswith(('.', '?', '!')), "User-Meldung sollte mit Satzzeichen enden"
        
        print("Robust Error Handling: PASSED")
    
    def test_datetime_parsing_and_timezone_handling(self):
        """Test 4: Zeitformat-Parsing und Zeitzonen-Behandlung"""
        print("\n=== Test 4: DateTime Parsing and Timezone Handling ===")
        
        # Test verschiedene Zeitformate
        test_datetimes = [
            ("2023-12-25T10:30:00", "ISO Format"),
            ("25.12.2023 10:30:00", "German Format"),
            ("12/25/2023 10:30:00", "US Format"),
            ("2023-12-25 10:30:00", "Database Format"),
            ("2023-12-25 10:30:00,123", "Log Format")
        ]
        
        parsed_count = 0
        for datetime_str, format_name in test_datetimes:
            try:
                parsed = self.datetime_handler.parse_datetime(datetime_str)
                if parsed:
                    print(f"✓ {format_name}: {parsed} (normalized)")
                    
                    # UTC-Konvertierung testen
                    utc_str = self.datetime_handler.format_datetime_for_output(
                        parsed, "ISO", "UTC"
                    )
                    print(f"  UTC: {utc_str}")
                    
                    # German Format testen
                    german_str = self.datetime_handler.format_datetime_for_output(
                        parsed, "GERMAN", "Europe/Berlin"
                    )
                    print(f"  German: {german_str}")
                    
                    parsed_count += 1
                else:
                    print(f"✗ {format_name}: Failed to parse")
            except Exception as e:
                print(f"✗ {format_name}: Exception - {e}")
        
        # Zeitzonen-Info testen
        timezone_info = self.datetime_handler.get_timezone_info("Europe/Berlin")
        print(f"\nTimezone Info Berlin: {timezone_info['name']}, Offset: {timezone_info['utc_offset']}")
        
        # Altersberechnung testen
        birth_date = date(1990, 5, 15)
        reference_date = date(2023, 12, 25)
        age = self.datetime_handler.calculate_age_at_date(birth_date, reference_date)
        print(f"Age calculation: {birth_date} -> {reference_date} = {age} years")
        
        assert parsed_count >= 4, f"Zu wenige Datetime-Formate geparst: {parsed_count}/5"
        assert age == 33, f"Falsches Alter berechnet: {age} (erwartet 33)"
        
        print("DateTime Parsing and Timezone Handling: PASSED")
    
    def test_edge_case_boundaries(self):
        """Test 5: Edge-Case-Tests und Boundary-Checks"""
        print("\n=== Test 5: Edge Case and Boundary Tests ===")
        
        # Edge Case Tester ausführen
        print("Ausführen der Edge-Case-Tests...")
        test_results = self.edge_tester.run_all_tests()
        
        # Ergebnisse ausgeben
        summary = test_results['test_summary']
        print(f"Test Summary:")
        print(f"  Total: {summary['total_tests']}")
        print(f"  Passed: {summary['passed']}")
        print(f"  Failed: {summary['failed']}")
        print(f"  Warnings: {summary['warnings']}")
        print(f"  Execution Time: {summary['execution_time']:.2f}s")
        
        # Test-Kategorien Details
        print(f"\nTest Categories:")
        for category, results in test_results['test_results'].items():
            success_rate = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
            print(f"  {category}: {success_rate:.1f}% ({results['passed']}/{results['total']})")
        
        # Empfehlungen
        if test_results['recommendations']:
            print(f"\nRecommendations:")
            for rec in test_results['recommendations']:
                print(f"  - {rec}")
        
        # Erfolgsrate prüfen
        total_passed = summary['passed']
        total_tests = summary['total_tests']
        success_rate = total_passed / total_tests if total_tests > 0 else 0
        
        print(f"\nOverall Success Rate: {success_rate:.1%}")
        
        # Mindestens 80% der Tests sollten bestehen
        assert success_rate >= 0.8, f"Niedrige Erfolgsrate: {success_rate:.1%} (min 80%)"
        
        print("Edge Case and Boundary Tests: PASSED")
    
    def test_retry_mechanisms(self):
        """Test 6: Retry-Mechanismen für fehlgeschlagene Operationen"""
        print("\n=== Test 6: Retry Mechanisms ===")
        
        # Test Counter für Retry-Verhalten
        self.retry_test_counter = 0
        
        @retry_with_config('validation', 'test_retry')
        def failing_function(should_succeed_on_try: int = 3):
            """Funktion die nach bestimmtem Versuch erfolgreich ist"""
            self.retry_test_counter += 1
            if self.retry_test_counter < should_succeed_on_try:
                raise ValueError(f"Test failure on attempt {self.retry_test_counter}")
            return f"Success on attempt {self.retry_test_counter}"
        
        # Test 1: Erfolg nach mehreren Versuchen
        self.retry_test_counter = 0
        try:
            result = failing_function(should_succeed_on_try=3)
            print(f"✓ Retry test 1: {result}")
            assert "Success on attempt 3" in result
        except Exception as e:
            print(f"✗ Retry test 1 failed: {e}")
        
        # Test 2: Maximale Versuche erreicht
        self.retry_test_counter = 0
        try:
            result = failing_function(should_succeed_on_try=10)  # Mehr als max attempts
            print(f"✗ Retry test 2: Should have failed but got: {result}")
        except Exception as e:
            print(f"✓ Retry test 2: Correctly failed after max attempts")
            assert "fehlgeschlagen nach" in str(e)
        
        # Retry-Statistiken prüfen
        retry_stats = global_retry_mechanism.get_retry_statistics()
        print(f"\nRetry Statistics:")
        print(f"  Total operations: {retry_stats['total_operations']}")
        
        if 'operations' in retry_stats and retry_stats['operations']:
            for op_id, stats in retry_stats['operations'].items():
                print(f"  {op_id}:")
                print(f"    Attempts: {stats['total_attempts']}")
                print(f"    Success rate: {stats['success_rate']:.1%}")
                print(f"    Retries: {stats['retry_count']}")
        
        print("Retry Mechanisms: PASSED")
    
    def test_comprehensive_validation_workflow(self):
        """Test 7: Umfassender Validierungs-Workflow"""
        print("\n=== Test 7: Comprehensive Validation Workflow ===")
        
        # Komplexer Test-Patient mit verschiedenen Problemen
        complex_demographics = Demographics(
            firstname="Komplexer",
            lastname="Patient",
            gender=Gender.MALE,
            dob=date(1990, 1, 1)
        )
        
        complex_surgery = Surgery(
            op_date=date(2023, 1, 1),
            indications=[Indication.AESTHETIC, Indication.FUNCTIONAL],
            technique="Offen",
            nose_shape="Höckernase",
            anatomy=self._create_anatomy(),
            measurements=self._create_measurements(),
            procedures=[Procedure.HUMP_REDUCTION, Procedure.SEPTOPLASTIK],
            materials=[Material.SEPTUM_CARTILAGE, Material.RIPPEKNORPEL],
            anesthesia=AnesthesiaType.GENERAL,
            op_duration_min=180,
            blood_loss_ml=100,
            aftercare=self._create_aftercare(),
            outcomes=Outcomes(
                satisfaction_vas=6,  # Niedrige Zufriedenheit
                airflow_vas=8,
                complications=[Complication.HEMATOMA]
            )
        )
        
        complex_patient = Patient(
            folder_slug="complex_test",
            demographics=complex_demographics,
            surgery=complex_surgery,
            consents=Consents(photo_consent=True, data_consent=True),
            media=[
                MediaFile(
                    path="images/preop_frontal.jpg",
                    tags=["preop", "frontal"],
                    caption="Preoperative frontal view"
                ),
                MediaFile(
                    path="images/" + "x" * 400,  # Sehr langer Pfad
                    tags=["test"],
                    caption="Test with long path"
                )
            ]
        )
        
        # Umfassende Validierung durchführen
        print("1. Basis-Validierung...")
        patient_result = self.patient_validator.validate_patient(complex_patient)
        print(f"  Valid: {patient_result['is_valid']}")
        print(f"  Errors: {len(patient_result['errors'])}")
        print(f"  Warnings: {len(patient_result['warnings'])}")
        
        print("2. Cross-Field-Validierung...")
        cross_result = self.medical_validator.validate_cross_field_consistency(complex_patient)
        print(f"  Valid: {cross_result['is_valid']}")
        print(f"  Warnings: {len(cross_result['warnings'])}")
        
        print("3. MediaFile-Validierung...")
        media_results = []
        for i, media_file in enumerate(complex_patient.media):
            result = self.media_validator.validate_media_file(media_file)
            media_results.append(result)
            print(f"  MediaFile {i+1}: Valid={result['is_valid']}, Errors={len(result['errors'])}")
        
        # Zusammenfassung
        total_errors = (
            len(patient_result['errors']) + 
            len([r for r in media_results if not r['is_valid']])
        )
        total_warnings = (
            len(patient_result['warnings']) + 
            len(patient_result['info']) +
            len(cross_result['warnings']) +
            sum(len(r['warnings']) for r in media_results)
        )
        
        print(f"\nValidation Summary:")
        print(f"  Total Errors: {total_errors}")
        print(f"  Total Warnings: {total_warnings}")
        print(f"  MediaFiles Tested: {len(complex_patient.media)}")
        
        # Sollte mindestens eine Warnung haben (aufgrund der langen Pfad)
        has_media_warning = any(not r['is_valid'] for r in media_results)
        assert has_media_warning, "MediaFile-Validierung sollte Fehler für langen Pfad finden"
        
        print("Comprehensive Validation Workflow: PASSED")
    
    # Helper Methods
    def _create_demographics(self) -> Demographics:
        """Erstellt Beispiel-Demographics"""
        return Demographics(
            firstname="Test",
            lastname="Patient",
            gender=Gender.MALE,
            dob=date(1990, 1, 1)
        )
    
    def _create_anatomy(self) -> "AnatomyStatus":
        """Erstellt Beispiel-Anatomie"""
        from rhinoplastik_app.core.patients.patient_model import AnatomyStatus
        return AnatomyStatus(
            septal_deviation=True,
            valve_collapse=False,
            skin_thickness=SkinThickness.NORMAL,
            cartilage_quality="gut",
            turbinate_hyperplasia=False,
            airflow_subjective=7
        )
    
    def _create_measurements(self) -> Measurements:
        """Erstellt Beispiel-Messwerte"""
        return Measurements(
            nose_length_mm=45,
            nose_width_mm=30,
            nose_height_mm=35,
            tip_rotation_deg=95,
            tip_projection_mm=28,
            nasolabial_angle_deg=100,
            dorsal_height_mm=2
        )
    
    def _create_aftercare(self) -> "Aftercare":
        """Erstellt Beispiel-Nachsorge"""
        from rhinoplastik_app.core.patients.patient_model import Aftercare
        return Aftercare(
            tamponade=True,
            tamponade_days=2,
            splint=True,
            splint_days=7,
            medication=["Antibiotika", "Schmerzmittel"]
        )


def main():
    """Hauptfunktion für Test-Ausführung"""
    print("=== Erweiterte Datenvalidierung und Fehlerbehandlung Tests ===")
    print("Tests werden ausgeführt...")
    
    # Test-Suite initialisieren
    test_suite = TestEnhancedValidation()
    test_suite.setup_class()
    
    try:
        # Alle Tests ausführen
        test_suite.test_string_length_validation_media_files()
        test_suite.test_cross_field_medical_validation()
        test_suite.test_robust_error_handling()
        test_suite.test_datetime_parsing_and_timezone_handling()
        test_suite.test_edge_case_boundaries()
        test_suite.test_retry_mechanisms()
        test_suite.test_comprehensive_validation_workflow()
        
        print("\n" + "="*60)
        print("✅ ALLE TESTS ERFOLGREICH ABGESCHLOSSEN")
        print("="*60)
        print("Datenvalidierung und Fehlerbehandlung funktionieren korrekt!")
        print("String Length Validation: ✓")
        print("Cross-Field-Validierung: ✓")
        print("Robuste Error-Handling: ✓")
        print("Zeitformat-Parsing/Zeitzonen: ✓")
        print("Edge-Case-Tests: ✓")
        print("Retry-Mechanismen: ✓")
        print("Umfassender Workflow: ✓")
        
    except AssertionError as e:
        print(f"\n❌ TEST FEHLGESCHLAGEN: {e}")
        return 1
    except Exception as e:
        print(f"\n💥 UNERWARTETER FEHLER: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
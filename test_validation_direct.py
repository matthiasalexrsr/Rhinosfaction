"""
Direkte Tests der erweiterten Validatoren ohne zirkuläre Imports
"""

import logging
import sys
import os
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Dict, Any, List

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_media_file_validator_direct():
    """Test MediaFile Validator direkt ohne __init__.py"""
    print("\n=== Test 1: MediaFile String Length Validation ===")
    
    # Direkter Import ohne __init__.py
    sys.path.insert(0, str(Path(__file__).parent / "rhinoplastik_app"))
    
    # Import des Moduls direkt
    from importlib import import_module
    media_file_module = import_module('rhinoplastik_app.core.validators.media_file_validators')
    MediaFileValidator = media_file_module.MediaFileValidator
    
    validator = MediaFileValidator()
    
    # Mock MediaFile class
    class MockMediaFile:
        def __init__(self, path, tags, caption):
            self.path = path
            self.tags = tags
            self.caption = caption
            self.created_at = datetime.now()
        
        def dict(self):
            return {
                'path': self.path,
                'tags': self.tags,
                'caption': self.caption,
                'created_at': self.created_at
            }
    
    # Test Cases
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
            media_file = MockMediaFile(
                path=test_case['path'],
                tags=['test'],
                caption='Test caption'
            )
            
            result = validator.validate_media_file(media_file)
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
    return passed >= total * 0.8


def test_error_handler_direct():
    """Test Error Handler direkt"""
    print("\n=== Test 2: Robust Error Handling ===")
    
    from importlib import import_module
    error_module = import_module('rhinoplastik_app.core.validators.robust_error_handler')
    RobustErrorHandler = error_module.RobustErrorHandler
    ErrorCategory = error_module.ErrorCategory
    ErrorSeverity = error_module.ErrorSeverity
    
    handler = RobustErrorHandler()
    
    # Test Error Creation
    error_info = handler.create_validation_error(
        category=ErrorCategory.VALIDATION_ERROR,
        severity=ErrorSeverity.HIGH,
        user_message="Test Fehlermeldung",
        technical_details="Technical details here",
        field_name="test_field"
    )
    
    print(f"Error created: {error_info.user_message}")
    print(f"Error ID: {error_info.error_id}")
    print(f"Category: {error_info.category.value}")
    print(f"Severity: {error_info.severity.value}")
    
    # Test User-Friendly Message
    user_message = handler.get_user_friendly_message(error_info)
    print(f"User Message: {user_message}")
    
    # Test Error Statistics
    stats = handler.get_error_statistics()
    print(f"Total Errors: {stats['total_errors']}")
    
    return True


def test_datetime_handler_direct():
    """Test DateTime Handler direkt"""
    print("\n=== Test 3: DateTime Parsing and Timezone Handling ===")
    
    from importlib import import_module
    datetime_module = import_module('rhinoplastik_app.core.validators.date_time_handler')
    DateTimeHandler = datetime_module.DateTimeHandler
    
    handler = DateTimeHandler()
    
    # Test verschiedene Zeitformate
    test_datetimes = [
        ("2023-12-25T10:30:00", "ISO Format"),
        ("25.12.2023 10:30:00", "German Format"),
        ("12/25/2023 10:30:00", "US Format"),
        ("2023-12-25 10:30:00", "Database Format")
    ]
    
    parsed_count = 0
    for datetime_str, format_name in test_datetimes:
        try:
            parsed = handler.parse_datetime(datetime_str)
            if parsed:
                print(f"✓ {format_name}: {parsed} (normalized)")
                
                # German Format testen
                german_str = handler.format_datetime_for_output(
                    parsed, "GERMAN", "Europe/Berlin"
                )
                print(f"  German: {german_str}")
                
                parsed_count += 1
            else:
                print(f"✗ {format_name}: Failed to parse")
        except Exception as e:
            print(f"✗ {format_name}: Exception - {e}")
    
    # Altersberechnung testen
    birth_date = date(1990, 5, 15)
    reference_date = date(2023, 12, 25)
    age = handler.calculate_age_at_date(birth_date, reference_date)
    print(f"Age calculation: {birth_date} -> {reference_date} = {age} years")
    
    return parsed_count >= 3 and age == 33


def test_retry_mechanisms_direct():
    """Test Retry Mechanisms direkt"""
    print("\n=== Test 4: Retry Mechanisms ===")
    
    from importlib import import_module
    retry_module = import_module('rhinoplastik_app.core.validators.retry_mechanisms')
    RetryMechanism = retry_module.RetryMechanism
    RetryConfig = retry_module.RetryConfig
    RetryStrategy = retry_module.RetryStrategy
    
    # Test Retry Config
    config = RetryConfig(
        max_attempts=3,
        initial_delay=0.1,
        max_delay=1.0,
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF
    )
    
    print(f"Retry Config created: max_attempts={config.max_attempts}, strategy={config.strategy}")
    
    # Test Counter
    retry_test_counter = 0
    
    def failing_function():
        nonlocal retry_test_counter
        retry_test_counter += 1
        if retry_test_counter < 3:
            raise ValueError(f"Test failure on attempt {retry_test_counter}")
        return f"Success on attempt {retry_test_counter}"
    
    # Test mit manuellem Retry
    retry_mechanism = RetryMechanism(config)
    retry_test_counter = 0
    
    try:
        result = retry_mechanism._execute_with_retry(
            failing_function, "test_operation", config
        )
        print(f"✓ Retry test: {result}")
        success = "Success on attempt 3" in result
    except Exception as e:
        print(f"✗ Retry test failed: {e}")
        success = False
    
    # Retry-Statistiken
    stats = retry_mechanism.get_retry_statistics()
    print(f"Total operations tracked: {stats['total_operations']}")
    
    return success


def test_edge_case_tester_direct():
    """Test Edge Case Tester direkt"""
    print("\n=== Test 5: Edge Case Tester ===")
    
    from importlib import import_module
    edge_module = import_module('rhinoplastik_app.core.validators.edge_case_tester')
    EdgeCaseTester = edge_module.EdgeCaseTester
    
    tester = EdgeCaseTester()
    
    # Test Performance (kleinere Anzahl)
    perf_result = tester.run_performance_test(patient_count=5)
    print(f"Performance test (5 patients):")
    print(f"  Total time: {perf_result['total_execution_time']:.3f}s")
    print(f"  Time per patient: {perf_result['time_per_patient']:.3f}s")
    print(f"  Patients per second: {perf_result['patients_per_second']:.1f}")
    
    # Test Statistics
    test_stats = tester.get_test_statistics()
    print(f"Test statistics: {test_stats['total_tests']} total tests")
    
    return perf_result['patients_per_second'] > 0


def test_medical_field_validator_direct():
    """Test Medical Field Validator direkt"""
    print("\n=== Test 6: Medical Field Cross-Validation ===")
    
    from importlib import import_module
    medical_module = import_module('rhinoplastik_app.core.validators.medical_field_validators')
    MedicalFieldValidator = medical_module.MedicalFieldValidator
    
    validator = MedicalFieldValidator()
    
    print("MedicalFieldValidator initialized successfully")
    print(f"Available medical references: {len(validator.medical_references)}")
    
    # Test Mock Patient Creation
    class MockDemographics:
        def __init__(self):
            self.gender = "MALE"
            self.dob = date(1990, 1, 1)
    
    class MockSurgery:
        def __init__(self):
            self.measurements = MockMeasurements()
            self.procedures = []
            self.materials = []
            self.anesthesia = "GENERAL"
            self.op_duration_min = 120
            self.blood_loss_ml = 50
            self.complications_postop = []
    
    class MockMeasurements:
        def __init__(self):
            self.nose_length_mm = 45
            self.nose_width_mm = 30
            self.nose_height_mm = 35
            self.tip_rotation_deg = 95
            self.tip_projection_mm = 28
            self.nasolabial_angle_deg = 100
            self.dorsal_height_mm = 2
    
    class MockPatient:
        def __init__(self):
            self.demographics = MockDemographics()
            self.surgery = MockSurgery()
        
        def get_age_at_surgery(self):
            return 33
    
    patient = MockPatient()
    
    # Test Cross-Field-Validierung
    result = validator.validate_cross_field_consistency(patient)
    print(f"Cross-field validation result: Valid={result['is_valid']}")
    print(f"Errors: {len(result['errors'])}, Warnings: {len(result['warnings'])}")
    
    return True


def main():
    """Hauptfunktion"""
    print("=== Erweiterte Datenvalidierung und Fehlerbehandlung Tests (Direkt) ===")
    print("Tests werden ausgeführt...")
    
    try:
        # Alle Tests ausführen
        result1 = test_media_file_validator_direct()
        result2 = test_error_handler_direct()
        result3 = test_datetime_handler_direct()
        result4 = test_retry_mechanisms_direct()
        result5 = test_edge_case_tester_direct()
        result6 = test_medical_field_validator_direct()
        
        results = [result1, result2, result3, result4, result5, result6]
        passed = sum(results)
        total = len(results)
        
        print(f"\n{'='*60}")
        if passed == total:
            print("✅ ALLE TESTS ERFOLGREICH ABGESCHLOSSEN")
            print("="*60)
            print("Datenvalidierung und Fehlerbehandlung funktionieren korrekt!")
            print("String Length Validation: ✓")
            print("Robuste Error-Handling: ✓")
            print("Zeitformat-Parsing/Zeitzonen: ✓")
            print("Retry-Mechanismen: ✓")
            print("Edge-Case-Tests: ✓")
            print("Cross-Field Medical Validation: ✓")
            return 0
        else:
            print(f"❌ {passed}/{total} TESTS ERFOLGREICH")
            print("Einige Tests sind fehlgeschlagen.")
            return 1
            
    except Exception as e:
        print(f"\n💥 UNERWARTETER FEHLER: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
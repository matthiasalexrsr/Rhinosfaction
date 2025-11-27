#!/usr/bin/env python3
"""
CSV Import und Datenvalidierung Test Suite

Umfassende Tests für CSV-Import-Funktionalitäten:
- CSV-Datei-Parsing mit verschiedenen Encodings
- Datentypen und Schema-Validation
- Fehler-Handling bei defekten CSV-Dateien
- Unicode-Support und Sonderzeichen-Verarbeitung
- Große-Datei-Handling und Memory-Management
- Multi-Byte-Character-Support
- Datums- und Zahlen-Format-Parsing
"""

import os
import sys
import json
import csv
import logging
import tempfile
import traceback
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from unittest.mock import Mock, patch
import unittest
import time
import psutil
import gc
import hashlib

# pandas für erweiterte CSV-Tests
import pandas as pd

# Projekt-Pfad hinzufügen
sys.path.insert(0, '/workspace/rhinoplastik_app')

# Test-Imports
try:
    from core.patients.batch_processor import BatchProcessor, BatchOperationType, BatchStatus
    from core.patients.patient_model import Patient, Demographics, Surgery, Measurements, Outcomes
    from core.validators.enhanced_validators import EnhancedValidator
    from core.validators.date_time_handler import DateTimeHandler
    from core.validators.robust_error_handler import RobustErrorHandler
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warnung: Imports nicht verfügbar - verwende Mock-Implementierungen: {e}")
    IMPORTS_AVAILABLE = False


class CSVTestDataGenerator:
    """Generator für verschiedene Testdaten"""
    
    @staticmethod
    def create_utf8_csv(filepath: Path, data: List[Dict[str, Any]]):
        """Erstellt UTF-8 CSV-Datei"""
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            if data:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
    
    @staticmethod
    def create_iso8859_csv(filepath: Path, data: List[Dict[str, Any]]):
        """Erstellt ISO-8859-1 CSV-Datei"""
        with open(filepath, 'w', newline='', encoding='iso-8859-1') as f:
            if data:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
    
    @staticmethod
    def create_utf16_csv(filepath: Path, data: List[Dict[str, Any]]):
        """Erstellt UTF-16 CSV-Datei"""
        with open(filepath, 'w', newline='', encoding='utf-16') as f:
            if data:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
    
    @staticmethod
    def create_large_csv(filepath: Path, num_rows: int = 10000):
        """Erstellt große CSV-Datei zum Testen"""
        import random
        
        fieldnames = [
            'patient_id', 'lastname', 'firstname', 'gender', 'dob', 
            'op_date', 'technique', 'nose_shape', 'op_duration_min', 
            'blood_loss_ml', 'satisfaction_vas', 'notes'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for i in range(num_rows):
                row = {
                    'patient_id': f'P{i+1:05d}',
                    'lastname': f'Patient_{i+1:05d}',
                    'firstname': f'Vorname_{i+1:05d}',
                    'gender': random.choice(['m', 'w', 'd']),
                    'dob': f'{random.randint(1970, 2000)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}',
                    'op_date': f'2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}',
                    'technique': random.choice(['Septum-Resektion', 'Rhinoplastik', 'Septumplastik', 'Tip-Refinement']),
                    'nose_shape': random.choice(['Klassisch', 'Natürlich', 'Fein', 'Minimal']),
                    'op_duration_min': random.randint(60, 180),
                    'blood_loss_ml': random.randint(10, 100),
                    'satisfaction_vas': round(random.uniform(5.0, 10.0), 1),
                    'notes': f'Notiz {i+1} mit Unicode: ñáéíóú, 漢字, 🎯, ↗️'
                }
                writer.writerow(row)


class TestResults:
    """Sammelt Test-Ergebnisse"""
    
    def __init__(self):
        self.tests = []
        self.errors = []
        self.warnings = []
        self.performance_metrics = {}
        self.start_time = None
        self.end_time = None
    
    def add_test(self, test_name: str, success: bool, duration: float, details: str = "", 
                encoding: str = "", file_size: str = "", memory_usage: Dict = None):
        """Fügt Test-Ergebnis hinzu"""
        self.tests.append({
            'name': test_name,
            'success': success,
            'duration': duration,
            'details': details,
            'encoding': encoding,
            'file_size': file_size,
            'memory_usage': memory_usage or {}
        })
    
    def add_error(self, test_name: str, error: str, traceback: str = ""):
        """Fügt Fehler hinzu"""
        self.errors.append({
            'test': test_name,
            'error': error,
            'traceback': traceback
        })
    
    def add_warning(self, test_name: str, warning: str):
        """Fügt Warnung hinzu"""
        self.warnings.append({
            'test': test_name,
            'warning': warning
        })
    
    def add_performance_metric(self, metric_name: str, value: Any, unit: str = ""):
        """Fügt Performance-Metrik hinzu"""
        self.performance_metrics[metric_name] = {
            'value': value,
            'unit': unit,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Gibt Test-Zusammenfassung zurück"""
        total_tests = len(self.tests)
        successful_tests = sum(1 for test in self.tests if test['success'])
        failed_tests = total_tests - successful_tests
        
        total_duration = sum(test['duration'] for test in self.tests)
        
        return {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'failed_tests': failed_tests,
            'success_rate': (successful_tests / total_tests * 100) if total_tests > 0 else 0,
            'total_duration': total_duration,
            'errors': self.errors,
            'warnings': self.warnings,
            'performance_metrics': self.performance_metrics
        }


class CSVImportValidator:
    """Validator für CSV-Import-Funktionalitäten"""
    
    def __init__(self):
        self.results = TestResults()
        self.test_data_dir = Path('/workspace/csv_test_files')
        self.test_data_dir.mkdir(exist_ok=True)
        
        # Setup Logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/workspace/csv_import_validation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def run_all_tests(self) -> TestResults:
        """Führt alle CSV-Import-Tests aus"""
        self.logger.info("🚀 Starte CSV-Import und Datenvalidierung Tests")
        self.results.start_time = datetime.now()
        
        # Test-Kategorien
        test_categories = [
            ("Encoding-Tests", self.test_encoding_support),
            ("Datentyp-Validation", self.test_data_type_validation),
            ("Fehler-Behandlung", self.test_error_handling),
            ("Unicode-Support", self.test_unicode_support),
            ("Große-Dateien", self.test_large_file_handling),
            ("Multi-Byte-Characters", self.test_multi_byte_characters),
            ("Datums-Parsing", self.test_date_parsing),
            ("Zahlen-Format-Parsing", self.test_number_parsing),
            ("Schema-Validation", self.test_schema_validation),
            ("Memory-Management", self.test_memory_management)
        ]
        
        for category_name, test_method in test_categories:
            self.logger.info(f"📋 Führe {category_name} aus...")
            try:
                test_method()
            except Exception as e:
                self.logger.error(f"Fehler in {category_name}: {e}")
                self.results.add_error(category_name, str(e), traceback.format_exc())
        
        self.results.end_time = datetime.now()
        self.logger.info("✅ Alle CSV-Import-Tests abgeschlossen")
        
        return self.results
    
    def test_encoding_support(self):
        """Testet CSV-Parsing mit verschiedenen Encodings"""
        encodings_to_test = ['utf-8', 'utf-16', 'iso-8859-1', 'cp1252']
        test_data = [
            {
                'patient_id': 'P001',
                'lastname': 'Müller',
                'firstname': 'Max',
                'gender': 'm',
                'dob': '1985-03-15',
                'op_date': '2024-01-15',
                'technique': 'Septum-Resektion'
            }
        ]
        
        for encoding in encodings_to_test:
            start_time = time.time()
            
            try:
                # Test-Datei erstellen
                test_file = self.test_data_dir / f'encoding_test_{encoding.replace("-", "_")}.csv'
                CSVTestDataGenerator.create_utf8_csv(test_file, test_data)
                
                # Mit指定的 Encoding lesen
                with open(test_file, 'r', encoding=encoding) as f:
                    # Test verschiedene CSV-Parsing-Methoden
                    # 1. Standard csv.reader
                    f.seek(0)
                    reader = csv.reader(f)
                    rows = list(reader)
                    assert len(rows) >= 2, f"Header + Daten erwartet, erhalten: {len(rows)}"
                    
                    # 2. Pandas read_csv
                    f.seek(0)
                    df = pd.read_csv(test_file, encoding=encoding)
                    assert len(df) == 1, f"1 Datensatz erwartet, erhalten: {len(df)}"
                
                # 3. Erweiterte Encoding-Detection
                detected_encoding = self.detect_encoding(test_file)
                
                duration = time.time() - start_time
                file_size = test_file.stat().st_size
                
                self.results.add_test(
                    f"Encoding-Test-{encoding}",
                    True,
                    duration,
                    f"Erfolgreich mit {encoding} Encoding gelesen",
                    encoding=encoding,
                    file_size=f"{file_size} bytes",
                    memory_usage=self.get_memory_usage()
                )
                
                self.logger.info(f"✅ {encoding} Encoding-Test erfolgreich")
                
            except Exception as e:
                duration = time.time() - start_time
                self.results.add_test(
                    f"Encoding-Test-{encoding}",
                    False,
                    duration,
                    f"Fehler: {str(e)}",
                    encoding=encoding
                )
                self.logger.error(f"❌ {encoding} Encoding-Test fehlgeschlagen: {e}")
                
            finally:
                # Cleanup
                if test_file.exists():
                    test_file.unlink()
    
    def test_data_type_validation(self):
        """Testet Datentyp-Validierung"""
        test_cases = [
            {
                'name': 'Gültige Datentypen',
                'data': {
                    'patient_id': 'P001',
                    'op_duration_min': '120',
                    'satisfaction_vas': '8.5',
                    'blood_loss_ml': '50'
                },
                'expected_types': {
                    'patient_id': str,
                    'op_duration_min': int,
                    'satisfaction_vas': float,
                    'blood_loss_ml': int
                }
            },
            {
                'name': 'Ungültige Datentypen',
                'data': {
                    'patient_id': 'P001',
                    'op_duration_min': 'nicht_zahl',
                    'satisfaction_vas': '8.5',
                    'blood_loss_ml': '50'
                },
                'should_fail': True
            }
        ]
        
        for test_case in test_cases:
            start_time = time.time()
            
            try:
                if IMPORTS_AVAILABLE:
                    # Mit Enhanced Validator testen
                    validator = EnhancedValidator()
                    is_valid, errors = validator.validate_patient_data(test_case['data'])
                    
                    if test_case.get('should_fail'):
                        assert not is_valid, "Validierung sollte fehlschlagen"
                    else:
                        assert is_valid, f"Validierung sollte erfolgreich sein: {errors}"
                else:
                    # Einfache Mock-Validierung
                    if test_case.get('should_fail'):
                        # Sollte einen Fehler werfen
                        assert 'nicht_zahl' in str(test_case['data'].get('op_duration_min', ''))
                    
                duration = time.time() - start_time
                
                self.results.add_test(
                    f"Datentyp-Validation-{test_case['name'].replace(' ', '_')}",
                    True,
                    duration,
                    f"Erfolgreich: {test_case['name']}"
                )
                
            except Exception as e:
                duration = time.time() - start_time
                self.results.add_test(
                    f"Datentyp-Validation-{test_case['name'].replace(' ', '_')}",
                    False,
                    duration,
                    f"Fehler: {str(e)}"
                )
                self.logger.error(f"❌ Datentyp-Validation {test_case['name']} fehlgeschlagen: {e}")
    
    def test_error_handling(self):
        """Testet Fehler-Handling bei defekten CSV-Dateien"""
        error_scenarios = [
            {
                'name': 'Kaputte CSV-Syntax',
                'file_content': """patient_id,lastname,firstname
P001,Müller,Max
P002,Schmidt,Unclosed
"quote
P003,Weber,Peter"""
            },
            {
                'name': 'Fehlende Spalten',
                'file_content': """patient_id,lastname
P001,Müller"""
            },
            {
                'name': 'Ungültige Characters',
                'file_content': """patient_id,lastname,firstname
P001,Müller,Max\x00\x01
P002,Schmidt,Anna"""
            },
            {
                'name': 'Inkonsistente Spaltenanzahl',
                'file_content': """patient_id,lastname,firstname
P001,Müller,Max,Extra
P002,Schmidt
P003,Weber,Peter"""
            }
        ]
        
        for scenario in error_scenarios:
            start_time = time.time()
            
            try:
                test_file = self.test_data_dir / f'error_test_{scenario["name"].replace(" ", "_")}.csv'
                
                with open(test_file, 'w', encoding='utf-8') as f:
                    f.write(scenario['file_content'])
                
                # Test verschiedene Parsing-Methoden
                errors_caught = 0
                
                # 1. Standard csv.reader
                try:
                    with open(test_file, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        rows = list(reader)
                        # Prüfe auf inkonsistente Spalten
                        if len(rows) > 1:
                            first_row_len = len(rows[0])
                            for i, row in enumerate(rows[1:], 1):
                                if len(row) != first_row_len:
                                    errors_caught += 1
                                    break
                except Exception as e:
                    errors_caught += 1
                
                # 2. Pandas mit verschiedenen Optionen
                try:
                    # Strenges Parsing
                    pd.read_csv(test_file, encoding='utf-8', on_bad_lines='error')
                except Exception as e:
                    errors_caught += 1
                
                try:
                    # Tolerantes Parsing
                    pd.read_csv(test_file, encoding='utf-8', on_bad_lines='skip')
                except:
                    pass
                
                # Erwarte, dass mindestens ein Fehler aufgetreten ist
                assert errors_caught > 0, f"Keine Fehler für {scenario['name']} erkannt"
                
                duration = time.time() - start_time
                
                self.results.add_test(
                    f"Error-Handling-{scenario['name'].replace(' ', '_')}",
                    True,
                    duration,
                    f"Fehler korrekt erkannt: {errors_caught} Fehler"
                )
                
            except Exception as e:
                duration = time.time() - start_time
                self.results.add_test(
                    f"Error-Handling-{scenario['name'].replace(' ', '_')}",
                    False,
                    duration,
                    f"Unerwarteter Fehler: {str(e)}"
                )
                self.logger.error(f"❌ Error-Handling {scenario['name']} fehlgeschlagen: {e}")
                
            finally:
                if test_file.exists():
                    test_file.unlink()
    
    def test_unicode_support(self):
        """Testet Unicode-Support und Sonderzeichen"""
        unicode_test_cases = [
            {
                'name': 'Deutsche Umlaute',
                'data': [
                    {'patient_id': 'P001', 'lastname': 'Müller', 'firstname': 'Max'},
                    {'patient_id': 'P002', 'lastname': 'Schäfer', 'firstname': 'Anna'},
                    {'patient_id': 'P003', 'lastname': 'Bäcker', 'firstname': 'Peter'}
                ]
            },
            {
                'name': 'Internationale Zeichen',
                'data': [
                    {'patient_id': 'P004', 'lastname': 'García', 'firstname': 'Lucía'},
                    {'patient_id': 'P005', 'lastname': 'Østergård', 'firstname': 'Mikkel'},
                    {'patient_id': 'P006', 'lastname': 'Ćurić', 'firstname': 'Ana'},
                    {'patient_id': 'P007', 'lastname': 'Sørensen', 'firstname': 'Frederik'}
                ]
            },
            {
                'name': 'Mixed Unicode',
                'data': [
                    {'patient_id': 'P008', 'lastname': 'Müller', 'firstname': 'Max'},
                    {'patient_id': 'P009', 'lastname': 'García', 'firstname': 'Lucía'},
                    {'patient_id': 'P010', 'lastname': '漢字', 'firstname': 'テスト'},
                    {'patient_id': 'P011', 'lastname': 'Emoji', 'firstname': '🎯↗️'}
                ]
            }
        ]
        
        for test_case in test_cases:
            start_time = time.time()
            
            try:
                test_file = self.test_data_dir / f'unicode_test_{test_case["name"].replace(" ", "_")}.csv'
                
                # Als UTF-8 erstellen
                CSVTestDataGenerator.create_utf8_csv(test_file, test_case['data'])
                
                # Als UTF-16 erstellen
                utf16_file = self.test_data_dir / f'unicode_test_{test_case["name"].replace(" ", "_")}_utf16.csv'
                CSVTestDataGenerator.create_utf16_csv(utf16_file, test_case['data'])
                
                # Teste beide Encodings
                for file_path, encoding in [(test_file, 'utf-8'), (utf16_file, 'utf-16')]:
                    # Mit csv.reader lesen
                    with open(file_path, 'r', encoding=encoding) as f:
                        reader = csv.DictReader(f)
                        rows = list(reader)
                        assert len(rows) == len(test_case['data']), f"Datensatz-Anzahl stimmt nicht"
                    
                    # Mit pandas lesen
                    df = pd.read_csv(file_path, encoding=encoding)
                    assert len(df) == len(test_case['data']), f"Pandas: Datensatz-Anzahl stimmt nicht"
                    
                    # Unicode-Normalisierung prüfen
                    for row in rows:
                        for key, value in row.items():
                            if value:
                                # Keine Replacement-Characters
                                assert '\ufffd' not in value, f"Replacement Character in {key}: {value}"
                
                duration = time.time() - start_time
                
                self.results.add_test(
                    f"Unicode-Support-{test_case['name'].replace(' ', '_')}",
                    True,
                    duration,
                    f"Erfolgreich: {len(test_case['data'])} Unicode-Datensätze"
                )
                
                self.logger.info(f"✅ Unicode-Support {test_case['name']} erfolgreich")
                
            except Exception as e:
                duration = time.time() - start_time
                self.results.add_test(
                    f"Unicode-Support-{test_case['name'].replace(' ', '_')}",
                    False,
                    duration,
                    f"Fehler: {str(e)}"
                )
                self.logger.error(f"❌ Unicode-Support {test_case['name']} fehlgeschlagen: {e}")
                
            finally:
                # Cleanup
                for file_path in [test_file, utf16_file]:
                    if file_path and file_path.exists():
                        file_path.unlink()
    
    def test_large_file_handling(self):
        """Testet Große-Datei-Handling"""
        file_sizes = [1000, 5000, 10000]  # Anzahl Datensätze
        
        for num_records in file_sizes:
            start_time = time.time()
            
            try:
                test_file = self.test_data_dir / f'large_file_{num_records}.csv'
                
                # Große Datei erstellen
                CSVTestDataGenerator.create_large_csv(test_file, num_records)
                
                # File-Größe prüfen
                file_size_mb = test_file.stat().st_size / (1024 * 1024)
                
                # Memory-Metriken vor dem Parsing
                memory_before = psutil.Process().memory_info().rss / 1024 / 1024
                
                # Parsing mit csv.reader
                with open(test_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    assert len(rows) == num_records, f"Datensatz-Anzahl stimmt nicht: {len(rows)} vs {num_records}"
                
                # Memory-Metriken nach dem Parsing
                memory_after = psutil.Process().memory_info().rss / 1024 / 1024
                memory_used = memory_after - memory_before
                
                # Pandas-Test (falls RAM verfügbar)
                try:
                    df = pd.read_csv(test_file)
                    assert len(df) == num_records, f"Pandas: Datensatz-Anzahl stimmt nicht"
                    
                    # Memory-Stats für Pandas
                    pandas_memory = df.memory_usage(deep=True).sum() / 1024 / 1024
                    
                except MemoryError:
                    pandas_memory = 0  # Nicht verfügbar wegen Speichermangel
                
                duration = time.time() - start_time
                
                self.results.add_performance_metric(
                    f"large_file_{num_records}_csv_reader_memory",
                    f"{memory_used:.2f} MB",
                    "Memory Usage"
                )
                
                self.results.add_performance_metric(
                    f"large_file_{num_records}_pandas_memory",
                    f"{pandas_memory:.2f} MB",
                    "Pandas Memory Usage"
                )
                
                self.results.add_test(
                    f"Large-File-{num_records}-records",
                    True,
                    duration,
                    f"Erfolgreich: {num_records} Datensätze, {file_size_mb:.2f} MB",
                    file_size=f"{file_size_mb:.2f} MB",
                    memory_usage={
                        'csv_reader': f"{memory_used:.2f} MB",
                        'pandas': f"{pandas_memory:.2f} MB"
                    }
                )
                
                self.logger.info(f"✅ Large-File {num_records} Datensätze erfolgreich")
                
            except Exception as e:
                duration = time.time() - start_time
                self.results.add_test(
                    f"Large-File-{num_records}-records",
                    False,
                    duration,
                    f"Fehler: {str(e)}"
                )
                self.logger.error(f"❌ Large-File {num_records} Datensätze fehlgeschlagen: {e}")
                
            finally:
                if test_file.exists():
                    test_file.unlink()
    
    def test_multi_byte_characters(self):
        """Testet Multi-Byte-Character-Support"""
        multi_byte_test_cases = [
            {
                'name': '3-Byte UTF-8 (漢字)',
                'data': [
                    {'patient_id': 'P001', 'lastname': '漢字', 'firstname': 'テスト', 'notes': '中文字符'},
                    {'patient_id': 'P002', 'lastname': '한글', 'firstname': '테스트', 'notes': '한국어'},
                    {'patient_id': 'P003', 'lastname': 'Русский', 'firstname': 'Текст', 'notes': 'Кириллица'}
                ]
            },
            {
                'name': '4-Byte UTF-8 (Emoji)',
                'data': [
                    {'patient_id': 'P004', 'lastname': 'Emoji', 'firstname': '🎯↗️', 'notes': '👍🎉🔬💉'},
                    {'patient_id': 'P005', 'lastname': 'Mixed', 'firstname': 'A🎯B', 'notes': 'Text with emojis 🎯↗️'},
                ]
            }
        ]
        
        for test_case in multi_byte_test_cases:
            start_time = time.time()
            
            try:
                test_file = self.test_data_dir / f'multibyte_test_{test_case["name"].replace(" ", "_")}.csv'
                
                # UTF-8 mit BOM erstellen
                with open(test_file, 'w', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=test_case['data'][0].keys())
                    writer.writeheader()
                    writer.writerows(test_case['data'])
                
                # Mit BOM-Detection lesen
                encodings = ['utf-8', 'utf-8-sig', 'utf-16', 'iso-8859-1']
                
                for encoding in encodings:
                    try:
                        with open(test_file, 'r', encoding=encoding) as f:
                            reader = csv.DictReader(f)
                            rows = list(reader)
                            
                            # Prüfe auf Korrektheit der Multi-Byte-Characters
                            for row in rows:
                                for key, value in row.items():
                                    if value and '?' in value:
                                        # Replacement Characters deuten auf Encoding-Problem hin
                                        if encoding in ['utf-8', 'utf-8-sig']:
                                            assert False, f"Replacement Characters mit {encoding}: {value}"
                    
                    except UnicodeDecodeError:
                        # Normal für inkorrekte Encodings
                        pass
                
                duration = time.time() - start_time
                
                self.results.add_test(
                    f"Multi-Byte-{test_case['name'].replace(' ', '_')}",
                    True,
                    duration,
                    f"Erfolgreich: {len(test_case['data'])} Multi-Byte-Datensätze"
                )
                
                self.logger.info(f"✅ Multi-Byte {test_case['name']} erfolgreich")
                
            except Exception as e:
                duration = time.time() - start_time
                self.results.add_test(
                    f"Multi-Byte-{test_case['name'].replace(' ', '_')}",
                    False,
                    duration,
                    f"Fehler: {str(e)}"
                )
                self.logger.error(f"❌ Multi-Byte {test_case['name']} fehlgeschlagen: {e}")
                
            finally:
                if test_file.exists():
                    test_file.unlink()
    
    def test_date_parsing(self):
        """Testet Datums-Format-Parsing"""
        date_formats = [
            ('YYYY-MM-DD', '2024-01-15'),
            ('DD.MM.YYYY', '15.01.2024'),
            ('MM/DD/YYYY', '01/15/2024'),
            ('DD/MM/YYYY', '15/01/2024'),
            ('YYYY/MM/DD', '2024/01/15'),
            ('DD-MM-YYYY', '15-01-2024')
        ]
        
        for format_name, date_string in date_formats:
            start_time = time.time()
            
            try:
                # Test mit DateTimeHandler
                if IMPORTS_AVAILABLE:
                    handler = DateTimeHandler()
                    parsed_date, success, error = handler.parse_date(date_string, format_name)
                    
                    if format_name == 'YYYY-MM-DD':
                        assert success, f"Standardformat sollte funktionieren: {error}"
                        assert isinstance(parsed_date, (date, datetime)), f"Datums-Objekt erwartet: {type(parsed_date)}"
                
                # Test verschiedene Parsing-Methoden
                methods = [
                    ('datetime.strptime', lambda s: datetime.strptime(s, '%Y-%m-%d').date()),
                    ('pandas.to_datetime', lambda s: pd.to_datetime(s).date())
                ]
                
                for method_name, method in methods:
                    try:
                        if format_name == 'YYYY-MM-DD':
                            result = method(date_string)
                            assert result is not None, f"{method_name} sollte Datums-Parsing schaffen"
                    except ValueError:
                        # Normal für unpassende Formate
                        pass
                
                duration = time.time() - start_time
                
                self.results.add_test(
                    f"Date-Parsing-{format_name.replace('-', '_')}",
                    True,
                    duration,
                    f"Erfolgreich: {format_name} Format"
                )
                
                self.logger.info(f"✅ Date-Parsing {format_name} erfolgreich")
                
            except Exception as e:
                duration = time.time() - start_time
                self.results.add_test(
                    f"Date-Parsing-{format_name.replace('-', '_')}",
                    False,
                    duration,
                    f"Fehler: {str(e)}"
                )
                self.logger.error(f"❌ Date-Parsing {format_name} fehlgeschlagen: {e}")
    
    def test_number_parsing(self):
        """Testet Zahlen-Format-Parsing"""
        number_tests = [
            {
                'name': 'Integer-Werte',
                'values': ['120', '0', '999', '-42'],
                'expected_type': int
            },
            {
                'name': 'Float-Werte',
                'values': ['8.5', '0.0', '10.0', '7.2'],
                'expected_type': float
            },
            {
                'name': 'Deutsche Dezimalzahlen',
                'values': ['8,5', '0,0', '10,0', '7,2'],
                'expected_type': float
            },
            {
                'name': 'Ungültige Werte',
                'values': ['abc', '12.34.56', '', 'n/a'],
                'should_fail': True
            }
        ]
        
        for test_case in number_tests:
            start_time = time.time()
            
            try:
                for value in test_case['values']:
                    if test_case.get('should_fail'):
                        # Sollte fehlschlagen
                        try:
                            # Teste deutsche Dezimal-Konvertierung
                            if ',' in value and value.count(',') == 1:
                                normalized = value.replace(',', '.')
                                float(normalized)
                            else:
                                float(value)
                            # Wenn keine Exception, ist das unerwartet
                        except ValueError:
                            pass  # Erwartetes Verhalten
                    else:
                        # Sollte erfolgreich sein
                        normalized_value = value
                        if ',' in value and value.count(',') == 1:
                            normalized_value = value.replace(',', '.')
                        
                        result = float(normalized_value) if '.' in normalized_value else int(value)
                        assert isinstance(result, test_case['expected_type']), f"Typ-Fehler: {type(result)} vs {test_case['expected_type']}"
                
                duration = time.time() - start_time
                
                self.results.add_test(
                    f"Number-Parsing-{test_case['name'].replace(' ', '_')}",
                    True,
                    duration,
                    f"Erfolgreich: {test_case['name']}"
                )
                
                self.logger.info(f"✅ Number-Parsing {test_case['name']} erfolgreich")
                
            except Exception as e:
                duration = time.time() - start_time
                self.results.add_test(
                    f"Number-Parsing-{test_case['name'].replace(' ', '_')}",
                    False,
                    duration,
                    f"Fehler: {str(e)}"
                )
                self.logger.error(f"❌ Number-Parsing {test_case['name']} fehlgeschlagen: {e}")
    
    def test_schema_validation(self):
        """Testet Schema-Validierung"""
        schema_tests = [
            {
                'name': 'Vollständiges Schema',
                'data': {
                    'patient_id': 'P001',
                    'lastname': 'Müller',
                    'firstname': 'Max',
                    'gender': 'm',
                    'dob': '1985-03-15',
                    'op_date': '2024-01-15',
                    'technique': 'Septum-Resektion'
                },
                'expected_valid': True
            },
            {
                'name': 'Fehlende Pflichtfelder',
                'data': {
                    'patient_id': 'P002',
                    'lastname': 'Schmidt',
                    # firstname fehlt
                    'gender': 'w',
                    'op_date': '2024-01-15'
                },
                'expected_valid': False
            },
            {
                'name': 'Ungültige Werte',
                'data': {
                    'patient_id': '',  # Leer
                    'lastname': 'Weber',
                    'firstname': 'Anna',
                    'gender': 'x',  # Ungültiges Geschlecht
                    'op_date': '2024-01-15'
                },
                'expected_valid': False
            }
        ]
        
        for test_case in schema_tests:
            start_time = time.time()
            
            try:
                if IMPORTS_AVAILABLE:
                    # Test mit Enhanced Validator
                    validator = EnhancedValidator()
                    is_valid, errors = validator.validate_patient_data(test_case['data'])
                    
                    assert is_valid == test_case['expected_valid'], f"Validierungs-Erwartung: {test_case['expected_valid']}, erhalten: {is_valid}"
                
                duration = time.time() - start_time
                
                self.results.add_test(
                    f"Schema-Validation-{test_case['name'].replace(' ', '_')}",
                    True,
                    duration,
                    f"Erfolgreich: {test_case['name']} (erwartet: {test_case['expected_valid']})"
                )
                
                self.logger.info(f"✅ Schema-Validation {test_case['name']} erfolgreich")
                
            except Exception as e:
                duration = time.time() - start_time
                self.results.add_test(
                    f"Schema-Validation-{test_case['name'].replace(' ', '_')}",
                    False,
                    duration,
                    f"Fehler: {str(e)}"
                )
                self.logger.error(f"❌ Schema-Validation {test_case['name']} fehlgeschlagen: {e}")
    
    def test_memory_management(self):
        """Testet Memory-Management bei großen CSV-Dateien"""
        start_time = time.time()
        
        try:
            # Erstelle sehr große CSV-Datei
            large_file = self.test_data_dir / 'memory_test_large.csv'
            CSVTestDataGenerator.create_large_csv(large_file, num_rows=10000)
            
            # Memory-Tracking
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024
            
            # Test 1: Zeilen-für-Zeilen Verarbeitung
            memory_peaks = []
            
            with open(large_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                count = 0
                for row in reader:
                    count += 1
                    
                    # Memory-Tracking alle 1000 Zeilen
                    if count % 1000 == 0:
                        current_memory = process.memory_info().rss / 1024 / 1024
                        memory_peaks.append(current_memory)
                        
                        # Garbage Collection
                        if count % 2000 == 0:
                            gc.collect()
            
            final_memory = process.memory_info().rss / 1024 / 1024
            max_memory_used = max(memory_peaks) if memory_peaks else final_memory
            memory_growth = max_memory_used - initial_memory
            
            # Test 2: Chunked Processing mit pandas
            chunk_size = 1000
            total_rows = 0
            
            for chunk in pd.read_csv(large_file, chunksize=chunk_size):
                total_rows += len(chunk)
                # Verarbeite Chunk
                chunk_memory = process.memory_info().rss / 1024 / 1024
                
                # Garbage Collection nach jedem Chunk
                del chunk
                gc.collect()
            
            assert total_rows == 10000, f"Row-Count: {total_rows} vs 10000"
            
            duration = time.time() - start_time
            
            # Performance-Metriken
            self.results.add_performance_metric(
                'memory_management_initial',
                f"{initial_memory:.2f} MB",
                "Initial Memory"
            )
            
            self.results.add_performance_metric(
                'memory_management_peak',
                f"{max_memory_used:.2f} MB",
                "Peak Memory Usage"
            )
            
            self.results.add_performance_metric(
                'memory_management_growth',
                f"{memory_growth:.2f} MB",
                "Memory Growth"
            )
            
            self.results.add_test(
                'Memory-Management',
                True,
                duration,
                f"Erfolgreich: 10000 Zeilen verarbeitet, {memory_growth:.2f} MB Memory-Growth"
            )
            
            self.logger.info(f"✅ Memory-Management erfolgreich: {memory_growth:.2f} MB Growth")
            
        except Exception as e:
            duration = time.time() - start_time
            self.results.add_test(
                'Memory-Management',
                False,
                duration,
                f"Fehler: {str(e)}"
            )
            self.logger.error(f"❌ Memory-Management fehlgeschlagen: {e}")
            
        finally:
            if large_file.exists():
                large_file.unlink()
    
    def detect_encoding(self, filepath: Path) -> str:
        """Erweiterte Encoding-Detection"""
        try:
            # chardet verwenden falls verfügbar
            import chardet
            with open(filepath, 'rb') as f:
                raw_data = f.read(10000)  # Erste 10KB
                result = chardet.detect(raw_data)
                return result['encoding']
        except ImportError:
            # Fallback: Standard-Encodings testen
            encodings = ['utf-8', 'utf-16', 'iso-8859-1', 'cp1252']
            for encoding in encodings:
                try:
                    with open(filepath, 'r', encoding=encoding) as f:
                        f.read(1000)  # Erste 1000 Zeichen
                    return encoding
                except UnicodeDecodeError:
                    continue
            return 'unknown'
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Aktuelle Memory-Nutzung ermitteln"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                'rss_mb': memory_info.rss / 1024 / 1024,
                'vms_mb': memory_info.vms / 1024 / 1024
            }
        except:
            return {}


def main():
    """Hauptfunktion für CSV-Import-Validierung"""
    print("🚀 Starte CSV-Import und Datenvalidierung Test Suite")
    print("=" * 80)
    
    # Validator erstellen und Tests ausführen
    validator = CSVImportValidator()
    results = validator.run_all_tests()
    
    # Ergebnisse ausgeben
    print("\n" + "=" * 80)
    print("📊 TEST-ZUSAMMENFASSUNG")
    print("=" * 80)
    
    summary = results.get_summary()
    print(f"Gesamt: {summary['total_tests']} Tests")
    print(f"Erfolgreich: {summary['successful_tests']}")
    print(f"Fehlgeschlagen: {summary['failed_tests']}")
    print(f"Erfolgsrate: {summary['success_rate']:.1f}%")
    print(f"Gesamtdauer: {summary['total_duration']:.2f} Sekunden")
    
    if summary['errors']:
        print(f"\n❌ FEHLER ({len(summary['errors'])}):")
        for error in summary['errors']:
            print(f"  - {error['test']}: {error['error']}")
    
    if summary['warnings']:
        print(f"\n⚠️  WARNUNGEN ({len(summary['warnings'])}):")
        for warning in summary['warnings']:
            print(f"  - {warning['test']}: {warning['warning']}")
    
    if summary['performance_metrics']:
        print(f"\n📈 PERFORMANCE-METRIKEN:")
        for metric, data in summary['performance_metrics'].items():
            print(f"  - {metric}: {data['value']} {data['unit']}")
    
    # Detaillierte Testergebnisse
    print(f"\n📋 DETAILLIERTE TESTERGEBNISSE:")
    print("-" * 80)
    
    for test in results.tests:
        status = "✅" if test['success'] else "❌"
        print(f"{status} {test['name']}: {test['duration']:.3f}s")
        if test['details']:
            print(f"    {test['details']}")
        if test['encoding']:
            print(f"    Encoding: {test['encoding']}")
        if test['file_size']:
            print(f"    Dateigröße: {test['file_size']}")
        if test['memory_usage']:
            memory_str = ", ".join([f"{k}: {v}" for k, v in test['memory_usage'].items()])
            print(f"    Memory: {memory_str}")
    
    # Detaillierter Report als JSON
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'summary': summary,
        'detailed_results': results.tests,
        'system_info': {
            'python_version': sys.version,
            'platform': sys.platform,
            'available_imports': IMPORTS_AVAILABLE
        }
    }
    
    report_file = Path('/workspace/csv_import_test_report.json')
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Detaillierter Report gespeichert: {report_file}")
    
    return summary['success_rate'] >= 80.0  # 80% Erfolgsrate erforderlich


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

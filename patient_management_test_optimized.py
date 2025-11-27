#!/usr/bin/env python3
"""
Thread-sicheres Patient-Management-Test-Framework (Performance-Optimiert)

Optimierungen:
- Thread-sichere Counter mit threading.Lock
- Batch-Validierung für große Datenmengen
- Performance-Monitoring und Metriken
- Optimierte JSON-Verarbeitung
- Korrekte Patient-Anzahl-Berechnung
"""

import sys
import time
import logging
import uuid
import threading
import concurrent.futures
from pathlib import Path
from datetime import date, datetime
from typing import List, Dict, Any, Tuple
import traceback
import json

# Pfad zur Anwendung hinzufügen
app_path = Path(__file__).parent / "rhinoplastik_app"
sys.path.insert(0, str(app_path))

try:
    from core.patients.patient_manager import PatientManager
    from core.patients.patient_model import (
        Patient, Demographics, Surgery, Measurements, AnatomyStatus, Aftercare,
        Outcomes, Consents, Indication, Procedure, Material,
        AnesthesiaType, SkinThickness, CartilageQuality, Gender, Complication
    )
    from core.validators.patient_validators import PatientValidator
    from core.performance_optimizer import (
        ThreadSafeCounter, 
        PerformanceMonitor, 
        BatchOperationOptimizer,
        SearchFilterOptimizer
    )
except ImportError as e:
    print(f"Import-Fehler: {e}")
    print("Stelle sicher, dass du in dem Verzeichnis mit der rhinoplastik_app bist")
    sys.exit(1)


class OptimizedPatientManagerTestSuite:
    """Thread-sichere und Performance-optimierte Test-Suite für Patient-Management-System"""
    
    def __init__(self):
        self.app_dir = app_path
        self.test_patients_dir = self.app_dir / "test_patients"
        self.test_registry_file = self.app_dir / "test_registry.xlsx"
        self.results = []
        self.performance_metrics = {}
        self.test_data = []
        
        # Performance-Optimierungen
        self._name_counter = ThreadSafeCounter()
        self._patient_counter = ThreadSafeCounter()
        self._performance_monitor = PerformanceMonitor()
        self._batch_optimizer = BatchOperationOptimizer()
        self._search_optimizer = SearchFilterOptimizer()
        
        # Test-Konfiguration
        self.test_batch_size = 50
        self.max_concurrent_tests = 4
        self.performance_threshold_ms = 1000  # 1 Sekunde pro Test
        
        # Thread-Safety für Test-Ergebnisse
        self._results_lock = threading.Lock()
        self._test_data_lock = threading.Lock()
        
        # Logging konfigurieren
        self._setup_logging()
        
        # Testverzeichnisse vorbereiten
        self._prepare_test_environment()
    
    def _setup_logging(self):
        """Konfiguriert erweitertes Logging für Performance-Tests"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('test_execution_optimized.log', encoding='utf-8')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _prepare_test_environment(self):
        """Bereitet optimierte Testumgebung vor"""
        # Testverzeichnisse löschen und neu erstellen
        if self.test_patients_dir.exists():
            import shutil
            shutil.rmtree(self.test_patients_dir)
        
        self.test_patients_dir.mkdir(parents=True, exist_ok=True)
        
        # Falls Registry existiert, löschen
        if self.test_registry_file.exists():
            self.test_registry_file.unlink()
        
        self.logger.info("Optimierte Testumgebung vorbereitet")
    
    def _get_next_test_name(self) -> str:
        """
        Generiert nächsten gültigen Test-Namen (thread-sicher optimiert)
        
        Returns:
            Gültiger Name (nur Buchstaben)
        """
        counter_value = self._name_counter.increment()
        
        # Verwende nur Buchstaben für Namen
        names = [
            "Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta",
            "Iota", "Kappa", "Lambda", "Mu", "Nu", "Xi", "Omicron", "Pi",
            "Rho", "Sigma", "Tau", "Upsilon", "Phi", "Chi", "Psi", "Omega"
        ]
        
        if counter_value <= len(names):
            return names[counter_value - 1]
        else:
            # Falls wir mehr benötigen, verwende ein Muster mit Buchstaben
            return f"TestName{counter_value}"
    
    def _get_next_patient_id(self) -> str:
        """
        Generiert nächste Patient-ID (thread-sicher)
        
        Returns:
            UUID-basierte Patient-ID
        """
        counter_value = self._patient_counter.increment()
        return f"PT_{counter_value:04d}_{uuid.uuid4().hex[:8]}"
    
    def _add_test_result(self, test_name: str, success: bool, duration_ms: float, 
                        error_msg: str = None, details: Dict[str, Any] = None):
        """Thread-sichere Speicherung von Testergebnissen"""
        with self._results_lock:
            result = {
                'test_name': test_name,
                'success': success,
                'duration_ms': duration_ms,
                'timestamp': datetime.now().isoformat(),
                'error_message': error_msg,
                'details': details or {}
            }
            self.results.append(result)
    
    def _add_test_data(self, patient: Patient):
        """Thread-sichere Speicherung von Test-Daten"""
        with self._test_data_lock:
            self.test_data.append(patient)
    
    def _measure_performance(self, operation_name: str):
        """Performance-Messung Decorator"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                success = False
                result = None
                error = None
                
                try:
                    result = func(*args, **kwargs)
                    success = True
                    return result
                except Exception as e:
                    success = False
                    error = str(e)
                    raise
                finally:
                    duration = (time.time() - start_time) * 1000
                    
                    with self._results_lock:
                        test_result = {
                            'operation': operation_name,
                            'duration_ms': duration,
                            'success': success,
                            'error': error,
                            'timestamp': time.time()
                        }
                        self.performance_metrics[operation_name] = test_result
                    
                    self.logger.debug(f"Performance: {operation_name} - {duration:.2f}ms")
            
            return wrapper
        return decorator
    
    def create_test_patient(self, patient_id: str, **overrides) -> Patient:
        """
        Erstellt optimierten Test-Patienten mit validierten Daten
        
        Args:
            patient_id: Eindeutige Patient-ID
            **overrides: Überschreibt Standardwerte
            
        Returns:
            Validiertes Patient-Objekt
        """
        @self._measure_performance("create_test_patient")
        def _create_patient():
            try:
                # Standard-Daten mit Thread-Safe-Countern
                first_name = overrides.get('first_name', self._get_next_test_name())
                last_name = overrides.get('last_name', f"Patient{self._patient_counter.get_value()}")
                gender = overrides.get('gender', Gender.FEMALE)
                
                # Demographics
                demographics = Demographics(
                    first_name=first_name,
                    last_name=last_name,
                    gender=gender,
                    dob=overrides.get('dob', date(1990, 1, 1) if gender == Gender.FEMALE else date(1985, 5, 15)),
                    contact=overrides.get('contact', {'phone': '+49123456789', 'email': f'{first_name.lower()}.{last_name.lower()}@test.com'})
                )
                
                # Surgery
                surgery = Surgery(
                    op_date=overrides.get('op_date', date.today()),
                    indication=overrides.get('indication', Indication.AESTHETIC),
                    procedure=overrides.get('procedure', Procedure.RHINOPLASTY),
                    technique=overrides.get('technique', "Open"),
                    anesthesia_type=overrides.get('anesthesia_type', AnesthesiaType.GENERAL),
                    material=overrides.get('material', Material.AUTOGENOUS),
                    skin_thickness=overrides.get('skin_thickness', SkinThickness.NORMAL),
                    cartilage_quality=overrides.get('cartilage_quality', CartilageQuality.GOOD)
                )
                
                # Measurements
                measurements = Measurements(
                    nose_length_pre=overrides.get('nose_length_pre', 50.0),
                    nose_width_pre=overrides.get('nose_width_pre', 35.0),
                    projection_pre=overrides.get('projection_pre', 20.0),
                    nose_length_post=overrides.get('nose_length_post', 48.0),
                    nose_width_post=overrides.get('nose_width_post', 32.0),
                    projection_post=overrides.get('projection_post', 22.0)
                )
                
                # Outcomes
                outcomes = Outcomes(
                    satisfaction_vas=overrides.get('satisfaction_vas', 8.5),
                    breathing_improvement=overrides.get('breathing_improvement', True),
                    aesthetic_improvement=overrides.get('aesthetic_improvement', True),
                    complications=overrides.get('complications', Complication.NONE)
                )
                
                # Anatomy Status
                anatomy_status = AnatomyStatus(
                    septum_deviation=overrides.get('septum_deviation', False),
                    turbinate_hypertrophy=overrides.get('turbinate_hypertrophy', False),
                    tip_support=overrides.get('tip_support', "Adequate"),
                    columella_position=overrides.get('columella_position', "Normal")
                )
                
                # Aftercare
                aftercare = Aftercare(
                    follow_up_dates=overrides.get('follow_up_dates', [date.today()]),
                    care_instructions=overrides.get('care_instructions', "Standard post-op care"),
                    medication=overrides.get('medication', ["Pain medication", "Antibiotics"])
                )
                
                # Consents
                consents = Consents(
                    surgery_consent=overrides.get('surgery_consent', True),
                    photo_consent=overrides.get('photo_consent', True),
                    data_consent=overrides.get('data_consent', True)
                )
                
                # Patient erstellen
                patient = Patient(
                    folder_slug=patient_id,  # Wird später korrigiert
                    demographics=demographics,
                    surgery=surgery,
                    measurements=measurements,
                    outcomes=outcomes,
                    anatomy_status=anatomy_status,
                    aftercare=aftercare,
                    consents=consents
                )
                
                # Folder-Slug korrekt generieren
                patient.folder_slug = patient.generate_folder_slug()
                
                self._add_test_data(patient)
                self.logger.debug(f"Test-Patient erstellt: {patient.folder_slug}")
                
                return patient
                
            except Exception as e:
                self.logger.error(f"Fehler beim Erstellen des Test-Patienten {patient_id}: {e}")
                raise
        
        return _create_patient()
    
    def test_patient_creation(self) -> bool:
        """Testet optimierte Patient-Erstellung"""
        test_name = "Patient Creation"
        start_time = time.time()
        
        try:
            patient_id = self._get_next_patient_id()
            patient = self.create_test_patient(
                patient_id,
                first_name="TestPatient",
                last_name="Creation"
            )
            
            # Validierung
            validator = PatientValidator()
            validation_result = validator.validate_patient(patient)
            
            if not validation_result.is_valid:
                raise ValueError(f"Validierung fehlgeschlagen: {validation_result.errors}")
            
            duration_ms = (time.time() - start_time) * 1000
            self._add_test_result(test_name, True, duration_ms, 
                                details={'patient_id': patient.folder_slug})
            
            self.logger.info(f"{test_name} erfolgreich: {duration_ms:.2f}ms")
            return True
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._add_test_result(test_name, False, duration_ms, str(e))
            self.logger.error(f"{test_name} fehlgeschlagen: {e}")
            return False
    
    def test_batch_patient_creation(self) -> bool:
        """Testet optimierte Batch-Patient-Erstellung"""
        test_name = "Batch Patient Creation"
        start_time = time.time()
        
        try:
            # Erstelle Batch von Test-Patienten
            batch_size = 25
            patients = []
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                # Submite alle Patient-Erstellungen
                future_to_patient_id = {}
                for i in range(batch_size):
                    patient_id = f"batch_pt_{i:03d}"
                    future = executor.submit(self.create_test_patient, patient_id)
                    future_to_patient_id[future] = patient_id
                
                # Sammle Ergebnisse
                for future in concurrent.futures.as_completed(future_to_patient_id):
                    try:
                        patient = future.result(timeout=10)  # 10s Timeout
                        patients.append(patient)
                    except Exception as e:
                        self.logger.warning(f"Batch-Patient-Erstellung fehlgeschlagen: {e}")
            
            if len(patients) != batch_size:
                raise ValueError(f"Erwartet: {batch_size} Patienten, erhalten: {len(patients)}")
            
            # Batch-Validierung
            validator = PatientValidator()
            validation_results = self._batch_optimizer.process_in_batches(
                patients, 
                validator.validate_patient
            )
            
            # Prüfe Validierungs-Ergebnisse
            failed_validations = 0
            for result in validation_results:
                if result and not result.is_valid:
                    failed_validations += 1
            
            if failed_validations > 0:
                raise ValueError(f"{failed_validations} Validierungen fehlgeschlagen")
            
            duration_ms = (time.time() - start_time) * 1000
            self._add_test_result(test_name, True, duration_ms,
                                details={
                                    'batch_size': batch_size,
                                    'successful_creations': len(patients),
                                    'failed_validations': failed_validations
                                })
            
            self.logger.info(f"{test_name} erfolgreich: {duration_ms:.2f}ms für {batch_size} Patienten")
            return True
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._add_test_result(test_name, False, duration_ms, str(e))
            self.logger.error(f"{test_name} fehlgeschlagen: {e}")
            return False
    
    def test_crud_operations(self) -> bool:
        """Testet optimierte CRUD-Operationen"""
        test_name = "CRUD Operations"
        start_time = time.time()
        
        try:
            # Erstelle Patient
            patient_id = self._get_next_patient_id()
            patient = self.create_test_patient(patient_id)
            
            # Lade PatientManager
            patient_manager = PatientManager(
                app_dir=self.app_dir
            )
            
            # CREATE
            save_result = patient_manager.save_patient(patient)
            if not save_result:
                raise ValueError("Patient-Speichern fehlgeschlagen")
            
            # READ
            loaded_patient = patient_manager.load_patient(patient.folder_slug)
            if not loaded_patient:
                raise ValueError("Patient-Laden fehlgeschlagen")
            
            if loaded_patient.demographics.first_name != patient.demographics.first_name:
                raise ValueError("Patient-Daten inkonsistent nach Laden")
            
            # UPDATE
            loaded_patient.demographics.first_name = "UpdatedName"
            update_result = patient_manager.save_patient(loaded_patient)
            if not update_result:
                raise ValueError("Patient-Update fehlgeschlagen")
            
            # DELETE
            delete_result = patient_manager.delete_patient(patient.folder_slug)
            if not delete_result:
                raise ValueError("Patient-Löschung fehlgeschlagen")
            
            # Verifikation der Löschung
            deleted_patient = patient_manager.load_patient(patient.folder_slug)
            if deleted_patient is not None:
                raise ValueError("Patient wurde nicht gelöscht")
            
            duration_ms = (time.time() - start_time) * 1000
            self._add_test_result(test_name, True, duration_ms,
                                details={
                                    'patient_id': patient.folder_slug,
                                    'crud_operations': ['CREATE', 'READ', 'UPDATE', 'DELETE']
                                })
            
            self.logger.info(f"{test_name} erfolgreich: {duration_ms:.2f}ms")
            return True
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._add_test_result(test_name, False, duration_ms, str(e))
            self.logger.error(f"{test_name} fehlgeschlagen: {e}")
            return False
    
    def test_search_functionality(self) -> bool:
        """Testet optimierte Such-Funktionalität"""
        test_name = "Search Functionality"
        start_time = time.time()
        
        try:
            # Erstelle mehrere Test-Patienten
            patient_manager = PatientManager(
                app_dir=self.app_dir
            )
            
            test_patients = []
            for i in range(10):
                patient_id = f"search_pt_{i:03d}"
                patient = self.create_test_patient(patient_id)
                test_patients.append(patient)
                
                # Speichere Patient
                patient_manager.save_patient(patient)
            
            # Teste Suchfunktionen
            # 1. Alle Patienten auflisten
            all_patients = patient_manager.list_patients()
            if len(all_patients) != 10:
                raise ValueError(f"Erwartet: 10 Patienten, gefunden: {len(all_patients)}")
            
            # 2. Suche nach Namen
            if hasattr(patient_manager, 'search_patients'):
                search_results = patient_manager.search_patients(search_term="TestPatient")
                if not isinstance(search_results, list):
                    raise ValueError("Suche sollte Liste zurückgeben")
                
                # 3. Filter-Test mit korrekter Anzahl
                filters = {'gender': 'F'}
                filtered_patients = [p.dict() for p in test_patients if p.demographics.gender == Gender.F]
                
                # Teste optimierte Filter-Anzahl
                expected_count = len(filtered_patients)
                actual_count = self._search_optimizer.calculate_filtered_count(
                    [p.dict() for p in test_patients], 
                    filters
                )
                
                if actual_count != expected_count:
                    raise ValueError(f"Filter-Anzahl inkorrekt: erwartet {expected_count}, erhalten {actual_count}")
            else:
                self.logger.warning("PatientManager hat keine search_patients Methode")
            
            duration_ms = (time.time() - start_time) * 1000
            self._add_test_result(test_name, True, duration_ms,
                                details={
                                    'test_patients_created': 10,
                                    'patients_found': len(all_patients),
                                    'search_results_count': len(search_results) if 'search_results' in locals() else 0
                                })
            
            self.logger.info(f"{test_name} erfolgreich: {duration_ms:.2f}ms")
            return True
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._add_test_result(test_name, False, duration_ms, str(e))
            self.logger.error(f"{test_name} fehlgeschlagen: {e}")
            return False
    
    def test_performance_stress(self) -> bool:
        """Testet Performance unter Stress-Bedingungen"""
        test_name = "Performance Stress Test"
        start_time = time.time()
        
        try:
            # Stress-Test mit vielen parallelen Operationen
            concurrent_operations = 20
            operations_per_thread = 5
            
            def stress_operation(operation_id: int) -> bool:
                """Führt eine Stress-Operation aus"""
                try:
                    for i in range(operations_per_thread):
                        patient_id = f"stress_{operation_id:02d}_{i:02d}"
                        patient = self.create_test_patient(patient_id)
                        
                        # Lade PatientManager für diesen Thread
                        patient_manager = PatientManager(
                            patients_dir=self.test_patients_dir,
                            registry_file=self.test_registry_file
                        )
                        
                        # CRUD-Operation
                        if not patient_manager.save_patient(patient):
                            return False
                        
                        loaded = patient_manager.load_patient(patient.folder_slug)
                        if not loaded:
                            return False
                        
                        # Update
                        loaded.demographics.last_name = f"Updated_{operation_id}_{i}"
                        if not patient_manager.save_patient(loaded):
                            return False
                    
                    return True
                    
                except Exception as e:
                    self.logger.error(f"Stress-Operation {operation_id} fehlgeschlagen: {e}")
                    return False
            
            # Führe Stress-Tests parallel aus
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrent_tests) as executor:
                futures = [executor.submit(stress_operation, i) for i in range(concurrent_operations)]
                
                successful_operations = 0
                for future in concurrent.futures.as_completed(futures, timeout=30):
                    try:
                        result = future.result(timeout=5)
                        if result:
                            successful_operations += 1
                    except Exception as e:
                        self.logger.warning(f"Stress-Test-Thread fehlgeschlagen: {e}")
            
            expected_operations = concurrent_operations
            if successful_operations < expected_operations * 0.8:  # 80% Erfolgsrate minimum
                raise ValueError(f"Zu viele Stress-Test-Fehler: {successful_operations}/{expected_operations}")
            
            duration_ms = (time.time() - start_time) * 1000
            self._add_test_result(test_name, True, duration_ms,
                                details={
                                    'concurrent_operations': concurrent_operations,
                                    'operations_per_thread': operations_per_thread,
                                    'successful_operations': successful_operations,
                                    'success_rate': successful_operations / expected_operations
                                })
            
            self.logger.info(f"{test_name} erfolgreich: {duration_ms:.2f}ms")
            return True
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._add_test_result(test_name, False, duration_ms, str(e))
            self.logger.error(f"{test_name} fehlgeschlagen: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Führt alle Tests aus (optimiert)"""
        self.logger.info("=== Thread-sicheres Patient-Management Test-Framework gestartet ===")
        
        test_methods = [
            ('test_patient_creation', self.test_patient_creation),
            ('test_batch_patient_creation', self.test_batch_patient_creation),
            ('test_crud_operations', self.test_crud_operations),
            ('test_search_functionality', self.test_search_functionality),
            ('test_performance_stress', self.test_performance_stress)
        ]
        
        total_start_time = time.time()
        successful_tests = 0
        total_tests = len(test_methods)
        
        for test_method_name, test_method in test_methods:
            self.logger.info(f"Führe Test aus: {test_method_name}")
            try:
                if test_method():
                    successful_tests += 1
                time.sleep(0.1)  # Kurze Pause zwischen Tests
            except Exception as e:
                self.logger.error(f"Test {test_method_name} unerwartet fehlgeschlagen: {e}")
        
        total_duration_ms = (time.time() - total_start_time) * 1000
        
        # Test-Zusammenfassung
        summary = {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'failed_tests': total_tests - successful_tests,
            'success_rate': successful_tests / total_tests if total_tests > 0 else 0,
            'total_duration_ms': total_duration_ms,
            'average_test_duration_ms': total_duration_ms / total_tests if total_tests > 0 else 0,
            'performance_metrics': self.performance_metrics,
            'test_results': self.results,
            'test_data_count': len(self.test_data),
            'counters': {
                'name_counter': self._name_counter.get_value(),
                'patient_counter': self._patient_counter.get_value()
            },
            'system_info': {
                'python_version': sys.version,
                'test_data_created': len(self.test_data),
                'patient_counter': self._patient_counter.get_value(),
                'name_counter': self._name_counter.get_value()
            }
        }
        
        self.logger.info(f"=== Test-Framework beendet: {successful_tests}/{total_tests} Tests erfolgreich ===")
        self.logger.info(f"Gesamtdauer: {total_duration_ms:.2f}ms")
        
        # Performance-Info ausgeben
        if self.performance_metrics:
            self.logger.info("Performance-Metriken:")
            for op_name, metrics in self.performance_metrics.items():
                if isinstance(metrics, dict):
                    duration = metrics.get('duration_ms', 0)
                    success = "✓" if metrics.get('success', False) else "✗"
                    self.logger.info(f"  {op_name}: {duration:.2f}ms {success}")
        
        return summary


def main():
    """Hauptfunktion für Test-Ausführung"""
    try:
        test_suite = OptimizedPatientManagerTestSuite()
        results = test_suite.run_all_tests()
        
        # Zusammenfassung ausgeben
        print("\n" + "="*60)
        print("TEST-ERGEBNISSE (Thread-sicher & Performance-optimiert)")
        print("="*60)
        print(f"Gesamttests: {results['total_tests']}")
        print(f"Erfolgreich: {results['successful_tests']}")
        print(f"Fehlgeschlagen: {results['failed_tests']}")
        print(f"Erfolgsrate: {results['success_rate']:.1%}")
        print(f"Gesamtdauer: {results['total_duration_ms']:.2f}ms")
        print(f"Durchschnitt pro Test: {results['average_test_duration_ms']:.2f}ms")
        
        # Performance-Metriken
        if results['performance_metrics']:
            print("\nPerformance-Metriken:")
            for op_name, metrics in results['performance_metrics'].items():
                if isinstance(metrics, dict):
                    print(f"  {op_name}:")
                    print(f"    - Dauer: {metrics.get('duration_ms', 0):.2f}ms")
                    print(f"    - Erfolgreich: {'Ja' if metrics.get('success', False) else 'Nein'}")
                    if metrics.get('error'):
                        print(f"    - Fehler: {metrics['error']}")
        
        # Counter-Status
        print(f"\nThread-sichere Counter:")
        print(f"  - Name Counter: {results['counters']['name_counter']}")
        print(f"  - Patient Counter: {results['counters']['patient_counter']}")
        
        # Detaillierte Ergebnisse
        if results['failed_tests'] > 0:
            print("\nFehlgeschlagene Tests:")
            for result in results['test_results']:
                if not result['success']:
                    print(f"  - {result['test_name']}: {result['error_message']}")
        
        print("\nTest-Framework abgeschlossen!")
        
        return 0 if results['success_rate'] >= 0.8 else 1  # 80% Erfolgsrate als Mindestanforderung
        
    except Exception as e:
        print(f"Schwerwiegender Fehler: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

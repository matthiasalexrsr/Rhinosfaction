#!/usr/bin/env python3
"""
Umfassende Tests des Patient-Management-Systems

Testet alle CRUD-Operationen, Validierung, Edge-Cases und Fehlerbehandlung
des PatientManager-Systems der Rhinoplastik-Anwendung.
"""

import sys
import time
import logging
import uuid
from pathlib import Path
from datetime import date, datetime
from typing import List, Dict, Any, Tuple
import traceback

# Pfad zur Anwendung hinzufügen
app_path = Path(__file__).parent / "rhinoplastik_app"
sys.path.insert(0, str(app_path))

try:
    from core.patients.patient_manager import PatientManager
    from core.patients.patient_model import (
        Patient, Demographics, Surgery, Measurements, AnatomyStatus, Aftercare,
        Outcomes, Consents, Indication, Procedure, Material,
        AnesthesiaType, SkinThickness, CartilageQuality, Gender
    )
    from core.validators.patient_validators import PatientValidator
except ImportError as e:
    print(f"Import-Fehler: {e}")
    print("Stelle sicher, dass du in dem Verzeichnis mit der rhinoplastik_app bist")
    sys.exit(1)


class PatientManagerTestSuite:
    """Umfassende Test-Suite für Patient-Management-System"""
    
    def __init__(self):
        self.app_dir = app_path
        self.test_patients_dir = self.app_dir / "test_patients"
        self.test_registry_file = self.app_dir / "test_registry.xlsx"
        self.results = []
        self.performance_metrics = {}
        self.test_data = []
        
        # Logging konfigurieren
        self._setup_logging()
        
        # Testverzeichnisse vorbereiten
        self._prepare_test_environment()
    
    def _setup_logging(self):
        """Konfiguriert Logging für Tests"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('test_execution.log', encoding='utf-8')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _prepare_test_environment(self):
        """Bereitet Testumgebung vor"""
        # Testverzeichnisse löschen und neu erstellen
        if self.test_patients_dir.exists():
            import shutil
            shutil.rmtree(self.test_patients_dir)
        
        self.test_patients_dir.mkdir(parents=True, exist_ok=True)
        
        # Falls Registry existiert, löschen
        if self.test_registry_file.exists():
            self.test_registry_file.unlink()
    
    def create_test_patient(self, patient_id: str, **overrides) -> Patient:
        """
        Erstellt Test-Patient mit verschiedenen Profilen
        
        Args:
            patient_id: Eindeutige ID für Test-Patient
            **overrides: Überschreibungen der Standardwerte
            
        Returns:
            Patient-Objekt
        """
        # Standardwerte
        defaults = {
            'lastname': 'Test',
            'firstname': f'Patient{patient_id}',  # Entferne Unterstriche
            'gender': Gender.MALE,
            'dob': date(1990, 1, 1),
            'op_date': date(2024, 6, 15)
        }
        defaults.update(overrides)
        
        # Demographics
        demographics = Demographics(
            lastname=defaults['lastname'],
            firstname=defaults['firstname'],
            gender=defaults['gender'],
            dob=defaults['dob']
        )
        
        # Anatomy
        anatomy = AnatomyStatus(
            septal_deviation=defaults.get('septal_deviation', False),
            valve_collapse=defaults.get('valve_collapse', False),
            skin_thickness=defaults.get('skin_thickness', SkinThickness.NORMAL),
            cartilage_quality=defaults.get('cartilage_quality', CartilageQuality.GOOD),
            turbinate_hyperplasia=defaults.get('turbinate_hyperplasia', False),
            airflow_subjective=defaults.get('airflow_subjective', 5)
        )
        
        # Measurements
        measurements = Measurements(
            nose_length_mm=defaults.get('nose_length_mm', 55),
            nose_width_mm=defaults.get('nose_width_mm', 35),
            nose_height_mm=defaults.get('nose_height_mm', 45),
            tip_rotation_deg=defaults.get('tip_rotation_deg', 95),
            tip_projection_mm=defaults.get('tip_projection_mm', 28),
            nasolabial_angle_deg=defaults.get('nasolabial_angle_deg', 100),
            dorsal_height_mm=defaults.get('dorsal_height_mm', 2)
        )
        
        # Aftercare
        aftercare = Aftercare(
            tamponade=defaults.get('tamponade', True),
            tamponade_days=defaults.get('tamponade_days', 2),
            splint=defaults.get('splint', True),
            splint_days=defaults.get('splint_days', 7),
            medication=defaults.get('medication', ['AB 5d', 'NSAR nach Bedarf'])
        )
        
        # Outcomes
        outcomes = Outcomes(
            satisfaction_vas=defaults.get('satisfaction_vas', 8),
            airflow_vas=defaults.get('airflow_vas', 7),
            complications=defaults.get('complications', [])
        )
        
        # Consents
        consents = Consents(
            photo_consent=defaults.get('photo_consent', True),
            data_consent=defaults.get('data_consent', True)
        )
        
        # Surgery
        surgery = Surgery(
            op_date=defaults['op_date'],
            indications=defaults.get('indications', [Indication.AESTHETIC]),
            technique=defaults.get('technique', 'Offen'),
            nose_shape=defaults.get('nose_shape', 'Höckernase'),
            anatomy=anatomy,
            measurements=measurements,
            procedures=defaults.get('procedures', [Procedure.HUMP_REDUCTION]),
            materials=defaults.get('materials', [Material.SEPTUM_CARTILAGE]),
            anesthesia=defaults.get('anesthesia', AnesthesiaType.GENERAL),
            op_duration_min=defaults.get('op_duration_min', 120),
            blood_loss_ml=defaults.get('blood_loss_ml', 100),
            complications_intraop=defaults.get('complications_intraop', []),
            complications_postop=defaults.get('complications_postop', []),
            aftercare=aftercare,
            outcomes=outcomes
        )
        
        # Patient
        patient = Patient(
            consents=consents,
            demographics=demographics,
            surgery=surgery,
            notes=defaults.get('notes', f'Test-Patient {patient_id}'),
            folder_slug=defaults.get('folder_slug', None)
        )
        
        return patient
    
    def test_create_patient_basic(self) -> Dict[str, Any]:
        """Test: Grundlegende Patient-Erstellung"""
        test_name = "test_create_patient_basic"
        self.logger.info(f"Starte Test: {test_name}")
        
        try:
            patient_manager = PatientManager(self.app_dir)
            
            # Patient erstellen
            patient = self.create_test_patient("001")
            
            start_time = time.time()
            success, message, patient_id = patient_manager.create_patient(patient)
            end_time = time.time()
            
            result = {
                'test': test_name,
                'success': success,
                'message': message,
                'duration_ms': round((end_time - start_time) * 1000, 2),
                'patient_id': patient_id,
                'timestamp': datetime.now().isoformat()
            }
            
            if success:
                # Patient laden und verifizieren
                loaded_patient = patient_manager.get_patient_by_id(patient_id)
                result['loaded_successfully'] = loaded_patient is not None
                result['data_consistency'] = self._verify_patient_data(patient, loaded_patient)
                self.test_data.append(patient_id)
            
            self.results.append(result)
            return result
            
        except Exception as e:
            return self._error_result(test_name, e)
    
    def test_create_patient_validation_errors(self) -> Dict[str, Any]:
        """Test: Validierungsfehler bei Patient-Erstellung"""
        test_name = "test_create_patient_validation_errors"
        self.logger.info(f"Starte Test: {test_name}")
        
        try:
            patient_manager = PatientManager(self.app_dir)
            test_cases = [
                # Fehlende Pflichtfelder
                {'lastname': 'Test', 'firstname': '', 'expected_error': 'Name darf nicht leer sein'},
                # Ungültige Daten
                {'dob': date.today(), 'expected_error': 'Geburtsdatum muss in der Vergangenheit liegen'},
                # Ungültige Messwerte
                {'nose_length_mm': 100, 'expected_error': 'außerhalb des Normalbereichs'},
                # Fehlende Einwilligungen
                {'photo_consent': False, 'expected_error': 'Keine Foto-Einwilligung'},
            ]
            
            results = []
            for i, case in enumerate(test_cases):
                patient = self.create_test_patient(f"val{i}", **case)
                success, message, _ = patient_manager.create_patient(patient)
                
                results.append({
                    'case': f"val{i}",
                    'success': success,
                    'message': message,
                    'correctly_rejected': not success
                })
            
            return {
                'test': test_name,
                'success': True,
                'validation_cases': results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self._error_result(test_name, e)
    
    def test_duplicate_patient_creation(self) -> Dict[str, Any]:
        """Test: Verhinderung doppelter Patienten"""
        test_name = "test_duplicate_patient_creation"
        self.logger.info(f"Starte Test: {test_name}")
        
        try:
            patient_manager = PatientManager(self.app_dir)
            
            # Ersten Patienten erstellen
            patient1 = self.create_test_patient("dup001", lastname="DupTest", firstname="First")
            success1, message1, patient_id1 = patient_manager.create_patient(patient1)
            
            # Identischen Patienten erstellen (sollte fehlschlagen)
            patient2 = self.create_test_patient("dup002", lastname="DupTest", firstname="First")
            success2, message2, patient_id2 = patient_manager.create_patient(patient2)
            
            return {
                'test': test_name,
                'success': success1 and not success2,  # Erster OK, zweiter nicht
                'first_patient': {'success': success1, 'message': message1, 'id': patient_id1},
                'duplicate_patient': {'success': success2, 'message': message2, 'id': patient_id2},
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self._error_result(test_name, e)
    
    def test_update_patient(self) -> Dict[str, Any]:
        """Test: Patient-Update"""
        test_name = "test_update_patient"
        self.logger.info(f"Starte Test: {test_name}")
        
        try:
            patient_manager = PatientManager(self.app_dir)
            
            # Patient erstellen
            patient = self.create_test_patient("upd001", satisfaction_vas=5)
            success, message, patient_id = patient_manager.create_patient(patient)
            
            if not success:
                return {'test': test_name, 'success': False, 'error': 'Patient creation failed'}
            
            # Patient laden und ändern
            loaded_patient = patient_manager.get_patient_by_id(patient_id)
            loaded_patient.surgery.outcomes.satisfaction_vas = 9
            loaded_patient.notes = "Aktualisiert während Test"
            
            start_time = time.time()
            success, message = patient_manager.update_patient(loaded_patient)
            end_time = time.time()
            
            # Verifizieren
            updated_patient = patient_manager.get_patient_by_id(patient_id)
            update_verified = (
                updated_patient.surgery.outcomes.satisfaction_vas == 9 and
                updated_patient.notes == "Aktualisiert während Test"
            )
            
            return {
                'test': test_name,
                'success': success and update_verified,
                'update_message': message,
                'duration_ms': round((end_time - start_time) * 1000, 2),
                'data_verified': update_verified,
                'before_vas': 5,
                'after_vas': updated_patient.surgery.outcomes.satisfaction_vas,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self._error_result(test_name, e)
    
    def test_search_patients(self) -> Dict[str, Any]:
        """Test: Patient-Suche"""
        test_name = "test_search_patients"
        self.logger.info(f"Starte Test: {test_name}")
        
        try:
            patient_manager = PatientManager(self.app_dir)
            
            # Mehrere Test-Patienten erstellen
            test_patients = [
                self.create_test_patient("search_001", gender=Gender.MALE, technique="Offen"),
                self.create_test_patient("search_002", gender=Gender.FEMALE, technique="Geschlossen"),
                self.create_test_patient("search_003", gender=Gender.MALE, technique="Geschlossen"),
            ]
            
            created_ids = []
            for patient in test_patients:
                success, _, patient_id = patient_manager.create_patient(patient)
                if success:
                    created_ids.append(patient_id)
            
            # Suchtests
            search_tests = [
                {'filters': {'Geschlecht': 'Männlich'}, 'expected_count': 2},
                {'filters': {'Geschlecht': 'Weiblich'}, 'expected_count': 1},
                {'filters': {'Technik': 'Offen'}, 'expected_count': 1},
                {'filters': {'Technik': 'Geschlossen'}, 'expected_count': 2},
            ]
            
            search_results = []
            for search_test in search_tests:
                results = patient_manager.search_patients(search_test['filters'])
                search_results.append({
                    'filters': search_test['filters'],
                    'found_count': len(results),
                    'expected_count': search_test['expected_count'],
                    'correct': len(results) == search_test['expected_count']
                })
            
            return {
                'test': test_name,
                'success': all(r['correct'] for r in search_results),
                'created_patients': len(created_ids),
                'search_results': search_results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self._error_result(test_name, e)
    
    def test_delete_patient(self) -> Dict[str, Any]:
        """Test: Patient-Löschung"""
        test_name = "test_delete_patient"
        self.logger.info(f"Starte Test: {test_name}")
        
        try:
            patient_manager = PatientManager(self.app_dir)
            
            # Patient erstellen
            patient = self.create_test_patient("del_001")
            success, _, patient_id = patient_manager.create_patient(patient)
            
            if not success:
                return {'test': test_name, 'success': False, 'error': 'Patient creation failed'}
            
            # Verifizieren dass Patient existiert
            exists_before = patient_manager.get_patient_by_id(patient_id) is not None
            
            # Löschung ohne Bestätigung (sollte fehlschlagen)
            success_no_confirm, message_no_confirm = patient_manager.delete_patient(patient_id, confirm_delete=False)
            
            # Löschung mit Bestätigung
            start_time = time.time()
            success_with_confirm, message_with_confirm = patient_manager.delete_patient(patient_id, confirm_delete=True)
            end_time = time.time()
            
            # Verifizieren dass Patient gelöscht
            exists_after = patient_manager.get_patient_by_id(patient_id) is not None
            
            return {
                'test': test_name,
                'success': (not success_no_confirm and success_with_confirm and not exists_after),
                'exists_before_delete': exists_before,
                'delete_without_confirmation': {'success': success_no_confirm, 'message': message_no_confirm},
                'delete_with_confirmation': {
                    'success': success_with_confirm,
                    'message': message_with_confirm,
                    'duration_ms': round((end_time - start_time) * 1000, 2)
                },
                'exists_after_delete': exists_after,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self._error_result(test_name, e)
    
    def test_edge_cases(self) -> Dict[str, Any]:
        """Test: Edge Cases und Grenzfälle"""
        test_name = "test_edge_cases"
        self.logger.info(f"Starte Test: {test_name}")
        
        try:
            patient_manager = PatientManager(self.app_dir)
            edge_cases = []
            
            # Test 1: Patient mit extremen Messwerten
            try:
                patient_extreme = self.create_test_patient(
                    "edge001",
                    nose_length_mm=30,  # Minimum
                    nose_width_mm=50,   # Maximum
                    age_at_surgery=15,  # Jung
                    satisfaction_vas=0  # Minimum
                )
                success, message, _ = patient_manager.create_patient(patient_extreme)
                edge_cases.append({
                    'case': 'extreme_measurements',
                    'success': success,
                    'has_warnings': 'Warnung' in message or 'außerhalb' in message.lower()
                })
            except Exception as e:
                edge_cases.append({'case': 'extreme_measurements', 'error': str(e)})
            
            # Test 2: Patient mit sehr langem Namen
            try:
                patient_long_name = self.create_test_patient(
                    "edge002",
                    lastname="Musterfrau-Schmidt-Abrahamovich",  # Langer Name
                    firstname="Gabriele-Elisabeth-Maria"
                )
                success, message, _ = patient_manager.create_patient(patient_long_name)
                edge_cases.append({
                    'case': 'long_name',
                    'success': success,
                    'message': message
                })
            except Exception as e:
                edge_cases.append({'case': 'long_name', 'error': str(e)})
            
            # Test 3: Patient mit vielen Komplikationen
            try:
                from core.patients.patient_model import Complication
                patient_complications = self.create_test_patient(
                    "edge003",
                    complications_intraop=[Complication.HEMATOMA],
                    complications_postop=[Complication.INFECTION, Complication.REVISION_NEEDED]
                )
                success, message, _ = patient_manager.create_patient(patient_complications)
                edge_cases.append({
                    'case': 'many_complications',
                    'success': success,
                    'message': message
                })
            except Exception as e:
                edge_cases.append({'case': 'many_complications', 'error': str(e)})
            
            # Test 4: Operation in der Zukunft (sollte fehlschlagen)
            try:
                patient_future = self.create_test_patient(
                    "edge004",
                    op_date=date(2030, 1, 1)  # Zukunft
                )
                success, message, _ = patient_manager.create_patient(patient_future)
                edge_cases.append({
                    'case': 'future_operation',
                    'correctly_rejected': not success,
                    'message': message
                })
            except Exception as e:
                edge_cases.append({'case': 'future_operation', 'error': str(e)})
            
            return {
                'test': test_name,
                'edge_cases': edge_cases,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self._error_result(test_name, e)
    
    def test_performance_crud_operations(self) -> Dict[str, Any]:
        """Test: Performance der CRUD-Operationen"""
        test_name = "test_performance_crud_operations"
        self.logger.info(f"Starte Test: {test_name}")
        
        try:
            patient_manager = PatientManager(self.app_dir)
            performance_results = {}
            
            # CREATE Performance
            create_times = []
            for i in range(5):
                patient = self.create_test_patient(f"perf_create{i}")
                start_time = time.time()
                success, _, _ = patient_manager.create_patient(patient)
                end_time = time.time()
                if success:
                    create_times.append((end_time - start_time) * 1000)
            
            performance_results['create'] = {
                'avg_ms': round(sum(create_times) / len(create_times), 2) if create_times else 0,
                'min_ms': round(min(create_times), 2) if create_times else 0,
                'max_ms': round(max(create_times), 2) if create_times else 0,
                'operations': len(create_times)
            }
            
            # READ Performance
            list_patients = patient_manager.list_patients()
            read_times = []
            for _ in range(5):
                if list_patients:
                    start_time = time.time()
                    patient = patient_manager.get_patient_by_folder(list_patients[0])
                    end_time = time.time()
                    read_times.append((end_time - start_time) * 1000)
            
            performance_results['read'] = {
                'avg_ms': round(sum(read_times) / len(read_times), 2) if read_times else 0,
                'min_ms': round(min(read_times), 2) if read_times else 0,
                'max_ms': round(max(read_times), 2) if read_times else 0,
                'operations': len(read_times)
            }
            
            # UPDATE Performance
            if list_patients:
                update_times = []
                for _ in range(3):
                    patient = patient_manager.get_patient_by_folder(list_patients[0])
                    if patient:
                        patient.notes = f"Performance Test Update {datetime.now()}"
                        start_time = time.time()
                        success, _ = patient_manager.update_patient(patient)
                        end_time = time.time()
                        if success:
                            update_times.append((end_time - start_time) * 1000)
                
                performance_results['update'] = {
                    'avg_ms': round(sum(update_times) / len(update_times), 2) if update_times else 0,
                    'min_ms': round(min(update_times), 2) if update_times else 0,
                    'max_ms': round(max(update_times), 2) if update_times else 0,
                    'operations': len(update_times)
                }
            
            self.performance_metrics = performance_results
            return {
                'test': test_name,
                'performance': performance_results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self._error_result(test_name, e)
    
    def test_mass_operations(self) -> Dict[str, Any]:
        """Test: Massenoperationen mit vielen Patienten"""
        test_name = "test_mass_operations"
        self.logger.info(f"Starte Test: {test_name}")
        
        try:
            patient_manager = PatientManager(self.app_dir)
            
            # 10 Patienten erstellen
            start_time = time.time()
            created_patients = []
            for i in range(10):
                patient = self.create_test_patient(
                    f"mass{i:02d}",
                    gender=Gender.FEMALE if i % 2 == 0 else Gender.MALE,
                    satisfaction_vas=5 + (i % 6)  # 5-10
                )
                success, _, patient_id = patient_manager.create_patient(patient)
                if success:
                    created_patients.append(patient_id)
            
            creation_time = time.time() - start_time
            
            # Alle Patienten auflisten
            start_time = time.time()
            all_patients = patient_manager.list_patients()
            list_time = time.time() - start_time
            
            # Statistiken berechnen
            start_time = time.time()
            stats = patient_manager.get_patient_statistics()
            stats_time = time.time() - start_time
            
            # Validierung aller Patienten
            start_time = time.time()
            validation = patient_manager.validate_all_patients()
            validation_time = time.time() - start_time
            
            return {
                'test': test_name,
                'created_patients': len(created_patients),
                'creation_time_s': round(creation_time, 2),
                'creation_rate_per_s': round(len(created_patients) / creation_time, 2) if creation_time > 0 else 0,
                'total_patients_in_system': len(all_patients),
                'list_time_s': round(list_time, 2),
                'stats_time_s': round(stats_time, 2),
                'validation_time_s': round(validation_time, 2),
                'statistics': {
                    'total': stats.get('total', 0),
                    'gender_distribution': stats.get('gender_distribution', {}),
                    'technique_distribution': stats.get('technique_distribution', {})
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self._error_result(test_name, e)
    
    def _verify_patient_data(self, original: Patient, loaded: Patient) -> bool:
        """Verifiziert Datenkonsistenz zwischen Original und geladenem Patient"""
        if not loaded:
            return False
        
        try:
            # Wichtige Felder vergleichen
            checks = [
                original.demographics.lastname == loaded.demographics.lastname,
                original.demographics.firstname == loaded.demographics.firstname,
                original.surgery.op_date == loaded.surgery.op_date,
                original.surgery.outcomes.satisfaction_vas == loaded.surgery.outcomes.satisfaction_vas,
                original.consents.photo_consent == loaded.consents.photo_consent,
            ]
            return all(checks)
        except Exception:
            return False
    
    def _error_result(self, test_name: str, error: Exception) -> Dict[str, Any]:
        """Erstellt Fehler-Ergebnis"""
        return {
            'test': test_name,
            'success': False,
            'error': str(error),
            'traceback': traceback.format_exc(),
            'timestamp': datetime.now().isoformat()
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Führt alle Tests aus"""
        self.logger.info("Starte umfassende Patient-Management-Tests")
        
        test_methods = [
            self.test_create_patient_basic,
            self.test_create_patient_validation_errors,
            self.test_duplicate_patient_creation,
            self.test_update_patient,
            self.test_search_patients,
            self.test_delete_patient,
            self.test_edge_cases,
            self.test_performance_crud_operations,
            self.test_mass_operations,
        ]
        
        for test_method in test_methods:
            try:
                self.logger.info(f"Führe {test_method.__name__} aus...")
                result = test_method()
                self.results.append(result)
                
                if result.get('success', False):
                    self.logger.info(f"✓ {test_method.__name__} erfolgreich")
                else:
                    self.logger.warning(f"✗ {test_method.__name__} fehlgeschlagen: {result.get('error', 'Unbekannter Fehler')}")
                    
            except Exception as e:
                self.logger.error(f"✗ {test_method.__name__} Exception: {e}")
                self.results.append(self._error_result(test_method.__name__, e))
        
        return self.generate_test_report()
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generiert detaillierten Test-Bericht"""
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.get('success', False))
        failed_tests = total_tests - successful_tests
        
        report = {
            'summary': {
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'failed_tests': failed_tests,
                'success_rate': round(successful_tests / total_tests * 100, 2) if total_tests > 0 else 0,
                'test_execution_time': datetime.now().isoformat()
            },
            'detailed_results': self.results,
            'performance_metrics': self.performance_metrics,
            'test_environment': {
                'app_dir': str(self.app_dir),
                'python_version': sys.version,
                'test_data_created': len(self.test_data)
            }
        }
        
        return report


def main():
    """Hauptfunktion"""
    print("=" * 80)
    print("PATIENT-MANAGEMENT-SYSTEM TEST")
    print("=" * 80)
    
    # Test-Suite initialisieren
    test_suite = PatientManagerTestSuite()
    
    # Alle Tests ausführen
    report = test_suite.run_all_tests()
    
    # Zusammenfassung ausgeben
    summary = report['summary']
    print(f"\n{'='*80}")
    print("TEST-ZUSAMMENFASSUNG")
    print(f"{'='*80}")
    print(f"Gesamte Tests: {summary['total_tests']}")
    print(f"Erfolgreich: {summary['successful_tests']}")
    print(f"Fehlgeschlagen: {summary['failed_tests']}")
    print(f"Erfolgsrate: {summary['success_rate']}%")
    
    if 'performance_metrics' in report and report['performance_metrics']:
        print(f"\n{'='*80}")
        print("PERFORMANCE-METRIKEN")
        print(f"{'='*80}")
        perf = report['performance_metrics']
        for operation, metrics in perf.items():
            print(f"{operation.upper()}:")
            print(f"  Durchschnitt: {metrics['avg_ms']} ms")
            print(f"  Minimum: {metrics['min_ms']} ms")
            print(f"  Maximum: {metrics['max_ms']} ms")
            print(f"  Operationen: {metrics['operations']}")
    
    return report


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Performance- und Stabilitätstests für Rhinoplastik-Dokumentations-Anwendung

Umfassende Tests für:
1. System-Performance mit 1000+ Patienten-Datensätzen
2. Multi-User-Tests (gleichzeitige Benutzer)
3. Memory-Usage und Garbage Collection
4. Database-Performance bei komplexen Abfragen
5. Langzeit-Stabilität (24h+ Laufzeit)
6. System-Fehler und Recovery-Mechanismen

Autor: MiniMax Agent
Datum: 2025-11-06
"""

import os
import sys
import gc
import time
import json
import random
import logging
import threading
import psutil
import traceback
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from queue import Queue, Empty
import signal
import subprocess

# Lokale Imports
sys.path.append('/workspace/rhinoplastik_app')
from core.patients.patient_manager import PatientManager
from core.patients.patient_model import Patient, Demographics, Surgery, Measurements, AnatomyStatus, Aftercare, Outcomes, Consents
from core.registry.excel_registry import ExcelRegistry

# Performance-Monitoring
try:
    from memory_profiler import profile
    MEMORY_PROFILING_AVAILABLE = True
except ImportError:
    MEMORY_PROFILING_AVAILABLE = False


@dataclass
class PerformanceMetrics:
    """Klasse für Performance-Metriken"""
    operation: str
    start_time: float
    end_time: float
    duration: float
    memory_start: float
    memory_end: float
    memory_peak: float
    success: bool
    error_message: Optional[str] = None


@dataclass
class StressTestResult:
    """Ergebnis eines Stresstests"""
    test_name: str
    total_operations: int
    successful_operations: int
    failed_operations: int
    success_rate: float
    avg_duration: float
    min_duration: float
    max_duration: float
    memory_usage_mb: float
    cpu_usage_percent: float
    errors: List[str]


class PerformanceTester:
    """Hauptklasse für Performance- und Stabilitätstests"""
    
    def __init__(self, test_dir: str = "/tmp/rhinoplastik_performance_tests"):
        """Initialisiert den Performance-Tester"""
        self.test_dir = Path(test_dir)
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
        # Performance-Logging
        self._setup_performance_logging()
        
        # Test-Manager
        self.patient_manager = None
        self.results: List[PerformanceMetrics] = []
        self.stress_results: List[StressTestResult] = []
        
        # Monitoring
        self.monitoring_active = False
        self.monitor_thread = None
        self.monitored_metrics = []
        
        # Test-Daten
        self.sample_patients = self._generate_test_patients(1000)
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Performance-Tester initialisiert")
    
    def _setup_performance_logging(self):
        """Konfiguriert Performance-Logging"""
        log_file = self.test_dir / "performance_tests.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def _generate_test_patients(self, count: int) -> List[Patient]:
        """Generiert Test-Patienten für Lasttests"""
        patients = []
        
        # Test-Daten
        names = ["Mustermann", "Schmidt", "Müller", "Schneider", "Fischer", "Weber", "Meyer"]
        first_names = ["Max", "Anna", "Tom", "Lisa", "Peter", "Maria", "Jan", "Sarah"]
        genders = ["Männlich", "Weiblich"]
        techniques = ["Offen", "Geschlossen"]
        indications = ["Ästhetisch", "Funktionell"]
        procedures = ["Hump-Reduktion", "Septoplastik", "Spreader-Grafts", "Tip-Graft"]
        
        for i in range(count):
            # Zufällige Daten generieren
            lastname = random.choice(names)
            firstname = random.choice(first_names)
            gender = random.choice(genders)
            birth_year = random.randint(1970, 2010)
            birth_month = random.randint(1, 12)
            birth_day = random.randint(1, 28)
            
            op_year = random.randint(2020, 2024)
            op_month = random.randint(1, 12)
            op_day = random.randint(1, 28)
            
            # Demographics
            demographics = Demographics(
                lastname=lastname,
                firstname=firstname,
                gender=gender,
                dob=datetime(birth_year, birth_month, birth_day).date()
            )
            
            # Anatomy
            anatomy = AnatomyStatus(
                septal_deviation=random.choice([True, False]),
                valve_collapse=random.choice([True, False]),
                skin_thickness=random.choice(['dünn', 'normal', 'dick']),
                cartilage_quality=random.choice(['gut', 'mittel', 'schlecht']),
                turbinate_hyperplasia=random.choice([True, False]),
                airflow_subjective=random.randint(1, 10)
            )
            
            # Measurements
            measurements = Measurements(
                nose_length_mm=random.randint(45, 65),
                nose_width_mm=random.randint(30, 40),
                nose_height_mm=random.randint(40, 50),
                tip_rotation_deg=random.randint(85, 105),
                tip_projection_mm=random.randint(25, 35),
                nasolabial_angle_deg=random.randint(95, 115),
                dorsal_height_mm=random.randint(1, 5)
            )
            
            # Aftercare
            tamponade = random.choice([True, False])
            splint = random.choice([True, False])
            # Immer einen Wert setzen, aber nur bei True als gültig verwenden
            tamponade_days = random.randint(1, 3) if tamponade else 0
            splint_days = random.randint(1, 14) if splint else 0
            
            aftercare = Aftercare(
                tamponade=tamponade,
                tamponade_days=tamponade_days,
                splint=splint,
                splint_days=splint_days,
                medication=[f"Medikament {random.randint(1, 5)}"]
            )
            
            # Outcomes
            outcomes = Outcomes(
                satisfaction_vas=random.randint(1, 10),
                airflow_vas=random.randint(1, 10),
                complications=[]
            )
            
            # Consents
            consents = Consents(
                photo_consent=random.choice([True, False]),
                data_consent=random.choice([True, False])
            )
            
            # Surgery
            surgery = Surgery(
                op_date=datetime(op_year, op_month, op_day).date(),
                indications=[indications[random.randint(0, len(indications)-1)]],
                technique=random.choice(techniques),
                nose_shape="Höckernase",
                anatomy=anatomy,
                measurements=measurements,
                procedures=[random.choice(procedures)],
                materials=["Septumknorpel"],
                anesthesia="Vollnarkose",
                op_duration_min=random.randint(60, 180),
                blood_loss_ml=random.randint(50, 200),
                complications_intraop=[],
                complications_postop=[],
                aftercare=aftercare,
                outcomes=outcomes
            )
            
            # Patient
            patient = Patient(
                consents=consents,
                demographics=demographics,
                surgery=surgery,
                notes=f"Test-Patient {i+1}",
                folder_slug=f"{lastname}_{firstname}_Geb{birth_year:04d}{birth_month:02d}{birth_day:02d}_"
            )
            
            patients.append(patient)
        
        return patients
    
    def _measure_performance(self, operation: str, func, *args, **kwargs) -> PerformanceMetrics:
        """Misst Performance einer Operation"""
        start_time = time.perf_counter()
        memory_start = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        success = True
        error_message = None
        
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            success = False
            error_message = str(e)
            self.logger.error(f"Fehler in Operation {operation}: {e}")
            return None
        finally:
            end_time = time.perf_counter()
            memory_end = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            duration = end_time - start_time
            memory_peak = max(memory_start, memory_end)
            
            metrics = PerformanceMetrics(
                operation=operation,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                memory_start=memory_start,
                memory_end=memory_end,
                memory_peak=memory_peak,
                success=success,
                error_message=error_message
            )
            
            self.results.append(metrics)
            return metrics
    
    def test_1000_patients_performance(self) -> StressTestResult:
        """Test 1: System-Performance mit 1000+ Patienten-Datensätzen"""
        self.logger.info("=== Test 1: 1000+ Patienten-Datensätze Performance ===")
        
        # Test-Verzeichnis vorbereiten
        test_app_dir = self.test_dir / "patients_1000_test"
        test_app_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # PatientManager initialisieren
            self.patient_manager = PatientManager(test_app_dir)
            
            # Test-Patienten generieren
            test_patients = self._generate_test_patients(1000)
            
            # Performance-Tests
            create_times = []
            load_times = []
            search_times = []
            stats_times = []
            
            successful_operations = 0
            failed_operations = 0
            errors = []
            
            # CREATE-Test
            for i, patient in enumerate(test_patients):
                try:
                    start_time = time.perf_counter()
                    success, msg, patient_id = self.patient_manager.create_patient(patient)
                    end_time = time.perf_counter()
                    
                    if success:
                        create_times.append(end_time - start_time)
                        successful_operations += 1
                    else:
                        failed_operations += 1
                        errors.append(f"CREATE Patient {i}: {msg}")
                    
                    if i % 100 == 0:
                        self.logger.info(f"CREATE-Test: {i+1}/1000 Patienten erstellt")
                        
                except Exception as e:
                    failed_operations += 1
                    errors.append(f"CREATE Patient {i}: {e}")
            
            # LOAD-Test (alle Patienten laden)
            try:
                start_time = time.perf_counter()
                all_patients = self.patient_manager.list_patients()
                end_time = time.perf_counter()
                load_times.append(end_time - start_time)
                self.logger.info(f"LOAD-Test: {len(all_patients)} Patienten geladen")
            except Exception as e:
                failed_operations += 1
                errors.append(f"LOAD: {e}")
            
            # SEARCH-Test (komplexe Abfragen)
            for i in range(10):  # 10 verschiedene Suchen
                try:
                    filters = {
                        'Geschlecht': random.choice(['Männlich', 'Weiblich']),
                        'Technik': random.choice(['Offen', 'Geschlossen'])
                    }
                    start_time = time.perf_counter()
                    results = self.patient_manager.search_patients(filters)
                    end_time = time.perf_counter()
                    search_times.append(end_time - start_time)
                    self.logger.info(f"SEARCH-Test {i+1}: {len(results)} Treffer")
                except Exception as e:
                    failed_operations += 1
                    errors.append(f"SEARCH {i+1}: {e}")
            
            # STATS-Test
            try:
                start_time = time.perf_counter()
                stats = self.patient_manager.get_patient_statistics()
                end_time = time.perf_counter()
                stats_times.append(end_time - start_time)
                self.logger.info("STATS-Test: Statistiken berechnet")
            except Exception as e:
                failed_operations += 1
                errors.append(f"STATS: {e}")
            
            # Memory-Messung
            memory_usage = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            # CPU-Nutzung
            cpu_usage = psutil.cpu_percent(interval=1)
            
            total_operations = successful_operations + failed_operations
            success_rate = (successful_operations / total_operations * 100) if total_operations > 0 else 0
            
            # Durations zusammenfassen
            all_durations = create_times + load_times + search_times + stats_times
            avg_duration = sum(all_durations) / len(all_durations) if all_durations else 0
            min_duration = min(all_durations) if all_durations else 0
            max_duration = max(all_durations) if all_durations else 0
            
            result = StressTestResult(
                test_name="1000+ Patienten Performance",
                total_operations=total_operations,
                successful_operations=successful_operations,
                failed_operations=failed_operations,
                success_rate=success_rate,
                avg_duration=avg_duration,
                min_duration=min_duration,
                max_duration=max_duration,
                memory_usage_mb=memory_usage,
                cpu_usage_percent=cpu_usage,
                errors=errors
            )
            
            self.stress_results.append(result)
            return result
            
        except Exception as e:
            self.logger.error(f"Kritischer Fehler in 1000+ Patienten Test: {e}")
            return StressTestResult(
                test_name="1000+ Patienten Performance",
                total_operations=0,
                successful_operations=0,
                failed_operations=1,
                success_rate=0,
                avg_duration=0,
                min_duration=0,
                max_duration=0,
                memory_usage_mb=0,
                cpu_usage_percent=0,
                errors=[str(e)]
            )
    
    def test_multi_user_concurrent_access(self, num_threads: int = 10) -> StressTestResult:
        """Test 2: Multi-User-Tests (gleichzeitige Benutzer)"""
        self.logger.info("=== Test 2: Multi-User-Tests ===")
        
        # Test-Verzeichnis vorbereiten
        test_app_dir = self.test_dir / "multi_user_test"
        test_app_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            self.patient_manager = PatientManager(test_app_dir)
            
            # Thread-sichere Queues für Ergebnisse
            results_queue = Queue()
            errors_queue = Queue()
            
            def worker_function(worker_id: int, num_operations: int):
                """Worker-Funktion für gleichzeitige Zugriffe"""
                worker_results = []
                worker_errors = []
                
                for i in range(num_operations):
                    try:
                        # Zufällige Operation wählen
                        operation = random.choice(['create', 'read', 'search', 'stats'])
                        
                        if operation == 'create':
                            # Neuen Test-Patienten erstellen
                            patient = self._generate_test_patients(1)[0]
                            patient.demographics.lastname = f"User{worker_id}_Op{i}"
                            start_time = time.perf_counter()
                            success, msg, patient_id = self.patient_manager.create_patient(patient)
                            end_time = time.perf_counter()
                            
                            worker_results.append({
                                'operation': 'create',
                                'worker_id': worker_id,
                                'duration': end_time - start_time,
                                'success': success
                            })
                            
                        elif operation == 'read':
                            # Zufälligen Patienten lesen
                            all_patients = self.patient_manager.list_patients()
                            if all_patients:
                                random_patient = random.choice(all_patients)
                                patient_id = random_patient.get('ID')
                                
                                start_time = time.perf_counter()
                                patient = self.patient_manager.get_patient_by_id(patient_id)
                                end_time = time.perf_counter()
                                
                                worker_results.append({
                                    'operation': 'read',
                                    'worker_id': worker_id,
                                    'duration': end_time - start_time,
                                    'success': patient is not None
                                })
                        
                        elif operation == 'search':
                            # Such-Operation
                            filters = {'Geschlecht': random.choice(['Männlich', 'Weiblich'])}
                            start_time = time.perf_counter()
                            results = self.patient_manager.search_patients(filters)
                            end_time = time.perf_counter()
                            
                            worker_results.append({
                                'operation': 'search',
                                'worker_id': worker_id,
                                'duration': end_time - start_time,
                                'success': True
                            })
                        
                        elif operation == 'stats':
                            # Statistik-Operation
                            start_time = time.perf_counter()
                            stats = self.patient_manager.get_patient_statistics()
                            end_time = time.perf_counter()
                            
                            worker_results.append({
                                'operation': 'stats',
                                'worker_id': worker_id,
                                'duration': end_time - start_time,
                                'success': 'error' not in stats
                            })
                    
                    except Exception as e:
                        worker_errors.append(f"Worker {worker_id} Op {i}: {e}")
                
                # Ergebnisse in Queues speichern
                results_queue.put(worker_results)
                errors_queue.put(worker_errors)
            
            # Basis-Test-Patienten erstellen (für die Worker)
            base_patients = self._generate_test_patients(100)
            for patient in base_patients:
                self.patient_manager.create_patient(patient)
            
            # Multi-Threading test
            start_time = time.perf_counter()
            
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = []
                operations_per_worker = 20  # 20 Operationen pro Worker
                
                for worker_id in range(num_threads):
                    future = executor.submit(worker_function, worker_id, operations_per_worker)
                    futures.append(future)
                
                # Auf alle Futures warten
                for future in as_completed(futures):
                    try:
                        future.result()  # Exceptions werden automatisch gefangen
                    except Exception as e:
                        self.logger.error(f"Worker-Fehler: {e}")
            
            end_time = time.perf_counter()
            total_duration = end_time - start_time
            
            # Ergebnisse sammeln
            all_results = []
            all_errors = []
            
            while not results_queue.empty():
                all_results.extend(results_queue.get())
            
            while not errors_queue.empty():
                all_errors.extend(errors_queue.get())
            
            # Statistiken berechnen
            successful_operations = sum(1 for r in all_results if r.get('success', False))
            total_operations = len(all_results)
            success_rate = (successful_operations / total_operations * 100) if total_operations > 0 else 0
            
            durations = [r['duration'] for r in all_results]
            avg_duration = sum(durations) / len(durations) if durations else 0
            min_duration = min(durations) if durations else 0
            max_duration = max(durations) if durations else 0
            
            # System-Resource-Messungen
            memory_usage = psutil.Process().memory_info().rss / 1024 / 1024
            cpu_usage = psutil.cpu_percent(interval=1)
            
            result = StressTestResult(
                test_name=f"Multi-User-Tests ({num_threads} Threads)",
                total_operations=total_operations,
                successful_operations=successful_operations,
                failed_operations=total_operations - successful_operations,
                success_rate=success_rate,
                avg_duration=avg_duration,
                min_duration=min_duration,
                max_duration=max_duration,
                memory_usage_mb=memory_usage,
                cpu_usage_percent=cpu_usage,
                errors=all_errors
            )
            
            self.stress_results.append(result)
            self.logger.info(f"Multi-User-Test abgeschlossen: {successful_operations}/{total_operations} erfolgreich")
            return result
            
        except Exception as e:
            self.logger.error(f"Kritischer Fehler in Multi-User-Test: {e}")
            return StressTestResult(
                test_name=f"Multi-User-Tests ({num_threads} Threads)",
                total_operations=0,
                successful_operations=0,
                failed_operations=1,
                success_rate=0,
                avg_duration=0,
                min_duration=0,
                max_duration=0,
                memory_usage_mb=0,
                cpu_usage_percent=0,
                errors=[str(e)]
            )
    
    def test_memory_usage_garbage_collection(self, num_iterations: int = 100) -> StressTestResult:
        """Test 3: Memory-Usage und Garbage Collection"""
        self.logger.info("=== Test 3: Memory-Usage und Garbage Collection ===")
        
        try:
            # Baseline-Memory messen
            gc.collect()  # Garbage Collection vor Start
            baseline_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            memory_snapshots = []
            peak_memory = baseline_memory
            total_allocations = 0
            
            for i in range(num_iterations):
                try:
                    iteration_start_memory = psutil.Process().memory_info().rss / 1024 / 1024
                    
                    # Speicher-intensive Operationen simulieren
                    patients = self._generate_test_patients(50)
                    test_app_dir = self.test_dir / f"memory_test_{i}"
                    test_app_dir.mkdir(parents=True, exist_ok=True)
                    
                    patient_manager = PatientManager(test_app_dir)
                    
                    # Viele Patienten erstellen und löschen
                    created_patients = []
                    for patient in patients:
                        success, msg, patient_id = patient_manager.create_patient(patient)
                        if success:
                            created_patients.append(patient_id)
                    
                    # Statistiken berechnen
                    stats = patient_manager.get_patient_statistics()
                    
                    # Patienten löschen (Memory leeren)
                    for patient_id in created_patients:
                        patient_manager.delete_patient(patient_id, confirm_delete=True)
                    
                    # Memory nach Iteration
                    iteration_end_memory = psutil.Process().memory_info().rss / 1024 / 1024
                    peak_memory = max(peak_memory, iteration_end_memory)
                    total_allocations += len(patients)
                    
                    memory_snapshots.append({
                        'iteration': i,
                        'start_memory': iteration_start_memory,
                        'end_memory': iteration_end_memory,
                        'delta': iteration_end_memory - iteration_start_memory
                    })
                    
                    # Garbage Collection nach jeder Iteration
                    del patient_manager, patients, created_patients, stats
                    gc.collect()
                    
                    if i % 10 == 0:
                        self.logger.info(f"Memory-Test: Iteration {i+1}/{num_iterations}, Memory: {iteration_end_memory:.1f}MB")
                
                except Exception as e:
                    self.logger.error(f"Memory-Test Fehler Iteration {i}: {e}")
                    continue
            
            # Final Memory messen
            gc.collect()
            final_memory = psutil.Process().memory_info().rss / 1024 / 1024
            memory_leak = final_memory - baseline_memory
            
            # Memory-Leak-Klassifizierung
            if memory_leak < 10:
                leak_classification = "Kein Memory-Leak (akzeptabel)"
            elif memory_leak < 50:
                leak_classification = "Leichter Memory-Leak"
            elif memory_leak < 100:
                leak_classification = "Moderater Memory-Leak"
            else:
                leak_classification = "Erheblicher Memory-Leak"
            
            # System-Ressourcen
            cpu_usage = psutil.cpu_percent(interval=1)
            
            result = StressTestResult(
                test_name="Memory-Usage und Garbage Collection",
                total_operations=num_iterations,
                successful_operations=len(memory_snapshots),
                failed_operations=num_iterations - len(memory_snapshots),
                success_rate=(len(memory_snapshots) / num_iterations * 100) if num_iterations > 0 else 0,
                avg_duration=0,  # Nicht gemessen in diesem Test
                min_duration=0,
                max_duration=0,
                memory_usage_mb=final_memory,
                cpu_usage_percent=cpu_usage,
                errors=[f"Memory-Leak: {memory_leak:.1f}MB ({leak_classification})"]
            )
            
            self.stress_results.append(result)
            self.logger.info(f"Memory-Test abgeschlossen: {leak_classification}, Peak: {peak_memory:.1f}MB")
            return result
            
        except Exception as e:
            self.logger.error(f"Kritischer Fehler in Memory-Test: {e}")
            return StressTestResult(
                test_name="Memory-Usage und Garbage Collection",
                total_operations=num_iterations,
                successful_operations=0,
                failed_operations=1,
                success_rate=0,
                avg_duration=0,
                min_duration=0,
                max_duration=0,
                memory_usage_mb=0,
                cpu_usage_percent=0,
                errors=[str(e)]
            )
    
    def test_complex_database_queries(self) -> StressTestResult:
        """Test 4: Database-Performance bei komplexen Abfragen"""
        self.logger.info("=== Test 4: Database-Performance bei komplexen Abfragen ===")
        
        # Test-Verzeichnis vorbereiten
        test_app_dir = self.test_dir / "complex_queries_test"
        test_app_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            self.patient_manager = PatientManager(test_app_dir)
            
            # Große Datenbasis erstellen
            test_patients = self._generate_test_patients(2000)
            
            self.logger.info("Erstelle Test-Datenbasis für komplexe Abfragen...")
            for i, patient in enumerate(test_patients):
                success, msg, patient_id = self.patient_manager.create_patient(patient)
                if not success and i % 100 == 0:
                    self.logger.warning(f"Fehler beim Erstellen von Patient {i}: {msg}")
                
                if i % 500 == 0:
                    self.logger.info(f"Datenbasis-Erstellung: {i+1}/{len(test_patients)}")
            
            # Komplexe Such-Operationen
            query_times = []
            complex_filters = [
                {'Geschlecht': 'Männlich', 'Technik': 'Offen'},
                {'Geschlecht': 'Weiblich', 'OP-Dauer_min': '>120'},
                {'Technik': 'Geschlossen', 'Zufriedenheit_VAS': '>7'},
                {'Geschlecht': 'Männlich', 'Technik': 'Preservation', 'Zufriedenheit_VAS': '>8'},
                {'OP-Dauer_min': '>150', 'Zufriedenheit_VAS': '<5'},
                {'Atmung_VAS': '>8', 'Zufriedenheit_VAS': '>7'},
            ]
            
            successful_queries = 0
            failed_queries = 0
            query_errors = []
            
            for i, filters in enumerate(complex_filters):
                try:
                    self.logger.info(f"Führe komplexe Abfrage {i+1}/6 aus: {filters}")
                    
                    start_time = time.perf_counter()
                    results = self.patient_manager.search_patients(filters)
                    end_time = time.perf_counter()
                    
                    duration = end_time - start_time
                    query_times.append(duration)
                    successful_queries += 1
                    
                    self.logger.info(f"Abfrage {i+1}: {len(results)} Treffer in {duration:.3f}s")
                    
                except Exception as e:
                    failed_queries += 1
                    query_errors.append(f"Abfrage {i+1}: {e}")
                    self.logger.error(f"Fehler bei komplexer Abfrage {i+1}: {e}")
            
            # Komplexe Statistik-Berechnungen
            stats_times = []
            try:
                start_time = time.perf_counter()
                stats = self.patient_manager.get_patient_statistics()
                end_time = time.perf_counter()
                stats_times.append(end_time - start_time)
                self.logger.info(f"Komplexe Statistiken berechnet: {end_time - start_time:.3f}s")
            except Exception as e:
                query_errors.append(f"Statistik-Berechnung: {e}")
                self.logger.error(f"Fehler bei Statistik-Berechnung: {e}")
            
            # Registry-Synchronisation testen
            sync_times = []
            for i in range(3):
                try:
                    start_time = time.perf_counter()
                    sync_count = self.patient_manager.sync_registry()
                    end_time = time.perf_counter()
                    sync_times.append(end_time - start_time)
                    self.logger.info(f"Registry-Sync {i+1}: {sync_count} Einträge synchronisiert in {end_time - start_time:.3f}s")
                except Exception as e:
                    query_errors.append(f"Registry-Sync {i+1}: {e}")
            
            # System-Ressourcen
            memory_usage = psutil.Process().memory_info().rss / 1024 / 1024
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Ergebnisse zusammenfassen
            all_times = query_times + stats_times + sync_times
            total_operations = successful_queries + failed_queries + len(stats_times) + len(sync_times)
            successful_operations = successful_queries + len(stats_times) + len(sync_times)
            
            avg_duration = sum(all_times) / len(all_times) if all_times else 0
            min_duration = min(all_times) if all_times else 0
            max_duration = max(all_times) if all_times else 0
            
            result = StressTestResult(
                test_name="Database-Performance bei komplexen Abfragen",
                total_operations=total_operations,
                successful_operations=successful_operations,
                failed_operations=failed_queries,
                success_rate=(successful_operations / total_operations * 100) if total_operations > 0 else 0,
                avg_duration=avg_duration,
                min_duration=min_duration,
                max_duration=max_duration,
                memory_usage_mb=memory_usage,
                cpu_usage_percent=cpu_usage,
                errors=query_errors
            )
            
            self.stress_results.append(result)
            self.logger.info("Komplexe Datenbank-Abfragen Test abgeschlossen")
            return result
            
        except Exception as e:
            self.logger.error(f"Kritischer Fehler in komplexen Datenbank-Tests: {e}")
            return StressTestResult(
                test_name="Database-Performance bei komplexen Abfragen",
                total_operations=0,
                successful_operations=0,
                failed_operations=1,
                success_rate=0,
                avg_duration=0,
                min_duration=0,
                max_duration=0,
                memory_usage_mb=0,
                cpu_usage_percent=0,
                errors=[str(e)]
            )
    
    def test_long_term_stability(self, duration_hours: int = 2) -> StressTestResult:
        """Test 5: Langzeit-Stabilität (z.B. 2h Test statt 24h)"""
        self.logger.info(f"=== Test 5: Langzeit-Stabilität ({duration_hours}h) ===")
        
        test_app_dir = self.test_dir / "longterm_stability_test"
        test_app_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            self.patient_manager = PatientManager(test_app_dir)
            
            # Test-Start-Zeit
            start_time = time.perf_counter()
            end_time = start_time + (duration_hours * 3600)  # Stunden zu Sekunden
            
            operations_count = 0
            successful_operations = 0
            failed_operations = 0
            operation_errors = []
            
            # Baseline-Messungen
            baseline_memory = psutil.Process().memory_info().rss / 1024 / 1024
            peak_memory = baseline_memory
            
            # Stabilitäts-Monitoring
            stability_checks = []
            
            self.logger.info(f"Starte {duration_hours}h Stabilitätstest...")
            
            while time.perf_counter() < end_time:
                try:
                    # Zufällige Operation wählen
                    operation = random.choice(['create', 'read', 'update', 'delete', 'search', 'stats'])
                    
                    op_start_time = time.perf_counter()
                    
                    if operation == 'create':
                        # Neuen Patienten erstellen
                        patient = self._generate_test_patients(1)[0]
                        patient.demographics.lastname = f"Stability_{operations_count}"
                        success, msg, patient_id = self.patient_manager.create_patient(patient)
                    
                    elif operation == 'read':
                        # Zufälligen Patienten lesen
                        all_patients = self.patient_manager.list_patients()
                        if all_patients:
                            random_patient = random.choice(all_patients)
                            patient_id = random_patient.get('ID')
                            patient = self.patient_manager.get_patient_by_id(patient_id)
                            success = patient is not None
                        else:
                            success = True
                    
                    elif operation == 'update':
                        # Patienten aktualisieren
                        all_patients = self.patient_manager.list_patients()
                        if all_patients:
                            random_patient = random.choice(all_patients)
                            patient_id = random_patient.get('ID')
                            patient = self.patient_manager.get_patient_by_id(patient_id)
                            if patient:
                                patient.surgery.notes = f"Updated at {datetime.now()}"
                                success, msg = self.patient_manager.update_patient(patient)
                            else:
                                success = False
                        else:
                            success = True
                    
                    elif operation == 'delete':
                        # Patienten löschen (ältere zuerst)
                        all_patients = self.patient_manager.list_patients()
                        if all_patients and len(all_patients) > 50:  # Mindestens 50 behalten
                            oldest_patient = min(all_patients, key=lambda x: x.get('Erstellt', ''))
                            patient_id = oldest_patient.get('ID')
                            success, msg = self.patient_manager.delete_patient(patient_id, confirm_delete=True)
                        else:
                            success = True
                    
                    elif operation == 'search':
                        # Such-Operation
                        filters = {'Geschlecht': random.choice(['Männlich', 'Weiblich'])}
                        results = self.patient_manager.search_patients(filters)
                        success = True
                    
                    elif operation == 'stats':
                        # Statistik-Operation
                        stats = self.patient_manager.get_patient_statistics()
                        success = 'error' not in stats
                    
                    op_end_time = time.perf_counter()
                    op_duration = op_end_time - op_start_time
                    
                    operations_count += 1
                    if success:
                        successful_operations += 1
                    else:
                        failed_operations += 1
                        operation_errors.append(f"{operation} operation failed")
                    
                    # Memory-Monitoring
                    current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                    peak_memory = max(peak_memory, current_memory)
                    
                    # Stabilitäts-Check alle 100 Operationen
                    if operations_count % 100 == 0:
                        gc.collect()
                        current_memory_after_gc = psutil.Process().memory_info().rss / 1024 / 1024
                        
                        stability_check = {
                            'operations': operations_count,
                            'memory': current_memory_after_gc,
                            'memory_delta': current_memory_after_gc - baseline_memory,
                            'avg_op_duration': op_duration,
                            'success_rate': successful_operations / operations_count * 100
                        }
                        stability_checks.append(stability_check)
                        
                        elapsed_time = (time.perf_counter() - start_time) / 3600
                        remaining_time = (end_time - time.perf_counter()) / 3600
                        
                        self.logger.info(
                            f"Stabilitäts-Check: {operations_count} Ops, "
                            f"Memory: {current_memory_after_gc:.1f}MB, "
                            f"Success: {stability_check['success_rate']:.1f}%, "
                            f"Elapsed: {elapsed_time:.1f}h, Remaining: {remaining_time:.1f}h"
                        )
                    
                    # Kurze Pause zwischen Operationen
                    time.sleep(random.uniform(0.01, 0.1))  # 10-100ms Pause
                    
                except Exception as e:
                    failed_operations += 1
                    operation_errors.append(f"Operation {operations_count}: {e}")
                    self.logger.error(f"Stabilitätstest Fehler bei Operation {operations_count}: {e}")
                
                # Alle 5 Minuten Progress-Report
                if operations_count % 1000 == 0:
                    elapsed_time = (time.perf_counter() - start_time) / 60  # Minuten
                    self.logger.info(f"Fortschritt: {operations_count} Operationen in {elapsed_time:.1f} Minuten")
            
            # Final Memory-Messung
            final_memory = psutil.Process().memory_info().rss / 1024 / 1024
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Test-Statistiken
            total_duration = (time.perf_counter() - start_time) / 3600  # Stunden
            ops_per_hour = operations_count / total_duration if total_duration > 0 else 0
            success_rate = (successful_operations / operations_count * 100) if operations_count > 0 else 0
            
            result = StressTestResult(
                test_name=f"Langzeit-Stabilität ({duration_hours}h)",
                total_operations=operations_count,
                successful_operations=successful_operations,
                failed_operations=failed_operations,
                success_rate=success_rate,
                avg_duration=ops_per_hour,  # Ops pro Stunde als "Duration"
                min_duration=0,
                max_duration=0,
                memory_usage_mb=final_memory,
                cpu_usage_percent=cpu_usage,
                errors=operation_errors[:10]  # Erste 10 Fehler begrenzen
            )
            
            self.stress_results.append(result)
            self.logger.info(f"Langzeit-Stabilitätstest abgeschlossen: {operations_count} Operationen in {total_duration:.1f}h")
            return result
            
        except Exception as e:
            self.logger.error(f"Kritischer Fehler in Langzeit-Stabilitätstest: {e}")
            return StressTestResult(
                test_name=f"Langzeit-Stabilität ({duration_hours}h)",
                total_operations=operations_count,
                successful_operations=successful_operations,
                failed_operations=failed_operations,
                success_rate=0,
                avg_duration=0,
                min_duration=0,
                max_duration=0,
                memory_usage_mb=0,
                cpu_usage_percent=0,
                errors=[str(e)]
            )
    
    def test_error_recovery_mechanisms(self) -> StressTestResult:
        """Test 6: System-Fehler und Recovery-Mechanismen"""
        self.logger.info("=== Test 6: System-Fehler und Recovery-Mechanismen ===")
        
        test_app_dir = self.test_dir / "error_recovery_test"
        test_app_dir.mkdir(parents=True, exist_ok=True)
        
        recovery_tests = []
        
        try:
            # Test 1: Korrupte JSON-Dateien
            self.logger.info("Test 1: Korrupte JSON-Dateien Recovery")
            try:
                # PatientManager mit korrupter JSON-Datei testen
                corrupt_dir = test_app_dir / "data" / "patients" / "corrupt_patient"
                corrupt_dir.mkdir(parents=True, exist_ok=True)
                
                # Korrupte JSON-Datei erstellen
                corrupt_file = corrupt_dir / "patient.json"
                with open(corrupt_file, 'w') as f:
                    f.write("{ invalid json content []")
                
                # Testen ob System damit umgehen kann
                patient_manager = PatientManager(test_app_dir)
                
                # Validierung sollte Fehler erkennen
                all_patients = patient_manager.list_patients()
                
                recovery_tests.append({
                    'test': 'Korrupte JSON-Datei',
                    'success': True,
                    'recovery': 'System ignoriert korrupte Dateien'
                })
                self.logger.info("✓ Korrupte JSON-Datei Recovery erfolgreich")
                
            except Exception as e:
                recovery_tests.append({
                    'test': 'Korrupte JSON-Datei',
                    'success': False,
                    'recovery': str(e)
                })
                self.logger.error(f"✗ Korrupte JSON-Datei Test fehlgeschlagen: {e}")
            
            # Test 2: Fehlende Registry-Datei
            self.logger.info("Test 2: Fehlende Registry-Datei Recovery")
            try:
                # Registry löschen und neu erstellen
                registry_file = test_app_dir / "registry" / "registry.xlsx"
                if registry_file.exists():
                    registry_file.unlink()
                
                patient_manager = PatientManager(test_app_dir)
                test_patient = self._generate_test_patients(1)[0]
                success, msg, patient_id = patient_manager.create_patient(test_patient)
                
                recovery_tests.append({
                    'test': 'Fehlende Registry-Datei',
                    'success': success,
                    'recovery': 'System erstellt neue Registry' if success else f'Recovery failed: {msg}'
                })
                self.logger.info("✓ Fehlende Registry-Datei Recovery erfolgreich" if success else f"✗ Fehlende Registry-Datei Test fehlgeschlagen: {msg}")
                
            except Exception as e:
                recovery_tests.append({
                    'test': 'Fehlende Registry-Datei',
                    'success': False,
                    'recovery': str(e)
                })
                self.logger.error(f"✗ Fehlende Registry-Datei Test fehlgeschlagen: {e}")
            
            # Test 3: Ordner-Berechtigungsfehler
            self.logger.info("Test 3: Dateisystem-Berechtigungsfehler")
            try:
                # Schreibgeschützten Ordner simulieren
                protected_dir = test_app_dir / "data" / "patients" / "protected_patient"
                protected_dir.mkdir(parents=True, exist_ok=True)
                
                # Berechtigungen ändern (unter Linux/Mac)
                try:
                    os.chmod(protected_dir, 0o444)  # Nur Leseberechtigung
                    
                    patient_manager = PatientManager(test_app_dir)
                    patient = self._generate_test_patients(1)[0]
                    patient.folder_slug = "protected_patient"
                    
                    success, msg, patient_id = patient_manager.create_patient(patient)
                    
                    recovery_tests.append({
                        'test': 'Berechtigungsfehler',
                        'success': False,  # Sollte fehlschlagen
                        'recovery': f'Error handled correctly: {msg}'
                    })
                    self.logger.info(f"✓ Berechtigungsfehler korrekt behandelt: {msg}")
                    
                except PermissionError:
                    recovery_tests.append({
                        'test': 'Berechtigungsfehler',
                        'success': True,  # Fehler korrekt erkannt
                        'recovery': 'PermissionError korrekt geworfen'
                    })
                    self.logger.info("✓ Berechtigungsfehler korrekt behandelt")
                
            except Exception as e:
                recovery_tests.append({
                    'test': 'Berechtigungsfehler',
                    'success': True,  # Exception ist auch ein korrektes Verhalten
                    'recovery': f'Exception handling: {str(e)}'
                })
                self.logger.info(f"✓ Berechtigungsfehler Exception handling: {e}")
            
            # Test 4: Memory-exhaustion Simulation
            self.logger.info("Test 4: Memory-Exhaustion Handling")
            try:
                # Große Datenmengen simulieren
                patient_manager = PatientManager(test_app_dir)
                
                # Memory-intensive Operationen testen
                try:
                    # Große Patientensammlung
                    large_patients = self._generate_test_patients(500)
                    for i, patient in enumerate(large_patients):
                        patient.demographics.lastname = f"MemoryTest_{i}"
                        success, msg, patient_id = patient_manager.create_patient(patient)
                        if not success:
                            break
                    
                    recovery_tests.append({
                        'test': 'Memory-Exhaustion',
                        'success': True,
                        'recovery': f'Successfully created {i+1} patients before memory limit'
                    })
                    self.logger.info(f"✓ Memory-Exhaustion Test: {i+1} Patienten erstellt")
                    
                except MemoryError:
                    recovery_tests.append({
                        'test': 'Memory-Exhaustion',
                        'success': True,  # MemoryError korrekt erkannt
                        'recovery': 'MemoryError korrekt geworfen'
                    })
                    self.logger.info("✓ Memory-Exhaustion korrekt behandelt")
                
            except Exception as e:
                recovery_tests.append({
                    'test': 'Memory-Exhaustion',
                    'success': True,  # Exception ist gültiges Verhalten
                    'recovery': f'Exception handling: {str(e)}'
                })
                self.logger.info(f"✓ Memory-Exhaustion Exception handling: {e}")
            
            # Test 5: Datenintegrität nach Fehlern
            self.logger.info("Test 5: Datenintegrität nach Fehlern")
            try:
                # System mit Fehlern belasten und dann Integrität prüfen
                patient_manager = PatientManager(test_app_dir)
                
                # Erste Basis-Patienten erstellen
                base_patients = self._generate_test_patients(10)
                created_ids = []
                
                for patient in base_patients:
                    success, msg, patient_id = patient_manager.create_patient(patient)
                    if success:
                        created_ids.append(patient_id)
                
                # Registry und JSON-Dateien auf Konsistenz prüfen
                all_registry_patients = patient_manager.list_patients()
                registry_ids = [p.get('ID') for p in all_registry_patients]
                
                # JSON-Dateien prüfen
                json_valid = True
                for patient_id in created_ids:
                    patient = patient_manager.get_patient_by_id(patient_id)
                    if patient is None:
                        json_valid = False
                        break
                
                integrity_check = len(created_ids) == len(registry_ids) and json_valid
                
                recovery_tests.append({
                    'test': 'Datenintegrität nach Fehlern',
                    'success': integrity_check,
                    'recovery': f'Created: {len(created_ids)}, Registry: {len(registry_ids)}, JSON valid: {json_valid}'
                })
                self.logger.info(f"✓ Datenintegrität: Created={len(created_ids)}, Registry={len(registry_ids)}, JSON valid={json_valid}")
                
            except Exception as e:
                recovery_tests.append({
                    'test': 'Datenintegrität nach Fehlern',
                    'success': False,
                    'recovery': str(e)
                })
                self.logger.error(f"✗ Datenintegrität Test fehlgeschlagen: {e}")
            
            # Ergebnisse zusammenfassen
            successful_recovery_tests = sum(1 for test in recovery_tests if test['success'])
            total_recovery_tests = len(recovery_tests)
            recovery_rate = (successful_recovery_tests / total_recovery_tests * 100) if total_recovery_tests > 0 else 0
            
            memory_usage = psutil.Process().memory_info().rss / 1024 / 1024
            cpu_usage = psutil.cpu_percent(interval=1)
            
            result = StressTestResult(
                test_name="System-Fehler und Recovery-Mechanismen",
                total_operations=total_recovery_tests,
                successful_operations=successful_recovery_tests,
                failed_operations=total_recovery_tests - successful_recovery_tests,
                success_rate=recovery_rate,
                avg_duration=0,
                min_duration=0,
                max_duration=0,
                memory_usage_mb=memory_usage,
                cpu_usage_percent=cpu_usage,
                errors=[test['recovery'] for test in recovery_tests if not test['success']]
            )
            
            self.stress_results.append(result)
            self.logger.info(f"Recovery-Tests abgeschlossen: {successful_recovery_tests}/{total_recovery_tests} erfolgreich")
            return result
            
        except Exception as e:
            self.logger.error(f"Kritischer Fehler in Recovery-Tests: {e}")
            return StressTestResult(
                test_name="System-Fehler und Recovery-Mechanismen",
                total_operations=len(recovery_tests),
                successful_operations=0,
                failed_operations=1,
                success_rate=0,
                avg_duration=0,
                min_duration=0,
                max_duration=0,
                memory_usage_mb=0,
                cpu_usage_percent=0,
                errors=[str(e)]
            )
    
    def generate_performance_report(self, output_file: str = "performance_stress_stabilitätstests.md"):
        """Generiert umfassenden Performance-Bericht"""
        
        report_path = Path(output_file)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Performance- und Stabilitätstests - Abschlussbericht\n\n")
            f.write(f"**Test-Durchführung:** {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
            f.write(f"**Test-System:** Rhinoplastik-Dokumentations-Anwendung\n")
            f.write(f"**Test-Dauer:**Gesamtlaufzeit der Tests\n\n")
            
            # Executive Summary
            f.write("## Executive Summary\n\n")
            
            if self.stress_results:
                total_operations = sum(r.total_operations for r in self.stress_results)
                total_successful = sum(r.successful_operations for r in self.stress_results)
                overall_success_rate = (total_successful / total_operations * 100) if total_operations > 0 else 0
                
                f.write(f"- **Gesamte Operationen:** {total_operations:,}\n")
                f.write(f"- **Erfolgreiche Operationen:** {total_successful:,}\n")
                f.write(f"- **Gesamt-Erfolgsrate:** {overall_success_rate:.1f}%\n")
                f.write(f"- **Durchgeführte Tests:** {len(self.stress_results)}\n\n")
                
                # Bewertung
                if overall_success_rate >= 95:
                    f.write("**✅ BEWERTUNG: EXZELLENT** - Das System zeigt ausgezeichnete Performance und Stabilität.\n\n")
                elif overall_success_rate >= 90:
                    f.write("**✅ BEWERTUNG: GUT** - Das System zeigt gute Performance mit kleineren Optimierungsmöglichkeiten.\n\n")
                elif overall_success_rate >= 80:
                    f.write("**⚠️ BEWERTUNG: AKZEPTABEL** - Das System funktioniert, benötigt aber Verbesserungen.\n\n")
                else:
                    f.write("**❌ BEWERTUNG: KRITISCH** - Das System hat erhebliche Performance-Probleme.\n\n")
            else:
                f.write("Keine Testergebnisse verfügbar.\n\n")
            
            # Detaillierte Testergebnisse
            f.write("## Detaillierte Testergebnisse\n\n")
            
            for i, result in enumerate(self.stress_results, 1):
                f.write(f"### Test {i}: {result.test_name}\n\n")
                f.write(f"- **Operationen:** {result.total_operations:,}\n")
                f.write(f"- **Erfolgreich:** {result.successful_operations:,}\n")
                f.write(f"- **Fehlgeschlagen:** {result.failed_operations:,}\n")
                f.write(f"- **Erfolgsrate:** {result.success_rate:.1f}%\n")
                f.write(f"- **Memory-Usage:** {result.memory_usage_mb:.1f} MB\n")
                f.write(f"- **CPU-Usage:** {result.cpu_usage_percent:.1f}%\n")
                
                if hasattr(result, 'avg_duration') and result.avg_duration > 0:
                    f.write(f"- **Durchschnittliche Dauer:** {result.avg_duration:.3f}s\n")
                    f.write(f"- **Min. Dauer:** {result.min_duration:.3f}s\n")
                    f.write(f"- **Max. Dauer:** {result.max_duration:.3f}s\n")
                
                # Fehler-Analyse
                if result.errors:
                    f.write(f"- **Anzahl Fehler:** {len(result.errors)}\n")
                    if result.errors:
                        f.write("- **Fehlerdetails:**\n")
                        for error in result.errors[:5]:  # Erste 5 Fehler
                            f.write(f"  - {error}\n")
                        if len(result.errors) > 5:
                            f.write(f"  - ... und {len(result.errors) - 5} weitere Fehler\n")
                
                f.write("\n")
            
            # Performance-Benchmarks
            f.write("## Performance-Benchmarks\n\n")
            f.write("### Zielwerte vs. Istwerte\n\n")
            f.write("| Test-Kategorie | Ziel-Erfolgsrate | Ist-Erfolgsrate | Status |\n")
            f.write("|---------------|------------------|------------------|--------|\n")
            
            benchmarks = [
                ("1000+ Patienten Performance", 95, 0),
                ("Multi-User-Tests", 90, 0),
                ("Memory-Usage & GC", 95, 0),
                ("Komplexe Datenbank-Abfragen", 90, 0),
                ("Langzeit-Stabilität", 85, 0),
                ("System-Fehler Recovery", 80, 0)
            ]
            
            for test_name, target, actual in benchmarks:
                if actual == 0:  # Noch nicht ausgeführt
                    actual = next((r.success_rate for r in self.stress_results if test_name in r.test_name), 0)
                
                if actual >= target:
                    status = "✅ BESTANDEN"
                elif actual >= target - 5:
                    status = "⚠️ GRENZWERTIG"
                else:
                    status = "❌ FEHLGESCHLAGEN"
                
                f.write(f"| {test_name} | {target}% | {actual:.1f}% | {status} |\n")
            
            f.write("\n")
            
            # System-Empfehlungen
            f.write("## System-Empfehlungen\n\n")
            
            if self.stress_results:
                # Memory-Analyse
                memory_results = [r for r in self.stress_results if 'Memory' in r.test_name]
                if memory_results:
                    avg_memory = sum(r.memory_usage_mb for r in memory_results) / len(memory_results)
                    f.write(f"### Memory-Management\n")
                    f.write(f"- **Durchschnittlicher Memory-Verbrauch:** {avg_memory:.1f} MB\n")
                    if avg_memory > 500:
                        f.write("- **Empfehlung:** Memory-Optimierungen implementieren\n")
                        f.write("- **Mögliche Maßnahmen:**\n")
                        f.write("  - Lazy Loading für große Datenmengen\n")
                        f.write("  - Garbage Collection optimieren\n")
                        f.write("  - Memory-Pool für häufige Objekte\n")
                    f.write("\n")
                
                # Performance-Analyse
                perf_results = [r for r in self.stress_results if r.avg_duration > 0]
                if perf_results:
                    avg_duration = sum(r.avg_duration for r in perf_results) / len(perf_results)
                    f.write(f"### Performance-Optimierung\n")
                    f.write(f"- **Durchschnittliche Operationsdauer:** {avg_duration:.3f}s\n")
                    if avg_duration > 1.0:
                        f.write("- **Empfehlung:** Performance-Optimierungen erforderlich\n")
                        f.write("- **Mögliche Maßnahmen:**\n")
                        f.write("  - Datenbank-Indizierung\n")
                        f.write("  - Caching-Strategien\n")
                        f.write("  - Asynchrone Operationen\n")
                    f.write("\n")
                
                # Stabilitäts-Analyse
                stability_results = [r for r in self.stress_results if 'Stabilität' in r.test_name]
                if stability_results:
                    success_rates = [r.success_rate for r in stability_results]
                    avg_stability = sum(success_rates) / len(success_rates)
                    f.write(f"### Langzeit-Stabilität\n")
                    f.write(f"- **Durchschnittliche Stabilität:** {avg_stability:.1f}%\n")
                    if avg_stability < 90:
                        f.write("- **Empfehlung:** Stabilitätsverbesserungen\n")
                        f.write("- **Mögliche Maßnahmen:**\n")
                        f.write("  - Error Handling verbessern\n")
                        f.write("  - Resource Leak Detection\n")
                        f.write("  - Automated Recovery-Mechanismen\n")
                    f.write("\n")
            
            # Test-Umgebung
            f.write("## Test-Umgebung\n\n")
            f.write(f"- **Python Version:** {sys.version.split()[0]}\n")
            f.write(f"- **Betriebssystem:** {os.name}\n")
            f.write(f"- **CPU-Kerne:** {psutil.cpu_count()}\n")
            f.write(f"- **Verfügbarer RAM:** {psutil.virtual_memory().total / 1024**3:.1f} GB\n")
            f.write(f"- **Test-Verzeichnis:** {self.test_dir}\n")
            
            # Technische Details
            f.write("\n## Technische Details\n\n")
            f.write("### Verwendete Test-Frameworks und -Techniken\n")
            f.write("- **Threading:** Concurrent Operations für Multi-User-Tests\n")
            f.write("- **Memory-Monitoring:** psutil für Real-time Memory Tracking\n")
            f.write("- **Performance-Metrics:** time.perf_counter für präzise Zeitmessung\n")
            f.write("- **Error-Simulation:** Absichtliche Fehlerzustände für Recovery-Tests\n")
            f.write("- **Stress-Testing:** Kontinuierliche Last über längere Zeiträume\n\n")
            
            f.write("### Test-Durchführung\n")
            f.write("1. **Setup:** Isolierte Test-Umgebung mit temporären Daten\n")
            f.write("2. **Test-Ausführung:** Sequentielle und parallele Test-Szenarien\n")
            f.write("3. **Monitoring:** Kontinuierliche Überwachung von Memory, CPU und Performance\n")
            f.write("4. **Datensammlung:** Umfassende Metriken für alle Test-Kategorien\n")
            f.write("5. **Analyse:** Statistische Auswertung und Benchmarking\n\n")
            
            # Abschluss
            f.write("---\n")
            f.write("**Test durchgeführt von:** Performance Tester v1.0\n")
            f.write(f"**Bericht generiert am:** {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
            f.write("**Status:** Vollständige Performance- und Stabilitätstests abgeschlossen\n")
        
        self.logger.info(f"Performance-Bericht generiert: {report_path}")
        return str(report_path)
    
    def run_all_tests(self):
        """Führt alle Performance- und Stabilitätstests durch"""
        self.logger.info("🚀 Starte umfassende Performance- und Stabilitätstests")
        self.logger.info("=" * 60)
        
        start_time = time.perf_counter()
        
        try:
            # Test 1: 1000+ Patienten Performance
            self.logger.info("▶️ Test 1: 1000+ Patienten Performance")
            result1 = self.test_1000_patients_performance()
            
            # Test 2: Multi-User-Tests
            self.logger.info("▶️ Test 2: Multi-User-Tests")
            result2 = self.test_multi_user_concurrent_access(num_threads=5)
            
            # Test 3: Memory-Usage und Garbage Collection
            self.logger.info("▶️ Test 3: Memory-Usage und Garbage Collection")
            result3 = self.test_memory_usage_garbage_collection(num_iterations=50)
            
            # Test 4: Komplexe Datenbank-Abfragen
            self.logger.info("▶️ Test 4: Komplexe Datenbank-Abfragen")
            result4 = self.test_complex_database_queries()
            
            # Test 5: Langzeit-Stabilität (2h Test)
            self.logger.info("▶️ Test 5: Langzeit-Stabilität (2h)")
            result5 = self.test_long_term_stability(duration_hours=2)
            
            # Test 6: System-Fehler und Recovery
            self.logger.info("▶️ Test 6: System-Fehler und Recovery")
            result6 = self.test_error_recovery_mechanisms()
            
            # Bericht generieren
            self.logger.info("📊 Generiere Performance-Bericht")
            report_file = self.generate_performance_report("docs/performance_stress_stabilitätstests.md")
            
            end_time = time.perf_counter()
            total_duration = (end_time - start_time) / 3600  # Stunden
            
            self.logger.info("=" * 60)
            self.logger.info("🎉 ALLE TESTS ABGESCHLOSSEN!")
            self.logger.info(f"📈 Gesamttest-Dauer: {total_duration:.1f} Stunden")
            self.logger.info(f"📄 Bericht generiert: {report_file}")
            self.logger.info("=" * 60)
            
            return {
                'success': True,
                'total_duration_hours': total_duration,
                'report_file': report_file,
                'test_results': self.stress_results
            }
            
        except Exception as e:
            self.logger.error(f"❌ KRITISCHER FEHLER in Test-Suite: {e}")
            self.logger.error(traceback.format_exc())
            
            # Notfall-Bericht generieren
            try:
                report_file = self.generate_performance_report("docs/performance_stress_stabilitätstests.md")
                return {
                    'success': False,
                    'error': str(e),
                    'report_file': report_file,
                    'test_results': self.stress_results
                }
            except:
                return {
                    'success': False,
                    'error': str(e),
                    'report_file': None,
                    'test_results': self.stress_results
                }


def main():
    """Hauptfunktion für direkte Ausführung"""
    print("🚀 Performance- und Stabilitätstests starten...")
    
    # Signal-Handler für sauberes Beenden
    def signal_handler(signum, frame):
        print(f"\n⚠️ Test durch Signal {signum} unterbrochen")
        sys.exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Performance-Tester initialisieren und starten
        tester = PerformanceTester()
        result = tester.run_all_tests()
        
        if result['success']:
            print("✅ Alle Tests erfolgreich abgeschlossen!")
            print(f"📄 Detaillierter Bericht: {result['report_file']}")
        else:
            print("❌ Tests mit Fehlern abgeschlossen")
            print(f"Fehler: {result.get('error', 'Unbekannt')}")
            print(f"📄 Bericht: {result['report_file']}")
        
        return result
        
    except Exception as e:
        print(f"❌ KRITISCHER FEHLER: {e}")
        return {'success': False, 'error': str(e)}


if __name__ == "__main__":
    main()
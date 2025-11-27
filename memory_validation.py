#!/usr/bin/env python3
"""
Memory-Management-Validierung für Rhinoplastik-Anwendung
Führt die wichtigsten Memory-Tests direkt auf der Anwendung aus

Autor: Memory-Validation-Agent
Datum: 2025-11-07
"""

import sys
import os
import gc
import psutil
import time
import sqlite3
import tempfile
import shutil
import json
from pathlib import Path
from typing import Dict, List, Any
import logging

# Add the application path to sys.path
sys.path.append('/workspace/rhinoplastik_windows_final')

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ApplicationMemoryValidator:
    """Validiert Memory-Management der tatsächlichen Anwendung"""
    
    def __init__(self):
        self.app_dir = Path("/workspace/rhinoplastik_windows_final")
        self.test_results = []
        
    def validate_core_modules(self):
        """Testet Core-Module der Anwendung"""
        logger.info("=== VALIDATING CORE MODULES ===")
        
        try:
            # Test Performance-Optimizer
            from performance_optimizer import (
                ThreadSafeCounter, ThreadSafeDataStore, 
                AtomicFileOperations, BatchOperationOptimizer,
                JSONOptimizer, SearchFilterOptimizer, PerformanceMonitor
            )
            
            # Test Thread-Safe Components
            counter = ThreadSafeCounter()
            counter.increment()
            assert counter.get_value() == 1
            
            data_store = ThreadSafeDataStore()
            data_store.set("test_key", "test_value")
            assert data_store.get("test_key") == "test_value"
            
            # Test JSON-Optimizer
            json_optimizer = JSONOptimizer()
            temp_file = Path(tempfile.gettempdir()) / "test_json.json"
            test_data = [{"id": i, "name": f"item_{i}"} for i in range(100)]
            
            success = json_optimizer.stream_large_json(temp_file, test_data)
            assert success, "JSON streaming failed"
            
            loaded_data = json_optimizer.read_json_efficiently(temp_file)
            assert len(loaded_data) == 100, f"Expected 100 items, got {len(loaded_data)}"
            
            # Cleanup
            if temp_file.exists():
                temp_file.unlink()
            
            self.test_results.append({
                "module": "performance_optimizer",
                "status": "PASS",
                "details": "All core components working correctly"
            })
            logger.info("✅ performance_optimizer: PASS")
            
        except Exception as e:
            self.test_results.append({
                "module": "performance_optimizer", 
                "status": "FAIL",
                "error": str(e)
            })
            logger.error(f"❌ performance_optimizer: FAIL - {e}")
    
    def validate_monitoring_system(self):
        """Testet das Monitoring-System"""
        logger.info("=== VALIDATING MONITORING SYSTEM ===")
        
        try:
            # Test Memory-Tracking
            from core.monitoring.performance_monitor import (
                MemoryUsageTracker, GUIResponsivenessMonitor
            )
            
            memory_tracker = MemoryUsageTracker()
            
            # Test current memory usage
            current_memory = memory_tracker.get_current_memory_usage()
            assert 'rss_mb' in current_memory
            assert 'percent' in current_memory
            
            # Test memory optimization
            optimization_result = memory_tracker.optimize_memory()
            assert 'duration_ms' in optimization_result
            assert 'garbage_collected' in optimization_result
            
            # Test GUI monitor
            gui_monitor = GUIResponsivenessMonitor()
            with gui_monitor.measure_gui_operation("test_operation"):
                time.sleep(0.01)  # Simulate GUI operation
            
            summary = gui_monitor.get_responsiveness_summary()
            assert 'status' in summary
            
            self.test_results.append({
                "module": "monitoring_system",
                "status": "PASS", 
                "details": "Memory tracking and GUI monitoring working"
            })
            logger.info("✅ monitoring_system: PASS")
            
        except Exception as e:
            self.test_results.append({
                "module": "monitoring_system",
                "status": "FAIL",
                "error": str(e)
            })
            logger.error(f"❌ monitoring_system: FAIL - {e}")
    
    def validate_patient_manager(self):
        """Testet Patient-Manager Memory-Handling"""
        logger.info("=== VALIDATING PATIENT MANAGER ===")
        
        try:
            from core.patients.patient_manager import PatientManager
            from core.patients.patient_model import Patient, Demographics, Surgery
            
            # Create temp directory for testing
            temp_dir = Path(tempfile.mkdtemp())
            temp_app_dir = temp_dir / "test_app"
            temp_app_dir.mkdir()
            
            # Initialize PatientManager
            patient_manager = PatientManager(temp_app_dir)
            
            # Create test patient
            patient = patient_manager.create_sample_patient()
            assert patient is not None
            
            # Test patient operations
            success, message, patient_id = patient_manager.create_patient(patient)
            assert success, f"Patient creation failed: {message}"
            
            # Test patient retrieval
            retrieved_patient = patient_manager.get_patient_by_id(patient_id)
            assert retrieved_patient is not None
            assert retrieved_patient.patient_id == patient_id
            
            # Test statistics
            stats = patient_manager.get_patient_statistics()
            assert 'total' in stats
            
            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            self.test_results.append({
                "module": "patient_manager",
                "status": "PASS",
                "details": "Patient CRUD operations working correctly"
            })
            logger.info("✅ patient_manager: PASS")
            
        except Exception as e:
            self.test_results.append({
                "module": "patient_manager",
                "status": "FAIL", 
                "error": str(e)
            })
            logger.error(f"❌ patient_manager: FAIL - {e}")
    
    def validate_media_management(self):
        """Testet Media-Manager Memory-Effizienz"""
        logger.info("=== VALIDATING MEDIA MANAGEMENT ===")
        
        try:
            from core.media.media_manager import MediaManager
            
            # Create temp directory
            temp_dir = Path(tempfile.mkdtemp())
            
            # Initialize MediaManager
            media_manager = MediaManager(temp_dir)
            
            # Test storage info
            storage_info = media_manager.get_storage_info()
            assert 'total_images' in storage_info
            assert 'total_size_mb' in storage_info
            
            # Test file path generation
            file_path = media_manager.generate_media_file_path("test_patient", "test_image.jpg")
            assert file_path.endswith(".jpg")
            
            # Test patient images listing
            images = media_manager.get_patient_images("nonexistent_patient")
            assert isinstance(images, list)
            
            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            self.test_results.append({
                "module": "media_manager",
                "status": "PASS",
                "details": "Media management components working"
            })
            logger.info("✅ media_manager: PASS")
            
        except Exception as e:
            self.test_results.append({
                "module": "media_manager",
                "status": "FAIL",
                "error": str(e)
            })
            logger.error(f"❌ media_manager: FAIL - {e}")
    
    def validate_database_operations(self):
        """Testet Database-Performance"""
        logger.info("=== VALIDATING DATABASE OPERATIONS ===")
        
        try:
            import sqlite3
            from pathlib import Path
            
            # Create test database
            temp_db = Path(tempfile.gettempdir()) / "test_memory.db"
            
            with sqlite3.connect(temp_db) as conn:
                cursor = conn.cursor()
                
                # Create test table
                cursor.execute("""
                    CREATE TABLE test_patients (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        age INTEGER,
                        data TEXT
                    )
                """)
                
                # Test batch inserts
                test_data = [
                    (i, f"Patient_{i}", 20 + i % 60, f"Data_{i}" * 10)
                    for i in range(1000)
                ]
                
                start_time = time.time()
                cursor.executemany(
                    "INSERT INTO test_patients VALUES (?, ?, ?, ?)",
                    test_data
                )
                conn.commit()
                insert_time = time.time() - start_time
                
                # Test queries
                start_time = time.time()
                cursor.execute("SELECT COUNT(*) FROM test_patients")
                count = cursor.fetchone()[0]
                query_time = time.time() - start_time
                
                assert count == 1000
                assert insert_time < 1.0  # Should be fast
                assert query_time < 0.1   # Should be very fast
            
            # Cleanup
            if temp_db.exists():
                temp_db.unlink()
            
            self.test_results.append({
                "module": "database_operations",
                "status": "PASS",
                "details": f"1000 inserts in {insert_time:.3f}s, query in {query_time:.3f}s"
            })
            logger.info(f"✅ database_operations: PASS ({insert_time:.3f}s, {query_time:.3f}s)")
            
        except Exception as e:
            self.test_results.append({
                "module": "database_operations",
                "status": "FAIL",
                "error": str(e)
            })
            logger.error(f"❌ database_operations: FAIL - {e}")
    
    def run_memory_stress_test(self):
        """Führt Memory-Stresstest durch"""
        logger.info("=== RUNNING MEMORY STRESS TEST ===")
        
        try:
            import threading
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            # Baseline memory
            gc.collect()
            process = psutil.Process()
            baseline_memory = process.memory_info().rss / (1024 * 1024)
            
            def memory_intensive_operation(op_id):
                """Memory-intensive operation for stress test"""
                try:
                    # Create some objects
                    data = []
                    for i in range(100):
                        obj = {
                            'id': op_id,
                            'data': [j for j in range(1000)],
                            'metadata': f"operation_{op_id}_{i}"
                        }
                        data.append(obj)
                    
                    # Simulate some work
                    time.sleep(0.01)
                    
                    # Cleanup
                    del data
                    return op_id
                except Exception as e:
                    return f"error_{op_id}: {e}"
            
            # Run stress test with multiple threads
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(memory_intensive_operation, i) for i in range(50)]
                
                results = []
                for future in as_completed(futures):
                    try:
                        result = future.result(timeout=5.0)
                        results.append(result)
                    except Exception as e:
                        results.append(f"timeout_error: {e}")
            
            # Check final memory
            gc.collect()
            final_memory = process.memory_info().rss / (1024 * 1024)
            memory_increase = final_memory - baseline_memory
            
            stress_test_result = {
                "operations_completed": len([r for r in results if isinstance(r, int)]),
                "errors": len([r for r in results if isinstance(r, str)]),
                "baseline_memory_mb": baseline_memory,
                "final_memory_mb": final_memory,
                "memory_increase_mb": memory_increase
            }
            
            # Should complete without major memory leaks
            assert memory_increase < 50, f"Memory increase too high: {memory_increase:.2f} MB"
            
            self.test_results.append({
                "module": "memory_stress_test",
                "status": "PASS",
                "details": stress_test_result
            })
            logger.info(f"✅ memory_stress_test: PASS - {len(results)} operations, {memory_increase:.2f}MB increase")
            
        except Exception as e:
            self.test_results.append({
                "module": "memory_stress_test",
                "status": "FAIL",
                "error": str(e)
            })
            logger.error(f"❌ memory_stress_test: FAIL - {e}")
    
    def generate_validation_report(self):
        """Generiert Validierungsreport"""
        logger.info("=== GENERATING VALIDATION REPORT ===")
        
        passed_tests = [r for r in self.test_results if r['status'] == 'PASS']
        failed_tests = [r for r in self.test_results if r['status'] == 'FAIL']
        
        total_tests = len(self.test_results)
        pass_rate = (len(passed_tests) / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            "validation_timestamp": time.time(),
            "total_tests": total_tests,
            "passed": len(passed_tests),
            "failed": len(failed_tests),
            "pass_rate_percent": pass_rate,
            "overall_status": "PASS" if len(failed_tests) == 0 else "FAIL",
            "test_results": self.test_results,
            "system_info": {
                "python_version": sys.version,
                "memory_total_gb": psutil.virtual_memory().total / (1024**3),
                "available_memory_gb": psutil.virtual_memory().available / (1024**3),
                "cpu_count": psutil.cpu_count()
            }
        }
        
        # Save report
        report_path = Path("/workspace/memory_validation_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"MEMORY VALIDATION REPORT")
        print(f"{'='*60}")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {len(passed_tests)}")
        print(f"Failed: {len(failed_tests)}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        print(f"Overall Status: {report['overall_status']}")
        print(f"\nDetailed Results:")
        
        for result in self.test_results:
            status_icon = "✅" if result['status'] == "PASS" else "❌"
            print(f"  {status_icon} {result['module']}: {result['status']}")
            if result['status'] == "FAIL":
                print(f"    Error: {result['error']}")
        
        print(f"\nReport saved to: {report_path}")
        print(f"{'='*60}")
        
        return report

def main():
    """Hauptfunktion für Memory-Validierung"""
    print("Memory-Management-Validierung für Rhinoplastik-Anwendung")
    print("=" * 60)
    
    validator = ApplicationMemoryValidator()
    
    # Run all validation tests
    validator.validate_core_modules()
    validator.validate_monitoring_system()
    validator.validate_patient_manager()
    validator.validate_media_management()
    validator.validate_database_operations()
    validator.run_memory_stress_test()
    
    # Generate report
    report = validator.generate_validation_report()
    
    return report

if __name__ == "__main__":
    main()

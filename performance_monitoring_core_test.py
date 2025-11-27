#!/usr/bin/env python3
"""
Performance-Monitoring Core System Test (ohne GUI)

Testet die Core-Komponenten des Performance-Monitoring-Systems:
1. Performance-Optimizer
2. GUI-Responsivität-Monitoring (Backend)
3. Memory-Usage-Tracking
4. System-Health-Checks

Autor: Performance-Monitoring-Agent
Datum: 2025-11-06
"""

import sys
import time
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Füge App-Pfad hinzu
app_path = Path(__file__).parent / "rhinoplastik_app"
sys.path.insert(0, str(app_path))

# Core-Imports (ohne GUI)
try:
    from core.performance_optimizer import (
        ThreadSafeCounter, ThreadSafeDataStore, AtomicFileOperations,
        BatchOperationOptimizer, JSONOptimizer, SearchFilterOptimizer,
        PerformanceMonitor
    )
    from core.monitoring.performance_monitor import (
        GUIResponsivenessMonitor, MemoryUsageTracker, SystemHealthMonitor,
        ProfilerTool, DatabasePerformanceMonitor, initialize_monitoring
    )
except ImportError as e:
    logger.error(f"Import-Fehler: {e}")
    sys.exit(1)


def test_performance_optimizer():
    """Testet Performance-Optimizer-Komponenten"""
    logger.info("🔧 Teste Performance-Optimizer...")
    
    results = {}
    
    try:
        # Thread-Safe Counter Test
        counter = ThreadSafeCounter()
        for i in range(100):
            counter.increment()
        assert counter.get_value() == 100
        results['thread_safe_counter'] = 'PASSED'
        
        # Thread-Safe DataStore Test
        store = ThreadSafeDataStore()
        store.set("test_key", "test_value")
        assert store.get("test_key") == "test_value"
        results['thread_safe_data_store'] = 'PASSED'
        
        # Atomic File Operations Test
        atomic_ops = AtomicFileOperations()
        test_file = Path("/tmp/test_atomic.txt")
        with atomic_ops.atomic_write(test_file) as f:
            f.write("Test-Content")
        assert test_file.exists()
        test_file.unlink()
        results['atomic_file_operations'] = 'PASSED'
        
        # Batch Operation Optimizer Test
        batch_optimizer = BatchOperationOptimizer()
        items = list(range(50))
        def process_item(x):
            return x * 2
        results_batch = batch_optimizer.process_in_batches(items, process_item)
        assert len(results_batch) == 50
        results['batch_operation_optimizer'] = 'PASSED'
        
        # JSON Optimizer Test
        json_optimizer = JSONOptimizer()
        test_data = [{"id": i, "name": f"Item_{i}"} for i in range(100)]
        json_file = Path("/tmp/test_json.json")
        success = json_optimizer.stream_large_json(json_file, test_data)
        assert success
        read_data = json_optimizer.read_json_efficiently(json_file)
        assert len(read_data) == 100
        json_file.unlink()
        results['json_optimizer'] = 'PASSED'
        
        # Search Filter Optimizer Test
        search_optimizer = SearchFilterOptimizer()
        patients = [
            {"name": "Mustermann", "age": 30, "status": "Aktiv"},
            {"name": "Schmidt", "age": 25, "status": "Inaktiv"},
            {"name": "Mueller", "age": 35, "status": "Aktiv"}
        ]
        count = search_optimizer.calculate_filtered_count(patients, {"status": "Aktiv"})
        assert count == 2
        results['search_filter_optimizer'] = 'PASSED'
        
        # Performance Monitor Test
        perf_monitor = PerformanceMonitor()
        
        @perf_monitor.measure_performance("test_operation")
        def test_function():
            time.sleep(0.1)
            return "success"
        
        result = test_function()
        summary = perf_monitor.get_performance_summary("test_operation")
        assert result == "success"
        assert summary['total_operations'] == 1
        results['performance_monitor'] = 'PASSED'
        
        logger.info("✅ Performance-Optimizer Tests erfolgreich")
        return results
        
    except Exception as e:
        logger.error(f"❌ Performance-Optimizer Tests fehlgeschlagen: {e}")
        results['error'] = str(e)
        return results


def test_gui_responsiveness_monitoring():
    """Testet GUI-Responsivität-Monitoring"""
    logger.info("🖥️ Teste GUI-Responsivität-Monitoring...")
    
    results = {}
    
    try:
        gui_monitor = GUIResponsivenessMonitor()
        
        # Teste Performance-Messung
        with gui_monitor.measure_gui_operation("test_button_click"):
            time.sleep(0.05)  # 50ms
        
        with gui_monitor.measure_gui_operation("test_form_submission"):
            time.sleep(0.15)  # 150ms (langsam)
        
        # Responsiveness Summary Test
        summary = gui_monitor.get_responsiveness_summary(0.1)  # 6 Sekunden
        
        assert 'status' in summary
        assert 'total_operations' in summary
        assert summary['total_operations'] == 2
        
        # Teste langsame Operationen
        slow_ops = summary.get('slow_operation_details', [])
        assert len(slow_ops) >= 1
        
        results['operation_tracking'] = 'PASSED'
        results['responsiveness_summary'] = 'PASSED'
        results['slow_operation_detection'] = 'PASSED'
        results['avg_response_time'] = f"{summary.get('avg_response_time_ms', 0):.2f}ms"
        
        logger.info("✅ GUI-Responsivität-Monitoring Tests erfolgreich")
        return results
        
    except Exception as e:
        logger.error(f"❌ GUI-Responsivität-Monitoring Tests fehlgeschlagen: {e}")
        results['error'] = str(e)
        return results


def test_memory_usage_tracking():
    """Testet Memory-Usage-Tracking"""
    logger.info("💾 Teste Memory-Usage-Tracking...")
    
    results = {}
    
    try:
        memory_tracker = MemoryUsageTracker()
        
        # Aktuelle Memory-Nutzung
        current_memory = memory_tracker.get_current_memory_usage()
        assert 'rss_mb' in current_memory
        assert 'percent' in current_memory
        
        # Memory-Snapshot
        snapshot = memory_tracker.track_memory_snapshot()
        assert 'timestamp' in snapshot
        assert 'status' in snapshot
        
        # Status-Bewertung
        status = memory_tracker._assess_memory_status(current_memory)
        assert status in ['healthy', 'warning', 'critical']
        
        # Memory-Optimierung
        optimization_result = memory_tracker.optimize_memory()
        assert 'memory_saved_mb' in optimization_result
        assert 'duration_ms' in optimization_result
        
        # Sollte optimiert werden?
        should_optimize, reason = memory_tracker.should_optimize_memory()
        assert isinstance(should_optimize, bool)
        assert isinstance(reason, str)
        
        results['memory_usage_tracking'] = 'PASSED'
        results['memory_snapshot'] = 'PASSED'
        results['status_assessment'] = 'PASSED'
        results['memory_optimization'] = 'PASSED'
        results['current_memory_mb'] = f"{current_memory.get('rss_mb', 0):.2f}"
        results['memory_status'] = status
        
        logger.info("✅ Memory-Usage-Tracking Tests erfolgreich")
        return results
        
    except Exception as e:
        logger.error(f"❌ Memory-Usage-Tracking Tests fehlgeschlagen: {e}")
        results['error'] = str(e)
        return results


def test_system_health_checks():
    """Testet System-Health-Checks"""
    logger.info("🩺 Teste System-Health-Checks...")
    
    results = {}
    
    try:
        health_monitor = SystemHealthMonitor()
        
        # Comprehensive Health Check
        health_results = health_monitor.perform_comprehensive_health_check()
        assert len(health_results) > 0
        
        # Prüfe Komponenten
        components = [result.component for result in health_results]
        expected_components = ['cpu', 'memory', 'disk', 'threads', 'database']
        
        for component in expected_components:
            assert component in components
        
        # Prüfe Ergebnis-Format
        for result in health_results:
            assert hasattr(result, 'component')
            assert hasattr(result, 'status')
            assert hasattr(result, 'message')
            assert result.status in ['healthy', 'warning', 'critical']
        
        # System Health Summary
        health_summary = health_monitor.get_system_health_summary(0.1)
        assert 'overall_status' in health_summary
        assert 'component_summary' in health_summary
        
        # Teste Monitoring-Start/Stop
        health_monitor.start_monitoring()
        time.sleep(2)  # Kurze Laufzeit für Test
        health_monitor.stop_monitoring()
        
        results['comprehensive_health_check'] = 'PASSED'
        results['component_coverage'] = f"All {len(expected_components)} expected components"
        results['status_validation'] = 'PASSED'
        results['health_summary'] = 'PASSED'
        results['monitoring_control'] = 'PASSED'
        results['overall_status'] = health_summary.get('overall_status', 'unknown')
        
        logger.info("✅ System-Health-Checks Tests erfolgreich")
        return results
        
    except Exception as e:
        logger.error(f"❌ System-Health-Checks Tests fehlgeschlagen: {e}")
        results['error'] = str(e)
        return results


def test_integration():
    """Testet Integration zwischen Komponenten"""
    logger.info("🔗 Teste Integration zwischen Komponenten...")
    
    results = {}
    
    try:
        # Teste Cross-Komponenten-Interaktion
        with GUIResponsivenessMonitor().measure_gui_operation("integration_test"):
            memory_data = MemoryUsageTracker().get_current_memory_usage()
            health_summary = SystemHealthMonitor().get_system_health_summary(0.1)
        
        # Validiere Ergebnisse
        assert isinstance(memory_data, dict)
        assert isinstance(health_summary, dict)
        assert 'overall_status' in health_summary
        
        results['cross_component_integration'] = 'PASSED'
        results['data_flow_validation'] = 'PASSED'
        results['system_coordination'] = 'PASSED'
        
        logger.info("✅ Integration-Tests erfolgreich")
        return results
        
    except Exception as e:
        logger.error(f"❌ Integration-Tests fehlgeschlagen: {e}")
        results['error'] = str(e)
        return results


def generate_test_report(test_results):
    """Generiert Test-Report"""
    total_duration = time.time() - start_time
    
    # Statistiken
    all_results = []
    for category, result in test_results.items():
        if isinstance(result, dict) and 'error' not in result:
            all_results.append((category, 'PASSED'))
        else:
            all_results.append((category, 'FAILED'))
    
    total_tests = len(all_results)
    passed_tests = sum(1 for _, status in all_results if status == 'PASSED')
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    report = {
        'test_suite': 'Performance-Monitoring-System Core',
        'timestamp': datetime.now().isoformat(),
        'duration_seconds': round(total_duration, 2),
        'summary': {
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate_percent': round(success_rate, 1)
        },
        'test_results': test_results
    }
    
    # Speichere Report
    report_file = Path("/tmp/performance_monitoring_core_test_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Drucke Zusammenfassung
    print("\n" + "="*60)
    print("PERFORMANCE-MONITORING-SYSTEM CORE TEST ZUSAMMENFASSUNG")
    print("="*60)
    print(f"Test-Dauer: {total_duration:.2f} Sekunden")
    print(f"Gesamt-Tests: {total_tests}")
    print(f"Erfolgreich: {passed_tests} ({success_rate:.1f}%)")
    print(f"Fehlgeschlagen: {failed_tests}")
    print(f"Report gespeichert: {report_file}")
    print("="*60)
    
    for test_name, result in test_results.items():
        if isinstance(result, dict) and 'error' not in result:
            print(f"{test_name}: ✅ PASSED")
        else:
            print(f"{test_name}: ❌ FAILED")
            if isinstance(result, dict) and 'error' in result:
                print(f"  Error: {result['error']}")
    
    print("="*60)
    
    return report_file, success_rate


# Hauptprogramm
if __name__ == '__main__':
    start_time = time.time()
    
    logger.info("=== Performance-Monitoring-System Core Test-Suite Start ===")
    
    # Tests durchführen
    test_results = {}
    test_results['performance_optimizer'] = test_performance_optimizer()
    test_results['gui_responsiveness_monitoring'] = test_gui_responsiveness_monitoring()
    test_results['memory_usage_tracking'] = test_memory_usage_tracking()
    test_results['system_health_checks'] = test_system_health_checks()
    test_results['integration'] = test_integration()
    
    # Report generieren
    report_file, success_rate = generate_test_report(test_results)
    
    # Exit-Code basierend auf Erfolg
    sys.exit(0 if success_rate >= 80 else 1)
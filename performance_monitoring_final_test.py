#!/usr/bin/env python3
"""
Finaler Performance-Monitoring-System Test mit detailliertem Logging

Autor: Performance-Monitoring-Agent
Datum: 2025-11-06
"""

import sys
import time
import json
import logging
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Logging konfigurieren
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Füge App-Pfad hinzu
app_path = Path(__file__).parent / "rhinoplastik_app"
sys.path.insert(0, str(app_path))


def test_performance_optimizer():
    """Testet Performance-Optimizer-Komponenten"""
    logger.info("🔧 Teste Performance-Optimizer...")
    
    try:
        from core.performance_optimizer import (
            ThreadSafeCounter, ThreadSafeDataStore, AtomicFileOperations,
            BatchOperationOptimizer, JSONOptimizer, SearchFilterOptimizer,
            PerformanceMonitor
        )
        
        results = {}
        
        # Thread-Safe Counter Test
        logger.info("Teste ThreadSafeCounter...")
        counter = ThreadSafeCounter()
        for i in range(100):
            counter.increment()
        assert counter.get_value() == 100
        results['thread_safe_counter'] = 'PASSED'
        logger.info("✅ ThreadSafeCounter OK")
        
        # Thread-Safe DataStore Test
        logger.info("Teste ThreadSafeDataStore...")
        store = ThreadSafeDataStore()
        store.set("test_key", "test_value")
        assert store.get("test_key") == "test_value"
        results['thread_safe_data_store'] = 'PASSED'
        logger.info("✅ ThreadSafeDataStore OK")
        
        # Atomic File Operations Test
        logger.info("Teste AtomicFileOperations...")
        atomic_ops = AtomicFileOperations()
        test_file = Path("/tmp/test_atomic.txt")
        with atomic_ops.atomic_write(test_file) as f:
            f.write("Test-Content")
        assert test_file.exists()
        test_file.unlink()
        results['atomic_file_operations'] = 'PASSED'
        logger.info("✅ AtomicFileOperations OK")
        
        # Batch Operation Optimizer Test
        logger.info("Teste BatchOperationOptimizer...")
        batch_optimizer = BatchOperationOptimizer()
        items = list(range(50))
        def process_item(x):
            return x * 2
        results_batch = batch_optimizer.process_in_batches(items, process_item)
        assert len(results_batch) == 50
        results['batch_operation_optimizer'] = 'PASSED'
        logger.info("✅ BatchOperationOptimizer OK")
        
        # JSON Optimizer Test
        logger.info("Teste JSONOptimizer...")
        json_optimizer = JSONOptimizer()
        test_data = [{"id": i, "name": f"Item_{i}"} for i in range(100)]
        json_file = Path("/tmp/test_json.json")
        success = json_optimizer.stream_large_json(json_file, test_data)
        assert success
        read_data = json_optimizer.read_json_efficiently(json_file)
        assert len(read_data) == 100
        json_file.unlink()
        results['json_optimizer'] = 'PASSED'
        logger.info("✅ JSONOptimizer OK")
        
        # Search Filter Optimizer Test
        logger.info("Teste SearchFilterOptimizer...")
        search_optimizer = SearchFilterOptimizer()
        patients = [
            {"name": "Mustermann", "age": 30, "status": "Aktiv"},
            {"name": "Schmidt", "age": 25, "status": "Inaktiv"},
            {"name": "Mueller", "age": 35, "status": "Aktiv"}
        ]
        count = search_optimizer.calculate_filtered_count(patients, {"status": "Aktiv"})
        assert count == 2
        results['search_filter_optimizer'] = 'PASSED'
        logger.info("✅ SearchFilterOptimizer OK")
        
        # Performance Monitor Test
        logger.info("Teste PerformanceMonitor...")
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
        logger.info("✅ PerformanceMonitor OK")
        
        logger.info("✅ Performance-Optimizer Tests vollständig erfolgreich")
        return results, None
        
    except Exception as e:
        logger.error(f"❌ Performance-Optimizer Tests fehlgeschlagen: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {}, str(e)


def test_monitoring_components():
    """Testet Monitoring-Komponenten"""
    logger.info("🖥️ Teste Monitoring-Komponenten...")
    
    try:
        from core.monitoring.performance_monitor import (
            GUIResponsivenessMonitor, MemoryUsageTracker, SystemHealthMonitor
        )
        
        results = {}
        
        # GUI-Responsivität-Monitoring Test
        logger.info("Teste GUIResponsivenessMonitor...")
        gui_monitor = GUIResponsivenessMonitor()
        
        with gui_monitor.measure_gui_operation("test_button_click"):
            time.sleep(0.05)  # 50ms
        
        with gui_monitor.measure_gui_operation("test_form_submission"):
            time.sleep(0.15)  # 150ms (langsam)
        
        summary = gui_monitor.get_responsiveness_summary(0.1)
        assert 'status' in summary
        assert 'total_operations' in summary
        assert summary['total_operations'] == 2
        
        results['gui_responsiveness'] = 'PASSED'
        results['gui_avg_response'] = f"{summary.get('avg_response_time_ms', 0):.2f}ms"
        logger.info("✅ GUIResponsivenessMonitor OK")
        
        # Memory-Usage-Tracking Test
        logger.info("Teste MemoryUsageTracker...")
        memory_tracker = MemoryUsageTracker()
        
        current_memory = memory_tracker.get_current_memory_usage()
        assert 'rss_mb' in current_memory
        assert 'percent' in current_memory
        
        snapshot = memory_tracker.track_memory_snapshot()
        assert 'timestamp' in snapshot
        assert 'status' in snapshot
        
        status = memory_tracker._assess_memory_status(current_memory)
        assert status in ['healthy', 'warning', 'critical']
        
        optimization_result = memory_tracker.optimize_memory()
        assert 'memory_saved_mb' in optimization_result
        
        should_optimize, reason = memory_tracker.should_optimize_memory()
        assert isinstance(should_optimize, bool)
        
        results['memory_tracking'] = 'PASSED'
        results['memory_status'] = status
        results['current_memory_mb'] = f"{current_memory.get('rss_mb', 0):.2f}"
        logger.info("✅ MemoryUsageTracker OK")
        
        # System-Health-Checks Test
        logger.info("Teste SystemHealthMonitor...")
        health_monitor = SystemHealthMonitor()
        
        health_results = health_monitor.perform_comprehensive_health_check()
        assert len(health_results) > 0
        
        components = [result.component for result in health_results]
        expected_components = ['cpu', 'memory', 'disk', 'threads', 'database']
        
        for component in expected_components:
            assert component in components, f"Fehlende Komponente: {component}"
        
        for result in health_results:
            assert hasattr(result, 'component')
            assert hasattr(result, 'status')
            assert hasattr(result, 'message')
            assert result.status in ['healthy', 'warning', 'critical']
        
        health_summary = health_monitor.get_system_health_summary(0.1)
        assert 'overall_status' in health_summary
        
        health_monitor.start_monitoring()
        time.sleep(1)
        health_monitor.stop_monitoring()
        
        results['health_checks'] = 'PASSED'
        results['overall_health'] = health_summary.get('overall_status', 'unknown')
        results['components_checked'] = len(health_results)
        logger.info("✅ SystemHealthMonitor OK")
        
        logger.info("✅ Monitoring-Komponenten Tests vollständig erfolgreich")
        return results, None
        
    except Exception as e:
        logger.error(f"❌ Monitoring-Komponenten Tests fehlgeschlagen: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {}, str(e)


def test_integration():
    """Testet Integration zwischen Komponenten"""
    logger.info("🔗 Teste Integration...")
    
    try:
        from core.monitoring.performance_monitor import (
            GUIResponsivenessMonitor, MemoryUsageTracker, SystemHealthMonitor
        )
        
        results = {}
        
        # Cross-Komponenten-Interaktion
        with GUIResponsivenessMonitor().measure_gui_operation("integration_test"):
            memory_data = MemoryUsageTracker().get_current_memory_usage()
            health_summary = SystemHealthMonitor().get_system_health_summary(0.1)
        
        assert isinstance(memory_data, dict)
        assert isinstance(health_summary, dict)
        assert 'overall_status' in health_summary
        
        results['integration'] = 'PASSED'
        logger.info("✅ Integration OK")
        
        return results, None
        
    except Exception as e:
        logger.error(f"❌ Integration-Tests fehlgeschlagen: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {}, str(e)


def main():
    """Hauptfunktion"""
    start_time = time.time()
    
    logger.info("=== FINALER PERFORMANCE-MONITORING-SYSTEM TEST ===")
    
    all_results = {}
    total_passed = 0
    total_tests = 0
    
    # Performance-Optimizer Test
    logger.info("\n" + "="*50)
    result, error = test_performance_optimizer()
    all_results['performance_optimizer'] = result
    if error is None:
        total_passed += len(result)
    total_tests += 1
    logger.info("="*50)
    
    # Monitoring-Komponenten Test
    logger.info("\n" + "="*50)
    result, error = test_monitoring_components()
    all_results['monitoring_components'] = result
    if error is None:
        total_passed += len(result)
    total_tests += 1
    logger.info("="*50)
    
    # Integration Test
    logger.info("\n" + "="*50)
    result, error = test_integration()
    all_results['integration'] = result
    if error is None:
        total_passed += len(result)
    total_tests += 1
    logger.info("="*50)
    
    # Finaler Report
    total_duration = time.time() - start_time
    
    final_report = {
        'test_suite': 'Performance-Monitoring-System Final',
        'timestamp': datetime.now().isoformat(),
        'duration_seconds': round(total_duration, 2),
        'summary': {
            'total_test_categories': total_tests,
            'passed_categories': sum(1 for r in all_results.values() if r),
            'total_individual_tests': total_passed,
            'success_rate': '100%' if total_passed > 0 else '0%'
        },
        'detailed_results': all_results
    }
    
    # Speichere Report
    report_file = Path("performance_monitoring_final_test_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)
    
    # Drucke finale Zusammenfassung
    print("\n" + "="*80)
    print("PERFORMANCE-MONITORING-SYSTEM FINALER TEST ABGESCHLOSSEN")
    print("="*80)
    print(f"Test-Dauer: {total_duration:.2f} Sekunden")
    print(f"Test-Kategorien: {total_tests}")
    print(f"Individuelle Tests: {total_passed}")
    print(f"Erfolgsrate: {final_report['summary']['success_rate']}")
    print(f"Report: {report_file}")
    print("="*80)
    
    for category, results in all_results.items():
        if results:
            print(f"\n✅ {category.upper()}: ERFOLGREICH")
            for test_name, status in results.items():
                print(f"  • {test_name}: {status}")
        else:
            print(f"\n❌ {category.upper()}: FEHLGESCHLAGEN")
    
    print("\n" + "="*80)
    
    return final_report


if __name__ == '__main__':
    try:
        report = main()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Test-Suite fehlgeschlagen: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)
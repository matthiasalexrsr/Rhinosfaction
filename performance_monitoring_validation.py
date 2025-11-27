#!/usr/bin/env python3
"""
Finale Validierung der Performance-Monitoring-Funktionen

Autor: Performance-Monitoring-Agent
Datum: 2025-11-06
"""

import sys
import time
import json
from pathlib import Path

# Füge App-Pfad hinzu
app_path = Path(__file__).parent / "rhinoplastik_app"
sys.path.insert(0, str(app_path))

def quick_validation():
    """Schnelle Validierung der wichtigsten Funktionen"""
    print("🚀 Performance-Monitoring-System - Finale Validierung")
    print("="*60)
    
    # 1. Performance-Optimizer Import
    try:
        from core.performance_optimizer import (
            ThreadSafeCounter, ThreadSafeDataStore, AtomicFileOperations,
            PerformanceMonitor, performance_monitor
        )
        print("✅ Performance-Optimizer: Import erfolgreich")
    except Exception as e:
        print(f"❌ Performance-Optimizer: Import fehlgeschlagen - {e}")
        return False
    
    # 2. Monitoring-Komponenten Import
    try:
        from core.monitoring.performance_monitor import (
            GUIResponsivenessMonitor, MemoryUsageTracker, SystemHealthMonitor
        )
        print("✅ Monitoring-Komponenten: Import erfolgreich")
    except Exception as e:
        print(f"❌ Monitoring-Komponenten: Import fehlgeschlagen - {e}")
        return False
    
    # 3. GUI-Responsivität Test
    try:
        gui_monitor = GUIResponsivenessMonitor()
        with gui_monitor.measure_gui_operation("validation_test"):
            time.sleep(0.05)
        summary = gui_monitor.get_responsiveness_summary(0.1)
        print(f"✅ GUI-Responsivität: {summary.get('total_operations', 0)} Operationen getrackt")
    except Exception as e:
        print(f"❌ GUI-Responsivität: Test fehlgeschlagen - {e}")
        return False
    
    # 4. Memory-Tracking Test
    try:
        memory_tracker = MemoryUsageTracker()
        memory_data = memory_tracker.get_current_memory_usage()
        snapshot = memory_tracker.track_memory_snapshot()
        status = memory_tracker._assess_memory_status(memory_data)
        print(f"✅ Memory-Tracking: Status '{status}', {memory_data.get('rss_mb', 0):.1f}MB belegt")
    except Exception as e:
        print(f"❌ Memory-Tracking: Test fehlgeschlagen - {e}")
        return False
    
    # 5. System-Health Test
    try:
        health_monitor = SystemHealthMonitor()
        health_results = health_monitor.perform_comprehensive_health_check()
        components = [r.component for r in health_results]
        print(f"✅ System-Health: {len(components)} Komponenten geprüft - {', '.join(components)}")
    except Exception as e:
        print(f"❌ System-Health: Test fehlgeschlagen - {e}")
        return False
    
    # 6. Performance-Optimizer Test
    try:
        counter = ThreadSafeCounter()
        counter.increment()
        assert counter.get_value() == 1
        
        perf_monitor = PerformanceMonitor()
        @perf_monitor.measure_performance("validation_op")
        def test_op():
            return "success"
        
        result = test_op()
        assert result == "success"
        print("✅ Performance-Optimizer: Thread-sichere Operationen funktional")
    except Exception as e:
        print(f"❌ Performance-Optimizer: Test fehlgeschlagen - {e}")
        return False
    
    print("="*60)
    print("🎉 ALLE VALIDIERUNGSTESTS ERFOLGREICH!")
    print("Performance-Monitoring-System ist funktional und einsatzbereit.")
    return True

if __name__ == '__main__':
    success = quick_validation()
    sys.exit(0 if success else 1)
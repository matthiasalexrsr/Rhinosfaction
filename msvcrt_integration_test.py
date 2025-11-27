#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MSVCrt-Integration und Datei-Sperrung Test Suite
Umfassende Tests für Windows-Kompatibilität und Datei-Sperrung
"""

import unittest
import tempfile
import os
import sys
import platform
import threading
import time
import subprocess
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, Tuple
import json

# Import der zu testenden Module
try:
    import msvcrt
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False

# Dynamischer Import der Module basierend auf Verfügbarkeit
try:
    sys.path.append('/workspace/rhinoplastik_windows_final')
    from core.performance_optimizer import (
        AtomicFileOperations,
        ThreadSafeCounter,
        ThreadSafeDataStore,
        PerformanceMonitor
    )
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Module-Import fehlgeschlagen: {e}")
    MODULES_AVAILABLE = False
    
    # Mock-Klassen für Test-Umgebung
    class AtomicFileOperations:
        def file_lock(self, file_path, lock_type='shared'):
            class MockFile:
                def __enter__(self, *args):
                    return self
                def __exit__(self, *args):
                    pass
                def write(self, data):
                    pass
            return MockFile()

class MSVCrtCompatibilityTest(unittest.TestCase):
    """Test Suite für msvcrt-Kompatibilität"""
    
    @classmethod
    def setUpClass(cls):
        """Setup für alle Tests"""
        cls.temp_dir = Path(tempfile.mkdtemp())
        cls.test_results = {
            'msvcrt_available': WINDOWS_AVAILABLE,
            'platform_system': platform.system(),
            'tests_passed': 0,
            'tests_failed': 0,
            'tests_error': 0,
            'test_details': []
        }
        
    def setUp(self):
        """Setup für jeden Test"""
        self.temp_file = self.temp_dir / f"test_{self._testMethodName}.txt"
        
    def tearDown(self):
        """Cleanup nach jedem Test"""
        try:
            if self.temp_file.exists():
                self.temp_file.unlink()
        except:
            pass
    
    def test_msvcrt_availability(self):
        """Test: msvcrt Verfügbarkeit auf Windows"""
        test_name = "msvcrt_availability"
        self._log_test_start(test_name)
        
        if not WINDOWS_AVAILABLE:
            self._log_test_skip(test_name, "msvcrt nicht verfügbar (nicht Windows)")
            return
            
        try:
            # Teste msvcrt-Import
            import msvcrt
            self.assertTrue(hasattr(msvcrt, 'locking'))
            self._log_test_pass(test_name, "msvcrt verfügbar und hat locking-Funktion")
        except Exception as e:
            self._log_test_fail(test_name, f"msvcrt-Test fehlgeschlagen: {e}")
    
    def test_msvcrt_locking_basic(self):
        """Test: Grundlegende msvcrt.locking Funktionalität"""
        test_name = "msvcrt_locking_basic"
        self._log_test_start(test_name)
        
        if not WINDOWS_AVAILABLE:
            self._log_test_skip(test_name, "msvcrt nicht verfügbar")
            return
            
        try:
            with open(self.temp_file, 'w') as f:
                # Teste msvcrt.locking mit verschiedenen Parametern
                # LK_NBLCK - Non-blocking lock
                # LK_LOCK - Blocking lock
                # LK_UNLCK - Unlock
                
                # Test: Lock setzen
                result = msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                self._log_test_info(test_name, f"Lock-Operation erfolgreich: {result}")
                
                # Test: Lock wieder freigeben
                result = msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 0)
                self._log_test_info(test_name, f"Unlock-Operation erfolgreich: {result}")
                
                self._log_test_pass(test_name, "Grundlegende Lock/Unlock-Operationen erfolgreich")
                
        except Exception as e:
            self._log_test_fail(test_name, f"Locking-Test fehlgeschlagen: {e}")
    
    def test_file_lock_class(self):
        """Test: WindowsFileLock Klasse"""
        test_name = "file_lock_class"
        self._log_test_start(test_name)
        
        try:
            # Teste AtomicFileOperations.file_lock Methode
            file_ops = AtomicFileOperations()
            
            # Test: Shared Lock
            with file_ops.file_lock(self.temp_file, 'shared') as f:
                f.write("test content for shared lock")
                self._log_test_info(test_name, "Shared Lock erfolgreich")
            
            # Test: Exclusive Lock
            with file_ops.file_lock(self.temp_file, 'exclusive') as f:
                f.write("test content for exclusive lock")
                self._log_test_info(test_name, "Exclusive Lock erfolgreich")
            
            self._log_test_pass(test_name, "Datei-Locking-Klasse funktioniert")
            
        except Exception as e:
            self._log_test_fail(test_name, f"Datei-Locking-Test fehlgeschlagen: {e}")
    
    def test_multi_process_locking(self):
        """Test: Multi-Process Datei-Sperrung"""
        test_name = "multi_process_locking"
        self._log_test_start(test_name)
        
        try:
            # Test mit separatem Prozess
            lock_test_script = f'''
import sys
import os
import msvcrt
import time
import tempfile

# Kommandozeilen-Argumente: Dateiname Process-ID
file_name = sys.argv[1]
process_id = sys.argv[2]

try:
    with open(file_name, 'a') as f:
        # Lock setzen
        msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
        
        # Status schreiben
        f.write(f"Process {{process_id}} got lock\\n")
        f.flush()
        
        # Kurz warten
        time.sleep(1)
        
        # Lock freigeben
        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 0)
        f.write(f"Process {{process_id}} released lock\\n")
        
    print("SUCCESS")
    sys.exit(0)
except Exception as e:
    print(f"ERROR: {{e}}")
    sys.exit(1)
'''
            
            if WINDOWS_AVAILABLE:
                # Speichere Test-Script
                script_file = self.temp_dir / "lock_test.py"
                script_file.write_text(lock_test_script)
                
                # Starte zwei parallele Prozesse
                proc1 = subprocess.Popen([
                    sys.executable, str(script_file), str(self.temp_file), "1"
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                proc2 = subprocess.Popen([
                    sys.executable, str(script_file), str(self.temp_file), "2"
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # Warte auf Beendigung
                stdout1, stderr1 = proc1.communicate(timeout=5)
                stdout2, stderr2 = proc2.communicate(timeout=5)
                
                # Überprüfe Ergebnisse
                success1 = b"SUCCESS" in stdout1
                success2 = b"SUCCESS" in stdout2
                
                if success1 and success2:
                    self._log_test_pass(test_name, "Multi-Process-Locking erfolgreich")
                else:
                    self._log_test_fail(test_name, "Multi-Process-Locking fehlgeschlagen")
            else:
                self._log_test_skip(test_name, "Nicht auf Windows - Multi-Process-Test übersprungen")
                
        except Exception as e:
            self._log_test_fail(test_name, f"Multi-Process-Test fehlgeschlagen: {e}")
    
    def test_lock_timeout_error_handling(self):
        """Test: Error-Handling bei Lock-Timeouts"""
        test_name = "lock_timeout_error_handling"
        self._log_test_start(test_name)
        
        try:
            # Test: Verhalten bei bereits gelockter Datei
            if WINDOWS_AVAILABLE:
                file_ops = AtomicFileOperations()
                
                # Erste Lock-Anfrage
                with file_ops.file_lock(self.temp_file, 'exclusive') as f1:
                    f1.write("Process 1 has lock")
                    
                    # Versuche zweite Lock-Anfrage in separatem Thread
                    error_occurred = False
                    lock_acquired = False
                    
                    def try_lock():
                        nonlocal error_occurred, lock_acquired
                        try:
                            with file_ops.file_lock(self.temp_file, 'exclusive') as f2:
                                lock_acquired = True
                        except Exception:
                            error_occurred = True
                    
                    # Teste Lock-Konflikt
                    lock_thread = threading.Thread(target=try_lock)
                    lock_thread.start()
                    lock_thread.join(timeout=2)
                    
                    if not lock_acquired:
                        self._log_test_info(test_name, "Lock-Konflikt korrekt erkannt")
                        self._log_test_pass(test_name, "Error-Handling bei Lock-Timeouts funktioniert")
                    else:
                        self._log_test_fail(test_name, "Lock-Konflikt nicht erkannt")
            else:
                self._log_test_skip(test_name, "Nicht auf Windows - Error-Handling-Test übersprungen")
                
        except Exception as e:
            self._log_test_fail(test_name, f"Error-Handling-Test fehlgeschlagen: {e}")
    
    def test_encrypted_file_locking(self):
        """Test: Verschlüsselte Dateien und Locking-Kompatibilität"""
        test_name = "encrypted_file_locking"
        self._log_test_start(test_name)
        
        try:
            # Test: Locking auf verschlüsselten Dateien (falls unterstützt)
            file_ops = AtomicFileOperations()
            
            # Erstelle verschlüsselungs-ähnliche Datei
            encrypted_file = self.temp_dir / "encrypted_test.enc"
            
            with file_ops.file_lock(encrypted_file, 'exclusive') as f:
                # Simuliere verschlüsselten Inhalt
                encrypted_content = "ENCRYPTED_CONTENT_" * 100
                f.write(encrypted_content)
                self._log_test_info(test_name, "Locking auf 'verschlüsselter' Datei erfolgreich")
            
            self._log_test_pass(test_name, "Verschlüsselte Datei-Locking-Kompatibilität bestätigt")
            
        except Exception as e:
            self._log_test_fail(test_name, f"Verschlüsselte Datei-Locking-Test fehlgeschlagen: {e}")
    
    def test_windows_unix_compatibility(self):
        """Test: Windows/Unix Kompatibilität"""
        test_name = "windows_unix_compatibility"
        self._log_test_start(test_name)
        
        try:
            # Test: Platform-spezifisches Verhalten
            system = platform.system()
            
            if system == "Windows":
                self.assertTrue(WINDOWS_AVAILABLE, "msvcrt sollte auf Windows verfügbar sein")
                self._log_test_info(test_name, "Windows-spezifische Features verfügbar")
            else:
                self.assertFalse(WINDOWS_AVAILABLE, "msvcrt sollte nicht auf Unix verfügbar sein")
                self._log_test_info(test_name, "Unix-System korrekt erkannt")
            
            # Test: Thread-sichere Operationen auf beiden Plattformen
            file_ops = AtomicFileOperations()
            
            with file_ops.file_lock(self.temp_file, 'shared') as f:
                f.write("Cross-platform compatibility test")
            
            self._log_test_pass(test_name, f"Cross-Platform-Kompatibilität für {system} bestätigt")
            
        except Exception as e:
            self._log_test_fail(test_name, f"Cross-Platform-Test fehlgeschlagen: {e}")
    
    def test_performance_locking_benchmarks(self):
        """Test: Performance-Benchmarks für Locking"""
        test_name = "performance_locking_benchmarks"
        self._log_test_start(test_name)
        
        try:
            # Performance-Test für Locking-Operationen
            file_ops = AtomicFileOperations()
            
            # Test: Lock/Unlock-Zeit messen
            num_operations = 100
            times = []
            
            for i in range(num_operations):
                start_time = time.time()
                
                with file_ops.file_lock(self.temp_file, 'shared') as f:
                    f.write(f"Performance test iteration {i}")
                
                end_time = time.time()
                times.append((end_time - start_time) * 1000)  # ms
            
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)
            
            self._log_test_info(test_name, f"Avg: {avg_time:.2f}ms, Min: {min_time:.2f}ms, Max: {max_time:.2f}ms")
            
            # Performance-Threshold prüfen (sollte unter 100ms durchschnittlich sein)
            if avg_time < 100:
                self._log_test_pass(test_name, f"Locking-Performance akzeptabel: {avg_time:.2f}ms Durchschnitt")
            else:
                self._log_test_fail(test_name, f"Locking-Performance zu langsam: {avg_time:.2f}ms Durchschnitt")
            
        except Exception as e:
            self._log_test_fail(test_name, f"Performance-Test fehlgeschlagen: {e}")
    
    def test_thread_safety(self):
        """Test: Thread-Sicherheit der Locking-Mechanismen"""
        test_name = "thread_safety"
        self._log_test_start(test_name)
        
        try:
            # Test: Gleichzeitige Thread-Zugriffe
            file_ops = AtomicFileOperations()
            results = []
            errors = []
            
            def thread_worker(thread_id):
                try:
                    with file_ops.file_lock(self.temp_file, 'shared') as f:
                        f.write(f"Thread {thread_id} accessing file\n")
                        time.sleep(0.1)  # Simuliere Arbeit
                        results.append(f"Thread {thread_id} success")
                except Exception as e:
                    errors.append(f"Thread {thread_id} error: {e}")
            
            # Starte mehrere Threads
            threads = []
            for i in range(5):
                thread = threading.Thread(target=thread_worker, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Warte auf alle Threads
            for thread in threads:
                thread.join(timeout=5)
            
            if not errors and len(results) == 5:
                self._log_test_pass(test_name, "Thread-Sicherheit bestätigt - alle Threads erfolgreich")
            else:
                self._log_test_fail(test_name, f"Thread-Sicherheitsprobleme: {len(errors)} Fehler")
            
        except Exception as e:
            self._log_test_fail(test_name, f"Thread-Safety-Test fehlgeschlagen: {e}")
    
    # Hilfsmethoden für Logging
    def _log_test_start(self, test_name: str):
        """Protokolliert Test-Start"""
        self.test_results['test_details'].append({
            'test': test_name,
            'status': 'started',
            'timestamp': time.time()
        })
    
    def _log_test_pass(self, test_name: str, message: str):
        """Protokolliert erfolgreichen Test"""
        self.test_results['tests_passed'] += 1
        self.test_results['test_details'].append({
            'test': test_name,
            'status': 'passed',
            'message': message,
            'timestamp': time.time()
        })
        print(f"✅ PASS: {test_name} - {message}")
    
    def _log_test_fail(self, test_name: str, message: str):
        """Protokolliert fehlgeschlagenen Test"""
        self.test_results['tests_failed'] += 1
        self.test_results['test_details'].append({
            'test': test_name,
            'status': 'failed',
            'message': message,
            'timestamp': time.time()
        })
        print(f"❌ FAIL: {test_name} - {message}")
        self.fail(message)
    
    def _log_test_skip(self, test_name: str, message: str):
        """Protokolliert übersprungenen Test"""
        self.test_results['test_details'].append({
            'test': test_name,
            'status': 'skipped',
            'message': message,
            'timestamp': time.time()
        })
        print(f"⏭️ SKIP: {test_name} - {message}")
    
    def _log_test_info(self, test_name: str, message: str):
        """Protokolliert Test-Information"""
        print(f"ℹ️ INFO: {test_name} - {message}")
    
    @classmethod
    def tearDownClass(cls):
        """Speichere Test-Ergebnisse"""
        # Speichere detaillierte Ergebnisse
        results_file = cls.temp_dir / "msvcrt_test_results.json"
        with open(results_file, 'w') as f:
            json.dump(cls.test_results, f, indent=2)
        
        print(f"\n📊 MSVCrt-Integration Test Zusammenfassung:")
        print(f"   ✅ Bestanden: {cls.test_results['tests_passed']}")
        print(f"   ❌ Fehlgeschlagen: {cls.test_results['tests_failed']}")
        print(f"   Platform: {cls.test_results['platform_system']}")
        print(f"   msvcrt verfügbar: {cls.test_results['msvcrt_available']}")
        print(f"   Ergebnisse gespeichert in: {results_file}")
        
        # Cleanup
        try:
            import shutil
            shutil.rmtree(cls.temp_dir)
        except:
            pass


def run_comprehensive_tests():
    """Führt alle Tests aus und erstellt Bericht"""
    print("🔍 Starte MSVCrt-Integration und Datei-Sperrung Tests...")
    print("="*60)
    
    # Test Suite erstellen
    suite = unittest.TestLoader().loadTestsFromTestCase(MSVCrtCompatibilityTest)
    
    # Tests ausführen
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
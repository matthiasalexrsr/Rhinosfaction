#!/usr/bin/env python3
"""
Rate Limiting und Performance-basierte Sicherheitstests
"""

import os
import sys
import time
import threading
from pathlib import Path
import tempfile
import shutil

# Pfad zur Anwendung hinzufügen
sys.path.insert(0, '/workspace/rhinoplastik_app')

from core.security.auth import AuthenticationManager


def test_rate_limiting():
    """Test Rate Limiting bei Login-Versuchen"""
    print("\n⏱️  Teste Rate Limiting...")
    
    test_dir = Path(tempfile.mkdtemp())
    test_users_file = test_dir / "test_users.json"
    
    try:
        auth_manager = AuthenticationManager(test_users_file)
        
        # Schnelle aufeinanderfolgende Login-Versuche
        print("  🔄 Führe 20 schnelle Login-Versuche durch...")
        start_time = time.time()
        
        results = []
        for i in range(20):
            attempt_start = time.time()
            result = auth_manager.authenticate('admin', f'wrongpass{i}')
            attempt_end = time.time()
            
            results.append({
                'attempt': i + 1,
                'result': result,
                'duration': attempt_end - attempt_start
            })
            
            # Sehr kurze Pause zwischen Versuchen
            time.sleep(0.01)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Ergebnisse analysieren
        successful_attempts = sum(1 for r in results if r['result'] is not None)
        avg_duration = sum(r['duration'] for r in results) / len(results)
        
        print(f"  📊 Gesamtzeit: {total_time:.2f}s")
        print(f"  📊 Durchschnittliche Versuchsdauer: {avg_duration:.4f}s")
        print(f"  📊 Erfolgreiche Versuche: {successful_attempts}")
        
        # Prüfe auf Rate Limiting
        if avg_duration < 0.1 and successful_attempts > 5:
            print(f"  ⚠️  VULNERABILITÄT: Kein Rate Limiting - zu schnelle Versuche")
            return True
        else:
            print(f"  ✅ Rate Limiting scheint aktiv")
            return False
            
    except Exception as e:
        print(f"  ❌ Fehler: {e}")
        return False
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_concurrent_login_attacks():
    """Test gleichzeitige Login-Angriffe"""
    print("\n⚡ Teste Concurrent Login-Angriffe...")
    
    test_dir = Path(tempfile.mkdtemp())
    test_users_file = test_dir / "test_users.json"
    
    try:
        auth_manager = AuthenticationManager(test_users_file)
        
        results = []
        lock = threading.Lock()
        
        def login_attack(thread_id):
            """Simuliert Login-Angriff in Thread"""
            thread_results = []
            for i in range(5):
                start = time.time()
                result = auth_manager.authenticate('admin', f'password{i}')
                end = time.time()
                
                with lock:
                    thread_results.append({
                        'thread': thread_id,
                        'attempt': i,
                        'success': result is not None,
                        'duration': end - start
                    })
                
                time.sleep(0.05)  # Kurze Pause
            
            with lock:
                results.extend(thread_results)
        
        # 5 parallele Threads starten
        threads = []
        for i in range(5):
            t = threading.Thread(target=login_attack, args=(i,))
            threads.append(t)
            t.start()
        
        # Auf alle Threads warten
        for t in threads:
            t.join()
        
        # Ergebnisse analysieren
        total_attempts = len(results)
        successful_attempts = sum(1 for r in results if r['success'])
        avg_duration = sum(r['duration'] for r in results) / total_attempts
        
        print(f"  📊 Gesamtversuche: {total_attempts}")
        print(f"  📊 Erfolgreiche Versuche: {successful_attempts}")
        print(f"  📊 Durchschnittsdauer: {avg_duration:.4f}s")
        
        # Prüfe Thread-Safety
        admin_user = None
        for user in auth_manager.users.values():
            if user.username == 'admin':
                admin_user = user
                break
        
        if admin_user and admin_user.failed_attempts < total_attempts:
            print(f"  ⚠️  VULNERABILITÄT: Thread-Safety Problem erkannt")
            print(f"     Erwartete fehlgeschlagene Versuche: {total_attempts}")
            print(f"     Tatsächliche fehlgeschlagene Versuche: {admin_user.failed_attempts}")
            return True
        else:
            print(f"  ✅ Thread-Safety scheint gewährleistet")
            return False
            
    except Exception as e:
        print(f"  ❌ Fehler: {e}")
        return False
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_memory_timing_attacks():
    """Test Memory-Timing-basierte Angriffe"""
    print("\n🧠 Teste Memory-Timing Angriffe...")
    
    test_dir = Path(tempfile.mkdtemp())
    test_users_file = test_dir / "test_users.json"
    
    try:
        auth_manager = AuthenticationManager(test_users_file)
        
        # Teste Timing-Unterschiede zwischen existierenden und nicht-existierenden Usern
        existing_user_times = []
        nonexistent_user_times = []
        
        # 50 Messungen für existierenden User
        for i in range(50):
            start = time.time()
            auth_manager.authenticate('admin', 'wrongpassword')
            end = time.time()
            existing_user_times.append(end - start)
        
        # 50 Messungen für nicht-existierenden User
        for i in range(50):
            start = time.time()
            auth_manager.authenticate(f'nonexistent{i}', 'anypassword')
            end = time.time()
            nonexistent_user_times.append(end - start)
        
        # Statistiken berechnen
        import statistics
        
        existing_avg = statistics.mean(existing_user_times)
        nonexistent_avg = statistics.mean(nonexistent_user_times)
        existing_stdev = statistics.stdev(existing_user_times)
        nonexistent_stdev = statistics.stdev(nonexistent_user_times)
        
        print(f"  📊 Existierender User - Durchschnitt: {existing_avg:.6f}s, StdDev: {existing_stdev:.6f}s")
        print(f"  📊 Nicht-existierender User - Durchschnitt: {nonexistent_avg:.6f}s, StdDev: {nonexistent_stdev:.6f}s")
        
        # Timing-Unterschied prüfen
        time_diff = abs(existing_avg - nonexistent_avg)
        if time_diff > 0.001:  # 1ms Unterschied
            print(f"  ⚠️  VULNERABILITÄT: Signifikanter Timing-Unterschied erkannt")
            print(f"     Differenz: {time_diff:.6f}s (könnte für User Enumeration genutzt werden)")
            return True
        else:
            print(f"  ✅ Timing-Unterschiede vernachlässigbar")
            return False
            
    except Exception as e:
        print(f"  ❌ Fehler: {e}")
        return False
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def main():
    """Hauptfunktion für Performance-basierte Sicherheitstests"""
    print("⚡ PERFORMANCE-BASIERTE SICHERHEITSTESTS")
    print("=" * 60)
    
    tests = [
        ("Rate Limiting", test_rate_limiting),
        ("Concurrent Attacks", test_concurrent_login_attacks),
        ("Memory Timing", test_memory_timing_attacks)
    ]
    
    vulnerabilities = []
    
    for test_name, test_func in tests:
        try:
            is_vulnerable = test_func()
            if is_vulnerable:
                vulnerabilities.append(test_name)
        except Exception as e:
            print(f"  ❌ Test {test_name} fehlgeschlagen: {e}")
    
    print("\n" + "=" * 60)
    print("📊 PERFORMANCE-TEST ZUSAMMENFASSUNG")
    print("=" * 60)
    
    if vulnerabilities:
        print(f"❌ GEFUNDENE PERFORMANCE-VULNERABILITÄTEN ({len(vulnerabilities)}):")
        for vuln in vulnerabilities:
            print(f"  • {vuln}")
    else:
        print("✅ Keine kritischen Performance-Vulnerabilities gefunden")
    
    return len(vulnerabilities)


if __name__ == '__main__':
    main()
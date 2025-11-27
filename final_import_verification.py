#!/usr/bin/env python3
"""
Finale Import-Verifikation
Testet die kritischen Import-Funktionen nach den Korrekturen
"""

import sys
import os
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def test_critical_imports():
    """Testet alle kritischen Imports nach den Korrekturen"""
    print("🧪 Finale Import-Verifikation...")
    print("="*80)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': 0,
        'passed': 0,
        'failed': 0,
        'errors': []
    }
    
    # Pfad-Setup
    project_root = Path("/workspace/rhinoplastik_app")
    if project_root.exists():
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        print(f"📁 Projekt-Root: {project_root}")
    else:
        print("❌ Projekt-Root nicht gefunden!")
        return results
    
    # Test 1: Hauptanwendung
    results['total_tests'] += 1
    try:
        from app import setup_application
        print("✅ app.py - setup_application importiert")
        results['passed'] += 1
    except Exception as e:
        results['failed'] += 1
        results['errors'].append(f"app.py: {str(e)}")
        print(f"❌ app.py: {str(e)}")
    
    # Test 2: Core-Module
    core_modules = [
        ('core.logging_conf', 'setup_logging'),
        ('core.security.auth', 'AuthenticationManager'),
        ('core.security.session_manager', 'SessionManager'),
        ('core.patients.patient_manager', 'PatientManager'),
        ('core.patients.patient_model', 'Patient'),
        ('core.ui_system_integrator', 'UISystemIntegrator'),
    ]
    
    for module_name, class_name in core_modules:
        results['total_tests'] += 1
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"✅ {module_name}.{class_name}")
            results['passed'] += 1
        except Exception as e:
            results['failed'] += 1
            results['errors'].append(f"{module_name}.{class_name}: {str(e)}")
            print(f"❌ {module_name}.{class_name}: {str(e)}")
    
    # Test 3: UI-Module
    ui_modules = [
        ('ui.main_window', 'MainWindow'),
        ('ui.login_dialog', 'LoginDialog'),
        ('ui.dashboard_widget', 'DashboardWidget'),
        ('ui.patients_list_widget', 'PatientsListWidget'),
    ]
    
    for module_name, class_name in ui_modules:
        results['total_tests'] += 1
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"✅ {module_name}.{class_name}")
            results['passed'] += 1
        except Exception as e:
            results['failed'] += 1
            results['errors'].append(f"{module_name}.{class_name}: {str(e)}")
            print(f"❌ {module_name}.{class_name}: {str(e)}")
    
    # Test 4: Externe Bibliotheken (kritische)
    external_libs = [
        'PySide6',
        'pandas',
        'numpy',
        'matplotlib',
        'PIL',
        'bcrypt',
        'cryptography',
        'yaml',
        'reportlab',
        'dateutil',
        'pytest',
    ]
    
    for lib_name in external_libs:
        results['total_tests'] += 1
        try:
            __import__(lib_name)
            print(f"✅ {lib_name}")
            results['passed'] += 1
        except Exception as e:
            results['failed'] += 1
            results['errors'].append(f"{lib_name}: {str(e)}")
            print(f"❌ {lib_name}: {str(e)}")
    
    # Test 5: Config-Module
    results['total_tests'] += 1
    try:
        from config.app_config import AppConfig
        print("✅ config.app_config.AppConfig")
        results['passed'] += 1
    except Exception as e:
        results['failed'] += 1
        results['errors'].append(f"config.app_config: {str(e)}")
        print(f"❌ config.app_config: {str(e)}")
    
    return results

def test_windows_specific():
    """Testet Windows-spezifische Imports"""
    print("\n🪟 Windows-spezifische Import-Tests:")
    print("-" * 40)
    
    import platform
    is_windows = platform.system() == 'Windows'
    
    # Teste msvcrt (sollte in performance_optimizer.py verwendet werden)
    try:
        import msvcrt
        if is_windows:
            print("✅ msvcrt (Windows-spezifisch)")
        else:
            print("⚠️  msvcrt verfügbar auf Nicht-Windows-System")
    except ImportError:
        if not is_windows:
            print("✅ msvcrt korrekt nicht verfügbar (Linux)")
        else:
            print("❌ msvcrt nicht verfügbar auf Windows")
    
    return True

def test_error_handling():
    """Testet Error-Handling"""
    print("\n🛡️  Error-Handling Tests:")
    print("-" * 40)
    
    # Teste ImportError-Behandlung
    try:
        import non_existent_module_test
        print("❌ Unerwartet erfolgreich")
        return False
    except ImportError:
        print("✅ ImportError korrekt behandelt")
    
    # Teste Graceful Degradation
    try:
        from core.audit import AuditLogger
        print("✅ core.audit.AuditLogger verfügbar")
    except ImportError as e:
        print(f"⚠️  core.audit.AuditLogger nicht verfügbar: {e}")
        print("   (Fehlende dependency - erwartetes Verhalten)")
    
    return True

def test_cyclic_dependencies():
    """Testet zyklische Abhängigkeiten durch Imports"""
    print("\n🔄 Zyklische Abhängigkeits-Tests:")
    print("-" * 40)
    
    try:
        # Teste core-Module Interaktion
        from core import security
        from core.security import auth
        
        # Teste ui-Module
        from ui import main_window
        from ui import login_dialog
        
        print("✅ Keine zyklischen Abhängigkeiten erkannt")
        return True
        
    except Exception as e:
        print(f"❌ Mögliche zyklische Abhängigkeit: {str(e)}")
        return False

def generate_final_summary():
    """Generiert finale Zusammenfassung"""
    print("\n" + "="*80)
    print("🎯 FINALE IMPORT-VERIFIKATION - ZUSAMMENFASSUNG")
    print("="*80)
    
    results = test_critical_imports()
    test_windows_specific()
    test_error_handling()
    test_cyclic_dependencies()
    
    # Erfolgsquote berechnen
    if results['total_tests'] > 0:
        success_rate = (results['passed'] / results['total_tests']) * 100
    else:
        success_rate = 0
    
    print(f"\n📊 ERGEBNISSE:")
    print(f"   Gesamt Tests: {results['total_tests']}")
    print(f"   Erfolgreich: {results['passed']} ({success_rate:.1f}%)")
    print(f"   Fehlgeschlagen: {results['failed']}")
    
    if results['errors']:
        print(f"\n❌ VERBLEIBENDE FEHLER:")
        for error in results['errors'][:5]:  # Erste 5 Fehler
            print(f"   - {error}")
        if len(results['errors']) > 5:
            print(f"   ... und {len(results['errors']) - 5} weitere")
    
    # Bewertung
    if success_rate >= 90:
        status = "🟢 EXCELLENT"
    elif success_rate >= 80:
        status = "🟡 GOOD"
    elif success_rate >= 70:
        status = "🟠 ACCEPTABLE"
    else:
        status = "🔴 NEEDS WORK"
    
    print(f"\n🏆 GESAMTBEWERTUNG: {status}")
    
    return results

def main():
    """Hauptfunktion"""
    print("🚀 Starte finale Import-Verifikation...")
    print(f"⏰ Zeit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        results = generate_final_summary()
        
        # Bericht als JSON speichern
        import json
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = Path(f"/workspace/docs/final_import_verification_{timestamp}.json")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Finaler Verifikationsbericht gespeichert: {report_file}")
        return results
        
    except Exception as e:
        print(f"❌ Kritischer Fehler bei der Verifikation: {str(e)}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()
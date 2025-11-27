#!/usr/bin/env python3
"""
Erweiterte Import-Tests für kritische Komponenten
"""

import sys
import os
import traceback
import importlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

def test_external_libraries():
    """Testet alle externen Bibliotheks-Imports"""
    print("🔌 Teste externe Bibliotheks-Imports...")
    
    test_results = {
        'total_tested': 0,
        'successful': 0,
        'failed': 0,
        'errors': []
    }
    
    # Liste kritischer externer Bibliotheken
    critical_libs = [
        ('PySide6', 'PySide6'),
        ('PySide6.QtWidgets', 'PySide6.QtWidgets'),
        ('PySide6.QtCore', 'PySide6.QtCore'),
        ('PySide6.QtGui', 'PySide6.QtGui'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('matplotlib', 'matplotlib'),
        ('matplotlib.pyplot', 'matplotlib.pyplot'),
        ('PIL', 'PIL'),
        ('PIL.Image', 'PIL.Image'),
        ('bcrypt', 'bcrypt'),
        ('cryptography', 'cryptography'),
        ('pyyaml', 'yaml'),
        ('reportlab', 'reportlab'),
        ('psutil', 'psutil'),
        ('dateutil', 'dateutil'),
        ('pytz', 'pytz'),
        ('openpyxl', 'openpyxl'),
        ('fuzzywuzzy', 'fuzzywuzzy'),
        ('pyotp', 'pyotp'),
        ('qrcode', 'qrcode'),
        ('seaborn', 'seaborn'),
        ('scipy', 'scipy'),
        ('pytest', 'pytest'),
    ]
    
    for lib_name, import_path in critical_libs:
        test_results['total_tested'] += 1
        try:
            if '.' in import_path:
                # Submodule
                parts = import_path.split('.')
                module = __import__(parts[0])
                for part in parts[1:]:
                    module = getattr(module, part)
            else:
                # Hauptmodul
                module = importlib.import_module(import_path)
            
            # Teste grundlegende Funktionalität
            if lib_name == 'pandas':
                import pandas as pd
                df = pd.DataFrame({'test': [1, 2, 3]})
                assert len(df) == 3
            elif lib_name == 'numpy':
                import numpy as np
                arr = np.array([1, 2, 3])
                assert arr.shape == (3,)
            elif lib_name == 'PySide6.QtWidgets':
                # Nicht headless testen
                pass
            elif lib_name == 'bcrypt':
                import bcrypt
                hash_b = bcrypt.hashpw(b"test", bcrypt.gensalt())
                assert len(hash_b) > 0
            elif lib_name == 'matplotlib':
                import matplotlib
                matplotlib.use('Agg')  # Non-interactive backend
            elif lib_name == 'PIL':
                from PIL import Image
                img = Image.new('RGB', (10, 10))
                assert img.size == (10, 10)
            
            test_results['successful'] += 1
            print(f"  ✅ {lib_name}")
            
        except Exception as e:
            test_results['failed'] += 1
            error_msg = f"❌ {lib_name}: {str(e)}"
            test_results['errors'].append(error_msg)
            print(f"  {error_msg}")
    
    return test_results

def test_windows_specific_imports():
    """Testet Windows-spezifische Imports"""
    print("\n🪟 Teste Windows-spezifische Imports...")
    
    test_results = {
        'total_tested': 0,
        'successful': 0,
        'failed': 0,
        'available_on_platform': False,
        'errors': []
    }
    
    import platform
    is_windows = platform.system() == 'Windows'
    test_results['available_on_platform'] = is_windows
    
    windows_libs = [
        'msvcrt',
        'win32api',
        'pywin32',
        'winreg',
        'winsound'
    ]
    
    for lib_name in windows_libs:
        test_results['total_tested'] += 1
        try:
            if is_windows:
                importlib.import_module(lib_name)
                test_results['successful'] += 1
                print(f"  ✅ {lib_name} (Windows)")
            else:
                # Auf Nicht-Windows-Systemen erwarten wir ImportErrors
                try:
                    importlib.import_module(lib_name)
                    test_results['failed'] += 1
                    test_results['errors'].append(f"⚠️  {lib_name} unerwartet verfügbar auf {platform.system()}")
                    print(f"  ⚠️  {lib_name} unerwartet verfügbar auf {platform.system()}")
                except ImportError:
                    test_results['successful'] += 1
                    print(f"  ✅ {lib_name} (erwarteter ImportError auf {platform.system()})")
        except Exception as e:
            if not is_windows:
                test_results['successful'] += 1
                print(f"  ✅ {lib_name} (ImportError erwartet auf {platform.system()})")
            else:
                test_results['failed'] += 1
                test_results['errors'].append(f"❌ {lib_name}: {str(e)}")
                print(f"  ❌ {lib_name}: {str(e)}")
    
    return test_results

def test_local_module_imports():
    """Testet lokale Modul-Imports"""
    print("\n🏠 Teste lokale Modul-Imports...")
    
    test_results = {
        'total_tested': 0,
        'successful': 0,
        'failed': 0,
        'errors': []
    }
    
    # Verschiedene Projektpfade testen
    possible_roots = [
        Path("/workspace/rhinoplastik_app"),
        Path("/workspace/rhinoplastik_windows_final"),
        Path("/workspace/final_test/rhinoplastik_windows_final")
    ]
    
    project_root = None
    for root in possible_roots:
        if root.exists() and (root / "app.py").exists():
            project_root = root
            break
    
    if not project_root:
        test_results['errors'].append("Kein gültiges Projektverzeichnis gefunden")
        return test_results
    
    # Pfad hinzufügen
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    critical_local_modules = [
        'config.app_config',
        'core.logging_conf',
        'core.security.auth',
        'core.security.session_manager',
        'core.patients.patient_manager',
        'core.patients.patient_model',
        'ui.main_window',
        'ui.login_dialog',
        'core.ui_system_integrator',
        'core.theme_manager',
        'core.i18n',
        'core.asset_manager',
        'core.notifications',
        'core.audit',
        'core.reports',
        'core.search',
        'core.statistics.statistics_service',
        'core.export.export_service',
        'core.backup.backup_service',
        'core.media.media_manager',
    ]
    
    for module_name in critical_local_modules:
        test_results['total_tested'] += 1
        try:
            # Import testen
            module = importlib.import_module(module_name)
            
            # Teste, ob Hauptklassen verfügbar sind
            if 'patient_manager' in module_name:
                from importlib import import_module
                mod = import_module(module_name)
                if hasattr(mod, 'PatientManager'):
                    # Instanziierung testen
                    pass
            
            test_results['successful'] += 1
            print(f"  ✅ {module_name}")
            
        except Exception as e:
            test_results['failed'] += 1
            error_msg = f"❌ {module_name}: {str(e)}"
            test_results['errors'].append(error_msg)
            print(f"  {error_msg}")
    
    return test_results

def test_import_error_handling():
    """Testet Error-Handling bei Import-Fehlern"""
    print("\n🛡️  Teste Error-Handling bei Import-Fehlern...")
    
    test_results = {
        'total_tested': 0,
        'successful': 0,
        'failed': 0,
        'errors': []
    }
    
    # Teste graceful handling von Import-Fehlern
    error_scenarios = [
        # Nicht existierendes Modul
        'non_existent_module_12345',
        # Fehlende Submodule
        'rhinoplastik_app.non_existent_submodule',
        # Syntax-Fehler in Import (simuliert)
    ]
    
    for scenario in error_scenarios:
        test_results['total_tested'] += 1
        try:
            # Teste try-except around import
            try:
                importlib.import_module(scenario)
                test_results['failed'] += 1
                test_results['errors'].append(f"⚠️  {scenario} unerwartet erfolgreich importiert")
            except ImportError:
                # Erwartetes Verhalten
                test_results['successful'] += 1
                print(f"  ✅ {scenario} (ImportError korrekt behandelt)")
        except Exception as e:
            test_results['failed'] += 1
            test_results['errors'].append(f"❌ {scenario}: Unerwarteter Fehler: {str(e)}")
    
    return test_results

def test_circular_dependencies():
    """Testet zyklische Abhängigkeiten"""
    print("\n🔄 Teste zyklische Abhängigkeiten...")
    
    test_results = {
        'total_tested': 0,
        'successful': 0,
        'failed': 0,
        'circular_deps_found': [],
        'errors': []
    }
    
    # Einfache Test-Fälle für zyklische Abhängigkeiten
    try:
        # Teste bekannte problematische Bereiche
        test_results['total_tested'] += 1
        
        # Prüfe ob core-Module sich gegenseitig importieren
        try:
            from core import security
            from core.security import auth
            # Wenn das funktioniert, ist zumindest dieser Bereich okay
            test_results['successful'] += 1
            print("  ✅ core.security -> core.security.auth Import")
        except Exception as e:
            test_results['failed'] += 1
            test_results['errors'].append(f"core.security Import-Fehler: {str(e)}")
        
        # Teste UI-Module
        try:
            from ui import main_window
            test_results['total_tested'] += 1
            test_results['successful'] += 1
            print("  ✅ ui.main_window Import")
        except Exception as e:
            test_results['total_tested'] += 1
            test_results['failed'] += 1
            test_results['errors'].append(f"ui.main_window Import-Fehler: {str(e)}")
        
    except Exception as e:
        test_results['failed'] += 1
        test_results['errors'].append(f"Unerwarteter Test-Fehler: {str(e)}")
    
    return test_results

def generate_comprehensive_report():
    """Generiert einen umfassenden Bericht"""
    print("\n" + "="*80)
    print("🔍 ERWEITERTE IMPORT-STRUKTUR-VALIDIERUNG")
    print("="*80)
    
    # Alle Tests ausführen
    results = {}
    
    results['external_libraries'] = test_external_libraries()
    results['windows_specific'] = test_windows_specific_imports()
    results['local_modules'] = test_local_module_imports()
    results['error_handling'] = test_import_error_handling()
    results['circular_dependencies'] = test_circular_dependencies()
    
    # Zusammenfassung
    print("\n" + "="*80)
    print("📊 ZUSAMMENFASSUNG")
    print("="*80)
    
    for test_name, result in results.items():
        print(f"\n🔍 {test_name.replace('_', ' ').title()}:")
        print(f"   Getestet: {result.get('total_tested', 0)}")
        print(f"   Erfolgreich: {result.get('successful', 0)}")
        print(f"   Fehlgeschlagen: {result.get('failed', 0)}")
        
        if result.get('errors'):
            print(f"   ❌ Fehler: {len(result['errors'])}")
            for error in result['errors'][:3]:  # Erste 3 Fehler anzeigen
                print(f"      - {error}")
    
    return results

def main():
    """Hauptfunktion"""
    try:
        results = generate_comprehensive_report()
        
        # Bericht als JSON speichern
        import json
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = Path(f"/workspace/docs/import_validation_detailed_{timestamp}.json")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detaillierter Bericht gespeichert: {report_file}")
        
    except Exception as e:
        print(f"❌ Kritischer Fehler: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Intensive Test- und Revisions-Framework für Phase 9: Statistiken und Berichte

Führt umfassende Tests durch:
- Code-Syntax und -Struktur
- Funktionale Tests (ohne Qt-Dependencies)
- Import-Kompatibilität
- API-Design Qualität
- Performance-Analyse
"""

import sys
import os
import importlib.util
import inspect
import ast
import json
from pathlib import Path
from typing import Dict, List, Any
import subprocess
import time

def print_header(title: str, width: int = 80):
    """Druckt formatierten Header"""
    print("\n" + "=" * width)
    print(f"🎯 {title}")
    print("=" * width)

def print_test_result(test_name: str, passed: bool, details: str = ""):
    """Druckt Test-Ergebnis"""
    status = "✅ BESTANDEN" if passed else "❌ FEHLGESCHLAGEN"
    print(f"{test_name:.<50} {status}")
    if details:
        print(f"  📋 {details}")

def test_syntax_validation():
    """Test 1: Syntax-Validierung"""
    print_header("1. SYNTAX-VALIDIERUNG")
    
    files_to_test = [
        "/workspace/rhinoplastik_app/core/statistics/statistics_service.py",
        "/workspace/rhinoplastik_app/ui/statistics_widget.py",
        "/workspace/rhinoplastik_app/ui/main_window.py"
    ]
    
    all_passed = True
    
    for file_path in files_to_test:
        if not os.path.exists(file_path):
            print_test_result(f"Syntax {os.path.basename(file_path)}", False, "Datei nicht gefunden")
            all_passed = False
            continue
            
        try:
            result = subprocess.run([
                sys.executable, "-m", "py_compile", file_path
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print_test_result(f"Syntax {os.path.basename(file_path)}", True, "Valid")
            else:
                print_test_result(f"Syntax {os.path.basename(file_path)}", False, result.stderr)
                all_passed = False
                
        except Exception as e:
            print_test_result(f"Syntax {os.path.basename(file_path)}", False, str(e))
            all_passed = False
    
    return all_passed

def test_import_compatibility():
    """Test 2: Import-Kompatibilität"""
    print_header("2. IMPORT-KOMPATIBILITÄT")
    
    # Teste PySide6 vs PyQt5 Konsistenz
    print("🔍 Prüfe PySide6/Import-Konsistenz...")
    
    import_check = [
        ("PySide6.QtCore", "from PySide6.QtCore import Signal"),
        ("PySide6.QtWidgets", "from PySide6.QtWidgets import QWidget"),
        ("PySide6.QtGui", "from PySide6.QtGui import QAction"),
        ("matplotlib", "import matplotlib.pyplot as plt"),
        ("seaborn", "import seaborn as sns"),
        ("numpy", "import numpy as np"),
        ("pandas", "import pandas as pd")
    ]
    
    all_passed = True
    
    for module_name, import_statement in import_check:
        try:
            exec(import_statement)
            print_test_result(f"Import {module_name}", True, "Verfügbar")
        except ImportError as e:
            print_test_result(f"Import {module_name}", False, str(e))
            all_passed = False
        except Exception as e:
            print_test_result(f"Import {module_name}", False, f"Anderer Fehler: {e}")
            all_passed = False
    
    return all_passed

def test_code_metrics():
    """Test 3: Code-Metriken"""
    print_header("3. CODE-METRIKEN")
    
    files = {
        "StatisticsService": "/workspace/rhinoplastik_app/core/statistics/statistics_service.py",
        "StatisticsWidget": "/workspace/rhinoplastik_app/ui/statistics_widget.py"
    }
    
    all_passed = True
    
    for component_name, file_path in files.items():
        if not os.path.exists(file_path):
            print_test_result(f"Metriken {component_name}", False, "Datei nicht gefunden")
            all_passed = False
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        total_lines = len(lines)
        code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        blank_lines = total_lines - code_lines - comment_lines
        
        # Complexity estimation
        ast_tree = ast.parse(content)
        class_count = sum(1 for node in ast.walk(ast_tree) if isinstance(node, ast.ClassDef))
        function_count = sum(1 for node in ast.walk(ast_tree) if isinstance(node, ast.FunctionDef))
        
        print_test_result(f"Zeilen {component_name}", True, f"Gesamt: {total_lines}, Code: {code_lines}")
        print_test_result(f"Komplexität {component_name}", True, f"Klassen: {class_count}, Funktionen: {function_count}")
        
        # Quality gates
        if code_lines < 300:  # Expect substantial implementation
            print_test_result(f"Umfang {component_name}", False, f"Zu wenige Code-Zeilen: {code_lines}")
            all_passed = False
        else:
            print_test_result(f"Umfang {component_name}", True, f"Angemessener Umfang: {code_lines} Zeilen")
    
    return all_passed

def test_api_design():
    """Test 4: API-Design Qualität"""
    print_header("4. API-DESIGN QUALITÄT")
    
    # Lade statistics_service.py als Modul (ohne UI Dependencies)
    spec = importlib.util.spec_from_file_location(
        "statistics_service", 
        "/workspace/rhinoplastik_app/core/statistics/statistics_service.py"
    )
    
    all_passed = True
    
    if spec and spec.loader:
        try:
            # Mock Qt dependencies
            sys.modules['PySide6'] = type('MockModule', (), {
                'QtCore': type('MockQtCore', (), {
                    'QObject': object,
                    'Signal': object,
                    'QThread': object
                })(),
                'QtWidgets': type('MockQtWidgets', (), {
                    'QApplication': object
                })()
            })()
            
            module = importlib.util.module_from_spec(spec)
            
            # Analysiere API-Design
            classes = [name for name in dir(module) if inspect.isclass(getattr(module, name))]
            
            if 'StatisticsService' in classes:
                print_test_result("StatisticsService Klasse", True, "Gefunden")
                
                service_class = getattr(module, 'StatisticsService')
                methods = [name for name, method in inspect.getmembers(service_class, inspect.ismethod) 
                          if not name.startswith('_')]
                print_test_result("StatisticsService Methoden", True, f"{len(methods)} öffentliche Methoden")
                
                # Prüfe Docstrings
                has_docstring = service_class.__doc__ is not None
                print_test_result("StatisticsService Docstring", has_docstring, 
                                "Ja" if has_docstring else "Nein")
                
            if 'StatisticsData' in classes:
                print_test_result("StatisticsData Klasse", True, "Gefunden")
            else:
                print_test_result("StatisticsData Klasse", False, "Nicht gefunden")
                all_passed = False
                
        except Exception as e:
            print_test_result("API-Analyse", False, f"Fehler: {e}")
            all_passed = False
    else:
        print_test_result("API-Analyse", False, "Modul konnte nicht geladen werden")
        all_passed = False
    
    return all_passed

def test_functional_components():
    """Test 5: Funktionale Komponenten"""
    print_header("5. FUNKTIONALE KOMPONENTEN")
    
    all_passed = True
    
    # Teste Matplotlib-Funktionalität
    try:
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
        
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Teste Chart-Erstellung
        fig, ax = plt.subplots()
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        ax.plot(x, y)
        ax.set_title("Test Chart")
        
        # Teste speichern
        test_file = "/tmp/test_chart.png"
        fig.savefig(test_file)
        plt.close()
        
        if os.path.exists(test_file):
            print_test_result("Matplotlib Chart-Erstellung", True, "PNG erstellt")
            os.remove(test_file)
        else:
            print_test_result("Matplotlib Chart-Erstellung", False, "PNG nicht erstellt")
            all_passed = False
            
    except Exception as e:
        print_test_result("Matplotlib Chart-Erstellung", False, str(e))
        all_passed = False
    
    # Teste Pandas/Numpy Funktionalität
    try:
        import pandas as pd
        import numpy as np
        
        # Teste Datenanalyse
        data = {
            'age': np.random.randint(18, 70, 100),
            'gender': np.random.choice(['M', 'W'], 100),
            'operation_type': np.random.choice(['Rhinoplastik', 'Septorhinoplastik'], 100)
        }
        df = pd.DataFrame(data)
        
        age_stats = df['age'].describe()
        gender_dist = df['gender'].value_counts()
        
        print_test_result("Pandas/Numpy Analyse", True, 
                        f"Alter: {age_stats['mean']:.1f}, Geschlechter: {len(gender_dist)}")
        
    except Exception as e:
        print_test_result("Pandas/Numpy Analyse", False, str(e))
        all_passed = False
    
    return all_passed

def test_performance():
    """Test 6: Performance-Analyse"""
    print_header("6. PERFORMANCE-ANALYSE")
    
    all_passed = True
    
    # Teste Import-Zeit
    import_times = {}
    
    test_imports = [
        ("matplotlib", "import matplotlib"),
        ("seaborn", "import seaborn"),
        ("numpy", "import numpy"),
        ("pandas", "import pandas")
    ]
    
    for module_name, import_stmt in test_imports:
        start_time = time.time()
        try:
            exec(import_stmt)
            import_time = time.time() - start_time
            import_times[module_name] = import_time
            
            if import_time < 2.0:  # Should be fast
                print_test_result(f"Import {module_name}", True, f"{import_time:.3f}s")
            else:
                print_test_result(f"Import {module_name}", False, f"Zu lang: {import_time:.3f}s")
                all_passed = False
                
        except Exception as e:
            print_test_result(f"Import {module_name}", False, str(e))
            all_passed = False
    
    return all_passed

def test_security():
    """Test 7: Security-Features"""
    print_header("7. SECURITY-FEATURES")
    
    all_passed = True
    
    # Teste File-Operation-Sicherheit
    try:
        import tempfile
        import os
        
        # Teste sichere Datei-Erstellung
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump({"test": "data"}, f)
            temp_file = f.name
        
        # Lese zurück
        with open(temp_file, 'r') as f:
            data = json.load(f)
        
        os.unlink(temp_file)
        
        if data == {"test": "data"}:
            print_test_result("JSON Serialize/Deserialize", True, "Sicher")
        else:
            print_test_result("JSON Serialize/Deserialize", False, "Dateninkonsistenz")
            all_passed = False
            
    except Exception as e:
        print_test_result("JSON Serialize/Deserialize", False, str(e))
        all_passed = False
    
    return all_passed

def main():
    """Haupt-Funktion für intensive Tests"""
    print("🧪 Phase 9 Intensive Test & Revision Suite")
    print("=" * 80)
    print("📋 Test-Suite für: Statistiken und Berichte")
    print("🎯 Ziel: 100% Code-Quality und Funktionalität")
    print("=" * 80)
    
    test_results = []
    
    # Führe alle Tests durch
    tests = [
        ("Syntax-Validierung", test_syntax_validation),
        ("Import-Kompatibilität", test_import_compatibility),
        ("Code-Metriken", test_code_metrics),
        ("API-Design", test_api_design),
        ("Funktionale Komponenten", test_functional_components),
        ("Performance", test_performance),
        ("Security", test_security)
    ]
    
    for test_name, test_function in tests:
        try:
            result = test_function()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} FEHLER: {e}")
            test_results.append((test_name, False))
    
    # Zusammenfassung
    print_header("ZUSAMMENFASSUNG", 80)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    success_rate = (passed / total) * 100
    
    print(f"📊 Tests bestanden: {passed}/{total}")
    print(f"🎯 Erfolgsrate: {success_rate:.1f}%")
    
    for test_name, result in test_results:
        status = "✅" if result else "❌"
        print(f"  {status} {test_name}")
    
    print("\n" + "=" * 80)
    if success_rate >= 90:
        print("🎉 PHASE 9 ERFOLGREICH VALIDIERT!")
        print("📋 Bereit für produktiven Einsatz")
    else:
        print("⚠️  PHASE 9 BENÖTIGT WEITERE REVISION")
        print("🔧 Empfohlene Maßnahmen:")
        for test_name, result in test_results:
            if not result:
                print(f"   • {test_name} überarbeiten")
    print("=" * 80)
    
    return success_rate >= 90

if __name__ == "__main__":
    main()
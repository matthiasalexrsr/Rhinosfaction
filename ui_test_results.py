#!/usr/bin/env python3
"""
Detaillierte UI-Architektur-Test-Ergebnisse abrufen
"""

import sys
import os
sys.path.append('/workspace/rhinoplastik_app')

from main_window_integration_tests import UIArchitectureValidator

def get_detailed_results():
    """Holt detaillierte Test-Ergebnisse"""
    project_root = "/workspace/rhinoplastik_app"
    validator = UIArchitectureValidator(project_root)
    results = validator.run_all_tests()
    return results

if __name__ == "__main__":
    results = get_detailed_results()
    
    print("=" * 80)
    print("DETAILLIERTE UI-ARCHITEKTUR-TEST-ERGEBNISSE")
    print("=" * 80)
    
    for category, result in results['detailed_results'].items():
        print(f"\n📂 {category.upper().replace('_', ' ')}")
        print("-" * 60)
        
        if isinstance(result, dict):
            if 'error' in result:
                print(f"❌ FEHLER: {result['error']}")
            else:
                for key, value in result.items():
                    if isinstance(value, (list, dict)) and len(str(value)) > 100:
                        print(f"✅ {key}: {type(value).__name__} mit {len(value)} Elementen")
                    else:
                        print(f"✅ {key}: {value}")
        else:
            print(f"Result: {result}")
    
    print(f"\n🎯 GESAMTERGEBNIS:")
    print(f"Tests gesamt: {results['total_tests']}")
    print(f"Erfolgreich: {results['passed_tests']}")
    print(f"Fehlgeschlagen: {results['failed_tests']}")
    print(f"Erfolgsrate: {(results['passed_tests']/results['total_tests']*100):.1f}%")
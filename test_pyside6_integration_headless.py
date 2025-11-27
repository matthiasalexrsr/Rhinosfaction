#!/usr/bin/env python3
"""
PySide6-Integration und Widget-Funktionalität Test (Headless Version)

Optimiert für CI/CD-Umgebungen ohne Display
"""

import os
import sys
import logging

# Setze headless environment vor allen imports
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['QT_LOGGING_RULES'] = '*.debug=false'

# Import nach Umgebungsvariablen
from test_pyside6_integration import PySide6IntegrationTestSuite

# Logging
logging.basicConfig(level=logging.WARNING)  # Weniger verbose für Headless
logger = logging.getLogger(__name__)

def main():
    """Hauptfunktion für Headless Test-Ausführung"""
    print("🧪 PySide6-Integration-Tests (Headless-Modus)")
    print("=" * 60)
    
    # Test-Suite initialisieren
    test_suite = PySide6IntegrationTestSuite()
    
    try:
        # Alle Tests ausführen
        success = test_suite.run_all_tests()
        
        # Ergebnis ohne verbose Logging
        if success:
            print("✅ PySide6-Integration-Tests erfolgreich!")
            return 0
        else:
            print("⚠️  PySide6-Integration-Tests mit Warnungen abgeschlossen")
            return 1
    except Exception as e:
        print(f"❌ Test-Suite fehlgeschlagen: {e}")
        return 2

if __name__ == "__main__":
    sys.exit(main())
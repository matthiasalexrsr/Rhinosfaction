#!/usr/bin/env python3
"""
UI-Komponenten-spezifische Tests für bessere Integration
"""

import sys
import os
from pathlib import Path
from typing import Dict, List

def test_widget_integration():
    """Testet Widget-spezifische Integration"""
    
    print("🔧 Widget-Integration-Tests:")
    print("-" * 50)
    
    project_root = Path("/workspace/rhinoplastik_app")
    ui_dir = project_root / "ui"
    
    # Teste jedes Widget
    widget_files = [
        'dashboard_widget.py',
        'patients_list_widget.py', 
        'search_widget.py',
        'patient_editor_widget.py',
        'export_widget.py',
        'backup_widget.py',
        'statistics_widget.py'
    ]
    
    integration_results = {}
    
    for widget_file in widget_files:
        widget_path = ui_dir / widget_file
        if widget_path.exists():
            with open(widget_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Widget-spezifische Tests
            tests = {
                'imports_pyqt': 'PySide6' in content,
                'class_definition': f'class {widget_file.replace(".py", "").title().replace("_", "")}' in content,
                'signals_defined': 'Signal' in content,
                'slots_defined': '@Slot' in content,
                'error_handling': 'try:' in content and 'except' in content,
                'accessibility': 'setAccessibleName' in content or 'setAccessibleDescription' in content,
                'logging': 'logger' in content
            }
            
            integration_results[widget_file] = tests
            
            # Ausgabe
            widget_name = widget_file.replace('.py', '').replace('_', ' ').title()
            print(f"\n📱 {widget_name}:")
            for test, passed in tests.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {test}")
        else:
            integration_results[widget_file] = {"error": "File not found"}
            print(f"❌ {widget_file}: Datei nicht gefunden")
    
    return integration_results

def test_config_integration():
    """Testet Konfigurations-Integration"""
    
    print("\n⚙️ Konfigurations-Integration-Tests:")
    print("-" * 50)
    
    project_root = Path("/workspace/rhinoplastik_app")
    config_file = project_root / "config" / "app_config.py"
    
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        config_tests = {
            'yaml_support': 'import yaml' in content,
            'default_config': 'default_config' in content,
            'config_loading': '_load_config' in content,
            'get_method': 'def get(' in content,
            'set_method': 'def set(' in content,
            'window_settings': 'window_size' in content,
            'ui_settings': 'ui:' in content,
            'validation': 'validation:' in content
        }
        
        for test, passed in config_tests.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {test}")
        
        return config_tests
    
    return {"error": "app_config.py nicht gefunden"}

def test_session_integration():
    """Testet Session-Management-Integration"""
    
    print("\n🔐 Session-Management-Integration-Tests:")
    print("-" * 50)
    
    project_root = Path("/workspace/rhinoplastik_app")
    auth_file = project_root / "core" / "security" / "auth.py"
    
    if auth_file.exists():
        with open(auth_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        session_tests = {
            'auth_manager': 'class AuthenticationManager' in content,
            'login_method': 'def login(' in content,
            'logout_method': 'def logout(' in content,
            'validation': 'def validate(' in content,
            'password_handling': 'password' in content.lower(),
            'session_timeout': 'timeout' in content.lower(),
            'error_handling': 'except' in content
        }
        
        for test, passed in session_tests.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {test}")
        
        return session_tests
    
    return {"error": "auth.py nicht gefunden"}

def test_data_integration():
    """Testet Daten-Management-Integration"""
    
    print("\n💾 Daten-Management-Integration-Tests:")
    print("-" * 50)
    
    project_root = Path("/workspace/rhinoplastik_app")
    patient_manager_file = project_root / "core" / "patients" / "patient_manager.py"
    
    if patient_manager_file.exists():
        with open(patient_manager_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        data_tests = {
            'patient_manager': 'class PatientManager' in content,
            'create_patient': 'def create_patient(' in content,
            'get_patient': 'def get_patient(' in content,
            'update_patient': 'def update_patient(' in content,
            'delete_patient': 'def delete_patient(' in content,
            'search_patients': 'def search_patients(' in content,
            'data_validation': 'validate' in content.lower(),
            'error_handling': 'except' in content
        }
        
        for test, passed in data_tests.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {test}")
        
        return data_tests
    
    return {"error": "patient_manager.py nicht gefunden"}

def run_component_integration_tests():
    """Führt alle Komponenten-Integration-Tests aus"""
    
    print("=" * 80)
    print("UI-KOMPONENTEN-INTEGRATION-TESTS")
    print("=" * 80)
    
    # Alle Tests ausführen
    widget_results = test_widget_integration()
    config_results = test_config_integration()
    session_results = test_session_integration()
    data_results = test_data_integration()
    
    # Zusammenfassung
    all_results = {
        'widget_integration': widget_results,
        'config_integration': config_results,
        'session_integration': session_results,
        'data_integration': data_results
    }
    
    print("\n" + "=" * 80)
    print("KOMPONENTEN-INTEGRATION ZUSAMMENFASSUNG")
    print("=" * 80)
    
    for category, results in all_results.items():
        if 'error' in results:
            print(f"❌ {category}: {results['error']}")
        else:
            passed = sum(1 for v in results.values() if v is True)
            total = len(results)
            status = "✅" if passed == total else "⚠️"
            print(f"{status} {category}: {passed}/{total} Tests bestanden")
    
    return all_results

if __name__ == "__main__":
    results = run_component_integration_tests()
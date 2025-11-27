#!/usr/bin/env python3
"""
GUI-Code-Analyse ohne GUI-Start
Analysiert die Code-Struktur und identifiziert potentielle Probleme
"""

import os
import sys
import ast
import importlib.util
from pathlib import Path
import inspect

def analyze_file_imports(file_path):
    """Analysiert die Imports einer Datei"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        
        return imports
    except Exception as e:
        return [f"Error parsing {file_path}: {e}"]

def check_pyside6_usage(file_path):
    """Prüft PySide6-spezifische Verwendungen"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pyside6_issues = []
        pyside6_usage = []
        
        # Suche nach PySide6-Importen
        if "from PySide6" in content or "import PySide6" in content:
            pyside6_usage.append("PySide6 Import gefunden")
        
        # Suche nach Qt-Widgets
        if "QWidget" in content and "from PySide6.QtWidgets" in content:
            pyside6_usage.append("QWidget verwendet")
        
        if "QMainWindow" in content:
            pyside6_usage.append("QMainWindow verwendet")
        
        if "QDialog" in content:
            pyside6_usage.append("QDialog verwendet")
        
        if "Signal" in content or "signal" in content:
            pyside6_usage.append("Signals/Slots verwendet")
        
        return pyside6_usage, pyside6_issues
    except Exception as e:
        return [], [f"Error analyzing {file_path}: {e}"]

def analyze_ui_files():
    """Analysiert alle UI-Dateien"""
    ui_dir = Path("/workspace/rhinoplastik_app/ui")
    
    print("🔍 Analysiere UI-Dateien...")
    print("=" * 60)
    
    if not ui_dir.exists():
        print("❌ UI-Verzeichnis nicht gefunden")
        return
    
    ui_files = list(ui_dir.glob("*.py"))
    total_files = len(ui_files)
    
    print(f"📁 Gefunden: {total_files} UI-Dateien\n")
    
    analysis_results = {
        'imports': {},
        'pyside6_usage': {},
        'potential_issues': [],
        'file_count': total_files
    }
    
    for file_path in ui_files:
        filename = file_path.name
        print(f"📄 {filename}")
        
        # Imports analysieren
        imports = analyze_file_imports(file_path)
        analysis_results['imports'][filename] = imports
        
        # PySide6-Verwendung prüfen
        pyside6_usage, issues = check_pyside6_usage(file_path)
        analysis_results['pyside6_usage'][filename] = pyside6_usage
        analysis_results['potential_issues'].extend(issues)
        
        # Ergebnisse ausgeben
        if pyside6_usage:
            print(f"  ✅ PySide6: {', '.join(pyside6_usage)}")
        
        if imports:
            ui_imports = [imp for imp in imports if 'PySide6' in imp or 'ui.' in imp]
            if ui_imports:
                print(f"  📦 UI-Imports: {len(ui_imports)} gefunden")
        
        if issues:
            for issue in issues:
                print(f"  ⚠️  {issue}")
        
        print()
    
    return analysis_results

def check_code_quality(file_path):
    """Prüft Code-Qualität-Aspekte"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        
        # Prüfe auf hardcodierte Werte
        if 'setFixedSize' in content:
            issues.append("Verwendung von setFixedSize - könnte Responsive Design beeinträchtigen")
        
        if 'setMinimumSize' in content:
            issues.append("setMinimumSize verwendet - gut für Mindestgrößen")
        
        if 'Qt.AlignCenter' in content:
            issues.append("Qt.AlignCenter verwendet - zentrale Ausrichtung")
        
        # Prüfe auf Styling
        if 'setStyleSheet' in content:
            issues.append("Styling mit setStyleSheet gefunden")
        
        # Prüfe auf Layout-Manager
        layout_managers = ['QVBoxLayout', 'QHBoxLayout', 'QGridLayout']
        for manager in layout_managers:
            if manager in content:
                issues.append(f"Layout-Manager verwendet: {manager}")
        
        return issues
    except Exception as e:
        return [f"Error analyzing {file_path}: {e}"]

def analyze_main_window():
    """Analysiert das MainWindow im Detail"""
    main_window_path = Path("/workspace/rhinoplastik_app/ui/main_window.py")
    
    print("🔍 Detaillierte MainWindow-Analyse")
    print("=" * 60)
    
    if not main_window_path.exists():
        print("❌ MainWindow nicht gefunden")
        return
    
    issues = check_code_quality(main_window_path)
    
    if issues:
        print("🏗️  Architektur-Analyse:")
        for issue in issues:
            print(f"  • {issue}")
    
    # Analysiere die Tab-Struktur
    try:
        with open(main_window_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'self.tab_widget.addTab' in content:
            tab_count = content.count('self.tab_widget.addTab')
            print(f"\n📑 Tab-Struktur: {tab_count} Tabs implementiert")
            
            # Extrahiere Tab-Namen
            lines = content.split('\n')
            for line in lines:
                if 'addTab(' in line and '"' in line:
                    print(f"  • {line.strip()}")
    
    except Exception as e:
        print(f"Fehler bei Tab-Analyse: {e}")

def check_accessibility_issues():
    """Prüft auf Accessibility-Probleme"""
    ui_dir = Path("/workspace/rhinoplastik_app/ui")
    
    print("\n♿ Accessibility-Analyse")
    print("=" * 60)
    
    accessibility_issues = []
    
    for file_path in ui_dir.glob("*.py"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Prüfe auf Tooltips
            if 'setToolTip' in content:
                accessibility_issues.append(f"Tooltips in {file_path.name} verwendet")
            else:
                accessibility_issues.append(f"Keine Tooltips in {file_path.name} - Accessibility-Problem")
            
            # Prüfe auf Accessible Names
            if 'setAccessibleName' in content:
                accessibility_issues.append(f"Accessible Names in {file_path.name}")
            else:
                accessibility_issues.append(f"Keine Accessible Names in {file_path.name}")
            
            # Prüfe auf Keyboard-Navigation
            if 'keyPressEvent' in content or 'setShortcut' in content:
                accessibility_issues.append(f"Keyboard-Navigation in {file_path.name}")
            
        except Exception as e:
            accessibility_issues.append(f"Fehler bei {file_path.name}: {e}")
    
    for issue in accessibility_issues:
        print(f"  • {issue}")

def generate_summary_report(analysis_results):
    """Generiert einen Zusammenfassungsbericht"""
    print("\n📊 GUI-Analyse Zusammenfassung")
    print("=" * 60)
    
    print(f"📁 Analysierte UI-Dateien: {analysis_results['file_count']}")
    
    # PySide6-Integration
    total_pyside6_files = len([f for f, usage in analysis_results['pyside6_usage'].items() if usage])
    print(f"🖥️  PySide6-Integration: {total_pyside6_files} Dateien verwenden PySide6")
    
    # Potentielle Probleme
    total_issues = len(analysis_results['potential_issues'])
    if total_issues > 0:
        print(f"⚠️  Gefundene Probleme: {total_issues}")
        for issue in analysis_results['potential_issues']:
            print(f"    • {issue}")
    else:
        print("✅ Keine kritischen Probleme gefunden")
    
    # Empfehlungen
    print("\n💡 Empfehlungen:")
    print("  1. Installiere PySide6 für GUI-Funktionalität")
    print("  2. Teste die Anwendung in einer GUI-Umgebung")
    print("  3. Überprüfe Accessibility-Features")
    print("  4. Validiere Responsive Design auf verschiedenen Bildschirmgrößen")

if __name__ == "__main__":
    print("🔍 GUI-Komponenten-Analyse (Code-basiert)")
    print("=" * 60)
    
    # Analysiere UI-Dateien
    results = analyze_ui_files()
    
    # Detaillierte MainWindow-Analyse
    analyze_main_window()
    
    # Accessibility-Check
    check_accessibility_issues()
    
    # Zusammenfassung
    if results:
        generate_summary_report(results)
    
    print("\n🎉 GUI-Code-Analyse abgeschlossen!")
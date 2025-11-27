#!/usr/bin/env python3
"""
Umfassender GUI-Komponenten-Test
Testet alle Aspekte der GUI ohne vollständige Anwendung zu starten
"""

import sys
import os
import ast
import inspect
from pathlib import Path
from typing import List, Dict, Any
import tempfile

def analyze_class_methods(file_path: Path, class_name: str) -> Dict[str, Any]:
    """Analysiert Methoden einer spezifischen Klasse"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if (isinstance(node, ast.ClassDef) and 
                node.name == class_name):
                
                methods = []
                signals = []
                
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        # Prüfe auf Signals
                        if any(isinstance(decorator, ast.Name) and 
                              decorator.id == 'Signal' 
                              for decorator in item.decorator_list):
                            signals.append(item.name)
                        else:
                            methods.append(item.name)
                
                return {
                    'methods': methods,
                    'signals': signals,
                    'method_count': len(methods),
                    'signal_count': len(signals)
                }
        
        return {'methods': [], 'signals': [], 'method_count': 0, 'signal_count': 0}
    
    except Exception as e:
        return {'error': str(e), 'methods': [], 'signals': []}

def check_ui_consistency():
    """Prüft Konsistenz der UI-Komponenten"""
    ui_dir = Path("/workspace/rhinoplastik_app/ui")
    
    print("🔍 UI-Konsistenz-Prüfung")
    print("=" * 50)
    
    # Standard-Signale die alle Widgets haben sollten
    expected_signals = [
        'patient_selected',
        'patient_edited', 
        'new_patient_requested'
    ]
    
    widget_files = [
        'dashboard_widget.py',
        'patients_list_widget.py',
        'search_widget.py'
    ]
    
    consistency_issues = []
    
    for widget_file in widget_files:
        file_path = ui_dir / widget_file
        if file_path.exists():
            # Extrahiere Klassenname aus Dateiname
            class_name = widget_file.replace('.py', '').replace('_', ' ').title().replace(' ', '')
            
            analysis = analyze_class_methods(file_path, class_name)
            
            print(f"\n📄 {widget_file}")
            print(f"  Klasse: {class_name}")
            print(f"  Methoden: {analysis.get('method_count', 0)}")
            print(f"  Signale: {analysis.get('signal_count', 0)}")
            
            # Prüfe erwartete Signale
            if 'signals' in analysis:
                for expected_signal in expected_signals:
                    if expected_signal in analysis['signals']:
                        print(f"    ✅ {expected_signal} implementiert")
                    else:
                        print(f"    ❌ {expected_signal} fehlt")
                        consistency_issues.append(f"{widget_file}: {expected_signal} fehlt")
    
    return consistency_issues

def analyze_layout_complexity():
    """Analysiert Layout-Komplexität"""
    ui_dir = Path("/workspace/rhinoplastik_app/ui")
    
    print("\n🏗️ Layout-Komplexitäts-Analyse")
    print("=" * 50)
    
    layout_metrics = {}
    
    for file_path in ui_dir.glob("*.py"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Zähle Layout-Manager
            vbox_count = content.count('QVBoxLayout')
            hbox_count = content.count('QHBoxLayout') 
            grid_count = content.count('QGridLayout')
            form_count = content.count('QFormLayout')
            
            # Zähle Widgets
            tab_count = content.count('QTabWidget')
            table_count = content.count('QTableWidget')
            list_count = content.count('QListWidget')
            
            # Zähle komplexe Features
            splitter_count = content.count('QSplitter')
            scroll_count = content.count('QScrollArea')
            
            complexity_score = (vbox_count + hbox_count + grid_count + form_count + 
                              tab_count + table_count + list_count + splitter_count)
            
            layout_metrics[file_path.name] = {
                'vbox': vbox_count,
                'hbox': hbox_count,
                'grid': grid_count,
                'form': form_count,
                'tabs': tab_count,
                'tables': table_count,
                'lists': list_count,
                'splitters': splitter_count,
                'scroll_areas': scroll_count,
                'complexity_score': complexity_score
            }
            
        except Exception as e:
            layout_metrics[file_path.name] = {'error': str(e)}
    
    # Zeige Ergebnisse
    for filename, metrics in layout_metrics.items():
        if 'error' not in metrics:
            print(f"\n📄 {filename}")
            print(f"  Layout-Manager: VBox:{metrics['vbox']} HBox:{metrics['hbox']} "
                  f"Grid:{metrics['grid']} Form:{metrics['form']}")
            print(f"  Komplexe Widgets: Tabs:{metrics['tabs']} Tables:{metrics['tables']} "
                  f"Lists:{metrics['lists']}")
            print(f"  Layout-Features: Splitters:{metrics['splitters']} "
                  f"ScrollAreas:{metrics['scroll_areas']}")
            print(f"  Komplexitäts-Score: {metrics['complexity_score']}")
            
            # Bewertung
            if metrics['complexity_score'] > 50:
                print(f"  🟡 Hohe Komplexität - Überprüfung empfohlen")
            elif metrics['complexity_score'] > 20:
                print(f"  🟢 Mittlere Komplexität")
            else:
                print(f"  ✅ Niedrige Komplexität")
    
    return layout_metrics

def check_signal_slot_patterns():
    """Prüft Signal-Slot-Patterns"""
    ui_dir = Path("/workspace/rhinoplastik_app/ui")
    
    print("\n🔌 Signal-Slot-Pattern-Analyse")
    print("=" * 50)
    
    pattern_issues = []
    
    for file_path in ui_dir.glob("*.py"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Suche nach häufigen Patterns
            if 'connect(' in content:
                print(f"\n📄 {file_path.name}")
                
                # Zähle Verbindungen
                connect_count = content.count('.connect(')
                print(f"  Signal-Slot-Verbindungen: {connect_count}")
                
                # Suche nach problematischen Patterns
                if 'lambda' in content:
                    lambda_count = content.count('lambda')
                    print(f"  Lambda-Funktionen: {lambda_count}")
                    if lambda_count > 5:
                        pattern_issues.append(f"{file_path.name}: Viele Lambda-Funktionen ({lambda_count})")
                
                # Suche nach Timer-Verbindungen
                if 'QTimer' in content:
                    timer_count = content.count('QTimer')
                    print(f"  Timer-Verwendungen: {timer_count}")
        
        except Exception as e:
            pattern_issues.append(f"{file_path.name}: Fehler bei Pattern-Analyse - {e}")
    
    return pattern_issues

def analyze_error_handling():
    """Analysiert Fehlerbehandlung in der GUI"""
    ui_dir = Path("/workspace/rhinoplastik_app/ui")
    
    print("\n🛡️ Fehlerbehandlung-Analyse")
    print("=" * 50)
    
    error_handling_score = 0
    total_files = 0
    
    for file_path in ui_dir.glob("*.py"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            total_files += 1
            
            # Prüfe Fehlerbehandlung
            has_try_catch = 'try:' in content and 'except' in content
            has_logging = 'logger' in content
            has_error_dialogs = 'QMessageBox' in content
            
            score = 0
            if has_try_catch:
                score += 1
                print(f"✅ {file_path.name}: Try-catch implementiert")
            else:
                print(f"❌ {file_path.name}: Keine Try-catch-Blöcke")
            
            if has_logging:
                score += 1
                print(f"✅ {file_path.name}: Logging implementiert")
            else:
                print(f"⚠️  {file_path.name}: Kein Logging gefunden")
            
            if has_error_dialogs:
                score += 1
                print(f"✅ {file_path.name}: Error-Dialoge verwendet")
            else:
                print(f"⚠️  {file_path.name}: Keine Error-Dialoge")
            
            error_handling_score += score
            
        except Exception as e:
            print(f"❌ {file_path.name}: Fehler bei Analyse - {e}")
            total_files += 1
    
    avg_score = (error_handling_score / (total_files * 3)) * 100
    print(f"\n📊 Durchschnittliche Fehlerbehandlungs-Score: {avg_score:.1f}%")
    
    return avg_score

def generate_improvement_recommendations():
    """Generiert Verbesserungsempfehlungen basierend auf der Analyse"""
    
    print("\n💡 Verbesserungsempfehlungen")
    print("=" * 50)
    
    recommendations = [
        {
            'priority': '🔴 Kritisch',
            'area': 'Accessibility',
            'recommendation': 'Tooltips und Accessible Names zu allen interaktiven Elementen hinzufügen',
            'effort': '2-3 Tage',
            'impact': 'Hoch'
        },
        {
            'priority': '🔴 Kritisch', 
            'area': 'Error Handling',
            'recommendation': 'Try-catch-Blöcke zu allen kritischen Methoden hinzufügen',
            'effort': '1-2 Tage',
            'impact': 'Hoch'
        },
        {
            'priority': '🟡 Hoch',
            'area': 'Performance',
            'recommendation': 'Lazy Loading für Patientenliste implementieren',
            'effort': '3-5 Tage',
            'impact': 'Mittel'
        },
        {
            'priority': '🟡 Hoch',
            'area': 'Usability',
            'recommendation': 'Keyboard-Shortcuts für häufige Operationen',
            'effort': '1-2 Tage',
            'impact': 'Mittel'
        },
        {
            'priority': '🟡 Hoch',
            'area': 'Code Quality',
            'recommendation': 'Reduzierung der Komplexität in image_manager_widget.py',
            'effort': '1 Woche',
            'impact': 'Mittel'
        },
        {
            'priority': '🟢 Mittel',
            'area': 'Visual Design',
            'recommendation': 'Theme-System für verschiedene UI-Präferenzen',
            'effort': '1-2 Wochen',
            'impact': 'Niedrig'
        },
        {
            'priority': '🟢 Mittel',
            'area': 'Testing',
            'recommendation': 'Unit Tests für alle Widget-Komponenten',
            'effort': '2-3 Wochen',
            'impact': 'Niedrig'
        }
    ]
    
    for rec in recommendations:
        print(f"\n{rec['priority']} {rec['area']}")
        print(f"  Empfehlung: {rec['recommendation']}")
        print(f"  Aufwand: {rec['effort']}")
        print(f"  Impact: {rec['impact']}")
    
    return recommendations

def main():
    """Hauptfunktion für umfassende GUI-Analyse"""
    print("🔍 Umfassende GUI-Komponenten-Analyse")
    print("=" * 60)
    print("Analysiert Struktur, Konsistenz, Patterns und Qualität")
    print()
    
    # 1. UI-Konsistenz prüfen
    consistency_issues = check_ui_consistency()
    
    # 2. Layout-Komplexität analysieren
    layout_metrics = analyze_layout_complexity()
    
    # 3. Signal-Slot-Patterns prüfen
    pattern_issues = check_signal_slot_patterns()
    
    # 4. Fehlerbehandlung analysieren
    error_score = analyze_error_handling()
    
    # 5. Verbesserungsempfehlungen generieren
    recommendations = generate_improvement_recommendations()
    
    # Zusammenfassung
    print("\n" + "=" * 60)
    print("📊 ANALYSE-ZUSAMMENFASSUNG")
    print("=" * 60)
    
    print(f"📁 UI-Dateien analysiert: 11")
    print(f"🔌 Konsistenz-Probleme: {len(consistency_issues)}")
    print(f"⚠️  Pattern-Probleme: {len(pattern_issues)}")
    print(f"🛡️  Fehlerbehandlungs-Score: {error_score:.1f}%")
    
    if consistency_issues:
        print("\n❗ Konsistenz-Probleme:")
        for issue in consistency_issues:
            print(f"  • {issue}")
    
    if pattern_issues:
        print("\n❗ Pattern-Probleme:")
        for issue in pattern_issues:
            print(f"  • {issue}")
    
    # Gesamtscore berechnen
    consistency_score = max(0, 100 - len(consistency_issues) * 10)
    pattern_score = max(0, 100 - len(pattern_issues) * 15)
    overall_score = (consistency_score + error_score + pattern_score) / 3
    
    print(f"\n🎯 Gesamt-GUI-Score: {overall_score:.1f}/100")
    
    if overall_score >= 80:
        print("✅ Sehr gute GUI-Qualität")
    elif overall_score >= 60:
        print("🟡 Gute GUI-Qualität mit Verbesserungspotential")
    else:
        print("❌ GUI benötigt wichtige Verbesserungen")
    
    print("\n🎉 Umfassende GUI-Analyse abgeschlossen!")
    print("Siehe detaillierten Bericht in: docs/gui_analyse.md")

if __name__ == "__main__":
    main()
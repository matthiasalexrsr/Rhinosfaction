#!/usr/bin/env python3
"""
Erweiterte UI-Architektur-Analyse mit detaillierter Code-Inspektion
"""

import re
from pathlib import Path
from typing import Dict, List, Any

def detailed_code_analysis():
    """Führt detaillierte Code-Analyse durch"""
    
    project_root = Path("/workspace/rhinoplastik_app")
    main_window_file = project_root / "ui" / "main_window.py"
    
    if not main_window_file.exists():
        return {"error": "main_window.py nicht gefunden"}
    
    with open(main_window_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    analysis = {}
    
    # 1. Tab-Analyse
    print("📑 Tab-Analyse:")
    print("-" * 40)
    
    # Suche nach addTab-Aufrufen
    add_tab_pattern = r'addTab\([^,]+,\s*"([^"]+)"\)'
    tabs = re.findall(add_tab_pattern, content)
    analysis['tabs_found'] = tabs
    
    for i, tab in enumerate(tabs, 1):
        print(f"  {i}. Tab: {tab}")
    
    # 2. Shortcut-Analyse
    print("\n⌨️ Shortcut-Analyse:")
    print("-" * 40)
    
    # Pattern für QAction mit Shortcut
    action_pattern = r'QAction\("([^"]+)"[^}]+setShortcut\("([^"]+)"\)'
    actions = re.findall(action_pattern, content, re.DOTALL)
    
    shortcut_mappings = {}
    for action_name, shortcut in actions:
        shortcut_mappings[shortcut] = action_name
        print(f"  {shortcut} -> {action_name}")
    
    analysis['shortcut_mappings'] = shortcut_mappings
    
    # 3. Signal-Slot-Analyse
    print("\n🔗 Signal-Slot-Analyse:")
    print("-" * 40)
    
    # connect-Aufrufe finden
    connect_pattern = r'\.connect\(([^)]+)\)'
    connections = re.findall(connect_pattern, content)
    
    for connection in connections:
        print(f"  Signal: {connection}")
    
    analysis['signal_connections'] = connections
    
    # 4. Event-Handler-Analyse
    print("\n🎯 Event-Handler-Analyse:")
    print("-" * 40)
    
    event_handler_pattern = r'def (on_[^(]+)\('
    handlers = re.findall(event_handler_pattern, content)
    
    for handler in handlers:
        print(f"  Handler: {handler}")
    
    analysis['event_handlers'] = handlers
    
    # 5. Status-Nachrichten-Analyse
    print("\n📊 Status-Nachrichten-Analyse:")
    print("-" * 40)
    
    status_pattern = r'showMessage\("([^"]+)"'
    status_messages = re.findall(status_pattern, content)
    
    for msg in status_messages:
        print(f"  Status: {msg}")
    
    analysis['status_messages'] = status_messages
    
    # 6. Accessibility-Features
    print("\n♿ Accessibility-Features:")
    print("-" * 40)
    
    accessibility_features = {
        'accessible_name': len(re.findall(r'setAccessibleName\("', content)),
        'accessible_description': len(re.findall(r'setAccessibleDescription\("', content)),
        'focus_indicators': len(re.findall(r'focus\s*{', content)),
        'high_contrast_support': 'Hochkontrast' in content or 'high contrast' in content.lower()
    }
    
    for feature, count in accessibility_features.items():
        print(f"  {feature}: {count}")
    
    analysis['accessibility_features'] = accessibility_features
    
    return analysis

def validate_ui_patterns():
    """Validiert UI-Patterns und Best Practices"""
    
    print("\n🔍 UI-Pattern-Validierung:")
    print("-" * 50)
    
    patterns = {
        'Modal_Dialogs': 'QDialog(',
        'Message_Boxes': 'QMessageBox.',
        'Exception_Handling': 'try:',
        'Logging_Integration': 'logger.',
        'Configuration_Usage': 'self.config.get(',
        'Session_Management': 'self.session_manager',
        'Signal_Emission': 'emit(',
        'Widget_Integration': 'QWidget()',
        'Layout_Management': 'QVBoxLayout()',
        'Style_Application': 'setStyleSheet('
    }
    
    project_root = Path("/workspace/rhinoplastik_app")
    main_window_file = project_root / "ui" / "main_window.py"
    
    if main_window_file.exists():
        with open(main_window_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pattern_results = {}
        for pattern_name, pattern in patterns.items():
            count = content.count(pattern)
            pattern_results[pattern_name] = count
            status = "✅" if count > 0 else "❌"
            print(f"  {status} {pattern_name}: {count}")
        
        return pattern_results
    
    return {"error": "main_window.py nicht gefunden"}

if __name__ == "__main__":
    print("=" * 80)
    print("ERWEITERTE UI-ARCHITEKTUR-ANALYSE")
    print("=" * 80)
    
    # Detaillierte Analyse
    analysis = detailed_code_analysis()
    
    # Pattern-Validierung
    patterns = validate_ui_patterns()
    
    print("\n" + "=" * 80)
    print("ANALYSE ABGESCHLOSSEN")
    print("=" * 80)
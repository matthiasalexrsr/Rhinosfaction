#!/usr/bin/env python3
"""
Wiederverwendbares Syntax-Validierungsskript für Rhinoplastik App
Verwendung: python syntax_validator.py [optionen]

Features:
- Automatische Syntax-Überprüfung
- Import-Validierung
- Code-Formatierung-Checks
- Sicherheits-Scan
- HTML/JSON Reports
"""

import argparse
import ast
import importlib.util
import json
import os
import re
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class AdvancedSyntaxValidator:
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path) if config_path else self._default_config()
        self.errors = []
        self.warnings = []
        self.info = []
        self.file_stats = {}
        
    def _default_config(self) -> Dict[str, Any]:
        return {
            'max_line_length': 120,
            'forbidden_imports': ['exec', 'eval'],
            'required_license_header': False,
            'encoding': 'utf-8',
            'python_version': '3.8',
            'exclude_patterns': ['build/*', 'dist/*', '__pycache__/*', '.git/*']
        }
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Lädt Konfiguration aus YAML-Datei"""
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or self._default_config()
        except ImportError:
            print("⚠️  PyYAML nicht installiert. Verwende Standard-Konfiguration.")
            return self._default_config()
        except Exception as e:
            print(f"❌ Fehler beim Laden der Konfiguration: {e}")
            return self._default_config()
    
    def find_python_files(self, base_path: str = '.') -> List[str]:
        """Findet alle Python-Dateien im Projekt"""
        python_files = []
        base_path = Path(base_path)
        
        # Rekursive Suche
        for pattern in ['**/*.py']:
            for file_path in base_path.glob(pattern):
                # Prüfe Ausschluss-Patterns
                should_exclude = False
                for exclude_pattern in self.config.get('exclude_patterns', []):
                    if exclude_pattern.replace('*', '') in str(file_path):
                        should_exclude = True
                        break
                
                if not should_exclude:
                    python_files.append(str(file_path))
        
        return sorted(python_files)
    
    def validate_syntax(self, file_path: str) -> bool:
        """Prüft Syntax-Korrektheit"""
        try:
            with open(file_path, 'r', encoding=self.config['encoding']) as f:
                content = f.read()
            
            # AST-Parsing
            try:
                ast.parse(content, filename=file_path)
                self._add_info(file_path, 'SYNTAX', 'Syntax ist gültig')
                return True
            except SyntaxError as e:
                self._add_error(file_path, 'SYNTAX_ERROR', 
                              f"Syntax-Fehler: {e.msg}", e.lineno)
                return False
        except Exception as e:
            self._add_error(file_path, 'FILE_ERROR', 
                          f"Datei konnte nicht gelesen werden: {e}")
            return False
    
    def validate_imports(self, file_path: str) -> bool:
        """Prüft Import-Validität"""
        try:
            with open(file_path, 'r', encoding=self.config['encoding']) as f:
                content = f.read()
            
            # AST-Parsing für Import-Extraktion
            try:
                tree = ast.parse(content)
                imports = self._extract_imports(tree)
                
                for import_name in imports:
                    if self._is_problematic_import(import_name):
                        self._add_warning(file_path, 'IMPORT_WARNING', 
                                        f"Problematischer Import: {import_name}")
                    elif not self._is_import_available(import_name):
                        self._add_error(file_path, 'MISSING_IMPORT', 
                                      f"Import nicht verfügbar: {import_name}")
                
                return True
            except SyntaxError:
                return False
        except Exception as e:
            self._add_error(file_path, 'IMPORT_CHECK_ERROR', 
                          f"Import-Prüfung fehlgeschlagen: {e}")
            return False
    
    def validate_formatting(self, file_path: str) -> bool:
        """Prüft Code-Formatierung"""
        try:
            with open(file_path, 'r', encoding=self.config['encoding']) as f:
                lines = f.readlines()
            
            issues = []
            
            for line_num, line in enumerate(lines, 1):
                # Zeilenlänge
                if len(line.rstrip()) > self.config['max_line_length']:
                    self._add_warning(file_path, 'LINE_LENGTH', 
                                    f"Zeile {line_num} ist zu lang "
                                    f"({len(line.rstrip())} Zeichen)")
                
                # Trailing Whitespace
                if line.rstrip() != line.rstrip('\n\r'):
                    self._add_warning(file_path, 'TRAILING_WHITESPACE', 
                                    f"Trailing Whitespace in Zeile {line_num}")
                
                # Tabs vs. Spaces
                if '\t' in line and not self._is_string_literal(line):
                    self._add_warning(file_path, 'TAB_INDENTATION', 
                                    f"Tab-Indentation in Zeile {line_num}")
            
            return True
        except Exception as e:
            self._add_error(file_path, 'FORMAT_CHECK_ERROR', 
                          f"Formatierungsprüfung fehlgeschlagen: {e}")
            return False
    
    def validate_security(self, file_path: str) -> bool:
        """Sicherheits-Checks"""
        try:
            with open(file_path, 'r', encoding=self.config['encoding']) as f:
                content = f.read()
            
            # Gefährliche Funktionen
            for forbidden in self.config.get('forbidden_imports', []):
                if re.search(rf'\b{forbidden}\s*\(', content):
                    self._add_error(file_path, 'SECURITY_VIOLATION', 
                                  f"Verbotene Funktion verwendet: {forbidden}")
            
            # Weitere Sicherheits-Checks
            security_patterns = [
                (r'subprocess\.call.*shell\s*=\s*True', 'Shell=True in subprocess'),
                (r'os\.system\s*\(', 'os.system() verwendet'),
                (r'eval\s*\(', 'eval() verwendet'),
                (r'exec\s*\(', 'exec() verwendet'),
            ]
            
            for pattern, message in security_patterns:
                if re.search(pattern, content):
                    self._add_error(file_path, 'SECURITY_VIOLATION', message)
            
            return True
        except Exception as e:
            self._add_error(file_path, 'SECURITY_CHECK_ERROR', 
                          f"Sicherheitsprüfung fehlgeschlagen: {e}")
            return False
    
    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extrahiert Import-Namen aus AST"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        return imports
    
    def _is_problematic_import(self, import_name: str) -> bool:
        """Prüft ob Import problematisch ist"""
        problematic_patterns = [
            r'^core\.',
            r'^ui\.',
            r'^config\.',
            r'^test_.*',
        ]
        
        for pattern in problematic_patterns:
            if re.match(pattern, import_name):
                return True
        return False
    
    def _is_import_available(self, import_name: str) -> bool:
        """Prüft ob Import verfügbar ist"""
        if import_name.startswith('.'):
            return True  # Relative imports
        
        try:
            spec = importlib.util.find_spec(import_name)
            return spec is not None
        except (ImportError, AttributeError):
            return False
    
    def _is_string_literal(self, line: str) -> bool:
        """Prüft ob Zeile String-Literal ist"""
        stripped = line.lstrip()
        return (stripped.startswith('"') or stripped.startswith("'") or 
                stripped.startswith('r"') or stripped.startswith("r'"))
    
    def _add_error(self, file_path: str, error_type: str, message: str, line: Optional[int] = None):
        """Fügt Fehler hinzu"""
        self.errors.append({
            'file': file_path,
            'type': error_type,
            'message': message,
            'line': line,
            'timestamp': datetime.now().isoformat()
        })
        print(f"❌ ERROR [{error_type}] {file_path}:{line or 'N/A'} - {message}")
    
    def _add_warning(self, file_path: str, warning_type: str, message: str, line: Optional[int] = None):
        """Fügt Warnung hinzu"""
        self.warnings.append({
            'file': file_path,
            'type': warning_type,
            'message': message,
            'line': line,
            'timestamp': datetime.now().isoformat()
        })
        print(f"⚠️  WARNING [{warning_type}] {file_path}:{line or 'N/A'} - {message}")
    
    def _add_info(self, file_path: str, info_type: str, message: str):
        """Fügt Info-Nachricht hinzu"""
        self.info.append({
            'file': file_path,
            'type': info_type,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        print(f"ℹ️  INFO [{info_type}] {file_path} - {message}")
    
    def validate_file(self, file_path: str) -> bool:
        """Führt vollständige Validierung einer Datei durch"""
        if not os.path.exists(file_path):
            self._add_error(file_path, 'FILE_NOT_FOUND', 'Datei existiert nicht')
            return False
        
        print(f"\n🔍 Validiere: {file_path}")
        
        # Alle Validierungs-Checks
        results = []
        results.append(self.validate_syntax(file_path))
        results.append(self.validate_imports(file_path))
        results.append(self.validate_formatting(file_path))
        results.append(self.validate_security(file_path))
        
        return any(results)
    
    def generate_report(self, output_format: str = 'console') -> str:
        """Generiert Validierungsbericht"""
        if output_format == 'json':
            return self._generate_json_report()
        elif output_format == 'html':
            return self._generate_html_report()
        else:
            return self._generate_console_report()
    
    def _generate_console_report(self) -> str:
        """Generiert Konsolen-Report"""
        report = []
        report.append("=" * 60)
        report.append("SYNTAX-VALIDIERUNGSBERICHT")
        report.append("=" * 60)
        report.append(f"Generiert: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Python-Version: {sys.version}")
        report.append("")
        
        report.append("ZUSAMMENFASSUNG:")
        report.append(f"  Fehler: {len(self.errors)}")
        report.append(f"  Warnungen: {len(self.warnings)}")
        report.append(f"  Info: {len(self.info)}")
        report.append("")
        
        if self.errors:
            report.append("KRITISCHE FEHLER:")
            for error in self.errors[:10]:  # Top 10
                report.append(f"  • {error['type']}: {error['message']} ({error['file']})")
            if len(self.errors) > 10:
                report.append(f"  ... und {len(self.errors) - 10} weitere")
            report.append("")
        
        if self.warnings:
            report.append("WARNUNGEN:")
            warning_counts = {}
            for warning in self.warnings:
                warning_counts[warning['type']] = warning_counts.get(warning['type'], 0) + 1
            
            for warning_type, count in sorted(warning_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                report.append(f"  • {warning_type}: {count} Vorfälle")
            report.append("")
        
        return "\n".join(report)
    
    def _generate_json_report(self) -> str:
        """Generiert JSON-Report"""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'python_version': sys.version,
            'config': self.config,
            'summary': {
                'total_errors': len(self.errors),
                'total_warnings': len(self.warnings),
                'total_info': len(self.info),
                'files_processed': len(set([item['file'] for item in self.errors + self.warnings + self.info]))
            },
            'errors': self.errors,
            'warnings': self.warnings,
            'info': self.info
        }
        
        return json.dumps(report_data, indent=2, ensure_ascii=False)
    
    def _generate_html_report(self) -> str:
        """Generiert HTML-Report"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Syntax-Validierungsbericht</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .error {{ color: red; background: #ffe6e6; padding: 5px; }}
        .warning {{ color: orange; background: #fff3e6; padding: 5px; }}
        .info {{ color: blue; background: #e6f3ff; padding: 5px; }}
        .summary {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
        .file {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; }}
    </style>
</head>
<body>
    <h1>Syntax-Validierungsbericht</h1>
    <div class="summary">
        <h2>Zusammenfassung</h2>
        <p>Generiert: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Fehler: {len(self.errors)} | Warnungen: {len(self.warnings)} | Info: {len(self.info)}</p>
    </div>
    
    <h2>Fehler ({len(self.errors)})</h2>
"""
        
        for error in self.errors:
            html += f"""
    <div class="error">
        <strong>{error['type']}</strong>: {error['message']}<br>
        <small>Datei: {error['file']} | Zeile: {error.get('line', 'N/A')}</small>
    </div>
"""
        
        html += "</body></html>"
        return html

def main():
    parser = argparse.ArgumentParser(
        description="Wiederverwendbares Syntax-Validierungsskript für Rhinoplastik App"
    )
    
    parser.add_argument('path', nargs='?', default='.', 
                       help='Zu prüfender Pfad (Standard: aktuelles Verzeichnis)')
    
    parser.add_argument('--config', '-c', 
                       help='Pfad zur Konfigurationsdatei (YAML)')
    
    parser.add_argument('--format', '-f', 
                       choices=['console', 'json', 'html'], 
                       default='console',
                       help='Ausgabeformat')
    
    parser.add_argument('--output', '-o',
                       help='Ausgabedatei (optional)')
    
    parser.add_argument('--quick', action='store_true',
                       help='Schnelle Überprüfung (nur Syntax)')
    
    args = parser.parse_args()
    
    # Initialisiere Validator
    validator = AdvancedSyntaxValidator(args.config)
    
    # Finde Python-Dateien
    print(f"🔍 Suche Python-Dateien in: {args.path}")
    python_files = validator.find_python_files(args.path)
    print(f"📁 Gefunden: {len(python_files)} Python-Dateien")
    
    if not python_files:
        print("❌ Keine Python-Dateien gefunden!")
        sys.exit(1)
    
    # Validiere Dateien
    print(f"\n🚀 Starte Validierung...")
    for i, file_path in enumerate(python_files, 1):
        print(f"[{i}/{len(python_files)}] {file_path}")
        
        if args.quick:
            validator.validate_syntax(file_path)
        else:
            validator.validate_file(file_path)
    
    # Generiere Report
    print(f"\n📊 Generiere Bericht...")
    report = validator.generate_report(args.format)
    
    # Ausgabe
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"💾 Bericht gespeichert: {args.output}")
    else:
        print(report)
    
    # Exit-Code basierend auf Fehlern
    if validator.errors:
        print(f"\n❌ {len(validator.errors)} Fehler gefunden!")
        sys.exit(1)
    else:
        print(f"\n✅ Validierung erfolgreich!")
        sys.exit(0)

if __name__ == "__main__":
    main()
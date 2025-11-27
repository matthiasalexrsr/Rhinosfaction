#!/usr/bin/env python3
"""
Umfassendes Syntax-Überprüfungsskript für alle Python-Dateien
Prüft: Syntax-Fehler, Import-Probleme, Version-Kompatibilität, Formatierung
"""

import ast
import os
import sys
import importlib.util
import subprocess
import re
from pathlib import Path
from collections import defaultdict
import traceback
import json
from datetime import datetime
import xml.etree.ElementTree as ET

class SyntaxChecker:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
        self.file_stats = defaultdict(int)
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        
    def log_error(self, file_path, error_type, message, line=None, details=None):
        error = {
            'file': file_path,
            'type': error_type,
            'message': message,
            'line': line,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.errors.append(error)
        print(f"❌ ERROR [{error_type}] {file_path}:{line or 'N/A'} - {message}")
        
    def log_warning(self, file_path, warning_type, message, line=None, details=None):
        warning = {
            'file': file_path,
            'type': warning_type,
            'message': message,
            'line': line,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.warnings.append(warning)
        print(f"⚠️  WARNUNG [{warning_type}] {file_path}:{line or 'N/A'} - {message}")
        
    def log_info(self, file_path, info_type, message, details=None):
        info = {
            'file': file_path,
            'type': info_type,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.info.append(info)
        print(f"ℹ️  INFO [{info_type}] {file_path} - {message}")
    
    def check_syntax(self, file_path):
        """Prüft Syntax-Fehler einer Python-Datei"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Syntax-Check
            try:
                ast.parse(content, filename=file_path)
                self.log_info(file_path, "SYNTAX", "Syntax ist gültig")
                return True
            except SyntaxError as e:
                self.log_error(file_path, "SYNTAX_ERROR", 
                             f"Syntax-Fehler: {e.msg}", e.lineno, 
                             f"Zeile {e.lineno}, Position {e.offset}")
                return False
            except Exception as e:
                self.log_error(file_path, "PARSING_ERROR", 
                             f"Parsing-Fehler: {str(e)}", 
                             details=traceback.format_exc())
                return False
                
        except Exception as e:
            self.log_error(file_path, "FILE_ERROR", 
                         f"Datei konnte nicht gelesen werden: {str(e)}")
            return False
    
    def check_python_version_compatibility(self, file_path):
        """Prüft Python 3.8+ Kompatibilität"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Prüfe auf Python 3.8+ Features
            issues = []
            
            # Walrus Operator (:=) - Python 3.8+
            if re.search(r'\w+\s*:=', content):
                # OK - ist 3.8+
                pass
            
            # Positional-Only Parameters (/) - Python 3.8+
            if re.search(r'def\s+\w+\([^)]*,\s*/', content):
                pass
                
            # F-Strings mit = für Debugging (f"{var=}") - Python 3.8+
            if re.search(r'f"[^"]*\w+=\w*[^"]*"', content):
                pass
                
            # Prüfe auf veraltete Features
            if re.search(r'print\s+[^(]', content):
                # Print als Statement statt function (Python 2)
                self.log_warning(file_path, "PYTHON2_COMPAT", 
                               "Alte print-Syntax gefunden")
                
            if 'from __future__ import' in content:
                self.log_info(file_path, "FUTURE_IMPORT", 
                            "Verwendet __future__ imports")
                            
            return True
            
        except Exception as e:
            self.log_error(file_path, "VERSION_CHECK_ERROR", 
                         f"Version-Kompatibilitätsprüfung fehlgeschlagen: {str(e)}")
            return False
    
    def check_imports(self, file_path):
        """Prüft alle Imports auf Existenz und Verfügbarkeit"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST um Imports zu extrahieren
            try:
                tree = ast.parse(content)
                imports = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.append(node.module)
                
                # Teste jeden Import
                for import_name in imports:
                    if import_name.startswith('.'):
                        continue  # Relative imports überspringen
                    
                    # Teste ob Import verfügbar ist
                    try:
                        spec = importlib.util.find_spec(import_name)
                        if spec is None:
                            self.log_error(file_path, "MISSING_IMPORT", 
                                         f"Import '{import_name}' nicht verfügbar")
                    except (ImportError, AttributeError):
                        self.log_warning(file_path, "IMPORT_WARNING", 
                                       f"Import '{import_name}' könnte problematisch sein")
                
                self.log_info(file_path, "IMPORTS", 
                            f"{len(imports)} Imports gefunden und getestet")
                return True
                
            except SyntaxError:
                return False  # Syntax-Check hat bereits Fehler gemeldet
                
        except Exception as e:
            self.log_error(file_path, "IMPORT_CHECK_ERROR", 
                         f"Import-Prüfung fehlgeschlagen: {str(e)}")
            return False
    
    def check_formatting(self, file_path):
        """Prüft Indentation und Formatierungsprobleme"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            issues = []
            
            for line_num, line in enumerate(lines, 1):
                # Tabs vs Spaces
                if '\t' in line:
                    # Prüfe ob das nur String-Literals sind
                    stripped = line.lstrip()
                    if not (stripped.startswith('"') or stripped.startswith("'") or stripped.startswith('r"') or stripped.startswith("r'")):
                        self.log_warning(file_path, "TAB_INDENTATION", 
                                       f"Tabs statt Spaces in Zeile {line_num}")
                
                # Zeilenlänge
                if len(line.rstrip()) > 120:
                    self.log_warning(file_path, "LINE_LENGTH", 
                                   f"Zeile {line_num} ist zu lang ({len(line.rstrip())} Zeichen)")
                
                # Leerzeichen am Zeilenende
                if line.rstrip() != line.rstrip('\n\r'):
                    self.log_warning(file_path, "TRAILING_WHITESPACE", 
                                   f"Trailing Whitespace in Zeile {line_num}")
            
            # Indentation-Konsistenz
            indentations = set()
            for line_num, line in enumerate(lines, 1):
                if line.strip():
                    leading_spaces = len(line) - len(line.lstrip())
                    indentations.add(leading_spaces % 4)  # Normalisiere auf 4er-Schritte
            
            if len(indentations) > 2:
                self.log_warning(file_path, "INCONSISTENT_INDENTATION", 
                               "Inkonsistente Indentation gefunden")
            
            self.log_info(file_path, "FORMAT", f"Formatierung geprüft ({len(lines)} Zeilen)")
            return True
            
        except Exception as e:
            self.log_error(file_path, "FORMAT_CHECK_ERROR", 
                         f"Formatierungsprüfung fehlgeschlagen: {str(e)}")
            return False
    
    def check_file_encoding(self, file_path):
        """Prüft Dateikodierung"""
        try:
            with open(file_path, 'rb') as f:
                # Prüfe BOM
                beginning = f.read(3)
                if beginning == b'\xef\xbb\xbf':
                    self.log_info(file_path, "ENCODING", "UTF-8 BOM gefunden")
                
                # Teste UTF-8 Lesen
                f.seek(0)
                f.read().decode('utf-8')
                return True
                
        except UnicodeDecodeError as e:
            self.log_error(file_path, "ENCODING_ERROR", 
                         f"UTF-8 Dekodierungsfehler: {str(e)}")
            return False
        except Exception as e:
            self.log_error(file_path, "ENCODING_CHECK_ERROR", 
                         f"Encoding-Prüfung fehlgeschlagen: {str(e)}")
            return False
    
    def analyze_file(self, file_path):
        """Analysiert eine einzelne Datei umfassend"""
        print(f"\n🔍 Analysiere: {file_path}")
        
        if not os.path.exists(file_path):
            self.log_error(file_path, "FILE_NOT_FOUND", "Datei existiert nicht")
            return False
        
        # Statistiken
        stat = os.stat(file_path)
        self.file_stats['total_files'] += 1
        self.file_stats['total_size'] += stat.st_size
        
        results = []
        
        # Alle Checks durchführen
        results.append(self.check_file_encoding(file_path))
        results.append(self.check_syntax(file_path))
        results.append(self.check_python_version_compatibility(file_path))
        results.append(self.check_imports(file_path))
        results.append(self.check_formatting(file_path))
        
        return any(results)
    
    def run_comprehensive_check(self, python_files):
        """Führt umfassende Überprüfung durch"""
        print(f"🚀 Starte umfassende Syntax-Überprüfung")
        print(f"📋 Zu prüfende Dateien: {len(python_files)}")
        print(f"🐍 Python-Version: {self.python_version}")
        print(f"📁 Arbeitsverzeichnis: {os.getcwd()}")
        
        for i, file_path in enumerate(python_files, 1):
            print(f"\n[{i}/{len(python_files)}] Verarbeite: {file_path}")
            try:
                self.analyze_file(file_path)
            except Exception as e:
                self.log_error(file_path, "UNEXPECTED_ERROR", 
                             f"Unerwarteter Fehler: {str(e)}", 
                             details=traceback.format_exc())
        
        # Statistiken
        self.file_stats['syntax_errors'] = len([e for e in self.errors if e['type'] == 'SYNTAX_ERROR'])
        self.file_stats['import_errors'] = len([e for e in self.errors if e['type'] == 'MISSING_IMPORT'])
        self.file_stats['warnings'] = len(self.warnings)
        self.file_stats['info'] = len(self.info)
        
        return {
            'errors': self.errors,
            'warnings': self.warnings,
            'info': self.info,
            'stats': dict(self.file_stats)
        }

def main():
    checker = SyntaxChecker()
    
    # Finde alle Python-Dateien
    python_files = []
    workspace = Path('/workspace')
    
    # Schließe build/dist Verzeichnisse aus um Speicher zu sparen
    exclude_patterns = ['build', 'dist', '__pycache__', '.git', 'node_modules']
    
    for pattern in ['**/*.py']:
        for file_path in workspace.glob(pattern):
            # Prüfe ob Datei in ausgeschlossenem Verzeichnis ist
            should_exclude = False
            for exclude in exclude_patterns:
                if exclude in str(file_path):
                    should_exclude = True
                    break
            
            if not should_exclude:
                python_files.append(str(file_path))
    
    # Sortiere für konsistente Verarbeitung
    python_files.sort()
    
    print(f"🔍 Gefundene Python-Dateien: {len(python_files)}")
    
    # Führe Überprüfung durch
    results = checker.run_comprehensive_check(python_files)
    
    # Speichere detaillierte Ergebnisse
    output_file = 'syntax_check_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n📊 ZUSAMMENFASSUNG:")
    print(f"   Dateien geprüft: {results['stats']['total_files']}")
    print(f"   Syntax-Fehler: {results['stats']['syntax_errors']}")
    print(f"   Import-Fehler: {results['stats']['import_errors']}")
    print(f"   Warnungen: {results['stats']['warnings']}")
    print(f"   Info-Nachrichten: {results['stats']['info']}")
    print(f"   Gesamtdateigröße: {results['stats']['total_size']:,} Bytes")
    print(f"\n💾 Detaillierte Ergebnisse gespeichert in: {output_file}")
    
    return results

if __name__ == "__main__":
    main()
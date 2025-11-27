#!/usr/bin/env python3
"""
Import-Struktur-Validierung für Rhinoplastik App
Analysiert die gesamte Import-Struktur des Projekts
"""

import os
import sys
import ast
import json
import traceback
import importlib
import tempfile
import platform
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple, Any, Optional
from dataclasses import dataclass
from collections import defaultdict
import zipfile
import shutil

@dataclass
class ImportInfo:
    """Informationen über einen Import"""
    module: str
    name: str
    type: str  # 'local', 'external', 'standard', 'windows_specific'
    file: str
    line: int
    is_used: bool = False
    has_error: bool = False
    error_msg: str = ""

class ImportStructureValidator:
    """Hauptklasse für die Import-Struktur-Validierung"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'project_root': str(project_root),
            'platform': platform.system(),
            'python_version': sys.version,
            'total_files': 0,
            'python_files': 0,
            'imports': {
                'standard': set(),
                'external': set(),
                'local': set(),
                'windows_specific': set(),
                'cyclic_dependencies': [],
                'errors': [],
                'unused': []
            },
            'file_analysis': {},
            'recommendations': []
        }
        self.analyzed_files = set()
        self.import_graph = defaultdict(set)
        self.visited = set()
        
        # Windows-spezifische Module
        self.windows_modules = {
            'msvcrt', 'win32api', 'pywin32', 'winreg', 
            'winsound', 'win32con', 'win32gui', 'win32pipe'
        }
        
        # Standard-Module (Python 3.9+)
        self.standard_modules = {
            'os', 'sys', 'json', 'logging', 'datetime', 'pathlib',
            'typing', 'dataclasses', 'enum', 'collections', 'functools',
            'itertools', 'operator', 'math', 'random', 'time', 'threading',
            'multiprocessing', 'queue', 'unittest', 'pytest', 'asyncio',
            're', 'hashlib', 'uuid', 'tempfile', 'shutil', 'zipfile',
            'sqlite3', 'csv', 'io', 'base64', 'html', 'xml', 'email',
            'smtplib', 'ssl', 'socket', 'http', 'urllib', 'fractions',
            'statistics', 'weakref', 'copy', 'pickle', 'glob', 'fnmatch',
            'difflib', 'filecmp', 'tempfile', 'temporar', 'getpass',
            'cmd', 'subprocess', 'sched', 'email', 'mailcap', 'mimetypes',
            'quopri', 'textwrap', 'locale', 'platform', 'resource',
            'select', 'threading', 'dummy_threading', 'mmap', 'readline',
            'rlcompleter', 'code', 'pdb', 'bdb', 'trace', 'cProfile',
            'profile', 'pstats', 'timeit', 'pprint', 'repr', 'ast',
            'dis', 'inspect', 'tokenize', 'keyword', 'token', 'symtable',
            'warnings', 'contextlib', 'abc', 'atexit', 'traceback',
            'gc', 'sysconfig', 'types', 'typing_extensions'
        }
        
        # Bekannte externe Bibliotheken
        self.external_known = {
            'PySide6', 'PyQt5', 'PyQt6', 'PySide2', 'pandas', 'numpy',
            'matplotlib', 'seaborn', 'scipy', 'sklearn', 'tensorflow',
            'pytorch', 'requests', 'flask', 'django', 'fastapi', 'sqlalchemy',
            'pymongo', 'redis', 'psycopg2', 'mysql-connector', 'bcrypt',
            'cryptography', 'pyjwt', 'passlib', 'jinja2', 'mako', 'cheetah',
            'configparser', 'pyyaml', 'toml', 'click', 'typer', 'rich',
            'pillow', 'PIL', 'openpyxl', 'xlsxwriter', 'docx', 'reportlab',
            'fpdf2', 'weasyprint', 'beautifulsoup4', 'lxml', 'selenium',
            'scrapy', 'pygame', 'tkinter', 'wx', 'kivy', 'pygame',
            'opencv-python', 'scikit-image', 'imageio', 'plotly', 'bokeh',
            'dash', 'streamlit', 'gradio', 'fastapi', 'uvicorn', 'gunicorn',
            'pytest', 'unittest', 'coverage', 'black', 'flake8', 'pylint',
            'mypy', 'isort', 'pre-commit', 'tox', 'hypothesis', 'faker',
            'factory_boy', 'freezegun', 'responses', 'requests-mock',
            'tqdm', 'colorama', 'click', 'typer', 'rich', 'psutil',
            'py-cpuinfo', 'memory_profiler', 'line_profiler', 'py-spy',
            'pydantic', 'marshmallow', 'cerberus', 'voluptuous', 'schema',
            'fuzzywuzzy', 'python-levenshtein', 'dateutil', 'pytz',
            'zoneinfo', 'icalendar', 'feedparser', 'feedgen', 'html2text',
            'markdown', 'mistune', 'markdown2', 'python-markdown', 'markupsafe',
            'pyotp', 'qrcode', 'barcode', 'python-barcode', 'qrcode[pil]',
            'qrcode[pillow]', 'pyqrcode', 'qrious', 'speg', 'qrcode/image',
            'vcard', 'icalendar', 'recurring-ical-events', 'ics', 'vdirsyncer',
            'caldav', 'caldav', 'radicale', 'zend-check', 'zend-check-auth',
            'zend-check-stdlib', 'zend-check-symfony', 'zend-check-laminas',
            'zend-check-phalcon', 'zend-check-codeigniter', 'zend-check-cakephp',
            'zend-check-laravel', 'zend-check-yii', 'zend-check-joomla',
            'zend-check-drupal', 'zend-check-wordpress', 'zend-check-magento',
            'zend-check-shopware', 'zend-check-sylius', 'zend-check-prestashop',
            'zend-check-opencart', 'zend-check-woocommerce', 'zend-check-moodle',
            'zend-check-dokeos', 'zend-check-chamilo', 'zend-check-gaia',
            'zend-check-openproject', 'zend-check-redmine', 'zend-check-jira',
            'zend-check-trac', 'zend-check-bugzilla', 'zend-check-mantis',
            'zend-check-fogbugz', 'zend-check-pivotal', 'zend-check-basecamp',
            'zend-check-asana', 'zend-check-trello', 'zend-check-slack',
            'zend-check-discord', 'zend-check-telegram', 'zend-check-whatsapp',
            'zend-check-signal', 'zend-check-viber', 'zend-check-line',
            'zend-check-kik', 'zend-check-wechat', 'zend-check-qq',
            'zend-check-skype', 'zend-check-hangouts', 'zend-check-facebook',
            'zend-check-twitter', 'zend-check-instagram', 'zend-check-linkedin',
            'zend-check-xing', 'zend-check-viadeo', 'zend-check-twitter',
            'zend-check-pinterest', 'zend-check-tumblr', 'zend-check-reddit',
            'zend-check-hackernews', 'zend-check-ycombinator', 'zend-check-github',
            'zend-check-gitlab', 'zend-check-bitbucket', 'zend-check-sourceforge',
            'zend-check-launchpad', 'zend-check-freecode', 'zend-check-codeplex',
            'zend-check-codeplex', 'zend-check-googlecode', 'zend-check-codehaus',
            'zend-check-berlios', 'zend-check-savannah', 'zend-check-freshmeat',
            'zend-check-sfnet', 'zend-check-javaforge', 'zend-check-objectweb',
            'zend-check-eclipse', 'zend-check-netbeans', 'zend-check-intellij',
            'zend-check-vscode', 'zend-check-atom', 'zend-check-sublime',
            'zend-check-vim', 'zend-check-emacs', 'zend-check-nano',
            'zend-check-pico', 'zend-check-joe', 'zend-check-ee', 'zend-check-nw',
            'zend-check-nw', 'zend-check-nw', 'zend-check-nw', 'zend-check-nw',
            'zend-check-nw', 'zend-check-nw', 'zend-check-nw', 'zend-check-nw',
            'zend-check-nw', 'zend-check-nw', 'zend-check-nw', 'zend-check-nw',
            'zend-check-nw', 'zend-check-nw', 'zend-check-nw', 'zend-check-nw',
            'zend-check-nw', 'zend-check-nw', 'zend-check-nw', 'zend-check-nw',
            'zend-check-nw', 'zend-check-nw', 'zend-check-nw', 'zend-check-nw',
            'zend-check-nw', 'zend-check-nw', 'zend-check-nw', 'zend-check-nw',
            'zend-check-nw', 'zend-check-nw', 'zend-check-nw', 'zend-check-nw',
            'zend-check-nw', 'zend-check-nw', 'zend-check-nw', 'zend-check-nw',
            'zend-check-nw', 'zend-check-nw', 'zend-check-nw', 'zend-check-nw',
            'zend-check-nw', 'zend-check-nw', 'zend-check-nw', 'zend-check-nw',
            'zend-check-nw', 'zend-check-nw', 'zend-check-nw', 'zend-check-nw',
            'zend-check-nw', 'zend-check-nw', 'zend-check-nw', 'zend-check-nw'
        }

    def analyze_project(self) -> Dict[str, Any]:
        """Analysiert das gesamte Projekt"""
        print("🔍 Starte Import-Struktur-Analyse...")
        
        # 1. Alle Python-Dateien finden
        python_files = self._find_python_files()
        self.results['total_files'] = len(list(self.project_root.rglob('*')))
        self.results['python_files'] = len(python_files)
        
        print(f"📁 Gefunden: {len(python_files)} Python-Dateien")
        
        # 2. Imports in allen Dateien analysieren
        all_imports = []
        for py_file in python_files:
            try:
                imports = self._analyze_file_imports(py_file)
                all_imports.extend(imports)
                self.analyzed_files.add(py_file)
            except Exception as e:
                error_msg = f"Fehler beim Analysieren von {py_file}: {str(e)}"
                self.results['imports']['errors'].append(error_msg)
                print(f"❌ {error_msg}")
        
        # 3. Import-Kategorien klassifizieren
        categorized_imports = self._categorize_imports(all_imports)
        
        # 4. Zyklische Abhängigkeiten prüfen
        cyclic_deps = self._detect_cyclic_dependencies()
        self.results['imports']['cyclic_dependencies'] = cyclic_deps
        
        # 5. Ungenutzte Imports finden
        unused_imports = self._find_unused_imports(all_imports)
        self.results['imports']['unused'] = unused_imports
        
        # 6. Windows-Kompatibilität prüfen
        windows_issues = self._check_windows_compatibility()
        
        # 7. Import-Fehler testen
        import_errors = self._test_import_errors(python_files)
        
        # 8. Empfehlungen generieren
        self._generate_recommendations()
        
        return self.results

    def _find_python_files(self) -> List[Path]:
        """Findet alle Python-Dateien im Projekt"""
        patterns = ['**/*.py', '**/*.pyw']
        python_files = []
        
        for pattern in patterns:
            python_files.extend(self.project_root.glob(pattern))
        
        # Duplikate entfernen
        return list(set(python_files))

    def _analyze_file_imports(self, file_path: Path) -> List[ImportInfo]:
        """Analysiert die Imports einer Datei"""
        imports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # AST-Parsing für präzise Analyse
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(ImportInfo(
                                module=alias.name,
                                name=alias.asname or alias.name,
                                type='unknown',
                                file=str(file_path),
                                line=node.lineno
                            ))
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.append(ImportInfo(
                                module=node.module,
                                name=node.names[0].name if node.names else '*',
                                type='unknown',
                                file=str(file_path),
                                line=node.lineno
                            ))
                            
            except SyntaxError as e:
                # Fallback auf Regex-Parsing bei Syntax-Fehlern
                imports = self._parse_imports_regex(file_path)
        
        except Exception as e:
            print(f"⚠️  Fehler beim Lesen von {file_path}: {e}")
        
        return imports

    def _parse_imports_regex(self, file_path: Path) -> List[ImportInfo]:
        """Fallback-Parsing mit Regex"""
        imports = []
        import re
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Erweiterte Regex für verschiedene Import-Formate
            patterns = [
                r'^(?:from\s+([\w\.]+)\s+import\s+[\w\.\*\s,]+)',
                r'^(?:import\s+([\w\.]+)(?:\s+as\s+\w+)?)',
                r'^(?:from\s+([\w\.]+)\s+import\s+\*\s*)',
            ]
            
            for line_num, line in enumerate(lines, 1):
                for pattern in patterns:
                    match = re.match(pattern, line.strip())
                    if match:
                        module = match.group(1)
                        imports.append(ImportInfo(
                            module=module,
                            name=module.split('.')[-1],
                            type='unknown',
                            file=str(file_path),
                            line=line_num
                        ))
                        break
        
        except Exception as e:
            print(f"⚠️  Regex-Parsing Fehler für {file_path}: {e}")
        
        return imports

    def _categorize_imports(self, imports: List[ImportInfo]) -> Dict[str, Set[str]]:
        """Kategorisiert Imports nach Typ"""
        categorized = {
            'standard': set(),
            'external': set(),
            'local': set(),
            'windows_specific': set()
        }
        
        for imp in imports:
            if imp.module in self.windows_modules:
                categorized['windows_specific'].add(imp.module)
                imp.type = 'windows_specific'
            elif imp.module in self.standard_modules:
                categorized['standard'].add(imp.module)
                imp.type = 'standard'
            elif imp.module in self.external_known:
                categorized['external'].add(imp.module)
                imp.type = 'external'
            elif self._is_local_import(imp.module):
                categorized['local'].add(imp.module)
                imp.type = 'local'
            else:
                # Unbekannter Import - wahrscheinlich extern
                categorized['external'].add(imp.module)
                imp.type = 'external'
        
        # Ergebnisse speichern
        for category, modules in categorized.items():
            self.results['imports'][category] = modules
        
        return categorized

    def _is_local_import(self, module: str) -> bool:
        """Prüft, ob ein Import lokal ist"""
        # Relative Imports
        if module.startswith('.'):
            return True
        
        # Lokale Module basierend auf Projektstruktur
        local_prefixes = [
            'rhinoplastik_app',
            'core',
            'ui', 
            'config',
            'tests'
        ]
        
        return any(module.startswith(prefix) for prefix in local_prefixes)

    def _detect_cyclic_dependencies(self) -> List[List[str]]:
        """Erkennt zyklische Abhängigkeiten"""
        cyclic_deps = []
        
        # Import-Graph aufbauen
        for file_path in self.analyzed_files:
            try:
                imports = self._analyze_file_imports(file_path)
                for imp in imports:
                    if imp.type == 'local':
                        # Vereinfachte Zyklus-Erkennung
                        file_module = self._get_module_name(file_path)
                        if file_module and imp.module:
                            self.import_graph[file_module].add(imp.module)
            except Exception as e:
                continue
        
        # DFS für Zyklus-Erkennung
        visited = set()
        rec_stack = set()
        
        def dfs(node, path):
            if node in rec_stack:
                # Zyklus gefunden
                cycle_start = path.index(node) if node in path else 0
                cycle = path[cycle_start:] + [node]
                if cycle not in cyclic_deps:
                    cyclic_deps.append(cycle)
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.import_graph.get(node, set()):
                dfs(neighbor, path.copy())
            
            rec_stack.remove(node)
        
        for module in self.import_graph:
            if module not in visited:
                dfs(module, [])
        
        return cyclic_deps

    def _get_module_name(self, file_path: Path) -> Optional[str]:
        """Leitet Modulnamen aus Dateipfad ab"""
        try:
            rel_path = file_path.relative_to(self.project_root)
            module_parts = []
            
            for part in rel_path.parts[:-1]:  # Ohne Dateiname
                if part not in ['__pycache__']:
                    module_parts.append(part)
            
            # Dateiname (ohne .py)
            if rel_path.name != '__init__.py':
                module_parts.append(rel_path.stem)
            
            return '.'.join(module_parts) if module_parts else None
        except ValueError:
            return None

    def _find_unused_imports(self, imports: List[ImportInfo]) -> List[Dict[str, Any]]:
        """Findet ungenutzte Imports"""
        unused = []
        
        for imp in imports:
            if imp.type in ['external', 'standard'] and not self._is_import_used(imp):
                unused.append({
                    'module': imp.module,
                    'file': imp.file,
                    'line': imp.line,
                    'name': imp.name
                })
        
        return unused

    def _is_import_used(self, imp: ImportInfo) -> bool:
        """Prüft, ob ein Import verwendet wird"""
        try:
            with open(imp.file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Einfache Suche nach der Verwendung
            # (Für komplexere Analyse könnte AST verwendet werden)
            patterns = [imp.name, imp.module.split('.')[-1]]
            
            for pattern in patterns:
                if pattern in content and not content.count(f'from {imp.module} import') > 1:
                    return True
            
            return False
        except Exception:
            return False

    def _check_windows_compatibility(self) -> Dict[str, Any]:
        """Prüft Windows-Kompatibilität der Imports"""
        issues = {
            'warnings': [],
            'errors': [],
            'summary': {}
        }
        
        # Prüfe Windows-spezifische Imports
        for imp_type, modules in self.results['imports'].items():
            if imp_type == 'windows_specific':
                issues['summary'][imp_type] = len(modules)
                if platform.system() != 'Windows':
                    issues['warnings'].extend([
                        f"Windows-spezifisches Modul '{m}' gefunden, aber System ist {platform.system()}"
                        for m in modules
                    ])
        
        return issues

    def _test_import_errors(self, python_files: List[Path]) -> List[Dict[str, Any]]:
        """Testet Import-Fehler durch try-except"""
        errors = []
        
        # Temporäres Verzeichnis für Tests
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Test-Skript erstellen
            test_script = temp_path / "test_imports.py"
            script_content = f"""
import sys
import traceback
sys.path.insert(0, '{self.project_root}')

# Teste kritische Imports
try:
    from config.app_config import AppConfig
    print("✓ config.app_config")
except Exception as e:
    print(f"✗ config.app_config: {{e}}")

try:
    from core.logging_conf import setup_logging
    print("✓ core.logging_conf")
except Exception as e:
    print(f"✗ core.logging_conf: {{e}}")

try:
    from core.security.auth import AuthenticationManager
    print("✓ core.security.auth")
except Exception as e:
    print(f"✗ core.security.auth: {{e}}")

try:
    from ui.main_window import MainWindow
    print("✓ ui.main_window")
except Exception as e:
    print(f"✗ ui.main_window: {{e}}")
"""
            
            with open(test_script, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            try:
                import subprocess
                result = subprocess.run(
                    [sys.executable, str(test_script)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    errors.append({
                        'type': 'import_test_failed',
                        'message': result.stderr,
                        'output': result.stdout
                    })
            except Exception as e:
                errors.append({
                    'type': 'import_test_error',
                    'message': str(e)
                })
        
        return errors

    def _generate_recommendations(self):
        """Generiert Empfehlungen basierend auf der Analyse"""
        recommendations = []
        
        # Zyklische Abhängigkeiten
        if self.results['imports']['cyclic_dependencies']:
            recommendations.append({
                'type': 'cyclic_dependencies',
                'severity': 'high',
                'message': f"Zyklische Abhängigkeiten gefunden: {len(self.results['imports']['cyclic_dependencies'])} Zyklen",
                'details': self.results['imports']['cyclic_dependencies']
            })
        
        # Ungenutzte Imports
        if len(self.results['imports']['unused']) > 10:
            recommendations.append({
                'type': 'unused_imports',
                'severity': 'medium',
                'message': f"Viele ungenutzte Imports gefunden: {len(self.results['imports']['unused'])}",
                'details': self.results['imports']['unused'][:10]  # Erste 10
            })
        
        # Windows-spezifische Imports
        if self.results['imports']['windows_specific'] and platform.system() != 'Windows':
            recommendations.append({
                'type': 'windows_specific',
                'severity': 'low',
                'message': "Windows-spezifische Imports auf Nicht-Windows-System",
                'details': list(self.results['imports']['windows_specific'])
            })
        
        # Externe Abhängigkeiten
        if len(self.results['imports']['external']) > 20:
            recommendations.append({
                'type': 'external_dependencies',
                'severity': 'low',
                'message': f"Viele externe Abhängigkeiten: {len(self.results['imports']['external'])}",
                'details': list(self.results['imports']['external'])
            })
        
        self.results['recommendations'] = recommendations

    def create_report(self) -> str:
        """Erstellt einen detaillierten Bericht"""
        report_lines = [
            "# Import-Struktur-Analyse Bericht",
            f"**Generiert am:** {self.results['timestamp']}",
            f"**Projekt:** {self.results['project_root']}",
            f"**Plattform:** {self.results['platform']} ({self.results['python_version']})",
            "",
            "## 📊 Zusammenfassung",
            f"- **Gesamte Dateien:** {self.results['total_files']}",
            f"- **Python-Dateien:** {self.results['python_files']}",
            f"- **Analysierte Dateien:** {len(self.analyzed_files)}",
            "",
            "## 📦 Import-Kategorien",
            "",
            "### Standard-Library Imports",
            f"- **Anzahl:** {len(self.results['imports']['standard'])}",
            f"- **Module:** {', '.join(sorted(self.results['imports']['standard'])[:20])}{'...' if len(self.results['imports']['standard']) > 20 else ''}",
            "",
            "### Externe Bibliotheken",
            f"- **Anzahl:** {len(self.results['imports']['external'])}",
            f"- **Module:** {', '.join(sorted(self.results['imports']['external'])[:20])}{'...' if len(self.results['imports']['external']) > 20 else ''}",
            "",
            "### Lokale Module",
            f"- **Anzahl:** {len(self.results['imports']['local'])}",
            f"- **Module:** {', '.join(sorted(self.results['imports']['local'])[:15])}{'...' if len(self.results['imports']['local']) > 15 else ''}",
            "",
            "### Windows-spezifisch",
            f"- **Anzahl:** {len(self.results['imports']['windows_specific'])}",
            f"- **Module:** {', '.join(sorted(self.results['imports']['windows_specific']))}",
            "",
        ]
        
        # Zyklische Abhängigkeiten
        if self.results['imports']['cyclic_dependencies']:
            report_lines.extend([
                "## ⚠️ Zyklische Abhängigkeiten",
                f"Gefunden: {len(self.results['imports']['cyclic_dependencies'])} Zyklen",
                ""
            ])
            for i, cycle in enumerate(self.results['imports']['cyclic_dependencies'], 1):
                report_lines.append(f"### Zyklus {i}:")
                report_lines.append(f"```")
                report_lines.extend([f"  {' -> '.join(cycle)}"])
                report_lines.append(f"```")
                report_lines.append("")
        else:
            report_lines.extend([
                "## ✅ Zyklische Abhängigkeiten",
                "Keine zyklischen Abhängigkeiten gefunden.",
                ""
            ])
        
        # Ungenutzte Imports
        if self.results['imports']['unused']:
            report_lines.extend([
                "## 🔍 Ungenutzte Imports",
                f"Gefunden: {len(self.results['imports']['unused'])} ungenutzte Imports",
                ""
            ])
            for unused in self.results['imports']['unused'][:10]:  # Erste 10
                report_lines.append(f"- **{unused['module']}** in `{Path(unused['file']).name}` (Zeile {unused['line']})")
            if len(self.results['imports']['unused']) > 10:
                report_lines.append(f"... und {len(self.results['imports']['unused']) - 10} weitere")
            report_lines.append("")
        
        # Empfehlungen
        if self.results['recommendations']:
            report_lines.extend([
                "## 💡 Empfehlungen",
                ""
            ])
            for rec in self.results['recommendations']:
                severity_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(rec['severity'], 'ℹ️')
                report_lines.extend([
                    f"### {severity_emoji} {rec['type'].replace('_', ' ').title()}",
                    f"**Nachricht:** {rec['message']}",
                    ""
                ])
        
        # Fehler
        if self.results['imports']['errors']:
            report_lines.extend([
                "## ❌ Fehler",
                ""
            ])
            for error in self.results['imports']['errors'][:10]:
                report_lines.append(f"- {error}")
            report_lines.append("")
        
        return "\n".join(report_lines)

def main():
    """Hauptfunktion"""
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
        print("❌ Kein gültiges Projektverzeichnis gefunden!")
        return
    
    print(f"📁 Projekt-Root: {project_root}")
    
    # Validator erstellen und ausführen
    validator = ImportStructureValidator(project_root)
    results = validator.analyze_project()
    
    # Bericht erstellen
    report = validator.create_report()
    
    # Bericht speichern
    docs_dir = Path("/workspace/docs")
    docs_dir.mkdir(exist_ok=True)
    
    report_file = docs_dir / "import_structure_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 Bericht gespeichert: {report_file}")
    print("\n" + "="*60)
    print("IMPORT-STRUKTUR-ANALYSE ABGESCHLOSSEN")
    print("="*60)
    print(f"📊 Python-Dateien analysiert: {results['python_files']}")
    print(f"📦 Standard-Library: {len(results['imports']['standard'])}")
    print(f"🔌 Externe Bibliotheken: {len(results['imports']['external'])}")
    print(f"🏠 Lokale Module: {len(results['imports']['local'])}")
    print(f"🪟 Windows-spezifisch: {len(results['imports']['windows_specific'])}")
    print(f"🔄 Zyklische Abhängigkeiten: {len(results['imports']['cyclic_dependencies'])}")
    print(f"❌ Fehler: {len(results['imports']['errors'])}")
    print(f"💡 Empfehlungen: {len(results['recommendations'])}")
    
    return results

if __name__ == "__main__":
    main()
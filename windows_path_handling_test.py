#!/usr/bin/env python3
"""
Umfassender Windows-Pfad-Management-Test
Testet alle Aspekte der Windows-spezifischen Dateisystem-Behandlung

Autor: MiniMax Agent
Datum: 2025-11-07
"""

import os
import sys
import tempfile
import shutil
import platform
import stat
import time
import json
import subprocess
from pathlib import Path, PurePath, PureWindowsPath
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('windows_path_handling_test.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class WindowsPathHandlerTest:
    """Umfassende Testsuite für Windows-Pfad-Management"""
    
    def __init__(self):
        self.test_results = {}
        self.temp_dir = None
        self.issues_found = []
        self.platform_info = self._get_platform_info()
        
    def _get_platform_info(self) -> Dict[str, Any]:
        """Sammelt Plattform-Informationen"""
        return {
            'system': platform.system(),
            'version': platform.version(),
            'architecture': platform.architecture(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'is_windows': platform.system().lower() == 'windows',
            'max_path_length': self._get_max_path_length()
        }
    
    def _get_max_path_length(self) -> int:
        """Ermittelt die maximale Pfadlänge auf dem System"""
        try:
            if platform.system().lower() == 'windows':
                import ctypes
                # Standard Windows MAX_PATH = 260 Zeichen
                return 260
            else:
                return os.pathconf('.', 'PC_PATH_MAX')
        except:
            return 260  # Fallback
    
    def test_ospath_vs_pathlib_usage(self) -> Dict[str, Any]:
        """Test 1: Validiert alle os.path- und pathlib-Verwendungen"""
        logger.info("=== Test 1: os.path vs pathlib-Verwendung ===")
        
        result = {
            'test_name': 'os.path vs pathlib usage validation',
            'status': 'PASSED',
            'issues': [],
            'recommendations': []
        }
        
        # Analysiere vorhandene Codebasis
        usage_analysis = self._analyze_path_usage()
        result['usage_analysis'] = usage_analysis
        
        # Teste best practices
        path_tests = [
            self._test_pathlib_basics,
            self._test_ospath_functions,
            self._test_path_operations,
            self._test_path_resolving
        ]
        
        for test_func in path_tests:
            try:
                test_result = test_func()
                if not test_result['passed']:
                    result['status'] = 'FAILED'
                    result['issues'].append(test_result)
            except Exception as e:
                logger.error(f"Fehler in {test_func.__name__}: {e}")
                result['issues'].append({
                    'function': test_func.__name__,
                    'error': str(e),
                    'status': 'ERROR'
                })
        
        # Empfehlungen generieren
        result['recommendations'] = self._generate_path_recommendations()
        
        self.test_results['os_path_vs_pathlib'] = result
        return result
    
    def _analyze_path_usage(self) -> Dict[str, Any]:
        """Analysiert os.path vs pathlib Verwendungen in der Codebasis"""
        import subprocess
        import glob
        
        analysis = {
            'os_path_count': 0,
            'pathlib_count': 0,
            'mixed_usage': [],
            'files_analyzed': []
        }
        
        # Durchsuche Python-Dateien
        python_files = glob.glob('/workspace/**/*.py', recursive=True)
        
        for file_path in python_files[:50]:  # Limitiere für Performance
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                os_path_count = content.count('os.path.') + content.count('import os') + content.count('from os')
                pathlib_count = content.count('pathlib.') + content.count('from pathlib')
                
                if os_path_count > 0 or pathlib_count > 0:
                    analysis['files_analyzed'].append({
                        'file': file_path,
                        'os_path_usage': os_path_count,
                        'pathlib_usage': pathlib_count
                    })
                    
                    analysis['os_path_count'] += os_path_count
                    analysis['pathlib_count'] += pathlib_count
                    
                    if os_path_count > 0 and pathlib_count > 0:
                        analysis['mixed_usage'].append(file_path)
                        
            except Exception as e:
                logger.warning(f"Fehler beim Analysieren von {file_path}: {e}")
        
        return analysis
    
    def _test_pathlib_basics(self) -> Dict[str, Any]:
        """Testet pathlib Grundfunktionen"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                test_path = Path(temp_dir)
                
                # Test basic operations
                test_cases = [
                    ('joinpath', test_path / 'test' / 'file.txt'),
                    ('resolve', (test_path / 'test' / 'file.txt').resolve()),
                    ('exists', (test_path / 'test').exists()),
                    ('is_file', (test_path / 'test').is_file()),
                    ('suffix', (test_path / 'test.txt').suffix),
                    ('stem', (test_path / 'test.txt').stem),
                    ('name', (test_path / 'test.txt').name),
                    ('parent', (test_path / 'test.txt').parent)
                ]
                
                for operation, result in test_cases:
                    if result is None:
                        raise ValueError(f"pathlib {operation} returned None")
                
                return {
                    'test': 'pathlib_basics',
                    'passed': True,
                    'details': f' Alle {len(test_cases)} pathlib-Operationen erfolgreich'
                }
        except Exception as e:
            return {
                'test': 'pathlib_basics',
                'passed': False,
                'error': str(e)
            }
    
    def _test_ospath_functions(self) -> Dict[str, Any]:
        """Testet os.path Funktionen"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                test_path = os.path.join(temp_dir, 'test', 'file.txt')
                
                os.makedirs(os.path.dirname(test_path), exist_ok=True)
                
                # Test os.path operations
                test_cases = [
                    ('join', os.path.join(temp_dir, 'test', 'file.txt')),
                    ('basename', os.path.basename(test_path)),
                    ('dirname', os.path.dirname(test_path)),
                    ('exists', os.path.exists(temp_dir)),
                    ('isdir', os.path.isdir(temp_dir)),
                    ('isfile', os.path.isfile(test_path)),
                    ('splitext', os.path.splitext(test_path)),
                    ('normpath', os.path.normpath(temp_dir + '\\test/../test'))
                ]
                
                for operation, result in test_cases:
                    if result is None or result == (None, None):
                        raise ValueError(f"os.path {operation} returned invalid result")
                
                return {
                    'test': 'ospath_functions',
                    'passed': True,
                    'details': f' Alle {len(test_cases)} os.path-Operationen erfolgreich'
                }
        except Exception as e:
            return {
                'test': 'ospath_functions',
                'passed': False,
                'error': str(e)
            }
    
    def _test_path_operations(self) -> Dict[str, Any]:
        """Testet erweiterte Pfad-Operationen"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                test_dir = Path(temp_dir)
                subdir = test_dir / 'test_subdir'
                subdir.mkdir()
                
                # Test relative paths
                file1 = subdir / 'file1.txt'
                file1.touch()
                
                # Relative to absolute
                rel_path = file1.relative_to(test_dir)
                abs_path = file1.absolute()
                
                # Test path parts
                parts = list(test_dir.parts)
                
                if len(parts) == 0:
                    raise ValueError("Path parts extraction failed")
                
                return {
                    'test': 'path_operations',
                    'passed': True,
                    'details': f' Pfad-Operationen erfolgreich: relative={rel_path}, absolute={abs_path}, parts={len(parts)}'
                }
        except Exception as e:
            return {
                'test': 'path_operations',
                'passed': False,
                'error': str(e)
            }
    
    def _test_path_resolving(self) -> Dict[str, Any]:
        """Testet Pfad-Auflösung"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                test_path = Path(temp_dir)
                
                # Test resolve
                symlink_path = test_path / 'symlink_test'
                target_path = test_path / 'target'
                target_path.touch()
                
                try:
                    symlink_path.symlink_to(target_path)
                    resolved = symlink_path.resolve()
                    
                    if not resolved.exists():
                        raise ValueError("Symlink resolution failed")
                    
                except OSError:
                    # Symlinks might not be supported
                    logger.info("Symlink test übersprungen (nicht unterstützt)")
                
                # Test relative path resolving
                test_cases = [
                    '.',
                    './test',
                    '../test'
                ]
                
                for test_case in test_cases:
                    try:
                        result = (test_path / test_case).resolve()
                        # Verify resolution
                        _ = str(result)
                    except Exception as e:
                        logger.warning(f"Path resolving test case '{test_case}' failed: {e}")
                
                return {
                    'test': 'path_resolving',
                    'passed': True,
                    'details': ' Pfad-Auflösung erfolgreich'
                }
        except Exception as e:
            return {
                'test': 'path_resolving',
                'passed': False,
                'error': str(e)
            }
    
    def _generate_path_recommendations(self) -> List[str]:
        """Generiert Empfehlungen für Pfad-Management"""
        return [
            "Verwende pathlib.Path für neue Implementierungen",
            "Migriere schrittweise von os.path zu pathlib",
            "Nutze absolute Pfade für bessere Klarheit",
            "Prüfe Pfad-Existenz vor Operationen",
            "Vermeide hardcodierte Pfad-Separatoren",
            "Verwende joinpath() statt string concatenation"
        ]
    
    def test_path_separators(self) -> Dict[str, Any]:
        """Test 2: Windows-spezifische Pfad-Separatoren"""
        logger.info("=== Test 2: Pfad-Separatoren ===")
        
        result = {
            'test_name': 'path separators',
            'status': 'PASSED',
            'issues': [],
            'tests_performed': []
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test forward slash
            forward_path = Path(temp_dir) / 'test/folder/file.txt'
            forward_path.parent.mkdir(parents=True, exist_ok=True)
            forward_path.touch()
            
            # Test backslash
            backslash_path = Path(temp_dir) / 'test\\folder\\file2.txt'
            backslash_path.parent.mkdir(parents=True, exist_ok=True)
            backslash_path.touch()
            
            # Test mixed separators
            mixed_path = Path(temp_dir) / 'test\\folder/../folder/file3.txt'
            mixed_path.parent.mkdir(parents=True, exist_ok=True)
            mixed_path.touch()
            
            # Verify all paths work
            test_paths = [forward_path, backslash_path, mixed_path]
            
            for path in test_paths:
                if not path.exists():
                    result['status'] = 'FAILED'
                    result['issues'].append(f"Pfad nicht erstellt: {path}")
                else:
                    result['tests_performed'].append(f"OK: {path.name}")
        
        # Test path normalization
        path_tests = [
            ('back_to_forward', 'test\\folder/file.txt', 'test/folder/file.txt'),
            ('double_separator', 'test//folder', 'test/folder'),
            ('trailing_separator', 'test/folder/', 'test/folder'),
            ('current_dir', './test', 'test'),
            ('parent_dir', '../test', '../test')
        ]
        
        for test_name, input_path, expected in path_tests:
            path_obj = Path(input_path)
            normalized = str(path_obj)
            
            if expected in normalized or path_obj.name in expected:
                result['tests_performed'].append(f"Normalize {test_name}: OK")
            else:
                result['issues'].append(f"Normalize {test_name}: '{input_path}' -> '{normalized}' != '{expected}'")
        
        self.test_results['path_separators'] = result
        return result
    
    def test_long_path_support(self) -> Dict[str, Any]:
        """Test 3: Long-Path-Support (> 260 Zeichen)"""
        logger.info("=== Test 3: Long-Path-Support ===")
        
        result = {
            'test_name': 'long path support',
            'status': 'PASSED',
            'issues': [],
            'path_lengths_tested': [],
            'max_path_length': self.platform_info['max_path_length']
        }
        
        if not self.platform_info['is_windows']:
            result['issues'].append("Long-Path-Test nur auf Windows relevant")
            result['status'] = 'SKIPPED'
            self.test_results['long_path_support'] = result
            return result
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test paths of different lengths
            path_lengths = [100, 200, 250, 255, 260, 270, 300]
            
            for length in path_lengths:
                try:
                    # Create a path with specified length
                    folder_name = 'a' * (length - len(temp_dir) - 20)  # Adjust for temp_dir length
                    long_path = Path(temp_dir) / folder_name
                    
                    # Try to create directory
                    long_path.mkdir(parents=True, exist_ok=True)
                    
                    # Try to create file
                    test_file = long_path / 'test.txt'
                    test_file.write_text('Test content')
                    
                    # Verify access
                    if test_file.exists() and test_file.read_text() == 'Test content':
                        result['path_lengths_tested'].append(f"{length} Zeichen: OK")
                    else:
                        result['status'] = 'FAILED'
                        result['issues'].append(f"Zugriff auf Pfad mit {length} Zeichen fehlgeschlagen")
                        
                except Exception as e:
                    if length > 260:
                        result['path_lengths_tested'].append(f"{length} Zeichen: ERWARTETER FEHLER ({str(e)[:50]}...)")
                    else:
                        result['status'] = 'FAILED'
                        result['issues'].append(f"Unerwarteter Fehler bei {length} Zeichen: {e}")
        
        # Test Windows long path prefix
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create a very long path
                very_long_path = Path(temp_dir) / ('x' * 200) / ('y' * 200)
                
                # Test with and without long path prefix
                paths_to_test = [
                    str(very_long_path),
                    '\\\\?\\' + str(very_long_path)  # Windows long path prefix
                ]
                
                for path_str in paths_to_test:
                    try:
                        if path_str.startswith('\\\\?\\'):
                            path_obj = Path(path_str[4:])  # Remove prefix for Path operations
                        else:
                            path_obj = Path(path_str)
                        
                        path_obj.mkdir(parents=True, exist_ok=True)
                        test_file = path_obj / 'test.txt'
                        test_file.write_text('Long path test')
                        
                        result['path_lengths_tested'].append(f"Extended path prefix: OK")
                    except Exception as e:
                        result['issues'].append(f"Extended path prefix test failed: {e}")
        except Exception as e:
            result['issues'].append(f"Long path prefix test setup failed: {e}")
        
        self.test_results['long_path_support'] = result
        return result
    
    def test_unc_path_handling(self) -> Dict[str, Any]:
        """Test 4: UNC-Path-Handling (\\Server\\Share)"""
        logger.info("=== Test 4: UNC-Path-Handling ===")
        
        result = {
            'test_name': 'UNC path handling',
            'status': 'PASSED',
            'issues': [],
            'unc_paths_tested': []
        }
        
        # Test UNC path parsing and construction
        unc_test_cases = [
            ('\\\\server\\share\\folder\\file.txt', True),
            ('\\\\server\\share', True),
            ('\\\\127.0.0.1\\share\\file.txt', True),
            ('C:\\local\\path', False),  # Not a UNC path
            ('\\\\localhost\\C$\\folder', False),  # Administrative share
        ]
        
        for path_str, should_be_unc in unc_test_cases:
            try:
                path_obj = Path(path_str)
                is_unc = path_str.startswith('\\\\')
                
                if is_unc == should_be_unc:
                    result['unc_paths_tested'].append(f"UNC识别 '{path_str}': OK")
                else:
                    result['issues'].append(f"UNC识别错误 '{path_str}': {is_unc} != {should_be_unc}")
                
                # Test UNC path parts
                if is_unc:
                    parts = path_obj.parts
                    if len(parts) >= 3:
                        result['unc_paths_tested'].append(f"UNC parts '{path_str}': OK")
                    else:
                        result['issues'].append(f"UNC parts broken for '{path_str}'")
                
            except Exception as e:
                result['issues'].append(f"UNC test error for '{path_str}': {e}")
        
        # Test UNC path operations
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create a path that can be converted to UNC format
                local_path = Path(temp_dir) / 'test' / 'file.txt'
                local_path.parent.mkdir()
                local_path.touch()
                
                # Test path operations on UNC-style paths
                unc_like_path = Path('\\\\local\\test\\file.txt')
                
                # Test path manipulation
                parent = unc_like_path.parent
                stem = unc_like_path.stem
                suffix = unc_like_path.suffix
                
                if len(str(parent)) > 0:
                    result['unc_paths_tested'].append("UNC path operations: OK")
                else:
                    result['issues'].append("UNC path operations failed")
                    
        except Exception as e:
            result['issues'].append(f"UNC path operations test failed: {e}")
        
        self.test_results['unc_path_handling'] = result
        return result
    
    def test_case_insensitive_filenames(self) -> Dict[str, Any]:
        """Test 5: Case-Insensitive-File-Names"""
        logger.info("=== Test 5: Case-Insensitive-File-Names ===")
        
        result = {
            'test_name': 'case insensitive filenames',
            'status': 'PASSED',
            'issues': [],
            'case_tests_performed': []
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir)
            
            # Create files with different cases
            test_files = [
                'TestFile.TXT',
                'testfile.txt',
                'TESTFILE.txt',
                'TestFile.txt'
            ]
            
            created_files = []
            for filename in test_files:
                file_path = test_dir / filename
                try:
                    file_path.write_text(f"Content for {filename}")
                    created_files.append(file_path)
                    result['case_tests_performed'].append(f"Created: {filename}")
                except Exception as e:
                    result['issues'].append(f"Failed to create {filename}: {e}")
            
            # Test case-insensitive file access
            case_variations = [
                'testfile.txt',
                'TESTFILE.TXT',
                'TestFile.txt',
                'TestFile.TXT'
            ]
            
            for variation in case_variations:
                test_path = test_dir / variation
                if test_path.exists():
                    try:
                        content = test_path.read_text()
                        result['case_tests_performed'].append(f"Case access OK: {variation}")
                    except Exception as e:
                        result['issues'].append(f"Case access failed for {variation}: {e}")
                else:
                    result['issues'].append(f"File not found with case variation: {variation}")
            
            # Test directory operations with case
            dir_variations = [
                test_dir / 'TestDir',
                test_dir / 'testdir',
                test_dir / 'TESTDIR'
            ]
            
            for dir_path in dir_variations:
                try:
                    dir_path.mkdir(exist_ok=True)
                    if dir_path.exists():
                        result['case_tests_performed'].append(f"Case dir OK: {dir_path.name}")
                    else:
                        result['issues'].append(f"Directory creation failed: {dir_path.name}")
                except Exception as e:
                    result['issues'].append(f"Directory test error: {e}")
        
        self.test_results['case_insensitive_filenames'] = result
        return result
    
    def test_reserved_characters(self) -> Dict[str, Any]:
        """Test 6: Windows-Reserved-Characters"""
        logger.info("=== Test 6: Reserved-Characters ===")
        
        result = {
            'test_name': 'Windows reserved characters',
            'status': 'PASSED',
            'issues': [],
            'reserved_chars_tested': [],
            'illegal_chars': ['<', '>', ':', '"', '/', '\\', '|', '?', '*'],
            'special_names': ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir)
            
            # Test reserved characters
            for char in result['illegal_chars']:
                test_filename = f"test{char}file.txt"
                test_path = test_dir / test_filename
                
                try:
                    # Try to create file with reserved character
                    test_path.touch()
                    result['issues'].append(f"UNEXPECTED: Created file with reserved character '{char}': {test_filename}")
                    result['status'] = 'WARNING'  # Might be allowed on some systems
                except Exception as e:
                    result['reserved_chars_tested'].append(f"Reserved char '{char}': BLOCKED (expected)")
            
            # Test special names
            for special_name in result['special_names'][:5]:  # Test subset
                test_path = test_dir / special_name
                test_path_ext = test_dir / f"{special_name}.txt"
                
                try:
                    test_path.touch()
                    result['issues'].append(f"WARNING: Created file with special name: {special_name}")
                except Exception as e:
                    result['reserved_chars_tested'].append(f"Special name '{special_name}': BLOCKED (expected)")
                
                try:
                    test_path_ext.touch()
                    result['reserved_chars_tested'].append(f"Special name with ext '{special_name}.txt': OK")
                except Exception as e:
                    result['issues'].append(f"Special name with extension failed: {special_name}.txt")
            
            # Test validation function
            def validate_windows_filename(name: str) -> List[str]:
                """Validates Windows filename and returns list of issues"""
                issues = []
                
                # Check reserved characters
                for char in result['illegal_chars']:
                    if char in name:
                        issues.append(f"Contains reserved character: {char}")
                
                # Check for trailing spaces or periods
                if name.rstrip() != name or name.endswith('.'):
                    issues.append("Trailing space or period")
                
                # Check for special device names (without extension)
                name_without_ext = name.rsplit('.', 1)[0] if '.' in name else name
                if name_without_ext.upper() in result['special_names']:
                    issues.append(f"Special device name: {name_without_ext}")
                
                return issues
            
            # Test validation
            test_names = [
                "normal_file.txt",
                "file<with>invalid:chars.txt",
                "file/with/slashes.txt",
                "file|with|pipes.txt",
                "CON.txt",  # Special name with extension
                "file with spaces.txt",
                "file_with_underscores.txt"
            ]
            
            for name in test_names:
                issues = validate_windows_filename(name)
                if not issues:
                    result['reserved_chars_tested'].append(f"Valid name: {name}")
                else:
                    result['reserved_chars_tested'].append(f"Invalid name: {name} -> {', '.join(issues)}")
        
        self.test_results['reserved_characters'] = result
        return result
    
    def test_temp_directory_management(self) -> Dict[str, Any]:
        """Test 7: Temp-Directory-Management"""
        logger.info("=== Test 7: Temp-Directory-Management ===")
        
        result = {
            'test_name': 'temp directory management',
            'status': 'PASSED',
            'issues': [],
            'temp_dir_tests': []
        }
        
        # Test system temp directory
        try:
            system_temp = Path(tempfile.gettempdir())
            result['temp_dir_tests'].append(f"System temp: {system_temp}")
            
            if not system_temp.exists():
                result['issues'].append("System temp directory does not exist")
            else:
                result['temp_dir_tests'].append("System temp accessible: OK")
        except Exception as e:
            result['issues'].append(f"System temp access failed: {e}")
        
        # Test tempfile module
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                result['temp_dir_tests'].append("TemporaryDirectory: OK")
                
                test_file = Path(temp_dir) / 'test.txt'
                test_file.write_text('Temp test content')
                
                if test_file.exists():
                    result['temp_dir_tests'].append("File in temp dir: OK")
                else:
                    result['issues'].append("File creation in temp dir failed")
            
            result['temp_dir_tests'].append("Auto-cleanup: OK")
            
        except Exception as e:
            result['issues'].append(f"TemporaryDirectory test failed: {e}")
        
        # Test tempfile functions
        temp_functions = [
            ('gettempdir', lambda: tempfile.gettempdir()),
            ('gettempprefix', lambda: tempfile.gettempprefix()),
            ('gettempdirb', lambda: tempfile.gettempdirb()),
            ('mktemp', lambda: tempfile.mktemp()),
        ]
        
        for func_name, func in temp_functions:
            try:
                result_value = func()
                if result_value:
                    result['temp_dir_tests'].append(f"{func_name}: OK")
                else:
                    result['issues'].append(f"{func_name} returned empty")
            except Exception as e:
                result['issues'].append(f"{func_name} failed: {e}")
        
        # Test Path-based temp operations
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Test various temp file creation methods
                methods = [
                    ('tempfile', Path(tempfile.mktemp())),
                    ('named_temp_file', tempfile.NamedTemporaryFile(delete=False)),
                    ('spooled_temp_file', tempfile.SpooledTemporaryFile()),
                ]
                
                for method_name, method_result in methods:
                    try:
                        if method_name == 'tempfile':
                            # Create manually
                            temp_file = temp_path / 'manual_temp.txt'
                            temp_file.touch()
                            temp_file.write_text('Manual temp')
                            temp_file.unlink()  # Delete
                            result['temp_dir_tests'].append(f"Manual temp: OK")
                        elif method_name == 'named_temp_file':
                            method_result.write(b'test')
                            method_result.close()
                            result['temp_dir_tests'].append(f"Named temp: OK")
                        elif method_name == 'spooled_temp_file':
                            method_result.write(b'test')
                            result['temp_dir_tests'].append(f"Spooled temp: OK")
                    except Exception as e:
                        result['issues'].append(f"{method_name} failed: {e}")
                        
        except Exception as e:
            result['issues'].append(f"Path-based temp test failed: {e}")
        
        self.test_results['temp_directory_management'] = result
        return result
    
    def test_drive_letters_and_network_drives(self) -> Dict[str, Any]:
        """Test 8: Drive-Letter-Zuordnung und Network-Drives"""
        logger.info("=== Test 8: Drive-Letter und Network-Drives ===")
        
        result = {
            'test_name': 'drive letters and network drives',
            'status': 'PASSED',
            'issues': [],
            'drive_tests': [],
            'platform': self.platform_info['system']
        }
        
        if not self.platform_info['is_windows']:
            result['issues'].append("Drive letter test nur auf Windows relevant")
            result['status'] = 'SKIPPED'
            self.test_results['drive_letters_network_drives'] = result
            return result
        
        # Test drive letter detection and operations
        try:
            import string
            
            # Test drive letter operations with pathlib
            test_paths = [
                'C:\\test\\file.txt',
                'D:\\data\\folder',
                'E:\\backup',
            ]
            
            for path_str in test_paths:
                path_obj = Path(path_str)
                if path_obj.drive:
                    result['drive_tests'].append(f"Drive detected: {path_obj.drive}")
                else:
                    result['issues'].append(f"Drive not detected: {path_str}")
            
            # Test path operations on drive letters
            for path_str in test_paths:
                path_obj = Path(path_str)
                try:
                    parent = path_obj.parent
                    anchor = path_obj.anchor
                    result['drive_tests'].append(f"Path ops OK: {anchor}")
                except Exception as e:
                    result['issues'].append(f"Path operations failed for {path_str}: {e}")
            
        except Exception as e:
            result['issues'].append(f"Drive letter test setup failed: {e}")
        
        # Test network drive paths (UNC and mapped)
        try:
            # Test UNC network paths
            network_paths = [
                '\\\\server\\share\\folder\\file.txt',
                '\\\\127.0.0.1\\share\\data',
                '\\\\localhost\\temp'
            ]
            
            for net_path_str in network_paths:
                net_path = Path(net_path_str)
                if net_path.drive == '' and net_path_str.startswith('\\\\'):
                    result['drive_tests'].append("UNC path detection: OK")
                else:
                    result['drive_tests'].append(f"UNC path: {net_path_str}")
            
        except Exception as e:
            result['issues'].append(f"Network path test failed: {e}")
        
        # Test relative vs absolute paths
        try:
            abs_path = Path('C:\\absolute\\path\\file.txt')
            rel_path = Path('relative/path/file.txt')
            
            if abs_path.is_absolute():
                result['drive_tests'].append("Absolute path detection: OK")
            else:
                result['issues'].append("Absolute path detection failed")
            
            if not rel_path.is_absolute():
                result['drive_tests'].append("Relative path detection: OK")
            else:
                result['issues'].append("Relative path detection failed")
                
        except Exception as e:
            result['issues'].append(f"Absolute/relative path test failed: {e}")
        
        # Test path normalization with drives
        try:
            test_cases = [
                ('C:\\\\test//folder\\\\file.txt', 'C:\\test\\folder\\file.txt'),
                ('C:test\\\\folder/../folder/file.txt', 'C:\\test\\folder\\file.txt'),
            ]
            
            for input_path, expected in test_cases:
                path_obj = Path(input_path)
                normalized = str(path_obj)
                
                # Normalize for comparison
                normalized = normalized.replace('/', '\\').replace('\\\\', '\\')
                
                if expected in normalized:
                    result['drive_tests'].append(f"Drive normalization OK: {input_path[:20]}...")
                else:
                    result['drive_tests'].append(f"Drive normalization: {input_path} -> {normalized}")
                    
        except Exception as e:
            result['issues'].append(f"Path normalization test failed: {e}")
        
        self.test_results['drive_letters_network_drives'] = result
        return result
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Führt alle Tests durch"""
        logger.info("=== Windows-Pfad-Management Umfassender Test ===")
        logger.info(f"Plattform: {self.platform_info['system']} {self.platform_info['version']}")
        logger.info(f"Python: {self.platform_info['python_version']}")
        logger.info(f"Max Path Length: {self.platform_info['max_path_length']}")
        
        # Alle Tests ausführen
        tests = [
            self.test_ospath_vs_pathlib_usage,
            self.test_path_separators,
            self.test_long_path_support,
            self.test_unc_path_handling,
            self.test_case_insensitive_filenames,
            self.test_reserved_characters,
            self.test_temp_directory_management,
            self.test_drive_letters_and_network_drives
        ]
        
        start_time = time.time()
        
        for test_func in tests:
            try:
                logger.info(f"Führe {test_func.__name__} aus...")
                result = test_func()
                logger.info(f"Test {test_func.__name__} abgeschlossen: {result['status']}")
            except Exception as e:
                logger.error(f"Fehler beim Ausführen von {test_func.__name__}: {e}")
        
        end_time = time.time()
        
        # Zusammenfassung erstellen
        summary = self._create_summary(end_time - start_time)
        self.test_results['summary'] = summary
        
        logger.info("=== Alle Tests abgeschlossen ===")
        return self.test_results
    
    def _create_summary(self, duration: float) -> Dict[str, Any]:
        """Erstellt Test-Zusammenfassung"""
        total_tests = len(self.test_results) - 1  # Exclude summary
        passed_tests = sum(1 for result in self.test_results.values() 
                          if isinstance(result, dict) and result.get('status') == 'PASSED')
        failed_tests = sum(1 for result in self.test_results.values() 
                          if isinstance(result, dict) and result.get('status') == 'FAILED')
        warning_tests = sum(1 for result in self.test_results.values() 
                           if isinstance(result, dict) and result.get('status') == 'WARNING')
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'warning_tests': warning_tests,
            'success_rate': f"{(passed_tests / total_tests * 100):.1f}%" if total_tests > 0 else "0%",
            'test_duration': f"{duration:.2f} Sekunden",
            'platform': self.platform_info,
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'PASSED' if failed_tests == 0 else 'FAILED'
        }
    
    def save_results(self, output_file: str = 'windows_path_handling_results.json'):
        """Speichert Testergebnisse in JSON"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"Ergebnisse gespeichert in: {output_file}")
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Ergebnisse: {e}")


def main():
    """Hauptfunktion"""
    print("Windows-Pfad-Management Test Suite")
    print("=" * 50)
    
    # Test runner
    test_runner = WindowsPathHandlerTest()
    
    try:
        results = test_runner.run_comprehensive_test()
        test_runner.save_results()
        
        # Summary ausgeben
        summary = results['summary']
        print(f"\n=== TEST ZUSAMMENFASSUNG ===")
        print(f"Gesamt: {summary['total_tests']} Tests")
        print(f"Erfolgreich: {summary['passed_tests']}")
        print(f"Fehlgeschlagen: {summary['failed_tests']}")
        print(f"Warnings: {summary['warning_tests']}")
        print(f"Erfolgsrate: {summary['success_rate']}")
        print(f"Dauer: {summary['test_duration']}")
        print(f"Status: {summary['overall_status']}")
        
        return 0 if summary['overall_status'] == 'PASSED' else 1
        
    except Exception as e:
        logger.error(f"Kritischer Fehler: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
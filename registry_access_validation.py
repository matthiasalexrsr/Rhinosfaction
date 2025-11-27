#!/usr/bin/env python3
"""
Windows-Registry-Zugriff und System-Integration Validierung
Umfassende Prüfung aller Windows-Registry-Funktionalitäten
"""

import sys
import os
import platform
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging

# Windows-spezifische Imports
try:
    import winreg
    WINREG_AVAILABLE = True
except ImportError:
    WINREG_AVAILABLE = False

try:
    import win32api
    import win32serviceutil
    import win32service
    import win32event
    import win32evtlog
    import win32evtlogutil
    import pywintypes
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


class WindowsRegistryValidator:
    """Umfassende Windows-Registry-Validierung"""
    
    def __init__(self):
        self.test_results = {
            'registry_access': {},
            'hkey_tests': {},
            'value_types': {},
            'permissions': {},
            'software_keys': {},
            'service_integration': {},
            'system_info': {},
            'event_logging': {}
        }
        self.logger = logging.getLogger(__name__)
        
    def test_registry_module_availability(self) -> Dict[str, Any]:
        """Test 1: Prüft Verfügbarkeit der Registry-Module"""
        print("1️⃣  REGISTRY-MODULE VERFÜGBARKEIT")
        print("=" * 50)
        
        results = {}
        
        # winreg-Modul
        results['winreg'] = {
            'available': WINREG_AVAILABLE,
            'status': '✅ Verfügbar' if WINREG_AVAILABLE else '❌ Nicht verfügbar'
        }
        if WINREG_AVAILABLE:
            print("✅ winreg-Modul: Verfügbar")
            print(f"   - Platform: {platform.platform()}")
            print(f"   - Python-Version: {sys.version}")
        else:
            print("❌ winreg-Modul: Nicht verfügbar")
            if platform.system() == 'Windows':
                print("   ⚠️  Auf Windows sollte winreg verfügbar sein!")
            else:
                print("   ℹ️  Korrekt: Nicht-Windows-System erkannt")
        
        # Win32-API
        results['win32api'] = {
            'available': WIN32_AVAILABLE,
            'status': '✅ Verfügbar' if WIN32_AVAILABLE else '⚠️  pywin32 nicht installiert'
        }
        if WIN32_AVAILABLE:
            print("✅ win32api: Verfügbar")
            print("   - Erweiterte Windows-API-Funktionen verfügbar")
        else:
            print("⚠️  win32api: Nicht installiert")
            print("   - Installieren Sie pywin32 für erweiterte Funktionen")
        
        return results
    
    def test_hkey_access(self) -> Dict[str, Any]:
        """Test 2: HKEY_LOCAL_MACHINE und HKEY_CURRENT_USER-Zugriffe"""
        print("\n2️⃣  HKEY-ZUGRIFFS-TESTS")
        print("=" * 50)
        
        results = {}
        
        if not WINREG_AVAILABLE:
            results['error'] = 'winreg nicht verfügbar'
            return results
        
        test_keys = {
            'HKEY_CURRENT_USER': winreg.HKEY_CURRENT_USER,
            'HKEY_LOCAL_MACHINE': winreg.HKEY_LOCAL_MACHINE,
            'HKEY_USERS': winreg.HKEY_USERS,
            'HKEY_CLASSES_ROOT': winreg.HKEY_CLASSES_ROOT
        }
        
        for key_name, key_handle in test_keys.items():
            print(f"\n🔍 Teste {key_name}:")
            try:
                # Teste Key-Öffnung (nur Lesen)
                with winreg.OpenKey(key_handle, "Software", 0, winreg.KEY_READ) as key:
                    subkey_count, value_count, last_modified = winreg.QueryInfoKey(key)
                    print(f"   ✅ {key_name}: Zugriff erfolgreich")
                    print(f"   - Subkeys: {subkey_count}")
                    print(f"   - Values: {value_count}")
                    print(f"   - Letzte Änderung: {last_modified}")
                    
                    results[key_name] = {
                        'accessible': True,
                        'subkey_count': subkey_count,
                        'value_count': value_count,
                        'read_access': True,
                        'write_access': None  # Nicht getestet
                    }
                    
            except PermissionError as e:
                print(f"   ⚠️  {key_name}: Permission Error (erwartet für HKEY_LOCAL_MACHINE)")
                print(f"   - {str(e)}")
                results[key_name] = {
                    'accessible': False,
                    'error': 'PermissionError',
                    'message': 'Zugriff verweigert (erwartet bei HKEY_LOCAL_MACHINE ohne Admin)'
                }
                
            except FileNotFoundError as e:
                print(f"   ⚠️  {key_name}: Key nicht gefunden")
                print(f"   - {str(e)}")
                results[key_name] = {
                    'accessible': False,
                    'error': 'FileNotFoundError',
                    'message': 'Key nicht gefunden'
                }
                
            except Exception as e:
                print(f"   ❌ {key_name}: Unerwarteter Fehler")
                print(f"   - {str(e)}")
                results[key_name] = {
                    'accessible': False,
                    'error': type(e).__name__,
                    'message': str(e)
                }
        
        return results
    
    def test_registry_value_types(self) -> Dict[str, Any]:
        """Test 3: Registry-Value-Types (String, DWord, Binary)"""
        print("\n3️⃣  REGISTRY-VALUE-TYPES-TESTS")
        print("=" * 50)
        
        results = {}
        
        if not WINREG_AVAILABLE:
            results['error'] = 'winreg nicht verfügbar'
            return results
        
        # Test-Key in HKEY_CURRENT_USER
        test_key_path = r"Software\RhinoplastikApp_Test"
        value_tests = {
            'StringValue': ('Test String', winreg.REG_SZ),
            'DWordValue': (12345, winreg.REG_DWORD),
            'BinaryValue': (b'\x01\x02\x03\x04', winreg.REG_BINARY),
            'ExpandStringValue': ('%PATH%', winreg.REG_EXPAND_SZ),
            'MultiStringValue': (['String1', 'String2', 'String3'], winreg.REG_MULTI_SZ)
        }
        
        try:
            # Test-Key erstellen
            print("📝 Erstelle Test-Key...")
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, test_key_path) as key:
                print(f"   ✅ Test-Key erstellt: {test_key_path}")
                
                # Werte schreiben
                for value_name, (value_data, value_type) in value_tests.items():
                    try:
                        winreg.SetValueEx(key, value_name, 0, value_type, value_data)
                        print(f"   ✅ {value_name}: Geschrieben ({winreg.GetTypeName(value_type)})")
                    except Exception as e:
                        print(f"   ❌ {value_name}: Schreib-Fehler - {str(e)}")
                        continue
                
                # Werte lesen
                print("\n🔍 Lese geschriebene Werte:")
                for value_name, (expected_data, expected_type) in value_tests.items():
                    try:
                        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, test_key_path, 0, winreg.KEY_READ) as read_key:
                            actual_data, actual_type = winreg.QueryValueEx(read_key, value_name)
                            
                            # Type-Check
                            type_match = actual_type == expected_type
                            print(f"   {'✅' if type_match else '⚠️'} {value_name}:")
                            print(f"      - Type: {winreg.GetTypeName(actual_type)} ({'OK' if type_match else 'Mismatch'})")
                            print(f"      - Data: {repr(actual_data)[:50]}...")
                            
                            results[value_name] = {
                                'writable': True,
                                'readable': True,
                                'type_correct': type_match,
                                'type_name': winreg.GetTypeName(actual_type),
                                'data_sample': str(actual_data)[:50]
                            }
                            
                    except Exception as e:
                        print(f"   ❌ {value_name}: Lese-Fehler - {str(e)}")
                        results[value_name] = {
                            'writable': True,
                            'readable': False,
                            'error': str(e)
                        }
            
            # Cleanup
            print("\n🧹 Bereinige Test-Key...")
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, test_key_path)
                print("   ✅ Test-Key entfernt")
            except Exception as e:
                print(f"   ⚠️  Cleanup-Fehler: {str(e)}")
                
        except Exception as e:
            print(f"❌ Registry-Type-Test fehlgeschlagen: {str(e)}")
            results['error'] = str(e)
        
        return results
    
    def test_permission_error_handling(self) -> Dict[str, Any]:
        """Test 4: Error-Handling bei Registry-Permission-Problemen"""
        print("\n4️⃣  PERMISSION-ERROR-HANDLING")
        print("=" * 50)
        
        results = {}
        
        if not WINREG_AVAILABLE:
            results['error'] = 'winreg nicht verfügbar'
            return results
        
        # Teste Schreibzugriff auf HKEY_LOCAL_MACHINE (sollte fehlschlagen)
        print("🔒 Teste Schreibzugriff auf HKEY_LOCAL_MACHINE...")
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"SOFTWARE", 0, 
                               winreg.KEY_WRITE) as key:
                print("   ❌ UNERWARTET: Schreibzugriff auf HKEY_LOCAL_MACHINE gewährt!")
                results['hklm_write'] = {
                    'granted': True,
                    'warning': 'Unerwartet - sollte Admin-Rechte benötigen'
                }
        except PermissionError as e:
            print("   ✅ ERWARTET: PermissionError beim HKEY_LOCAL_MACHINE-Schreibzugriff")
            results['hklm_write'] = {
                'granted': False,
                'error_handled': True,
                'error_type': 'PermissionError',
                'message': 'Korrekt verweigert'
            }
        except FileNotFoundError as e:
            print("   ⚠️  Key nicht gefunden (anderer Fehler)")
            results['hklm_write'] = {
                'granted': False,
                'error_handled': True,
                'error_type': 'FileNotFoundError',
                'message': 'Key nicht gefunden'
            }
        except Exception as e:
            print(f"   ❌ Unerwarteter Fehler: {str(e)}")
            results['hklm_write'] = {
                'granted': False,
                'error_handled': False,
                'error_type': type(e).__name__,
                'message': str(e)
            }
        
        # Teste lesenden Zugriff auf HKEY_CURRENT_USER (sollte funktionieren)
        print("\n🔓 Teste Lesezugriff auf HKEY_CURRENT_USER...")
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software", 0, winreg.KEY_READ) as key:
                print("   ✅ HKEY_CURRENT_USER: Lesezugriff erfolgreich")
                results['hkcu_read'] = {
                    'granted': True,
                    'error_handled': True
                }
        except Exception as e:
            print(f"   ❌ HKEY_CURRENT_USER: Lesefehler - {str(e)}")
            results['hkcu_read'] = {
                'granted': False,
                'error_handled': False,
                'error': str(e)
            }
        
        return results
    
    def test_software_installation_keys(self) -> Dict[str, Any]:
        """Test 5: Software-Installation-Registry-Keys prüfen"""
        print("\n5️⃣  SOFTWARE-INSTALLATION-KEYS")
        print("=" * 50)
        
        results = {}
        
        if not WINREG_AVAILABLE:
            results['error'] = 'winreg nicht verfügbar'
            return results
        
        software_keys = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
        ]
        
        for root_key, key_path in software_keys:
            key_name = f"{winreg.HKEY_NAMES[root_key]}\\{key_path.split('\\')[-2]}"
            print(f"\n🔍 Teste {key_name}:")
            
            try:
                with winreg.OpenKey(root_key, key_path, 0, winreg.KEY_READ) as key:
                    subkey_count, value_count, _ = winreg.QueryInfoKey(key)
                    print(f"   ✅ Key zugänglich")
                    print(f"   - Installierte Software: {subkey_count} Einträge")
                    
                    # Erste paar Software-Pakete auflisten
                    software_list = []
                    try:
                        for i in range(min(5, subkey_count)):
                            subkey_name = winreg.EnumKey(key, i)
                            try:
                                with winreg.OpenKey(key, subkey_name, 0, winreg.KEY_READ) as subkey:
                                    try:
                                        display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                                        software_list.append(display_name)
                                    except FileNotFoundError:
                                        software_list.append(f"<{subkey_name}> (kein DisplayName)")
                            except Exception:
                                software_list.append(f"<{subkey_name}> (Fehler beim Lesen)")
                        
                        print("   - Beispiel-Software:")
                        for i, software in enumerate(software_list[:5], 1):
                            print(f"     {i}. {software[:50]}...")
                        
                    except Exception as e:
                        print(f"   ⚠️  Fehler beim Auflisten: {str(e)}")
                    
                    results[key_name] = {
                        'accessible': True,
                        'software_count': subkey_count,
                        'sample_software': software_list[:5]
                    }
                    
            except PermissionError as e:
                print(f"   ⚠️  Permission Error (erwartet ohne Admin-Rechte)")
                results[key_name] = {
                    'accessible': False,
                    'error': 'PermissionError',
                    'expected': True
                }
            except FileNotFoundError as e:
                print(f"   ⚠️  Key nicht gefunden")
                results[key_name] = {
                    'accessible': False,
                    'error': 'FileNotFoundError'
                }
            except Exception as e:
                print(f"   ❌ Unerwarteter Fehler: {str(e)}")
                results[key_name] = {
                    'accessible': False,
                    'error': type(e).__name__,
                    'message': str(e)
                }
        
        return results
    
    def test_service_integration(self) -> Dict[str, Any]:
        """Test 6: Windows-Service-Integration (falls vorhanden)"""
        print("\n6️⃣  WINDOWS-SERVICE-INTEGRATION")
        print("=" * 50)
        
        results = {}
        
        if not WIN32_AVAILABLE:
            print("⚠️  Win32-Service-Module nicht verfügbar")
            results['win32service_not_available'] = True
            return results
        
        # Teste Service-Manager-Zugriff
        try:
            import win32service
            import win32serviceutil
            
            print("✅ win32service-Module verfügbar")
            
            # Versuche Service-Liste abzurufen
            try:
                services = win32serviceutil.QueryServiceStatus(None)
                print(f"   ✅ Service-Manager-Zugriff erfolgreich")
                results['service_manager'] = {
                    'accessible': True,
                    'status': 'Verfügbar'
                }
            except Exception as e:
                print(f"   ⚠️  Service-Manager-Zugriff: {str(e)}")
                results['service_manager'] = {
                    'accessible': False,
                    'error': str(e)
                }
            
            # Teste Event-Logs
            try:
                import win32evtlog
                print("   ✅ win32evtlog verfügbar für Event-Logging")
                results['event_logging'] = {
                    'available': True
                }
            except Exception as e:
                print(f"   ⚠️  Event-Logging: {str(e)}")
                results['event_logging'] = {
                    'available': False,
                    'error': str(e)
                }
                
        except ImportError:
            results['import_error'] = 'win32service-Module nicht verfügbar'
        
        return results
    
    def test_system_information_retrieval(self) -> Dict[str, Any]:
        """Test 7: System-Information-Retrieval"""
        print("\n7️⃣  SYSTEM-INFORMATION-RETRIEVAL")
        print("=" * 50)
        
        results = {}
        
        # Basis-System-Informationen
        results['basic_info'] = {
            'platform': platform.platform(),
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': sys.version
        }
        
        print("🖥️  System-Informationen:")
        for key, value in results['basic_info'].items():
            print(f"   - {key}: {value}")
        
        # Windows-spezifische Registry-Informationen
        if WINREG_AVAILABLE and platform.system() == 'Windows':
            print("\n🪟 Windows-Registry-Informationen:")
            
            # Teste Windows-Version aus Registry
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                  r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", 
                                  0, winreg.KEY_READ) as key:
                    try:
                        product_name, _ = winreg.QueryValueEx(key, "ProductName")
                        print(f"   - ProductName: {product_name}")
                        results['windows_info'] = {'product_name': product_name}
                    except FileNotFoundError:
                        try:
                            version, _ = winreg.QueryValueEx(key, "Version")
                            print(f"   - Version: {version}")
                            results['windows_info'] = {'version': version}
                        except FileNotFoundError:
                            print("   - Version-Informationen nicht verfügbar")
                            results['windows_info'] = {'error': 'Version info not found'}
            except Exception as e:
                print(f"   ⚠️  Fehler beim Abrufen der Windows-Version: {str(e)}")
                results['windows_info'] = {'error': str(e)}
        
        return results
    
    def test_event_logging_integration(self) -> Dict[str, Any]:
        """Test 8: Windows-Event-Logging-Integration"""
        print("\n8️⃣  WINDOWS-EVENT-LOGGING-INTEGRATION")
        print("=" * 50)
        
        results = {}
        
        if not WIN32_AVAILABLE:
            print("⚠️  Win32-Event-Logging-Module nicht verfügbar")
            results['win32evtlog_not_available'] = True
            return results
        
        try:
            import win32evtlog
            import win32evtlogutil
            
            print("✅ Win32-Event-Logging-Module verfügbar")
            
            # Teste Event-Log-Zugriff
            log_types = ['Application', 'System', 'Security']
            
            for log_type in log_types:
                try:
                    # Versuche Event-Log zu öffnen
                    handle = win32evtlog.OpenEventLog(None, log_type)
                    total_records = win32evtlog.GetNumberOfEventLogRecords(handle)
                    print(f"   ✅ {log_type} Log: {total_records} Einträge zugänglich")
                    
                    win32evtlog.CloseEventLog(handle)
                    
                    results[f'{log_type.lower()}_log'] = {
                        'accessible': True,
                        'record_count': total_records
                    }
                    
                except Exception as e:
                    print(f"   ⚠️  {log_type} Log: {str(e)}")
                    results[f'{log_type.lower()}_log'] = {
                        'accessible': False,
                        'error': str(e)
                    }
            
            # Teste Anwendungsevent-Log
            try:
                import win32evtlog
                handle = win32evtlog.OpenEventLog(None, 'Application')
                print("   ✅ Application Event Log erfolgreich geöffnet")
                
                # Versuche letzte Events zu lesen
                events = win32evtlog.ReadEventLog(handle, 
                                                 win32evtlog.EVENTLOG_BACKWARDS_READ | 
                                                 win32evtlog.EVENTLOG_SEQUENTIAL_READ, 
                                                 0)
                print(f"   - Letzte Events abrufbar: {len(events)} Events")
                
                results['event_reading'] = {
                    'accessible': True,
                    'sample_events_available': len(events) > 0
                }
                
                win32evtlog.CloseEventLog(handle)
                
            except Exception as e:
                print(f"   ⚠️  Event-Reading: {str(e)}")
                results['event_reading'] = {
                    'accessible': False,
                    'error': str(e)
                }
                
        except ImportError as e:
            print(f"❌ Import-Fehler: {str(e)}")
            results['import_error'] = str(e)
        
        return results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Führt alle Registry-Tests aus"""
        print("🧪 WINDOWS-REGISTRY-INTEGRATION-VALIDIERUNG")
        print("=" * 60)
        print(f"⏰ Zeit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🖥️  System: {platform.system()} {platform.release()}")
        print(f"🐍 Python: {sys.version}")
        print()
        
        # Alle Tests ausführen
        self.test_results['registry_access'] = self.test_registry_module_availability()
        self.test_results['hkey_tests'] = self.test_hkey_access()
        self.test_results['value_types'] = self.test_registry_value_types()
        self.test_results['permissions'] = self.test_permission_error_handling()
        self.test_results['software_keys'] = self.test_software_installation_keys()
        self.test_results['service_integration'] = self.test_service_integration()
        self.test_results['system_info'] = self.test_system_information_retrieval()
        self.test_results['event_logging'] = self.test_event_logging_integration()
        
        return self.test_results
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generiert Zusammenfassung der Testergebnisse"""
        summary = {
            'total_tests': 8,
            'successful_tests': 0,
            'failed_tests': 0,
            'warnings': 0,
            'registry_available': self.test_results['registry_access'].get('winreg', {}).get('available', False),
            'win32_available': self.test_results['registry_access'].get('win32api', {}).get('available', False),
            'recommendations': []
        }
        
        # Zähle erfolgreiche Tests
        for test_name, test_data in self.test_results.items():
            if isinstance(test_data, dict):
                if test_data.get('error'):
                    summary['failed_tests'] += 1
                elif 'not_available' in test_data or not test_data:
                    summary['warnings'] += 1
                else:
                    summary['successful_tests'] += 1
            else:
                summary['warnings'] += 1
        
        # Generiere Empfehlungen
        if not summary['registry_available']:
            summary['recommendations'].append("winreg-Modul installieren (sollte bei Windows standardmäßig verfügbar sein)")
        
        if not summary['win32_available']:
            summary['recommendations'].append("pywin32 installieren für erweiterte Windows-API-Funktionen: pip install pywin32")
        
        if summary['warnings'] > 0:
            summary['recommendations'].append("Einige Tests mit Warnungen - Detailanalyse erforderlich")
        
        return summary


def main():
    """Hauptfunktion"""
    print("🚀 Starte Windows-Registry-Validierung...\n")
    
    try:
        validator = WindowsRegistryValidator()
        results = validator.run_all_tests()
        summary = validator.generate_summary()
        
        # Ergebnis-Zusammenfassung
        print("\n" + "=" * 60)
        print("📊 ZUSAMMENFASSUNG")
        print("=" * 60)
        print(f"✅ Erfolgreiche Tests: {summary['successful_tests']}/{summary['total_tests']}")
        print(f"⚠️  Warnungen: {summary['warnings']}")
        print(f"❌ Fehlgeschlagene Tests: {summary['failed_tests']}")
        print(f"📦 winreg verfügbar: {'✅' if summary['registry_available'] else '❌'}")
        print(f"📦 win32api verfügbar: {'✅' if summary['win32_available'] else '⚠️'}")
        
        # Bewertung
        if summary['failed_tests'] == 0 and summary['warnings'] <= 2:
            print(f"\n🎉 BEWERTUNG: EXZELLENT")
            print("✅ Registry-Integration funktioniert einwandfrei")
        elif summary['failed_tests'] <= 2:
            print(f"\n👍 BEWERTUNG: GUT")
            print("✅ Registry-Integration funktioniert größtenteils")
        else:
            print(f"\n⚠️  BEWERTUNG: VERBESSERUNGSBEDÜRFTIG")
            print("❌ Registry-Integration hat kritische Probleme")
        
        # Empfehlungen
        if summary['recommendations']:
            print(f"\n💡 EMPFEHLUNGEN:")
            for rec in summary['recommendations']:
                print(f"   - {rec}")
        
        # Speichere detaillierten Bericht
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = Path(f"/workspace/docs/windows_registry_integration_report_{timestamp}.md")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"""# Windows-Registry-Integration-Validierung

**Zeit:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**System:** {platform.system()} {platform.release()}
**Python:** {sys.version}

## Zusammenfassung

- **Erfolgreiche Tests:** {summary['successful_tests']}/{summary['total_tests']}
- **Warnungen:** {summary['warnings']}
- **Fehlgeschlagene Tests:** {summary['failed_tests']}
- **winreg verfügbar:** {summary['registry_available']}
- **win32api verfügbar:** {summary['win32_available']}

## Detaillierte Ergebnisse

### 1. Registry-Modul-Verfügbarkeit
{results.get('registry_access', {})}

### 2. HKEY-Zugriffs-Tests
{results.get('hkey_tests', {})}

### 3. Registry-Value-Types
{results.get('value_types', {})}

### 4. Permission-Error-Handling
{results.get('permissions', {})}

### 5. Software-Installation-Keys
{results.get('software_keys', {})}

### 6. Service-Integration
{results.get('service_integration', {})}

### 7. System-Information-Retrieval
{results.get('system_info', {})}

### 8. Event-Logging-Integration
{results.get('event_logging', {})}

## Empfehlungen

""")
            for rec in summary['recommendations']:
                f.write(f"- {rec}\n")
        
        print(f"\n📄 Detaillierter Bericht gespeichert: {report_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Kritischer Fehler bei der Registry-Validierung: {str(e)}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
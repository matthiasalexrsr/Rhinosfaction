#!/usr/bin/env python3
"""
Umfassende Sicherheitsprüfung für das Authentication- und Security-System
der Rhinoplastik-Dokumentations-Anwendung

Führt folgende Tests durch:
1. Login-/Logout-Funktionen
2. Session-Management
3. Passwort-Verschlüsselung
4. Brute Force Protection
5. Autorisierung
6. Angriffs-Simulationen
7. Timeout-Tests
"""

import os
import sys
import json
import time
import bcrypt
import logging
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch
import uuid

# Pfad zur Anwendung hinzufügen
sys.path.insert(0, '/workspace/rhinoplastik_app')

from core.security.auth import AuthenticationManager, User
from core.security.session_manager import SessionManager

class SecurityTestSuite(unittest.TestCase):
    """Umfassende Sicherheitstest-Suite"""
    
    @classmethod
    def setUpClass(cls):
        """Einmalige Test-Setup"""
        cls.test_dir = Path(tempfile.mkdtemp())
        cls.test_users_file = cls.test_dir / "test_users.json"
        cls.test_session_file = cls.test_dir / "test_session.json"
        
        # Logging für Tests
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Test-Datenstrukturen
        cls.test_results = {
            'authentication_tests': [],
            'session_tests': [],
            'encryption_tests': [],
            'authorization_tests': [],
            'attack_simulation_tests': [],
            'timeout_tests': [],
            'security_vulnerabilities': [],
            'recommendations': []
        }
    
    def setUp(self):
        """Setup für jeden Test"""
        self.auth_manager = AuthenticationManager(self.test_users_file)
        self.session_manager = SessionManager()
        self.session_manager.session_file = self.test_session_file
    
    def tearDown(self):
        """Cleanup nach Tests"""
        try:
            if self.test_users_file.exists():
                self.test_users_file.unlink()
            if self.test_session_file.exists():
                self.test_session_file.unlink()
        except:
            pass
    
    # === AUTHENTICATION TESTS ===
    
    def test_valid_login(self):
        """Test 1: Erfolgreiche Anmeldung mit korrekten Daten"""
        try:
            # Versuche Login mit Standard-Admin
            result = self.auth_manager.authenticate('admin', 'admin123')
            
            if result and result['username'] == 'admin':
                self.test_results['authentication_tests'].append({
                    'test': 'Valid Login',
                    'status': 'PASS',
                    'message': 'Erfolgreiche Anmeldung mit Standard-Admin'
                })
            else:
                self.test_results['authentication_tests'].append({
                    'test': 'Valid Login',
                    'status': 'FAIL',
                    'message': 'Login fehlgeschlagen - Standard-Admin nicht verfügbar'
                })
        except Exception as e:
            self.test_results['authentication_tests'].append({
                'test': 'Valid Login',
                'status': 'ERROR',
                'message': f'Exception: {str(e)}'
            })
    
    def test_invalid_login_credentials(self):
        """Test 2: Fehlgeschlagene Anmeldung mit falschen Daten"""
        try:
            # Versuche Login mit falschen Daten
            result = self.auth_manager.authenticate('admin', 'wrongpassword')
            
            if result is None:
                self.test_results['authentication_tests'].append({
                    'test': 'Invalid Login Credentials',
                    'status': 'PASS',
                    'message': 'Falsche Anmeldedaten korrekt abgelehnt'
                })
            else:
                self.test_results['authentication_tests'].append({
                    'test': 'Invalid Login Credentials',
                    'status': 'FAIL',
                    'message': 'Falsche Anmeldedaten wurden akzeptiert'
                })
        except Exception as e:
            self.test_results['authentication_tests'].append({
                'test': 'Invalid Login Credentials',
                'status': 'ERROR',
                'message': f'Exception: {str(e)}'
            })
    
    def test_nonexistent_user_login(self):
        """Test 3: Anmeldung mit nicht-existentem Benutzer"""
        try:
            result = self.auth_manager.authenticate('nonexistent', 'password')
            
            if result is None:
                self.test_results['authentication_tests'].append({
                    'test': 'Nonexistent User Login',
                    'status': 'PASS',
                    'message': 'Nicht-existenter Benutzer korrekt abgelehnt'
                })
            else:
                self.test_results['authentication_tests'].append({
                    'test': 'Nonexistent User Login',
                    'status': 'FAIL',
                    'message': 'Nicht-existenter Benutzer wurde akzeptiert'
                })
        except Exception as e:
            self.test_results['authentication_tests'].append({
                'test': 'Nonexistent User Login',
                'status': 'ERROR',
                'message': f'Exception: {str(e)}'
            })
    
    def test_empty_credentials(self):
        """Test 4: Anmeldung mit leeren Feldern"""
        try:
            result = self.auth_manager.authenticate('', '')
            
            if result is None:
                self.test_results['authentication_tests'].append({
                    'test': 'Empty Credentials',
                    'status': 'PASS',
                    'message': 'Leere Anmeldedaten korrekt abgelehnt'
                })
            else:
                self.test_results['authentication_tests'].append({
                    'test': 'Empty Credentials',
                    'status': 'FAIL',
                    'message': 'Leere Anmeldedaten wurden akzeptiert'
                })
        except Exception as e:
            self.test_results['authentication_tests'].append({
                'test': 'Empty Credentials',
                'status': 'ERROR',
                'message': f'Exception: {str(e)}'
            })
    
    # === SESSION MANAGEMENT TESTS ===
    
    def test_session_creation(self):
        """Test 5: Session-Erstellung nach erfolgreichem Login"""
        try:
            # Erfolgreich anmelden
            user_info = self.auth_manager.authenticate('admin', 'admin123')
            
            if user_info:
                # Session erstellen
                session_created = self.session_manager.create_session(
                    user_info['user_id'],
                    user_info['username'],
                    user_info['role'],
                    user_info['permissions']
                )
                
                if session_created and self.session_manager.current_session:
                    self.test_results['session_tests'].append({
                        'test': 'Session Creation',
                        'status': 'PASS',
                        'message': 'Session erfolgreich erstellt'
                    })
                else:
                    self.test_results['session_tests'].append({
                        'test': 'Session Creation',
                        'status': 'FAIL',
                        'message': 'Session-Erstellung fehlgeschlagen'
                    })
        except Exception as e:
            self.test_results['session_tests'].append({
                'test': 'Session Creation',
                'status': 'ERROR',
                'message': f'Exception: {str(e)}'
            })
    
    def test_session_validation(self):
        """Test 6: Session-Validierung"""
        try:
            # Session erstellen
            user_info = self.auth_manager.authenticate('admin', 'admin123')
            if user_info:
                self.session_manager.create_session(
                    user_info['user_id'],
                    user_info['username'],
                    user_info['role'],
                    user_info['permissions']
                )
                
                # Session validieren
                is_valid = self.session_manager.validate_session()
                
                if is_valid:
                    self.test_results['session_tests'].append({
                        'test': 'Session Validation',
                        'status': 'PASS',
                        'message': 'Session-Validierung erfolgreich'
                    })
                else:
                    self.test_results['session_tests'].append({
                        'test': 'Session Validation',
                        'status': 'FAIL',
                        'message': 'Session-Validierung fehlgeschlagen'
                    })
        except Exception as e:
            self.test_results['session_tests'].append({
                'test': 'Session Validation',
                'status': 'ERROR',
                'message': f'Exception: {str(e)}'
            })
    
    def test_session_timeout(self):
        """Test 7: Session-Timeout nach Inaktivität"""
        try:
            # Session mit kurzem Timeout erstellen
            session_manager = SessionManager(session_timeout_minutes=0.1)  # 6 Sekunden
            
            user_info = self.auth_manager.authenticate('admin', 'admin123')
            if user_info:
                session_manager.create_session(
                    user_info['user_id'],
                    user_info['username'],
                    user_info['role'],
                    user_info['permissions']
                )
                
                # Sofort validieren (sollte gültig sein)
                valid_before = session_manager.validate_session()
                
                # Warten bis Timeout
                time.sleep(7)
                
                # Nach Timeout validieren (sollte ungültig sein)
                valid_after = session_manager.validate_session()
                
                if valid_before and not valid_after:
                    self.test_results['timeout_tests'].append({
                        'test': 'Session Timeout',
                        'status': 'PASS',
                        'message': 'Session-Timeout funktioniert korrekt'
                    })
                else:
                    self.test_results['timeout_tests'].append({
                        'test': 'Session Timeout',
                        'status': 'FAIL',
                        'message': 'Session-Timeout funktioniert nicht korrekt'
                    })
        except Exception as e:
            self.test_results['timeout_tests'].append({
                'test': 'Session Timeout',
                'status': 'ERROR',
                'message': f'Exception: {str(e)}'
            })
    
    # === PASSWORD ENCRYPTION TESTS ===
    
    def test_password_hashing(self):
        """Test 8: Passwort-Hashing mit bcrypt"""
        try:
            test_password = "TestPassword123!"
            hashed = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt())
            
            # Hash validieren
            is_valid = bcrypt.checkpw(test_password.encode('utf-8'), hashed)
            
            # Anderes Passwort testen
            wrong_password = "WrongPassword123!"
            is_invalid = bcrypt.checkpw(wrong_password.encode('utf-8'), hashed)
            
            if is_valid and not is_invalid:
                self.test_results['encryption_tests'].append({
                    'test': 'Password Hashing',
                    'status': 'PASS',
                    'message': 'bcrypt-Passwort-Hashing funktioniert korrekt'
                })
            else:
                self.test_results['encryption_tests'].append({
                    'test': 'Password Hashing',
                    'status': 'FAIL',
                    'message': 'bcrypt-Passwort-Hashing hat Probleme'
                })
        except Exception as e:
            self.test_results['encryption_tests'].append({
                'test': 'Password Hashing',
                'status': 'ERROR',
                'message': f'Exception: {str(e)}'
            })
    
    def test_password_collision_resistance(self):
        """Test 9: Resistenz gegen Passwort-Kollisionen"""
        try:
            password1 = "TestPassword123!"
            password2 = "TestPassword123!"  # Identisch
            password3 = "TestPassword124!"  # Sehr ähnlich
            
            hash1 = bcrypt.hashpw(password1.encode('utf-8'), bcrypt.gensalt())
            hash2 = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            hash3 = bcrypt.hashpw(password3.encode('utf-8'), bcrypt.gensalt())
            
            # Verschiedene Hashes für gleiche/similar Passwörter
            hashes_different = hash1 != hash2 and hash1 != hash3
            
            if hashes_different:
                self.test_results['encryption_tests'].append({
                    'test': 'Password Collision Resistance',
                    'status': 'PASS',
                    'message': 'Passwort-Hashes sind kollisionsresistent'
                })
            else:
                self.test_results['encryption_tests'].append({
                    'test': 'Password Collision Resistance',
                    'status': 'FAIL',
                    'message': 'Passwort-Hashes sind nicht kollisionsresistent'
                })
        except Exception as e:
            self.test_results['encryption_tests'].append({
                'test': 'Password Collision Resistance',
                'status': 'ERROR',
                'message': f'Exception: {str(e)}'
            })
    
    # === BRUTE FORCE PROTECTION TESTS ===
    
    def test_brute_force_protection(self):
        """Test 10: Brute Force Protection durch Account Lockout"""
        try:
            # Falsche Passwörter 3x versuchen
            attempts = []
            for i in range(3):
                result = self.auth_manager.authenticate('admin', f'wrongpassword{i}')
                attempts.append(result)
            
            # 4. Versuch sollte Account locken
            locked_result = self.auth_manager.authenticate('admin', 'wrongpassword3')
            
            # Account sollte jetzt gesperrt sein
            # (Durch Prüfung der failed_attempts)
            admin_user = None
            for user in self.auth_manager.users.values():
                if user.username == 'admin':
                    admin_user = user
                    break
            
            if admin_user and admin_user.locked_until:
                self.test_results['attack_simulation_tests'].append({
                    'test': 'Brute Force Protection',
                    'status': 'PASS',
                    'message': 'Account Lockout nach fehlgeschlagenen Versuchen aktiviert'
                })
            else:
                self.test_results['attack_simulation_tests'].append({
                    'test': 'Brute Force Protection',
                    'status': 'FAIL',
                    'message': 'Account Lockout nicht aktiviert'
                })
        except Exception as e:
            self.test_results['attack_simulation_tests'].append({
                'test': 'Brute Force Protection',
                'status': 'ERROR',
                'message': f'Exception: {str(e)}'
            })
    
    def test_sequential_brute_force_attempt(self):
        """Test 11: Sequenzielle Brute Force Angriffe"""
        try:
            # Viele schnelle Angriffe simulieren
            start_time = time.time()
            attack_results = []
            
            for i in range(10):
                result = self.auth_manager.authenticate('admin', f'password{i}')
                attack_results.append(result)
                time.sleep(0.1)  # Kurze Pausen zwischen Versuchen
            
            end_time = time.time()
            
            # Prüfe ob Account gesperrt wurde
            admin_user = None
            for user in self.auth_manager.users.values():
                if user.username == 'admin':
                    admin_user = user
                    break
            
            if admin_user and admin_user.locked_until:
                self.test_results['attack_simulation_tests'].append({
                    'test': 'Sequential Brute Force',
                    'status': 'PASS',
                    'message': 'Sequenzielle Brute Force Angriffe erfolgreich abgewehrt'
                })
            else:
                self.test_results['attack_simulation_tests'].append({
                    'test': 'Sequential Brute Force',
                    'status': 'FAIL',
                    'message': 'Sequenzielle Brute Force Angriffe nicht abgewehrt'
                })
        except Exception as e:
            self.test_results['attack_simulation_tests'].append({
                'test': 'Sequential Brute Force',
                'status': 'ERROR',
                'message': f'Exception: {str(e)}'
            })
    
    # === AUTHORIZATION TESTS ===
    
    def test_role_based_permissions(self):
        """Test 12: Rollenbasierte Berechtigungen"""
        try:
            # Admin-Permissions testen
            user_info = self.auth_manager.authenticate('admin', 'admin123')
            if user_info:
                session_created = self.session_manager.create_session(
                    user_info['user_id'],
                    user_info['username'],
                    user_info['role'],
                    user_info['permissions']
                )
                
                if session_created:
                    # Permissions testen
                    can_read = self.session_manager.has_permission('read')
                    can_write = self.session_manager.has_permission('write')
                    can_delete = self.session_manager.has_permission('delete')
                    can_user_mgmt = self.session_manager.has_permission('user_management')
                    
                    if can_read and can_write and can_delete and can_user_mgmt:
                        self.test_results['authorization_tests'].append({
                            'test': 'Admin Role Permissions',
                            'status': 'PASS',
                            'message': 'Admin-Berechtigungen korrekt zugewiesen'
                        })
                    else:
                        self.test_results['authorization_tests'].append({
                            'test': 'Admin Role Permissions',
                            'status': 'FAIL',
                            'message': 'Admin-Berechtigungen unvollständig'
                        })
        except Exception as e:
            self.test_results['authorization_tests'].append({
                'test': 'Admin Role Permissions',
                'status': 'ERROR',
                'message': f'Exception: {str(e)}'
            })
    
    def test_privilege_escalation_protection(self):
        """Test 13: Schutz vor Privilegien-Eskalation"""
        try:
            # Neuen Benutzer mit niedrigen Privilegien erstellen
            created = self.auth_manager.create_user(
                'testuser', 
                'testpass123', 
                'readonly', 
                ['read']
            )
            
            if created:
                # Als normaler Benutzer anmelden
                user_info = self.auth_manager.authenticate('testuser', 'testpass123')
                if user_info:
                    session_created = self.session_manager.create_session(
                        user_info['user_id'],
                        user_info['username'],
                        user_info['role'],
                        user_info['permissions']
                    )
                    
                    # Höhere Privilegien versuchen zu erlangen
                    can_write = self.session_manager.has_permission('write')
                    can_delete = self.session_manager.has_permission('delete')
                    can_user_mgmt = self.session_manager.has_permission('user_management')
                    
                    if not can_write and not can_delete and not can_user_mgmt:
                        self.test_results['authorization_tests'].append({
                            'test': 'Privilege Escalation Protection',
                            'status': 'PASS',
                            'message': 'Privilegien-Eskalation verhindert'
                        })
                    else:
                        self.test_results['authorization_tests'].append({
                            'test': 'Privilege Escalation Protection',
                            'status': 'FAIL',
                            'message': 'Privilegien-Eskalation möglich'
                        })
        except Exception as e:
            self.test_results['authorization_tests'].append({
                'test': 'Privilege Escalation Protection',
                'status': 'ERROR',
                'message': f'Exception: {str(e)}'
            })
    
    # === SECURITY VULNERABILITY TESTS ===
    
    def test_default_password_vulnerability(self):
        """Test 14: Schwache Standard-Passwörter"""
        try:
            # Standard-Admin Passwort prüfen
            admin_user = None
            for user in self.auth_manager.users.values():
                if user.username == 'admin':
                    admin_user = user
                    break
            
            if admin_user:
                # Passwort-Stärke prüfen
                default_password = 'admin123'
                is_weak = bcrypt.checkpw(default_password.encode('utf-8'), 
                                       admin_user.password_hash.encode('utf-8'))
                
                if is_weak:
                    self.test_results['security_vulnerabilities'].append({
                        'vulnerability': 'Weak Default Password',
                        'severity': 'HOCH',
                        'description': 'Standard-Admin verwendet schwaches Passwort "admin123"',
                        'impact': 'Kann zu unbefugtem Systemzugriff führen'
                    })
                else:
                    self.test_results['security_vulnerabilities'].append({
                        'vulnerability': 'Weak Default Password',
                        'severity': 'KEINE',
                        'description': 'Standard-Admin verwendet sicheres Passwort'
                    })
        except Exception as e:
            self.test_results['security_vulnerabilities'].append({
                'vulnerability': 'Weak Default Password',
                'severity': 'FEHLER',
                'description': f'Konnte nicht geprüft werden: {str(e)}'
            })
    
    def test_session_persistence_security(self):
        """Test 15: Session-Persistenz und Sicherheit"""
        try:
            # Session erstellen und Persistenz prüfen
            user_info = self.auth_manager.authenticate('admin', 'admin123')
            if user_info:
                self.session_manager.create_session(
                    user_info['user_id'],
                    user_info['username'],
                    user_info['role'],
                    user_info['permissions']
                )
                
                # Session-Datei prüfen
                if self.session_manager.session_file.exists():
                    with open(self.session_manager.session_file, 'r') as f:
                        session_data = json.load(f)
                    
                    # Session-ID vorhanden?
                    has_session_id = 'session_id' in session_data
                    
                    if has_session_id:
                        self.test_results['session_tests'].append({
                            'test': 'Session Security',
                            'status': 'PASS',
                            'message': 'Session mit eindeutiger ID gesichert'
                        })
                    else:
                        self.test_results['security_vulnerabilities'].append({
                            'vulnerability': 'Insecure Session ID',
                            'severity': 'MITTEL',
                            'description': 'Session-ID fehlt oder ist unsicher',
                            'impact': 'Session Hijacking möglich'
                        })
        except Exception as e:
            self.test_results['session_tests'].append({
                'test': 'Session Security',
                'status': 'ERROR',
                'message': f'Exception: {str(e)}'
            })
    
    def test_user_enumeration_protection(self):
        """Test 16: Schutz vor User Enumeration"""
        try:
            # Unterschiedliche Fehlermeldungen für falsche User/Pass
            nonexistent_result = self.auth_manager.authenticate('nonexistentuser', 'anypassword')
            wrongpass_result = self.auth_manager.authenticate('admin', 'wrongpassword')
            
            # Beide sollten None zurückgeben (gleiche Fehlermeldung)
            if nonexistent_result is None and wrongpass_result is None:
                self.test_results['security_vulnerabilities'].append({
                    'vulnerability': 'User Enumeration',
                    'severity': 'KEINE',
                    'description': 'Keine User Enumeration möglich - gleiche Fehlermeldungen'
                })
            else:
                self.test_results['security_vulnerabilities'].append({
                    'vulnerability': 'User Enumeration',
                    'severity': 'NIEDRIG',
                    'description': 'Mögliche User Enumeration basierend auf unterschiedlichen Reaktionen',
                    'impact': 'Angreifer kann existierende Benutzer identifizieren'
                })
        except Exception as e:
            self.test_results['security_vulnerabilities'].append({
                'vulnerability': 'User Enumeration',
                'severity': 'FEHLER',
                'description': f'Konnte nicht geprüft werden: {str(e)}'
            })


def run_security_tests():
    """Führt alle Sicherheitstests aus und erstellt Bericht"""
    print("🔒 Starte umfassende Sicherheitsprüfung des Authentication-Systems...")
    print("=" * 80)
    
    # Test-Suite erstellen und ausführen
    suite = unittest.TestLoader().loadTestsFromTestCase(SecurityTestSuite)
    runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w'))
    result = runner.run(suite)
    
    # Ergebnisse sammeln
    test_instance = SecurityTestSuite()
    test_instance.setUpClass()
    
    return test_instance.test_results


if __name__ == '__main__':
    results = run_security_tests()
    
    # Ergebnisse ausgeben
    for category, tests in results.items():
        if tests:  # Nur Kategorien mit Tests anzeigen
            print(f"\n📋 {category.upper()}:")
            print("-" * 50)
            for test in tests:
                status = test.get('status', test.get('severity', 'UNBEKANNT'))
                print(f"  {status}: {test['test'] or test.get('vulnerability', 'Unbekannt')}")
                print(f"    {test['message']}")
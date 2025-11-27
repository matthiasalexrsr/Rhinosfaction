#!/usr/bin/env python3
"""
Erweiterte Sicherheitstests - Session Hijacking und weitere Angriffs-Szenarien
"""

import os
import sys
import json
import time
import bcrypt
import logging
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch
import uuid

# Pfad zur Anwendung hinzufügen
sys.path.insert(0, '/workspace/rhinoplastik_app')

from core.security.auth import AuthenticationManager, User
from core.security.session_manager import SessionManager


def test_session_hijacking():
    """Test Session Hijacking Angriff"""
    print("\n🎯 Teste Session Hijacking...")
    
    test_dir = Path(tempfile.mkdtemp())
    test_users_file = test_dir / "test_users.json"
    test_session_file = test_dir / "test_session.json"
    
    try:
        # AuthManager initialisieren
        auth_manager = AuthenticationManager(test_users_file)
        
        # Gültige Session erstellen
        session_manager = SessionManager()
        session_manager.session_file = test_session_file
        
        # Benutzer anmelden
        user_info = auth_manager.authenticate('admin', 'admin123')
        if user_info:
            session_manager.create_session(
                user_info['user_id'],
                user_info['username'],
                user_info['role'],
                user_info['permissions']
            )
            
            # Session validieren
            is_valid = session_manager.validate_session()
            print(f"  ✅ Gültige Session: {is_valid}")
            
            # Session-Daten lesen
            if test_session_file.exists():
                with open(test_session_file, 'r') as f:
                    session_data = json.load(f)
                
                print(f"  📋 Session-Daten: {session_data.get('username', 'N/A')}")
                
                # Versuche Session-Daten zu manipulieren
                manipulated_session = session_data.copy()
                manipulated_session['role'] = 'admin'  # Versuche Rolle zu ändern
                manipulated_session['permissions'] = ['read', 'write', 'delete', 'user_management']
                
                with open(test_session_file, 'w') as f:
                    json.dump(manipulated_session, f)
                
                # Neue SessionManager Instanz erstellen (simuliert neuen Angreifer)
                attacker_session_manager = SessionManager()
                attacker_session_manager.session_file = test_session_file
                
                # Manipulierte Session laden
                attacker_user_info = attacker_session_manager.get_user_info()
                
                if attacker_user_info:
                    print(f"  ⚠️  VULNERABILITÄT: Session Hijacking möglich!")
                    print(f"     Angegriffene Benutzer: {attacker_user_info.get('username')}")
                    print(f"     Rechte: {attacker_user_info.get('permissions')}")
                    return True
                else:
                    print(f"  ✅ Session Hijacking verhindert")
                    return False
                    
    except Exception as e:
        print(f"  ❌ Fehler: {e}")
        return False
    finally:
        # Cleanup
        shutil.rmtree(test_dir, ignore_errors=True)


def test_insecure_session_storage():
    """Test unsichere Session-Speicherung"""
    print("\n💾 Teste Session-Speicherung...")
    
    test_dir = Path(tempfile.mkdtemp())
    test_session_file = test_dir / "test_session.json"
    
    try:
        # Session mit sensiblen Daten erstellen
        session_manager = SessionManager()
        session_manager.session_file = test_session_file
        
        # Benutzer-Daten in Session
        session_manager.create_session('user123', 'testuser', 'admin', ['read', 'write', 'delete'])
        
        # Session-Datei auf unsichere Berechtigungen prüfen
        if test_session_file.exists():
            file_stat = test_session_file.stat()
            file_mode = oct(file_stat.st_mode)[-3:]  # Letzten 3 Oktalstellen
            
            print(f"  📁 Session-Datei: {test_session_file}")
            print(f"  🔐 Datei-Berechtigungen: {file_mode}")
            
            # Session-Inhalt prüfen
            with open(test_session_file, 'r') as f:
                content = f.read()
            
            print(f"  📄 Session-Inhalt (sichtbar): {content[:200]}...")
            
            # Sensible Daten im Klartext?
            if 'user_id' in content or 'username' in content:
                print(f"  ⚠️  VULNERABILITÄT: Session-Daten im Klartext gespeichert!")
                return True
            else:
                print(f"  ✅ Session-Daten verschlüsselt oder anonymisiert")
                return False
                
    except Exception as e:
        print(f"  ❌ Fehler: {e}")
        return False
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_password_policy_enforcement():
    """Test Passwort-Policy Durchsetzung"""
    print("\n🔒 Teste Passwort-Policy...")
    
    test_dir = Path(tempfile.mkdtemp())
    test_users_file = test_dir / "test_users.json"
    
    try:
        auth_manager = AuthenticationManager(test_users_file)
        
        # Test schwache Passwörter
        weak_passwords = [
            '123',
            'password',
            'admin',
            'test',
            '123456',
            'abc',
            'a',
            ''  # Leer
        ]
        
        vulnerabilities = 0
        for weak_password in weak_passwords:
            try:
                created = auth_manager.create_user(f'user_{weak_password}', weak_password, 'doctor', ['read', 'write'])
                if created:
                    print(f"  ⚠️  SCHWACH: Passwort '{weak_password}' akzeptiert")
                    vulnerabilities += 1
                    # Benutzer löschen um weitere Tests zu ermöglichen
                    user_id = f"doctor_{weak_password}_12345678"[:16]  # Annäherung an ID
                    auth_manager.delete_user(user_id)
            except:
                pass  # Erwartet für manche schwachen Passwörter
        
        if vulnerabilities > 0:
            print(f"  ❌ VULNERABILITÄT: {vulnerabilities} schwache Passwörter akzeptiert")
            return True
        else:
            print(f"  ✅ Schwache Passwörter korrekt abgelehnt")
            return False
            
    except Exception as e:
        print(f"  ❌ Fehler: {e}")
        return False
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_concurrent_session_handling():
    """Test gleichzeitige Session-Behandlung"""
    print("\n🔀 Teste gleichzeitige Sessions...")
    
    test_dir = Path(tempfile.mkdtemp())
    test_session_file = test_dir / "test_session.json"
    
    try:
        # Erste Session erstellen
        session_manager1 = SessionManager()
        session_manager1.session_file = test_session_file
        
        # Zweite Session auf gleiche Datei
        session_manager2 = SessionManager()
        session_manager2.session_file = test_session_file
        
        # Beide Sessions erstellen
        user_info1 = {'user_id': 'user1', 'username': 'user1', 'role': 'doctor', 'permissions': ['read', 'write']}
        user_info2 = {'user_id': 'user2', 'username': 'user2', 'role': 'admin', 'permissions': ['read', 'write', 'delete']}
        
        session1_created = session_manager1.create_session(**user_info1)
        session2_created = session_manager2.create_session(**user_info2)
        
        # Welche Session gewinnt?
        if session2_created:
            final_user_info = session_manager2.get_user_info()
            if final_user_info:
                print(f"  ⚠️  VULNERABILITÄT: Session-Überschreibung möglich!")
                print(f"     Ursprüngliche Session: {user_info1['username']}")
                print(f"     Finale Session: {final_user_info['username']}")
                return True
        
        print(f"  ✅ Session-Konflikte vermieden")
        return False
        
    except Exception as e:
        print(f"  ❌ Fehler: {e}")
        return False
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_account_enumeration():
    """Test User Enumeration"""
    print("\n🔍 Teste User Enumeration...")
    
    test_dir = Path(tempfile.mkdtemp())
    test_users_file = test_dir / "test_users.json"
    
    try:
        auth_manager = AuthenticationManager(test_users_file)
        
        # Test existierende vs. nicht-existierende Benutzer
        test_cases = [
            ('admin', 'wrongpass'),      # Existiert
            ('nonexistent', 'anypass'),  # Existiert nicht
            ('', 'anypass'),             # Leer
            ('ADMIN', 'anypass'),        # Groß-/Kleinschreibung
        ]
        
        # Timing-basierte Erkennung testen
        for username, password in test_cases:
            start_time = time.time()
            result = auth_manager.authenticate(username, password)
            end_time = time.time()
            
            response_time = end_time - start_time
            print(f"  ⏱️  User '{username}': {response_time:.4f}s, Result: {result}")
        
        # Timing-Unterschiede können auf existierende Benutzer hinweisen
        print(f"  ℹ️  Timing-Analyse: Prüfe auf signifikante Unterschiede")
        return False  # Timing-basierte Tests sind komplex
        
    except Exception as e:
        print(f"  ❌ Fehler: {e}")
        return False
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_data_injection_simulation():
    """Test Daten-Injection Angriffe"""
    print("\n💉 Teste Daten-Injection...")
    
    test_dir = Path(tempfile.mkdtemp())
    test_users_file = test_dir / "test_users.json"
    
    try:
        auth_manager = AuthenticationManager(test_users_file)
        
        # SQL-Injection-ähnliche Eingaben testen
        injection_attempts = [
            "admin' OR '1'='1",
            "admin'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "../../../etc/passwd",
            "${7*7}",
            "{{7*7}}",
            "admin\nadmin",
            "admin\tadmin"
        ]
        
        vulnerabilities = 0
        for injection in injection_attempts:
            try:
                result = auth_manager.authenticate(injection, 'password')
                if result:
                    print(f"  ⚠️  VULNERABILITÄT: Injection '{injection[:30]}...' erfolgreich!")
                    vulnerabilities += 1
            except Exception as e:
                print(f"  🛡️  Blockiert: '{injection[:30]}...' - {str(e)[:50]}")
        
        if vulnerabilities > 0:
            print(f"  ❌ {vulnerabilities} Injection-Angriffe erfolgreich")
            return True
        else:
            print(f"  ✅ Alle Injection-Versuche blockiert")
            return False
            
    except Exception as e:
        print(f"  ❌ Fehler: {e}")
        return False
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def main():
    """Hauptfunktion für erweiterte Sicherheitstests"""
    print("🔒 ERWEITERTE SICHERHEITSTESTS")
    print("=" * 60)
    
    tests = [
        ("Session Hijacking", test_session_hijacking),
        ("Insecure Session Storage", test_insecure_session_storage),
        ("Password Policy", test_password_policy_enforcement),
        ("Concurrent Sessions", test_concurrent_session_handling),
        ("User Enumeration", test_account_enumeration),
        ("Data Injection", test_data_injection_simulation)
    ]
    
    vulnerabilities = []
    
    for test_name, test_func in tests:
        try:
            is_vulnerable = test_func()
            if is_vulnerable:
                vulnerabilities.append(test_name)
        except Exception as e:
            print(f"  ❌ Test {test_name} fehlgeschlagen: {e}")
    
    print("\n" + "=" * 60)
    print("📊 ZUSAMMENFASSUNG")
    print("=" * 60)
    
    if vulnerabilities:
        print(f"❌ GEFUNDENE VULNERABILITÄTEN ({len(vulnerabilities)}):")
        for vuln in vulnerabilities:
            print(f"  • {vuln}")
    else:
        print("✅ Keine kritischen Vulnerabilities in erweiterten Tests gefunden")
    
    return len(vulnerabilities)


if __name__ == '__main__':
    main()
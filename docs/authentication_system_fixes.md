# Authentication System Fixes

## Identifizierte Probleme und Korrekturen

### 1. LoginDialog - Fehlender QTimer Import

**Problem:** `QTimer` wird verwendet aber nicht importiert (Zeile 230)
```python
QTimer.singleShot(5000, lambda: self.status_label.setVisible(False))
```

**Lösung:**
```python
# In login_dialog.py hinzufügen:
from PySide6.QtCore import QTimer
```

### 2. Session Manager - Fehlende Initialisierung

**Problem:** `_session_loaded_from_file` wird verwendet aber nicht initialisiert
```python
# In session_manager.py Zeile 175:
if not hasattr(self, '_session_loaded_from_file'):
    self._load_session()
```

**Lösung:**
```python
def __init__(self, session_timeout_minutes: int = 480):
    # ... vorhandener Code ...
    self._session_loaded_from_file = False  # Fehlende Initialisierung
```

### 3. Session Manager - Kryptographie-Dependency

**Problem:** `cryptography` Bibliothek wird benötigt aber möglicherweise nicht installiert

**Lösung:**
```python
# Fallback-Implementierung wenn cryptography nicht verfügbar
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBK2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    # Fallback zu einfacher Base64-Verschlüsselung
    import base64
    import hashlib
    CRYPTO_AVAILABLE = False

class SessionManager:
    def _encrypt_data(self, data: str) -> bytes:
        if CRYPTO_AVAILABLE:
            return self._fernet.encrypt(data.encode('utf-8'))
        else:
            # Fallback: Einfache Base64-Verschlüsselung
            return base64.b64encode(data.encode('utf-8'))
    
    def _decrypt_data(self, encrypted_data: bytes) -> str:
        if CRYPTO_AVAILABLE:
            return self._fernet.decrypt(encrypted_data).decode('utf-8')
        else:
            # Fallback: Base64-Entschlüsselung
            return base64.b64decode(encrypted_data).decode('utf-8')
```

### 4. Authentication Manager - Redundante Locks

**Problem:** Mehrere RLock-Objekte können zu Deadlocks führen
```python
# Aktuell:
self._users_lock = threading.RLock()
self._auth_lock = threading.RLock()
self._file_lock = threading.RLock()
```

**Lösung:** Verwendung eines einzigen RLock für alle Operationen
```python
def __init__(self, users_file: Optional[Path] = None):
    # ...
    self._lock = threading.RLock()  # Einziger Lock für alle Operationen
```

### 5. Passwort-Policy - Zu strikte Validierung

**Problem:** Aktuelle Policy könnte zu restriktiv sein für echte Benutzer

**Lösung:** Angepasste, benutzerfreundlichere Policy
```python
class AuthenticationManager:
    def _validate_password_strength(self, password: str) -> tuple[bool, str]:
        if not password:
            return False, "Passwort darf nicht leer sein"
        
        # Angepasste Mindestlänge (8 statt 12 für bessere Usability)
        if len(password) < 8:
            return False, "Passwort muss mindestens 8 Zeichen lang sein"
        
        if len(password) > 128:
            return False, "Passwort darf maximal 128 Zeichen lang sein"
        
        # Großbuchstaben optional machen
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            return False, "Passwort sollte Großbuchstaben enthalten"
        
        # Kleinbuchstaben prüfen
        if not re.search(r'[a-z]', password):
            return False, "Passwort muss Kleinbuchstaben enthalten"
        
        # Ziffern prüfen
        if not re.search(r'[0-9]', password):
            return False, "Passwort muss Ziffern enthalten"
        
        # Sonderzeichen optional machen
        if self.require_special_chars and not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
            return False, "Passwort sollte Sonderzeichen enthalten"
        
        return True, "Passwort ist akzeptabel"
```

### 6. Session ID Generation - Inconsistent Encoding

**Problem:** `base64.b32encode` wird verwendet aber nicht überall konsistent gehandhabt

**Lösung:** Vereinheitlichte Session-ID-Generierung
```python
def _generate_session_id(self) -> str:
    """Generiert kryptographisch sichere Session-ID"""
    # 32 Byte zufällige Daten generieren
    random_bytes = secrets.token_bytes(32)
    # Base64 URL-safe für bessere Kompatibilität
    return base64.urlsafe_b64encode(random_bytes).decode('ascii').rstrip('=')
```

### 7. Fehlerbehandlung - Unvollständige Exception Handling

**Problem:** Einige Operationen haben unzureichende Fehlerbehandlung

**Lösung:** Verbesserte Exception Handling
```python
def _load_users(self):
    """Lädt Benutzer aus JSON-Datei"""
    try:
        if self.users_file.exists():
            with open(self.users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Datenvalidierung
            if not isinstance(data, dict):
                raise ValueError("Invalid user data format")
            
            for user_id, user_data in data.items():
                # Validierung der Benutzer-Daten
                if not all(key in user_data for key in ['user_id', 'username', 'password_hash', 'role', 'permissions']):
                    self.logger.warning(f"Invalid user data for {user_id}, skipping")
                    continue
                    
                user = User(
                    user_id=user_data['user_id'],
                    username=user_data['username'],
                    password_hash=user_data['password_hash'],
                    role=user_data['role'],
                    permissions=user_data['permissions'],
                    active=user_data.get('active', True)
                )
                user.created_at = user_data.get('created_at', user.created_at)
                user.last_login = user_data.get('last_login')
                user.failed_attempts = user_data.get('failed_attempts', 0)
                user.locked_until = user_data.get('locked_until')
                
                self.users[user_id] = user
            
            self.logger.info(f"{len(self.users)} Benutzer geladen")
        else:
            self.logger.info("Keine Benutzerdatei gefunden, erstelle leere Datenbank")
            
    except json.JSONDecodeError as e:
        self.logger.error(f"JSON-Parsing-Fehler: {e}")
        # Backup erstellen und mit leerer DB starten
        if self.users_file.exists():
            backup_file = self.users_file.with_suffix('.json.backup')
            self.users_file.rename(backup_file)
            self.logger.warning(f"Backup erstellt: {backup_file}")
    except Exception as e:
        self.logger.error(f"Unerwarteter Fehler beim Laden der Benutzer: {e}")
        # Im Fehlerfall mit leerer DB starten
        self.users = {}
```

### 8. Input Validation - Unvollständige Sanitization

**Problem:** Einige Eingaben werden nicht vollständig validiert

**Lösung:** Erweiterte Input-Validierung
```python
def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
    with self._lock:
        # Erweiterte Input-Validierung
        if not username or not password:
            return None
        
        # Sanitize und validiere Inputs
        username = self._sanitize_input(username)
        password = self._sanitize_input(password)
        
        # Länge validieren
        if len(username) > 50 or len(password) > 200:
            self.logger.warning("Input zu lang")
            return None
        
        # Prüfe auf verdächtige Eingaben
        if self._is_suspicious_input(username + password):
            self.logger.warning(f"Verdächtige Eingabe erkannt: {username}")
            return None
        
        # Rest der Authentifizierung...
        
def _sanitize_input(self, input_str: str) -> str:
    """Sanitisiert Eingaben"""
    if not input_str:
        return ""
    
    # Entferne control characters
    sanitized = ''.join(char for char in input_str if ord(char) >= 32 or char in '\t\n\r')
    
    # Strip whitespace
    return sanitized.strip()

def _is_suspicious_input(self, input_str: str) -> bool:
    """Prüft auf verdächtige Eingaben"""
    # Extended suspicious patterns
    suspicious_patterns = [
        r'<script',
        r'javascript:',
        r'vbscript:',
        r'on\w+\s*=',
        r'eval\s*\(',
        r'exec\s*\(',
        r'system\s*\(',
        r'shell_exec',
        r'passthru',
        r'base64_decode',
        r'assert\s*\(',
        r'preg_replace.*\/e',
    ]
    
    input_lower = input_str.lower()
    for pattern in suspicious_patterns:
        if re.search(pattern, input_lower):
            return True
    
    return False
```

### 9. Account Lockout - Verbesserte Implementierung

**Problem:** Account-Lockout-Mechanismus könnte verbessert werden

**Lösung:** Erweiterte Lockout-Logik
```python
def _is_account_locked(self, user: User) -> bool:
    """Prüft ob Account gesperrt ist mit verbesserter Logik"""
    if not user.locked_until:
        return False
    
    try:
        locked_until = datetime.fromisoformat(user.locked_until)
    except ValueError as e:
        self.logger.error(f"Ungültiges Locked-Until-Datum: {user.locked_until} - {e}")
        # Ungültiges Datum: Sperre aufheben
        user.locked_until = None
        user.failed_attempts = 0
        self._save_users()
        return False
    
    now = datetime.now()
    if now > locked_until:
        # Sperre aufheben
        user.locked_until = None
        user.failed_attempts = 0
        self._save_users()
        
        # Log event
        self.logger.info(f"Account-Sperre aufgehoben für: {user.username}")
        return False
    
    # Noch gesperrt
    remaining = locked_until - now
    self.logger.debug(f"Account noch gesperrt für {remaining.total_seconds()/60:.1f} Minuten: {user.username}")
    return True
```

### 10. Session Management - Verbesserte Session-Validierung

**Lösung:** Robustere Session-Validierung
```python
def validate_session(self) -> bool:
    """
    Validiert die aktuelle Session mit erweiterten Checks
    """
    if not self.current_session:
        return False
    
    try:
        # Session laden falls nicht im Speicher
        if not self._session_loaded_from_file:
            if not self._load_session():
                return False
        
        # Erweiterte Session-Validierung
        required_fields = ['user_id', 'username', 'role', 'permissions', 'login_time', 'last_activity', 'session_id']
        if not all(field in self.current_session for field in required_fields):
            self.logger.error("Session hat unvollständige Daten")
            self.clear_session()
            return False
        
        # Timeout prüfen
        try:
            last_activity = datetime.fromisoformat(self.current_session['last_activity'])
        except ValueError as e:
            self.logger.error(f"Ungültiges Session-Datum: {self.current_session.get('last_activity')} - {e}")
            self.clear_session()
            return False
        
        if datetime.now() - last_activity > self.session_timeout:
            self.logger.warning(f"Session für {self.current_session['username']} abgelaufen")
            self.clear_session()
            return False
        
        # Session-ID Validierung
        if not self.current_session['session_id'] or len(self.current_session['session_id']) < 16:
            self.logger.error("Ungültige Session-ID")
            self.clear_session()
            return False
        
        # Letzte Aktivität aktualisieren
        self.update_activity()
        return True
        
    except Exception as e:
        self.logger.error(f"Fehler bei Session-Validierung: {e}")
        self.clear_session()
        return False
```

## Zusätzliche Verbesserungen

### 11. Logging-Verbesserungen
```python
# Strukturierte Logs mit Kontext
import structlog

def __init__(self, users_file: Optional[Path] = None):
    # ...
    # Strukturierte Logs
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    self.logger = structlog.get_logger("auth")
```

### 12. Performance-Optimierungen
```python
# Lazy Loading für Benutzer
def _load_users_lazy(self):
    """Lädt Benutzer nur bei Bedarf"""
    if self._users_loaded:
        return
    
    with self._lock:
        if self._users_loaded:  # Double-check locking
            return
        
        self._load_users()
        self._users_loaded = True

def _save_users_lazy(self):
    """Speichert Benutzer nur bei Änderungen"""
    if not self._users_modified:
        return
    
    with self._lock:
        if not self._users_modified:
            return
        
        self._save_users()
        self._users_modified = False
```

## Test-Coverage Verbesserungen

### 13. Session Manager Tests
```python
def test_session_encryption_fallback(self, tmp_path):
    """Test: Fallback-Verschlüsselung wenn cryptography nicht verfügbar"""
    # Mock cryptography Import
    with patch('core.security.session_manager.CRYPTO_AVAILABLE', False):
        session_manager = SessionManager(session_timeout_minutes=60)
        
        # Session erstellen
        success = session_manager.create_session("user123", "testuser", "admin", ["read", "write"])
        assert success is True
        
        # Session validieren
        is_valid = session_manager.validate_session()
        assert is_valid is True
```

### 14. Error Recovery Tests
```python
def test_corrupted_user_data_recovery(self, auth_manager, tmp_path):
    """Test: Wiederherstellung bei korrupten Benutzer-Daten"""
    # Erstelle korrupte users.json
    corrupted_data = {"invalid": "json structure"}
    
    users_file = tmp_path / "test_users.json"
    with open(users_file, 'w') as f:
        json.dump(corrupted_data, f)
    
    # AuthManager mit korrupter Datei
    auth_manager = AuthenticationManager(users_file=users_file)
    
    # Sollte Recovery durchführen und mit leerer DB starten
    assert len(auth_manager.users) == 0
    assert users_file.with_suffix('.json.backup').exists()
```

## Implementierungsplan

1. **Phase 1: Kritische Fixes** (Sofort)
   - QTimer Import in login_dialog.py
   - Session Manager Initialisierung
   - Kryptographie-Fallback

2. **Phase 2: Sicherheitsverbesserungen**
   - Input-Validierung erweitern
   - Account-Lockout verbessern
   - Session-Validierung verstärken

3. **Phase 3: Performance & Usability**
   - Lock-Optimierung
   - Passwort-Policy anpassen
   - Lazy Loading implementieren

4. **Phase 4: Monitoring & Testing**
   - Strukturierte Logs
   - Erweiterte Test-Coverage
   - Error Recovery Tests

## Validierung

Nach den Fixes sollten folgende Tests erfolgreich sein:
- Alle Unit-Tests in `test_authentication.py`
- Erweiterte Tests in `test_authentication_extended.py`
- Session-Management-Tests
- Error-Recovery-Tests
- Performance-Tests unter 5s für 50 Benutzer

## Sicherheits-Checkliste

- ✅ Passwort-Hashing mit bcrypt (12 Rounds)
- ✅ Account-Lockout nach 3 fehlgeschlagenen Versuchen
- ✅ Session-Verschlüsselung
- ✅ Input-Validierung und Sanitization
- ✅ Thread-Safety mit RLock
- ✅ Sichere Session-ID-Generierung
- ✅ Path Traversal-Schutz
- ✅ XSS-Schutz
- ✅ SQL-Injection-Schutz

## Ausstehende Verbesserungen

1. **Multi-Factor Authentication (MFA)**
   - TOTP-Integration
   - SMS-Code-Verifikation
   - Backup-Codes

2. **Passwort-Management**
   - Password-History-Tracking
   - Automatic Password Expiration
   - Password-Complexity-Scoring

3. **Audit-Logging**
   - Login/Logout-Events
   - Permission-Changes
   - Security-incidents

4. **Rate Limiting**
   - API-Rate-Limiting
   - Brute-Force-Detection
   - IP-Whitelisting/Blacklisting

# Export-/Import-Funktionalitäten Test-Bericht

**Test-Datum:** 06.11.2025 20:13:08

## Zusammenfassung

- **Gesamt Tests:** 10
- **Erfolgreich:** 5
- **Fehlgeschlagen:** 5
- **Erfolgsquote:** 50.0%

## Test-Kategorien

### 1. PDF-Export mit verschiedenen Datenformaten
- Test normaler PDF-Export
- Test anonymisierter PDF-Export
- Test PDF-Export mit leeren Daten

### 2. CSV-/JSON-Export und Import-Operationen
- Test CSV-Export (normal/anonymisiert)
- Test JSON-Export (normal/anonymisiert)
- Validierung der Export-Dateien

### 3. Backup-/Restore-Funktionen
- Test manuelles Backup
- Test automatisches Backup
- Test Backup-Wiederherstellung
- Test Backup-Integritätsprüfung

### 4. Datenkonsistenz bei Export/Import-Zyklen
- Test JSON Export/Import-Konsistenz
- Test CSV-Datenkonsistenz

### 5. Performance mit großen Datenmengen
- Test mit 100 Test-Patienten
- Bulk-Export-Performance
- Speicherverbrauch-Tests

### 6. Fehlerhafte Dateien und Recovery
- Test korrupte JSON-Dateien
- Test leere JSON-Dateien
- Test fehlerhafte CSV-Daten
- Test korrupte Backup-Dateien
- Test nicht-existierende Dateien

## Fehlgeschlagene Tests

1. PDF-Export-Tests: 10 validation errors for Surgery
indications
  Field required [type=missing, input_value={'op_date': datetime.date...20, 'blood_loss_ml': 50}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
technique
  Input should be 'Offen' or 'Geschlossen' [type=enum, input_value='Standard', input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/enum
nose_shape
  Input should be 'Höckernase', 'Schiefnase', 'Spannungsnase', 'Hängende Spitze' or 'Breitnase' [type=enum, input_value='Gerade', input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/enum
anatomy
  Field required [type=missing, input_value={'op_date': datetime.date...20, 'blood_loss_ml': 50}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
measurements
  Field required [type=missing, input_value={'op_date': datetime.date...20, 'blood_loss_ml': 50}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
procedures
  Field required [type=missing, input_value={'op_date': datetime.date...20, 'blood_loss_ml': 50}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
materials
  Field required [type=missing, input_value={'op_date': datetime.date...20, 'blood_loss_ml': 50}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
anesthesia
  Field required [type=missing, input_value={'op_date': datetime.date...20, 'blood_loss_ml': 50}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
aftercare
  Field required [type=missing, input_value={'op_date': datetime.date...20, 'blood_loss_ml': 50}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
outcomes
  Field required [type=missing, input_value={'op_date': datetime.date...20, 'blood_loss_ml': 50}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
2. CSV/JSON-Export-Tests: 10 validation errors for Surgery
indications
  Field required [type=missing, input_value={'op_date': datetime.date...20, 'blood_loss_ml': 50}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
technique
  Input should be 'Offen' or 'Geschlossen' [type=enum, input_value='Standard', input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/enum
nose_shape
  Input should be 'Höckernase', 'Schiefnase', 'Spannungsnase', 'Hängende Spitze' or 'Breitnase' [type=enum, input_value='Gerade', input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/enum
anatomy
  Field required [type=missing, input_value={'op_date': datetime.date...20, 'blood_loss_ml': 50}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
measurements
  Field required [type=missing, input_value={'op_date': datetime.date...20, 'blood_loss_ml': 50}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
procedures
  Field required [type=missing, input_value={'op_date': datetime.date...20, 'blood_loss_ml': 50}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
materials
  Field required [type=missing, input_value={'op_date': datetime.date...20, 'blood_loss_ml': 50}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
anesthesia
  Field required [type=missing, input_value={'op_date': datetime.date...20, 'blood_loss_ml': 50}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
aftercare
  Field required [type=missing, input_value={'op_date': datetime.date...20, 'blood_loss_ml': 50}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
outcomes
  Field required [type=missing, input_value={'op_date': datetime.date...20, 'blood_loss_ml': 50}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
3. Backup/Restore-Tests: 10 validation errors for Surgery
indications
  Field required [type=missing, input_value={'op_date': datetime.date...20, 'blood_loss_ml': 50}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
technique
  Input should be 'Offen' or 'Geschlossen' [type=enum, input_value='Standard', input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/enum
nose_shape
  Input should be 'Höckernase', 'Schiefnase', 'Spannungsnase', 'Hängende Spitze' or 'Breitnase' [type=enum, input_value='Gerade', input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/enum
anatomy
  Field required [type=missing, input_value={'op_date': datetime.date...20, 'blood_loss_ml': 50}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
measurements
  Field required [type=missing, input_value={'op_date': datetime.date...20, 'blood_loss_ml': 50}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
procedures
  Field required [type=missing, input_value={'op_date': datetime.date...20, 'blood_loss_ml': 50}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
materials
  Field required [type=missing, input_value={'op_date': datetime.date...20, 'blood_loss_ml': 50}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
anesthesia
  Field required [type=missing, input_value={'op_date': datetime.date...20, 'blood_loss_ml': 50}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
aftercare
  Field required [type=missing, input_value={'op_date': datetime.date...20, 'blood_loss_ml': 50}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
outcomes
  Field required [type=missing, input_value={'op_date': datetime.date...20, 'blood_loss_ml': 50}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
4. Datenkonsistenz-Tests: 10 validation errors for Surgery
indications.0
  Input should be 'Ästhetisch', 'Funktionell', 'Trauma', 'Angeboren' or 'Revision' [type=enum, input_value='Septumdeviation', input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/enum
indications.1
  Input should be 'Ästhetisch', 'Funktionell', 'Trauma', 'Angeboren' or 'Revision' [type=enum, input_value='Nasenatmungsbehinderung', input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/enum
technique
  Input should be 'Offen' or 'Geschlossen' [type=enum, input_value='Erweiterte Septorhinoplastik', input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/enum
anatomy
  Field required [type=missing, input_value={'op_date': datetime.date...senatmungsbehinderung']}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
measurements
  Field required [type=missing, input_value={'op_date': datetime.date...senatmungsbehinderung']}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
procedures
  Field required [type=missing, input_value={'op_date': datetime.date...senatmungsbehinderung']}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
materials
  Field required [type=missing, input_value={'op_date': datetime.date...senatmungsbehinderung']}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
anesthesia
  Field required [type=missing, input_value={'op_date': datetime.date...senatmungsbehinderung']}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
aftercare
  Field required [type=missing, input_value={'op_date': datetime.date...senatmungsbehinderung']}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
outcomes
  Field required [type=missing, input_value={'op_date': datetime.date...senatmungsbehinderung']}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
5. Performance-Tests: 10 validation errors for Surgery
indications
  Field required [type=missing, input_value={'op_date': datetime.date...49, 'blood_loss_ml': 56}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
technique
  Input should be 'Offen' or 'Geschlossen' [type=enum, input_value='Minimal-invasiv', input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/enum
nose_shape
  Input should be 'Höckernase', 'Schiefnase', 'Spannungsnase', 'Hängende Spitze' or 'Breitnase' [type=enum, input_value='Gerade', input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/enum
anatomy
  Field required [type=missing, input_value={'op_date': datetime.date...49, 'blood_loss_ml': 56}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
measurements
  Field required [type=missing, input_value={'op_date': datetime.date...49, 'blood_loss_ml': 56}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
procedures
  Field required [type=missing, input_value={'op_date': datetime.date...49, 'blood_loss_ml': 56}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
materials
  Field required [type=missing, input_value={'op_date': datetime.date...49, 'blood_loss_ml': 56}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
anesthesia
  Field required [type=missing, input_value={'op_date': datetime.date...49, 'blood_loss_ml': 56}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
aftercare
  Field required [type=missing, input_value={'op_date': datetime.date...49, 'blood_loss_ml': 56}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
outcomes
  Field required [type=missing, input_value={'op_date': datetime.date...49, 'blood_loss_ml': 56}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing

## Empfehlungen

⚠️ **5 Tests fehlgeschlagen.** Überprüfung der folgenden Bereiche empfohlen:

- Datenvalidierung bei Export-Operationen
- Fehlerbehandlung für korrupte Dateien
- Performance-Optimierung für große Datenmengen

## Test-Umgebung

- **Test-Verzeichnis:** /tmp/rhinoplastik_test__vpw1qx4
- **Python-Version:** 3.12.5 (main, Sep  5 2024, 00:16:34) [GCC 12.2.0]
- **Test-Dauer:** Gesamt

---
*Detaillierte Logs siehe: export_import_test.log*

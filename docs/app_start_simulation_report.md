# App-Start-Simulation Report

**Generiert am:** 2025-11-07T07:10:18.107343  
**App-Pfad:** /workspace/final_test/rhinoplastik_windows_final  
**Ausführungszeit:** 0.08 Sekunden

## Zusammenfassung

- **Gesamttests:** 8
- **Erfolgreich:** 6
- **Fehlgeschlagen:** 2
- **Erfolgsrate:** 75.0%

## Detaillierte Testergebnisse

### QApplication Start

**Status:** FAILED


**Fehler:** No module named 'PyQt5'

**Traceback:**
```
Traceback (most recent call last):
  File "/workspace/app_start_simulation.py", line 57, in test_qapplication_start
    with patch('PyQt5.QtWidgets.QApplication') as mock_qapp:
  File "/usr/local/lib/python3.12/unittest/mock.py", line 1445, in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/pkgutil.py", line 513, in resolve_name
    mod = importlib.import_module(modname)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/importlib/__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1324, in _find_and_load_unlocked
ModuleNotFoundError: No module named 'PyQt5'

```

### Module Imports

**Status:** FAILED

**Details:**
- core.asset_manager: import_error: unsupported operand type(s) for +: 'PosixPath' and 'str'
- core.audit: import_error: unsupported operand type(s) for +: 'PosixPath' and 'str'
- core.i18n: import_error: unsupported operand type(s) for +: 'PosixPath' and 'str'
- core.logging_conf: import_error: unsupported operand type(s) for +: 'PosixPath' and 'str'
- core.notifications: import_error: unsupported operand type(s) for +: 'PosixPath' and 'str'
- core.performance_optimizer: import_error: unsupported operand type(s) for +: 'PosixPath' and 'str'
- core.reports: import_error: unsupported operand type(s) for +: 'PosixPath' and 'str'
- core.search: import_error: unsupported operand type(s) for +: 'PosixPath' and 'str'
- core.theme_manager: import_error: unsupported operand type(s) for +: 'PosixPath' and 'str'
- core.ui_system_integrator: import_error: unsupported operand type(s) for +: 'PosixPath' and 'str'
- ui.main_window: import_error: unsupported operand type(s) for +: 'PosixPath' and 'str'
- ui.login_dialog: import_error: unsupported operand type(s) for +: 'PosixPath' and 'str'
- ui.patient_editor_widget: import_error: unsupported operand type(s) for +: 'PosixPath' and 'str'
- ui.patients_list_widget: import_error: unsupported operand type(s) for +: 'PosixPath' and 'str'
- ui.statistics_widget: import_error: unsupported operand type(s) for +: 'PosixPath' and 'str'
- ui.search_widget: import_error: unsupported operand type(s) for +: 'PosixPath' and 'str'
- ui.export_widget: import_error: unsupported operand type(s) for +: 'PosixPath' and 'str'
- config.app_config: import_error: unsupported operand type(s) for +: 'PosixPath' and 'str'

### Configuration Loading

**Status:** PASSED

**Details:**
- app_config.py: {'exists': True, 'valid_syntax': True, 'has_config_class': True, 'has_default_values': True}
- app_config.yaml: {'exists': True, 'valid_yaml': False, 'error': 'could not determine a constructor for the tag \'tag:yaml.org,2002:python/tuple\'\n  in "/workspace/final_test/rhinoplastik_windows_final/config/app_config.yaml", line 15, column 19'}

### Database Connection

**Status:** PASSED

**Details:**
- patients.db: {'exists': True, 'connectable': True, 'tables': ['patients', 'operations']}

### Widget Initialization

**Status:** PASSED

**Details:**
- ui/main_window.py: {'exists': True, 'has_class_definition': True, 'has_qt_imports': True, 'headless_compatible': True}
- ui/login_dialog.py: {'exists': True, 'has_class_definition': True, 'has_qt_imports': True, 'headless_compatible': True}
- ui/patient_editor_widget.py: {'exists': True, 'has_class_definition': True, 'has_qt_imports': True, 'headless_compatible': True}
- ui/patients_list_widget.py: {'exists': True, 'has_class_definition': True, 'has_qt_imports': True, 'headless_compatible': True}

### Error Handling Missing Dependencies

**Status:** PASSED

**Details:**
- Qt_import: {'handled': True, 'error_message': "No module named 'PyQt5'"}
- DB_connection: {'handled': True, 'error_message': 'Database connection failed'}
- config_missing: {'handled': True, 'config_exists': False}

### Logging System Initialization

**Status:** PASSED

**Details:**
- logging_conf.py: {'exists': True, 'has_logging_setup': True, 'has_config': True, 'has_levels': True}
- logs_directory: {'exists': True, 'writable': True}

### Session Management

**Status:** PASSED

**Details:**
- registry_directory: {'exists': True, 'files': ['registry.xlsx']}
- assets_registry.json: {'exists': True, 'valid_json': True, 'keys': ['ui.save', 'ui.open', 'ui.delete', 'ui.edit', 'ui.search', 'ui.settings', 'ui.home', 'ui.user', 'ui.calendar', 'ui.chart', 'ui.export', 'ui.import', 'ui.refresh', 'ui.print', 'ui.zoom_in', 'ui.zoom_out', 'ui.fullscreen', 'ui.minimize', 'ui.maximize', 'ui.close', 'ui.add', 'ui.remove', 'ui.upload', 'ui.download', 'ui.back', 'ui.forward', 'ui.up', 'ui.down', 'ui.left', 'ui.right', 'ui.info', 'ui.warning', 'ui.error', 'ui.success', 'ui.question', 'medical.stethoscope', 'medical.scalpel', 'medical.forceps', 'medical.clipboard', 'medical.heart_pulse', 'medical.pharmacy', 'medical.ambulance', 'medical.lab', 'medical.doctor', 'medical.patient', 'medical.surgery', 'medical.anatomy_nose', 'medical.bandage', 'medical.thermometer', 'medical.syringe', 'medical.microscope', 'medical.xray', 'medical.brain', 'medical.lung', 'medical.bone', 'status.active', 'status.inactive', 'status.pending', 'status.completed', 'status.cancelled', 'status.urgent', 'status.normal', 'status.warning', 'status.critical', 'app.logo', 'app.icon', 'app.splash']}
- tmp_directory: {'exists': True, 'writable': True}

## Empfehlungen

Basierend auf den Testergebnissen sollten folgende Bereiche überprüft werden:

- Fehlgeschlagene Tests:
  - QApplication Start
  - Module Imports

## Technische Details

- **Python Version:** 3.12.5 (main, Sep  5 2024, 00:16:34) [GCC 12.2.0]
- **Plattform:** linux
- **Arbeitsverzeichnis:** /workspace

## App-Struktur Analyse

Die getestete App-Struktur umfasst:
- Core-Module für Geschäftslogik
- UI-Module für Benutzeroberfläche  
- Konfigurationsmanagement
- Datenbank-Integration
- Asset-Management
- Logging-System
- Session-Management

---
*Report generiert von App-Start-Simulation Tool*

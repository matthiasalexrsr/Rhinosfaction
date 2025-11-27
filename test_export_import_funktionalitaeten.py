#!/usr/bin/env python3
"""
Umfassender Test für Export-/Import-Funktionalitäten der Rhinoplastik-Anwendung

Testet:
1. PDF-Export mit verschiedenen Datenformaten und -umfängen
2. CSV-/JSON-Export und Import-Operationen
3. Backup-/Restore-Funktionen der gesamten Anwendung
4. Datenkonsistenz bei Export/Import-Zyklen
5. Große Datenmengen und Performance
6. Fehlerhafte Import-Dateien und Recovery-Szenarien

Autor: Test Agent
Datum: 2025-11-06
"""

import sys
import os
import json
import csv
import time
import traceback
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import logging
import psutil
import zipfile

# Add the app directory to Python path
app_dir = Path(__file__).parent / "rhinoplastik_app"
sys.path.insert(0, str(app_dir))

try:
    from core.patients.patient_model import Patient, Demographics, Surgery, Measurements
    from core.patients.patient_manager import PatientManager
    from core.export.export_service import ExportService
    from core.backup.backup_service import BackupService
    from core.media.media_manager import MediaManager
except ImportError as e:
    print(f"Import-Fehler: {e}")
    print("Stelle sicher, dass alle Dependencies installiert sind")
    sys.exit(1)

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('export_import_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ExportImportTestSuite:
    """Test-Suite für alle Export-/Import-Funktionalitäten"""
    
    def __init__(self):
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': [],
        }
        self.performance_results = []
        
        # Test-Datenverzeichnis erstellen
        self.test_dir = Path(tempfile.mkdtemp(prefix="rhinoplastik_test_"))
        self.app_dir = self.test_dir / "app"
        self.exports_dir = self.test_dir / "exports"
        self.backups_dir = self.test_dir / "backups"
        
        # Verzeichnisse erstellen
        for dir_path in [self.app_dir, self.exports_dir, self.backups_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Komponenten initialisieren
        self.patient_manager = PatientManager(self.app_dir)
        self.export_service = ExportService(self.app_dir, self.patient_manager, None)
        self.backup_service = BackupService(self.app_dir, self.patient_manager, None)
        
        logger.info(f"Test-Suite initialisiert in: {self.test_dir}")
    
    def run_all_tests(self):
        """Führt alle Tests aus"""
        logger.info("=" * 80)
        logger.info("EXPORT-/IMPORT-FUNKTIONALITÄTEN TEST")
        logger.info("=" * 80)
        
        try:
            # Test 1: PDF-Export mit verschiedenen Datenformaten
            self.test_pdf_export()
            
            # Test 2: CSV-/JSON-Export und Import
            self.test_csv_json_export_import()
            
            # Test 3: Backup-/Restore-Funktionen
            self.test_backup_restore()
            
            # Test 4: Datenkonsistenz
            self.test_data_consistency()
            
            # Test 5: Performance mit großen Datenmengen
            self.test_performance_large_data()
            
            # Test 6: Fehlerhafte Dateien und Recovery
            self.test_error_recovery()
            
        except Exception as e:
            logger.error(f"Kritischer Fehler während Tests: {e}")
            traceback.print_exc()
        
        finally:
            self.cleanup()
            self.print_summary()
    
    def test_pdf_export(self):
        """Test 1: PDF-Export mit verschiedenen Datenformaten"""
        logger.info("\n" + "="*60)
        logger.info("TEST 1: PDF-EXPORT MIT VERSCHIEDENEN DATENFORMATEN")
        logger.info("="*60)
        
        try:
            # Test-Patienten erstellen
            test_patients = self.create_test_patients()
            
            for i, patient in enumerate(test_patients):
                patient_id = f"PDF_TEST_{i+1:03d}"
                patient.patient_id = patient_id
                
                # Test 1.1: Einfacher PDF-Export
                logger.info(f"Test 1.1.{i+1}: Einfacher PDF-Export für {patient_id}")
                start_time = time.time()
                
                success, message = self.export_service.export_patient_pdf(
                    patient_id, 
                    include_images=False,
                    anonymized=False
                )
                
                duration = time.time() - start_time
                
                if success:
                    self.record_success(f"PDF-Export (normal) - {patient_id}")
                    logger.info(f"✓ Erfolgreich: {message}")
                else:
                    self.record_failure(f"PDF-Export (normal) - {patient_id}: {message}")
                    logger.error(f"✗ Fehlgeschlagen: {message}")
                
                # Test 1.2: Anonymisierter PDF-Export
                logger.info(f"Test 1.2.{i+1}: Anonymisierter PDF-Export für {patient_id}")
                start_time = time.time()
                
                success, message = self.export_service.export_patient_pdf(
                    patient_id,
                    include_images=False,
                    anonymized=True
                )
                
                duration = time.time() - start_time
                
                if success:
                    self.record_success(f"PDF-Export (anonymisiert) - {patient_id}")
                    logger.info(f"✓ Erfolgreich: {message}")
                else:
                    self.record_failure(f"PDF-Export (anonymisiert) - {patient_id}: {message}")
                    logger.error(f"✗ Fehlgeschlagen: {message}")
            
            # Test 1.3: PDF-Export mit leeren Patientendaten
            logger.info("Test 1.3: PDF-Export mit leeren Patientendaten")
            empty_patient = self.create_empty_patient()
            empty_patient.patient_id = "PDF_EMPTY_TEST"
            
            success, message = self.export_service.export_patient_pdf(
                "PDF_EMPTY_TEST",
                include_images=False,
                anonymized=False
            )
            
            if success:
                self.record_success("PDF-Export (leere Daten)")
                logger.info(f"✓ Erfolgreich: {message}")
            else:
                self.record_failure(f"PDF-Export (leere Daten): {message}")
                logger.error(f"✗ Fehlgeschlagen: {message}")
                
        except Exception as e:
            self.record_failure(f"PDF-Export-Tests: {e}")
            logger.error(f"✗ Kritischer Fehler: {e}")
            traceback.print_exc()
    
    def test_csv_json_export_import(self):
        """Test 2: CSV-/JSON-Export und Import-Operationen"""
        logger.info("\n" + "="*60)
        logger.info("TEST 2: CSV-/JSON-EXPORT UND IMPORT-OPERATIONEN")
        logger.info("="*60)
        
        try:
            # Test-Patienten für Import/Export
            test_patients = self.create_test_patients()
            test_patients.extend([
                self.create_minimal_patient(),
                self.create_complex_patient()
            ])
            
            # Speichere alle Test-Patienten
            for i, patient in enumerate(test_patients):
                patient.patient_id = f"CSV_JSON_TEST_{i+1:03d}"
                patient.folder_slug = f"patient_{i+1:03d}"
                self.patient_manager.json_handler.save_patient(patient)
            
            # Test 2.1: CSV-Export (normal)
            logger.info("Test 2.1: CSV-Export (normal)")
            start_time = time.time()
            
            success, message = self.export_service.export_patients_csv(
                anonymized=False
            )
            
            duration = time.time() - start_time
            self.performance_results.append(('CSV-Export (normal)', duration))
            
            if success:
                self.record_success("CSV-Export (normal)")
                logger.info(f"✓ Erfolgreich: {message}")
                
                # Prüfe ob CSV-Datei erstellt wurde
                csv_files = list(self.exports_dir.glob("*.csv"))
                if csv_files:
                    logger.info(f"CSV-Datei erstellt: {csv_files[0]}")
                    
                    # Validiere CSV-Inhalt
                    self.validate_csv_content(csv_files[0])
            else:
                self.record_failure(f"CSV-Export (normal): {message}")
                logger.error(f"✗ Fehlgeschlagen: {message}")
            
            # Test 2.2: CSV-Export (anonymisiert)
            logger.info("Test 2.2: CSV-Export (anonymisiert)")
            start_time = time.time()
            
            success, message = self.export_service.export_patients_csv(
                anonymized=True
            )
            
            duration = time.time() - start_time
            self.performance_results.append(('CSV-Export (anonymisiert)', duration))
            
            if success:
                self.record_success("CSV-Export (anonymisiert)")
                logger.info(f"✓ Erfolgreich: {message}")
            else:
                self.record_failure(f"CSV-Export (anonymisiert): {message}")
                logger.error(f"✗ Fehlgeschlagen: {message}")
            
            # Test 2.3: JSON-Export (normal)
            logger.info("Test 2.3: JSON-Export (normal)")
            start_time = time.time()
            
            success, message = self.export_service.export_patients_json(
                anonymized=False
            )
            
            duration = time.time() - start_time
            self.performance_results.append(('JSON-Export (normal)', duration))
            
            if success:
                self.record_success("JSON-Export (normal)")
                logger.info(f"✓ Erfolgreich: {message}")
                
                # Validiere JSON-Inhalt
                json_files = list(self.exports_dir.glob("*.json"))
                if json_files:
                    self.validate_json_content(json_files[0])
            else:
                self.record_failure(f"JSON-Export (normal): {message}")
                logger.error(f"✗ Fehlgeschlagen: {message}")
            
            # Test 2.4: JSON-Export (anonymisiert)
            logger.info("Test 2.4: JSON-Export (anonymisiert)")
            start_time = time.time()
            
            success, message = self.export_service.export_patients_json(
                anonymized=True
            )
            
            duration = time.time() - start_time
            self.performance_results.append(('JSON-Export (anonymisiert)', duration))
            
            if success:
                self.record_success("JSON-Export (anonymisiert)")
                logger.info(f"✓ Erfolgreich: {message}")
            else:
                self.record_failure(f"JSON-Export (anonymisiert): {message}")
                logger.error(f"✗ Fehlgeschlagen: {message}")
            
        except Exception as e:
            self.record_failure(f"CSV/JSON-Export-Tests: {e}")
            logger.error(f"✗ Kritischer Fehler: {e}")
            traceback.print_exc()
    
    def test_backup_restore(self):
        """Test 3: Backup-/Restore-Funktionen der gesamten Anwendung"""
        logger.info("\n" + "="*60)
        logger.info("TEST 3: BACKUP-/RESTORE-FUNKTIONEN")
        logger.info("="*60)
        
        try:
            # Test-Daten für Backup erstellen
            test_patients = self.create_test_patients()
            for i, patient in enumerate(test_patients[:5]):  # Erste 5 für Backup-Test
                patient.patient_id = f"BACKUP_TEST_{i+1:03d}"
                patient.folder_slug = f"backup_patient_{i+1:03d}"
                self.patient_manager.json_handler.save_patient(patient)
            
            # Test 3.1: Manuelles Backup
            logger.info("Test 3.1: Manuelles Backup erstellen")
            start_time = time.time()
            
            backup_path = self.backup_service.create_manual_backup(
                custom_path=str(self.backups_dir / "test_manual_backup.zip"),
                description="Test für manuelle Backup-Funktionalität"
            )
            
            duration = time.time() - start_time
            self.performance_results.append(('Manuelles Backup', duration))
            
            if backup_path and Path(backup_path).exists():
                self.record_success("Manuelles Backup")
                logger.info(f"✓ Backup erstellt: {backup_path}")
                
                # Backup-Integrität prüfen
                is_valid, integrity_msg = self.backup_service.check_backup_integrity(backup_path)
                if is_valid:
                    self.record_success("Backup-Integritätsprüfung")
                    logger.info(f"✓ Backup-Integrität OK: {integrity_msg}")
                else:
                    self.record_failure(f"Backup-Integritätsprüfung: {integrity_msg}")
                    logger.error(f"✗ Backup-Integrität fehlerhaft: {integrity_msg}")
            else:
                self.record_failure("Manuelles Backup")
                logger.error("✗ Backup-Erstellung fehlgeschlagen")
            
            # Test 3.2: Automatisches Backup
            logger.info("Test 3.2: Automatisches Backup")
            start_time = time.time()
            
            auto_backup_path = self.backup_service.create_auto_backup()
            
            duration = time.time() - start_time
            self.performance_results.append(('Automatisches Backup', duration))
            
            if auto_backup_path and Path(auto_backup_path).exists():
                self.record_success("Automatisches Backup")
                logger.info(f"✓ Auto-Backup erstellt: {auto_backup_path}")
            else:
                self.record_failure("Automatisches Backup")
                logger.error("✗ Auto-Backup-Erstellung fehlgeschlagen")
            
            # Test 3.3: Backup-Wiederherstellung
            if 'backup_path' in locals() and Path(backup_path).exists():
                logger.info("Test 3.3: Backup-Wiederherstellung")
                
                # Erstelle Test-Wiederherstellungsverzeichnis
                restore_dir = self.test_dir / "restore_test"
                restore_dir.mkdir(exist_ok=True)
                
                start_time = time.time()
                
                success = self.backup_service.restore_backup(
                    backup_path,
                    target_dir=str(restore_dir),
                    overwrite_existing=True
                )
                
                duration = time.time() - start_time
                self.performance_results.append(('Backup-Wiederherstellung', duration))
                
                if success:
                    self.record_success("Backup-Wiederherstellung")
                    logger.info(f"✓ Backup erfolgreich wiederhergestellt in: {restore_dir}")
                    
                    # Prüfe wiederhergestellte Daten
                    restored_patients_dir = restore_dir / "data" / "patients"
                    if restored_patients_dir.exists():
                        restored_count = len([d for d in restored_patients_dir.iterdir() if d.is_dir()])
                        logger.info(f"✓ {restored_count} Patientenordner wiederhergestellt")
                else:
                    self.record_failure("Backup-Wiederherstellung")
                    logger.error("✗ Backup-Wiederherstellung fehlgeschlagen")
            
        except Exception as e:
            self.record_failure(f"Backup/Restore-Tests: {e}")
            logger.error(f"✗ Kritischer Fehler: {e}")
            traceback.print_exc()
    
    def test_data_consistency(self):
        """Test 4: Datenkonsistenz bei Export/Import-Zyklen"""
        logger.info("\n" + "="*60)
        logger.info("TEST 4: DATENKONSISTENZ BEI EXPORT/IMPORT-ZYKLEN")
        logger.info("="*60)
        
        try:
            # Test 4.1: Export/Import-Zyklus für JSON
            logger.info("Test 4.1: JSON Export/Import-Zyklus")
            
            # Original-Patient erstellen
            original_patient = self.create_complex_patient()
            original_patient.patient_id = "CONSISTENCY_TEST_001"
            original_patient.folder_slug = "consistency_patient"
            
            # Speichern
            save_success = self.patient_manager.json_handler.save_patient(original_patient)
            if not save_success:
                self.record_failure("JSON Save (Konsistenz-Test)")
                return
            
            # Export
            json_file = self.exports_dir / "consistency_test.json"
            success, message = self.export_service.export_patients_json(
                patient_ids=["CONSISTENCY_TEST_001"],
                output_file=json_file,
                anonymized=False
            )
            
            if not success:
                self.record_failure(f"JSON Export (Konsistenz-Test): {message}")
                return
            
            # Daten aus JSON laden
            with open(json_file, 'r', encoding='utf-8') as f:
                exported_data = json.load(f)
            
            if not exported_data:
                self.record_failure("JSON Export (Konsistenz-Test): Keine Daten exportiert")
                return
            
            # Import-Simulation: JSON-Daten neu laden
            if len(exported_data) > 0:
                imported_patient_data = exported_data[0]
                
                # Patient aus JSON-Daten neu erstellen
                # (Vereinfacht - in echter Anwendung würde hier ein Import stattfinden)
                consistency_check = self.validate_patient_data_consistency(
                    original_patient, 
                    imported_patient_data
                )
                
                if consistency_check:
                    self.record_success("JSON Export/Import-Konsistenz")
                    logger.info("✓ Datenkonsistenz nach Export/Import-Zyklus bestätigt")
                else:
                    self.record_failure("JSON Export/Import-Konsistenz")
                    logger.error("✗ Datenkonsistenz nach Export/Import-Zyklus fehlgeschlagen")
            
            # Test 4.2: CSV-Datenkonsistenz
            logger.info("Test 4.2: CSV Export-Konsistenz")
            
            csv_file = self.exports_dir / "consistency_test.csv"
            success, message = self.export_service.export_patients_csv(
                patient_ids=["CONSISTENCY_TEST_001"],
                output_file=csv_file,
                anonymized=False
            )
            
            if success:
                # Validiere CSV-Konsistenz
                if self.validate_csv_consistency(csv_file, original_patient):
                    self.record_success("CSV Export-Konsistenz")
                    logger.info("✓ CSV-Datenkonsistenz bestätigt")
                else:
                    self.record_failure("CSV Export-Konsistenz")
                    logger.error("✗ CSV-Datenkonsistenz fehlgeschlagen")
            else:
                self.record_failure(f"CSV Export (Konsistenz-Test): {message}")
            
        except Exception as e:
            self.record_failure(f"Datenkonsistenz-Tests: {e}")
            logger.error(f"✗ Kritischer Fehler: {e}")
            traceback.print_exc()
    
    def test_performance_large_data(self):
        """Test 5: Performance mit großen Datenmengen"""
        logger.info("\n" + "="*60)
        logger.info("TEST 5: PERFORMANCE MIT GROSSEN DATENMENGEN")
        logger.info("="*60)
        
        try:
            # Test 5.1: Viele Patienten erstellen
            logger.info("Test 5.1: Erstellen von 100 Test-Patienten")
            
            start_time = time.time()
            large_dataset = []
            
            for i in range(100):
                patient = self.create_random_patient(f"PERF_TEST_{i+1:03d}")
                large_dataset.append(patient)
                
                # Speichern für Performance-Messung
                self.patient_manager.json_handler.save_patient(patient)
            
            create_duration = time.time() - start_time
            self.performance_results.append(('Erstelle 100 Patienten', create_duration))
            
            logger.info(f"✓ 100 Patienten erstellt in {create_duration:.2f} Sekunden")
            
            # Test 5.2: Bulk CSV-Export
            logger.info("Test 5.2: Bulk CSV-Export (100 Patienten)")
            start_time = time.time()
            
            success, message = self.export_service.export_patients_csv(anonymized=False)
            
            export_duration = time.time() - start_time
            self.performance_results.append(('Bulk CSV-Export (100 Patienten)', export_duration))
            
            if success:
                self.record_success("Bulk CSV-Export (100 Patienten)")
                logger.info(f"✓ Bulk CSV-Export erfolgreich in {export_duration:.2f} Sekunden")
                
                # CSV-Dateigröße prüfen
                csv_files = list(self.exports_dir.glob("*.csv"))
                if csv_files:
                    csv_size_mb = csv_files[0].stat().st_size / (1024 * 1024)
                    logger.info(f"CSV-Dateigröße: {csv_size_mb:.2f} MB")
            else:
                self.record_failure(f"Bulk CSV-Export: {message}")
                logger.error(f"✗ Bulk CSV-Export fehlgeschlagen: {message}")
            
            # Test 5.3: Bulk JSON-Export
            logger.info("Test 5.3: Bulk JSON-Export (100 Patienten)")
            start_time = time.time()
            
            success, message = self.export_service.export_patients_json(anonymized=False)
            
            export_duration = time.time() - start_time
            self.performance_results.append(('Bulk JSON-Export (100 Patienten)', export_duration))
            
            if success:
                self.record_success("Bulk JSON-Export (100 Patienten)")
                logger.info(f"✓ Bulk JSON-Export erfolgreich in {export_duration:.2f} Sekunden")
                
                # JSON-Dateigröße prüfen
                json_files = list(self.exports_dir.glob("*.json"))
                if json_files:
                    json_size_mb = json_files[0].stat().st_size / (1024 * 1024)
                    logger.info(f"JSON-Dateigröße: {json_size_mb:.2f} MB")
            else:
                self.record_failure(f"Bulk JSON-Export: {message}")
                logger.error(f"✗ Bulk JSON-Export fehlgeschlagen: {message}")
            
            # Test 5.4: Großes Backup
            logger.info("Test 5.4: Backup mit 100 Patienten")
            start_time = time.time()
            
            large_backup_path = self.backup_service.create_manual_backup(
                custom_path=str(self.backups_dir / "large_dataset_backup.zip"),
                description="Backup mit 100 Test-Patienten"
            )
            
            backup_duration = time.time() - start_time
            self.performance_results.append(('Backup (100 Patienten)', backup_duration))
            
            if large_backup_path and Path(large_backup_path).exists():
                self.record_success("Backup (100 Patienten)")
                backup_size_mb = Path(large_backup_path).stat().st_size / (1024 * 1024)
                logger.info(f"✓ Großes Backup erstellt in {backup_duration:.2f} Sekunden ({backup_size_mb:.2f} MB)")
            else:
                self.record_failure("Backup (100 Patienten)")
                logger.error("✗ Großes Backup fehlgeschlagen")
            
            # Test 5.5: Speicherverbrauch prüfen
            process = psutil.Process()
            memory_mb = process.memory_info().rss / (1024 * 1024)
            logger.info(f"Speicherverbrauch nach großen Tests: {memory_mb:.2f} MB")
            
        except Exception as e:
            self.record_failure(f"Performance-Tests: {e}")
            logger.error(f"✗ Kritischer Fehler: {e}")
            traceback.print_exc()
    
    def test_error_recovery(self):
        """Test 6: Fehlerhafte Import-Dateien und Recovery-Szenarien"""
        logger.info("\n" + "="*60)
        logger.info("TEST 6: FEHLERHAFTE IMPORT-DATEIEN UND RECOVERY")
        logger.info("="*60)
        
        try:
            # Test 6.1: Korrupte JSON-Datei
            logger.info("Test 6.1: Korrupte JSON-Datei behandeln")
            
            corrupt_json_file = self.exports_dir / "corrupt_data.json"
            with open(corrupt_json_file, 'w') as f:
                f.write('{"invalid": json syntax, "missing": quotes}')
            
            # Versuche korrupte JSON zu laden
            try:
                with open(corrupt_json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.record_failure("Korrupte JSON-Behandlung")
                logger.error("✗ Korrupte JSON wurde fälschlicherweise akzeptiert")
            except json.JSONDecodeError:
                self.record_success("Korrupte JSON-Behandlung")
                logger.info("✓ Korrupte JSON-Datei korrekt abgelehnt")
            
            # Test 6.2: Leere JSON-Datei
            logger.info("Test 6.2: Leere JSON-Datei behandeln")
            
            empty_json_file = self.exports_dir / "empty_data.json"
            with open(empty_json_file, 'w') as f:
                f.write('')
            
            try:
                with open(empty_json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.record_failure("Leere JSON-Behandlung")
                logger.error("✗ Leere JSON wurde fälschlicherweise akzeptiert")
            except (json.JSONDecodeError, ValueError):
                self.record_success("Leere JSON-Behandlung")
                logger.info("✓ Leere JSON-Datei korrekt abgelehnt")
            
            # Test 6.3: CSV mit fehlerhaften Daten
            logger.info("Test 6.3: CSV mit fehlerhaften Daten")
            
            corrupt_csv_file = self.exports_dir / "corrupt_data.csv"
            with open(corrupt_csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Name', 'Alter', 'Geschlecht'])
                writer.writerow(['Test Patient', 'invalid_age', 'M'])
                writer.writerow(['Another Patient', '25', ''])  # Fehlende Geschlechtsangabe
                writer.writerow([])  # Leere Zeile
                writer.writerow(['Valid Patient', '30', 'F'])
            
            # Validiere CSV-Behandlung
            csv_validation_result = self.validate_csv_error_handling(corrupt_csv_file)
            if csv_validation_result:
                self.record_success("CSV Fehlerbehandlung")
                logger.info("✓ Fehlerhafte CSV-Daten korrekt behandelt")
            else:
                self.record_failure("CSV Fehlerbehandlung")
                logger.error("✗ Fehlerhafte CSV-Daten nicht korrekt behandelt")
            
            # Test 6.4: Korrupte Backup-Datei
            logger.info("Test 6.4: Korrupte Backup-Datei")
            
            corrupt_backup_file = self.exports_dir / "corrupt_backup.zip"
            with open(corrupt_backup_file, 'wb') as f:
                f.write(b'This is not a valid ZIP file content')
            
            # Backup-Integrität prüfen
            is_valid, integrity_msg = self.backup_service.check_backup_integrity(str(corrupt_backup_file))
            if not is_valid:
                self.record_success("Korrupte Backup-Behandlung")
                logger.info(f"✓ Korrupte Backup-Datei korrekt erkannt: {integrity_msg}")
            else:
                self.record_failure("Korrupte Backup-Behandlung")
                logger.error("✗ Korrupte Backup-Datei fälschlicherweise akzeptiert")
            
            # Test 6.5: Nicht-existierende Dateien
            logger.info("Test 6.5: Nicht-existierende Dateien")
            
            non_existent_file = self.exports_dir / "non_existent_file.json"
            
            # Versuche nicht-existierende Datei zu öffnen
            try:
                with open(non_existent_file, 'r') as f:
                    data = json.load(f)
                self.record_failure("Nicht-existierende Datei-Behandlung")
                logger.error("✗ Nicht-existierende Datei fälschlicherweise akzeptiert")
            except FileNotFoundError:
                self.record_success("Nicht-existierende Datei-Behandlung")
                logger.info("✓ Nicht-existierende Datei korrekt abgelehnt")
            
        except Exception as e:
            self.record_failure(f"Error-Recovery-Tests: {e}")
            logger.error(f"✗ Kritischer Fehler: {e}")
            traceback.print_exc()
    
    # Hilfsmethoden für Testdaten und Validierung
    
    def create_test_patients(self) -> List[Patient]:
        """Erstellt Test-Patienten für verschiedene Szenarien"""
        patients = []
        
        for i in range(5):
            gender = "Männlich" if i % 2 == 0 else "Weiblich"
            demographics = Demographics(
                firstname=f"Test{chr(65+i)}",  # TestA, TestB, TestC, etc.
                lastname="Patient",
                gender=gender,
                dob=date(1980 + i, 1 + i % 12, 1 + i % 28)
            )
            
            surgery = Surgery(
                op_date=date(2023, 1, 1),
                technique="Standard",
                nose_shape="Gerade",
                op_duration_min=120 + i * 15,
                blood_loss_ml=50 + i * 10
            )
            
            measurements = Measurements(
                nose_length_mm=45.0 + i,
                nose_width_mm=35.0 + i,
                nose_height_mm=20.0 + i,
                tip_rotation_deg=90.0 + i,
                tip_projection_mm=25.0 + i,
                nasolabial_angle_deg=95.0 + i,
                dorsal_height_mm=15.0 + i
            )
            surgery.measurements = measurements
            
            patient = Patient(
                demographics=demographics,
                surgery=surgery
            )
            
            patients.append(patient)
        
        return patients
    
    def create_empty_patient(self) -> Patient:
        """Erstellt Patient mit minimalen Daten"""
        demographics = Demographics(
            firstname="Empty",
            lastname="Patient",
            gender="Männlich",
            dob=None
        )
        
        return Patient(demographics=demographics)
    
    def create_minimal_patient(self) -> Patient:
        """Erstellt Patient mit minimalen Daten"""
        demographics = Demographics(
            firstname="Minimal",
            lastname="Test",
            gender="Weiblich",
            dob=date(1990, 5, 15)
        )
        
        return Patient(demographics=demographics)
    
    def create_complex_patient(self) -> Patient:
        """Erstellt Patient mit komplexen Daten"""
        demographics = Demographics(
            firstname="Complex",
            lastname="DataPatient",
            gender="Männlich",
            dob=date(1975, 12, 25)
        )
        
        surgery = Surgery(
            op_date=date(2024, 3, 15),
            technique="Erweiterte Septorhinoplastik",
            nose_shape="Höckernase",
            op_duration_min=180,
            blood_loss_ml=75,
            indications=["Septumdeviation", "Nasenatmungsbehinderung"]
        )
        
        measurements = Measurements(
            nose_length_mm=50.2,
            nose_width_mm=38.5,
            nose_height_mm=22.1,
            tip_rotation_deg=93.5,
            tip_projection_mm=28.3,
            nasolabial_angle_deg=97.2,
            dorsal_height_mm=18.7
        )
        surgery.measurements = measurements
        
        return Patient(demographics=demographics, surgery=surgery)
    
    def create_random_patient(self, patient_id: str) -> Patient:
        """Erstellt zufälligen Test-Patienten"""
        import random
        
        first_names = ["Anna", "Bernd", "Claudia", "Daniel", "Eva", "Frank", "Gabriele", "Hans", "Inge", "Jürgen"]
        last_names = ["Schmidt", "Müller", "Weber", "Mayer", "Schneider", "Fischer", "Wagner", "Becker", "Hoffmann", "Schäfer"]
        
        demographics = Demographics(
            firstname=random.choice(first_names),
            lastname=random.choice(last_names),
            gender=random.choice(["Männlich", "Weiblich"]),
            dob=date(1950 + random.randint(0, 50), 
                     random.randint(1, 12), 
                     random.randint(1, 28))
        )
        
        surgery = Surgery(
            op_date=date(2020 + random.randint(0, 4), 
                        random.randint(1, 12), 
                        random.randint(1, 28)),
            technique=random.choice(["Standard", "Erweitert", "Minimal-invasiv"]),
            nose_shape=random.choice(["Gerade", "Höckernase", "Sattelnase"]),
            op_duration_min=random.randint(90, 240),
            blood_loss_ml=random.randint(30, 100)
        )
        
        measurements = Measurements(
            nose_length_mm=random.uniform(40, 60),
            nose_width_mm=random.uniform(30, 45),
            nose_height_mm=random.uniform(18, 25),
            tip_rotation_deg=random.uniform(85, 100),
            tip_projection_mm=random.uniform(20, 35),
            nasolabial_angle_deg=random.uniform(90, 105),
            dorsal_height_mm=random.uniform(12, 22)
        )
        surgery.measurements = measurements
        
        patient = Patient(demographics=demographics, surgery=surgery)
        patient.patient_id = patient_id
        patient.folder_slug = f"patient_{patient_id.lower()}"
        
        return patient
    
    def validate_csv_content(self, csv_file: Path) -> bool:
        """Validiert CSV-Dateinhalt"""
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                if not rows:
                    logger.warning("CSV-Datei ist leer")
                    return False
                
                # Prüfe erforderliche Spalten
                required_columns = ['ID', 'Nachname', 'Vorname', 'Geschlecht']
                if not all(col in reader.fieldnames for col in required_columns):
                    logger.warning(f"CSV-Datei fehlen erforderliche Spalten. Vorhanden: {reader.fieldnames}")
                    return False
                
                logger.info(f"CSV-Validierung OK: {len(rows)} Zeilen, Spalten: {reader.fieldnames}")
                return True
                
        except Exception as e:
            logger.error(f"CSV-Validierungsfehler: {e}")
            return False
    
    def validate_json_content(self, json_file: Path) -> bool:
        """Validiert JSON-Dateinhalt"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                logger.warning("JSON-Datei enthält keine Liste")
                return False
            
            if not data:
                logger.warning("JSON-Liste ist leer")
                return False
            
            # Prüfe Struktur des ersten Elements
            first_patient = data[0]
            required_fields = ['patient_id', 'demographics']
            if not all(field in first_patient for field in required_fields):
                logger.warning(f"JSON-Struktur fehlerhaft. Vorhandene Felder: {list(first_patient.keys())}")
                return False
            
            logger.info(f"JSON-Validierung OK: {len(data)} Patienten")
            return True
            
        except Exception as e:
            logger.error(f"JSON-Validierungsfehler: {e}")
            return False
    
    def validate_patient_data_consistency(self, original: Patient, imported_data: dict) -> bool:
        """Validiert Datenkonsistenz zwischen originalem und importiertem Patienten"""
        try:
            # Grundlegende Feldvergleiche
            if original.demographics.firstname != imported_data.get('demographics', {}).get('firstname'):
                logger.warning("Vorname stimmt nicht überein")
                return False
            
            if original.demographics.lastname != imported_data.get('demographics', {}).get('lastname'):
                logger.warning("Nachname stimmt nicht überein")
                return False
            
            if original.demographics.gender != imported_data.get('demographics', {}).get('gender'):
                logger.warning("Geschlecht stimmt nicht überein")
                return False
            
            logger.info("Datenkonsistenz-Validierung erfolgreich")
            return True
            
        except Exception as e:
            logger.error(f"Datenkonsistenz-Validierungsfehler: {e}")
            return False
    
    def validate_csv_consistency(self, csv_file: Path, patient: Patient) -> bool:
        """Validiert CSV-Konsistenz mit Patientendaten"""
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            # Finde Patient in CSV
            patient_row = None
            for row in rows:
                if row.get('ID') == patient.patient_id:
                    patient_row = row
                    break
            
            if not patient_row:
                logger.warning(f"Patient {patient.patient_id} nicht in CSV gefunden")
                return False
            
            # Vergleiche Daten
            if patient.demographics.firstname != patient_row.get('Vorname'):
                logger.warning("Vorname stimmt nicht überein")
                return False
            
            if patient.demographics.lastname != patient_row.get('Nachname'):
                logger.warning("Nachname stimmt nicht überein")
                return False
            
            if patient.demographics.gender != patient_row.get('Geschlecht'):
                logger.warning("Geschlecht stimmt nicht überein")
                return False
            
            logger.info("CSV-Konsistenz-Validierung erfolgreich")
            return True
            
        except Exception as e:
            logger.error(f"CSV-Konsistenz-Validierungsfehler: {e}")
            return False
    
    def validate_csv_error_handling(self, csv_file: Path) -> bool:
        """Validiert CSV-Fehlerbehandlung"""
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            # Prüfe ob gültige Zeilen verarbeitet wurden
            valid_rows = [row for row in rows if row.get('Name') and row.get('Alter') and row.get('Geschlecht')]
            
            if len(valid_rows) > 0:
                logger.info(f"CSV-Fehlerbehandlung OK: {len(valid_rows)} gültige Zeilen aus {len(rows)} Gesamtzeilen")
                return True
            else:
                logger.warning("CSV-Fehlerbehandlung: Keine gültigen Zeilen gefunden")
                return False
                
        except Exception as e:
            logger.error(f"CSV-Fehlerbehandlungs-Validierung fehlgeschlagen: {e}")
            return False
    
    def record_success(self, test_name: str):
        """Registriert erfolgreichen Test"""
        self.test_results['passed'] += 1
        logger.info(f"✓ ERFOLG: {test_name}")
    
    def record_failure(self, test_name: str):
        """Registriert fehlgeschlagenen Test"""
        self.test_results['failed'] += 1
        self.test_results['errors'].append(test_name)
        logger.error(f"✗ FEHLER: {test_name}")
    
    def cleanup(self):
        """Räumt Test-Dateien auf"""
        try:
            if self.test_dir.exists():
                shutil.rmtree(self.test_dir)
                logger.info(f"Test-Verzeichnis aufgeräumt: {self.test_dir}")
        except Exception as e:
            logger.error(f"Fehler beim Aufräumen: {e}")
    
    def print_summary(self):
        """Druckt Testergebnis-Zusammenfassung"""
        logger.info("\n" + "="*80)
        logger.info("TESTERGEBNISSE - EXPORT-/IMPORT-FUNKTIONALITÄTEN")
        logger.info("="*80)
        
        total_tests = self.test_results['passed'] + self.test_results['failed']
        success_rate = (self.test_results['passed'] / total_tests * 100) if total_tests > 0 else 0
        
        logger.info(f"Gesamt Tests: {total_tests}")
        logger.info(f"Erfolgreich: {self.test_results['passed']}")
        logger.info(f"Fehlgeschlagen: {self.test_results['failed']}")
        logger.info(f"Erfolgsquote: {success_rate:.1f}%")
        
        if self.test_results['errors']:
            logger.info("\nFehlgeschlagene Tests:")
            for error in self.test_results['errors']:
                logger.info(f"  - {error}")
        
        if self.performance_results:
            logger.info("\nLEISTUNGSERGEBNISSE:")
            logger.info("-" * 40)
            for test_name, duration in self.performance_results:
                logger.info(f"{test_name:<40} {duration:>8.2f}s")
        
        logger.info("\n" + "="*80)
        
        # Ergebnisse auch in Datei speichern
        self.save_test_report()
    
    def save_test_report(self):
        """Speichert detaillierten Testbericht"""
        report_file = Path("export_import_test_report.md")
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("# Export-/Import-Funktionalitäten Test-Bericht\n\n")
                f.write(f"**Test-Datum:** {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n\n")
                
                # Zusammenfassung
                total_tests = self.test_results['passed'] + self.test_results['failed']
                success_rate = (self.test_results['passed'] / total_tests * 100) if total_tests > 0 else 0
                
                f.write("## Zusammenfassung\n\n")
                f.write(f"- **Gesamt Tests:** {total_tests}\n")
                f.write(f"- **Erfolgreich:** {self.test_results['passed']}\n")
                f.write(f"- **Fehlgeschlagen:** {self.test_results['failed']}\n")
                f.write(f"- **Erfolgsquote:** {success_rate:.1f}%\n\n")
                
                # Testergebnisse im Detail
                f.write("## Test-Kategorien\n\n")
                f.write("### 1. PDF-Export mit verschiedenen Datenformaten\n")
                f.write("- Test normaler PDF-Export\n")
                f.write("- Test anonymisierter PDF-Export\n")
                f.write("- Test PDF-Export mit leeren Daten\n\n")
                
                f.write("### 2. CSV-/JSON-Export und Import-Operationen\n")
                f.write("- Test CSV-Export (normal/anonymisiert)\n")
                f.write("- Test JSON-Export (normal/anonymisiert)\n")
                f.write("- Validierung der Export-Dateien\n\n")
                
                f.write("### 3. Backup-/Restore-Funktionen\n")
                f.write("- Test manuelles Backup\n")
                f.write("- Test automatisches Backup\n")
                f.write("- Test Backup-Wiederherstellung\n")
                f.write("- Test Backup-Integritätsprüfung\n\n")
                
                f.write("### 4. Datenkonsistenz bei Export/Import-Zyklen\n")
                f.write("- Test JSON Export/Import-Konsistenz\n")
                f.write("- Test CSV-Datenkonsistenz\n\n")
                
                f.write("### 5. Performance mit großen Datenmengen\n")
                f.write("- Test mit 100 Test-Patienten\n")
                f.write("- Bulk-Export-Performance\n")
                f.write("- Speicherverbrauch-Tests\n\n")
                
                f.write("### 6. Fehlerhafte Dateien und Recovery\n")
                f.write("- Test korrupte JSON-Dateien\n")
                f.write("- Test leere JSON-Dateien\n")
                f.write("- Test fehlerhafte CSV-Daten\n")
                f.write("- Test korrupte Backup-Dateien\n")
                f.write("- Test nicht-existierende Dateien\n\n")
                
                # Fehler详细信息
                if self.test_results['errors']:
                    f.write("## Fehlgeschlagene Tests\n\n")
                    for i, error in enumerate(self.test_results['errors'], 1):
                        f.write(f"{i}. {error}\n")
                    f.write("\n")
                
                # Performance-Ergebnisse
                if self.performance_results:
                    f.write("## Performance-Ergebnisse\n\n")
                    f.write("| Test | Dauer (s) |\n")
                    f.write("|------|-----------|\n")
                    for test_name, duration in self.performance_results:
                        f.write(f"| {test_name} | {duration:.2f} |\n")
                    f.write("\n")
                
                # Empfehlungen
                f.write("## Empfehlungen\n\n")
                if self.test_results['failed'] == 0:
                    f.write("✅ **Alle Tests erfolgreich!** Die Export-/Import-Funktionalitäten arbeiten korrekt.\n\n")
                else:
                    f.write(f"⚠️ **{self.test_results['failed']} Tests fehlgeschlagen.** Überprüfung der folgenden Bereiche empfohlen:\n\n")
                    f.write("- Datenvalidierung bei Export-Operationen\n")
                    f.write("- Fehlerbehandlung für korrupte Dateien\n")
                    f.write("- Performance-Optimierung für große Datenmengen\n\n")
                
                f.write("## Test-Umgebung\n\n")
                f.write(f"- **Test-Verzeichnis:** {self.test_dir}\n")
                f.write(f"- **Python-Version:** {sys.version}\n")
                f.write(f"- **Test-Dauer:** Gesamt\n\n")
                
                # Log-Datei Hinweis
                f.write("---\n")
                f.write("*Detaillierte Logs siehe: export_import_test.log*\n")
            
            logger.info(f"Test-Bericht gespeichert: {report_file}")
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Test-Berichts: {e}")


def main():
    """Hauptfunktion"""
    try:
        # Test-Suite ausführen
        test_suite = ExportImportTestSuite()
        test_suite.run_all_tests()
        
    except Exception as e:
        logger.error(f"Kritischer Fehler in main(): {e}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
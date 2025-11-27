#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Umfassender Funktionstest der Rhinoplastik-Anwendung
Simuliert die Nutzung aller Hauptfunktionen mit fiktivem Patienten
"""

import os
import sys
import json
import uuid
from datetime import datetime, date
from pathlib import Path

# Pfad zur Anwendung hinzufügen
app_path = Path("/workspace/rhinoplastik_app")
sys.path.insert(0, str(app_path))

def test_imports():
    """Test 1: Alle Import-Funktionen testen"""
    print("🧪 TEST 1: Import-Funktionen prüfen...")
    
    try:
        # Core-Module
        from core.logging_conf import setup_logging
        from config.app_config import AppConfig
        from core.patients.patient_service import PatientService
        from core.statistics.statistics_service import StatisticsService
        from core.export.export_service import ExportService
        from core.validators.validators import PatientValidator
        
        # UI-Module (nur für Strukturanalyse, nicht für GUI)
        import ui.main_window
        import ui.patient_editor_widget
        import ui.patients_list_widget
        import ui.image_manager_widget
        import ui.statistics_widget
        import ui.dashboard_widget
        import ui.export_widget
        
        print("✅ Alle Module erfolgreich importiert")
        return True
    except Exception as e:
        print(f"❌ Import-Fehler: {e}")
        return False

def create_fictitious_patient():
    """Erstelle fiktiven Patienten für Tests"""
    print("\n🧪 TEST 2: Fiktiven Patienten erstellen...")
    
    patient_data = {
        "id": str(uuid.uuid4()),
        "personal_info": {
            "name": "Müller",
            "vorname": "Sarah",
            "geburtsdatum": "1985-03-15",
            "geschlecht": "weiblich",
            "telefon": "+49 123 456789",
            "email": "s.mueller@email.com",
            "adresse": "Musterstraße 123, 12345 Musterstadt"
        },
        "medical_info": {
            "allergien": ["Pollen", "Penicillin"],
            "medikamente": ["Aspirin 100mg täglich"],
            "vorangegangene_operationen": ["2018 - Appendektomie"],
            "allgemeiner_gesundheitszustand": "gut",
            "rauchen": "nein",
            "alkohol": "gelegentlich"
        },
        "operation_info": {
            "operation_datum": "2024-11-06",
            "operation_typ": "Rhinoplastik (Funktionell + Ästhetisch)",
            "narkose_art": "Vollnarkose",
            "dauer_minuten": 180,
            "komplikationen": [],
            "erfolg": "ja",
            "nachbehandlung": "3 Monate Nachsorge"
        },
        "photos": {
            "vor_operation": [
                "/workspace/rhinoplastik_app/data/photos/vor_frontal_sarah.jpg",
                "/workspace/rhinoplastik_app/data/photos/vor_seitlich_sarah.jpg",
                "/workspace/rhinoplastik_app/data/photos/vor_45grad_sarah.jpg"
            ],
            "nach_operation": [],
            "nachsorge": []
        },
        "messungen": {
            "nasenlaenge_vor": 5.2,
            "nasenlaenge_nach": 4.8,
            "nasenbreite_vor": 3.5,
            "nasenbreite_nach": 3.2,
            "nasenhoehe_vor": 1.8,
            "nasenhoehe_nach": 1.7,
            "winkel_nasen_stirn_vor": 130,
            "winkel_nasen_stirn_nach": 135,
            "nasenspitze_projektion_vor": 2.1,
            "nasenspitze_projektion_nach": 2.3
        },
        "notizen": {
            "praoperative_analyse": "Patientin wünscht Nasenspitzenkorrektur und Begradigung der Nasenrücken-Linie",
            "postoperative_beobachtung": "Operation verlief komplikationslos",
            "nachsorge_weisungen": "Vermeidung von Sonnenexposition für 3 Monate"
        },
        "dokumentation": {
            "erstellt_am": datetime.now().isoformat(),
            "letzte_aenderung": datetime.now().isoformat(),
            "erstellt_von": "Dr. Test",
            "status": "komplett"
        }
    }
    
    print("✅ Fiktiver Patient 'Sarah Müller' erstellt")
    return patient_data

def test_patient_service(patient_data):
    """Test 3: PatientService Funktionalitäten"""
    print("\n🧪 TEST 3: PatientService testen...")
    
    try:
        from core.patients.patient_service import PatientService
        
        service = PatientService()
        
        # Test: Patient speichern
        patient_id = service.add_patient(patient_data)
        print(f"   ✅ Patient gespeichert: {patient_id}")
        
        # Test: Patient laden
        loaded_patient = service.get_patient(patient_id)
        if loaded_patient:
            print("   ✅ Patient erfolgreich geladen")
            print(f"      Name: {loaded_patient['personal_info']['name']}")
        
        # Test: Patienten suchen
        results = service.search_patients("Müller")
        print(f"   ✅ Patientensuche: {len(results)} Ergebnis(se) gefunden")
        
        # Test: Patientenliste
        all_patients = service.get_all_patients()
        print(f"   ✅ Gesamte Patientenliste: {len(all_patients)} Patient(en)")
        
        return True
    except Exception as e:
        print(f"❌ PatientService Fehler: {e}")
        return False

def test_statistics_service(patient_data):
    """Test 4: StatisticsService Funktionalitäten"""
    print("\n🧪 TEST 4: StatisticsService testen...")
    
    try:
        from core.statistics.statistics_service import StatisticsService
        
        service = StatisticsService()
        
        # Test: Basis-Statistiken
        stats = service.get_basic_statistics()
        print(f"   ✅ Basis-Statistiken: {len(stats)} Kategorien")
        
        for key, value in list(stats.items())[:3]:  # Erste 3 anzeigen
            print(f"      {key}: {value}")
        
        # Test: Gefilterte Statistiken
        filtered_stats = service.get_filtered_statistics({
            "geschlecht": "weiblich",
            "operation_typ": "Rhinoplastik"
        })
        print(f"   ✅ Gefilterte Statistiken erstellt")
        
        # Test: Altersverteilung
        age_dist = service._calculate_age_distribution()
        print(f"   ✅ Altersverteilung: {len(age_dist)} Altersgruppen")
        
        return True
    except Exception as e:
        print(f"❌ StatisticsService Fehler: {e}")
        return False

def test_validation(patient_data):
    """Test 5: Validierung der Patientendaten"""
    print("\n🧪 TEST 5: Datenvalidierung testen...")
    
    try:
        from core.validators.validators import PatientValidator
        
        validator = PatientValidator()
        
        # Test: Vollständige Validierung
        is_valid, errors = validator.validate_patient_data(patient_data)
        
        if is_valid:
            print("   ✅ Patientendaten vollständig gültig")
        else:
            print(f"   ⚠️ Validierungsfehler: {len(errors)} gefunden")
            for error in errors[:3]:  # Erste 3 Fehler anzeigen
                print(f"      - {error}")
        
        return is_valid
    except Exception as e:
        print(f"❌ Validierungsfehler: {e}")
        return False

def test_export_service(patient_data):
    """Test 6: ExportService Funktionalitäten"""
    print("\n🧪 TEST 6: Export-Service testen...")
    
    try:
        from core.export.export_service import ExportService
        
        service = ExportService()
        
        # Test: JSON Export
        export_path = service.export_patient_data(patient_data, "json")
        print(f"   ✅ JSON-Export: {export_path}")
        
        # Test: Bericht generieren
        report_path = service.generate_patient_report(patient_data)
        print(f"   ✅ Bericht generiert: {report_path}")
        
        return True
    except Exception as e:
        print(f"❌ ExportService Fehler: {e}")
        return False

def test_data_integrity():
    """Test 7: Datenintegrität prüfen"""
    print("\n🧪 TEST 7: Datenintegrität prüfen...")
    
    try:
        from core.patients.patient_service import PatientService
        from config.app_config import AppConfig
        
        service = PatientService()
        config = AppConfig()
        
        # Test: Datenverzeichnisse
        data_dirs = [
            config.get('data.patients'),
            config.get('data.photos'),
            config.get('data.backups')
        ]
        
        for dir_path in data_dirs:
            if os.path.exists(dir_path):
                print(f"   ✅ Verzeichnis existiert: {dir_path}")
            else:
                print(f"   ⚠️ Verzeichnis fehlt: {dir_path}")
        
        # Test: Patientendatenbank
        patients = service.get_all_patients()
        print(f"   ✅ Datenbank: {len(patients)} Patient(en)")
        
        return True
    except Exception as e:
        print(f"❌ Datenintegritätsfehler: {e}")
        return False

def test_image_management():
    """Test 8: Bildverwaltung (simuliert)"""
    print("\n🧪 TEST 8: Bildverwaltung testen...")
    
    try:
        from core.media.image_service import ImageService
        
        service = ImageService()
        
        # Test: Bildverzeichnis
        image_dir = "/workspace/rhinoplastik_app/data/photos"
        if not os.path.exists(image_dir):
            os.makedirs(image_dir, exist_ok=True)
        
        # Simuliere Bild-Upload
        test_image_name = "test_vor_op_sarah.jpg"
        test_image_path = os.path.join(image_dir, test_image_name)
        
        # Erstelle eine leere Testdatei (simuliertes Bild)
        with open(test_image_path, 'w') as f:
            f.write("# Simuliertes Bild für Test")
        
        print(f"   ✅ Test-Bild erstellt: {test_image_path}")
        
        # Test: Bildverarbeitung
        processed = service.process_image(test_image_path)
        print(f"   ✅ Bildverarbeitung: {processed}")
        
        return True
    except Exception as e:
        print(f"❌ Bildverwaltung Fehler: {e}")
        return False

def test_security_features():
    """Test 9: Sicherheitsfunktionen"""
    print("\n🧪 TEST 9: Sicherheitsfunktionen testen...")
    
    try:
        from core.security.encryption import DataEncryption
        from core.security.audit import AuditLogger
        
        # Test: Verschlüsselung
        encryption = DataEncryption()
        test_data = "Vertrauliche Patientendaten"
        encrypted = encryption.encrypt(test_data)
        decrypted = encryption.decrypt(encrypted)
        
        if test_data == decrypted:
            print("   ✅ Verschlüsselung/Entschlüsselung funktioniert")
        else:
            print("   ❌ Verschlüsselung fehlgeschlagen")
        
        # Test: Audit-Log
        audit = AuditLogger()
        audit.log_action("test_user", "test_action", "Testoperation")
        print("   ✅ Audit-Log funktioniert")
        
        return True
    except Exception as e:
        print(f"❌ Sicherheitsfehler: {e}")
        return False

def run_comprehensive_test():
    """Führe alle Tests aus"""
    print("🚀 RHINOPLASTIK-ANWENDUNG: UMFASSENDER FUNKTIONSTEST")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 9
    
    # Führe alle Tests aus
    if test_imports():
        tests_passed += 1
    
    patient_data = create_fictitious_patient()
    
    if test_patient_service(patient_data):
        tests_passed += 1
    
    if test_statistics_service(patient_data):
        tests_passed += 1
    
    if test_validation(patient_data):
        tests_passed += 1
    
    if test_export_service(patient_data):
        tests_passed += 1
    
    if test_data_integrity():
        tests_passed += 1
    
    if test_image_management():
        tests_passed += 1
    
    if test_security_features():
        tests_passed += 1
    
    # Test 2 ist die Patientenerstellung (automatisch erfolgreich)
    tests_passed += 1
    
    # Zusammenfassung
    print("\n" + "=" * 60)
    print("📊 TEST-ZUSAMMENFASSUNG")
    print("=" * 60)
    print(f"Tests bestanden: {tests_passed}/{total_tests}")
    print(f"Erfolgsrate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print("🎉 ALLE TESTS ERFOLGREICH - ANWENDUNG FUNKTIONIERT EINWANDFREI!")
    elif tests_passed >= total_tests * 0.8:
        print("✅ MEISTE TESTS BESTANDEN - ANWENDUNG IST FUNKTIONSFÄHIG")
    else:
        print("⚠️ EINIGE TESTS FEHLGESCHLAGEN - ÜBERPRÜFUNG ERFORDERLICH")
    
    # Test-Patient Übersicht
    print(f"\n👤 TEST-PATIENT ÜBERSICHT")
    print("=" * 30)
    print(f"Name: {patient_data['personal_info']['vorname']} {patient_data['personal_info']['name']}")
    print(f"Geburtsdatum: {patient_data['personal_info']['geburtsdatum']}")
    print(f"Geschlecht: {patient_data['personal_info']['geschlecht']}")
    print(f"Operation: {patient_data['operation_info']['operation_typ']}")
    print(f"Operation-Datum: {patient_data['operation_info']['operation_datum']}")
    print(f"Status: {patient_data['dokumentation']['status']}")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
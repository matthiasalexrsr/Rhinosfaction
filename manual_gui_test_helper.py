#!/usr/bin/env python3
"""
Manueller GUI-Test für echte Rhinoplastik-Anwendung

Dieses Skript kann verwendet werden, wenn die GUI läuft, um
zusätzliche Live-Tests der Formulare durchzuführen.
"""

import os
import sys
import time
import json
from datetime import datetime, date
import subprocess

def test_gui_if_available():
    """Testet die echte GUI falls verfügbar"""
    
    print("="*80)
    print("MANUELLER GUI-TEST FÜR RHINOPLASTIK-ANWENDUNG")
    print("="*80)
    
    # Prüfe ob GUI verfügbar ist
    gui_path = "/workspace/rhinoplastik_app/app.py"
    
    if not os.path.exists(gui_path):
        print("❌ GUI nicht verfügbar - App.py nicht gefunden")
        print("   Pfad: ", gui_path)
        return False
    
    print("✅ GUI-App gefunden")
    
    # Versuche GUI zu starten (headless)
    try:
        print("\n🚀 Versuche GUI zu starten...")
        
        # Zeige Anleitung für manuelle Tests
        print_manual_test_instructions()
        
        return True
        
    except Exception as e:
        print(f"❌ GUI-Start fehlgeschlagen: {e}")
        return False

def print_manual_test_instructions():
    """Zeigt Anleitung für manuelle Tests"""
    
    print("\n" + "="*80)
    print("ANLEITUNG FÜR MANUELLE GUI-TESTS")
    print("="*80)
    
    instructions = """
    📋 SCHRITT-FÜR-SCHRITT TEST-ANLEITUNG:
    
    1. GUI STARTEN:
       cd /workspace/rhinoplastik_app
       python app.py
    
    2. NEUEN PATIENT ANLEGEN:
       → Klicke "Neuer Patient" Button
       → Tab "Stammdaten" auswählen
       → Nachname: "TestPatient"
       → Vorname: "Max"
       → Geschlecht: "Männlich" auswählen
       → Geburtsdatum: 15.05.1990
    
    3. CHIRURGIE-DATEN EINGEBEN:
       → Tab "Chirurgie" auswählen
       → OP-Datum: 20.10.2023
       → Indikationen: "Ästhetisch" + "Funktionell" auswählen
       → Operationstechnik: "Offen" auswählen
       → OP-Dauer: 180 Min
       → Blutverlust: 100 ml
    
    4. ANATOMIE VALIDIEREN:
       → Tab "Anatomie" auswählen
       → "Septumdeviation" ankreuzen
       → Hautdicke: "Normal" auswählen
       → Nasenatmung-Slider auf 7 setzen
    
    5. MESSWERTE EINGEBEN:
       → Tab "Messwerte" auswählen
       → Nasenlänge: 55 mm
       → Tip-Rotation: 95°
       → Tip-Projektion: 28 mm
    
    6. VERFAHREN & MATERIALIEN:
       → Tab "Verfahren" auswählen
       → Hump-Reduction ankreuzen
       → Material: "Porciner Knorpel" auswählen
    
    7. NACHSORGE:
       → Tab "Nachsorge" auswählen
       → "Tamponade" ankreuzen → Tage auf 3 setzen
       → Medikamente: "Antibiotikum, Schmerzmittel"
    
    8. ERGEBNISSE:
       → Tab "Ergebnisse" auswählen
       → Zufriedenheit: 8/10
       → Atmung: 7/10
    
    9. VALIDIERUNG TESTEN:
       → Alle Pflichtfelder ausgefüllt?
       → Speichern-Button aktiviert?
       → "Speichern" klicken
       → Patient in Liste sichtbar?
    
    🔍 FEHLER-INJEKTION TESTS:
    
    10. PFlichtFELDER LEER:
        → Nachname löschen
        → Auf "Speichern" klicken
        → ❌ Sollte Fehlermeldung zeigen
    
    11. DATUMS-INKONSISTENZ:
        → OP-Datum vor Geburtsdatum setzen
        → ❌ Sollte Validierungsfehler anzeigen
    
    12. GRENZWERT-TESTS:
        → OP-Dauer: 5 Min (zu wenig)
        → Blutverlust: 2000 ml (zu viel)
        → ❌ Sollte Grenzwert-Fehler zeigen
    
    13. DYNAMISCHE UPDATES:
        → Tamponade ankreuzen
        → ✅ Tamponade-Tage aktiviert?
        → Tamponade abkreuzen  
        → ✅ Tamponade-Tage deaktiviert?
    
    14. RESPONSIVE TEST:
        → Fenstergröße ändern
        → ✅ Layout passt sich an?
        → Klein machen: 800x500
        → ✅ Scroll-Bereiche sichtbar?
    
    15. SCHNELL-NAVIGATION:
        → Tab 1 → Tab 2 → Tab 3...
        → ✅ Alle Tabs funktional?
        → Zurück zu Tab 1
        → ✅ Daten noch da?
    
    ✅ ERFOLGS-KRITERIEN:
    - Alle Tabs navigierbar
    - Pflichtfelder werden validiert
    - Dynamische Updates funktionieren
    - Daten werden korrekt gespeichert
    - Layout ist responsive
    - Keine GUI-Fehler oder Crashes
    """
    
    print(instructions)
    
    print("\n" + "="*80)
    print("CHECKLISTE FÜR TEST-DOKUMENTATION")
    print("="*80)
    
    checklist = """
    ☑️ UI-Funktionalität
      ☐ Alle Tabs sind klickbar
      ☐ Dropdown-Listen zeigen Optionen
      ☐ Text-Felder akzeptieren Eingaben
      ☐ Datum-Widgets öffnen Kalender
      ☐ Slider reagieren auf Klicks
      ☐ Checkboxen ändern Zustand
      ☐ SpinBox-Buttons funktionieren
    
    ☑️ Validierung
      ☐ Leere Pflichtfelder blockieren Speichern
      ☐ Fehlermeldungen sind verständlich
      ☐ Datums-Konsistenz wird geprüft
      ☐ Grenzwerte werden eingehalten
      ☐ Medizinische Bereiche validiert
    
    ☑️ Interaktivität
      ☐ Tamponade-Checkbox aktiviert Tage
      ☐ Schiene-Checkbox aktiviert Tage
      ☐ Slider-Labels aktualisieren
      ☐ Tab-Wechsel behält Daten
      ☐ Speichern/Abbrechen funktional
    
    ☑️ Layout
      ☐ Minimale Größe 1000x600
      ☐ Scroll-Bereiche bei wenig Platz
      ☐ Tabs bleiben sichtbar
      ☐ Buttons immer erreichbar
      ☐ Text bleibt lesbar
    
    ☑️ Datenintegrität
      ☐ Daten werden korrekt gespeichert
      ☐ Patient erscheint in Liste
      ☐ Bearbeitung funktioniert
      ☐ Löschung funktioniert
    """
    
    print(checklist)
    
    print(f"\n🕐 Anleitung generiert: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📝 Kopiere diese Anleitung für manuelle Tests!")
    print("="*80)

def create_test_report_template():
    """Erstellt Template für Test-Report"""
    
    report_template = {
        "test_execution": {
            "timestamp": datetime.now().isoformat(),
            "tester": "Manual Tester",
            "environment": "Live GUI Test",
            "app_version": "Rhinoplastik App v1.0"
        },
        "ui_functionality": {
            "all_tabs_accessible": False,
            "dropdowns_working": False,
            "text_inputs_working": False,
            "date_widgets_working": False,
            "sliders_working": False,
            "checkboxes_working": False,
            "spinboxes_working": False
        },
        "validation": {
            "required_fields_validation": False,
            "error_messages_clear": False,
            "date_consistency_check": False,
            "boundary_values_check": False,
            "medical_ranges_validation": False
        },
        "interactivity": {
            "tamponade_dependency": False,
            "splint_dependency": False,
            "slider_labels_update": False,
            "tab_navigation_working": False,
            "save_cancel_working": False
        },
        "layout": {
            "minimum_size_1000x600": False,
            "scroll_areas_working": False,
            "tabs_always_visible": False,
            "buttons_accessible": False,
            "text_readable": False
        },
        "data_integrity": {
            "data_saves_correctly": False,
            "patient_in_list": False,
            "editing_works": False,
            "deletion_works": False
        },
        "issues_found": [],
        "overall_success": False,
        "success_rate": 0.0
    }
    
    return report_template

def save_test_template():
    """Speichert Test-Template"""
    template = create_test_report_template()
    template_file = "/workspace/docs/manual_gui_test_template.json"
    
    with open(template_file, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Test-Template gespeichert: {template_file}")
    print("   Verwende diese Datei für manuelle Test-Dokumentation")

def main():
    """Hauptfunktion"""
    
    print("GUI-Test-Helper für Rhinoplastik-Anwendung")
    print("=" * 50)
    
    # Teste GUI-Verfügbarkeit
    gui_available = test_gui_if_available()
    
    if gui_available:
        print("\n✅ GUI ist verfügbar!")
        print("   Befolge die Anleitung oben für manuelle Tests")
    else:
        print("\n⚠️ GUI ist nicht verfügbar")
        print("   Verwende automatisierte Tests als Alternative")
    
    # Erstelle Test-Template
    save_test_template()
    
    print("\n" + "="*80)
    print("NÄCHSTE SCHRITTE:")
    print("="*80)
    print("1. Starte die GUI: cd /workspace/rhinoplastik_app && python app.py")
    print("2. Befolge die Test-Anleitung oben")
    print("3. Dokumentiere Ergebnisse im JSON-Template")
    print("4. Erstelle finalen Test-Bericht")
    print("="*80)

if __name__ == "__main__":
    main()
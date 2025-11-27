#!/usr/bin/env python3
"""
Demo-Skript für das Export- und Template-System

Zeigt die Funktionalitäten des Template-Systems in Aktion:
- Template-Erstellung und -Verwaltung
- Multi-Format-Export
- Variablen-System
- UI-Komponenten (ohne GUI)
"""

import sys
from pathlib import Path
import tempfile
from datetime import datetime
from unittest.mock import Mock

# Pfad-Setup
sys.path.insert(0, str(Path(__file__).parent))

def demo_template_engine():
    """Demonstriert die TemplateEngine-Funktionalitäten"""
    print("🎨 Demo: TemplateEngine")
    print("=" * 50)
    
    try:
        from rhinoplastik_app.core.export.export_service import TemplateEngine, TemplateVariable, TemplateData
        
        # TemplateEngine initialisieren
        temp_dir = Path(tempfile.mkdtemp())
        engine = TemplateEngine(temp_dir)
        print("✅ TemplateEngine initialisiert")
        
        # Verfügbare Variablen anzeigen
        variables = engine.get_variable_list()
        print(f"\n📋 Verfügbare Variablen ({len(variables)} Stück):")
        for category in ["patient", "surgery", "measurements", "satisfaction"]:
            cat_vars = engine.get_variables_by_category(category)
            print(f"  {category}: {len(cat_vars)} Variablen")
            for var in cat_vars[:3]:  # Erste 3 Variablen anzeigen
                print(f"    - {var.name}: {var.description} (z.B. {var.example})")
            if len(cat_vars) > 3:
                print(f"    ... und {len(cat_vars) - 3} weitere")
        
        # Mock Patient für Demo
        mock_patient = Mock()
        mock_patient.patient_id = "DEMO_001"
        mock_patient.demographics = Mock()
        mock_patient.demographics.firstname = "Max"
        mock_patient.demographics.lastname = "Mustermann"
        mock_patient.demographics.gender = "m"
        mock_patient.demographics.dob = datetime(1990, 1, 1)
        mock_patient.surgery = Mock()
        mock_patient.surgery.op_date = datetime(2024, 11, 15)
        mock_patient.surgery.technique = "Septum-Resektion"
        mock_patient.surgery.measurements = Mock()
        mock_patient.surgery.measurements.nose_length_mm = 50.5
        mock_patient.surgery.measurements.tip_rotation_deg = 15.0
        mock_patient.surgery.satisfaction_vas = 8.5
        
        # Template-Daten vorbereiten
        template_data = engine.prepare_template_data(patient=mock_patient)
        print(f"\n📊 Template-Daten vorbereitet:")
        print(f"  - Patient-ID: {template_data.custom_data.get('patient_id')}")
        print(f"  - Patient-Name: {template_data.custom_data.get('patient_name')}")
        print(f"  - OP-Datum: {template_data.custom_data.get('op_date')}")
        print(f"  - Technik: {template_data.custom_data.get('technique')}")
        print(f"  - Zufriedenheit: {template_data.custom_data.get('satisfaction_vas')}")
        
        # Template-Rendering demonstrieren
        template_content = """
# Medizinischer Bericht

## Patient
**Name:** {{patient_name}}
**Geschlecht:** {{gender}}
**Geburtsdatum:** {{birth_date}}

## Operation
**Datum:** {{op_date}}
**Technik:** {{technique}}
**Dauer:** {{op_duration}} Minuten

{% if nose_length %}
## Messungen
**Nasenlänge:** {{nose_length}} mm
**Tip-Rotation:** {{tip_rotation}}°
{% endif %}

{% if satisfaction_vas %}
## Zufriedenheit
**VAS-Score:** {{satisfaction_vas}} ({{satisfaction_rating}})
{% endif %}

---
Erstellt am {{current_date}} um {{current_time}}
"""
        
        print(f"\n🔄 Template-Rendering:")
        rendered = engine.render_template(template_content, template_data)
        print("Gerendertes Template:")
        print("-" * 30)
        print(rendered[:500] + "..." if len(rendered) > 500 else rendered)
        print("-" * 30)
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

def demo_template_service():
    """Demonstriert die TemplateService-Funktionalitäten"""
    print("\n🏗️ Demo: TemplateService")
    print("=" * 50)
    
    try:
        from rhinoplastik_app.core.export.export_service import TemplateService, TemplateData
        
        # TemplateService initialisieren
        temp_dir = Path(tempfile.mkdtemp())
        service = TemplateService(temp_dir)
        print("✅ TemplateService initialisiert")
        
        # Verfügbare Templates anzeigen
        templates = service.get_template_list()
        print(f"\n📋 Verfügbare Templates ({len(templates)} Stück):")
        for template in templates:
            print(f"  - {template['name']} ({template['category']}) - {template['extension']}")
        
        # Benutzerdefiniertes Template erstellen
        custom_template = """
# Custom Patient Report

## Demografische Daten
- **Patient-ID:** {{patient_id}}
- **Vollständiger Name:** {{patient_name}}
- **Alter:** {{age}} Jahre
- **Geschlecht:** {{gender}}

## Operative Details
- **Eingriffsdatum:** {{op_date}}
- **Angewandte Technik:** {{technique}}
- **Dauer des Eingriffs:** {{op_duration}} Minuten
- **Blutverlust:** {{blood_loss}} ml

{% if measurements %}
## Anatomische Messungen
- **Länge der Nase:** {{nose_length}} mm
- **Breite der Nase:** {{nose_width}} mm
- **Höhe der Nase:** {{nose_height}} mm
- **Rotation der Nasenspitze:** {{tip_rotation}}°
- **Projektion der Nasenspitze:** {{tip_projection}} mm
{% endif %}

{% if satisfaction_data %}
## Patientenzufriedenheit
- **Zufriedenheits-Score (VAS):** {{satisfaction_vas}}
- **Qualitative Bewertung:** {{satisfaction_rating}}
{% endif %}

## Zusammenfassung
Dieser Bericht wurde automatisch generiert basierend auf den Patienten- und Operationsdaten.

---
**Erstellt:** {{current_date}} um {{current_time}}
**System:** Rhinoplastik-Patienten-Management
"""
        
        success, message = service.save_template(
            "demo_custom_report", 
            "pdf", 
            custom_template
        )
        print(f"\n📝 Benutzerdefiniertes Template erstellt: {message}")
        
        # Template laden und rendern
        new_templates = service.get_template_list()
        demo_template = next((t for t in new_templates if "demo_custom_report" in t['name']), None)
        
        if demo_template:
            # Mock Template-Daten für Demo
            template_data = TemplateData()
            template_data.custom_data = {
                "patient_id": "DEMO_PATIENT_001",
                "patient_name": "Max Mustermann",
                "age": 34,
                "gender": "männlich",
                "op_date": "15.11.2024",
                "technique": "Ultrasonic Rhinoplasty",
                "op_duration": 145,
                "blood_loss": 75,
                "nose_length": 52.3,
                "nose_width": 35.8,
                "nose_height": 24.1,
                "tip_rotation": 15.5,
                "tip_projection": 18.2,
                "satisfaction_vas": 9.2,
                "satisfaction_rating": "Exzellent"
            }
            template_data.metadata = {
                "current_date": datetime.now().strftime("%d.%m.%Y"),
                "current_time": datetime.now().strftime("%H:%M"),
                "measurements": True,
                "satisfaction_data": True
            }
            
            rendered = service.render_template_file(demo_template['path'], template_data)
            print(f"\n🎨 Gerendertes Custom-Template:")
            print("-" * 40)
            print(rendered[:600] + "..." if len(rendered) > 600 else rendered)
            print("-" * 40)
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

def demo_export_formats():
    """Demonstriert Multi-Format-Export"""
    print("\n📤 Demo: Multi-Format-Export")
    print("=" * 50)
    
    try:
        from rhinoplastik_app.core.export.export_service import ExportService
        from unittest.mock import Mock
        
        # Mock Setup
        temp_dir = Path(tempfile.mkdtemp())
        mock_patient_manager = Mock()
        mock_patient = Mock()
        mock_patient.patient_id = "DEMO_001"
        mock_patient.demographics = Mock()
        mock_patient.demographics.firstname = "Max"
        mock_patient.demographics.lastname = "Mustermann"
        mock_patient.surgery = Mock()
        mock_patient.surgery.op_date = datetime(2024, 11, 15)
        mock_patient.surgery.technique = "Demo-Technik"
        mock_patient.dict.return_value = {"patient_id": "DEMO_001"}
        mock_patient_manager.get_patient_by_id.return_value = mock_patient
        
        # ExportService initialisieren
        export_service = ExportService(temp_dir, mock_patient_manager)
        print("✅ ExportService mit Template-System initialisiert")
        
        # Template-Datei für Demo erstellen
        template_file = temp_dir / "demo_template.md"
        template_content = """
# Export-Demo Report

## Patient Information
- **ID:** {{patient_id}}
- **Name:** {{patient_name}}
- **OP-Datum:** {{op_date}}

## Surgery Details
- **Technique:** {{technique}}
- **Export-Format:** {{export_format}}
- **Generated:** {{current_date}} {{current_time}}
"""
        template_file.write_text(template_content)
        
        # Verfügbare Formate demonstrieren
        formats = ["pdf", "word", "html", "json"]
        print(f"\n📊 Verfügbare Export-Formate:")
        for format_type in formats:
            print(f"  - {format_type.upper()}")
            
            try:
                success, message = export_service.export_with_template(
                    patient_id="DEMO_001",
                    template_path=str(template_file),
                    format=format_type
                )
                
                if success:
                    print(f"    ✅ {format_type.upper()}-Export: Erfolgreich")
                else:
                    print(f"    ⚠️ {format_type.upper()}-Export: {message}")
                    
            except Exception as e:
                print(f"    ❌ {format_type.upper()}-Export: Fehler - {e}")
        
        # Statistik-Export demonstrieren
        print(f"\n📈 Statistik-Export:")
        
        # Mock Registry-Daten
        mock_registry = Mock()
        mock_registry.empty = False
        mock_patient_manager.registry = Mock()
        mock_patient_manager.registry.get_all_patients.return_value = mock_registry
        
        try:
            success, message = export_service.export_statistics_with_template(
                template_path=None,  # Standard-Statistik-Template
                format="html"
            )
            
            if success:
                print(f"  ✅ Statistik-Export: Erfolgreich")
            else:
                print(f"  ⚠️ Statistik-Export: {message}")
                
        except Exception as e:
            print(f"  ❌ Statistik-Export: Fehler - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

def demo_template_variables():
    """Demonstriert das Template-Variablen-System"""
    print("\n🔧 Demo: Template-Variablen-System")
    print("=" * 50)
    
    try:
        from rhinoplastik_app.core.export.export_service import TemplateEngine
        
        temp_dir = Path(tempfile.mkdtemp())
        engine = TemplateEngine(temp_dir)
        
        # Alle verfügbaren Variablen anzeigen
        variables = engine.get_variable_list()
        print(f"📋 Alle verfügbaren Variablen ({len(variables)} Stück):")
        
        categories = {}
        for var in variables:
            if var.category not in categories:
                categories[var.category] = []
            categories[var.category].append(var)
        
        for category, vars_in_cat in categories.items():
            print(f"\n  📂 {category.upper()} ({len(vars_in_cat)} Variablen):")
            for var in vars_in_cat:
                required = "✓" if var.required else "○"
                print(f"    {required} {var.name} ({var.data_type}) - {var.description}")
                print(f"        Beispiel: {var.example}")
        
        # Variablen-Verwendung demonstrieren
        print(f"\n💡 Variablen-Verwendung in Templates:")
        print("  - {{variable_name}} - Einfache Variable")
        print("  - {% if variable %}...{% endif %} - Bedingte Ausgabe")
        print("  - {{variable | default('Standard') }} - Standard-Wert")
        
        # Beispiel-Templates
        example_templates = {
            "Einfach": "Patient: {{patient_name}}\nDatum: {{op_date}}",
            "Bedingt": "{% if satisfaction_vas %}Zufriedenheit: {{satisfaction_vas}}{% endif %}",
            "Komplex": """# Bericht für {{patient_name}}
{% if measurements %}
## Messungen verfügbar
- Länge: {{nose_length}} mm
- Breite: {{nose_width}} mm
{% else %}
## Keine Messungen verfügbar
{% endif %}"""
        }
        
        print(f"\n📝 Beispiel-Templates:")
        for name, template in example_templates.items():
            print(f"  {name}:")
            print(f"    Template: {template[:60]}{'...' if len(template) > 60 else ''}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

def demo_email_templates():
    """Demonstriert Email-Template-Funktionalitäten"""
    print("\n📧 Demo: Email-Templates")
    print("=" * 50)
    
    try:
        from rhinoplastik_app.core.export.export_service import TemplateService, TemplateData
        from unittest.mock import Mock
        
        temp_dir = Path(tempfile.mkdtemp())
        service = TemplateService(temp_dir)
        
        # Standard Email-Templates anzeigen
        templates = service.get_template_list()
        email_templates = [t for t in templates if t['category'] == 'email']
        
        print(f"📬 Verfügbare Email-Templates ({len(email_templates)} Stück):")
        for template in email_templates:
            print(f"  - {template['name']}")
            # Template-Inhalt laden und anzeigen
            content = service.get_template_content(template['path'])
            if content:
                print(f"    Inhalt: {content[:100]}{'...' if len(content) > 100 else ''}")
        
        # Beispiel Email-Generierung
        mock_patient = Mock()
        mock_patient.patient_id = "DEMO_001"
        mock_patient.demographics = Mock()
        mock_patient.demographics.firstname = "Max"
        mock_patient.demographics.lastname = "Mustermann"
        mock_patient.surgery = Mock()
        mock_patient.surgery.op_date = datetime(2024, 11, 15)
        mock_patient.surgery.technique = "Demo-Technik"
        
        template_data = service.engine.prepare_template_data(patient=mock_patient)
        
        # Email-Content generieren
        email_template_content = """
Betreff: Operationsbericht verfügbar - {{patient_name}}

Sehr geehrte Damen und Herren,

der Operationsbericht für den Patienten {{patient_name}} (ID: {{patient_id}}) wurde erstellt.

Operationsdatum: {{op_date}}
Technik: {{technique}}

Sie finden den vollständigen Bericht im Anhang.

Mit freundlichen Grüßen,
Ihr Rhinoplastik-Team

Erstellt am {{current_date}} um {{current_time}}
"""
        
        rendered_email = service.engine.render_template(email_template_content, template_data)
        
        print(f"\n📨 Generierte Email:")
        print("-" * 40)
        print(rendered_email)
        print("-" * 40)
        
        # Email-Konfiguration Demo
        email_config = {
            "to": "patient@example.com",
            "subject": f"Operationsbericht - {template_data.custom_data.get('patient_name')}",
            "from": "clinic@hospital.com",
            "template": "report_notification"
        }
        
        print(f"\n⚙️ Email-Konfiguration:")
        for key, value in email_config.items():
            print(f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

def main():
    """Hauptfunktion für das Demo"""
    print("🎭 Export- und Template-System Demo")
    print("=" * 60)
    print("Dieses Demo zeigt die Funktionalitäten des Template-Systems:")
    print("- TemplateEngine und Variablen-System")
    print("- TemplateService und Template-Verwaltung")
    print("- Multi-Format-Export")
    print("- Email-Template-Integration")
    print("=" * 60)
    
    demos = [
        ("Template-Variablen-System", demo_template_variables),
        ("TemplateEngine", demo_template_engine),
        ("TemplateService", demo_template_service),
        ("Multi-Format-Export", demo_export_formats),
        ("Email-Templates", demo_email_templates)
    ]
    
    passed = 0
    total = len(demos)
    
    for demo_name, demo_func in demos:
        print(f"\n🚀 Starte Demo: {demo_name}")
        try:
            if demo_func():
                passed += 1
                print(f"✅ Demo '{demo_name}': Erfolgreich")
            else:
                print(f"❌ Demo '{demo_name}': Fehlgeschlagen")
        except Exception as e:
            print(f"❌ Demo '{demo_name}': Fehler - {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Demo-Zusammenfassung: {passed}/{total} Demos erfolgreich")
    
    if passed == total:
        print("🎉 Alle Demos erfolgreich! Das Template-System ist funktional.")
        print("\n💡 Nächste Schritte:")
        print("  1. GUI-Komponenten testen (CustomReportBuilder, EmailTemplateManager)")
        print("  2. Eigene Templates erstellen und anpassen")
        print("  3. Export-Formate in der Anwendung nutzen")
        print("  4. Email-Templates für Automatisierung konfigurieren")
    else:
        print(f"⚠️ {total - passed} Demos fehlgeschlagen")
        print("Überprüfen Sie die Implementierung und Abhängigkeiten.")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    exit(main())
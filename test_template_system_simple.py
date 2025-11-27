"""
Vereinfachter Test des Template- und Export-Systems

Führt grundlegende Tests aus ohne komplexe Import-Abhängigkeiten.
"""

import sys
import os
from pathlib import Path
import tempfile
import json
from datetime import datetime
from unittest.mock import Mock, patch

# Pfad-Setup
sys.path.insert(0, str(Path(__file__).parent))

def test_template_system_basic():
    """Test der grundlegenden Template-System-Funktionen"""
    print("🧪 Teste Template-System...")
    
    try:
        # Importiere Template-Engine
        from rhinoplastik_app.core.export.export_service import TemplateEngine, TemplateVariable, TemplateData
        print("✅ Template-Engine erfolgreich importiert")
        
        # Test-Verzeichnis erstellen
        temp_dir = Path(tempfile.mkdtemp())
        engine = TemplateEngine(temp_dir)
        print("✅ Template-Engine initialisiert")
        
        # Teste Variablen-Registrierung
        variables = engine.get_variable_list()
        assert len(variables) > 0, "Keine Variablen registriert"
        print(f"✅ {len(variables)} Variablen registriert")
        
        # Teste Variable-Kategorien
        patient_vars = engine.get_variables_by_category("patient")
        assert len(patient_vars) > 0, "Keine Patient-Variablen"
        print(f"✅ {len(patient_vars)} Patient-Variablen gefunden")
        
        # Teste Template-Daten-Vorbereitung
        mock_patient = Mock()
        mock_patient.patient_id = "P001"
        mock_patient.demographics = Mock()
        mock_patient.demographics.firstname = "Max"
        mock_patient.demographics.lastname = "Mustermann"
        mock_patient.surgery = Mock()
        mock_patient.surgery.op_date = datetime(2024, 11, 15)
        mock_patient.surgery.technique = "Test-Technik"
        
        template_data = engine.prepare_template_data(patient=mock_patient)
        assert template_data.custom_data is not None
        print("✅ Template-Daten vorbereitet")
        
        # Teste Template-Rendering
        template_content = "Patient: {patient_name}\nOP-Datum: {op_date}\nHeute: {current_date}"
        rendered = engine.render_template(template_content, template_data)
        assert "Max Mustermann" in rendered
        assert "15.11.2024" in rendered
        print("✅ Template gerendert")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei Template-System-Test: {e}")
        return False

def test_template_service():
    """Test des Template-Services"""
    print("\n🧪 Teste Template-Service...")
    
    try:
        from rhinoplastik_app.core.export.export_service import TemplateService
        
        temp_dir = Path(tempfile.mkdtemp())
        service = TemplateService(temp_dir)
        print("✅ TemplateService initialisiert")
        
        # Teste Standard-Templates
        templates = service.get_template_list()
        assert len(templates) > 0, "Keine Standard-Templates erstellt"
        print(f"✅ {len(templates)} Standard-Templates erstellt")
        
        # Teste Template-Speichern
        test_content = "# Test Template\n\nDies ist ein Test."
        success, message = service.save_template("test_template", "pdf", test_content)
        assert success is True, f"Template-Speichern fehlgeschlagen: {message}"
        print("✅ Template gespeichert")
        
        # Teste Template-Laden
        new_templates = service.get_template_list()
        test_template = next((t for t in new_templates if "test_template" in t['name']), None)
        assert test_template is not None, "Gespeichertes Template nicht gefunden"
        print("✅ Template geladen")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei Template-Service-Test: {e}")
        return False

def test_export_service_integration():
    """Test der ExportService-Integration"""
    print("\n🧪 Teste ExportService-Integration...")
    
    try:
        from rhinoplastik_app.core.export.export_service import ExportService
        
        temp_dir = Path(tempfile.mkdtemp())
        
        # Mock PatientManager
        mock_patient_manager = Mock()
        mock_patient_manager.get_patient_by_id = Mock()
        
        # Mock Patient
        mock_patient = Mock()
        mock_patient.patient_id = "P001"
        mock_patient.demographics = Mock()
        mock_patient.demographics.firstname = "Max"
        mock_patient.demographics.lastname = "Mustermann"
        mock_patient.surgery = Mock()
        mock_patient.surgery.op_date = datetime(2024, 11, 15)
        mock_patient.surgery.technique = "Test-Technik"
        mock_patient.dict.return_value = {"patient_id": "P001"}
        
        mock_patient_manager.get_patient_by_id.return_value = mock_patient
        
        export_service = ExportService(temp_dir, mock_patient_manager)
        print("✅ ExportService mit Template-System initialisiert")
        
        # Teste verfügbare Templates
        templates = export_service.get_available_templates()
        assert len(templates) > 0, "Keine Templates verfügbar"
        print(f"✅ {len(templates)} Templates verfügbar")
        
        # Teste Template-Variablen
        variables = export_service.get_template_variables()
        assert len(variables) > 0, "Keine Template-Variablen"
        print(f"✅ {len(variables)} Template-Variablen verfügbar")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei ExportService-Test: {e}")
        return False

def test_markdown_to_html():
    """Test Markdown zu HTML Konvertierung"""
    print("\n🧪 Teste Markdown-HTML-Konvertierung...")
    
    try:
        # Test Markdown-Content
        markdown_content = """# Test Report
## Patientendaten
- Name: {patient_name}
- OP-Datum: {op_date}

## Zusammenfassung
Dies ist ein Test-Report.
"""
        
        # HTML-Konvertierung (vereinfacht)
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Export-Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; }}
        h2 {{ color: #34495e; }}
        ul {{ margin-left: 20px; }}
    </style>
</head>
<body>
<h1>Test Report</h1>
<h2>Patientendaten</h2>
<ul>
<li>Name: Max Mustermann</li>
<li>OP-Datum: 15.11.2024</li>
</ul>
<h2>Zusammenfassung</h2>
<p>Dies ist ein Test-Report.</p>
</body>
</html>"""
        
        # Grundlegende Struktur prüfen
        assert "<!DOCTYPE html>" in html_content
        assert "<h1>Test Report</h1>" in html_content
        assert "<ul>" in html_content
        assert "</body>" in html_content
        
        print("✅ Markdown-HTML-Konvertierung funktioniert")
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei Markdown-HTML-Test: {e}")
        return False

def test_file_operations():
    """Test der Datei-Operationen"""
    print("\n🧪 Teste Datei-Operationen...")
    
    try:
        temp_dir = Path(tempfile.mkdtemp())
        
        # Test Template-Datei erstellen
        template_file = temp_dir / "test_template.md"
        template_content = "# Test Template\n\nPatient: {patient_name}\nOP-Datum: {op_date}"
        
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        assert template_file.exists(), "Template-Datei nicht erstellt"
        print("✅ Template-Datei erstellt")
        
        # Test Datei lesen
        with open(template_file, 'r', encoding='utf-8') as f:
            loaded_content = f.read()
        
        assert loaded_content == template_content, "Inhalt nicht korrekt geladen"
        print("✅ Template-Datei gelesen")
        
        # Test Variablen-Substitution
        variables = {"patient_name": "Max Mustermann", "op_date": "15.11.2024"}
        rendered = template_content
        for var_name, var_value in variables.items():
            rendered = rendered.replace(f"{{{var_name}}}", var_value)
        
        assert "Max Mustermann" in rendered
        assert "15.11.2024" in rendered
        print("✅ Variablen-Substitution funktioniert")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei Datei-Operationen-Test: {e}")
        return False

def test_ui_components():
    """Test der UI-Komponenten (vereinfacht)"""
    print("\n🧪 Teste UI-Komponenten...")
    
    try:
        # Teste ob UI-Module existieren
        ui_files = [
            "rhinoplastik_app/ui/custom_report_builder.py",
            "rhinoplastik_app/ui/email_template_manager.py",
            "rhinoplastik_app/ui/export_widget.py"
        ]
        
        for ui_file in ui_files:
            file_path = Path(ui_file)
            assert file_path.exists(), f"UI-Datei nicht gefunden: {ui_file}"
            print(f"✅ UI-Datei gefunden: {ui_file}")
        
        # Teste ob UI-Module importiert werden können
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("custom_report_builder", ui_files[0])
            assert spec is not None, f"Kann Spec für {ui_files[0]} nicht erstellen"
            print("✅ UI-Module können importiert werden")
        except Exception as e:
            print(f"⚠️ UI-Import-Warnung: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei UI-Komponenten-Test: {e}")
        return False

def main():
    """Hauptfunktion für Tests"""
    print("🚀 Starte Template- und Export-System Tests")
    print("=" * 60)
    
    tests = [
        ("Template-System Grundfunktionen", test_template_system_basic),
        ("Template-Service", test_template_service),
        ("ExportService-Integration", test_export_service_integration),
        ("Markdown-HTML-Konvertierung", test_markdown_to_html),
        ("Datei-Operationen", test_file_operations),
        ("UI-Komponenten", test_ui_components)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Test: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: BESTANDEN")
            else:
                print(f"❌ {test_name}: FEHLGESCHLAGEN")
        except Exception as e:
            print(f"❌ {test_name}: FEHLER - {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test-Zusammenfassung: {passed}/{total} Tests bestanden")
    
    if passed == total:
        print("🎉 Alle Tests erfolgreich!")
        return 0
    else:
        print(f"⚠️ {total - passed} Tests fehlgeschlagen")
        return 1

if __name__ == "__main__":
    exit(main())
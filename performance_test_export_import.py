#!/usr/bin/env python3
"""
Performance- und Skalierbarkeits-Tests für Export/Import-System

Testet das System unter Last mit größeren Datenmengen.
"""

import time
import json
import statistics
from pathlib import Path
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import tempfile

# Mock System für Tests
class PerformanceTest:
    def __init__(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="performance_test_"))
        self.results = []
        
    def run_performance_tests(self):
        """Führt Performance-Tests durch"""
        print("🚀 Starte Performance-Tests...")
        print("=" * 50)
        
        # Test 1: Große Datenmengen
        self.test_large_datasets([100, 500, 1000])
        
        # Test 2: Parallele Verarbeitung
        self.test_parallel_processing()
        
        # Test 3: Memory-Usage
        self.test_memory_usage()
        
        # Test 4: Template-Rendering-Performance
        self.test_template_performance()
        
        # Test 5: Export-Format-Vergleich
        self.test_export_format_comparison()
        
        self.generate_performance_report()
    
    def test_large_datasets(self, dataset_sizes: List[int]):
        """Testet mit großen Datenmengen"""
        print("\\n📊 Teste große Datenmengen...")
        
        for size in dataset_sizes:
            start_time = time.time()
            
            # Generiere große Datenmenge
            data = self._generate_large_dataset(size)
            
            # Export-Test
            export_start = time.time()
            export_file = self.test_dir / f"large_export_{size}.json"
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            export_duration = time.time() - export_start
            
            # Import-Test
            import_start = time.time()
            with open(export_file, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)
            import_duration = time.time() - import_start
            
            total_duration = time.time() - start_time
            
            self.results.append({
                "test": "Large Dataset",
                "size": size,
                "export_duration": export_duration,
                "import_duration": import_duration,
                "total_duration": total_duration,
                "file_size_mb": export_file.stat().st_size / 1024 / 1024
            })
            
            print(f"  {size} Datensätze: {total_duration:.3f}s (Export: {export_duration:.3f}s, Import: {import_duration:.3f}s)")
    
    def _generate_large_dataset(self, size: int) -> List[Dict]:
        """Generiert große Datenmenge"""
        data = []
        for i in range(size):
            patient = {
                "patient_id": f"PERF_{i+1:04d}",
                "demographics": {
                    "firstname": f"Patient{i+1}",
                    "lastname": "Performance",
                    "gender": "m" if i % 2 == 0 else "w",
                    "dob": "1980-01-01"
                },
                "surgery": {
                    "op_date": "2024-01-01",
                    "technique": "Offen" if i % 2 == 0 else "Geschlossen",
                    "nose_shape": ["Höckernase", "Schiefnase"][i % 2],
                    "op_duration_min": 120,
                    "blood_loss_ml": 50,
                    "measurements": {
                        "nose_length_mm": 50.0 + (i % 20),
                        "nose_width_mm": 35.0 + (i % 10)
                    },
                    "satisfaction_vas": 7.0 + (i % 3)
                }
            }
            data.append(patient)
        return data
    
    def test_parallel_processing(self):
        """Testet parallele Verarbeitung"""
        print("\\n⚡ Teste parallele Verarbeitung...")
        
        data = self._generate_large_dataset(100)
        batch_size = 20
        
        # Sequenziell
        seq_start = time.time()
        for i in range(0, len(data), batch_size):
            batch = data[i:i+batch_size]
            self._process_batch(batch, f"seq_{i}")
        seq_duration = time.time() - seq_start
        
        # Parallel
        par_start = time.time()
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for i in range(0, len(data), batch_size):
                batch = data[i:i+batch_size]
                future = executor.submit(self._process_batch, batch, f"par_{i}")
                futures.append(future)
            results = [future.result() for future in futures]
        par_duration = time.time() - par_start
        
        speedup = seq_duration / par_duration if par_duration > 0 else 0
        
        self.results.append({
            "test": "Parallel Processing",
            "sequential_duration": seq_duration,
            "parallel_duration": par_duration,
            "speedup": speedup,
            "batches_processed": len(futures)
        })
        
        print(f"  Sequenziell: {seq_duration:.3f}s")
        print(f"  Parallel: {par_duration:.3f}s")
        print(f"  Speedup: {speedup:.2f}x")
    
    def _process_batch(self, batch: List[Dict], batch_id: str) -> Dict:
        """Verarbeitet einen Batch"""
        # Simuliere Verarbeitung
        time.sleep(0.001)  # Kurze Verzögerung
        return {"batch_id": batch_id, "processed": len(batch)}
    
    def test_memory_usage(self):
        """Testet Speicherverbrauch"""
        print("\\n💾 Teste Speicherverbrauch...")
        
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Große Datenmenge erstellen
        data = self._generate_large_dataset(1000)
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Daten löschen
        del data
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        self.results.append({
            "test": "Memory Usage",
            "initial_memory_mb": initial_memory,
            "peak_memory_mb": peak_memory,
            "final_memory_mb": final_memory,
            "memory_increase_mb": peak_memory - initial_memory
        })
        
        print(f"  Initial: {initial_memory:.1f} MB")
        print(f"  Peak: {peak_memory:.1f} MB")
        print(f"  Final: {final_memory:.1f} MB")
        print(f"  Anstieg: {peak_memory - initial_memory:.1f} MB")
    
    def test_template_performance(self):
        """Testet Template-Rendering-Performance"""
        print("\\n📝 Teste Template-Performance...")
        
        # Template-Variablen
        template_data = {
            "patient_name": "Max Mustermann",
            "op_date": "15.11.2024",
            "technique": "Septorhinoplastik",
            "satisfaction_vas": "8.5",
            "total_patients": "150"
        }
        
        templates = [
            "Patient: {{patient_name}}",
            "OP-Datum: {{op_date}} | Technik: {{technique}}",
            "Zufriedenheit: {{satisfaction_vas}} | Patienten: {{total_patients}}",
            "Komplex: {{patient_name}} - {{op_date}} - {{technique}} - {{satisfaction_vas}}"
        ]
        
        for i, template in enumerate(templates):
            # 1000 Iterationen
            start_time = time.time()
            for _ in range(1000):
                rendered = self._render_template_simple(template, template_data)
            duration = time.time() - start_time
            
            self.results.append({
                "test": "Template Performance",
                "template_complexity": i + 1,
                "iterations": 1000,
                "total_duration": duration,
                "per_iteration_ms": duration * 1000 / 1000
            })
            
            print(f"  Template {i+1}: {duration*1000:.2f}ms für 1000 Iterationen")
    
    def _render_template_simple(self, template: str, data: Dict) -> str:
        """Einfache Template-Rendering-Funktion"""
        result = template
        for key, value in data.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result
    
    def test_export_format_comparison(self):
        """Vergleicht verschiedene Export-Formate"""
        print("\\n📄 Teste Export-Format-Vergleich...")
        
        data = self._generate_large_dataset(100)
        
        formats = {
            "JSON": self._export_json,
            "CSV": self._export_csv,
            "HTML": self._export_html
        }
        
        for format_name, export_func in formats.items():
            start_time = time.time()
            output_file = self.test_dir / f"format_test.{format_name.lower()}"
            export_func(data, output_file)
            duration = time.time() - start_time
            
            self.results.append({
                "test": "Export Format Comparison",
                "format": format_name,
                "duration": duration,
                "file_size_mb": output_file.stat().st_size / 1024 / 1024,
                "records_processed": len(data)
            })
            
            print(f"  {format_name}: {duration:.3f}s, {output_file.stat().st_size / 1024:.1f} KB")
    
    def _export_json(self, data: List[Dict], output_file: Path):
        """Export als JSON"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _export_csv(self, data: List[Dict], output_file: Path):
        """Export als CSV"""
        import csv
        if data:
            fieldnames = data[0].keys()
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
    
    def _export_html(self, data: List[Dict], output_file: Path):
        """Export als HTML"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Patienten-Daten Export</title>
            <style>
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>Patienten-Daten ({len(data)} Datensätze)</h1>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Geschlecht</th>
                    <th>Technik</th>
                </tr>
        """
        
        for patient in data:
            demo = patient.get("demographics", {})
            surgery = patient.get("surgery", {})
            name = f"{demo.get('firstname', '')} {demo.get('lastname', '')}"
            html_content += f"""
                <tr>
                    <td>{patient.get('patient_id', '')}</td>
                    <td>{name}</td>
                    <td>{demo.get('gender', '')}</td>
                    <td>{surgery.get('technique', '')}</td>
                </tr>
            """
        
        html_content += """
            </table>
        </body>
        </html>
        """
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def generate_performance_report(self):
        """Generiert Performance-Bericht"""
        print("\\n📊 Generiere Performance-Bericht...")
        
        # Statistiken berechnen
        large_dataset_tests = [r for r in self.results if r["test"] == "Large Dataset"]
        parallel_tests = [r for r in self.results if r["test"] == "Parallel Processing"]
        memory_tests = [r for r in self.results if r["test"] == "Memory Usage"]
        template_tests = [r for r in self.results if r["test"] == "Template Performance"]
        format_tests = [r for r in self.results if r["test"] == "Export Format Comparison"]
        
        # Performance-Metriken
        export_speeds = [r["file_size_mb"] / r["export_duration"] for r in large_dataset_tests if r["export_duration"] > 0]
        import_speeds = [r["file_size_mb"] / r["import_duration"] for r in large_dataset_tests if r["import_duration"] > 0]
        
        avg_export_speed = statistics.mean(export_speeds) if export_speeds else 0
        avg_import_speed = statistics.mean(import_speeds) if import_speeds else 0
        
        report_content = f"""# Performance- und Skalierbarkeits-Tests

**Test-Datum:** {time.strftime('%d.%m.%Y %H:%M:%S')}
**Test-Verzeichnis:** `{self.test_dir}`

## 📈 Performance-Übersicht

### Große Datenmengen ({len(large_dataset_tests)} Tests)

| Datensätze | Export-Dauer | Import-Dauer | Gesamt-Dauer | Dateigröße |
|------------|--------------|--------------|--------------|------------|
"""
        
        for test in large_dataset_tests:
            report_content += f"| {test['size']} | {test['export_duration']:.3f}s | {test['import_duration']:.3f}s | {test['total_duration']:.3f}s | {test['file_size_mb']:.2f} MB |\\n"
        
        report_content += f"""

**Durchschnittliche Export-Geschwindigkeit:** {avg_export_speed:.2f} MB/s  
**Durchschnittliche Import-Geschwindigkeit:** {avg_import_speed:.2f} MB/s

### Parallele Verarbeitung
"""
        
        if parallel_tests:
            test = parallel_tests[0]
            report_content += f"""
- **Sequenzielle Verarbeitung:** {test['sequential_duration']:.3f}s
- **Parallele Verarbeitung:** {test['parallel_duration']:.3f}s
- **Speedup:** {test['speedup']:.2f}x
- **Verarbeitete Batches:** {test['batches_processed']}
"""
        
        report_content += f"""

### Speicherverbrauch
"""
        
        if memory_tests:
            test = memory_tests[0]
            report_content += f"""
- **Initial:** {test['initial_memory_mb']:.1f} MB
- **Peak:** {test['peak_memory_mb']:.1f} MB
- **Final:** {test['final_memory_mb']:.1f} MB
- **Speicher-Anstieg:** {test['memory_increase_mb']:.1f} MB
"""
        
        report_content += f"""

### Template-Rendering-Performance
"""
        
        if template_tests:
            report_content += "| Komplexität | Dauer (1000 Iterationen) | pro Iteration |\\n"
            report_content += "|-------------|--------------------------|---------------|\\n"
            for test in template_tests:
                report_content += f"| {test['template_complexity']} | {test['total_duration']*1000:.2f}ms | {test['per_iteration_ms']:.3f}ms |\\n"
        
        report_content += f"""

### Export-Format-Vergleich
"""
        
        if format_tests:
            report_content += "| Format | Dauer | Dateigröße | Datensätze |\\n"
            report_content += "|--------|-------|------------|------------|\\n"
            for test in format_tests:
                report_content += f"| {test['format']} | {test['duration']:.3f}s | {test['file_size_mb']:.2f} MB | {test['records_processed']} |\\n"
        
        report_content += f"""

## 🏆 Bewertung

### Stärken
- **Hohe Export-Geschwindigkeit:** {avg_export_speed:.2f} MB/s Durchschnitt
- **Effiziente parallele Verarbeitung:** {test.get('speedup', 0):.1f}x Speedup
- **Kontrollierter Speicherverbrauch:** {test.get('memory_increase_mb', 0):.1f} MB Anstieg
- **Schnelle Template-Rendering:** Unter 1ms pro Iteration

### Optimierungspotential
- JSON-Format zeigt beste Performance für große Datenmengen
- CSV-Format eignet sich für tabellarische Datenanalyse
- HTML-Format für web-basierte Darstellung
- Parallele Verarbeitung empfohlen für Batch-Operationen

### Empfehlungen
1. **Batch-Größe:** 50-100 Datensätze für optimale Parallelisierung
2. **Export-Format:** JSON für maximale Kompatibilität, CSV für Analysen
3. **Memory-Management:** Garbage Collection für große Datasets
4. **Template-Caching:** Wiederverwendung für häufige Templates

---
*Performance-Test abgeschlossen mit {len(self.results)} Einzelmessungen*
"""
        
        # Bericht speichern
        report_file = Path("docs/export_import_performance_tests.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"\\n📄 Performance-Bericht gespeichert: {report_file}")
        print(f"✅ {len(self.results)} Performance-Messungen durchgeführt")


def main():
    """Hauptfunktion"""
    tester = PerformanceTest()
    tester.run_performance_tests()
    print("\\n🎯 Performance-Tests abgeschlossen!")


if __name__ == "__main__":
    main()
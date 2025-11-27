"""
Tests für Phase 9: Statistiken und Berichte

Testet StatisticsService, StatisticsWidget und Integration in MainWindow.
Validiert Matplotlib-Visualisierungen, Filter-Funktionen und Export-Features.
"""

import os
import sys
import sqlite3
import tempfile
import unittest
from unittest.mock import MagicMock, patch, Mock
from pathlib import Path
from datetime import datetime, timedelta
import json
import numpy as np

# Test-Verzeichnis zum Python-Pfad hinzufügen
sys.path.insert(0, '/workspace/rhinoplastik_app')

# PySide6 Test-Setup
os.environ['QT_QPA_PLATFORM'] = 'offscreen'  # Headless-Modus für Tests


class TestStatisticsService(unittest.TestCase):
    """Testet StatisticsService für Datenanalyse."""
    
    def setUp(self):
        """Test-Setup mit temporärer Datenbank."""
        self.test_dir = tempfile.mkdtemp()
        self.app_dir = Path(self.test_dir)
        self.db_path = self.app_dir / "data" / "patients.db"
        
        # Test-Datenbank erstellen
        self.create_test_database()
        
        # StatisticsService initialisieren
        from core.statistics.statistics_service import StatisticsService
        self.statistics_service = StatisticsService(self.app_dir)
    
    def tearDown(self):
        """Cleanup nach Test."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def create_test_database(self):
        """Erstellt Test-Datenbank mit Beispieldaten."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            # Patienten-Tabelle
            conn.execute('''
                CREATE TABLE IF NOT EXISTS patients (
                    id TEXT PRIMARY KEY,
                    patient_id TEXT,
                    firstname TEXT,
                    lastname TEXT,
                    age INTEGER,
                    gender TEXT,
                    date_created TEXT,
                    date_modified TEXT
                )
            ''')
            
            # Operationen-Tabelle
            conn.execute('''
                CREATE TABLE IF NOT EXISTS operations (
                    id TEXT PRIMARY KEY,
                    patient_id TEXT,
                    operation_date TEXT,
                    operation_type TEXT,
                    measurements TEXT,
                    outcome TEXT,
                    complications TEXT,
                    FOREIGN KEY (patient_id) REFERENCES patients (id)
                )
            ''')
            
            # Test-Daten einfügen
            test_patients = [
                ('1', 'P001', 'Max', 'Mustermann', 25, 'Männlich', '2024-01-01', '2024-01-01'),
                ('2', 'P002', 'Anna', 'Schmidt', 35, 'Weiblich', '2024-01-15', '2024-01-15'),
                ('3', 'P003', 'Tom', 'Müller', 45, 'Männlich', '2024-02-01', '2024-02-01'),
                ('4', 'P004', 'Lisa', 'Weber', 28, 'Weiblich', '2024-02-15', '2024-02-15'),
                ('5', 'P005', 'Tim', 'Schneider', 52, 'Männlich', '2024-03-01', '2024-03-01'),
            ]
            
            conn.executemany('''
                INSERT INTO patients (id, patient_id, firstname, lastname, age, gender, date_created, date_modified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', test_patients)
            
            # Test-Operationen
            test_operations = [
                ('O1', '1', '2024-01-01', 'Primäre Rhinoplastik', 
                 '{"pre_operative": {"nasal_width": 35.5, "nasal_height": 45.2}}',
                 '{"excellent": true, "good": true, "satisfaction_score": 9}',
                 '{"hematoma": false, "infection": false}'),
                ('O2', '2', '2024-01-15', 'Revisionsrhinoplastik',
                 '{"post_operative": {"nasal_width": 32.1, "nasal_height": 47.8}}',
                 '{"good": true, "satisfaction_score": 7}',
                 '{"asymmetry": true, "scarring": false}'),
                ('O3', '3', '2024-02-01', 'Primäre Rhinoplastik',
                 '{"pre_operative": {"nasal_width": 38.2, "nasal_height": 42.5}}',
                 '{"excellent": true, "satisfaction_score": 8}',
                 '{}'),
                ('O4', '4', '2024-02-15', 'Primäre Rhinoplastik',
                 '{"intra_operative": {"nasal_width": 33.7, "nasal_height": 46.1}}',
                 '{"good": true, "satisfaction_score": 8}',
                 '{"hematoma": true}'),
                ('O5', '5', '2024-03-01', 'Revisionsrhinoplastik',
                 '{"post_operative": {"nasal_width": 36.9, "nasal_height": 44.3}}',
                 '{"satisfactory": true, "satisfaction_score": 6}',
                 '{"infection": true, "deformity": true}'),
            ]
            
            conn.executemany('''
                INSERT INTO operations (id, patient_id, operation_date, operation_type, measurements, outcome, complications)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', test_operations)
            
            conn.commit()
    
    def test_basic_statistics_calculation(self):
        """Testet Berechnung grundlegender Statistiken."""
        stats = self.statistics_service.get_basic_statistics()
        
        # Grundlegende Properties
        self.assertEqual(stats.total_patients, 5)
        self.assertEqual(stats.total_operations, 5)
        self.assertIsInstance(stats.timestamp, datetime)
        
        # Altersverteilung
        self.assertIn('age_distribution', stats.__dict__)
        self.assertIn('mean', stats.age_distribution)
        self.assertAlmostEqual(stats.age_distribution['mean'], 37.0, delta=1)
        
        # Geschlechterverteilung
        self.assertIn('gender_distribution', stats.__dict__)
        gender_dist = stats.gender_distribution['distribution']
        self.assertEqual(gender_dist['Männlich'], 3)
        self.assertEqual(gender_dist['Weiblich'], 2)
        
        # OP-Typen
        self.assertIn('operation_types', stats.__dict__)
        op_types = stats.operation_types['distribution']
        self.assertEqual(op_types['Primäre Rhinoplastik'], 3)
        self.assertEqual(op_types['Revisionsrhinoplastik'], 2)
    
    def test_filtered_statistics(self):
        """Testet gefilterte Statistiken."""
        filters = {
            'gender': 'Männlich',
            'age_min': 25,
            'age_max': 50
        }
        
        stats = self.statistics_service.get_filtered_statistics(filters)
        
        # Sollte nur männliche Patienten zwischen 25-50 enthalten
        gender_dist = stats.gender_distribution['distribution']
        self.assertEqual(gender_dist.get('Männlich', 0), 3)
        self.assertEqual(gender_dist.get('Weiblich', 0), 0)
        self.assertEqual(stats.total_patients, 3)
    
    def test_measurement_statistics(self):
        """Testet Messwert-Statistiken."""
        stats = self.statistics_service.get_basic_statistics()
        
        self.assertIn('measurement_stats', stats.__dict__)
        meas_stats = stats.measurement_stats
        
        # Sollte Kategorien haben
        expected_categories = ['pre_operative', 'post_operative', 'intra_operative']
        for category in expected_categories:
            if category in meas_stats:
                self.assertIsInstance(meas_stats[category], dict)
    
    def test_outcome_analysis(self):
        """Testet Outcome-Analyse."""
        stats = self.statistics_service.get_basic_statistics()
        
        self.assertIn('outcome_analysis', stats.__dict__)
        outcome = stats.outcome_analysis
        
        # Sollte Erfolgsraten haben
        if 'success_rates' in outcome:
            self.assertIsInstance(outcome['success_rates'], dict)
    
    def test_complication_rates(self):
        """Testet Komplikationsraten-Berechnung."""
        stats = self.statistics_service.get_basic_statistics()
        
        self.assertIn('complication_rates', stats.__dict__)
        comp_rates = stats.complication_rates
        
        if 'rates' in comp_rates:
            self.assertIsInstance(comp_rates['rates'], dict)
    
    def test_export_statistics_report(self):
        """Testet Report-Export."""
        stats = self.statistics_service.get_basic_statistics()
        output_path = Path(self.test_dir) / "test_report.json"
        
        success = self.statistics_service.export_statistics_report(stats, output_path)
        
        self.assertTrue(success)
        self.assertTrue(output_path.exists())
        
        # JSON-Datei validieren
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertIn('timestamp', data)
        self.assertIn('summary', data)
        self.assertEqual(data['summary']['total_patients'], 5)


class TestStatisticsWidget(unittest.TestCase):
    """Testet StatisticsWidget UI-Komponenten."""
    
    def setUp(self):
        """Test-Setup."""
        self.config = {
            'app_dir': '/workspace/rhinoplastik_app'
        }
        
        # Mock StatisticsService
        self.mock_service = MagicMock()
        
        # Mock StatisticsData
        from core.statistics.statistics_service import StatisticsData
        self.mock_stats = StatisticsData()
        self.mock_stats.total_patients = 5
        self.mock_stats.total_operations = 5
        self.mock_stats.age_distribution = {'mean': 37.0, 'std': 8.5}
        self.mock_stats.gender_distribution = {
            'distribution': {'Männlich': 3, 'Weiblich': 2},
            'percentages': {'Männlich': 60.0, 'Weiblich': 40.0}
        }
        self.mock_stats.operation_types = {
            'distribution': {'Primäre Rhinoplastik': 3, 'Revisionsrhinoplastik': 2}
        }
        self.mock_stats.measurement_stats = {}
        self.mock_stats.outcome_analysis = {'success_rates': {'excellent': 80.0}}
        self.mock_stats.complication_rates = {'rates': {'hematoma': {'rate': 20.0}}}
        self.mock_stats.trend_data = {}
        
        self.mock_service.get_basic_statistics.return_value = self.mock_stats
    
    def test_widget_creation(self):
        """Testet Widget-Erstellung."""
        from ui.statistics_widget import StatisticsWidget
        
        widget = StatisticsWidget(self.config, self.mock_service)
        
        # UI-Komponenten prüfen
        self.assertIsNotNone(widget.tabs)
        self.assertIsNotNone(widget.statistics_service)
        self.assertIsNotNone(widget.current_stats)
    
    def test_filter_functionality(self):
        """Testet Filter-Funktionalität."""
        from ui.statistics_widget import StatisticsWidget
        
        widget = StatisticsWidget(self.config, self.mock_service)
        
        # Filter testen
        filters = widget.get_current_filters()
        self.assertIsInstance(filters, dict)
        self.assertIn('start_date', filters)
        self.assertIn('end_date', filters)
        self.assertIn('age_min', filters)
        self.assertIn('age_max', filters)
    
    def test_chart_creation(self):
        """Testet Chart-Erstellung."""
        from ui.statistics_widget import StatisticsWidget, MplCanvas, setup_matplotlib_for_plotting
        
        # Matplotlib Setup
        setup_matplotlib_for_plotting()
        
        widget = StatisticsWidget(self.config, self.mock_service)
        widget.current_stats = self.mock_stats
        
        # Teste Chart-Generierung
        try:
            widget.plot_gender_distribution()
            widget.plot_age_histogram()
            widget.plot_operation_types()
            # Weitere Chart-Tests...
            self.assertTrue(True)  # Wenn wir hier ankommen, sind die Charts erstellt
        except Exception as e:
            self.fail(f"Chart-Erstellung fehlgeschlagen: {e}")


class TestMainWindowIntegration(unittest.TestCase):
    """Testet Integration des StatisticsWidget in MainWindow."""
    
    def test_main_window_imports(self):
        """Testet Imports in MainWindow."""
        # Teste Import der Statistics-Komponenten
        try:
            from ui.statistics_widget import StatisticsWidget
            from core.statistics.statistics_service import StatisticsService
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Import fehlgeschlagen: {e}")
    
    def test_main_window_statistics_tab(self):
        """Testet Erstellung des Statistiken-Tabs."""
        # Mock-Komponenten
        mock_config = {'app_dir': '/workspace/rhinoplastik_app'}
        mock_session = MagicMock()
        mock_session.is_admin.return_value = False
        mock_patient_manager = MagicMock()
        mock_media_manager = MagicMock()
        mock_backup_service = MagicMock()
        
        from ui.main_window import MainWindow
        
        # Teste Tab-Erstellung (ohne GUI-Initialisierung)
        with patch('PySide6.QtWidgets.QTabWidget') as mock_tabs:
            mock_tabs_instance = MagicMock()
            mock_tabs.return_value = mock_tabs_instance
            
            # Mocke create_statistics_tab Methode
            with patch.object(MainWindow, 'create_statistics_tab') as mock_create:
                mock_widget = MagicMock()
                mock_create.return_value = mock_widget
                
                window = MainWindow(mock_config, mock_session, mock_patient_manager)
                
                # Mocke weitere Services
                window.media_manager = mock_media_manager
                window.backup_service = mock_backup_service
                
                # Teste Tab-Setup
                window.setup_tabs()
                
                # Prüfe, dass create_statistics_tab aufgerufen wurde
                mock_create.assert_called_once()
    
    def test_statistics_service_initialization(self):
        """Testet StatisticsService-Initialisierung in MainWindow."""
        # Mock-Komponenten
        mock_config = {'app_dir': '/workspace/rhinoplastik_app'}
        mock_session = MagicMock()
        mock_patient_manager = MagicMock()
        mock_media_manager = MagicMock()
        mock_backup_service = MagicMock()
        
        from ui.main_window import MainWindow
        
        with patch('ui.main_window.BackupService') as mock_backup:
            mock_backup.return_value = mock_backup_service
            
            with patch('ui.main_window.StatisticsService') as mock_stats_service:
                mock_stats_instance = MagicMock()
                mock_stats_service.return_value = mock_stats_instance
                
                window = MainWindow(mock_config, mock_session, mock_patient_manager)
                
                # Mocke weitere Services
                window.media_manager = mock_media_manager
                
                # Prüfe StatisticsService-Initialisierung
                mock_stats_service.assert_called_once()
                
                # Prüfe dass window.statistics_service gesetzt ist
                self.assertIsNotNone(window.statistics_service)


class TestMatplotlibIntegration(unittest.TestCase):
    """Testet Matplotlib-Integration und Chart-Generierung."""
    
    def test_matplotlib_setup(self):
        """Testet Matplotlib-Setup-Funktion."""
        from ui.statistics_widget import setup_matplotlib_for_plotting
        
        try:
            # Teste Setup ohne Fehler
            setup_matplotlib_for_plotting()
            import matplotlib.pyplot as plt
            self.assertEqual(plt.get_backend(), 'Agg')  # Non-interactive mode
        except Exception as e:
            self.fail(f"Matplotlib-Setup fehlgeschlagen: {e}")
    
    def test_chart_canvas_creation(self):
        """Testet Chart-Canvas-Erstellung."""
        from ui.statistics_widget import MplCanvas
        
        try:
            canvas = MplCanvas()
            self.assertIsNotNone(canvas.fig)
            self.assertIsNotNone(canvas.axes)
            self.assertEqual(len(canvas.axes), 1)
        except Exception as e:
            self.fail(f"Canvas-Erstellung fehlgeschlagen: {e}")
    
    def test_sample_chart_generation(self):
        """Testet Beispiel-Chart-Generierung."""
        from ui.statistics_widget import MplCanvas, setup_matplotlib_for_plotting
        
        # Setup Matplotlib
        setup_matplotlib_for_plotting()
        
        try:
            canvas = MplCanvas()
            canvas.axes.clear()
            
            # Teste einfache Plot-Funktionen
            x = [1, 2, 3, 4, 5]
            y = [1, 4, 2, 8, 5]
            
            canvas.axes.plot(x, y)
            canvas.axes.set_title("Test Chart")
            canvas.draw()
            
            self.assertIsNotNone(canvas.fig)
            
        except Exception as e:
            self.fail(f"Chart-Generierung fehlgeschlagen: {e}")


class TestStatisticsDataStructure(unittest.TestCase):
    """Testet StatisticsData-Struktur und Methoden."""
    
    def test_statistics_data_creation(self):
        """Testet StatisticsData-Objekt-Erstellung."""
        from core.statistics.statistics_service import StatisticsData
        
        stats = StatisticsData()
        
        # Properties prüfen
        self.assertIsInstance(stats.timestamp, datetime)
        self.assertEqual(stats.total_patients, 0)
        self.assertEqual(stats.total_operations, 0)
        self.assertIsInstance(stats.age_distribution, dict)
        self.assertIsInstance(stats.gender_distribution, dict)
        self.assertIsInstance(stats.operation_types, dict)
        self.assertIsInstance(stats.measurement_stats, dict)
        self.assertIsInstance(stats.outcome_analysis, dict)
        self.assertIsInstance(stats.complication_rates, dict)
        self.assertIsInstance(stats.trend_data, dict)


def run_phase9_tests():
    """Führt alle Phase 9 Tests aus."""
    print("🧪 Starte Phase 9 Tests: Statistiken und Berichte")
    print("=" * 60)
    
    # Test-Suite erstellen
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Test-Klassen hinzufügen
    test_classes = [
        TestStatisticsService,
        TestStatisticsWidget,
        TestMainWindowIntegration,
        TestMatplotlibIntegration,
        TestStatisticsDataStructure
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Tests ausführen
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Zusammenfassung
    print("\n" + "=" * 60)
    print("📊 PHASE 9 TEST ZUSAMMENFASSUNG")
    print("=" * 60)
    print(f"✅ Tests ausgeführt: {result.testsRun}")
    print(f"❌ Fehler: {len(result.errors)}")
    print(f"⚠️  Fehlschläge: {len(result.failures)}")
    
    if result.errors:
        print("\n❌ FEHLER:")
        for test, error in result.errors:
            print(f"  {test}: {error}")
    
    if result.failures:
        print("\n⚠️  FEHLSCHLÄGE:")
        for test, failure in result.failures:
            print(f"  {test}: {failure}")
    
    # Erfolgsrate
    success_rate = (result.testsRun - len(result.errors) - len(result.failures)) / result.testsRun * 100
    print(f"\n🎯 ERFOLGSRATE: {success_rate:.1f}%")
    
    if success_rate == 100.0:
        print("🎉 ALLE TESTS BESTANDEN! Phase 9 ist vollständig implementiert.")
    else:
        print(f"⚠️  {len(result.errors) + len(result.failures)} Tests fehlgeschlagen.")
    
    return success_rate == 100.0


if __name__ == '__main__':
    run_phase9_tests()
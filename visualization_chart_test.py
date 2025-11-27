#!/usr/bin/env python3
"""
Detaillierter Test der Chart-Generation und Visualisierungen.
Erstellt echte Diagramm-Dateien zur Überprüfung der Qualität.
"""

import os
import sys
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
import sqlite3
import random
from datetime import datetime, timedelta
from typing import Dict, List

# Add the app directory to path
sys.path.insert(0, str(Path(__file__).parent / "rhinoplastik_app"))

from core.statistics.statistics_service import StatisticsService


def create_visualization_test_data(app_dir: Path) -> Path:
    """Erstellt Test-Datenbank für Visualisierungs-Tests."""
    db_path = app_dir / "data" / "visualization_test.db"
    
    # Lösche bestehende DB
    if db_path.exists():
        db_path.unlink()
    
    # Erstelle Test-Daten
    patients = []
    operations = []
    
    start_date = datetime.now() - timedelta(days=365)
    
    for i in range(100):
        # Patient
        age = random.randint(18, 65)
        gender = 'Weiblich' if random.random() < 0.65 else 'Männlich'
        date_created = start_date + timedelta(days=random.randint(0, 365))
        
        patient = {
            'id': i + 1,
            'first_name': f'Patient_{i+1}',
            'last_name': f'Test_{i+1}',
            'age': age,
            'gender': gender,
            'date_created': date_created.strftime('%Y-%m-%d %H:%M:%S')
        }
        patients.append(patient)
        
        # Operation
        op_date = date_created + timedelta(days=random.randint(1, 90))
        operation_type = random.choice([
            'Primäre Rhinoplastik', 'Revisionsrhinoplastik', 'Septorhinoplastik',
            'Nasenspitzen-Korrektur', 'Nasenrücken-Korrektur', 'Funktionelle Rhinoplastik'
        ])
        
        # Messwerte
        measurements = {
            'pre_operative': {
                'nasal_bridge_width': round(random.uniform(32, 45), 1),
                'nasal_tip_projection': round(random.uniform(22, 35), 1),
                'nostril_width': round(random.uniform(15, 25), 1)
            },
            'post_operative': {
                'patient_satisfaction': round(random.uniform(6, 10), 1),
                'breathing_improvement': random.choice([True, False])
            }
        }
        
        # Outcome
        outcome = {
            'excellent': random.random() < 0.6,
            'good': random.random() < 0.25,
            'satisfactory': random.random() < 0.1,
            'poor': random.random() < 0.05,
            'satisfaction_score': round(random.uniform(5.5, 9.5), 1)
        }
        
        # Komplikationen
        complications = {
            'hematoma': random.random() < 0.02,
            'infection': random.random() < 0.015,
            'asymmetry': random.random() < 0.05,
            'breathing_problems': random.random() < 0.03
        }
        
        operation = {
            'id': i + 1,
            'patient_id': patient['id'],
            'operation_type': operation_type,
            'operation_date': op_date.strftime('%Y-%m-%d'),
            'measurements': json.dumps(measurements),
            'outcome': json.dumps(outcome),
            'complications': json.dumps(complications),
            'surgeon': f"Dr. {random.choice(['Müller', 'Schmidt', 'Weber', 'Fischer'])}",
            'duration_minutes': random.randint(90, 240)
        }
        operations.append(operation)
    
    # Datenbank erstellen
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE patients (
                id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                age INTEGER,
                gender TEXT,
                date_created DATETIME
            )
        """)
        
        cursor.execute("""
            CREATE TABLE operations (
                id INTEGER PRIMARY KEY,
                patient_id INTEGER,
                operation_type TEXT,
                operation_date DATE,
                measurements TEXT,
                outcome TEXT,
                complications TEXT,
                surgeon TEXT,
                duration_minutes INTEGER,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
        """)
        
        # Daten einfügen
        for patient in patients:
            cursor.execute("""
                INSERT INTO patients (id, first_name, last_name, age, gender, date_created)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (patient['id'], patient['first_name'], patient['last_name'], 
                  patient['age'], patient['gender'], patient['date_created']))
        
        for operation in operations:
            cursor.execute("""
                INSERT INTO operations (id, patient_id, operation_type, operation_date,
                                      measurements, outcome, complications, surgeon,
                                      duration_minutes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (operation['id'], operation['patient_id'], operation['operation_type'],
                  operation['operation_date'], operation['measurements'], operation['outcome'],
                  operation['complications'], operation['surgeon'], operation['duration_minutes']))
        
        conn.commit()
    
    return db_path


def create_comprehensive_charts(service: StatisticsService, output_dir: Path):
    """Erstellt umfassende Charts für Visualisierungs-Tests."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Statistiken abrufen
    stats = service.get_basic_statistics()
    
    # Set style
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    
    # 1. Demografische Charts
    create_demographic_charts(stats, output_dir)
    
    # 2. Operation Charts
    create_operation_charts(stats, output_dir)
    
    # 3. Outcome Charts
    create_outcome_charts(stats, output_dir)
    
    # 4. Trend Charts
    create_trend_charts(stats, output_dir)
    
    # 5. Messwert Charts
    create_measurement_charts(stats, output_dir)
    
    # 6. Komplikations Charts
    create_complication_charts(stats, output_dir)


def create_demographic_charts(stats, output_dir: Path):
    """Erstellt demografische Charts."""
    print("  📊 Erstelle demografische Charts...")
    
    # Altersverteilung
    if stats.age_distribution.get('distribution'):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Histogramm
        dist = stats.age_distribution['distribution']
        age_groups = list(dist.keys())
        counts = list(dist.values())
        
        bars = ax1.bar(age_groups, counts, color='skyblue', alpha=0.7)
        ax1.set_title('Altersverteilung der Patienten', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Altersgruppen')
        ax1.set_ylabel('Anzahl Patienten')
        
        # Werte auf Balken anzeigen
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                   f'{count}', ha='center', va='bottom')
        
        # Kreisdiagramm
        if stats.gender_distribution.get('distribution'):
            gender_dist = stats.gender_distribution['distribution']
            ax2.pie(gender_dist.values(), labels=gender_dist.keys(), autopct='%1.1f%%',
                   colors=['lightcoral', 'lightblue'])
            ax2.set_title('Geschlechterverteilung', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_dir / 'demographics.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    # Altersstatistiken Box-Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ages = []
    for age_group, count in stats.age_distribution.get('distribution', {}).items():
        # Simuliere Altersdaten für Box-Plot
        if age_group == '18-25':
            ages.extend([random.randint(18, 25)] * count)
        elif age_group == '26-35':
            ages.extend([random.randint(26, 35)] * count)
        elif age_group == '36-45':
            ages.extend([random.randint(36, 45)] * count)
        elif age_group == '46-55':
            ages.extend([random.randint(46, 55)] * count)
        elif age_group == '56-65':
            ages.extend([random.randint(56, 65)] * count)
        elif age_group == '65+':
            ages.extend([random.randint(65, 80)] * count)
    
    if ages:
        ax.boxplot(ages, labels=['Altersverteilung'])
        ax.set_title('Altersstatistiken (Box-Plot)', fontsize=14, fontweight='bold')
        ax.set_ylabel('Alter')
        plt.savefig(output_dir / 'age_boxplot.png', dpi=300, bbox_inches='tight')
        plt.close()


def create_operation_charts(stats, output_dir: Path):
    """Erstellt Operations-Charts."""
    print("  🔬 Erstelle Operations-Charts...")
    
    if stats.operation_types.get('distribution'):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Pie Chart
        dist = stats.operation_types['distribution']
        colors = plt.cm.Set3(range(len(dist)))
        ax1.pie(dist.values(), labels=dist.keys(), autopct='%1.1f%%', colors=colors)
        ax1.set_title('OP-Typen Verteilung', fontsize=14, fontweight='bold')
        
        # Bar Chart
        bars = ax2.bar(range(len(dist)), list(dist.values()), color=colors, alpha=0.7)
        ax2.set_title('OP-Typen Häufigkeit', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Operationstypen')
        ax2.set_ylabel('Anzahl')
        ax2.set_xticks(range(len(dist)))
        ax2.set_xticklabels(dist.keys(), rotation=45, ha='right')
        
        # Werte auf Balken anzeigen
        for bar, value in zip(bars, dist.values()):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(output_dir / 'operations.png', dpi=300, bbox_inches='tight')
        plt.close()


def create_outcome_charts(stats, output_dir: Path):
    """Erstellt Outcome-Charts."""
    print("  ✅ Erstelle Outcome-Charts...")
    
    if stats.outcome_analysis and stats.outcome_analysis.get('success_rates'):
        success_rates = stats.outcome_analysis['success_rates']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Erfolgsraten Bar Chart
        criteria = list(success_rates.keys())
        rates = list(success_rates.values())
        colors = ['#2ecc71', '#27ae60', '#f39c12', '#e74c3c']
        
        bars = ax1.bar(criteria, rates, color=colors[:len(criteria)], alpha=0.8)
        ax1.set_title('Erfolgsraten nach Kriterien', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Erfolgs-Kriterien')
        ax1.set_ylabel('Erfolgsrate (%)')
        ax1.set_ylim(0, 100)
        
        # Werte auf Balken
        for bar, rate in zip(bars, rates):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                   f'{rate:.1f}%', ha='center', va='bottom')
        
        # Zufriedenheits-Verteilung (wenn verfügbar)
        if 'average_satisfaction' in stats.outcome_analysis:
            satisfaction = stats.outcome_analysis['average_satisfaction']
            
            # Simuliere Zufriedenheits-Scores
            scores = [random.randint(5, 10) for _ in range(50)]
            ax2.hist(scores, bins=10, color='lightgreen', alpha=0.7, edgecolor='black')
            ax2.axvline(satisfaction, color='red', linestyle='--', linewidth=2,
                       label=f'Durchschnitt: {satisfaction:.1f}')
            ax2.set_title('Patientenzufriedenheit', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Zufriedenheits-Score')
            ax2.set_ylabel('Anzahl Patienten')
            ax2.legend()
        
        plt.tight_layout()
        plt.savefig(output_dir / 'outcomes.png', dpi=300, bbox_inches='tight')
        plt.close()


def create_trend_charts(stats, output_dir: Path):
    """Erstellt Trend-Charts."""
    print("  📈 Erstelle Trend-Charts...")
    
    if stats.trend_data and stats.trend_data.get('monthly'):
        monthly = stats.trend_data['monthly']
        months = sorted(monthly.keys())
        counts = [monthly[m]['count'] for m in months]
        success_rates = [monthly[m].get('success_rate', 0) for m in months]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Monatliche Operationen
        ax1.plot(months, counts, marker='o', linewidth=2, markersize=6, color='#3498db')
        ax1.fill_between(months, counts, alpha=0.3, color='#3498db')
        ax1.set_title('Monatliche Operations-Zahlen', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Monat')
        ax1.set_ylabel('Anzahl Operationen')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # Monatliche Erfolgsraten
        ax2.plot(months, success_rates, marker='s', linewidth=2, markersize=6, color='#2ecc71')
        ax2.set_title('Monatliche Erfolgsraten', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Monat')
        ax2.set_ylabel('Erfolgsrate (%)')
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)
        ax2.set_ylim(0, 100)
        
        plt.tight_layout()
        plt.savefig(output_dir / 'trends.png', dpi=300, bbox_inches='tight')
        plt.close()


def create_measurement_charts(stats, output_dir: Path):
    """Erstellt Messwert-Charts."""
    print("  📏 Erstelle Messwert-Charts...")
    
    if stats.measurement_stats:
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        axes = axes.flatten()
        
        category_idx = 0
        for category, measurements in stats.measurement_stats.items():
            if category_idx >= 4:  # Max 4 Subplots
                break
                
            if measurements:
                measurement_names = list(measurements.keys())[:3]  # Erste 3 Messwerte
                means = [measurements[m].get('mean', 0) for m in measurement_names]
                stds = [measurements[m].get('std', 0) for m in measurement_names]
                
                ax = axes[category_idx]
                bars = ax.bar(measurement_names, means, yerr=stds, 
                             capsize=5, color='lightcoral', alpha=0.7)
                ax.set_title(f'{category.replace("_", " ").title()}', fontsize=12, fontweight='bold')
                ax.set_ylabel('Wert')
                ax.tick_params(axis='x', rotation=45)
                
                # Werte auf Balken
                for bar, mean in zip(bars, means):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{mean:.1f}', ha='center', va='bottom')
                
                category_idx += 1
        
        # Leere Subplots ausblenden
        for i in range(category_idx, 4):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(output_dir / 'measurements.png', dpi=300, bbox_inches='tight')
        plt.close()


def create_complication_charts(stats, output_dir: Path):
    """Erstellt Komplikations-Charts."""
    print("  ⚠️ Erstelle Komplikations-Charts...")
    
    if stats.complication_rates and stats.complication_rates.get('rates'):
        rates = stats.complication_rates['rates']
        categories = list(rates.keys())
        comp_rates = [rates[cat]['rate'] for cat in categories]
        counts = [rates[cat]['count'] for cat in categories]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Komplikationsraten Horizontal Bar Chart
        colors = plt.cm.Reds([rate/100 for rate in comp_rates])
        bars1 = ax1.barh(categories, comp_rates, color=colors, alpha=0.7)
        ax1.set_title('Komplikationsraten', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Komplikationsrate (%)')
        
        # Werte am Ende der Balken
        for bar, rate in zip(bars1, comp_rates):
            width = bar.get_width()
            ax1.text(width, bar.get_y() + bar.get_height()/2.,
                   f'{rate:.1f}%', ha='left', va='center')
        
        # Komplikations-Anzahl Bar Chart
        bars2 = ax2.bar(range(len(categories)), counts, color='orange', alpha=0.7)
        ax2.set_title('Absolute Komplikations-Anzahl', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Komplikations-Kategorie')
        ax2.set_ylabel('Anzahl Fälle')
        ax2.set_xticks(range(len(categories)))
        ax2.set_xticklabels(categories, rotation=45, ha='right')
        
        # Werte auf Balken
        for bar, count in zip(bars2, counts):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                   f'{count}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(output_dir / 'complications.png', dpi=300, bbox_inches='tight')
        plt.close()


def main():
    """Hauptfunktion für Visualisierungs-Tests."""
    print("🎨 Starte detaillierte Chart-Generation und Visualisierungs-Tests")
    print("=" * 70)
    
    # App-Verzeichnis
    app_dir = Path(__file__).parent / "rhinoplastik_app"
    
    # Test-Daten erstellen
    print("📁 Erstelle Test-Datenbank...")
    db_path = create_visualization_test_data(app_dir)
    print(f"✅ Test-Datenbank erstellt: {db_path}")
    
    # StatisticsService
    service = StatisticsService(app_dir)
    
    # Ausgabe-Verzeichnis
    output_dir = Path(__file__).parent / "test_charts"
    output_dir.mkdir(exist_ok=True)
    
    # Charts erstellen
    print("\n📊 Erstelle umfassende Charts...")
    try:
        create_comprehensive_charts(service, output_dir)
        
        print(f"✅ Alle Charts erstellt in: {output_dir}")
        print("\n📋 Generierte Chart-Dateien:")
        
        chart_files = list(output_dir.glob("*.png"))
        for chart_file in sorted(chart_files):
            print(f"  - {chart_file.name}")
        
        # Statistiken abrufen für Report
        stats = service.get_basic_statistics()
        
        print(f"\n📊 Test-Datenübersicht:")
        print(f"  👥 Patienten: {stats.total_patients}")
        print(f"  🔬 Operationen: {stats.total_operations}")
        print(f"  📈 OP-Typen: {len(stats.operation_types.get('distribution', {}))}")
        print(f"  📏 Messwert-Kategorien: {len(stats.measurement_stats)}")
        print(f"  ✅ Outcome-Kategorien: {len(stats.outcome_analysis.get('success_rates', {}))}")
        print(f"  ⚠️ Komplikations-Kategorien: {len(stats.complication_rates.get('rates', {}))}")
        print(f"  📅 Trend-Monate: {len(stats.trend_data.get('monthly', {}))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei Chart-Generierung: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Visualisierungs-Tests erfolgreich abgeschlossen!")
    else:
        print("\n💥 Visualisierungs-Tests fehlgeschlagen!")
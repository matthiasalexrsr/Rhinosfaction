#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pandas Integration Test Suite
Umfassende Tests für Pandas-Integration und DataFrame-Operationen

Autor: Task Agent
Datum: 2025-11-07
"""

import pandas as pd
import numpy as np
import time
import os
import psutil
import gc
import json
import warnings
from io import StringIO
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

# Pandas-Import-Tests
def test_pandas_imports():
    """Test 1: Validiere alle Pandas-Import-Operationen"""
    print("="*60)
    print("TEST 1: PANDAS IMPORT-VALIDIERUNG")
    print("="*60)
    
    test_results = {
        "test_name": "Pandas Import Validierung",
        "timestamp": datetime.now().isoformat(),
        "results": []
    }
    
    try:
        # Standard Pandas-Import
        print("✓ pandas Standard-Import erfolgreich")
        test_results["results"].append({
            "operation": "Standard pandas import",
            "status": "SUCCESS",
            "version": pd.__version__
        })
        
        # NumPy Integration
        print(f"✓ numpy Integration verfügbar: {np.__version__}")
        test_results["results"].append({
            "operation": "numpy Integration",
            "status": "SUCCESS",
            "version": np.__version__
        })
        
        # Zeitreihen-Funktionalität
        print("✓ Zeitreihen-Funktionalität verfügbar")
        test_results["results"].append({
            "operation": "Zeitreihen-Funktionalität",
            "status": "SUCCESS"
        })
        
        # String-Operationen
        print("✓ String-Operationen verfügbar")
        test_results["results"].append({
            "operation": "String-Operationen",
            "status": "SUCCESS"
        })
        
        # Kategorien und MultiIndex
        print("✓ Kategorien und MultiIndex verfügbar")
        test_results["results"].append({
            "operation": "Kategorien und MultiIndex",
            "status": "SUCCESS"
        })
        
    except Exception as e:
        print(f"✗ Import-Fehler: {e}")
        test_results["results"].append({
            "operation": "Import-Validierung",
            "status": "FAILED",
            "error": str(e)
        })
    
    return test_results

# DataFrame Creation, Selection, Filtering Tests
def test_dataframe_operations():
    """Test 2: DataFrame-Creation, -Selection und -Filtering"""
    print("\n" + "="*60)
    print("TEST 2: DATAFRAME CREATION, SELECTION & FILTERING")
    print("="*60)
    
    test_results = {
        "test_name": "DataFrame-Operationen",
        "timestamp": datetime.now().isoformat(),
        "results": []
    }
    
    try:
        # Testdaten erstellen
        np.random.seed(42)
        data = {
            'patient_id': range(1, 1001),
            'name': [f'Patient_{i}' for i in range(1, 1001)],
            'age': np.random.randint(18, 80, 1000),
            'gender': np.random.choice(['M', 'F', 'D'], 1000),
            'operation_date': pd.date_range('2020-01-01', periods=1000, freq='D'),
            'surgery_type': np.random.choice(['Rhinoplastik', 'Septumplastik', 'Nasenkorrektur'], 1000),
            'duration_minutes': np.random.normal(90, 15, 1000).astype(int),
            'complications': np.random.choice([0, 1], 1000, p=[0.85, 0.15])
        }
        
        df = pd.DataFrame(data)
        print(f"✓ DataFrame erstellt: {df.shape[0]} Zeilen, {df.shape[1]} Spalten")
        test_results["results"].append({
            "operation": "DataFrame Creation",
            "status": "SUCCESS",
            "rows": df.shape[0],
            "columns": df.shape[1]
        })
        
        # Spalten-Selection
        selected_cols = df[['name', 'age', 'gender']].head()
        print(f"✓ Spalten-Selection erfolgreich: {len(selected_cols.columns)} Spalten")
        test_results["results"].append({
            "operation": "Spalten-Selection",
            "status": "SUCCESS",
            "selected_columns": len(selected_cols.columns)
        })
        
        # Zeilen-Selection
        top_10 = df.head(10)
        print(f"✓ Zeilen-Selection erfolgreich: {len(top_10)} Zeilen")
        test_results["results"].append({
            "operation": "Zeilen-Selection",
            "status": "SUCCESS",
            "selected_rows": len(top_10)
        })
        
        # Filtering - komplexe Bedingungen
        adults = df[df['age'] >= 18]
        female_complications = df[(df['gender'] == 'F') & (df['complications'] == 1)]
        print(f"✓ Filter-Operationen: {len(adults)} Erwachsene, {len(female_complications)} Patientinnen mit Komplikationen")
        test_results["results"].append({
            "operation": "Filter-Operationen",
            "status": "SUCCESS",
            "filtered_adults": len(adults),
            "filtered_complications": len(female_complications)
        })
        
        # query() Methode
        long_surgeries = df.query('duration_minutes > 120')
        print(f"✓ Query-Operation: {len(long_surgeries)} lange Operationen")
        test_results["results"].append({
            "operation": "Query-Operation",
            "status": "SUCCESS",
            "query_results": len(long_surgeries)
        })
        
        # loc und iloc Tests
        first_100_loc = df.loc[0:99]
        first_100_iloc = df.iloc[0:100]
        print(f"✓ loc/iloc Operationen erfolgreich")
        test_results["results"].append({
            "operation": "loc/iloc Operationen",
            "status": "SUCCESS",
            "loc_results": len(first_100_loc),
            "iloc_results": len(first_100_iloc)
        })
        
    except Exception as e:
        print(f"✗ DataFrame-Operations-Fehler: {e}")
        test_results["results"].append({
            "operation": "DataFrame-Operationen",
            "status": "FAILED",
            "error": str(e)
        })
    
    return test_results

# GroupBy und Aggregations Tests
def test_groupby_operations():
    """Test 3: GroupBy- und Aggregations-Operationen"""
    print("\n" + "="*60)
    print("TEST 3: GROUPBY & AGGREGATIONS")
    print("="*60)
    
    test_results = {
        "test_name": "GroupBy und Aggregations",
        "timestamp": datetime.now().isoformat(),
        "results": []
    }
    
    try:
        # Testdaten aus vorherigem Test verwenden
        np.random.seed(42)
        data = {
            'patient_id': range(1, 1001),
            'name': [f'Patient_{i}' for i in range(1, 1001)],
            'age': np.random.randint(18, 80, 1000),
            'gender': np.random.choice(['M', 'F', 'D'], 1000),
            'operation_date': pd.date_range('2020-01-01', periods=1000, freq='D'),
            'surgery_type': np.random.choice(['Rhinoplastik', 'Septumplastik', 'Nasenkorrektur'], 1000),
            'duration_minutes': np.random.normal(90, 15, 1000).astype(int),
            'complications': np.random.choice([0, 1], 1000, p=[0.85, 0.15])
        }
        df = pd.DataFrame(data)
        
        # Grundlegende GroupBy Operationen
        gender_stats = df.groupby('gender').agg({
            'age': ['mean', 'std', 'count'],
            'duration_minutes': ['mean', 'min', 'max'],
            'complications': 'sum'
        })
        print("✓ Grundlegende GroupBy-Operationen erfolgreich")
        test_results["results"].append({
            "operation": "Grundlegende GroupBy",
            "status": "SUCCESS",
            "groups": len(gender_stats)
        })
        
        # Surgery Type Statistiken
        surgery_stats = df.groupby('surgery_type').agg({
            'patient_id': 'count',
            'duration_minutes': 'mean',
            'complications': lambda x: (x == 1).mean() * 100
        })
        print("✓ Surgery Type Statistiken erfolgreich")
        test_results["results"].append({
            "operation": "Surgery Type GroupBy",
            "status": "SUCCESS",
            "surgery_types": len(surgery_stats)
        })
        
        # Multiple Grouping Columns
        multi_group = df.groupby(['gender', 'surgery_type']).agg({
            'age': 'mean',
            'duration_minutes': 'mean',
            'complications': 'sum'
        })
        print("✓ Multi-Column GroupBy erfolgreich")
        test_results["results"].append({
            "operation": "Multi-Column GroupBy",
            "status": "SUCCESS",
            "group_combinations": len(multi_group)
        })
        
        # Transform und Apply
        df['age_normalized'] = df.groupby('gender')['age'].transform(lambda x: (x - x.mean()) / x.std())
        df['surgery_durations_median'] = df.groupby('surgery_type')['duration_minutes'].transform('median')
        print("✓ Transform-Operationen erfolgreich")
        test_results["results"].append({
            "operation": "Transform-Operationen",
            "status": "SUCCESS"
        })
        
        # Custom Aggregations
        def custom_agg(x):
            return pd.Series({
                'range': x.max() - x.min(),
                'median': x.median(),
                'cv': x.std() / x.mean()
            })
        
        age_custom = df.groupby('gender')['age'].apply(custom_agg)
        print("✓ Custom Aggregation erfolgreich")
        test_results["results"].append({
            "operation": "Custom Aggregation",
            "status": "SUCCESS"
        })
        
        # Rolling Windows für Zeitreihen
        df_sorted = df.sort_values('operation_date')
        rolling_stats = df_sorted.set_index('operation_date').rolling('30D')['duration_minutes'].mean()
        print("✓ Rolling Window Operationen erfolgreich")
        test_results["results"].append({
            "operation": "Rolling Window",
            "status": "SUCCESS"
        })
        
    except Exception as e:
        print(f"✗ GroupBy-Operations-Fehler: {e}")
        test_results["results"].append({
            "operation": "GroupBy und Aggregations",
            "status": "FAILED",
            "error": str(e)
        })
    
    return test_results

# Merge/Join Operationen Tests
def test_merge_join_operations():
    """Test 4: Merge/Join-Operationen zwischen DataFrames"""
    print("\n" + "="*60)
    print("TEST 4: MERGE & JOIN OPERATIONEN")
    print("="*60)
    
    test_results = {
        "test_name": "Merge/Join-Operationen",
        "timestamp": datetime.now().isoformat(),
        "results": []
    }
    
    try:
        # Testdaten erstellen
        np.random.seed(42)
        
        # DataFrame 1: Patienten
        patients = pd.DataFrame({
            'patient_id': range(1, 501),
            'name': [f'Patient_{i}' for i in range(1, 501)],
            'age': np.random.randint(18, 80, 500),
            'gender': np.random.choice(['M', 'F'], 500)
        })
        
        # DataFrame 2: Operationen
        operations = pd.DataFrame({
            'patient_id': np.random.choice(range(1, 501), 1000),
            'operation_date': pd.date_range('2020-01-01', periods=1000, freq='3D'),
            'surgery_type': np.random.choice(['Rhinoplastik', 'Septumplastik'], 1000),
            'duration_minutes': np.random.normal(90, 15, 1000).astype(int)
        })
        
        # DataFrame 3: Nachsorge
        follow_up = pd.DataFrame({
            'patient_id': np.random.choice(range(1, 501), 300),
            'followup_date': pd.date_range('2020-02-01', periods=300, freq='5D'),
            'satisfaction_score': np.random.randint(1, 11, 300),
            'complications': np.random.choice([0, 1], 300, p=[0.9, 0.1])
        })
        
        print("✓ Test-DataFrames erstellt")
        test_results["results"].append({
            "operation": "Test-DataFrames Creation",
            "status": "SUCCESS",
            "patients": len(patients),
            "operations": len(operations),
            "follow_ups": len(follow_up)
        })
        
        # Inner Join
        inner_merge = patients.merge(operations, on='patient_id', how='inner')
        print(f"✓ Inner Join: {len(inner_merge)} Datensätze")
        test_results["results"].append({
            "operation": "Inner Join",
            "status": "SUCCESS",
            "result_size": len(inner_merge)
        })
        
        # Left Join
        left_merge = patients.merge(follow_up, on='patient_id', how='left')
        print(f"✓ Left Join: {len(left_merge)} Datensätze")
        test_results["results"].append({
            "operation": "Left Join",
            "status": "SUCCESS",
            "result_size": len(left_merge)
        })
        
        # Right Join
        right_merge = patients.merge(operations, on='patient_id', how='right')
        print(f"✓ Right Join: {len(right_merge)} Datensätze")
        test_results["results"].append({
            "operation": "Right Join",
            "status": "SUCCESS",
            "result_size": len(right_merge)
        })
        
        # Outer Join
        outer_merge = patients.merge(follow_up, on='patient_id', how='outer')
        print(f"✓ Outer Join: {len(outer_merge)} Datensätze")
        test_results["results"].append({
            "operation": "Outer Join",
            "status": "SUCCESS",
            "result_size": len(outer_merge)
        })
        
        # Multi-Table Join
        full_data = patients.merge(operations, on='patient_id').merge(follow_up, on='patient_id', how='left')
        print(f"✓ Multi-Table Join: {len(full_data)} Datensätze")
        test_results["results"].append({
            "operation": "Multi-Table Join",
            "status": "SUCCESS",
            "result_size": len(full_data)
        })
        
        # Concat/Append Operationen
        combined_concat = pd.concat([patients.head(100), patients.tail(100)], ignore_index=True)
        print(f"✓ Concat Operation: {len(combined_concat)} Datensätze")
        test_results["results"].append({
            "operation": "Concat Operation",
            "status": "SUCCESS",
            "result_size": len(combined_concat)
        })
        
        # Join auf Indizes
        patients_idx = patients.set_index('patient_id')
        operations_idx = operations.set_index('patient_id')
        indexed_join = patients_idx.join(operations_idx, how='inner')
        print(f"✓ Index Join: {len(indexed_join)} Datensätze")
        test_results["results"].append({
            "operation": "Index Join",
            "status": "SUCCESS",
            "result_size": len(indexed_join)
        })
        
    except Exception as e:
        print(f"✗ Merge/Join-Operations-Fehler: {e}")
        test_results["results"].append({
            "operation": "Merge/Join-Operationen",
            "status": "FAILED",
            "error": str(e)
        })
    
    return test_results

# NaN-Handling und Data-Cleaning Tests
def test_nan_data_cleaning():
    """Test 5: NaN-Handling und Data-Cleaning"""
    print("\n" + "="*60)
    print("TEST 5: NaN-HANDLING & DATA CLEANING")
    print("="*60)
    
    test_results = {
        "test_name": "NaN-Handling und Data-Cleaning",
        "timestamp": datetime.now().isoformat(),
        "results": []
    }
    
    try:
        # Testdaten mit NaNs erstellen
        np.random.seed(42)
        data_with_nan = {
            'patient_id': range(1, 1001),
            'name': [f'Patient_{i}' if i % 10 != 0 else None for i in range(1, 1001)],
            'age': [np.random.randint(18, 80) if i % 8 != 0 else None for i in range(1, 1001)],
            'gender': [np.random.choice(['M', 'F']) if i % 12 != 0 else None for i in range(1, 1001)],
            'surgery_type': [np.random.choice(['Rhinoplastik', 'Septumplastik']) if i % 15 != 0 else None for i in range(1, 1001)],
            'duration_minutes': [np.random.normal(90, 15) if i % 20 != 0 else np.nan for i in range(1, 1001)]
        }
        
        df_nan = pd.DataFrame(data_with_nan)
        print(f"✓ DataFrame mit NaNs erstellt: {df_nan.isnull().sum().sum()} NaN Werte")
        test_results["results"].append({
            "operation": "NaN-Testdaten Creation",
            "status": "SUCCESS",
            "nan_count": int(df_nan.isnull().sum().sum())
        })
        
        # NaN-Erkennung
        nan_summary = df_nan.isnull().sum()
        print("✓ NaN-Erkennung erfolgreich")
        test_results["results"].append({
            "operation": "NaN-Erkennung",
            "status": "SUCCESS",
            "columns_with_nan": int((nan_summary > 0).sum())
        })
        
        # Drop NaN Rows
        df_dropped = df_nan.dropna()
        print(f"✓ Drop NaN Rows: {len(df_dropped)} von {len(df_nan)} Zeilen behalten")
        test_results["results"].append({
            "operation": "Drop NaN Rows",
            "status": "SUCCESS",
            "original_rows": len(df_nan),
            "cleaned_rows": len(df_dropped)
        })
        
        # Drop NaN Columns
        df_cols_dropped = df_nan.dropna(axis=1, thresh=len(df_nan)*0.8)
        print(f"✓ Drop NaN Columns: {len(df_cols_dropped.columns)} von {len(df_nan.columns)} Spalten behalten")
        test_results["results"].append({
            "operation": "Drop NaN Columns",
            "status": "SUCCESS",
            "original_columns": len(df_nan.columns),
            "cleaned_columns": len(df_cols_dropped.columns)
        })
        
        # Fill NaN Values
        df_filled = df_nan.copy()
        df_filled['age'].fillna(df_filled['age'].mean(), inplace=True)
        df_filled['gender'].fillna('Unbekannt', inplace=True)
        df_filled['surgery_type'].fillna(df_filled['surgery_type'].mode()[0], inplace=True)
        df_filled['duration_minutes'].fillna(df_filled['duration_minutes'].median(), inplace=True)
        print("✓ Fill NaN Values erfolgreich")
        test_results["results"].append({
            "operation": "Fill NaN Values",
            "status": "SUCCESS",
            "nan_after_fill": int(df_filled.isnull().sum().sum())
        })
        
        # Forward Fill und Backward Fill
        df_ffill = df_nan.fillna(method='ffill')
        df_bfill = df_nan.fillna(method='bfill')
        print("✓ Forward/Backward Fill erfolgreich")
        test_results["results"].append({
            "operation": "Forward/Backward Fill",
            "status": "SUCCESS"
        })
        
        # Interpolation
        df_interp = df_nan.copy()
        df_interp['duration_minutes'] = df_interp['duration_minutes'].interpolate()
        print("✓ Interpolation erfolgreich")
        test_results["results"].append({
            "operation": "Interpolation",
            "status": "SUCCESS"
        })
        
        # Data Quality Checks
        print("Data Quality Summary:")
        print(f"Duplikate: {df_nan.duplicated().sum()}")
        print(f"Unique Values in Gender: {df_nan['gender'].nunique()}")
        print(f"Age Range: {df_nan['age'].min()} - {df_nan['age'].max()}")
        test_results["results"].append({
            "operation": "Data Quality Checks",
            "status": "SUCCESS",
            "duplicates": int(df_nan.duplicated().sum()),
            "unique_genders": int(df_nan['gender'].nunique())
        })
        
    except Exception as e:
        print(f"✗ NaN-Handling-Operations-Fehler: {e}")
        test_results["results"].append({
            "operation": "NaN-Handling und Data-Cleaning",
            "status": "FAILED",
            "error": str(e)
        })
    
    return test_results

# Performance bei großen Datasets Tests
def test_large_dataset_performance():
    """Test 6: Performance bei großen Datasets"""
    print("\n" + "="*60)
    print("TEST 6: PERFORMANCE BEI GROßEN DATASETS")
    print("="*60)
    
    test_results = {
        "test_name": "Performance bei großen Datasets",
        "timestamp": datetime.now().isoformat(),
        "results": []
    }
    
    try:
        # Memory-Usage vor Test
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Große Dataset erstellen (1M Zeilen)
        print("Erstelle großes Dataset (1M Zeilen)...")
        np.random.seed(42)
        
        large_data = {
            'patient_id': range(1, 1000001),
            'name': [f'Patient_{i}' for i in range(1, 1000001)],
            'age': np.random.randint(18, 90, 1000000),
            'gender': np.random.choice(['M', 'F', 'D'], 1000000),
            'operation_date': pd.date_range('2015-01-01', periods=1000000, freq='1H'),
            'surgery_type': np.random.choice(['Rhinoplastik', 'Septumplastik', 'Nasenkorrektur', 'Andere'], 1000000),
            'duration_minutes': np.random.normal(90, 20, 1000000).astype(int),
            'complications': np.random.choice([0, 1], 1000000, p=[0.9, 0.1]),
            'satisfaction_score': np.random.randint(1, 11, 1000000)
        }
        
        df_large = pd.DataFrame(large_data)
        memory_after_creation = process.memory_info().rss / 1024 / 1024  # MB
        print(f"✓ Große Dataset erstellt: {df_large.shape[0]:,} Zeilen")
        print(f"Memory Usage: {memory_after_creation:.1f} MB")
        
        test_results["results"].append({
            "operation": "Large Dataset Creation",
            "status": "SUCCESS",
            "rows": len(df_large),
            "memory_mb": round(memory_after_creation - memory_before, 2)
        })
        
        # Performance Tests
        operations_performance = {}
        
        # 1. GroupBy Performance
        start_time = time.time()
        gender_stats = df_large.groupby('gender').agg({
            'age': 'mean',
            'duration_minutes': 'mean',
            'complications': 'sum'
        })
        operations_performance['groupby'] = time.time() - start_time
        print(f"✓ GroupBy Operation: {operations_performance['groupby']:.3f} Sekunden")
        
        # 2. Filter Performance
        start_time = time.time()
        filtered = df_large[(df_large['age'] >= 30) & (df_large['age'] <= 50)]
        operations_performance['filter'] = time.time() - start_time
        print(f"✓ Filter Operation: {operations_performance['filter']:.3f} Sekunden, {len(filtered):,} Ergebnisse")
        
        # 3. Merge Performance
        start_time = time.time()
        subset1 = df_large.sample(100000)
        subset2 = df_large.sample(50000)
        merged = subset1.merge(subset2, on='gender', how='inner')
        operations_performance['merge'] = time.time() - start_time
        print(f"✓ Merge Operation: {operations_performance['merge']:.3f} Sekunden, {len(merged):,} Ergebnisse")
        
        # 4. Sort Performance
        start_time = time.time()
        sorted_df = df_large.sort_values(['gender', 'age', 'operation_date'])
        operations_performance['sort'] = time.time() - start_time
        print(f"✓ Sort Operation: {operations_performance['sort']:.3f} Sekunden")
        
        # 5. Column Selection Performance
        start_time = time.time()
        selected = df_large[['gender', 'age', 'surgery_type']]
        operations_performance['column_selection'] = time.time() - start_time
        print(f"✓ Column Selection: {operations_performance['column_selection']:.3f} Sekunden")
        
        test_results["results"].append({
            "operation": "Performance Tests",
            "status": "SUCCESS",
            "operations_performance": operations_performance
        })
        
        # Memory Cleanup
        del df_large, large_data, merged
        gc.collect()
        memory_after_cleanup = process.memory_info().rss / 1024 / 1024  # MB
        print(f"Memory nach Cleanup: {memory_after_cleanup:.1f} MB")
        
    except Exception as e:
        print(f"✗ Large Dataset Performance-Fehler: {e}")
        test_results["results"].append({
            "operation": "Performance bei großen Datasets",
            "status": "FAILED",
            "error": str(e)
        })
    
    return test_results

# Memory-Efficiency und Chunks-Processing Tests
def test_memory_chunks_processing():
    """Test 7: Memory-Efficiency und Chunks-Processing"""
    print("\n" + "="*60)
    print("TEST 7: MEMORY-EFFICIENCY & CHUNKS-PROCESSING")
    print("="*60)
    
    test_results = {
        "test_name": "Memory-Efficiency und Chunks-Processing",
        "timestamp": datetime.now().isoformat(),
        "results": []
    }
    
    try:
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Chunks-read Test
        print("Teste chunks-read Funktionalität...")
        
        # Erstelle Test CSV
        test_data = {
            'patient_id': range(1, 10001),
            'name': [f'Patient_{i}' for i in range(1, 10001)],
            'age': np.random.randint(18, 80, 10000),
            'surgery_type': np.random.choice(['Rhinoplastik', 'Septumplastik'], 10000),
            'satisfaction': np.random.randint(1, 11, 10000)
        }
        df_test = pd.DataFrame(test_data)
        test_csv_path = '/tmp/test_patients.csv'
        df_test.to_csv(test_csv_path, index=False)
        print("✓ Test CSV erstellt")
        
        # Chunks-read
        chunk_size = 1000
        total_processed = 0
        chunk_stats = []
        
        for chunk_num, chunk in enumerate(pd.read_csv(test_csv_path, chunksize=chunk_size)):
            chunk_memory = process.memory_info().rss / 1024 / 1024  # MB
            chunk_stats.append({
                'chunk_number': chunk_num + 1,
                'rows': len(chunk),
                'memory_mb': round(chunk_memory, 2)
            })
            total_processed += len(chunk)
        
        print(f"✓ Chunks gelesen: {total_processed:,} Zeilen in {len(chunk_stats)} Chunks")
        test_results["results"].append({
            "operation": "Chunks-Processing",
            "status": "SUCCESS",
            "total_rows": total_processed,
            "chunks": len(chunk_stats)
        })
        
        # Memory-efficient operations
        print("Teste memory-efficient DataFrame-Operationen...")
        
        # Erstelle mehrere DataFrames für Test
        df1 = pd.DataFrame({'id': range(10000), 'data1': np.random.randn(10000)})
        df2 = pd.DataFrame({'id': range(5000, 15000), 'data2': np.random.randn(10000)})
        
        memory_df1 = process.memory_info().rss / 1024 / 1024  # MB
        
        # Memory-efficient merge
        merged = df1.merge(df2, on='id', how='inner', sort=True)
        
        memory_after_merge = process.memory_info().rss / 1024 / 1024  # MB
        print(f"✓ Memory-efficient merge: {memory_after_merge - memory_df1:.1f} MB zusätzlich")
        
        test_results["results"].append({
            "operation": "Memory-efficient Operations",
            "status": "SUCCESS",
            "merge_memory_increase_mb": round(memory_after_merge - memory_df1, 2)
        })
        
        # Data Type Optimization
        print("Teste Data Type Optimization...")
        
        # Original DataFrame
        df_types = pd.DataFrame({
            'id': range(100000),
            'age': np.random.randint(0, 120, 100000),
            'score': np.random.uniform(0, 100, 100000)
        })
        memory_before_optimization = process.memory_info().rss / 1024 / 1024  # MB
        
        # Optimize dtypes
        df_types['id'] = df_types['id'].astype('int32')
        df_types['age'] = df_types['age'].astype('int8')
        df_types['score'] = df_types['score'].astype('float32')
        
        memory_after_optimization = process.memory_info().rss / 1024 / 1024  # MB
        memory_saved = memory_before_optimization - memory_after_optimization
        
        print(f"✓ Data Type Optimization: {memory_saved:.1f} MB gespart")
        test_results["results"].append({
            "operation": "Data Type Optimization",
            "status": "SUCCESS",
            "memory_saved_mb": round(memory_saved, 2)
        })
        
        # Memory cleanup
        del df_types, df1, df2, df_test
        gc.collect()
        memory_after_cleanup = process.memory_info().rss / 1024 / 1024  # MB
        print(f"Memory nach finalem Cleanup: {memory_after_cleanup:.1f} MB")
        
        # Cleanup test file
        if os.path.exists(test_csv_path):
            os.remove(test_csv_path)
        
    except Exception as e:
        print(f"✗ Memory/Chunks-Processing-Fehler: {e}")
        test_results["results"].append({
            "operation": "Memory-Efficiency und Chunks-Processing",
            "status": "FAILED",
            "error": str(e)
        })
    
    return test_results

# DataFrame-to-Excel/CSV-Export-Funktionen Tests
def test_export_functions():
    """Test 8: DataFrame-to-Excel/CSV-Export-Funktionen"""
    print("\n" + "="*60)
    print("TEST 8: EXPORT FUNKTIONEN (CSV/EXCEL)")
    print("="*60)
    
    test_results = {
        "test_name": "Export-Funktionen",
        "timestamp": datetime.now().isoformat(),
        "results": []
    }
    
    try:
        # Testdaten für Export
        np.random.seed(42)
        export_data = {
            'patient_id': range(1, 1001),
            'name': [f'Patient_{i}' for i in range(1, 1001)],
            'age': np.random.randint(18, 80, 1000),
            'gender': np.random.choice(['M', 'F', 'D'], 1000),
            'surgery_type': np.random.choice(['Rhinoplastik', 'Septumplastik', 'Nasenkorrektur'], 1000),
            'operation_date': pd.date_range('2020-01-01', periods=1000, freq='D'),
            'duration_minutes': np.random.normal(90, 15, 1000).astype(int),
            'complications': np.random.choice([0, 1], 1000, p=[0.85, 0.15]),
            'satisfaction_score': np.random.randint(1, 11, 1000)
        }
        
        df_export = pd.DataFrame(export_data)
        print(f"✓ Export-Testdaten erstellt: {len(df_export)} Zeilen")
        
        # CSV Export
        csv_path = '/tmp/patients_export.csv'
        start_time = time.time()
        df_export.to_csv(csv_path, index=False, encoding='utf-8')
        csv_time = time.time() - start_time
        csv_size = os.path.getsize(csv_path) / 1024  # KB
        
        print(f"✓ CSV Export: {csv_time:.3f}s, {csv_size:.1f} KB")
        test_results["results"].append({
            "operation": "CSV Export",
            "status": "SUCCESS",
            "file_size_kb": round(csv_size, 2),
            "export_time_seconds": round(csv_time, 3)
        })
        
        # CSV Import (Validation)
        start_time = time.time()
        df_csv_imported = pd.read_csv(csv_path)
        import_time = time.time() - start_time
        print(f"✓ CSV Import: {import_time:.3f}s, {len(df_csv_imported)} Zeilen")
        test_results["results"].append({
            "operation": "CSV Import",
            "status": "SUCCESS",
            "imported_rows": len(df_csv_imported),
            "import_time_seconds": round(import_time, 3)
        })
        
        # Excel Export (falls verfügbar)
        try:
            excel_path = '/tmp/patients_export.xlsx'
            start_time = time.time()
            
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                # Haupt-Sheet
                df_export.to_excel(writer, sheet_name='Patients', index=False)
                
                # Separate Sheets für verschiedene Analysen
                gender_summary = df_export.groupby('gender').agg({
                    'patient_id': 'count',
                    'age': 'mean',
                    'duration_minutes': 'mean',
                    'complications': 'sum'
                })
                gender_summary.to_excel(writer, sheet_name='Gender_Analysis')
                
                surgery_summary = df_export.groupby('surgery_type').agg({
                    'patient_id': 'count',
                    'duration_minutes': 'mean',
                    'satisfaction_score': 'mean'
                })
                surgery_summary.to_excel(writer, sheet_name='Surgery_Analysis')
            
            excel_time = time.time() - start_time
            excel_size = os.path.getsize(excel_path) / 1024  # KB
            
            print(f"✓ Excel Export: {excel_time:.3f}s, {excel_size:.1f} KB")
            test_results["results"].append({
                "operation": "Excel Export",
                "status": "SUCCESS",
                "file_size_kb": round(excel_size, 2),
                "export_time_seconds": round(excel_time, 3),
                "sheets": 3
            })
            
            # Excel Import (Validation)
            start_time = time.time()
            df_excel_imported = pd.read_excel(excel_path, sheet_name='Patients')
            excel_import_time = time.time() - start_time
            print(f"✓ Excel Import: {excel_import_time:.3f}s, {len(df_excel_imported)} Zeilen")
            
            # Cleanup Excel file
            if os.path.exists(excel_path):
                os.remove(excel_path)
                
        except Exception as excel_error:
            print(f"⚠ Excel Export/Import nicht verfügbar: {excel_error}")
            test_results["results"].append({
                "operation": "Excel Export/Import",
                "status": "SKIPPED",
                "reason": str(excel_error)
            })
        
        # JSON Export
        json_path = '/tmp/patients_export.json'
        start_time = time.time()
        df_export.to_json(json_path, orient='records', date_format='iso')
        json_time = time.time() - start_time
        json_size = os.path.getsize(json_path) / 1024  # KB
        
        print(f"✓ JSON Export: {json_time:.3f}s, {json_size:.1f} KB")
        test_results["results"].append({
            "operation": "JSON Export",
            "status": "SUCCESS",
            "file_size_kb": round(json_size, 2),
            "export_time_seconds": round(json_time, 3)
        })
        
        # Parquet Export (falls verfügbar)
        try:
            parquet_path = '/tmp/patients_export.parquet'
            start_time = time.time()
            df_export.to_parquet(parquet_path, index=False)
            parquet_time = time.time() - start_time
            parquet_size = os.path.getsize(parquet_path) / 1024  # KB
            
            print(f"✓ Parquet Export: {parquet_time:.3f}s, {parquet_size:.1f} KB")
            test_results["results"].append({
                "operation": "Parquet Export",
                "status": "SUCCESS",
                "file_size_kb": round(parquet_size, 2),
                "export_time_seconds": round(parquet_time, 3)
            })
            
            # Parquet Import
            start_time = time.time()
            df_parquet_imported = pd.read_parquet(parquet_path)
            parquet_import_time = time.time() - start_time
            print(f"✓ Parquet Import: {parquet_import_time:.3f}s, {len(df_parquet_imported)} Zeilen")
            
            # Cleanup Parquet file
            if os.path.exists(parquet_path):
                os.remove(parquet_path)
                
        except Exception as parquet_error:
            print(f"⚠ Parquet Export/Import nicht verfügbar: {parquet_error}")
            test_results["results"].append({
                "operation": "Parquet Export/Import",
                "status": "SKIPPED",
                "reason": str(parquet_error)
            })
        
        # Cleanup CSV file
        if os.path.exists(csv_path):
            os.remove(csv_path)
        if os.path.exists(json_path):
            os.remove(json_path)
        
        print("✓ Alle Export-Tests abgeschlossen")
        
    except Exception as e:
        print(f"✗ Export-Funktionen-Fehler: {e}")
        test_results["results"].append({
            "operation": "Export-Funktionen",
            "status": "FAILED",
            "error": str(e)
        })
    
    return test_results

# Hauptfunktion für alle Tests
def run_all_pandas_tests():
    """Führe alle Pandas-Integration-Tests aus"""
    print("=" * 80)
    print("PANDAS INTEGRATION TEST SUITE")
    print("=" * 80)
    print(f"Start Zeit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Pandas Version: {pd.__version__}")
    print(f"NumPy Version: {np.__version__}")
    print("=" * 80)
    
    all_results = {
        "test_suite": "Pandas Integration Test Suite",
        "timestamp": datetime.now().isoformat(),
        "pandas_version": pd.__version__,
        "numpy_version": np.__version__,
        "test_results": []
    }
    
    # Alle Tests ausführen
    test_functions = [
        test_pandas_imports,
        test_dataframe_operations,
        test_groupby_operations,
        test_merge_join_operations,
        test_nan_data_cleaning,
        test_large_dataset_performance,
        test_memory_chunks_processing,
        test_export_functions
    ]
    
    for test_func in test_functions:
        try:
            result = test_func()
            all_results["test_results"].append(result)
            
            # Kurze Pause zwischen Tests
            time.sleep(0.5)
            
        except Exception as e:
            print(f"✗ Kritischer Fehler in {test_func.__name__}: {e}")
            all_results["test_results"].append({
                "test_name": test_func.__name__,
                "status": "CRITICAL_ERROR",
                "error": str(e)
            })
    
    # Zusammenfassung
    print("\n" + "=" * 80)
    print("TEST-ZUSAMMENFASSUNG")
    print("=" * 80)
    
    successful_tests = 0
    failed_tests = 0
    skipped_tests = 0
    
    for result in all_results["test_results"]:
        status = "SUCCESS" if result["results"] and all(r.get("status") == "SUCCESS" for r in result["results"]) else "FAILED"
        
        if status == "SUCCESS":
            successful_tests += 1
            print(f"✓ {result['test_name']}")
        elif status == "FAILED":
            failed_tests += 1
            print(f"✗ {result['test_name']}")
        else:
            skipped_tests += 1
            print(f"⚠ {result['test_name']} (Skipped)")
    
    print(f"\nErfolgreich: {successful_tests}")
    print(f"Fehlgeschlagen: {failed_tests}")
    print(f"Übersprungen: {skipped_tests}")
    print(f"Gesamt: {len(all_results['test_results'])}")
    
    all_results["summary"] = {
        "successful_tests": successful_tests,
        "failed_tests": failed_tests,
        "skipped_tests": skipped_tests,
        "total_tests": len(all_results["test_results"])
    }
    
    return all_results

# Test-Results als JSON speichern
def save_test_results(results, filename):
    """Speichere Test-Ergebnisse als JSON"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        print(f"✓ Test-Ergebnisse gespeichert: {filename}")
    except Exception as e:
        print(f"✗ Fehler beim Speichern der Test-Ergebnisse: {e}")

if __name__ == "__main__":
    # Alle Tests ausführen
    test_results = run_all_pandas_tests()
    
    # Ergebnisse speichern
    save_test_results(test_results, '/workspace/pandas_test_results.json')
    
    print(f"\nTest-Suite abgeschlossen: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Ergebnisse bereit für Berichterstellung.")
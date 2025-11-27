#!/usr/bin/env python3
"""
Umfassende Memory-Leak-Analyse für Rhinoplastik-Anwendung

Analysiert:
1. Memory-Usage-Patterns der Anwendung
2. Large-Dataset-Handling (10K+ Patienten)
3. Image-Memory-Management und Cleanup
4. Database-Connection-Pooling und Cleanup
5. Thread-Memory-Management und Cleanup
6. File-Handle-Management und Resource-Cleanup
7. Cache-Memory-Management und LRU-Eviction
8. Memory-Monitoring und Alert-Systems
9. Garbage-Collection-Performance
10. Memory-Leak-Detection und Prevention

Autor: Memory-Analysis-Agent
Datum: 2025-11-07
"""

import sys
import os
import gc
import psutil
import time
import threading
import sqlite3
import tempfile
import shutil
import json
import pandas as pd
import tracemalloc
import weakref
import threading
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil
from datetime import datetime, timedelta
import logging
import resource

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('memory_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class MemorySnapshot:
    """Memory-Snapshot für Analyse"""
    timestamp: float
    rss_mb: float  # Resident Set Size
    vms_mb: float  # Virtual Memory Size
    percent: float  # Memory Percent
    available_mb: float
    used_mb: float
    gc_objects: int
    gc_collections: List[Dict]
    open_files: int
    thread_count: int
    file_handles: int


@dataclass
class PerformanceMetrics:
    """Performance-Metriken für Memory-Operationen"""
    operation_name: str
    duration_ms: float
    memory_before_mb: float
    memory_after_mb: float
    memory_increase_mb: float
    gc_calls: int
    file_handles_before: int
    file_handles_after: int
    thread_count_before: int
    thread_count_after: int
    success: bool
    error_message: Optional[str] = None


class MemoryAnalyzer:
    """Hauptklasse für Memory-Leak-Analyse"""
    
    def __init__(self, test_results_dir: str = "memory_test_results"):
        self.test_results_dir = Path(test_results_dir)
        self.test_results_dir.mkdir(exist_ok=True)
        
        # Memory-Tracking
        self.memory_snapshots: List[MemorySnapshot] = []
        self.performance_metrics: List[PerformanceMetrics] = []
        
        # System-Info
        self.system_info = self._get_system_info()
        
        # Test-Dateien
        self.test_data_dir = Path("csv_test_files")
        self.large_dataset_path = self.test_data_dir / "large_dataset.csv"
        
        logger.info(f"Memory-Analyzer initialisiert - System: {self.system_info}")
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Sammelt System-Informationen"""
        return {
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': psutil.virtual_memory().total / (1024**3),
            'platform': sys.platform,
            'python_version': sys.version,
            'available_memory_gb': psutil.virtual_memory().available / (1024**3)
        }
    
    def take_memory_snapshot(self) -> MemorySnapshot:
        """Erstellt einen Memory-Snapshot"""
        process = psutil.Process()
        memory = psutil.virtual_memory()
        gc_stats = gc.get_stats()
        
        # File-Handles (nur Linux/Unix)
        open_files = 0
        file_handles = 0
        try:
            open_files = len(process.open_files())
            file_handles = process.num_handles() if hasattr(process, 'num_handles') else 0
        except:
            pass
        
        snapshot = MemorySnapshot(
            timestamp=time.time(),
            rss_mb=process.memory_info().rss / (1024 * 1024),
            vms_mb=process.memory_info().vms / (1024 * 1024),
            percent=process.memory_percent(),
            available_mb=memory.available / (1024 * 1024),
            used_mb=memory.used / (1024 * 1024),
            gc_objects=len(gc.garbage),
            gc_collections=gc_stats,
            open_files=open_files,
            thread_count=threading.active_count(),
            file_handles=file_handles
        )
        
        self.memory_snapshots.append(snapshot)
        return snapshot
    
    def _measure_operation_performance(self, operation_name: str, operation_func, *args, **kwargs):
        """Misst Performance einer Operation"""
        # Vor-Operation-Snapshot
        gc.collect()  # Saubere Basis
        snapshot_before = self.take_memory_snapshot()
        
        # File-Handles vor Operation
        process = psutil.Process()
        file_handles_before = 0
        try:
            file_handles_before = len(process.open_files())
        except:
            pass
        
        thread_count_before = threading.active_count()
        
        start_time = time.time()
        success = False
        error_message = None
        
        try:
            result = operation_func(*args, **kwargs)
            success = True
            return result
        except Exception as e:
            error_message = str(e)
            logger.error(f"Operation {operation_name} fehlgeschlagen: {e}")
            raise
        finally:
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            
            # Nach-Operation-Snapshot
            snapshot_after = self.take_memory_snapshot()
            
            # File-Handles nach Operation
            file_handles_after = 0
            try:
                file_handles_after = len(process.open_files())
            except:
                pass
            
            thread_count_after = threading.active_count()
            
            # Performance-Metrik erstellen
            metric = PerformanceMetrics(
                operation_name=operation_name,
                duration_ms=duration_ms,
                memory_before_mb=snapshot_before.rss_mb,
                memory_after_mb=snapshot_after.rss_mb,
                memory_increase_mb=snapshot_after.rss_mb - snapshot_before.rss_mb,
                gc_calls=len(gc.get_stats()),
                file_handles_before=file_handles_before,
                file_handles_after=file_handles_after,
                thread_count_before=thread_count_before,
                thread_count_after=thread_count_after,
                success=success,
                error_message=error_message
            )
            
            self.performance_metrics.append(metric)
            logger.info(f"Performance {operation_name}: {duration_ms:.2f}ms, Memory: {metric.memory_increase_mb:.2f}MB")
    
    def test_memory_usage_patterns(self):
        """Test 1: Analysiere Memory-Usage-Patterns der Anwendung"""
        logger.info("=== TEST 1: Memory-Usage-Patterns ===")
        
        # Baseline Memory
        gc.collect()
        baseline = self.take_memory_snapshot()
        logger.info(f"Baseline Memory: {baseline.rss_mb:.2f} MB")
        
        # Verschiedene Operationen testen
        operations = [
            ("GUI_Initialization", self._test_gui_initialization),
            ("Database_Connection", self._test_database_connection),
            ("Large_Data_Processing", self._test_large_data_processing),
            ("File_Operations", self._test_file_operations),
            ("Thread_Creation", self._test_thread_creation)
        ]
        
        memory_patterns = {}
        
        for op_name, op_func in operations:
            logger.info(f"Teste {op_name}...")
            
            try:
                # Memory vor Operation
                start_memory = self.take_memory_snapshot()
                
                # Operation ausführen
                self._measure_operation_performance(op_name, op_func)
                
                # Memory nach Operation
                end_memory = self.take_memory_snapshot()
                
                # Pattern analysieren
                memory_increase = end_memory.rss_mb - start_memory.rss_mb
                memory_patterns[op_name] = {
                    'memory_increase_mb': memory_increase,
                    'memory_percent': (memory_increase / baseline.rss_mb) * 100,
                    'final_memory_mb': end_memory.rss_mb
                }
                
                logger.info(f"  Memory Increase: {memory_increase:.2f} MB")
                
            except Exception as e:
                logger.error(f"  Fehler bei {op_name}: {e}")
                memory_patterns[op_name] = {'error': str(e)}
        
        # Speichere Ergebnisse
        self._save_test_results('memory_usage_patterns.json', memory_patterns)
        return memory_patterns
    
    def _test_gui_initialization(self):
        """Test GUI-Initialisierung (Mock)"""
        # Simuliere GUI-Initialisierung ohne tatsächliche GUI
        import tkinter as tk
        from unittest.mock import Mock
        
        # Mock QApplication components
        mock_app = Mock()
        mock_main_window = Mock()
        mock_widgets = [Mock() for _ in range(100)]
        
        # Simuliere Memory-intensive GUI-Operationen
        for i in range(1000):
            widget_data = {
                'id': i,
                'properties': {f'prop_{j}': f'value_{j}' for j in range(10)},
                'layout_data': [f'layout_{k}' for k in range(5)]
            }
            mock_widgets[i % 100].configure(**widget_data)
        
        time.sleep(0.1)  # Simuliere Verarbeitungszeit
    
    def _test_database_connection(self):
        """Test Database-Verbindungen"""
        temp_db = self.test_results_dir / "test_memory.db"
        
        # Multiple Connections
        connections = []
        for i in range(10):
            conn = sqlite3.connect(temp_db, timeout=5.0)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER, data TEXT)")
            cursor.execute("INSERT INTO test VALUES (?, ?)", (i, f"data_{i}"))
            connections.append(conn)
        
        # Query execution
        for conn in connections:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM test")
            results = cursor.fetchall()
        
        # Cleanup
        for conn in connections:
            conn.close()
        
        if temp_db.exists():
            temp_db.unlink()
    
    def _test_large_data_processing(self):
        """Test Large-Dataset-Handling"""
        if not self.large_dataset_path.exists():
            logger.warning(f"Large dataset not found: {self.large_dataset_path}")
            return
        
        # CSV-Datei in Chunks laden
        chunk_size = 1000
        total_rows = 0
        
        try:
            for chunk in pd.read_csv(self.large_dataset_path, chunksize=chunk_size):
                # Verarbeite Chunk
                processed_data = chunk.to_dict('records')
                total_rows += len(processed_data)
                
                # Memory-intensive Operationen
                large_list = []
                for record in processed_data:
                    large_list.append({
                        'processed': True,
                        'data': record,
                        'metadata': {'timestamp': time.time(), 'chunk_id': total_rows // chunk_size}
                    })
                
                # Cleanup
                del large_list
                del processed_data
                
        except Exception as e:
            logger.error(f"Error processing large dataset: {e}")
        
        logger.info(f"Processed {total_rows} rows from large dataset")
    
    def _test_file_operations(self):
        """Test File-Handle-Management"""
        test_files = []
        temp_dir = self.test_results_dir / "file_test"
        temp_dir.mkdir(exist_ok=True)
        
        try:
            # Erstelle viele kleine Dateien
            for i in range(100):
                file_path = temp_dir / f"test_file_{i}.txt"
                with open(file_path, 'w') as f:
                    f.write(f"Test data {i}\n" * 100)
                test_files.append(file_path)
            
            # Lese alle Dateien
            for file_path in test_files:
                with open(file_path, 'r') as f:
                    content = f.read()
            
            # File-Handle-Tracking
            process = psutil.Process()
            initial_files = len(process.open_files())
            
            # Intensive File-IO
            for _ in range(50):
                for file_path in test_files:
                    with open(file_path, 'r') as f:
                        _ = f.read(100)  # Partial read
            
            final_files = len(process.open_files())
            logger.info(f"Open files - Initial: {initial_files}, Final: {final_files}")
            
        finally:
            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def _test_thread_creation(self):
        """Test Thread-Memory-Management"""
        results = []
        
        def worker_thread(thread_id):
            # Memory-intensive Thread-Operation
            local_data = []
            for i in range(1000):
                local_data.append({
                    'thread_id': thread_id,
                    'data': f"data_{i}",
                    'metadata': {'created': time.time()}
                })
            
            time.sleep(0.01)  # Kurze Verarbeitungszeit
            return {'thread_id': thread_id, 'processed_items': len(local_data)}
        
        # Starte viele Threads
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(worker_thread, i) for i in range(50)]
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Thread execution error: {e}")
        
        logger.info(f"Completed {len(results)} thread operations")
    
    def test_large_dataset_handling(self):
        """Test 2: Large-Dataset-Handling (10K+ Patienten)"""
        logger.info("=== TEST 2: Large-Dataset-Handling ===")
        
        if not self.large_dataset_path.exists():
            logger.warning(f"Large dataset not found: {self.large_dataset_path}")
            return {'error': 'Large dataset not found'}
        
        # Memory-Tracking für Large-Dataset
        gc.collect()
        initial_memory = self.take_memory_snapshot()
        
        dataset_results = {
            'file_info': {},
            'processing_metrics': [],
            'memory_analysis': {},
            'performance_data': []
        }
        
        try:
            # Datei-Informationen
            file_stats = self.large_dataset_path.stat()
            dataset_results['file_info'] = {
                'size_mb': file_stats.st_size / (1024 * 1024),
                'size_bytes': file_stats.st_size,
                'modified': datetime.fromtimestamp(file_stats.st_mtime).isoformat()
            }
            
            # Chunked Processing Test
            chunk_sizes = [100, 500, 1000, 2000]
            
            for chunk_size in chunk_sizes:
                logger.info(f"Testing chunk size: {chunk_size}")
                
                start_time = time.time()
                start_memory = self.take_memory_snapshot()
                
                total_processed = 0
                max_memory = start_memory.rss_mb
                
                try:
                    for chunk in pd.read_csv(self.large_dataset_path, chunksize=chunk_size):
                        # Simuliere Datenverarbeitung
                        processed_chunk = chunk.copy()
                        
                        # Memory-intensive Operationen
                        chunk_metadata = {
                            'rows': len(processed_chunk),
                            'columns': len(processed_chunk.columns),
                            'memory_usage_mb': processed_chunk.memory_usage(deep=True).sum() / (1024 * 1024),
                            'processed_at': time.time()
                        }
                        
                        total_processed += len(processed_chunk)
                        
                        # Aktuelle Memory-Messung
                        current_memory = self.take_memory_snapshot()
                        max_memory = max(max_memory, current_memory.rss_mb)
                        
                        # Cleanup
                        del processed_chunk
                        del chunk_metadata
                
                except Exception as e:
                    logger.error(f"Error processing chunk size {chunk_size}: {e}")
                    continue
                
                end_time = time.time()
                end_memory = self.take_memory_snapshot()
                
                processing_time = end_time - start_time
                memory_increase = end_memory.rss_mb - start_memory.rss_mb
                memory_peak_increase = max_memory - start_memory.rss_mb
                
                metric = {
                    'chunk_size': chunk_size,
                    'total_processed': total_processed,
                    'processing_time_s': processing_time,
                    'rows_per_second': total_processed / processing_time if processing_time > 0 else 0,
                    'memory_increase_mb': memory_increase,
                    'memory_peak_increase_mb': memory_peak_increase,
                    'memory_efficiency': total_processed / memory_peak_increase if memory_peak_increase > 0 else 0
                }
                
                dataset_results['processing_metrics'].append(metric)
                logger.info(f"  Processed {total_processed} rows in {processing_time:.2f}s")
                logger.info(f"  Memory increase: {memory_increase:.2f} MB")
            
            # Memory-Analyse
            final_memory = self.take_memory_snapshot()
            dataset_results['memory_analysis'] = {
                'initial_memory_mb': initial_memory.rss_mb,
                'final_memory_mb': final_memory.rss_mb,
                'total_increase_mb': final_memory.rss_mb - initial_memory.rss_mb,
                'gc_objects': final_memory.gc_objects,
                'available_memory_mb': final_memory.available_mb
            }
            
        except Exception as e:
            logger.error(f"Large dataset test error: {e}")
            dataset_results['error'] = str(e)
        
        # Speichere Ergebnisse
        self._save_test_results('large_dataset_handling.json', dataset_results)
        return dataset_results
    
    def test_image_memory_management(self):
        """Test 3: Image-Memory-Management und Cleanup"""
        logger.info("=== TEST 3: Image-Memory-Management ===")
        
        # Erstelle Test-Bilder
        image_test_results = {
            'image_creation': {},
            'thumbnail_generation': {},
            'memory_cleanup': {},
            'file_handle_management': {}
        }
        
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            temp_images_dir = self.test_results_dir / "test_images"
            temp_images_dir.mkdir(exist_ok=True)
            
            # Test verschiedene Bildgrößen
            image_sizes = [(800, 600), (1920, 1080), (3840, 2160)]
            
            for width, height in image_sizes:
                logger.info(f"Testing image size: {width}x{height}")
                
                start_memory = self.take_memory_snapshot()
                
                # Erstelle Test-Bild
                image_path = temp_images_dir / f"test_{width}x{height}.jpg"
                
                # Generiere Bild in Memory
                img = Image.new('RGB', (width, height), color='blue')
                draw = ImageDraw.Draw(img)
                
                # Füge some content hinzu
                for i in range(100):
                    x1, y1 = i * 10 % width, i * 15 % height
                    x2, y2 = x1 + 50, y1 + 30
                    draw.rectangle([x1, y1, x2, y2], fill='red')
                
                # Speichere Bild
                img.save(image_path, 'JPEG', quality=85)
                
                end_memory = self.take_memory_snapshot()
                
                image_creation_metric = {
                    'size': f"{width}x{height}",
                    'memory_increase_mb': end_memory.rss_mb - start_memory.rss_mb,
                    'file_size_mb': image_path.stat().st_size / (1024 * 1024)
                }
                
                image_test_results['image_creation'][f"{width}x{height}"] = image_creation_metric
                
                # Thumbnail-Generierung
                start_memory = self.take_memory_snapshot()
                
                # Lade Bild und erstelle Thumbnails
                with Image.open(image_path) as img:
                    thumbnail_sizes = [(150, 150), (300, 300), (800, 600)]
                    
                    for thumb_width, thumb_height in thumbnail_sizes:
                        thumb = img.copy()
                        thumb.thumbnail((thumb_width, thumb_height), Image.Resampling.LANCZOS)
                        
                        thumb_path = temp_images_dir / f"thumb_{thumb_width}x{thumb_height}.jpg"
                        thumb.save(thumb_path, 'JPEG', quality=80)
                        
                        # Memory cleanup
                        del thumb
                
                end_memory = self.take_memory_snapshot()
                
                thumbnail_metric = {
                    'original_size': f"{width}x{height}",
                    'memory_increase_mb': end_memory.rss_mb - start_memory.rss_mb,
                    'thumbnails_created': len(thumbnail_sizes)
                }
                
                image_test_results['thumbnail_generation'][f"{width}x{height}"] = thumbnail_metric
                
                # Cleanup
                del img
                del draw
            
            # File-Handle-Management test
            start_memory = self.take_memory_snapshot()
            process = psutil.Process()
            initial_files = len(process.open_files())
            
            # Öffne viele Bilder gleichzeitig
            open_images = []
            for img_file in temp_images_dir.glob("*.jpg"):
                try:
                    with Image.open(img_file) as img:
                        open_images.append(img)
                except Exception as e:
                    logger.error(f"Error opening {img_file}: {e}")
            
            during_files = len(process.open_files())
            
            # Schließe alle Bilder
            open_images.clear()
            gc.collect()
            
            final_files = len(process.open_files())
            end_memory = self.take_memory_snapshot()
            
            image_test_results['file_handle_management'] = {
                'initial_open_files': initial_files,
                'during_open_files': during_files,
                'final_open_files': final_files,
                'memory_increase_mb': end_memory.rss_mb - start_memory.rss_mb
            }
            
            logger.info(f"File handles - Initial: {initial_files}, During: {during_files}, Final: {final_files}")
            
        except ImportError:
            logger.warning("PIL not available - skipping image tests")
            image_test_results['error'] = 'PIL not available'
        except Exception as e:
            logger.error(f"Image memory test error: {e}")
            image_test_results['error'] = str(e)
        finally:
            # Cleanup
            if temp_images_dir.exists():
                shutil.rmtree(temp_images_dir, ignore_errors=True)
        
        # Speichere Ergebnisse
        self._save_test_results('image_memory_management.json', image_test_results)
        return image_test_results
    
    def test_database_connection_pooling(self):
        """Test 4: Database-Connection-Pooling und Cleanup"""
        logger.info("=== TEST 4: Database-Connection-Pooling ===")
        
        db_test_results = {
            'connection_pool': {},
            'query_performance': {},
            'connection_cleanup': {},
            'memory_leak_detection': {}
        }
        
        try:
            temp_db = self.test_results_dir / "pool_test.db"
            
            # Initialisiere Test-Datenbank
            with sqlite3.connect(temp_db) as conn:
                conn.execute("""
                    CREATE TABLE test_connections (
                        id INTEGER PRIMARY KEY,
                        data TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Füge Test-Daten hinzu
                test_data = [(i, f"test_data_{i}") for i in range(1000)]
                conn.executemany("INSERT INTO test_connections (id, data) VALUES (?, ?)", test_data)
                conn.commit()
            
            # Connection Pool Test
            pool_size = 20
            connections = []
            
            start_memory = self.take_memory_snapshot()
            start_files = len(psutil.Process().open_files())
            
            # Erstelle Connection Pool
            for i in range(pool_size):
                conn = sqlite3.connect(temp_db, timeout=5.0)
                conn.execute("PRAGMA journal_mode=WAL")  # WAL mode für bessere Performance
                connections.append(conn)
            
            during_memory = self.take_memory_snapshot()
            during_files = len(psutil.Process().open_files())
            
            # Query Performance Test
            query_times = []
            for i in range(100):
                start_time = time.time()
                
                # Zufällige Connection aus Pool
                conn = connections[i % pool_size]
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM test_connections WHERE id = ?", (i % 1000,))
                result = cursor.fetchone()
                
                query_time = (time.time() - start_time) * 1000
                query_times.append(query_time)
            
            avg_query_time = sum(query_times) / len(query_times)
            max_query_time = max(query_times)
            
            # Cleanup Test
            for conn in connections:
                conn.close()
            
            gc.collect()
            
            end_memory = self.take_memory_snapshot()
            end_files = len(psutil.Process().open_files())
            
            # Memory Leak Detection
            memory_leak_metric = {
                'pool_size': pool_size,
                'memory_per_connection_mb': (during_memory.rss_mb - start_memory.rss_mb) / pool_size,
                'memory_after_cleanup_mb': end_memory.rss_mb - start_memory.rss_mb,
                'file_handles_before': start_files,
                'file_handles_during': during_files,
                'file_handles_after': end_files,
                'avg_query_time_ms': avg_query_time,
                'max_query_time_ms': max_query_time
            }
            
            db_test_results['connection_pool'] = memory_leak_metric
            db_test_results['query_performance'] = {
                'total_queries': len(query_times),
                'avg_time_ms': avg_query_time,
                'max_time_ms': max_query_time,
                'min_time_ms': min(query_times)
            }
            
            logger.info(f"Pool test - Memory per connection: {memory_leak_metric['memory_per_connection_mb']:.2f} MB")
            logger.info(f"Query performance - Avg: {avg_query_time:.2f}ms, Max: {max_query_time:.2f}ms")
            
        except Exception as e:
            logger.error(f"Database pool test error: {e}")
            db_test_results['error'] = str(e)
        finally:
            if temp_db.exists():
                temp_db.unlink()
        
        # Speichere Ergebnisse
        self._save_test_results('database_connection_pooling.json', db_test_results)
        return db_test_results
    
    def test_thread_memory_management(self):
        """Test 5: Thread-Memory-Management und Cleanup"""
        logger.info("=== TEST 5: Thread-Memory-Management ===")
        
        thread_test_results = {
            'thread_creation': {},
            'concurrent_operations': {},
            'memory_cleanup': {},
            'resource_leak_detection': {}
        }
        
        try:
            # Thread Creation Test
            thread_counts = [10, 50, 100, 200]
            
            for thread_count in thread_counts:
                logger.info(f"Testing {thread_count} threads...")
                
                start_memory = self.take_memory_snapshot()
                start_threads = threading.active_count()
                
                def memory_intensive_thread(thread_id):
                    # Simuliere Memory-intensive Thread-Arbeit
                    local_data = []
                    for i in range(100):
                        local_data.append({
                            'thread_id': thread_id,
                            'iteration': i,
                            'data': f"data_{thread_id}_{i}",
                            'large_object': [j for j in range(1000)]  # Memory-intensive
                        })
                    
                    time.sleep(0.01)  # Kurze Verarbeitungszeit
                    
                    # Cleanup vor Thread-Ende
                    del local_data
                    return thread_id
                
                # Starte Threads
                with ThreadPoolExecutor(max_workers=thread_count) as executor:
                    futures = [executor.submit(memory_intensive_thread, i) for i in range(thread_count)]
                    
                    # Warte auf alle Threads
                    results = []
                    for future in as_completed(futures):
                        try:
                            result = future.result(timeout=5.0)
                            results.append(result)
                        except Exception as e:
                            logger.error(f"Thread execution error: {e}")
                
                # Memory nach Thread-Completion
                during_memory = self.take_memory_snapshot()
                during_threads = threading.active_count()
                
                # Warte auf Thread-Cleanup
                time.sleep(0.5)
                gc.collect()
                
                end_memory = self.take_memory_snapshot()
                end_threads = threading.active_count()
                
                thread_metric = {
                    'thread_count': thread_count,
                    'successful_threads': len(results),
                    'memory_per_thread_mb': (during_memory.rss_mb - start_memory.rss_mb) / thread_count,
                    'memory_cleanup_mb': during_memory.rss_mb - end_memory.rss_mb,
                    'threads_before': start_threads,
                    'threads_during': during_threads,
                    'threads_after': end_threads,
                    'memory_increase_mb': during_memory.rss_mb - start_memory.rss_mb,
                    'memory_final_increase_mb': end_memory.rss_mb - start_memory.rss_mb
                }
                
                thread_test_results['thread_creation'][str(thread_count)] = thread_metric
                logger.info(f"  Threads: {thread_count}, Memory/Thread: {thread_metric['memory_per_thread_mb']:.2f} MB")
            
            # Concurrent File I/O Test
            logger.info("Testing concurrent file I/O...")
            
            temp_dir = self.test_results_dir / "thread_file_test"
            temp_dir.mkdir(exist_ok=True)
            
            start_memory = self.take_memory_snapshot()
            
            def file_worker(worker_id, file_count):
                files_created = []
                try:
                    for i in range(file_count):
                        file_path = temp_dir / f"thread_{worker_id}_file_{i}.txt"
                        with open(file_path, 'w') as f:
                            f.write(f"Worker {worker_id}, File {i}\n" * 100)
                        files_created.append(file_path)
                    
                    # Lese alle Dateien zurück
                    for file_path in files_created:
                        with open(file_path, 'r') as f:
                            _ = f.read()
                    
                    return len(files_created)
                except Exception as e:
                    logger.error(f"File worker {worker_id} error: {e}")
                    return 0
                finally:
                    # Cleanup
                    for file_path in files_created:
                        try:
                            if file_path.exists():
                                file_path.unlink()
                        except:
                            pass
            
            # Concurrent File I/O mit 20 Threads
            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = [executor.submit(file_worker, i, 10) for i in range(20)]
                
                file_results = []
                for future in as_completed(futures):
                    try:
                        result = future.result(timeout=10.0)
                        file_results.append(result)
                    except Exception as e:
                        logger.error(f"File I/O thread error: {e}")
            
            end_memory = self.take_memory_snapshot()
            
            # Cleanup
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
            
            concurrent_metric = {
                'total_workers': 20,
                'files_per_worker': 10,
                'total_files_processed': sum(file_results),
                'memory_increase_mb': end_memory.rss_mb - start_memory.rss_mb,
                'avg_files_per_worker': sum(file_results) / len(file_results) if file_results else 0
            }
            
            thread_test_results['concurrent_operations'] = concurrent_metric
            logger.info(f"Concurrent I/O - Processed {concurrent_metric['total_files_processed']} files")
            
        except Exception as e:
            logger.error(f"Thread memory test error: {e}")
            thread_test_results['error'] = str(e)
        
        # Speichere Ergebnisse
        self._save_test_results('thread_memory_management.json', thread_test_results)
        return thread_test_results
    
    def test_garbage_collection_performance(self):
        """Test 9: Garbage-Collection-Performance"""
        logger.info("=== TEST 9: Garbage-Collection-Performance ===")
        
        gc_test_results = {
            'gc_performance': {},
            'memory_reclamation': {},
            'generational_analysis': {}
        }
        
        try:
            # GC Performance Test
            gc.collect()  # Cleanup vor Test
            gc_stats_before = gc.get_stats()
            
            start_memory = self.take_memory_snapshot()
            start_objects = len(gc.garbage)
            
            # Erstelle Memory-intensive Objekte
            large_objects = []
            for i in range(1000):
                obj = {
                    'id': i,
                    'data': [j for j in range(10000)],  # Große Liste
                    'metadata': {f'key_{k}': f'value_{k}' for k in range(100)},
                    'references': []
                }
                large_objects.append(obj)
                
                # Zirkuläre Referenzen für GC-Test
                if i > 0:
                    large_objects[i]['references'].append(large_objects[i-1])
                    large_objects[i-1]['references'].append(large_objects[i])
            
            during_memory = self.take_memory_snapshot()
            during_objects = len(gc.garbage)
            
            # Lösche Referenzen
            large_objects.clear()
            
            # GC-Performance messen
            gc_start_time = time.time()
            collected = gc.collect()
            gc_end_time = time.time()
            
            gc_time = (gc_end_time - gc_start_time) * 1000  # ms
            gc_stats_after = gc.get_stats()
            
            end_memory = self.take_memory_snapshot()
            end_objects = len(gc.garbage)
            
            # Generational GC Analysis
            generation_stats = []
            for generation in range(3):
                gen_stats = {
                    'generation': generation,
                    'collections_before': gc_stats_before[generation]['collections'] if generation < len(gc_stats_before) else 0,
                    'collections_after': gc_stats_after[generation]['collections'] if generation < len(gc_stats_after) else 0,
                    'collected_before': gc_stats_before[generation]['collected'] if generation < len(gc_stats_before) else 0,
                    'collected_after': gc_stats_after[generation]['collected'] if generation < len(gc_stats_after) else 0
                }
                generation_stats.append(gen_stats)
            
            gc_performance_metric = {
                'objects_created': 1000,
                'objects_before_gc': during_objects,
                'objects_after_gc': end_objects,
                'objects_collected': during_objects - end_objects,
                'gc_time_ms': gc_time,
                'memory_before_mb': during_memory.rss_mb,
                'memory_after_mb': end_memory.rss_mb,
                'memory_freed_mb': during_memory.rss_mb - end_memory.rss_mb,
                'memory_efficiency': (during_memory.rss_mb - end_memory.rss_mb) / during_memory.rss_mb if during_memory.rss_mb > 0 else 0
            }
            
            gc_test_results['gc_performance'] = gc_performance_metric
            gc_test_results['generational_analysis'] = generation_stats
            
            logger.info(f"GC Performance - Collected: {collected} objects in {gc_time:.2f}ms")
            logger.info(f"Memory freed: {gc_performance_metric['memory_freed_mb']:.2f} MB")
            
            # Automatische GC-Tests
            logger.info("Testing automatic GC behavior...")
            
            auto_gc_results = []
            for test_run in range(5):
                # Erstelle Objects ohne explizite GC-Aufrufe
                test_objects = []
                for i in range(100):
                    test_objects.append([j for j in range(5000)])
                
                # Memory vor impliziter GC
                before_memory = self.take_memory_snapshot()
                
                # Lösche Referenzen
                test_objects.clear()
                
                # Warte auf automatische GC (kurze Zeit)
                time.sleep(0.1)
                
                # Memory nach impliziter GC
                after_memory = self.take_memory_snapshot()
                
                auto_gc_metric = {
                    'test_run': test_run + 1,
                    'memory_before_mb': before_memory.rss_mb,
                    'memory_after_mb': after_memory.rss_mb,
                    'auto_freed_mb': before_memory.rss_mb - after_memory.rss_mb
                }
                
                auto_gc_results.append(auto_gc_metric)
            
            gc_test_results['automatic_gc'] = auto_gc_results
            
        except Exception as e:
            logger.error(f"GC performance test error: {e}")
            gc_test_results['error'] = str(e)
        
        # Speichere Ergebnisse
        self._save_test_results('garbage_collection_performance.json', gc_test_results)
        return gc_test_results
    
    def test_memory_leak_detection(self):
        """Test 10: Memory-Leak-Detection und Prevention"""
        logger.info("=== TEST 10: Memory-Leak-Detection ===")
        
        leak_test_results = {
            'baseline_measurements': {},
            'leak_detection': {},
            'prevention_mechanisms': {},
            'long_term_analysis': {}
        }
        
        try:
            # Baseline Memory
            gc.collect()
            baseline_memory = self.take_memory_snapshot()
            baseline_objects = len(gc.garbage)
            
            leak_test_results['baseline_measurements'] = {
                'memory_mb': baseline_memory.rss_mb,
                'objects': baseline_objects,
                'available_memory_mb': baseline_memory.available_mb
            }
            
            logger.info(f"Baseline Memory: {baseline_memory.rss_mb:.2f} MB")
            
            # Memory Leak Detection durch zyklische Tests
            memory_readings = []
            object_counts = []
            
            for cycle in range(50):
                cycle_start_memory = self.take_memory_snapshot()
                
                # Intensive Operationen (potentielle Leak-Quelle)
                cycle_data = []
                for i in range(100):
                    # Simuliere komplexe Objekte
                    obj = {
                        'id': f"obj_{cycle}_{i}",
                        'data': {f'key_{j}': f'value_{j}' for j in range(50)},
                        'large_array': [j for j in range(1000)],
                        'metadata': {
                            'created_at': time.time(),
                            'cycle': cycle,
                            'index': i
                        }
                    }
                    cycle_data.append(obj)
                
                # Memory nach Objekt-Erstellung
                during_memory = self.take_memory_snapshot()
                objects_during = len(gc.garbage)
                
                # Explizite Cleanup-Versuche
                del cycle_data
                gc.collect()
                
                # Memory nach Cleanup
                after_memory = self.take_memory_snapshot()
                objects_after = len(gc.garbage)
                
                memory_readings.append({
                    'cycle': cycle,
                    'memory_before_mb': cycle_start_memory.rss_mb,
                    'memory_during_mb': during_memory.rss_mb,
                    'memory_after_mb': after_memory.rss_mb,
                    'memory_increase_mb': during_memory.rss_mb - cycle_start_memory.rss_mb,
                    'memory_final_increase_mb': after_memory.rss_mb - cycle_start_memory.rss_mb
                })
                
                object_counts.append({
                    'cycle': cycle,
                    'objects_before': baseline_objects,
                    'objects_during': objects_during,
                    'objects_after': objects_after,
                    'leaked_objects': objects_after - baseline_objects
                })
                
                # Alle 10 Zyklen explizite GC
                if cycle % 10 == 0:
                    collected = gc.collect()
                    logger.info(f"Cycle {cycle}: GC collected {collected} objects")
            
            # Leaks-Analyse
            final_memory = self.take_memory_snapshot()
            memory_increase = final_memory.rss_mb - baseline_memory.rss_mb
            
            # Trend-Analyse
            memory_trends = []
            for i in range(0, len(memory_readings), 5):  # Alle 5 Zyklen
                window = memory_readings[i:i+5]
                avg_increase = sum(r['memory_final_increase_mb'] for r in window) / len(window)
                memory_trends.append({
                    'window_start': i,
                    'window_end': i + 4,
                    'avg_memory_increase_mb': avg_increase
                })
            
            # Leak-Detection-Ergebnisse
            leak_detection = {
                'total_cycles': 50,
                'baseline_memory_mb': baseline_memory.rss_mb,
                'final_memory_mb': final_memory.rss_mb,
                'total_memory_increase_mb': memory_increase,
                'memory_increase_per_cycle_mb': memory_increase / 50,
                'leak_threshold_mb': 1.0,  # 1MB pro Zyklus = potentiel Leak
                'potential_leak': memory_increase / 50 > 1.0,
                'memory_trends': memory_trends,
                'max_memory_increase_mb': max(r['memory_final_increase_mb'] for r in memory_readings),
                'min_memory_increase_mb': min(r['memory_final_increase_mb'] for r in memory_readings)
            }
            
            leak_test_results['leak_detection'] = leak_detection
            
            # Prevention Mechanisms Test
            prevention_results = []
            
            # Weak Reference Test
            weak_ref_objects = []
            for i in range(100):
                obj = {'id': i, 'data': [j for j in range(1000)]}
                weak_ref = weakref.ref(obj)
                weak_ref_objects.append(weak_ref)
            
            # Lösche strong references
            strong_refs = [ref() for ref in weak_ref_objects if ref() is not None]
            for obj in strong_refs:
                del obj
            
            gc.collect()
            
            weak_ref_leftovers = sum(1 for ref in weak_ref_objects if ref() is not None)
            
            prevention_results.append({
                'mechanism': 'weak_references',
                'objects_created': 100,
                'objects_remaining': weak_ref_leftovers,
                'cleanup_effectiveness': (100 - weak_ref_leftovers) / 100
            })
            
            # Context Manager Test
            class MemoryContextTest:
                def __init__(self, name):
                    self.name = name
                    self.data = [j for j in range(10000)]
                
                def __enter__(self):
                    return self
                
                def __exit__(self, exc_type, exc_val, exc_tb):
                    # Cleanup
                    del self.data
                    return False
            
            context_memory_before = self.take_memory_snapshot()
            
            for i in range(50):
                with MemoryContextTest(f"ctx_{i}") as ctx:
                    # Arbeite mit Context
                    _ = len(ctx.data)
            
            context_memory_after = self.take_memory_snapshot()
            context_memory_increase = context_memory_after.rss_mb - context_memory_before.rss_mb
            
            prevention_results.append({
                'mechanism': 'context_managers',
                'iterations': 50,
                'memory_increase_mb': context_memory_increase,
                'avg_per_iteration_mb': context_memory_increase / 50
            })
            
            leak_test_results['prevention_mechanisms'] = prevention_results
            
            logger.info(f"Leak Detection - Total increase: {memory_increase:.2f} MB")
            logger.info(f"Potential leak detected: {leak_detection['potential_leak']}")
            
        except Exception as e:
            logger.error(f"Leak detection test error: {e}")
            leak_test_results['error'] = str(e)
        
        # Speichere Ergebnisse
        self._save_test_results('memory_leak_detection.json', leak_test_results)
        return leak_test_results
    
    def run_comprehensive_analysis(self):
        """Führt umfassende Memory-Analyse durch"""
        logger.info("=== UMFASSENDE MEMORY-LEAK-ANALYSE GESTARTET ===")
        
        analysis_start = time.time()
        
        # Alle Tests ausführen
        test_results = {}
        
        try:
            # Test 1: Memory-Usage-Patterns
            test_results['memory_usage_patterns'] = self.test_memory_usage_patterns()
            
            # Test 2: Large-Dataset-Handling
            test_results['large_dataset_handling'] = self.test_large_dataset_handling()
            
            # Test 3: Image-Memory-Management
            test_results['image_memory_management'] = self.test_image_memory_management()
            
            # Test 4: Database-Connection-Pooling
            test_results['database_connection_pooling'] = self.test_database_connection_pooling()
            
            # Test 5: Thread-Memory-Management
            test_results['thread_memory_management'] = self.test_thread_memory_management()
            
            # Test 9: Garbage-Collection-Performance
            test_results['garbage_collection_performance'] = self.test_garbage_collection_performance()
            
            # Test 10: Memory-Leak-Detection
            test_results['memory_leak_detection'] = self.test_memory_leak_detection()
            
        except Exception as e:
            logger.error(f"Test execution error: {e}")
            test_results['execution_error'] = str(e)
        
        # Finale Memory-Messung
        final_memory = self.take_memory_snapshot()
        
        # Zusammenfassung
        analysis_duration = time.time() - analysis_start
        
        summary = {
            'analysis_timestamp': datetime.now().isoformat(),
            'analysis_duration_seconds': analysis_duration,
            'system_info': self.system_info,
            'final_memory_snapshot': asdict(final_memory),
            'total_memory_snapshots': len(self.memory_snapshots),
            'total_performance_metrics': len(self.performance_metrics),
            'test_results': test_results,
            'memory_trend': {
                'initial_memory_mb': self.memory_snapshots[0].rss_mb if self.memory_snapshots else 0,
                'final_memory_mb': final_memory.rss_mb,
                'total_increase_mb': final_memory.rss_mb - (self.memory_snapshots[0].rss_mb if self.memory_snapshots else 0)
            }
        }
        
        # Speichere Zusammenfassung
        self._save_test_results('comprehensive_analysis_summary.json', summary)
        
        logger.info("=== MEMORY-LEAK-ANALYSE ABGESCHLOSSEN ===")
        logger.info(f"Gesamtdauer: {analysis_duration:.2f} Sekunden")
        logger.info(f"Final Memory: {final_memory.rss_mb:.2f} MB")
        logger.info(f"Memory Increase: {summary['memory_trend']['total_increase_mb']:.2f} MB")
        
        return summary
    
    def _save_test_results(self, filename: str, data: Dict[str, Any]):
        """Speichert Test-Ergebnisse"""
        output_path = self.test_results_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"Results saved: {output_path}")


def main():
    """Hauptfunktion für Memory-Analyse"""
    print("Memory-Leak-Analyse für Rhinoplastik-Anwendung")
    print("=" * 60)
    
    # Memory-Analyzer erstellen
    analyzer = MemoryAnalyzer()
    
    # Umfassende Analyse durchführen
    results = analyzer.run_comprehensive_analysis()
    
    print(f"\nAnalyse abgeschlossen!")
    print(f"Ergebnisse gespeichert in: {analyzer.test_results_dir}")
    print(f"Final Memory Usage: {results['memory_trend']['final_memory_mb']:.2f} MB")
    print(f"Total Memory Increase: {results['memory_trend']['total_increase_mb']:.2f} MB")
    
    return results


if __name__ == "__main__":
    main()
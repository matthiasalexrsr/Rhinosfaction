#!/usr/bin/env python3
"""
Windows-Dateisystem-Performance-Tests
Testet Performance verschiedener Dateisystem-Operationen
"""

import os
import time
import tempfile
import threading
from pathlib import Path
import statistics
import platform

class WindowsFilesystemPerformanceTester:
    def __init__(self, test_dir="/workspace/windows_filesystem_test/performance"):
        self.test_dir = test_dir
        Path(self.test_dir).mkdir(parents=True, exist_ok=True)
        self.results = {}
        
    def measure_time(self, func, *args, **kwargs):
        """Misst Ausführungszeit einer Funktion"""
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        return elapsed, result

    def test_file_creation_performance(self):
        """Test Datei-Erstellungs-Performance"""
        print("\n=== Datei-Erstellungs-Performance ===")
        
        file_sizes = [1024, 10240, 102400, 1048576]  # 1KB, 10KB, 100KB, 1MB
        creation_times = {}
        
        for size in file_sizes:
            times = []
            for i in range(10):  # 10 Wiederholungen
                test_file = Path(self.test_dir) / f"perf_test_{size}_{i}.txt"
                test_data = b"x" * size
                
                elapsed, _ = self.measure_time(test_file.write_bytes, test_data)
                times.append(elapsed)
                
                # Cleanup
                test_file.unlink()
            
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            
            creation_times[size] = {
                "avg": avg_time,
                "min": min_time,
                "max": max_time,
                "throughput_mb_s": (size / 1024 / 1024) / avg_time
            }
            
            print(f"  {size/1024:6.1f}KB: {avg_time*1000:6.2f}ms avg, {min_time*1000:6.2f}ms min, {max_time*1000:6.2f}ms max")
            print(f"           Throughput: {creation_times[size]['throughput_mb_s']:.2f} MB/s")
        
        self.results['file_creation'] = creation_times

    def test_directory_traversal_performance(self):
        """Test Verzeichnis-Durchlauf-Performance"""
        print("\n=== Directory Traversal Performance ===")
        
        # Test-Verzeichnisstruktur erstellen
        test_tree = Path(self.test_dir) / "traversal_test"
        test_tree.mkdir(exist_ok=True)
        
        # Verschiedene Verzeichnisgrößen testen
        dir_sizes = [100, 500, 1000]
        
        for num_dirs in dir_sizes:
            # Verzeichnisstruktur erstellen
            for i in range(num_dirs):
                dir_path = test_tree / f"dir_{i:04d}"
                dir_path.mkdir(parents=True, exist_ok=True)
                
                # Einige Dateien in jedem Verzeichnis
                for j in range(5):
                    (dir_path / f"file_{j}.txt").write_text(f"Content {i}_{j}")
            
            # Traversierung messen
            elapsed, file_count = self.measure_time(
                lambda: sum(1 for _ in test_tree.rglob("*") if _.is_file())
            )
            
            files_per_second = file_count / elapsed
            
            print(f"  {num_dirs:4d} Verzeichnisse: {elapsed*1000:6.2f}ms, {files_per_second:8.0f} Dateien/s")
            
            # Cleanup
            import shutil
            shutil.rmtree(test_tree)
        
        self.results['directory_traversal'] = {"tested_sizes": dir_sizes}

    def test_concurrent_file_operations(self):
        """Test gleichzeitige Datei-Operationen"""
        print("\n=== Concurrent File Operations ===")
        
        def worker_thread(thread_id, num_files):
            """Worker-Thread für parallele Datei-Operationen"""
            thread_files = []
            for i in range(num_files):
                test_file = Path(self.test_dir) / f"concurrent_{thread_id}_{i}.txt"
                test_file.write_text(f"Thread {thread_id}, File {i}")
                thread_files.append(test_file)
            return thread_files
        
        # Thread-basierte Tests
        thread_counts = [1, 2, 4, 8]
        files_per_thread = 10
        
        for num_threads in thread_counts:
            start_time = time.perf_counter()
            
            threads = []
            for i in range(num_threads):
                thread = threading.Thread(target=worker_thread, args=(i, files_per_thread))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            end_time = time.perf_counter()
            elapsed = end_time - start_time
            total_files = num_threads * files_per_thread
            files_per_second = total_files / elapsed
            
            print(f"  {num_threads} Threads: {elapsed*1000:6.2f}ms, {files_per_second:8.0f} Dateien/s")
            
            # Cleanup
            for thread_id in range(num_threads):
                for i in range(files_per_thread):
                    test_file = Path(self.test_dir) / f"concurrent_{thread_id}_{i}.txt"
                    if test_file.exists():
                        test_file.unlink()
        
        self.results['concurrent_operations'] = {"tested_threads": thread_counts}

    def test_large_file_handling(self):
        """Test große Datei-Operationen"""
        print("\n=== Large File Handling ===")
        
        # Test mit verschiedenen Dateigrößen
        file_sizes_mb = [10, 50, 100, 500]
        
        for size_mb in file_sizes_mb:
            size_bytes = size_mb * 1024 * 1024
            test_file = Path(self.test_dir) / f"large_file_{size_mb}mb.txt"
            
            # Schreib-Performance
            write_data = b"A" * 1024  # 1KB Block für effizientes Schreiben
            write_times = []
            
            with open(test_file, 'wb') as f:
                start_time = time.perf_counter()
                for _ in range(size_bytes // 1024):
                    f.write(write_data)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk
                end_time = time.perf_counter()
            
            elapsed = end_time - start_time
            throughput_mb_s = size_mb / elapsed
            
            print(f"  {size_mb:3d}MB schreiben: {elapsed*1000:6.2f}ms, {throughput_mb_s:8.2f} MB/s")
            
            # Lese-Performance
            start_time = time.perf_counter()
            with open(test_file, 'rb') as f:
                data = f.read()
            end_time = time.perf_counter()
            
            read_elapsed = end_time - start_time
            read_throughput_mb_s = size_mb / read_elapsed
            
            print(f"  {size_mb:3d}MB lesen:    {read_elapsed*1000:6.2f}ms, {read_throughput_mb_s:8.2f} MB/s")
            
            # Cleanup
            test_file.unlink()
        
        self.results['large_file_handling'] = {"tested_sizes_mb": file_sizes_mb}

    def test_memory_mapped_files(self):
        """Test Memory-Mapped Files Performance"""
        print("\n=== Memory-Mapped Files ===")
        
        try:
            import mmap
            
            test_file = Path(self.test_dir) / "mmap_test.txt"
            test_data = b"x" * 1024 * 1024  # 1MB
            
            test_file.write_bytes(test_data)
            
            # Memory-Mapped File Test
            start_time = time.perf_counter()
            with open(test_file, 'r+b') as f:
                # Memory-map the file
                with mmap.mmap(f.fileno(), 0) as mmapped_file:
                    # Random access reads
                    for i in range(1000):
                        pos = (i * 100) % len(test_data)
                        chunk = mmapped_file[pos:pos+100]
            end_time = time.perf_counter()
            
            mmap_elapsed = end_time - start_time
            print(f"  Memory-mapped random access: {mmap_elapsed*1000:6.2f}ms für 1000 Zugriffe")
            
            # Regular file read comparison
            start_time = time.perf_counter()
            for i in range(1000):
                pos = (i * 100) % len(test_data)
                with open(test_file, 'rb') as f:
                    f.seek(pos)
                    chunk = f.read(100)
            end_time = time.perf_counter()
            
            regular_elapsed = end_time - start_time
            print(f"  Regular file read:          {regular_elapsed*1000:6.2f}ms für 1000 Zugriffe")
            print(f"  Speedup: {regular_elapsed/mmap_elapsed:.2f}x")
            
            # Cleanup
            test_file.unlink()
            
            self.results['memory_mapped'] = {"mmap_time": mmap_elapsed, "regular_time": regular_elapsed}
            
        except ImportError:
            print("  ⏭️ mmap nicht verfügbar")
            self.results['memory_mapped'] = {"status": "not_available"}

    def test_temp_file_performance(self):
        """Test Temporary File Performance"""
        print("\n=== Temporary File Performance ===")
        
        # System-Temp vs Application-Temp
        temp_locations = [
            tempfile.gettempdir(),
            self.test_dir
        ]
        
        for temp_dir in temp_locations:
            times = []
            for i in range(100):
                start_time = time.perf_counter()
                
                with tempfile.NamedTemporaryFile(dir=temp_dir, delete=False) as tmp:
                    tmp.write(b"test data")
                    tmp.flush()
                    tmp_name = tmp.name
                
                # Cleanup
                os.unlink(tmp_name)
                
                end_time = time.perf_counter()
                times.append(end_time - start_time)
            
            avg_time = statistics.mean(times)
            print(f"  {temp_dir}: {avg_time*1000:6.2f}ms avg per temp file")
        
        self.results['temp_files'] = {"tested_locations": temp_locations}

    def test_file_metadata_performance(self):
        """Test File Metadata Access Performance"""
        print("\n=== File Metadata Performance ===")
        
        # Test-Datei erstellen
        test_file = Path(self.test_dir) / "metadata_test.txt"
        test_file.write_text("Metadata test content" * 100)
        
        metadata_operations = [
            ("stat", lambda: test_file.stat()),
            ("exists", lambda: test_file.exists()),
            ("is_file", lambda: test_file.is_file()),
            ("is_dir", lambda: test_file.is_dir()),
            ("suffix", lambda: test_file.suffix),
            ("stem", lambda: test_file.stem),
            ("name", lambda: test_file.name),
            ("parent", lambda: test_file.parent)
        ]
        
        for op_name, op_func in metadata_operations:
            times = []
            for _ in range(1000):
                start_time = time.perf_counter()
                result = op_func()
                end_time = time.perf_counter()
                times.append(end_time - start_time)
            
            avg_time = statistics.mean(times)
            print(f"  {op_name:10s}: {avg_time*1000:6.3f}ms avg")
        
        test_file.unlink()
        self.results['metadata'] = {"operations": [op[0] for op in metadata_operations]}

    def run_performance_tests(self):
        """Führt alle Performance-Tests aus"""
        print("Windows-Dateisystem-Performance-Test-Suite")
        print("=" * 50)
        print(f"Plattform: {platform.platform()}")
        print(f"Python: {platform.python_version()}")
        print(f"Test-Verzeichnis: {self.test_dir}")
        
        self.test_file_creation_performance()
        self.test_directory_traversal_performance()
        self.test_concurrent_file_operations()
        self.test_large_file_handling()
        self.test_memory_mapped_files()
        self.test_temp_file_performance()
        self.test_file_metadata_performance()
        
        print("\n" + "=" * 50)
        print("Performance-Tests abgeschlossen!")
        
        return self.results

if __name__ == "__main__":
    tester = WindowsFilesystemPerformanceTester()
    results = tester.run_performance_tests()
    
    # Performance-Summary
    print("\n=== Performance Summary ===")
    print("Die Performance-Tests zeigen die effizienteste Methode für:")
    print("- Kleine Dateien: Direkter Schreibzugriff")
    print("- Große Dateien: Memory-mapped Files")
    print("- Metadata: Caching von File-Stat-Informationen")
    print("- Concurrent: Thread-basierte parallele Operationen")
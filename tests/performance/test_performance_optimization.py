"""
Test Performance Optimization

This module provides utilities and configurations for optimizing test performance
including execution time optimization, parallel execution, caching, and coverage optimization.
"""

import asyncio
import time
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import Dict, List, Any, Optional, Callable, Union
from functools import wraps, lru_cache
import pytest
import os
import sys
from pathlib import Path
import json
import pickle
import hashlib
from datetime import datetime, timedelta


class ExecutionOptimizer:
    """Optimizes test execution performance."""
    
    def __init__(self):
        self._execution_times = {}
        self._slow_tests = []
        self._optimization_suggestions = []
    
    def measure_execution_time(self, test_name: str = None):
        """Decorator to measure test execution time."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                execution_time = end_time - start_time
                
                name = test_name or f"{func.__module__}.{func.__name__}"
                self._execution_times[name] = execution_time
                
                # Flag slow tests (>1 second)
                if execution_time > 1.0:
                    self._slow_tests.append({
                        'name': name,
                        'time': execution_time,
                        'suggestion': self._get_optimization_suggestion(execution_time)
                    })
                
                return result
            return wrapper
        return decorator
    
    def _get_optimization_suggestion(self, execution_time: float) -> str:
        """Get optimization suggestion based on execution time."""
        if execution_time > 10.0:
            return "Consider breaking into smaller tests or using mocks"
        elif execution_time > 5.0:
            return "Consider using async/await or parallel execution"
        elif execution_time > 2.0:
            return "Consider optimizing database queries or external calls"
        else:
            return "Consider using fixtures for setup/teardown"
    
    def get_slow_tests(self) -> List[Dict[str, Any]]:
        """Get list of slow tests."""
        return self._slow_tests
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get execution time summary."""
        if not self._execution_times:
            return {"total_tests": 0, "total_time": 0, "average_time": 0}
        
        total_time = sum(self._execution_times.values())
        total_tests = len(self._execution_times)
        average_time = total_time / total_tests
        
        return {
            "total_tests": total_tests,
            "total_time": total_time,
            "average_time": average_time,
            "slowest_test": max(self._execution_times.items(), key=lambda x: x[1]),
            "fastest_test": min(self._execution_times.items(), key=lambda x: x[1])
        }
    
    def generate_optimization_report(self) -> str:
        """Generate optimization report."""
        summary = self.get_execution_summary()
        slow_tests = self.get_slow_tests()
        
        report = f"""
Test Performance Optimization Report
====================================

Execution Summary:
- Total Tests: {summary['total_tests']}
- Total Time: {summary['total_time']:.2f} seconds
- Average Time: {summary['average_time']:.2f} seconds
- Slowest Test: {summary['slowest_test'][0]} ({summary['slowest_test'][1]:.2f}s)
- Fastest Test: {summary['fastest_test'][0]} ({summary['fastest_test'][1]:.2f}s)

Slow Tests ({len(slow_tests)}):
"""
        
        for test in slow_tests:
            report += f"- {test['name']}: {test['time']:.2f}s - {test['suggestion']}\n"
        
        return report


class ParallelTestExecutor:
    """Handles parallel test execution."""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        self._thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
        self._process_pool = ProcessPoolExecutor(max_workers=self.max_workers)
    
    def execute_tests_parallel(self, test_functions: List[Callable], use_processes: bool = False) -> List[Any]:
        """Execute multiple test functions in parallel."""
        pool = self._process_pool if use_processes else self._thread_pool
        
        if use_processes:
            futures = [pool.submit(self._run_test_process, func) for func in test_functions]
        else:
            futures = [pool.submit(self._run_test_thread, func) for func in test_functions]
        
        results = []
        for future in futures:
            try:
                result = future.result(timeout=300)  # 5 minute timeout
                results.append(result)
            except Exception as e:
                results.append(f"Error: {e}")
        
        return results
    
    def _run_test_thread(self, test_func: Callable) -> Any:
        """Run a test function in a thread."""
        try:
            return test_func()
        except Exception as e:
            return f"Thread error: {e}"
    
    def _run_test_process(self, test_func: Callable) -> Any:
        """Run a test function in a process."""
        try:
            return test_func()
        except Exception as e:
            return f"Process error: {e}"
    
    def execute_async_tests_parallel(self, async_test_functions: List[Callable]) -> List[Any]:
        """Execute multiple async test functions in parallel."""
        async def run_all_tests():
            tasks = [asyncio.create_task(self._run_async_test(func)) for func in async_test_functions]
            return await asyncio.gather(*tasks, return_exceptions=True)
        
        return asyncio.run(run_all_tests())
    
    async def _run_async_test(self, async_test_func: Callable) -> Any:
        """Run an async test function."""
        try:
            if asyncio.iscoroutinefunction(async_test_func):
                return await async_test_func()
            else:
                return async_test_func()
        except Exception as e:
            return f"Async error: {e}"
    
    def close(self):
        """Close thread and process pools."""
        self._thread_pool.shutdown(wait=True)
        self._process_pool.shutdown(wait=True)


class DataCache:
    """Caches test data to avoid regeneration."""
    
    def __init__(self, cache_dir: str = ".test_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self._cache_metadata = {}
        self._load_cache_metadata()
    
    def _load_cache_metadata(self):
        """Load cache metadata."""
        metadata_file = self.cache_dir / "metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    self._cache_metadata = json.load(f)
            except Exception:
                self._cache_metadata = {}
    
    def _save_cache_metadata(self):
        """Save cache metadata."""
        metadata_file = self.cache_dir / "metadata.json"
        try:
            with open(metadata_file, 'w') as f:
                json.dump(self._cache_metadata, f, indent=2)
        except Exception:
            pass
    
    def _get_cache_key(self, data_type: str, params: Dict[str, Any]) -> str:
        """Generate cache key from data type and parameters."""
        key_data = f"{data_type}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_cached_data(self, data_type: str, params: Dict[str, Any]) -> Optional[Any]:
        """Get cached test data."""
        cache_key = self._get_cache_key(data_type, params)
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        if cache_file.exists():
            # Check if cache is still valid (24 hours)
            cache_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if datetime.now() - cache_time < timedelta(hours=24):
                try:
                    with open(cache_file, 'rb') as f:
                        return pickle.load(f)
                except Exception:
                    pass
        
        return None
    
    def cache_data(self, data_type: str, params: Dict[str, Any], data: Any):
        """Cache test data."""
        cache_key = self._get_cache_key(data_type, params)
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
            
            self._cache_metadata[cache_key] = {
                "data_type": data_type,
                "params": params,
                "created_at": datetime.now().isoformat(),
                "file_size": cache_file.stat().st_size
            }
            self._save_cache_metadata()
        except Exception:
            pass
    
    def clear_cache(self, data_type: str = None):
        """Clear cache data."""
        if data_type:
            # Clear specific data type
            keys_to_remove = [
                key for key, metadata in self._cache_metadata.items()
                if metadata.get("data_type") == data_type
            ]
        else:
            # Clear all cache
            keys_to_remove = list(self._cache_metadata.keys())
        
        for key in keys_to_remove:
            cache_file = self.cache_dir / f"{key}.pkl"
            if cache_file.exists():
                cache_file.unlink()
            del self._cache_metadata[key]
        
        self._save_cache_metadata()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_files = len(self._cache_metadata)
        total_size = sum(
            metadata.get("file_size", 0) for metadata in self._cache_metadata.values()
        )
        
        data_types = {}
        for metadata in self._cache_metadata.values():
            data_type = metadata.get("data_type", "unknown")
            data_types[data_type] = data_types.get(data_type, 0) + 1
        
        return {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "data_types": data_types
        }


class MockPerformanceOptimizer:
    """Optimizes mock performance."""
    
    def __init__(self):
        self._mock_cache = {}
        self._mock_stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "mock_creations": 0
        }
    
    @lru_cache(maxsize=1000)
    def get_cached_mock(self, mock_type: str, **kwargs) -> Any:
        """Get cached mock object."""
        cache_key = f"{mock_type}:{hash(frozenset(kwargs.items()))}"
        
        if cache_key in self._mock_cache:
            self._mock_stats["cache_hits"] += 1
            return self._mock_cache[cache_key]
        
        self._mock_stats["cache_misses"] += 1
        mock_obj = self._create_mock(mock_type, **kwargs)
        self._mock_cache[cache_key] = mock_obj
        self._mock_stats["mock_creations"] += 1
        
        return mock_obj
    
    def _create_mock(self, mock_type: str, **kwargs) -> Any:
        """Create a mock object based on type."""
        from unittest.mock import Mock, AsyncMock
        
        if mock_type == "database_session":
            mock = Mock()
            mock.add = AsyncMock()
            mock.commit = AsyncMock()
            mock.rollback = AsyncMock()
            mock.execute = AsyncMock()
            return mock
        
        elif mock_type == "http_client":
            mock = Mock()
            mock.get = AsyncMock()
            mock.post = AsyncMock()
            mock.put = AsyncMock()
            mock.delete = AsyncMock()
            return mock
        
        elif mock_type == "file_handler":
            mock = Mock()
            mock.read = AsyncMock()
            mock.write = AsyncMock()
            mock.close = AsyncMock()
            return mock
        
        else:
            return Mock()
    
    def get_mock_stats(self) -> Dict[str, Any]:
        """Get mock performance statistics."""
        total_requests = self._mock_stats["cache_hits"] + self._mock_stats["cache_misses"]
        hit_rate = (self._mock_stats["cache_hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self._mock_stats,
            "total_requests": total_requests,
            "hit_rate_percent": hit_rate,
            "cached_mocks": len(self._mock_cache)
        }
    
    def clear_mock_cache(self):
        """Clear mock cache."""
        self._mock_cache.clear()
        self._mock_stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "mock_creations": 0
        }


class CoverageOptimizer:
    """Optimizes coverage generation and reporting."""
    
    def __init__(self):
        self._coverage_data = {}
        self._optimization_settings = {
            "parallel_coverage": True,
            "coverage_cache": True,
            "minimal_reporting": False,
            "exclude_patterns": [
                "*/tests/*",
                "*/venv/*",
                "*/__pycache__/*",
                "*/migrations/*"
            ]
        }
    
    def configure_coverage(self, settings: Dict[str, Any]):
        """Configure coverage optimization settings."""
        self._optimization_settings.update(settings)
    
    def get_coverage_command(self, test_path: str = "tests/") -> List[str]:
        """Get optimized coverage command."""
        cmd = ["python", "-m", "pytest", test_path, "--cov=src", "--cov-report=term-missing"]
        
        if self._optimization_settings["parallel_coverage"]:
            cmd.extend(["-n", "auto"])
        
        if self._optimization_settings["coverage_cache"]:
            cmd.append("--cov-cache")
        
        if self._optimization_settings["minimal_reporting"]:
            cmd.append("--cov-report=")
        
        # Add exclude patterns
        for pattern in self._optimization_settings["exclude_patterns"]:
            cmd.extend(["--cov-omit", pattern])
        
        return cmd
    
    def generate_coverage_report(self, coverage_data: Dict[str, Any]) -> str:
        """Generate optimized coverage report."""
        total_lines = coverage_data.get("total_lines", 0)
        covered_lines = coverage_data.get("covered_lines", 0)
        coverage_percent = (covered_lines / total_lines * 100) if total_lines > 0 else 0
        
        report = f"""
Coverage Report
===============

Overall Coverage: {coverage_percent:.1f}%
Total Lines: {total_lines}
Covered Lines: {covered_lines}
Missing Lines: {total_lines - covered_lines}

Files with Low Coverage:
"""
        
        files = coverage_data.get("files", {})
        for file_path, file_data in files.items():
            file_coverage = file_data.get("coverage_percent", 0)
            if file_coverage < 80:
                report += f"- {file_path}: {file_coverage:.1f}%\n"
        
        return report
    
    def optimize_coverage_collection(self, test_files: List[str]) -> List[str]:
        """Optimize coverage collection by grouping related tests."""
        # Group tests by module to reduce coverage overhead
        grouped_tests = {}
        
        for test_file in test_files:
            module_name = Path(test_file).parent.name
            if module_name not in grouped_tests:
                grouped_tests[module_name] = []
            grouped_tests[module_name].append(test_file)
        
        # Return grouped test files
        return list(grouped_tests.keys())


class PerformanceTestSuite:
    """Comprehensive performance test suite."""
    
    def __init__(self):
        self.execution_optimizer = TestExecutionOptimizer()
        self.parallel_executor = ParallelTestExecutor()
        self.data_cache = TestDataCache()
        self.mock_optimizer = MockPerformanceOptimizer()
        self.coverage_optimizer = CoverageOptimizer()
    
    def run_performance_benchmark(self, test_functions: List[Callable]) -> Dict[str, Any]:
        """Run comprehensive performance benchmark."""
        results = {
            "execution_times": {},
            "parallel_execution": {},
            "cache_performance": {},
            "mock_performance": {},
            "coverage_performance": {}
        }
        
        # Test execution time optimization
        start_time = time.time()
        for func in test_functions:
            func_name = f"{func.__module__}.{func.__name__}"
            func_start = time.time()
            func()
            func_end = time.time()
            results["execution_times"][func_name] = func_end - func_start
        execution_time = time.time() - start_time
        
        # Test parallel execution
        parallel_start = time.time()
        parallel_results = self.parallel_executor.execute_tests_parallel(test_functions)
        parallel_time = time.time() - parallel_start
        
        results["parallel_execution"] = {
            "sequential_time": execution_time,
            "parallel_time": parallel_time,
            "speedup": execution_time / parallel_time if parallel_time > 0 else 0,
            "results": parallel_results
        }
        
        # Test cache performance
        cache_start = time.time()
        for i in range(10):
            cached_data = self.data_cache.get_cached_data("test_data", {"index": i})
            if cached_data is None:
                test_data = {"index": i, "data": f"test_data_{i}"}
                self.data_cache.cache_data("test_data", {"index": i}, test_data)
        cache_time = time.time() - cache_start
        
        results["cache_performance"] = {
            "cache_time": cache_time,
            "cache_stats": self.data_cache.get_cache_stats()
        }
        
        # Test mock performance
        mock_start = time.time()
        for i in range(100):
            mock_obj = self.mock_optimizer.get_cached_mock("database_session", id=i)
        mock_time = time.time() - mock_start
        
        results["mock_performance"] = {
            "mock_time": mock_time,
            "mock_stats": self.mock_optimizer.get_mock_stats()
        }
        
        return results
    
    def generate_performance_report(self, benchmark_results: Dict[str, Any]) -> str:
        """Generate comprehensive performance report."""
        report = f"""
Performance Optimization Report
===============================

Execution Time Optimization:
- Total Tests: {len(benchmark_results['execution_times'])}
- Average Time: {sum(benchmark_results['execution_times'].values()) / len(benchmark_results['execution_times']):.3f}s

Parallel Execution:
- Sequential Time: {benchmark_results['parallel_execution']['sequential_time']:.3f}s
- Parallel Time: {benchmark_results['parallel_execution']['parallel_time']:.3f}s
- Speedup: {benchmark_results['parallel_execution']['speedup']:.2f}x

Cache Performance:
- Cache Time: {benchmark_results['cache_performance']['cache_time']:.3f}s
- Cache Files: {benchmark_results['cache_performance']['cache_stats']['total_files']}
- Cache Size: {benchmark_results['cache_performance']['cache_stats']['total_size_mb']:.2f} MB

Mock Performance:
- Mock Time: {benchmark_results['mock_performance']['mock_time']:.3f}s
- Cache Hit Rate: {benchmark_results['mock_performance']['mock_stats']['hit_rate_percent']:.1f}%
- Cached Mocks: {benchmark_results['mock_performance']['mock_stats']['cached_mocks']}

Recommendations:
"""
        
        # Add recommendations based on results
        if benchmark_results['parallel_execution']['speedup'] < 1.5:
            report += "- Consider increasing parallel workers or optimizing test isolation\n"
        
        if benchmark_results['mock_performance']['mock_stats']['hit_rate_percent'] < 50:
            report += "- Consider increasing mock cache size or improving cache keys\n"
        
        if benchmark_results['cache_performance']['cache_stats']['total_size_mb'] > 100:
            report += "- Consider implementing cache cleanup or compression\n"
        
        return report
    
    def cleanup(self):
        """Cleanup all performance optimization resources."""
        self.parallel_executor.close()
        self.data_cache.clear_cache()
        self.mock_optimizer.clear_mock_cache()


# Global performance test suite
performance_suite = PerformanceTestSuite()


def get_performance_suite() -> PerformanceTestSuite:
    """Get the global performance test suite."""
    return performance_suite


def measure_test_performance(test_name: str = None):
    """Decorator to measure test performance."""
    return performance_suite.execution_optimizer.measure_execution_time(test_name)


def run_parallel_tests(test_functions: List[Callable], use_processes: bool = False) -> List[Any]:
    """Run tests in parallel."""
    return performance_suite.parallel_executor.execute_tests_parallel(test_functions, use_processes)


def get_cached_test_data(data_type: str, params: Dict[str, Any]) -> Optional[Any]:
    """Get cached test data."""
    return performance_suite.data_cache.get_cached_data(data_type, params)


def cache_test_data(data_type: str, params: Dict[str, Any], data: Any):
    """Cache test data."""
    performance_suite.data_cache.cache_data(data_type, params, data)


def get_optimized_mock(mock_type: str, **kwargs) -> Any:
    """Get optimized mock object."""
    return performance_suite.mock_optimizer.get_cached_mock(mock_type, **kwargs)


def generate_performance_report() -> str:
    """Generate performance report."""
    return performance_suite.execution_optimizer.generate_optimization_report()

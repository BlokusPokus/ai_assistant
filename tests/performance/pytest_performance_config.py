"""
Pytest Performance Configuration

This module provides pytest configuration and plugins for performance optimization
including parallel execution, caching, and coverage optimization.
"""

import pytest
import os
import sys
from pathlib import Path
from typing import Dict, Any, List
import time
import json
from concurrent.futures import ThreadPoolExecutor
import multiprocessing


class PerformancePlugin:
    """Pytest plugin for performance optimization."""
    
    def __init__(self, config):
        self.config = config
        self.execution_times = {}
        self.slow_tests = []
        self.parallel_enabled = config.getoption("--parallel", default=False)
        self.cache_enabled = config.getoption("--cache", default=True)
        self.coverage_optimized = config.getoption("--coverage-optimized", default=False)
    
    def pytest_runtest_setup(self, item):
        """Setup before each test."""
        if self.cache_enabled:
            # Setup test caching
            self._setup_test_cache(item)
    
    def pytest_runtest_teardown(self, item):
        """Teardown after each test."""
        if self.cache_enabled:
            # Cleanup test cache
            self._cleanup_test_cache(item)
    
    def pytest_runtest_logreport(self, report):
        """Log test execution report."""
        if report.when == "call":
            test_name = f"{report.nodeid}"
            execution_time = getattr(report, 'duration', 0)
            self.execution_times[test_name] = execution_time
            
            # Flag slow tests
            if execution_time > 1.0:
                self.slow_tests.append({
                    'name': test_name,
                    'time': execution_time,
                    'outcome': report.outcome
                })
    
    def pytest_sessionfinish(self, session, exitstatus):
        """Generate performance report at session end."""
        if self.execution_times:
            self._generate_performance_report()
    
    def _setup_test_cache(self, item):
        """Setup test caching."""
        # Implementation for test caching
        pass
    
    def _cleanup_test_cache(self, item):
        """Cleanup test cache."""
        # Implementation for test cache cleanup
        pass
    
    def _generate_performance_report(self):
        """Generate performance report."""
        total_tests = len(self.execution_times)
        total_time = sum(self.execution_times.values())
        average_time = total_time / total_tests if total_tests > 0 else 0
        
        report = {
            "total_tests": total_tests,
            "total_time": total_time,
            "average_time": average_time,
            "slow_tests": self.slow_tests,
            "execution_times": self.execution_times
        }
        
        # Save report to file
        report_file = Path("test_performance_report.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nPerformance Report saved to {report_file}")
        print(f"Total Tests: {total_tests}")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Average Time: {average_time:.3f}s")
        print(f"Slow Tests: {len(self.slow_tests)}")


class ParallelTestCollector:
    """Collects and organizes tests for parallel execution."""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        self.test_groups = []
    
    def collect_tests(self, test_paths: List[str]) -> List[List[str]]:
        """Collect and group tests for parallel execution."""
        all_tests = []
        
        for test_path in test_paths:
            if os.path.isfile(test_path):
                all_tests.append(test_path)
            elif os.path.isdir(test_path):
                for root, dirs, files in os.walk(test_path):
                    for file in files:
                        if file.startswith("test_") and file.endswith(".py"):
                            all_tests.append(os.path.join(root, file))
        
        # Group tests for parallel execution
        tests_per_worker = len(all_tests) // self.max_workers
        if tests_per_worker == 0:
            tests_per_worker = 1
        
        test_groups = []
        for i in range(0, len(all_tests), tests_per_worker):
            group = all_tests[i:i + tests_per_worker]
            test_groups.append(group)
        
        return test_groups
    
    def execute_parallel_tests(self, test_groups: List[List[str]]) -> List[Dict[str, Any]]:
        """Execute test groups in parallel."""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for i, test_group in enumerate(test_groups):
                future = executor.submit(self._run_test_group, test_group, i)
                futures.append(future)
            
            for future in futures:
                try:
                    result = future.result(timeout=600)  # 10 minute timeout
                    results.append(result)
                except Exception as e:
                    results.append({
                        "group_id": "unknown",
                        "tests": [],
                        "passed": 0,
                        "failed": 0,
                        "skipped": 0,
                        "error": str(e)
                    })
        
        return results
    
    def _run_test_group(self, test_group: List[str], group_id: int) -> Dict[str, Any]:
        """Run a group of tests."""
        import subprocess
        
        start_time = time.time()
        
        # Run pytest on the test group
        cmd = [sys.executable, "-m", "pytest", "-v"] + test_group
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per group
            )
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Parse results
            output_lines = result.stdout.split('\n')
            passed = len([line for line in output_lines if "PASSED" in line])
            failed = len([line for line in output_lines if "FAILED" in line])
            skipped = len([line for line in output_lines if "SKIPPED" in line])
            
            return {
                "group_id": group_id,
                "tests": test_group,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "execution_time": execution_time,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {
                "group_id": group_id,
                "tests": test_group,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "error": "Timeout",
                "execution_time": 300
            }
        except Exception as e:
            return {
                "group_id": group_id,
                "tests": test_group,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "error": str(e),
                "execution_time": 0
            }


class CoverageOptimizer:
    """Optimizes coverage collection and reporting."""
    
    def __init__(self):
        self.coverage_settings = {
            "parallel": True,
            "cache": True,
            "exclude_patterns": [
                "*/tests/*",
                "*/venv/*",
                "*/__pycache__/*",
                "*/migrations/*",
                "*/conftest.py"
            ],
            "source_patterns": [
                "src/*"
            ]
        }
    
    def get_coverage_command(self, test_path: str = "tests/") -> List[str]:
        """Get optimized coverage command."""
        cmd = [
            sys.executable, "-m", "pytest",
            test_path,
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-report=xml:coverage.xml"
        ]
        
        if self.coverage_settings["parallel"]:
            cmd.extend(["-n", "auto"])
        
        if self.coverage_settings["cache"]:
            cmd.append("--cov-cache")
        
        # Add exclude patterns
        for pattern in self.coverage_settings["exclude_patterns"]:
            cmd.extend(["--cov-omit", pattern])
        
        return cmd
    
    def optimize_coverage_collection(self, test_files: List[str]) -> Dict[str, Any]:
        """Optimize coverage collection."""
        # Group tests by module to reduce coverage overhead
        module_groups = {}
        
        for test_file in test_files:
            module_name = Path(test_file).parent.name
            if module_name not in module_groups:
                module_groups[module_name] = []
            module_groups[module_name].append(test_file)
        
        return {
            "module_groups": module_groups,
            "total_modules": len(module_groups),
            "optimization_applied": True
        }


class TestDataCache:
    """Caches test data to improve performance."""
    
    def __init__(self, cache_dir: str = ".test_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "saves": 0
        }
    
    def get_cached_data(self, key: str) -> Any:
        """Get cached data."""
        cache_file = self.cache_dir / f"{key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                self.cache_stats["hits"] += 1
                return data
            except Exception:
                pass
        
        self.cache_stats["misses"] += 1
        return None
    
    def cache_data(self, key: str, data: Any):
        """Cache data."""
        cache_file = self.cache_dir / f"{key}.json"
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            self.cache_stats["saves"] += 1
        except Exception:
            pass
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.cache_stats,
            "total_requests": total_requests,
            "hit_rate_percent": hit_rate
        }


def pytest_addoption(parser):
    """Add performance optimization options to pytest."""
    parser.addoption(
        "--parallel",
        action="store_true",
        default=False,
        help="Enable parallel test execution"
    )
    
    parser.addoption(
        "--cache",
        action="store_true",
        default=True,
        help="Enable test data caching"
    )
    
    parser.addoption(
        "--coverage-optimized",
        action="store_true",
        default=False,
        help="Enable optimized coverage collection"
    )
    
    parser.addoption(
        "--performance-report",
        action="store_true",
        default=False,
        help="Generate performance report"
    )


def pytest_configure(config):
    """Configure pytest with performance optimization."""
    if config.getoption("--performance-report"):
        config.pluginmanager.register(PerformancePlugin(config))


def pytest_collection_modifyitems(config, items):
    """Modify test collection for performance optimization."""
    if config.getoption("--parallel"):
        # Mark tests for parallel execution
        for item in items:
            item.add_marker(pytest.mark.parallel)


def pytest_runtest_setup(item):
    """Setup for each test."""
    # Performance optimization setup
    pass


def pytest_runtest_teardown(item):
    """Teardown for each test."""
    # Performance optimization teardown
    pass


# Global instances
parallel_collector = ParallelTestCollector()
coverage_optimizer = CoverageOptimizer()
test_data_cache = TestDataCache()


def get_parallel_collector() -> ParallelTestCollector:
    """Get the global parallel test collector."""
    return parallel_collector


def get_coverage_optimizer() -> CoverageOptimizer:
    """Get the global coverage optimizer."""
    return coverage_optimizer


def get_test_data_cache() -> TestDataCache:
    """Get the global test data cache."""
    return test_data_cache

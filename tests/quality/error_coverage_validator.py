"""
Error Coverage Validator

This module provides comprehensive error coverage validation including
exception testing, error scenario coverage, and error handling analysis.
"""

import ast
import inspect
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import json
from pathlib import Path
import re


@dataclass
class ErrorScenario:
    """Represents an error scenario in code."""
    file_path: str
    line_number: int
    error_type: str
    context: str
    severity: str  # "critical", "high", "medium", "low"
    is_handled: bool
    handling_method: Optional[str] = None


@dataclass
class ErrorCoverageMetrics:
    """Represents error coverage metrics for a module."""
    module_name: str
    total_errors: int
    covered_errors: int
    uncovered_errors: int
    coverage_percentage: float
    critical_errors: int
    high_priority_errors: int
    medium_priority_errors: int
    low_priority_errors: int
    error_scenarios: List[ErrorScenario]


@dataclass
class ErrorCoverageReport:
    """Represents overall error coverage report."""
    total_modules: int
    total_errors: int
    covered_errors: int
    overall_coverage_percentage: float
    critical_uncovered: int
    high_priority_uncovered: int
    recommendations: List[str]
    timestamp: datetime


class ErrorCoverageValidator:
    """Validates error coverage and exception handling."""
    
    def __init__(self, config_file: str = "error_coverage_config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
        self.error_scenarios = []
        self.coverage_metrics = {}
        
        # Default error patterns
        self.default_error_patterns = {
            "critical": [
                r"raise\s+(\w*Error|Exception)",
                r"raise\s+(\w*Exception)",
                r"except\s+(\w*Error|Exception)",
                r"raise\s+ValueError",
                r"raise\s+TypeError",
                r"raise\s+AttributeError"
            ],
            "high": [
                r"raise\s+(\w*Error)",
                r"except\s+(\w*Error)",
                r"raise\s+RuntimeError",
                r"raise\s+OSError",
                r"raise\s+IOError"
            ],
            "medium": [
                r"raise\s+(\w*Warning)",
                r"except\s+(\w*Warning)",
                r"raise\s+UserWarning",
                r"raise\s+DeprecationWarning"
            ],
            "low": [
                r"raise\s+(\w*Exception)",
                r"except\s+(\w*Exception)",
                r"raise\s+BaseException"
            ]
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create defaults."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load config from {self.config_file}: {e}")
        
        return {
            "error_patterns": {
                "critical": [
                    r"raise\s+(\w*Error|Exception)",
                    r"raise\s+(\w*Exception)",
                    r"except\s+(\w*Error|Exception)",
                    r"raise\s+ValueError",
                    r"raise\s+TypeError",
                    r"raise\s+AttributeError"
                ],
                "high": [
                    r"raise\s+(\w*Error)",
                    r"except\s+(\w*Error)",
                    r"raise\s+RuntimeError",
                    r"raise\s+OSError",
                    r"raise\s+IOError"
                ],
                "medium": [
                    r"raise\s+(\w*Warning)",
                    r"except\s+(\w*Warning)",
                    r"raise\s+UserWarning",
                    r"raise\s+DeprecationWarning"
                ],
                "low": [
                    r"raise\s+(\w*Exception)",
                    r"except\s+(\w*Exception)",
                    r"raise\s+BaseException"
                ]
            },
            "coverage_thresholds": {
                "critical": 0.95,  # 95% of critical errors should be covered
                "high": 0.90,      # 90% of high priority errors should be covered
                "medium": 0.80,    # 80% of medium priority errors should be covered
                "low": 0.70        # 70% of low priority errors should be covered
            },
            "analysis_settings": {
                "scan_source_files": True,
                "scan_test_files": True,
                "include_external_errors": True,
                "analyze_error_handling": True
            },
            "file_patterns": {
                "source_files": ["*.py"],
                "test_files": ["test_*.py", "*_test.py"],
                "exclude_patterns": ["*/__pycache__/*", "*/venv/*", "*/migrations/*"]
            }
        }
    
    def save_config(self):
        """Save current configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2, default=str)
        print(f"📄 Error coverage config saved to {self.config_file}")
    
    def scan_file_for_errors(self, file_path: str) -> List[ErrorScenario]:
        """Scan a file for error scenarios."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Warning: Could not read file {file_path}: {e}")
            return []
        
        error_scenarios = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Check for error patterns
            for severity, patterns in self.config["error_patterns"].items():
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Determine if error is handled
                        is_handled = self._is_error_handled(content, line_num)
                        handling_method = self._get_handling_method(content, line_num) if is_handled else None
                        
                        # Extract error type
                        error_type = self._extract_error_type(line, pattern)
                        
                        error_scenario = ErrorScenario(
                            file_path=file_path,
                            line_number=line_num,
                            error_type=error_type,
                            context=line.strip(),
                            severity=severity,
                            is_handled=is_handled,
                            handling_method=handling_method
                        )
                        
                        error_scenarios.append(error_scenario)
        
        return error_scenarios
    
    def _is_error_handled(self, content: str, line_number: int) -> bool:
        """Check if an error is properly handled."""
        lines = content.split('\n')
        
        # Look for try-except blocks around the error
        for i in range(max(0, line_number - 10), min(len(lines), line_number + 10)):
            if 'try:' in lines[i] or 'except' in lines[i]:
                return True
        
        # Look for error handling in the same function
        function_start = self._find_function_start(lines, line_number)
        if function_start:
            function_content = '\n'.join(lines[function_start:line_number + 5])
            if 'try:' in function_content or 'except' in function_content:
                return True
        
        return False
    
    def _get_handling_method(self, content: str, line_number: int) -> Optional[str]:
        """Get the method used to handle the error."""
        lines = content.split('\n')
        
        # Look for try-except blocks
        for i in range(max(0, line_number - 10), min(len(lines), line_number + 10)):
            if 'except' in lines[i]:
                return "try-except"
        
        # Look for other handling methods
        for i in range(max(0, line_number - 5), min(len(lines), line_number + 5)):
            if 'if' in lines[i] and ('error' in lines[i].lower() or 'exception' in lines[i].lower()):
                return "conditional-check"
        
        return None
    
    def _extract_error_type(self, line: str, pattern: str) -> str:
        """Extract the error type from a line."""
        # Try to extract error type from raise statement
        match = re.search(r'raise\s+(\w+)', line)
        if match:
            return match.group(1)
        
        # Try to extract from except statement
        match = re.search(r'except\s+(\w+)', line)
        if match:
            return match.group(1)
        
        return "Unknown"
    
    def _find_function_start(self, lines: List[str], line_number: int) -> Optional[int]:
        """Find the start of the function containing the given line."""
        for i in range(line_number - 1, -1, -1):
            if lines[i].strip().startswith('def ') or lines[i].strip().startswith('async def '):
                return i
        return None
    
    def analyze_module_error_coverage(self, module_path: str) -> ErrorCoverageMetrics:
        """Analyze error coverage for a module."""
        error_scenarios = self.scan_file_for_errors(module_path)
        
        # Count errors by severity
        critical_errors = len([e for e in error_scenarios if e.severity == "critical"])
        high_priority_errors = len([e for e in error_scenarios if e.severity == "high"])
        medium_priority_errors = len([e for e in error_scenarios if e.severity == "medium"])
        low_priority_errors = len([e for e in error_scenarios if e.severity == "low"])
        
        total_errors = len(error_scenarios)
        covered_errors = len([e for e in error_scenarios if e.is_handled])
        uncovered_errors = total_errors - covered_errors
        
        coverage_percentage = (covered_errors / total_errors * 100) if total_errors > 0 else 100.0
        
        metrics = ErrorCoverageMetrics(
            module_name=module_path,
            total_errors=total_errors,
            covered_errors=covered_errors,
            uncovered_errors=uncovered_errors,
            coverage_percentage=coverage_percentage,
            critical_errors=critical_errors,
            high_priority_errors=high_priority_errors,
            medium_priority_errors=medium_priority_errors,
            low_priority_errors=low_priority_errors,
            error_scenarios=error_scenarios
        )
        
        self.coverage_metrics[module_path] = metrics
        return metrics
    
    def analyze_test_error_coverage(self, test_file_path: str) -> Dict[str, Any]:
        """Analyze error coverage in test files."""
        try:
            with open(test_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {"error": f"Could not read test file: {e}"}
        
        # Find test functions
        test_functions = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if re.match(r'def\s+test_', line) or re.match(r'async\s+def\s+test_', line):
                test_functions.append({
                    "name": line.strip(),
                    "line": line_num
                })
        
        # Analyze error testing in each test function
        error_test_analysis = []
        for test_func in test_functions:
            func_start = test_func["line"]
            func_end = self._find_function_end(lines, func_start)
            
            if func_end:
                func_content = '\n'.join(lines[func_start:func_end])
                error_tests = self._analyze_error_tests(func_content)
                error_test_analysis.append({
                    "function": test_func["name"],
                    "error_tests": error_tests
                })
        
        return {
            "test_functions": len(test_functions),
            "error_test_analysis": error_test_analysis,
            "total_error_tests": sum(len(analysis["error_tests"]) for analysis in error_test_analysis)
        }
    
    def _find_function_end(self, lines: List[str], start_line: int) -> Optional[int]:
        """Find the end of a function."""
        indent_level = len(lines[start_line - 1]) - len(lines[start_line - 1].lstrip())
        
        for i in range(start_line, len(lines)):
            line = lines[i]
            if line.strip() and not line.startswith(' ' * (indent_level + 1)) and not line.startswith('\t'):
                return i
        
        return len(lines)
    
    def _analyze_error_tests(self, func_content: str) -> List[str]:
        """Analyze error testing in a test function."""
        error_tests = []
        
        # Look for error testing patterns
        error_patterns = [
            r'with\s+pytest\.raises\(',
            r'assertRaises\(',
            r'pytest\.raises\(',
            r'with\s+assertRaises\(',
            r'@pytest\.mark\.raises',
            r'except\s+.*:',
            r'raise\s+.*Error',
            r'raise\s+.*Exception'
        ]
        
        for pattern in error_patterns:
            if re.search(pattern, func_content, re.IGNORECASE):
                error_tests.append(pattern)
        
        return error_tests
    
    def validate_error_coverage(self) -> Dict[str, Any]:
        """Validate overall error coverage."""
        validation_results = {
            "overall_status": "passed",
            "violations": [],
            "warnings": [],
            "recommendations": [],
            "summary": {}
        }
        
        if not self.coverage_metrics:
            validation_results["overall_status"] = "no_data"
            return validation_results
        
        # Check coverage against thresholds
        thresholds = self.config["coverage_thresholds"]
        
        for module_path, metrics in self.coverage_metrics.items():
            # Check critical errors
            if metrics.critical_errors > 0:
                critical_coverage = (metrics.covered_errors / metrics.total_errors) if metrics.total_errors > 0 else 1.0
                if critical_coverage < thresholds["critical"]:
                    validation_results["violations"].append({
                        "type": "critical_error_coverage",
                        "module": module_path,
                        "coverage": critical_coverage,
                        "threshold": thresholds["critical"],
                        "uncovered_critical": metrics.critical_errors - metrics.covered_errors
                    })
            
            # Check high priority errors
            if metrics.high_priority_errors > 0:
                high_coverage = (metrics.covered_errors / metrics.total_errors) if metrics.total_errors > 0 else 1.0
                if high_coverage < thresholds["high"]:
                    validation_results["warnings"].append({
                        "type": "high_priority_error_coverage",
                        "module": module_path,
                        "coverage": high_coverage,
                        "threshold": thresholds["high"]
                    })
        
        # Determine overall status
        if validation_results["violations"]:
            validation_results["overall_status"] = "failed"
        elif validation_results["warnings"]:
            validation_results["overall_status"] = "warning"
        
        # Generate recommendations
        validation_results["recommendations"] = self._generate_error_coverage_recommendations(
            validation_results["violations"], validation_results["warnings"]
        )
        
        # Generate summary
        total_errors = sum(m.total_errors for m in self.coverage_metrics.values())
        total_covered = sum(m.covered_errors for m in self.coverage_metrics.values())
        overall_coverage = (total_covered / total_errors * 100) if total_errors > 0 else 100.0
        
        validation_results["summary"] = {
            "total_modules": len(self.coverage_metrics),
            "total_errors": total_errors,
            "covered_errors": total_covered,
            "overall_coverage_percentage": overall_coverage,
            "critical_uncovered": sum(m.critical_errors - m.covered_errors for m in self.coverage_metrics.values()),
            "high_priority_uncovered": sum(m.high_priority_errors - m.covered_errors for m in self.coverage_metrics.values())
        }
        
        return validation_results
    
    def _generate_error_coverage_recommendations(self, violations: List[Dict], warnings: List[Dict]) -> List[str]:
        """Generate recommendations based on error coverage analysis."""
        recommendations = []
        
        if violations:
            critical_violations = [v for v in violations if v["type"] == "critical_error_coverage"]
            if critical_violations:
                recommendations.append(f"🚨 {len(critical_violations)} modules have insufficient critical error coverage. Immediate attention required.")
        
        if warnings:
            high_priority_warnings = [w for w in warnings if w["type"] == "high_priority_error_coverage"]
            if high_priority_warnings:
                recommendations.append(f"⚠️  {len(high_priority_warnings)} modules have insufficient high-priority error coverage.")
        
        # General recommendations
        recommendations.append("Add comprehensive error handling tests using pytest.raises()")
        recommendations.append("Test both expected and unexpected error scenarios")
        recommendations.append("Ensure error messages are meaningful and actionable")
        recommendations.append("Test error recovery and fallback mechanisms")
        
        return recommendations
    
    def generate_error_coverage_report(self) -> str:
        """Generate comprehensive error coverage report."""
        if not self.coverage_metrics:
            return "No error coverage data available."
        
        validation = self.validate_error_coverage()
        
        report = f"""
Error Coverage Validation Report
================================

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERALL STATUS: {validation['overall_status'].upper()}

SUMMARY
=======
Total Modules: {validation['summary']['total_modules']}
Total Errors: {validation['summary']['total_errors']}
Covered Errors: {validation['summary']['covered_errors']}
Overall Coverage: {validation['summary']['overall_coverage_percentage']:.1f}%
Critical Uncovered: {validation['summary']['critical_uncovered']}
High Priority Uncovered: {validation['summary']['high_priority_uncovered']}

MODULE BREAKDOWN
================
"""
        
        for module_path, metrics in self.coverage_metrics.items():
            report += f"""
{module_path}:
  Total Errors: {metrics.total_errors}
  Covered Errors: {metrics.covered_errors}
  Coverage: {metrics.coverage_percentage:.1f}%
  Critical: {metrics.critical_errors}
  High Priority: {metrics.high_priority_errors}
  Medium Priority: {metrics.medium_priority_errors}
  Low Priority: {metrics.low_priority_errors}
"""
        
        if validation['violations']:
            report += "\nVIOLATIONS\n==========\n"
            for violation in validation['violations']:
                report += f"- {violation['type'].replace('_', ' ').title()}: {violation['module']}\n"
        
        if validation['warnings']:
            report += "\nWARNINGS\n========\n"
            for warning in validation['warnings']:
                report += f"- {warning['type'].replace('_', ' ').title()}: {warning['module']}\n"
        
        if validation['recommendations']:
            report += "\nRECOMMENDATIONS\n===============\n"
            for i, recommendation in enumerate(validation['recommendations'], 1):
                report += f"{i}. {recommendation}\n"
        
        return report
    
    def save_error_coverage_report(self, filename: str = None):
        """Save error coverage report to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"error_coverage_report_{timestamp}.txt"
        
        report = self.generate_error_coverage_report()
        report_file = Path(filename)
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"📄 Error coverage report saved to {report_file}")
    
    def clear_error_data(self):
        """Clear error analysis data."""
        self.error_scenarios.clear()
        self.coverage_metrics.clear()


# Global validator instance
error_coverage_validator = ErrorCoverageValidator()


def get_error_coverage_validator() -> ErrorCoverageValidator:
    """Get the global error coverage validator."""
    return error_coverage_validator


def scan_file_for_errors(file_path: str) -> List[ErrorScenario]:
    """Scan a file for error scenarios."""
    return error_coverage_validator.scan_file_for_errors(file_path)


def analyze_module_error_coverage(module_path: str) -> ErrorCoverageMetrics:
    """Analyze error coverage for a module."""
    return error_coverage_validator.analyze_module_error_coverage(module_path)


def validate_error_coverage() -> Dict[str, Any]:
    """Validate error coverage."""
    return error_coverage_validator.validate_error_coverage()


def generate_error_coverage_report() -> str:
    """Generate error coverage report."""
    return error_coverage_validator.generate_error_coverage_report()

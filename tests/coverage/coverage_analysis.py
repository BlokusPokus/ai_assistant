"""
Coverage Analysis System

This module provides comprehensive coverage analysis including
coverage collection, gap identification, target validation, and report generation.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import xml.etree.ElementTree as ET
import re


class CoverageAnalyzer:
    """Comprehensive coverage analysis system."""
    
    def __init__(self, source_dir: str = "src", test_dir: str = "tests"):
        self.source_dir = Path(source_dir)
        self.test_dir = Path(test_dir)
        self.coverage_data = {}
        self.coverage_targets = {
            "overall": 80.0,
            "critical_modules": 90.0,
            "tools": 75.0,
            "database": 85.0,
            "api": 80.0,
            "auth": 95.0
        }
        self.exclude_patterns = [
            "*/tests/*",
            "*/venv/*",
            "*/__pycache__/*",
            "*/migrations/*",
            "*/conftest.py",
            "*/setup.py",
            "*/venv_personal_assistant/*"
        ]
    
    def run_coverage_analysis(self, test_paths: List[str] = None) -> Dict[str, Any]:
        """Run comprehensive coverage analysis."""
        if test_paths is None:
            test_paths = [str(self.test_dir)]
        
        print("🔍 Running comprehensive coverage analysis...")
        
        # Run coverage collection
        coverage_result = self._collect_coverage(test_paths)
        
        # Parse coverage data
        coverage_data = self._parse_coverage_data()
        
        # Analyze coverage gaps
        gaps = self._identify_coverage_gaps(coverage_data)
        
        # Validate coverage targets
        target_validation = self._validate_coverage_targets(coverage_data)
        
        # Generate comprehensive report
        report = self._generate_coverage_report(coverage_data, gaps, target_validation)
        
        return {
            "coverage_data": coverage_data,
            "coverage_gaps": gaps,
            "target_validation": target_validation,
            "report": report,
            "collection_result": coverage_result
        }
    
    def _collect_coverage(self, test_paths: List[str]) -> Dict[str, Any]:
        """Collect coverage data by running tests."""
        cmd = [
            sys.executable, "-m", "pytest",
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-report=xml:coverage.xml",
            "--cov-report=json:coverage.json",
            "--tb=short",
            "-q"
        ]
        
        # Add exclude patterns
        for pattern in self.exclude_patterns:
            cmd.extend(["--cov-omit", pattern])
        
        # Add test paths
        cmd.extend(test_paths)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            return {
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {
                "return_code": -1,
                "stdout": "",
                "stderr": "Coverage collection timed out",
                "success": False
            }
        except Exception as e:
            return {
                "return_code": -1,
                "stdout": "",
                "stderr": str(e),
                "success": False
            }
    
    def _parse_coverage_data(self) -> Dict[str, Any]:
        """Parse coverage data from various sources."""
        coverage_data = {
            "overall": {},
            "files": {},
            "modules": {},
            "summary": {}
        }
        
        # Parse JSON coverage data
        json_file = Path("coverage.json")
        if json_file.exists():
            try:
                with open(json_file, 'r') as f:
                    json_data = json.load(f)
                
                coverage_data["overall"] = {
                    "total_lines": json_data.get("totals", {}).get("num_statements", 0),
                    "covered_lines": json_data.get("totals", {}).get("covered_lines", 0),
                    "missing_lines": json_data.get("totals", {}).get("missing_lines", 0),
                    "coverage_percent": json_data.get("totals", {}).get("percent_covered", 0)
                }
                
                # Parse file-level coverage
                for file_path, file_data in json_data.get("files", {}).items():
                    coverage_data["files"][file_path] = {
                        "total_lines": file_data.get("summary", {}).get("num_statements", 0),
                        "covered_lines": file_data.get("summary", {}).get("covered_lines", 0),
                        "missing_lines": file_data.get("summary", {}).get("missing_lines", 0),
                        "coverage_percent": file_data.get("summary", {}).get("percent_covered", 0),
                        "missing_line_numbers": file_data.get("missing_lines", [])
                    }
                
            except Exception as e:
                print(f"Warning: Failed to parse JSON coverage data: {e}")
        
        # Parse XML coverage data
        xml_file = Path("coverage.xml")
        if xml_file.exists():
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                # Extract overall coverage from XML
                if "line-rate" in root.attrib:
                    coverage_data["overall"]["coverage_percent"] = float(root.attrib["line-rate"]) * 100
                
                # Parse package-level coverage
                for package in root.findall(".//package"):
                    package_name = package.get("name", "unknown")
                    coverage_data["modules"][package_name] = {
                        "coverage_percent": float(package.get("line-rate", 0)) * 100,
                        "total_lines": int(package.get("lines-valid", 0)),
                        "covered_lines": int(package.get("lines-covered", 0))
                    }
                
            except Exception as e:
                print(f"Warning: Failed to parse XML coverage data: {e}")
        
        # Generate summary statistics
        coverage_data["summary"] = self._generate_summary_stats(coverage_data)
        
        return coverage_data
    
    def _generate_summary_stats(self, coverage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics from coverage data."""
        files = coverage_data.get("files", {})
        modules = coverage_data.get("modules", {})
        
        # File-level statistics
        total_files = len(files)
        files_with_coverage = len([f for f in files.values() if f.get("coverage_percent", 0) > 0])
        files_fully_covered = len([f for f in files.values() if f.get("coverage_percent", 0) == 100])
        files_low_coverage = len([f for f in files.values() if f.get("coverage_percent", 0) < 50])
        
        # Module-level statistics
        total_modules = len(modules)
        modules_high_coverage = len([m for m in modules.values() if m.get("coverage_percent", 0) >= 80])
        modules_medium_coverage = len([m for m in modules.values() if 50 <= m.get("coverage_percent", 0) < 80])
        modules_low_coverage = len([m for m in modules.values() if m.get("coverage_percent", 0) < 50])
        
        return {
            "total_files": total_files,
            "files_with_coverage": files_with_coverage,
            "files_fully_covered": files_fully_covered,
            "files_low_coverage": files_low_coverage,
            "total_modules": total_modules,
            "modules_high_coverage": modules_high_coverage,
            "modules_medium_coverage": modules_medium_coverage,
            "modules_low_coverage": modules_low_coverage
        }
    
    def _identify_coverage_gaps(self, coverage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify coverage gaps and areas needing attention."""
        gaps = {
            "critical_gaps": [],
            "medium_gaps": [],
            "low_gaps": [],
            "uncovered_files": [],
            "recommendations": []
        }
        
        files = coverage_data.get("files", {})
        modules = coverage_data.get("modules", {})
        
        # Analyze file-level gaps
        for file_path, file_data in files.items():
            coverage_percent = file_data.get("coverage_percent", 0)
            missing_lines = file_data.get("missing_lines", 0)
            
            if coverage_percent == 0:
                gaps["uncovered_files"].append({
                    "file": file_path,
                    "total_lines": file_data.get("total_lines", 0),
                    "missing_lines": missing_lines
                })
            elif coverage_percent < 30:
                gaps["critical_gaps"].append({
                    "file": file_path,
                    "coverage_percent": coverage_percent,
                    "missing_lines": missing_lines,
                    "missing_line_numbers": file_data.get("missing_line_numbers", [])
                })
            elif coverage_percent < 60:
                gaps["medium_gaps"].append({
                    "file": file_path,
                    "coverage_percent": coverage_percent,
                    "missing_lines": missing_lines
                })
            elif coverage_percent < 80:
                gaps["low_gaps"].append({
                    "file": file_path,
                    "coverage_percent": coverage_percent,
                    "missing_lines": missing_lines
                })
        
        # Analyze module-level gaps
        for module_name, module_data in modules.items():
            coverage_percent = module_data.get("coverage_percent", 0)
            
            if coverage_percent < 50:
                gaps["critical_gaps"].append({
                    "module": module_name,
                    "coverage_percent": coverage_percent,
                    "type": "module"
                })
        
        # Generate recommendations
        gaps["recommendations"] = self._generate_gap_recommendations(gaps)
        
        return gaps
    
    def _generate_gap_recommendations(self, gaps: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on coverage gaps."""
        recommendations = []
        
        critical_gaps = gaps.get("critical_gaps", [])
        uncovered_files = gaps.get("uncovered_files", [])
        
        if len(critical_gaps) > 0:
            recommendations.append(f"Priority 1: Address {len(critical_gaps)} critical coverage gaps (<30% coverage)")
        
        if len(uncovered_files) > 0:
            recommendations.append(f"Priority 2: Add tests for {len(uncovered_files)} uncovered files")
        
        if len(gaps.get("medium_gaps", [])) > 0:
            recommendations.append(f"Priority 3: Improve coverage for {len(gaps['medium_gaps'])} medium-gap files (30-60% coverage)")
        
        if len(gaps.get("low_gaps", [])) > 0:
            recommendations.append(f"Priority 4: Enhance coverage for {len(gaps['low_gaps'])} low-gap files (60-80% coverage)")
        
        # Add specific recommendations based on file types
        critical_files = [gap.get("file", "") for gap in critical_gaps if "file" in gap]
        
        if any("auth" in f.lower() for f in critical_files):
            recommendations.append("Security: Prioritize authentication module coverage")
        
        if any("database" in f.lower() for f in critical_files):
            recommendations.append("Data Integrity: Prioritize database module coverage")
        
        if any("api" in f.lower() for f in critical_files):
            recommendations.append("API Reliability: Prioritize API endpoint coverage")
        
        return recommendations
    
    def _validate_coverage_targets(self, coverage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate coverage against targets."""
        validation = {
            "overall_target_met": False,
            "module_targets": {},
            "summary": {}
        }
        
        overall_coverage = coverage_data.get("overall", {}).get("coverage_percent", 0)
        overall_target = self.coverage_targets.get("overall", 80.0)
        
        validation["overall_target_met"] = overall_coverage >= overall_target
        
        # Validate module-specific targets
        modules = coverage_data.get("modules", {})
        for module_name, module_data in modules.items():
            coverage_percent = module_data.get("coverage_percent", 0)
            
            # Determine target based on module type
            target = self._get_module_target(module_name)
            target_met = coverage_percent >= target
            
            validation["module_targets"][module_name] = {
                "coverage_percent": coverage_percent,
                "target": target,
                "target_met": target_met,
                "gap": max(0, target - coverage_percent)
            }
        
        # Generate validation summary
        validation["summary"] = {
            "overall_coverage": overall_coverage,
            "overall_target": overall_target,
            "overall_gap": max(0, overall_target - overall_coverage),
            "modules_meeting_targets": len([m for m in validation["module_targets"].values() if m["target_met"]]),
            "total_modules": len(validation["module_targets"]),
            "target_compliance_rate": len([m for m in validation["module_targets"].values() if m["target_met"]]) / max(1, len(validation["module_targets"])) * 100
        }
        
        return validation
    
    def _get_module_target(self, module_name: str) -> float:
        """Get coverage target for a specific module."""
        module_lower = module_name.lower()
        
        if any(keyword in module_lower for keyword in ["auth", "security", "password", "jwt"]):
            return self.coverage_targets.get("auth", 95.0)
        elif any(keyword in module_lower for keyword in ["database", "model", "migration"]):
            return self.coverage_targets.get("database", 85.0)
        elif any(keyword in module_lower for keyword in ["api", "endpoint", "route"]):
            return self.coverage_targets.get("api", 80.0)
        elif any(keyword in module_lower for keyword in ["tool", "service", "utility"]):
            return self.coverage_targets.get("tools", 75.0)
        else:
            return self.coverage_targets.get("overall", 80.0)
    
    def _generate_coverage_report(self, coverage_data: Dict[str, Any], gaps: Dict[str, Any], validation: Dict[str, Any]) -> str:
        """Generate comprehensive coverage report."""
        overall = coverage_data.get("overall", {})
        summary = coverage_data.get("summary", {})
        validation_summary = validation.get("summary", {})
        
        report = f"""
Coverage Analysis Report
========================

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Overall Coverage Summary:
- Total Lines: {overall.get('total_lines', 0):,}
- Covered Lines: {overall.get('covered_lines', 0):,}
- Missing Lines: {overall.get('missing_lines', 0):,}
- Coverage Percentage: {overall.get('coverage_percent', 0):.1f}%
- Target: {self.coverage_targets.get('overall', 80.0):.1f}%
- Target Met: {'✅ YES' if validation.get('overall_target_met', False) else '❌ NO'}
- Gap: {validation_summary.get('overall_gap', 0):.1f}%

File-Level Statistics:
- Total Files: {summary.get('total_files', 0)}
- Files with Coverage: {summary.get('files_with_coverage', 0)}
- Files Fully Covered: {summary.get('files_fully_covered', 0)}
- Files with Low Coverage: {summary.get('files_low_coverage', 0)}

Module-Level Statistics:
- Total Modules: {summary.get('total_modules', 0)}
- High Coverage (≥80%): {summary.get('modules_high_coverage', 0)}
- Medium Coverage (50-80%): {summary.get('modules_medium_coverage', 0)}
- Low Coverage (<50%): {summary.get('modules_low_coverage', 0)}

Target Validation:
- Modules Meeting Targets: {validation_summary.get('modules_meeting_targets', 0)}/{validation_summary.get('total_modules', 0)}
- Target Compliance Rate: {validation_summary.get('target_compliance_rate', 0):.1f}%

Coverage Gaps Analysis:
- Critical Gaps (<30%): {len(gaps.get('critical_gaps', []))}
- Medium Gaps (30-60%): {len(gaps.get('medium_gaps', []))}
- Low Gaps (60-80%): {len(gaps.get('low_gaps', []))}
- Uncovered Files: {len(gaps.get('uncovered_files', []))}

Recommendations:
"""
        
        for i, recommendation in enumerate(gaps.get("recommendations", []), 1):
            report += f"{i}. {recommendation}\n"
        
        # Add detailed gap information
        if gaps.get("critical_gaps"):
            report += "\nCritical Coverage Gaps:\n"
            for gap in gaps["critical_gaps"][:10]:  # Show top 10
                if "file" in gap:
                    report += f"- {gap['file']}: {gap['coverage_percent']:.1f}% coverage\n"
                elif "module" in gap:
                    report += f"- Module {gap['module']}: {gap['coverage_percent']:.1f}% coverage\n"
        
        if gaps.get("uncovered_files"):
            report += "\nUncovered Files:\n"
            for file_info in gaps["uncovered_files"][:10]:  # Show top 10
                report += f"- {file_info['file']}: {file_info['total_lines']} lines\n"
        
        return report
    
    def save_coverage_report(self, report: str, filename: str = "coverage_analysis_report.txt"):
        """Save coverage report to file."""
        report_file = Path(filename)
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"📄 Coverage report saved to {report_file}")
    
    def get_coverage_summary(self) -> Dict[str, Any]:
        """Get a quick coverage summary."""
        if not self.coverage_data:
            return {"error": "No coverage data available. Run coverage analysis first."}
        
        overall = self.coverage_data.get("overall", {})
        return {
            "coverage_percent": overall.get("coverage_percent", 0),
            "total_lines": overall.get("total_lines", 0),
            "covered_lines": overall.get("covered_lines", 0),
            "missing_lines": overall.get("missing_lines", 0)
        }


class CoverageGapAnalyzer:
    """Specialized analyzer for coverage gaps."""
    
    def __init__(self, coverage_data: Dict[str, Any]):
        self.coverage_data = coverage_data
    
    def analyze_missing_lines(self, file_path: str) -> Dict[str, Any]:
        """Analyze missing lines in a specific file."""
        files = self.coverage_data.get("files", {})
        file_data = files.get(file_path, {})
        
        if not file_data:
            return {"error": f"No coverage data for file: {file_path}"}
        
        missing_line_numbers = file_data.get("missing_line_numbers", [])
        
        return {
            "file": file_path,
            "total_missing": len(missing_line_numbers),
            "missing_lines": missing_line_numbers,
            "coverage_percent": file_data.get("coverage_percent", 0),
            "suggestions": self._generate_line_specific_suggestions(file_path, missing_line_numbers)
        }
    
    def _generate_line_specific_suggestions(self, file_path: str, missing_lines: List[int]) -> List[str]:
        """Generate suggestions for specific missing lines."""
        suggestions = []
        
        if not missing_lines:
            return ["All lines are covered - excellent!"]
        
        # Analyze patterns in missing lines
        consecutive_gaps = self._find_consecutive_gaps(missing_lines)
        
        if consecutive_gaps:
            suggestions.append(f"Consider adding tests for consecutive line ranges: {consecutive_gaps}")
        
        # Suggest based on file type
        if "test_" in file_path:
            suggestions.append("Add more test cases to cover missing lines")
        elif "auth" in file_path.lower():
            suggestions.append("Add security-focused test cases")
        elif "database" in file_path.lower():
            suggestions.append("Add database integration tests")
        elif "api" in file_path.lower():
            suggestions.append("Add API endpoint tests with various scenarios")
        
        return suggestions
    
    def _find_consecutive_gaps(self, missing_lines: List[int]) -> List[Tuple[int, int]]:
        """Find consecutive gaps in missing lines."""
        if not missing_lines:
            return []
        
        sorted_lines = sorted(missing_lines)
        consecutive_gaps = []
        start = sorted_lines[0]
        end = start
        
        for i in range(1, len(sorted_lines)):
            if sorted_lines[i] == end + 1:
                end = sorted_lines[i]
            else:
                if end - start >= 2:  # Only report gaps of 3+ consecutive lines
                    consecutive_gaps.append((start, end))
                start = sorted_lines[i]
                end = start
        
        # Add the last gap if it's significant
        if end - start >= 2:
            consecutive_gaps.append((start, end))
        
        return consecutive_gaps


# Global coverage analyzer instance
coverage_analyzer = CoverageAnalyzer()


def get_coverage_analyzer() -> CoverageAnalyzer:
    """Get the global coverage analyzer."""
    return coverage_analyzer


def run_coverage_analysis(test_paths: List[str] = None) -> Dict[str, Any]:
    """Run comprehensive coverage analysis."""
    return coverage_analyzer.run_coverage_analysis(test_paths)


def get_coverage_summary() -> Dict[str, Any]:
    """Get quick coverage summary."""
    return coverage_analyzer.get_coverage_summary()

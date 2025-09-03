"""
Coverage Gap Analyzer

This module provides specialized tools for identifying and analyzing
coverage gaps, including line-by-line analysis and gap prioritization.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict
import ast
import json


class CoverageGapAnalyzer:
    """Advanced coverage gap analysis and prioritization."""
    
    def __init__(self, source_dir: str = "src", coverage_data: Dict[str, Any] = None):
        self.source_dir = Path(source_dir)
        self.coverage_data = coverage_data or {}
        self.gap_priorities = {
            "critical": 1,
            "high": 2,
            "medium": 3,
            "low": 4
        }
        self.priority_patterns = {
            "critical": [
                r"def.*auth.*",
                r"def.*password.*",
                r"def.*token.*",
                r"def.*security.*",
                r"def.*validate.*",
                r"def.*check.*",
                r"class.*Auth.*",
                r"class.*Security.*"
            ],
            "high": [
                r"def.*create.*",
                r"def.*update.*",
                r"def.*delete.*",
                r"def.*save.*",
                r"def.*load.*",
                r"class.*Model.*",
                r"class.*Database.*"
            ],
            "medium": [
                r"def.*get.*",
                r"def.*find.*",
                r"def.*search.*",
                r"def.*list.*",
                r"class.*Service.*",
                r"class.*Manager.*"
            ],
            "low": [
                r"def.*helper.*",
                r"def.*util.*",
                r"def.*format.*",
                r"def.*parse.*",
                r"class.*Helper.*",
                r"class.*Util.*"
            ]
        }
    
    def analyze_coverage_gaps(self) -> Dict[str, Any]:
        """Comprehensive coverage gap analysis."""
        gaps = {
            "by_priority": defaultdict(list),
            "by_module": defaultdict(list),
            "by_file_type": defaultdict(list),
            "statistics": {},
            "recommendations": []
        }
        
        files = self.coverage_data.get("files", {})
        
        for file_path, file_data in files.items():
            coverage_percent = file_data.get("coverage_percent", 0)
            missing_lines = file_data.get("missing_lines", 0)
            missing_line_numbers = file_data.get("missing_line_numbers", [])
            
            if coverage_percent < 100:  # Only analyze files with gaps
                gap_info = {
                    "file": file_path,
                    "coverage_percent": coverage_percent,
                    "missing_lines": missing_lines,
                    "missing_line_numbers": missing_line_numbers,
                    "priority": self._determine_gap_priority(file_path, missing_line_numbers),
                    "module": self._extract_module_name(file_path),
                    "file_type": self._determine_file_type(file_path)
                }
                
                # Categorize by priority
                gaps["by_priority"][gap_info["priority"]].append(gap_info)
                
                # Categorize by module
                gaps["by_module"][gap_info["module"]].append(gap_info)
                
                # Categorize by file type
                gaps["by_file_type"][gap_info["file_type"]].append(gap_info)
        
        # Generate statistics
        gaps["statistics"] = self._generate_gap_statistics(gaps)
        
        # Generate recommendations
        gaps["recommendations"] = self._generate_gap_recommendations(gaps)
        
        return gaps
    
    def _determine_gap_priority(self, file_path: str, missing_line_numbers: List[int]) -> str:
        """Determine priority level for coverage gap."""
        file_content = self._read_file_content(file_path)
        if not file_content:
            return "low"
        
        # Analyze missing lines for critical patterns
        critical_score = 0
        high_score = 0
        medium_score = 0
        
        for line_num in missing_line_numbers:
            if line_num <= len(file_content):
                line_content = file_content[line_num - 1]
                
                # Check for critical patterns
                for pattern in self.priority_patterns["critical"]:
                    if re.search(pattern, line_content, re.IGNORECASE):
                        critical_score += 3
                
                # Check for high priority patterns
                for pattern in self.priority_patterns["high"]:
                    if re.search(pattern, line_content, re.IGNORECASE):
                        high_score += 2
                
                # Check for medium priority patterns
                for pattern in self.priority_patterns["medium"]:
                    if re.search(pattern, line_content, re.IGNORECASE):
                        medium_score += 1
        
        # Determine priority based on scores
        if critical_score > 0:
            return "critical"
        elif high_score >= 2:
            return "high"
        elif medium_score >= 2:
            return "medium"
        else:
            return "low"
    
    def _read_file_content(self, file_path: str) -> List[str]:
        """Read file content for analysis."""
        try:
            full_path = self.source_dir / file_path
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    return f.readlines()
        except Exception:
            pass
        return []
    
    def _extract_module_name(self, file_path: str) -> str:
        """Extract module name from file path."""
        path_parts = Path(file_path).parts
        if len(path_parts) >= 2:
            return path_parts[1]  # e.g., "auth", "database", "tools"
        return "unknown"
    
    def _determine_file_type(self, file_path: str) -> str:
        """Determine file type based on path and content."""
        path_lower = file_path.lower()
        
        if "test_" in path_lower:
            return "test"
        elif "auth" in path_lower or "security" in path_lower:
            return "auth"
        elif "database" in path_lower or "model" in path_lower:
            return "database"
        elif "api" in path_lower or "endpoint" in path_lower:
            return "api"
        elif "tool" in path_lower or "service" in path_lower:
            return "service"
        elif "util" in path_lower or "helper" in path_lower:
            return "utility"
        else:
            return "other"
    
    def _generate_gap_statistics(self, gaps: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive gap statistics."""
        by_priority = gaps["by_priority"]
        by_module = gaps["by_module"]
        by_file_type = gaps["by_file_type"]
        
        return {
            "total_files_with_gaps": sum(len(files) for files in by_priority.values()),
            "priority_distribution": {
                priority: len(files) for priority, files in by_priority.items()
            },
            "module_distribution": {
                module: len(files) for module, files in by_module.items()
            },
            "file_type_distribution": {
                file_type: len(files) for file_type, files in by_file_type.items()
            },
            "average_coverage_by_priority": {
                priority: sum(f["coverage_percent"] for f in files) / len(files) if files else 0
                for priority, files in by_priority.items()
            },
            "total_missing_lines": sum(
                sum(f["missing_lines"] for f in files)
                for files in by_priority.values()
            )
        }
    
    def _generate_gap_recommendations(self, gaps: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on gap analysis."""
        recommendations = []
        statistics = gaps["statistics"]
        by_priority = gaps["by_priority"]
        
        # Priority-based recommendations
        critical_files = by_priority.get("critical", [])
        if critical_files:
            recommendations.append(
                f"🚨 CRITICAL: Address {len(critical_files)} files with critical coverage gaps. "
                f"These likely contain security or core functionality that needs immediate attention."
            )
        
        high_files = by_priority.get("high", [])
        if high_files:
            recommendations.append(
                f"⚠️  HIGH: Improve coverage for {len(high_files)} high-priority files. "
                f"Focus on data manipulation and core business logic."
            )
        
        # Module-based recommendations
        module_stats = statistics["module_distribution"]
        if "auth" in module_stats and module_stats["auth"] > 0:
            recommendations.append(
                "🔐 SECURITY: Prioritize authentication module coverage. "
                "Security-related code should have near 100% coverage."
            )
        
        if "database" in module_stats and module_stats["database"] > 0:
            recommendations.append(
                "💾 DATA: Focus on database module coverage. "
                "Data integrity is critical for application reliability."
            )
        
        # Coverage improvement recommendations
        total_missing = statistics["total_missing_lines"]
        if total_missing > 1000:
            recommendations.append(
                f"📊 SCOPE: Large coverage gap detected ({total_missing:,} missing lines). "
                f"Consider a phased approach to coverage improvement."
            )
        
        # File type recommendations
        file_type_stats = statistics["file_type_distribution"]
        if "test" in file_type_stats and file_type_stats["test"] > 0:
            recommendations.append(
                "🧪 TESTING: Some test files have coverage gaps. "
                "Consider adding integration tests or improving test coverage."
            )
        
        return recommendations
    
    def get_priority_gaps(self, priority: str = "critical") -> List[Dict[str, Any]]:
        """Get gaps for a specific priority level."""
        gaps = self.analyze_coverage_gaps()
        return gaps["by_priority"].get(priority, [])
    
    def get_module_gaps(self, module: str) -> List[Dict[str, Any]]:
        """Get gaps for a specific module."""
        gaps = self.analyze_coverage_gaps()
        return gaps["by_module"].get(module, [])
    
    def get_file_type_gaps(self, file_type: str) -> List[Dict[str, Any]]:
        """Get gaps for a specific file type."""
        gaps = self.analyze_coverage_gaps()
        return gaps["by_file_type"].get(file_type, [])
    
    def generate_gap_report(self) -> str:
        """Generate comprehensive gap analysis report."""
        gaps = self.analyze_coverage_gaps()
        statistics = gaps["statistics"]
        
        report = f"""
Coverage Gap Analysis Report
============================

Gap Statistics:
- Total Files with Gaps: {statistics['total_files_with_gaps']}
- Total Missing Lines: {statistics['total_missing_lines']:,}

Priority Distribution:
"""
        
        for priority, count in statistics["priority_distribution"].items():
            avg_coverage = statistics["average_coverage_by_priority"][priority]
            report += f"- {priority.title()}: {count} files (avg {avg_coverage:.1f}% coverage)\n"
        
        report += "\nModule Distribution:\n"
        for module, count in statistics["module_distribution"].items():
            report += f"- {module.title()}: {count} files\n"
        
        report += "\nFile Type Distribution:\n"
        for file_type, count in statistics["file_type_distribution"].items():
            report += f"- {file_type.title()}: {count} files\n"
        
        report += "\nRecommendations:\n"
        for i, recommendation in enumerate(gaps["recommendations"], 1):
            report += f"{i}. {recommendation}\n"
        
        # Add detailed gap information
        for priority in ["critical", "high", "medium", "low"]:
            priority_gaps = gaps["by_priority"].get(priority, [])
            if priority_gaps:
                report += f"\n{priority.title()} Priority Gaps:\n"
                for gap in priority_gaps[:5]:  # Show top 5
                    report += f"- {gap['file']}: {gap['coverage_percent']:.1f}% coverage, {gap['missing_lines']} missing lines\n"
        
        return report


class LineByLineGapAnalyzer:
    """Analyzes specific lines that are missing coverage."""
    
    def __init__(self, source_dir: str = "src"):
        self.source_dir = Path(source_dir)
    
    def analyze_missing_lines(self, file_path: str, missing_line_numbers: List[int]) -> Dict[str, Any]:
        """Analyze specific missing lines in detail."""
        file_content = self._read_file_content(file_path)
        if not file_content:
            return {"error": f"Could not read file: {file_path}"}
        
        analysis = {
            "file": file_path,
            "missing_lines": [],
            "patterns": {},
            "suggestions": []
        }
        
        for line_num in missing_line_numbers:
            if line_num <= len(file_content):
                line_content = file_content[line_num - 1].strip()
                line_analysis = self._analyze_line(line_content, line_num)
                analysis["missing_lines"].append(line_analysis)
        
        # Analyze patterns
        analysis["patterns"] = self._analyze_patterns(analysis["missing_lines"])
        
        # Generate suggestions
        analysis["suggestions"] = self._generate_line_specific_suggestions(analysis)
        
        return analysis
    
    def _read_file_content(self, file_path: str) -> List[str]:
        """Read file content."""
        try:
            full_path = self.source_dir / file_path
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    return f.readlines()
        except Exception:
            pass
        return []
    
    def _analyze_line(self, line_content: str, line_num: int) -> Dict[str, Any]:
        """Analyze a specific line of code."""
        return {
            "line_number": line_num,
            "content": line_content,
            "type": self._classify_line_type(line_content),
            "complexity": self._assess_line_complexity(line_content),
            "test_suggestion": self._suggest_test_type(line_content)
        }
    
    def _classify_line_type(self, line_content: str) -> str:
        """Classify the type of line."""
        if line_content.startswith("def "):
            return "function_definition"
        elif line_content.startswith("class "):
            return "class_definition"
        elif line_content.startswith("if "):
            return "conditional"
        elif line_content.startswith("elif "):
            return "conditional"
        elif line_content.startswith("else:"):
            return "conditional"
        elif line_content.startswith("for "):
            return "loop"
        elif line_content.startswith("while "):
            return "loop"
        elif line_content.startswith("return "):
            return "return_statement"
        elif line_content.startswith("raise "):
            return "exception"
        elif "=" in line_content and not line_content.startswith("#"):
            return "assignment"
        else:
            return "other"
    
    def _assess_line_complexity(self, line_content: str) -> str:
        """Assess the complexity of a line."""
        complexity_indicators = ["if", "elif", "else", "for", "while", "try", "except", "and", "or", "not"]
        complexity_count = sum(1 for indicator in complexity_indicators if indicator in line_content)
        
        if complexity_count >= 3:
            return "high"
        elif complexity_count >= 1:
            return "medium"
        else:
            return "low"
    
    def _suggest_test_type(self, line_content: str) -> str:
        """Suggest the type of test needed for a line."""
        if line_content.startswith("def "):
            return "unit_test"
        elif line_content.startswith("class "):
            return "class_test"
        elif "if " in line_content or "elif " in line_content:
            return "conditional_test"
        elif "for " in line_content or "while " in line_content:
            return "loop_test"
        elif "raise " in line_content:
            return "exception_test"
        elif "return " in line_content:
            return "return_value_test"
        else:
            return "integration_test"
    
    def _analyze_patterns(self, missing_lines: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in missing lines."""
        line_types = [line["type"] for line in missing_lines]
        complexity_levels = [line["complexity"] for line in missing_lines]
        test_types = [line["test_suggestion"] for line in missing_lines]
        
        return {
            "most_common_type": max(set(line_types), key=line_types.count) if line_types else "none",
            "most_common_complexity": max(set(complexity_levels), key=complexity_levels.count) if complexity_levels else "none",
            "most_common_test_type": max(set(test_types), key=test_types.count) if test_types else "none",
            "type_distribution": {t: line_types.count(t) for t in set(line_types)},
            "complexity_distribution": {c: complexity_levels.count(c) for c in set(complexity_levels)}
        }
    
    def _generate_line_specific_suggestions(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate specific suggestions based on line analysis."""
        suggestions = []
        patterns = analysis["patterns"]
        
        most_common_type = patterns["most_common_type"]
        most_common_complexity = patterns["most_common_complexity"]
        
        if most_common_type == "conditional":
            suggestions.append("Add tests for different conditional branches")
        elif most_common_type == "function_definition":
            suggestions.append("Add unit tests for function definitions")
        elif most_common_type == "exception":
            suggestions.append("Add exception handling tests")
        
        if most_common_complexity == "high":
            suggestions.append("Focus on high-complexity lines - they need thorough testing")
        
        if patterns["type_distribution"].get("conditional", 0) > 3:
            suggestions.append("Multiple conditionals detected - add edge case tests")
        
        return suggestions


# Global instances
gap_analyzer = CoverageGapAnalyzer()
line_analyzer = LineByLineGapAnalyzer()


def get_gap_analyzer() -> CoverageGapAnalyzer:
    """Get the global gap analyzer."""
    return gap_analyzer


def get_line_analyzer() -> LineByLineGapAnalyzer:
    """Get the global line analyzer."""
    return line_analyzer


def analyze_coverage_gaps(coverage_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze coverage gaps with the global analyzer."""
    gap_analyzer.coverage_data = coverage_data
    return gap_analyzer.analyze_coverage_gaps()


def analyze_missing_lines(file_path: str, missing_line_numbers: List[int]) -> Dict[str, Any]:
    """Analyze specific missing lines."""
    return line_analyzer.analyze_missing_lines(file_path, missing_line_numbers)

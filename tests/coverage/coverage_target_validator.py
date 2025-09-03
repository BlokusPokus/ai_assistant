"""
Coverage Target Validator

This module provides comprehensive coverage target validation including
target definition, validation logic, and compliance reporting.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class CoverageTarget:
    """Represents a coverage target for a specific module or component."""
    name: str
    target_percentage: float
    priority: str  # "critical", "high", "medium", "low"
    description: str
    rationale: str
    module_patterns: List[str]  # Patterns to match module names
    file_patterns: List[str]    # Patterns to match file names
    weight: float = 1.0         # Weight for overall calculation


@dataclass
class CoverageValidation:
    """Represents the validation result for a coverage target."""
    target: CoverageTarget
    actual_coverage: float
    target_met: bool
    gap: float
    compliance_score: float
    files_analyzed: List[str]
    recommendations: List[str]


class CoverageTargetValidator:
    """Validates coverage against defined targets."""
    
    def __init__(self, targets_file: str = "coverage_targets.json"):
        self.targets_file = Path(targets_file)
        self.targets = self._load_targets()
        self.validation_results = {}
    
    def _load_targets(self) -> List[CoverageTarget]:
        """Load coverage targets from file or create defaults."""
        if self.targets_file.exists():
            try:
                with open(self.targets_file, 'r') as f:
                    targets_data = json.load(f)
                return [CoverageTarget(**target) for target in targets_data]
            except Exception as e:
                print(f"Warning: Failed to load targets from {self.targets_file}: {e}")
        
        # Return default targets
        return self._get_default_targets()
    
    def _get_default_targets(self) -> List[CoverageTarget]:
        """Get default coverage targets."""
        return [
            CoverageTarget(
                name="Overall Coverage",
                target_percentage=80.0,
                priority="high",
                description="Overall code coverage target",
                rationale="Industry standard for good test coverage",
                module_patterns=["*"],
                file_patterns=["*.py"]
            ),
            CoverageTarget(
                name="Authentication & Security",
                target_percentage=95.0,
                priority="critical",
                description="Authentication and security-related code",
                rationale="Security-critical code must have near-perfect coverage",
                module_patterns=["*auth*", "*security*", "*password*", "*jwt*", "*token*"],
                file_patterns=["*auth*.py", "*security*.py", "*password*.py", "*jwt*.py", "*token*.py"]
            ),
            CoverageTarget(
                name="Database Models",
                target_percentage=90.0,
                priority="high",
                description="Database models and data access",
                rationale="Data integrity is critical for application reliability",
                module_patterns=["*model*", "*database*", "*db*"],
                file_patterns=["*model*.py", "*database*.py", "*db*.py"]
            ),
            CoverageTarget(
                name="API Endpoints",
                target_percentage=85.0,
                priority="high",
                description="API endpoints and routes",
                rationale="API endpoints are the primary interface and need good coverage",
                module_patterns=["*api*", "*route*", "*endpoint*"],
                file_patterns=["*api*.py", "*route*.py", "*endpoint*.py"]
            ),
            CoverageTarget(
                name="Business Logic",
                target_percentage=80.0,
                priority="high",
                description="Core business logic and services",
                rationale="Business logic contains critical application functionality",
                module_patterns=["*service*", "*business*", "*logic*", "*core*"],
                file_patterns=["*service*.py", "*business*.py", "*logic*.py", "*core*.py"]
            ),
            CoverageTarget(
                name="Tools & Utilities",
                target_percentage=75.0,
                priority="medium",
                description="Tools and utility functions",
                rationale="Utility functions should be well-tested but are less critical",
                module_patterns=["*tool*", "*util*", "*helper*"],
                file_patterns=["*tool*.py", "*util*.py", "*helper*.py"]
            ),
            CoverageTarget(
                name="Configuration & Setup",
                target_percentage=70.0,
                priority="low",
                description="Configuration and setup code",
                rationale="Configuration code is important but less frequently changed",
                module_patterns=["*config*", "*setup*", "*init*"],
                file_patterns=["*config*.py", "*setup*.py", "*__init__*.py"]
            )
        ]
    
    def save_targets(self):
        """Save current targets to file."""
        targets_data = [asdict(target) for target in self.targets]
        with open(self.targets_file, 'w') as f:
            json.dump(targets_data, f, indent=2)
        print(f"📄 Coverage targets saved to {self.targets_file}")
    
    def add_target(self, target: CoverageTarget):
        """Add a new coverage target."""
        self.targets.append(target)
    
    def remove_target(self, target_name: str):
        """Remove a coverage target by name."""
        self.targets = [t for t in self.targets if t.name != target_name]
    
    def validate_coverage_targets(self, coverage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate coverage against all defined targets."""
        validation_results = {
            "overall_compliance": 0.0,
            "target_validations": [],
            "summary": {},
            "recommendations": []
        }
        
        total_weight = sum(target.weight for target in self.targets)
        weighted_score = 0.0
        
        for target in self.targets:
            validation = self._validate_single_target(target, coverage_data)
            validation_results["target_validations"].append(validation)
            
            # Calculate weighted score
            weighted_score += validation.compliance_score * target.weight
        
        # Calculate overall compliance
        validation_results["overall_compliance"] = weighted_score / total_weight if total_weight > 0 else 0.0
        
        # Generate summary
        validation_results["summary"] = self._generate_validation_summary(validation_results["target_validations"])
        
        # Generate recommendations
        validation_results["recommendations"] = self._generate_validation_recommendations(validation_results["target_validations"])
        
        self.validation_results = validation_results
        return validation_results
    
    def _validate_single_target(self, target: CoverageTarget, coverage_data: Dict[str, Any]) -> CoverageValidation:
        """Validate a single coverage target."""
        files = coverage_data.get("files", {})
        modules = coverage_data.get("modules", {})
        
        # Find files and modules that match this target
        matching_files = self._find_matching_files(target, files)
        matching_modules = self._find_matching_modules(target, modules)
        
        # Calculate coverage for matching files/modules
        if matching_files:
            total_lines = sum(f.get("total_lines", 0) for f in matching_files.values())
            covered_lines = sum(f.get("covered_lines", 0) for f in matching_files.values())
            actual_coverage = (covered_lines / total_lines * 100) if total_lines > 0 else 0.0
        elif matching_modules:
            total_lines = sum(m.get("total_lines", 0) for m in matching_modules.values())
            covered_lines = sum(m.get("covered_lines", 0) for m in matching_modules.values())
            actual_coverage = (covered_lines / total_lines * 100) if total_lines > 0 else 0.0
        else:
            actual_coverage = 0.0
        
        # Determine if target is met
        target_met = actual_coverage >= target.target_percentage
        gap = max(0, target.target_percentage - actual_coverage)
        
        # Calculate compliance score (0-1)
        compliance_score = min(1.0, actual_coverage / target.target_percentage) if target.target_percentage > 0 else 0.0
        
        # Generate recommendations
        recommendations = self._generate_target_recommendations(target, actual_coverage, target_met, gap)
        
        return CoverageValidation(
            target=target,
            actual_coverage=actual_coverage,
            target_met=target_met,
            gap=gap,
            compliance_score=compliance_score,
            files_analyzed=list(matching_files.keys()) if matching_files else list(matching_modules.keys()),
            recommendations=recommendations
        )
    
    def _find_matching_files(self, target: CoverageTarget, files: Dict[str, Any]) -> Dict[str, Any]:
        """Find files that match the target patterns."""
        matching_files = {}
        
        for file_path, file_data in files.items():
            if self._matches_patterns(file_path, target.file_patterns):
                matching_files[file_path] = file_data
        
        return matching_files
    
    def _find_matching_modules(self, target: CoverageTarget, modules: Dict[str, Any]) -> Dict[str, Any]:
        """Find modules that match the target patterns."""
        matching_modules = {}
        
        for module_name, module_data in modules.items():
            if self._matches_patterns(module_name, target.module_patterns):
                matching_modules[module_name] = module_data
        
        return matching_modules
    
    def _matches_patterns(self, text: str, patterns: List[str]) -> bool:
        """Check if text matches any of the patterns."""
        import fnmatch
        
        for pattern in patterns:
            if fnmatch.fnmatch(text.lower(), pattern.lower()):
                return True
        return False
    
    def _generate_target_recommendations(self, target: CoverageTarget, actual_coverage: float, target_met: bool, gap: float) -> List[str]:
        """Generate recommendations for a specific target."""
        recommendations = []
        
        if target_met:
            recommendations.append(f"✅ Target met! {target.name} has {actual_coverage:.1f}% coverage (target: {target.target_percentage}%)")
        else:
            recommendations.append(f"❌ Target not met. {target.name} has {actual_coverage:.1f}% coverage, need {gap:.1f}% more")
            
            if gap > 20:
                recommendations.append(f"🚨 Large gap detected ({gap:.1f}%). Consider prioritizing this target.")
            elif gap > 10:
                recommendations.append(f"⚠️  Moderate gap ({gap:.1f}%). Focus on improving coverage for this area.")
            else:
                recommendations.append(f"📈 Small gap ({gap:.1f}%). Close to target, minor improvements needed.")
        
        # Priority-specific recommendations
        if target.priority == "critical":
            recommendations.append("🔐 CRITICAL PRIORITY: This target is security or core functionality related.")
        elif target.priority == "high":
            recommendations.append("⚠️  HIGH PRIORITY: This target is important for application reliability.")
        
        return recommendations
    
    def _generate_validation_summary(self, validations: List[CoverageValidation]) -> Dict[str, Any]:
        """Generate summary of validation results."""
        total_targets = len(validations)
        targets_met = len([v for v in validations if v.target_met])
        targets_not_met = total_targets - targets_met
        
        # Priority breakdown
        priority_breakdown = {}
        for priority in ["critical", "high", "medium", "low"]:
            priority_validations = [v for v in validations if v.target.priority == priority]
            priority_met = len([v for v in priority_validations if v.target_met])
            priority_total = len(priority_validations)
            
            priority_breakdown[priority] = {
                "met": priority_met,
                "total": priority_total,
                "percentage": (priority_met / priority_total * 100) if priority_total > 0 else 0.0
            }
        
        # Average compliance by priority
        avg_compliance_by_priority = {}
        for priority in ["critical", "high", "medium", "low"]:
            priority_validations = [v for v in validations if v.target.priority == priority]
            if priority_validations:
                avg_compliance = sum(v.compliance_score for v in priority_validations) / len(priority_validations)
                avg_compliance_by_priority[priority] = avg_compliance
        
        return {
            "total_targets": total_targets,
            "targets_met": targets_met,
            "targets_not_met": targets_not_met,
            "overall_success_rate": (targets_met / total_targets * 100) if total_targets > 0 else 0.0,
            "priority_breakdown": priority_breakdown,
            "avg_compliance_by_priority": avg_compliance_by_priority
        }
    
    def _generate_validation_recommendations(self, validations: List[CoverageValidation]) -> List[str]:
        """Generate overall recommendations based on validation results."""
        recommendations = []
        
        # Overall compliance recommendations
        overall_compliance = self.validation_results.get("overall_compliance", 0.0)
        if overall_compliance >= 0.9:
            recommendations.append("🎉 Excellent! Overall compliance is very high (≥90%)")
        elif overall_compliance >= 0.8:
            recommendations.append("✅ Good! Overall compliance is above 80%")
        elif overall_compliance >= 0.7:
            recommendations.append("📈 Fair. Overall compliance is above 70%, room for improvement")
        else:
            recommendations.append("⚠️  Needs attention. Overall compliance is below 70%")
        
        # Priority-specific recommendations
        summary = self.validation_results.get("summary", {})
        priority_breakdown = summary.get("priority_breakdown", {})
        
        for priority in ["critical", "high", "medium", "low"]:
            priority_info = priority_breakdown.get(priority, {})
            met = priority_info.get("met", 0)
            total = priority_info.get("total", 0)
            
            if total > 0:
                percentage = priority_info.get("percentage", 0.0)
                if percentage < 50:
                    recommendations.append(f"🚨 {priority.title()} priority targets need immediate attention ({percentage:.1f}% met)")
                elif percentage < 80:
                    recommendations.append(f"⚠️  {priority.title()} priority targets need improvement ({percentage:.1f}% met)")
        
        # Specific target recommendations
        unmet_targets = [v for v in validations if not v.target_met]
        if unmet_targets:
            critical_unmet = [v for v in unmet_targets if v.target.priority == "critical"]
            if critical_unmet:
                recommendations.append(f"🔐 Focus on {len(critical_unmet)} critical targets first")
            
            high_unmet = [v for v in unmet_targets if v.target.priority == "high"]
            if high_unmet:
                recommendations.append(f"⚠️  Address {len(high_unmet)} high-priority targets")
        
        return recommendations
    
    def generate_validation_report(self) -> str:
        """Generate comprehensive validation report."""
        if not self.validation_results:
            return "No validation results available. Run validate_coverage_targets() first."
        
        validations = self.validation_results["target_validations"]
        summary = self.validation_results["summary"]
        overall_compliance = self.validation_results["overall_compliance"]
        
        report = f"""
Coverage Target Validation Report
=================================

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Overall Compliance: {overall_compliance:.1%}

Summary:
- Total Targets: {summary['total_targets']}
- Targets Met: {summary['targets_met']}
- Targets Not Met: {summary['targets_not_met']}
- Overall Success Rate: {summary['overall_success_rate']:.1f}%

Priority Breakdown:
"""
        
        for priority in ["critical", "high", "medium", "low"]:
            priority_info = summary["priority_breakdown"].get(priority, {})
            if priority_info.get("total", 0) > 0:
                report += f"- {priority.title()}: {priority_info['met']}/{priority_info['total']} met ({priority_info['percentage']:.1f}%)\n"
        
        report += "\nTarget Details:\n"
        for validation in validations:
            status = "✅" if validation.target_met else "❌"
            report += f"{status} {validation.target.name}: {validation.actual_coverage:.1f}% (target: {validation.target.target_percentage}%)\n"
            if not validation.target_met:
                report += f"   Gap: {validation.gap:.1f}% | Priority: {validation.target.priority}\n"
        
        report += "\nRecommendations:\n"
        for i, recommendation in enumerate(self.validation_results["recommendations"], 1):
            report += f"{i}. {recommendation}\n"
        
        return report
    
    def save_validation_report(self, filename: str = "coverage_validation_report.txt"):
        """Save validation report to file."""
        report = self.generate_validation_report()
        report_file = Path(filename)
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"📄 Validation report saved to {report_file}")


# Global validator instance
target_validator = CoverageTargetValidator()


def get_target_validator() -> CoverageTargetValidator:
    """Get the global target validator."""
    return target_validator


def validate_coverage_targets(coverage_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate coverage against targets using the global validator."""
    return target_validator.validate_coverage_targets(coverage_data)


def add_coverage_target(target: CoverageTarget):
    """Add a coverage target to the global validator."""
    target_validator.add_target(target)


def save_coverage_targets():
    """Save coverage targets to file."""
    target_validator.save_targets()

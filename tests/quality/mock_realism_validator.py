"""
Mock Realism Validator

This module provides comprehensive mock realism validation including
mock behavior analysis, realism scoring, and mock quality assessment.
"""

import inspect
from typing import Dict, List, Any, Optional, Callable, Type, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import json
from pathlib import Path
from unittest.mock import Mock, MagicMock, AsyncMock
import asyncio


@dataclass
class MockBehaviorAnalysis:
    """Represents analysis of mock behavior."""
    mock_name: str
    mock_type: str
    call_count: int
    call_args: List[tuple]
    call_kwargs: List[dict]
    return_values: List[Any]
    side_effects: List[Any]
    exceptions_raised: List[Exception]
    async_calls: int
    sync_calls: int


@dataclass
class MockRealismScore:
    """Represents realism score for a mock."""
    mock_name: str
    overall_score: float  # 0-1, higher is more realistic
    behavior_score: float
    data_score: float
    interaction_score: float
    error_handling_score: float
    performance_score: float
    issues: List[str]
    recommendations: List[str]


@dataclass
class MockQualityReport:
    """Represents overall mock quality report."""
    total_mocks: int
    high_quality_mocks: int
    medium_quality_mocks: int
    low_quality_mocks: int
    average_realism_score: float
    common_issues: List[str]
    recommendations: List[str]
    timestamp: datetime


class MockRealismValidator:
    """Validates mock realism and quality."""
    
    def __init__(self, config_file: str = "mock_realism_config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
        self.mock_analyses = {}
        self.mock_scores = {}
        
        # Default scoring weights
        self.default_weights = {
            "behavior": 0.3,      # How realistic the behavior is
            "data": 0.25,         # How realistic the data is
            "interaction": 0.2,   # How realistic the interactions are
            "error_handling": 0.15,  # How realistic error handling is
            "performance": 0.1    # How realistic performance is
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
            "scoring_weights": {
                "behavior": 0.3,      # How realistic the behavior is
                "data": 0.25,         # How realistic the data is
                "interaction": 0.2,   # How realistic the interactions are
                "error_handling": 0.15,  # How realistic error handling is
                "performance": 0.1    # How realistic performance is
            },
            "realism_thresholds": {
                "high_quality": 0.8,
                "medium_quality": 0.6,
                "low_quality": 0.4
            },
            "analysis_settings": {
                "track_call_arguments": True,
                "track_return_values": True,
                "track_side_effects": True,
                "track_exceptions": True,
                "analyze_async_behavior": True
            },
            "mock_types": {
                "database": {
                    "expected_methods": ["execute", "fetchone", "fetchall", "commit", "rollback"],
                    "expected_async": True,
                    "expected_transactions": True
                },
                "http_client": {
                    "expected_methods": ["get", "post", "put", "delete", "request"],
                    "expected_async": True,
                    "expected_headers": True
                },
                "file_system": {
                    "expected_methods": ["read", "write", "open", "close", "exists"],
                    "expected_async": False,
                    "expected_paths": True
                },
                "api_client": {
                    "expected_methods": ["authenticate", "make_request", "handle_response"],
                    "expected_async": True,
                    "expected_auth": True
                }
            }
        }
    
    def save_config(self):
        """Save current configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2, default=str)
        print(f"📄 Mock realism config saved to {self.config_file}")
    
    def analyze_mock_behavior(self, mock: Union[Mock, MagicMock, AsyncMock], 
                            mock_name: str, mock_type: str = "generic") -> MockBehaviorAnalysis:
        """Analyze the behavior of a mock object."""
        # Get call information
        call_count = mock.call_count
        call_args = list(mock.call_args_list)
        call_kwargs = [call.kwargs for call in call_args if hasattr(call, 'kwargs')]
        
        # Get return values
        return_values = []
        if hasattr(mock, 'return_value') and mock.return_value is not None:
            return_values.append(mock.return_value)
        
        # Get side effects
        side_effects = []
        if hasattr(mock, 'side_effect') and mock.side_effect is not None:
            if callable(mock.side_effect):
                side_effects.append("callable")
            else:
                side_effects.append(mock.side_effect)
        
        # Count async vs sync calls
        async_calls = 0
        sync_calls = 0
        
        # Analyze method calls
        for call in call_args:
            if asyncio.iscoroutinefunction(call):
                async_calls += 1
            else:
                sync_calls += 1
        
        # Get exceptions raised
        exceptions_raised = []
        if hasattr(mock, 'side_effect') and isinstance(mock.side_effect, Exception):
            exceptions_raised.append(type(mock.side_effect).__name__)
        
        analysis = MockBehaviorAnalysis(
            mock_name=mock_name,
            mock_type=mock_type,
            call_count=call_count,
            call_args=call_args,
            call_kwargs=call_kwargs,
            return_values=return_values,
            side_effects=side_effects,
            exceptions_raised=exceptions_raised,
            async_calls=async_calls,
            sync_calls=sync_calls
        )
        
        self.mock_analyses[mock_name] = analysis
        return analysis
    
    def calculate_realism_score(self, mock_name: str, mock_type: str = "generic") -> MockRealismScore:
        """Calculate realism score for a mock."""
        if mock_name not in self.mock_analyses:
            return MockRealismScore(
                mock_name=mock_name,
                overall_score=0.0,
                behavior_score=0.0,
                data_score=0.0,
                interaction_score=0.0,
                error_handling_score=0.0,
                performance_score=0.0,
                issues=["No analysis data available"],
                recommendations=["Run mock behavior analysis first"]
            )
        
        analysis = self.mock_analyses[mock_name]
        
        # Calculate individual scores
        behavior_score = self._calculate_behavior_score(analysis, mock_type)
        data_score = self._calculate_data_score(analysis, mock_type)
        interaction_score = self._calculate_interaction_score(analysis, mock_type)
        error_handling_score = self._calculate_error_handling_score(analysis, mock_type)
        performance_score = self._calculate_performance_score(analysis, mock_type)
        
        # Calculate overall score using weights
        weights = self.config["scoring_weights"]
        overall_score = (
            behavior_score * weights["behavior"] +
            data_score * weights["data"] +
            interaction_score * weights["interaction"] +
            error_handling_score * weights["error_handling"] +
            performance_score * weights["performance"]
        )
        
        # Generate issues and recommendations
        issues = self._identify_mock_issues(analysis, mock_type)
        recommendations = self._generate_mock_recommendations(analysis, mock_type, issues)
        
        score = MockRealismScore(
            mock_name=mock_name,
            overall_score=overall_score,
            behavior_score=behavior_score,
            data_score=data_score,
            interaction_score=interaction_score,
            error_handling_score=error_handling_score,
            performance_score=performance_score,
            issues=issues,
            recommendations=recommendations
        )
        
        self.mock_scores[mock_name] = score
        return score
    
    def _calculate_behavior_score(self, analysis: MockBehaviorAnalysis, mock_type: str) -> float:
        """Calculate behavior realism score."""
        score = 0.0
        
        # Check if mock has been called
        if analysis.call_count > 0:
            score += 0.3
        
        # Check for realistic call patterns
        if len(analysis.call_args) > 1:
            score += 0.2  # Multiple calls suggest realistic usage
        
        # Check for async behavior if expected
        mock_type_config = self.config["mock_types"].get(mock_type, {})
        if mock_type_config.get("expected_async", False):
            if analysis.async_calls > 0:
                score += 0.3
            else:
                score -= 0.2  # Penalty for missing async behavior
        
        # Check for side effects (indicates realistic behavior)
        if analysis.side_effects:
            score += 0.2
        
        return min(1.0, max(0.0, score))
    
    def _calculate_data_score(self, analysis: MockBehaviorAnalysis, mock_type: str) -> float:
        """Calculate data realism score."""
        score = 0.0
        
        # Check for return values
        if analysis.return_values:
            score += 0.4
        
        # Check for realistic data types
        for return_value in analysis.return_values:
            if isinstance(return_value, (dict, list, str, int, float, bool)):
                score += 0.2
            elif return_value is None:
                score += 0.1  # None is sometimes realistic
        
        # Check for call arguments (indicates data passing)
        if analysis.call_kwargs:
            score += 0.2
        
        return min(1.0, max(0.0, score))
    
    def _calculate_interaction_score(self, analysis: MockBehaviorAnalysis, mock_type: str) -> float:
        """Calculate interaction realism score."""
        score = 0.0
        
        # Check for multiple interactions
        if analysis.call_count > 1:
            score += 0.3
        
        # Check for argument passing
        if analysis.call_args:
            score += 0.3
        
        # Check for keyword arguments
        if analysis.call_kwargs:
            score += 0.2
        
        # Check for realistic call patterns
        if analysis.call_count > 0 and analysis.return_values:
            score += 0.2  # Calls with returns suggest realistic interaction
        
        return min(1.0, max(0.0, score))
    
    def _calculate_error_handling_score(self, analysis: MockBehaviorAnalysis, mock_type: str) -> float:
        """Calculate error handling realism score."""
        score = 0.5  # Start with neutral score
        
        # Check for exceptions
        if analysis.exceptions_raised:
            score += 0.3  # Exceptions can be realistic
        
        # Check for side effects that might handle errors
        if analysis.side_effects:
            score += 0.2
        
        return min(1.0, max(0.0, score))
    
    def _calculate_performance_score(self, analysis: MockBehaviorAnalysis, mock_type: str) -> float:
        """Calculate performance realism score."""
        score = 0.5  # Start with neutral score
        
        # Check for reasonable call count
        if 1 <= analysis.call_count <= 100:
            score += 0.3
        elif analysis.call_count > 100:
            score -= 0.2  # Too many calls might indicate unrealistic usage
        
        # Check for async behavior (can affect performance)
        if analysis.async_calls > 0:
            score += 0.2
        
        return min(1.0, max(0.0, score))
    
    def _identify_mock_issues(self, analysis: MockBehaviorAnalysis, mock_type: str) -> List[str]:
        """Identify issues with mock realism."""
        issues = []
        
        # Check for never called mocks
        if analysis.call_count == 0:
            issues.append("Mock was never called")
        
        # Check for unrealistic call patterns
        if analysis.call_count > 1000:
            issues.append("Unrealistically high call count")
        
        # Check for missing async behavior
        mock_type_config = self.config["mock_types"].get(mock_type, {})
        if mock_type_config.get("expected_async", False) and analysis.async_calls == 0:
            issues.append("Missing expected async behavior")
        
        # Check for missing return values
        if analysis.call_count > 0 and not analysis.return_values:
            issues.append("No return values for called mock")
        
        # Check for missing side effects
        if analysis.call_count > 0 and not analysis.side_effects:
            issues.append("No side effects for called mock")
        
        return issues
    
    def _generate_mock_recommendations(self, analysis: MockBehaviorAnalysis, mock_type: str, 
                                     issues: List[str]) -> List[str]:
        """Generate recommendations for improving mock realism."""
        recommendations = []
        
        if "Mock was never called" in issues:
            recommendations.append("Ensure the mock is actually used in tests")
        
        if "Unrealistically high call count" in issues:
            recommendations.append("Review test logic to ensure realistic call patterns")
        
        if "Missing expected async behavior" in issues:
            recommendations.append("Add async behavior to match real implementation")
        
        if "No return values for called mock" in issues:
            recommendations.append("Add realistic return values")
        
        if "No side effects for called mock" in issues:
            recommendations.append("Add side effects to simulate real behavior")
        
        # Type-specific recommendations
        mock_type_config = self.config["mock_types"].get(mock_type, {})
        expected_methods = mock_type_config.get("expected_methods", [])
        
        if expected_methods:
            recommendations.append(f"Ensure mock implements expected methods: {', '.join(expected_methods)}")
        
        return recommendations
    
    def validate_mock_realism(self) -> Dict[str, Any]:
        """Validate overall mock realism."""
        validation_results = {
            "overall_status": "passed",
            "issues": [],
            "recommendations": [],
            "summary": {}
        }
        
        if not self.mock_scores:
            validation_results["overall_status"] = "no_data"
            return validation_results
        
        # Analyze all mock scores
        scores = list(self.mock_scores.values())
        thresholds = self.config["realism_thresholds"]
        
        high_quality = [s for s in scores if s.overall_score >= thresholds["high_quality"]]
        medium_quality = [s for s in scores if thresholds["medium_quality"] <= s.overall_score < thresholds["high_quality"]]
        low_quality = [s for s in scores if s.overall_score < thresholds["medium_quality"]]
        
        # Generate issues
        if low_quality:
            validation_results["issues"].append(f"{len(low_quality)} mocks have low realism scores")
        
        if medium_quality:
            validation_results["issues"].append(f"{len(medium_quality)} mocks have medium realism scores")
        
        # Generate recommendations
        if low_quality:
            validation_results["recommendations"].append("Focus on improving low-quality mocks first")
        
        if medium_quality:
            validation_results["recommendations"].append("Consider improving medium-quality mocks")
        
        # Overall status
        if low_quality:
            validation_results["overall_status"] = "failed"
        elif medium_quality:
            validation_results["overall_status"] = "warning"
        
        # Generate summary
        validation_results["summary"] = {
            "total_mocks": len(scores),
            "high_quality_mocks": len(high_quality),
            "medium_quality_mocks": len(medium_quality),
            "low_quality_mocks": len(low_quality),
            "average_realism_score": sum(s.overall_score for s in scores) / len(scores) if scores else 0.0
        }
        
        return validation_results
    
    def generate_mock_quality_report(self) -> str:
        """Generate comprehensive mock quality report."""
        if not self.mock_scores:
            return "No mock quality data available."
        
        validation = self.validate_mock_realism()
        scores = list(self.mock_scores.values())
        
        report = f"""
Mock Realism Validation Report
==============================

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERALL STATUS: {validation['overall_status'].upper()}

SUMMARY
=======
Total Mocks: {validation['summary']['total_mocks']}
High Quality Mocks: {validation['summary']['high_quality_mocks']}
Medium Quality Mocks: {validation['summary']['medium_quality_mocks']}
Low Quality Mocks: {validation['summary']['low_quality_mocks']}
Average Realism Score: {validation['summary']['average_realism_score']:.3f}

MOCK DETAILS
============
"""
        
        # Sort mocks by score
        sorted_scores = sorted(scores, key=lambda s: s.overall_score, reverse=True)
        
        for score in sorted_scores:
            report += f"""
{score.mock_name}:
  Overall Score: {score.overall_score:.3f}
  Behavior Score: {score.behavior_score:.3f}
  Data Score: {score.data_score:.3f}
  Interaction Score: {score.interaction_score:.3f}
  Error Handling Score: {score.error_handling_score:.3f}
  Performance Score: {score.performance_score:.3f}
  Issues: {len(score.issues)}
  Recommendations: {len(score.recommendations)}
"""
        
        if validation['issues']:
            report += "\nISSUES\n======\n"
            for issue in validation['issues']:
                report += f"- {issue}\n"
        
        if validation['recommendations']:
            report += "\nRECOMMENDATIONS\n===============\n"
            for i, recommendation in enumerate(validation['recommendations'], 1):
                report += f"{i}. {recommendation}\n"
        
        return report
    
    def save_mock_quality_report(self, filename: str = None):
        """Save mock quality report to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mock_quality_report_{timestamp}.txt"
        
        report = self.generate_mock_quality_report()
        report_file = Path(filename)
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"📄 Mock quality report saved to {report_file}")
    
    def clear_mock_data(self):
        """Clear mock analysis and score data."""
        self.mock_analyses.clear()
        self.mock_scores.clear()


# Global validator instance
mock_realism_validator = MockRealismValidator()


def get_mock_realism_validator() -> MockRealismValidator:
    """Get the global mock realism validator."""
    return mock_realism_validator


def analyze_mock_behavior(mock: Union[Mock, MagicMock, AsyncMock], 
                        mock_name: str, mock_type: str = "generic") -> MockBehaviorAnalysis:
    """Analyze mock behavior."""
    return mock_realism_validator.analyze_mock_behavior(mock, mock_name, mock_type)


def calculate_mock_realism_score(mock_name: str, mock_type: str = "generic") -> MockRealismScore:
    """Calculate mock realism score."""
    return mock_realism_validator.calculate_realism_score(mock_name, mock_type)


def validate_mock_realism() -> Dict[str, Any]:
    """Validate mock realism."""
    return mock_realism_validator.validate_mock_realism()


def generate_mock_quality_report() -> str:
    """Generate mock quality report."""
    return mock_realism_validator.generate_mock_quality_report()

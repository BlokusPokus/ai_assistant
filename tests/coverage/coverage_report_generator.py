"""
Coverage Report Generator

This module provides comprehensive coverage report generation including
HTML reports, JSON exports, and detailed analysis reports.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import html
import base64


class CoverageReportGenerator:
    """Generates comprehensive coverage reports in multiple formats."""
    
    def __init__(self, output_dir: str = "coverage_reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def generate_comprehensive_report(self, coverage_data: Dict[str, Any], 
                                    gaps: Dict[str, Any], 
                                    validation: Dict[str, Any]) -> Dict[str, str]:
        """Generate comprehensive coverage report in multiple formats."""
        reports = {}
        
        # Generate HTML report
        html_report = self._generate_html_report(coverage_data, gaps, validation)
        html_file = self.output_dir / f"coverage_report_{self.timestamp}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
        reports["html"] = str(html_file)
        
        # Generate JSON report
        json_report = self._generate_json_report(coverage_data, gaps, validation)
        json_file = self.output_dir / f"coverage_report_{self.timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_report, f, indent=2)
        reports["json"] = str(json_file)
        
        # Generate text report
        text_report = self._generate_text_report(coverage_data, gaps, validation)
        text_file = self.output_dir / f"coverage_report_{self.timestamp}.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(text_report)
        reports["text"] = str(text_file)
        
        # Generate markdown report
        markdown_report = self._generate_markdown_report(coverage_data, gaps, validation)
        md_file = self.output_dir / f"coverage_report_{self.timestamp}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(markdown_report)
        reports["markdown"] = str(md_file)
        
        return reports
    
    def _generate_html_report(self, coverage_data: Dict[str, Any], 
                            gaps: Dict[str, Any], 
                            validation: Dict[str, Any]) -> str:
        """Generate HTML coverage report."""
        overall = coverage_data.get("overall", {})
        summary = coverage_data.get("summary", {})
        validation_summary = validation.get("summary", {})
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Coverage Analysis Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }}
        .header h1 {{
            color: #333;
            margin: 0;
            font-size: 2.5em;
        }}
        .header .timestamp {{
            color: #666;
            font-size: 0.9em;
            margin-top: 10px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid #007bff;
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .summary-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }}
        .summary-card .label {{
            color: #666;
            font-size: 0.9em;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section h2 {{
            color: #333;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }}
        .coverage-bar {{
            background: #e0e0e0;
            height: 20px;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .coverage-fill {{
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            transition: width 0.3s ease;
        }}
        .coverage-fill.low {{
            background: linear-gradient(90deg, #dc3545, #fd7e14);
        }}
        .coverage-fill.medium {{
            background: linear-gradient(90deg, #ffc107, #fd7e14);
        }}
        .file-list {{
            background: #f8f9fa;
            border-radius: 6px;
            padding: 15px;
        }}
        .file-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #e0e0e0;
        }}
        .file-item:last-child {{
            border-bottom: none;
        }}
        .file-name {{
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.9em;
        }}
        .coverage-percent {{
            font-weight: bold;
            padding: 4px 8px;
            border-radius: 4px;
            color: white;
        }}
        .coverage-percent.high {{ background: #28a745; }}
        .coverage-percent.medium {{ background: #ffc107; color: #333; }}
        .coverage-percent.low {{ background: #dc3545; }}
        .recommendations {{
            background: #e7f3ff;
            border-left: 4px solid #007bff;
            padding: 15px;
            border-radius: 0 6px 6px 0;
        }}
        .recommendations ul {{
            margin: 0;
            padding-left: 20px;
        }}
        .recommendations li {{
            margin-bottom: 8px;
        }}
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .status-badge.success {{ background: #d4edda; color: #155724; }}
        .status-badge.warning {{ background: #fff3cd; color: #856404; }}
        .status-badge.danger {{ background: #f8d7da; color: #721c24; }}
        .chart-container {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            margin: 20px 0;
        }}
        .progress-item {{
            margin-bottom: 15px;
        }}
        .progress-label {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
        }}
        .progress-bar {{
            background: #e0e0e0;
            height: 8px;
            border-radius: 4px;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            background: #007bff;
            transition: width 0.3s ease;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Coverage Analysis Report</h1>
            <div class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        
        <div class="summary-grid">
            <div class="summary-card">
                <h3>Overall Coverage</h3>
                <div class="value">{overall.get('coverage_percent', 0):.1f}%</div>
                <div class="label">Target: {validation.get('summary', {}).get('overall_target', 80):.1f}%</div>
                <div class="coverage-bar">
                    <div class="coverage-fill {'low' if overall.get('coverage_percent', 0) < 70 else 'medium' if overall.get('coverage_percent', 0) < 85 else ''}" 
                         style="width: {overall.get('coverage_percent', 0)}%"></div>
                </div>
            </div>
            
            <div class="summary-card">
                <h3>Total Lines</h3>
                <div class="value">{overall.get('total_lines', 0):,}</div>
                <div class="label">Covered: {overall.get('covered_lines', 0):,}</div>
            </div>
            
            <div class="summary-card">
                <h3>Missing Lines</h3>
                <div class="value">{overall.get('missing_lines', 0):,}</div>
                <div class="label">Need Coverage</div>
            </div>
            
            <div class="summary-card">
                <h3>Target Compliance</h3>
                <div class="value">{validation.get('summary', {}).get('overall_success_rate', 0):.1f}%</div>
                <div class="label">Targets Met</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📈 Coverage Statistics</h2>
            <div class="chart-container">
                <div class="progress-item">
                    <div class="progress-label">
                        <span>Files with Coverage</span>
                        <span>{summary.get('files_with_coverage', 0)}/{summary.get('total_files', 0)}</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {(summary.get('files_with_coverage', 0) / max(1, summary.get('total_files', 0))) * 100}%"></div>
                    </div>
                </div>
                
                <div class="progress-item">
                    <div class="progress-label">
                        <span>Fully Covered Files</span>
                        <span>{summary.get('files_fully_covered', 0)}/{summary.get('total_files', 0)}</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {(summary.get('files_fully_covered', 0) / max(1, summary.get('total_files', 0))) * 100}%"></div>
                    </div>
                </div>
                
                <div class="progress-item">
                    <div class="progress-label">
                        <span>High Coverage Modules</span>
                        <span>{summary.get('modules_high_coverage', 0)}/{summary.get('total_modules', 0)}</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {(summary.get('modules_high_coverage', 0) / max(1, summary.get('total_modules', 0))) * 100}%"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🎯 Target Validation</h2>
            <div class="file-list">
                {self._generate_target_validation_html(validation)}
            </div>
        </div>
        
        <div class="section">
            <h2>🔍 Coverage Gaps</h2>
            <div class="file-list">
                {self._generate_gaps_html(gaps)}
            </div>
        </div>
        
        <div class="section">
            <h2>📋 Recommendations</h2>
            <div class="recommendations">
                <ul>
                    {self._generate_recommendations_html(gaps.get('recommendations', []))}
                </ul>
            </div>
        </div>
        
        <div class="section">
            <h2>📁 File Coverage Details</h2>
            <div class="file-list">
                {self._generate_file_coverage_html(coverage_data.get('files', {}))}
            </div>
        </div>
    </div>
</body>
</html>
"""
        return html_content
    
    def _generate_target_validation_html(self, validation: Dict[str, Any]) -> str:
        """Generate HTML for target validation section."""
        validations = validation.get("target_validations", [])
        html_content = ""
        
        for val in validations:
            target = val.get("target", {})
            actual = val.get("actual_coverage", 0)
            target_pct = target.get("target_percentage", 0)
            met = val.get("target_met", False)
            
            status_class = "success" if met else "warning" if actual >= target_pct * 0.8 else "danger"
            status_text = "✅ Met" if met else "⚠️ Close" if actual >= target_pct * 0.8 else "❌ Not Met"
            
            html_content += f"""
            <div class="file-item">
                <div>
                    <strong>{target.get('name', 'Unknown Target')}</strong>
                    <br>
                    <small>{target.get('description', '')}</small>
                </div>
                <div>
                    <span class="coverage-percent {status_class}">{actual:.1f}%</span>
                    <br>
                    <small>Target: {target_pct:.1f}%</small>
                    <br>
                    <span class="status-badge {status_class}">{status_text}</span>
                </div>
            </div>
            """
        
        return html_content
    
    def _generate_gaps_html(self, gaps: Dict[str, Any]) -> str:
        """Generate HTML for coverage gaps section."""
        html_content = ""
        
        for priority in ["critical", "high", "medium", "low"]:
            priority_gaps = gaps.get("by_priority", {}).get(priority, [])
            if priority_gaps:
                priority_class = {"critical": "danger", "high": "warning", "medium": "warning", "low": "success"}[priority]
                html_content += f"""
                <h3 style="color: #333; margin-top: 20px;">{priority.title()} Priority Gaps ({len(priority_gaps)} files)</h3>
                """
                
                for gap in priority_gaps[:10]:  # Show top 10
                    file_name = gap.get("file", "Unknown")
                    coverage = gap.get("coverage_percent", 0)
                    missing = gap.get("missing_lines", 0)
                    
                    html_content += f"""
                    <div class="file-item">
                        <div class="file-name">{file_name}</div>
                        <div>
                            <span class="coverage-percent {priority_class}">{coverage:.1f}%</span>
                            <br>
                            <small>{missing} missing lines</small>
                        </div>
                    </div>
                    """
        
        return html_content
    
    def _generate_recommendations_html(self, recommendations: List[str]) -> str:
        """Generate HTML for recommendations section."""
        return "".join(f"<li>{html.escape(rec)}</li>" for rec in recommendations)
    
    def _generate_file_coverage_html(self, files: Dict[str, Any]) -> str:
        """Generate HTML for file coverage details."""
        html_content = ""
        
        # Sort files by coverage percentage
        sorted_files = sorted(files.items(), key=lambda x: x[1].get("coverage_percent", 0))
        
        for file_path, file_data in sorted_files:
            coverage = file_data.get("coverage_percent", 0)
            total_lines = file_data.get("total_lines", 0)
            covered_lines = file_data.get("covered_lines", 0)
            missing_lines = file_data.get("missing_lines", 0)
            
            coverage_class = "high" if coverage >= 80 else "medium" if coverage >= 60 else "low"
            
            html_content += f"""
            <div class="file-item">
                <div>
                    <div class="file-name">{file_path}</div>
                    <small>{covered_lines}/{total_lines} lines covered</small>
                </div>
                <div>
                    <span class="coverage-percent {coverage_class}">{coverage:.1f}%</span>
                    <br>
                    <small>{missing_lines} missing</small>
                </div>
            </div>
            """
        
        return html_content
    
    def _generate_json_report(self, coverage_data: Dict[str, Any], 
                            gaps: Dict[str, Any], 
                            validation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate JSON coverage report."""
        return {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_version": "1.0",
                "generator": "CoverageReportGenerator"
            },
            "coverage_data": coverage_data,
            "coverage_gaps": gaps,
            "target_validation": validation,
            "summary": {
                "overall_coverage": coverage_data.get("overall", {}).get("coverage_percent", 0),
                "total_files": coverage_data.get("summary", {}).get("total_files", 0),
                "files_with_gaps": len(gaps.get("by_priority", {}).get("critical", [])) + 
                                 len(gaps.get("by_priority", {}).get("high", [])) +
                                 len(gaps.get("by_priority", {}).get("medium", [])) +
                                 len(gaps.get("by_priority", {}).get("low", [])),
                "targets_met": validation.get("summary", {}).get("targets_met", 0),
                "total_targets": validation.get("summary", {}).get("total_targets", 0)
            }
        }
    
    def _generate_text_report(self, coverage_data: Dict[str, Any], 
                            gaps: Dict[str, Any], 
                            validation: Dict[str, Any]) -> str:
        """Generate text coverage report."""
        overall = coverage_data.get("overall", {})
        summary = coverage_data.get("summary", {})
        validation_summary = validation.get("summary", {})
        
        report = f"""
Coverage Analysis Report
========================

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERALL SUMMARY
===============
Total Lines: {overall.get('total_lines', 0):,}
Covered Lines: {overall.get('covered_lines', 0):,}
Missing Lines: {overall.get('missing_lines', 0):,}
Coverage Percentage: {overall.get('coverage_percent', 0):.1f}%
Target Compliance: {validation_summary.get('overall_success_rate', 0):.1f}%

FILE STATISTICS
===============
Total Files: {summary.get('total_files', 0)}
Files with Coverage: {summary.get('files_with_coverage', 0)}
Files Fully Covered: {summary.get('files_fully_covered', 0)}
Files with Low Coverage: {summary.get('files_low_coverage', 0)}

MODULE STATISTICS
=================
Total Modules: {summary.get('total_modules', 0)}
High Coverage (≥80%): {summary.get('modules_high_coverage', 0)}
Medium Coverage (50-80%): {summary.get('modules_medium_coverage', 0)}
Low Coverage (<50%): {summary.get('modules_low_coverage', 0)}

TARGET VALIDATION
=================
Total Targets: {validation_summary.get('total_targets', 0)}
Targets Met: {validation_summary.get('targets_met', 0)}
Targets Not Met: {validation_summary.get('targets_not_met', 0)}
Overall Success Rate: {validation_summary.get('overall_success_rate', 0):.1f}%

COVERAGE GAPS
=============
"""
        
        for priority in ["critical", "high", "medium", "low"]:
            priority_gaps = gaps.get("by_priority", {}).get(priority, [])
            if priority_gaps:
                report += f"\n{priority.upper()} PRIORITY GAPS ({len(priority_gaps)} files):\n"
                for gap in priority_gaps[:10]:  # Show top 10
                    file_name = gap.get("file", "Unknown")
                    coverage = gap.get("coverage_percent", 0)
                    missing = gap.get("missing_lines", 0)
                    report += f"  - {file_name}: {coverage:.1f}% coverage, {missing} missing lines\n"
        
        report += "\nRECOMMENDATIONS\n===============\n"
        for i, recommendation in enumerate(gaps.get("recommendations", []), 1):
            report += f"{i}. {recommendation}\n"
        
        return report
    
    def _generate_markdown_report(self, coverage_data: Dict[str, Any], 
                                gaps: Dict[str, Any], 
                                validation: Dict[str, Any]) -> str:
        """Generate markdown coverage report."""
        overall = coverage_data.get("overall", {})
        summary = coverage_data.get("summary", {})
        validation_summary = validation.get("summary", {})
        
        report = f"""# 📊 Coverage Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📈 Overall Summary

| Metric | Value |
|--------|-------|
| **Total Lines** | {overall.get('total_lines', 0):,} |
| **Covered Lines** | {overall.get('covered_lines', 0):,} |
| **Missing Lines** | {overall.get('missing_lines', 0):,} |
| **Coverage Percentage** | {overall.get('coverage_percent', 0):.1f}% |
| **Target Compliance** | {validation_summary.get('overall_success_rate', 0):.1f}% |

## 📁 File Statistics

| Metric | Count |
|--------|-------|
| **Total Files** | {summary.get('total_files', 0)} |
| **Files with Coverage** | {summary.get('files_with_coverage', 0)} |
| **Files Fully Covered** | {summary.get('files_fully_covered', 0)} |
| **Files with Low Coverage** | {summary.get('files_low_coverage', 0)} |

## 🎯 Target Validation

| Target | Status | Coverage | Target | Gap |
|--------|--------|----------|--------|-----|
"""
        
        for val in validation.get("target_validations", []):
            target = val.get("target", {})
            actual = val.get("actual_coverage", 0)
            target_pct = target.get("target_percentage", 0)
            met = val.get("target_met", False)
            gap = val.get("gap", 0)
            
            status = "✅ Met" if met else "❌ Not Met"
            report += f"| {target.get('name', 'Unknown')} | {status} | {actual:.1f}% | {target_pct:.1f}% | {gap:.1f}% |\n"
        
        report += "\n## 🔍 Coverage Gaps\n\n"
        
        for priority in ["critical", "high", "medium", "low"]:
            priority_gaps = gaps.get("by_priority", {}).get(priority, [])
            if priority_gaps:
                report += f"### {priority.title()} Priority Gaps ({len(priority_gaps)} files)\n\n"
                report += "| File | Coverage | Missing Lines |\n"
                report += "|------|----------|---------------|\n"
                
                for gap in priority_gaps[:10]:  # Show top 10
                    file_name = gap.get("file", "Unknown")
                    coverage = gap.get("coverage_percent", 0)
                    missing = gap.get("missing_lines", 0)
                    report += f"| `{file_name}` | {coverage:.1f}% | {missing} |\n"
                
                report += "\n"
        
        report += "## 📋 Recommendations\n\n"
        for i, recommendation in enumerate(gaps.get("recommendations", []), 1):
            report += f"{i}. {recommendation}\n"
        
        return report


# Global report generator instance
report_generator = CoverageReportGenerator()


def get_report_generator() -> CoverageReportGenerator:
    """Get the global report generator."""
    return report_generator


def generate_coverage_reports(coverage_data: Dict[str, Any], 
                            gaps: Dict[str, Any], 
                            validation: Dict[str, Any]) -> Dict[str, str]:
    """Generate comprehensive coverage reports."""
    return report_generator.generate_comprehensive_report(coverage_data, gaps, validation)

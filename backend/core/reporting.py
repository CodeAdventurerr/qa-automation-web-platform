from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from backend.models.schemas import ExecutionReport, TestResult, TestStatus


class ReportBuilder:
    def finalize(self, project_id: str, results: list[TestResult]) -> ExecutionReport:
        report = ExecutionReport(project_id=project_id, total_tests=len(results), results=results)
        report.passed = sum(1 for result in results if result.status == TestStatus.PASSED)
        report.failed = sum(1 for result in results if result.status == TestStatus.FAILED)
        report.healed = sum(1 for result in results if result.status == TestStatus.HEALED)
        report.completed_at = datetime.now(UTC)
        return report

    def bug_report(self, title: str, steps: list[str], expected: str, actual: str, severity: str) -> dict[str, str | list[str]]:
        return {
            "title": title,
            "steps_to_reproduce": steps,
            "expected": expected,
            "actual": actual,
            "severity": severity,
        }

    def export_json(self, report: ExecutionReport, reports_dir: Path) -> Path:
        reports_dir.mkdir(parents=True, exist_ok=True)
        output = reports_dir / f"{report.project_id}-{report.run_id}.json"
        output.write_text(report.model_dump_json(indent=2), encoding="utf-8")
        return output

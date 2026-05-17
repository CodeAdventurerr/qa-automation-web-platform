from __future__ import annotations

from backend.core.reporting import ReportBuilder
from backend.core.selenium_runner import SeleniumRunner
from backend.models.schemas import ExecutionReport, Project, RunTestsRequest, TestStatus


class ExecutionController:
    def __init__(self) -> None:
        self.runner = SeleniumRunner()
        self.report_builder = ReportBuilder()

    def run_project(self, project: Project, request: RunTestsRequest) -> ExecutionReport:
        results = []
        for test_case in project.test_cases:
            result = self.runner.run_case(test_case, headless=request.headless, demo_mode=request.demo_mode)
            if result.status == TestStatus.FAILED:
                result.bug_report = self.report_builder.bug_report(
                    title=f"{test_case.title} failed",
                    steps=[step.description for step in test_case.steps],
                    expected=test_case.expected_result,
                    actual=result.logs[-1].message if result.logs else "Execution stopped unexpectedly.",
                    severity=test_case.severity,
                )
            results.append(result)
        return self.report_builder.finalize(project.id, results)


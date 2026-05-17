from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.models.schemas import ExecutionReport, Project


class JsonStore:
    def __init__(self, root: Path | str = "storage_data") -> None:
        self.root = Path(root)
        self.projects_dir = self.root / "projects"
        self.reports_dir = self.root / "reports"
        self.logs_dir = self.root / "logs"
        for directory in (self.projects_dir, self.reports_dir, self.logs_dir):
            directory.mkdir(parents=True, exist_ok=True)

    def save_project(self, project: Project) -> Project:
        self._write_json(self.projects_dir / f"{project.id}.json", project.model_dump(mode="json"))
        return project

    def get_project(self, project_id: str) -> Project:
        data = self._read_json(self.projects_dir / f"{project_id}.json")
        return Project.model_validate(data)

    def save_report(self, report: ExecutionReport) -> ExecutionReport:
        self._write_json(self.reports_dir / f"{report.project_id}.json", report.model_dump(mode="json"))
        return report

    def get_report(self, project_id: str) -> ExecutionReport:
        data = self._read_json(self.reports_dir / f"{project_id}.json")
        return ExecutionReport.model_validate(data)

    def get_test_logs(self, test_id: str) -> list[dict[str, Any]]:
        logs: list[dict[str, Any]] = []
        for report_path in self.reports_dir.glob("*.json"):
            report = self._read_json(report_path)
            for result in report.get("results", []):
                if result.get("test_id") == test_id:
                    logs.extend(result.get("logs", []))
        return logs

    @staticmethod
    def _write_json(path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        if not path.exists():
            raise FileNotFoundError(f"No stored record at {path}")
        return json.loads(path.read_text(encoding="utf-8"))


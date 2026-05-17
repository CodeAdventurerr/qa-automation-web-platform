from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, HttpUrl


class StepAction(StrEnum):
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    WAIT = "wait"
    ASSERT_TEXT = "assert_text"


class TestStatus(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    HEALED = "HEALED"


class GenerateTestsRequest(BaseModel):
    url: HttpUrl
    feature: str = Field(min_length=3, max_length=500)


class TestStep(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    action: StepAction
    description: str
    selector: str | None = None
    value: str | None = None
    expected: str | None = None
    timeout_seconds: int = 8


class TestCase(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    type: str = Field(pattern="^(positive|negative|edge)$")
    severity: str = "medium"
    steps: list[TestStep]
    expected_result: str


class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    url: str
    feature: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    test_cases: list[TestCase]


class RunTestsRequest(BaseModel):
    project_id: str
    headless: bool = True
    demo_mode: bool = True


class StepLog(BaseModel):
    step_id: str
    status: TestStatus
    message: str
    selector_used: str | None = None
    healed_selector: str | None = None
    screenshot_path: str | None = None
    dom_snapshot_path: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class TestResult(BaseModel):
    test_id: str
    title: str
    status: TestStatus
    healed_steps: int = 0
    logs: list[StepLog] = Field(default_factory=list)
    bug_report: dict[str, Any] | None = None


class ExecutionReport(BaseModel):
    project_id: str
    run_id: str = Field(default_factory=lambda: str(uuid4()))
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    healed: int = 0
    results: list[TestResult] = Field(default_factory=list)


class GenerateTestsResponse(BaseModel):
    project_id: str
    test_cases: list[TestCase]
